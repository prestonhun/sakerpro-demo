# strava.py
"""
Strava API integration for Saker Pro.
Handles OAuth2 authentication, token management, and activity fetching.
All tokens stored locally in YAML — no cloud dependencies.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE = "https://www.strava.com/api/v3"
REQUIRED_SCOPES = "read,activity:read_all"

_TOKEN_FILE = Path.home() / ".saker_pro" / "strava_tokens.yaml"
_LOCATION_CACHE_FILE = Path.home() / ".saker_pro" / "strava_activity_locations.yaml"
_GEOCODE_CACHE_FILE = Path.home() / ".saker_pro" / "geocode_cache.yaml"


# ---------------------------------------------------------------------------
# Token persistence (local YAML — no cloud)
# ---------------------------------------------------------------------------

def _ensure_dir() -> None:
    _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_location_cache() -> dict:
    if not _LOCATION_CACHE_FILE.exists():
        return {}
    try:
        data = yaml.safe_load(_LOCATION_CACHE_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_location_cache(cache: dict) -> None:
    _ensure_dir()
    try:
        _LOCATION_CACHE_FILE.write_text(yaml.dump(cache, default_flow_style=False))
    except Exception:
        pass


def _load_geocode_cache() -> dict:
    if not _GEOCODE_CACHE_FILE.exists():
        return {}
    try:
        data = yaml.safe_load(_GEOCODE_CACHE_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_geocode_cache(cache: dict) -> None:
    _ensure_dir()
    try:
        _GEOCODE_CACHE_FILE.write_text(yaml.dump(cache, default_flow_style=False))
    except Exception:
        pass


def _reverse_geocode_nominatim(lat: float, lon: float) -> dict:
    """Reverse geocode via OSM Nominatim (no extra Python deps).

    Returns a dict with best-effort `city`, `state`, `country` (name).
    Caller is responsible for rate limiting.
    """
    resp = requests.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={
            "format": "jsonv2",
            "lat": f"{lat:.7f}",
            "lon": f"{lon:.7f}",
            # zoom=14 is typically city/town level; 10 often returns only state.
            "zoom": 14,
            "addressdetails": 1,
        },
        headers={"User-Agent": "sakerpro-demo/1.0 (Streamlit; location enrichment)"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json() if resp.content else {}
    address = data.get("address") if isinstance(data, dict) else {}
    if not isinstance(address, dict):
        address = {}

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("hamlet")
        or address.get("municipality")
        or address.get("suburb")
        or address.get("neighbourhood")
        or address.get("locality")
    )
    state = (
        address.get("state")
        or address.get("state_district")
        or address.get("region")
        or address.get("county")
        or address.get("district")
    )
    country = address.get("country")
    if not country:
        cc = address.get("country_code")
        country = cc.upper() if isinstance(cc, str) and cc else ""
    return {
        "city": city or "",
        "state": state or "",
        "country": country or "",
    }


def save_tokens(tokens: dict) -> None:
    """Persist Strava OAuth tokens to local YAML file."""
    _ensure_dir()
    athlete = tokens.get("athlete", {}) if isinstance(tokens.get("athlete"), dict) else {}
    payload = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": int(tokens["expires_at"]),
        "athlete_id": athlete.get("id") or tokens.get("athlete_id"),
        "athlete_firstname": athlete.get("firstname") or tokens.get("athlete_firstname", ""),
        "athlete_lastname": athlete.get("lastname") or tokens.get("athlete_lastname", ""),
    }
    _TOKEN_FILE.write_text(yaml.dump(payload, default_flow_style=False))


def load_tokens() -> dict | None:
    """Load saved tokens, or return None if not connected."""
    if not _TOKEN_FILE.exists():
        return None
    try:
        data = yaml.safe_load(_TOKEN_FILE.read_text())
        if data and "access_token" in data:
            return data
    except Exception:
        pass
    return None


def clear_tokens() -> None:
    """Remove stored tokens (disconnect)."""
    if _TOKEN_FILE.exists():
        _TOKEN_FILE.unlink()


def is_connected() -> bool:
    """Check if valid Strava tokens exist."""
    return load_tokens() is not None


# ---------------------------------------------------------------------------
# OAuth2 helpers
# ---------------------------------------------------------------------------

def get_authorization_url(client_id: str, redirect_uri: str) -> str:
    """Build Strava OAuth authorization URL."""
    return (
        f"{STRAVA_AUTH_URL}"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope={REQUIRED_SCOPES}"
        f"&approval_prompt=auto"
    )


def exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    """Exchange authorization code for access + refresh tokens."""
    resp = requests.post(
        STRAVA_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    resp.raise_for_status()
    tokens = resp.json()
    save_tokens(tokens)
    return tokens


def refresh_access_token(client_id: str, client_secret: str) -> dict:
    """Refresh the access token if expired. Returns updated tokens."""
    stored = load_tokens()
    if stored is None:
        raise RuntimeError("No Strava tokens stored — connect first.")

    # Still valid? (with 60s buffer)
    if stored.get("expires_at", 0) > time.time() + 60:
        return stored

    resp = requests.post(
        STRAVA_TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": stored["refresh_token"],
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    resp.raise_for_status()
    tokens = resp.json()
    tokens["athlete_id"] = stored.get("athlete_id")
    save_tokens(tokens)
    return tokens


def _get_valid_token(client_id: str, client_secret: str) -> str:
    """Return a valid access token, refreshing if needed."""
    tokens = refresh_access_token(client_id, client_secret)
    return tokens["access_token"]


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------

def get_athlete(client_id: str, client_secret: str) -> dict:
    """Fetch authenticated athlete profile."""
    token = _get_valid_token(client_id, client_secret)
    resp = requests.get(
        f"{STRAVA_API_BASE}/athlete",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_activities(
    client_id: str,
    client_secret: str,
    days: int = 3650,
    per_page: int = 200,
) -> list[dict]:
    """
    Fetch activities from the Strava API.

    Parameters
    ----------
    days : int
        How many days of history to pull (default ~10 years = all data).
    per_page : int
        Strava page size (max 200).

    Returns
    -------
    list[dict]
        Raw activity dicts from the Strava API.
    """
    token = _get_valid_token(client_id, client_secret)
    after = int((datetime.now(tz=timezone.utc) - timedelta(days=days)).timestamp())
    activities: list[dict] = []
    page = 1

    while True:
        resp = requests.get(
            f"{STRAVA_API_BASE}/athlete/activities",
            headers={"Authorization": f"Bearer {token}"},
            params={"after": after, "per_page": per_page, "page": page},
            timeout=15,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        activities.extend(batch)
        if len(batch) < per_page:
            break
        page += 1

    return activities


def fetch_activity_detail(client_id: str, client_secret: str, activity_id: int) -> dict:
    """Fetch a single activity detail from Strava."""
    token = _get_valid_token(client_id, client_secret)
    resp = requests.get(
        f"{STRAVA_API_BASE}/activities/{activity_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()

    # If Strava includes rate limit headers, stop aggressive follow-up calls.
    # Format: "X-RateLimit-Limit: 100,1000" and "X-RateLimit-Usage: 12,123"
    try:
        limit = resp.headers.get("X-RateLimit-Limit")
        usage = resp.headers.get("X-RateLimit-Usage")
        if limit and usage:
            lim_parts = [int(x.strip()) for x in limit.split(",") if x.strip().isdigit()]
            use_parts = [int(x.strip()) for x in usage.split(",") if x.strip().isdigit()]
            if lim_parts and use_parts and len(lim_parts) == len(use_parts):
                remaining = [l - u for l, u in zip(lim_parts, use_parts)]
                # If we're within 2 calls of *either* window, bail.
                if any(r <= 2 for r in remaining):
                    raise RuntimeError("Strava rate limit nearly exhausted")
    except RuntimeError:
        raise
    except Exception:
        pass

    return resp.json()


def enrich_activity_locations(
    activities: list[dict],
    client_id: str,
    client_secret: str,
    *,
    max_detail_lookups: int = 75,
    allow_external_geocode: bool = True,
    max_geocode_lookups: int = 35,
    detail_sleep_s: float = 0.25,
) -> list[dict]:
    """Enrich activities with `location_city/state/country` using Strava-only data.

    Streamlit Community Cloud friendly:
    - avoids SciPy/GEOS heavy dependencies
    - avoids third-party geocoding services

    Uses the activity detail endpoint as a fallback and caches results locally.
    """
    if not activities:
        return []

    def _norm_str(v: Any) -> str:
        return v.strip() if isinstance(v, str) else ""

    cache = _load_location_cache()
    geo_cache = _load_geocode_cache()
    cache_changed = False
    lookups_used = 0
    geocode_changed = False

    # We'll pick a capped set of unique lat/lon keys spread across the
    # *entire* activity history (not just the first N) to avoid missing
    # older/remote locations.
    pending_geo: list[tuple[int, str]] = []

    def _geo_key(lat: float, lon: float, *, precision: int = 3) -> str:
        # 3 decimals ≈ 110m; collapses nearby start points into one key.
        fmt = f"{{:.{precision}f}},{{:.{precision}f}}"
        return fmt.format(lat, lon)

    def _lookup_geo_cache(lat: float, lon: float) -> tuple[str, dict | None]:
        """Return (key, place) trying both new (3dp) and legacy (4dp) keys."""
        if not isinstance(geo_cache, dict):
            return "", None
        k3 = _geo_key(lat, lon, precision=3)
        v3 = geo_cache.get(k3)
        if isinstance(v3, dict):
            return k3, v3
        k4 = _geo_key(lat, lon, precision=4)
        v4 = geo_cache.get(k4)
        if isinstance(v4, dict):
            return k4, v4
        return k3, None

    enriched: list[dict] = []
    for act in activities:
        if not isinstance(act, dict):
            continue

        out = dict(act)
        act_id = out.get("id")
        act_key = str(act_id) if act_id is not None else None

        city = _norm_str(out.get("location_city"))
        state = _norm_str(out.get("location_state"))
        country = _norm_str(out.get("location_country"))

        missing_any = (not city) or (not state) or (not country)

        # Cache first
        if missing_any and act_key and isinstance(cache.get(act_key), dict):
            c = cache[act_key]
            if not city and _norm_str(c.get("location_city")):
                out["location_city"] = c.get("location_city")
            if not state and _norm_str(c.get("location_state")):
                out["location_state"] = c.get("location_state")
            if not country and _norm_str(c.get("location_country")):
                out["location_country"] = c.get("location_country")
            city = _norm_str(out.get("location_city"))
            state = _norm_str(out.get("location_state"))
            country = _norm_str(out.get("location_country"))
            missing_any = (not city) or (not state) or (not country)

        # Detail endpoint fallback
        if missing_any and act_id is not None and lookups_used < max_detail_lookups:
            try:
                # Avoid bursting Strava detail calls.
                if lookups_used > 0 and detail_sleep_s > 0:
                    time.sleep(detail_sleep_s)
                detail = fetch_activity_detail(client_id, client_secret, int(act_id))
                d_city = _norm_str(detail.get("location_city"))
                d_state = _norm_str(detail.get("location_state"))
                d_country = _norm_str(detail.get("location_country"))

                if d_city and not city:
                    out["location_city"] = d_city
                if d_state and not state:
                    out["location_state"] = d_state
                if d_country and not country:
                    out["location_country"] = d_country

                if act_key:
                    cache[act_key] = {
                        "location_city": out.get("location_city"),
                        "location_state": out.get("location_state"),
                        "location_country": out.get("location_country"),
                    }
                    cache_changed = True

                lookups_used += 1
            except RuntimeError:
                # Likely rate-limit protection from fetch_activity_detail(); stop further Strava detail lookups.
                lookups_used = max_detail_lookups
            except Exception:
                pass

        # Track any remaining missing locations for a later, capped geocode pass.
        city = _norm_str(out.get("location_city"))
        state = _norm_str(out.get("location_state"))
        country = _norm_str(out.get("location_country"))
        missing_any = (not city) or (not state) or (not country)

        start = out.get("start_latlng")
        has_latlng = isinstance(start, (list, tuple)) and len(start) == 2 and all(v is not None for v in start)
        if allow_external_geocode and missing_any and has_latlng:
            try:
                lat, lon = float(start[0]), float(start[1])
                key, place = _lookup_geo_cache(lat, lon)
                out["_geo_key"] = key
                # Apply cached geocode immediately (covers many activities once key precision is coarse)
                if isinstance(place, dict):
                    if not city and _norm_str(place.get("city")):
                        out["location_city"] = place.get("city")
                    if not state and _norm_str(place.get("state")):
                        out["location_state"] = place.get("state")
                    if not country and _norm_str(place.get("country")):
                        out["location_country"] = place.get("country")

                # If we're still missing anything (or cache is incomplete), schedule for re-geocode.
                city2 = _norm_str(out.get("location_city"))
                state2 = _norm_str(out.get("location_state"))
                country2 = _norm_str(out.get("location_country"))
                if (not city2) or (not state2) or (not country2):
                    pending_geo.append((len(enriched), key))
            except Exception:
                pass

        enriched.append(out)

    # Geocode pass (cached + rate-limited)
    if allow_external_geocode and pending_geo and isinstance(geo_cache, dict):
        def _incomplete_place(v: Any) -> bool:
            if not isinstance(v, dict):
                return True
            return (not _norm_str(v.get("city"))) or (not _norm_str(v.get("state"))) or (not _norm_str(v.get("country")))

        # Determine which unique keys still need lookups
        key_counts: dict[str, int] = {}
        for _, k in pending_geo:
            key_counts[k] = key_counts.get(k, 0) + 1

        # Include keys that are missing from cache OR have incomplete cached data
        unique_keys: list[str] = [k for k in key_counts.keys() if (k not in geo_cache) or _incomplete_place(geo_cache.get(k))]

        # Select keys to maximize coverage:
        # - geographic outliers (min/max lat/lon)
        # - most common keys (resolve majority area first)
        # - plus spread across history (front/back alternation)
        selected: list[str] = []
        selected_set: set[str] = set()

        def _add(k: str) -> None:
            if k and k not in selected_set and len(selected) < max_geocode_lookups:
                selected.append(k)
                selected_set.add(k)

        parsed: list[tuple[str, float, float]] = []
        for k in unique_keys:
            try:
                lat_s, lon_s = k.split(",", 1)
                parsed.append((k, float(lat_s), float(lon_s)))
            except Exception:
                continue

        if parsed:
            min_lat_k = min(parsed, key=lambda x: x[1])[0]
            max_lat_k = max(parsed, key=lambda x: x[1])[0]
            min_lon_k = min(parsed, key=lambda x: x[2])[0]
            max_lon_k = max(parsed, key=lambda x: x[2])[0]
            for k in (min_lat_k, max_lat_k, min_lon_k, max_lon_k):
                _add(k)

        # Resolve the densest cluster first (typically "home" location)
        for k, _cnt in sorted(key_counts.items(), key=lambda kv: kv[1], reverse=True):
            if k in geo_cache and not _incomplete_place(geo_cache.get(k)):
                continue
            _add(k)
            if len(selected) >= max_geocode_lookups:
                break

        i, j = 0, len(unique_keys) - 1
        while i <= j and len(selected) < max_geocode_lookups:
            _add(unique_keys[i])
            i += 1
            if i <= j and len(selected) < max_geocode_lookups:
                _add(unique_keys[j])
                j -= 1

        for k in selected:
            try:
                lat_s, lon_s = k.split(",", 1)
                lat, lon = float(lat_s), float(lon_s)
                time.sleep(1.05)
                # Store under the key we requested (3dp), not the raw lat/lon.
                geo_cache[k] = _reverse_geocode_nominatim(lat, lon)
                geocode_changed = True
            except Exception:
                continue

        # Apply cache back onto enriched activities
        for out in enriched:
            k = out.get("_geo_key")
            if not k or not isinstance(k, str):
                continue
            place = geo_cache.get(k)
            if not isinstance(place, dict):
                continue

            city = _norm_str(out.get("location_city"))
            state = _norm_str(out.get("location_state"))
            country = _norm_str(out.get("location_country"))

            if not city and _norm_str(place.get("city")):
                out["location_city"] = place.get("city")
            if not state and _norm_str(place.get("state")):
                out["location_state"] = place.get("state")
            if not country and _norm_str(place.get("country")):
                out["location_country"] = place.get("country")

            # Ensure state is present for places that don't have an admin1 in OSM.
            if not _norm_str(out.get("location_state")) and _norm_str(out.get("location_country")):
                out["location_state"] = out.get("location_country")

        # Strip internal key
        for out in enriched:
            out.pop("_geo_key", None)

    if cache_changed:
        _save_location_cache(cache)

    if geocode_changed and isinstance(geo_cache, dict):
        _save_geocode_cache(geo_cache)

    return enriched


# ---------------------------------------------------------------------------
# Normalisation → DataFrames expected by the dashboard
# ---------------------------------------------------------------------------

_CARDIO_TYPES = {"Run", "Ride", "Walk", "Hike", "Swim", "VirtualRide", "VirtualRun"}
_STRENGTH_TYPES = {"WeightTraining", "Crossfit", "Workout"}

# Strava sport_type → friendly name
_TYPE_MAP = {
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


def _parse_date_naive(date_str: str) -> pd.Timestamp:
    """Parse a date string to a tz-naive normalised Timestamp.

    Strava's ``start_date_local`` contains the athlete's wall-clock time
    but may carry a misleading 'Z' suffix or a real offset.  We must keep
    the wall-clock digits intact (i.e. NOT convert to UTC) and just strip
    any timezone marker.
    """
    ts = pd.to_datetime(date_str)
    if ts.tzinfo is not None:
        # replace(tzinfo=None) keeps wall-clock time; tz_localize(None)
        # would shift to UTC, potentially changing the date.
        ts = ts.replace(tzinfo=None)
    return ts.normalize()


def activities_to_cardio_df(activities: list[dict]) -> pd.DataFrame:
    """
    Convert Strava activities into a cardio/activities DataFrame
    matching the schema used by the dashboard.

    Columns: date, activity_type, duration_min, distance_miles, avg_hr
    """
    rows: list[dict[str, Any]] = []
    for act in activities:
        sport = act.get("sport_type") or act.get("type", "")
        # Skip strength activities — those go in workouts_df
        if sport in _STRENGTH_TYPES:
            continue
        friendly = _TYPE_MAP.get(sport, sport)

        rows.append({
            "date": _parse_date_naive(act["start_date_local"]),
            "activity_type": friendly,
            "duration_min": round(act.get("elapsed_time", 0) / 60, 1),
            "distance_miles": round(act.get("distance", 0) / 1609.344, 2),
            "avg_hr": act.get("average_heartrate"),
            "strava_id": act.get("id"),
            "name": act.get("name", ""),
        })

    if not rows:
        return pd.DataFrame(
            columns=["date", "activity_type", "duration_min",
                     "distance_miles", "avg_hr", "strava_id", "name"]
        )
    return pd.DataFrame(rows)


# Maps common workout split names → representative exercises for muscle balance
_SPLIT_EXERCISES: dict[str, list[tuple[str, float]]] = {
    # (exercise_title, relative_weight)  — weights sum to 1.0 per split
    "push": [
        ("Bench Press", 0.35), ("Overhead Press", 0.25),
        ("Incline Dumbbell Press", 0.2), ("Tricep Pushdown", 0.2),
    ],
    "pull": [
        ("Barbell Row", 0.3), ("Pull Up", 0.25),
        ("Face Pull", 0.15), ("Barbell Curl", 0.3),
    ],
    "legs": [
        ("Squat", 0.35), ("Romanian Deadlift", 0.30),
        ("Leg Press", 0.15), ("Calf Raise", 0.20),
    ],
    "leg": [
        ("Squat", 0.35), ("Romanian Deadlift", 0.30),
        ("Leg Press", 0.15), ("Calf Raise", 0.20),
    ],
    "upper": [
        ("Bench Press", 0.25), ("Barbell Row", 0.25),
        ("Overhead Press", 0.2), ("Bicep Curl", 0.15),
        ("Tricep Pushdown", 0.15),
    ],
    "lower": [
        ("Squat", 0.35), ("Romanian Deadlift", 0.30),
        ("Leg Curl", 0.15), ("Calf Raise", 0.20),
    ],
    "chest": [
        ("Bench Press", 0.4), ("Incline Dumbbell Press", 0.3),
        ("Cable Fly", 0.3),
    ],
    "back": [
        ("Barbell Row", 0.35), ("Pull Up", 0.35),
        ("Lat Pulldown", 0.3),
    ],
    "shoulder": [
        ("Overhead Press", 0.5), ("Lateral Raise", 0.5),
    ],
    "arm": [
        ("Bicep Curl", 0.5), ("Tricep Pushdown", 0.5),
    ],
    "full body": [
        ("Squat", 0.2), ("Bench Press", 0.2), ("Barbell Row", 0.2),
        ("Overhead Press", 0.15), ("Romanian Deadlift", 0.15),
        ("Bicep Curl", 0.1),
    ],
}


def _infer_exercises(name: str, description: str | None = None) -> list[str]:
    """Infer exercise names from a Strava activity name or description."""
    # First, try to extract real exercise names from description
    if description:
        # Common patterns from Hevy/Strong syncs: exercise name on its own line
        import re
        _EXERCISE_KEYWORDS = [
            "squat", "bench", "deadlift", "press", "row", "curl",
            "fly", "pull.?up", "lat pulldown", "leg press", "leg curl",
            "leg extension", "calf raise", "lunge", "rdl", "romanian",
            "pushdown", "tricep", "bicep", "face pull", "lateral raise",
            "shrug", "dip", "push.?up", "chin.?up", "cable",
            "incline", "decline", "overhead",
        ]
        pattern = "|".join(_EXERCISE_KEYWORDS)
        lines = description.split("\n")
        found: list[str] = []
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and re.search(pattern, line_stripped, re.IGNORECASE):
                # Take up to the first number or 'x' pattern (set notation)
                clean = re.split(r"\d+\s*[x×]|\d+\s*sets?", line_stripped, maxsplit=1)[0].strip()
                if clean and len(clean) > 2:
                    found.append(clean)
        if found:
            return found

    # Fall back to split-name inference
    name_l = name.lower().strip()
    for split_key, exercises in _SPLIT_EXERCISES.items():
        if split_key in name_l:
            return [ex for ex, _ in exercises]

    return [name]  # fallback: use activity name as-is


def activities_to_workouts_df(activities: list[dict]) -> pd.DataFrame:
    """
    Convert Strava WeightTraining / Crossfit / Workout activities into a
    workout DataFrame compatible with the existing dashboard.

    Parses activity names (and descriptions when available) to infer
    individual exercises. This enables muscle-balance analysis even when
    only Strava summary data is available.

    Columns mirror the Hevy-style schema:
        date, title, exercise_title, set_index, weight_lbs, weight_kg,
        reps, rpe, duration_seconds, distance_miles, tonnage_lbs
    """
    rows: list[dict[str, Any]] = []
    for act in activities:
        sport = act.get("sport_type") or act.get("type", "")
        if sport not in _STRENGTH_TYPES:
            continue

        duration_s = act.get("elapsed_time", 0)
        duration_min = duration_s / 60
        name = act.get("name", "Weight Training")
        description = act.get("description")

        # Estimate tonnage from duration:
        # Typical density ≈ 1 set/2.5 min, ~10 reps @ ~100 lbs avg
        est_sets = max(1, int(duration_min / 2.5))
        est_reps = 10
        est_weight = 100.0  # lbs, conservative average
        total_tonnage = est_sets * est_reps * est_weight

        # Infer exercises from name/description
        exercises = _infer_exercises(name, description)
        n_exercises = len(exercises)
        per_exercise_tonnage = total_tonnage / n_exercises
        per_exercise_sets = max(1, est_sets // n_exercises)
        per_exercise_reps = est_reps
        per_exercise_dur = duration_s / n_exercises

        for i, ex_title in enumerate(exercises):
            rows.append({
                "date": _parse_date_naive(act["start_date_local"]),
                "title": name,
                "exercise_title": ex_title,
                "set_index": i + 1,
                "weight_lbs": est_weight,
                "weight_kg": est_weight / 2.20462,
                "reps": per_exercise_sets * per_exercise_reps,
                "rpe": None,
                "duration_seconds": per_exercise_dur,
                "distance_miles": 0.0,
                "tonnage_lbs": per_exercise_tonnage,
                "strava_id": act.get("id"),
            })

    if not rows:
        return pd.DataFrame(
            columns=["date", "title", "exercise_title", "set_index",
                     "weight_lbs", "weight_kg", "reps", "rpe",
                     "duration_seconds", "distance_miles", "tonnage_lbs",
                     "strava_id"]
        )
    return pd.DataFrame(rows)


def get_best_run_efforts(activities: list[dict]) -> dict:
    """
    Scan Strava activities for the best (fastest) run at common distances.

    Returns a dict like:
        {"5K": 24.5, "10K": 52.3, "Half Marathon": 115.0, ...}
    where values are time in minutes, or None if no run at that distance.
    """
    # Distance buckets with ±15% tolerance
    buckets = {
        "5K": (5000 * 0.85, 5000 * 1.15),
        "10K": (10000 * 0.85, 10000 * 1.15),
        "Half Marathon": (21097 * 0.85, 21097 * 1.15),
        "Marathon": (42195 * 0.85, 42195 * 1.15),
    }
    best: dict[str, float | None] = {k: None for k in buckets}

    for act in activities:
        sport = act.get("sport_type") or act.get("type", "")
        if sport not in ("Run", "VirtualRun", "TrailRun"):
            continue
        dist_m = act.get("distance", 0)
        time_min = act.get("elapsed_time", 0) / 60
        if dist_m <= 0 or time_min <= 0:
            continue

        for label, (lo, hi) in buckets.items():
            if lo <= dist_m <= hi:
                if best[label] is None or time_min < best[label]:
                    best[label] = round(time_min, 1)

    return best


def _decode_polyline(polyline_str: str) -> list[tuple[float, float]]:
    """Decode a Strava/Google encoded polyline to (lat, lon) tuples.

    Implementation based on the public Google Encoded Polyline Algorithm.
    We keep this dependency-free to avoid pulling in heavyweight GIS libs.
    """
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


def get_fastest_run_routes(activities: list[dict]) -> dict[str, dict | None]:
    """Return fastest run per distance bucket including a drawable route.

    Uses Strava's activity list summary fields only (no extra API calls),
    and relies on ``map.summary_polyline`` for the route.

    Returns
    -------
    dict
        {
          "5K": {"time_min": 24.5, "summary_polyline": "...", ...} | None,
          "10K": {...} | None,
          ...
        }
    """
    buckets = {
        "5K": (5000 * 0.85, 5000 * 1.15),
        "10K": (10000 * 0.85, 10000 * 1.15),
        "Half Marathon": (21097 * 0.85, 21097 * 1.15),
        "Marathon": (42195 * 0.85, 42195 * 1.15),
    }

    best: dict[str, dict | None] = {k: None for k in buckets}

    for act in activities:
        sport = act.get("sport_type") or act.get("type", "")
        if sport not in ("Run", "VirtualRun", "TrailRun"):
            continue

        dist_m = act.get("distance", 0) or 0
        elapsed_s = act.get("elapsed_time", 0) or 0
        if dist_m <= 0 or elapsed_s <= 0:
            continue

        map_obj = act.get("map") if isinstance(act.get("map"), dict) else {}
        summary_polyline = map_obj.get("summary_polyline") if isinstance(map_obj, dict) else None
        if not summary_polyline:
            # Treadmill/indoor runs often have no GPS route; skip for map feature.
            continue

        time_min = elapsed_s / 60

        for label, (lo, hi) in buckets.items():
            if not (lo <= dist_m <= hi):
                continue

            prev = best[label]
            if prev is None or time_min < float(prev.get("time_min", 1e18)):
                # Validate we can decode at least a few points before accepting.
                pts = _decode_polyline(summary_polyline)
                if len(pts) < 2:
                    continue
                best[label] = {
                    "strava_id": act.get("id"),
                    "name": act.get("name", ""),
                    "start_date_local": act.get("start_date_local"),
                    "distance_m": float(dist_m),
                    "elapsed_time_s": int(elapsed_s),
                    "time_min": round(time_min, 1),
                    "summary_polyline": summary_polyline,
                    "start_latlng": act.get("start_latlng"),
                    "end_latlng": act.get("end_latlng"),
                    "location_city": act.get("location_city"),
                    "location_state": act.get("location_state"),
                    "location_country": act.get("location_country"),
                }

    return best
