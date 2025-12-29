import streamlit as st
from pathlib import Path

from ciro_agent import run_ciro_flow
from invoice_agent import run_invoice_flow

# --------------------
# PATHS
# --------------------
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

# --------------------
# PAGE CONFIG
# --------------------
st.set_page_config(
    page_title="YORAI | Yorglass",
    layout="wide",
)

# --------------------
# SESSION STATE INIT
# --------------------
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if "step" not in st.session_state:
    st.session_state.step = "prompt"

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

# --------------------
# THEME SWITCH (FIXED)
# --------------------
def apply_theme(mode: str):
    if mode == "Dark":
        st.markdown("""
        <style>
        html, body, .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }

        section.main {
            background-color: #0E1117;
        }

        .block-container {
            background-color: #0E1117;
            padding-top: 2rem;
        }

        h1, h2, h3, h4 {
            color: #00A6B2;
        }

        p, span, label, li {
            color: #E0E0E0 !important;
        }

        input, textarea {
            background-color: #1C1F26 !important;
            color: #FFFFFF !important;
        }

        div[data-baseweb="radio"] label {
            color: #E0E0E0 !important;
        }

        button {
            background-color: #00A6B2 !important;
            color: #FFFFFF !important;
            border: none;
        }

        button:hover {
            background-color: #008C96 !important;
        }

        hr {
            border-color: #2A2E39;
        }

        [data-testid="stSidebar"] {
            background-color: #161A23;
        }
        </style>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <style>
        html, body, .stApp {
            background-color: #FFFFFF;
            color: #5A5A5A;
        }

        .block-container {
            background-color: #FFFFFF;
        }

        h1, h2, h3 {
            color: #00A6B2;
        }

        [data-testid="stSidebar"] {
            background-color: #F4F7F8;
        }
        </style>
        """, unsafe_allow_html=True)

# --------------------
# SIDEBAR
# --------------------
with st.sidebar:
    st.image(ASSETS_DIR / "yorglass_logo.png", use_column_width=True)

    st.markdown("---")
    st.subheader("🎨 Tema")

    theme = st.radio(
        "Görünüm",
        ["Light", "Dark"],
        index=0 if st.session_state.theme_mode == "Light" else 1
    )

    st.session_state.theme_mode = theme
    apply_theme(theme)

    st.markdown("---")
    if st.button("🔄 Baştan Başla"):
        st.session_state.onboarded = False
        st.session_state.step = "prompt"
        st.rerun()

# --------------------
# HEADER
# --------------------
st.title("YORAI")
st.caption("Yorglass Yapay Zeka Destek Asistanı")

st.markdown(
    "<span style='color:#00A6B2'>Veriye dayalı, hızlı ve güvenilir analizler</span>",
    unsafe_allow_html=True
)

st.markdown("---")

# --------------------
# ONBOARDING
# --------------------
if not st.session_state.onboarded:
    st.markdown("## 👋 YORAI’ye Hoş Geldiniz")

    st.markdown("""
    **YORAI**, Yorglass için geliştirilmiş bir **yapay zeka destekli karar destek sistemidir**.

    ### YORAI ile neler yapabilirsiniz?
    - 📊 **Müşteri bazlı ciro tahmini**
    - 🧾 **Fatura görsellerinden otomatik veri çıkarımı**
    - 🤖 **Veriye dayalı finansal yorumlar**
    """)

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🚀 Başla"):
            st.session_state.onboarded = True
            st.session_state.step = "prompt"
            st.rerun()

    with col2:
        st.info(
            "Bu uygulama bir **karar destek sistemi**dir. "
            "Nihai karar kullanıcıya aittir."
        )

# --------------------
# STEP 1 – PROMPT
# --------------------
elif st.session_state.step == "prompt":
    prompt = st.text_input(
        "Sana nasıl yardımcı olmamı istersin?",
        placeholder="Örn: Satışları analiz etmek istiyorum"
    )

    if st.button("Devam ▶️"):
        st.session_state.step = "select"
        st.rerun()

# --------------------
# STEP 2 – SELECT
# --------------------
elif st.session_state.step == "select":
    st.success(
        "Merhaba, ben **YORAI** 👋  \n"
        "Şu an sadece aşağıdaki iki konuda destek olabiliyorum."
    )

    option = st.radio(
        "Lütfen birini seç:",
        [
            "📊 Ciro Tahmin Uygulaması",
            "🧾 Fatura Yükleyip JSON Çıktı Alma"
        ]
    )

    if st.button("Çalıştır 🚀"):
        st.session_state.option = option
        st.session_state.step = "result"
        st.rerun()

# --------------------
# STEP 3 – RESULT
# --------------------
elif st.session_state.step == "result":

    if "Ciro" in st.session_state.option:
        st.subheader("📊 Ciro Tahmin Senaryoları")

        with st.spinner("Senaryolar hesaplanıyor..."):
            result = run_ciro_flow(DATA_DIR / "mock_ciro.xlsx")

        st.metric("Son Ay Gerçekleşen Ciro", f"{result['last_month_total']:,.0f} ₺")

        st.markdown("### 📈 Senaryo Bazlı Tahminler")
        st.dataframe(result["scenarios"], use_container_width=True)

        st.markdown("### 🤖 YORAI Yorumu")
        st.write(result["ai_commentary"])

        st.dataframe(result["table"], use_container_width=True)

    else:
        st.subheader("🧾 Fatura JSON Çıktısı")

        with st.spinner("Fatura analiz ediliyor..."):
            invoice = run_invoice_flow(DATA_DIR / "fatura.png")

        st.json(invoice)

    st.markdown("---")
    if st.button("🔁 Yeni İşlem"):
        st.session_state.step = "prompt"
        st.rerun()
