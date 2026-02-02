import streamlit as st
import FinanceDataReader as fdr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# ==========================================
# 1. 페이지 및 레이아웃 설정
# ==========================================
st.set_page_config(
    page_title="Team Project Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 스타일 적용 (다크 모드 스타일)
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .main-header {
        font-size: 2.5rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #1f2937;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #374151;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 및 종목 설정
# ==========================================
# 팀원별 종목 리스트
COMPANIES = {
    "SK하이닉스": "000660",
    "삼성전자": "005930",
    "카카오": "035720",
    "마음AI": "377480",
    "솔트록스": "304100",
    "한글과컴퓨터": "030520"
}

# 기간 설정 (기본값: 2025년 전체)
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

# ==========================================
# 3. 함수 정의
# ==========================================
@st.cache_data
def load_data(ticker, start, end):
    try:
        df = fdr.DataReader(ticker, start, end)
        if df.empty:
            return None
        
        # 이동평균선 계산
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

def create_dashboard(df, company_name):
    # 최근 데이터 기준 정보 표시 (마지막 날짜)
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2] if len(df) > 1 else last_row
    
    change = last_row['Close'] - prev_row['Close']
    pct_change = (change / prev_row['Close']) * 100
    color = "red" if change >= 0 else "blue"
    
    # 상단 메트릭 표시
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("종가 (Close)", f"{last_row['Close']:,} KRW", f"{change:+,} ({pct_change:+.2f}%)")
    with col2:
        st.metric("시가 (Open)", f"{last_row['Open']:,} KRW")
    with col3:
        st.metric("고가 (High)", f"{last_row['High']:,} KRW")
    with col4:
        st.metric("거래량 (Volume)", f"{last_row['Volume']:,}")

    # 차트 생성 (Candlestick + Volume)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03,
        subplot_titles=(f'{company_name} 주가 흐름', '거래량'),
        row_heights=[0.7, 0.3]
    )

    # 캔들스틱 - 상승(빨강), 하락(파랑)
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price',
        increasing_line_color='#ff5252',
        decreasing_line_color='#448aff'
    ), row=1, col=1)

    # 이동평균선
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='#ffeb3b', width=1.5), name='MA 5'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#00e676', width=1.5), name='MA 20'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='#e040fb', width=1.5), name='MA 60'), row=1, col=1)

    # 거래량 (색상 구분)
    colors = ['#ff5252' if r.Close >= r.Open else '#448aff' for i, r in df.iterrows()]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        marker_color=colors,
        name='Volume',
        opacity=0.8
    ), row=2, col=1)

    # 레이아웃 업데이트
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(17, 17, 17, 1)',
        paper_bgcolor='rgba(10, 10, 10, 1)',
        height=800,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, width='stretch')

# ==========================================
# 4. 사이드바 및 메인 로직
# ==========================================
st.sidebar.title("📈 주가 대시보드")
st.sidebar.markdown("팀 프로젝트 종목 분석")
st.sidebar.markdown("---")

# 종목 선택
selected_company = st.sidebar.radio(
    "분석할 종목을 선택하세요:",
    list(COMPANIES.keys()),
    index=0  # 기본값 SK하이닉스
)

# 메인 화면
st.markdown(f"<div class='main-header'>{selected_company} 대시보드</div>", unsafe_allow_html=True)

ticker = COMPANIES[selected_company]

# 데이터 로드
with st.spinner(f'{selected_company} ({ticker}) 데이터를 불러오는 중...'):
    df = load_data(ticker, START_DATE, END_DATE)

if df is not None:
    create_dashboard(df, selected_company)
    
    # 데이터프레임 표시 (옵션)
    with st.expander("📊 데이터 원본 보기"):
        st.dataframe(df.style.format("{:.0f}").background_gradient(cmap="Reds", subset=["Close"]), width='stretch')
else:
    st.error("데이터를 찾을 수 없습니다. 종목 코드나 기간을 확인해주세요.")

# Footer
st.markdown("---")
st.markdown("Generative AI 10th Team Project | Created with Streamlit & Plotly")
