<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>불만 고객 조기 경보 모델 | Early Warning System for Negative Feedback</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #f5f7fb;
      --card: #ffffff;
      --text: #111827;
      --muted: #6b7280;
      --line: #e5e7eb;
      --blue: #2563eb;
      --blue2: #1e40af;
      --red: #dc2626;
      --orange: #f97316;
      --green: #16a34a;
      --shadow: 0 14px 35px rgba(15, 23, 42, 0.10);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.14), transparent 32%),
        linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
      color: var(--text);
    }

    .container {
      max-width: 1220px;
      margin: 0 auto;
      padding: 34px 22px 60px;
    }

    .hero {
      background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 48%, #2563eb 100%);
      color: white;
      padding: 34px;
      border-radius: 28px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }

    .hero::after {
      content: "";
      position: absolute;
      right: -80px;
      top: -80px;
      width: 240px;
      height: 240px;
      background: rgba(255,255,255,0.14);
      border-radius: 50%;
    }

    .hero h1 {
      margin: 0 0 10px;
      font-size: clamp(30px, 5vw, 50px);
      letter-spacing: -0.04em;
    }

    .hero p {
      margin: 0;
      color: rgba(255,255,255,0.84);
      font-size: 17px;
      line-height: 1.6;
      max-width: 820px;
    }

    .section-title {
      margin: 34px 0 12px;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .section-title h2 {
      margin: 0;
      font-size: 25px;
      letter-spacing: -0.03em;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      padding: 6px 11px;
      border-radius: 999px;
      background: #dbeafe;
      color: #1d4ed8;
      font-size: 13px;
      font-weight: 700;
    }

    .grid {
      display: grid;
      gap: 18px;
    }

    .grid.two {
      grid-template-columns: 1fr 1.25fr;
    }

    .grid.three {
      grid-template-columns: repeat(3, 1fr);
    }

    .card {
      background: rgba(255,255,255,0.92);
      border: 1px solid rgba(226,232,240,0.9);
      border-radius: 24px;
      padding: 22px;
      box-shadow: 0 10px 26px rgba(15, 23, 42, 0.07);
      backdrop-filter: blur(12px);
    }

    .card h3 {
      margin: 0 0 8px;
      font-size: 19px;
      letter-spacing: -0.02em;
    }

    .card .desc {
      margin: 0 0 16px;
      color: var(--muted);
      line-height: 1.55;
      font-size: 14px;
    }

    .metric {
      background: #f8fafc;
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
    }

    .metric span {
      display: block;
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 6px;
    }

    .metric strong {
      font-size: 24px;
      letter-spacing: -0.02em;
    }

    .table-wrap {
      overflow-x: auto;
      border-radius: 16px;
      border: 1px solid var(--line);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      background: white;
      min-width: 760px;
    }

    th, td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
      text-align: left;
      font-size: 14px;
    }

    th {
      background: #f8fafc;
      color: #334155;
      font-size: 13px;
    }

    .pill {
      display: inline-flex;
      padding: 5px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
    }

    .pill.critical { background: #fee2e2; color: #991b1b; }
    .pill.risk { background: #ffedd5; color: #9a3412; }
    .pill.normal { background: #dcfce7; color: #166534; }

    textarea {
      width: 100%;
      min-height: 170px;
      resize: vertical;
      border: 1px solid #d1d5db;
      border-radius: 18px;
      padding: 16px;
      font-size: 16px;
      line-height: 1.55;
      outline: none;
      font-family: inherit;
      background: white;
    }

    textarea:focus {
      border-color: var(--blue);
      box-shadow: 0 0 0 4px rgba(37,99,235,0.15);
    }

    button {
      width: 100%;
      border: 0;
      border-radius: 16px;
      background: linear-gradient(135deg, var(--blue), var(--blue2));
      color: white;
      padding: 15px 18px;
      font-size: 16px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 10px 20px rgba(37, 99, 235, 0.22);
    }

    button:hover { filter: brightness(1.05); }

    .result-box {
      border-radius: 22px;
      padding: 20px;
      border: 1px solid var(--line);
      background: #f8fafc;
    }

    .result-box.critical { background: #fef2f2; border-color: #fecaca; }
    .result-box.risk { background: #fff7ed; border-color: #fed7aa; }
    .result-box.normal { background: #f0fdf4; border-color: #bbf7d0; }

    .result-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
    }

    .result-head strong {
      font-size: 24px;
    }

    .keyword-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }

    .keyword-chip {
      padding: 6px 10px;
      background: #eff6ff;
      color: #1d4ed8;
      border-radius: 999px;
      font-weight: 700;
      font-size: 13px;
    }

    .formula {
      background: #0f172a;
      color: #e5e7eb;
      border-radius: 18px;
      padding: 18px;
      font-family: "SFMono-Regular", Consolas, monospace;
      line-height: 1.7;
      font-size: 14px;
    }

    .small-note {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.6;
    }

    canvas {
      max-height: 300px;
    }


    .warning-hero {
      border-radius: 26px;
      padding: 26px;
      border: 2px solid #fecaca;
      background: linear-gradient(135deg, #fff1f2 0%, #fff7ed 100%);
      box-shadow: 0 16px 40px rgba(220, 38, 38, 0.10);
    }

    .warning-hero.risk {
      border-color: #fed7aa;
      background: linear-gradient(135deg, #fff7ed 0%, #fffbeb 100%);
      box-shadow: 0 16px 40px rgba(249, 115, 22, 0.10);
    }

    .warning-hero.normal {
      border-color: #bbf7d0;
      background: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 100%);
      box-shadow: 0 16px 40px rgba(22, 163, 74, 0.10);
    }

    .warning-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 14px;
      margin-bottom: 18px;
    }

    .warning-title {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: clamp(28px, 4vw, 44px);
      font-weight: 900;
      letter-spacing: -0.05em;
      margin: 0;
      color: #111827;
    }

    .warning-subtitle {
      margin: 8px 0 0 54px;
      color: #6b7280;
      font-weight: 700;
      font-size: 15px;
    }

    .score-badge {
      flex: 0 0 auto;
      padding: 10px 16px;
      border-radius: 999px;
      font-size: 18px;
      font-weight: 900;
      background: #fee2e2;
      color: #991b1b;
    }

    .warning-hero.risk .score-badge {
      background: #ffedd5;
      color: #9a3412;
    }

    .warning-hero.normal .score-badge {
      background: #dcfce7;
      color: #166534;
    }

    .risk-meter {
      margin: 14px 0 20px;
      padding: 16px;
      border-radius: 18px;
      background: rgba(255,255,255,0.72);
      border: 1px solid rgba(226,232,240,0.9);
    }

    .meter-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
      font-weight: 800;
    }

    .meter-label {
      color: #374151;
    }

    .meter-value {
      font-size: 22px;
      color: #991b1b;
    }

    .warning-hero.risk .meter-value {
      color: #9a3412;
    }

    .warning-hero.normal .meter-value {
      color: #166534;
    }

    .meter-track {
      height: 18px;
      border-radius: 999px;
      background: #e5e7eb;
      overflow: hidden;
      position: relative;
    }

    .meter-fill {
      height: 100%;
      width: 0%;
      border-radius: 999px;
      background: linear-gradient(90deg, #f97316, #dc2626);
      transition: width 0.5s ease;
    }

    .warning-hero.risk .meter-fill {
      background: linear-gradient(90deg, #fbbf24, #f97316);
    }

    .warning-hero.normal .meter-fill {
      background: linear-gradient(90deg, #22c55e, #16a34a);
    }

    .signal-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin: 18px 0;
    }

    .signal-card {
      background: rgba(255,255,255,0.78);
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      padding: 16px;
    }

    .signal-card span {
      display: block;
      color: #6b7280;
      font-weight: 700;
      margin-bottom: 8px;
    }

    .signal-card strong {
      display: block;
      font-size: 30px;
      letter-spacing: -0.03em;
      color: #111827;
    }

    .signal-card em {
      display: inline-block;
      margin-top: 8px;
      font-style: normal;
      font-size: 13px;
      font-weight: 800;
      color: #991b1b;
      background: #fee2e2;
      padding: 4px 8px;
      border-radius: 999px;
    }

    .reason-table {
      width: 100%;
      min-width: 0;
      border-collapse: separate;
      border-spacing: 0;
      overflow: hidden;
      border-radius: 16px;
      margin: 16px 0;
      background: white;
      border: 1px solid #e5e7eb;
    }

    .reason-table th,
    .reason-table td {
      min-width: 0;
      font-size: 14px;
      padding: 12px 13px;
    }

    .reason-table th {
      background: #f8fafc;
      color: #475569;
    }

    .insight-box {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-left: 6px solid #dc2626;
      border-radius: 18px;
      padding: 16px 18px;
      line-height: 1.65;
      color: #374151;
      margin-top: 14px;
    }

    .warning-hero.risk .insight-box {
      border-left-color: #f97316;
    }

    .warning-hero.normal .insight-box {
      border-left-color: #16a34a;
    }

    .action-box {
      margin-top: 12px;
      padding: 16px 18px;
      border-radius: 18px;
      background: #0f172a;
      color: white;
      line-height: 1.65;
    }

    .action-box strong {
      color: #fef3c7;
    }


    .process-flow {
      margin-top: 18px;
      padding: 18px;
      border-radius: 20px;
      background: #f8fafc;
      border: 1px solid #e5e7eb;
    }

    .process-flow h4,
    .insight-panel h4 {
      margin: 0 0 12px;
      font-size: 17px;
      letter-spacing: -0.02em;
    }

    .flow-steps {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      align-items: center;
    }

    .flow-step {
      text-align: center;
      padding: 12px 8px;
      border-radius: 16px;
      background: white;
      border: 1px solid #e5e7eb;
      font-weight: 800;
      font-size: 13px;
      color: #1f2937;
    }

    .flow-step span {
      display: block;
      font-size: 22px;
      margin-bottom: 4px;
    }

    .insight-panel {
      margin-top: 18px;
      padding: 18px;
      border-radius: 20px;
      background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
      border: 1px solid #bfdbfe;
    }

    .insight-list {
      margin: 0;
      padding-left: 20px;
      color: #374151;
      line-height: 1.7;
      font-size: 14px;
    }

    .insight-list strong {
      color: #1d4ed8;
    }

    .mini-kpi-row {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 14px;
    }

    .mini-kpi {
      background: white;
      border: 1px solid #dbeafe;
      border-radius: 16px;
      padding: 12px;
      text-align: center;
    }

    .mini-kpi b {
      display: block;
      font-size: 20px;
      color: #1d4ed8;
    }

    .mini-kpi span {
      color: #64748b;
      font-size: 12px;
      font-weight: 700;
    }

    @media (max-width: 900px) {
      .flow-steps,
      .mini-kpi-row {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 900px) {
      .warning-top {
        flex-direction: column;
      }
      .warning-subtitle {
        margin-left: 0;
      }
      .signal-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 900px) {
      .grid.two, .grid.three {
        grid-template-columns: 1fr;
      }
      .hero {
        padding: 26px;
      }
    }
  
    /* ===============================
       Final visual polish overrides
       =============================== */
    body, button, textarea, table, .card, .metric, .warning-hero {
      word-break: keep-all;
      overflow-wrap: normal;
    }

    .container {
      max-width: 1280px;
      padding: 28px 28px 56px;
    }

    .hero {
      padding: 30px 34px;
      border-radius: 24px;
    }

    .hero h1 {
      margin: 0 0 14px;
    }
    .hero-title span {
      display: block;
      font-size: clamp(32px, 4vw, 48px);
      line-height: 1.15;
      white-space: nowrap;
    }
    .hero-title small {
      display: block;
      margin-top: 8px;
      font-size: clamp(18px, 2vw, 26px);
      line-height: 1.3;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: rgba(255,255,255,0.78);
      white-space: nowrap;
    }

    .hero p {
      max-width: 900px;
      font-size: 16px;
    }

    .grid.two {
      grid-template-columns: minmax(390px, 0.95fr) minmax(560px, 1.45fr);
      align-items: start;
    }

    .card {
      padding: 22px 24px;
      border-radius: 22px;
    }

    .card h3,
    .section-title h2,
    .badge,
    button,
    .metric strong,
    .flow-step,
    .mini-kpi b,
    .mini-kpi span,
    .score-badge,
    .warning-title,
    .pill {
      white-space: nowrap;
    }

    .card .desc {
      font-size: 13px;
      line-height: 1.55;
    }

    canvas {
      max-height: 270px;
    }

    .insight-panel {
      margin-top: 14px;
      padding: 16px;
    }

    .insight-panel h4,
    .process-flow h4 {
      font-size: 16px;
      white-space: nowrap;
    }

    .insight-list {
      font-size: 13px;
      line-height: 1.65;
    }

    .mini-kpi-row {
      grid-template-columns: repeat(3, minmax(105px, 1fr));
      gap: 8px;
    }

    .mini-kpi {
      padding: 10px 8px;
      min-height: 76px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .mini-kpi b {
      font-size: 18px;
      line-height: 1.1;
    }

    .mini-kpi span {
      font-size: 11px;
      line-height: 1.25;
    }

    .process-flow {
      margin-top: 16px;
      padding: 16px;
    }

    .flow-steps {
      grid-template-columns: repeat(5, minmax(72px, 1fr));
      gap: 9px;
    }

    .flow-step {
      padding: 12px 6px;
      font-size: 12px;
      line-height: 1.2;
      min-height: 78px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }

    .flow-step span {
      font-size: 22px;
      margin-bottom: 6px;
    }

    .metric {
      min-height: 92px;
    }

    .metric strong {
      font-size: 21px;
    }

    .table-wrap table {
      min-width: 680px;
    }

    th, td {
      padding: 11px 12px;
      font-size: 13px;
      line-height: 1.45;
    }

    th {
      font-size: 12px;
      white-space: nowrap;
    }

    .pill {
      padding: 5px 9px;
      font-size: 11px;
    }

    textarea {
      min-height: 145px;
      font-size: 15px;
    }

    button {
      font-size: 15px;
      padding: 14px 16px;
    }

    .small-note {
      font-size: 12px;
      line-height: 1.55;
    }

    .warning-hero {
      padding: 22px;
      border-radius: 24px;
    }

    .warning-top {
      align-items: center;
      gap: 14px;
      margin-bottom: 14px;
    }

    .warning-title {
      font-size: clamp(25px, 2.5vw, 34px);
      line-height: 1.15;
      letter-spacing: -0.055em;
      flex-wrap: nowrap;
    }

    .warning-subtitle {
      margin: 8px 0 0 0;
      font-size: 14px;
      line-height: 1.45;
    }

    .score-badge {
      font-size: 15px;
      padding: 9px 13px;
    }

    .risk-meter {
      margin: 12px 0 16px;
      padding: 14px;
    }

    .meter-value {
      font-size: 20px;
    }

    .signal-grid {
      gap: 10px;
      margin: 14px 0;
    }

    .signal-card {
      padding: 14px 12px;
      min-width: 0;
    }

    .signal-card span {
      font-size: 12px;
      white-space: nowrap;
    }

    .signal-card strong {
      font-size: 27px;
      white-space: nowrap;
    }

    .signal-card em {
      font-size: 12px;
      white-space: nowrap;
    }

    .reason-table {
      margin: 14px 0;
    }

    .reason-table th,
    .reason-table td {
      font-size: 12px;
      padding: 10px 11px;
      line-height: 1.45;
    }

    .keyword-chip {
      white-space: nowrap;
      font-size: 12px;
    }

    .insight-box,
    .action-box {
      padding: 14px 15px;
      font-size: 13px;
      line-height: 1.65;
    }

    .formula {
      font-size: 13px;
      padding: 16px;
    }

    @media (max-width: 1080px) {
      .grid.two {
        grid-template-columns: 1fr;
      }

      .hero h1 {
        white-space: normal;
      }

      .flow-steps {
        grid-template-columns: repeat(5, minmax(68px, 1fr));
      }

      .mini-kpi-row {
        grid-template-columns: repeat(3, 1fr);
      }

      .warning-title {
        white-space: normal;
      }
    }

    @media (max-width: 640px) {
      .container {
        padding: 18px 14px 42px;
      }

      .hero {
        padding: 24px;
      }

      .flow-steps,
      .mini-kpi-row,
      .signal-grid {
        grid-template-columns: 1fr;
      }

      .warning-top {
        flex-direction: column;
        align-items: flex-start;
      }

      .score-badge {
        align-self: flex-start;
      }
    }

  </style>
</head>
<body>
  <main class="container">
    <section class="hero">
      <h1 class="hero-title"><span>🚨 불만 고객 조기 경보 모델</span><small>Early Warning System for Negative Feedback</small></h1>
      <p>
        리뷰 텍스트를 입력하면 감정 점수, 부정 키워드, 리뷰 길이를 바탕으로
        불만 고객 가능성을 Normal / Risk / Critical 단계로 판단하는 조기 경보 시뮬레이터입니다.
      </p>
    </section>

    <section class="section-title">
      <span class="badge">Dashboard</span>
      <h2>1. 조기 경보 모델 시각화</h2>
    </section>

    <section class="grid two">
      <div class="card">
        <h3>자동 추출 부정 키워드 TOP 15</h3>
        <p class="desc">
          TF-IDF 기반으로 저평점·부정 리뷰에서 주요 키워드를 자동 추출했습니다.
        </p>
        <canvas id="keywordChart"></canvas>

        <div class="insight-panel">
          <h4>📊 데이터 분석 인사이트</h4>
          <ul class="insight-list">
            <li><strong>bad</strong>, <strong>broken</strong>은 강한 불만을 직접적으로 나타내는 핵심 키워드입니다.</li>
            <li><strong>battery</strong>, <strong>charging</strong>은 제품 기능·성능 문제와 연결됩니다.</li>
            <li><strong>return</strong>, <strong>refund</strong>는 고객 대응 우선순위를 높이는 신호입니다.</li>
          </ul>
          <div class="mini-kpi-row">
            <div class="mini-kpi"><b>15</b><span>핵심 키워드</span></div>
            <div class="mini-kpi"><b>3단계</b><span>경보 분류</span></div>
            <div class="mini-kpi"><b>실시간</b><span>리뷰 판정</span></div>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>실제 조기 경보 리뷰 예시</h3>
        <p class="desc">
          높은 경보 점수를 받은 리뷰는 감정 점수가 낮거나, 부정 키워드가 많이 포함된 리뷰입니다.
        </p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>리뷰 내용</th>
                <th>별점</th>
                <th>감정 점수</th>
                <th>부정 키워드</th>
                <th>경보 단계</th>
              </tr>
            </thead>
            <tbody id="exampleTable"></tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="grid three" style="margin-top:18px;">
      <div class="metric">
        <span>분석 기준</span>
        <strong>감정 + 키워드 + 길이</strong>
      </div>
      <div class="metric">
        <span>Risk 기준</span>
        <strong>0.25 이상</strong>
      </div>
      <div class="metric">
        <span>Critical 기준</span>
        <strong>0.45 이상</strong>
      </div>
    </section>

    <section class="section-title">
      <span class="badge">Simulator</span>
      <h2>2. 리뷰 입력 시뮬레이터</h2>
    </section>

    <section class="grid two">
      <div class="card">
        <h3>리뷰 입력</h3>
        <p class="desc">아래에 리뷰를 입력하면 조기 경보 점수를 계산합니다.</p>
        <textarea id="reviewInput">The product stopped working after two days. Battery is terrible and I want a refund.</textarea>
        <div style="height:12px"></div>
        <button id="analyzeBtn">🚨 불만 고객 조기 경보 분석하기</button>
        <p class="small-note">
          ※ 이 HTML 버전은 발표용 시뮬레이터입니다. 감정 분석은 단어 기반 간이 규칙으로 구현했으며,
          Streamlit/Python 버전에서는 TextBlob 기반으로 확장할 수 있습니다.
        </p>

        <div class="process-flow">
          <h4>🔍 조기 경보 시스템 작동 방식</h4>
          <div class="flow-steps">
            <div class="flow-step"><span>✍️</span>리뷰 입력</div>
            <div class="flow-step"><span>😡</span>감정 분석</div>
            <div class="flow-step"><span>🔎</span>키워드탐지</div>
            <div class="flow-step"><span>📊</span>위험점수</div>
            <div class="flow-step"><span>🚨</span>경보판단</div>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>분석 결과</h3>

        <div id="resultBox" class="warning-hero normal">
          <div class="warning-top">
            <div>
              <h2 id="levelText" class="warning-title">✅ 정상 리뷰</h2>
              <p id="levelSubtitle" class="warning-subtitle">현재 기준으로는 불만 위험도가 낮습니다.</p>
            </div>
            <div id="scorePill" class="score-badge">score 0.000</div>
          </div>

          <div class="risk-meter">
            <div class="meter-row">
              <span class="meter-label">고객 불만 위험도</span>
              <span id="riskPercent" class="meter-value">0%</span>
            </div>
            <div class="meter-track">
              <div id="meterFill" class="meter-fill"></div>
            </div>
          </div>

          <div class="signal-grid">
            <div class="signal-card">
              <span>감정 점수</span>
              <strong id="sentimentMetric">0.000</strong>
              <em id="sentimentTag">중립</em>
            </div>
            <div class="signal-card">
              <span>부정 키워드 수</span>
              <strong id="keywordMetric">0</strong>
              <em id="keywordTag">낮음</em>
            </div>
            <div class="signal-card">
              <span>리뷰 길이</span>
              <strong id="lengthMetric">0</strong>
              <em id="lengthTag">짧음</em>
            </div>
          </div>

          <table class="reason-table">
            <thead>
              <tr>
                <th>감지 신호</th>
                <th>분석 결과</th>
                <th>위험 수준</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>😡 고객 감정</td>
                <td id="reasonSentiment">-</td>
                <td id="riskSentiment">-</td>
              </tr>
              <tr>
                <td>🚨 불만 키워드</td>
                <td id="reasonKeyword">-</td>
                <td id="riskKeyword">-</td>
              </tr>
              <tr>
                <td>📝 리뷰 길이</td>
                <td id="reasonLength">-</td>
                <td id="riskLength">-</td>
              </tr>
            </tbody>
          </table>

          <div>
            <strong>🔍 감지된 불만 표현</strong>
            <div class="keyword-list" id="matchedKeywords"></div>
          </div>

          <div id="insightBox" class="insight-box">
            리뷰를 입력하면 AI 분석 인사이트가 표시됩니다.
          </div>

          <div id="actionBox" class="action-box">
            <strong>권장 대응</strong><br/>
            분석 결과에 따라 고객 대응 우선순위를 제안합니다.
          </div>
        </div>
      </div>
    </section>

    <section class="grid two" style="margin-top:18px;">
      <div class="card">
        <h3>경보 점수 구성</h3>
        <p class="desc">입력 리뷰의 위험 점수가 어떤 요소에서 나왔는지 보여줍니다.</p>
        <canvas id="scoreChart"></canvas>
      </div>
      <div class="card">
        <h3>모델 계산식</h3>
        <div class="formula">
          Early Warning Score<br/>
          = 0.55 × negative_sentiment_strength<br/>
          + 0.30 × negative_keyword_score<br/>
          + 0.15 × review_length_norm
        </div>
        <p class="small-note">
          부정 감정이 강하고, 부정 키워드가 많고, 리뷰가 상세할수록 고객 불만 가능성이 높은 리뷰로 판단합니다.
        </p>
      </div>
    </section>
  </main>

  <script>
    const negativeKeywords = [
      "bad", "broken", "poor", "waste", "wasted", "disappointed", "damage",
      "defective", "issue", "problem", "refund", "return", "doesnt", "dont",
      "failed", "useless", "worst", "stopped", "slow", "hard", "cheap",
      "fake", "missing", "dead", "faulty", "terrible", "awful"
    ];

    const positiveWords = [
      "good", "great", "excellent", "love", "perfect", "nice", "best",
      "amazing", "satisfied", "recommend", "useful", "durable", "easy"
    ];

    const keywordData = [
      { keyword: "bad", score: 9.79 },
      { keyword: "broken", score: 8.46 },
      { keyword: "doesnt", score: 7.85 },
      { keyword: "battery", score: 6.84 },
      { keyword: "poor", score: 5.78 },
      { keyword: "issue", score: 4.21 },
      { keyword: "return", score: 3.89 },
      { keyword: "waste", score: 3.62 },
      { keyword: "disappointed", score: 3.41 },
      { keyword: "damage", score: 3.08 },
      { keyword: "refund", score: 2.87 },
      { keyword: "stopped", score: 2.65 },
      { keyword: "slow", score: 2.44 },
      { keyword: "defective", score: 2.12 },
      { keyword: "worst", score: 1.96 }
    ];

    const examples = [
      {
        review: "Battery died after 2 weeks. Doesn't charge at all and waste of money.",
        rating: "1.0",
        sentiment: "-0.84",
        keywords: "battery, doesnt, waste",
        level: "Critical"
      },
      {
        review: "This product is broken. It stopped working after a few days. Very poor quality.",
        rating: "2.0",
        sentiment: "-0.63",
        keywords: "broken, stopped, poor",
        level: "Critical"
      },
      {
        review: "Charging is too slow and often doesn't work properly.",
        rating: "2.5",
        sentiment: "-0.52",
        keywords: "slow, doesnt, work",
        level: "Risk"
      },
      {
        review: "Not as good as expected. The remote barely works from a distance.",
        rating: "3.0",
        sentiment: "-0.21",
        keywords: "not, works",
        level: "Risk"
      }
    ];

    let scoreChart;

    function countMatches(text) {
      const lower = text.toLowerCase();
      const matched = [];
      let count = 0;

      negativeKeywords.forEach(word => {
        const regex = new RegExp("\\b" + word.replace("'", "\\'") + "\\b", "g");
        const matches = lower.match(regex);
        if (matches) {
          count += matches.length;
          matched.push(word);
        }
      });

      return { count, matched: [...new Set(matched)] };
    }

    function sentimentScore(text) {
      const lower = text.toLowerCase();
      let neg = 0;
      let pos = 0;

      negativeKeywords.forEach(word => {
        if (lower.includes(word)) neg += 1;
      });
      positiveWords.forEach(word => {
        if (lower.includes(word)) pos += 1;
      });

      const raw = (pos - neg) / Math.max(pos + neg, 1);
      return Math.max(-1, Math.min(1, raw));
    }

    function analyzeReview() {
      const text = document.getElementById("reviewInput").value.trim();
      const words = text ? text.split(/\s+/).length : 0;
      const sent = sentimentScore(text);
      const negativeSentimentStrength = sent < 0 ? Math.abs(sent) : 0;
      const { count, matched } = countMatches(text);

      const keywordScore = Math.min(count / 10, 1);
      const lengthNorm = Math.min(words / 120, 1);

      const score =
        negativeSentimentStrength * 0.55 +
        keywordScore * 0.30 +
        lengthNorm * 0.15;

      let level = "Normal";
      if (score >= 0.45) level = "Critical";
      else if (score >= 0.25) level = "Risk";

      renderResult(level, score, sent, count, words, matched);
      renderScoreChart([
        negativeSentimentStrength * 0.55,
        keywordScore * 0.30,
        lengthNorm * 0.15
      ]);
    }

    function renderResult(level, score, sent, count, words, matched) {
      const box = document.getElementById("resultBox");
      const levelText = document.getElementById("levelText");
      const subtitle = document.getElementById("levelSubtitle");
      const pill = document.getElementById("scorePill");

      const levelLower = level.toLowerCase();
      box.className = "warning-hero " + levelLower;

      const riskPercent = Math.min(Math.round((score / 0.70) * 100), 100);

      if (level === "Critical") {
        levelText.textContent = "🚨 불만 고객 경보";
        subtitle.textContent = "즉각적인 확인이 필요한 고위험 리뷰입니다.";
      } else if (level === "Risk") {
        levelText.textContent = "⚠️ 불만 가능성 감지";
        subtitle.textContent = "모니터링이 필요한 주의 리뷰입니다.";
      } else {
        levelText.textContent = "✅ 정상 리뷰";
        subtitle.textContent = "현재 기준으로는 불만 위험도가 낮습니다.";
      }

      pill.className = "score-badge";
      pill.textContent = "score " + score.toFixed(3);

      document.getElementById("riskPercent").textContent = riskPercent + "%";
      document.getElementById("meterFill").style.width = riskPercent + "%";

      document.getElementById("sentimentMetric").textContent = sent.toFixed(3);
      document.getElementById("keywordMetric").textContent = count;
      document.getElementById("lengthMetric").textContent = words;

      const sentimentTag =
        sent <= -0.6 ? "매우 부정" :
        sent < -0.2 ? "부정" :
        sent < 0.2 ? "중립" : "긍정";

      const keywordTag =
        count >= 3 ? "높음" :
        count >= 1 ? "보통" : "낮음";

      const lengthTag =
        words >= 50 ? "상세" :
        words >= 20 ? "보통" : "짧음";

      document.getElementById("sentimentTag").textContent = sentimentTag;
      document.getElementById("keywordTag").textContent = keywordTag;
      document.getElementById("lengthTag").textContent = lengthTag;

      document.getElementById("reasonSentiment").textContent =
        sent < 0 ? `부정 감정 ${sent.toFixed(3)} 감지` : `부정 감정 낮음 (${sent.toFixed(3)})`;

      document.getElementById("reasonKeyword").textContent =
        count > 0 ? `${count}개의 불만 키워드 감지` : "불만 키워드 없음";

      document.getElementById("reasonLength").textContent =
        `${words}단어로 작성됨`;

      document.getElementById("riskSentiment").textContent =
        sent <= -0.6 ? "🔴 위험" :
        sent < -0.2 ? "🟠 주의" : "🟢 낮음";

      document.getElementById("riskKeyword").textContent =
        count >= 3 ? "🔴 위험" :
        count >= 1 ? "🟠 주의" : "🟢 낮음";

      document.getElementById("riskLength").textContent =
        words >= 50 ? "🟠 상세 불만 가능" :
        words >= 20 ? "🟡 보통" : "🟢 짧음";

      const keywordBox = document.getElementById("matchedKeywords");
      keywordBox.innerHTML = "";

      if (matched.length === 0) {
        const chip = document.createElement("span");
        chip.className = "keyword-chip";
        chip.textContent = "탐지된 부정 키워드 없음";
        keywordBox.appendChild(chip);
      } else {
        matched.forEach(word => {
          const chip = document.createElement("span");
          chip.className = "keyword-chip";
          chip.textContent = word;
          keywordBox.appendChild(chip);
        });
      }

      const insight = document.getElementById("insightBox");
      const action = document.getElementById("actionBox");

      if (level === "Critical") {
        insight.innerHTML = `💡 <strong>AI 분석 인사이트</strong><br/>
          리뷰에서 <strong>${matched.slice(0, 3).join(", ") || "강한 부정 표현"}</strong>이 감지되었고,
          감정 점수도 부정적으로 나타났습니다. 제품 결함, 환불 요청, 작동 불량 가능성이 있는 리뷰로 해석할 수 있습니다.`;
        action.innerHTML = `<strong>⚡ 권장 대응</strong><br/>
          고객 문의를 우선 확인하고, 환불/교환 요청 또는 제품 결함 여부를 빠르게 점검하는 것이 좋습니다.`;
      } else if (level === "Risk") {
        insight.innerHTML = `💡 <strong>AI 분석 인사이트</strong><br/>
          일부 부정 표현이 포함되어 있어 불만 가능성이 있습니다. 아직 심각한 수준은 아니지만 반복 발생 시 제품 개선 신호로 볼 수 있습니다.`;
        action.innerHTML = `<strong>⚡ 권장 대응</strong><br/>
          동일 상품군에서 유사 키워드가 반복되는지 모니터링하고, 필요 시 고객 응대를 준비하는 것이 좋습니다.`;
      } else {
        insight.innerHTML = `💡 <strong>AI 분석 인사이트</strong><br/>
          강한 부정 감정이나 핵심 불만 키워드가 크게 나타나지 않았습니다. 현재 기준에서는 일반 리뷰로 분류됩니다.`;
        action.innerHTML = `<strong>⚡ 권장 대응</strong><br/>
          즉각적인 대응보다는 일반 리뷰 데이터로 누적하여 상품 만족도 분석에 활용할 수 있습니다.`;
      }
    }

    function renderKeywordChart() {
      const ctx = document.getElementById("keywordChart");
      new Chart(ctx, {
        type: "bar",
        data: {
          labels: keywordData.map(d => d.keyword),
          datasets: [{
            label: "TF-IDF Score",
            data: keywordData.map(d => d.score),
            borderRadius: 8,
            backgroundColor: "#2563eb"
          }]
        },
        options: {
          indexAxis: "y",
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: { callbacks: { label: ctx => "score " + ctx.raw } }
          },
          scales: {
            x: { grid: { color: "#e5e7eb" } },
            y: { grid: { display: false } }
          }
        }
      });
    }

    function renderExampleTable() {
      const tbody = document.getElementById("exampleTable");
      examples.forEach(row => {
        const tr = document.createElement("tr");
        const levelClass = row.level.toLowerCase();
        tr.innerHTML = `
          <td>${row.review}</td>
          <td>${row.rating}</td>
          <td>${row.sentiment}</td>
          <td>${row.keywords}</td>
          <td><span class="pill ${levelClass}">${row.level}</span></td>
        `;
        tbody.appendChild(tr);
      });
    }

    function renderScoreChart(values) {
      const ctx = document.getElementById("scoreChart");

      if (scoreChart) scoreChart.destroy();

      scoreChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["부정 감정", "부정 키워드", "리뷰 길이"],
          datasets: [{
            label: "Score contribution",
            data: values,
            borderRadius: 10,
            backgroundColor: ["#dc2626", "#f97316", "#2563eb"]
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, max: 0.6, grid: { color: "#e5e7eb" } },
            x: { grid: { display: false } }
          }
        }
      });
    }

    document.getElementById("analyzeBtn").addEventListener("click", analyzeReview);

    renderKeywordChart();
    renderExampleTable();
    analyzeReview();
  </script>
</body>
</html>
