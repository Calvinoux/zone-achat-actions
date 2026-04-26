import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import warnings
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from pathlib import Path

warnings.filterwarnings('ignore')
st.set_page_config(page_title="BuyTheDip | Smart Entry Points", layout="centered", page_icon="📈")

# 🎨 CSS PROFESSIONNEL BUYTHEDIP
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {
        --bg-main: #0b0e14; --bg-card: #131620; --border: #222738;
        --text-primary: #e2e8f0; --text-secondary: #94a3b8;
        --accent: #14b8a6; --accent-gradient: linear-gradient(135deg, #14b8a6, #0ea5e9);
        --tv-green: #26a69a; --tv-red: #ef5350; --tv-bg: #131722; --tv-grid: #2a2e39;
    }
    .main { background-color: var(--bg-main); color: var(--text-primary); font-family: 'Inter', system-ui, sans-serif; }
    header, footer, [data-testid="stDecoration"], .stDeployButton { display: none !important; }
    
    .app-wrapper { max-width: 1000px; margin: 0 auto; padding: 1.5rem 0; }
    .brand-header { display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem; }
    .brand-logo { width: 50px; height: 50px; margin-right: 12px; border-radius: 10px; object-fit: contain; }
    .brand-title { font-size: 2rem; font-weight: 800; background: var(--accent-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; }
    .brand-subtitle { color: var(--text-secondary); font-size: 0.9rem; margin-top: -0.2rem; text-align: center; }
    
    .control-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; margin: 1.5rem 0; box-shadow: 0 6px 24px rgba(0,0,0,0.35); }
    .control-panel label { color: var(--text-secondary) !important; font-size: 0.8rem !important; font-weight: 500 !important; margin-bottom: 0.4rem !important; display: block; }
    .control-panel input, .control-panel select { background: var(--bg-main) !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 10px !important; padding: 0.55rem 0.8rem !important; width: 100% !important; }
    .control-panel input:focus, .control-panel select:focus { border-color: var(--accent) !important; outline: none !important; }
    .control-panel .stSlider > div > div > div > div { background: var(--accent) !important; }
    .control-panel .stButton > button { background: var(--accent-gradient) !important; color: white !important; border: none !important; border-radius: 12px !important; padding: 0.85rem 0 !important; font-weight: 600 !important; width: 100% !important; transition: all 0.25s !important; box-shadow: 0 4px 14px rgba(20,184,166,0.35) !important; }
    .control-panel .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(20,184,166,0.5) !important; }
    
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 1.1rem; text-align: center; transition: transform 0.2s, border-color 0.2s; }
    .card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .metric-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.4rem; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); }
    .delta-pos { color: #00ff00; font-size: 0.8rem; margin-top: 0.2rem; }
    .delta-neg { color: var(--tv-red); font-size: 0.8rem; margin-top: 0.2rem; }
    
    .chart-container { border-radius: 14px; overflow: hidden; border: 1px solid var(--border); background: var(--tv-bg); margin: 1.5rem 0; }
    .section-title { border-left: 4px solid var(--accent); padding-left: 0.8rem; margin: 1.5rem 0 0.8rem; font-size: 1.1rem; font-weight: 600; }
    .alert-box { padding: 0.9rem 1.1rem; border-radius: 10px; margin: 0.8rem 0; border: 1px solid; font-size: 0.9rem; animation: fadeIn 0.3s ease; }
    @keyframes fadeIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }
    .alert-warning { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); color: #fbbf24; }
    .alert-success { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: #34d399; }
    .alert-danger { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.3); color: #f87171; }
    .app-footer { text-align: center; margin-top: 2rem; padding: 1rem; color: var(--text-secondary); font-size: 0.8rem; border-top: 1px solid var(--border); }
</style>
""", unsafe_allow_html=True)

# 🖼️ GESTION DU LOGO
def get_logo():
    logo_path = Path("logo.png")
    if logo_path.exists():
        encoded = base64.b64encode(open(logo_path, 'rb').read()).decode()
        return f'<img src="image/png;base64,{encoded}" class="brand-logo">'
    # Fallback visuel si le fichier n'est pas encore uploadé
    return '<div style="width:50px;height:50px;margin-right:12px;border-radius:10px;background:linear-gradient(135deg,#1e3a8a,#14b8a6);display:flex;align-items:center;justify-content:center;color:white;font-weight:800;font-size:1.5rem;">B</div>'

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
    if price < ath * (1 - max_drop): return -1
    s = 40 * max(0, 1 - min([abs(price-f)/f for f in [fibs['0.500'], fibs['0.618']]]) * 5)
    s += 20 * max(0, 1 - min([abs(price-r)/r for r in rounds]) * 10)
    if len(demands) > 0: s += 25 * max(0, 1 - min([abs(price-d)/d for d in demands]) * 4)
    if len(breakouts) > 0: s += 15 * max(0, 1 - min([abs(price-b)/b for b in breakouts]) * 5)
    return min(s, 100)

def backtest(df, zone, years):
    periods = int(years * 52)
    idx = np.argmin(np.abs(df['Close'].values - zone))
    exit_idx = min(idx + periods, len(df)-1)
    total = (df.iloc[exit_idx]['Close'] - df.iloc[idx]['Close']) / df.iloc[idx]['Close'] * 100
    return total, ((1 + total/100)**(1/years) - 1)*100

# 📊 GRAPHIQUE STYLE TRADINGVIEW (Plotly haute fidélité)
def build_tv_chart(df, z_mid, currency):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
    
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Prix', increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
        increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'
    ), row=1, col=1)
    
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors, opacity=0.6), row=2, col=1)
    
    # 🟢 LIGNE VERTE DYNAMIQUE (ancrée à l'axe Y, suit le zoom/pan)
    fig.add_hline(y=z_mid, line_width=3, line_color="#00ff00", line_dash="solid", 
                  annotation_text=f"🎯 ZONE: {currency}{z_mid:.2f}", annotation_position="right",
                  annotation_font=dict(color="#00ff00", size=11, family="Inter"))
    
    fig.add_hline(y=df['High'].max(), line_dash="dash", line_color="#ef5350", line_width=1, opacity=0.7)
    fig.add_hline(y=df.iloc[-1]['Close'], line_dash="dot", line_color="#60a5fa", line_width=1, opacity=0.7)
    
    fig.update_layout(
        height=620, template='plotly_dark', plot_bgcolor='#131722', paper_bgcolor='#131722',
        font=dict(color='#d1d4dc', family="Inter", size=11),
        xaxis_rangeslider_visible=False, showlegend=False, hovermode='x unified',
        margin=dict(l=10, r=10, t=30, b=10)
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#2a2e39', zerolinecolor='#2a2e39')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2a2e39', zerolinecolor='#2a2e39', row=1, col=1)
    fig.update_yaxes(showgrid=False, row=2, col=1)
    return fig

# 🖥️ INTERFACE PRINCIPALE
st.markdown("<div class='app-wrapper'>", unsafe_allow_html=True)
st.markdown(f"""
<div class='brand-header'>
    {get_logo()}
    <div><div class='brand-title'>BuyTheDip</div></div>
</div>
<p class='brand-subtitle'>Identifie les meilleurs points d'entrée sur les corrections</p>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    c1, c2 = st.columns([2.5, 1], gap="medium")
    with c1: company = st.text_input("🏢 Nom de l'entreprise", value="Apple", key="company")
    with c2: 
        st.markdown("<br>", unsafe_allow_html=True)
        analyze = st.button("🔍 LANCER L'ANALYSE", type="primary", use_container_width=True, key="analyze")
        
    cols = st.columns(4, gap="medium")
    with cols[0]: interval = st.selectbox("⏱️ Unité de temps", ["1wk", "1mo", "1d"], index=0, key="interval")
    with cols[1]: currency = st.selectbox("💱 Devise", ["$", "€", "£"], index=0, key="currency")
    with cols[2]: max_drop = st.slider("📉 Baisse max vs ATH (%)", 50, 90, 81, key="max_drop")
    with cols[3]: hold_years = st.slider("📅 Horizon (ans)", 1, 10, 3, key="hold_years")
    st.markdown("</div>", unsafe_allow_html=True)

if analyze:
    with st.spinner("⚙️ Calcul des confluences..."):
        ticker, full_name = resolve_ticker(company)
        if not ticker:
            st.error("❌ Actif introuvable. Vérifie l'orthographe.")
            st.stop()
            
        df = fetch_data(ticker, interval)
        if df.empty:
            st.error("❌ Aucune donnée disponible pour cet actif sur cette période.")
            st.stop()
            
        current = df.iloc[-1]['Close']
        ath = df['High'].max()
        atl = df['Low'].min()
        
        fibs = calc_fib(ath, atl)
        rounds = find_rounds(current)
        demands = detect_demand(df)
        breakouts = detect_breakouts(df)
        
        candidates = [{'price': p, 'score': score_zone(p, fibs, rounds, demands, breakouts, ath, max_drop/100)} for p in df['Close']]
        candidates = [c for c in candidates if c['score'] > 0]
        
        min_allowed = ath * (1 - max_drop/100)
        best = max(candidates, key=lambda x: x['score']) if candidates else {'price': min_allowed, 'score': 0}
        
        z_mid = best['price']
        drop = ((z_mid - ath) / ath) * 100
        total_ret, annual_ret = backtest(df, z_mid, hold_years)
        
        # 📊 GRAPHIQUE DYNAMIQUE
        st.plotly_chart(build_tv_chart(df, z_mid, currency), use_container_width=True)
        
        # 📈 MÉTRIQUES
        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1: st.markdown(f"<div class='card'><div class='metric-label'>💰 Prix Actuel</div><div class='metric-value'>{current:.2f}</div><div class='delta-neg'>{((current-ath)/ath)*100:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='card'><div class='metric-label'>🚀 ATH Historique</div><div class='metric-value'>{ath:.2f}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='card'><div class='metric-label'>🎯 Zone Optimale</div><div class='metric-value'>{z_mid:.2f}</div><div class='delta-pos'>{drop:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='card'><div class='metric-label'>⭐ Score Confluence</div><div class='metric-value'>{best['score']:.0f}/100</div></div>", unsafe_allow_html=True)
        
        # 🔍 CONFLUENCE
        st.markdown("<h3 class='section-title'>🔍 Analyse Technique & Confluence</h3>", unsafe_allow_html=True)
        ca, cb, cc, cd = st.columns(4, gap="small")
        with ca: st.markdown(f"<div class='card'><div class='metric-label'>🔢 Fibonacci</div><div class='metric-value' style='font-size:0.9rem;'>0.50: {fibs['0.500']:.2f}<br>0.618: {fibs['0.618']:.2f}</div></div>", unsafe_allow_html=True)
        with cb: st.markdown(f"<div class='card'><div class='metric-label'>⭕ Niveaux Ronds</div><div class='metric-value' style='font-size:0.85rem;'>{', '.join([currency+str(round(r,1)) for r in rounds[:3]]) if len(rounds)>0 else 'Aucun'}</div></div>", unsafe_allow_html=True)
        with cc: st.markdown(f"<div class='card'><div class='metric-label'>📥 Zones de Demande</div><div class='metric-value' style='font-size:0.85rem;'>{', '.join([currency+str(round(d,1)) for d in demands[:2]]) if len(demands)>0 else 'Aucune'}</div></div>", unsafe_allow_html=True)
        with cd: st.markdown(f"<div class='card'><div class='metric-label'>🚀 Breakout Retest</div><div class='metric-value' style='font-size:0.85rem;'>{', '.join([currency+str(round(b,1)) for b in breakouts[:2]]) if len(breakouts)>0 else 'Aucun'}</div></div>", unsafe_allow_html=True)
        
        cx, cy = st.columns(2, gap="small")
        with cx: st.markdown(f"<div class='card'><div class='metric-label'>📈 Rendement Total ({hold_years} ans)</div><div class='metric-value' style='color:#00ff00'>+{total_ret:.1f}%</div></div>", unsafe_allow_html=True)
        with cy: st.markdown(f"<div class='card'><div class='metric-label'>💰 Annualisé</div><div class='metric-value' style='color:#00ff00'>+{annual_ret:.1f}% / an</div></div>", unsafe_allow_html=True)
        
        # 💡 LECTURE
        st.markdown("<h3 class='section-title'>💡 Lecture Stratégique</h3>", unsafe_allow_html=True)
        if drop > -10:
            st.markdown("<div class='alert-box alert-warning'>⚠️ <b>Proche de l'ATH</b> : L'actif est en zone haute. Privilégiez un DCA progressif ou attendez un repli vers la zone optimale.</div>", unsafe_allow_html=True)
        elif drop > -max_drop + 5:
            st.markdown("<div class='alert-box alert-success'>✅ <b>Zone idéale</b> : Correction structurelle saine avec confluence technique forte. Opportunité d'accumulation long terme.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-box alert-danger'>🛑 <b>Proche du plancher</b> : La baisse dépasse les seuils historiques. Vérifiez impérativement les fondamentaux avant toute entrée.</div>", unsafe_allow_html=True)
            
        st.caption("⚖️ BuyTheDip est un outil d'aide à la décision. Ne constitue pas un conseil financier.")
else:
    st.info("👈 Configurez vos paramètres ci-dessus et cliquez sur **LANCER L'ANALYSE**")

st.markdown("<div class='app-footer'>📈 BuyTheDip © 2024 | Smart Entry Points for Long-Term Investors</div></div>", unsafe_allow_html=True)