import os
import pandas as pd
from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def run_ciro_flow(excel_path):
    df = pd.read_excel(excel_path)

    # Beklenen kolonlar: Ay, Musteri, Ciro
    df["Ay"] = pd.to_datetime(df["Ay"])

    # Son ay ve önceki ay
    last_month = df["Ay"].max()
    prev_month = last_month - pd.DateOffset(months=1)

    last_month_total = df[df["Ay"] == last_month]["Ciro"].sum()
    prev_month_total = df[df["Ay"] == prev_month]["Ciro"].sum()

    # Senaryo hesapları
    scenarios = {
        "İyimser": round(last_month_total * 1.10, 2),
        "Normal": round(last_month_total * 1.00, 2),
        "Kötümser": round(last_month_total * 0.90, 2),
    }

    scenario_table = pd.DataFrame([
        {
            "Senaryo": k,
            "Tahmini Ciro (₺)": v,
            "Değişim (%)": round(((v - last_month_total) / last_month_total) * 100, 2)
        }
        for k, v in scenarios.items()
    ])

    # AI yorumu (yönetici dili)
    prompt = f"""
    Aşağıdaki ciro tahmin senaryolarını Yorglass üst yönetimi için yorumla.
    Kısa, net ve aksiyon odaklı ol.

    Senaryolar:
    {scenario_table.to_string(index=False)}
    """

    ai_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sen deneyimli bir finans analistisin."},
            {"role": "user", "content": prompt}
        ]
    )

    commentary = ai_response.choices[0].message.content

    return {
        "last_month_total": last_month_total,
        "scenarios": scenario_table,
        "ai_commentary": commentary
    }
