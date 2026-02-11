"""
widgets.py - Reusable Streamlit UI widgets (glassmorphism metric cards, timeline buttons).
"""

import re
import streamlit as st
from ui.icons import get_icon


def render_timeline_buttons(key_prefix: str, current_value: str) -> str:
    """Render a row of timeline filter buttons. Returns selected value."""
    options = ["1W", "1M", "3M", "6M", "1Y", "ALL"]
    cols = st.columns(len(options))
    selected = current_value
    for i, opt in enumerate(options):
        with cols[i]:
            btn_type = "primary" if current_value == opt else "secondary"
            if st.button(opt, key=f"{key_prefix}_tl_{opt}", type=btn_type, use_container_width=True):
                selected = opt
    return selected


def render_custom_metric_card(
    icon_name: str,
    icon_color: str,
    label: str,
    value: str,
    sub_label: str,
    status: str = "neutral",
):
    """Render a glassmorphism metric card with status-tinted background."""
    status_styles = {
        "good": ("rgba(11,218,91,0.1)", "rgba(11,218,91,0.3)", "rgba(11,218,91,0.15)"),
        "maintenance": ("rgba(37,140,244,0.1)", "rgba(37,140,244,0.3)", "rgba(37,140,244,0.15)"),
        "warning": ("rgba(245,158,11,0.1)", "rgba(245,158,11,0.3)", "rgba(245,158,11,0.15)"),
        "bad": ("rgba(239,68,68,0.1)", "rgba(239,68,68,0.3)", "rgba(239,68,68,0.15)"),
        "neutral": ("rgba(30,41,59,0.5)", "rgba(255,255,255,0.08)", "rgba(37,140,244,0.1)"),
    }
    bg, border, glow = status_styles.get(status, status_styles["neutral"])
    icon_html = get_icon(icon_name, icon_color)
    css_id = re.sub(r"[^a-zA-Z0-9-]", "", label.replace(" ", "-").lower())

    st.markdown(f"""
    <style>
        .mc-{css_id} {{
            background: {bg}; backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid {border}; border-radius: 12px;
            padding: 20px; min-height: 120px; margin-bottom: 12px;
            position: relative; overflow: hidden;
            transition: all .3s cubic-bezier(.4,0,.2,1);
        }}
        .mc-{css_id}:hover {{
            border-color: rgba(37,140,244,0.4);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,.3), 0 0 20px {glow};
            transform: translateY(-2px);
        }}
    </style>
    <div class="mc-{css_id}">
        <div style="display:flex;align-items:center;margin-bottom:8px;">
            {icon_html}
            <span style="font-size:10px;font-weight:600;color:#94a3b8;margin-left:8px;text-transform:uppercase;letter-spacing:.05em;">{label}</span>
        </div>
        <div style="font-size:2rem;font-weight:700;color:#fff;">{value}</div>
        <div style="font-size:.75rem;color:#94a3b8;margin-top:6px;">{sub_label}</div>
    </div>
    """, unsafe_allow_html=True)
