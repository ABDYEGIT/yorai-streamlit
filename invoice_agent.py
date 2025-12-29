import os
import json
import base64
from openai import OpenAI



api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()



INVOICE_SCHEMA_HINT = {
  "fatura_bilgileri": {"fatura_no": "string|null", "duzenlenme_tarihi": "string|null"},
  "satici_bilgileri": {
    "firma_adi": "string|null",
    "adres": {"mahalle":"string|null","cadde":"string|null","no":"string|null","posta_kodu":"string|null","ilce":"string|null","il":"string|null"},
    "telefon":"string|null",
    "email":"string|null"
  },
  "alici_bilgileri": {
    "firma_adi":"string|null",
    "adres":{"mahalle":"string|null","cadde":"string|null","no":"string|null","posta_kodu":"string|null","ilce":"string|null","il":"string|null"},
    "email":"string|null"
  },
  "kalemler": [
    {"aciklama":"string|null","miktar":"number|null","kdv_orani":"number|null","birim_fiyat":"number|null","toplam":"number|null","para_birimi":"string|null"}
  ],
  "toplamlar": {"ara_toplam":"number|null","vergi_orani":"string|null","genel_toplam":"number|null","para_birimi":"string|null"},
  "odeme_bilgileri": {"hesap_adi":"string|null","hesap_no":"string|null","odeme_vadesi":"string|null"},
  "alt_bilgi": {"tesekkur_metni":"string|null","aciklama":"string|null"},
  "meta": {"warnings": ["string"], "confidence": {"overall":"number", "fields":{"field_path":"number"}}}
}

def run_invoice_flow(invoice_path):
    """
    data/fatura.png dosyasını alır, OpenAI Vision ile JSON çıkarır.
    API servis yok, tamamen local akış.
    """

    if not client:
        return {
            "error": True,
            "message": "OPENAI_API_KEY tanımlı değil. Fatura JSON çıkarımı için API key gereklidir."
        }

    img_bytes = invoice_path.read_bytes()
    b64 = base64.b64encode(img_bytes).decode("utf-8")

    system = (
        "Sen bir fatura veri çıkarım ajanısın. "
        "Sadece geçerli JSON döndür. Ek metin yazma. "
        "Okuyamadığın alanları null yap. Tahmin/uydurma yapma."
    )

    user = (
        "Bu fatura görselindeki alanları aşağıdaki şemaya göre çıkar.\n"
        "Şema ipucu:\n"
        f"{json.dumps(INVOICE_SCHEMA_HINT, ensure_ascii=False)}\n\n"
        "Kurallar:\n"
        "- Çıktı sadece JSON olsun.\n"
        "- Sayılar numeric olsun (100.00).\n"
        "- Para birimini 'TL'/'TRY' gibi yaz.\n"
        "- Toplamlar tutmuyorsa meta.warnings içine yaz.\n"
    )

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": [
                    {"type": "text", "text": user},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}}
                ]},
            ],
        )
        content = resp.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"error": True, "message": str(e)}
