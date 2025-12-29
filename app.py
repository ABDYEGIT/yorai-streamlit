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
# SESSION STATE
# --------------------
if "step" not in st.session_state:
    st.session_state.step = "prompt"

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"

# --------------------
# THEME SWITCH (CSS)
# --------------------
def apply_theme(mode: str):
    if mode == "Dark":
        st.markdown("""
        <style>
        body {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        h1, h2, h3 {
            color: #00A6B2;
        }
        [data-testid="stSidebar"] {
            background-color: #161A23;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        h1, h2, h3 {
            color: #00A6B2;
        }
        [data-testid="stSidebar"] {
            background-color: #F4F7F8;
        }
        </style>
        """, unsafe_allow_html=True)

# --------------------
# SIDEBAR (LOGO + THEME)
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
        st.session_state.step = "prompt"
        st.experimental_rerun()

# --------------------
# HEADER
# --------------------
st.title("YORAI")
st.caption("Yorglass Yapay Zeka Destek Asistanı")

st.markdown(
    "<span style='color:#008C96'>Veriye dayalı, hızlı ve güvenilir analizler</span>",
    unsafe_allow_html=True
)

st.markdown("---")

# --------------------
# STEP 1 – PROMPT
# --------------------
if st.session_state.step == "prompt":
    prompt = st.text_input(
        "Sana nasıl yardımcı olmamı istersin?",
        placeholder="Örn: Satışları analiz etmek istiyorum"
    )

    if st.button("Devam ▶️"):
        st.session_state.step = "select"
        st.experimental_rerun()

# --------------------
# STEP 2 – SELECTION
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
        st.experimental_rerun()

# --------------------
# STEP 3 – RESULT
# --------------------
elif st.session_state.step == "result":

    if "Ciro" in st.session_state.option:
        st.subheader("📊 Ciro Tahmin Sonucu")

        with st.spinner("Tahmin hesaplanıyor..."):
            result = run_ciro_flow(DATA_DIR / "mock_ciro.xlsx")

        st.metric("Gelecek Ay Tahmini", result["forecast_total_try"])
        st.metric("Değişim Oranı", result["forecast_vs_last_month"])

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
        st.experimental_rerun()
