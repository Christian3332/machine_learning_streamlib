import hashlib

import streamlit as st

from utils.config import EKSTENSI_GAMBAR, NAMA_MODEL
from utils.preprocess import gambar_valid, buka_dari_bytes, crop_manual
from utils.prediksi import model_tersedia, identifikasi
from utils.riwayat_lokal import tambah_riwayat
from utils.tampilan import label, tampilkan_hasil

st.session_state.setdefault("kunci_input", 0)
st.session_state.setdefault("pakai_kamera", False)
st.session_state.setdefault("hasil_terakhir", None)


# hapus gambar caranya ganti key widget, jadi uploader/kamera kosong lagi
def hapus_gambar():
    st.session_state.kunci_input += 1
    st.session_state.hasil_terakhir = None


def ganti_sumber():
    st.session_state.pakai_kamera = not st.session_state.pakai_kamera
    hapus_gambar()


st.markdown("### Identifikasi penulis")
if not model_tersedia():
    st.warning(f"Model {NAMA_MODEL} belum tersedia. Jalankan notebook training di Colab, "
               "lalu taruh file hasilnya di folder `model/` dan muat ulang halaman ini.")

# kotak upload: pilih dari galeri atau ambil langsung dari kamera
kunci = st.session_state.kunci_input
with st.container(border=True, key="kotak_upload"):
    kiri, kanan = st.columns([3, 1.2], vertical_alignment="center")
    with kiri:
        if st.session_state.pakai_kamera:
            st.markdown('<p class="judul-upload">Ambil foto tulisan</p>'
                        '<p class="teks-redup">Posisikan kertas lurus dan cahayanya terang</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="judul-upload">Seret foto tulisan ke sini</p>'
                        '<p class="teks-redup">JPG atau PNG, tulisan lurus dan terang</p>', unsafe_allow_html=True)
    with kanan:
        if st.session_state.pakai_kamera:
            st.button("Galeri", icon=":material/image:", on_click=ganti_sumber, width="stretch")
        else:
            st.button("Kamera", icon=":material/photo_camera:", on_click=ganti_sumber, width="stretch")

    if st.session_state.pakai_kamera:
        file = st.camera_input("Foto tulisan", key=f"kamera_{kunci}", label_visibility="collapsed")
    else:
        file = st.file_uploader("Pilih gambar", type=EKSTENSI_GAMBAR, key=f"upload_{kunci}",
                                label_visibility="collapsed")

if file is None:
    st.stop()

# validasi file
isi = file.getvalue()
if not gambar_valid(isi):
    st.error("File ini bukan gambar JPG/PNG yang valid. Coba pilih gambar lain.")
    st.stop()
gambar = buka_dari_bytes(isi)

# crop sederhana pakai slider, area kosong di sekitar tulisan nanti tetap dipotong otomatis
label("Pratinjau gambar")
with st.expander("Crop gambar (opsional)", icon=":material/crop:"):
    st.caption("Geser kalau di foto masih ada benda lain selain tulisan.")
    kiri_kanan = st.slider("Batas kiri - kanan (%)", 0, 100, (0, 100), key=f"crop_h_{kunci}")
    atas_bawah = st.slider("Batas atas - bawah (%)", 0, 100, (0, 100), key=f"crop_v_{kunci}")
if kiri_kanan[1] - kiri_kanan[0] < 5 or atas_bawah[1] - atas_bawah[0] < 5:
    st.warning("Area crop terlalu kecil, jadi gambar dipakai utuh.")
    kiri_kanan, atas_bawah = (0, 100), (0, 100)
gambar = crop_manual(gambar, kiri_kanan[0], kiri_kanan[1], atas_bawah[0], atas_bawah[1])

with st.container(border=True, key="kartu_pratinjau"):
    st.image(gambar, width="stretch")

kol1, kol2 = st.columns([3, 1])
tombol = kol1.button("Identifikasi Penulis", type="primary", icon=":material/search:", width="stretch",
                     disabled=not model_tersedia())
kol2.button("Hapus gambar", icon=":material/delete:", on_click=hapus_gambar, width="stretch")

# penanda gambar + crop yang sedang dipakai, biar hasil lama tidak tampil untuk gambar baru
sumber = hashlib.md5(isi + str((kiri_kanan, atas_bawah)).encode()).hexdigest()

# proses identifikasi, hasilnya langsung disimpan ke riwayat
if tombol:
    try:
        with st.spinner("Sedang mengidentifikasi penulis..."):
            hasil, crop, overlay = identifikasi(gambar)
            item = tambah_riwayat(hasil, crop, overlay)
        st.session_state.hasil_terakhir = dict(item, sumber=sumber)
        st.toast("Identifikasi selesai, hasil disimpan ke riwayat", icon=":material/check_circle:")
    except Exception as e:
        st.session_state.hasil_terakhir = None
        st.error(f"Terjadi masalah saat prediksi: {e}")

hasil = st.session_state.hasil_terakhir
if hasil and hasil.get("sumber") == sumber:
    st.divider()
    tampilkan_hasil(hasil)
