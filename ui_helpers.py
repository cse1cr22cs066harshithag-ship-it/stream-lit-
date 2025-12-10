import streamlit as st

# Simple UI helpers and style injection for a healthcare look

def inject_style():
    st.markdown("""
    <style>
    :root{
      --primary: #0b5fa5; /* medical blue */
      --accent: #2aa389;  /* soft green */
      --muted: #f6f7fb;
    }
    .ch-card{background:var(--muted); padding:16px; border-radius:12px; box-shadow:0 1px 4px rgba(16,24,40,0.04);}
    .ch-header{color:var(--primary); font-weight:700}
    .ch-status{display:inline-block; padding:6px 10px; border-radius:999px; background:#e8f6ff; color:var(--primary); font-weight:600}
    .ch-action{background:var(--primary); color:white; padding:10px 18px; border-radius:10px; font-weight:600}
    .ch-metric{background:white; padding:12px; border-radius:8px}
    .small-muted{color:#6b7280}
    </style>
    """, unsafe_allow_html=True)


def status_badge(status: str):
    color = "#2aa389" if status.lower() in ("good","ok","stable","normal","low") else "#f59e0b"
    st.markdown(f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;background:{'#e6fffa' if color=='#2aa389' else '#fff7ed'};color:{color};font-weight:600'>{status}</span>", unsafe_allow_html=True)


def metric_card(title: str, value: str, trend: str = None, subtitle: str = None):
    st.markdown("<div class='ch-metric'>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-weight:700'>{title}</div>")
    st.markdown(f"<div style='font-size:20px;font-weight:800'>{value} {'↑' if trend=='up' else ('↓' if trend=='down' else '')}</div>")
    if subtitle:
        st.markdown(f"<div class='small-muted'>{subtitle}</div>")
    st.markdown("</div>", unsafe_allow_html=True)
