# =============================================================================
# SAKER PRO - Demo Edition (Streamlit Community Cloud)
# =============================================================================
"""
Simplified demo of the Saker Pro fitness coach.
Supports Hevy CSV upload; all other data sources replaced with demo data.
"""

import base64
import sys
from pathlib import Path

# Ensure saker_pro_source is on sys.path for local imports
_SAKER_DIR = Path(__file__).parent.resolve()
if str(_SAKER_DIR) not in sys.path:
    sys.path.insert(0, str(_SAKER_DIR))

# --- Third Party ---
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# --- Local ---
from data.data_loader import load_workouts
from data.demo_data import (
    generate_all_demo_data,
    generate_demo_activities,
    generate_demo_nutrition,
    generate_demo_weight,
    is_demo_data,
)
from ui.icons import get_icon
from ui.theme import apply_new_styles
from ui.widgets import render_custom_metric_card, render_timeline_buttons

# =============================================================================
# PAGE CONFIG (MUST be first Streamlit command)
# =============================================================================
st.set_page_config(
    page_title="SAKER PRO",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply theme CSS
apply_new_styles()

# =============================================================================
# PLOTLY DEFAULTS
# =============================================================================
_PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=30, b=0),
    font=dict(color="#94a3b8"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
)


def _styled_chart(fig):
    """Apply Saker dark styling to a Plotly figure."""
    fig.update_layout(**_PLOTLY_LAYOUT)
    return fig


# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data(show_spinner=False)
def _load_hevy(file_bytes) -> pd.DataFrame:
    """Parse uploaded Hevy CSV bytes."""
    import io
    return load_workouts(io.BytesIO(file_bytes))


def _get_data():
    """
    Return (workouts_df, activities_df, nutrition_df, weight_df, using_demo).
    Uses uploaded Hevy data if available, otherwise demo data.
    """
    workouts_df = st.session_state.get("workouts_df")
    if workouts_df is not None and not workouts_df.empty:
        # Real Hevy data uploaded — fill other sources with demo
        demo = generate_all_demo_data()
        return workouts_df, demo["activities"], demo["nutrition"], demo["weight"], False

    # Full demo mode
    demo = generate_all_demo_data()
    return demo["workouts"], demo["activities"], demo["nutrition"], demo["weight"], True


# =============================================================================
# SIDEBAR
# =============================================================================

def _render_sidebar():
    """Build sidebar navigation and return selected page name."""
    with st.sidebar:
        # === LOGO ===
        _logo_path = _SAKER_DIR / "assets" / "img" / "bluelogo_small.png"
        if not _logo_path.exists():
            _logo_path = _SAKER_DIR / "assets" / "img" / "bluelogo.png"

        if _logo_path.exists():
            with open(_logo_path, "rb") as _f:
                _logo_b64 = base64.b64encode(_f.read()).decode()
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0 14px 0;
                        margin:0 0 12px 0;border-bottom:1px solid rgba(255,255,255,0.08);">
                <img src="data:image/png;base64,{_logo_b64}"
                     style="width:40px;height:40px;min-width:40px;border-radius:10px;
                            object-fit:cover;box-shadow:0 0 15px rgba(37,140,244,0.4);" />
                <div>
                    <div style="font-size:1.1rem;font-weight:700;color:#ffffff;
                                letter-spacing:0.1em;line-height:1.2;">SAKER <b style="color:#258cf4;">PRO</b></div>
                    <div style="font-size:.65rem;color:#258cf4;text-transform:uppercase;
                                letter-spacing:.08em;font-weight:600;">DEMO</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:12px;padding:10px 0 14px 0;
                        margin:0 0 12px 0;border-bottom:1px solid rgba(255,255,255,0.08);">
                <div style="width:40px;height:40px;min-width:40px;background:linear-gradient(135deg,#258cf4,#1d72c4);
                            border-radius:10px;display:flex;align-items:center;justify-content:center;
                            box-shadow:0 0 15px rgba(37,140,244,0.5);">
                    <span style="font-size:1.25rem;font-weight:800;color:#ffffff;
                                text-shadow:0 0 10px rgba(255,255,255,0.5);">S</span>
                </div>
                <div>
                    <div style="font-size:1.1rem;font-weight:700;color:#ffffff;
                                letter-spacing:0.1em;line-height:1.2;">SAKER <b style="color:#258cf4;">PRO</b></div>
                    <div style="font-size:.65rem;color:#258cf4;text-transform:uppercase;
                                letter-spacing:.08em;font-weight:600;">DEMO</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # === NAVIGATION (st.radio + JS-injected SVG icons) ===
        _nav_icons = {
            "Dashboard": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
            "Coach": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
            "Plan": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
            "Analytics": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
            "Race Prep": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
            "Settings": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
        }

        _nav_list = list(_nav_icons.keys())
        if "sidebar_nav" not in st.session_state:
            st.session_state["sidebar_nav"] = "Dashboard"

        st.radio(
            "Navigation",
            options=_nav_list,
            key="sidebar_nav",
            label_visibility="collapsed",
        )

        # Inject SVG icons into radio labels + pin pilot card to bottom via JavaScript
        _icons_js = '''<script>(function(){
            const pd = window.parent.document;
            const icons = {''' + ",".join(
                f'"{k}": `{v}`' for k, v in _nav_icons.items()
            ) + '''};
            function inject(){
                const labels = pd.querySelectorAll('[data-testid="stSidebar"] .stRadio label p');
                labels.forEach(p => {
                    const t = p.textContent.trim();
                    if(icons[t] && !p.querySelector('svg')){
                        p.innerHTML = icons[t] + '<span style="margin-left:10px;">' + t + '</span>';
                        p.style.display = 'flex';
                        p.style.alignItems = 'center';
                    }
                });
            }
            inject();
            setInterval(inject, 500);
        })();</script>'''
        components.html(_icons_js, height=0)

        # Spacer pushes the pilot card to the bottom
        st.markdown('<div style="flex:1;"></div>', unsafe_allow_html=True)

        # === PILOT CARD (pinned to bottom via sidebar flex layout) ===
        st.markdown("""
        <style>
            section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
                display: flex !important;
                flex-direction: column !important;
                height: 100vh !important;
                padding-bottom: 1rem !important;
            }
        </style>
        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:14px;display:flex;align-items:center;gap:12px;
                    margin-top:auto;">
            <div style="width:42px;height:42px;min-width:42px;border-radius:50%;
                        background:linear-gradient(135deg,#258cf4,#1d72c4);
                        display:flex;align-items:center;justify-content:center;
                        font-weight:700;color:#fff;font-size:1rem;">
                SP
            </div>
            <div>
                <div style="color:#e2e8f0;font-weight:600;font-size:.85rem;">Demo Pilot</div>
                <div style="color:#64748b;font-size:.7rem;">Community Cloud</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state["sidebar_nav"]


# =============================================================================
# ANALYTICS HELPERS
# =============================================================================

def _filter_by_range(df: pd.DataFrame, timeline: str) -> pd.DataFrame:
    """Filter DataFrame by timeline string (1W, 1M, 3M, etc)."""
    if df is None or df.empty or "date" not in df.columns:
        return df
    today = pd.Timestamp.today().normalize()
    mapping = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    days = mapping.get(timeline)
    if days is None:
        return df
    cutoff = today - pd.Timedelta(days=days)
    return df[df["date"] >= cutoff]


def _compute_acwr(workouts_df: pd.DataFrame) -> dict:
    """Compute Acute-to-Chronic Workload Ratio from workout tonnage."""
    if workouts_df is None or workouts_df.empty:
        return {"acwr": None, "acute": 0, "chronic": 0}
    daily = workouts_df.groupby("date")["tonnage_lbs"].sum().sort_index()
    today = pd.Timestamp.today().normalize()
    week_ago = today - pd.Timedelta(days=7)
    month_ago = today - pd.Timedelta(days=28)
    acute = daily[daily.index >= week_ago].mean()
    chronic = daily[daily.index >= month_ago].mean()
    if pd.isna(chronic) or chronic == 0:
        return {"acwr": None, "acute": float(acute or 0), "chronic": 0}
    ratio = float(acute / chronic)
    return {"acwr": round(ratio, 2), "acute": float(acute), "chronic": float(chronic)}


def _compute_readiness(acwr_val, avg_rpe):
    """Simple readiness score 0-100."""
    score = 75.0
    if acwr_val is not None:
        if 0.8 <= acwr_val <= 1.3:
            score += 15
        elif acwr_val > 1.5:
            score -= 20
        elif acwr_val < 0.6:
            score -= 10
    if avg_rpe is not None:
        if avg_rpe > 8.5:
            score -= 10
        elif avg_rpe < 7:
            score += 5
    return max(0, min(100, int(score)))


def _lift_snapshot(workouts_df: pd.DataFrame) -> pd.DataFrame:
    """Best set (heaviest weight) for each exercise."""
    if workouts_df is None or workouts_df.empty:
        return pd.DataFrame()
    best = (
        workouts_df.dropna(subset=["weight_lbs"])
        .sort_values("weight_lbs", ascending=False)
        .groupby("exercise_title")
        .first()
        .reset_index()
    )
    return best[["exercise_title", "weight_lbs", "reps", "date"]].head(15)


def _compute_cardio_acwr(activities_df: pd.DataFrame) -> dict:
    """Compute Acute-to-Chronic Workload Ratio for cardio (duration-based)."""
    if activities_df is None or activities_df.empty:
        return {"acwr": None, "acute": 0, "chronic": 0}
    daily = activities_df.groupby("date")["duration_min"].sum().sort_index()
    today = pd.Timestamp.today().normalize()
    acute = daily[daily.index >= today - pd.Timedelta(days=7)].mean()
    chronic = daily[daily.index >= today - pd.Timedelta(days=28)].mean()
    if pd.isna(chronic) or chronic == 0:
        return {"acwr": None, "acute": float(acute or 0), "chronic": 0}
    return {"acwr": round(float(acute / chronic), 2), "acute": float(acute), "chronic": float(chronic)}


def _compute_leg_interference(workouts_df: pd.DataFrame, activities_df: pd.DataFrame) -> dict:
    """Compute leg-training / running overlap (interference score 0–100)."""
    if workouts_df is None or workouts_df.empty or activities_df is None or activities_df.empty:
        return {"score": 0, "events": 0, "status": "No Data", "lsl48": 0, "lel24": 0}
    leg_kw = ["squat", "leg press", "lunge", "leg curl", "leg extension", "calf"]
    w_lower = workouts_df["exercise_title"].str.lower()
    leg_dates = sorted(
        workouts_df[w_lower.apply(lambda x: any(k in str(x) for k in leg_kw))]["date"].dt.date.unique()
    )
    run_dates = sorted(
        activities_df[activities_df["activity_type"] == "Running"]["date"].dt.date.unique()
    )
    lsl48 = 0  # leg sessions with a run within 48h before
    lel24 = 0  # leg sessions with a run within 24h after
    for ld in leg_dates:
        for rd in run_dates:
            diff = (rd - ld).days
            if -2 <= diff < 0:
                lsl48 += 1
            elif 0 < diff <= 1:
                lel24 += 1
    total_events = lsl48 + lel24
    max_possible = max(len(leg_dates), 1)
    score = min(100, int(total_events / max_possible * 100))
    status = "Low Risk" if score < 30 else "Moderate" if score < 60 else "High Risk"
    return {"score": score, "events": total_events, "status": status,
            "lsl48": lsl48, "lel24": lel24}


def _muscle_group(exercise_title: str) -> str:
    """Map exercise name to muscle group."""
    ex = str(exercise_title).lower()
    if any(k in ex for k in ["squat", "leg press", "lunge", "leg extension"]):
        return "Quads"
    if any(k in ex for k in ["deadlift", "rdl", "romanian", "leg curl", "hamstring"]):
        return "Post. Chain"
    if any(k in ex for k in ["bench", "chest", "push-up", "fly"]):
        return "Chest"
    if any(k in ex for k in ["row", "pull", "lat"]):
        return "Back"
    if any(k in ex for k in ["press", "shoulder", "overhead"]):
        return "Shoulders"
    if any(k in ex for k in ["curl", "bicep", "tricep", "arm", "pushdown"]):
        return "Arms"
    if any(k in ex for k in ["calf"]):
        return "Calves"
    return "Other"


# =============================================================================
# PAGE: DASHBOARD
# =============================================================================

def render_dashboard(workouts_df, activities_df, nutrition_df, weight_df, using_demo):
    """Main dashboard with KPI cards, risk console, and overview charts."""
    if using_demo:
        st.info("Viewing sample data. Upload your Hevy export in **Settings** to see your real stats.", icon="ℹ️")

    # Pre-compute shared data
    acwr = _compute_acwr(workouts_df)
    cardio_acwr = _compute_cardio_acwr(activities_df)
    last_7 = _filter_by_range(workouts_df, "1W")
    last_28 = _filter_by_range(workouts_df, "1M")
    avg_rpe = round(last_7["rpe"].mean(), 1) if (not last_7.empty and "rpe" in last_7.columns and last_7["rpe"].notna().any()) else None
    acwr_val = acwr["acwr"]

    # ── MISSION STATUS ─────────────────────────────────────────────────
    st.markdown(f"### {get_icon('analytics', 'blue', 20)} Mission Status", unsafe_allow_html=True)

    # Equal-height card CSS
    st.markdown("""
    <style>
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div {
            display: flex; flex-direction: column;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- Lifting Status ---
    if acwr_val is None:
        lift_status, lift_label = "neutral", "No data"
        lift_display = "--"
        lift_phase = "No Data"
    elif acwr_val > 1.5:
        lift_status, lift_label = "bad", "Spike Risk"
        lift_display = "Overreaching"
        lift_phase = "Overreaching"
    elif 1.1 < acwr_val <= 1.5:
        lift_status, lift_label = "good", "Sweet Spot"
        lift_display = "Peaking"
        lift_phase = "Peaking"
    elif 0.8 <= acwr_val <= 1.1:
        lift_status, lift_label = "maintenance", "Stable"
        lift_display = "Maintenance"
        lift_phase = "Maintenance"
    else:
        lift_status, lift_label = "warning", "Under-loading"
        lift_display = "Deloading"
        lift_phase = "Deloading"

    # --- Cardio Status ---
    c_acwr_val = cardio_acwr["acwr"]
    if c_acwr_val is None:
        cardio_status, cardio_label = "neutral", "No data"
        cardio_display = "--"
        cardio_phase = "No Data"
    elif c_acwr_val > 1.5:
        cardio_status, cardio_label = "bad", "Spike Risk"
        cardio_display = "Overreaching"
        cardio_phase = "Overreaching"
    elif 1.1 < c_acwr_val <= 1.5:
        cardio_status, cardio_label = "good", "Sweet Spot"
        cardio_display = "Peaking"
        cardio_phase = "Peaking"
    elif 0.8 <= c_acwr_val <= 1.1:
        cardio_status, cardio_label = "maintenance", "Stable"
        cardio_display = "Maintenance"
        cardio_phase = "Maintenance"
    else:
        cardio_status, cardio_label = "warning", "Under-loading"
        cardio_display = "Deloading"
        cardio_phase = "Deloading"

    # --- Diet Status ---
    if nutrition_df is not None and not nutrition_df.empty:
        recent_n = nutrition_df.tail(7)
        avg_cal = int(recent_n["calories"].mean())
        tdee_est = 2500  # baseline estimate
        cal_diff = avg_cal - tdee_est
        if abs(cal_diff) < 150:
            diet_status, diet_label = "good", "On Target"
            diet_display = "Maintenance"
        elif cal_diff > 300:
            diet_status, diet_label = "warning", "Surplus"
            diet_display = "Bulking"
        elif cal_diff < -300:
            diet_status, diet_label = "warning", "Deficit"
            diet_display = "Cutting"
        else:
            diet_status, diet_label = "maintenance", "Slight " + ("Surplus" if cal_diff > 0 else "Deficit")
            diet_display = "Lean " + ("Bulk" if cal_diff > 0 else "Cut")
    else:
        diet_status, diet_label, diet_display = "neutral", "No data", "--"
        avg_cal = 0

    c1, c2, c3 = st.columns(3)
    with c1:
        render_custom_metric_card("dumbbell", "blue", "Lifting Status", lift_display, f"ACWR {acwr_val:.2f} · {lift_label}" if acwr_val else "No data", lift_status)
    with c2:
        render_custom_metric_card("activity", "green", "Cardio Status", cardio_display, f"ACWR {c_acwr_val:.2f} · {cardio_label}" if c_acwr_val else "No data", cardio_status)
    with c3:
        render_custom_metric_card("food", "orange", "Diet Status", diet_display, f"{avg_cal:,} kcal avg · {diet_label}" if avg_cal else "No data", diet_status)

    # ── RISK CONSOLE ───────────────────────────────────────────────────
    st.markdown(f"### {get_icon('zap', 'orange', 20)} Risk Console", unsafe_allow_html=True)

    risk_l, risk_r = st.columns(2)

    with risk_l:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                {get_icon('activity', 'red', 20)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Leg Interference Monitor</span>
            </div>
            """, unsafe_allow_html=True)

            # Leg interference gauge
            leg_data = _compute_leg_interference(workouts_df, activities_df)
            _li_score = leg_data["score"]
            _li_color = "#0bda5b" if _li_score < 30 else "#f59e0b" if _li_score < 60 else "#ef4444"
            _li_pct = min(100, _li_score)

            st.markdown(f"""
            <div style="text-align:center;padding:16px 0 8px;">
                <div style="position:relative;width:180px;height:110px;margin:0 auto;overflow:hidden;">
                    <div style="width:180px;height:180px;border-radius:50%;
                                background:conic-gradient({_li_color} {_li_pct * 1.8}deg, rgba(30,41,59,0.8) 0deg);
                                clip-path:inset(0 0 50% 0);"></div>
                    <div style="position:absolute;top:15px;left:15px;width:150px;height:150px;border-radius:50%;
                                background:#0f172a;clip-path:inset(0 0 50% 0);"></div>
                    <div style="position:absolute;top:35px;left:0;right:0;text-align:center;">
                        <div style="font-size:2rem;font-weight:700;color:{_li_color};">{_li_score}%</div>
                        <div style="font-size:.7rem;color:#94a3b8;margin-top:2px;">INTERFERENCE</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;gap:8px;">
                <div style="flex:1;text-align:center;padding:8px;background:rgba(30,41,59,0.5);border-radius:8px;">
                    <div style="font-size:1.1rem;font-weight:700;color:#60a5fa;">{leg_data['lsl48']}</div>
                    <div style="font-size:.7rem;color:#94a3b8;">LSL-48h</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:rgba(30,41,59,0.5);border-radius:8px;">
                    <div style="font-size:1.1rem;font-weight:700;color:#a78bfa;">{leg_data['lel24']}</div>
                    <div style="font-size:.7rem;color:#94a3b8;">LEL-24h</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:rgba(30,41,59,0.5);border-radius:8px;">
                    <div style="font-size:1.1rem;font-weight:700;color:{_li_color};">{leg_data['status']}</div>
                    <div style="font-size:.7rem;color:#94a3b8;">STATUS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Explanatory note
            st.markdown("""
            <div style="margin-top:10px;padding:8px 10px;background:rgba(30,41,59,0.3);border-left:3px solid #60a5fa;
                        border-radius:0 6px 6px 0;font-size:.75rem;color:#94a3b8;line-height:1.5;">
                <strong style="color:#e2e8f0;">What is this?</strong> Measures overlap between leg-heavy
                lifting sessions and running. <strong>LSL-48h</strong> = runs within 48h before a leg day.
                <strong>LEL-24h</strong> = runs within 24h after. High scores indicate insufficient recovery
                between lower-body work and cardio.
            </div>
            """, unsafe_allow_html=True)

    with risk_r:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                {get_icon('bolt', 'purple', 20)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Training Monotony</span>
            </div>
            """, unsafe_allow_html=True)

            # Calculate monotony (std dev of daily loads)
            if not last_28.empty:
                _daily_loads = last_28.groupby("date")["tonnage_lbs"].sum()
                _mono_mean = _daily_loads.mean()
                _mono_std = _daily_loads.std()
                _monotony = round(_mono_mean / _mono_std, 2) if _mono_std > 0 else 0
            else:
                _mono_mean, _mono_std, _monotony = 0, 0, 0

            _mono_color = "#0bda5b" if _monotony < 1.5 else "#f59e0b" if _monotony < 2.0 else "#ef4444"
            _mono_label = "Low Risk" if _monotony < 1.5 else "Moderate" if _monotony < 2.0 else "High Risk"
            _mono_pct = min(100, int(_monotony / 3.0 * 100))

            st.markdown(f"""
            <div style="text-align:center;padding:16px 0 8px;">
                <div style="position:relative;width:180px;height:110px;margin:0 auto;overflow:hidden;">
                    <div style="width:180px;height:180px;border-radius:50%;
                                background:conic-gradient({_mono_color} {_mono_pct * 1.8}deg, rgba(30,41,59,0.8) 0deg);
                                clip-path:inset(0 0 50% 0);"></div>
                    <div style="position:absolute;top:15px;left:15px;width:150px;height:150px;border-radius:50%;
                                background:#0f172a;clip-path:inset(0 0 50% 0);"></div>
                    <div style="position:absolute;top:35px;left:0;right:0;text-align:center;">
                        <div style="font-size:2rem;font-weight:700;color:{_mono_color};">{_monotony:.2f}</div>
                        <div style="font-size:.7rem;color:#94a3b8;margin-top:2px;">MONOTONY</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;gap:8px;">
                <div style="flex:1;text-align:center;padding:8px;background:rgba(30,41,59,0.5);border-radius:8px;">
                    <div style="font-size:1.1rem;font-weight:700;color:#60a5fa;">{_mono_mean:,.0f}</div>
                    <div style="font-size:.7rem;color:#94a3b8;">AVG LOAD</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:rgba(30,41,59,0.5);border-radius:8px;">
                    <div style="font-size:1.1rem;font-weight:700;color:#a78bfa;">{_mono_std:,.0f}</div>
                    <div style="font-size:.7rem;color:#94a3b8;">STD DEV</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:rgba(30,41,59,0.5);border-radius:8px;">
                    <div style="font-size:1.1rem;font-weight:700;color:{_mono_color};">{_mono_label}</div>
                    <div style="font-size:.7rem;color:#94a3b8;">STATUS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Explanatory note
            st.markdown("""
            <div style="margin-top:10px;padding:8px 10px;background:rgba(30,41,59,0.3);border-left:3px solid #a78bfa;
                        border-radius:0 6px 6px 0;font-size:.75rem;color:#94a3b8;line-height:1.5;">
                <strong style="color:#e2e8f0;">What is this?</strong> Training monotony = avg daily load ÷
                std deviation. Values <strong>&lt;1.5</strong> are healthy variation.
                <strong>&gt;2.0</strong> means sessions are too uniform, raising overtraining and
                illness risk. Vary intensity to keep monotony low.
            </div>
            """, unsafe_allow_html=True)

    # ── PERFORMANCE ARCHITECTURE ────────────────────────────────────────
    st.markdown(f"### {get_icon('trending_up', 'blue', 20)} Performance Architecture", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            {get_icon('activity', 'blue', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Fitness, Fatigue &amp; Form</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Chronic Training Load (CTL) builds fitness. Acute Training Load (ATL) tracks fatigue. The difference is your Form (TSB).")

        if not workouts_df.empty:
            # Compute CTL (42-day EMA), ATL (7-day EMA), TSB
            daily = workouts_df.groupby("date")["tonnage_lbs"].sum().sort_index()
            idx = pd.date_range(daily.index.min(), daily.index.max())
            daily = daily.reindex(idx, fill_value=0)
            ctl = daily.ewm(span=42).mean()
            atl = daily.ewm(span=7).mean()
            tsb = ctl - atl
            pmc_df = pd.DataFrame({"Date": idx, "Fitness (CTL)": ctl.values, "Fatigue (ATL)": atl.values, "Form (TSB)": tsb.values})

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=pmc_df["Date"], y=pmc_df["Fitness (CTL)"], name="Fitness (CTL)",
                                     line=dict(color="#258cf4", width=3)))
            fig.add_trace(go.Scatter(x=pmc_df["Date"], y=pmc_df["Fatigue (ATL)"], name="Fatigue (ATL)",
                                     line=dict(color="#ec4899", width=2, dash="dot")))
            fig.add_trace(go.Bar(x=pmc_df["Date"], y=pmc_df["Form (TSB)"], name="Form (TSB)",
                                 marker_color=[("#0bda5b" if v >= 0 else "#ef4444") for v in pmc_df["Form (TSB)"]],
                                 opacity=0.5))
            fig.update_layout(**_PLOTLY_LAYOUT, height=350, barmode="overlay",
                              legend=dict(orientation="h", y=-0.12))
            st.plotly_chart(fig)

            # PMC summary metrics
            _ctl_now = ctl.iloc[-1] if len(ctl) > 0 else 0
            _atl_now = atl.iloc[-1] if len(atl) > 0 else 0
            _tsb_now = _ctl_now - _atl_now
            _tsb_label = "Fresh" if _tsb_now > 15 else "Recovered" if _tsb_now > 0 else "Balanced" if _tsb_now > -10 else "Deep Fatigue"
            _tsb_color = "#0bda5b" if _tsb_now > 0 else "#f59e0b" if _tsb_now > -10 else "#ef4444"

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Fitness (CTL)", f"{_ctl_now:,.0f}")
            with m2:
                st.metric("Fatigue (ATL)", f"{_atl_now:,.0f}")
            with m3:
                st.metric("Form (TSB)", f"{_tsb_now:+,.0f}")
            with m4:
                st.markdown(f"""
                <div style="text-align:center;padding:10px;">
                    <div style="font-size:.75rem;color:#94a3b8;margin-bottom:4px;">STATUS</div>
                    <div style="background:{_tsb_color}22;color:{_tsb_color};padding:6px 12px;
                                border-radius:20px;font-weight:700;font-size:.85rem;">{_tsb_label}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No workout data available for PMC.")

    # ── TRAINING VOLUME ─────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {get_icon('chart', 'blue', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Training Volume</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Weekly cardio duration by type (bars) with lifting tonnage trend (line).")

        has_lifting = not workouts_df.empty
        has_cardio = not activities_df.empty

        if has_lifting or has_cardio:
            fig = go.Figure()

            # Cardio bars (by type, stacked)
            if has_cardio:
                cardio_weekly = activities_df.copy()
                cardio_weekly["week"] = cardio_weekly["date"].dt.to_period("W").dt.start_time
                for act_type, color in [("Running", "#0bda5b"), ("Cycling", "#a78bfa"), ("Walking", "#f59e0b")]:
                    subset = cardio_weekly[cardio_weekly["activity_type"] == act_type]
                    if not subset.empty:
                        wk = subset.groupby("week")["duration_min"].sum().reset_index()
                        wk.columns = ["Week", "Minutes"]
                        fig.add_trace(go.Bar(
                            x=wk["Week"], y=wk["Minutes"],
                            name=f"{act_type} (min)", marker_color=color,
                            yaxis="y",
                        ))

            # Lifting line
            if has_lifting:
                daily_ton = workouts_df.groupby("date")["tonnage_lbs"].sum().reset_index()
                daily_ton["week"] = daily_ton["date"].dt.to_period("W").dt.start_time
                weekly_lift = daily_ton.groupby("week")["tonnage_lbs"].sum().reset_index()
                weekly_lift.columns = ["Week", "Tonnage"]
                fig.add_trace(go.Scatter(
                    x=weekly_lift["Week"], y=weekly_lift["Tonnage"],
                    name="Lifting (lbs)", line=dict(color="#258cf4", width=3),
                    mode="lines+markers", marker=dict(size=5, color="#258cf4"),
                    yaxis="y2",
                ))

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=30, b=0),
                font=dict(color="#94a3b8"),
                height=380, barmode="stack",
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(title="Cardio (min)", gridcolor="rgba(255,255,255,0.05)", side="left"),
                yaxis2=dict(title="Tonnage (lbs)", overlaying="y", side="right",
                            gridcolor="rgba(255,255,255,0.03)"),
                legend=dict(orientation="h", y=-0.15),
            )
            st.plotly_chart(fig)
        else:
            st.caption("No training data available.")

    # ── NUTRITION & BODY WEIGHT ─────────────────────────────────────────
    col_n, col_w = st.columns(2)
    with col_n:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('food', 'green', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Nutrition Balance</span>
            </div>
            """, unsafe_allow_html=True)
            if not nutrition_df.empty:
                recent_n = nutrition_df.tail(30)
                avg_cal = int(recent_n["calories"].mean())
                # Nutrition gap summary
                st.markdown(f"""
                <div style="display:flex;justify-content:center;padding:8px 0 12px;
                            border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:12px;">
                    <div style="text-align:center;">
                        <div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;">AVG CALORIES</div>
                        <div style="color:#bef264;font-size:1.25rem;font-weight:700;">{avg_cal:,} kcal</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=recent_n["date"], y=recent_n["calories"], name="Calories",
                                         line=dict(color="#bef264", width=2),
                                         fill="tozeroy", fillcolor="rgba(190,242,100,0.1)"))
                fig.update_layout(**_PLOTLY_LAYOUT, height=280, showlegend=False)
                st.plotly_chart(fig)
            else:
                st.caption("No nutrition data.")

    with col_w:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('scale', 'blue', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Body Weight</span>
            </div>
            """, unsafe_allow_html=True)
            if not weight_df.empty:
                recent_w = weight_df.tail(60).copy()
                current_wt = recent_w["weight_lbs"].iloc[-1]
                wt_change = current_wt - recent_w["weight_lbs"].iloc[0]
                wt_arrow = "↑" if wt_change > 0 else "↓" if wt_change < 0 else "→"
                wt_color = "#ef4444" if abs(wt_change) > 5 else "#f59e0b" if abs(wt_change) > 2 else "#0bda5b"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;padding:8px 0 12px;
                            border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:12px;">
                    <div>
                        <div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;">CURRENT</div>
                        <div style="color:#258cf4;font-size:1.25rem;font-weight:700;">{current_wt:.1f} lbs</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;">60-DAY CHANGE</div>
                        <div style="color:{wt_color};font-size:1.25rem;font-weight:700;">{wt_arrow} {abs(wt_change):.1f} lbs</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                recent_w["trend"] = recent_w["weight_lbs"].rolling(7, min_periods=1).mean()
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=recent_w["date"], y=recent_w["weight_lbs"], name="Scale",
                                         mode="markers", marker=dict(color="#94a3b8", size=5, opacity=0.6)))
                fig.add_trace(go.Scatter(x=recent_w["date"], y=recent_w["trend"], name="7d Trend",
                                         line=dict(color="#258cf4", width=3)))
                fig.update_layout(**_PLOTLY_LAYOUT, height=280, legend=dict(orientation="h", y=-0.15))
                st.plotly_chart(fig)
            else:
                st.caption("No weight data.")

    # ── ACTIVITY LEDGER ────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {get_icon('clipboard', 'blue', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Activity Ledger</span>
        </div>
        """, unsafe_allow_html=True)

        # Build combined ledger from workouts and activities (last 14 days)
        ledger_rows = []
        today = pd.Timestamp.today().normalize()
        cutoff = today - pd.Timedelta(days=14)

        if not workouts_df.empty:
            recent_w = workouts_df[workouts_df["date"] >= cutoff]
            for d, grp in recent_w.groupby("date"):
                tonnage = int(grp["tonnage_lbs"].sum())
                n_sets = len(grp)
                title = grp["title"].iloc[0] if "title" in grp.columns else "Weights"
                load_lvl = "High" if tonnage > 30000 else "Medium" if tonnage > 15000 else "Light"
                load_color = "#ef4444" if load_lvl == "High" else "#f59e0b" if load_lvl == "Medium" else "#0bda5b"
                tag = "Strength"
                tag_color = "#258cf4"
                ledger_rows.append({
                    "date": d, "type": title, "detail": f"{n_sets} sets · {tonnage:,} lbs",
                    "load": load_lvl, "load_color": load_color,
                    "tag": tag, "tag_color": tag_color,
                })

        if not activities_df.empty:
            recent_a = activities_df[activities_df["date"] >= cutoff]
            for _, row in recent_a.iterrows():
                atype = row.get("activity_type", "Cardio")
                dist = row.get("distance_miles", 0)
                dur = row.get("duration_min", 0)
                load_lvl = "High" if dur > 50 else "Medium" if dur > 30 else "Light"
                load_color = "#ef4444" if load_lvl == "High" else "#f59e0b" if load_lvl == "Medium" else "#0bda5b"
                tag = "Cardio"
                tag_color = "#0bda5b"
                ledger_rows.append({
                    "date": row["date"], "type": atype,
                    "detail": f"{dur:.0f} min · {dist:.1f} mi",
                    "load": load_lvl, "load_color": load_color,
                    "tag": tag, "tag_color": tag_color,
                })

        if ledger_rows:
            ledger_rows.sort(key=lambda r: r["date"], reverse=True)
            # Build HTML table
            rows_html = ""
            for r in ledger_rows[:20]:
                date_str = r["date"].strftime("%b %d")
                rows_html += f"""
                <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:10px 12px;color:#94a3b8;font-size:.8rem;white-space:nowrap;">{date_str}</td>
                    <td style="padding:10px 12px;text-align:center;">
                        <span style="background:{r['tag_color']}22;color:{r['tag_color']};
                                     padding:3px 10px;border-radius:12px;font-size:.7rem;font-weight:600;">{r['tag']}</span>
                    </td>
                    <td style="padding:10px 12px;color:#e2e8f0;font-weight:600;font-size:.85rem;">{r['type']}</td>
                    <td style="padding:10px 12px;color:#94a3b8;font-size:.8rem;">{r['detail']}</td>
                    <td style="padding:10px 12px;text-align:center;">
                        <span style="background:{r['load_color']}22;color:{r['load_color']};
                                     padding:3px 10px;border-radius:12px;font-size:.7rem;font-weight:600;">{r['load']}</span>
                    </td>
                </tr>"""

            # Color key
            key_html = """
            <div style="display:flex;gap:16px;margin-bottom:10px;">
                <span style="display:flex;align-items:center;gap:5px;font-size:.75rem;color:#94a3b8;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#0bda5b;"></span> Light
                </span>
                <span style="display:flex;align-items:center;gap:5px;font-size:.75rem;color:#94a3b8;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f59e0b;"></span> Medium
                </span>
                <span style="display:flex;align-items:center;gap:5px;font-size:.75rem;color:#94a3b8;">
                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#ef4444;"></span> High
                </span>
            </div>
            """

            st.markdown(f"""
            {key_html}
            <div style="overflow-x:auto;border-radius:8px;">
            <table style="width:100%;border-collapse:collapse;font-family:inherit;">
                <thead>
                    <tr style="border-bottom:2px solid rgba(37,140,244,0.3);position:sticky;top:0;background:#0f172a;">
                        <th style="padding:10px 12px;text-align:left;color:#64748b;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;">Date</th>
                        <th style="padding:10px 12px;text-align:center;color:#64748b;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;">Tag</th>
                        <th style="padding:10px 12px;text-align:left;color:#64748b;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;">Activity</th>
                        <th style="padding:10px 12px;text-align:left;color:#64748b;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;">Detail</th>
                        <th style="padding:10px 12px;text-align:center;color:#64748b;font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;">Load</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.caption("No recent activities.")

    # ── MUSCLE BALANCE & CARDIO ZONES ──────────────────────────────────
    sys_l, sys_r = st.columns(2)

    with sys_l:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('dumbbell', 'teal', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Muscle Balance</span>
            </div>
            """, unsafe_allow_html=True)
            if not workouts_df.empty and "exercise_title" in workouts_df.columns:
                w_copy = workouts_df.copy()
                w_copy["muscle"] = w_copy["exercise_title"].apply(_muscle_group)
                muscle_sets = w_copy.groupby("muscle").size().reset_index(name="Sets")
                muscle_vol = w_copy.groupby("muscle")["tonnage_lbs"].sum().reset_index()
                muscle_vol.columns = ["muscle", "Volume"]

                # Build closed radar (repeat first point to close the shape)
                _theta_labels = [f"{m} ({s})" for m, s in zip(muscle_sets["muscle"], muscle_sets["Sets"])]
                _sets_r = muscle_sets["Sets"].tolist()
                _theta_closed = _theta_labels + [_theta_labels[0]]
                _sets_closed = _sets_r + [_sets_r[0]]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=_sets_closed,
                    theta=_theta_closed,
                    fill="toself", name="Sets",
                    line=dict(color="#6366f1"), fillcolor="rgba(99,102,241,0.15)",
                ))
                if not muscle_vol.empty:
                    _max_sets = muscle_sets["Sets"].max() if muscle_sets["Sets"].max() > 0 else 1
                    _max_vol = muscle_vol["Volume"].max() if muscle_vol["Volume"].max() > 0 else 1
                    _norm_vol = (muscle_vol["Volume"] / _max_vol * _max_sets).tolist()
                    _vol_closed = _norm_vol + [_norm_vol[0]]
                    fig.add_trace(go.Scatterpolar(
                        r=_vol_closed,
                        theta=_theta_closed,
                        fill="toself", name="Volume (scaled)",
                        line=dict(color="#14b8a6"), fillcolor="rgba(20,184,166,0.1)",
                    ))
                fig.update_layout(**_PLOTLY_LAYOUT, height=350,
                                  polar=dict(bgcolor="rgba(0,0,0,0)",
                                             radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.08)"),
                                             angularaxis=dict(gridcolor="rgba(255,255,255,0.08)")),
                                  legend=dict(orientation="h", y=-0.05))
                st.plotly_chart(fig)
            else:
                st.caption("No workout data.")

    with sys_r:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('heart', 'green', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Cardio Zones</span>
            </div>
            """, unsafe_allow_html=True)
            if not activities_df.empty and "avg_hr" in activities_df.columns:
                def _hr_zone(hr):
                    if hr < 130:
                        return "Zone 1 (Recovery)"
                    elif hr < 150:
                        return "Zone 2 (Aerobic)"
                    elif hr < 165:
                        return "Zone 3 (Tempo)"
                    elif hr < 180:
                        return "Zone 4 (Threshold)"
                    else:
                        return "Zone 5 (VO2max)"

                act_copy = activities_df.copy()
                act_copy["zone"] = act_copy["avg_hr"].apply(_hr_zone)
                zone_counts = act_copy.groupby("zone")["duration_min"].sum().reset_index()
                zone_counts.columns = ["Zone", "Minutes"]

                zone_colors = {
                    "Zone 1 (Recovery)": "#94a3b8",
                    "Zone 2 (Aerobic)": "#0bda5b",
                    "Zone 3 (Tempo)": "#f59e0b",
                    "Zone 4 (Threshold)": "#ef4444",
                    "Zone 5 (VO2max)": "#ec4899",
                }
                colors = [zone_colors.get(z, "#258cf4") for z in zone_counts["Zone"]]

                fig = go.Figure(data=[go.Pie(
                    labels=zone_counts["Zone"], values=zone_counts["Minutes"],
                    hole=0, textinfo="percent",
                    textposition="inside",
                    marker=dict(colors=colors),
                    textfont=dict(size=13, color="#ffffff"),
                    insidetextorientation="horizontal",
                )])
                fig.update_layout(**_PLOTLY_LAYOUT, height=380,
                                  showlegend=True,
                                  legend=dict(orientation="h", y=-0.1,
                                              font=dict(size=11, color="#e2e8f0")))
                st.plotly_chart(fig)
            else:
                st.caption("No HR data available.")


# =============================================================================
# PAGE: ANALYTICS
# =============================================================================

def render_analytics(workouts_df, activities_df, nutrition_df, weight_df, using_demo):
    """Detailed analytics with timeline filters, radar chart, and exercise progress."""
    st.markdown(f"### {get_icon('chart', 'blue', 20)} Analytics", unsafe_allow_html=True)

    if using_demo:
        st.info("Viewing sample data. Upload your Hevy export in **Settings**.", icon="ℹ️")

    # Timeline filter
    tl_key = "analytics_timeline"
    if tl_key not in st.session_state:
        st.session_state[tl_key] = "3M"

    # Data Range selector row
    dr_left, dr_right = st.columns([2, 3])
    with dr_left:
        st.markdown("##### Data Range")
    with dr_right:
        selected_tl = render_timeline_buttons("analytics", st.session_state[tl_key])
        if selected_tl != st.session_state[tl_key]:
            st.session_state[tl_key] = selected_tl
            st.rerun()

    w_filtered = _filter_by_range(workouts_df, selected_tl)
    a_filtered = _filter_by_range(activities_df, selected_tl)

    # ── LIFTING VOLUME (Line) ────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {get_icon('trending_up', 'blue', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Lifting Volume Over Time</span>
        </div>
        """, unsafe_allow_html=True)
        if not w_filtered.empty:
            daily_vol = w_filtered.groupby("date")["tonnage_lbs"].sum().reset_index()
            daily_vol.columns = ["Date", "Volume (lbs)"]
            daily_vol = daily_vol.sort_values("Date")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_vol["Date"], y=daily_vol["Volume (lbs)"],
                mode="lines+markers", name="Tonnage",
                line=dict(color="#258cf4", width=2),
                marker=dict(size=4, color="#258cf4"),
                fill="tozeroy", fillcolor="rgba(37,140,244,0.1)",
            ))
            # 7-day rolling average
            if len(daily_vol) >= 3:
                daily_vol["Trend"] = daily_vol["Volume (lbs)"].rolling(
                    min(7, len(daily_vol)), min_periods=1
                ).mean()
                fig.add_trace(go.Scatter(
                    x=daily_vol["Date"], y=daily_vol["Trend"],
                    mode="lines", name="7d Avg",
                    line=dict(color="#f59e0b", width=2, dash="dot"),
                ))
            fig.update_layout(**_PLOTLY_LAYOUT, height=300,
                              legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig)
        else:
            st.caption("No lifting data for selected range.")

    # ── CARDIO VOLUME (Bar by type) ─────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {get_icon('activity', 'green', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Cardio Volume by Activity</span>
        </div>
        """, unsafe_allow_html=True)
        if not a_filtered.empty:
            cardio_data = a_filtered.copy()
            cardio_data["week"] = cardio_data["date"].dt.to_period("W").dt.start_time
            type_colors = {"Running": "#0bda5b", "Cycling": "#a78bfa", "Walking": "#f59e0b",
                           "Swimming": "#38bdf8"}
            fig = go.Figure()
            for act_type in cardio_data["activity_type"].unique():
                subset = cardio_data[cardio_data["activity_type"] == act_type]
                wk = subset.groupby("week")["duration_min"].sum().reset_index()
                wk.columns = ["Week", "Minutes"]
                color = type_colors.get(act_type, "#94a3b8")
                fig.add_trace(go.Bar(
                    x=wk["Week"], y=wk["Minutes"],
                    name=act_type, marker_color=color,
                ))
            fig.update_layout(**_PLOTLY_LAYOUT, height=300, barmode="stack",
                              legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig)
        else:
            st.caption("No cardio data for selected range.")

    # ── SYSTEM OPTIMIZATION ─────────────────────────────────────────────
    st.markdown(f"### {get_icon('dumbbell', 'teal', 20)} System Optimization", unsafe_allow_html=True)

    opt_l, opt_r = st.columns(2)

    with opt_l:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('dumbbell', 'teal', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Muscle Balance</span>
            </div>
            """, unsafe_allow_html=True)
            if not w_filtered.empty and "exercise_title" in w_filtered.columns:
                def _muscle(ex):
                    ex_l = str(ex).lower()
                    if any(k in ex_l for k in ["squat", "leg press", "lunge"]):
                        return "Quads"
                    if any(k in ex_l for k in ["deadlift", "rdl", "romanian"]):
                        return "Post. Chain"
                    if any(k in ex_l for k in ["bench", "chest", "push-up", "fly"]):
                        return "Chest"
                    if any(k in ex_l for k in ["row", "pull", "lat"]):
                        return "Back"
                    if any(k in ex_l for k in ["press", "shoulder", "overhead"]):
                        return "Shoulders"
                    if any(k in ex_l for k in ["curl", "bicep", "tricep", "arm"]):
                        return "Arms"
                    if any(k in ex_l for k in ["calf"]):
                        return "Calves"
                    return "Other"

                w_copy = w_filtered.copy()
                w_copy["muscle"] = w_copy["exercise_title"].apply(_muscle)

                # Radar chart — sets and volume per muscle group
                muscle_sets = w_copy.groupby("muscle").size().reset_index(name="Sets")
                muscle_vol = w_copy.groupby("muscle")["tonnage_lbs"].sum().reset_index()
                muscle_vol.columns = ["muscle", "Volume"]

                categories = muscle_sets["muscle"].tolist()
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=muscle_sets["Sets"].tolist(),
                    theta=[f"{m} ({s})" for m, s in zip(muscle_sets["muscle"], muscle_sets["Sets"])],
                    fill="toself", name="Sets",
                    line=dict(color="#6366f1"), fillcolor="rgba(99,102,241,0.15)",
                ))
                if not muscle_vol.empty:
                    # Normalize volume to same scale as sets for overlay
                    _max_sets = muscle_sets["Sets"].max() if muscle_sets["Sets"].max() > 0 else 1
                    _max_vol = muscle_vol["Volume"].max() if muscle_vol["Volume"].max() > 0 else 1
                    _norm_vol = (muscle_vol["Volume"] / _max_vol * _max_sets).tolist()
                    fig.add_trace(go.Scatterpolar(
                        r=_norm_vol,
                        theta=[f"{m} ({s})" for m, s in zip(muscle_sets["muscle"], muscle_sets["Sets"])],
                        fill="toself", name="Volume (scaled)",
                        line=dict(color="#14b8a6"), fillcolor="rgba(20,184,166,0.1)",
                    ))
                fig.update_layout(**_PLOTLY_LAYOUT, height=350,
                                  polar=dict(bgcolor="rgba(0,0,0,0)",
                                             radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.08)"),
                                             angularaxis=dict(gridcolor="rgba(255,255,255,0.08)")),
                                  legend=dict(orientation="h", y=-0.05))
                st.plotly_chart(fig)
            else:
                st.caption("No data.")

    with opt_r:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('activity', 'green', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Cardio Distance</span>
            </div>
            """, unsafe_allow_html=True)
            if not a_filtered.empty and "distance_miles" in a_filtered.columns:
                weekly_dist = a_filtered.copy()
                weekly_dist["week"] = weekly_dist["date"].dt.to_period("W").dt.start_time
                wd = weekly_dist.groupby("week")["distance_miles"].sum().reset_index()
                wd.columns = ["Week", "Miles"]
                fig = px.bar(wd, x="Week", y="Miles", color_discrete_sequence=["#0bda5b"])
                fig.update_layout(**_PLOTLY_LAYOUT, height=350)
                st.plotly_chart(fig)
            else:
                st.caption("No cardio data.")

    # ── RPE TREND ───────────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {get_icon('bolt', 'orange', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">RPE Trend</span>
        </div>
        """, unsafe_allow_html=True)
        if not w_filtered.empty and "rpe" in w_filtered.columns and w_filtered["rpe"].notna().any():
            rpe_daily = w_filtered.groupby("date")["rpe"].mean().reset_index()
            rpe_daily.columns = ["Date", "Avg RPE"]
            fig = px.line(rpe_daily, x="Date", y="Avg RPE", color_discrete_sequence=["#f59e0b"])
            fig.add_hline(y=8.5, line_dash="dash", line_color="#ef4444", annotation_text="High fatigue")
            fig.update_traces(line_width=2)
            fig.update_layout(**_PLOTLY_LAYOUT, height=280)
            st.plotly_chart(fig)
        else:
            st.caption("No RPE data available.")

    # ── EXERCISE PROGRESS ───────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {get_icon('trending_up', 'teal', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Exercise Progress</span>
        </div>
        """, unsafe_allow_html=True)
        if not w_filtered.empty and "exercise_title" in w_filtered.columns:
            exercises = sorted(w_filtered["exercise_title"].dropna().unique())
            if exercises:
                sel_ex = st.selectbox("Select exercise", exercises, key="analytics_ex_select")
                ex_data = w_filtered[w_filtered["exercise_title"] == sel_ex].copy()
                if not ex_data.empty:
                    best_per_day = ex_data.groupby("date")["weight_lbs"].max().reset_index()
                    best_per_day.columns = ["Date", "Best Weight (lbs)"]
                    best_per_day = best_per_day.sort_values("Date")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=best_per_day["Date"], y=best_per_day["Best Weight (lbs)"],
                        mode="markers", name="Best Set",
                        marker=dict(color="#258cf4", size=8),
                    ))
                    # Rolling trend line instead of lowess (avoids statsmodels dependency)
                    if len(best_per_day) >= 3:
                        trend = best_per_day["Best Weight (lbs)"].rolling(
                            min(5, len(best_per_day)), min_periods=1, center=True
                        ).mean()
                        fig.add_trace(go.Scatter(
                            x=best_per_day["Date"], y=trend,
                            mode="lines", name="Trend",
                            line=dict(color="#6366f1", width=2, dash="dot"),
                        ))
                    fig.update_layout(**_PLOTLY_LAYOUT, height=300)
                    st.plotly_chart(fig)
        else:
            st.caption("No exercise data.")


# =============================================================================
# PAGE: COACH (Placeholder)
# =============================================================================

def render_coach():
    """AI Coach page - placeholder for demo."""
    st.markdown(f"### {get_icon('brain', 'purple', 20)} AI Coach", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                border-radius:16px;padding:40px;text-align:center;margin:20px 0;">
        <div style="font-size:3rem;margin-bottom:16px;">🧠</div>
        <h3 style="color:#258cf4;margin-bottom:12px;">Unlock AI Coach with Saker Pro</h3>
        <p style="color:#94a3b8;max-width:500px;margin:0 auto;line-height:1.6;">
            Saker Pro Desktop includes a local LLM-powered coach
            that runs entirely on your hardware via <strong>llama.cpp</strong>.
            Get personalised training insights, injury guidance, and
            adaptive programming — all without sending your data to the cloud.
        </p>
        <div style="margin-top:24px;">
            <span style="background:rgba(37,140,244,0.15);color:#258cf4;padding:8px 20px;
                         border-radius:20px;font-size:.85rem;font-weight:600;letter-spacing:.03em;">
                Upgrade to Saker Pro
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Richer sample insights demonstrating what the coach does
    st.markdown(f"#### {get_icon('chat', 'blue', 18)} Sample Coach Outputs", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
            <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#258cf4,#1d72c4);
                        display:flex;align-items:center;justify-content:center;font-size:.9rem;">🧠</div>
            <div><span style="color:#258cf4;font-weight:700;font-size:.9rem;">SAKER COACH</span>
            <span style="color:#64748b;font-size:.75rem;margin-left:8px;">Weekly Debrief</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
**Load Management — Week of Feb 3**

Your ACWR is **1.12** — right in the sweet spot (0.8–1.3). Acute load averaged
38,400 lbs vs a 28-day chronic baseline of 34,200 lbs. No spike risk detected.

**Strength Observations:**
- Bench press moved from 185 → 190 lbs for 3×5 — solid 2.7% progression
- Squat volume is 14 sets this week vs 16 last week. Consider adding 1–2 back-off sets.
- Your posterior chain (RDL, rows) is under-represented at 8 sets vs 14 for pressing. Target a 1:1.5 push-pull ratio.

**Cardio & Recovery:**
- 3 running sessions this week totalling 12.4 miles. Zone 2 HR compliance was 78% — aim for 80%+.
- Average RPE is 7.8 — well managed. If RPE climbs above 8.5, consider a deload.

**Next Week Guidance:**
- Progress squat to 275 lbs 3×4 (RPE ~8)
- Add 2 sets of barbell rows to balance push-pull ratio
- Keep the Wednesday easy run under 35 minutes
        """)
        st.caption("This is a static sample. The full AI Coach generates personalised insights from your actual data.")


# =============================================================================
# PAGE: PLAN (Placeholder)
# =============================================================================

def render_plan():
    """Training Plan page - placeholder for demo."""
    st.markdown(f"### {get_icon('calendar', 'blue', 20)} Training Plan", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                border-radius:16px;padding:40px;text-align:center;margin:20px 0;">
        <div style="font-size:3rem;margin-bottom:16px;">📅</div>
        <h3 style="color:#258cf4;margin-bottom:12px;">Unlock Plan Generator with Saker Pro</h3>
        <p style="color:#94a3b8;max-width:500px;margin:0 auto;line-height:1.6;">
            Saker Pro Desktop generates periodised training plans with
            <strong>phase calculation</strong>, <strong>auto-regulation</strong>,
            and <strong>calendar export</strong>. Plans are built using
            pure Python math — no LLM needed.
        </p>
        <div style="margin-top:24px;">
            <span style="background:rgba(37,140,244,0.15);color:#258cf4;padding:8px 20px;
                         border-radius:20px;font-size:.85rem;font-weight:600;letter-spacing:.03em;">
                Upgrade to Saker Pro
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Feature highlights
    st.markdown(f"#### {get_icon('clipboard', 'teal', 18)} What the Plan Generator Does", unsafe_allow_html=True)
    feat_cols = st.columns(3)
    with feat_cols[0]:
        st.markdown("""
        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:20px;min-height:140px;">
            <div style="font-size:1.5rem;margin-bottom:8px;">📊</div>
            <div style="color:#e2e8f0;font-weight:600;font-size:.9rem;margin-bottom:6px;">Phase Periodisation</div>
            <div style="color:#94a3b8;font-size:.8rem;line-height:1.5;">Base → Build → Peak → Taper → Race. Phases calculated backwards from your target event date.</div>
        </div>
        """, unsafe_allow_html=True)
    with feat_cols[1]:
        st.markdown("""
        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:20px;min-height:140px;">
            <div style="font-size:1.5rem;margin-bottom:8px;">🔄</div>
            <div style="color:#e2e8f0;font-weight:600;font-size:.9rem;margin-bottom:6px;">Auto-Regulation</div>
            <div style="color:#94a3b8;font-size:.8rem;line-height:1.5;">Volume and intensity adjust based on your ACWR, RPE trends, and recovery status from daily check-ins.</div>
        </div>
        """, unsafe_allow_html=True)
    with feat_cols[2]:
        st.markdown("""
        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:20px;min-height:140px;">
            <div style="font-size:1.5rem;margin-bottom:8px;">📅</div>
            <div style="color:#e2e8f0;font-weight:600;font-size:.9rem;margin-bottom:6px;">Calendar Export</div>
            <div style="color:#94a3b8;font-size:.8rem;line-height:1.5;">Export your plan as an .ics file. Import directly into Google Calendar, Apple Calendar, or Outlook.</div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE: RACE PREP (Placeholder)
# =============================================================================

def render_race_prep(workouts_df, activities_df):
    """Race preparation page."""
    st.markdown(f"### {get_icon('trophy', 'orange', 20)} Race Prep", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                border-radius:16px;padding:40px;text-align:center;margin:20px 0;">
        <div style="font-size:3rem;margin-bottom:16px;">🏆</div>
        <h3 style="color:#f59e0b;margin-bottom:12px;">Race Prep Tools</h3>
        <p style="color:#94a3b8;max-width:500px;margin:0 auto;line-height:1.6;">
            The full version includes race-specific preparation tools:
            pace prediction via the <strong>Riegel formula</strong>, DOTS score
            calculation for powerlifting, taper planning, and HYROX split analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Pace estimator demo
    st.markdown(f"#### {get_icon('speed', 'green', 18)} Pace Estimator (Demo)", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        ref_dist = st.selectbox("Reference distance", ["5K", "10K", "Half Marathon"], key="rp_ref")
    with col2:
        ref_time = st.number_input("Time (minutes)", min_value=10, max_value=300, value=25, key="rp_time")
    with col3:
        target_dist = st.selectbox("Predict for", ["10K", "Half Marathon", "Marathon"], key="rp_target")

    dist_map = {"5K": 5.0, "10K": 10.0, "Half Marathon": 21.1, "Marathon": 42.2}
    d1 = dist_map.get(ref_dist, 5.0)
    d2 = dist_map.get(target_dist, 10.0)
    # Riegel formula: T2 = T1 * (D2/D1)^1.06
    predicted = ref_time * (d2 / d1) ** 1.06
    hours = int(predicted // 60)
    mins = int(predicted % 60)
    secs = int((predicted % 1) * 60)
    time_str = f"{hours}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins}:{secs:02d}"
    pace_per_km = predicted / d2
    pace_min = int(pace_per_km)
    pace_sec = int((pace_per_km % 1) * 60)

    r1, r2 = st.columns(2)
    with r1:
        render_custom_metric_card("timer", "green", "Predicted Time", time_str,
                                  f"Based on {ref_dist} in {ref_time} min", "good")
    with r2:
        render_custom_metric_card("speed", "blue", "Predicted Pace", f"{pace_min}:{pace_sec:02d}/km",
                                  f"For {target_dist}", "maintenance")

    # Training readiness for race
    st.markdown(f"#### {get_icon('target', 'red', 18)} Race Readiness", unsafe_allow_html=True)
    if not workouts_df.empty:
        acwr = _compute_acwr(workouts_df)
        last_7 = _filter_by_range(workouts_df, "1W")
        sess_count = last_7["date"].nunique() if not last_7.empty else 0
        metrics = {
            "Training Consistency": min(100, sess_count * 20),
            "Volume Trend": 75 if acwr["acwr"] and 0.8 <= acwr["acwr"] <= 1.3 else 50,
            "Taper Status": 60,
        }
        for label, score in metrics.items():
            col_l, col_r = st.columns([3, 1])
            with col_l:
                st.progress(score / 100, text=label)
            with col_r:
                st.markdown(f"**{score}%**")
    else:
        st.caption("Upload workout data to see race readiness metrics.")


# =============================================================================
# PAGE: SETTINGS
# =============================================================================

def render_settings():
    """Settings page — only Hevy CSV upload."""
    st.markdown(f"### {get_icon('settings', 'blue', 20)} Settings", unsafe_allow_html=True)

    # --- Data Import ---
    st.markdown(f"#### {get_icon('upload', 'green', 18)} Import Workout Data", unsafe_allow_html=True)
    st.caption("Upload your Hevy workout export CSV to see your real training data.")

    uploaded_file = st.file_uploader(
        "Upload Hevy CSV",
        type=["csv"],
        key="hevy_uploader",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        try:
            df = _load_hevy(uploaded_file.getvalue())
            st.session_state["workouts_df"] = df
            st.success(f"Loaded {len(df):,} sets from {df['date'].nunique()} sessions.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to parse CSV: {e}")

    # Show current data status
    st.markdown("---")
    st.markdown(f"#### {get_icon('info', 'blue', 18)} Data Status", unsafe_allow_html=True)
    wdf = st.session_state.get("workouts_df")
    if wdf is not None and not wdf.empty and not is_demo_data(wdf):
        st.success(f"**Hevy data loaded:** {len(wdf):,} sets across {wdf['date'].nunique()} sessions")
        date_range = f"{wdf['date'].min().strftime('%b %d, %Y')} — {wdf['date'].max().strftime('%b %d, %Y')}"
        st.caption(f"Date range: {date_range}")
        if st.button("Clear uploaded data", type="secondary", key="clear_hevy"):
            st.session_state.pop("workouts_df", None)
            _load_hevy.clear()
            st.rerun()
    else:
        st.warning("No Hevy data uploaded. Using demo data for all visualisations.")

    # --- Demo data info ---
    st.markdown("---")
    st.markdown(f"#### {get_icon('lightbulb', 'orange', 18)} About Demo Data", unsafe_allow_html=True)
    st.markdown("""
    When no Hevy export is uploaded, Saker Pro displays **120 days of synthetic
    training data** including:
    - **Workouts:** Push/Pull/Legs split with progressive overload
    - **Cardio:** Running, cycling, and walking activities
    - **Nutrition:** ~2,400 kcal/day with macro breakdown
    - **Weight:** Gradual trend with realistic daily variance

    All cardio, nutrition, and weight data is always synthetic in this demo.
    The full desktop version supports Garmin, Apple Health, MacroFactor, and more.
    """)

    # --- About ---
    st.markdown("---")
    st.markdown(f"#### {get_icon('shield', 'blue', 18)} About Saker Pro", unsafe_allow_html=True)
    st.markdown("""
    **Saker Pro** is a local-first, privacy-hardened desktop app for hybrid athletes.

    This is a **free demo** deployed on Streamlit Community Cloud showing the
    dashboard and analytics capabilities. The full desktop version includes:
    - Local LLM coaching via llama.cpp (100% offline)
    - Periodised plan generation with calendar export
    - Garmin / Apple Health / MacroFactor integration
    - Injury tracking with Physio-Bot
    - Advanced race preparation tools
    """)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    page = _render_sidebar()

    # Load data
    workouts_df, activities_df, nutrition_df, weight_df, using_demo = _get_data()

    # Route to page
    if page == "Dashboard":
        render_dashboard(workouts_df, activities_df, nutrition_df, weight_df, using_demo)
    elif page == "Analytics":
        render_analytics(workouts_df, activities_df, nutrition_df, weight_df, using_demo)
    elif page == "Coach":
        render_coach()
    elif page == "Plan":
        render_plan()
    elif page == "Race Prep":
        render_race_prep(workouts_df, activities_df)
    elif page == "Settings":
        render_settings()


if __name__ == "__main__":
    main()
else:
    # When run via `streamlit run main.py`
    main()
