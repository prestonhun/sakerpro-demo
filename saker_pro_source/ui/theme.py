import streamlit as st

def apply_new_styles():
    """
    Apply Saker Pro theme styles - matching the reference design.
    
    DESIGN SYSTEM:
    - Background: #0F172A (Deep Stratosphere)
    - Cards: rgba(30, 41, 59, 0.5) with backdrop-filter blur
    - Primary Accent: #258cf4 (Saker Blue)
    - Success: #0bda5b | Warning: #f59e0b | Danger: #ef4444
    - Border: rgba(255, 255, 255, 0.08)
    """

    st.markdown("""
        <style>
        /* ============================================ */
        /* 1. FONTS & CSS VARIABLES                     */
        /* ============================================ */

        /* --- Fonts via Google CDN (Community Cloud) --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        :root {
            /* Core Palette */
            --bg-primary: #0F172A;
            --bg-card: #1E293B;
            --bg-glass: rgba(30, 41, 59, 0.5);
            --bg-glass-hover: rgba(30, 41, 59, 0.7);
            --bg-inner: rgba(15, 23, 42, 0.4);
            
            /* Accent Colors */
            --primary: #258cf4;
            --primary-glow: rgba(37, 140, 244, 0.5);
            --accent-green: #0bda5b;
            --accent-yellow: #f59e0b;
            --accent-red: #ef4444;
            
            /* Text */
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            /* Borders */
            --border-color: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(37, 140, 244, 0.4);
            
            /* Typography */
            --font-main: 'Inter', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }
        
        /* ============================================ */
        /* 2. SCROLLBAR                                 */
        /* ============================================ */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #1d72c4;
        }

        /* ============================================ */
        /* 2.5 HIDE STREAMLIT TOOLBAR & LOADING         */
        /* ============================================ */
        /* Hide the entire top-right toolbar (Stop, Deploy menu, running emoji) */
        [data-testid="stStatusWidget"],
        [data-testid="stToolbar"],
        .stDeployButton,
        header[data-testid="stHeader"] button,
        #MainMenu {
            display: none !important;
            visibility: hidden !important;
        }

        /* ============================================ */
        /* 3. GLOBAL APP BACKGROUND                     */
        /* ============================================ */
        .stApp {
            background-color: var(--bg-primary) !important;
            background-image: 
                radial-gradient(circle at 50% -20%, rgba(37, 140, 244, 0.15), transparent 60%),
                radial-gradient(circle at 80% 20%, rgba(11, 218, 91, 0.05), transparent 40%),
                radial-gradient(circle at 10% 40%, rgba(239, 68, 68, 0.05), transparent 40%) !important;
            font-family: var(--font-main) !important;
        }
        
        /* Ensure main container doesn't cover header */
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewBlockContainer"],
        .stMainBlockContainer {
            margin-top: 0 !important;
            z-index: 1 !important;
            overflow: visible !important;
        }
        
        /* Ensure main content area doesn't block sidebar toggle buttons */
        [data-testid="stMain"],
        .main {
            z-index: 1 !important;
        }
        
        /* Remove default Streamlit top padding from main content */
        .stMainBlockContainer,
        [data-testid="stMainBlockContainer"],
        .block-container,
        [data-testid="block-container"] {
            padding-top: 1rem !important;
        }
        
        /* Also target the main element */
        .main .block-container,
        [data-testid="stMain"] .block-container,
        [data-testid="stMain"] > div:first-child {
            padding-top: 1rem !important;
        }
        
        /* Text selection */
        ::selection {
            background: rgba(37, 140, 244, 0.3);
            color: white;
        }

        /* ============================================ */
        /* 4. SIDEBAR - Fixed Width, No Resize          */
        /* ============================================ */
        
        /* Base sidebar styling */
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"] {
            background-color: var(--bg-primary) !important;
            border-right: 1px solid var(--border-color) !important;
            flex-shrink: 0 !important;
            overflow: hidden !important;
            transition: width 0.3s ease, min-width 0.3s ease !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child {
            transition: margin-left 0.3s ease !important;
        }
        
        /* EXPANDED state - show sidebar at fixed width */
        section[data-testid="stSidebar"][aria-expanded="true"],
        [data-testid="stSidebar"][aria-expanded="true"] {
            width: 256px !important;
            min-width: 256px !important;
            max-width: 256px !important;
        }
        
        section[data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 256px !important;
            min-width: 256px !important;
            max-width: 256px !important;
        }
        
        /* COLLAPSED state - hide sidebar content but keep structure */
        section[data-testid="stSidebar"][aria-expanded="false"],
        [data-testid="stSidebar"][aria-expanded="false"] {
            width: 0 !important;
            min-width: 0 !important;
        }
        
        section[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 256px !important;
            margin-left: -256px !important;
        }
        
        /* Hide sidebar scrollbar */
        [data-testid="stSidebarContent"] {
            overflow-y: auto !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        [data-testid="stSidebarContent"]::-webkit-scrollbar {
            display: none !important;
            width: 0 !important;
        }
        
        /* Kill resize handle completely */
        [data-testid="stSidebar"] > div[style*="cursor"],
        [data-testid="stSidebar"] > div[style*="resize"],
        .stSidebar > div:last-child,
        [data-testid="stSidebar"]::after,
        [data-testid="stSidebar"] > div:last-child {
            display: none !important;
            width: 0 !important;
            pointer-events: none !important;
        }
        
        /* No resize cursor anywhere on sidebar */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] * {
            resize: none !important;
        }
        
        /* Sidebar content styling - minimal top padding */
        [data-testid="stSidebarContent"] {
            padding: 0.5rem 1rem 1rem 1rem !important;
        }
        
        /* Sidebar text colors - except inline-styled elements like logo */
        section[data-testid="stSidebar"] .stMarkdown p:not([style]),
        section[data-testid="stSidebar"] p:not([style]),
        section[data-testid="stSidebar"] span:not([style]) {
            color: var(--text-secondary) !important;
            font-size: 14px;
        }
        
        /* Allow inline styles to override (for logo S and other custom elements) */
        section[data-testid="stSidebar"] span[style*="color"],
        section[data-testid="stSidebar"] div[style*="color"] span {
            color: inherit !important;
        }
        
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: var(--text-primary) !important;
        }
        
        /* Sidebar header area - keep collapse button visible */
        [data-testid="stSidebarHeader"] {
            position: absolute !important;
            top: 0 !important;
            right: 0 !important;
            left: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            overflow: visible !important;
            z-index: 100 !important;
        }
        
        [data-testid="stLogoSpacer"] {
            display: none !important;
        }
        
        /* Logo header styling */
        .saker-logo-header {
            display: flex !important;
            align-items: center !important;
            gap: 10px !important;
            flex: 1 !important;
        }
        
        .saker-logo-box {
            width: 32px !important;
            height: 32px !important;
            min-width: 32px !important;
            background: linear-gradient(135deg, #258cf4, #1d72c4) !important;
            border-radius: 8px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 0 12px rgba(37, 140, 244, 0.4) !important;
        }
        
        .saker-logo-text {
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            letter-spacing: 0.08em !important;
            line-height: 1.1 !important;
        }
        
        .saker-logo-sub {
            font-size: 0.55rem !important;
            color: #258cf4 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            font-weight: 500 !important;
        }
        
        /* COLLAPSE BUTTON - pinned to sidebar edge, rounded */
        /* When sidebar is OPEN - button on right edge of sidebar */
        [data-testid="stSidebarCollapseButton"] {
            position: fixed !important;
            top: 50% !important;
            left: 256px !important;
            transform: translate(-50%, -50%) !important;
            z-index: 9999999 !important;
            margin: 0 !important;
            transition: left 0.3s ease !important;
        }
        
        /* When sidebar is COLLAPSED - button moves to left edge */
        section[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stSidebarCollapseButton"],
        body:has(section[data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebarCollapseButton"] {
            left: 20px !important;
        }
        
        [data-testid="stSidebarCollapseButton"] button {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-muted) !important;
            padding: 0 !important;
            border-radius: 50% !important;
            transition: all 0.2s ease !important;
            width: 28px !important;
            height: 28px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: hidden !important;
            position: relative !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
        }
        
        [data-testid="stSidebarCollapseButton"] button:hover {
            background-color: var(--bg-glass-hover) !important;
            border-color: var(--primary) !important;
            box-shadow: 0 0 12px var(--primary-glow) !important;
        }
        
        /* Hide the text completely */
        [data-testid="stSidebarCollapseButton"] button span {
            font-size: 0 !important;
            color: transparent !important;
            visibility: hidden !important;
        }
        
        /* Create CSS chevron icon - points left when open */
        [data-testid="stSidebarCollapseButton"] button::before {
            content: '' !important;
            position: absolute !important;
            width: 6px !important;
            height: 6px !important;
            border-left: 2px solid var(--text-muted) !important;
            border-bottom: 2px solid var(--text-muted) !important;
            transform: rotate(45deg) !important;
            margin-left: 2px !important;
            transition: transform 0.2s ease !important;
        }
        
        /* Chevron points right when sidebar is collapsed */
        section[data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="stSidebarCollapseButton"] button::before,
        body:has(section[data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebarCollapseButton"] button::before {
            transform: rotate(-135deg) !important;
            margin-left: -2px !important;
        }
        
        [data-testid="stSidebarCollapseButton"] button:hover::before {
            border-color: var(--text-primary) !important;
        }
        
        /* RADIO BUTTONS - Hide circles, clean nav styling */
        section[data-testid="stSidebar"] .stRadio {
            width: 100% !important;
        }
        
        section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
            gap: 4px !important;
            padding: 0 !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        
        /* Hide the radio input circles */
        section[data-testid="stSidebar"] .stRadio input[type="radio"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            position: absolute !important;
        }
        
        /* Hide the visual radio circle div */
        section[data-testid="stSidebar"] .stRadio label > div:first-child {
            display: none !important;
        }
        
        /* Style the radio labels as nav items - FULL WIDTH backgrounds */
        section[data-testid="stSidebar"] .stRadio label {
            background: transparent !important;
            border: none !important;
            border-left: 3px solid transparent !important;
            border-radius: 0 8px 8px 0 !important;
            padding: 12px 16px 12px 13px !important;
            margin: 3px 8px 3px 0 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            display: block !important;
            width: calc(100% - 8px) !important;
            min-width: 220px !important;
            box-sizing: border-box !important;
        }
        
        section[data-testid="stSidebar"] .stRadio label p {
            display: flex !important;
            align-items: center !important;
        }
        
        section[data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255, 255, 255, 0.05) !important;
        }
        
        /* Active nav item with blue left accent line */
        section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
            background: rgba(37, 140, 244, 0.15) !important;
            border-left: 3px solid var(--primary) !important;
        }
        
        section[data-testid="stSidebar"] .stRadio label:has(input:checked) p {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        
        section[data-testid="stSidebar"] .stRadio label:has(input:checked) p span {
            color: #ffffff !important;
        }
        
        /* Active nav item - icon color change */
        section[data-testid="stSidebar"] .stRadio label:has(input:checked) svg {
            stroke: var(--primary) !important;
        }
        
        /* Nav item hover - icon color */
        section[data-testid="stSidebar"] .stRadio label:hover svg {
            stroke: var(--text-primary) !important;
        }
        
        /* Nav item text */
        section[data-testid="stSidebar"] .stRadio label p {
            color: var(--text-secondary) !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
        }
        
        /* Nav icons */
        section[data-testid="stSidebar"] .stRadio label p svg {
            flex-shrink: 0 !important;
            transition: stroke 0.2s ease !important;
        }
        
        /* Hide "Navigation" label */
        section[data-testid="stSidebar"] .stRadio > label[data-testid="stWidgetLabel"] {
            display: none !important;
        }

        /* ============================================ */
        /* 5. HEADER - Transparent + Expand Button      */
        /* ============================================ */
        header[data-testid="stHeader"] {
            background: transparent !important;
            border: none !important;
            z-index: 999998 !important;
            height: auto !important;
            min-height: 48px !important;
            pointer-events: none !important;
        }
        
        /* Make header children clickable */
        header[data-testid="stHeader"] > * {
            pointer-events: auto !important;
        }
        
        /* Hide toolbar but keep header functional for expand button */
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* EXPAND BUTTON in header - when sidebar is collapsed */
        header[data-testid="stHeader"] button,
        header[data-testid="stHeader"] button[data-testid="stBaseButton-headerNoPadding"] {
            position: fixed !important;
            top: 1rem !important;
            left: 1rem !important;
            z-index: 999999 !important;
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
            width: 40px !important;
            height: 40px !important;
            padding: 0 !important;
            opacity: 1 !important;
            visibility: visible !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease !important;
            pointer-events: auto !important;
            overflow: hidden !important;
        }
        
        header[data-testid="stHeader"] button:hover {
            background-color: var(--bg-glass-hover) !important;
            border-color: var(--primary) !important;
            box-shadow: 0 0 15px var(--primary-glow) !important;
        }
        
        /* Hide text in header expand button */
        header[data-testid="stHeader"] button span {
            font-size: 0 !important;
            visibility: hidden !important;
        }
        
        /* CSS chevron for header expand button - points right */
        header[data-testid="stHeader"] button::before {
            content: '' !important;
            position: absolute !important;
            width: 8px !important;
            height: 8px !important;
            border-right: 2px solid var(--text-secondary) !important;
            border-bottom: 2px solid var(--text-secondary) !important;
            transform: rotate(-45deg) !important;
        }
        
        header[data-testid="stHeader"] button:hover::before {
            border-color: var(--text-primary) !important;
        }

        /* ============================================ */
        /* 6. GLASS PANEL CARDS                         */
        /* ============================================ */
        /* 
         * Target st.container(border=True) cards
         * Structure: stColumn > stVerticalBlock > stLayoutWrapper > stVerticalBlock (content)
         * The inner stLayoutWrapper (with stVerticalBlock child) is the actual card
         */
        
        /* Cards: stLayoutWrapper that contains stVerticalBlock (not stHorizontalBlock) */
        /* EXCLUDE dialogs from card styling */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]):not([data-testid="stModal"] *):not([role="dialog"] *) {
            background: rgba(30, 41, 59, 0.5) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            margin-bottom: 16px !important;
            position: relative !important;
            overflow: visible !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        /* Dialog content should NOT have card styling */
        [data-testid="stModal"] [data-testid="stLayoutWrapper"],
        [role="dialog"] [data-testid="stLayoutWrapper"] {
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Legacy selector */
        [data-testid="stVerticalBlockBorderWrapper"]:not([data-testid="stModal"] *):not([role="dialog"] *) {
            background: rgba(30, 41, 59, 0.5) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            margin-bottom: 16px !important;
            position: relative !important;
            overflow: visible !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        /* Row/Horizontal wrappers should NOT be styled as cards - this overrides the above */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stHorizontalBlock"]) {
            background: transparent !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: visible !important;
        }
        
        /* Inner stVerticalBlock inside cards - remove Streamlit's default border */
        [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"],
        [data-testid="stLayoutWrapper"] > .stVerticalBlock {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        
        /* Hover state for cards (stLayoutWrapper with stVerticalBlock child) - exclude dialogs */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]):not([data-testid="stModal"] *):not([role="dialog"] *):hover,
        [data-testid="stVerticalBlockBorderWrapper"]:not([data-testid="stModal"] *):not([role="dialog"] *):hover {
            border-color: rgba(37, 140, 244, 0.4) !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 0 20px rgba(37, 140, 244, 0.15) !important;
            transform: translateY(-2px) !important;
        }
        
        /* But row wrappers should NOT have hover effects */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stHorizontalBlock"]):hover {
            border-color: transparent !important;
            box-shadow: none !important;
            transform: none !important;
        }
        
        /* Glow effect on hover for cards - exclude dialogs */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]):not([data-testid="stModal"] *):not([role="dialog"] *)::after,
        [data-testid="stVerticalBlockBorderWrapper"]:not([data-testid="stModal"] *):not([role="dialog"] *)::after {
            content: '' !important;
            position: absolute !important;
            right: -24px !important;
            bottom: -24px !important;
            width: 96px !important;
            height: 96px !important;
            background: rgba(37, 140, 244, 0.1) !important;
            border-radius: 50% !important;
            filter: blur(32px) !important;
            opacity: 0.5 !important;
            pointer-events: none !important;
            transition: opacity 0.3s ease !important;
        }
        
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]):not([data-testid="stModal"] *):not([role="dialog"] *):hover::after,
        [data-testid="stVerticalBlockBorderWrapper"]:not([data-testid="stModal"] *):not([role="dialog"] *):hover::after {
            opacity: 1 !important;
        }
        
        /* No glow for row wrappers */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stHorizontalBlock"])::after {
            display: none !important;
        }
        
        /* No glow/pseudo elements in dialogs */
        [data-testid="stModal"] [data-testid="stLayoutWrapper"]::after,
        [role="dialog"] [data-testid="stLayoutWrapper"]::after {
            display: none !important;
        }
        
        /* Card content should be above the glow */
        [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            position: relative !important;
            z-index: 1 !important;
        }
        
        /* ============================================ */
        /* EQUAL HEIGHT COLUMNS                         */
        /* ============================================ */
        /* Make columns in a row stretch to equal heights */
        [data-testid="stHorizontalBlock"] {
            display: flex !important;
            align-items: stretch !important;
        }
        
        /* Each column in a row should stretch */
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            display: flex !important;
            flex-direction: column !important;
        }
        
        /* Vertical blocks inside columns should stretch */
        [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 !important;
        }
        
        /* Cards (bordered containers) inside columns should stretch to fill */
        [data-testid="stColumn"] [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]),
        [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }
        
        /* Content inside cards should also flex-grow */
        [data-testid="stColumn"] [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"],
        [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] > div {
            flex: 1 !important;
            display: flex !important;
            flex-direction: column !important;
        }
        
        /* 
         * Nested layout wrappers inside CARDS should NOT be styled.
         * A "card" is stLayoutWrapper:has(> stVerticalBlock).
         * The outer row wrapper has stHorizontalBlock, so it's not a card.
         * We only want to remove styling from cards nested inside OTHER cards.
         */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]) [data-testid="stLayoutWrapper"],
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent !important;
            border: none !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            transform: none !important;
            border-radius: 0 !important;
        }
        
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]) [data-testid="stLayoutWrapper"]:hover,
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"]:hover {
            background: transparent !important;
            border: none !important;
            border-color: transparent !important;
            box-shadow: none !important;
            transform: none !important;
        }
        
        /* Disable glow on nested wrappers inside cards */
        [data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"]) [data-testid="stLayoutWrapper"]::after,
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"]::after {
            display: none !important;
            content: none !important;
        }
        
        /* Ensure charts inside cards have transparent background */
        [data-testid="stVerticalBlockBorderWrapper"] .js-plotly-plot,
        [data-testid="stLayoutWrapper"] .js-plotly-plot,
        [data-testid="stVerticalBlockBorderWrapper"] .js-plotly-plot .plotly,
        [data-testid="stLayoutWrapper"] .js-plotly-plot .plotly {
            background: transparent !important;
        }

        /* ============================================ */
        /* 7. METRICS - Telemetry Style                 */
        /* ============================================ */
        /* Metrics inside cards - NO card styling, just content */
        [data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stMetric"],
        [data-testid="stLayoutWrapper"] div[data-testid="stMetric"],
        div[data-testid="stMetric"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 0.5rem 0 !important;
            backdrop-filter: none !important;
            transition: none !important;
            transform: none !important;
            box-shadow: none !important;
        }
        
        div[data-testid="stMetric"]:hover {
            border-color: transparent !important;
            background: transparent !important;
            box-shadow: none !important;
            transform: none !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        
        [data-testid="stMetricValue"] {
            color: var(--text-primary) !important;
            font-family: var(--font-mono) !important;
            font-size: 1.25rem !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 10px !important;
            font-weight: 500 !important;
        }
        
        [data-testid="stMetricDelta"] svg {
            width: 12px !important;
            height: 12px !important;
        }
        
        /* Delta colors */
        [data-testid="stMetricDelta"][data-testid-delta="positive"] {
            color: var(--accent-green) !important;
            background: rgba(11, 218, 91, 0.1) !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }
        
        [data-testid="stMetricDelta"][data-testid-delta="negative"] {
            color: var(--accent-red) !important;
            background: rgba(239, 68, 68, 0.1) !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
        }

        /* ============================================ */
        /* 8. BUTTONS                                   */
        /* ============================================ */
        .stButton > button {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-primary) !important;
            border-radius: 0.375rem !important;
            font-weight: 500 !important;
            font-size: 12px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border-color: var(--primary) !important;
        }
        
        /* Primary button style */
        .stButton > button[kind="primary"] {
            background: var(--primary) !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 4px 12px var(--primary-glow) !important;
        }
        
        /* Secondary button style - ensure visible on dark background */
        .stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid var(--primary) !important;
            color: var(--text-primary) !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: rgba(37, 140, 244, 0.15) !important;
            border-color: var(--primary) !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: #1d72c4 !important;
            box-shadow: 0 6px 16px var(--primary-glow) !important;
        }

        /* ============================================ */
        /* 9. INPUTS & FORMS                            */
        /* ============================================ */
        /* Standard inputs - border on inner container (label stays outside) */
        .stTextInput > div > div,
        .stSelectbox > div > div,
        .stTextArea > div > div {
            background-color: var(--bg-inner) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.375rem !important;
            color: var(--text-primary) !important;
        }
        
        /* Remove nested borders from text input to prevent double border */
        .stTextInput > div > div > div,
        .stTextInput [data-baseweb="input"],
        .stTextInput [data-baseweb="base-input"],
        .stSelectbox > div > div > div,
        .stTextArea > div > div > div {
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Text input focus - blue border */
        .stTextInput > div > div:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Number input - remove borders from wrapper divs (border is on [data-baseweb] element below) */
        .stNumberInput > div:last-child {
            background-color: transparent !important;
            border: none !important;
        }
        
        /* Remove borders from wrapper divs inside number input */
        .stNumberInput > div:last-child > div {
            border: none !important;
            box-shadow: none !important;
        }
        
        .stTextInput > div > div:focus-within,
        .stSelectbox > div > div:focus-within,
        .stTextArea > div > div:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Labels */
        .stTextInput label,
        .stNumberInput label,
        .stSelectbox label,
        .stTextArea label {
            color: var(--text-secondary) !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        /* ============================================ */
        /* 9B. MULTISELECT                              */
        /* ============================================ */
        /* Style the inner select container (after the label) */
        [data-testid="stMultiSelect"] > div:last-child {
            background-color: var(--bg-inner) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.375rem !important;
        }
        
        /* Remove borders from nested elements to prevent double border */
        [data-testid="stMultiSelect"] > div:last-child > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Focus state on the inner container */
        [data-testid="stMultiSelect"] > div:last-child:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Label styling */
        [data-testid="stMultiSelect"] label {
            color: var(--text-secondary) !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        
        /* Multiselect tags/pills - override red */
        [data-testid="stMultiSelect"] [data-baseweb="tag"],
        [data-baseweb="tag"] {
            background-color: rgba(37, 140, 244, 0.2) !important;
            border: 1px solid rgba(37, 140, 244, 0.4) !important;
            color: var(--text-primary) !important;
            border-radius: 4px !important;
        }
        
        [data-testid="stMultiSelect"] [data-baseweb="tag"]:hover,
        [data-baseweb="tag"]:hover {
            background-color: rgba(37, 140, 244, 0.3) !important;
            border-color: var(--primary) !important;
        }
        
        /* Tag close/remove button */
        [data-baseweb="tag"] [role="presentation"] {
            color: var(--text-secondary) !important;
        }
        
        [data-baseweb="tag"] [role="presentation"]:hover {
            color: var(--text-primary) !important;
            background: rgba(255, 255, 255, 0.1) !important;
        }

        /* ============================================ */
        /* 9C. SLIDERS                                  */
        /* ============================================ */
        
        /* Slider track - single solid color */
        [data-testid="stSlider"] [data-baseweb="slider"] > div,
        [data-testid="stSlider"] [data-baseweb="slider"] > div > div,
        [data-baseweb="slider"] > div > div {
            background: rgba(100, 116, 139, 0.4) !important;
            background-color: rgba(100, 116, 139, 0.4) !important;
        }
        
        /* Slider thumb (the draggable circle) */
        [data-testid="stSlider"] [role="slider"],
        [data-baseweb="slider"] [role="slider"] {
            background-color: var(--primary) !important;
            border: 2px solid white !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
        }
        
        [data-testid="stSlider"] [role="slider"]:hover,
        [data-testid="stSlider"] [role="slider"]:focus,
        [data-baseweb="slider"] [role="slider"]:hover,
        [data-baseweb="slider"] [role="slider"]:focus {
            background-color: #1d72c4 !important;
            box-shadow: 0 0 0 4px rgba(37, 140, 244, 0.3), 0 2px 6px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Slider value display (min/max labels) */
        [data-testid="stSlider"] [data-testid="stTickBarMin"],
        [data-testid="stSlider"] [data-testid="stTickBarMax"] {
            color: var(--text-secondary) !important;
        }
        
        /* Slider current value tooltip/display (text above thumb) */
        [data-testid="stSlider"] [data-testid="stThumbValue"],
        [data-baseweb="slider"] [data-testid="stThumbValue"],
        [data-testid="stSlider"] > div:first-child > div:first-child,
        [data-testid="stSlider"] > div > div:first-child {
            color: var(--primary) !important;
            background-color: transparent !important;
            background: transparent !important;
        }
        
        /* Slider tick labels/options for select_slider */
        [data-testid="stSlider"] [data-baseweb="slider"] > div:last-child {
            color: var(--text-secondary) !important;
            background: transparent !important;
        }
        
        /* Select slider options text */
        [data-testid="stSlider"] label + div > div > div > div:last-child > div {
            color: var(--text-secondary) !important;
            background: transparent !important;
        }

        /* ============================================ */
        /* 9D. DATE INPUT & CALENDAR                    */
        /* ============================================ */
        /* Date input field text */
        [data-testid="stDateInput"] input {
            color: var(--text-primary) !important;
            background-color: transparent !important;
        }
        
        /* Style the inner input container (after the label) with standard border */
        /* Target multiple possible container structures */
        [data-testid="stDateInput"] > div:last-child,
        [data-testid="stDateInput"] > div > div,
        [data-testid="stDateInput"] [data-baseweb="input"],
        [data-testid="stDateInput"] [data-baseweb="base-input"] {
            background-color: var(--bg-inner) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.375rem !important;
        }
        
        /* Ensure nested divs don't add extra borders */
        [data-testid="stDateInput"] [data-baseweb="input"] > div,
        [data-testid="stDateInput"] [data-baseweb="base-input"] > div {
            border: none !important;
            box-shadow: none !important;
            background-color: transparent !important;
        }
        
        /* Date input focus border - blue border only when selected */
        [data-testid="stDateInput"] > div:last-child:focus-within,
        [data-testid="stDateInput"] [data-baseweb="input"]:focus-within,
        [data-testid="stDateInput"] [data-baseweb="base-input"]:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 3px rgba(37, 140, 244, 0.3) !important;
        }
        
        /* Label styling */
        [data-testid="stDateInput"] label {
            color: var(--text-secondary) !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        
        /* ============================================ */
        /* 9D2. TIME INPUT                              */
        /* ============================================ */
        /* Style the inner input container (after the label) */
        [data-testid="stTimeInput"] > div:last-child {
            background-color: var(--bg-inner) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.375rem !important;
        }
        
        /* Remove borders from nested elements to prevent double border */
        [data-testid="stTimeInput"] > div:last-child > div,
        [data-testid="stTimeInput"] [data-baseweb="input"] {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }
        
        /* Time input field text */
        [data-testid="stTimeInput"] input {
            color: var(--text-primary) !important;
            background: transparent !important;
        }
        
        /* Time input focus border - blue instead of red */
        [data-testid="stTimeInput"] > div:last-child:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Time input label */
        [data-testid="stTimeInput"] label {
            color: var(--text-secondary) !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }

        /* Calendar popup styling */
        [data-baseweb="calendar"] {
            background-color: #1E293B !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 12px !important;
        }
        
        /* Calendar text colors */
        [data-baseweb="calendar"] * {
            color: #f5f5f7 !important;
        }
        
        /* CRITICAL: Override Streamlit's .st-XX::after pseudo-element that creates the red bubble */
        /* These are dynamically generated classes, so we target ALL ::after on calendar gridcells */
        [data-baseweb="calendar"] div[role="gridcell"] div::after,
        [data-baseweb="calendar"] [role="gridcell"] *::after,
        [data-baseweb="popover"] div[role="gridcell"] div::after,
        [data-baseweb="popover"] [role="gridcell"] *::after {
            background-color: #258cf4 !important;
            background: #258cf4 !important;
            border: none !important;
            border-color: #258cf4 !important;
        }
        
        /* Also target any class starting with st- inside calendar that uses ::after */
        [data-baseweb="calendar"] [class*="st-"]::after,
        [data-baseweb="popover"] [class*="st-"]::after {
            background-color: #258cf4 !important;
            background: #258cf4 !important;
            border: none !important;
            border-color: #258cf4 !important;
        }
        
        /* CRITICAL: Remove red border from calendar selected dates - use blue instead */
        [data-baseweb="calendar"] [class*="st-"],
        [data-baseweb="popover"] [class*="st-"],
        [data-baseweb="calendar"] div[role="gridcell"] [class*="st-"],
        [data-baseweb="popover"] div[role="gridcell"] [class*="st-"] {
            border-color: transparent !important;
            outline: none !important;
        }
        
        /* Force blue border on selected calendar day containers */
        [data-baseweb="calendar"] div[role="gridcell"][aria-selected="true"],
        [data-baseweb="calendar"] div[role="gridcell"][aria-selected="true"] > div,
        [data-baseweb="calendar"] div[role="gridcell"][aria-selected="true"] > div > div {
            border: 2px solid #258cf4 !important;
            border-radius: 50% !important;
            outline: none !important;
        }
        
        /* Hide empty gridcells (no content/date number) - these appear as rectangular boxes */
        [data-baseweb="calendar"] div[role="gridcell"]:empty,
        [data-baseweb="popover"] div[role="gridcell"]:empty {
            visibility: hidden !important;
            background: transparent !important;
            border: none !important;
        }
        
        /* Also hide gridcells that have no text content (empty placeholder cells) */
        [data-baseweb="calendar"] div[role="gridcell"]:not(:has(*)),
        [data-baseweb="popover"] div[role="gridcell"]:not(:has(*)) {
            visibility: hidden !important;
            background: transparent !important;
            border: none !important;
        }
        
        /* Hide the ::after pseudo-element on empty/placeholder gridcells */
        [data-baseweb="calendar"] div[role="gridcell"]:empty::after,
        [data-baseweb="popover"] div[role="gridcell"]:empty::after,
        [data-baseweb="calendar"] div[role="gridcell"]:not(:has(*))::after,
        [data-baseweb="popover"] div[role="gridcell"]:not(:has(*))::after {
            display: none !important;
            background: transparent !important;
        }
        
        /* NUCLEAR: Override ALL calendar day backgrounds - target the inner div that has the color */
        [data-baseweb="calendar"] div[role="gridcell"] > div,
        [data-baseweb="calendar"] div[role="gridcell"] > div > div,
        [data-baseweb="calendar"] [role="gridcell"] div[style],
        [data-baseweb="calendar"] [role="gridcell"] div[style*="background"] {
            background: transparent !important;
            background-color: transparent !important;
        }
        
        /* Calendar day - SELECTED state - solid blue bubble */
        [data-baseweb="calendar"] div[role="gridcell"][aria-selected="true"] > div,
        [data-baseweb="calendar"] div[role="gridcell"][aria-selected="true"] > div > div,
        [data-baseweb="calendar"] div[role="gridcell"][aria-selected="true"] div[style],
        [data-baseweb="calendar"] [aria-selected="true"],
        [data-baseweb="calendar"] [aria-selected="true"] > div {
            background: #258cf4 !important;
            background-color: #258cf4 !important;
            color: white !important;
            border-radius: 50% !important;
        }
        
        /* Calendar day - HOVER state */
        [data-baseweb="calendar"] div[role="gridcell"]:hover > div,
        [data-baseweb="calendar"] div[role="gridcell"]:hover > div > div,
        [data-baseweb="calendar"] [data-highlighted="true"],
        [data-baseweb="calendar"] [data-highlighted="true"] > div {
            background: rgba(37, 140, 244, 0.3) !important;
            background-color: rgba(37, 140, 244, 0.3) !important;
        }
        
        /* Popover / dropdown styling */
        [data-baseweb="popover"] {
            background-color: #1E293B !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 12px !important;
            z-index: 999999 !important;
        }

        /* ============================================ */
        /* 9E. TOGGLE / CHECKBOX                        */
        /* ============================================ */
        /* Regular checkbox */
        [data-testid="stCheckbox"] > label > div:first-child {
            border-color: var(--border-color) !important;
            background-color: var(--bg-inner) !important;
        }
        
        [data-testid="stCheckbox"] > label > div:first-child:has(input:checked) {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
        }
        
        /* Toggle switch appearance (st.toggle uses stCheckbox testid) */
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > div:first-child {
            background-color: rgba(100, 116, 139, 0.4) !important;
            border: none !important;
            border-radius: 999px !important;
            width: 48px !important;
            height: 24px !important;
            padding: 2px !important;
        }
        
        /* Toggle switch thumb */
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > div:first-child > div {
            background-color: white !important;
            border-radius: 50% !important;
            width: 20px !important;
            height: 20px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
            transition: transform 0.2s ease !important;
        }
        
        /* Toggle checked state - track */
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input:checked) > div:first-child {
            background-color: var(--primary) !important;
        }
        
        /* Toggle checked state - thumb position */
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"]:has(input:checked) > div:first-child > div {
            transform: translateX(24px) !important;
        }
        
        /* Label text next to toggle */
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > div:last-child {
            background: transparent !important;
            color: var(--text-primary) !important;
        }
        
        /* Remove any background from label container */
        [data-testid="stCheckbox"] label[data-baseweb="checkbox"] > div:last-child > div {
            background: transparent !important;
        }
        
        [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] {
            background: transparent !important;
        }
        
        [data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] {
            background: transparent !important;
        }

        /* ============================================ */
        /* 9F. SEGMENTED CONTROL / TOGGLE BUTTON        */
        /* ============================================ */
        [data-testid="stSegmentedControl"],
        [data-baseweb="button-group"] {
            background: var(--bg-inner) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            padding: 2px !important;
        }
        
        [data-testid="stSegmentedControl"] button,
        [data-baseweb="button-group"] button {
            background: transparent !important;
            border: none !important;
            color: var(--text-secondary) !important;
            border-radius: 0.375rem !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stSegmentedControl"] button:hover,
        [data-baseweb="button-group"] button:hover {
            background: rgba(255, 255, 255, 0.05) !important;
            color: var(--text-primary) !important;
        }
        
        [data-testid="stSegmentedControl"] button[aria-checked="true"],
        [data-testid="stSegmentedControl"] button[aria-pressed="true"],
        [data-baseweb="button-group"] button[aria-checked="true"],
        [data-baseweb="button-group"] button[aria-selected="true"] {
            background: var(--primary) !important;
            color: white !important;
            box-shadow: 0 2px 8px var(--primary-glow) !important;
        }

        /* ============================================ */
        /* 10. EXPANDER                                 */
        /* ============================================ */
        [data-testid="stExpander"] {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            backdrop-filter: blur(20px) !important;
        }
        
        [data-testid="stExpander"] summary {
            color: var(--text-primary) !important;
            font-weight: 600 !important;
            display: flex !important;
            align-items: center !important;
            flex-direction: row !important;
        }

        /* Expander toggle icon — keep inline with text */
        [data-testid="stExpander"] summary [data-testid="stExpanderToggleIcon"] {
            font-family: 'Material Symbols Rounded', sans-serif !important;
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
            font-size: 20px !important;
            font-weight: normal !important;
            font-style: normal !important;
            line-height: 1 !important;
            display: inline-flex !important;
            align-items: center !important;
            width: 20px !important;
            height: 20px !important;
            overflow: hidden !important;
            flex-shrink: 0 !important;
        }

        /* Hide the info/help tooltip icon globally */
        [data-testid="stTooltipIcon"] {
            display: none !important;
        }

        /* ============================================ */
        /* 11. TABS                                     */
        /* ============================================ */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid var(--border-color) !important;
            gap: 0 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            color: var(--text-secondary) !important;
            border: none !important;
            padding: 0.75rem 1rem !important;
            font-size: 12px !important;
            font-weight: 500 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text-primary) !important;
        }
        
        .stTabs [aria-selected="true"] {
            color: var(--text-primary) !important;
            border-bottom: 2px solid var(--primary) !important;
            background: transparent !important;
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            background: var(--primary) !important;
        }

        /* ============================================ */
        /* 12. PROGRESS BARS                            */
        /* ============================================ */
        
        /* Main progress bar container - hide default background */
        .stProgress,
        [data-testid="stProgress"] {
            background: transparent !important;
        }
        
        /* The track (background of progress bar) */
        .stProgress [data-baseweb="progress-bar"],
        [data-testid="stProgress"] [data-baseweb="progress-bar"],
        [role="progressbar"].st-ck {
            background-color: rgba(100, 116, 139, 0.3) !important;
            border-radius: 9999px !important;
            height: 8px !important;
            overflow: hidden !important;
        }
        
        /* The filled portion */
        .stProgress [data-baseweb="progress-bar"] > div > div > div,
        [data-testid="stProgress"] [data-baseweb="progress-bar"] > div > div > div,
        [role="progressbar"] .st-jb {
            background: linear-gradient(90deg, #1d4ed8, var(--primary)) !important;
            border-radius: 9999px !important;
        }
        
        /* Hide any extra wrapper divs that might show grey */
        .stProgress > div:first-child > div:not([data-baseweb="progress-bar"]):not([data-testid="stMarkdownContainer"]),
        [data-testid="stProgress"] > div:first-child > div:not([data-baseweb="progress-bar"]):not([data-testid="stMarkdownContainer"]) {
            background: transparent !important;
        }
        
        /* BaseWeb progress bar inner elements */
        [data-baseweb="progress-bar"] > div {
            background: transparent !important;
        }
        
        [data-baseweb="progress-bar"] > div > div {
            background-color: rgba(100, 116, 139, 0.3) !important;
            border-radius: 9999px !important;
        }
        
        [data-baseweb="progress-bar"] > div > div > div {
            background: linear-gradient(90deg, #1d4ed8, var(--primary)) !important;
            border-radius: 9999px !important;
        }

        /* ============================================ */
        /* 13. CHARTS (Plotly)                          */
        /* ============================================ */
        .js-plotly-plot .plotly .bg {
            fill: transparent !important;
        }
        
        .js-plotly-plot {
            background: transparent !important;
        }

        /* ============================================ */
        /* 14. FILE UPLOADER - Apple-Style Native Look  */
        /* ============================================ */
        /* Container - clean, minimal with subtle card look */
        [data-testid="stFileUploader"] {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: rgba(255, 255, 255, 0.15) !important;
            background: var(--bg-glass-hover) !important;
        }
        
        /* Hide the default dropzone section styling */
        [data-testid="stFileUploader"] section {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        
        /* Hide drag & drop text and icon for cleaner look */
        [data-testid="stFileUploader"] section > div:first-child {
            display: none !important;
        }
        
        /* Apple-style "Browse files" button - pill shaped, subtle */
        [data-testid="stFileUploader"] button,
        [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 8px 16px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }
        
        [data-testid="stFileUploader"] button:hover,
        [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"]:hover {
            background: rgba(255, 255, 255, 0.12) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }
        
        [data-testid="stFileUploader"] button:active {
            background: rgba(255, 255, 255, 0.06) !important;
            transform: scale(0.98) !important;
        }
        
        /* File name display when file is selected */
        [data-testid="stFileUploader"] small {
            color: var(--text-secondary) !important;
            font-size: 12px !important;
        }
        
        /* Uploaded file info styling */
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
            background: rgba(37, 140, 244, 0.1) !important;
            border: 1px solid rgba(37, 140, 244, 0.2) !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            margin-top: 8px !important;
        }
        
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] span {
            color: var(--text-primary) !important;
        }
        
        /* Delete button for uploaded file */
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button {
            background: transparent !important;
            border: none !important;
            padding: 4px !important;
            min-width: auto !important;
        }
        
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button:hover {
            background: rgba(239, 68, 68, 0.2) !important;
            border-radius: 4px !important;
        }
        
        /* Label styling */
        [data-testid="stFileUploader"] label {
            color: var(--text-secondary) !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            margin-bottom: 8px !important;
        }

        /* ============================================ */
        /* 15. NOTIFICATIONS & ALERTS                   */
        /* ============================================ */
        div[data-baseweb="toast"] {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-left: 4px solid var(--primary) !important;
            color: var(--text-primary) !important;
            backdrop-filter: blur(12px) !important;
        }
        
        .stAlert {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
            color: var(--text-primary) !important;
        }

        /* ============================================ */
        /* 16. DATAFRAMES & TABLES                      */
        /* ============================================ */
        [data-testid="stDataFrame"] {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
        }
        
        [data-testid="stDataFrame"] th {
            background: rgba(255, 255, 255, 0.05) !important;
            color: var(--text-secondary) !important;
            font-size: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }
        
        [data-testid="stDataFrame"] td {
            color: var(--text-primary) !important;
            border-color: var(--border-color) !important;
        }

        /* ============================================ */
        /* 17. DIALOGS                                  */
        /* ============================================ */
        [data-testid="stModal"] > div {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.75rem !important;
            backdrop-filter: blur(20px) !important;
        }

        /* ============================================ */
        /* 18. HIDE FOOTER                              */
        /* ============================================ */
        footer {
            display: none !important;
        }
        
        #MainMenu {
            display: none !important;
        }

        /* ============================================ */
        /* 19. GLOBAL TEXT COLORS                       */
        /* ============================================ */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
            font-family: var(--font-main) !important;
        }
        
        p, span, div {
            font-family: var(--font-main) !important;
        }
        
        .stMarkdown {
            color: var(--text-secondary) !important;
        }
        
        .stMarkdown h1,
        .stMarkdown h2,
        .stMarkdown h3 {
            color: var(--text-primary) !important;
        }

        /* ============================================ */
        /* 20. STATUS BADGES                            */
        /* ============================================ */
        .status-online {
            background: rgba(11, 218, 91, 0.2) !important;
            color: #0bda5b !important;
            border: 1px solid rgba(11, 218, 91, 0.3) !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            font-size: 9px !important;
            font-weight: 700 !important;
        }
        
        /* ============================================ */
        /* 21. CUSTOM EXPAND BUTTON (always visible)    */
        /* ============================================ */
        #custom-expand-btn {
            position: fixed !important;
            top: 1rem !important;
            left: 1rem !important;
            z-index: 9999999 !important;
            background-color: #1E293B !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
            width: 40px !important;
            height: 40px !important;
            cursor: pointer !important;
            display: none !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease !important;
        }
        
        #custom-expand-btn:hover {
            background-color: rgba(30, 41, 59, 0.7) !important;
            border-color: #258cf4 !important;
            box-shadow: 0 0 15px rgba(37, 140, 244, 0.5) !important;
        }
        
        #custom-expand-btn::before {
            content: '' !important;
            width: 8px !important;
            height: 8px !important;
            border-right: 2px solid #94a3b8 !important;
            border-bottom: 2px solid #94a3b8 !important;
            transform: rotate(-45deg) !important;
            margin-left: -2px !important;
        }
        
        #custom-expand-btn:hover::before {
            border-color: #ffffff !important;
        }
        /* --- PILOT CARD (Restored) --- */
        .profile-card {
            background: linear-gradient(135deg, rgba(30, 30, 40, 0.8), rgba(20, 20, 30, 0.9));
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 24px; /* Push settings down */
            margin-top: 10px;    /* Space from top */
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            position: relative;
            z-index: 1;
        }
        
        .profile-avatar {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 14px;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        }
        
        .profile-info {
            display: flex;
            flex-direction: column;
        }
        
        .profile-name {
            color: white;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: -0.5px;
        }
        
        .profile-badge {
            color: #4ade80; /* Green */
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 2px;
        }

        /* --- SIDEBAR CLOSE BUTTON POSITIONING --- */
        /* Note: Main positioning is in section 4, this section removed to avoid conflicts */

        /* ============================================ */
        /* 18. MATERIAL ICONS FIX                       */
        /* ============================================ */
        /* Fix for Material icons showing as text */
        [data-testid="stIconMaterial"] {
            font-family: 'Material Symbols Rounded', sans-serif !important;
            font-variation-settings:
                'FILL' 0,
                'wght' 400,
                'GRAD' 0,
                'opsz' 24;
            font-size: 24px !important;
            font-weight: normal !important;
            font-style: normal !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
            text-rendering: optimizeLegibility !important;
        }

        /* ============================================ */
        /* 19. INPUT ERROR STATES (Remove Red)          */
        /* ============================================ */
        /* Override Streamlit's default red error/invalid states */
        .stTextInput > div > div:invalid,
        .stNumberInput > div > div:invalid,
        .stSelectbox > div > div:invalid,
        .stTextArea > div > div:invalid {
            border-color: var(--border-color) !important;
            box-shadow: none !important;
        }
        
        /* Remove red borders on focus for invalid inputs */
        .stTextInput > div > div:focus-within:invalid,
        .stNumberInput > div > div:focus-within:invalid,
        .stSelectbox > div > div:focus-within:invalid,
        .stTextArea > div > div:focus-within:invalid {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Override any red helper text */
        [data-baseweb="form-control-caption"] {
            color: var(--text-secondary) !important;
        }
        
        /* Remove borders from outer number input containers - only inner input should have border */
        .stNumberInput,
        .stNumberInput > div {
            border: none !important;
            border-color: transparent !important;
            box-shadow: none !important;
        }
        
        /* Style just the baseweb input container (NOT the outer wrappers) */
        .stNumberInput [data-baseweb="input"],
        .stNumberInput [data-baseweb="base-input"] {
            border: 1px solid var(--border-color) !important;
            border-radius: 0.375rem !important;
            background-color: var(--bg-inner) !important;
        }
        
        .stNumberInput [data-baseweb="input"]:focus-within,
        .stNumberInput [data-baseweb="base-input"]:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Ensure number input buttons don't have red styling */
        .stNumberInput button {
            background: var(--bg-glass) !important;
            border-color: var(--border-color) !important;
            color: var(--text-primary) !important;
            border: none !important;
        }
        
        .stNumberInput button:hover {
            background: var(--bg-glass-hover) !important;
            color: var(--primary) !important;
        }
        
        /* Remove red from select/dropdown elements */
        [data-baseweb="select"] > div {
            border-color: var(--border-color) !important;
        }
        
        [data-baseweb="select"] > div:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Override any inline red colors from Streamlit */
        input::-webkit-outer-spin-button,
        input::-webkit-inner-spin-button {
            -webkit-appearance: none !important;
            margin: 0 !important;
        }
        
        /* Ensure step buttons maintain theme colors */
        [data-testid="stNumberInput-StepUp"],
        [data-testid="stNumberInput-StepDown"] {
            background: transparent !important;
            border: none !important;
            color: var(--text-secondary) !important;
        }
        
        [data-testid="stNumberInput-StepUp"]:hover,
        [data-testid="stNumberInput-StepDown"]:hover {
            color: var(--primary) !important;
        }
        
        /* ============================================ */
        /* 19B. SELECT SLIDER VALUE (Remove Red)        */
        /* ============================================ */
        /* Force the selected value text to be blue, not red */
        [data-testid="stSlider"] > div:first-child > div:first-child,
        [data-testid="stSlider"] > div > div:first-child > div {
            color: var(--primary) !important;
        }
        
        /* Target the value display span specifically */
        [data-testid="stSlider"] [data-baseweb="slider"] + div,
        [data-testid="stSlider"] > div > div > div:last-child {
            color: var(--primary) !important;
        }
        
        /* Override any inline style that sets color to red */
        [data-testid="stSlider"] span[style*="color"],
        [data-testid="stSlider"] div[style*="color"] {
            color: var(--primary) !important;
        }
        /* ============================================ */
        /* Pills in st.pills or st.radio with horizontal options */
        [data-testid="stPills"] button,
        .stPill,
        [data-baseweb="pill"] {
            background: var(--bg-inner) !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-secondary) !important;
            border-radius: 9999px !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stPills"] button:hover,
        .stPill:hover,
        [data-baseweb="pill"]:hover {
            background: rgba(37, 140, 244, 0.1) !important;
            border-color: var(--primary) !important;
            color: var(--text-primary) !important;
        }
        
        [data-testid="stPills"] button[aria-checked="true"],
        [data-testid="stPills"] button[aria-selected="true"],
        .stPill[aria-selected="true"],
        [data-baseweb="pill"][aria-selected="true"] {
            background: var(--primary) !important;
            border-color: var(--primary) !important;
            color: white !important;
        }

        /* ============================================ */
        /* 21. RADIO BUTTONS (Override Red)             */
        /* ============================================ */
        [data-testid="stRadio"] > div > label > div:first-child {
            border-color: var(--border-color) !important;
            background: var(--bg-inner) !important;
        }
        
        [data-testid="stRadio"] > div > label[data-checked="true"] > div:first-child {
            border-color: var(--primary) !important;
            background: var(--primary) !important;
        }
        
        [data-testid="stRadio"] > div > label[data-checked="true"] > div:first-child::after {
            background: white !important;
        }

        /* ============================================ */
        /* 22. GLOBAL RED OVERRIDE - For UI Elements    */
        /* ============================================ */
        /* Override Streamlit's default red accent in UI elements only.
           EXCLUDE: markdown content, headings, and user-styled text.
           This targets form elements, borders, and Streamlit widgets only. */
        
        /* Form inputs with red borders - convert to blue */
        [data-baseweb="input"][style*="rgb(255, 75, 75)"],
        [data-baseweb="input"][style*="#ff4b4b"],
        [data-baseweb="input"][style*="#ef4444"],
        [data-baseweb="textarea"][style*="rgb(255, 75, 75)"],
        [data-baseweb="textarea"][style*="#ff4b4b"],
        [data-baseweb="textarea"][style*="#ef4444"] {
            border-color: var(--primary) !important;
        }
        
        /* Toast/alert containers with red backgrounds - convert to blue */
        [data-testid="stToast"][style*="rgb(255, 75, 75)"],
        [data-testid="stToast"][style*="#ff4b4b"],
        .stAlert[style*="rgb(255, 75, 75)"],
        .stAlert[style*="#ff4b4b"] {
            background-color: rgba(37, 140, 244, 0.1) !important;
            border-color: var(--primary) !important;
        }
        
        /* Override Streamlit's default accent color in various places */
        [data-baseweb="input"]:focus,
        [data-baseweb="textarea"]:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Selectbox dropdown icon and focus states */
        [data-baseweb="select"] svg {
            color: var(--text-secondary) !important;
        }
        
        [data-baseweb="popover"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.5rem !important;
        }
        
        [data-baseweb="popover"] li:hover {
            background: rgba(37, 140, 244, 0.1) !important;
        }
        
        [data-baseweb="popover"] li[aria-selected="true"] {
            background: rgba(37, 140, 244, 0.2) !important;
        }

        /* ============================================ */
        /* 23. COMPREHENSIVE STREAMLIT ACCENT OVERRIDE  */
        /* ============================================ */
        /* Override all Streamlit theme accent colors */
        :root {
            --st-accent-color: #258cf4 !important;
        }
        
        /* Primary buttons everywhere */
        button[kind="primary"],
        button[data-testid="baseButton-primary"],
        [data-testid="stButton"] button[kind="primary"],
        .stButton button[kind="primary"] {
            background-color: var(--primary) !important;
            border-color: var(--primary) !important;
            color: white !important;
        }
        
        button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover,
        [data-testid="stButton"] button[kind="primary"]:hover {
            background-color: #1d72c4 !important;
            border-color: #1d72c4 !important;
        }
        
        /* All multiselect/tag elements */
        [data-baseweb="tag"] {
            background-color: rgba(37, 140, 244, 0.2) !important;
            border-color: rgba(37, 140, 244, 0.4) !important;
            color: var(--text-primary) !important;
        }
        
        [data-baseweb="tag"] span {
            color: var(--text-primary) !important;
        }
        
        /* All slider elements */
        [data-baseweb="slider"] [role="slider"] {
            background-color: var(--primary) !important;
            border-color: white !important;
        }
        
        [data-baseweb="slider"] > div > div:first-child {
            background: linear-gradient(90deg, #1d4ed8, var(--primary)) !important;
        }
        
        /* Date input clear button */
        [data-testid="stDateInput"] button {
            color: var(--text-secondary) !important;
            background: transparent !important;
            border: none !important;
        }
        
        [data-testid="stDateInput"] button:hover {
            color: var(--primary) !important;
        }
        
        /* Multiselect clear button */
        [data-testid="stMultiSelect"] button {
            color: var(--text-secondary) !important;
        }
        
        [data-testid="stMultiSelect"] button:hover {
            color: var(--primary) !important;
        }
        
        /* Number input increment/decrement */
        [data-testid="stNumberInput"] button {
            color: var(--text-secondary) !important;
            background: transparent !important;
        }
        
        [data-testid="stNumberInput"] button:hover {
            color: var(--primary) !important;
        }
        
        /* Override BaseWeb specific red accents */
        [data-baseweb="base-input"][aria-invalid="true"],
        [data-baseweb="input"][aria-invalid="true"] {
            border-color: var(--border-color) !important;
        }
        
        [data-baseweb="form-control"][data-invalid="true"] div {
            border-color: var(--border-color) !important;
        }
        
        /* ============================================ */
        /* CHAT MESSAGE STYLING                         */
        /* ============================================ */
        /* Chat input container - limit z-index so it doesn't block sidebar buttons */
        [data-testid="stChatInput"] {
            z-index: 100 !important;
        }
        
        /* The bottom container that holds chat input - also limit z-index */
        [data-testid="stBottom"],
        [data-testid="stBottomBlockContainer"],
        .stChatFloatingInputContainer,
        [data-testid="stBottom"] > div,
        [data-testid="stBottom"] > div > div {
            z-index: 100 !important;
        }
        
        /* Ensure all content in main area has lower z-index than sidebar buttons */
        [data-testid="stMain"] *,
        [data-testid="stVerticalBlock"] *,
        .stChatMessage *,
        [data-testid="stChatMessageContent"] * {
            z-index: auto;
        }
        
        /* Chat input container - REMOVE ALL RED BORDERS */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] [data-baseweb="base-input"],
        [data-testid="stChatInput"] [data-baseweb="input"],
        [data-testid="stChatInput"] [data-baseweb="input-container"] {
            background: var(--bg-glass) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0.75rem !important;
            backdrop-filter: blur(20px) !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        /* Remove inner borders */
        [data-testid="stChatInput"] [data-baseweb="base-input"] {
            border: none !important;
        }
        
        [data-testid="stChatInput"]:focus-within {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(37, 140, 244, 0.2) !important;
        }
        
        /* Remove ALL red/error styling from chat input */
        [data-testid="stChatInput"] *:focus,
        [data-testid="stChatInput"] *:focus-within,
        [data-testid="stChatInput"] *:active {
            border-color: var(--primary) !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        [data-testid="stChatInput"] textarea {
            background: transparent !important;
            color: var(--text-primary) !important;
            border: none !important;
            outline: none !important;
        }
        
        [data-testid="stChatInput"] textarea:focus {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        [data-testid="stChatInput"] button {
            background: var(--primary) !important;
            color: white !important;
            border: none !important;
            border-radius: 0.5rem !important;
        }
        
        [data-testid="stChatInput"] button:hover {
            background: #1d72c4 !important;
        }
        
        /* ============================================ */
        /* CHAT MESSAGE STYLING - PERFORMANCE LAB       */
        /* ============================================ */
        /* Chat message bubbles - sharp corners, solid borders */
        [data-testid="stChatMessage"],
        .stChatMessage {
            border-radius: 2px !important;
            padding: 1rem !important;
            backdrop-filter: none !important;
            margin-bottom: 0.5rem !important;
            box-shadow: none !important;
        }
        
        /* User messages - matte dark background */
        [data-testid="stChatMessage"][data-testid*="user"],
        .stChatMessage:has([data-testid="chatAvatarIcon-user"]),
        [data-testid="stChatMessage"]:has(img[alt="user"]) {
            background: #1A1C24 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Assistant messages - darker background with blue left accent */
        [data-testid="stChatMessage"][data-testid*="assistant"],
        .stChatMessage:has([data-testid="chatAvatarIcon-assistant"]),
        [data-testid="stChatMessage"]:has(img[alt="assistant"]) {
            background: #0E1117 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-left: 3px solid #007AFF !important;
        }
        
        /* Container holding chat messages - no card styling */
        [data-testid="stChatMessage"] > div,
        .stChatMessage > div,
        [data-testid="stChatMessageContent"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Container that wraps all chat messages - ensure no card effect */
        .stVerticalBlock:has([data-testid="stChatMessage"]) {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Chat avatar styling - remove default colored background */
        [data-testid="chatAvatarIcon-user"],
        [data-testid="chatAvatarIcon-assistant"] {
            background: transparent !important;
        }
        
        /* Avatar image sizing */
        [data-testid="stChatMessage"] img[data-testid="chatAvatarIcon-user"],
        [data-testid="stChatMessage"] img[data-testid="chatAvatarIcon-assistant"],
        .stChatMessage img {
            width: 40px !important;
            height: 40px !important;
            border-radius: 50% !important;
        }
        
        </style>
    """, unsafe_allow_html=True)
    
    # Persistent expand button - injects into parent document
    import streamlit.components.v1 as components
    components.html("""
        <script>
            (function() {
                // Run in parent window context
                const parentDoc = window.parent.document;
                
                // === FIX SLIDER STYLES ===
                function fixSliderStyles() {
                    const sliders = parentDoc.querySelectorAll('[data-testid="stSlider"]');
                    sliders.forEach(slider => {
                        // Find all divs and replace any gradient with solid gray
                        const divs = slider.querySelectorAll('div');
                        divs.forEach(div => {
                            // Check inline styles
                            const inlineBg = div.style.background || div.style.backgroundImage || '';
                            
                            // Also check computed styles (catches CSS-applied gradients)
                            const computedBg = window.parent.getComputedStyle(div).background || '';
                            
                            // Check for any gradient or red color in either
                            if (inlineBg.includes('linear-gradient') || inlineBg.includes('rgb(255, 75, 75)') ||
                                computedBg.includes('linear-gradient') || computedBg.includes('rgb(255, 75, 75)')) {
                                // Make track solid gray
                                div.style.setProperty('background', 'rgba(100, 116, 139, 0.4)', 'important');
                            }
                            
                            // Fix red text color
                            const computedColor = window.parent.getComputedStyle(div).color;
                            if (computedColor === 'rgb(255, 75, 75)') {
                                div.style.setProperty('color', '#258cf4', 'important');
                            }
                        });
                        
                        // Fix thumb value text specifically
                        const thumbValues = slider.querySelectorAll('[data-testid="stThumbValue"]');
                        thumbValues.forEach(tv => {
                            tv.style.setProperty('color', '#258cf4', 'important');
                            tv.style.setProperty('background', 'transparent', 'important');
                        });
                        
                        // Ensure thumb stays blue
                        const thumbs = slider.querySelectorAll('[role="slider"]');
                        thumbs.forEach(thumb => {
                            thumb.style.setProperty('background-color', '#258cf4', 'important');
                        });
                    });
                }
                
                // Run fix periodically
                setInterval(fixSliderStyles, 100);
                
                // Initial run
                fixSliderStyles();
                
                // Force remove old button to recreate with fresh event handlers
                const oldBtn = parentDoc.getElementById('saker-expand-btn');
                if (oldBtn) oldBtn.remove();
                
                // Also remove debug element
                const oldDebug = parentDoc.getElementById('saker-debug');
                if (oldDebug) oldDebug.remove();
                
                // Create or get expand button
                function ensureExpandButton() {
                    let btn = parentDoc.getElementById('saker-expand-btn');
                    if (!btn) {
                        btn = parentDoc.createElement('div');
                        btn.id = 'saker-expand-btn';
                        btn.style.cssText = `
                            position: fixed;
                            top: 50%;
                            left: 14px;
                            transform: translateY(-50%);
                            z-index: 2147483647;
                            background-color: #1E293B;
                            border: 1px solid rgba(255, 255, 255, 0.08);
                            border-radius: 50%;
                            width: 28px;
                            height: 28px;
                            cursor: pointer;
                            display: none;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                            transition: all 0.2s ease;
                            pointer-events: auto;
                        `;
                        
                        // Create chevron - points right
                        const chevron = parentDoc.createElement('div');
                        chevron.style.cssText = `
                            width: 6px;
                            height: 6px;
                            border-right: 2px solid #94a3b8;
                            border-bottom: 2px solid #94a3b8;
                            transform: rotate(-45deg);
                            margin-left: -2px;
                        `;
                        btn.appendChild(chevron);
                        
                        // Hover effects
                        btn.onmouseenter = () => {
                            btn.style.backgroundColor = 'rgba(30, 41, 59, 0.9)';
                            btn.style.borderColor = '#258cf4';
                            btn.style.boxShadow = '0 0 12px rgba(37, 140, 244, 0.5)';
                            chevron.style.borderColor = '#ffffff';
                        };
                        btn.onmouseleave = () => {
                            btn.style.backgroundColor = '#1E293B';
                            btn.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                            btn.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
                            chevron.style.borderColor = '#94a3b8';
                        };
                        
                        // Click handler - try multiple selectors to find working toggle
                        btn.onclick = (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const selectors = [
                                '[data-testid="stSidebarCollapseButton"] button',
                                '[data-testid="collapsedControl"] button',
                                'header[data-testid="stHeader"] button',
                                'button[kind="headerNoPadding"]'
                            ];
                            
                            for (const selector of selectors) {
                                const toggleBtn = parentDoc.querySelector(selector);
                                if (toggleBtn) {
                                    toggleBtn.click();
                                    break;
                                }
                            }
                        };
                        
                        parentDoc.body.appendChild(btn);
                    }
                    return btn;
                }
                
                // Check sidebar state and show/hide button
                function updateButton() {
                    let sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
                    if (!sidebar) {
                        sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
                    }
                    
                    const btn = ensureExpandButton();
                    if (btn) {
                        let isCollapsed = false;
                        
                        if (sidebar) {
                            isCollapsed = sidebar.getAttribute('aria-expanded') === 'false';
                        } else {
                            const sidebarContent = parentDoc.querySelector('[data-testid="stSidebarContent"]');
                            isCollapsed = !sidebarContent || sidebarContent.offsetWidth === 0;
                        }
                        
                        btn.style.display = isCollapsed ? 'flex' : 'none';
                    }
                }
                
                // Run periodically to handle Streamlit re-renders
                setInterval(updateButton, 200);
                updateButton();
                
                // Also observe sidebar changes with multiple fallbacks
                function setupObserver() {
                    let sidebar = parentDoc.querySelector('[data-testid="stSidebar"]');
                    if (!sidebar) {
                        sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
                    }
                    
                    if (sidebar) {
                        const observer = new MutationObserver(updateButton);
                        observer.observe(sidebar, { attributes: true, attributeFilter: ['aria-expanded'] });
                    } else {
                        // Retry after a short delay
                        setTimeout(setupObserver, 500);
                    }
                }
                setupObserver();
            })();
        </script>
    """, height=0)
