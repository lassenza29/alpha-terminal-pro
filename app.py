import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime
import numpy as np

# ==============================================================================
# 0. CONFIGURATION DE LA PAGE & DESIGN UI/UX (CSS PERSONNALISÉ)
# ==============================================================================
st.set_page_config(
    page_title="Alpha Terminal Pro | Terminal Financier Institutionnel",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection de styles CSS pour un rendu sombre haut de gamme, épuré et corporate
st.markdown("""
<style>
    /* Global Background and Typography */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Custom Financial Metric Card */
    .fin-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    .fin-card-title {
        font-size: 0.85rem;
        color: #8b949e;
        text-transform: uppercase;
        margin-bottom: 5px;
        font-weight: 600;
    }
    .fin-card-value {
        font-size: 1.4rem;
        color: #58a6ff;
        font-weight: bold;
    }
    .fin-card-sub {
        font-size: 0.75rem;
        color: #8b949e;
        margin-top: 5px;
    }
    
    /* Score Indicator Styles */
    .score-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #30363d;
    }
    
    /* Headers customization */
    h1, h2, h3 {
        color: #f0f6fc !important;
        font-weight: 500 !important;
    }
    
    /* Status styling overrides */
    div[data-testid="stNotification"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 1. PARSING DÉFENSIF & CONFIGURATION DES DEVISES (ROBUSTESSE)
# ==============================================================================
@st.cache_data(ttl=3600)
def get_fx_rate(currency_code):
    """
    Récupère le taux de change pour convertir une devise d'origine vers l'EURO (€).
    Inclut des valeurs de secours (fallbacks) strictes en cas de panne de l'API.
    """
    if not currency_code:
        return 1.0
    
    curr_upper = currency_code.upper().strip()
    
    # Traitement spécifique pour la devise de Londres (Pence Sterling)
    is_pence = False
    if curr_upper in ["GBp", "GBX"]:
        curr_upper = "GBP"
        is_pence = True
        
    if curr_upper == "EUR":
        return 0.01 if is_pence else 1.0

    # Table de secours immuable en cas de défaillance réseau ou d'API
    fallbacks = {
        "USD": 0.92,
        "GBP": 1.17,
        "CHF": 1.04,
        "CAD": 0.68,
        "JPY":
