#!/usr/bin/env python3
"""
Alpha Terminal Pro - Professional Financial Analysis Platform
Version: 2.0 (Production Ready - Fixed & Completed)
Author: Lassenza29 & Gemini
Description: Complete financial analysis with 21 ratios, ETF analysis, DCA simulator, comparator, and news feed
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
from typing import Dict, Tuple, Optional, List
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG & THEME
# ============================================================================

st.set_page_config(
    page_title="Alpha Terminal Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode Custom CSS
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body, [data-testid="stAppViewContainer"] {
        background-color: #0a0e27 !important;
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1f3a !important;
    }
    
    [data-testid="stMetric"] {
        background-color: #1a1f3a;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #00d4ff;
        margin: 5px 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1f3a 0%, #252f4d 100%);
        border: 1px solid #00d4ff;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        color: #e0e0e0;
    }
    
    .score-card {
        background: linear-gradient(135deg, #1a3a3a 0%, #2d4d4d 100%);
        border: 2px solid #00ff88;
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        margin: 15px 0;
    }
    
    .ratio-section {
        background-color: #1a1f3a;
        border-left: 4px solid #ff6b6b;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .header-title {
        color: #00d4ff;
        font-size: 32px;
        font-weight: bold;
        margin: 20px 0;
    }
    
    .subheader {
        color: #00ff88;
        font-size: 20px;
        margin: 15px 0;
    }
    
    h1, h2, h3 {
        color: #00d4ff !important;
    }
    
    [data-testid="stTabs"] [role="tablist"] button {
        background-color: #1a1f3a;
        border: 1px solid #333;
        color: #e0e0e0;
        padding: 10px 20px;
        margin: 5px;
        border-radius: 5px;
    }
    
    [data-testid="stTabs"] [role="tablist"] button[aria-selected="true"] {
        background-color: #00d4ff;
        color: #0a0e27;
        border: 1px solid #00d4ff;
    }
    
    .stDataFrame {
        background-color: #1a1f3a !important;
    }
    
    table {
        background-color: #1a1f3a !important;
        color: #e0e0e0 !important;
    }
    
    .stButton > button {
        background-color: #00d4ff;
        color: #0a0e27;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #00ff88;
        color: #0a0e27;
    }
    
    .stTextInput > div > div > input {
        background-color: #1a1f3a;
        color: #e0e0e0;
        border: 1px solid #333;
    }
    
    .success-box {
        background-color: #1a3a2a;
        border: 2px solid #00ff88;
        border-radius: 8px;
        padding: 20px;
        color: #00ff88;
        margin: 15px 0;
    }
    
    .warning-box {
        background-color: #3a2a1a;
        border: 2px solid #ffaa00;
        border-radius: 8px;
        padding: 15px;
        color: #ffaa00;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #3a1a1a;
        border: 2px solid #ff6b6b;
        border-radius: 8px;
        padding: 15px;
        color: #ff6b6b;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# UTILITY FUNCTIONS - DATA PARSING & FORMATTING
# ============================================================================

def safe_float(value: any, default: float = 0.0) -> float:
    """Safely convert any value to float"""
    if value is None or pd.isna(value):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value: any, default: str = "N/A") -> str:
    """Safely convert any value to string"""
    if value is None or pd.isna(value):
        return default
    try:
        return str(value).strip()
    except:
        return default

def safe_pct(value: any, default: str = "N/A") -> str:
    """Safely format percentage"""
    try:
        num = safe_float(value)
        if num == 0.0 and value is None:
            return default
        return f"{num:.2f}%"
    except:
        return default

def format_currency(value: float, currency: str = "€", decimals: int = 2) -> str:
    """Format currency with proper symbols"""
    if value is None or pd.isna(value):
        return "N/A"
    try:
        if abs(value) >= 1_000_000_000:
            return f"{currency}{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{currency}{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{currency}{value / 1_000:.2f}K"
        else:
            return f"{currency}{value:.{decimals}f}"
    except:
        return "N/A"

def format_large_number(value: float) -> str:
    """Format large numbers (millions, billions)"""
    if value is None or pd.isna(value):
        return "N/A"
    try:
        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"
        else:
            return f"{value:.2f}"
    except:
        return "N/A"

# ============================================================================
# CURRENCY CONVERSION MODULE
# ============================================================================

CURRENCY_FALLBACKS = {
    "USD": 0.92,
    "GBP": 1.17,
    "CHF": 1.03,
    "CAD": 0.67,
    "JPY": 0.0067,
    "AUD": 0.60,
    "SGD": 0.68,
    "HKD": 0.118,
    "INR": 0.011,
    "BRL": 0.18,
    "EUR": 1.0,
}

@st.cache_data(ttl=3600)
def get_exchange_rate(from_currency: str, to_currency: str = "EUR") -> float:
    """Get exchange rate with fallback values"""
    if from_currency == to_currency:
        return 1.0
    try:
        pair = f"{from_currency}{to_currency}=X"
        rate_ticker = yf.Ticker(pair)
        rate = rate_ticker.info.get('currentPrice')
        if rate and rate > 0:
            return float(rate)
    except:
        pass
    if from_currency in CURRENCY_FALLBACKS:
        return CURRENCY_FALLBACKS[from_currency]
    return 1.0

def detect_currency(ticker: str) -> str:
    """Detect currency from ticker suffix"""
    ticker_upper = ticker.upper()
    if ticker_upper.endswith('.PA'): return "EUR"
    elif ticker_upper.endswith('.L'): return "GBP"
    elif ticker_upper.endswith('.DE'): return "EUR"
    elif ticker_upper.endswith('.AS'): return "EUR"
    elif ticker_upper.endswith('.TO'): return "CAD"
    elif ticker_upper.endswith('.AX'): return "AUD"
    elif ticker_upper.endswith('.HK'): return "HKD"
    elif ticker_upper.endswith('.SI'): return "SGD"
    else: return "USD"

def convert_to_eur(value: float, currency: str) -> float:
    """Convert any currency to EUR"""
    if value is None or pd.isna(value):
        return 0.0
    rate = get_exchange_rate(currency, "EUR")
    return value * rate

# ============================================================================
# MODULE 1: FUNDAMENTAL ANALYSIS - 21 RATIOS
# ============================================================================

@st.cache_data(ttl=300)
def get_ticker_data(ticker: str) -> Tuple[Optional[yf.Ticker], Dict]:
    """Fetch ticker data with error handling"""
    try:
        tick = yf.Ticker(ticker)
        info = tick.info
        return tick, info
    except Exception as e:
        return None, {}

def calculate_fundamental_ratios(ticker_obj: yf.Ticker, info: Dict, currency: str) -> Dict:
    """Calculate all 21 fundamental ratios"""
    ratios = {}
    try:
        # ===== SECTION A: VALORISATION (8 ratios) =====
        trailing_pe = safe_float(info.get('trailingPE'))
        ratios['trailing_pe'] = trailing_pe if trailing_pe > 0 else None
        
        forward_pe = safe_float(info.get('forwardPE'))
        ratios['forward_pe'] = forward_pe if forward_pe > 0 else None
        
        ps_ratio = safe_float(info.get('priceToSalesTrailing12Months'))
        ratios['ps_ratio'] = ps_ratio if ps_ratio > 0 else None
        
        pb_ratio = safe_float(info.get('priceToBook'))
        ratios['pb_ratio'] = pb_ratio if pb_ratio > 0 else None
        
        ev_ebitda = safe_float(info.get('enterpriseToEbitda'))
        ratios['ev_ebitda'] = ev_ebitda if ev_ebitda > 0 else None
        
        eps = safe_float(info.get('trailingEps'))
        eps_eur = convert_to_eur(eps, currency) if eps > 0 else 0
        ratios['eps_eur'] = eps_eur if eps_eur > 0 else None
        
        book_value = safe_float(info.get('bookValue'))
        book_value_eur = convert_to_eur(book_value, currency) if book_value > 0 else 0
        ratios['book_value_eur'] = book_value_eur if book_value_eur > 0 else None
        
        if eps_eur and book_value_eur and eps_eur > 0 and book_value_eur > 0:
            try:
                ratios['graham_price'] = np.sqrt(22.5 * eps_eur * book_value_eur)
            except:
                ratios['graham_price'] = None
        else:
            ratios['graham_price'] = None
        
        # ===== SECTION B: RENTABILITÉ (5 ratios) =====
        gross_margin = safe_float(info.get('grossMargins'))
        ratios['gross_margin'] = gross_margin * 100 if gross_margin else None
        
        operating_margin = safe_float(info.get('operatingMargins'))
        ratios['operating_margin'] = operating_margin * 100 if operating_margin else None
        
        profit_margin = safe_float(info.get('profitMargins'))
        ratios['profit_margin'] = profit_margin * 100 if profit_margin else None
        
        roe = safe_float(info.get('returnOnEquity'))
        ratios['roe'] = roe * 100 if roe else None
        
        roa = safe_float(info.get('returnOnAssets'))
        ratios['roa'] = roa * 100 if roa else None
        
        # ===== SECTION C: SANTÉ FINANCIÈRE (6 ratios) =====
        total_debt = safe_float(info.get('totalDebt'))
        cash = safe_float(info.get('totalCash'))
        net_debt = (total_debt - cash) / 1_000_000 if total_debt or cash else 0.0
        ratios['net_debt_m_eur'] = net_debt
        
        ebitda = safe_float(info.get('ebitda'))
        ebitda_m = ebitda / 1_000_000 if ebitda else None
        ratios['ebitda_m_eur'] = ebitda_m
        
        if net_debt < 0:
            ratios['debt_ebitda_ratio'] = "Cash Positif"
        elif ebitda_m and ebitda_m > 0:
            ratios['debt_ebitda_ratio'] = net_debt / ebitda_m
        else:
            ratios['debt_ebitda_ratio'] = None
            
        ratios['current_ratio'] = safe_float(info.get('currentRatio')) if safe_float(info.get('currentRatio')) > 0 else None
        ratios['quick_ratio'] = safe_float(info.get('quickRatio')) if safe_float(info.get('quickRatio')) > 0 else None
        
        debt_to_equity = safe_float(info.get('debtToEquity'))
        ratios['debt_to_equity'] = debt_to_equity * 100 if debt_to_equity else None
        
        # ===== SECTION D: CROISSANCE & DIVIDENDES (2 ratios) =====
        revenue_growth = safe_float(info.get('revenueGrowth'))
        ratios['revenue_growth'] = revenue_growth * 100 if revenue_growth else None
        
        payout_ratio = safe_float(info.get('payoutRatio'))
        ratios['payout_ratio'] = payout_ratio * 100 if payout_ratio else None
        
    except Exception as e:
        st.warning(f"⚠️ Alerte calcul ratios: {str(e)}")
    return ratios

def calculate_fundamental_score(ratios: Dict, current_price: float, currency: str) -> Tuple[int, Dict]:
    """Calculate Fundamental Score (0-100) based on strict rules"""
    score = 0
    score_details = {}
    
    if ratios.get('trailing_pe') and 0 < ratios['trailing_pe'] < 20:
        score += 15
        score_details['PER Attractif'] = '+15'
    
    debt_ebitda = ratios.get('debt_ebitda_ratio')
    if isinstance(debt_ebitda, str) and "Cash" in debt_ebitda:
        score += 15
        score_details['Cash Positif'] = '+15'
    elif isinstance(debt_ebitda, (int, float)) and debt_ebitda < 2:
        score += 15
        score_details['Levier Sain'] = '+15'
        
    if ratios.get('roe') and ratios['roe'] > 15:
        score += 15
        score_details['ROE Excellent'] = '+15'
        
    if ratios.get('profit_margin') and ratios['profit_margin'] > 12:
        score += 15
        score_details['Marge Nette Saine'] = '+15'
        
    if ratios.get('graham_price') and ratios['graham_price'] > current_price:
        score += 10
        score_details['Graham Favorable'] = '+10'
        
    if ratios.get('revenue_growth') and ratios['revenue_growth'] > 5:
        score += 10
        score_details['Croissance Positive'] = '+10'
        
    if ratios.get('current_ratio') and ratios['current_ratio'] > 1.5:
        score += 5
        score_details['Liquidité Bonne'] = '+5'
        
    if ratios.get('payout_ratio') and ratios['payout_ratio'] < 60:
        score += 5
        score_details['Dividende Soutenable'] = '+5'
        
    return min(score, 100), score_details

def get_analyst_consensus(info: Dict) -> Dict:
    return {
        'target_price': safe_float(info.get('targetMeanPrice')),
        'num_analysts': safe_float(info.get('numberOfAnalysts')),
        'recommendation': safe_str(info.get('recommendationKey', 'N/A')).upper(),
    }

# ============================================================================
# MODULE 2: ETF ANALYSIS
# ============================================================================

def is_etf(info: Dict, ticker: str) -> bool:
    quote_type = safe_str(info.get('quoteType', '')).upper()
    if quote_type == 'ETF': return True
    if 'fund' in safe_str(info.get('category', '')).lower(): return True
    return False

def analyze_etf(ticker_obj: yf.Ticker, info: Dict) -> Dict:
    etf_data = {
        'ter': safe_float(info.get('expenseRatio')) * 100 if info.get('expenseRatio') else 0.0,
        'aum': safe_float(info.get('totalAssets')),
        'distribution': safe_str(info.get('distributionType', 'Accumulation (Acc)')),
        'replication': safe_str(info.get('replicationMethod', 'Physique (Réel)')),
    }
    ticker_upper = ticker_obj.ticker.upper()
    etf_data['pea_eligible'] = ticker_upper.endswith('.PA') or "PEA" in safe_str(info.get('longName', '')).upper()
    etf_data['closure_risk'] = etf_data['aum'] > 0 and etf_data['aum'] < 100_000_000
    return etf_data

# ============================================================================
# MODULE 3: MULTI-ASSET COMPARATOR
# ============================================================================

@st.cache_data(ttl=300)
def create_comparison_df(tickers: List[str]) -> pd.DataFrame:
    data = []
    for ticker in tickers:
        ticker = ticker.strip().upper()
        try:
            tick_obj, info = get_ticker_data(ticker)
            if not info: continue
            currency = detect_currency(ticker)
            current_price = safe_float(info.get('currentPrice') or info.get('previousClose'))
            ratios = calculate_fundamental_ratios(tick_obj, info, currency)
            score, _ = calculate_fundamental_score(ratios, current_price, currency)
            market_cap = safe_float(info.get('marketCap') or info.get('totalAssets'))
            
            data.append({
                'Ticker': ticker,
                'Prix €': f"{convert_to_eur(current_price, currency):.2f} €",
                'Capitalisation / Assets': format_large_number(convert_to_eur(market_cap, currency)),
                'Score Fondamental': score,
                'PER': f"{ratios.get('trailing_pe'):.1f}" if ratios.get('trailing_pe') else 'N/A',
                'Marge Nette': safe_pct(ratios.get('profit_margin')),
                'ROE': safe_pct(ratios.get('roe')),
                'Dette/EBITDA': f"{ratios.get('debt_ebitda_ratio'):.2f}" if isinstance(ratios.get('debt_ebitda_ratio'), (int, float)) else str(ratios.get('debt_ebitda_ratio', 'N/A')),
            })
        except:
            continue
    return pd.DataFrame(data).sort_values('Score Fondamental', ascending=False) if data else pd.DataFrame()

# ============================================================================
# MODULE 4: DCA SIMULATOR (HIGH PRECISION)
# ============================================================================

def simulate_dca(ticker: str, monthly_amount: float, years: int) -> Tuple[pd.DataFrame, Dict]:
    try:
        tick_obj = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)
        hist = tick_obj.history(start=start_date, end=end_date)
        
        if hist.empty: return pd.DataFrame(), {}
        
        hist['YearMonth'] = hist.index.to_period('M')
        monthly_data = hist.groupby('YearMonth').first()
        
        shares_owned, total_invested = 0.0, 0.0
        portfolio_values, dates, invested_values = [], [], []
        
        for date, row in monthly_data.iterrows():
            price = safe_float(row.get('Close'))
            if price <= 0: continue
            shares_owned += monthly_amount / price
            total_invested += monthly_amount
            dates.append(date.to_timestamp())
            invested_values.append(total_invested)
            portfolio_values.append(shares_owned * price)
            
        df_results = pd.DataFrame({'Date': dates, 'Total Investi': invested_values, 'Valeur Portefeuille': portfolio_values})
        final_value = portfolio_values[-1] if portfolio_values else 0
        gain_loss = final_value - total_invested
        
        return df_results, {
            'shares': shares_owned, 'final_invested': total_invested,
            'final_value': final_value, 'gain_loss': gain_loss,
            'roi': (gain_loss / total_invested * 100) if total_invested > 0 else 0
        }
    except:
        return pd.DataFrame(), {}

# ============================================================================
# MODULE 5: NEWS FEED
# ============================================================================

def get_news_feed(ticker_obj: yf.Ticker) -> List[Dict]:
    try:
        news = ticker_obj.news
        if not news: return []
        articles = []
        for item in news[:10]:
            pub_time = item.get('providerPublishTime')
            try:
                date_str = datetime.fromtimestamp(int(pub_time)).strftime('%d/%m/%Y %H:%M') if pub_time else "N/A"
            except:
                date_str = "N/A"
            articles.append({
                'title': safe_str(item.get('title')),
                'link': safe_str(item.get('link')),
                'source': safe_str(item.get('source')),
                'published': date_str,
            })
        return articles
    except:
        return []

# ============================================================================
# MODULE 6: TECHNICAL ANALYSIS (SMA 50/200 + RSI)
# ============================================================================

def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    return data.rolling(window=window).mean()

def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def plot_technical_analysis(ticker: str) -> Optional[go.Figure]:
    try:
        tick_obj = yf.Ticker(ticker)
        hist = tick_obj.history(start=datetime.now() - timedelta(days=1825), end=datetime.now())
        if hist.empty or len(hist) < 200: return None
        
        hist['SMA50'] = calculate_sma(hist['Close'], 50)
        hist['SMA200'] = calculate_sma(hist['Close'], 200)
        hist['RSI'] = calculate_rsi(hist['Close'], 14)
        
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
        
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Prix', line=dict(color='#00d4ff', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA50'], name='SMA 50', line=dict(color='#ff6b6b', width=1, dash='dot')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA200'], name='SMA 200', line=dict(color='#00ff88', width=1, dash='dash')), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name='RSI', line=dict(color='#ffaa00', width=2)), row=2, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="#ff6b6b", annotation_text="Suracheté (70)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", annotation_text="Survendu (30)", row=2, col=1)
        
        fig.update_layout(template="plotly_dark", hovermode="x unified", height=600, paper_bgcolor='#0a0e27', plot_bgcolor='#1a1f3a')
        return fig
    except:
        return None

# ============================================================================
# DISPLAY COMPONENT CARDS
# ============================================================================

def display_metric_card(label: str, value: str, color: str = "#00d4ff") -> None:
    st.markdown(f"""
    <div style="background-color: #1a1f3a; border-left: 4px solid {color}; padding: 15px; border-radius: 5px; margin: 5px 0;">
        <p style="color: #999; font-size: 12px; margin: 0;">{label}</p>
        <p style="color: {color}; font-size: 18px; font-weight: bold; margin: 5px 0;">{value}</p>
    </div>
    """, unsafe_allow_html=True)

def display_score_card(score: int) -> None:
    color = "#00ff88" if score >= 70 else "#ffaa00" if score >= 50 else "#ff6b6b"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a3a3a 0%, #2d4d4d 100%); border: 2px solid {color}; border-radius: 10px; padding: 20px; text-align: center; margin: 10px 0;">
        <p style="color: #999; font-size: 13px; margin: 0;">SCORE FONDAMENTAL GLOBAL</p>
        <p style="color: {color}; font-size: 42px; font-weight: bold; margin: 5px 0;">{score}/100</p>
        <div style="background-color: #0a0e27; height: 6px; border-radius: 3px; overflow: hidden;">
            <div style="background-color: {color}; height: 100%; width: {score}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION ENGINE
# ============================================================================

def main():
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <h1 style="color: #00d4ff; font-size: 42px; margin: 0;">📈 Alpha Terminal Pro</h1>
        <p style="color: #999; font-size: 13px; margin-top: 5px;">Terminal Financier Professionnel d'Analyse Quantitative | v2.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🎯 Navigation")
    mode = st.sidebar.radio(
        "Sélectionnez le mode:",
        ["📊 Analyse Complète", "⚖️ Comparateur", "💰 DCA Simulator", "📰 Actualités"],
        label_visibility="collapsed"
    )
    
    # Résolution du bug de rechargement Streamlit via Session State
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = ""

    if mode == "📊 Analyse Complète":
        st.markdown("### 🔍 Analyse Individuelle de Valeur")
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            ticker_input = st.text_input("Saisir un Ticker (ex: AAPL, LVMH.PA, CW8.PA) :", value=st.session_state.active_ticker, label_visibility="collapsed").strip().upper()
        with col_s2:
            if st.button("Rechercher", use_container_width=True) and ticker_input:
                st.session_state.active_ticker = ticker_input
                
        if st.session_state.active_ticker:
            tk = st.session_state.active_ticker
            with st.spinner(f"Extraction des bases financières pour {tk}..."):
                tick_obj, info = get_ticker_data(tk)
                
                if not info:
                    st.error("❌ Ticker introuvable ou erreur de communication avec l'API.")
                else:
                    currency = detect_currency(tk)
                    price = safe_float(info.get('currentPrice') or info.get('navPrice') or info.get('previousClose'))
                    price_eur = convert_to_eur(price, currency)
                    is_fund = is_etf(info, tk)
                    
                    st.markdown("---")
                    c_left, c_right = st.columns([2, 1])
                    with c_left:
                        st.markdown(f"## {info.get('longName', tk)}")
                        st.markdown(f"**Secteur :** {info.get('sector', info.get('category', 'N/A'))} | **Devise :** {currency}")
                        
                        cm1, cm2 = st.columns(2)
                        with cm1: display_metric_card("Cours Actuel", f"{price_eur:.2f} €", "#00d4ff")
                        with cm2: 
                            cap = safe_float(info.get('marketCap') or info.get('totalAssets'))
                            display_metric_card("Capitalisation / Encours", format_currency(convert_to_eur(cap, currency)), "#00ff88")
                    
                    with c_right:
                        if not is_fund:
                            ratios = calculate_fundamental_ratios(tick_obj, info, currency)
                            score, _ = calculate_fundamental_score(ratios, price_eur, currency)
                            display_score_card(score)
                        else:
                            st.markdown("""<div style="background: #1a2f4d; border:1px solid #00d4ff; padding:20px; border-radius:8px; text-align:center;"><h4>Fonds Indexé / ETF</h4><p style="color:#999; font-size:12px;">Filtre analytique pour trackers appliqué</p></div>""", unsafe_allow_html=True)
                    
                    # Ratios ou Spécificités ETF
                    if not is_fund:
                        ratios = calculate_fundamental_ratios(tick_obj, info, currency)
                        t_rat, t_tech, t_con = st.tabs(["📊 Ratios Financiers", "📈 Graphique Technique", "🤝 Consensus"])
                        
                        with t_rat:
                            st.markdown("#### A. Valorisation & Prix")
                            r1, r2, r3, r4 = st.columns(4)
                            r1.metric("1. PER Actuel", f"{ratios.get('trailing_pe') or 'N/A'}")
                            r2.metric("2. PER Futur", f"{ratios.get('forward_pe') or 'N/A'}")
                            r3.metric("3. Price to Sales", f"{ratios.get('ps_ratio') or 'N/A'}")
                            r4.metric("4. Price to Book", f"{ratios.get('pb_ratio') or 'N/A'}")
                            
                            r5, r6, r7, r8 = st.columns(4)
                            r5.metric("5. EV/EBITDA", f"{ratios.get('ev_ebitda') or 'N/A'}")
                            r6.metric("6. BPA (€)", f"{ratios.get('eps_eur'):.2f} €" if ratios.get('eps_eur') else "N/A")
                            r7.metric("7. Valeur Comptable/Action", f"{ratios.get('book_value_eur'):.2f} €" if ratios.get('book_value_eur') else "N/A")
                            r8.metric("8. Prix Graham", f"{ratios.get('graham_price'):.2f} €" if ratios.get('graham_price') else "N/A")
                            
                            st.markdown("#### B. Rentabilité")
                            r9, r10, r11, r12, r13 = st.columns(5)
                            r9.metric("9. Marge Brute", safe_pct(ratios.get('gross_margin')))
                            r10.metric("10. Marge Opér.", safe_pct(ratios.get('operating_margin')))
                            r11.metric("11. Marge Nette", safe_pct(ratios.get('profit_margin')))
                            r12.metric("12. ROE", safe_pct(ratios.get('roe')))
                            r13.metric("13. ROA", safe_pct(ratios.get('roa')))
                            
                            st.markdown("#### C. Bilan & Santé Financière")
                            r14, r15, r16 = st.columns(3)
                            r14.metric("14. Dette Nette", f"{ratios.get('net_debt_m_eur'):.1f} M€" if ratios.get('net_debt_m_eur') else "N/A")
                            r15.metric("15. EBITDA", f"{ratios.get('ebitda_m_eur'):.1f} M€" if ratios.get('ebitda_m_eur') else "N/A")
                            deb_eb = ratios.get('debt_ebitda_ratio')
                            r16.metric("16. Dette Nette / EBITDA", f"{deb_eb:.2f}" if isinstance(deb_eb, (int, float)) else str(deb_eb or 'N/A'))
                            
                            r17, r18, r19 = st.columns(3)
                            r17.metric("17. Liquidité Générale", f"{ratios.get('current_ratio') or 'N/A'}")
                            r18.metric("18. Liquidité Immédiate", f"{ratios.get('quick_ratio') or 'N/A'}")
                            r19.metric("19. Dette / Cap. Propres", safe_pct(ratios.get('debt_to_equity')))
                            
                            st.markdown("#### D. Croissance & Dividende")
                            r20, r21 = st.columns(2)
                            r20.metric("20. Croissance CA", safe_pct(ratios.get('revenue_growth')))
                            r21.metric("21. Payout Ratio", safe_pct(ratios.get('payout_ratio')))
                        
                        with t_tech:
                            fig = plot_technical_analysis(tk)
                            if fig: st.plotly_chart(fig, use_container_width=True)
                            else: st.info("Historique insuffisant pour tracer les indicateurs techniques.")
                        
                        with t_con:
                            con = get_analyst_consensus(info)
                            rc1, rc2, rc3 = st.columns(3)
                            rc1.metric("Objectif Moyen", f"{convert_to_eur(con['target_price'], currency):.2f} €" if con['target_price'] else "N/A")
                            rc2.metric("Nombre de Suivis", f"{con['num_analysts'] or 'N/A'}")
                            rc3.metric("Avis global", con['recommendation'])
                    else:
                        st.markdown("#### 🛠️ Analyse Trackers (ETF)")
                        etf_m = analyze_etf(tick_obj, info)
                        e1, e2, e3, e4, e5 = st.columns(5)
                        e1.metric("Frais (TER)", f"{etf_m['ter']:.2f}%")
                        e2.metric("Encours", format_large_number(convert_to_eur(etf_m['aum'], currency)))
                        e3.metric("Distribution", etf_m['distribution'])
                        e4.metric("Réplication", etf_m['replication'])
                        e5.metric("Éligibilité PEA", "Oui ✅" if etf_m['pea_eligible'] else "Non (CTO) ❌")
                        
                        if etf_m['closure_risk']:
                            st.markdown("""<div class="warning-box">⚠️ <strong>Alerte Liquidité :</strong> Encours inférieur à 100M€. Risque accru de fermeture ou spreads élevés.</div>""", unsafe_allow_html=True)

    elif mode == "⚖️ Comparateur":
        st.markdown("### ⚖️ Matrice Comparative Multi-Actifs")
        tk_list_str = st.text_input("Entrez les tickers séparés par des virgules :", "AAPL, MSFT, LVMH.PA, NVDA")
        if tk_list_str:
            parsed_list = [t.strip() for t in tk_list_str.split(",") if t.strip()]
            res_df = create_comparison_df(parsed_list)
            if not res_df.empty:
                st.dataframe(res_df, use_container_width=True)
                csv = res_df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exporter en CSV", data=csv, file_name="alpha_export.csv", mime="text/csv")
            else:
                st.info("Aucune donnée disponible pour ces valeurs.")

    elif mode == "💰 DCA Simulator":
        st.markdown("### 💰 Simulateur DCA Historique")
        c_d1, c_d2, c_d3 = st.columns(3)
        d_tk = c_d1.text_input("Ticker cible :", "AAPL").strip().upper()
        d_amt = c_d2.number_input("Versement Mensuel (€) :", min_value=10.0, value=150.0)
        d_y = c_d3.slider("Historique (Années) :", min_value=1, max_value=15, value=5)
        
        if st.button("Lancer la simulation", use_container_width=True):
            df_dca, metrics = simulate_dca(d_tk, d_amt, d_y)
            if not df_dca.empty:
                st.markdown(f"""
                <div class="success-box">
                    <h4>Résultats de la stratégie DCA ({d_tk})</h4>
                    <p>Total Investi : {metrics['final_invested']:.2f} € | Valeur Finale : {metrics['final_value']:.2f} €</p>
                    <p>Performance : <strong style="color: {'#00ff88' if metrics['gain_loss'] >= 0 else '#ff6b6b'}">{metrics['gain_loss']:.2f} € ({metrics['roi']:.2f}%)</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                fig_dca = go.Figure()
                fig_dca.add_trace(go.Scatter(x=df_dca['Date'], y=df_dca['Total Investi'], name="Capital Versé", line=dict(color='#ff6b6b', width=2, dash='dash')))
                fig_dca.add_trace(go.Scatter(x=df_dca['Date'], y=df_dca['Valeur Portefeuille'], name="Valeur de la Poche", line=dict(color='#00ff88', width=3), fill='tonexty', fillcolor='rgba(0, 255, 136, 0.04)'))
                fig_dca.update_layout(template="plotly_dark", height=400, paper_bgcolor='#0a0e27', plot_bgcolor='#1a1f3a')
                st.plotly_chart(fig_dca, use_container_width=True)
            else:
                st.error("Impossible de simuler l'historique de ce actif.")

    elif mode == "📰 Actualités":
        st.markdown("### 📰 Actualités de Marché")
        news_tk = st.text_input("Entrer le Ticker pour voir ses News :", value=st.session_state.active_ticker if st.session_state.active_ticker else "AAPL").strip().upper()
        if news_tk:
            t_obj, _ = get_ticker_data(news_tk)
            if t_obj:
                feed = get_news_feed(t_obj)
                if feed:
                    for art in feed:
                        st.markdown(f"""
                        <div style="background-color: #1a1f3a; padding: 12px; border-radius: 6px; margin: 8px 0; border-left: 3px solid #ffaa00;">
                            <h5 style="margin: 0;"><a href="{art['link']}" target="_blank" style="color: #00d4ff; text-decoration: none;">{art['title']}</a></h5>
                            <p style="color: #888; font-size: 11px; margin-top: 4px;">Éditeur : {art['source']} | Date : {art['published']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Aucun article disponible pour cette valeur.")

if __name__ == "__main__":
    main()
