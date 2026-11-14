import json

import pandas as pd
import streamlit as st

from utils.config import (
    FILE_KELAS, FILE_METRIK, FILE_SPLIT, FILE_PERBANDINGAN,
    GRAFIK_TRAINING, CONFUSION_MATRIX, NAMA_MODEL, TINGGI, LEBAR, AMBANG_DIKENALI,
)
from utils.prediksi import model_tersedia
from utils.tampilan import label, persen, angka


def baca_json(path):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


kelas = baca_json(FILE_KELAS)
metrik = baca_json(FILE_METRIK)
split = baca_json(FILE_SPLIT)

st.markdown("### Tentang model")

# kartu nama model dan penjelasan singkat
with st.container(border=True, key="kartu_model"):
    status = '<span class="badge hijau">Model aktif</span>' if model_tersedia() else \
        '<span class="badge oranye">Belum tersedia</span>'
    st.markdown(f"""
    <div class="baris-judul"><span class="penulis-besar">{NAMA_MODEL}</span>{status}</div>
    <p class="teks-redup">Model terbaik dari penelitian "Identifikasi Penulis Tulisan Tangan:
    EfficientNetV2, ConvNeXt, dan Swin Transformer"</p>
    """, unsafe_allow_html=True)
    st.write(
        "ConvNeXt (Liu dkk., 2022) adalah CNN yang didesain ulang dengan meniru cara kerja Vision Transformer. "
        "Gambar dipotong jadi patch 4×4, lalu diproses 4 tahap (3, 3, 9, 3 blok). Tiap blok memakai "
        "konvolusi depthwise 7×7 yang jangkauannya lebar, LayerNorm, dan aktivasi GELU. "
        "Versi Tiny punya sekitar 28 juta parameter dan memakai bobot pretrained ImageNet (transfer learning)."
    )

label("Fungsi model di aplikasi ini")
st.write(
    "Model mengenali **gaya** tulisan tangan, seperti bentuk huruf, kemiringan, tebal goresan, dan jarak antarhuruf, "
    "lalu menebak tulisan itu milik penulis (NIM) yang mana. Model tidak membaca isi tulisannya. "
    f"Kalau confidence tertinggi di bawah {persen(AMBANG_DIKENALI, 0)}, hasilnya ditampilkan sebagai **Tidak Dikenali**."
)

# info dataset dari ringkasan_split.json
label("Dataset")
if split:
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Jumlah penulis", split["jumlah_penulis"])
    k2.metric("Train", split["total"]["train"])
    k3.metric("Validation", split["total"]["validation"])
    k4.metric("Test", split["total"]["test"])
    st.caption(f"Dataset tulisan tangan mahasiswa, 1 folder = 1 penulis (NIM). Dibagi 70/15/15 per penulis, "
               f"{len(split.get('duplikat', []))} gambar duplikat dibuang. Input model {TINGGI} × {LEBAR} piksel.")
else:
    st.metric("Jumlah kelas penulis", len(kelas) if kelas else "Belum tersedia")
    st.caption("Ringkasan dataset belum tersedia (file ringkasan_split.json belum ada di folder model/).")

# hasil evaluasi di data test, kalau belum ada tampilkan "Belum tersedia"
label("Hasil pengujian model (data test)")
m1, m2, m3, m4 = st.columns(4)
for kolom, nama, kunci in [(m1, "Accuracy", "accuracy"), (m2, "Precision", "precision"),
                           (m3, "Recall", "recall"), (m4, "F1-Score", "f1_score")]:
    kolom.metric(nama, persen(metrik[kunci], 2) if metrik else "Belum tersedia")
if metrik:
    st.caption(f"Dihitung dari {metrik['jumlah_test']} citra test yang tidak dipakai saat training "
               f"(precision, recall, F1 rata-rata macro). Dengan ambang {persen(metrik['ambang'], 0)}, "
               f"{persen(metrik['persen_dikenali'])} citra test berstatus Dikenali dan akurasinya "
               f"{persen(metrik['akurasi_saat_dikenali'])}.")

# tabel hasil perbandingan 3 model dari notebook penelitian
label(f"Kenapa memilih {NAMA_MODEL}?")
if FILE_PERBANDINGAN.exists():
    tabel = pd.read_csv(FILE_PERBANDINGAN).set_index("Model")
    baris = ""
    for nama, r in tabel.iterrows():
        kelas_baris = ' class="terbaik"' if nama == NAMA_MODEL else ""
        baris += (f"<tr{kelas_baris}><td>{nama}</td><td>{persen(r['Accuracy'], 2)}</td>"
                  f"<td>{persen(r['F1-Score'], 2)}</td><td>{angka(r['Waktu Prediksi (ms/citra)'], 1)}</td>"
                  f"<td>{angka(r['Ukuran Bobot (MB)'], 1)}</td></tr>")
    st.markdown(f"""
    <table class="tabel-banding">
        <tr><th>Model</th><th>Accuracy</th><th>F1-Score</th><th>Prediksi (ms/citra)</th><th>Bobot (MB)</th></tr>
        {baris}
    </table>
    """, unsafe_allow_html=True)

    akurasi = tabel["Accuracy"]
    lain = akurasi.drop(NAMA_MODEL)
    selisih = ", ".join(f"{angka((akurasi[NAMA_MODEL] - v) * 100)} poin dari {n}" for n, v in lain.items())
    st.write(
        f"Pada data test yang sama, {NAMA_MODEL} mendapat akurasi tertinggi ({persen(akurasi[NAMA_MODEL], 2)}), "
        f"unggul {selisih}. Bobotnya memang lebih besar dari EfficientNetV2B0, tetapi waktu prediksinya hampir sama, "
        "dan selisih akurasinya lebih dari 2 poin, jadi ConvNeXtTiny dipilih untuk aplikasi."
    )
else:
    st.caption("Tabel perbandingan belum ada (file tabel_perbandingan.csv di folder model/).")

# grafik dari proses training, kalau filenya ada
if GRAFIK_TRAINING.exists() or CONFUSION_MATRIX.exists():
    tab1, tab2 = st.tabs(["Grafik training", "Confusion matrix"])
    with tab1:
        if GRAFIK_TRAINING.exists():
            st.image(str(GRAFIK_TRAINING), width="stretch")
    with tab2:
        if CONFUSION_MATRIX.exists():
            st.image(str(CONFUSION_MATRIX), width="stretch")

label("Tentang Grad-CAM")
st.write(
    "Grad-CAM (Selvaraju dkk., 2017) menunjukkan bagian gambar yang paling memengaruhi keputusan model. "
    "Caranya: hitung gradien skor penulis yang diprediksi terhadap peta fitur terakhir ConvNeXtTiny, "
    "rata-ratakan jadi bobot tiap channel, lalu jumlahkan peta fitur sesuai bobotnya. Hasilnya dibesarkan "
    "dan ditempel di atas gambar sebagai heatmap. Merah/kuning berarti area itu paling berpengaruh."
)
