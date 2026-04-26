import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="BuyTheDip | Smart Entry Points", layout="centered", page_icon="📈")

# 🎨 CSS PREMIUM (Bouton WOW, Layout épuré, Zéro artefact)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {
        --bg-main: #0b0e14; --bg-card: #131620; --border: #222738;
        --text-primary: #e2e8f0; --text-secondary: #94a3b8;
        --accent: #14b8a6; --accent-grad: linear-gradient(135deg, #0ea5e9, #14b8a6, #0ea5e9);
        --tv-green: #26a69a; --tv-red: #ef5350; --tv-bg: #131722; --tv-grid: #2a2e39;
    }
    .main { background-color: var(--bg-main); color: var(--text-primary); font-family: 'Inter', system-ui, sans-serif; }
    header, footer, [data-testid="stDecoration"], .stDeployButton { display: none !important; }
    
    .app-wrapper { max-width: 1000px; margin: 0 auto; padding: 1.5rem 0; }
    .brand-header { display: flex; align-items: center; justify-content: center; margin-bottom: 0.8rem; }
    .brand-logo { width: 44px; height: 44px; margin-right: 14px; }
    .brand-title { font-size: 1.9rem; font-weight: 800; background: var(--accent-grad); background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradText 4s ease infinite; letter-spacing: -0.5px; }
    .brand-subtitle { color: var(--text-secondary); font-size: 0.85rem; margin-top: -0.2rem; text-align: center; }
    @keyframes gradText { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    
    .control-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; margin: 1.2rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
    .control-panel label { color: var(--text-secondary) !important; font-size: 0.75rem !important; font-weight: 600 !important; margin-bottom: 0.4rem !important; display: block; text-transform: uppercase; letter-spacing: 0.5px; }
    .control-panel input, .control-panel select { background: #0f1118 !important; border: 1px solid #2a2e39 !important; color: white !important; border-radius: 10px !important; padding: 0.6rem 0.8rem !important; width: 100% !important; transition: all 0.2s; }
    .control-panel input:focus, .control-panel select:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(20,184,166,0.2); outline: none; }
    .control-panel .stSlider > div > div > div > div { background: var(--accent) !important; }
    
    /* BOUTON SCAN ANIMÉ */
    div[data-testid="stButton"] > button {
        background: var(--accent-grad) !important; background-size: 200% 200% !important;
        animation: btnPulse 3s ease infinite !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: 1rem 0 !important; font-weight: 800 !important; font-size: 1.1rem !important;
        width: 100% !important; letter-spacing: 2px; text-transform: uppercase;
        box-shadow: 0 0 25px rgba(20,184,166,0.35) !important;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important; position: relative; overflow: hidden;
    }
    div[data-testid="stButton"] > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 0 40px rgba(20,184,166,0.6) !important;
    }
    div[data-testid="stButton"] > button::after {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: linear-gradient(transparent, rgba(255,255,255,0.15), transparent);
        transform: rotate(45deg); animation: shine 2.5s infinite;
    }
    @keyframes btnPulse { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    @keyframes shine { 0%{left:-50%} 100%{left:150%} }
    
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 1rem; text-align: center; transition: transform 0.2s, border-color 0.2s; }
    .card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .metric-label { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.3rem; }
    .metric-value { font-size: 1.3rem; font-weight: 700; color: var(--text-primary); }
    .delta-pos { color: #00ff00; font-size: 0.8rem; margin-top: 0.2rem; font-weight: 600; }
    .delta-neg { color: var(--tv-red); font-size: 0.8rem; margin-top: 0.2rem; font-weight: 600; }
    
    .section-title { border-left: 4px solid var(--accent); padding-left: 0.8rem; margin: 1.5rem 0 0.8rem; font-size: 1.05rem; font-weight: 600; }
    .alert-box { padding: 0.9rem 1.1rem; border-radius: 10px; margin: 0.8rem 0; border: 1px solid; font-size: 0.9rem; animation: fadeIn 0.3s ease; }
    @keyframes fadeIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }
    .alert-warning { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); color: #fbbf24; }
    .alert-success { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: #34d399; }
    .alert-danger { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.3); color: #f87171; }
    .app-footer { text-align: center; margin-top: 2rem; padding: 1rem; color: var(--text-secondary); font-size: 0.75rem; border-top: 1px solid var(--border); }
</style>
""", unsafe_allow_html=True)

# 🖼️ LOGO SVG INLINE (Vectoriel, léger, s'affiche instantanément)
LOGO_SVG = """
<svg class="brand-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="g1" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#0ea5e9"/>
            <stop offset="100%" style="stop-color:#14b8a6"/>
        </linearGradient>
    </defs>
    <path d="M15 75 L35 55 L55 65 L85 25" fill="none" stroke="url(#g1)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M70 25 L85 25 L85 40" fill="none" stroke="url(#g1)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
    <rect x="10" y="10" width="80" height="80" rx="16" fill="none" stroke="#222738" stroke-width="4"/>
</svg>
"""

# ───────── LOGIQUE MÉTIER ─────────
@st.cache_data(ttl=3600)
def resolve_ticker(name):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={requests.utils.quote(name)}"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        equities = [q for q in res.json().get('quotes', []) if q.get('quoteType') == 'EQUITY']
        if equities: return equities[0]['symbol'], equities[0].get('longname', name)
    except: pass
    return None, None

def fetch_data(ticker, interval="1wk", period="10y"):
    return yf.Ticker(ticker).history(interval=interval, period=period).dropna(subset=['Close', 'Volume', 'High', 'Low'])

def get_market_cap(ticker):
    try:
        mc = yf.Ticker(ticker).fast_info.get('marketCap') or yf.Ticker(ticker).info.get('marketCap', 0)
        if mc >= 1e12: return f"${mc/1e12:.2f}T"
        elif mc >= 1e9: return f"${mc/1e9:.2f}B"
        elif mc >= 1e6: return f"${mc/1e6:.2f}M"
        return f"${mc:,.0f}"
    except: return "N/A"

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
                    broken.append(prev); break
    return np.unique(np.round(broken, 2)) if broken else np.array([])

def score_zone(price, fibs, rounds, demands, breakouts, ath, max_drop):
    if price < ath * (1 - max_drop): return -1, []
    reasons = []
    s = 0
    fib_dev = min([abs(price-f)/f for f in [fibs['0.500'], fibs['0.618']]])
    if fib_dev < 0.04: s += 40 * max(0, 1 - fib_dev * 5); reasons.append("Fibonacci 0.5/0.618")
    round_dev = min([abs(price-r)/r for r in rounds])
    if round_dev < 0.02: s += 20 * max(0, 1 - round_dev * 10); reasons.append("Niveau Psychologique")
    if len(demands) > 0:
        dem_dev = min([abs(price-d)/d for d in demands])
        if dem_dev < 0.04: s += 25 * max(0, 1 - dem_dev * 4); reasons.append("Zone de Demande")
    if len(breakouts) > 0:
        brk_dev = min([abs(price-b)/b for b in breakouts])
        if brk_dev < 0.03: s += 15 * max(0, 1 - brk_dev * 5); reasons.append("Breakout Retest")
    return min(s, 100), reasons

def backtest(df, zone, years):
    periods = int(years * 52)
    idx = np.argmin(np.abs(df['Close'].values - zone))
    exit_idx = min(idx + periods, len(df)-1)
    total = (df.iloc[exit_idx]['Close'] - df.iloc[idx]['Close']) / df.iloc[idx]['Close'] * 100
    return total, ((1 + total/100)**(1/years) - 1)*100

def build_chart(df_view, z_mid, currency, valid_zone):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(x=df_view.index, open=df_view['Open'], high=df_view['High'], low=df_view['Low'], close=df_view['Close'],
                                 increasing_line_color='#26a69a', decreasing_line_color='#ef5350'), row=1, col=1)
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df_view['Close'], df_view['Open'])]
    fig.add_trace(go.Bar(x=df_view.index, y=df_view['Volume'], marker_color=colors, opacity=0.6), row=2, col=1)
    
    if valid_zone:
        fig.add_hline(y=z_mid, line_width=3, line_color="#00ff00", line_dash="solid", 
                      annotation_text=f"🎯 ENTRY: {currency}{z_mid:.2f}", annotation_position="right",
                      annotation_font=dict(color="#00ff00", size=11, family="Inter"))
    fig.add_hline(y=df_view['High'].max(), line_dash="dash", line_color="#ef5350", line_width=1, opacity=0.6)
    fig.add_hline(y=df_view.iloc[-1]['Close'], line_dash="dot", line_color="#60a5fa", line_width=1, opacity=0.6)
    
    fig.update_layout(height=620, template='plotly_dark', plot_bgcolor='#131722', paper_bgcolor='#131722',
                      font=dict(color='#d1d4dc', family="Inter", size=11), xaxis_rangeslider_visible=False, 
                      showlegend=False, hovermode='x unified', margin=dict(l=10, r=10, t=30, b=10))
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#2a2e39', zerolinecolor='#2a2e39')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2a2e39', zerolinecolor='#2a2e39', row=1, col=1)
    fig.update_yaxes(showgrid=False, row=2, col=1)
    return fig

# 🖥️ INTERFACE
st.markdown("<div class='app-wrapper'>", unsafe_allow_html=True)
st.markdown(f"""
<div class='brand-header'>
    {LOGO_SVG}
    <div><div class='brand-title'>BuyTheDip</div></div>
</div>
<p class='brand-subtitle'>Analyse institutionnelle multi-timeframe</p>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    c1, c2 = st.columns([2.5, 1], gap="medium")
    with c1: company = st.text_input("🏢 Entreprise", value="Apple", key="company")
    with c2: 
        st.markdown("<br>", unsafe_allow_html=True)
        analyze = st.button("⚡ SCAN", type="primary", use_container_width=True, key="analyze")
        
    cols = st.columns(4, gap="medium")
    with cols[0]: view_interval = st.selectbox("👁️ Vue", ["1wk", "1mo", "1d"], index=0, key="view_interval")
    with cols[1]: currency = st.selectbox("💱 Devise", ["$", "€", "£"], index=0, key="currency")
    with cols[2]: max_drop = st.slider("📉 Max Drawdown (%)", 50, 90, 81, key="max_drop")
    st.markdown("</div>", unsafe_allow_html=True)

if analyze:
    with st.spinner("⚙️ Scan des confluences en cours..."):
        ticker, full_name = resolve_ticker(company)
        if not ticker:
            st.error("❌ Actif introuvable."); st.stop()
            
        df_calc = fetch_data(ticker, "1wk")
        if df_calc.empty:
            st.error("❌ Données insuffisantes."); st.stop()
            
        current = df_calc.iloc[-1]['Close']
        ath = df_calc['High'].max()
        atl = df_calc['Low'].min()
        market_cap = get_market_cap(ticker)
        
        fibs = calc_fib(ath, atl)
        rounds = find_rounds(current)
        demands = detect_demand(df_calc)
        breakouts = detect_breakouts(df_calc)
        
        best_price, best_score, best_reasons = 0, 0, []
        for p in df_calc['Close']:
            sc, reasons = score_zone(p, fibs, rounds, demands, breakouts, ath, max_drop/100)
            if sc > best_score: best_price, best_score, best_reasons = p, sc, reasons
            
        min_allowed = ath * (1 - max_drop/100)
        if best_score == 0: best_price = min_allowed
            
        valid_zone = best_score >= 50
        drop = ((best_price - ath) / ath) * 100
        ret_3y, ret_ann = backtest(df_calc, best_price, 3)
        
        df_view = fetch_data(ticker, view_interval)
        st.plotly_chart(build_chart(df_view, best_price, currency, valid_zone), use_container_width=True)
        
        # 📊 MÉTRIQUES
        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1: st.markdown(f"<div class='card'><div class='metric-label'>💰 Prix Actuel</div><div class='metric-value'>{current:.2f}</div><div class='delta-neg'>{((current-ath)/ath)*100:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='card'><div class='metric-label'>🏢 Market Cap</div><div class='metric-value'>{market_cap}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='card'><div class='metric-label'>🎯 Cible</div><div class='metric-value'>{best_price:.2f}</div><div class='delta-pos'>{drop:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='card'><div class='metric-label'>⭐ Confluence</div><div class='metric-value'>{best_score:.0f}/100</div></div>", unsafe_allow_html=True)
        
        # 💡 RAISON PRINCIPALE
        st.markdown("<h3 class='section-title'>💡 Pourquoi entrer à ce prix ?</h3>", unsafe_allow_html=True)
        if valid_zone:
            main_reason = best_reasons[0] if best_reasons else "Alignement technique optimal sur support majeur"
            st.markdown(f"<div class='alert-box alert-success'>✅ <b>Raison principale :</b> Le prix cible converge avec <u>{main_reason}</u>, créant une zone d'accumulation à forte probabilité historique. Score >50 validé.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-box alert-danger'>🛑 <b>Zone non validée :</b> Score de confluence < 50. Les indicateurs ne s'alignent pas suffisamment pour justifier une entrée sécurisée actuellement.</div>", unsafe_allow_html=True)
            
        # 📈 RENDMENTS 3 ANS
        st.markdown("<h3 class='section-title'>📊 Backtest 3 Ans</h3>", unsafe_allow_html=True)
        cx, cy = st.columns(2, gap="small")
        with cx: st.markdown(f"<div class='card'><div class='metric-label'>📈 Rendement Total (3 ans)</div><div class='metric-value' style='color:#00ff00'>+{ret_3y:.1f}%</div></div>", unsafe_allow_html=True)
        with cy: st.markdown(f"<div class='card'><div class='metric-label'>💰 Annualisé</div><div class='metric-value' style='color:#00ff00'>+{ret_ann:.1f}% / an</div></div>", unsafe_allow_html=True)
        
        st.caption("⚖️ BuyTheDip est un outil d'aide à la décision. Ne constitue pas un conseil financier.")
else:
    st.info("👈 Entrez une entreprise et cliquez sur **⚡ SCAN**")

st.markdown("<div class='app-footer'>📈 BuyTheDip © 2024 | One Target. All Timeframes.</div></div>", unsafe_allow_html=True)