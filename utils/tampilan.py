import streamlit as st

from utils.riwayat_lokal import path_gambar

HIJAU = "#2ECC71"
ABU = "#9E9E9E"
ORANYE = "#FFB74D"
NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


# CSS tambahan biar tampilannya mirip desain: kotak upload putus-putus, kartu gelap, bar hijau
def pasang_css():
    st.html("""
    <style>
    [data-testid="stSidebarNav"]::before {
        content: "Cek penulis";
        display: block;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 0.2rem 0 1rem 0.75rem;
        color: #FFFFFF;
    }
    .st-key-kotak_upload {
        border: 1.5px dashed #4A4A4A !important;
        border-radius: 14px;
    }
    .st-key-kotak_upload [data-testid="stFileUploaderDropzone"] {
        background: #1A1A1A;
        border: 1px solid #2C2C2C;
    }
    [class*="st-key-kartu"] {
        background: #1E1E1E;
        border-radius: 12px;
    }
    .st-key-tombol_hapus_ya button {
        background: #E57373;
        border-color: #E57373;
        color: #151515;
    }
    .label-kecil { color: #9E9E9E; font-size: 0.9rem; margin: 0.4rem 0 0.2rem 0; }
    .teks-redup { color: #9E9E9E; font-size: 0.85rem; }
    .judul-upload { font-size: 1.15rem; font-weight: 500; margin: 0; }
    .badge {
        display: inline-block; padding: 2px 10px; border-radius: 6px;
        font-size: 0.85rem; font-weight: 600;
    }
    .badge.hijau { background: rgba(46, 204, 113, 0.15); color: #2ECC71; }
    .badge.oranye { background: rgba(255, 183, 77, 0.15); color: #FFB74D; }
    .baris-judul { display: flex; justify-content: space-between; align-items: center; }
    .pred { margin: 0.55rem 0; }
    .pred-atas { display: flex; justify-content: space-between; font-size: 0.95rem; }
    .jalur { height: 8px; background: #2C2C2C; border-radius: 4px; margin-top: 4px; overflow: hidden; }
    .isi { height: 100%; border-radius: 4px; }
    .penulis-besar { font-size: 1.9rem !important; font-weight: 700; line-height: 1.3; }
    .info-bawah { color: #9E9E9E; font-size: 0.9rem; display: flex; gap: 1.2rem; flex-wrap: wrap; }
    .tabel-banding { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    .tabel-banding th { color: #9E9E9E; font-weight: 500; text-align: left; padding: 6px 8px; border-bottom: 1px solid #2C2C2C; }
    .tabel-banding td { padding: 6px 8px; border-bottom: 1px solid #2C2C2C; }
    .tabel-banding tr.terbaik td { color: #2ECC71; font-weight: 600; }
    </style>
    """)


# format angka ala Indonesia: 0.873 -> 87,3%
def persen(nilai, desimal=1):
    return f"{nilai * 100:.{desimal}f}%".replace(".", ",")


def angka(nilai, desimal=2):
    return f"{nilai:.{desimal}f}".replace(".", ",")


def format_tanggal(teks):
    tanggal, jam = teks.split(" ")
    tahun, bulan, hari = tanggal.split("-")
    return f"{int(hari)} {NAMA_BULAN[int(bulan) - 1]} {tahun}, {jam[:5]}"


def label(teks):
    st.markdown(f'<p class="label-kecil">{teks}</p>', unsafe_allow_html=True)


def badge_status(dikenali):
    if dikenali:
        return '<span class="badge hijau">Dikenali</span>'
    return '<span class="badge oranye">Tidak Dikenali</span>'


# bar tiga teratas, bar pertama hijau, sisanya abu-abu
def html_tiga_teratas(top):
    isi = ""
    for i, p in enumerate(top):
        warna = HIJAU if i == 0 else "#5A5A5A"
        isi += f"""
        <div class="pred">
            <div class="pred-atas"><span>{p['penulis']}</span><span>{persen(p['confidence'])}</span></div>
            <div class="jalur"><div class="isi" style="width:{p['confidence'] * 100:.1f}%; background:{warna};"></div></div>
        </div>"""
    return isi


# tampilan hasil dipakai di halaman identifikasi dan di detail riwayat
def tampilkan_hasil(item):
    dikenali = item["status"] == "dikenali"
    pertama = item["top"][0]

    # ringkasan: siapa penulisnya atau tidak dikenali
    with st.container(border=True, key=f"kartu_ringkas_{item['id']}"):
        if dikenali:
            st.markdown(f"""
            <p class="teks-redup">Penulis teridentifikasi</p>
            <div class="baris-judul"><span class="penulis-besar">{item['penulis']}</span>{badge_status(True)}</div>
            <p class="teks-redup">Confidence {persen(item['confidence'])}</p>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <p class="teks-redup">Penulis teridentifikasi</p>
            <div class="baris-judul"><span class="penulis-besar" style="color:{ORANYE}">Tidak Dikenali</span>{badge_status(False)}</div>
            <p class="teks-redup">Confidence tertinggi {persen(pertama['confidence'])} ({pertama['penulis']}) masih di bawah
            ambang {persen(item['ambang'], 0)}, jadi hasilnya tidak dipaksakan sebagai identitas yang pasti.</p>
            """, unsafe_allow_html=True)

    # gambar setelah preprocessing (area tulisan saja)
    label("Hasil crop")
    with st.container(border=True, key=f"kartu_crop_{item['id']}"):
        st.image(path_gambar(item["crop"]), width="stretch")

    # kiri tiga teratas, kanan Grad-CAM
    kiri, kanan = st.columns(2, gap="medium")
    with kiri:
        st.markdown(f"""
        <div class="baris-judul"><p class="label-kecil">Tiga teratas</p>{badge_status(dikenali)}</div>
        {html_tiga_teratas(item['top'])}
        """, unsafe_allow_html=True)
    with kanan:
        label("Grad-CAM: area yang diperhatikan model")
        with st.container(border=True, key=f"kartu_gradcam_{item['id']}"):
            st.image(path_gambar(item["gradcam"]), width="stretch")
        st.caption("Warna merah/kuning = bagian tulisan yang paling berpengaruh ke keputusan model, "
                   "biru = kurang berpengaruh.")

    # info proses
    st.markdown(f"""
    <div class="info-bawah">
        <span>Waktu prediksi {angka(item['waktu_prediksi'])} detik</span>
        <span>Algoritma: {item['model']}</span>
        <span>Status: Berhasil</span>
    </div>
    """, unsafe_allow_html=True)

    # OCR belum ada, cuma disiapkan tempatnya
    with st.container(border=True, key=f"kartu_ocr_{item['id']}"):
        st.markdown("**Teks tulisan (OCR)**")
        st.caption("Fitur OCR belum tersedia. ConvNeXtTiny hanya mengenali gaya tulisan, bukan membaca isinya.")
