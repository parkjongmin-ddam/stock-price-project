# !pip install yfinance plotly

import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -----------------------------------------------------------
# 1. 종목 설정 및 데이터 가져오기
# -----------------------------------------------------------
# 마음AI (구 마인즈랩)
ticker = "377480.KQ"
start_date = "2025-01-01"
end_date = "2025-12-31"  # 25년 꽉 채워서

print(f"[{ticker}] 데이터 긁어오는 중...")
df = yf.download(ticker, start=start_date, end=end_date)

# 데이터 없으면 걍 종료
if df.empty:
    print("데이터 없음. 티커 확인 요망.")
    exit()

# yfinance 멀티인덱스 컬럼 문제 해결 (가끔 이상하게 들어옴)
if isinstance(df.columns, pd.MultiIndex):
    try:
        df = df.xs(ticker, axis=1, level=1)
    except:
        df.columns = df.columns.get_level_values(0)

# 필요한 것만 딱 복사
df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

# Series 변환 (가끔 DataFrame으로 잡혀서 에러나는거 방지)
for c in df.columns:
    if isinstance(df[c], pd.DataFrame):
        df[c] = df[c].iloc[:, 0]

# -----------------------------------------------------------
# 2. 보조지표 계산 (이평선, 볼밴)
# -----------------------------------------------------------
# 이평선: 20일(생명선), 60일(수급선), 120일(경기선)
df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA60'] = df['Close'].rolling(window=60).mean()
df['MA120'] = df['Close'].rolling(window=120).mean()

# 볼린저밴드 (20일, 승수 2)
df['BB_Mid'] = df['MA20']
std = df['Close'].rolling(window=20).std()
df['BB_Up'] = df['BB_Mid'] + (std * 2)
df['BB_Down'] = df['BB_Mid'] - (std * 2)

# 등락률 (%)
df['Pct_Chg'] = df['Close'].pct_change() * 100

# -----------------------------------------------------------
# 3. 수급 포착 로직 (거래량 터진 날 찾기)
# -----------------------------------------------------------
# 상위 10% 기준 잡기
vol_cond = df['Volume'].quantile(0.9)     # 거래량 상위 10%
up_cond = df['Pct_Chg'].quantile(0.9)     # 상승폭 상위 10%
down_cond = df['Pct_Chg'].quantile(0.1)   # 하락폭 하위 10% (많이 떨어진거)

# 거래량 터지면서 급등 or 급락한 날 마킹
df['Signal_Buy'] = (df['Volume'] >= vol_cond) & (df['Pct_Chg'] >= up_cond)
df['Signal_Sell'] = (df['Volume'] >= vol_cond) & (df['Pct_Chg'] <= down_cond)

# -----------------------------------------------------------
# 4. 차트 그리기 (Plotly)
# -----------------------------------------------------------
fig = make_subplots(
    rows=2, cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.03, 
    row_heights=[0.7, 0.3], # 위 70%, 아래 30%
    specs=[[{"type": "xy"}], [{"type": "xy"}]]
)

# [1] 캔들 차트 (한국식: 빨강/파랑)
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name='Price',
    increasing_line_color='#ef5350', # 빨강
    decreasing_line_color='#42a5f5'  # 파랑
), row=1, col=1)

# [2] 이평선 추가
fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='gold', width=1.5), name='MA20'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='lime', width=1.5), name='MA60'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['MA120'], line=dict(color='magenta', width=1.5), name='MA120'), row=1, col=1)

# [3] 볼린저밴드 (배경색 은은하게)
fig.add_trace(go.Scatter(x=df.index, y=df['BB_Up'], line=dict(color='rgba(200,200,200,0.5)', width=1), name='BB 상단'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['BB_Down'], line=dict(color='rgba(200,200,200,0.5)', width=1), fill='tonexty', fillcolor='rgba(200,200,200,0.05)', name='BB 하단'), row=1, col=1)

# [4] 시그널 마커 (화살표)
# 급등날
buy_days = df[df['Signal_Buy']]
fig.add_trace(go.Scatter(
    x=buy_days.index, y=buy_days['Close'],
    mode='markers', marker=dict(symbol='triangle-up', size=12, color='red', line=dict(width=1, color='white')),
    name='급등 포착'
), row=1, col=1)

# 급락날
sell_days = df[df['Signal_Sell']]
fig.add_trace(go.Scatter(
    x=sell_days.index, y=sell_days['Close'],
    mode='markers', marker=dict(symbol='triangle-down', size=12, color='blue', line=dict(width=1, color='white')),
    name='급락 포착'
), row=1, col=1)

# [5] 거래량 (색상 처리)
# 기본: 양봉이면 빨강, 음봉이면 파랑
colors = np.where(df['Close'] >= df['Open'], 'rgba(239, 83, 80, 0.5)', 'rgba(66, 165, 245, 0.5)')
# 특이 거래일은 노란색으로 덮어쓰기
colors = np.where(df['Signal_Buy'] | df['Signal_Sell'], 'rgba(255, 215, 0, 0.9)', colors)

fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'), row=2, col=1)

# [6] 레이아웃 설정 (다크모드)
fig.update_layout(
    title=f"마음AI ({ticker}) 트레이딩 차트",
    title_x=0.5,
    template='plotly_dark',
    xaxis_rangeslider_visible=False, # 밑에 슬라이더 제거
    height=800,
    legend=dict(orientation="h", y=1.02, x=0.5), # 범례 위로 올리기
    margin=dict(t=100, b=50, l=50, r=50)
)

# 그리드 색상 좀 더 연하게
fig.update_xaxes(gridcolor='#333')
fig.update_yaxes(gridcolor='#333')

fig.show()
print("차트 생성 완료.")