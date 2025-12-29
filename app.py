import streamlit as st
from pathlib import Path

from ciro_agent import run_ciro_flow
from invoice_agent import run_invoice_flow

APP_TITLE = "YORAI - Yorglass Yapay Zeka Asistanı"
DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(page_title=APP_TITLE, layout="centered")

# --- Session State defaults
if "step" not in st.session_state:
    st.session_state.step = "ask_prompt"  # ask_prompt -> choose -> result
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""


st.title("🤖 YORAI")
st.caption("Yorglass içi PoC - Kontrollü Asistan")

# --- Reset button (her yerden sıfırlamak için)
with st.sidebar:
    if st.button("🔄 Sıfırla / Baştan Başla"):
        st.session_state.step = "ask_prompt"
        st.session_state.user_prompt = ""
        st.rerun()


# ==============
# STEP 1: Prompt al
# ==============
if st.session_state.step == "ask_prompt":
    st.subheader("Sana nasıl yardımcı olayım?")
    prompt = st.text_input(
        "Prompt gir:",
        value="",
        placeholder="Örn: Bu ay satışlarımızı analiz etmek istiyorum...",
        key="prompt_input"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        send = st.button("Gönder ✅")

    if send:
        st.session_state.user_prompt = prompt.strip()
        # Prompt boş olsa bile akışı ilerletiyoruz (kullanıcı deneyimi)
        st.session_state.step = "choose"
        st.rerun()


# ==========================
# STEP 2: Seçenek seçtir (prompt kilit)
# ==========================
if st.session_state.step == "choose":
    st.success("Mesajını aldım ✅")

    st.markdown(
        """
**Merhaba, ben YORAI.**  
Şimdilik sadece aşağıdaki iki konuda destek olabiliyorum.  
Lütfen birini seç:
"""
    )

    choice = st.radio(
        "Seçenekler",
        ["1) Ciro Tahmin Uygulaması", "2) Fatura Alanlarını JSON’a Çevirme"],
        index=0
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        go = st.button("Devam ▶️")
    with col2:
        back = st.button("⬅️ Prompt’a dön")

    if back:
        st.session_state.step = "ask_prompt"
        st.rerun()

    if go:
        st.session_state.choice = choice
        st.session_state.step = "result"
        st.rerun()


# ==========================
# STEP 3: Sonuç üret (tek akış)
# ==========================
if st.session_state.step == "result":
    st.info("Seçimin işleniyor…")

    choice = st.session_state.get("choice", "")
    if choice.startswith("1)"):
        st.subheader("📊 Ciro Tahmin Uygulaması")

        # Excel upload yok → data/mock_ciro.xlsx içerden okunur
        excel_path = DATA_DIR / "mock_ciro.xlsx"
        if not excel_path.exists():
            st.error(f"`{excel_path}` bulunamadı. Lütfen data klasörüne mock_ciro.xlsx koy.")
        else:
            with st.spinner("Tahmin hesaplanıyor..."):
                out = run_ciro_flow(excel_path)

            st.success("Tamamlandı ✅")
            st.metric("Gelecek Ay Toplam Ciro Tahmini", out["forecast_total_try"])
            st.metric("Son Aya Göre Değişim", out["forecast_vs_last_month"])

            st.subheader("🤖 YORAI Yorumu")
            st.write(out["ai_commentary"])

            st.subheader("📋 Müşteri Bazlı Çıktı")
            st.dataframe(out["table"], use_container_width=True)

    else:
        st.subheader("🧾 Fatura → JSON")

        # API yok → data/fatura.png içerden okunur
        invoice_path = DATA_DIR / "fatura.png"
        if not invoice_path.exists():
            st.error(f"`{invoice_path}` bulunamadı. Lütfen data klasörüne fatura.png koy.")
        else:
            with st.spinner("Fatura analiz ediliyor..."):
                result = run_invoice_flow(invoice_path)

            if result.get("error"):
                st.error(result["message"])
            else:
                st.success("JSON üretildi ✅")
                st.json(result)

    st.divider()
    if st.button("🔁 Yeni işlem yap"):
        st.session_state.step = "ask_prompt"
        st.session_state.user_prompt = ""
        st.rerun()
