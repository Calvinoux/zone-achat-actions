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

# 🎨 CSS PREMIUM
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {
        --bg-main: #0b0e14; --bg-card: #131620; --border: #222738;
        --text-primary: #e2e8f0; --text-secondary: #94a3b8;
        --accent: #14b8a6; --accent-grad: linear-gradient(135deg, #0ea5e9, #14b8a6, #0ea5e9);
        --tv-green: #26a69a; --tv-red: #ef5350; --tv-bg: #131722; --tv-grid: #2a2e39;
        --risk-low: #10b981; --risk-med: #f59e0b; --risk-high: #ef4444;
    }
    .main { background-color: var(--bg-main); color: var(--text-primary); font-family: 'Inter', system-ui, sans-serif; }
    header, footer, [data-testid="stDecoration"], .stDeployButton { display: none !important; }
    
    .app-wrapper { max-width: 1000px; margin: 0 auto; padding: 2rem 1rem; }
    .brand-header { text-align: center; margin-bottom: 1.5rem; }
    .brand-logo { width: 80px; height: 80px; margin: 0 auto 1rem; display: block; }
    .brand-title { font-size: 2.4rem; font-weight: 800; background: var(--accent-grad); background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradText 4s ease infinite; letter-spacing: -0.5px; margin: 0; }
    .brand-subtitle { color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.3rem; }
    @keyframes gradText { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    
    .stForm { background: transparent; border: none; }
    .stForm > div { background: transparent !important; }
    
    .control-panel { padding: 1rem 0 1.5rem; }
    .control-panel label { color: var(--text-secondary) !important; font-size: 0.75rem !important; font-weight: 600 !important; margin-bottom: 0.4rem !important; display: block; text-transform: uppercase; letter-spacing: 0.5px; }
    .control-panel input, .control-panel select { background: var(--bg-card) !important; border: 1px solid var(--border) !important; color: white !important; border-radius: 10px !important; padding: 0.6rem 0.8rem !important; width: 100% !important; transition: all 0.2s; }
    .control-panel input:focus, .control-panel select:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(20,184,166,0.2); outline: none; }
    .control-panel .stSlider > div > div > div > div { background: var(--accent) !important; }
    
    .stFormSubmitButton button {
        background: var(--accent-grad) !important; background-size: 200% 200% !important;
        animation: btnPulse 3s ease infinite !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: 1rem 0 !important; font-weight: 800 !important; font-size: 1.1rem !important;
        width: 100% !important; letter-spacing: 2px; text-transform: uppercase;
        box-shadow: 0 0 25px rgba(20,184,166,0.35) !important;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important; position: relative; overflow: hidden;
    }
    .stFormSubmitButton button:hover { transform: translateY(-3px) scale(1.02) !important; box-shadow: 0 0 40px rgba(20,184,166,0.6) !important; }
    .stFormSubmitButton button::after {
        content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
        background: linear-gradient(transparent, rgba(255,255,255,0.15), transparent);
        transform: rotate(45deg); animation: shine 2.5s infinite;
    }
    @keyframes btnPulse { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
    @keyframes shine { 0%{left:-50%} 100%{left:150%} }
    
    .key-metrics-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; justify-content: center; }
    .key-card { flex: 1; min-width: 180px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 1rem; text-align: center; transition: all 0.2s; }
    .key-card:hover { border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
    .key-label { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.4rem; }
    .key-value { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); }
    .key-delta { font-size: 0.8rem; margin-top: 0.2rem; font-weight: 600; }
    .delta-pos { color: #00ff00; } .delta-neg { color: var(--tv-red); }
    
    .fundamental-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin: 1rem 0; }
    .fund-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 0.9rem; text-align: center; }
    .fund-label { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; }
    .fund-value { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); }
    .risk-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    .risk-low { background: rgba(16,185,129,0.15); color: var(--risk-low); border: 1px solid var(--risk-low); }
    .risk-med { background: rgba(245,158,11,0.15); color: var(--risk-med); border: 1px solid var(--risk-med); }
    .risk-high { background: rgba(239,68,68,0.15); color: var(--risk-high); border: 1px solid var(--risk-high); }
    
    .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 1rem; text-align: center; transition: transform 0.2s, border-color 0.2s; }
    .card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .metric-label { font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 0.3rem; }
    .metric-value { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); }
    
    .section-title { border-left: 4px solid var(--accent); padding-left: 0.8rem; margin: 1.5rem 0 0.8rem; font-size: 1.05rem; font-weight: 600; }
    .alert-box { padding: 0.9rem 1.1rem; border-radius: 10px; margin: 0.8rem 0; border: 1px solid; font-size: 0.9rem; animation: fadeIn 0.3s ease; }
    @keyframes fadeIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:translateY(0); } }
    .alert-warning { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); color: #fbbf24; }
    .alert-success { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: #34d399; }
    .alert-danger { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.3); color: #f87171; }
    .alert-info { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.3); color: #60a5fa; }
    .app-footer { text-align: center; margin-top: 2.5rem; padding: 1rem; color: var(--text-secondary); font-size: 0.75rem; border-top: 1px solid var(--border); }
</style>
""", unsafe_allow_html=True)

# 🖼️ LOGO SVG
LOGO_SVG = """
<svg class="brand-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="logoGrad" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#0ea5e9;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#14b8a6;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect x="5" y="5" width="90" height="90" rx="20" fill="none" stroke="url(#logoGrad)" stroke-width="4"/>
    <path d="M25 65 L45 45 L60 55 L80 25" fill="none" stroke="url(#logoGrad)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M70 25 L80 25 L80 35" fill="none" stroke="url(#logoGrad)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
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

def fetch_data(ticker, years):
    period_map = {1: "1y", 3: "3y", 5: "5y", 10: "10y"}
    return yf.Ticker(ticker).history(interval="1wk", period=period_map.get(years, "5y")).dropna(subset=['Close', 'Volume', 'High', 'Low'])

def get_fundamentals(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            'pe_ratio': info.get('trailingPE') or info.get('forwardPE'),
            'profitable': info.get('profitMargins', 0) > 0,
            'free_cashflow': info.get('freeCashflow'),
            'total_cash': info.get('totalCash'),
            'sector': info.get('sector', 'N/A'),
            'beta': info.get('beta', 1.0),
            'debt_to_equity': info.get('debtToEquity'),
            'market_cap': info.get('marketCap', 0)
        }
    except:
        return {'pe_ratio': None, 'profitable': None, 'free_cashflow': None, 'total_cash': None, 
                'sector': 'N/A', 'beta': None, 'debt_to_equity': None, 'market_cap': 0}

def calc_risk_score(fund, df):
    score = 0
    if len(df) >= 30:
        vol = df['Close'].pct_change().tail(30).std() * np.sqrt(52)
        if vol < 0.2: score += 30
        elif vol < 0.4: score += 20
        elif vol < 0.6: score += 10
    if fund['beta'] and fund['beta'] < 1.2: score += 25
    elif fund['beta'] and fund['beta'] < 1.5: score += 15
    if fund['debt_to_equity'] and fund['debt_to_equity'] < 50: score += 25
    elif fund['debt_to_equity'] and fund['debt_to_equity'] < 100: score += 15
    if fund['profitable']: score += 20
    return min(score, 100)

def get_risk_label(score):
    if score >= 70: return "Faible", "risk-low"
    elif score >= 40: return "Modéré", "risk-med"
    else: return "Élevé", "risk-high"

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

def score_zone(price, fibs, rounds, demands, breakouts, ath):
    reasons = []
    s = 0
    fib_dev = min([abs(price-f)/f for f in [fibs['0.500'], fibs['0.618']]])
    if fib_dev < 0.04: s += 40 * max(0, 1 - fib_dev * 5); reasons.append("Fibonacci")
    round_dev = min([abs(price-r)/r for r in rounds])
    if round_dev < 0.02: s += 20 * max(0, 1 - round_dev * 10); reasons.append("Niveau Rond")
    if len(demands) > 0:
        dem_dev = min([abs(price-d)/d for d in demands])
        if dem_dev < 0.04: s += 25 * max(0, 1 - dem_dev * 4); reasons.append("Demande")
    if len(breakouts) > 0:
        brk_dev = min([abs(price-b)/b for b in breakouts])
        if brk_dev < 0.03: s += 15 * max(0, 1 - brk_dev * 5); reasons.append("Breakout")
    return min(s, 100), reasons

def backtest(df, zone_low, zone_high, years):
    periods = int(years * 52)
    idx = np.argmin(np.abs(df['Close'].values - (zone_low + zone_high)/2))
    exit_idx = min(idx + periods, len(df)-1)
    entry = (zone_low + zone_high) / 2
    total = (df.iloc[exit_idx]['Close'] - entry) / entry * 100
    annual = ((1 + total/100)**(1/years) - 1)*100 if years > 0 else 0
    return total, annual

def build_chart(df, zone_low, zone_high, currency, valid_zone, years):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                 increasing_line_color='#26a69a', decreasing_line_color='#ef5350'), row=1, col=1)
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, opacity=0.6), row=2, col=1)
    
    if valid_zone and len(df) > 0:
        fig.add_hrect(y0=zone_low, y1=zone_high, fillcolor="rgba(0, 255, 0, 0.15)", line_width=0,
                      annotation_text=f"🎯 ZONE: {currency}{zone_low:.2f} → {currency}{zone_high:.2f}",
                      annotation_position="top right", annotation_font=dict(color="#00ff00", size=10))
        fig.add_hline(y=zone_low, line_width=2, line_color="#00ff00", line_dash="dot", opacity=0.7)
        fig.add_hline(y=zone_high, line_width=2, line_color="#00ff00", line_dash="dot", opacity=0.7)
    
    if len(df) > 0:
        fig.add_hline(y=df['High'].max(), line_dash="dash", line_color="#ef5350", line_width=1, opacity=0.6)
        fig.add_hline(y=df.iloc[-1]['Close'], line_dash="dot", line_color="#60a5fa", line_width=1, opacity=0.6)
    
    height = 400 if years <= 1 else (500 if years <= 3 else 580)
    fig.update_layout(height=height, template='plotly_dark', plot_bgcolor='#131722', paper_bgcolor='#131722',
                      font=dict(color='#d1d4dc', family="Inter", size=11), xaxis_rangeslider_visible=False, 
                      showlegend=False, hovermode='x unified', margin=dict(l=10, r=10, t=20, b=10),
                      title=f"📊 {years} an(s) | {len(df)} semaines de données")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#2a2e39', zerolinecolor='#2a2e39')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#2a2e39', zerolinecolor='#2a2e39', row=1, col=1)
    fig.update_yaxes(showgrid=False, row=2, col=1)
    return fig

# 🖥️ INTERFACE
st.markdown("<div class='app-wrapper'>", unsafe_allow_html=True)
st.markdown(LOGO_SVG, unsafe_allow_html=True)
st.markdown("<div class='brand-header'><h1 class='brand-title'>BuyTheDip</h1><p class='brand-subtitle'>Points d'entrée institutionnels. Zéro bruit.</p></div>", unsafe_allow_html=True)

with st.form(key="scan_form", clear_on_submit=False):
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    c1, c2 = st.columns([2.5, 1], gap="medium")
    with c1: 
        company = st.text_input("🏢 Entreprise", value="Apple", key="company", placeholder="Ex: Apple, Tesla...")
    with c2: 
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("⚡ SCAN", use_container_width=True)
    
    cols = st.columns(3, gap="medium")
    with cols[0]: currency = st.selectbox("💱 Devise", ["$", "€", "£"], index=0, key="currency")
    with cols[1]: precision = st.selectbox("🎯 Précision", ["Faible", "Moyenne", "Haute"], index=1, key="precision")
    with cols[2]: hold_years = st.selectbox("⏳ Horizon", [1, 3, 5, 10], index=1, key="hold_years")
    st.markdown("</div>", unsafe_allow_html=True)

if submit:
    with st.spinner(f"⚙️ Scan sur {hold_years} an(s) (Précision: {precision})..."):
        ticker, full_name = resolve_ticker(company)
        if not ticker:
            st.error("❌ Actif introuvable."); st.stop()
            
        df = fetch_data(ticker, hold_years)
        if df.empty:
            st.error(f"❌ Données insuffisantes sur {hold_years} an(s)."); st.stop()
            
        current = df.iloc[-1]['Close']
        ath = df['High'].max()
        atl = df['Low'].min()
        
        fund = get_fundamentals(ticker)
        risk_score = calc_risk_score(fund, df)
        risk_label, risk_class = get_risk_label(risk_score)
        
        fibs = calc_fib(ath, atl)
        rounds = find_rounds(current)
        demands = detect_demand(df)
        breakouts = detect_breakouts(df)
        
        # 🧠 CALCUL PRÉALABLE DE TOUS LES SCORES POUR DÉTECTER LE MAX HISTORIQUE
        all_candidates = []
        for p in df['Close']:
            sc, reasons = score_zone(p, fibs, rounds, demands, breakouts, ath)
            all_candidates.append({'price': p, 'score': sc, 'reasons': reasons})
            
        max_hist_score = max([c['score'] for c in all_candidates]) if all_candidates else 0
        
        # 🎯 MAPPING DYNAMIQUE DE LA PRÉCISION
        if precision == "Haute":
            threshold = max_hist_score  # ✅ UTILISE TOUJOURS LA VALEUR MAXIMALE EXISTANTE
            precision_label = f"Maximale ({threshold}/100)"
        elif precision == "Moyenne":
            threshold = 60
            precision_label = "Moyenne (60/100)"
        else:
            threshold = 40
            precision_label = "Faible (40/100)"
            
        valid_candidates = [c for c in all_candidates if c['score'] >= threshold]
        
        # Fallback intelligent si la précision haute est trop stricte
        if len(valid_candidates) < 2:
            if precision == "Haute":
                valid_candidates = sorted(all_candidates, key=lambda x: x['score'], reverse=True)[:2]
                precision_label += " (Top 2 historiques)"
            else:
                valid_candidates = sorted(all_candidates, key=lambda x: x['score'], reverse=True)[:2]
                
        # Extraction des 2 zones
        if len(valid_candidates) >= 2:
            valid_candidates.sort(key=lambda x: x['score'], reverse=True)
            z1 = valid_candidates[0]['price']
            for c in valid_candidates[1:]:
                if abs(c['price'] - z1) / z1 > 0.05:
                    z2 = c['price']
                    break
            else:
                z2 = z1 * 0.95
            zone_high, zone_low = (z1, z2) if z1 > z2 else (z2, z1)
            zone_method = f"Confluence {precision_label}"
        else:
            zone_high, zone_low = ath * 0.75, ath * 0.65
            zone_method = "Fallback structurel"
            
        valid_zone = "Fallback" not in zone_method
        ret_total, ret_ann = backtest(df, zone_low, zone_high, hold_years)
        
        # 📈 MÉTRIQUES
        st.markdown("<div class='key-metrics-row'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='key-card'><div class='key-label'>💰 Prix Actuel</div><div class='key-value'>{current:.2f} {currency}</div><div class='key-delta delta-neg'>{((current-ath)/ath)*100:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='key-card'><div class='key-label'>🎯 Zone d'achat parfaite</div><div class='key-value' style='color:#00ff00'>{zone_low:.2f} → {zone_high:.2f} {currency}</div><div class='key-delta delta-pos'>{((zone_low-ath)/ath)*100:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='key-card'><div class='key-label'>🏢 Market Cap</div><div class='key-value'>{fund['market_cap']/1e9:.1f}B {currency}</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 📋 FONDAMENTAUX
        st.markdown("<h3 class='section-title'>📋 Données Fondamentales</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='fundamental-grid'>
            <div class='fund-card'><div class='fund-label'>📈 PER</div><div class='fund-value'>{f"{fund['pe_ratio']:.1f}x" if fund['pe_ratio'] else "N/A"}</div></div>
            <div class='fund-card'><div class='fund-label'>💰 Rentable</div><div class='fund-value' style='color:{"#10b981" if fund["profitable"] else "#ef4444"}'>{"✅ Oui" if fund["profitable"] else "❌ Non"}</div></div>
            <div class='fund-card'><div class='fund-label'>💵 Cash Flow</div><div class='fund-value'>{f"{fund['free_cashflow']/1e9:.1f}B" if fund['free_cashflow'] else "N/A"}</div></div>
            <div class='fund-card'><div class='fund-label'>🏭 Secteur</div><div class='fund-value'>{fund['sector']}</div></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 🛡️ RISQUE
        st.markdown(f"""
        <div style='text-align:center; margin:1rem 0;'>
            <span class='risk-badge {risk_class}'>🛡️ Risque: {risk_label} (Score: {risk_score}/100)</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 📊 GRAPHIQUE
        st.plotly_chart(build_chart(df, zone_low, zone_high, currency, valid_zone, hold_years), use_container_width=True)
        
        # 💡 RAISON
        st.markdown("<h3 class='section-title'>💡 Pourquoi cette zone ?</h3>", unsafe_allow_html=True)
        if valid_zone:
            st.markdown(f"<div class='alert-box alert-success'>✅ <b>Méthode :</b> {zone_method}. Analyse sur {hold_years} an(s). Accumulez entre {currency}{zone_low:.2f} et {currency}{zone_high:.2f}.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='alert-box alert-warning'>⚠️ <b>Note :</b> {zone_method}. La précision demandée dépasse les setups historiques disponibles. Zone structurelle affichée.</div>", unsafe_allow_html=True)
            
        # ⚙️ CONFIG
        st.markdown("<h3 class='section-title'>⚙️ Configuration</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='alert-box alert-info'>🎯 Précision: {precision_label} | 💱 Devise: {currency} | ⏳ Horizon: {hold_years} an(s) | 📊 Données: {len(df)} semaines | 📈 Max historique détecté: {max_hist_score}/100</div>", unsafe_allow_html=True)
        
        # 🔍 CONFLUENCE & BACKTEST
        st.markdown("<h3 class='section-title'>🔍 Confluence & Performance</h3>", unsafe_allow_html=True)
        ca, cb, cc, cd = st.columns(4, gap="small")
        with ca: st.markdown(f"<div class='card'><div class='metric-label'>⭐ Score Moyen</div><div class='metric-value'>{score_zone((zone_low+zone_high)/2, fibs, rounds, demands, breakouts, ath)[0]:.0f}/100</div></div>", unsafe_allow_html=True)
        with cb: st.markdown(f"<div class='card'><div class='metric-label'>🔢 Fibonacci</div><div class='metric-value' style='font-size:0.85rem;'>0.5: {fibs['0.500']:.2f}<br>0.618: {fibs['0.618']:.2f}</div></div>", unsafe_allow_html=True)
        with cc: st.markdown(f"<div class='card'><div class='metric-label'>📥 Demande</div><div class='metric-value' style='font-size:0.85rem;'>{len(demands)} zone(s)</div></div>", unsafe_allow_html=True)
        with cd: st.markdown(f"<div class='card'><div class='metric-label'>🚀 Breakout</div><div class='metric-value' style='font-size:0.85rem;'>{len(breakouts)} niveau(x)</div></div>", unsafe_allow_html=True)
        
        cx, cy = st.columns(2, gap="small")
        with cx: st.markdown(f"<div class='card'><div class='metric-label'>📈 Rendement {hold_years} An(s)</div><div class='metric-value' style='color:#00ff00'>+{ret_total:.1f}%</div></div>", unsafe_allow_html=True)
        with cy: st.markdown(f"<div class='card'><div class='metric-label'>💰 Annualisé</div><div class='metric-value' style='color:#00ff00'>+{ret_ann:.1f}% / an</div></div>", unsafe_allow_html=True)
        
        st.caption("⚖️ BuyTheDip est un outil d'aide à la décision. Ne constitue pas un conseil financier.")
else:
    st.info("👈 Entrez une entreprise et appuyez sur **Entrée** ou cliquez sur **⚡ SCAN**")

st.markdown("<div class='app-footer'>📈 BuyTheDip © 2024 | One Target. All Timeframes.</div></div>", unsafe_allow_html=True)