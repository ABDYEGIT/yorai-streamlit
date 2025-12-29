import os
import pandas as pd
from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def run_ciro_flow(excel_path):
    """
    data/mock_ciro.xlsx dosyasından ciro verisini okur,
    basit bir tahmin üretir ve OpenAI ile yönetici yorumu ekler.
    """
    df = pd.read_excel(excel_path, sheet_name="SAP_CIRO_6AY")

    # Son 6 ay kolonlarını otomatik bul (MüşteriKodu vb. dışındaki aylık kolonlar)
    non_month_cols = {"MüşteriKodu", "MüşteriAdı", "Bölge", "Segment", "ParaBirimi", "Toplam_6Ay"}
    month_cols = [c for c in df.columns if c not in non_month_cols]

    if len(month_cols) < 2:
        raise ValueError("Excel formatı beklenen gibi değil: Aylık kolonlar bulunamadı.")

    last_month_col = month_cols[-1]
    prev_month_col = month_cols[-2]

    # Basit tahmin: son ay * (1 + büyüme) -> büyümeyi son 2 ay değişiminden al
    last_total = float(df[last_month_col].sum())
    prev_total = float(df[prev_month_col].sum())
    growth = 0.0 if prev_total == 0 else (last_total - prev_total) / prev_total
    # büyümeyi aşırı uçlardan kırp
    growth = max(min(growth, 0.25), -0.25)

    forecast_total = last_total * (1 + growth)

    # Müşteri bazlı tahmin (aynı growth ile)
    df_out = df.copy()
    df_out["Gelecek_Ay_Tahmin"] = (df_out[last_month_col] * (1 + growth)).round(2)

    # OpenAI yorumu (key yoksa fallback)
    if client:
        prompt = f"""
Yorglass finans asistanısın. Aşağıdaki özet üzerinden kısa ve yönetici diliyle bir değerlendirme yaz.
- Önceki ay toplam: {prev_total:,.2f} TRY
- Son ay toplam: {last_total:,.2f} TRY
- Hesaplanan büyüme: %{growth*100:.2f}
- Gelecek ay tahmini: {forecast_total:,.2f} TRY

Çıktı formatı:
1) 3-5 cümle yönetici özeti
2) 3 madde aksiyon önerisi
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Sen bir finans analisti gibi net ve kısa yazarsın."},
                {"role": "user", "content": prompt},
            ],
        )
        commentary = resp.choices[0].message.content.strip()
    else:
        commentary = (
            "OPENAI_API_KEY tanımlı değil. Tahmin üretildi ancak AI yorumu için API key gereklidir.\n"
            "Öneri: Windows ortam değişkeni olarak OPENAI_API_KEY ekleyin."
        )

    return {
        "forecast_total_try": f"{forecast_total:,.2f} TRY",
        "forecast_vs_last_month": f"%{growth*100:.2f}",
        "ai_commentary": commentary,
        "table": df_out[["MüşteriKodu","MüşteriAdı","Bölge","Segment", last_month_col, "Gelecek_Ay_Tahmin"]]
    }
