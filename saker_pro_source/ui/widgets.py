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
    raw_activities: list[dict] | None,
    using_demo: bool,
    *,
    key_prefix: str = "dash_fastest_map",
):
    """Dashboard section: Run routes (fastest vs all) with country filter."""
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                {get_icon('gps_fixed', 'blue', 18)}
                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;">Run Routes</span>
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

        if not raw_activities or not isinstance(raw_activities, list):
            st.caption("Connect Strava in **Settings** to view your run routes.")
            return

        # Countries with run route data
        run_sports = {"Run", "VirtualRun", "TrailRun"}
        run_acts = [
            a for a in raw_activities
            if isinstance(a, dict)
            and (a.get("sport_type") or a.get("type", "")) in run_sports
            and isinstance(a.get("map"), dict)
            and bool(a.get("map", {}).get("summary_polyline"))
        ]
        if not run_acts:
            st.caption("No run routes found (GPS routes require outdoor runs with a recorded map).")
            return

        def _country_label(v: object) -> str:
            s = v.strip() if isinstance(v, str) else ""
            return _COUNTRY_NAME.get(s.upper(), s) if s else ""

        countries = sorted({
            _country_label(a.get("location_country")) for a in run_acts
            if _country_label(a.get("location_country"))
        })
        if not countries:
            st.caption("Run routes found, but no country labels yet. Use Settings → Resolve Activity Locations.")
            return

        mode_key = f"{key_prefix}_mode"
        country_key = f"{key_prefix}_country"
        mode = st.selectbox("Mode", options=["Fastest", "All"], key=mode_key)
        country = st.selectbox("Country", options=countries, key=country_key)

        # Filter runs by selected country
        run_acts_country = [a for a in run_acts if _country_label(a.get("location_country")) == country]
        if not run_acts_country:
            st.caption("No run routes in that country.")
            return

        if mode == "Fastest":
            if not fastest_routes or not isinstance(fastest_routes, dict):
                st.caption("Sync Strava in **Settings** to compute fastest routes.")
                return

            # Only distances whose fastest activity is in this country
            available = [
                k for k, v in fastest_routes.items()
                if v is not None
                and v.get("summary_polyline")
                and _country_label(v.get("location_country")) == country
            ]
            if not available:
                st.caption("No fastest-run routes available for that country.")
                return

            sel_key = f"{key_prefix}_distance"
            default_idx = 0
            current = st.session_state.get(sel_key)
            if current in available:
                default_idx = available.index(current)

            dist = st.selectbox("Distance", options=available, index=default_idx, key=sel_key)

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

            lat_span = max_lat - min_lat
            lon_span = max_lon - min_lon
            pad = 1.5
            min_lat_p = min_lat - (lat_span * pad)
            max_lat_p = max_lat + (lat_span * pad)
            min_lon_p = min_lon - (lon_span * pad)
            max_lon_p = max_lon + (lon_span * pad)
            if lat_span <= 1e-6:
                min_lat_p, max_lat_p = min_lat - 0.002, max_lat + 0.002
            if lon_span <= 1e-6:
                min_lon_p, max_lon_p = min_lon - 0.002, max_lon + 0.002

            center_lat = (min_lat_p + max_lat_p) / 2
            center_lon = (min_lon_p + max_lon_p) / 2
            zoom = max(1, _auto_zoom(max_lat_p - min_lat_p, max_lon_p - min_lon_p) - 3)

            elapsed_s = int(run.get("elapsed_time_s") or 0)
            name = run.get("name") or "Run"
            date_str = str(run.get("start_date_local") or "")[:10]

            dist_m = float(run.get("distance_m") or 0)
            dist_mi = dist_m / 1609.344 if dist_m > 0 else 0.0
            dist_part = f"{dist_mi:.2f} mi" if dist_mi else "--"

            city = run.get("location_city") or ""
            if isinstance(city, str):
                city = city.strip()
            state = (run.get("location_state") or "").strip() if isinstance(run.get("location_state"), str) else ""
            if not city:
                city = state
            city = city or ""

            caption_title = name
            caption_meta = f"{dist} · {dist_part} · {date_str or '--'} · {city or country} · {_format_duration_hm(elapsed_s)}"

            fig = go.Figure()
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
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
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
                x=0.5,
                y=0.07,
                xanchor="center",
                yanchor="bottom",
                align="center",
                text=caption_title,
                showarrow=False,
                font=dict(size=26, color="#ffffff", family="Inter, sans-serif"),
                bgcolor="rgba(15,23,42,0.55)",
                borderwidth=0,
            )
            fig.add_annotation(
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.025,
                xanchor="center",
                yanchor="bottom",
                align="center",
                text=caption_meta,
                showarrow=False,
                font=dict(size=15, color="#e2e8f0", family="Inter, sans-serif"),
                bgcolor="rgba(15,23,42,0.55)",
                borderwidth=0,
            )
            st.plotly_chart(fig, width="stretch", config=_map_config())
            return

        # mode == "All": aggregate all run routes for this country
        all_pts: list[tuple[float, float]] = []
        total_dist_m = 0.0
        total_time_s = 0
        n_acts = 0
        decoded_routes: list[list[tuple[float, float]]] = []
        for a in run_acts_country:
            poly = a.get("map", {}).get("summary_polyline")
            pts = _decode_polyline(poly)
            if len(pts) < 2:
                continue
            decoded_routes.append(pts)
            all_pts.extend(pts)
            total_dist_m += float(a.get("distance") or 0)
            total_time_s += int(a.get("elapsed_time") or 0)
            n_acts += 1

        if len(all_pts) < 2:
            st.caption("No drawable run routes for that country.")
            return

        # Overlap counts by rounded coordinate (local repetition proxy)
        counts: dict[tuple[float, float], int] = {}
        for lat, lon in all_pts:
            key = (round(lat, 4), round(lon, 4))
            counts[key] = counts.get(key, 0) + 1

        min_lat, max_lat = min(p[0] for p in all_pts), max(p[0] for p in all_pts)
        min_lon, max_lon = min(p[1] for p in all_pts), max(p[1] for p in all_pts)
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        zoom = max(1, _auto_zoom(max_lat - min_lat, max_lon - min_lon) - 1)

        total_mi = total_dist_m / 1609.344 if total_dist_m > 0 else 0.0
        caption = f"Total Distance: {total_mi:,.1f}mi  Total Time: {_format_duration_hm(total_time_s)}  {n_acts} Activities"

        fig = go.Figure()
        # Draw ONLY route lines; darker where repeated.
        # Implementation: segment the polylines and bucket segments by repetition
        # count, then draw bucketed line segments as same-hue blue with higher alpha.
        bins = [
            (1, 1, 0.18),
            (2, 3, 0.28),
            (4, 7, 0.42),
            (8, 15, 0.62),
            (16, 10**9, 0.92),
        ]
        seg_lats: list[list[float | None]] = [[] for _ in bins]
        seg_lons: list[list[float | None]] = [[] for _ in bins]

        def _bin_idx(c: float) -> int:
            for idx, (lo, hi, _a) in enumerate(bins):
                if lo <= c <= hi:
                    return idx
            return len(bins) - 1

        for pts in decoded_routes:
            for i in range(len(pts) - 1):
                lat1, lon1 = pts[i]
                lat2, lon2 = pts[i + 1]
                c1 = counts.get((round(lat1, 4), round(lon1, 4)), 1)
                c2 = counts.get((round(lat2, 4), round(lon2, 4)), 1)
                c = (c1 + c2) / 2
                bi = _bin_idx(c)
                seg_lats[bi].extend([lat1, lat2, None])
                seg_lons[bi].extend([lon1, lon2, None])

        # Draw light → dark so darker repetitions sit on top.
        for (lo, hi, alpha), lats, lons in zip(bins, seg_lats, seg_lons):
            if len(lats) < 2:
                continue
            fig.add_trace(
                go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode="lines",
                    line=dict(color=f"rgba(37,140,244,{alpha})", width=3),
                    hoverinfo="skip",
                    name=f"{lo}-{hi}",
                    showlegend=False,
                )
            )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            uirevision=key_prefix,
            height=_wallart_height(max_lat - min_lat, max_lon - min_lon),
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=center_lat, lon=center_lon),
                zoom=zoom,
            ),
        )
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.03,
            xanchor="center",
            yanchor="bottom",
            align="center",
            text=caption,
            showarrow=False,
            font=dict(size=16, color="#e2e8f0", family="Inter, sans-serif"),
            bgcolor="rgba(15,23,42,0.55)",
            borderwidth=0,
        )
        st.plotly_chart(fig, width="stretch", config=_map_config())
        return


_ACTIVITY_TYPE_MAP = {
    "Run": "Running",
    "VirtualRun": "Running",
    "TrailRun": "Running",
    "Ride": "Cycling",
    "VirtualRide": "Cycling",
    "GravelRide": "Cycling",
    "MountainBikeRide": "Cycling",
    "Walk": "Walking",
    "NordicWalk": "Walking",
    "TrailWalk": "Walking",
    "Hike": "Walking",
    "Swim": "Swimming",
    "OpenWaterSwim": "Swimming",
    "WeightTraining": "Weights",
    "Crossfit": "Weights",
    "Workout": "Weights",
}


_COUNTRY_NAME = {
    "US": "United States",
    "USA": "United States",
    "GB": "United Kingdom",
    "UK": "United Kingdom",
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
        kept_activities: list[dict] = []
        for act in raw_activities:
            if not isinstance(act, dict):
                continue
            start = act.get("start_latlng")
            if not (isinstance(start, (list, tuple)) and len(start) == 2):
                continue
            lat, lon = start
            if lat is None or lon is None:
                continue

            # Require state+country; Strava often omits city. If city is missing,
            # fall back to state for display/aggregation so miles aren't dropped.
            city = act.get("location_city")
            state = act.get("location_state")
            country = act.get("location_country")
            city_s = city.strip() if isinstance(city, str) else ""
            state_s = state.strip() if isinstance(state, str) else ""
            country_s = country.strip() if isinstance(country, str) else ""
            if country_s:
                country_s = _COUNTRY_NAME.get(country_s.upper(), country_s)
            if not state_s or not country_s:
                continue

            if not city_s:
                city_s = state_s

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

            kept_activities.append(act)
            points.append({
                "lat": float(lat),
                "lon": float(lon),
                "type": friendly,
                "date": date_str,
                "distance_mi": dist_mi,
                "time": time_str,
                "pace": pace_str,
                "name": act.get("name", ""),
                "city": city_s,
                "state": state_s,
                "country": country_s,
            })

        if not points:
            st.caption("No activities with complete location labels (city/state/country) were found.")
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
        for p in points:
            if not p.get("distance_mi"):
                continue
            city = str(p.get("city") or "").strip()
            state = str(p.get("state") or "").strip()
            country = str(p.get("country") or "").strip()
            if city and state and city.lower() == state.lower():
                place = f"{state}, {country}" if country else state
            else:
                place = ", ".join([x for x in [city, state, country] if x])
            rows.append({
                "type": p["type"],
                "miles": float(p["distance_mi"]),
                "place": place,
            })

        if rows:
            df = pd.DataFrame(rows)
            agg = (
                df.groupby(["type", "place"], as_index=False)["miles"]
                .sum()
                .sort_values(["type", "miles"], ascending=[True, False])
            )

            verb = {
                "Running": "Ran",
                "Cycling": "Biked",
                "Swimming": "Swam",
                "Walking": "Walked",
                "Hiking": "Hiked",
                "Weights": "Trained",
            }

            type_order = ["Running", "Cycling", "Swimming", "Walking", "Hiking", "Weights", "Other"]
            seen_types = [t for t in type_order if t in set(agg["type"].tolist())] + [
                t for t in agg["type"].unique().tolist() if t not in type_order
            ]

            def _fmt_miles(x: float) -> str:
                x1 = round(float(x), 1)
                return str(int(x1)) if abs(x1 - int(x1)) < 1e-9 else f"{x1:.1f}"

            st.markdown("##### Miles by Location")
            for t in seen_types:
                sub = agg[agg["type"] == t]
                if sub.empty:
                    continue
                st.markdown(f"**{t}**")
                lines = []
                v = verb.get(t, "Did")
                for _, r in sub.iterrows():
                    lines.append(f"- {_fmt_miles(r['miles'])} Miles {v} in {r['place']}.")
                st.markdown("\n".join(lines))


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
            if st.button(opt, key=f"{key_prefix}_tl_{opt}", type=btn_type, width="stretch"):
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
