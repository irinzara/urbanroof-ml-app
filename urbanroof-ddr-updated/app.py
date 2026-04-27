"""
app.py  —  UrbanRoof DDR Report Generator
Run: streamlit run app.py
API key loaded from .streamlit/secrets.toml — users never paste it.
"""

import streamlit as st
import os
import time
from extractor import extract_all
from generator import generate_ddr_text_only, generate_ddr_with_vision, generate_pdf

# ── PAGE CONFIG ──────────────────────────────
st.set_page_config(
    page_title="UrbanRoof DDR Generator",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── LOAD API KEYS FROM SECRETS (with fallback support) ────────────────
def _load_api_keys():
    keys = []
    for var in ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]:
        try:
            val = st.secrets[var]
            if val: keys.append(val)
        except Exception:
            val = os.environ.get(var, "")
            if val: keys.append(val)
    return keys

GEMINI_API_KEYS = _load_api_keys()
GEMINI_API_KEY  = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else ""

# ── CSS ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, .stApp {
    background-color: #0a0a0f !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header,
[data-testid="stDeployButton"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="collapsedControl"],
section[data-testid="stSidebar"] { display: none !important; }

.block-container { max-width: 1100px !important; padding: 2rem 2rem 4rem !important; }

.ur-header {
    position: relative;
    background: linear-gradient(135deg, #0e0e18 0%, #12121f 50%, #0a0a14 100%);
    border: 1px solid rgba(245,166,35,0.2);
    border-radius: 20px;
    padding: 3rem 2.5rem 2.5rem;
    margin-bottom: 2.5rem;
    overflow: hidden;
}
.ur-header::before {
    content: '';
    position: absolute; top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(245,166,35,0.12) 0%, transparent 70%);
}
.ur-badge {
    display: inline-block;
    background: rgba(245,166,35,0.12);
    border: 1px solid rgba(245,166,35,0.35);
    color: #f5a623;
    font-size: 0.72rem; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 0.3rem 0.9rem; border-radius: 100px; margin-bottom: 1.2rem;
}
.ur-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem; font-weight: 800;
    color: #f0ece4; margin: 0 0 0.6rem 0;
    line-height: 1.1; letter-spacing: -0.02em;
}
.ur-title span { background: linear-gradient(90deg, #f5a623, #ffcc70); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.ur-subtitle { color: #888; font-size: 1rem; font-weight: 300; margin: 0; }
.ur-pills { display: flex; gap: 0.6rem; margin-top: 1.5rem; flex-wrap: wrap; }
.ur-pill { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); color: #aaa; font-size: 0.78rem; padding: 0.3rem 0.8rem; border-radius: 100px; }

.ur-section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: #f5a623; margin-bottom: 0.8rem;
}
.ur-section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem; font-weight: 700;
    color: #f0ece4; margin-bottom: 1.5rem; letter-spacing: -0.01em;
}

.ur-upload-card {
    background: #0f0f1a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.5rem; margin-bottom: 0.5rem;
}
.ur-upload-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.ur-upload-title { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 700; color: #e8e4dc; margin-bottom: 0.25rem; }
.ur-upload-desc { font-size: 0.8rem; color: #666; margin-bottom: 1rem; line-height: 1.4; }

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(245,166,35,0.25) !important;
    border-radius: 10px !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #f5a623, #e8951a) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important; font-weight: 700 !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.8rem 2rem !important;
    box-shadow: 0 4px 24px rgba(245,166,35,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 8px 32px rgba(245,166,35,0.4) !important;
}
.stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: #c8c4bc !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
}
.stDownloadButton > button:hover {
    background: rgba(245,166,35,0.08) !important;
    border-color: rgba(245,166,35,0.3) !important;
    color: #f5a623 !important;
}

.stProgress > div > div { background: linear-gradient(90deg, #f5a623, #ffcc70) !important; border-radius: 100px !important; }
.stProgress > div { background: rgba(255,255,255,0.05) !important; border-radius: 100px !important; }

[data-testid="stMetricValue"] { color: #f5a623 !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #777 !important; font-size: 0.78rem !important; }
[data-testid="metric-container"] { background: #0f0f1a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 12px !important; padding: 1rem !important; }

.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid rgba(255,255,255,0.07) !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #666 !important; font-family: 'DM Sans', sans-serif !important; }
.stTabs [aria-selected="true"] { background: rgba(245,166,35,0.08) !important; color: #f5a623 !important; border-bottom: 2px solid #f5a623 !important; }

.ur-report { background: #0f0f1a; border: 1px solid rgba(255,255,255,0.07); border-radius: 16px; padding: 2.5rem; line-height: 1.7; color: #d4d0c8; }
.ur-report h1 { color: #f5a623; font-family: 'Syne', sans-serif; }
.ur-report h2 { color: #f0ece4; font-family: 'Syne', sans-serif; }
.ur-report table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; }
.ur-report th { background: rgba(245,166,35,0.1); color: #f5a623; padding: 0.7rem 1rem; text-align: left; border: 1px solid rgba(255,255,255,0.06); font-family: 'Syne', sans-serif; font-size: 0.78rem; letter-spacing: 0.05em; }
.ur-report td { border: 1px solid rgba(255,255,255,0.05); padding: 0.65rem 1rem; color: #c8c4bc; }
.ur-report tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
.ur-report hr { border-color: rgba(255,255,255,0.08); margin: 2rem 0; }

[data-testid="stExpander"] { background: #0f0f1a !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 12px !important; }
.stTextArea textarea { background: #0f0f1a !important; color: #888 !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 10px !important; }

hr { border-color: rgba(255,255,255,0.06) !important; }

.ur-footer { text-align: center; color: #333; font-size: 0.78rem; padding: 2rem 0 1rem; letter-spacing: 0.05em; }
.ur-footer span { color: #f5a623; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────
st.markdown("""
<div class="ur-header">
    <div class="ur-badge">AI-Powered Diagnostics</div>
    <h1 class="ur-title">UrbanRoof <span>DDR</span> Generator</h1>
    <p class="ur-subtitle">Upload your inspection &amp; thermal reports — get a complete Detailed Diagnostic Report in seconds.</p>
    <div class="ur-pills">
        <span class="ur-pill">📋 Inspection PDF</span>
        <span class="ur-pill">🌡️ Thermal PDF</span>
        <span class="ur-pill">🤖 Vision AI Analysis</span>
        <span class="ur-pill">⬇️ Downloadable Report</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── API KEY CHECK ─────────────────────────────
if not GEMINI_API_KEYS:
    st.error("⚙️ **Setup required:** Open `.streamlit/secrets.toml` and set `GEMINI_API_KEY = \"your-key\"`, then restart.")
    st.stop()

# ── HOW IT WORKS ──────────────────────────────
with st.expander("📖 How this works", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("**1 · Upload**\nInspection Report + Thermal PDF")
    with c2: st.markdown("**2 · Extract**\nAI pulls all text & images")
    with c3: st.markdown("**3 · Analyze**\nGemini correlates visual + thermal")
    with c4: st.markdown("**4 · Report**\nStructured DDR, ready to download")

st.markdown("---")

# ── UPLOAD ────────────────────────────────────
st.markdown('<div class="ur-section-label">Step 01</div>', unsafe_allow_html=True)
st.markdown('<div class="ur-section-title">Upload Your Documents</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""<div class="ur-upload-card">
        <div class="ur-upload-icon">📋</div>
        <div class="ur-upload-title">Inspection Report</div>
        <div class="ur-upload-desc">Visual observations, site checklist, inspection photos</div>
    </div>""", unsafe_allow_html=True)
    inspection_file = st.file_uploader("Inspection PDF", type=['pdf'], key="inspection", label_visibility="collapsed")
    if inspection_file:
        st.success(f"✅ {inspection_file.name}  ·  {round(inspection_file.size/1024,1)} KB")

with col2:
    st.markdown("""<div class="ur-upload-card">
        <div class="ur-upload-icon">🌡️</div>
        <div class="ur-upload-title">Thermal Images Report</div>
        <div class="ur-upload-desc">IR camera readings, temperature data, thermal photos</div>
    </div>""", unsafe_allow_html=True)
    thermal_file = st.file_uploader("Thermal PDF", type=['pdf'], key="thermal", label_visibility="collapsed")
    if thermal_file:
        st.success(f"✅ {thermal_file.name}  ·  {round(thermal_file.size/1024,1)} KB")

st.markdown("---")

# ── OPTIONS + GENERATE ────────────────────────
st.markdown('<div class="ur-section-label">Step 02</div>', unsafe_allow_html=True)
st.markdown('<div class="ur-section-title">Configure &amp; Generate</div>', unsafe_allow_html=True)

oc1, _ = st.columns([1, 2])
with oc1:
    use_vision = st.toggle("🔬 Vision Mode — AI sees images", value=True)

_, bc, _ = st.columns([1, 2, 1])
with bc:
    generate_btn = st.button("⚡ GENERATE DDR REPORT", type="primary", use_container_width=True)

# ── GENERATION LOGIC ──────────────────────────
if generate_btn:
    if not inspection_file:
        st.error("❌ Please upload the Inspection Report PDF.")
        st.stop()
    if not thermal_file:
        st.error("❌ Please upload the Thermal Images Report PDF.")
        st.stop()

    os.makedirs("uploads", exist_ok=True)
    os.makedirs("output/images", exist_ok=True)

    inspection_path = f"uploads/{inspection_file.name}"
    thermal_path    = f"uploads/{thermal_file.name}"
    with open(inspection_path, "wb") as f: f.write(inspection_file.getbuffer())
    with open(thermal_path,    "wb") as f: f.write(thermal_file.getbuffer())

    st.markdown("---")
    st.markdown('<div class="ur-section-label">Processing</div>', unsafe_allow_html=True)
    progress_bar = st.progress(0)
    status_text  = st.empty()
    detail_text  = st.empty()

    try:
        status_text.markdown("**📖 Extracting data from PDFs...**")
        detail_text.caption("Reading text and images from your documents...")
        progress_bar.progress(10)
        time.sleep(0.5)

        extracted = extract_all(inspection_path, thermal_path, "output/images")
        progress_bar.progress(35)

        status_text.markdown("**🤖 AI is analyzing and writing your DDR...**")
        detail_text.caption("Correlating visual observations with thermal data...")
        progress_bar.progress(50)

        # ── FALLBACK KEY LOGIC ─────────────────────────────────────────
        ddr_report = None
        last_error = None
        for key_index, api_key in enumerate(GEMINI_API_KEYS):
            try:
                if key_index > 0:
                    detail_text.caption(f"Switching to backup AI key {key_index + 1}...")
                if use_vision and extracted["all_images"]:
                    detail_text.caption(f"Vision Mode — analyzing {len(extracted['inspection_images'])} inspection + {len(extracted['thermal_images'])} thermal images...")
                    ddr_report = generate_ddr_with_vision(
                        extracted["inspection_text"], extracted["thermal_text"],
                        extracted["inspection_images"],
                        extracted["thermal_images"],
                        api_key
                    )
                else:
                    ddr_report = generate_ddr_text_only(
                        extracted["inspection_text"], extracted["thermal_text"], api_key
                    )
                break  # success — stop trying keys
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                    if key_index < len(GEMINI_API_KEYS) - 1:
                        continue  # try next key
                raise  # non-quota error or no more keys

        if ddr_report is None:
            raise last_error

        progress_bar.progress(100)
        status_text.empty(); detail_text.empty()
        st.success("🎉 DDR Report generated successfully!")

        st.markdown("---")
        st.markdown('<div class="ur-section-label">Step 03</div>', unsafe_allow_html=True)
        st.markdown('<div class="ur-section-title">Download Your DDR Report</div>', unsafe_allow_html=True)

        html_out = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>UrbanRoof DDR</title>
<style>body{{font-family:Arial,sans-serif;max-width:960px;margin:0 auto;padding:3rem;background:#0a0a0f;color:#d4d0c8}}
h1{{color:#f5a623}}h2{{color:#f0ece4;border-left:4px solid #f5a623;padding-left:1rem}}
table{{border-collapse:collapse;width:100%}}th{{background:rgba(245,166,35,.15);color:#f5a623;padding:.7rem;text-align:left;border:1px solid #222}}
td{{border:1px solid #1a1a1a;padding:.65rem;color:#aaa}}hr{{border-color:#1a1a1a}}</style></head>
<body><pre style="white-space:pre-wrap;font-family:Arial;line-height:1.7">{ddr_report}</pre>
<p style="color:#333;font-size:.78rem;margin-top:3rem">Generated by UrbanRoof AI DDR System</p></body></html>"""
        pdf_bytes = generate_pdf(ddr_report)

        st.markdown('''<div style="background:#0f0f1a;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">&#10003;</div>
            <div style="font-family:sans-serif;font-size:1.1rem;font-weight:700;color:#f0ece4;margin-bottom:0.4rem;">Your DDR Report is Ready</div>
            <div style="color:#666;font-size:0.85rem;">Choose a format below to download</div>
        </div>''', unsafe_allow_html=True)

        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button("⬇️ Download TXT", data=ddr_report,
                file_name="UrbanRoof_DDR_Report.txt", mime="text/plain", use_container_width=True)
        with d2:
            st.download_button("⬇️ Download HTML", data=html_out,
                file_name="UrbanRoof_DDR_Report.html", mime="text/html", use_container_width=True)
        with d3:
            st.download_button("⬇️ Download PDF", data=pdf_bytes,
                file_name="UrbanRoof_DDR_Report.pdf", mime="application/pdf", use_container_width=True)

        st.markdown("---")
        with st.expander("📸 View Extracted Images"):
            if extracted["inspection_images"]:
                st.markdown("##### 🔍 Inspection Photos")
                cols = st.columns(3)
                for i, p in enumerate(extracted["inspection_images"][:12]):
                    with cols[i%3]:
                        try: st.image(p, caption=f"Inspection {i+1}", use_column_width=True)
                        except: st.caption(f"Image {i+1} — could not display")
            if extracted["thermal_images"]:
                st.markdown("##### 🌡️ Thermal Images")
                cols = st.columns(3)
                for i, p in enumerate(extracted["thermal_images"][:12]):
                    with cols[i%3]:
                        try: st.image(p, caption=f"Thermal {i+1}", use_column_width=True)
                        except: st.caption(f"Thermal {i+1} — could not display")

    except Exception as e:
        progress_bar.empty(); status_text.empty(); detail_text.empty()
        st.error(f"❌ Something went wrong: {str(e)}")
        st.markdown("""**Common fixes:**\n- Make sure PDFs are not password protected\n- Try turning off Vision Mode\n- Try again in a moment""")

# ── FOOTER ────────────────────────────────────
st.markdown("---")
st.markdown('<div class="ur-footer">🏠 UrbanRoof AI DDR System &nbsp;·&nbsp; <span>AI/ML Engineer Assignment</span></div>', unsafe_allow_html=True)