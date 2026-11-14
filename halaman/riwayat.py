import streamlit as st

from utils.riwayat_lokal import baca_riwayat, hapus_riwayat, hapus_semua_riwayat, path_gambar
from utils.tampilan import badge_status, format_tanggal, persen, tampilkan_hasil


@st.dialog("Detail hasil", width="large")
def lihat_detail(item):
    st.caption(f"Diidentifikasi pada {format_tanggal(item['waktu'])}")
    tampilkan_hasil(item)


# konfirmasi dulu sebelum hapus, item=None artinya hapus semua
@st.dialog("Hapus riwayat")
def konfirmasi_hapus(item=None):
    if item is None:
        st.write("Semua riwayat beserta gambarnya akan dihapus. Lanjutkan?")
    else:
        nama = item["penulis"] or "Tidak Dikenali"
        st.write(f"Riwayat **{nama}** ({format_tanggal(item['waktu'])}) akan dihapus. Lanjutkan?")

    batal, ya = st.columns(2)
    if batal.button("Batal", width="stretch"):
        st.rerun()
    if ya.button("Hapus", key="tombol_hapus_ya", width="stretch"):
        if item is None:
            hapus_semua_riwayat()
        else:
            hapus_riwayat(item["id"])
        st.rerun()


daftar = baca_riwayat()

judul, tombol = st.columns([3, 1.3], vertical_alignment="center")
judul.markdown("### Riwayat")
if daftar and tombol.button("Hapus semua", icon=":material/delete_sweep:", width="stretch"):
    konfirmasi_hapus()

if not daftar:
    st.info("Belum ada riwayat. Hasil dari halaman Identifikasi akan otomatis tersimpan di sini.")
    st.stop()

st.caption(f"{len(daftar)} hasil identifikasi tersimpan, yang terbaru di paling atas.")

# satu kartu untuk satu hasil: thumbnail, penulis, confidence, tanggal, tombol detail & hapus
for item in daftar:
    dikenali = item["status"] == "dikenali"
    nama = item["penulis"] if dikenali else "Tidak Dikenali"
    with st.container(border=True, key=f"kartu_riwayat_{item['id']}"):
        gambar, teks, aksi = st.columns([1.5, 2.6, 1.2], vertical_alignment="center")
        gambar.image(path_gambar(item["crop"]), width="stretch")
        teks.markdown(f"""
        <p style="font-size:1.15rem; font-weight:600; margin:0">{nama}</p>
        <p class="teks-redup" style="margin:2px 0">Confidence {persen(item['confidence'])} · {format_tanggal(item['waktu'])}</p>
        {badge_status(dikenali)}
        """, unsafe_allow_html=True)
        with aksi:
            if st.button("Detail", key=f"detail_{item['id']}", icon=":material/visibility:", width="stretch"):
                lihat_detail(item)
            if st.button("Hapus", key=f"hapus_{item['id']}", icon=":material/delete:", width="stretch"):
                konfirmasi_hapus(item)
