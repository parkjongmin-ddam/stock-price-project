import FinanceDataReader as fdr
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ==========================================
# 1. 데이터 수집 (Data Collection)
# ==========================================
ticker = "000660" # SK 하이닉스
start_date = "2025-01-01"
end_date = "2025-12-31"

print(f"FinanceDataReader를 통해 {ticker} 데이터를 수집합니다...")
try:
    df = fdr.DataReader(ticker, start_date, end_date)
    if df.empty:
        raise ValueError("데이터가 텅 비어있습니다.")
    print(f"데이터 수집 완료: {len(df)}건")
except Exception as e:
    print(f"오류 발생: {e}")
    exit()

# ==========================================
# 2. 데이터 전처리 (Preprocessing)
# ==========================================
# 이동평균선(MA) 계산
# - MA 5 (5일): 최근 1주일간의 단기 추세 (심리선), 단기 매매의 기준
# - MA 20 (20일): 약 1개월간의 평균 (세력선/생명선), 추세의 기준
# - MA 60 (60일): 약 3개월간의 평균 (수급선), 중기적 경기 흐름
df['MA5'] = df['Close'].rolling(window=5).mean()
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA60'] = df['Close'].rolling(window=60).mean()

# 거래량 색상 구분 (상승: 빨강, 하락: 파랑)
# DataFrame 순회하며 색상 리스트 생성
colors = []
for i, row in df.iterrows():
    if row['Close'] >= row['Open']:
        colors.append('#ff5252') # Red
    else:
        colors.append('#448aff') # Blue

# ==========================================
# 3. 대시보드 시각화 (Visualization)
# ==========================================
# 서브플롯 생성 (2행 1열, 높이 비율 7:3)
fig = make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03,
    subplot_titles=('SK Hynix Stock Price', 'Volume'),
    row_heights=[0.7, 0.3]
)

# [Top] 캔들스틱 차트 (Price)
# - 빨간색 (양봉): 시가보다 종가가 상승
# - 파란색 (음봉): 시가보다 종가가 하락
# - 꼬리(심지): 장중 최고가(High)와 최저가(Low)
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'],
    low=df['Low'], close=df['Close'],
    name='Price',
    increasing_line_color='#ff5252',
    decreasing_line_color='#448aff'
), row=1, col=1)

# [Top] 이동평균선 시각화
# - 노란선 (MA 5): 단기 흐름 파악
# - 초록선 (MA 20): 상승/하락 추세의 중심
# - 보라선 (MA 60): 큰 흐름(수급) 파악
fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='#ffeb3b', width=1.5), name='MA 5'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#00e676', width=1.5), name='MA 20'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='#e040fb', width=1.5), name='MA 60'), row=1, col=1)

# [Bottom] 거래량 (Volume)
# - 막대 높이: 거래가 얼마나 활발했는지 (높을수록 거래 많음)
# - 색상: 주가 상승 시 빨강, 하락 시 파랑 (상승/하락의 강도와 동반된 거래량 확인)
fig.add_trace(go.Bar(
    x=df.index, y=df['Volume'],
    marker_color=colors,
    name='Volume',
    opacity=0.8
), row=2, col=1)

# ==========================================
# 4. 레이아웃 설정 (Layout)
# ==========================================
fig.update_layout(
    title=dict(
        text='<b>SK Hynix Final Dashboard (2025)</b>',
        x=0.5, y=0.95,
        font=dict(size=24, color='white')
    ),
    template='plotly_dark',
    plot_bgcolor='rgba(17, 17, 17, 1)',
    paper_bgcolor='rgba(10, 10, 10, 1)',
    height=900,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font=dict(color='white')
    ),
    xaxis_rangeslider_visible=False,
    hovermode='x unified'
)

# 축 스타일링
common_axis_style = dict(
    gridcolor='rgba(128, 128, 128, 0.2)',
    showspikes=True,
    spikethickness=1,
    spikedash='dot',
    spikecolor='#999999'
)

fig.update_xaxes(**common_axis_style)
fig.update_yaxes(**common_axis_style, tickformat=',')

# ==========================================
# 5. 결과 저장 및 실행 (Output)
# ==========================================
output_file = "hynix_dashboard_final.html"
fig.write_html(output_file)
print(f"최종 대시보드가 '{output_file}'로 저장되었습니다.")

# 윈도우 환경인 경우 자동으로 브라우저 열기
if os.name == 'nt':
    print("브라우저를 실행합니다...")
    os.startfile(output_file)
