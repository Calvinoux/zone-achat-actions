import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import warnings
from streamlit.components.v1 import html

warnings.filterwarnings('ignore')
st.set_page_config(page_title="🎯 AlphaZone | Scanner Long Terme", layout="wide", page_icon="📈")

# 🎨 CSS PROFESSIONNEL (Centré, Interactif, Dark Mode)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    :root {
        --bg-main: #0b0e14; --bg-card: #131620; --bg-hover: #1a1e2e;
        --border: #222738; --text-primary: #e2e8f0; --text-secondary: #94a3b8;
        --accent: #3b82f6; --accent-hover: #2563eb; --accent-gradient: linear-gradient(135deg, #3b82f6, #6366f1);
        --green: #10b981; --red: #ef4444; --yellow: #f59e0b;
    }
    .main { background-color: var(--bg-main); color: var(--text-primary); font-family: 'Inter', system-ui, sans-serif; }
    header, footer, [data-testid="stDecoration"] { display: none !important; }
    
    /* PANNEAU DE CONTRÔLE CENTRÉ */
    .control-panel {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem auto;
        max-width: 880px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
        transition: transform 0.2s ease;
    }
    .control-panel:hover { transform: translateY(-2px); }
    .control-panel label { color: var(--text-secondary) !important; font-size: 0.85rem !important; font-weight: 500 !important; margin-bottom: 0.4rem !important; }
    .control-panel input, .control-panel select {
        background: var(--bg-main) !important; border: 1px solid var(--border) !important;
        color: var(--text-primary) !important; border-radius: 10px !important; padding: 0.6rem !important;
    }
    .control-panel .stSlider > div > div > div > div { background: var(--accent) !important; }
    
    /* BOUTON INTERACTIF */
    .control-panel .stButton > button {
        background: var(--accent-gradient) !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: 0.9rem 0 !important; font-weight: 600 !important; font-size: 1.05rem !important;
        width: 100% !important; cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        letter-spacing: 0.5px !important;
    }
    .control-panel .stButton > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.45) !important;
        filter: brightness(1.1) !important;
    }
    .control-panel .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* CARTES & RÉSULTATS */
    .card {
        background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px;
        padding: 1.2rem; box-shadow: 0 4px 16px rgba(0,0,0,0.25);
        transition: border-color 0.2s, transform 0.2s;
    }
    .card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .metric-label { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.3rem; }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }
    .metric-delta { font-size: 0.8rem; margin-top: 0.3rem; font-weight: 500; }
    .delta-pos { color: var(--green); } .delta-neg { color: var(--red); }
    
    /* GRAPHIQUE & SECTIONS */
    .tv-wrapper { border-radius: 14px; overflow: hidden; border: 1px solid var(--border); background: var(--bg-card); margin: 1.5rem 0; }
    .section-title { border-left: 4px solid var(--accent); padding-left: 0.8rem; margin: 1.5rem 0 1rem; font-size: 1.25rem; font-weight: 600; }
    
    /* ALERTES */
    .alert-box { padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; border: 1px solid; font-size: 0.95rem; animation: fadeIn 0.4s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
    .alert-info { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.3); color: #60a5fa; }
    .alert-success { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.3); color: #34d399; }
    .alert-warning { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.3); color: #fbbf24; }
    .alert-danger { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.3); color: #f87171; }
</style>
""", unsafe_allow_html=True)

# ───────── LOGIQUE MÉTIER (Inchangée) ─────────
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
    tv_symbol = symbol.replace('.PA', ':EURONEXT').replace('.L', ':LSE').replace('.F', 'FRA:')
    tv_symbol = tv_symbol.replace('.DE', ':XETRA').replace('.CO', ':COPENHAGEN').replace('.AS', ':AMS')
    if ':' not in tv_symbol: tv_symbol = f"NASDAQ:{tv_symbol}"
    tv_interval = {'1wk': 'W', '1mo': 'M', '1d': 'D'}.get(interval, 'W')
    
    widget_html = f"""
    <!DOCTYPE html>
    <html><head><style>
      html, body {{ margin: 0; padding: 0; height: 100%; background: #131620; }}
      .tv-container {{ height: 600px; width: 100%; border-radius: 12px; overflow: hidden; border: 1px solid #222738; }}
    </style></head>
    <body>
      <div class="tv-container">
        <div id="tv_{symbol.replace('.','_')}" style="height:100%; width:100%;"></div>
      </div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
        new TradingView.widget({{
          "autosize": true, "symbol": "{tv_symbol}", "interval": "{tv_interval}", "timezone": "Etc/UTC",
          "theme": "dark", "style": "1", "locale": "fr", "toolbar_bg": "#131620",
          "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
          "container_id": "tv_{symbol.replace('.','_')}"
        }});
      </script>
    </body></html>
    """
    st.components.v1.html(widget_html, height=610)

# 🖥️ INTERFACE PRINCIPALE
st.markdown("<h1 style='text-align:center; font-size:2.2rem; letter-spacing:-0.5px; margin-top:1rem;'>🎯 AlphaZone <span style='color:#64748b; font-weight:400;'>| Scanner Long Terme</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; margin-top:-0.5rem; margin-bottom:1rem;'>Détection algorithmique de zones d'accumulation institutionnelles.</p>", unsafe_allow_html=True)

# 🎛️ PANNEAU DE CONTRÔLE CENTRÉ
with st.container():
    st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
    col_main, col_btn = st.columns([1, 1])
    with col_main:
        company = st.text_input("🏢 Nom de l'entreprise", value="Apple", key="company")
    with col_btn:
        st.write("")
        analyze = st.button("🔍 LANCER L'ANALYSE", type="primary", use_container_width=True, key="analyze")
    
    c1, c2, c3 = st.columns(3)
    with c1: interval = st.selectbox("⏱️ Unité de temps", ["1wk", "1mo", "1d"], index=0, key="interval")
    with c2: currency = st.selectbox("💱 Devise", ["$", "€", "£"], index=0, key="currency")
    with c3: max_drop = st.slider("📉 Baisse max vs ATH (%)", 50, 90, 81, key="max_drop")
    
    hold_years = st.slider("📅 Horizon de détention (ans)", 1, 10, 3, key="hold_years")
    st.markdown("</div>", unsafe_allow_html=True)

if analyze:
    with st.spinner("⚙️ Calcul des confluences techniques..."):
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
        
        # 📊 GRAPHIQUE TRADINGVIEW
        st.markdown("<div class='tv-wrapper'>", unsafe_allow_html=True)
        tv_widget(ticker, interval)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 📈 MÉTRIQUES
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"<div class='card'><div class='metric-label'>💰 Prix Actuel</div><div class='metric-value'>{current:.2f}</div><div class='metric-delta delta-neg'>{((current-ath)/ath)*100:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='card'><div class='metric-label'>🚀 ATH Historique</div><div class='metric-value'>{ath:.2f}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='card'><div class='metric-label'>🎯 Zone Optimale</div><div class='metric-value'>{z_mid:.2f}</div><div class='metric-delta delta-pos'>{drop:.1f}% vs ATH</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='card'><div class='metric-label'>⭐ Score Confluence</div><div class='metric-value'>{best['score']:.0f}/100</div></div>", unsafe_allow_html=True)
        
        # 🔍 CONFLUENCE
        st.markdown("<h3 class='section-title'>🔍 Analyse Technique & Confluence</h3>", unsafe_allow_html=True)
        ca, cb, cc, cd = st.columns(4)
        with ca: st.markdown(f"<div class='card'><div class='metric-label'>🔢 Fibonacci</div><div class='metric-value' style='font-size:0.95rem;'>0.50: {fibs['0.500']:.2f}<br>0.618: {fibs['0.618']:.2f}</div></div>", unsafe_allow_html=True)
        with cb: st.markdown(f"<div class='card'><div class='metric-label'>⭕ Niveaux Ronds</div><div class='metric-value' style='font-size:0.9rem;'>{', '.join([currency+str(round(r,1)) for r in rounds[:3]]) if len(rounds)>0 else 'Aucun'}</div></div>", unsafe_allow_html=True)
        with cc: st.markdown(f"<div class='card'><div class='metric-label'>📥 Zones de Demande</div><div class='metric-value' style='font-size:0.9rem;'>{', '.join([currency+str(round(d,1)) for d in demands[:2]]) if len(demands)>0 else 'Aucune'}</div></div>", unsafe_allow_html=True)
        with cd: st.markdown(f"<div class='card'><div class='metric-label'>🚀 Breakout Retest</div><div class='metric-value' style='font-size:0.9rem;'>{', '.join([currency+str(round(b,1)) for b in breakouts[:2]]) if len(breakouts)>0 else 'Aucun'}</div></div>", unsafe_allow_html=True)
        
        cx, cy = st.columns(2)
        with cx: st.markdown(f"<div class='card'><div class='metric-label'>📈 Rendement Total ({hold_years} ans)</div><div class='metric-value delta-pos'>+{total_ret:.1f}%</div></div>", unsafe_allow_html=True)
        with cy: st.markdown(f"<div class='card'><div class='metric-label'>💰 Annualisé</div><div class='metric-value delta-pos'>+{annual_ret:.1f}% / an</div></div>", unsafe_allow_html=True)
        
        # 💡 LECTURE STRATÉGIQUE
        st.markdown("<h3 class='section-title'>💡 Lecture Stratégique</h3>", unsafe_allow_html=True)
        if drop > -10:
            st.markdown("<div class='alert-box alert-warning'>⚠️ <b>Proche de l'ATH</b> : L'actif est en zone haute. Privilégiez un DCA progressif ou attendez un repli vers la zone optimale.</div>", unsafe_allow_html=True)
        elif drop > -max_drop + 5:
            st.markdown("<div class='alert-box alert-success'>✅ <b>Zone idéale</b> : Correction structurelle saine avec confluence technique forte. Opportunité d'accumulation long terme.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-box alert-danger'>🛑 <b>Proche du plancher</b> : La baisse dépasse les seuils historiques. Vérifiez impérativement les fondamentaux avant toute entrée.</div>", unsafe_allow_html=True)
            
        st.caption("⚖️ AlphaZone est un outil d'aide à la décision. Ne constitue pas un conseil financier.")
else:
    st.info("👈 Configurez vos paramètres dans le panneau ci-dessus et cliquez sur **LANCER L'ANALYSE** pour générer votre rapport.")