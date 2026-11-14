import json
import uuid
from datetime import datetime

import cv2

from utils.config import FILE_RIWAYAT, FOLDER_GAMBAR_RIWAYAT


# riwayat disimpan di riwayat/riwayat.json, gambarnya di riwayat/gambar/
# jadi tidak hilang walaupun aplikasi ditutup
def baca_riwayat():
    if not FILE_RIWAYAT.exists():
        return []
    try:
        return json.loads(FILE_RIWAYAT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def tulis_riwayat(daftar):
    FILE_RIWAYAT.parent.mkdir(parents=True, exist_ok=True)
    FILE_RIWAYAT.write_text(json.dumps(daftar, indent=2), encoding="utf-8")


# gambar yang lebarnya lebih dari 1200 px diperkecil biar folder riwayat tidak cepat penuh
def simpan_gambar(gambar, nama, rgb=False):
    if gambar.shape[1] > 1200:
        skala = 1200 / gambar.shape[1]
        gambar = cv2.resize(gambar, None, fx=skala, fy=skala, interpolation=cv2.INTER_AREA)
    if rgb:
        gambar = cv2.cvtColor(gambar, cv2.COLOR_RGB2BGR)
    FOLDER_GAMBAR_RIWAYAT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(FOLDER_GAMBAR_RIWAYAT / nama), gambar, [cv2.IMWRITE_JPEG_QUALITY, 90])


# hasil identifikasi + gambar crop + gambar Grad-CAM disimpan sebagai satu item
def tambah_riwayat(hasil, crop, overlay):
    id_item = uuid.uuid4().hex[:12]
    simpan_gambar(crop, f"{id_item}_crop.jpg")
    simpan_gambar(overlay, f"{id_item}_gradcam.jpg", rgb=True)

    item = dict(hasil)
    item["id"] = id_item
    item["waktu"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    item["crop"] = f"{id_item}_crop.jpg"
    item["gradcam"] = f"{id_item}_gradcam.jpg"

    daftar = baca_riwayat()
    daftar.insert(0, item)
    tulis_riwayat(daftar)
    return item


def hapus_gambar_item(item):
    for nama in (item.get("crop"), item.get("gradcam")):
        if nama:
            (FOLDER_GAMBAR_RIWAYAT / nama).unlink(missing_ok=True)


def hapus_riwayat(id_item):
    daftar = baca_riwayat()
    for item in daftar:
        if item["id"] == id_item:
            hapus_gambar_item(item)
    tulis_riwayat([item for item in daftar if item["id"] != id_item])


def hapus_semua_riwayat():
    for item in baca_riwayat():
        hapus_gambar_item(item)
    tulis_riwayat([])


def path_gambar(nama):
    return str(FOLDER_GAMBAR_RIWAYAT / nama)
