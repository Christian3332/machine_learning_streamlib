import streamlit as st

from utils.config import NAMA_MODEL
from utils.prediksi import model_tersedia
from utils.tampilan import pasang_css

st.set_page_config(page_title="Cek Penulis", page_icon=":material/draw:", layout="centered")
pasang_css()

# menu di sidebar: Identifikasi, Riwayat, Tentang model
halaman = st.navigation([
    st.Page("halaman/identifikasi.py", title="Identifikasi", icon=":material/document_scanner:", default=True),
    st.Page("halaman/riwayat.py", title="Riwayat", icon=":material/history:"),
    st.Page("halaman/tentang_model.py", title="Tentang model", icon=":material/bar_chart:"),
])

with st.sidebar:
    st.write("")
    if model_tersedia():
        st.caption(f"Model aktif: {NAMA_MODEL}, model terbaik hasil penelitian")
    else:
        st.caption(f"Model {NAMA_MODEL} belum ada di folder model/")

halaman.run()
