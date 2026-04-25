# app.py
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

# 🎨 CSS Style TradingView
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

# ───────── CONFIGURATION ─────────
CURRENCY_SYMBOL = "$"
INTERVAL = "1wk"
PERIOD = "10y"
HOLD_YEARS = 3
ZONE_WIDTH = 0.04
MAX_DROP_VS_ATH = 0.81  # 🛑 81% de baisse MAXIMUM autorisé pour la zone d'achat
# ─────────────────────────────────

@st.cache_data(ttl=3600)
def resolve_ticker(name):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={requests.utils.quote(name)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        equities = [q for q in res.json().get('quotes', []) if q.get('quoteType') == 'EQUITY']
        if equities:
            return equities[0]['symbol'], equities[0].get('longname', name)
    except: 
        pass
    return None, None

def fetch_data(ticker):
    df = yf.Ticker(ticker).history(interval=INTERVAL, period=PERIOD)
    df.dropna(subset=['Close', 'Volume', 'High', 'Low'], inplace=True)
    return df

def calc_fib(high, low):
    diff = high - low
    return {k: high - diff * v for k, v in {'0.236': 0.236, '0.382': 0.382, '0.500': 0.500, '0.618': 0.618, '0.786': 0.786}.items()}

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
    return np.unique(np.round(zones, 2)) if zones else []

def detect_breakouts(df):
    highs = df['High'].rolling(window=12).max().shift(1)
    broken = []
    for i in range(15, len(df)):
        prev = highs.iloc[i]
        if pd.isna(prev): 
            continue
        if df.iloc[i]['Close'] > prev * 1.02:
            for j in range(i+1, min(i+20, len(df))):
                if df.iloc[j]['Low'] <= prev * 1.02 and df.iloc[j]['High'] >= prev * 0.98:
                    broken.append(prev)
                    break
    return np.unique(np.round(broken, 2)) if broken else []

def score_zone(price, fibs, rounds, demands, breakouts, ath, max_drop):
    # 🛑 CONTRAINTE ABSOLUE : prix >= ATH * (1 - max_drop)
    min_price = ath * (1 - max_drop)
    if price < min_price:
        return -1  # Score négatif = rejet immédiat
    
    score = 0
    fibs_t = [fibs['0.500'], fibs['0.618']]
    score += 40 * max(0, 1 - min([abs(price-f)/f for f in fibs_t]) * 5)
    score += 20 * max(0, 1 - min([abs(price-r)/r for r in rounds]) * 10)
    if len(demands) > 0: 
        score += 25 * max(0, 1 - min([abs(price-d)/d for d in demands]) * 4)
    if len(breakouts) > 0: 
        score += 15 * max(0, 1 - min([abs(price-b)/b for b in breakouts]) * 5)
    return min(score, 100)

def backtest(df, zone, years):
    periods = int(years * 52 if INTERVAL == "1wk" else years * 12)
    idx = np.argmin(np.abs(df['Close'].values - zone))
    exit_idx = min(idx + periods, len(df)-1)
    entry, exit_p = df.iloc[idx]['Close'], df.iloc[exit_idx]['Close']
    total = (exit_p - entry)/entry * 100
    annual = ((1 + total/100)**(1/years) - 1)*100
    return total, annual

# 🖥️ INTERFACE
st.title("📈 Zone d'Achat Long Terme")
st.markdown("### 🎯 Contrainte : Maximum -81% vs ATH appliqué à la zone proposée")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Paramètres")
    company = st.text_input("Nom de l'entreprise", value="Apple")
    interval = st.selectbox("Unité de temps", ["1wk", "1mo", "1d"], index=0)
    hold_years = st.slider("Horizon de détention (ans)", 1, 10, 3)
    currency = st.selectbox("Devise", ["$", "€", "£"], index=0)
    max_drop = st.slider("Baisse max vs ATH autorisée (%)", 50, 90, 81)  # 👈 Tu peux ajuster ici
    analyze_btn = st.button("🔍 LANCER L'ANALYSE", type="primary", use_container_width=True)

if analyze_btn:
    with st.spinner(f"🔍 Analyse de {company}..."):
        ticker, full_name = resolve_ticker(company)
        
        if not ticker:
            st.error("❌ Action introuvable.")
            st.stop()
        
        df = fetch_data(ticker)
        current_price = df.iloc[-1]['Close']
        ath = df['High'].max()
        atl = df['Low'].min()
        
        # 🛑 PLANCHER ABSOLU : ATH * (1 - max_drop)
        min_allowed = ath * (1 - max_drop/100)
        
        fibs = calc_fib(ath, atl)
        rounds = find_rounds(current_price)
        demands = detect_demand(df)
        breakouts = detect_breakouts(df)
        
        # Scoring AVEC contrainte appliquée
        candidates = []
        for price in df['Close']:
            s = score_zone(price, fibs, rounds, demands, breakouts, ath, max_drop/100)
            if s > 0:
                candidates.append({'price': price, 'score': s})
        
        # Sélection du meilleur parmi les valides
        if candidates:
            best = max(candidates, key=lambda x: x['score'])
            adjusted = False
        else:
            # Aucun candidat valide → on remonte au plancher
            best = {'price': min_allowed, 'score': 0}
            adjusted = True
        
        zone_low = best['price'] * (1 - ZONE_WIDTH)
        zone_high = best['price'] * (1 + ZONE_WIDTH)
        zone_mid = best['price']
        
        drop_vs_ath = ((zone_mid - ath) / ath) * 100
        current_vs_ath = ((current_price - ath) / ath) * 100
        
        total_ret, annual_ret = backtest(df, best['price'], hold_years)
        
        # 📊 GRAPHIQUE
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.03, row_heights=[0.7, 0.3])
        
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name='Prix', increasing_line_color='#0ecb81', decreasing_line_color='#f7525f'
        ), row=1, col=1)
        
        colors = ['#0ecb81' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#f7525f' for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors, opacity=0.5), row=2, col=1)
        
        # 🟢 ZONE VERTE
        fig.add_hrect(y0=zone_low, y1=zone_high, fillcolor="rgba(14, 203, 129, 0.2)", line_width=0)
        fig.add_hline(y=zone_mid, line_width=4, line_color="#00ff00", line_dash="solid", 
                     annotation_text=f"ZONE: {currency}{zone_mid:.2f}", annotation_font_color="#00ff00")
        
        # Lignes de repère
        fig.add_hline(y=ath, line_dash="dash", line_color="#f7525f", line_width=2, annotation_text=f"ATH")
        fig.add_hline(y=current_price, line_dash="dot", line_color="#2962ff", line_width=2, annotation_text=f"Actuel")
        
        # 🛑 LIGNE ROUGE : PLANCHER -81%
        fig.add_hline(y=min_allowed, line_dash="dash", line_color="#ff9800", line_width=2, 
                     annotation_text=f"PLANCHER -{max_drop}%", annotation_font_color="#ff9800")
        
        fig.update_layout(height=800, template='plotly_dark', plot_bgcolor='#131722', paper_bgcolor='#131722',
                         font=dict(color='#d1d4dc'), xaxis_rangeslider_visible=False, showlegend=False, hovermode='x unified')
        fig.update_xaxes(gridcolor='#2a2e39', zerolinecolor='#2a2e39')
        fig.update_yaxes(gridcolor='#2a2e39', zerolinecolor='#2a2e39')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 📊 MÉTRIQUES
        st.markdown("### 📊 Métriques")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Prix Actuel", f"{currency}{current_price:.2f}", f"{current_vs_ath:.1f}% vs ATH")
        c2.metric("🚀 ATH", f"{currency}{ath:.2f}")
        c3.metric("🎯 Zone Proposée", f"{currency}{zone_mid:.2f}", f"{drop_vs_ath:.1f}% vs ATH")
        c4.metric("⭐ Score", f"{best['score']:.0f}/100")
        
        # 🛑 ALERTES CONTRAINTE
        if adjusted:
            st.warning(f"⚠️ **Zone ajustée au plancher** : La zone optimale calculée était en dessous de -{max_drop}% vs ATH. Elle a été remontée à {currency}{min_allowed:.2f} pour respecter ta contrainte.")
        
        if drop_vs_ath < -max_drop + 1:  # Marge de 1%
            st.error(f"🛑 **Attention** : La zone proposée est très proche du plancher -{max_drop}%. Vérifie les fondamentaux avant d'entrer.")
        
        # 🔍 CONFLUENCE
        st.markdown("---")
        st.markdown("### 🔍 Confluence")
        ca, cb, cc, cd = st.columns(4)
        ca.info(f"**🔢 Fibonacci**\n0.500: {currency}{fibs['0.500']:.2f}\n0.618: {currency}{fibs['0.618']:.2f}")
        cb.info(f"**⭕ Nombres Ronds**\n{', '.join([currency+str(round(r,1)) for r in rounds[:3]])}")
        cc.info(f"**📥 Demande**\n{', '.join([currency+str(round(d,1)) for d in demands[:2]]) if demands else 'Aucune'}")
        cd.info(f"**🚀 Breakout**\n{', '.join([currency+str(round(b,1)) for b in breakouts[:2]]) if breakouts else 'Aucune'}")
        
        # 📈 BACKTEST
        st.markdown("---")
        cx, cy = st.columns(2)
        cx.success(f"**📈 Rendement Total ({hold_years} ans)**\n## +{total_ret:.1f}%")
        cy.success(f"**💰 Rendement Annuelisé**\n## +{annual_ret:.1f}%/an")
        
        # 💡 INTERPRÉTATION
        st.markdown("---")
        if drop_vs_ath > -10:
            st.warning("💡 **Proche de l'ATH** : Patience ou DCA.")
        elif -max_drop + 5 <= drop_vs_ath <= -10:
            st.success("💡 **Zone idéale** : Correction saine, bon point d'entrée long terme.")
        else:
            st.error(f"💡 **Proche du plancher -{max_drop}%** : Correction profonde, vérifie les fondamentaux.")
        
        st.caption("⚖️ Outil d'aide à la décision. Ne remplace pas un conseil financier.")

else:
    st.info("👈 Entre une entreprise et clique sur **LANCER L'ANALYSE**")
    st.markdown(f"### ✅ Contrainte active : **Maximum -{MAX_DROP_VS_ATH*100:.0f}% vs ATH** pour la zone proposée")
