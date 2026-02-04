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
        /* 기본 폰트 색상 및 배경 */
        .stApp { 
            background-color: #0e1117; 
            color: #ffffff; 
        }
        
        /* 사이드바 스타일링 */
        section[data-testid="stSidebar"] { 
            background-color: #262730; 
        }
        
        /* 사이드바 내부 텍스트 색상 강제 지정 */
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }

        /* 헤더 스타일링 */
        header[data-testid="stHeader"] { 
            background-color: #0e1117; 
        }

        /* Metric 위젯 스타일 */
        [data-testid="stMetricValue"] { color: #00e676 !important; font-weight: 700 !important; }
        [data-testid="stMetricLabel"] { color: #e0e0e0 !important; }

        /* 상단 툴바 및 배포 버튼만 숨기기 */
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { visibility: hidden !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
    </style>
    """
else:
    css = """
    <style>
        /* Light Mode 기본 설정 */
        .stApp { 
            background-color: #ffffff; 
            color: #333333; 
        }
        
        /* 사이드바 스타일링 */
        section[data-testid="stSidebar"] { 
            background-color: #f8f9fa; 
            border-right: 1px solid #e0e0e0;
        }

        /* 사이드바 내부 텍스트 색상 */
        section[data-testid="stSidebar"] * {
            color: #31333F !important;
        }

        /* 헤더 스타일링 */
        header[data-testid="stHeader"] { 
            background-color: #ffffff; 
        }
        
        /* Metric 위젯 스타일 */
        [data-testid="stMetricValue"] { color: #111111 !important; }
        [data-testid="stMetricLabel"] { color: #666666 !important; }
        
        /* 상단 툴바 및 배포 버튼만 숨기기 */
        .stDeployButton { display: none !important; }
        [data-testid="stToolbar"] { visibility: hidden !important; }
        #MainMenu { visibility: hidden !important; }
        footer { visibility: hidden !important; }
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
    기본형 대시보드
    """
    # 전처리
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    
    colors = ['#ff5252' if c >= o else '#448aff' for c, o in zip(df['Close'], df['Open'])]

    # 통계 계산
    start_price, end_price, ret, drawdown, mdd = calculate_stats(df)

    # 서브플롯
    fig = make_subplots(
        rows=4, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.05,
        subplot_titles=(f'{name} ({ticker}) Price', 'Volume', 'Drawdown (Risk Analysis)', 'Summary Statistics'),
        row_heights=[0.5, 0.15, 0.15, 0.2],
        specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "xy"}], [{"type": "table"}]]
    )

    # 1. 캔들스틱
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Price', increasing_line_color='#ff5252', decreasing_line_color='#448aff'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='#ffeb3b', width=1), name='MA 5'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#00e676', width=1), name='MA 20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='#e040fb', width=1), name='MA 60'), row=1, col=1)

    # 2. 거래량
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], marker_color=colors, name='Volume'
    ), row=2, col=1)

    # 3. Drawdown
    fig.add_trace(go.Scatter(
        x=df.index, y=drawdown, 
        fill='tozeroy', 
        line=dict(color='#ef5350'), 
        name='Drawdown'
    ), row=3, col=1)

    # 4. Table (테마별 색상 적용)
    header_color = '#263238' if template == 'plotly_dark' else '#B0BEC5'
    cell_color = '#37474f' if template == 'plotly_dark' else '#ECEFF1'
    font_color = 'white' if template == 'plotly_dark' else 'black'
    
    fig.add_trace(go.Table(
        header=dict(values=["Metric", "Value"], fill_color=header_color, font=dict(color='white', size=12)),
        cells=dict(values=[['Start Price', 'End Price', 'Return', 'MDD (Max Loss)', 'Total Days'],
                           [f"{start_price:,.0f}", f"{end_price:,.0f}", f"{ret:+.2f}%", f"{mdd:.2f}%", len(df)]],
                   fill_color=cell_color, font=dict(color=font_color), align='left')
    ), row=4, col=1)

    fig.update_layout(
        title=dict(text=f'<b>{name} Dashboard</b>', x=0.5, font=dict(size=24)),
        template=template,
        height=1000, 
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    grid_color = 'rgba(128, 128, 128, 0.2)'
    fig.update_xaxes(gridcolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color, tickformat=',')
    
    return fig

def plot_kakao_dashboard(df, name="Kakao", template="plotly_dark"):
    """
    카카오 스타일 대시보드
    """
    # 전처리
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()
    bb_std = df["Close"].rolling(window=20).std()
    df["BB_UPPER"] = df["MA20"] + 2 * bb_std
    df["BB_LOWER"] = df["MA20"] - 2 * bb_std
    df["Return"] = df["Close"].pct_change()
    
    try:
        valid = df[["Return", "Volume"]].dropna()
        if not valid.empty:
            ret_up = np.percentile(valid["Return"], 90)
            ret_down = np.percentile(valid["Return"], 10)
            vol_th = np.percentile(valid["Volume"], 90)
            df["LargeUp"] = (df["Return"] >= ret_up) & (df["Volume"] >= vol_th)
            df["LargeDown"] = (df["Return"] <= ret_down) & (df["Volume"] >= vol_th)
        else:
            df["LargeUp"] = False; df["LargeDown"] = False
    except:
        df["LargeUp"] = False; df["LargeDown"] = False

    start_price, end_price, ret, drawdown, mdd = calculate_stats(df)

    # 차트
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=(f'{name} Price & BB', 'Volume', 'Drawdown (Risk Analysis)', 'Summary Statistics'),
        specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "xy"}], [{"type": "table"}]]
    )

    # 1. Price
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name="Price", increasing_line_color="#00B0F6", decreasing_line_color="#F63538"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_UPPER"], line=dict(color="rgba(135, 206, 250, 0.5)", width=1), name="BB Upper"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOWER"], line=dict(color="rgba(135, 206, 250, 0.5)", width=1), fill='tonexty', fillcolor="rgba(135, 206, 250, 0.1)", name="BB Lower"), row=1, col=1)

    # Markers
    if df["LargeUp"].any():
        fig.add_trace(go.Scatter(x=df.index[df["LargeUp"]], y=df["Close"][df["LargeUp"]], mode="markers", marker=dict(symbol="triangle-up", size=10, color="#00FF7F"), name="Large Up"), row=1, col=1)
    if df["LargeDown"].any():
        fig.add_trace(go.Scatter(x=df.index[df["LargeDown"]], y=df["Close"][df["LargeDown"]], mode="markers", marker=dict(symbol="triangle-down", size=10, color="#FF4500"), name="Large Down"), row=1, col=1)

    # 2. Volume
    colors = np.where(df["Close"] >= df["Open"], '#00B0F6', '#F63538')
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], marker_color=colors, name="Volume"), row=2, col=1)

    # 3. Drawdown
    fig.add_trace(go.Scatter(x=df.index, y=drawdown, fill='tozeroy', line=dict(color='#ef5350'), name='Drawdown'), row=3, col=1)

    # 4. Table
    header_color = '#263238' if template == 'plotly_dark' else '#B0BEC5'
    cell_color = '#37474f' if template == 'plotly_dark' else '#ECEFF1'
    font_color = 'white' if template == 'plotly_dark' else 'black'

    fig.add_trace(go.Table(
        header=dict(values=["Metric", "Value"], fill_color=header_color, font=dict(color='white')),
        cells=dict(values=[['Start Price', 'End Price', 'Return', 'MDD', 'Total Days'],
                           [f"{start_price:,.0f}", f"{end_price:,.0f}", f"{ret:+.2f}%", f"{mdd:.2f}%", len(df)]],
                   fill_color=cell_color, font=dict(color=font_color), align='left')
    ), row=4, col=1)

    fig.update_layout(title=f"<b>{name} Advanced Dashboard</b>", template=template, height=1000, xaxis_rangeslider_visible=False)
    grid_color = 'rgba(128, 128, 128, 0.2)'
    fig.update_xaxes(gridcolor=grid_color); fig.update_yaxes(gridcolor=grid_color)
    return fig


def plot_saltlux_report(df, name="Saltlux", template="plotly_white"):
    """
    솔트룩스 스타일 상세 분석 리포트
    """
    # 통계 계산
    start_price = df['Close'].iloc[0]; end_price = df['Close'].iloc[-1]
    ret = ((end_price - start_price)/start_price)*100
    mdd = (((df['Close'] - df['Close'].expanding().max()) / df['Close'].expanding().max()) * 100).min()
    
    df['MA20'] = df['Close'].rolling(20).mean()
    df['BB_Up'] = df['MA20'] + 2*df['Close'].rolling(20).std()
    df['BB_Low'] = df['MA20'] - 2*df['Close'].rolling(20).std()
    daily_ret = df['Close'].pct_change() * 100
    
    # 레이아웃
    fig = make_subplots(
        rows=4, cols=2,
        specs=[[{'colspan': 2, 'type': 'xy'}, None], 
               [{'type': 'xy'}, {'type': 'xy'}],
               [{'colspan': 2, 'type': 'xy'}, None], 
               [{'colspan': 2, 'type': 'table'}, None]],
        vertical_spacing=0.08,
        subplot_titles=("Price Trend & Bollinger Bands", "Daily Return Dist", "Volume Analysis", "Drawdown", "Summary Statistics")
    )

    # 1. Price
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Up'], line=dict(color='gray', dash='dot'), name='BB Up'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Low'], line=dict(color='gray', dash='dot'), fill='tonexty', fillcolor='rgba(200,200,200,0.2)', name='BB Low'), row=1, col=1)

    # 2. Daily Return
    fig.add_trace(go.Histogram(x=daily_ret, nbinsx=30, marker_color='#7E57C2', name='Return Dist'), row=2, col=1)

    # 3. Volume
    colors_vol = ['#26A69A' if c >= o else '#EF5350' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors_vol, name='Volume'), row=2, col=2)

    # 4. Drawdown
    dd = ((df['Close'] - df['Close'].expanding().max()) / df['Close'].expanding().max()) * 100
    fig.add_trace(go.Scatter(x=df.index, y=dd, fill='tozeroy', line=dict(color='#C62828'), name='Drawdown'), row=3, col=1)

    # 5. Table (테마별)
    header_color = '#455A64' if template == 'plotly_white' else '#263238'
    cell_color = 'white' if template == 'plotly_white' else '#37474f'
    font_color_table = 'black' if template == 'plotly_white' else 'white'
    
    fig.add_trace(go.Table(
        header=dict(values=["Metric", "Value"], fill_color=header_color, font=dict(color='white')),
        cells=dict(values=[['Start Price', 'End Price', 'Return', 'MDD', 'Total Days'],
                           [f"{start_price:,.0f}", f"{end_price:,.0f}", f"{ret:.2f}%", f"{mdd:.2f}%", len(df)]],
                   fill_color=cell_color, align='left', font=dict(color=font_color_table))
    ), row=4, col=1)

    fig.update_layout(title=f"<b>{name} Analytics Report</b>", height=1200, template=template, showlegend=False)
    return fig

# ... 종목 선택 및 Date Picker 로직 ...

# 종목 선택
menu = ["데이터를 선택해주세요", "Samsung (삼성전자)", "SK Hynix (SK하이닉스)", "Kakao (카카오)", "Saltlux (솔트룩스)", "Hancom (한글과컴퓨터)"]
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
           - *지원 종목: 삼성전자, SK하이닉스, 카카오, 솔트룩스, 한글과컴퓨터*
        3. 날짜를 변경하여 **원하는 기간**의 데이터를 조회해보세요.
        """)
        
    with col_tip:
        with st.expander("💡 꿀팁 (Tip)", expanded=True):
            st.markdown("""
            - **테마 자동 적응**: 다크/라이트 모드에 따라 최적의 색상으로 자동 변경됩니다.
            - **차트 확대**: 마우스 드래그로 차트의 특정 구간을 자세히 볼 수 있습니다.
            """)
else:
    # 종목별 설정 매핑
    stock_map = {
        "Samsung (삼성전자)": {"code": "005930", "type": "standard", "name": "Samsung Electronics"},
        "SK Hynix (SK하이닉스)": {"code": "000660", "type": "standard", "name": "SK Hynix"},
        "Kakao (카카오)": {"code": "035720", "type": "kakao", "name": "Kakao"},
        "Saltlux (솔트룩스)": {"code": "304100", "type": "saltlux", "name": "Saltlux"},
        "Hancom (한글과컴퓨터)": {"code": "030520", "type": "standard", "name": "Hancom"},
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

        # 차트 그리기 (Template 적용)
        if selected["type"] == "standard":
            fig = plot_standard_dashboard(df, name, ticker, plotly_template)
            st.plotly_chart(fig, use_container_width=True)
            
        elif selected["type"] == "kakao":
            fig = plot_kakao_dashboard(df, name, plotly_template)
            st.plotly_chart(fig, use_container_width=True)
            
        elif selected["type"] == "saltlux":
            fig = plot_saltlux_report(df, name, plotly_template)
            st.plotly_chart(fig, use_container_width=True)
        
        # 데이터 테이블 표시 (옵션)
        with st.expander("데이터 원본 보기 (Raw Data)"):
            st.dataframe(df.style.format("{:,.0f}"))
