import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import warnings
from streamlit.components.v1 import html

warnings.filterwarnings('ignore')
st.set_page_config(page_title="🎯 AlphaZone | Scanner Long Terme", layout="wide", page_icon="📈")

# 🎨 CSS PROFESSIONNEL (Sobre, Moderne, Dark Mode)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root {
        --bg-main: #0b0e14; --bg-card: #131620; --bg-sidebar: #0f1118;
        --border: #222738; --text-primary: #e2e8f0; --text-secondary: #94a3b8;
        --accent: #3b82f6; --accent-hover: #2563eb;
        --green: #10b981; --red: #ef4444; --yellow: #f59e0b;
    }
    .main { background-color: var(--bg-main); color: var(--text-primary); font-family: 'Inter', system-ui, sans-serif; }
    .stSidebar { background-color: var(--bg-sidebar); border-right: 1px solid var(--border); }
    .stSidebar > div { padding-top: 2rem; }
    
    /* Boutons & Inputs */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent), var(--accent-hover));
        color: white; border: none; border-radius: 8px; font-weight: 600; padding: 0.8rem 0; width: 100%;
        transition: all 0.2s ease; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3); }
    .stTextInput > div > div > input, .stSelectbox > div > div > select {
        background-color: var(--bg-card); border: 1px solid var(--border); color: white; border-radius: 8px; padding: 0.6rem;
    }
    .stSlider > div > div > div > div { background-color: var(--accent); }
    
    /* Cards & Métriques */
    .card {
        background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
        padding: 1.25rem; box-shadow: 0 4px 16px rgba(0,0,0,0.25); transition: border-color 0.2s;
    }
    .card:hover { border-color: var(--accent); }
    .metric-label { font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.3rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); }
    .metric-delta { font-size: 0.85rem; margin-top: 0.4rem; font-weight: 500; }
    .delta-pos { color: var(--green); } .delta-neg { color: var(--red); }
    
    /* TradingView Container */
    .tv-wrapper { border-radius: 12px; overflow: hidden; border: 1px solid var(--border); background: var(--bg-card); }
    
    /* Sections & Alertes */
    h1, h2, h3 { color: var(--text-primary); font-weight: 600; margin-bottom: 0.5rem; }
    .section-title { border-left: 4px solid var(--accent); padding-left: 0.8rem; margin: 1.5rem 0 1rem; }
    .alert-box { padding: 1rem 1.2rem; border-radius: 8px; margin: 1rem 0; border: 1px solid; font-size: 0.95rem; }
    .alert-info { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.3); color: #60a5fa; }
    .alert-success { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: #34d399; }
    .alert-warning { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); color: #fbbf24; }
    .alert-danger { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.3); color: #f87171; }
    
    /* Override Streamlit defaults */
    .stDeployButton { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

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
    df = yf.Ticker(ticker).history(interval=interval, period=period)
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

def tv_widget(symbol, interval):
    # Mapping Yahoo -> TradingView
    tv_symbol = symbol.replace('.PA', ':EURONEXT').replace('.L', ':LSE').replace('.F', 'FRA:')
    tv_symbol = tv_symbol.replace('.DE', ':XETRA').replace('.CO', ':COPENHAGEN').replace('.AS', ':AMS')
    if ':' not in tv_symbol: tv_symbol = f"NASDAQ:{tv_symbol}"
    
    tv_interval = {'1wk': 'W', '1mo': 'M', '1d': 'D'}.get(interval, 'W')
    
    widget_html = f"""
    <div class="tradingview-widget-container" style="height:100%;width:100%">
      <div id="tv_chart_{symbol.replace('.','_')}"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{tv_symbol}", "interval": "{tv_interval}", "timezone": "Etc/UTC",
        "theme": "dark", "style": "1", "locale": "fr", "toolbar_bg": "#131620",
        "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
        "container_id": "tv_chart_{symbol.replace('.','_')}"
      }});
      </script>
    </div>
    """
    html(widget_html, height=580)

# 🖥️ INTERFACE PRINCIPALE
with st.sidebar:
    st.markdown("<h3 style='margin:0 0 1rem;'>⚙️ Paramètres</h3>", unsafe_allow_html=True)
    company = st.text_input("Entreprise", value="Apple")
    interval = st.selectbox("Unité de temps", ["1wk", "1mo", "1d"], index=0)
    hold_years = st.slider("Horizon (ans)", 1, 10, 3)
    currency = st.selectbox("Devise", ["$", "€", "£"], index=0)
    max_drop = st.slider("Baisse max vs ATH (%)", 50, 90, 81)
    analyze = st.button("🔍 LANCER L'ANALYSE", type="primary")
    st.markdown("---")
    st.caption("📊 Données Yahoo Finance | Moteur AlphaZone v2.1")

st.markdown("<h1 style='font-size:2rem; letter-spacing:-0.5px;'>🎯 AlphaZone <span style='color:#64748b; font-weight:400;'>| Scanner Long Terme</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; margin-top:-1rem;'>Détection algorithmique de zones d'accumulation institutionnelles.</p>", unsafe_allow_html=True)

if analyze:
    with st.spinner("Calcul des confluences techniques..."):
        ticker, full_name = resolve_ticker(company)
        if not ticker:
            st.error("❌ Actif introuvable. Vérifie l'orthographe.")
            st.stop()
            
        df = fetch_data(ticker, interval)
        current = df.iloc[-1]['Close']
        ath = df['High'].max()
        atl = df['Low'].min()
        
        fibs = calc_fib(ath, atl)
        rounds = find_rounds(current)
        demands = detect_demand(df)
        breakouts = detect_breakouts(df)
        
        candidates = [{'price': p, 'score': score_zone(p, fibs, rounds, demands, breakouts, ath, max_drop/100)} 
                      for p in df['Close']]
        candidates = [c for c in candidates if c['score'] > 0]
        
        min_allowed = ath * (1 - max_drop/100)
        best = max(candidates, key=lambda x: x['score']) if candidates else {'price': min_allowed, 'score': 0}
        
        z_mid = best['price']
        drop = ((z_mid - ath) / ath) * 100
        total_ret, annual_ret = backtest(df, z_mid, hold_years)
        
        # 📊 GRAHIQUE TRADINGVIEW
        st.markdown("<div class='tv-wrapper'>", unsafe_allow_html=True)
        tv_widget(ticker, interval)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 📈 MÉTRIQUES
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown("<div class='card'><div class='metric-label'>💰 Prix Actuel</div><div class='metric-value'>{:.2f}</div><div class='metric-delta delta-neg'>{:.1f}% vs ATH</div></div>".format(current, ((current-ath)/ath)*100), unsafe_allow_html=True)
        with c2: st.markdown("<div class='card'><div class='metric-label'>🚀 ATH Historique</div><div class='metric-value'>{:.2f}</div></div>".format(ath), unsafe_allow_html=True)
        with c3: st.markdown("<div class='card'><div class='metric-label'>🎯 Zone Optimale</div><div class='metric-value'>{:.2f}</div><div class='metric-delta delta-pos'>{:.1f}% vs ATH</div></div>".format(z_mid, drop), unsafe_allow_html=True)
        with c4: st.markdown("<div class='card'><div class='metric-label'>⭐ Score Confluence</div><div class='metric-value'>{:.0f}/100</div></div>".format(best['score']), unsafe_allow_html=True)
        
        # 🔍 CONFLUENCE & BACKTEST
        st.markdown("<h3 class='section-title'>🔍 Analyse Technique & Confluence</h3>", unsafe_allow_html=True)
        ca, cb, cc, cd = st.columns(4)
        with ca: st.markdown("<div class='card'><div class='metric-label'>🔢 Fibonacci</div><div class='metric-value' style='font-size:1rem;'>0.50: {:.2f}<br>0.618: {:.2f}</div></div>".format(fibs['0.500'], fibs['0.618']), unsafe_allow_html=True)
        with cb: st.markdown("<div class='card'><div class='metric-label'>⭕ Niveaux Ronds</div><div class='metric-value' style='font-size:0.9rem;'>{}</div></div>".format(', '.join([currency+str(round(r,1)) for r in rounds[:3]]) if len(rounds)>0 else 'Aucun',), unsafe_allow_html=True)
        with cc: st.markdown("<div class='card'><div class='metric-label'>📥 Zones de Demande</div><div class='metric-value' style='font-size:0.9rem;'>{}</div></div>".format(', '.join([currency+str(round(d,1)) for d in demands[:2]]) if len(demands)>0 else 'Aucune'), unsafe_allow_html=True)
        with cd: st.markdown("<div class='card'><div class='metric-label'>🚀 Breakout Retest</div><div class='metric-value' style='font-size:0.9rem;'>{}</div></div>".format(', '.join([currency+str(round(b,1)) for b in breakouts[:2]]) if len(breakouts)>0 else 'Aucun'), unsafe_allow_html=True)
        
        cx, cy = st.columns(2)
        with cx: st.markdown("<div class='card'><div class='metric-label'>📈 Rendement Total ({} ans)</div><div class='metric-value delta-pos'>+{:.1f}%</div></div>".format(hold_years, total_ret), unsafe_allow_html=True)
        with cy: st.markdown("<div class='card'><div class='metric-label'>💰 Annualisé</div><div class='metric-value delta-pos'>+{:.1f}% / an</div></div>".format(annual_ret), unsafe_allow_html=True)
        
        # 💡 INTERPRÉTATION
        st.markdown("<h3 class='section-title'>💡 Lecture Stratégique</h3>", unsafe_allow_html=True)
        if drop > -10:
            st.markdown("<div class='alert-box alert-warning'>⚠️ <b>Proche de l'ATH</b> : L'actif est en zone haute. Privilégiez un DCA progressif ou attendez un repli vers la zone optimale.</div>", unsafe_allow_html=True)
        elif drop > -max_drop + 5:
            st.markdown("<div class='alert-box alert-success'>✅ <b>Zone idéale</b> : Correction structurelle saine avec confluence technique forte. Opportunité d'accumulation long terme.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-box alert-danger'>🛑 <b>Proche du plancher</b> : La baisse dépasse les seuils historiques. Vérifiez impérativement les fondamentaux avant toute entrée.</div>", unsafe_allow_html=True)
            
        st.caption("⚖️ AlphaZone est un outil d'aide à la décision. Ne constitue pas un conseil financier.")
else:
    st.info("👈 Configurez vos paramètres dans la barre latérale et cliquez sur **LANCER L'ANALYSE** pour générer votre rapport.")