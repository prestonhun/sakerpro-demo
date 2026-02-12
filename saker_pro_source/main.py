# =============================================================================
# SAKER PRO - Demo Edition (Streamlit Community Cloud)
# =============================================================================
"""
Simplified demo of the Saker Pro fitness coach.
Supports Strava Connect for real activity data; other sources use demo data.
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
from data.demo_data import (
    generate_all_demo_data,
    generate_demo_activities,
    generate_demo_nutrition,
    generate_demo_weight,
    is_demo_data,
)
from data.strava import (
    set_session_state_store as _strava_set_store,
    is_connected as strava_is_connected,
    get_authorization_url as strava_auth_url,
    exchange_code as strava_exchange_code,
    clear_tokens as strava_clear_tokens,
    load_tokens as strava_load_tokens,
    fetch_activities as strava_fetch_activities,
    get_athlete as strava_get_athlete,
    activities_to_cardio_df,
    activities_to_workouts_df,
    get_best_run_efforts,
    get_fastest_run_routes,
    enrich_activity_locations,
)
from ui.icons import get_icon
from ui.theme import apply_new_styles
from ui.widgets import (
    render_custom_metric_card,
    render_timeline_buttons,
    render_fastest_run_map_section,
    render_activity_start_map_section,
)

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
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1e293b",
        bordercolor="rgba(255,255,255,0.1)",
        font=dict(color="#e2e8f0"),
    ),
)


_HOVER_LABEL = dict(
    bgcolor="#1e293b",
    bordercolor="rgba(255,255,255,0.1)",
    font=dict(color="#e2e8f0"),
)


def _styled_chart(fig):
    """Apply Saker dark styling to a Plotly figure."""
    fig.update_layout(**_PLOTLY_LAYOUT)
    fig.update_traces(hoverlabel=_HOVER_LABEL)
    return fig


def _show_chart(fig, **kwargs):
    """Apply dark hoverlabel to every trace and display the chart."""
    # Layout-level hoverlabel is used by hovermode="x unified"
    fig.update_layout(hoverlabel=dict(
        bgcolor="#1e293b",
        bordercolor="rgba(255,255,255,0.1)",
        font=dict(color="#e2e8f0"),
    ))
    # Trace-level hoverlabel for hovermode="closest" charts
    fig.update_traces(hoverlabel=_HOVER_LABEL)
    st.plotly_chart(fig, **kwargs)


# =============================================================================
# DATA LOADING
# =============================================================================

# Strava API credentials — loaded from .streamlit/secrets.toml (NEVER committed)
try:
    _STRAVA_CLIENT_ID = st.secrets["STRAVA_CLIENT_ID"]
    _STRAVA_CLIENT_SECRET = st.secrets["STRAVA_CLIENT_SECRET"]
    _STRAVA_REDIRECT_URI = st.secrets.get("STRAVA_REDIRECT_URI", "https://sakerpro.streamlit.app/")
except Exception:
    _STRAVA_CLIENT_ID = ""
    _STRAVA_CLIENT_SECRET = ""
    _STRAVA_REDIRECT_URI = "https://sakerpro.streamlit.app/"


@st.cache_data(show_spinner="Syncing Strava…", ttl=900)
def _fetch_strava(client_id: str, client_secret: str):
    """Fetch & normalise all Strava activities (cached 15 min)."""
    raw = strava_fetch_activities(client_id, client_secret)
    # IMPORTANT: keep Strava detail calls low to avoid rate-limiting.
    # Location enrichment will improve over successive syncs via local caches.
    raw = enrich_activity_locations(raw, client_id, client_secret, max_detail_lookups=10)
    cardio_df = activities_to_cardio_df(raw)
    workouts_df = activities_to_workouts_df(raw)
    best_runs = get_best_run_efforts(raw)
    fastest_routes = get_fastest_run_routes(raw)
    return cardio_df, workouts_df, best_runs, fastest_routes, raw


def _get_data():
    """
    Return (workouts_df, activities_df, nutrition_df, weight_df, using_demo).
    Uses Strava data if connected, otherwise demo data.
    """
    strava_activities = st.session_state.get("strava_activities_df")
    strava_workouts = st.session_state.get("strava_workouts_df")

    has_strava = strava_activities is not None and not strava_activities.empty
    has_workouts = strava_workouts is not None and not strava_workouts.empty

    if has_strava or has_workouts:
        demo = generate_all_demo_data()
        act_df = strava_activities if has_strava else demo["activities"]
        wdf = strava_workouts if has_workouts else demo["workouts"]
        return wdf, act_df, demo["nutrition"], demo["weight"], False

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
        # === PILOT CARD (pinned to bottom via sidebar flex layout) ===
        # Show Strava user name if connected, otherwise "Demo Pilot"
        _strava_tokens = strava_load_tokens()
        if _strava_tokens and _strava_tokens.get("athlete_firstname"):
            _pilot_name = f"{_strava_tokens.get('athlete_firstname', '')} {_strava_tokens.get('athlete_lastname', '')}".strip()
            _pilot_initials = (_strava_tokens.get("athlete_firstname", "S")[:1] + _strava_tokens.get("athlete_lastname", "P")[:1]).upper()
            _pilot_sub = "Strava Connected"
        else:
            _pilot_name = "Demo Pilot"
            _pilot_initials = "SP"
            _pilot_sub = "Community Cloud"

        st.markdown(f"""
        <style>
            section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
                display: flex !important;
                flex-direction: column !important;
                height: 100vh !important;
                padding-bottom: 1rem !important;
            }}
        </style>
        <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:14px;display:flex;align-items:center;gap:12px;
                    margin-top:auto;">
            <div style="width:42px;height:42px;min-width:42px;border-radius:50%;
                        background:linear-gradient(135deg,#258cf4,#1d72c4);
                        display:flex;align-items:center;justify-content:center;
                        font-weight:700;color:#fff;font-size:1rem;">
                {_pilot_initials}
            </div>
            <div>
                <div style="color:#e2e8f0;font-weight:600;font-size:.85rem;">{_pilot_name}</div>
                <div style="color:#64748b;font-size:.7rem;">{_pilot_sub}</div>
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
    mapping = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730}
    days = mapping.get(timeline)
    if days is None:  # "ALL"
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
        st.info("Viewing sample data. Connect your Strava account in **Settings** to see your real stats.", icon="ℹ️")

    # Keep unfiltered copies for ACWR / risk computations that need full 28-day windows
    _raw_workouts = workouts_df
    _raw_activities = activities_df

    # Data Range selector (same component as Analytics)
    _dash_tl_key = "dashboard_timeline"
    if _dash_tl_key not in st.session_state:
        st.session_state[_dash_tl_key] = "3M"
    _dr_l, _dr_r = st.columns([2, 3])
    with _dr_l:
        st.markdown("##### Data Range")
    with _dr_r:
        _dash_sel = render_timeline_buttons("dashboard", st.session_state[_dash_tl_key])
        if _dash_sel != st.session_state[_dash_tl_key]:
            st.session_state[_dash_tl_key] = _dash_sel
            st.rerun()

    # Apply range filter to data used by charts
    dash_tl = st.session_state[_dash_tl_key]
    workouts_df = _filter_by_range(workouts_df, dash_tl)
    activities_df = _filter_by_range(activities_df, dash_tl)
    nutrition_df = _filter_by_range(nutrition_df, dash_tl)
    weight_df = _filter_by_range(weight_df, dash_tl)

    # Pre-compute shared data (ALWAYS from unfiltered data for correct 7/28 day windows)
    acwr = _compute_acwr(_raw_workouts)
    cardio_acwr = _compute_cardio_acwr(_raw_activities)
    last_7 = _filter_by_range(_raw_workouts, "1W")
    last_28 = _filter_by_range(_raw_workouts, "1M")
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
        _diet_sub = f"{avg_cal:,} kcal avg · {diet_label}" if avg_cal else "No data"
        _diet_sub = "Demo data · " + _diet_sub if avg_cal else "Demo data"
        render_custom_metric_card("food", "orange", "Diet Status", diet_display, _diet_sub, diet_status)

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

            # Leg interference gauge (uses unfiltered recent data)
            leg_data = _compute_leg_interference(_raw_workouts, _raw_activities)
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
            # Combine lifting + cardio into unified daily load
            _mono_parts = []
            if not last_28.empty:
                _mono_lift = last_28.groupby("date")["tonnage_lbs"].sum() / 1000
                _mono_parts.append(_mono_lift)
            _last_28_cardio = _filter_by_range(_raw_activities, "1M")
            if not _last_28_cardio.empty:
                _mono_cardio = _last_28_cardio.groupby("date")["duration_min"].sum()
                _mono_parts.append(_mono_cardio)

            if _mono_parts:
                _mono_combined = _mono_parts[0]
                for _mp in _mono_parts[1:]:
                    _mono_combined = _mono_combined.add(_mp, fill_value=0)
                _daily_loads = _mono_combined.sort_index()
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

            # Data-driven explanation
            if _mono_parts:
                _active_days = int((_daily_loads > 0).sum())
                _total_days = max(len(_daily_loads), 1)
                _max_load = _daily_loads.max()
                _min_load = _daily_loads[_daily_loads > 0].min() if (_daily_loads > 0).any() else 0
                _rest_days = _total_days - _active_days

                if _monotony >= 2.0:
                    _advice = ("Your daily loads are too uniform — this raises overtraining and illness risk. "
                               "Add an easy/rest day or vary intensity between hard and light sessions.")
                elif _monotony >= 1.5:
                    _advice = ("Load variation is borderline. Consider alternating a hard day with an easier one, "
                               "or adding a complete rest day to increase spread.")
                else:
                    _advice = ("Good variation. Your mix of hard, easy, and rest days keeps monotony healthy. "
                               "Maintain this pattern.")

                st.markdown(f"""
                <div style="margin-top:10px;padding:8px 10px;background:rgba(30,41,59,0.3);border-left:3px solid #a78bfa;
                            border-radius:0 6px 6px 0;font-size:.75rem;color:#94a3b8;line-height:1.6;">
                    <strong style="color:#e2e8f0;">Your data (28 days):</strong>
                    {_active_days} active days, {_rest_days} rest days.
                    Heaviest session: <strong>{_max_load:,.0f}</strong>,
                    lightest: <strong>{_min_load:,.0f}</strong>
                    (range {_max_load - _min_load:,.0f}).<br>
                    <strong style="color:{_mono_color};">{_advice}</strong>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="margin-top:10px;padding:8px 10px;background:rgba(30,41,59,0.3);border-left:3px solid #a78bfa;
                            border-radius:0 6px 6px 0;font-size:.75rem;color:#94a3b8;line-height:1.5;">
                    <strong style="color:#e2e8f0;">What is this?</strong> Training monotony = avg daily load ÷
                    std deviation. Values <strong>&lt;1.5</strong> are healthy variation.
                    <strong>&gt;2.0</strong> means sessions are too uniform, raising overtraining and
                    illness risk. Vary intensity to keep monotony low.
                </div>
                """, unsafe_allow_html=True)

    # ── NUTRITION & BODY WEIGHT ─────────────────────────────────────────
    col_n, col_w = st.columns(2)
    with col_n:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('food', 'green', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Nutrition Balance</span>
                <span style="font-size:.65rem;color:#f59e0b;background:rgba(245,158,11,0.15);padding:2px 8px;border-radius:8px;margin-left:auto;">DEMO DATA</span>
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
                _show_chart(fig)
            else:
                st.caption("No nutrition data.")

    with col_w:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('scale', 'blue', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Body Weight</span>
                <span style="font-size:.65rem;color:#f59e0b;background:rgba(245,158,11,0.15);padding:2px 8px;border-radius:8px;margin-left:auto;">DEMO DATA</span>
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
                _show_chart(fig)
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

        # Build combined ledger from all activities in the selected data range
        ledger_rows = []

        if not workouts_df.empty:
            recent_w = workouts_df
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
            recent_a = activities_df
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
            for r in ledger_rows:
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
            <div style="overflow-x:auto;max-height:420px;overflow-y:auto;border-radius:8px;">
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

    # ── ACTIVITY MAP (start points) ────────────────────────────────────
    render_activity_start_map_section(
        st.session_state.get("strava_raw"),
        using_demo=using_demo,
        key_prefix="dashboard_activity_map",
    )

    # ── FASTEST RUN PRETTYMAP (Strava route overlay) ───────────────────
    render_fastest_run_map_section(
        st.session_state.get("strava_fastest_routes"),
        st.session_state.get("strava_raw"),
        using_demo=using_demo,
        key_prefix="dashboard_fastest_route",
    )


# =============================================================================
# PAGE: ANALYTICS
# =============================================================================

def render_analytics(workouts_df, activities_df, nutrition_df, weight_df, using_demo):
    """Detailed analytics with timeline filters, radar chart, and exercise progress."""
    st.markdown(f"### {get_icon('chart', 'blue', 20)} Analytics", unsafe_allow_html=True)

    if using_demo:
        st.info("Viewing sample data. Connect Strava in **Settings** to see real data.", icon="ℹ️")

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

    # ── TRAINING VOLUME (unified) ────────────────────────────────────────
    with st.container(border=True):
        _atv_l, _atv_r = st.columns([3, 1])
        with _atv_l:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                {get_icon('chart', 'blue', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Training Volume</span>
            </div>
            """, unsafe_allow_html=True)
        with _atv_r:
            atv_unit = st.toggle("Show in minutes", value=False, key="atv_unit_toggle")

        _mod_colors = {
            "Running": "#0bda5b",
            "Cycling": "#a78bfa",
            "Walking": "#f59e0b",
            "Swimming": "#38bdf8",
            "Hiking": "#14b8a6",
            "Weights": "#258cf4",
        }

        has_lift = not w_filtered.empty
        has_card = not a_filtered.empty

        if has_lift or has_card:
            fig = go.Figure()

            # -- Cardio bars by modality (stacked, per day) --
            if has_card:
                c_day = a_filtered.copy()
                c_day["day"] = c_day["date"].dt.normalize()
                for at in sorted(c_day["activity_type"].unique()):
                    sub = c_day[c_day["activity_type"] == at]
                    if sub.empty:
                        continue
                    if atv_unit:
                        gd = sub.groupby("day")["duration_min"].sum().reset_index()
                        gd.columns = ["Day", "Value"]
                    else:
                        gd = sub.groupby("day")["distance_miles"].sum().reset_index()
                        gd.columns = ["Day", "Value"]
                    color = _mod_colors.get(at, "#94a3b8")
                    fig.add_trace(go.Bar(
                        x=gd["Day"], y=gd["Value"],
                        name=at, marker_color=color,
                    ))

            # -- Lifting (bars in minutes mode, line in miles/tonnage mode) --
            if has_lift:
                l_day = w_filtered.copy()
                l_day["day"] = l_day["date"].dt.normalize()
                if atv_unit:
                    if "duration_seconds" in l_day.columns:
                        l_day["lift_min"] = l_day["duration_seconds"].fillna(0) / 60
                    else:
                        l_day["lift_min"] = 0
                    dl = l_day.groupby("day")["lift_min"].sum().reset_index()
                    dl.columns = ["Day", "Value"]
                    fig.add_trace(go.Bar(
                        x=dl["Day"], y=dl["Value"],
                        name="Lifting", marker_color="#258cf4",
                    ))
                else:
                    dl = l_day.groupby("day")["tonnage_lbs"].sum().reset_index()
                    dl.columns = ["Day", "Tonnage"]
                    fig.add_trace(go.Scatter(
                        x=dl["Day"], y=dl["Tonnage"],
                        name="Lifting (tonnage)", mode="lines+markers",
                        line=dict(color="#258cf4", width=3),
                        marker=dict(size=5, color="#258cf4"),
                        yaxis="y2",
                    ))

            _abase = {k: v for k, v in _PLOTLY_LAYOUT.items() if k != "yaxis"}
            if atv_unit:
                fig.update_layout(
                    **_abase, height=340, barmode="stack",
                    yaxis=dict(title="Minutes", gridcolor="rgba(255,255,255,0.05)"),
                    legend=dict(orientation="h", y=-0.15),
                )
            else:
                fig.update_layout(
                    **_abase, height=340, barmode="stack",
                    yaxis=dict(title="Miles", gridcolor="rgba(255,255,255,0.05)", side="left"),
                    yaxis2=dict(title="Tonnage (lbs)", overlaying="y", side="right",
                                gridcolor="rgba(255,255,255,0.03)"),
                    legend=dict(orientation="h", y=-0.15),
                )
            _show_chart(fig, width="stretch")
        else:
            st.caption("No training data for selected range.")

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

        if not w_filtered.empty or not a_filtered.empty:
            load_parts = []
            if not w_filtered.empty:
                lift_load = w_filtered.groupby("date")["tonnage_lbs"].sum() / 1000
                load_parts.append(lift_load)
            if not a_filtered.empty:
                cardio_load = a_filtered.groupby("date")["duration_min"].sum()
                load_parts.append(cardio_load)

            if load_parts:
                combined = load_parts[0]
                for lp in load_parts[1:]:
                    combined = combined.add(lp, fill_value=0)
                daily = combined.sort_index()
            else:
                daily = pd.Series(dtype=float)

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
            _show_chart(fig)

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
            st.caption("No training data available for PMC.")

    # ── SYSTEM OPTIMIZATION ─────────────────────────────────────────────
    st.markdown(f"### {get_icon('dumbbell', 'teal', 20)} System Optimization", unsafe_allow_html=True)

    opt_l, opt_r = st.columns(2)

    with opt_l:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('dumbbell', 'teal', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Muscle Balance</span>
                <span style="font-size:.65rem;color:#f59e0b;background:rgba(245,158,11,0.15);padding:2px 8px;border-radius:8px;margin-left:auto;">DEMO DATA</span>
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

                muscle_sets = w_copy.groupby("muscle").size().reset_index(name="Sets")
                muscle_vol = w_copy.groupby("muscle")["tonnage_lbs"].sum().reset_index()
                muscle_vol.columns = ["muscle", "Volume"]

                _theta_labels = [f"{m} ({s})" for m, s in zip(muscle_sets["muscle"], muscle_sets["Sets"])]
                _sets_r = muscle_sets["Sets"].tolist()
                _theta_closed = _theta_labels + [_theta_labels[0]]
                _sets_closed = _sets_r + [_sets_r[0]]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=_sets_closed, theta=_theta_closed,
                    fill="toself", name="Sets",
                    line=dict(color="#6366f1"), fillcolor="rgba(99,102,241,0.15)",
                ))
                if not muscle_vol.empty:
                    _max_sets = muscle_sets["Sets"].max() if muscle_sets["Sets"].max() > 0 else 1
                    _max_vol = muscle_vol["Volume"].max() if muscle_vol["Volume"].max() > 0 else 1
                    _norm_vol = (muscle_vol["Volume"] / _max_vol * _max_sets).tolist()
                    _vol_closed = _norm_vol + [_norm_vol[0]]
                    fig.add_trace(go.Scatterpolar(
                        r=_vol_closed, theta=_theta_closed,
                        fill="toself", name="Volume (scaled)",
                        line=dict(color="#14b8a6"), fillcolor="rgba(20,184,166,0.1)",
                    ))
                fig.update_layout(**_PLOTLY_LAYOUT, height=350,
                                  polar=dict(bgcolor="rgba(0,0,0,0)",
                                             radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.08)"),
                                             angularaxis=dict(gridcolor="rgba(255,255,255,0.08)")),
                                  legend=dict(orientation="h", y=-0.05))
                _show_chart(fig)
            else:
                st.caption("No data.")

    with opt_r:
        with st.container(border=True):
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('heart', 'green', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Cardio Zones</span>
            </div>
            """, unsafe_allow_html=True)
            if not a_filtered.empty and "avg_hr" in a_filtered.columns:
                def _hr_zone(hr):
                    if pd.isna(hr) or hr == 0:
                        return None
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

                act_copy = a_filtered[a_filtered["avg_hr"].notna() & (a_filtered["avg_hr"] > 0)].copy()
                if act_copy.empty:
                    st.caption("No HR data available.")
                else:
                    act_copy["zone"] = act_copy["avg_hr"].apply(_hr_zone)
                    act_copy = act_copy[act_copy["zone"].notna()]
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
                    fig.update_layout(**_PLOTLY_LAYOUT, height=350,
                                      showlegend=True,
                                      legend=dict(orientation="h", y=-0.1,
                                                  font=dict(size=11, color="#e2e8f0")))
                    _show_chart(fig)
            else:
                st.caption("No HR data available.")

    # ── RUNNING PROGRESS ────────────────────────────────────────────────
    with st.container(border=True):
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            {get_icon('trending_up', 'green', 18)}
            <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Running Progress</span>
        </div>
        """, unsafe_allow_html=True)

        if not a_filtered.empty and "distance_miles" in a_filtered.columns:
            # Filter to running activities only
            _runs = a_filtered[a_filtered["activity_type"] == "Running"].copy()
            if not _runs.empty and "duration_min" in _runs.columns:
                _runs["distance_km"] = _runs["distance_miles"] * 1.60934
                _runs["pace_min_per_mi"] = _runs["duration_min"] / _runs["distance_miles"].replace(0, float("nan"))

                # Distance buckets for selection
                _dist_buckets = {
                    "1 Mile": (1.4, 1.85),       # km range
                    "5K": (4.5, 5.5),
                    "10K": (9.0, 11.0),
                    "Half Marathon": (19.0, 23.0),
                    "Marathon": (40.0, 44.0),
                    "All Runs": (0, 9999),
                }
                _rp_sel1, _rp_sel2 = st.columns(2)
                with _rp_sel1:
                    sel_dist = st.selectbox("Distance", list(_dist_buckets.keys()), key="run_progress_dist")
                with _rp_sel2:
                    sel_metric = st.selectbox("Metric", ["Time (min)", "Pace (min/mi)"], key="run_progress_metric")
                lo, hi = _dist_buckets[sel_dist]

                if sel_dist == "All Runs":
                    dist_runs = _runs.copy()
                else:
                    dist_runs = _runs[(_runs["distance_km"] >= lo) & (_runs["distance_km"] <= hi)].copy()

                if not dist_runs.empty:
                    dist_runs = dist_runs.sort_values("date")
                    dist_runs["time_str"] = dist_runs["duration_min"].apply(
                        lambda m: f"{int(m // 60)}:{int(m % 60):02d}" if m >= 60 else f"{m:.1f} min"
                    )
                    dist_runs["pace_str"] = dist_runs["pace_min_per_mi"].apply(
                        lambda p: f"{int(p)}:{int((p % 1) * 60):02d}/mi" if pd.notna(p) else "--"
                    )

                    _use_pace = sel_metric == "Pace (min/mi)"
                    _y_col = "pace_min_per_mi" if _use_pace else "duration_min"
                    _y_label = "Pace (min/mi)" if _use_pace else "Time (min)"
                    _trace_name = "Pace" if _use_pace else "Finish Time"
                    _text_col = "pace_str" if _use_pace else "time_str"
                    _hover_fmt = "%{x|%b %d, %Y}<br>Pace: %{text}<extra></extra>" if _use_pace else "%{x|%b %d, %Y}<br>Time: %{text}<br>%{y:.1f} min<extra></extra>"

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dist_runs["date"], y=dist_runs[_y_col],
                        mode="markers", name=_trace_name,
                        marker=dict(color="#0bda5b", size=9),
                        text=dist_runs[_text_col],
                        hovertemplate=_hover_fmt,
                    ))
                    if len(dist_runs) >= 3:
                        _trend = dist_runs[_y_col].rolling(
                            min(5, len(dist_runs)), min_periods=1, center=True
                        ).mean()
                        fig.add_trace(go.Scatter(
                            x=dist_runs["date"], y=_trend,
                            mode="lines", name="Trend",
                            line=dict(color="#258cf4", width=2, dash="dot"),
                        ))
                    fig.update_layout(**_PLOTLY_LAYOUT, height=320,
                                      yaxis_title=_y_label,
                                      legend=dict(orientation="h", y=-0.12))
                    _show_chart(fig)

                    # Summary metrics
                    _best_time = dist_runs["duration_min"].min()
                    _avg_time = dist_runs["duration_min"].mean()
                    _latest_time = dist_runs.iloc[-1]["duration_min"]
                    _best_pace = dist_runs["pace_min_per_mi"].min()
                    _avg_pace = dist_runs["pace_min_per_mi"].mean()
                    _latest_pace = dist_runs.iloc[-1]["pace_min_per_mi"]
                    _n = len(dist_runs)
                    _fmt_t = lambda m: f"{int(m // 60)}:{int(m % 60):02d}" if m >= 60 else f"{m:.1f}m"
                    _fmt_p = lambda p: f"{int(p)}:{int((p % 1) * 60):02d}/mi" if pd.notna(p) else "--"
                    rm1, rm2, rm3, rm4 = st.columns(4)
                    if _use_pace:
                        with rm1:
                            st.metric("Best Pace", _fmt_p(_best_pace))
                        with rm2:
                            st.metric("Avg Pace", _fmt_p(_avg_pace))
                        with rm3:
                            st.metric("Latest Pace", _fmt_p(_latest_pace))
                        with rm4:
                            st.metric("Runs", str(_n))
                    else:
                        with rm1:
                            st.metric("PR", _fmt_t(_best_time))
                        with rm2:
                            st.metric("Average", _fmt_t(_avg_time))
                        with rm3:
                            st.metric("Latest", _fmt_t(_latest_time))
                        with rm4:
                            st.metric("Runs", str(_n))
                else:
                    st.caption(f"No {sel_dist} runs found in selected range.")
            else:
                st.caption("No running data available.")
        else:
            st.caption("No cardio data available.")


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
    """Race preparation page with auto-estimated times from Strava data."""
    st.markdown(f"### {get_icon('trophy', 'orange', 20)} Race Prep", unsafe_allow_html=True)

    # Pull best run efforts from Strava if available
    best_runs = st.session_state.get("strava_best_runs", {})
    has_strava_runs = any(v is not None for v in best_runs.values())

    if has_strava_runs:
        st.markdown(f"""
        <div style="background:rgba(11,218,91,0.08);border:1px solid rgba(11,218,91,0.25);
                    border-radius:12px;padding:14px 18px;margin-bottom:16px;
                    display:flex;align-items:center;gap:10px;">
            {get_icon('check_circle', 'green', 20)}
            <span style="color:#0bda5b;font-weight:600;font-size:.9rem;">
                Race times auto-detected from your Strava history
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Show detected personal bests
        st.markdown(f"#### {get_icon('medal', 'orange', 18)} Your Personal Bests", unsafe_allow_html=True)
        pb_cols = st.columns(len([v for v in best_runs.values() if v is not None]))
        col_idx = 0
        for dist_label, time_min in best_runs.items():
            if time_min is None:
                continue
            hours = int(time_min // 60)
            mins = int(time_min % 60)
            secs = int((time_min % 1) * 60)
            time_str = f"{hours}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins}:{secs:02d}"
            with pb_cols[col_idx]:
                render_custom_metric_card("timer", "green", dist_label, time_str, "Personal Best", "good")
            col_idx += 1

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

    # Pace estimator — fully driven by Strava data
    st.markdown(f"#### {get_icon('speed', 'green', 18)} Pace Estimator", unsafe_allow_html=True)

    if not has_strava_runs:
        st.caption("Connect Strava in **Settings** to see pace predictions based on your run history.")
    else:
        # Build predictions from each available PB using Riegel formula
        ref_options = [d for d in ["5K", "10K", "Half Marathon"] if best_runs.get(d) is not None]
        target_options = ["10K", "Half Marathon", "Marathon"]

        col1, col2 = st.columns(2)
        with col1:
            ref_dist = st.selectbox("Reference distance", ref_options, key="rp_ref")
        with col2:
            target_dist = st.selectbox("Predict for", target_options, key="rp_target")

        ref_time = best_runs[ref_dist]  # minutes (from Strava PB)
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

        ref_h = int(ref_time // 60)
        ref_m = int(ref_time % 60)
        ref_s = int((ref_time % 1) * 60)
        ref_str = f"{ref_h}:{ref_m:02d}:{ref_s:02d}" if ref_h > 0 else f"{ref_m}:{ref_s:02d}"

        r1, r2 = st.columns(2)
        with r1:
            render_custom_metric_card("timer", "green", "Predicted Time", time_str,
                                      f"Based on {ref_dist} PB of {ref_str} (Strava)", "good")
        with r2:
            render_custom_metric_card("speed", "blue", "Predicted Pace", f"{pace_min}:{pace_sec:02d}/km",
                                      f"For {target_dist}", "maintenance")

    # Training readiness for race
    st.markdown(f"#### {get_icon('target', 'red', 18)} Race Readiness", unsafe_allow_html=True)
    has_activity_data = (not workouts_df.empty) or (activities_df is not None and not activities_df.empty)

    if has_activity_data:
        acwr = _compute_acwr(workouts_df)
        cardio_acwr = _compute_cardio_acwr(activities_df)
        l_acwr = acwr.get("acwr")
        c_acwr = cardio_acwr.get("acwr")

        # Consistency: count unique active days in last 28 days
        last_28_w = _filter_by_range(workouts_df, "1M")
        last_28_c = _filter_by_range(activities_df, "1M") if activities_df is not None else pd.DataFrame()
        lift_days_28 = last_28_w["date"].dt.normalize().nunique() if not last_28_w.empty else 0
        cardio_days_28 = last_28_c["date"].dt.normalize().nunique() if not last_28_c.empty else 0
        total_active_28 = min(28, lift_days_28 + cardio_days_28)
        consistency_score = min(100, int(total_active_28 / 28 * 125))  # ~4-5 days/wk = 100%

        # ACWR-based load balance (optimal 0.8-1.3)
        def _acwr_score(val):
            if val is None:
                return 40
            if 0.8 <= val <= 1.3:
                return min(100, int(80 + (1.0 - abs(val - 1.05) / 0.25) * 20))
            if 0.6 <= val < 0.8 or 1.3 < val <= 1.5:
                return 55
            return 30

        vol_score = _acwr_score(l_acwr)
        cardio_score = _acwr_score(c_acwr)

        # Volume trend (last 4 weeks vs prior 4 weeks of cardio)
        if activities_df is not None and not activities_df.empty:
            _now = pd.Timestamp.now().normalize()
            _recent_4w = activities_df[activities_df["date"] >= _now - pd.Timedelta(days=28)]
            _prior_4w = activities_df[(activities_df["date"] >= _now - pd.Timedelta(days=56)) &
                                      (activities_df["date"] < _now - pd.Timedelta(days=28))]
            _recent_vol = _recent_4w["duration_min"].sum() if not _recent_4w.empty else 0
            _prior_vol = _prior_4w["duration_min"].sum() if not _prior_4w.empty else 0
            if _prior_vol > 0:
                _vol_ratio = _recent_vol / _prior_vol
                taper_score = 80 if 0.6 <= _vol_ratio <= 0.85 else (70 if _vol_ratio < 1.0 else 50)
            else:
                taper_score = 50
        else:
            taper_score = 50

        overall = int((consistency_score + vol_score + cardio_score + taper_score) / 4)
        _ov_color = "#0bda5b" if overall >= 70 else "#f59e0b" if overall >= 50 else "#ef4444"

        st.markdown(f"""
        <div style="text-align:center;padding:12px 0 16px;">
            <div style="font-size:2.5rem;font-weight:700;color:{_ov_color};">{overall}%</div>
            <div style="font-size:.75rem;color:#94a3b8;">OVERALL READINESS</div>
        </div>
        """, unsafe_allow_html=True)

        _readiness_items = {
            "Training Consistency": (consistency_score, f"{total_active_28} days active / 28"),
            "Lifting Load Balance": (vol_score, f"ACWR {l_acwr:.2f}" if l_acwr else "No data"),
            "Cardio Load Balance": (cardio_score, f"ACWR {c_acwr:.2f}" if c_acwr else "No data"),
            "Taper Status": (taper_score, f"Vol ratio {_vol_ratio:.0%}" if activities_df is not None and not activities_df.empty and _prior_vol > 0 else "Needs more data"),
        }
        for label, (score, detail) in _readiness_items.items():
            col_l, col_m, col_r = st.columns([3, 2, 1])
            with col_l:
                st.progress(score / 100, text=label)
            with col_m:
                st.caption(detail)
            with col_r:
                st.markdown(f"**{score}%**")
    else:
        st.caption("Connect Strava in Settings to see race readiness metrics.")


# =============================================================================
# PAGE: SETTINGS
# =============================================================================

def _handle_strava_callback():
    """Process the Strava OAuth callback if an auth code is in the URL.

    Must be called EARLY in main(), before page routing, because Strava
    redirects to the root URL and the default page is Dashboard — not Settings.

    CRITICAL: The code is cleared from the URL *before* attempting the token
    exchange.  If the exchange fails or the app crashes later, the code won't
    persist in the URL and trigger a crash-restart redirect loop on Community
    Cloud.
    """
    import logging

    params = st.query_params
    code = params.get("code")
    if not code:
        return

    # ── Immediately strip the auth code from the URL ──────────────────
    # Strava codes are single-use.  Leaving it in the URL risks a loop:
    #   redirect → exchange/crash → session restart → code still in URL → repeat
    st.query_params.clear()

    # Guard: already processed this exact code in this session
    if st.session_state.get("_strava_code_used") == code:
        logging.info("[Saker Strava OAuth] Duplicate code, skipping exchange.")
        return

    if not _STRAVA_CLIENT_ID or not _STRAVA_CLIENT_SECRET:
        st.error("Strava OAuth callback received but API credentials are missing.")
        return

    logging.info(
        "[Saker Strava OAuth] Exchanging code=%s… redirect_uri=%s",
        code[:8], _STRAVA_REDIRECT_URI,
    )

    try:
        st.session_state["_strava_code_used"] = code  # mark BEFORE exchange
        strava_exchange_code(
            _STRAVA_CLIENT_ID,
            _STRAVA_CLIENT_SECRET,
            code,
            redirect_uri=_STRAVA_REDIRECT_URI,
        )
        st.session_state["_strava_exchanged"] = True
        logging.info("[Saker Strava OAuth] Token exchange succeeded.")
        st.rerun()
    except Exception as e:
        logging.error("[Saker Strava OAuth] Token exchange failed: %s", e)
        st.error(f"Strava authorization failed: {e}")
        with st.expander("Debug details", expanded=False):
            st.code(
                f"redirect_uri: {_STRAVA_REDIRECT_URI}\n"
                f"client_id:    {_STRAVA_CLIENT_ID[:6]}…\n"
                f"code:         {code[:12]}…\n"
                f"error:        {e}"
            )


def _sync_strava():
    """Fetch Strava activities and store in session state."""
    if not _STRAVA_CLIENT_ID or not _STRAVA_CLIENT_SECRET:
        st.warning("Strava credentials not configured. See `.streamlit/secrets.toml`.")
        return
    try:
        activities_df, workouts_df, best_runs, fastest_routes, raw = _fetch_strava(_STRAVA_CLIENT_ID, _STRAVA_CLIENT_SECRET)
        st.session_state["strava_activities_df"] = activities_df
        st.session_state["strava_workouts_df"] = workouts_df
        st.session_state["strava_best_runs"] = best_runs
        st.session_state["strava_fastest_routes"] = fastest_routes
        st.session_state["strava_raw"] = raw
    except Exception as e:
        st.error(f"Strava sync failed: {e}")


def render_settings():
    """Settings page — Strava Connect and data status."""
    st.markdown(f"### {get_icon('settings', 'blue', 20)} Settings", unsafe_allow_html=True)

    # Callback is now handled in main() before page routing — no need here

    # --- Strava Connect ---
    st.markdown(f"#### {get_icon('strava', 'orange', 18)} Connect Strava", unsafe_allow_html=True)
    st.caption("Link your Strava account to pull real activity data into the dashboard.")

    connected = strava_is_connected()
    has_credentials = bool(_STRAVA_CLIENT_ID and _STRAVA_CLIENT_SECRET)

    if not has_credentials:
        st.warning(
            "Strava API credentials not found.  \n"
            "Add your **Client ID** and **Client Secret** to "
            "`.streamlit/secrets.toml` and restart the app."
        )
        st.code(
            '# .streamlit/secrets.toml\n'
            'STRAVA_CLIENT_ID = "your-client-id"\n'
            'STRAVA_CLIENT_SECRET = "your-client-secret"',
            language="toml",
        )
    elif connected:
        # Show connected state
        tokens = strava_load_tokens()
        athlete_id = tokens.get("athlete_id", "Unknown") if tokens else "Unknown"
        st.markdown(f"""
        <div style="background:rgba(11,218,91,0.1);border:1px solid rgba(11,218,91,0.3);
                    border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
            {get_icon('check_circle', 'green', 24)}
            <div>
                <div style="color:#0bda5b;font-weight:700;font-size:.95rem;">Strava Connected</div>
                <div style="color:#94a3b8;font-size:.75rem;">Athlete ID: {athlete_id}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_sync, col_disconnect = st.columns(2)
        with col_sync:
            if st.button(f"Sync Activities", key="strava_sync", type="primary", use_container_width=True):
                _sync_strava()
                st.rerun()
        with col_disconnect:
            if st.button("Disconnect Strava", key="strava_disconnect", type="secondary", use_container_width=True):
                strava_clear_tokens()
                for k in ("strava_activities_df", "strava_workouts_df",
                          "strava_best_runs", "strava_fastest_routes", "strava_raw", "_strava_exchanged"):
                    st.session_state.pop(k, None)
                _fetch_strava.clear()
                st.rerun()

        # Auto-sync on first load if connected
        if "strava_activities_df" not in st.session_state:
            _sync_strava()
    elif has_credentials:
        # ── Strava Connect ────────────────────────────────────────────
        # Streamlit Community Cloud has its own auth proxy that intercepts
        # ALL incoming requests (303 → share.streamlit.io → login → back).
        # This proxy preserves Strava's ?code= query params through the
        # redirect chain, creating an infinite loop that never reaches the
        # Python code.  Direct redirect-based OAuth is therefore impossible.
        #
        # Solution: open Strava auth in a NEW TAB (target="_blank").  The
        # user authorises, Strava redirects the *new tab* which can't load
        # (since the redirect_uri points back to the app which loops), but
        # the auth code is visible in the new tab's URL bar.  The user
        # copies the code and pastes it here.
        auth_url = strava_auth_url(_STRAVA_CLIENT_ID, _STRAVA_REDIRECT_URI)

        st.markdown(
            "**Step 1** — Click the button below to authorise with Strava.  "
            "A new tab will open. After you approve access, the new tab "
            "may show an error page — **that's expected**."
        )
        st.markdown(f"""
        <a href="{auth_url}" target="_blank" rel="noopener" style="
            display:inline-flex;align-items:center;gap:10px;
            background:#FC4C02;color:#fff;font-weight:700;
            padding:12px 24px;border-radius:8px;text-decoration:none;
            font-size:.95rem;letter-spacing:.02em;
            box-shadow:0 4px 14px rgba(252,76,2,0.4);
            transition:all .2s ease;">
            {get_icon('strava', 'white', 20)}
            Connect with Strava
        </a>
        """, unsafe_allow_html=True)

        st.markdown(
            "**Step 2** — Copy the **full URL** from the new tab's address bar "
            "(it will look like `https://sakerpro.streamlit.app/?code=abc123…`) "
            "and paste it below."
        )
        pasted_url = st.text_input(
            "Paste the redirect URL here",
            key="strava_code_input",
            placeholder="https://sakerpro.streamlit.app/?code=…",
            label_visibility="collapsed",
        )
        if st.button("Complete Connection", key="strava_submit_code", type="primary"):
            # Extract the code from a full URL or accept a bare code
            _code = ""
            if pasted_url:
                if "code=" in pasted_url:
                    from urllib.parse import urlparse, parse_qs
                    try:
                        qs = parse_qs(urlparse(pasted_url).query)
                        _code = qs.get("code", [""])[0]
                    except Exception:
                        _code = pasted_url.strip()
                else:
                    _code = pasted_url.strip()

            if not _code:
                st.warning("Please paste the redirect URL or authorisation code.")
            else:
                try:
                    strava_exchange_code(
                        _STRAVA_CLIENT_ID,
                        _STRAVA_CLIENT_SECRET,
                        _code,
                        redirect_uri=_STRAVA_REDIRECT_URI,
                    )
                    st.session_state["_strava_exchanged"] = True
                    st.success("Strava connected! Syncing activities…")
                    _sync_strava()
                    st.rerun()
                except Exception as e:
                    st.error(f"Token exchange failed: {e}")
                    with st.expander("Debug details"):
                        st.code(
                            f"redirect_uri: {_STRAVA_REDIRECT_URI}\n"
                            f"code:         {_code[:20]}…\n"
                            f"error:        {e}"
                        )

    # Show current data status
    st.markdown("---")
    st.markdown(f"#### {get_icon('info', 'blue', 18)} Data Status", unsafe_allow_html=True)
    act_df = st.session_state.get("strava_activities_df")
    wkt_df = st.session_state.get("strava_workouts_df")
    best = st.session_state.get("strava_best_runs", {})
    has_any = (act_df is not None and not act_df.empty) or (wkt_df is not None and not wkt_df.empty)
    if has_any:
        n_cardio = len(act_df) if act_df is not None else 0
        n_lifting = len(wkt_df) if wkt_df is not None else 0
        all_dates = pd.concat([
            act_df[["date"]] if act_df is not None and not act_df.empty else pd.DataFrame(),
            wkt_df[["date"]] if wkt_df is not None and not wkt_df.empty else pd.DataFrame(),
        ])
        date_range = f"{all_dates['date'].min().strftime('%b %d, %Y')} — {all_dates['date'].max().strftime('%b %d, %Y')}"
        st.success(f"**Strava data loaded:** {n_cardio:,} cardio activities, {n_lifting:,} strength sessions")
        st.caption(f"Date range: {date_range}")
        if any(v is not None for v in best.values()):
            pb_str = " · ".join(f"{k}: {int(v)}min" for k, v in best.items() if v is not None)
            st.caption(f"Detected PBs: {pb_str}")
    else:
        st.warning("No Strava data synced. Using demo data for all visualisations.")

    # --- Demo data info ---
    st.markdown("---")
    st.markdown(f"#### {get_icon('lightbulb', 'orange', 18)} About Demo Data", unsafe_allow_html=True)
    st.markdown("""
    When Strava is not connected, Saker Pro displays **120 days of synthetic
    training data** including:
    - **Workouts:** Push/Pull/Legs split with progressive overload
    - **Cardio:** Running, cycling, and walking activities
    - **Nutrition:** ~2,400 kcal/day with macro breakdown
    - **Weight:** Gradual trend with realistic daily variance

    Nutrition and weight data is always synthetic in this demo.
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
    # ── Wire Strava token storage to this user's session_state ─────────
    # On Community Cloud every visitor shares the same filesystem.
    # Storing tokens in session_state keeps each user's connection private.
    _strava_set_store(
        getter=lambda: st.session_state.get("_strava_tokens"),
        setter=lambda t: st.session_state.__setitem__("_strava_tokens", t),
        clearer=lambda: st.session_state.pop("_strava_tokens", None),
    )

    # Handle Strava OAuth callback FIRST — before sidebar/page routing.
    # Strava redirects to the root URL, so this must run regardless of which
    # page the sidebar would otherwise show.
    _handle_strava_callback()

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
