import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="🎯 Zone d'Achat -81% Max", layout="wide", page_icon="📈")

st.markdown("""
<style>
    .main { background-color: #131722; color: #d1d4dc; }
    .stMetric { background-color: #1e222d; border: 1px solid #2a2e39; border-radius: 8px; padding: 15px; }
    [data-testid="stMetricValue"] { color: #00d084; }
    h1, h2, h3 { color: #d1d4dc; }
    .stButton>button { background-color: #2962ff; color: white; border: none; border-radius: 4px; font-weight: bold; }
    .stButton>button:hover { background-color: #1e53e5; }
</style>
""", unsafe_allow_html=True)

INTERVAL = "1wk"
PERIOD = "10y"
ZONE_WIDTH = 0.04

@st.cache_data(ttl=3600)
def resolve_ticker(name):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={requests.utils.quote(name)}"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        equities = [q for q in res.json().get('quotes', []) if q.get('quoteType') == 'EQUITY']
        if equities: return equities[0]['symbol'], equities[0].get('longname', name)
    except: pass
    return None, None

def fetch_data(ticker):
    df = yf.Ticker(ticker).history(interval=INTERVAL, period=PERIOD)
    df.dropna(subset=['Close', 'Volume', 'High', 'Low'], inplace=True)
    return df

def calc_fib(high, low):
    diff = high - low
    return {k: high - diff * v for k, v in {'0.236':0.236, '0.382':0.382, '0.500':0.500, '0.618':0.618, '0.786':0.786}.items()}

def find_rounds(price):
    base = 10 ** max(0, int(np.floor(np.log10(price))) - 1)
    step = base if price > 100 else base * 5
    lower = int(price // step) * step
    return [lower + i*step for i in range(-3, 4) if lower + i*step > 0]

def detect_demand(df):
    df['ret'] = df['Close'].pct_change()
    df['vol_ma'] = df['Volume'].rolling(20).mean()
    zones = []
    for i in range(2, len(df)):
        if df.iloc[i-2]['ret'] < -0.03 and df.iloc[i]['ret'] > 0.02 and df.iloc[i]['Volume'] > df.iloc[i-1]['vol_ma'] * 1.3:
            zones.append(df.iloc[i-2:i+1]['Close'].mean())
    return np.unique(np.round(zones, 2)) if zones else np.array([])

def detect_breakouts(df):
    highs = df['High'].rolling(window=12).max().shift(1)
    broken = []
    for i in range(15, len(df)):
        prev = highs.iloc[i]
        if pd.isna(prev): continue
        if df.iloc[i]['Close'] > prev * 1.02:
            for j in range(i+1, min(i+20, len(df))):
                if df.iloc[j]['Low'] <= prev * 1.02 and df.iloc[j]['High'] >= prev * 0.98:
                    broken.append(prev)
                    break
    return np.unique(np.round(broken, 2)) if broken else np.array([])

def score_zone(price, fibs, rounds, demands, breakouts, ath, max_drop):
    if price < ath * (1 - max_drop): return -1
    score = 40 * max(0, 1 - min([abs(price-f)/f for f in [fibs['0.500'], fibs['0.618']]]) * 5)
    score += 20 * max(0, 1 - min([abs(price-r)/r for r in rounds]) * 10)
    if len(demands) > 0: score += 25 * max(0, 1 - min([abs(price-d)/d for d in demands]) * 4)
    if len(breakouts) > 0: score += 15 * max(0, 1 - min([abs(price-b)/b for b in breakouts]) * 5)
    return min(score, 100)

def backtest(df, zone, years):
    periods = int(years * 52)
    idx = np.argmin(np.abs(df['Close'].values - zone))
    exit_idx = min(idx + periods, len(df)-1)
    total = (df.iloc[exit_idx]['Close'] - df.iloc[idx]['Close']) / df.iloc[idx]['Close'] * 100
    return total, ((1 + total/100)**(1/years) - 1)*100

st.title("📈 Zone d'Achat Long Terme")
st.markdown("### 🎯 Contrainte : Maximum -81% vs ATH")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Paramètres")
    company = st.text_input("Nom de l'entreprise", value="Apple")
    hold_years = st.slider("Horizon de détention (ans)", 1, 10, 3)
    currency = st.selectbox("Devise", ["$", "€", "£"], index=0)
    max_drop = st.slider("Baisse max vs ATH (%)", 50, 90, 81)
    if st.button("🔍 LANCER L'ANALYSE", type="primary", use_container_width=True):
        with st.spinner("Analyse..."):
            ticker, full_name = resolve_ticker(company)
            if not ticker:
                st.error("❌ Introuvable.")
                st.stop()
            
            df = fetch_data(ticker)
            current = df.iloc[-1]['Close']
            ath = df['High'].max()
            atl = df['Low'].min()
            min_allowed = ath * (1 - max_drop/100)
            
            fibs = calc_fib(ath, atl)
            rounds = find_rounds(current)
            demands = detect_demand(df)
            breakouts = detect_breakouts(df)
            
            candidates = []
            for p in df['Close']:
                s = score_zone(p, fibs, rounds, demands, breakouts, ath, max_drop/100)
                if s > 0: candidates.append({'price': p, 'score': s})
            
            if candidates:
                best = max(candidates, key=lambda x: x['score'])
                adjusted = False
            else:
                best = {'price': min_allowed, 'score': 0}
                adjusted = True
            
            z_low, z_high = best['price']*(1-ZONE_WIDTH), best['price']*(1+ZONE_WIDTH)
            drop = ((best['price']-ath)/ath)*100
            total_ret, annual_ret = backtest(df, best['price'], hold_years)
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                         increasing_line_color='#0ecb81', decreasing_line_color='#f7525f'), row=1, col=1)
            colors = ['#0ecb81' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#f7525f' for i in range(len(df))]
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, opacity=0.5), row=2, col=1)
            fig.add_hrect(y0=z_low, y1=z_high, fillcolor="rgba(14,203,129,0.2)", line_width=0)
            fig.add_hline(y=best['price'], line_width=4, line_color="#00ff00", annotation_text=f"ZONE {currency}{best['price']:.2f}")
            fig.add_hline(y=ath, line_dash="dash", line_color="#f7525f", line_width=2, annotation_text="ATH")
            fig.add_hline(y=current, line_dash="dot", line_color="#2962ff", line_width=2, annotation_text="ACTUEL")
            fig.add_hline(y=min_allowed, line_dash="dash", line_color="#ff9800", line_width=2, annotation_text=f"PLANCHER -{max_drop}%")
            fig.update_layout(height=800, template='plotly_dark', plot_bgcolor='#131722', paper_bgcolor='#131722',
                             font=dict(color='#d1d4dc'), xaxis_rangeslider_visible=False, showlegend=False)
            fig.update_xaxes(gridcolor='#2a2e39'); fig.update_yaxes(gridcolor='#2a2e39')
            st.plotly_chart(fig, use_container_width=True)
            
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("💰 Actuel", f"{currency}{current:.2f}", f"{((current-ath)/ath)*100:.1f}% vs ATH")
            c2.metric("🚀 ATH", f"{currency}{ath:.2f}")
            c3.metric("🎯 Zone", f"{currency}{best['price']:.2f}", f"{drop:.1f}% vs ATH")
            c4.metric("⭐ Score", f"{best['score']:.0f}/100")
            
            if adjusted: st.warning(f"⚠️ Zone ajustée au plancher ({currency}{min_allowed:.2f}) pour respecter -{max_drop}%.")
            
            ca,cb,cc,cd = st.columns(4)
            ca.info(f"**🔢 Fibonacci**\n0.5: {currency}{fibs['0.500']:.2f}\n0.618: {currency}{fibs['0.618']:.2f}")
            cb.info(f"**⭕ Ronds**\n{', '.join([currency+str(round(r,1)) for r in rounds[:3]]) if len(rounds)>0 else 'Aucun'}")
            cc.info(f"**📥 Demande**\n{', '.join([currency+str(round(d,1)) for d in demands[:2]]) if len(demands)>0 else 'Aucune'}")
            cd.info(f"**🚀 Breakout**\n{', '.join([currency+str(round(b,1)) for b in breakouts[:2]]) if len(breakouts)>0 else 'Aucun'}")
            
            st.markdown("---")
            cx,cy = st.columns(2)
            cx.success(f"**📈 Total ({hold_years} ans)**\n## +{total_ret:.1f}%")
            cy.success(f"**💰 Annuelisé**\n## +{annual_ret:.1f}%/an")
            
            if drop > -10: st.warning("💡 Proche ATH → DCA recommandé.")
            elif drop > -max_drop+5: st.success("💡 Zone idéale pour long terme.")
            else: st.error("💡 Proche plancher → Vérifie les fondamentaux.")
            st.caption("⚖️ Outil éducatif. Ne remplace pas un conseil financier.")