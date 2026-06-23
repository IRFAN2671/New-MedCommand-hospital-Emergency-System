"""
MedCommand — Professional Healthcare Dashboard CSS
Supports light and dark themes via Streamlit session state.
"""

LIGHT_THEME = {
    "bg": "#f0f4f8",
    "surface": "#ffffff",
    "surface2": "#f8fafc",
    "border": "#e2e8f0",
    "text": "#0f172a",
    "text2": "#475569",
    "text3": "#94a3b8",
    "accent": "#0ea5e9",
    "green": "#10b981",
    "red": "#ef4444",
    "amber": "#f59e0b",
    "purple": "#8b5cf6",
    "teal": "#14b8a6",
}

DARK_THEME = {
    "bg": "#0a0f1a",
    "surface": "#111827",
    "surface2": "#1e2a3a",
    "border": "#1e3a5f",
    "text": "#f1f5f9",
    "text2": "#94a3b8",
    "text3": "#475569",
    "accent": "#38bdf8",
    "green": "#34d399",
    "red": "#f87171",
    "amber": "#fbbf24",
    "purple": "#a78bfa",
    "teal": "#2dd4bf",
}


def get_dashboard_css(dark: bool = False) -> str:
    t = DARK_THEME if dark else LIGHT_THEME
    return f"""
<style>
/* ── MedCommand Dashboard v2.0 ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --bg: {t['bg']};
    --surface: {t['surface']};
    --surface2: {t['surface2']};
    --border: {t['border']};
    --text: {t['text']};
    --text2: {t['text2']};
    --text3: {t['text3']};
    --accent: {t['accent']};
    --green: {t['green']};
    --red: {t['red']};
    --amber: {t['amber']};
    --purple: {t['purple']};
    --teal: {t['teal']};
}}

.stApp {{
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}}

/* ── Header Bar ── */
.medcmd-header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 999;
    margin: -1rem -1rem 1rem;
}}

.medcmd-logo {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 16px;
    color: var(--accent);
}}

.medcmd-logo-icon {{
    width: 32px;
    height: 32px;
    background: var(--accent);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
}}

/* ── KPI Cards ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 16px;
}}

.kpi-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}}

.kpi-card:hover {{
    transform: translateY(-2px);
}}

.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}}

.kpi-card.blue::before {{ background: var(--accent); }}
.kpi-card.green::before {{ background: var(--green); }}
.kpi-card.amber::before {{ background: var(--amber); }}
.kpi-card.red::before {{ background: var(--red); }}
.kpi-card.purple::before {{ background: var(--purple); }}
.kpi-card.teal::before {{ background: var(--teal); }}

.kpi-label {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text3);
    margin-bottom: 8px;
}}

.kpi-value {{
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 4px;
}}

.kpi-value.blue {{ color: var(--accent); }}
.kpi-value.green {{ color: var(--green); }}
.kpi-value.amber {{ color: var(--amber); }}
.kpi-value.red {{ color: var(--red); }}
.kpi-value.purple {{ color: var(--purple); }}
.kpi-value.teal {{ color: var(--teal); }}

.kpi-delta {{
    font-size: 12px;
    color: var(--text2);
    display: flex;
    align-items: center;
    gap: 4px;
}}

.kpi-delta.up {{ color: var(--green); }}
.kpi-delta.dn {{ color: var(--red); }}

.kpi-bar {{
    height: 4px;
    background: var(--surface2);
    border-radius: 4px;
    margin-top: 8px;
    overflow: hidden;
}}

.kpi-bar-fill {{
    height: 100%;
    border-radius: 4px;
    transition: width 0.8s ease;
}}

/* ── Panel Cards ── */
.panel-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
}}

.panel-title {{
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text3);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

/* ── Status Badges ── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}}

.badge-green {{ background: rgba(16,185,129,.15); color: var(--green); }}
.badge-red {{ background: rgba(239,68,68,.15); color: var(--red); }}
.badge-amber {{ background: rgba(245,158,11,.15); color: var(--amber); }}
.badge-blue {{ background: rgba(14,165,233,.15); color: var(--accent); }}
.badge-purple {{ background: rgba(139,92,246,.15); color: var(--purple); }}
.badge-teal {{ background: rgba(20,184,166,.15); color: var(--teal); }}

/* ── Alert Banners ── */
.alert-banner {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 16px;
    border-radius: 8px;
    margin-bottom: 10px;
    border: 1px solid transparent;
    font-size: 13px;
}}

.alert-crit {{
    background: rgba(239,68,68,.1);
    border-color: var(--red);
    color: var(--red);
}}

.alert-warn {{
    background: rgba(245,158,11,.1);
    border-color: var(--amber);
    color: var(--amber);
}}

.alert-info {{
    background: rgba(14,165,233,.1);
    border-color: var(--accent);
    color: var(--accent);
}}

/* ── Doctor Cards ── */
.doctor-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
}}

.doctor-card {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
}}

.doctor-avatar {{
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 10px;
}}

.doctor-name {{
    font-weight: 600;
    font-size: 14px;
    color: var(--text);
    margin-bottom: 2px;
}}

.doctor-dept {{
    font-size: 12px;
    color: var(--text2);
    margin-bottom: 8px;
}}

/* ── Queue Rows ── */
.queue-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    margin-bottom: 6px;
    border-left: 4px solid transparent;
}}

.queue-critical {{ background: rgba(239,68,68,.08); border-left-color: var(--red); }}
.queue-urgent {{ background: rgba(245,158,11,.08); border-left-color: var(--amber); }}
.queue-normal {{ background: var(--surface2); border-left-color: var(--text3); }}

/* ── Activity Feed ── */
.feed-container {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 320px;
    overflow-y: auto;
}}

.feed-item {{
    display: flex;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 6px;
    background: var(--surface2);
    border-left: 3px solid transparent;
    font-size: 12px;
}}

.feed-info {{ border-left-color: var(--accent); }}
.feed-warn {{ border-left-color: var(--amber); }}
.feed-crit {{ border-left-color: var(--red); }}
.feed-ok {{ border-left-color: var(--green); }}

/* ── ML Model Cards ── */
.ml-card {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
}}

.ml-bar {{
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    margin-top: 8px;
    overflow: hidden;
}}

.ml-bar-fill {{
    height: 100%;
    border-radius: 4px;
    transition: width 1s ease;
}}

/* ── Progress Bar ── */
.progress-bar {{
    height: 6px;
    background: var(--surface2);
    border-radius: 4px;
    overflow: hidden;
}}

.progress-fill {{
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}}

/* ── Scrollbars ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}

/* ── Status dot ── */
.status-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}}

.dot-green {{ background: var(--green); }}
.dot-amber {{ background: var(--amber); }}
.dot-red {{ background: var(--red); }}
.dot-blue {{ background: var(--accent); }}

/* ── Live pulse ── */
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(0.8); }}
}}

.pulse-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    animation: pulse 1.5s ease infinite;
    margin-right: 6px;
}}

/* ── Tabs override ── */
.stTabs [data-baseweb="tab-list"] {{
    background: var(--surface2) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important;
    gap: 2px !important;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 6px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text2) !important;
    padding: 6px 14px !important;
}}

.stTabs [aria-selected="true"] {{
    background: var(--surface) !important;
    color: var(--text) !important;
}}

/* ── Sidebar ── */
.css-1d391kg, [data-testid="stSidebar"] {{
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}}

/* ── Metrics ── */
[data-testid="metric-container"] {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
}}

/* ── Footer ── */
.medcmd-footer {{
    text-align: center;
    padding: 16px;
    font-size: 11px;
    color: var(--text3);
    border-top: 1px solid var(--border);
    margin-top: 24px;
}}

/* ── Incident cards ── */
.incident-card {{
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 10px;
}}

/* ── Log rows ── */
.log-row {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 7px 0;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
}}

/* ── Heatmap ── */
.heatmap-cell {{
    display: inline-block;
    width: 28px;
    height: 28px;
    border-radius: 4px;
    margin: 2px;
    cursor: pointer;
    transition: opacity 0.2s;
}}

/* ── Animations ── */
@keyframes slideIn {{
    from {{ transform: translateX(100%); opacity: 0; }}
    to {{ transform: translateX(0); opacity: 1; }}
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(-6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

.fade-in {{ animation: fadeIn 0.3s ease forwards; }}
</style>
"""
