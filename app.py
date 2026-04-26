import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')
st.set_page_config(page_title="BuyTheDip | Simply Wall St Style", layout="wide", page_icon="📈")

# 🎨 CSS STYLE SIMPLY WALL ST
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    :root {
        --bg-main: #f8f9fa; --bg-card: #ffffff; --border: #e5e7eb;
        --text-primary: #111827; --text-secondary: #6b7280;
        --sww-blue: #3b82f6; --sww-green: #10b981; --sww-orange: #f59e0b;
        --sww-red: #ef4444; --sww-purple: #8b5cf6; --sww-pink: #ec4899;
    }
    .main { background-color: var(--bg-main); color: var(--text-primary); font-family: 'Inter', system-ui, sans-serif; }
    header, footer, [data-testid="stDecoration"], .stDeployButton { display: none !important; }
    
    .app-wrapper { max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }
    .brand-header { text-align: center; margin-bottom: 2rem; padding: 2rem; background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .brand-title { font-size: 2.2rem; font-weight: 800; color: var(--sww-blue); letter-spacing: -0.5px; }
    .brand-subtitle { color: var(--text-secondary); font-size: 1rem; margin-top: 0.5rem; }
    
    .control-panel { background: white; border-radius: 16px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .control-panel label { color: var(--text-secondary) !important; font-size: 0.75rem !important; font-weight: 600 !important; margin-bottom: 0.4rem !important; display: block; text-transform: uppercase; letter-spacing: 0.5px; }
    .control-panel input, .control-panel select { background: #f9fafb !important; border: 1px solid var(--border) !important; color: var(--text-primary) !important; border-radius: 8px !important; padding: 0.6rem 0.8rem !important; width: 100% !important; transition: all 0.2s; }
    .control-panel input:focus, .control-panel select:focus { border-color: var(--sww-blue) !important; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); outline: none; }
    
    .stFormSubmitButton button {
        background: linear-gradient(135deg, var(--sww-blue), var(--sww-purple)) !important;
        color: white !important; border: none !important; border-radius: 8px !important;
        padding: 0.9rem 0 !important; font-weight: 600 !important; font-size: 1rem !important;
        width: 100% !important; letter-spacing: 0.5px;
        box-shadow: 0 4px 6px rgba(59,130,246,0.2) !important;
        transition: all 0.2s !important;
    }
    .stFormSubmitButton button:hover { transform: translateY(-1px); box-shadow: 0 6px 12px rgba(59,130,246,0.3) !important; }
    
    .section-card { background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .section-title { font-size: 1.25rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
    .section-icon { width: 24px; height: 24px; }
    
    .snowflake-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center; }
    .metric-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
    .metric-card { background: #f9fafb; border-radius: 8px; padding: 1rem; text-align: center; border-left: 4px solid var(--sww-blue); }
    .metric-card.value { border-left-color: var(--sww-blue); }
    .metric-card.growth { border-left-color: var(--sww-green); }
    .metric-card.profitability { border-left-color: var(--sww-orange); }
    .metric-card.health { border-left-color: var(--sww-purple); }
    .metric-card.dividend { border-left-color: var(--sww-pink); }
    
    .metric-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; font-weight: 600; }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }
    .metric-score { font-size: 0.85rem; margin-top: 0.2rem; font-weight: 600; }
    .score-a { color: var(--sww-green); }
    .score-b { color: var(--sww-blue); }
    .score-c { color: var(--sww-orange); }
    .score-d { color: var(--sww-red); }
    
    .key-metrics-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
    .key-card { background: white; border-radius: 12px; padding: 1.25rem; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.2s; }
    .key-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .key-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.5rem; font-weight: 600; }
    .key-value { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); }
    .key-delta { font-size: 0.85rem; margin-top: 0.3rem; font-weight: 600; }
    .delta-pos { color: var(--sww-green); }
    .delta-neg { color: var(--sww-red); }
    
    .fundamental-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0; }
    .fund-card { background: #f9fafb; border-radius: 8px; padding: 1rem; text-align: center; }
    .fund-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; font-weight: 600; }
    .fund-value { font-size: 1.1rem; font-weight: 600; color: var(--text-primary); }
    
    .risk-badge { display: inline-block; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
    .risk-low { background: rgba(16,185,129,0.1); color: var(--sww-green); border: 1px solid var(--sww-green); }
    .risk-med { background: rgba(245,158,11,0.1); color: var(--sww-orange); border: 1px solid var(--sww-orange); }
    .risk-high { background: rgba(239,68,68,0.1); color: var(--sww-red); border: 1px solid var(--sww-red); }
    
    .alert-box { padding: 1rem 1.25rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid; font-size: 0.9rem; }
    .alert-success { background: rgba(16,185,129,0.05); border-color: var(--sww-green); color: var(--text-primary); }
    .alert-warning { background: rgba(245,158,11,0.05); border-color: var(--sww-orange); color: var(--text-primary); }
    .alert-info { background: rgba(59,130,246,0.05); border-color: var(--sww-blue); color: var(--text-primary); }
    
    .chart-container { background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
    
    .app-footer { text-align: center; margin-top: 3rem; padding: 1.5rem; color: var(--text-secondary); font-size: 0.8rem; border-top: 1px solid var(--border); }
    
    @media (max-width: 768px) {
        .snowflake-grid, .key-metrics-row, .fundamental-grid { grid-template-columns: 1fr; }
        .metric-grid { grid-template-columns: 1fr; }
    }
</style>
""", unsafe_allow_html=True)

# 🖼️ LOGO SVG
LOGO_SVG = """
<svg width="48" height="48" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect x="5" y="5" width="90" height="90" rx="20" fill="url(#logoGrad)"/>
    <path d="M30 65 L45 50 L60 55 L75 35" fill="none" stroke="white" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="75" cy="35" r="4" fill="white"/>
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
            'market_cap': info.get('marketCap', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'earnings_growth': info.get('earningsGrowth', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'roe': info.get('returnOnEquity', 0),
            'debt_to_equity_ratio': info.get('debtToEquity', 0)
        }
    except:
        return {'pe_ratio': None, 'profitable': False, 'free_cashflow': None, 'total_cash': None,
                'sector': 'N/A', 'beta': None, 'debt_to_equity': None, 'market_cap': 0,
                'revenue_growth': 0, 'earnings_growth': 0, 'dividend_yield': 0, 'roe': 0, 'debt_to_equity_ratio': 0}

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

def calculate_section_scores(fund, df):
    """Calcule les scores par section comme Simply Wall St"""
    scores = {}
    
    # Value Score (0-6)
    value_score = 0
    if fund['pe_ratio'] and fund['pe_ratio'] < 15: value_score += 2
    elif fund['pe_ratio'] and fund['pe_ratio'] < 25: value_score += 1
    if fund['profitable']: value_score += 1
    if fund.get('roe', 0) > 0.15: value_score += 1
    scores['value'] = min(value_score, 6)
    
    # Growth Score (0-6)
    growth_score = 0
    if fund.get('revenue_growth', 0) > 0.1: growth_score += 2
    elif fund.get('revenue_growth', 0) > 0.05: growth_score += 1
    if fund.get('earnings_growth', 0) > 0.1: growth_score += 2
    elif fund.get('earnings_growth', 0) > 0.05: growth_score += 1
    scores['growth'] = min(growth_score, 6)
    
    # Profitability Score (0-6)
    profit_score = 0
    if fund['profitable']: profit_score += 2
    if fund.get('roe', 0) > 0.1: profit_score += 2
    if fund.get('free_cashflow', 0) and fund['free_cashflow'] > 0: profit_score += 2
    scores['profitability'] = min(profit_score, 6)
    
    # Health Score (0-6)
    health_score = 0
    debt_ratio = fund.get('debt_to_equity_ratio', 0)
    if debt_ratio and debt_ratio < 0.5: health_score += 3
    elif debt_ratio and debt_ratio < 1: health_score += 2
    elif not debt_ratio: health_score += 1
    if fund['profitable']: health_score += 1
    scores['health'] = min(health_score, 6)
    
    # Dividend Score (0-6)
    div_score = 0
    div_yield = fund.get('dividend_yield', 0)
    if div_yield and div_yield > 0.04: div_score += 3
    elif div_yield and div_yield > 0.02: div_score += 2
    elif div_yield and div_yield > 0.01: div_score += 1
    if fund['profitable']: div_score += 1
    scores['dividend'] = min(div_score, 6)
    
    return scores

def create_snowflake_chart(scores):
    """Crée le radar chart style Simply Wall St"""
    categories = ['Value', 'Growth', 'Profitability', 'Health', 'Dividend']
    values = [scores['value'], scores['growth'], scores['profitability'], scores['health'], scores['dividend']]
    
    # Fermer le polygone
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist() + [0]
    
    fig = go.Figure()
    
    # Polygone principal
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.25)',
        line=dict(color='#3b82f6', width=3),
        name='Score'
    ))
    
    # Points aux sommets
    fig.add_trace(go.Scatterpolar(
        r=values[:-1],
        theta=categories,
        mode='markers+text',
        marker=dict(size=8, color='#3b82f6'),
        text=[str(v) for v in values[:-1]],
        textposition='top center',
        textfont=dict(size=12, color='#111827', weight='bold'),
        name='Points'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 6],
                tickmode='array',
                tickvals=[0, 2, 4, 6],
                tickcolor='#e5e7eb',
                gridcolor='#e5e7eb',
                linecolor='#e5e7eb'
            ),
            angularaxis=dict(
                tickcolor='#e5e7eb',
                gridcolor='#e5e7eb',
                rotation=90,
                direction='clockwise'
            ),
            bgcolor='rgba(249, 250, 251, 0.5)'
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_price_chart(df, zone_low, zone_high, currency):
    """Crée un graphique de prix propre style Simply Wall St"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, row_heights=[0.7, 0.3])
    
    # Prix
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines',
        line=dict(color='#3b82f6', width=2),
        name='Prix',
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ), row=1, col=1)
    
    # Zone d'achat
    fig.add_hrect(y0=zone_low, y1=zone_high, 
                  fillcolor="rgba(16, 185, 129, 0.15)", 
                  line_width=0,
                  annotation_text=f"Zone d'achat",
                  annotation_position="top right")
    fig.add_hline(y=zone_low, line_width=2, line_color="#10b981", line_dash="dash")
    fig.add_hline(y=zone_high, line_width=2, line_color="#10b981", line_dash="dash")
    
    # ATH
    fig.add_hline(y=df['High'].max(), line_dash="dash", line_color="#ef4444", 
                  line_width=1, opacity=0.6, annotation_text="ATH")
    
    # Volume
    colors = ['#10b981' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef4444' 
              for i in range(len(df))]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        marker_color=colors,
        opacity=0.6,
        name='Volume'
    ), row=2, col=1)
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#111827', family="Inter", size=11),
        showlegend=False,
        hovermode='x unified',
        margin=dict(l=10, r=10, t=20, b=10)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6', zeroline=False, row=1, col=1)
    fig.update_yaxes(showgrid=False, row=2, col=1)
    
    return fig

# 🖥️ INTERFACE
st.markdown("<div class='app-wrapper'>", unsafe_allow_html=True)
st.markdown(f"""
<div class='brand-header'>
    {LOGO_SVG}
    <h1 class='brand-title'>BuyTheDip</h1>
    <p class='brand-subtitle'>Analyse fondamentale et technique style Simply Wall St</p>
</div>
""", unsafe_allow_html=True)

with st.form(key="scan_form", clear_on_submit=False):
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    cols = st.columns([2, 1, 1, 1])
    with cols[0]: 
        company = st.text_input("🏢 Entreprise", value="Apple", key="company", 
                               placeholder="Ex: Apple, Tesla, Microsoft...")
    with cols[1]: 
        currency = st.selectbox("💱 Devise", ["$", "€", "£"], index=0, key="currency")
    with cols[2]: 
        precision = st.selectbox("🎯 Précision", ["Faible", "Moyenne", "Haute"], 
                                index=1, key="precision")
    with cols[3]: 
        hold_years = st.selectbox("⏳ Horizon", [1, 3, 5, 10], index=1, key="hold_years")
        st.markdown("<br>", unsafe_allow_html=True)
    submit = st.form_submit_button("⚡ Analyser", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if submit:
    threshold_map = {"Faible": 40, "Moyenne": 60, "Haute": 80}
    threshold = threshold_map[precision]

    with st.spinner(f"🔍 Analyse en cours..."):
        ticker, full_name = resolve_ticker(company)
        if not ticker:
            st.error("❌ Actif introuvable."); st.stop()
            
        df = fetch_data(ticker, hold_years)
        if df.empty:
            st.error(f"❌ Données insuffisantes."); st.stop()
            
        current = df.iloc[-1]['Close']
        ath = df['High'].max()
        atl = df['Low'].min()
        
        fund = get_fundamentals(ticker)
        risk_score = calc_risk_score(fund, df)
        risk_label, risk_class = get_risk_label(risk_score)
        
        # Calcul des scores par section
        section_scores = calculate_section_scores(fund, df)
        total_score = sum(section_scores.values())
        
        # Zone d'achat
        fibs = calc_fib(ath, atl)
        rounds = find_rounds(current)
        demands = detect_demand(df)
        breakouts = detect_breakouts(df)
        
        all_candidates = []
        for p in df['Close']:
            sc, reasons = score_zone(p, fibs, rounds, demands, breakouts, ath)
            all_candidates.append({'price': p, 'score': sc, 'reasons': reasons})
        
        max_hist_score = max([c['score'] for c in all_candidates]) if all_candidates else 0
        
        if precision == "Haute":
            threshold = max_hist_score
        
        valid_candidates = [c for c in all_candidates if c['score'] >= threshold]
        
        if len(valid_candidates) < 2:
            valid_candidates = sorted(all_candidates, key=lambda x: x['score'], reverse=True)[:2]
        
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
        else:
            zone_high, zone_low = ath * 0.75, ath * 0.65
        
        drop = ((zone_low - ath) / ath) * 100
        
        # 📊 MÉTRIQUES CLÉS
        st.markdown("<div class='key-metrics-row'>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            st.markdown(f"""
            <div class='key-card'>
                <div class='key-label'>💰 Prix Actuel</div>
                <div class='key-value'>{current:.2f} {currency}</div>
                <div class='key-delta delta-neg'>{((current-ath)/ath)*100:.1f}% vs ATH</div>
            </div>
            """, unsafe_allow_html=True)
        with c2: 
            st.markdown(f"""
            <div class='key-card'>
                <div class='key-label'>🎯 Zone d'achat</div>
                <div class='key-value'>{zone_low:.2f} → {zone_high:.2f}</div>
                <div class='key-delta delta-pos'>{drop:.1f}% vs ATH</div>
            </div>
            """, unsafe_allow_html=True)
        with c3: 
            st.markdown(f"""
            <div class='key-card'>
                <div class='key-label'>🏢 Market Cap</div>
                <div class='key-value'>{fund['market_cap']/1e9:.1f}B {currency}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4: 
            st.markdown(f"""
            <div class='key-card'>
                <div class='key-label'>⭐ Score Total</div>
                <div class='key-value'>{total_score}/30</div>
                <div class='key-delta'>Sur 5 critères</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 📊 SNOWFLAKE CHART + GRAPHIQUE PRIX
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("<div class='section-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>📊 Snowflake Analysis</div>", unsafe_allow_html=True)
            st.plotly_chart(create_snowflake_chart(section_scores), use_container_width=True)
            
            st.markdown("<div class='metric-grid'>", unsafe_allow_html=True)
            metrics = [
                ('value', 'Value', '💎'),
                ('growth', 'Growth', '📈'),
                ('profitability', 'Profitability', '💰'),
                ('health', 'Health', '💪'),
                ('dividend', 'Dividend', '💵')
            ]
            for key, label, icon in metrics:
                score = section_scores[key]
                grade = 'A' if score >= 5 else 'B' if score >= 4 else 'C' if score >= 3 else 'D'
                grade_class = 'score-a' if grade == 'A' else 'score-b' if grade == 'B' else 'score-c' if grade == 'C' else 'score-d'
                st.markdown(f"""
                <div class='metric-card {key}'>
                    <div class='metric-label'>{icon} {label}</div>
                    <div class='metric-value'>{score}/6</div>
                    <div class='metric-score {grade_class}'>Note: {grade}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.plotly_chart(create_price_chart(df, zone_low, zone_high, currency), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # 📋 FONDAMENTAUX
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📋 Données Fondamentales</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='fundamental-grid'>
            <div class='fund-card'><div class='fund-label'>📈 PER</div><div class='fund-value'>{f"{fund['pe_ratio']:.1f}x" if fund['pe_ratio'] else "N/A"}</div></div>
            <div class='fund-card'><div class='fund-label'>💰 Rentable</div><div class='fund-value' style='color:{"#10b981" if fund["profitable"] else "#ef4444"}'>{"✅ Oui" if fund["profitable"] else "❌ Non"}</div></div>
            <div class='fund-card'><div class='fund-label'>💵 Cash Flow</div><div class='fund-value'>{f"{fund['free_cashflow']/1e9:.1f}B" if fund['free_cashflow'] else "N/A"}</div></div>
            <div class='fund-card'><div class='fund-label'>🏭 Secteur</div><div class='fund-value'>{fund['sector']}</div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 🛡️ RISQUE
        st.markdown(f"""
        <div class='section-card' style='text-align:center;'>
            <span class='risk-badge {risk_class}' style='font-size:1rem; padding:0.5rem 1.5rem;'>
                🛡️ Risque: {risk_label} (Score: {risk_score}/100)
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # 💡 RECOMMANDATION
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>💡 Recommandation</div>", unsafe_allow_html=True)
        if drop < -20:
            st.markdown(f"""
            <div class='alert-box alert-success'>
                ✅ <b>Opportunité d'achat</b> : L'action est {abs(drop):.1f}% en dessous de son ATH. 
                La zone d'achat identifiée entre <b>{currency}{zone_low:.2f}</b> et <b>{currency}{zone_high:.2f}</b> 
                représente un point d'entrée attractif avec un score de confluence élevé.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-box alert-warning'>
                ⚠️ <b>Attente recommandée</b> : L'action est proche de son ATH ({drop:.1f}%). 
                Patientez pour une meilleure entrée ou utilisez un DCA.
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ⚙️ CONFIG
        st.markdown(f"""
        <div class='alert-box alert-info'>
            <b>Configuration :</b> Précision {precision} (Seuil ≥{threshold}) | 
            Horizon: {hold_years} an(s) | Données: {len(df)} semaines
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("⚖️ BuyTheDip est un outil d'aide à la décision. Ne constitue pas un conseil financier.")
else:
    st.markdown("""
    <div style='text-align:center; padding:4rem 2rem; background:white; border-radius:16px; box-shadow:0 1px 3px rgba(0,0,0,0.1);'>
        <div style='font-size:4rem; margin-bottom:1rem;'>📊</div>
        <h2 style='color:#111827; margin-bottom:0.5rem;'>Analyse complète style Simply Wall St</h2>
        <p style='color:#6b7280; margin-bottom:2rem;'>Entrez une entreprise ci-dessus pour obtenir :</p>
        <div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:1rem; max-width:800px; margin:0 auto;'>
            <div style='background:#f9fafb; padding:1.5rem; border-radius:8px;'><div style='font-size:2rem; margin-bottom:0.5rem;'>📊</div><div style='font-weight:600;'>Snowflake Analysis</div></div>
            <div style='background:#f9fafb; padding:1.5rem; border-radius:8px;'><div style='font-size:2rem; margin-bottom:0.5rem;'>💎</div><div style='font-weight:600;'>Value Score</div></div>
            <div style='background:#f9fafb; padding:1.5rem; border-radius:8px;'><div style='font-size:2rem; margin-bottom:0.5rem;'>📈</div><div style='font-weight:600;'>Growth Score</div></div>
            <div style='background:#f9fafb; padding:1.5rem; border-radius:8px;'><div style='font-size:2rem; margin-bottom:0.5rem;'>💰</div><div style='font-weight:600;'>Profitability</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='app-footer'>📈 BuyTheDip © 2024 | Inspired by Simply Wall St</div></div>", unsafe_allow_html=True)