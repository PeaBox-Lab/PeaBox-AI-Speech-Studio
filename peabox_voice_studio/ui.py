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
  --pb-navy:#13213c; --pb-blue:#235ea8; --pb-cyan:#3aa7c4; --pb-ink:#172033;
  --pb-muted:#667085; --pb-bg:#f4f7fb; --pb-card:#ffffff; --pb-border:#d9e2ef;
  --pb-good:#147d64; --pb-warn:#b54708; --pb-bad:#b42318;
}
.stApp { background:var(--pb-bg); color:var(--pb-ink); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#101b31 0%,#172a4d 100%); border-right:1px solid #23395f; }
[data-testid="stSidebar"] * { color:#eef4ff; }
[data-testid="stSidebar"] .stRadio label, [data-testid="stSidebar"] .stSelectbox label { font-weight:600; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background:#1d3359; border-color:#36517a; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding:.35rem .45rem; border-radius:7px; margin:.08rem 0; }
[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:#243d67; }
.block-container { max-width:1500px; padding-top:1.2rem; padding-bottom:3rem; }
.pb-topbar { background:linear-gradient(120deg,var(--pb-navy),#234a7d); border-radius:14px; padding:1.25rem 1.5rem; color:white; margin-bottom:1rem; box-shadow:0 8px 24px rgba(19,33,60,.12); }
.pb-eyebrow { color:#9fd8e8; font-size:.72rem; text-transform:uppercase; letter-spacing:.12em; font-weight:700; margin-bottom:.35rem; }
.pb-title { font-size:1.75rem; line-height:1.15; font-weight:720; margin:0; }
.pb-subtitle { color:#d9e7f7; margin-top:.45rem; max-width:900px; font-size:.94rem; }
.pb-card { background:var(--pb-card); border:1px solid var(--pb-border); border-radius:12px; padding:1rem 1.1rem; min-height:110px; box-shadow:0 3px 12px rgba(22,45,78,.05); }
.pb-card-label { color:var(--pb-muted); text-transform:uppercase; letter-spacing:.06em; font-size:.7rem; font-weight:700; }
.pb-card-value { color:var(--pb-navy); font-size:1.55rem; font-weight:750; margin:.2rem 0; }
.pb-card-note { color:var(--pb-muted); font-size:.8rem; }
.pb-section { border-left:4px solid var(--pb-blue); padding:.15rem 0 .15rem .75rem; margin:1.3rem 0 .7rem; }
.pb-section-title { font-weight:720; color:var(--pb-navy); font-size:1.05rem; }
.pb-section-note { color:var(--pb-muted); font-size:.82rem; margin-top:.15rem; }
.pb-callout { background:#edf5ff; border:1px solid #c8dcf5; border-radius:10px; padding:.8rem 1rem; color:#25446e; margin:.5rem 0 1rem; }
.pb-status { display:inline-block; padding:.18rem .55rem; border-radius:999px; font-weight:700; font-size:.72rem; }
.pb-status.good { color:#096b53; background:#dff6ee; }.pb-status.warn { color:#934b08; background:#fff1dc; }.pb-status.bad { color:#9b241c; background:#fee4e2; }.pb-status.neutral { color:#344054; background:#eaecf0; }
.pb-step { background:#fff; border:1px solid var(--pb-border); border-radius:10px; padding:.8rem 1rem; margin-bottom:.45rem; }
.pb-step strong { color:var(--pb-navy); }
[data-testid="stMetric"] { background:white; border:1px solid var(--pb-border); border-radius:11px; padding:.65rem .8rem; box-shadow:0 2px 8px rgba(22,45,78,.04); }
[data-testid="stExpander"] { background:white; border:1px solid var(--pb-border); border-radius:10px; }
.stButton > button, .stDownloadButton > button { border-radius:8px; font-weight:650; }
.stButton > button[kind="primary"] { background:var(--pb-blue); border-color:var(--pb-blue); }
hr { border-color:var(--pb-border); }
</style>
""", unsafe_allow_html=True)


def sidebar_navigation(version: str, project: Any = None) -> str:
    st.sidebar.markdown('<div style="font-size:1.12rem;font-weight:750;margin:.2rem 0 .1rem">PeaBox Voice Studio</div>', unsafe_allow_html=True)
    st.sidebar.caption(f"Enterprise workspace · v{version}")
    group_names = list(NAVIGATION)
    default_group = st.session_state.get("nav_group", "Overview")
    if default_group not in group_names:
        default_group = "Overview"
    group = st.sidebar.selectbox("Workspace area", group_names, index=group_names.index(default_group), key="nav_group")
    entries = NAVIGATION[group]
    labels = [f"{icon}  {label}" for label, _, icon in entries]
    selected_label = st.sidebar.radio("Navigation", labels, key=f"nav_page_{group}")
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
