"""Веб-інтерфейс (Streamlit): завантажити фото чека -> таблиця позицій + CSV."""
import os
import time

import streamlit as st
from dotenv import load_dotenv

from receipt_api import check_total, extract_receipt, items_table, make_client

load_dotenv()
st.set_page_config(page_title="Сканер чеків", page_icon="🧾")
st.title("🧾 Сканер чеків")
st.caption("Фото чека -> структуровані дані через Google Gemini API")

# Ключ: з .env локально або зі Streamlit Secrets у хмарі.
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
if not api_key:
    st.error("Не задано GEMINI_API_KEY. Додайте його у файл .env (локально) або в Streamlit Secrets.")
    st.stop()

file = st.file_uploader("Фото чека", type=["jpg", "jpeg", "png", "webp"])
SAMPLE = os.path.join(os.path.dirname(__file__), "samples", "sample_receipt.png")
if st.button("Взяти приклад чека") and os.path.exists(SAMPLE):
    st.session_state["sample"] = True
if file:
    st.session_state["sample"] = False

data = mime = None
if file:
    data, mime = file.getvalue(), file.type
elif st.session_state.get("sample"):
    with open(SAMPLE, "rb") as f:
        data, mime = f.read(), "image/png"

if data:
    st.image(data, caption="Чек для розпізнавання", use_container_width=True)
    if st.button("Розпізнати"):
        with st.spinner("Запит до Gemini API..."):
            t = time.time()
            try:
                receipt, tokens = extract_receipt(data, mime, client=make_client(api_key))
            except Exception as e:  # мережа, квота, неправильний ключ тощо
                st.error("Помилка запиту: %s" % e)
                st.stop()
            dt = time.time() - t

        c1, c2, c3 = st.columns(3)
        c1.metric("Магазин", receipt.store_name or "—")
        c2.metric("Дата", receipt.date or "—")
        c3.metric("Разом", "%s %s" % (receipt.total if receipt.total is not None else "—", receipt.currency or ""))

        df = items_table(receipt)
        st.dataframe(df, use_container_width=True, hide_index=True)

        ok, s = check_total(receipt)
        if ok:
            st.success("Сума позицій (%.2f) збігається із сумою чека." % s)
        else:
            st.warning("Сума позицій (%.2f) відрізняється від суми чека (%s): перевірте вручну." % (s, receipt.total))

        st.download_button("Завантажити CSV", df.to_csv(index=False).encode("utf-8"), "receipt.csv", "text/csv")
        st.caption("Час запиту: %.1f с%s" % (dt, ", токенів: %d" % tokens if tokens else ""))
