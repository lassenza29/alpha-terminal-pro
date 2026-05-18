import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Analyse Financière", layout="wide")

def get_fx_rate(currency):
    if currency == "EUR":
        return 1.0
    try:
        ticker = f"{currency}EUR=X"
        data = yf.Ticker(ticker).history(period="1d")
        return data['Close'].iloc[-1]
    except:
        return 1.0

def calculer_rsi(data, window=14):
    delta = data.diff()
    # CORRECTION : Ajout du "=" manquant ici
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def extraire_donnees(ticker_symbole):
    try:
        ticker = yf.Ticker(ticker_symbole)
        info = ticker.info
        
        nom = info.get('longName') or info.get('shortName') or ticker_symbole
        devise = info.get('currency', 'USD')
        taux = get_fx_rate(devise)
        
        # Sécurité pour éviter les crashs si yfinance renvoie du vide (None)
        prix_brut = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose') or 0
        prix = prix_brut * taux
        
        cap_brut = info.get('marketCap') or 0
        cap = (cap_brut / 1_000_000) * taux
        
        dette_brut = info.get('totalDebt') or 0
        dette = (dette_brut / 1_000_000) * taux
        
        treso_brut = info.get('totalCash') or 0
        treso = (treso_brut / 1_000_000) * taux
        dette_nette = dette - treso
        
        ebitda_brut = info.get('ebitda') or 1
        ebitda = (ebitda_brut / 1_000_000) * taux
        ratio_dette = dette_nette / ebitda if ebitda != 0 else 0
        
        per = info.get('trailingPE') or 0
        bna_brut = info.get('trailingEps') or 0
        bna = bna_brut * taux
        
        return {
            "nom": nom, "prix": prix, "cap": cap, "dette_nette": dette_nette,
            "ratio_dette": ratio_dette, "per": per, "bna": bna, "ticker": ticker
        }
    except:
        return None

# --- INTERFACE GRAPHIQUE ---
st.title("Analyse Fondamentale & Technique")

ticker_input = st.text_input("Entrez le symbole (ex: AAPL, MC.PA) :", "AAPL")

if ticker_input:
    data = extraire_donnees(ticker_input)
    if data:
        st.header(f"{data['nom']} ({ticker_input.upper()})")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Prix (€)", f"{data['prix']:.2f}")
        col2.metric("Cap. (M€)", f"{data['cap']:.0f}")
        col3.metric("Ratio Dette/EBITDA", f"{data['ratio_dette']:.2f}")
        
        # Graphique Évolution & RSI
        hist = data['ticker'].history(period="1y")
        if not hist.empty:
            hist['RSI'] = calculer_rsi(hist['Close'])
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="Prix (€)", line=dict(color="turquoise")), row=1, col=1)
            fig.add_trace(go.Scatter(x=hist.index, y=hist['RSI'], name="RSI (14)", line=dict(color="purple")), row=2, col=1)
            
            # Lignes guides pour le RSI
            fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)
            
            fig.update_layout(height=500, template="plotly_dark", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Action introuvable ou erreur de chargement des données.")
