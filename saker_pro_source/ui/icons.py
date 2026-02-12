# canon/icons.py

def get_icon(name, color="white", size=24):
    """
    Returns an SVG string for the requested icon name.
    Colors can be hex codes or predefined keys: 'red', 'blue', 'green', 'orange', 'purple', 'teal'.
    """
    
    # Apple-style Gradients (conservative but colorful)
    gradients = {
        "red": ("#ff3b30", "#ff9500"),    # Health / Heart
        "blue": ("#007aff", "#5ac8fa"),   # Sleep / Calm
        "green": ("#34c759", "#30d158"),  # Activity / Workouts
        "orange": ("#ff9500", "#ffcc00"), # Energy / Readiness
        "purple": ("#af52de", "#ff2d55"), # Intensity
        "teal": ("#30b0c7", "#5ac8fa"),   # Strength
        "indigo": ("#5856d6", "#af52de"), # Deep Sleep
        "white": ("#ffffff", "#e5e5e5"),
        "gray": ("#94a3b8", "#64748b"),   # Muted / secondary
        "yellow": ("#fbbf24", "#f59e0b"), # Warning
    }
    
    start_color, end_color = gradients.get(color, (color, color))
    
    # Unique ID for gradient to prevent collisions (sanitize special chars)
    safe_color = color.replace('#', '').replace(' ', '')
    grad_id = f"grad_{name}_{safe_color}_{size}"
    
    # Common SVG Envelope with Gradient Def
    svg_start = f"""<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 4px;"><defs><linearGradient id="{grad_id}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{start_color}" /><stop offset="100%" stop-color="{end_color}" /></linearGradient></defs>"""
    
    # Clean, well-formed SVG paths (Google Material / Lucide-style icons)
    paths = {
        # Existing icons
        "activity": f"""<circle cx="12" cy="12" r="10" stroke="url(#{grad_id})" stroke-width="2" fill="none" opacity="0.3"/><circle cx="12" cy="12" r="6" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><circle cx="12" cy="12" r="2" fill="url(#{grad_id})"/>""",
        
        "heart": f"""<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" fill="url(#{grad_id})"/>""",
        
        "moon": f"""<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="url(#{grad_id})"/>""",
        
        "bolt": f"""<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" fill="url(#{grad_id})"/>""",
        
        "dumbbell": f"""<path d="M6.5 6.5h11v11h-11z" fill="none"/><rect x="2" y="6" width="4" height="12" rx="1" fill="url(#{grad_id})"/><rect x="18" y="6" width="4" height="12" rx="1" fill="url(#{grad_id})"/><rect x="6" y="10" width="12" height="4" fill="url(#{grad_id})"/>""",
        
        "chart": f"""<rect x="3" y="3" width="18" height="18" rx="2" stroke="url(#{grad_id})" stroke-width="2" fill="none" opacity="0.3"/><rect x="7" y="10" width="2" height="7" fill="url(#{grad_id})"/><rect x="11" y="7" width="2" height="10" fill="url(#{grad_id})"/><rect x="15" y="13" width="2" height="4" fill="url(#{grad_id})"/>""",
        
        "scale": f"""<circle cx="12" cy="12" r="10" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M12 6v6l4 2" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/>""",
        
        "food": f"""<path d="M18 8h1a4 4 0 0 1 0 8h-1" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" fill="url(#{grad_id})" opacity="0.8"/><line x1="6" y1="1" x2="6" y2="4" stroke="url(#{grad_id})" stroke-width="2"/><line x1="10" y1="1" x2="10" y2="4" stroke="url(#{grad_id})" stroke-width="2"/><line x1="14" y1="1" x2="14" y2="4" stroke="url(#{grad_id})" stroke-width="2"/>""",
        
        "folder": f"""<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" fill="url(#{grad_id})" opacity="0.8"/><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # NEW: Google Material-style icons
        
        # Check / Success
        "check": f"""<path d="M9 12l2 2 4-4" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><circle cx="12" cy="12" r="10" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        "check_circle": f"""<circle cx="12" cy="12" r="10" fill="url(#{grad_id})"/><path d="M9 12l2 2 4-4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        # Warning / Alert
        "warning": f"""<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" fill="url(#{grad_id})"/><line x1="12" y1="9" x2="12" y2="13" stroke="white" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="17" r="1" fill="white"/>""",
        
        "alert_circle": f"""<circle cx="12" cy="12" r="10" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><line x1="12" y1="8" x2="12" y2="12" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="16" r="1" fill="url(#{grad_id})"/>""",
        
        # Error / Close
        "error": f"""<circle cx="12" cy="12" r="10" fill="url(#{grad_id})"/><path d="M15 9l-6 6M9 9l6 6" stroke="white" stroke-width="2" stroke-linecap="round"/>""",
        
        "close": f"""<path d="M18 6L6 18M6 6l12 12" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/>""",
        
        # Info
        "info": f"""<circle cx="12" cy="12" r="10" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><line x1="12" y1="16" x2="12" y2="12" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="8" r="1" fill="url(#{grad_id})"/>""",
        
        "info_filled": f"""<circle cx="12" cy="12" r="10" fill="url(#{grad_id})"/><line x1="12" y1="16" x2="12" y2="12" stroke="white" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="8" r="1" fill="white"/>""",
        
        # Lock / Security
        "lock": f"""<rect x="3" y="11" width="18" height="11" rx="2" fill="url(#{grad_id})"/><path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        "shield": f"""<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" fill="url(#{grad_id})"/>""",
        
        # Download / Import
        "download": f"""<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><polyline points="7 10 12 15 17 10" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><line x1="12" y1="15" x2="12" y2="3" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/>""",
        
        "upload": f"""<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><polyline points="17 8 12 3 7 8" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><line x1="12" y1="3" x2="12" y2="15" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/>""",
        
        # Running / Cardio
        "run": f"""<circle cx="12" cy="4" r="2" fill="url(#{grad_id})"/><path d="M4 17l4-4 3 3 5-6 4 4" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M15 21l-3-3-3 3" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        "directions_run": f"""<path d="M13.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM9.8 8.9L7 23h2.1l1.8-8 2.1 2v6h2v-7.5l-2.1-2 .6-3C14.8 12 16.8 13 19 13v-2c-1.9 0-3.5-1-4.3-2.4l-1-1.6c-.4-.6-1-1-1.7-1-.3 0-.5.1-.8.1L6 8.3V13h2V9.6l1.8-.7" fill="url(#{grad_id})"/>""",
        
        # Strength / Fitness
        "fitness": f"""<path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z" fill="url(#{grad_id})"/>""",
        
        "muscle": f"""<path d="M6.5 6.5h11v11h-11z" fill="none"/><rect x="2" y="6" width="4" height="12" rx="1" fill="url(#{grad_id})"/><rect x="18" y="6" width="4" height="12" rx="1" fill="url(#{grad_id})"/><rect x="6" y="10" width="12" height="4" fill="url(#{grad_id})"/>""",
        
        # Brain / AI
        "brain": f"""<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.5A2.5 2.5 0 0 1 9.5 2z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.5A2.5 2.5 0 0 0 14.5 2z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        "smart_toy": f"""<rect x="3" y="7" width="18" height="13" rx="2" fill="url(#{grad_id})" opacity="0.8"/><circle cx="9" cy="13" r="2" fill="white"/><circle cx="15" cy="13" r="2" fill="white"/><path d="M12 2v5" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="2" r="1" fill="url(#{grad_id})"/>""",
        
        # Chat / Message
        "chat": f"""<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" fill="url(#{grad_id})" opacity="0.8"/><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        "forum": f"""<path d="M21 6h-2V4c0-1.1-.9-2-2-2H3c-1.1 0-2 .9-2 2v14l4-4h9" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M21 8c1.1 0 2 .9 2 2v12l-4-4h-9c-1.1 0-2-.9-2-2V8h13z" fill="url(#{grad_id})" opacity="0.8"/>""",
        
        # Analytics / Stats
        "analytics": f"""<path d="M3 3v18h18" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        "trending_up": f"""<polyline points="22 7 13.5 15.5 8.5 10.5 2 17" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><polyline points="16 7 22 7 22 13" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        "trending_down": f"""<polyline points="22 17 13.5 8.5 8.5 13.5 2 7" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><polyline points="16 17 22 17 22 11" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        # Clipboard / Plan
        "clipboard": f"""<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1" fill="url(#{grad_id})"/>""",
        
        "assignment": f"""<path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z" fill="url(#{grad_id})" opacity="0.8"/><circle cx="12" cy="3" r="1" fill="white"/><path d="M7 10h10M7 14h7" stroke="white" stroke-width="1.5" stroke-linecap="round"/>""",
        
        # Timer / Clock
        "timer": f"""<circle cx="12" cy="13" r="8" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M12 9v4l2 2" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M10 2h4" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/>""",
        
        "schedule": f"""<circle cx="12" cy="12" r="10" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M12 6v6l4 2" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/>""",
        
        # Sleep
        "bedtime": f"""<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="url(#{grad_id})"/>""",
        
        "hotel": f"""<path d="M7 14c1.66 0 3-1.34 3-3S8.66 8 7 8s-3 1.34-3 3 1.34 3 3 3z" fill="url(#{grad_id})"/><path d="M19 6h-8.5c-.77 0-1.47.31-1.98.82A2.97 2.97 0 0 0 7 8c0 1.02.5 1.93 1.28 2.49-.01.17-.03.33-.03.51 0 .24.03.47.07.7H4v7h2v-3h12v3h2v-7c0-2.21-1.79-4-4-4z" fill="url(#{grad_id})" opacity="0.8"/>""",
        
        # User / Person
        "person": f"""<circle cx="12" cy="8" r="4" fill="url(#{grad_id})"/><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        "account_circle": f"""<circle cx="12" cy="12" r="10" fill="url(#{grad_id})" opacity="0.3"/><circle cx="12" cy="9" r="3" fill="url(#{grad_id})"/><path d="M6.168 18.849A4 4 0 0 1 10 16h4a4 4 0 0 1 3.834 2.855" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # Bird / Falcon (Saker)
        "falcon": f"""<path d="M21 10.5c-.69 0-1.39.14-2.03.4l-2.47-4.94c-.41-.82-1.25-1.34-2.14-1.34H9.64c-.89 0-1.73.52-2.14 1.34L5.03 10.9c-.64-.26-1.34-.4-2.03-.4C2 10.5 1 11.5 1 12.5s1 2 2 2c.69 0 1.39-.14 2.03-.4l2.47 4.94c.41.82 1.25 1.34 2.14 1.34h4.72c.89 0 1.73-.52 2.14-1.34l2.47-4.94c.64.26 1.34.4 2.03.4 1 0 2-1 2-2s-1-2-2-2z" fill="url(#{grad_id})"/><circle cx="8" cy="12" r="1" fill="white"/><circle cx="16" cy="12" r="1" fill="white"/>""",
        
        "bird": f"""<path d="M22 3L2 11l9 2 2 9 9-19z" fill="url(#{grad_id})" opacity="0.8"/><path d="M22 3L2 11l9 2 2 9 9-19z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # Trophy / Achievement
        "trophy": f"""<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M4 22h16" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M18 2H6v7a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V2z" fill="url(#{grad_id})"/>""",
        
        "medal": f"""<circle cx="12" cy="8" r="6" fill="url(#{grad_id})"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        "emoji_events": f"""<path d="M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94.63 1.5 1.98 2.63 3.61 2.96V19H7v2h10v-2h-4v-3.1c1.63-.33 2.98-1.46 3.61-2.96C19.08 12.63 21 10.55 21 8V7c0-1.1-.9-2-2-2zM5 8V7h2v3.82C5.84 10.4 5 9.3 5 8zm14 0c0 1.3-.84 2.4-2 2.82V7h2v1z" fill="url(#{grad_id})"/>""",
        
        # Calendar / Date
        "calendar": f"""<rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><line x1="16" y1="2" x2="16" y2="6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="2" x2="8" y2="6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><line x1="3" y1="10" x2="21" y2="10" stroke="url(#{grad_id})" stroke-width="2"/>""",
        
        "event": f"""<path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2z" fill="url(#{grad_id})" opacity="0.8"/><rect x="5" y="10" width="14" height="2" fill="white"/>""",
        
        # Refresh / Sync
        "refresh": f"""<path d="M21 2v6h-6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M3 22v-6h6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/>""",
        
        "sync": f"""<path d="M21.5 2v6h-6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M2.5 22v-6h6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M2.64 12.2a9 9 0 0 1 15.72-6.36l3.14 2.16" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M21.36 11.8a9 9 0 0 1-15.72 6.36L2.5 16" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/>""",
        
        # Lightbulb / Idea
        "lightbulb": f"""<path d="M9 21h6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M10 17h4" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M12 3a6 6 0 0 0-4 10.5V16h8v-2.5A6 6 0 0 0 12 3z" fill="url(#{grad_id})"/>""",
        
        "tips": f"""<path d="M9 21h6" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M10 17h4" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M12 3a6 6 0 0 0-4 10.5V16h8v-2.5A6 6 0 0 0 12 3z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # Celebration / Party
        "celebration": f"""<path d="M2 22l1-1h3l9-9" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M13 6l1.5-1.5" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M16 9l1.5-1.5" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M19 12l1.5-1.5" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M22 2l-7.5 7.5" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/>""",
        
        "party": f"""<polygon points="3 3 21 12 12 12 21 21 3 12 12 12 3 3" fill="url(#{grad_id})"/>""",
        
        # Star
        "star": f"""<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" fill="url(#{grad_id})"/>""",
        
        "star_outline": f"""<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # Arrows
        "arrow_up": f"""<path d="M12 19V5" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M5 12l7-7 7 7" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        "arrow_down": f"""<path d="M12 5v14" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M19 12l-7 7-7-7" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        "arrow_right": f"""<path d="M5 12h14" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M12 5l7 7-7 7" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        "arrow_left": f"""<path d="M19 12H5" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M12 19l-7-7 7-7" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>""",
        
        # Status circles (solid)
        "circle_green": f"""<circle cx="12" cy="12" r="8" fill="#34c759"/>""",
        
        "circle_yellow": f"""<circle cx="12" cy="12" r="8" fill="#fbbf24"/>""",
        
        "circle_red": f"""<circle cx="12" cy="12" r="8" fill="#ff3b30"/>""",
        
        "circle": f"""<circle cx="12" cy="12" r="8" fill="url(#{grad_id})"/>""",
        
        # Science / Lab
        "science": f"""<path d="M10 2v6l-6 10c-.67 1.13.13 2.5 1.5 2.5h13c1.38 0 2.17-1.37 1.5-2.5L14 8V2" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M8.5 2h7" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="15" r="1" fill="url(#{grad_id})"/><circle cx="14" cy="13" r="1" fill="url(#{grad_id})"/>""",
        
        # Target / Goal
        "target": f"""<circle cx="12" cy="12" r="10" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><circle cx="12" cy="12" r="6" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><circle cx="12" cy="12" r="2" fill="url(#{grad_id})"/>""",
        
        "gps_fixed": f"""<circle cx="12" cy="12" r="4" fill="url(#{grad_id})"/><path d="M12 2v2" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M12 20v2" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M2 12h2" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M20 12h2" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="12" r="8" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # Fire / Flame
        "fire": f"""<path d="M12 22c4.97 0 8-3.58 8-8 0-4.42-4-9-8-13-4 4-8 8.58-8 13 0 4.42 3.03 8 8 8z" fill="url(#{grad_id})"/>""",
        
        "local_fire": f"""<path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z" fill="url(#{grad_id})"/>""",
        
        # Healing / Medical
        "healing": f"""<path d="M17.73 12.02l3.98-3.98a.996.996 0 0 0 0-1.41l-4.34-4.34a.996.996 0 0 0-1.41 0l-3.98 3.98L8 2.29a1 1 0 0 0-1.41 0L2.25 6.63a.996.996 0 0 0 0 1.41l3.98 3.98L2.25 16a.996.996 0 0 0 0 1.41l4.34 4.34c.39.39 1.02.39 1.41 0l3.98-3.98 3.98 3.98c.39.39 1.02.39 1.41 0l4.34-4.34a.996.996 0 0 0 0-1.41l-3.98-3.98z" fill="url(#{grad_id})"/>""",
        
        "medical": f"""<path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z" fill="url(#{grad_id})" opacity="0.3"/><path d="M14 17h-4v-4H6v-2h4V7h4v4h4v2h-4z" fill="url(#{grad_id})"/>""",
        
        # Settings / Gear
        "settings": f"""<circle cx="12" cy="12" r="3" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # Delete / Trash
        "delete": f"""<path d="M3 6h18" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" stroke="url(#{grad_id})" stroke-width="2" fill="none"/>""",
        
        # Strava / Connect
        "strava": f"""<path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.598h4.172L10.463 0l-7 13.828h4.169" fill="url(#{grad_id})"/>""",

        "link": f"""<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/>""",

        # Add / Plus
        "add": f"""<line x1="12" y1="5" x2="12" y2="19" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><line x1="5" y1="12" x2="19" y2="12" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/>""",
        
        "add_circle": f"""<circle cx="12" cy="12" r="10" fill="url(#{grad_id})"/><line x1="12" y1="8" x2="12" y2="16" stroke="white" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="12" x2="16" y2="12" stroke="white" stroke-width="2" stroke-linecap="round"/>""",
        
        # Play / Speed
        "play": f"""<polygon points="5 3 19 12 5 21 5 3" fill="url(#{grad_id})"/>""",
        
        "speed": f"""<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" stroke="url(#{grad_id})" stroke-width="2" fill="none"/><path d="M12 6v6l5 3" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round" fill="none"/>""",
        
        # Weight / Scale  
        "weight": f"""<rect x="2" y="7" width="20" height="14" rx="2" fill="url(#{grad_id})" opacity="0.8"/><path d="M12 3v4" stroke="url(#{grad_id})" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="14" r="4" stroke="white" stroke-width="2" fill="none"/><path d="M12 12v4" stroke="white" stroke-width="1.5" stroke-linecap="round"/>""",
        
        # Body / Fitness Center
        "fitness_center": f"""<path d="M20.57 14.86L22 13.43 20.57 12 17 15.57 8.43 7 12 3.43 10.57 2 9.14 3.43 7.71 2 5.57 4.14 4.14 2.71 2.71 4.14l1.43 1.43L2 7.71l1.43 1.43L2 10.57 3.43 12 7 8.43 15.57 17 12 20.57 13.43 22l1.43-1.43L16.29 22l2.14-2.14 1.43 1.43 1.43-1.43-1.43-1.43L22 16.29z" fill="url(#{grad_id})"/>""",
    }
    
    return svg_start + paths.get(name, paths["activity"]) + "</svg>"


def get_icon_html(name, color="white", size=24, inline=True):
    """
    Returns icon wrapped in a span for inline use in markdown.
    """
    style = "display: inline-block; vertical-align: middle;" if inline else ""
    return f'<span style="{style}">{get_icon(name, color, size)}</span>'


def get_text_icon(name, color="gray", size=16):
    """
    Returns a smaller, text-inline icon suitable for use in paragraphs.
    Defaults to gray/muted color for less visual weight.
    """
    return get_icon(name, color, size)
