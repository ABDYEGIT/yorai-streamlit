import os
import pandas as pd
from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def run_ciro_flow(excel_path):
    df = pd.read_excel(excel_path)

    # 🔒 Kolon isimlerini normalize et
    df.columns = [c.strip().lower() for c in df.columns]

    # Olası tarih kolonları
    if "ay" in df.columns:
        date_col = "ay"
    elif "tarih" in df.columns:
        date_col = "tarih"
    elif "date" in df.columns:
        date_col = "date"
    else:
        raise ValueError(
            f"Tarih kolonu bulunamadı. Bulunan kolonlar: {df.columns.tolist()}"
        )

    # Olası ciro kolonları
    if "ciro" not in df.columns:
        raise ValueError("Excel içinde 'ciro' kolonu bulunamadı.")

    # Tarih dönüşümü
    df[date_col] = pd.to_datetime(df[date_col])

    # Son ay
    last_month = df[date_col].max()
    last_month_total = df[df[date_col] == last_month]["ciro"].sum()

    # Senaryolar
    scenarios = pd.DataFrame({
        "Senaryo": ["Kötümser", "Beklenen", "İyimser"],
        "Tahmini Ciro": [
            int(last_month_total * 0.9),
            int(last_month_total * 1.05),
            int(last_month_total * 1.2),
        ]
    })

    # AI Yorumu
    prompt = f"""
    Son ay ciro: {last_month_total} TL.
    Kötümser, beklenen ve iyimser senaryoları yorumla.
    Yöneticiye yönelik, kısa ve net bir analiz yaz.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "last_month_total": last_month_total,
        "scenarios": scenarios,
        "ai_commentary": response.choices[0].message.content
    }
