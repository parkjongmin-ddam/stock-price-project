import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. 페이지 설정 (Page Configuration)
# ==========================================
st.set_page_config(
    page_title="주가 차트 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto"
)

# ==========================================
# 4. 앱 메인 로직 - 테마 설정 (Theme Config)
# ==========================================
st.sidebar.title("🚀 주가 차트 대시보드")
st.sidebar.markdown("---")

# 테마 선택 (다크/라이트 모드)
theme_mode = st.sidebar.radio("화면 모드 (Theme)", ["Dark Mode", "Light Mode"], index=0)
is_dark = (theme_mode == "Dark Mode")
plotly_template = "plotly_dark" if is_dark else "plotly_white"

# 커스텀 CSS (테마별 스타일링)
if is_dark:
    css = """
    <style>
        /* 전체 배경 및 폰트 */
        .stApp { 
            background-color: #0e1117; 
            color: #ffffff; 
        }
        
        /* 사이드바 배경 및 텍스트 */
        section[data-testid="stSidebar"] { 
            background-color: #262730; 
        }
        
        /* 사이드바 제목과 라벨 */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: #ffffff !important;
        }
        
        /* 사이드바 라디오 버튼 텍스트 */
        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            color: #ffffff !important;
        }

        /* 헤더 배경 */
        header[data-testid="stHeader"] { 
            background-color: #0e1117; 
        }

        /* 제목 텍스트 */
        h1, h2, h3, h4, h5, h6 { 
            color: #ffffff !important; 
        }

        /* Metric 위젯 */
        [data-testid="stMetricValue"] { 
            color: #00e676 !important; 
            font-weight: 700 !important; 
        }
        [data-testid="stMetricLabel"] { 
            color: #e0e0e0 !important; 
        }

        /* 사이드바 접기 버튼 완전히 숨기기 */
        [data-testid="stSidebarCollapsedControl"] { 
            display: none !important; 
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        
        button[kind="header"] {
            display: none !important;
        }

        /* Deploy 버튼과 Toolbar 숨기기 */
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { visibility: hidden !important; }
        
        /* Expander 스타일 (다크 모드) */
        .streamlit-expanderHeader {
            background-color: #262730 !important;
            color: #ffffff !important;
            border: 1px solid #37474f !important;
            border-radius: 5px !important;
        }
        
        .streamlit-expanderContent {
            background-color: #1e1e1e !important;
            border: 1px solid #37474f !important;
            border-top: none !important;
            color: #cfd8dc !important;
        }
        
        /* Expander 아이콘 및 헤더 */
        [data-testid="stExpander"] summary {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        
        [data-testid="stExpander"] {
            background-color: transparent !important;
        }
        
        [data-testid="stExpander"] div[role="button"] {
            background-color: #262730 !important;
        }
    </style>
    """
else:
    css = """
    <style>
        /* 전체 배경 및 폰트 */
        .stApp { 
            background-color: #ffffff; 
            color: #333333; 
        }
        
        /* 사이드바 배경 및 텍스트 */
        section[data-testid="stSidebar"] { 
            background-color: #f8f9fa; 
            border-right: 1px solid #e0e0e0;
        }

        /* 사이드바 제목과 라벨 */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: #31333F !important;
        }
        
        /* 사이드바 라디오 버튼 텍스트 */
        section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            color: #31333F !important;
        }

        /* 헤더 배경 */
        header[data-testid="stHeader"] { 
            background-color: #ffffff; 
        }

        /* 제목 텍스트 */
        h1, h2, h3, h4, h5, h6 { 
            color: #111111 !important; 
        }
        
        /* Metric 위젯 */
        [data-testid="stMetricValue"] { 
            color: #111111 !important; 
        }
        [data-testid="stMetricLabel"] { 
            color: #666666 !important; 
        }

        /* 사이드바 접기 버튼 완전히 숨기기 */
        [data-testid="stSidebarCollapsedControl"] { 
            display: none !important; 
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        
        button[kind="header"] {
            display: none !important;
        }
        
        /* Deploy 버튼과 Toolbar 숨기기 */
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { visibility: hidden !important; }
        
        /* Expander 스타일 (라이트 모드) */
        .streamlit-expanderHeader {
            background-color: #f8f9fa !important;
            color: #31333F !important;
            border: 1px solid #e0e0e0 !important;
            border-radius: 5px !important;
        }
        
        .streamlit-expanderContent {
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
            border-top: none !important;
            color: #424242 !important;
        }
        
        /* Expander 아이콘 및 헤더 */
        [data-testid="stExpander"] summary {
            background-color: #f8f9fa !important;
            color: #31333F !important;
        }
        
        [data-testid="stExpander"] {
            background-color: transparent !important;
        }
        
        [data-testid="stExpander"] div[role="button"] {
            background-color: #f8f9fa !important;
        }
    </style>
    """
st.markdown(css, unsafe_allow_html=True)


# ==========================================
# 2. 데이터 로드 및 캐싱 (Data Loading)
# ==========================================
@st.cache_data
def get_stock_data(ticker, start="2025-01-01", end="2025-12-31"):
    try:
        df = fdr.DataReader(ticker, start, end)
        return df
    except Exception as e:
        st.error(f"데이터 수집 중 오류 발생: {e}")
        return pd.DataFrame()

# ==========================================
# 3. 차트 생성 함수들 (Chart Generators)
# ==========================================

def calculate_stats(df):
    """통계 지표 계산 헬퍼 함수"""
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    ret = ((end_price - start_price) / start_price) * 100
    
    cummax = df['Close'].expanding().max()
    drawdown = ((df['Close'] - cummax) / cummax) * 100
    mdd = drawdown.min()
    
    return start_price, end_price, ret, drawdown, mdd

def plot_standard_dashboard(df, name, ticker, template):
    """
    기본형 대시보드 (Standard Dashboard)
    캔들스틱, 이동평균선, 거래량, Drawdown 분석 제공
    """
    # -------------------------------------------------------------------------
    # 1. 지표 계산 (Indicator Calculation)
    # -------------------------------------------------------------------------
    # 이동평균선 (Moving Averages: Short/Mid/Long)
    df['MA5'] = df['Close'].rolling(window=5).mean()    # 단기 (5일)
    df['MA20'] = df['Close'].rolling(window=20).mean()  # 중기 (20일)
    df['MA60'] = df['Close'].rolling(window=60).mean()  # 장기 (60일)
    
    # 거래량 색상 (양봉: 빨강, 음봉: 파랑)
    colors = ['#ff5252' if c >= o else '#448aff' for c, o in zip(df['Close'], df['Open'])]

    # -------------------------------------------------------------------------
    # 2. 통계 지표 계산 (Statistical Metrics)
    # -------------------------------------------------------------------------
    start_price, end_price, ret, drawdown, mdd = calculate_stats(df)

    # -------------------------------------------------------------------------
    # 3. 차트 레이아웃 구성 (Chart Layout)
    # -------------------------------------------------------------------------
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05,
        subplot_titles=(
            f'{name} ({ticker}) Price', 
            'Volume', 
            'Drawdown (Risk Analysis)', 
            'Summary Statistics'
        ),
        row_heights=[0.5, 0.15, 0.15, 0.2],
        specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "xy"}], [{"type": "table"}]]
    )

    # -------------------------------------------------------------------------
    # 4. Row 1: 가격 차트 (Price Chart)
    # -------------------------------------------------------------------------
    # 캔들스틱 차트
    fig.add_trace(go.Candlestick(
        x=df.index, 
        open=df['Open'], 
        high=df['High'], 
        low=df['Low'], 
        close=df['Close'],
        name='Price', 
        increasing_line_color='#ff5252',  # 양봉: 빨강
        decreasing_line_color='#448aff'   # 음봉: 파랑
    ), row=1, col=1)

    # 이동평균선 추가
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA5'], 
        line=dict(color='#ffeb3b', width=1), 
        name='MA 5'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA20'], 
        line=dict(color='#00e676', width=1), 
        name='MA 20'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA60'], 
        line=dict(color='#e040fb', width=1), 
        name='MA 60'
    ), row=1, col=1)

    # -------------------------------------------------------------------------
    # 5. Row 2: 거래량 (Volume)
    # -------------------------------------------------------------------------
    fig.add_trace(go.Bar(
        x=df.index, 
        y=df['Volume'], 
        marker_color=colors, 
        name='Volume'
    ), row=2, col=1)

    # -------------------------------------------------------------------------
    # 6. Row 3: Drawdown (낙폭 분석)
    # -------------------------------------------------------------------------
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=drawdown, 
        fill='tozeroy', 
        line=dict(color='#ef5350'), 
        name='Drawdown'
    ), row=3, col=1)

    # -------------------------------------------------------------------------
    # 7. Row 4: 통계 테이블 (Summary Table)
    # -------------------------------------------------------------------------
    # 테마별 색상 설정
    header_color = '#263238' if template == 'plotly_dark' else '#B0BEC5'
    cell_color = '#37474f' if template == 'plotly_dark' else '#ECEFF1'
    font_color = 'white' if template == 'plotly_dark' else 'black'
    
    fig.add_trace(go.Table(
        header=dict(
            values=["Metric", "Value"], 
            fill_color=header_color, 
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[
                ['Start Price', 'End Price', 'Return', 'MDD (Max Loss)', 'Total Days'],
                [f"{start_price:,.0f}", f"{end_price:,.0f}", f"{ret:+.2f}%", f"{mdd:.2f}%", len(df)]
            ],
            fill_color=cell_color, 
            font=dict(color=font_color), 
            align='left'
        )
    ), row=4, col=1)

    # -------------------------------------------------------------------------
    # 8. 레이아웃 최종 설정 (Final Layout Configuration)
    # -------------------------------------------------------------------------
    fig.update_layout(
        title=dict(text=f'<b>{name} Dashboard</b>', x=0.5, font=dict(size=24)),
        template=template,
        height=1000, 
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # 그리드 색상 설정
    grid_color = 'rgba(128, 128, 128, 0.2)'
    fig.update_xaxes(gridcolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color, tickformat=',')
    
    return fig

def plot_kakao_dashboard(df, name="Kakao", template="plotly_dark"):
    """
    카카오 스타일 대시보드 (Kakao Advanced Dashboard)
    볼린저밴드, 거래량 급증 시그널, Drawdown 분석 제공
    """
    # -------------------------------------------------------------------------
    # 1. 지표 계산 (Indicator Calculation)
    # -------------------------------------------------------------------------
    # 이동평균선 (Moving Averages)
    df["MA20"] = df["Close"].rolling(window=20).mean()  # 중기 (20일)
    df["MA60"] = df["Close"].rolling(window=60).mean()  # 장기 (60일)
    
    # 볼린저밴드 (Bollinger Bands: 20일, ±2 표준편차)
    bb_std = df["Close"].rolling(window=20).std()
    df["BB_UPPER"] = df["MA20"].add(bb_std.mul(2))  # 상단 밴드
    df["BB_LOWER"] = df["MA20"].sub(bb_std.mul(2))  # 하단 밴드
    
    # 일간 수익률 (Daily Return)
    df["Return"] = df["Close"].pct_change()
    
    # -------------------------------------------------------------------------
    # 2. 시그널 감지 (Signal Detection)
    # -------------------------------------------------------------------------
    # 거래량 및 수익률 임계값 계산
    try:
        valid = df[["Return", "Volume"]].dropna()
        if not valid.empty:
            ret_up = np.percentile(valid["Return"], 90)      # 상위 10% 수익률
            ret_down = np.percentile(valid["Return"], 10)    # 하위 10% 수익률
            vol_th = np.percentile(valid["Volume"], 90)      # 상위 10% 거래량
            
            # 급등/급락 시그널 (거래량 급증 + 가격 변동)
            df["LargeUp"] = (df["Return"] >= ret_up) & (df["Volume"] >= vol_th)
            df["LargeDown"] = (df["Return"] <= ret_down) & (df["Volume"] >= vol_th)
        else:
            df["LargeUp"] = False
            df["LargeDown"] = False
    except:
        df["LargeUp"] = False
        df["LargeDown"] = False

    # -------------------------------------------------------------------------
    # 3. 통계 지표 계산 (Statistical Metrics)
    # -------------------------------------------------------------------------
    start_price, end_price, ret, drawdown, mdd = calculate_stats(df)

    # -------------------------------------------------------------------------
    # 4. 차트 레이아웃 구성 (Chart Layout)
    # -------------------------------------------------------------------------
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05, 
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=(
            f'{name} Price & BB', 
            'Volume', 
            'Drawdown (Risk Analysis)', 
            'Summary Statistics'
        ),
        specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "xy"}], [{"type": "table"}]]
    )

    # -------------------------------------------------------------------------
    # 5. Row 1: 가격 차트 + 볼린저밴드 (Price Chart + Bollinger Bands)
    # -------------------------------------------------------------------------
    # 캔들스틱 차트
    fig.add_trace(go.Candlestick(
        x=df.index, 
        open=df["Open"], 
        high=df["High"], 
        low=df["Low"], 
        close=df["Close"],
        name="Price", 
        increasing_line_color="#00B0F6",  # 양봉: 하늘색
        decreasing_line_color="#F63538"   # 음봉: 빨강
    ), row=1, col=1)
    
    # 볼린저밴드 상단
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df["BB_UPPER"], 
        line=dict(color="rgba(135, 206, 250, 0.5)", width=1), 
        name="BB Upper"
    ), row=1, col=1)
    
    # 볼린저밴드 하단 (채우기 효과)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df["BB_LOWER"], 
        line=dict(color="rgba(135, 206, 250, 0.5)", width=1), 
        fill='tonexty', 
        fillcolor="rgba(135, 206, 250, 0.1)", 
        name="BB Lower"
    ), row=1, col=1)

    # -------------------------------------------------------------------------
    # 6. 시그널 마커 (Signal Markers)
    # -------------------------------------------------------------------------
    # 급등 시그널 (Large Up)
    if df["LargeUp"].any():
        fig.add_trace(go.Scatter(
            x=df.index[df["LargeUp"]], 
            y=df["Close"][df["LargeUp"]], 
            mode="markers", 
            marker=dict(symbol="triangle-up", size=10, color="#00FF7F"), 
            name="Large Up"
        ), row=1, col=1)
    
    # 급락 시그널 (Large Down)
    if df["LargeDown"].any():
        fig.add_trace(go.Scatter(
            x=df.index[df["LargeDown"]], 
            y=df["Close"][df["LargeDown"]], 
            mode="markers", 
            marker=dict(symbol="triangle-down", size=10, color="#FF4500"), 
            name="Large Down"
        ), row=1, col=1)

    # -------------------------------------------------------------------------
    # 7. Row 2: 거래량 (Volume)
    # -------------------------------------------------------------------------
    # 거래량 색상 (양봉: 하늘색, 음봉: 빨강)
    colors = np.where(df["Close"] >= df["Open"], '#00B0F6', '#F63538')
    fig.add_trace(go.Bar(
        x=df.index, 
        y=df["Volume"], 
        marker_color=colors, 
        name="Volume"
    ), row=2, col=1)

    # -------------------------------------------------------------------------
    # 8. Row 3: Drawdown (낙폭 분석)
    # -------------------------------------------------------------------------
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=drawdown, 
        fill='tozeroy', 
        line=dict(color='#ef5350'), 
        name='Drawdown'
    ), row=3, col=1)

    # -------------------------------------------------------------------------
    # 9. Row 4: 통계 테이블 (Summary Table)
    # -------------------------------------------------------------------------
    # 테마별 색상 설정
    header_color = '#263238' if template == 'plotly_dark' else '#B0BEC5'
    cell_color = '#37474f' if template == 'plotly_dark' else '#ECEFF1'
    font_color = 'white' if template == 'plotly_dark' else 'black'

    fig.add_trace(go.Table(
        header=dict(
            values=["Metric", "Value"], 
            fill_color=header_color, 
            font=dict(color='white')
        ),
        cells=dict(
            values=[
                ['Start Price', 'End Price', 'Return', 'MDD', 'Total Days'],
                [f"{start_price:,.0f}", f"{end_price:,.0f}", f"{ret:+.2f}%", f"{mdd:.2f}%", len(df)]
            ],
            fill_color=cell_color, 
            font=dict(color=font_color), 
            align='left'
        )
    ), row=4, col=1)

    # -------------------------------------------------------------------------
    # 10. 레이아웃 최종 설정 (Final Layout Configuration)
    # -------------------------------------------------------------------------
    fig.update_layout(
        title=f"<b>{name} Advanced Dashboard</b>", 
        template=template, 
        height=1000, 
        xaxis_rangeslider_visible=False
    )
    
    # 그리드 색상 설정
    grid_color = 'rgba(128, 128, 128, 0.2)'
    fig.update_xaxes(gridcolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color)
    
    return fig


def plot_saltlux_report(df, name="Stock", template="plotly_white"):
    """
    종합 분석 리포트 대시보드 (Comprehensive Analysis Report)
    모든 종목에 적용 가능한 상세 분석 리포트
    - KPI 지표, 주가 흐름, 월별 분석, 거래 패턴, 리스크 분석, 통계 요약
    """
    # 전처리 및 지표 계산
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    year_return = ((end_price - start_price) / start_price) * 100
    high_price = df['High'].max()
    low_price = df['Low'].min()

    # 파생 변수 생성
    df['Daily_Return'] = df['Close'].pct_change() * 100
    df['Cumulative_Return'] = ((df['Close'] / start_price) - 1) * 100
    df['Trade_Value'] = df['Volume'] * df['Close']

    # 이동평균선
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()

    # 볼린저밴드
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)

    # 변동성 및 리스크 지표
    daily_volatility = df['Daily_Return'].std()
    annual_volatility = daily_volatility * (252 ** 0.5)
    df['Rolling_Volatility'] = df['Daily_Return'].rolling(window=20).std()

    # MDD 계산
    df['Cummax'] = df['Close'].expanding().max()
    df['Drawdown'] = ((df['Close'] - df['Cummax']) / df['Cummax']) * 100
    mdd = df['Drawdown'].min()

    # 월별 데이터 집계
    df['Month'] = df.index.month
    monthly_data = df.groupby('Month').agg({'Close': ['first', 'last']})
    monthly_data.columns = ['First', 'Last']
    monthly_data['Return'] = ((monthly_data['Last'] - monthly_data['First']) / monthly_data['First']) * 100
    monthly_trade = df.groupby('Month')['Trade_Value'].mean()

    # 거래 패턴 분석
    df['Price_Change'] = df['Close'] - df['Open']
    df['Is_Up'] = df['Price_Change'] > 0
    avg_volume = df['Volume'].mean()
    volume_std = df['Volume'].std()
    df['Volume_Spike'] = df['Volume'] > (avg_volume + 2 * volume_std)

    # 통계 요약
    total_days = len(df)
    up_days = df['Is_Up'].sum()
    down_days = total_days - up_days
    win_rate = (up_days / total_days) * 100 if total_days > 0 else 0
    avg_gain = df[df['Daily_Return'] > 0]['Daily_Return'].mean()
    avg_loss = df[df['Daily_Return'] < 0]['Daily_Return'].abs().mean()
    profit_loss_ratio = avg_gain / avg_loss if avg_loss > 0 else 0
    sharpe_ratio = (year_return - 3) / annual_volatility if annual_volatility > 0 else 0

    # 레이아웃 구성
    fig = make_subplots(
        rows=7, cols=6,
        specs=[
            [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'},
             {'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
            [{'colspan': 6, 'type': 'xy'}, None, None, None, None, None],
            [None, None, None, None, None, None],
            [{'colspan': 3, 'type': 'xy'}, None, None,
             {'colspan': 3, 'type': 'xy'}, None, None],
            [{'colspan': 2, 'type': 'xy'}, None, {'colspan': 2, 'type': 'xy'},
             None, {'colspan': 2, 'type': 'xy'}, None],
            [{'colspan': 3, 'type': 'xy'}, None, None,
             {'colspan': 3, 'type': 'xy'}, None, None],
            [{'colspan': 6, 'type': 'table'}, None, None, None, None, None]
        ],
        vertical_spacing=0.02,
        horizontal_spacing=0.03,
        subplot_titles=(
            None, None, None, None, None, None,
            "Price Flow & Trend (주가 흐름)",
            "Monthly Returns (월별 수익률)", "Monthly Trade Value (월별 거래대금)",
            "Trade Patterns (거래 패턴)", "Rolling Volatility (20일 변동성)",
            "Return Distribution (수익률 분포)",
            "Drawdown Risk (최대 낙폭)", "Cumulative Return (누적 수익률)",
            "Statistical Summary (통계 요약)"
        ),
        row_heights=[0.05, 0.21, 0.03, 0.175, 0.175, 0.175, 0.185]
    )

    # Row 1: KPI Indicators
    indicators = [
        ("연초가", start_price, "number", ""),
        ("연말가", end_price, "number", ""),
        ("수익률", year_return, "number+delta", "%"),
        ("최고가", high_price, "number", ""),
        ("최저가", low_price, "number", ""),
        ("MDD", mdd, "number", "%"),
    ]

    for i, (title, val, mode, suffix) in enumerate(indicators):
        fig.add_trace(go.Indicator(
            mode=mode, value=val,
            title={'text': title, 'font': {'size': 14, 'color': 'gray'}},
            number={'suffix': suffix, 'font': {'size': 24}},
            delta={'reference': 0} if "delta" in mode else None
        ), row=1, col=i+1)

    # Row 2: Main Chart
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price', increasing_line_color='#26A69A', decreasing_line_color='#EF5350'
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines', line=dict(color='#26A69A', width=2),
        name='Close Line', visible=False
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_Upper'],
        line=dict(color='gray', width=1, dash='dot'),
        name='BB Upper', showlegend=True
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['BB_Lower'],
        line=dict(color='gray', width=1, dash='dot'),
        name='BB Lower', fill='tonexty', fillcolor='rgba(200,200,200,0.1)', showlegend=True
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA20'],
        line=dict(color='#2962FF', width=1.5), name='MA20'
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA60'],
        line=dict(color='#FF6D00', width=1.5), name='MA60'
    ), row=2, col=1)

    # Row 4: Monthly Analysis
    months = list(range(1, 13))
    mon_ret = monthly_data['Return'].reindex(months, fill_value=0)
    mon_trade = monthly_trade.reindex(months, fill_value=0)

    colors_ret = ['#26A69A' if x > 0 else '#EF5350' for x in mon_ret]
    fig.add_trace(go.Bar(
        x=months, y=mon_ret, marker_color=colors_ret,
        name='Monthly Ret', showlegend=False
    ), row=4, col=1)

    fig.add_trace(go.Bar(
        x=months, y=mon_trade, marker_color='#5C6BC0',
        name='Avg Trade', showlegend=False
    ), row=4, col=4)

    # Row 5: Pattern & Volatility
    colors_vol = ['#26A69A' if up else '#EF5350' for up in df['Is_Up']]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Trade_Value'], marker_color=colors_vol,
        name='Trade Val', showlegend=False
    ), row=5, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['Rolling_Volatility'],
        line=dict(color='#AB47BC', width=1.5),
        name='Vol(20d)', showlegend=False
    ), row=5, col=3)

    fig.add_trace(go.Histogram(
        x=df['Daily_Return'], marker_color='#7E57C2', nbinsx=40,
        name='Dist', showlegend=False
    ), row=5, col=5)

    # Row 6: Risk & Cumulative
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Drawdown'], fill='tozeroy',
        line=dict(color='#C62828', width=1),
        name='DD', showlegend=False
    ), row=6, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df['Cumulative_Return'], fill='tozeroy',
        line=dict(color='#1565C0', width=2),
        name='Cum Ret', showlegend=False
    ), row=6, col=4)

    # Row 7: Table
    stats_data = [
        ['Total Days', 'Up Days (Win Rate)', 'Down Days', 'Avg Gain', 'Avg Loss',
         'P/L Ratio', 'Ann Volatility', 'Sharpe Ratio', 'Ann Return', 'Max Drawdown'],
        [f"{total_days}", f"{up_days} ({win_rate:.1f}%)", f"{down_days}",
         f"+{avg_gain:.2f}%", f"-{avg_loss:.2f}%", f"{profit_loss_ratio:.2f}",
         f"{annual_volatility:.1f}%", f"{sharpe_ratio:.2f}",
         f"{year_return:.1f}%", f"{mdd:.1f}%"]
    ]

    fig.add_trace(go.Table(
        header=dict(values=["Metric", "Value"], fill_color='#455A64',
                    font=dict(color='white', size=12), align='left'),
        cells=dict(values=stats_data, fill_color='#F5F5F5', align='left', height=30)
    ), row=7, col=1)

    # 최종 레이아웃
    fig.update_layout(
        title_text=f"<b>{name} 2025 Annual Analysis Report</b>",
        title_x=0.5,
        height=2200,
        template=template,
        margin=dict(l=40, r=40, t=120, b=40),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.90,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(255, 255, 255, 0.5)"
        ),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                active=0,
                x=0.01, y=0.92,
                buttons=list([
                    dict(label="Candle",
                         method="update",
                         args=[{"visible": [True]*6 + [True, False] + [True]*30}]),
                    dict(label="Line",
                         method="update",
                         args=[{"visible": [True]*6 + [False, True] + [True]*30}])
                ]),
            ),
            dict(
                type="buttons",
                direction="left",
                showactive=True,
                x=0.12, y=0.92,
                buttons=list([
                    dict(label="BB On",
                         method="restyle",
                         args=["visible", True, [8, 9]]),
                    dict(label="BB Off",
                         method="restyle",
                         args=["visible", False, [8, 9]])
                ]),
            )
        ]
    )

    fig.update_xaxes(rangeslider_visible=False)
    fig.update_xaxes(
        rangeslider=dict(visible=True, thickness=0.03),
        row=2, col=1
    )

    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='#ECEFF1',
        showspikes=True, spikemode='across', spikesnap='cursor', showline=True, spikedash='dash'
    )
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='#ECEFF1',
        showspikes=True, spikemode='across', spikesnap='cursor', showline=True, spikedash='dash'
    )

    return fig


def plot_mind_dashboard(df, name="Mind AI", template="plotly_dark"):
    """
    마음AI (구 마인즈랩) 트레이딩 차트 (Mind AI Trading Dashboard)
    수급 포착 중심 - 거래량 급증 + 급등/급락 시그널 감지
    """
    # -------------------------------------------------------------------------
    # 1. 지표 계산 (Indicator Calculation)
    # -------------------------------------------------------------------------
    # 이동평균선 (Moving Averages: Short/Mid/Long)
    df['MA20'] = df['Close'].rolling(window=20).mean()    # 생명선 (20일)
    df['MA60'] = df['Close'].rolling(window=60).mean()    # 수급선 (60일)
    df['MA120'] = df['Close'].rolling(window=120).mean()  # 경기선 (120일)
    
    # 볼린저밴드 (Bollinger Bands: 20일, ±2 표준편차)
    df['BB_Mid'] = df['MA20']
    std = df['Close'].rolling(window=20).std()
    df['BB_Up'] = df['BB_Mid'].add(std.mul(2))    # 상단 밴드
    df['BB_Down'] = df['BB_Mid'].sub(std.mul(2))  # 하단 밴드
    
    # 등락률 (Price Change Percentage)
    df['Pct_Chg'] = df['Close'].pct_change().mul(100)  # 일간 등락률 (%)
    
    # -------------------------------------------------------------------------
    # 2. 수급 포착 로직 (Supply-Demand Signal Detection)
    # -------------------------------------------------------------------------
    # 임계값 설정 (상위/하위 10% 기준)
    vol_cond = df['Volume'].quantile(0.9)      # 거래량 상위 10%
    up_cond = df['Pct_Chg'].quantile(0.9)      # 상승폭 상위 10%
    down_cond = df['Pct_Chg'].quantile(0.1)    # 하락폭 하위 10%
    
    # 시그널 생성 (거래량 터지면서 급등/급락한 날)
    df['Signal_Buy'] = (df['Volume'] >= vol_cond) & (df['Pct_Chg'] >= up_cond)    # 매수 시그널
    df['Signal_Sell'] = (df['Volume'] >= vol_cond) & (df['Pct_Chg'] <= down_cond)  # 매도 시그널
    
    # -------------------------------------------------------------------------
    # 3. 통계 지표 계산 (Statistical Metrics)
    # -------------------------------------------------------------------------
    start_price, end_price, ret, drawdown, mdd = calculate_stats(df)
    
    # -------------------------------------------------------------------------
    # 4. 차트 레이아웃 구성 (Chart Layout)
    # -------------------------------------------------------------------------
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=(
            f'{name} Price & Signals', 
            'Volume (Signal Detection)', 
            'Drawdown (Risk Analysis)', 
            'Summary Statistics'
        ),
        specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "xy"}], [{"type": "table"}]]
    )
    
    # -------------------------------------------------------------------------
    # 5. Row 1: 가격 차트 + 이평선 + 볼린저밴드 (Price Chart)
    # -------------------------------------------------------------------------
    # 캔들스틱 차트 (한국식: 빨강/파랑)
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], 
        high=df['High'], 
        low=df['Low'], 
        close=df['Close'],
        name='Price',
        increasing_line_color='#ef5350',  # 양봉: 빨강
        decreasing_line_color='#42a5f5'   # 음봉: 파랑
    ), row=1, col=1)
    
    # 이동평균선 추가
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['MA20'], 
        line=dict(color='gold', width=1.5), 
        name='MA20 (생명선)'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['MA60'], 
        line=dict(color='lime', width=1.5), 
        name='MA60 (수급선)'
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['MA120'], 
        line=dict(color='magenta', width=1.5), 
        name='MA120 (경기선)'
    ), row=1, col=1)
    
    # 볼린저밴드 상단
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['BB_Up'],
        line=dict(color='rgba(200,200,200,0.5)', width=1),
        name='BB 상단'
    ), row=1, col=1)
    
    # 볼린저밴드 하단 (채우기 효과)
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['BB_Down'],
        line=dict(color='rgba(200,200,200,0.5)', width=1),
        fill='tonexty', 
        fillcolor='rgba(200,200,200,0.05)',
        name='BB 하단'
    ), row=1, col=1)
    
    # -------------------------------------------------------------------------
    # 6. 시그널 마커 (Signal Markers)
    # -------------------------------------------------------------------------
    # 급등 포착 (Buy Signal)
    buy_days = df[df['Signal_Buy']]
    if not buy_days.empty:
        fig.add_trace(go.Scatter(
            x=buy_days.index, 
            y=buy_days['Close'],
            mode='markers',
            marker=dict(
                symbol='triangle-up', 
                size=12, 
                color='red', 
                line=dict(width=1, color='white')
            ),
            name='급등 포착'
        ), row=1, col=1)
    
    # 급락 포착 (Sell Signal)
    sell_days = df[df['Signal_Sell']]
    if not sell_days.empty:
        fig.add_trace(go.Scatter(
            x=sell_days.index, 
            y=sell_days['Close'],
            mode='markers',
            marker=dict(
                symbol='triangle-down', 
                size=12, 
                color='blue', 
                line=dict(width=1, color='white')
            ),
            name='급락 포착'
        ), row=1, col=1)
    
    # -------------------------------------------------------------------------
    # 7. Row 2: 거래량 (Volume with Signal Highlighting)
    # -------------------------------------------------------------------------
    # 기본 색상: 양봉(빨강), 음봉(파랑)
    colors = np.where(
        df['Close'] >= df['Open'], 
        'rgba(239, 83, 80, 0.5)',   # 양봉: 빨강 (반투명)
        'rgba(66, 165, 245, 0.5)'   # 음봉: 파랑 (반투명)
    )
    # 시그널 발생일은 노란색으로 강조
    colors = np.where(
        df['Signal_Buy'] | df['Signal_Sell'], 
        'rgba(255, 215, 0, 0.9)',  # 시그널: 금색
        colors
    )
    
    fig.add_trace(go.Bar(
        x=df.index, 
        y=df['Volume'],
        marker_color=colors,
        name='Volume'
    ), row=2, col=1)
    
    # -------------------------------------------------------------------------
    # 8. Row 3: Drawdown (낙폭 분석)
    # -------------------------------------------------------------------------
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=drawdown,
        fill='tozeroy',
        line=dict(color='#ef5350'),
        name='Drawdown'
    ), row=3, col=1)
    
    # -------------------------------------------------------------------------
    # 9. Row 4: 통계 테이블 (Summary Table with Signal Counts)
    # -------------------------------------------------------------------------
    # 테마별 색상 설정
    header_color = '#263238' if template == 'plotly_dark' else '#B0BEC5'
    cell_color = '#37474f' if template == 'plotly_dark' else '#ECEFF1'
    font_color = 'white' if template == 'plotly_dark' else 'black'
    
    fig.add_trace(go.Table(
        header=dict(
            values=["Metric", "Value"], 
            fill_color=header_color, 
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[
                ['Start Price', 'End Price', 'Return', 'MDD (Max Loss)', 'Total Days', 'Buy Signals', 'Sell Signals'],
                [
                    f"{start_price:,.0f}", 
                    f"{end_price:,.0f}", 
                    f"{ret:+.2f}%", 
                    f"{mdd:.2f}%", 
                    len(df), 
                    df['Signal_Buy'].sum(),   # 매수 시그널 횟수
                    df['Signal_Sell'].sum()   # 매도 시그널 횟수
                ]
            ],
            fill_color=cell_color, 
            font=dict(color=font_color), 
            align='left'
        )
    ), row=4, col=1)
    
    # -------------------------------------------------------------------------
    # 10. 레이아웃 최종 설정 (Final Layout Configuration)
    # -------------------------------------------------------------------------
    fig.update_layout(
        title=dict(text=f'<b>{name} Trading Dashboard</b>', x=0.5, font=dict(size=24)),
        template=template,
        height=1000,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # 그리드 색상 설정
    grid_color = 'rgba(128, 128, 128, 0.2)' if template == 'plotly_dark' else 'rgba(128, 128, 128, 0.3)'
    fig.update_xaxes(gridcolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color, tickformat=',')
    
    return fig

# ... 종목 선택 및 Date Picker 로직 ...

# 종목 선택
menu = ["데이터를 선택해주세요", "Samsung (삼성전자)", "SK Hynix (SK하이닉스)", "Kakao (카카오)", "Saltlux (솔트룩스)", "Mind AI (마음AI)", "Hancom (한글과컴퓨터)"]
choice = st.sidebar.selectbox("종목 선택 (Select Stock)", menu)

# 날짜 선택
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("시작일", pd.to_datetime("2025-01-01"))
end_date = col2.date_input("종료일", pd.to_datetime("2025-12-31"))

st.sidebar.markdown("---")
# st.sidebar.info("Data provided by FinanceDataReader")

if choice == "데이터를 선택해주세요":
    # 웰컴 화면 테마별 색상 설정 (다크/라이트 모드 대응)
    if is_dark:
        hero_color = "#ffffff"
        sub_color = "#b0bec5"
        card_bg = "#262730"
        card_border = "#37474f"
        card_title_c = "#ffffff"
        card_desc_c = "#cfd8dc"
        shadow_c = "rgba(0, 0, 0, 0.3)"
    else:
        hero_color = "#000000"     # 라이트 모드: 가독성 높은 검정
        sub_color = "#424242"      # 라이트 모드: 진한 회색
        card_bg = "#ffffff"        # 라이트 모드: 흰색 카드 배경
        card_border = "#e0e0e0"    # 라이트 모드: 연한 테두리
        card_title_c = "#000000"   # 라이트 모드: 검정 제목
        card_desc_c = "#424242"    # 라이트 모드: 진한 회색 설명
        shadow_c = "rgba(0, 0, 0, 0.1)"

    # 웰컴 화면 스타일링 (CSS)
    st.markdown(f"""
    <style>
        .hero-title {{
            font-size: 3rem !important;
            font-weight: 800 !important;
            color: {hero_color} !important;
            text-align: center;
            margin-bottom: 0.5rem !important;
        }}
        .hero-subtitle {{
            font-size: 1.2rem !important;
            text-align: center;
            color: {sub_color} !important;
            margin-bottom: 3rem !important;
        }}
        .feature-card {{
            background-color: {card_bg};
            border-radius: 10px;
            padding: 20px;
            border: 1px solid {card_border};
            height: 100%;
            box-shadow: 0 4px 6px {shadow_c};
            transition: transform 0.2s;
        }}
        .feature-card:hover {{
            transform: translateY(-5px);
            border-color: #2196f3;
        }}
        .card-icon {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}
        .card-title {{
            font-size: 1.1rem;
            font-weight: bold;
            color: {card_title_c} !important;
            margin-bottom: 10px;
        }}
        .card-desc {{
            font-size: 0.9rem;
            color: {card_desc_c} !important;
            line-height: 1.5;
        }}
    </style>
    
    <div class="hero-title">주가 차트 대시보드</div>
    <div class="hero-subtitle">데이터 기반의 스마트한 투자 분석을 시작하세요</div>
    """, unsafe_allow_html=True)

    st.divider()

    # 주요 기능 소개 (HTML/CSS 커스텀 카드)
    st.subheader("📌 주요 기능")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <div class="card-icon">📊</div>
            <div class="card-title">심층 차트 분석</div>
            <div class="card-desc">캔들스틱 차트, 이동평균선(MA), 거래량 분석을 통해 주가의 흐름을 한눈에 파악할 수 있습니다.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <div class="card-icon">📉</div>
            <div class="card-title">리스크 관리 (Drawdown)</div>
            <div class="card-desc">고점 대비 하락폭(Drawdown)을 시각화하여 투자 리스크를 직관적으로 분석합니다.</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="feature-card">
            <div class="card-icon">📑</div>
            <div class="card-title">핵심 통계 요약</div>
            <div class="card-desc">수익률, 최대 낙폭(MDD), 변동성 등 투자의사 결정에 필요한 핵심 지표를 제공합니다.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 사용 가이드
    col_guide, col_tip = st.columns([2, 1])
    
    with col_guide:
        st.subheader("🚀 시작하는 방법")
        st.markdown("""
        1. **좌측 사이드바**를 확인해주세요.
        2. **'종목 선택'** 메뉴를 클릭하여 분석하고 싶은 기업을 선택하세요.
           - *지원 종목: 삼성전자, SK하이닉스, 카카오, 솔트룩스, 마음AI, 한글과컴퓨터*
        3. 날짜를 변경하여 **원하는 기간**의 데이터를 조회해보세요.
        """)
        
    with col_tip:
        with st.expander("💡 꿀팁 (Tip)", expanded=True):
            st.markdown("""
            - **테마 자동 적응**: 다크/라이트 모드에 따라 최적의 색상으로 자동 변경됩니다.
            - **차트 확대**: 마우스 드래그로 차트의 특정 구간을 자세히 볼 수 있습니다.
            """)
else:
    # 종목별 설정 매핑 (모든 종목에 종합 분석 리포트 적용)
    stock_map = {
        "Samsung (삼성전자)": {"code": "005930", "type": "comprehensive", "name": "Samsung Electronics"},
        "SK Hynix (SK하이닉스)": {"code": "000660", "type": "comprehensive", "name": "SK Hynix"},
        "Kakao (카카오)": {"code": "035720", "type": "comprehensive", "name": "Kakao"},
        "Saltlux (솔트룩스)": {"code": "304100", "type": "comprehensive", "name": "Saltlux"},
        "Mind AI (마음AI)": {"code": "377480", "type": "comprehensive", "name": "Mind AI"},
        "Hancom (한글과컴퓨터)": {"code": "030520", "type": "comprehensive", "name": "Hancom"},
    }

    selected = stock_map[choice]
    ticker = selected["code"]
    name = selected["name"]

    # 데이터 로딩
    with st.spinner(f"{name} ({ticker}) 데이터 불러오는 중..."):
        df = get_stock_data(ticker, start=start_date, end=end_date)

    if df is None or df.empty:
        st.error("데이터를 불러올 수 없습니다. 날짜나 종목 코드를 확인해주세요.")
    else:
        # 메인 화면
        st.title(f"{choice} Dashboard")
        
        # 최신 데이터 요약
        try:
            last_row = df.iloc[-1]
            prev_row = df.iloc[-2] if len(df) > 1 else last_row
            diff = last_row['Close'] - prev_row['Close']
            pct = (diff / prev_row['Close']) * 100
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("현재가 (Close)", f"{last_row['Close']:,.0f}", f"{diff:+,.0f} ({pct:+.2f}%)")
            m2.metric("시가 (Open)", f"{last_row['Open']:,.0f}")
            m3.metric("고가 (High)", f"{last_row['High']:,.0f}")
            m4.metric("저가 (Low)", f"{last_row['Low']:,.0f}")
        except:
            pass
        
        st.markdown("---")

        # 차트 그리기 - 모든 종목에 종합 분석 리포트 적용
        fig = plot_saltlux_report(df, name, plotly_template)
        st.plotly_chart(fig, width='stretch')
        
        # 데이터 테이블 표시 (옵션)
        with st.expander("데이터 원본 보기 (Raw Data)"):
            st.dataframe(df.style.format("{:,.0f}"))
