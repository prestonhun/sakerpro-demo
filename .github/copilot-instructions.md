# Saker PRO - Copilot Instructions

> **Philosophy**: Local-First, Privacy-Hardened desktop app for hybrid athletes.
> **Stack**: Python 3.11/3.12 (NOT 3.14), Streamlit, Pandas, llama.cpp, PyInstaller

## Architecture Overview

Main application code lives in `/saker_pro_source/`.

| Module | Path | Purpose |
|--------|------|---------|
| `main.py` | `saker_pro_source/main.py` | **Entry Point** - Streamlit UI, dashboard, settings |
| `paths.py` | `saker_pro_source/utils/paths.py` | PyInstaller-compatible path resolution |
| `planner.py` | `saker_pro_source/logic/planner.py` | Training plan generation (pure Python math) |
| `plan_assembler.py` | `saker_pro_source/logic/plan_assembler.py` | Logic-first plan assembly with variable injection |
| `coach.py` | `saker_pro_source/logic/coach.py` | LLM interface - llama.cpp calls, RAG context |
| `analytics.py` | `saker_pro_source/logic/analytics.py` | ACWR calculations, pace estimation, readiness scores |
| `evaluation.py` | `saker_pro_source/logic/evaluation.py` | Goal progress evaluation |
| `powerlifting.py` | `saker_pro_source/logic/powerlifting.py` | DOTS calculations, lift balance analysis |
| `calendar_export.py` | `saker_pro_source/logic/calendar_export.py` | ICS calendar export |
| `hyrox_data.py` | `saker_pro_source/logic/hyrox_data.py` | Hyrox reference splits and benchmarks |
| `data_loader.py` | `saker_pro_source/data/data_loader.py` | CSV/Excel parsers (MacroFactor, Hevy) |
| `apple_health.py` | `saker_pro_source/data/apple_health.py` | Apple Health export.zip parser |
| `profile.py` | `saker_pro_source/data/profile.py` | User profile YAML management |
| `theme.py` | `saker_pro_source/ui/theme.py` | CSS styles (glassmorphism, Saker Blue accent) |
| `icons.py` | `saker_pro_source/ui/icons.py` | SVG icon generation with gradients |
| `volume.py` | `saker_pro_source/canon/volume.py` | Progressive overload calculations (10% rule) |
| `library.json` | `saker_pro_source/canon/library.json` | Smart workout template database |
| `index_canon.py` | `saker_pro_source/rag/index_canon.py` | Vector DB indexing |
| `query_canon.py` | `saker_pro_source/rag/query_canon.py` | Vector DB queries |

### Directory Structure
```
saker_pro_source/
├── __init__.py          # Package initialization with version
├── main.py              # **ENTRY POINT** - Streamlit app
├── utils/               # Utility functions
│   ├── __init__.py
│   └── paths.py         # PyInstaller-compatible path helpers
├── data/                # Data loading & integrations
│   ├── __init__.py
│   ├── apple_health.py
│   ├── data_loader.py
│   └── profile.py
├── logic/               # Core business logic
│   ├── __init__.py
│   ├── analytics.py
│   ├── analyzer.py      # Sports science analytics (Phase 0)
│   ├── calendar_export.py
│   ├── coach.py
│   ├── evaluation.py
│   ├── hyrox_data.py
│   ├── plan_assembler.py
│   ├── planner.py
│   ├── powerlifting.py
│   ├── schema.py        # Pydantic data models
│   └── load_models/     # Training load calculations
├── core/                # UI state & generation pipeline
│   ├── state.py         # Streamlit session state management
│   ├── generation.py    # Plan generation pipeline
│   ├── plan_quality.py  # Quality scoring & strength allocation
│   └── split_manager.py # Strength split rotation
├── ui/                  # UI components & styling
│   ├── __init__.py
│   ├── icons.py
│   └── theme.py
├── canon/               # Workout library & volume math
│   ├── __init__.py
│   ├── library.json
│   └── volume.py
└── rag/                 # Knowledge base indexing
    ├── __init__.py
    ├── index_canon.py
    └── query_canon.py
```

### Data Flow
1. **Sources**: Garmin Connect, MacroFactor `.xlsx`, Hevy `.csv`, Apple Health `.zip` → `uploads/`
2. **Config**: `user_profile.yaml` (goals, injuries, preferences)
3. **Knowledge**: `knowledge/canon_textbook/`, `knowledge/doctrine/`, `knowledge/research/` → `data/chroma_db/`
4. **LLM**: Local llama.cpp server on `localhost:8080` (model: `Phi-4-mini-instruct-Q4_K_M.gguf`)

## ⚠️ The "Physio-Gate" Rule (CRITICAL)

Before generating ANY workout content, **ALWAYS** check `user_profile.yaml` for `active_injury`:

```python
# REQUIRED PATTERN in planner.py / coach.py
if active_injury and active_injury.get('diagnosis'):
    constraints = active_injury.get('training_constraints', [])
    # FORBIDDEN: Schedule conflicting movements without modification
    if 'knee' in str(constraints).lower():
        suggest_alternative('Squat', 'Box Squat')
```

**Never** schedule high-load movements that conflict with injury constraints.

## Running the Application

```bash
cd saker_pro_source
source ../.venv/bin/activate
streamlit run main.py
```

Headless: `nohup streamlit run main.py --server.headless true > launch.log 2>&1 &`

The llama.cpp server starts automatically on first LLM call (model downloads if needed).

## Testing Strategy

**We test the MATH, not the UI** (Streamlit tests are flaky).

```bash
pytest tests/
```

Mandatory test coverage:
- `analytics.py`: ACWR calculations, Riegel formulas
- `planner.py`: Periodization math (taper weeks < build weeks)
- `powerlifting.py`: DOTS calculations, 1RM estimates

## UI/UX Standards ("Saker Pro Style")

**Never** use raw `st.metric` or `st.markdown` without styling.

```python
# CORRECT
from ui.theme import apply_new_styles
from ui.icons import get_icon

apply_new_styles()
with st.container(border=True):
    st.markdown(f"{get_icon('heart', 'red')} Readiness")
```

**Design System**:
- Background: `#0F172A` (Deep Stratosphere)
- Cards: `rgba(30, 41, 59, 0.5)` with backdrop-filter blur
- Primary Accent: `#258cf4` (Saker Blue)
- Success: `#0bda5b` | Warning: `#f59e0b` | Danger: `#ef4444`

**Anti-patterns**:
- White backgrounds
- Raw Matplotlib charts (use Plotly: `template="plotly_dark"`, `rgba(0,0,0,0)` background)
- Raw emojis (use `get_icon()` from `icons.py`)

## Key Patterns

### LLM Prompting
- Use XML tags: `<SYSTEM>`, `<CONTEXT>`, `<USER>`
- **Calculate metrics in Python**, pass as context (never ask LLM to compute ACWR)
- Always inject `injury_context` when `active_injury` exists

### Analytics (analytics.py)
- **ACWR**: 7-day acute vs 28-day chronic. Optimal: 0.8–1.3
- **Dual ACWR**: Separate cardio (metabolic) vs lifting (mechanical)

### Profile Structure (user_profile.yaml)
```yaml
primary_goal: bodybuilding|5k_time|ironman|powerlifting_meet|hyrox
diet:
  mode: cut|bulk|maintain
training:
  preferred_split: Upper_Lower|PPL|full_body
  preferred_strength_days: 4
  cardio_frequency: Auto|3|4
active_injury:  # CRITICAL - check before any plan generation
  diagnosis: "Iliotibial Band Syndrome"
  training_constraints: ["Limit running to <20 mins"]
  rehab_protocol: ["Glute bridges 3x15"]
```

### Phase Periodization (planner.py → compute_event_meta)
Phases calculated backward from race date:
- **Base** → **Build** → **Peak** → **Taper** → **Race Week**
- Phase lengths vary by goal type (Ironman needs longer taper than 5k)

### Data & Privacy
- **NO SQL, NO Cloud DBs** - Local flat files only (`/uploads/*.csv`, YAML)
- `st.session_state` is volatile; **YAML is truth** - persist immediately

### Streamlit State
- Use `@st.cache_data` for data loading (15-min TTL for Garmin)
- Use `@st.cache_resource` for persistent connections (ChromaDB client)

### Garmin Integration
- Users upload their Garmin `Activities` folder containing `.fit` files
- Parsed via `saker_pro_source/data/garmin_fit.py`
- No authentication required - fully offline

## Canon Knowledge Base

Exercise science source material organized by tier:
- **Tier 1**: Guidelines (ACSM, NSCA, ISSN)
- **Tier 2**: Peer-reviewed research
- **Tier 3**: Expert doctrine (trusted coaches)
- **Tier 4**: Personal preferences

Files use YAML frontmatter. Index with: `python saker_pro_source/rag/index_canon.py`

## Known Gotchas & Anti-Patterns

| Problem | Fix |
|---------|-----|
| Infinite Rerun Loop | Use `on_change` callbacks, don't modify `session_state` in draw functions |
| Hallucinated Metrics | Calculate in Python, pass result to LLM as context string |
| Cloud Leak Suggestions | **Reject** - Local JSON/YAML only, no Firebase/Supabase |
| Garmin 2FA Expiry | `try/except` + prompt user to re-login via UI on 401 |

## Deployment (PyInstaller)

- Build via `compound.spec`
- Include assets: `datas=[('assets', 'assets')]`
- Use `sys._MEIPASS` for asset paths in compiled `.exe`/`.dmg`

## Modifying Code

1. **New analytics**: Add to `saker_pro_source/logic/analytics.py`, export in `__init__.py`
2. **LLM prompts**: Edit `generate_training_block()` or `build_prompt()` in `coach.py`
3. **New data sources**: Parser in `saker_pro_source/data/data_loader.py`, integrate in settings modal
4. **UI changes**: `saker_pro_source/app.py` + `saker_pro_source/ui/theme.py`
5. **Workout templates**: Edit `saker_pro_source/canon/library.json`
6. **Volume calculations**: Edit `saker_pro_source/canon/volume.py`
