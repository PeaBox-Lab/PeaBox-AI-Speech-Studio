from html import escape
from typing import Any

import streamlit as st

NAVIGATION = {
    "Overview": [
        ("Executive Dashboard", "Dashboard", "▦"),
        ("Project Workspace", "Projects", "▣"),
    ],
    "Production": [
        ("Script Editor", "Script Blocks", "✎"),
        ("Speech Generator", "Create Speech", "◉"),
        ("Batch Jobs", "Batch Production", "⇄"),
        ("Timeline Studio", "Timeline Studio", "≡"),
    ],
    "Audio & Quality": [
        ("Voice Library", "Voice Library", "◫"),
        ("Quality Studio", "Quality Studio", "✓"),
        ("Audio Quality Lab", "Audio Quality Lab", "∿"),
        ("Transcription Studio", "Transcription", "▤"),
    ],
    "Administration": [
        ("Governance Center", "Governance", "◆"),
        ("Approval Queue", "Approvals", "✓"),
        ("Provider Setup", "Provider Setup", "⚙"),
        ("System Check", "System Check", "◇"),
        ("Activity & History", "Render History", "◷"),
    ],
    "Support": [
        ("Roadmap & Help", "Roadmap & Help", "?"),
    ],
}

PAGE_META = {
    "Dashboard": ("Executive Dashboard", "Portfolio status, production readiness, and recommended next actions.", "Overview"),
    "Projects": ("Project Workspace", "Create, open, import, export, and maintain portable production projects.", "Overview"),
    "Script Blocks": ("Script Editor", "Structure the master script into reusable, provider-aware production blocks.", "Production"),
    "Create Speech": ("Speech Generator", "Generate and review individual local voice outputs.", "Production"),
    "Batch Production": ("Batch Jobs", "Validate, queue, resume, retry, cancel, and package multi-provider production jobs.", "Production"),
    "Timeline Studio": ("Timeline Studio", "Arrange durable WAV clips non-destructively and export a mixed production master.", "Production"),
    "Voice Library": ("Voice Library", "Search available local and session-discovered cloud voices.", "Audio & Quality"),
    "Quality Studio": ("Quality Studio", "Manage pronunciation rules, pause controls, and processed-text previews.", "Audio & Quality"),
    "Audio Quality Lab": ("Audio Quality Lab", "Analyze WAV files, create normalized or trimmed copies, and compare voices.", "Audio & Quality"),
    "Transcription": ("Transcription Studio", "Transcribe, edit, validate, save, and export timestamped media text.", "Audio & Quality"),
    "Governance": ("Governance Center", "Manage ownership, workflow state, review comments, decisions, and project risk.", "Administration"),
    "Approvals": ("Approval Queue", "Request, decide, and review local approval attestations and workflow gates.", "Administration"),
    "Provider Setup": ("Provider Setup", "Configure session-only cloud credentials and discover provider voices.", "Administration"),
    "System Check": ("System Check", "Review runtime, media, model, and storage readiness.", "Administration"),
    "Render History": ("Activity & History", "Review project renders, timeline exports, jobs, comparisons, and saved transcripts.", "Administration"),
    "Roadmap & Help": ("Roadmap & Help", "Review delivered capabilities, planned architecture, and operating guidance.", "Support"),
}


def inject_corporate_theme() -> None:
    st.markdown("""
<style>
:root {
  --pb-navy:#13213c; --pb-navy-2:#1b3155; --pb-blue:#2f6fbb; --pb-blue-active:#316da8;
  --pb-cyan:#55bed6; --pb-ink:#172033; --pb-muted:#667085; --pb-bg:#f3f6fa;
  --pb-card:#ffffff; --pb-border:#d6e0ec; --pb-sidebar-text:#edf5ff;
  --pb-sidebar-muted:#b9c8dc; --pb-sidebar-control:#203b64; --pb-sidebar-border:#49698f;
  --pb-good:#147d64; --pb-warn:#b54708; --pb-bad:#b42318;
}
html, body, [data-testid="stAppViewContainer"] { overflow-x:hidden; }
.stApp { background:var(--pb-bg); color:var(--pb-ink); }
[data-testid="stHeader"] { background:rgba(243,246,250,.94); backdrop-filter:blur(8px); }
[data-testid="stToolbar"] { right:.75rem; }
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#101b31 0%,#172a4d 55%,#142441 100%);
  border-right:1px solid #2c466d;
  min-width:17rem;
}
[data-testid="stSidebarContent"] { padding-top:.75rem; overflow-y:auto; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color:var(--pb-sidebar-text); }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color:var(--pb-sidebar-muted)!important; }
/* Explicit select styling prevents inherited white text on Streamlit's default white control. */
[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  background:var(--pb-sidebar-control)!important;
  border:1px solid var(--pb-sidebar-border)!important;
  color:#ffffff!important;
  min-height:2.55rem;
  box-shadow:none!important;
}
[data-testid="stSidebar"] div[data-baseweb="select"] span,
[data-testid="stSidebar"] div[data-baseweb="select"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] svg {
  color:#ffffff!important; fill:#ffffff!important; -webkit-text-fill-color:#ffffff!important;
}
[data-testid="stSidebar"] div[data-baseweb="select"]:focus-within > div {
  border-color:#83c8e3!important; box-shadow:0 0 0 2px rgba(85,190,214,.22)!important;
}
/* Popovers render outside the sidebar and need dark text on their light surface. */
div[data-baseweb="popover"] ul[role="listbox"] { background:#ffffff!important; border:1px solid var(--pb-border); }
div[data-baseweb="popover"] li[role="option"],
div[data-baseweb="popover"] li[role="option"] span { color:var(--pb-ink)!important; -webkit-text-fill-color:var(--pb-ink)!important; }
div[data-baseweb="popover"] li[role="option"]:hover { background:#edf4fc!important; }
[data-testid="stSidebar"] div[role="radiogroup"] { gap:.2rem; }
[data-testid="stSidebar"] div[role="radiogroup"] label {
  min-height:2.35rem; padding:.42rem .62rem; border-radius:8px; margin:0;
  border:1px solid transparent; transition:background .14s ease,border-color .14s ease,transform .14s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:#243d67; border-color:#36557e; transform:translateX(1px); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
  background:linear-gradient(90deg,#2b659f,#28588f)!important;
  border-color:#69a7d3!important;
  box-shadow:inset 3px 0 0 #7fdbeb,0 4px 12px rgba(0,0,0,.14);
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color:#ffffff!important; font-weight:720; }
[data-testid="stSidebar"] div[role="radiogroup"] input { accent-color:#72d4e5; }
[data-testid="stSidebar"] hr { border-color:#385374; margin:.85rem 0; }
.block-container {
  width:100%; max-width:1440px; box-sizing:border-box;
  padding:3.35rem 2.25rem 4rem!important;
}
.pb-topbar {
  width:100%; max-width:100%; box-sizing:border-box; overflow:hidden;
  background:linear-gradient(120deg,var(--pb-navy),#234a7d 68%,#26638d);
  border:1px solid rgba(147,190,226,.22); border-radius:14px;
  padding:1.35rem 1.55rem; color:white; margin:.2rem 0 1.15rem;
  box-shadow:0 8px 24px rgba(19,33,60,.13); position:relative;
}
.pb-topbar::after {
  content:""; position:absolute; right:-3rem; top:-5rem; width:15rem; height:15rem;
  border-radius:50%; background:radial-gradient(circle,rgba(85,190,214,.2),rgba(85,190,214,0) 70%); pointer-events:none;
}
.pb-eyebrow { color:#aee3ef; font-size:.72rem; text-transform:uppercase; letter-spacing:.12em; font-weight:750; margin-bottom:.38rem; overflow-wrap:anywhere; }
.pb-title { font-size:clamp(1.45rem,2.1vw,1.85rem); line-height:1.18; font-weight:750; margin:0; overflow-wrap:anywhere; }
.pb-subtitle { color:#dceafb; margin-top:.48rem; max-width:920px; font-size:.94rem; line-height:1.45; overflow-wrap:anywhere; }
.pb-card { background:var(--pb-card); border:1px solid var(--pb-border); border-radius:12px; padding:1rem 1.1rem; min-height:110px; box-shadow:0 3px 12px rgba(22,45,78,.05); box-sizing:border-box; }
.pb-card-label { color:var(--pb-muted); text-transform:uppercase; letter-spacing:.06em; font-size:.7rem; font-weight:700; }
.pb-card-value { color:var(--pb-navy); font-size:1.55rem; font-weight:750; margin:.2rem 0; overflow-wrap:anywhere; }
.pb-card-note { color:var(--pb-muted); font-size:.8rem; line-height:1.35; }
.pb-section { border-left:4px solid var(--pb-blue); padding:.15rem 0 .15rem .75rem; margin:1.3rem 0 .7rem; }
.pb-section-title { font-weight:720; color:var(--pb-navy); font-size:1.05rem; }
.pb-section-note { color:var(--pb-muted); font-size:.82rem; margin-top:.15rem; }
.pb-callout { background:#edf5ff; border:1px solid #c8dcf5; border-radius:10px; padding:.8rem 1rem; color:#25446e; margin:.5rem 0 1rem; }
.pb-nav-label { color:#9fb3cc; font-size:.66rem; font-weight:750; letter-spacing:.12em; margin:.35rem 0 .3rem; }
.pb-status { display:inline-block; padding:.2rem .58rem; border-radius:999px; font-weight:750; font-size:.69rem; letter-spacing:.025em; }
.pb-status.good { color:#096b53; background:#dff6ee; }.pb-status.warn { color:#934b08; background:#fff1dc; }.pb-status.bad { color:#9b241c; background:#fee4e2; }.pb-status.neutral { color:#344054; background:#eaecf0; }
[data-testid="stSidebar"] .pb-status.neutral { color:#e7eef8; background:#344d70; border:1px solid #577397; }
[data-testid="stSidebar"] .pb-status.good { color:#c9fff0; background:#13654f; border:1px solid #27876e; }
.pb-step { background:#fff; border:1px solid var(--pb-border); border-radius:10px; padding:.8rem 1rem; margin-bottom:.45rem; min-height:100px; box-sizing:border-box; }
.pb-step strong { color:var(--pb-navy); }
[data-testid="stMetric"] { background:white; border:1px solid var(--pb-border); border-radius:11px; padding:.65rem .8rem; box-shadow:0 2px 8px rgba(22,45,78,.04); }
[data-testid="stExpander"] { background:white; border:1px solid var(--pb-border); border-radius:10px; overflow:hidden; }
[data-testid="stForm"], [data-testid="stDataFrame"], [data-testid="stFileUploader"] { max-width:100%; }
.stButton > button, .stDownloadButton > button { border-radius:8px; font-weight:650; min-height:2.35rem; }
.stButton > button[kind="primary"] { background:var(--pb-blue); border-color:var(--pb-blue); }
hr { border-color:var(--pb-border); }
@media (max-width:1100px) {
  .block-container { padding:3.15rem 1.35rem 3rem!important; }
  .pb-topbar { padding:1.15rem 1.2rem; }
  [data-testid="stHorizontalBlock"] { gap:.65rem; }
}
@media (max-width:760px) {
  .block-container { padding:3rem .85rem 2.5rem!important; }
  .pb-topbar { border-radius:11px; margin-top:.1rem; }
  .pb-subtitle { font-size:.87rem; }
  .pb-card,.pb-step { min-height:auto; }
  [data-testid="column"] { min-width:100%!important; width:100%!important; }
}
</style>
""", unsafe_allow_html=True)


def sidebar_navigation(version: str, project: Any = None) -> str:
    st.sidebar.markdown('<div style="font-size:1.12rem;font-weight:750;margin:.2rem 0 .1rem">PeaBox Voice Studio</div>', unsafe_allow_html=True)
    st.sidebar.caption(f"Enterprise workspace · v{version}")
    group_names = list(NAVIGATION)
    default_group = st.session_state.get("nav_group", "Overview")
    if default_group not in group_names:
        default_group = "Overview"
    st.sidebar.markdown('<div class="pb-nav-label">WORKSPACE AREA</div>', unsafe_allow_html=True)
    group = st.sidebar.selectbox("Workspace area", group_names, index=group_names.index(default_group), key="nav_group", label_visibility="collapsed")
    entries = NAVIGATION[group]
    labels = [f"{icon}  {label}" for label, _, icon in entries]
    st.sidebar.markdown('<div class="pb-nav-label" style="margin-top:.8rem">SCREENS</div>', unsafe_allow_html=True)
    selected_label = st.sidebar.radio("Navigation", labels, key=f"nav_page_{group}", label_visibility="collapsed")
    selected_index = labels.index(selected_label)
    page = entries[selected_index][1]
    st.sidebar.divider()
    if project:
        st.sidebar.markdown(f'<span class="pb-status good">ACTIVE PROJECT</span><div style="font-weight:700;margin-top:.4rem">{escape(project.name)}</div>', unsafe_allow_html=True)
        st.sidebar.caption(f"{len(project.blocks)} script blocks · {len(project.settings.get('audio_clips', []))} timeline clips")
    else:
        st.sidebar.markdown('<span class="pb-status neutral">NO ACTIVE PROJECT</span>', unsafe_allow_html=True)
        st.sidebar.caption("Open or create a project from Overview.")
    return page


def page_header(page: str, version: str, project: Any = None) -> None:
    title, subtitle, group = PAGE_META.get(page, (page, "", "Workspace"))
    context = f" · {escape(project.name)}" if project else ""
    st.markdown(
        f'<div class="pb-topbar"><div class="pb-eyebrow">{escape(group)} · PeaBox {escape(version)}{context}</div>'
        f'<div class="pb-title">{escape(title)}</div><div class="pb-subtitle">{escape(subtitle)}</div></div>',
        unsafe_allow_html=True,
    )


def section(title: str, note: str = "") -> None:
    st.markdown(f'<div class="pb-section"><div class="pb-section-title">{escape(title)}</div><div class="pb-section-note">{escape(note)}</div></div>', unsafe_allow_html=True)


def kpi_card(label: str, value: str, note: str = "") -> None:
    st.markdown(f'<div class="pb-card"><div class="pb-card-label">{escape(label)}</div><div class="pb-card-value">{escape(str(value))}</div><div class="pb-card-note">{escape(note)}</div></div>', unsafe_allow_html=True)


def callout(text: str) -> None:
    st.markdown(f'<div class="pb-callout">{escape(text)}</div>', unsafe_allow_html=True)


def status_badge(text: str, tone: str = "neutral") -> str:
    tone = tone if tone in {"good", "warn", "bad", "neutral"} else "neutral"
    return f'<span class="pb-status {tone}">{escape(text)}</span>'


def workflow_step(number: int, title: str, note: str) -> None:
    st.markdown(f'<div class="pb-step"><strong>{number}. {escape(title)}</strong><br><span style="color:#667085;font-size:.84rem">{escape(note)}</span></div>', unsafe_allow_html=True)
