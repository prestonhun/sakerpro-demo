"""
widgets.py - Reusable Streamlit UI widgets (glassmorphism metric cards, timeline buttons).
"""

import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ui.icons import get_icon


def _decode_polyline(polyline_str: str) -> list[tuple[float, float]]:
    """Decode an encoded polyline into (lat, lon) pairs (dependency-free)."""
    if not polyline_str or not isinstance(polyline_str, str):
        return []

    coords: list[tuple[float, float]] = []
    index = 0
    lat = 0
    lon = 0
    length = len(polyline_str)

    while index < length:
        shift = 0
        result = 0
        while True:
            if index >= length:
                return coords
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        shift = 0
        result = 0
        while True:
            if index >= length:
                return coords
            b = ord(polyline_str[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlon = ~(result >> 1) if (result & 1) else (result >> 1)
        lon += dlon

        coords.append((lat / 1e5, lon / 1e5))

    return coords


def _auto_zoom(lat_span: float, lon_span: float) -> float:
    """Heuristic map zoom based on route bounding box size."""
    span = max(abs(lat_span), abs(lon_span))
    if span <= 0.005:
        return 15
    if span <= 0.02:
        return 14
    if span <= 0.05:
        return 13
    if span <= 0.15:
        return 12
    if span <= 0.4:
        return 10
    if span <= 1.0:
        return 8
    return 5


def _map_config() -> dict:
    # Enable better map controls (scroll zoom + visible toolbar)
    return {
        "scrollZoom": True,
        "displayModeBar": True,
        "responsive": True,
    }


def _format_duration_hm(seconds: int) -> str:
    if seconds <= 0:
        return "--"
    minutes = int(round(seconds / 60))
    hours = minutes // 60
    mins = minutes % 60
    if hours <= 0:
        return f"{mins}m"
    return f"{hours}h {mins:02d}m"


def _wallart_height(lat_span: float, lon_span: float) -> int:
    """Pick a figure height that feels like a poster/wall-art based on route size."""
    span = max(abs(lat_span), abs(lon_span))
    if span <= 0.01:
        return 520
    if span <= 0.05:
        return 560
    if span <= 0.2:
        return 610
    return 660


def render_fastest_run_map_section(
    fastest_routes: dict | None,
    using_demo: bool,
    *,
    key_prefix: str = "dash_fastest_map",
):
    """Dashboard section: generate a 'PrettyMap' for the fastest run route."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('gps_fixed', 'blue', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Fastest Run Route</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if using_demo:
            st.markdown(
                f"""
                <div style="background:rgba(30,41,59,0.5);border:1px solid rgba(255,255,255,0.08);
                            border-radius:12px;padding:16px;display:flex;align-items:center;gap:12px;">
                    {get_icon('strava', 'orange', 22)}
                    <div>
                        <div style="color:#e2e8f0;font-weight:700;font-size:.9rem;">Connect Strava to see your fastest route</div>
                        <div style="color:#94a3b8;font-size:.75rem;line-height:1.4;">This section draws your fastest run route from Strava and overlays it on a dark map.</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        if not fastest_routes or not isinstance(fastest_routes, dict):
            st.caption("Connect Strava in **Settings** to generate a PrettyMap from your fastest run.")
            return

        available = [k for k, v in fastest_routes.items() if v is not None and v.get("summary_polyline")]
        if not available:
            st.caption("No GPS routes found for your fastest runs (indoor/treadmill runs often have no route).")
            return

        sel_key = f"{key_prefix}_distance"
        default_idx = 0
        current = st.session_state.get(sel_key)
        if current in available:
            default_idx = available.index(current)

        dist = st.selectbox(
            "Select distance",
            options=available,
            index=default_idx,
            key=sel_key,
        )

        run = fastest_routes.get(dist) or {}
        poly = run.get("summary_polyline")
        pts = _decode_polyline(poly)
        if len(pts) < 2:
            st.caption("Route polyline not available for that activity.")
            return

        lats = [p[0] for p in pts]
        lons = [p[1] for p in pts]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)

        # Pad bounds so the route doesn't get clipped by markers/title.
        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon
        pad = 1.5
        min_lat_p = min_lat - (lat_span * pad)
        max_lat_p = max_lat + (lat_span * pad)
        min_lon_p = min_lon - (lon_span * pad)
        max_lon_p = max_lon + (lon_span * pad)

        # If the route is essentially a point (very short activities), fall back to a sane pad.
        if lat_span <= 1e-6:
            min_lat_p, max_lat_p = min_lat - 0.002, max_lat + 0.002
        if lon_span <= 1e-6:
            min_lon_p, max_lon_p = min_lon - 0.002, max_lon + 0.002

        center_lat = (min_lat_p + max_lat_p) / 2
        center_lon = (min_lon_p + max_lon_p) / 2
        # NOTE: We intentionally do not set mapbox.bounds here, because that
        # prevents zooming out beyond the bounds (feels like zoom-out is disabled).
        zoom = max(1, _auto_zoom(max_lat_p - min_lat_p, max_lon_p - min_lon_p) - 3)

        elapsed_s = int(run.get("elapsed_time_s") or 0)
        name = run.get("name") or "Run"

        date_str = str(run.get("start_date_local") or "")[:10]
        date_part = f" · {date_str}" if date_str else ""

        dist_m = float(run.get("distance_m") or 0)
        dist_mi = dist_m / 1609.344 if dist_m > 0 else 0.0
        dist_part = f"{dist_mi:.2f} mi" if dist_mi else "--"

        city = run.get("location_city") or ""
        if isinstance(city, str):
            city = city.strip()
        if not city:
            # Fall back to state/country if city isn't available
            stt = run.get("location_state") or ""
            ctry = run.get("location_country") or ""
            city = " · ".join([p for p in [str(stt).strip(), str(ctry).strip()] if p])
        city = city or "Unknown"

        caption_lines = [
            name or "Run",
            f"{dist} · {dist_part}",
            f"{date_str or '--'} · {city}",
            f"Time: {_format_duration_hm(elapsed_s)}",
        ]
        caption_html = "<br>".join(caption_lines)

        fig = go.Figure()
        # Soft glow underlay for a cleaner 'pretty map' look.
        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode="lines",
                line=dict(color="rgba(37,140,244,0.25)", width=10),
                name="Glow",
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode="lines",
                line=dict(color="#258cf4", width=4),
                name="Route",
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=[lats[0]],
                lon=[lons[0]],
                mode="markers",
                marker=dict(size=10, color="#0bda5b"),
                name="Start",
                hovertemplate="Start<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=[lats[-1]],
                lon=[lons[-1]],
                mode="markers",
                marker=dict(size=10, color="#ef4444"),
                name="End",
                hovertemplate="End<extra></extra>",
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=62, b=0),
            showlegend=False,
            uirevision=key_prefix,
            height=_wallart_height(max_lat_p - min_lat_p, max_lon_p - min_lon_p),
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom,
            ),
        )

        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.01,
            y=0.02,
            xanchor="left",
            yanchor="bottom",
            align="left",
            text=(
                "<span style='font-size:14px;font-weight:700;color:#e2e8f0;'>"
                + caption_html
                + "</span>"
            ),
            showarrow=False,
            bgcolor="rgba(15,23,42,0.65)",
            bordercolor="rgba(255,255,255,0.12)",
            borderwidth=1,
            borderpad=10,
        )

        st.plotly_chart(fig, width="stretch", config=_map_config())


_ACTIVITY_TYPE_MAP = {
    "Run": "Running",
    "VirtualRun": "Running",
    "TrailRun": "Running",
    "Ride": "Cycling",
    "VirtualRide": "Cycling",
    "GravelRide": "Cycling",
    "MountainBikeRide": "Cycling",
    "Walk": "Walking",
    "Hike": "Walking",
    "Swim": "Swimming",
    "WeightTraining": "Weights",
    "Crossfit": "Weights",
    "Workout": "Weights",
}


_ACTIVITY_COLORS = {
    "Running": "#0bda5b",
    "Cycling": "#a78bfa",
    "Walking": "#f59e0b",
    "Swimming": "#38bdf8",
    "Hiking": "#14b8a6",
    "Weights": "#258cf4",
}


_US_STATE_ABBR = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC",
}


def _format_pace_min_mile(elapsed_s: int, dist_m: float) -> str:
    if elapsed_s <= 0 or dist_m <= 0:
        return "--"
    miles = dist_m / 1609.344
    if miles <= 0:
        return "--"
    pace_s = elapsed_s / miles
    pace_min = int(pace_s // 60)
    pace_sec = int(round(pace_s % 60))
    if pace_sec == 60:
        pace_min += 1
        pace_sec = 0
    return f"{pace_min}:{pace_sec:02d}/mi"


def render_activity_start_map_section(
    raw_activities: list[dict] | None,
    using_demo: bool,
    *,
    key_prefix: str = "dash_activity_start_map",
):
    """Replace the activity heatmap with a start-location dot map."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('map', 'green', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Activity Map</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if using_demo:
            st.caption("Connect Strava in **Settings** to see a map of your activity start locations.")
            return

        if not raw_activities:
            st.caption("No Strava activities synced yet.")
            return

        points: list[dict] = []
        us_state_counts: dict[str, int] = {}
        for act in raw_activities:
            start = act.get("start_latlng")
            if not (isinstance(start, (list, tuple)) and len(start) == 2):
                continue
            lat, lon = start
            if lat is None or lon is None:
                continue

            sport = act.get("sport_type") or act.get("type", "")
            friendly = _ACTIVITY_TYPE_MAP.get(sport, str(sport) if sport else "Other")
            date_str = str(act.get("start_date_local") or "")[:10] or "--"
            dist_m = float(act.get("distance") or 0)
            elapsed_s = int(act.get("elapsed_time") or 0)

            # Optional: US state aggregation (uses Strava-provided location_state)
            # This avoids reverse geocoding (privacy + extra dependencies).
            loc_country_raw = (act.get("location_country") or "")
            loc_country = str(loc_country_raw).strip().lower()
            loc_state = (act.get("location_state") or "").strip()

            # Accept either full names or ISO codes for US.
            is_us = loc_country in (
                "united states", "usa", "us", "u.s.", "u.s.a.", "united states of america", "us", "usa", "united-states", "united_states", "unitedstates",
                "us", "usa", "u.s", "u.s.", "u.s.a", "u.s.a.",
                "us"  # redundant but harmless
            ) or str(loc_country_raw).strip().upper() == "US"

            if loc_state and (is_us or loc_country == ""):
                abbr = None
                if len(loc_state) == 2 and loc_state.isalpha():
                    abbr = loc_state.upper()
                else:
                    abbr = _US_STATE_ABBR.get(loc_state.lower())
                if abbr:
                    us_state_counts[abbr] = us_state_counts.get(abbr, 0) + 1

            dist_mi = dist_m / 1609.344 if dist_m > 0 else 0.0
            time_str = _format_duration_hm(elapsed_s)
            pace_str = _format_pace_min_mile(elapsed_s, dist_m)

            points.append({
                "lat": float(lat),
                "lon": float(lon),
                "type": friendly,
                "date": date_str,
                "distance_mi": dist_mi,
                "time": time_str,
                "pace": pace_str,
                "name": act.get("name", ""),
            })

        if not points:
            st.caption("No activities with GPS start locations found.")
            return

        # US State heatmap (if we have any state info)
        if us_state_counts:
            state_df = pd.DataFrame({
                "state": list(us_state_counts.keys()),
                "count": list(us_state_counts.values()),
            })
            ch = px.choropleth(
                state_df,
                locations="state",
                locationmode="USA-states",
                color="count",
                scope="usa",
                color_continuous_scale=["#e2e8f0", "#94a3b8", "#258cf4"],
            )
            ch.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_showscale=False,
            )
            st.plotly_chart(ch, width="stretch", config=_map_config())

        # Robust centering: focus the viewport on where the *majority* of points are,
        # instead of letting a few outliers dominate the bounds.
        all_lats = sorted(p["lat"] for p in points)
        all_lons = sorted(p["lon"] for p in points)

        def _quantile(sorted_vals: list[float], q: float) -> float:
            if not sorted_vals:
                return 0.0
            n = len(sorted_vals)
            idx = int(round((n - 1) * q))
            idx = max(0, min(n - 1, idx))
            return float(sorted_vals[idx])

        q_lo, q_hi = 0.10, 0.90
        min_lat, max_lat = _quantile(all_lats, q_lo), _quantile(all_lats, q_hi)
        min_lon, max_lon = _quantile(all_lons, q_lo), _quantile(all_lons, q_hi)

        # Center on median cluster.
        center_lat = _quantile(all_lats, 0.50)
        center_lon = _quantile(all_lons, 0.50)

        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon
        pad = 0.30
        min_lat_p = min_lat - max(lat_span * pad, 0.02)
        max_lat_p = max_lat + max(lat_span * pad, 0.02)
        min_lon_p = min_lon - max(lon_span * pad, 0.02)
        max_lon_p = max_lon + max(lon_span * pad, 0.02)

        zoom = max(3, _auto_zoom(max_lat_p - min_lat_p, max_lon_p - min_lon_p) - 1)

        fig = go.Figure()

        # Global heat layer based on activity density (counts at start points).
        # This gives a "heatmap" view worldwide without requiring admin-boundary shapefiles.
        fig.add_trace(
            go.Densitymapbox(
                lat=[p["lat"] for p in points],
                lon=[p["lon"] for p in points],
                z=[1] * len(points),
                radius=12,
                opacity=0.35,
                colorscale=[
                    [0.0, "rgba(226,232,240,0.0)"],
                    [0.25, "rgba(37,140,244,0.15)"],
                    [0.6, "rgba(37,140,244,0.35)"],
                    [1.0, "rgba(37,140,244,0.7)"],
                ],
                showscale=False,
                name="Heat",
                hoverinfo="skip",
            )
        )

        types = sorted({p["type"] for p in points})
        for t in types:
            subset = [p for p in points if p["type"] == t]
            color = _ACTIVITY_COLORS.get(t, "#94a3b8")
            customdata = [
                [p["date"], f"{p['distance_mi']:.2f} mi" if p["distance_mi"] else "--", p["time"], p["pace"], p["name"]]
                for p in subset
            ]
            fig.add_trace(
                go.Scattermapbox(
                    lat=[p["lat"] for p in subset],
                    lon=[p["lon"] for p in subset],
                    mode="markers",
                    marker=dict(size=9, color=color, opacity=0.9),
                    name=t,
                    customdata=customdata,
                    hovertemplate=(
                        "<b>%{fullData.name}</b><br>"
                        "%{customdata[4]}<br>"
                        "Date: %{customdata[0]}<br>"
                        "Distance: %{customdata[1]}<br>"
                        "Time: %{customdata[2]}<br>"
                        "Pace: %{customdata[3]}"
                        "<extra></extra>"
                    ),
                )
            )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom,
                # No bounds constraint: allow zoom/pan all the way out worldwide.
            ),
        )

        st.plotly_chart(fig, width="stretch", config=_map_config())

        # ── Mileage summaries by location ─────────────────────────────
        rows = []
        for act in raw_activities:
            if not isinstance(act, dict):
                continue
            dist_m = float(act.get("distance") or 0)
            if dist_m <= 0:
                continue

            sport = act.get("sport_type") or act.get("type", "")
            friendly = _ACTIVITY_TYPE_MAP.get(sport, str(sport) if sport else "Other")

            city_raw = (act.get("location_city") or "").strip() if isinstance(act.get("location_city"), str) else ""
            state_raw = (act.get("location_state") or "").strip() if isinstance(act.get("location_state"), str) else ""
            country_raw = (act.get("location_country") or "").strip() if isinstance(act.get("location_country"), str) else ""

            # Build a composite location label: "City, State, Country"
            # When city is missing, show "Other areas in State, Country"
            if city_raw:
                parts = [p for p in [city_raw, state_raw, country_raw] if p]
                location = ", ".join(parts) if parts else "Unknown"
            elif state_raw:
                parts = [p for p in [state_raw, country_raw] if p]
                location = "Other areas in " + ", ".join(parts)
            elif country_raw:
                location = "Other areas in " + country_raw
            else:
                location = "Unknown Location"

            rows.append({
                "type": friendly,
                "miles": dist_m / 1609.344,
                "location": location,
                "state": state_raw or "Unknown",
                "country": country_raw or "Unknown",
            })

        if rows:
            df = pd.DataFrame(rows)

            def _summary_table(group_col: str) -> pd.DataFrame:
                pv = df.pivot_table(
                    index=group_col,
                    columns="type",
                    values="miles",
                    aggfunc="sum",
                    fill_value=0.0,
                )
                pv["Total"] = pv.sum(axis=1)
                pv = pv.sort_values("Total", ascending=False)
                # Keep it readable but still complete (scrollable)
                return pv.round(1)

            st.markdown("##### Miles by Location")
            st.dataframe(_summary_table("location"), width="stretch", height=240)

            st.markdown("##### Miles by State / Province")
            st.dataframe(_summary_table("state"), width="stretch", height=240)

            st.markdown("##### Miles by Country")
            st.dataframe(_summary_table("country"), width="stretch", height=240)


def render_timeline_buttons(key_prefix: str, current_value: str) -> str:
    """Render a row of timeline filter buttons. Returns selected value."""
    options = ["1W", "1M", "3M", "6M", "1Y", "2Y", "ALL"]
    # Inject CSS to prevent text wrapping inside buttons
    st.markdown("""
    <style>
        div[data-testid="stHorizontalBlock"] button {
            white-space: nowrap !important;
            padding-left: 4px !important;
            padding-right: 4px !important;
            min-width: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
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
