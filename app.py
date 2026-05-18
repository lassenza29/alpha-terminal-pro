#!/usr/bin/env python3
"""
Alpha Terminal Pro - Professional Financial Analysis Platform
Version: 2.0 (Production Ready)
Author: Lassenza29
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
    
    .stSelectbox > div > div > select {
        background-color: #1a1f3a;
        color: #e0e0e0;
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
        # Try to fetch from yfinance
        pair = f"{from_currency}{to_currency}=X"
        rate_ticker = yf.Ticker(pair)
        rate = rate_ticker.info.get('currentPrice')
        if rate and rate > 0:
            return float(rate)
    except:
        pass
    
    # Fallback to hardcoded rates
    if from_currency in CURRENCY_FALLBACKS:
        return CURRENCY_FALLBACKS[from_currency]
    
    return 1.0

def detect_currency(ticker: str) -> str:
    """Detect currency from ticker suffix"""
    ticker_upper = ticker.upper()
    
    if ticker_upper.endswith('.PA'):
        return "EUR"
    elif ticker_upper.endswith('.L'):
        return "GBP"
    elif ticker_upper.endswith('.DE'):
        return "EUR"
    elif ticker_upper.endswith('.AS'):
        return "EUR"
    elif ticker_upper.endswith('.TO'):
        return "CAD"
    elif ticker_upper.endswith('.AX'):
        return "AUD"
    elif ticker_upper.endswith('.HK'):
        return "HKD"
    elif ticker_upper.endswith('.SI'):
        return "SGD"
    else:
        return "USD"

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
def get_ticker_data(ticker: str) -> Tuple[yf.Ticker, Dict]:
    """Fetch ticker data with error handling"""
    try:
        tick = yf.Ticker(ticker)
        info = tick.info
        return tick, info
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de {ticker}: {str(e)}")
        return None, {}

def calculate_fundamental_ratios(ticker_obj: yf.Ticker, info: Dict, currency: str) -> Dict:
    """Calculate all 21 fundamental ratios"""
    ratios = {}
    
    try:
        # ===== SECTION A: VALORISATION (8 ratios) =====
        
        # 1. PER Actuel (Trailing P/E)
        trailing_pe = safe_float(info.get('trailingPE'))
        ratios['trailing_pe'] = trailing_pe if trailing_pe > 0 else None
        
        # 2. PER Futur (Forward P/E)
        forward_pe = safe_float(info.get('forwardPE'))
        ratios['forward_pe'] = forward_pe if forward_pe > 0 else None
        
        # 3. Price to Sales (P/S)
        ps_ratio = safe_float(info.get('priceToSalesTrailing12Months'))
        ratios['ps_ratio'] = ps_ratio if ps_ratio > 0 else None
        
        # 4. Price to Book (P/B)
        pb_ratio = safe_float(info.get('priceToBook'))
        ratios['pb_ratio'] = pb_ratio if pb_ratio > 0 else None
        
        # 5. EV/EBITDA
        ev_ebitda = safe_float(info.get('enterpriseToEbitda'))
        ratios['ev_ebitda'] = ev_ebitda if ev_ebitda > 0 else None
        
        # 6. BPA (EPS) en €
        eps = safe_float(info.get('trailingEps'))
        eps_eur = convert_to_eur(eps, currency) if eps > 0 else 0
        ratios['eps_eur'] = eps_eur if eps_eur > 0 else None
        
        # 7. Valeur Comptable par Action en €
        book_value = safe_float(info.get('bookValue'))
        book_value_eur = convert_to_eur(book_value, currency) if book_value > 0 else 0
        ratios['book_value_eur'] = book_value_eur if book_value_eur > 0 else None
        
        # 8. Prix Théorique de Graham
        if eps_eur and book_value_eur and eps_eur > 0 and book_value_eur > 0:
            try:
                graham_price = np.sqrt(22.5 * eps_eur * book_value_eur)
                ratios['graham_price'] = graham_price
            except:
                ratios['graham_price'] = None
        else:
            ratios['graham_price'] = None
        
        # ===== SECTION B: RENTABILITÉ (5 ratios) =====
        
        # 9. Marge Brute
        gross_margin = safe_float(info.get('grossMargins'))
        ratios['gross_margin'] = gross_margin * 100 if gross_margin else None
        
        # 10. Marge Opérationnelle
        operating_margin = safe_float(info.get('operatingMargins'))
        ratios['operating_margin'] = operating_margin * 100 if operating_margin else None
        
        # 11. Marge Nette
        profit_margin = safe_float(info.get('profitMargins'))
        ratios['profit_margin'] = profit_margin * 100 if profit_margin else None
        
        # 12. ROE (Rendement des Capitaux Propres)
        roe = safe_float(info.get('returnOnEquity'))
        ratios['roe'] = roe * 100 if roe else None
        
        # 13. ROA (Rendement des Actifs)
        roa = safe_float(info.get('returnOnAssets'))
        ratios['roa'] = roa * 100 if roa else None
        
        # ===== SECTION C: SANTÉ FINANCIÈRE (6 ratios) =====
        
        # 14. Dette Nette en M€
        total_debt = safe_float(info.get('totalDebt'))
        cash = safe_float(info.get('totalCash'))
        net_debt = (total_debt - cash) / 1_000_000 if total_debt or cash else None
        ratios['net_debt_m_eur'] = net_debt if net_debt is not None else 0
        ratios['is_cash_positive'] = net_debt < 0 if net_debt is not None else False
        
        # 15. EBITDA en M€
        ebitda = safe_float(info.get('ebitda'))
        ebitda_m = ebitda / 1_000_000 if ebitda else None
        ratios['ebitda_m_eur'] = ebitda_m if ebitda_m is not None else None
        
        # 16. Ratio Dette Nette / EBITDA
        if net_debt is not None and ebitda_m and ebitda_m > 0:
            if net_debt < 0:
                ratios['debt_ebitda_ratio'] = "Cash Positif"
            else:
                ratios['debt_ebitda_ratio'] = net_debt / ebitda_m if ebitda_m > 0 else None
        else:
            ratios['debt_ebitda_ratio'] = None
        
        # 17. Ratio de Liquidité Générale (Current Ratio)
        current_ratio = safe_float(info.get('currentRatio'))
        ratios['current_ratio'] = current_ratio if current_ratio > 0 else None
        
        # 18. Ratio de Liquidité Immédiate (Quick Ratio)
        quick_ratio = safe_float(info.get('quickRatio'))
        ratios['quick_ratio'] = quick_ratio if quick_ratio > 0 else None
        
        # 19. Ratio Dette / Capitaux Propres (Debt to Equity)
        debt_to_equity = safe_float(info.get('debtToEquity'))
        ratios['debt_to_equity'] = debt_to_equity * 100 if debt_to_equity else None
        
        # ===== SECTION D: CROISSANCE & DIVIDENDES (2 ratios) =====
        
        # 20. Revenue Growth
        revenue_growth = safe_float(info.get('revenueGrowth'))
        ratios['revenue_growth'] = revenue_growth * 100 if revenue_growth else None
        
        # 21. Payout Ratio
        payout_ratio = safe_float(info.get('payoutRatio'))
        ratios['payout_ratio'] = payout_ratio * 100 if payout_ratio else None
        
    except Exception as e:
        st.warning(f"⚠️ Erreur lors du calcul des ratios: {str(e)}")
    
    return ratios

def calculate_fundamental_score(ratios: Dict, current_price: float, currency: str) -> Tuple[int, Dict]:
    """Calculate Fundamental Score (0-100) based on strict rules"""
    score = 0
    score_details = {}
    
    # Rule 1: PER < 20 (Valuation attractive)
    if ratios.get('trailing_pe') and ratios['trailing_pe'] > 0 and ratios['trailing_pe'] < 20:
        score += 15
        score_details['PER Attractif'] = '+15'
    
    # Rule 2: Dette Nette / EBITDA < 2 (Santé financière)
    debt_ebitda = ratios.get('debt_ebitda_ratio')
    if isinstance(debt_ebitda, str) and "Cash" in debt_ebitda:
        score += 15
        score_details['Cash Positif'] = '+15'
    elif isinstance(debt_ebitda, (int, float)) and debt_ebitda < 2:
        score += 15
        score_details['Levier Sain'] = '+15'
    
    # Rule 3: ROE > 15% (Rentabilité)
    if ratios.get('roe') and ratios['roe'] > 15:
        score += 15
        score_details['ROE Excellent'] = '+15'
    
    # Rule 4: Marge Nette > 12% (Profitabilité)
    if ratios.get('profit_margin') and ratios['profit_margin'] > 12:
        score += 15
        score_details['Marge Nette Saine'] = '+15'
    
    # Rule 5: Graham Price > Current Price (Valuation)
    if ratios.get('graham_price') and current_price > 0:
        if ratios['graham_price'] > current_price * 1.2:
            score += 10
            score_details['Graham Favorable'] = '+10'
    
    # Rule 6: Revenue Growth > 5% (Croissance)
    if ratios.get('revenue_growth') and ratios['revenue_growth'] > 5:
        score += 10
        score_details['Croissance Positive'] = '+10'
    
    # Rule 7: Current Ratio > 1.5 (Liquidité)
    if ratios.get('current_ratio') and ratios['current_ratio'] > 1.5:
        score += 5
        score_details['Liquidité Bonne'] = '+5'
    
    # Rule 8: Dividend Payout < 60% (Durabilité)
    if ratios.get('payout_ratio') and ratios['payout_ratio'] < 60:
        score += 5
        score_details['Dividende Soutenable'] = '+5'
    
    return min(score, 100), score_details

def get_analyst_consensus(info: Dict) -> Dict:
    """Extract analyst consensus data"""
    consensus = {
        'target_price': safe_float(info.get('targetMeanPrice')),
        'num_analysts': safe_float(info.get('numberOfAnalysts')),
        'recommendation': safe_str(info.get('recommendationKey', 'N/A')).upper(),
        'target_high': safe_float(info.get('targetHighPrice')),
        'target_low': safe_float(info.get('targetLowPrice')),
    }
    return consensus

# ============================================================================
# MODULE 2: ETF ANALYSIS
# ============================================================================

def is_etf(info: Dict, ticker: str) -> bool:
    """Check if ticker is an ETF"""
    quote_type = safe_str(info.get('quoteType', '')).upper()
    if quote_type == 'ETF':
        return True
    if ticker.upper().endswith(('.PA', '.L', '.DE', '.AS')) and 'fund' in safe_str(info.get('category', '')).lower():
        return True
    return False

def analyze_etf(ticker_obj: yf.Ticker, info: Dict) -> Dict:
    """Analyze ETF-specific metrics"""
    etf_data = {
        'ter': safe_float(info.get('expenseRatio')),
        'aum': safe_float(info.get('totalAssets')),
        'distribution': safe_str(info.get('distributionType', 'N/A')),
        'replication': safe_str(info.get('replicationMethod', 'N/A')),
        'category': safe_str(info.get('category', 'N/A')),
        'inception_date': safe_str(info.get('inceptionDate', 'N/A')),
    }
    
    # Déterminer éligibilité PEA
    pea_eligible_issuers = ['AMUNDI', 'LYXOR', 'ISHARES', 'VANGUARD', 'BNYX', 'SPDR']
    provider = safe_str(info.get('fundFamily', '')).upper()
    ticker_upper = ticker_obj.ticker.upper()
    
    etf_data['pea_eligible'] = any(issuer in provider for issuer in pea_eligible_issuers) or ticker_upper.endswith('.PA')
    
    # Vérifier risque de clôture (faible AUM)
    aum = etf_data['aum']
    if aum and aum < 100_000_000:  # < 100M€
        etf_data['closure_risk'] = True
    else:
        etf_data['closure_risk'] = False
    
    return etf_data

# ============================================================================
# MODULE 3: MULTI-ASSET COMPARATOR
# ============================================================================

@st.cache_data(ttl=300)
def create_comparison_df(tickers: List[str]) -> pd.DataFrame:
    """Create comparison dataframe for multiple tickers"""
    data = []
    
    for ticker in tickers:
        ticker = ticker.strip().upper()
        try:
            tick_obj, info = get_ticker_data(ticker)
            if tick_obj is None:
                continue
            
            currency = detect_currency(ticker)
            current_price = safe_float(info.get('currentPrice'))
            
            ratios = calculate_fundamental_ratios(tick_obj, info, currency)
            score, _ = calculate_fundamental_score(ratios, current_price, currency)
            
            market_cap = safe_float(info.get('marketCap'))
            
            data.append({
                'Ticker': ticker,
                'Prix €': format_currency(convert_to_eur(current_price, currency)),
                'MarketCap': format_currency(convert_to_eur(market_cap, currency)) if market_cap else 'N/A',
                'Score': score,
                'PER': f"{ratios.get('trailing_pe'):.2f}" if ratios.get('trailing_pe') else 'N/A',
                'P/S': f"{ratios.get('ps_ratio'):.2f}" if ratios.get('ps_ratio') else 'N/A',
                'Marge Nette': safe_pct(ratios.get('profit_margin')),
                'ROE': safe_pct(ratios.get('roe')),
                'Dette/EBITDA': f"{ratios.get('debt_ebitda_ratio'):.2f}" if isinstance(ratios.get('debt_ebitda_ratio'), (int, float)) else 'N/A',
                'Dividend': safe_pct(ratios.get('payout_ratio')),
            })
        except Exception as e:
            st.warning(f"⚠️ Erreur pour {ticker}: {str(e)}")
            continue
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    df = df.sort_values('Score', ascending=False)
    return df

# ============================================================================
# MODULE 4: DCA SIMULATOR (HIGH PRECISION)
# ============================================================================

def simulate_dca(ticker: str, monthly_amount: float, years: int) -> Tuple[pd.DataFrame, Dict]:
    """Simulate Dollar Cost Averaging with real historical data"""
    try:
        tick_obj = yf.Ticker(ticker)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)
        
        hist = tick_obj.history(start=start_date, end=end_date)
        
        if hist.empty:
            return pd.DataFrame(), {}
        
        # Sample first trading day of each month
        hist['YearMonth'] = hist.index.to_period('M')
        monthly_data = hist.groupby('YearMonth').first()
        
        # Calculate DCA
        shares_owned = 0.0
        total_invested = 0.0
        portfolio_values = []
        dates = []
        invested_values = []
        
        for date, row in monthly_data.iterrows():
            price = safe_float(row.get('Close'))
            if price <= 0:
                continue
            
            # Buy shares
            shares_owned += monthly_amount / price
            total_invested += monthly_amount
            portfolio_value = shares_owned * price
            
            dates.append(date.to_timestamp())
            invested_values.append(total_invested)
            portfolio_values.append(portfolio_value)
        
        # Create results
        df_results = pd.DataFrame({
            'Date': dates,
            'Total Investi': invested_values,
            'Valeur Portefeuille': portfolio_values,
        })
        
        # Calculate metrics
        final_invested = total_invested
        final_value = portfolio_values[-1] if portfolio_values else 0
        gain_loss = final_value - final_invested
        roi = (gain_loss / final_invested * 100) if final_invested > 0 else 0
        
        metrics = {
            'shares': shares_owned,
            'final_invested': final_invested,
            'final_value': final_value,
            'gain_loss': gain_loss,
            'roi': roi,
        }
        
        return df_results, metrics
        
    except Exception as e:
        st.error(f"❌ Erreur DCA: {str(e)}")
        return pd.DataFrame(), {}

# ============================================================================
# MODULE 5: NEWS FEED
# ============================================================================

def get_news_feed(ticker_obj: yf.Ticker) -> List[Dict]:
    """Get news articles for ticker"""
    try:
        news = ticker_obj.news
        if not news:
            return []
        
        articles = []
        for item in news[:10]:  # Limit to 10 articles
            article = {
                'title': safe_str(item.get('title')),
                'link': safe_str(item.get('link')),
                'source': safe_str(item.get('source')),
                'published': safe_str(item.get('providerPublishTime')),
            }
            articles.append(article)
        
        return articles
    except Exception as e:
        st.warning(f"⚠️ Erreur lors du chargement des nouvelles: {str(e)}")
        return []

# ============================================================================
# MODULE 6: TECHNICAL ANALYSIS (SMA 50/200 + RSI)
# ============================================================================

def calculate_sma(data: pd.Series, window: int) -> pd.Series:
    """Calculate Simple Moving Average"""
    return data.rolling(window=window).mean()

def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def plot_technical_analysis(ticker: str) -> go.Figure:
    """Create technical analysis chart with SMA 50/200 + RSI"""
    try:
        tick_obj = yf.Ticker(ticker)
        
        # Get 5 years of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)
        
        hist = tick_obj.history(start=start_date, end=end_date)
        
        if hist.empty or len(hist) < 200:
            return None
        
        # Calculate indicators
        hist['SMA50'] = calculate_sma(hist['Close'], 50)
        hist['SMA200'] = calculate_sma(hist['Close'], 200)
        hist['RSI'] = calculate_rsi(hist['Close'], 14)
        
        # Create subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=(f"Prix & Moyennes Mobiles - {ticker}", "RSI (14)")
        )
        
        # Price chart
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist['Close'], name='Prix', 
                      line=dict(color='#00d4ff', width=2),
                      hovertemplate='%{x|%d/%m/%Y}<br>Prix: €%{y:.2f}'),
            row=1, col=1
        )
        
        # SMA 50
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist['SMA50'], name='SMA 50',
                      line=dict(color='#ff6b6b', width=1, dash='dot'),
                      hovertemplate='SMA50: €%{y:.2f}'),
            row=1, col=1
        )
        
        # SMA 200
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist['SMA200'], name='SMA 200',
                      line=dict(color='#00ff88', width=1, dash='dash'),
                      hovertemplate='SMA200: €%{y:.2f}'),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=hist.index, y=hist['RSI'], name='RSI',
                      line=dict(color='#ffaa00', width=2),
                      hovertemplate='RSI: %{y:.2f}'),
            row=2, col=1
        )
        
        # RSI Reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="#ff6b6b", 
                     annotation_text="Suracheté (70)", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", 
                     annotation_text="Survendu (30)", row=2, col=1)
        
        # Update layout
        fig.update_layout(
            title=f"Analyse Technique - {ticker} (5 ans)",
            template="plotly_dark",
            hovermode="x unified",
            height=700,
            showlegend=True,
            xaxis_rangeslider_visible=False,
            font=dict(color='#e0e0e0', size=11),
            paper_bgcolor='#0a0e27',
            plot_bgcolor='#1a1f3a',
        )
        
        fig.update_yaxes(title_text="Prix (€)", row=1, col=1, gridcolor='#333')
        fig.update_yaxes(title_text="RSI", row=2, col=1, gridcolor='#333')
        fig.update_xaxes(gridcolor='#333')
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Erreur analyse technique: {str(e)}")
        return None

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_metric_card(label: str, value: str, color: str = "#00d4ff") -> None:
    """Display a styled metric card"""
    st.markdown(f"""
    <div style="background-color: #1a1f3a; border-left: 4px solid {color}; 
                padding: 15px; border-radius: 5px; margin: 5px 0;">
        <p style="color: #999; font-size: 12px; margin: 0;">{label}</p>
        <p style="color: {color}; font-size: 18px; font-weight: bold; margin: 5px 0;">{value}</p>
    </div>
    """, unsafe_allow_html=True)

def display_score_card(score: int, max_score: int = 100) -> None:
    """Display fundamental score card"""
    percentage = (score / max_score) * 100
    color = "#00ff88" if score >= 70 else "#ffaa00" if score >= 50 else "#ff6b6b"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1a3a3a 0%, #2d4d4d 100%);
                border: 2px solid {color}; border-radius: 10px; padding: 25px;
                text-align: center; margin: 15px 0;">
        <p style="color: #999; font-size: 14px; margin: 0;">SCORE FONDAMENTAL</p>
        <p style="color: {color}; font-size: 48px; font-weight: bold; margin: 10px 0;">{score}/100</p>
        <div style="background-color: #0a0e27; height: 8px; border-radius: 4px; margin: 10px 0;
                    overflow: hidden;">
            <div style="background-color: {color}; height: 100%; width: {percentage}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application"""
    
    # Header
    st.markdown("""
    <div style="text-align: center; margin: 30px 0;">
        <h1 style="color: #00d4ff; font-size: 48px; margin: 0;">📈 Alpha Terminal Pro</h1>
        <p style="color: #999; font-size: 14px; margin-top: 10px;">Professional Financial Analysis Platform | v2.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.markdown("### 🎯 Navigation")
    mode = st.sidebar.radio(
        "Sélectionnez le mode:",
        ["📊 Analyse Complète", "⚖️ Comparateur", "💰 DCA Simulator", "📰 Actualités"],
        label_visibility="collapsed"
    )
    
    # ========================================================================
    # MODE 1: COMPLETE ANALYSIS
    # ========================================================================
    if mode == "📊 Analyse Complète":
        st.markdown("### Recherche d'un actif")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            ticker_input = st.text_input(
                "Entrez un ticker (ex: AAPL, LVMH.PA, SPY):",
                placeholder="AAPL",
                label_visibility="collapsed"
            ).strip().upper()
        
        with col2:
            search_button = st.button("🔍 Rechercher", use_container_width=True)
        
        if search_button and ticker_input:
            with st.spinner(f"⏳ Chargement de {ticker_input}..."):
                tick_obj, info = get_ticker_data(ticker_input)
                
                if tick_obj is None:
                    st.error(f"❌ Ticker '{ticker_input}' introuvable. Vérifiez l'orthographe.")
                else:
                    currency = detect_currency(ticker_input)
                    current_price = safe_float(info.get('currentPrice'))
                    current_price_eur = convert_to_eur(current_price, currency)
                    
                    # Top metrics row
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        display_metric_card("Prix Actuel", format_currency(current_price_eur), "#00d4ff")
                    with col2:
                        market_cap = safe_float(info.get('marketCap'))
                        display_metric_card("Capitalisation", 
                                          format_currency(convert_to_eur(market_cap, currency)) if market_cap else "N/A",
                                          "#00ff88")
                    with col3:
                        pe = safe_float(info.get('trailingPE'))
                        display_metric_card("PER Actuel", f"{pe:.2f}" if pe else "N/A", "#ffaa00")
                    with col4:
                        div_yield = safe_float(info.get('dividendYield'))
                        display_metric_card("Rendement Div", 
                                          f"{div_yield * 100:.2f}%" if div_yield else "N/A",
                                          "#ff6b6b")
                    
                    # Calculate ratios and score
                    ratios = calculate_fundamental_ratios(tick_obj, info, currency)
                    score, score_details = calculate_fundamental_score(ratios, current_price_eur, currency)
                    
                    # Fundamental score
                    col1, col2 = st.columns([1.5, 1])
                    with col1:
                        display_score_card(score)
                    
                    with col2:
                        st.markdown("### Score Breakdown")
                        if score_details:
                            for key, value in score_details.items():
                                st.markdown(f"- **{key}**: {value}")
                        else:
                            st.info("Données insuffisantes pour le scoring détaillé")
                    
                    # Check if ETF
                    st.markdown("---")
                    if is_etf(info, ticker_input):
                        st.markdown("### 📊 ANALYSE ETF")
                        etf_data = analyze_etf(tick_obj, info)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            ter = etf_data.get('ter')
                            if ter:
                                color = "#00ff88" if ter < 0.3 else "#ffaa00" if ter < 0.6 else "#ff6b6b"
                                display_metric_card("TER (Frais)", f"{ter * 100:.3f}%", color)
                            else:
                                display_metric_card("TER", "N/A")
                        
                        with col2:
                            aum = etf_data.get('aum')
                            if aum:
                                color = "#00ff88" if aum > 100_000_000 else "#ff6b6b"
                                display_metric_card("AUM", format_large_number(aum) + "€", color)
                            else:
                                display_metric_card("AUM", "N/A")
                        
                        with col3:
                            if etf_data.get('closure_risk'):
                                st.warning("⚠️ **Risque de clôture**: AUM < 100M€")
                            else:
                                st.success("✅ **AUM Suffisant**: > 100M€")
                        
                        # PEA Eligibility
                        if etf_data.get('pea_eligible'):
                            st.success("✅ **Éligible au PEA**")
                        else:
                            st.info("ℹ️ **Compte-Titres uniquement**")
                    
                    # Tabs for detailed ratios
                    st.markdown("---")
                    st.markdown("### 21 Ratios Fondamentaux")
                    
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "💰 Valorisation",
                        "📈 Rentabilité",
                        "🏦 Santé Financière",
                        "📊 Croissance",
                        "🎯 Consensus"
                    ])
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        with col1:
                            display_metric_card("1. PER Actuel", 
                                              f"{ratios.get('trailing_pe'):.2f}" if ratios.get('trailing_pe') else "N/A")
                            display_metric_card("3. Price/Sales", 
                                              f"{ratios.get('ps_ratio'):.2f}" if ratios.get('ps_ratio') else "N/A")
                            display_metric_card("5. EV/EBITDA", 
                                              f"{ratios.get('ev_ebitda'):.2f}" if ratios.get('ev_ebitda') else "N/A")
                            display_metric_card("7. Book Value/Action", 
                                              format_currency(ratios.get('book_value_eur')) if ratios.get('book_value_eur') else "N/A")
                        
                        with col2:
                            display_metric_card("2. PER Futur", 
                                              f"{ratios.get('forward_pe'):.2f}" if ratios.get('forward_pe') else "N/A")
                            display_metric_card("4. Price/Book", 
                                              f"{ratios.get('pb_ratio'):.2f}" if ratios.get('pb_ratio') else "N/A")
                            display_metric_card("6. BPA (EPS)", 
                                              format_currency(ratios.get('eps_eur')) if ratios.get('eps_eur') else "N/A")
                            display_metric_card("8. Prix Graham", 
                                              format_currency(ratios.get('graham_price')) if ratios.get('graham_price') else "N/A")
                    
                    with tab2:
                        col1, col2 = st.columns(2)
                        with col1:
                            display_metric_card("9. Marge Brute", 
                                              safe_pct(ratios.get('gross_margin')))
                            display_metric_card("11. Marge Nette", 
                                              safe_pct(ratios.get('profit_margin')))
                            display_metric_card("13. ROE", 
                                              safe_pct(ratios.get('roe')))
                        
                        with col2:
                            display_metric_card("10. Marge Opérationnelle", 
                                              safe_pct(ratios.get('operating_margin')))
                            display_metric_card("12. ROA", 
                                              safe_pct(ratios.get('roa')))
                    
                    with tab3:
                        col1, col2 = st.columns(2)
                        with col1:
                            display_metric_card("14. Dette Nette", 
                                              format_currency(ratios.get('net_debt_m_eur') * 1_000_000) if ratios.get('net_debt_m_eur') is not None else "N/A")
                            display_metric_card("16. Dette/EBITDA", 
                                              f"{ratios.get('debt_ebitda_ratio'):.2f}" if isinstance(ratios.get('debt_ebitda_ratio'), (int, float)) else str(ratios.get('debt_ebitda_ratio', 'N/A')))
                            display_metric_card("18. Quick Ratio", 
                                              f"{ratios.get('quick_ratio'):.2f}" if ratios.get('quick_ratio') else "N/A")
                        
                        with col2:
                            display_metric_card("15. EBITDA", 
                                              format_currency(ratios.get('ebitda_m_eur') * 1_000_000) if ratios.get('ebitda_m_eur') is not None else "N/A")
                            display_metric_card("17. Current Ratio", 
                                              f"{ratios.get('current_ratio'):.2f}" if ratios.get('current_ratio') else "N/A")
                            display_metric_card("19. Dette/Equity", 
                                              safe_pct(ratios.get('debt_to_equity')))
                    
                    with tab4:
                        col1, col2 = st.columns(2)
                        with col1:
                            display_metric_card("20. Revenue Growth", 
                                              safe_pct(ratios.get('revenue_growth')))
                        with col2:
                            display_metric_card("21. Payout Ratio", 
                                              safe_pct(ratios.get('payout_ratio')))
                    
                    with tab5:
                        consensus = get_analyst_consensus(info)
                        col1, col2 = st.columns(2)
                        with col1:
                            target = consensus.get('target_price')
                            if target and target > 0:
                                price_diff = ((target - current_price_eur) / current_price_eur * 100) if current_price_eur > 0 else 0
                                color = "#00ff88" if price_diff > 0 else "#ff6b6b"
                                display_metric_card("Prix Cible Analystes", 
                                                  format_currency(convert_to_eur(target, currency)), color)
                                display_metric_card("Potentiel", f"{price_diff:+.1f}%", color)
                        with col2:
                            display_metric_card("Nombre d'Analystes", 
                                              f"{int(consensus.get('num_analysts', 0))}")
                            display_metric_card("Recommandation", 
                                              consensus.get('recommendation'))
                    
                    # Technical Analysis
                    st.markdown("---")
                    st.markdown("### 📊 Analyse Technique (5 ans)")
                    
                    fig_tech = plot_technical_analysis(ticker_input)
                    if fig_tech:
                        st.plotly_chart(fig_tech, use_container_width=True)
                    else:
                        st.warning("⚠️ Données insuffisantes pour l'analyse technique")
                    
                    # News
                    st.markdown("---")
                    st.markdown("### 📰 Actualités Récentes")
                    
                    news = get_news_feed(tick_obj)
                    if news:
                        for idx, article in enumerate(news, 1):
                            st.markdown(f"""
                            **{idx}. [{article['title']}]({article['link']})**
                            
                            *Source: {article['source']}*
                            """)
                    else:
                        st.info("ℹ️ Aucune actualité disponible pour ce ticker")
    
    # ========================================================================
    # MODE 2: COMPARATOR
    # ========================================================================
    elif mode == "⚖️ Comparateur":
        st.markdown("### Comparer Plusieurs Actifs")
        
        ticker_list = st.text_input(
            "Entrez plusieurs tickers séparés par des virgules:",
            placeholder="AAPL, MSFT, NVDA, LVMH.PA",
            label_visibility="collapsed"
        )
        
        if ticker_list:
            tickers = [t.strip().upper() for t in ticker_list.split(',')]
            
            with st.spinner("⏳ Chargement du comparateur..."):
                df_comparison = create_comparison_df(tickers)
                
                if not df_comparison.empty:
                    st.markdown("### Matrice de Comparaison")
                    st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                    
                    # CSV Export
                    csv = df_comparison.to_csv(index=False)
                    st.download_button(
                        label="📥 Télécharger CSV",
                        data=csv,
                        file_name=f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
                    # Charts
                    st.markdown("---")
                    st.markdown("### Visualisations")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Score Chart
                        fig_score = px.bar(df_comparison, x='Ticker', y='Score', 
                                          color='Score', color_continuous_scale='RdYlGn',
                                          title="Score Fondamental par Actif")
                        fig_score.update_layout(
                            template="plotly_dark",
                            paper_bgcolor='#0a0e27',
                            plot_bgcolor='#1a1f3a',
                            font=dict(color='#e0e0e0'),
                        )
                        st.plotly_chart(fig_score, use_container_width=True)
                    
                    with col2:
                        # PER Chart
                        df_per = df_comparison[df_comparison['PER'] != 'N/A'].copy()
                        if not df_per.empty:
                            df_per['PER'] = pd.to_numeric(df_per['PER'], errors='coerce')
                            fig_per = px.bar(df_per, x='Ticker', y='PER',
                                            title="PER par Actif")
                            fig_per.update_layout(
                                template="plotly_dark",
                                paper_bgcolor='#0a0e27',
                                plot_bgcolor='#1a1f3a',
                                font=dict(color='#e0e0e0'),
                            )
                            st.plotly_chart(fig_per, use_container_width=True)
                else:
                    st.error("❌ Aucun actif trouvé. Vérifiez les tickers.")
    
    # ========================================================================
    # MODE 3: DCA SIMULATOR
    # ========================================================================
    elif mode == "💰 DCA Simulator":
        st.markdown("### Simulateur Dollar Cost Averaging")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            dca_ticker = st.text_input(
                "Ticker:",
                placeholder="AAPL",
                label_visibility="collapsed"
            ).strip().upper()
        
        with col2:
            dca_amount = st.number_input(
                "Montant mensuel (€):",
                min_value=10.0,
                max_value=10000.0,
                value=150.0,
                step=10.0
            )
        
        with col3:
            dca_years = st.selectbox(
                "Période:",
                [1, 3, 5, 10],
                label_visibility="collapsed"
            )
        
        if st.button("🚀 Simuler DCA", use_container_width=True):
            with st.spinner("⏳ Simulation en cours..."):
                df_dca, metrics = simulate_dca(dca_ticker, dca_amount, dca_years)
                
                if not df_dca.empty and metrics:
                    # Results
                    st.markdown("---")
                    st.markdown("### Résultats de la Simulation")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        display_metric_card(
                            "Total Investi",
                            format_currency(metrics['final_invested']),
                            "#00d4ff"
                        )
                    
                    with col2:
                        display_metric_card(
                            "Valeur du Portefeuille",
                            format_currency(metrics['final_value']),
                            "#00ff88" if metrics['gain_loss'] > 0 else "#ff6b6b"
                        )
                    
                    with col3:
                        display_metric_card(
                            "Plus-Value",
                            format_currency(metrics['gain_loss']),
                            "#00ff88" if metrics['gain_loss'] > 0 else "#ff6b6b"
                        )
                    
                    with col4:
                        display_metric_card(
                            "Rendement",
                            f"{metrics['roi']:+.2f}%",
                            "#00ff88" if metrics['roi'] > 0 else "#ff6b6b"
                        )
                    
                    # Chart
                    st.markdown("---")
                    st.markdown("### Évolution du Portefeuille")
                    
                    fig_dca = go.Figure()
                    
                    fig_dca.add_trace(go.Scatter(
                        x=df_dca['Date'], y=df_dca['Total Investi'],
                        name='Capital Investi',
                        line=dict(color='#00d4ff', width=3)
                    ))
                    
                    fig_dca.add_trace(go.Scatter(
                        x=df_dca['Date'], y=df_dca['Valeur Portefeuille'],
                        name='Valeur du Portefeuille',
                        line=dict(color='#00ff88', width=3),
                        fill='tonexty',
                        fillcolor='rgba(0, 255, 136, 0.1)'
                    ))
                    
                    fig_dca.update_layout(
                        title=f"DCA Simulation - {dca_ticker} ({dca_years} ans)",
                        xaxis_title="Date",
                        yaxis_title="Valeur (€)",
                        template="plotly_dark",
                        hovermode="x unified",
                        height=500,
                        paper_bgcolor='#0a0e27',
                        plot_bgcolor='#1a1f3a',
                        font=dict(color='#e0e0e0', size=11),
                        legend=dict(x=0.01, y=0.99, bgcolor='rgba(26, 31, 58, 0.8)'),
                    )
                    
                    fig_dca.update_yaxes(gridcolor='#333')
                    fig_dca.update_xaxes(gridcolor='#333')
                    
                    st.plotly_chart(fig_dca, use_container_width=True)
                else:
                    st.error(f"❌ Impossible de simuler DCA pour {dca_ticker}")
    
    # ========================================================================
    # MODE 4: NEWS FEED
    # ========================================================================
    elif mode == "📰 Actualités":
        st.markdown("### Actualités par Ticker")
        
        news_ticker = st.text_input(
            "Entrez un ticker:",
            placeholder="AAPL",
            label_visibility="collapsed"
        ).strip().upper()
        
        if news_ticker:
            with st.spinner("⏳ Chargement des actualités..."):
                tick_obj, info = get_ticker_data(news_ticker)
                
                if tick_obj is not None:
                    news = get_news_feed(tick_obj)
                    
                    if news:
                        st.markdown(f"### Articles Récents - {news_ticker}")
                        
                        for idx, article in enumerate(news, 1):
                            with st.container(border=True):
                                st.markdown(f"**{idx}. [{article['title']}]({article['link']})**")
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"_Source: {article['source']}_")
                                with col2:
                                    st.markdown(f"_{article['published']}_")
                    else:
                        st.info(f"ℹ️ Aucune actualité disponible pour {news_ticker}")
                else:
                    st.error(f"❌ Ticker '{news_ticker}' introuvable")

if __name__ == "__main__":
    main()
