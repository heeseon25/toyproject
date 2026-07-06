
import re
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS


# =========================================================
# Page Config
# =========================================================
st.set_page_config(
    page_title="Amazon Review Early Warning System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# Styling
# =========================================================
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #f7fbff 0%, #ffffff 45%, #f8fafc 100%);
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 28px 30px;
        border-radius: 24px;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 52%, #2563eb 100%);
        color: white;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18);
        margin-bottom: 22px;
    }
    .hero h1 {
        font-size: 2.35rem;
        line-height: 1.15;
        margin-bottom: 0.4rem;
    }
    .hero p {
        color: rgba(255, 255, 255, 0.82);
        font-size: 1.02rem;
        margin-bottom: 0;
    }
    .section-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.5rem 0 0.4rem 0;
    }
    .subtle {
        color: #64748b;
        font-size: 0.95rem;
    }
    .metric-card {
        border-radius: 20px;
        padding: 18px 20px;
        background: white;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
    }
    .alert-critical {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        border-radius: 16px;
        padding: 18px;
        font-weight: 700;
    }
    .alert-risk {
        background: #ffedd5;
        color: #9a3412;
        border: 1px solid #fed7aa;
        border-radius: 16px;
        padding: 18px;
        font-weight: 700;
    }
    .alert-normal {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 18px;
        font-weight: 700;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 800;
    }
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# Constants
# =========================================================
DEFAULT_NEGATIVE_LEXICON = [
    "bad", "broken", "poor", "waste", "wasted", "disappointed", "disappointing",
    "damage", "damaged", "defective", "issue", "problem", "refund", "return",
    "doesnt", "don't", "dont", "not", "failed", "fail", "useless", "worst",
    "stopped", "slow", "hard", "cheap", "fake", "missing", "dead", "faulty",
    "replacement", "complaint", "terrible", "awful", "wont", "won't"
]

CUSTOM_STOPWORDS = {
    "product", "products", "good", "quality", "use", "using", "used", "buy",
    "bought", "one", "time", "price", "amazon", "like", "also", "nice",
    "best", "really", "overall", "money", "phone", "cable", "item", "work",
    "working", "review", "purchase", "purchased"
}


# =========================================================
# Helper Functions
# =========================================================
def clean_text(text: str) -> str:
    """Basic text cleaning for review content."""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_review_column(df: pd.DataFrame) -> str:
    candidates = ["review_content", "review", "reviews", "content", "review_text"]
    for c in candidates:
        if c in df.columns:
            return c
    # fallback: first object column that looks long
    object_cols = df.select_dtypes(include="object").columns.tolist()
    if not object_cols:
        raise ValueError("리뷰 텍스트 컬럼을 찾을 수 없습니다.")
    avg_len = {c: df[c].astype(str).str.len().mean() for c in object_cols}
    return max(avg_len, key=avg_len.get)


def find_rating_column(df: pd.DataFrame) -> str | None:
    for c in ["rating", "ratings", "star", "stars"]:
        if c in df.columns:
            return c
    return None


def preprocess_amazon(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare Amazon review dataset."""
    df = df.copy()

    review_col = find_review_column(df)
    if review_col != "review_content":
        df["review_content"] = df[review_col]

    rating_col = find_rating_column(df)
    if rating_col and rating_col != "rating":
        df["rating"] = df[rating_col]

    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(
            df["rating"].astype(str).str.replace("|", "", regex=False),
            errors="coerce"
        )
        df["rating"] = df["rating"].fillna(df["rating"].median())
    else:
        df["rating"] = np.nan

    if "product_name" not in df.columns:
        df["product_name"] = "Unknown Product"

    df["review_content"] = df["review_content"].fillna("").astype(str)
    df["clean_review"] = df["review_content"].apply(clean_text)
    df["review_length"] = df["clean_review"].apply(lambda x: len(x.split()))

    df["sentiment_score"] = df["clean_review"].apply(
        lambda x: TextBlob(str(x)).sentiment.polarity
    )
    df["emotion_strength"] = df["sentiment_score"].abs()

    return df


def extract_negative_keywords(df: pd.DataFrame, top_n: int = 20):
    """Extract negative keywords from low-rating or negative-sentiment reviews."""
    negative_pool = df[
        ((df["rating"] <= 3.5) if "rating" in df.columns else False)
        | (df["sentiment_score"] < 0)
    ]["clean_review"].astype(str)

    if len(negative_pool) < 3:
        return DEFAULT_NEGATIVE_LEXICON[:top_n], pd.DataFrame({
            "keyword": DEFAULT_NEGATIVE_LEXICON[:top_n],
            "score": np.linspace(top_n, 1, top_n)
        })

    stop_words = list(ENGLISH_STOP_WORDS.union(CUSTOM_STOPWORDS))
    vectorizer = TfidfVectorizer(
        stop_words=stop_words,
        max_features=120,
        ngram_range=(1, 2),
        min_df=1
    )

    try:
        matrix = vectorizer.fit_transform(negative_pool)
        scores = matrix.sum(axis=0).A1
        keyword_df = pd.DataFrame({
            "keyword": vectorizer.get_feature_names_out(),
            "score": scores
        }).sort_values("score", ascending=False)

        # Keep terms that are plausibly complaint-related:
        # 1) terms in negative lexicon OR 2) terms appearing in negative pool after general stopword filtering
        remove_words = set(CUSTOM_STOPWORDS)
        keyword_df = keyword_df[~keyword_df["keyword"].isin(remove_words)]

        auto_keywords = keyword_df.head(top_n)["keyword"].tolist()

        # Blend with complaint lexicon so obvious complaint terms are not lost
        final_keywords = []
        for w in auto_keywords + DEFAULT_NEGATIVE_LEXICON:
            if w not in final_keywords and w not in remove_words:
                final_keywords.append(w)

        return final_keywords[:top_n], keyword_df.head(top_n)

    except Exception:
        return DEFAULT_NEGATIVE_LEXICON[:top_n], pd.DataFrame({
            "keyword": DEFAULT_NEGATIVE_LEXICON[:top_n],
            "score": np.linspace(top_n, 1, top_n)
        })


def count_keywords(text: str, keywords: list[str]) -> int:
    text = str(text).lower()
    count = 0
    for kw in keywords:
        if kw in text:
            count += text.count(kw)
    return count


def score_dataset(df: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    df = df.copy()
    df["negative_keyword_count"] = df["clean_review"].apply(lambda x: count_keywords(x, keywords))

    df["negative_sentiment_strength"] = df["sentiment_score"].apply(
        lambda x: abs(x) if x < 0 else 0
    )

    max_kw = max(df["negative_keyword_count"].max(), 1)
    max_len = max(df["review_length"].max(), 1)

    df["negative_keyword_score"] = df["negative_keyword_count"] / max_kw
    df["review_length_norm"] = df["review_length"] / max_len

    df["early_warning_score"] = (
        df["negative_sentiment_strength"] * 0.55
        + df["negative_keyword_score"] * 0.30
        + df["review_length_norm"] * 0.15
    )

    risk_threshold = df["early_warning_score"].quantile(0.85)
    critical_threshold = df["early_warning_score"].quantile(0.95)

    def level(score):
        if score >= critical_threshold:
            return "Critical"
        if score >= risk_threshold:
            return "Risk"
        return "Normal"

    df["warning_level"] = df["early_warning_score"].apply(level)
    return df, risk_threshold, critical_threshold


def score_single_review(text: str, keywords: list[str], risk_threshold: float, critical_threshold: float,
                        max_keyword_count: int = 10, max_review_length: int = 300):
    clean = clean_text(text)
    sentiment = TextBlob(clean).sentiment.polarity
    emotion = abs(sentiment)
    neg_sent = abs(sentiment) if sentiment < 0 else 0
    kw_count = count_keywords(clean, keywords)
    kw_score = min(kw_count / max(max_keyword_count, 1), 1)
    length = len(clean.split())
    length_norm = min(length / max(max_review_length, 1), 1)

    score = neg_sent * 0.55 + kw_score * 0.30 + length_norm * 0.15

    if score >= critical_threshold:
        level = "Critical"
    elif score >= risk_threshold:
        level = "Risk"
    else:
        level = "Normal"

    matched = [kw for kw in keywords if kw in clean]

    return {
        "clean_review": clean,
        "sentiment_score": sentiment,
        "emotion_strength": emotion,
        "negative_sentiment_strength": neg_sent,
        "negative_keyword_count": kw_count,
        "negative_keyword_score": kw_score,
        "review_length": length,
        "review_length_norm": length_norm,
        "early_warning_score": score,
        "warning_level": level,
        "matched_keywords": matched[:12]
    }


@st.cache_data(show_spinner=False)
def load_default_if_exists():
    for filename in ["amazon.csv", "data/amazon.csv", "Amazon.csv"]:
        try:
            return pd.read_csv(filename)
        except Exception:
            pass
    return None


# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("⚙️ 설정")
st.sidebar.caption("Amazon Sales Dataset CSV를 업로드하거나, repo에 amazon.csv를 넣으면 자동 로드됩니다.")

uploaded_file = st.sidebar.file_uploader("Amazon CSV 업로드", type=["csv"])

sample_review = """The product stopped working after two days. Battery is terrible and I want a refund."""

with st.sidebar.expander("모델 계산식", expanded=False):
    st.markdown(
        """
        **Early Warning Score**

        `0.55 × negative_sentiment_strength`

        `+ 0.30 × negative_keyword_score`

        `+ 0.15 × review_length_norm`

        - 부정 감정이 강할수록 위험도 증가
        - 부정 키워드가 많을수록 위험도 증가
        - 리뷰가 길수록 상세 불만 가능성 반영
        """
    )


# =========================================================
# Header
# =========================================================
st.markdown(
    """
    <div class="hero">
        <h1>🚨 Amazon Review Early Warning System</h1>
        <p>리뷰 텍스트를 입력하면 감정 점수, 부정 키워드, 리뷰 길이를 바탕으로 불만 고객 조기 경보 수준을 판단합니다.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# Data Load
# =========================================================
if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)
else:
    raw_df = load_default_if_exists()

if raw_df is None:
    st.info("CSV 파일을 업로드하면 위쪽 대시보드가 실제 데이터 기반으로 채워집니다. 아래 시뮬레이터는 기본 키워드로 바로 사용 가능합니다.")
    df = None
    keywords = DEFAULT_NEGATIVE_LEXICON[:20]
    keyword_df = pd.DataFrame({"keyword": keywords, "score": np.linspace(20, 1, len(keywords))})
    risk_threshold, critical_threshold = 0.25, 0.45
else:
    df = preprocess_amazon(raw_df)
    keywords, keyword_df = extract_negative_keywords(df, top_n=20)
    df, risk_threshold, critical_threshold = score_dataset(df, keywords)

# =========================================================
# Top Dashboard: Visualizations
# =========================================================
st.markdown('<div class="section-title">1. 데이터 기반 조기 경보 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">자동 추출된 부정 키워드와 실제 위험 리뷰 예시를 함께 보여줍니다.</div>', unsafe_allow_html=True)

top_cols = st.columns([1.05, 1.25])

with top_cols[0]:
    st.subheader("자동 추출 부정 키워드 TOP 15")
    top15 = keyword_df.head(15).sort_values("score", ascending=True)
    fig_kw = px.bar(
        top15,
        x="score",
        y="keyword",
        orientation="h",
        text=top15["score"].round(2),
        labels={"score": "TF-IDF score", "keyword": "Keyword"},
        title="TF-IDF 기반 부정 키워드 중요도"
    )
    fig_kw.update_traces(textposition="outside")
    fig_kw.update_layout(height=520, margin=dict(l=10, r=40, t=60, b=20))
    st.plotly_chart(fig_kw, use_container_width=True)

with top_cols[1]:
    st.subheader("조기 경보 리뷰 예시")
    if df is not None:
        example_df = df.sort_values("early_warning_score", ascending=False).head(8).copy()
        example_df["review"] = example_df["review_content"].astype(str).str.slice(0, 150) + "..."
        show_df = example_df[[
            "product_name", "rating", "review", "sentiment_score",
            "negative_keyword_count", "early_warning_score", "warning_level"
        ]].rename(columns={
            "product_name": "상품명",
            "rating": "별점",
            "review": "리뷰 내용",
            "sentiment_score": "감정 점수",
            "negative_keyword_count": "부정 키워드 수",
            "early_warning_score": "경보 점수",
            "warning_level": "경보 단계"
        })
        st.dataframe(
            show_df,
            use_container_width=True,
            height=520,
            hide_index=True
        )
    else:
        st.warning("CSV 업로드 시 실제 리뷰 예시 테이블이 표시됩니다.")

if df is not None:
    m1, m2, m3, m4 = st.columns(4)
    total = len(df)
    risk_count = int((df["warning_level"] == "Risk").sum())
    critical_count = int((df["warning_level"] == "Critical").sum())
    normal_count = int((df["warning_level"] == "Normal").sum())
    avg_score = df["early_warning_score"].mean()

    m1.metric("전체 리뷰", f"{total:,}")
    m2.metric("Risk 리뷰", f"{risk_count:,}")
    m3.metric("Critical 리뷰", f"{critical_count:,}")
    m4.metric("평균 경보 점수", f"{avg_score:.3f}")

# =========================================================
# Bottom: Simulator
# =========================================================
st.markdown('<div class="section-title">2. 리뷰 입력 시뮬레이터</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">리뷰를 입력하면 불만 고객인지 아닌지 즉시 판단합니다.</div>', unsafe_allow_html=True)

sim_cols = st.columns([1.1, 0.9])

with sim_cols[0]:
    user_review = st.text_area(
        "리뷰 텍스트 입력",
        value=sample_review,
        height=180,
        placeholder="예: The product is broken and I want a refund..."
    )

    analyze = st.button("🚨 조기 경보 분석하기", use_container_width=True)

with sim_cols[1]:
    st.markdown("#### 사용 중인 부정 키워드")
    st.write(", ".join(keywords[:20]))

if analyze or user_review:
    result = score_single_review(
        user_review,
        keywords,
        risk_threshold=risk_threshold,
        critical_threshold=critical_threshold,
        max_keyword_count=(df["negative_keyword_count"].max() if df is not None else 10),
        max_review_length=(df["review_length"].max() if df is not None else 300)
    )

    level = result["warning_level"]

    st.markdown("### 분석 결과")

    if level == "Critical":
        st.markdown('<div class="alert-critical">🚨 CRITICAL: 즉시 확인이 필요한 강한 불만 리뷰입니다.</div>', unsafe_allow_html=True)
    elif level == "Risk":
        st.markdown('<div class="alert-risk">⚠️ RISK: 불만 가능성이 있어 모니터링이 필요한 리뷰입니다.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-normal">✅ NORMAL: 현재 기준으로는 불만 위험도가 낮은 리뷰입니다.</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("감정 점수", f"{result['sentiment_score']:.3f}", help="-1에 가까울수록 부정, 1에 가까울수록 긍정")
    r2.metric("부정 감정 강도", f"{result['negative_sentiment_strength']:.3f}", help="부정 감정일 때만 반영되는 강도")
    r3.metric("부정 키워드 수", f"{result['negative_keyword_count']}")
    r4.metric("조기 경보 점수", f"{result['early_warning_score']:.3f}")

    chart_df = pd.DataFrame({
        "요소": ["부정 감정", "부정 키워드", "리뷰 길이"],
        "기여도": [
            result["negative_sentiment_strength"] * 0.55,
            result["negative_keyword_score"] * 0.30,
            result["review_length_norm"] * 0.15
        ]
    })

    c1, c2 = st.columns([1, 1])

    with c1:
        fig_score = px.bar(
            chart_df,
            x="요소",
            y="기여도",
            text=chart_df["기여도"].round(3),
            title="경보 점수 구성 요소"
        )
        fig_score.update_traces(textposition="outside")
        fig_score.update_layout(height=380, yaxis_title="Score contribution")
        st.plotly_chart(fig_score, use_container_width=True)

    with c2:
        gauge = px.pie(
            pd.DataFrame({
                "level": ["현재 점수", "남은 구간"],
                "value": [result["early_warning_score"], max(critical_threshold - result["early_warning_score"], 0)]
            }),
            names="level",
            values="value",
            hole=0.65,
            title="Critical 기준 대비 현재 위험도"
        )
        gauge.update_layout(height=380)
        st.plotly_chart(gauge, use_container_width=True)

    st.markdown("#### 탐지된 부정 키워드")
    if result["matched_keywords"]:
        st.write(" / ".join(result["matched_keywords"]))
    else:
        st.write("탐지된 부정 키워드가 없습니다.")

    st.markdown("#### 해석")
    st.write(
        f"""
        이 리뷰는 감정 점수 **{result['sentiment_score']:.3f}**, 
        부정 키워드 **{result['negative_keyword_count']}개**, 
        조기 경보 점수 **{result['early_warning_score']:.3f}**로 계산되었습니다.
        현재 기준에서 이 리뷰는 **{level}** 단계로 분류됩니다.
        """
    )
