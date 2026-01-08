# -*- coding: utf-8 -*-
import streamlit as st
from contracts.schema import MLSignal

def render_prediction_card(signal: MLSignal):
    """
    Enhanced prediction card UI with all 8 ML features displayed beautifully.
    """
    

    
    # ========================================
    # 1️⃣ PRIMARY SIGNAL DISPLAY
    # ========================================
    
    signal_emoji = "🟢" if signal.signal_value == 1 else ("🔴" if signal.signal_value == -1 else "🟡")
    
    st.markdown(f"""
    <div class="glass-card" style="padding: 20px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 2;">
                <h3 style="margin: 0; padding: 0; color: white;">🤖 AI Trading Signal</h3>
            </div>
            <div style="flex: 1; text-align: center;">
                <div class="model-badge">{signal_emoji} Signal: {signal.signal_value}</div>
            </div>
            <div style="flex: 1; text-align: right; opacity: 0.7; font-size: 12px; color: #cbd5e1;">
                📅 {signal.prediction_date}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Signal Section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Primary Signal")
        
        # Glass signal display with animations
        if signal.action == "BUY":
            st.markdown(
                '<div class="glass-signal-buy">'
                '<div style="font-size:42px; font-weight:bold; color:#00ff88;">🚀 BUY</div>'
                '</div>', 
                unsafe_allow_html=True
            )
        elif signal.action == "SELL":
            st.markdown(
                '<div class="glass-signal-sell">'
                '<div style="font-size:42px; font-weight:bold; color:#ff5555;">💥 SELL</div>'
                '</div>', 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="glass-signal-hold">'
                '<div style="font-size:42px; font-weight:bold; color:#ffcc00;">⏸️ HOLD</div>'
                '</div>', 
                unsafe_allow_html=True
            )
    
    with col2:
        # 5️⃣ CONFIDENCE SCORE DISPLAY
        st.markdown("#### Confidence Analysis")
        
        st.markdown(f"""
            <div class="glass-metric-card">
                <div style="font-size:32px; font-weight:bold; color:#6495ed;">{signal.confidence:.1f}%</div>
                <div style="font-size:14px; opacity:0.8; margin-top:5px;">Confidence Level: <strong>{signal.confidence_level}</strong></div>
                <div style="background: rgba(255,255,255,0.1); height:10px; border-radius:5px; margin-top:10px; overflow:hidden;">
                    <div class="feature-bar" style="width:{signal.confidence}%; background:linear-gradient(90deg,#667eea,#764ba2);"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        
        # 7️⃣ Prediction Frequency
        st.markdown(f"""
            <div style="margin-top:10px; font-size:12px; opacity:0.7; text-align:center;">
                🔄 Prediction Frequency: <strong>{signal.prediction_frequency}</strong>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================
    # 4️⃣ GEN-AI EXPLANATION
    # ========================================
    
    st.markdown("#### 🧠 AI Explanation")
    st.markdown(f"""
        <div class="glass-insight-box">
            <div style="white-space: pre-wrap; line-height: 1.6; color: rgba(255,255,255,0.9);">
{signal.reasoning}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================
    # 6️⃣ TOP FEATURES / INDICATORS USED
    # ========================================
    
    col_features1, col_features2 = st.columns(2)
    
    with col_features1:
        st.markdown("#### 📊 Key Factors")
        for i, factor in enumerate(signal.key_factors[:5], 1):
            st.markdown(f"""
                <div class="glass-factor-item">
                    <strong>{i}.</strong> {factor}
                </div>
            """, unsafe_allow_html=True)
    
    with col_features2:
        st.markdown("#### 🎯 Feature Importance")
        
        # Sort by importance
        sorted_features = sorted(signal.feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        for feature, importance in sorted_features[:5]:
            st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:3px;">
                        <span style="color:rgba(255,255,255,0.9);">{feature}</span>
                        <span style="color:#6495ed; font-weight:bold;">{importance:.1f}%</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.1); height:6px; border-radius:3px; overflow:hidden;">
                        <div style="width:{importance}%; height:100%; background:linear-gradient(90deg,#667eea,#764ba2); border-radius:3px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Glassmorphism alerts
    if signal.confidence < 60:
        st.markdown(
            '<div style="background:rgba(255,193,7,0.1); backdrop-filter:blur(10px); '
            'border-left:4px solid rgba(255,193,7,0.6); padding:15px; border-radius:10px; margin:10px 0;">'
            '⚠️ <strong>Caution:</strong> This signal has lower confidence. Consider waiting for stronger signals '
            'or reducing position size to manage risk.'
            '</div>', 
            unsafe_allow_html=True
        )
    elif signal.action == "SELL" and signal.confidence > 75:
        st.markdown(
            '<div style="background:rgba(244,67,54,0.1); backdrop-filter:blur(10px); '
            'border-left:4px solid rgba(244,67,54,0.6); padding:15px; border-radius:10px; margin:10px 0;">'
            '🚨 <strong>Strong Sell Signal:</strong> Consider reviewing your position. '
            'High confidence sell signals may indicate significant downside risk.'
            '</div>', 
            unsafe_allow_html=True
        )
    elif signal.action == "BUY" and signal.confidence > 80:
        st.markdown(
            '<div style="background:rgba(76,175,80,0.1); backdrop-filter:blur(10px); '
            'border-left:4px solid rgba(76,175,80,0.6); padding:15px; border-radius:10px; margin:10px 0;">'
            '✅ <strong>Strong Buy Signal:</strong> High confidence indicates favorable conditions. '
            'Consider this for portfolio entry or position increase.'
            '</div>', 
            unsafe_allow_html=True
        )
