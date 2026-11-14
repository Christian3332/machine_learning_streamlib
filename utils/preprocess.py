import io

import cv2
import numpy as np
from PIL import Image, ImageOps

from utils.config import TINGGI, LEBAR, FORMAT_DIIZINKAN


# cek file benar-benar gambar JPG/PNG, bukan cuma ganti ekstensi
def gambar_valid(isi_file):
    try:
        img = Image.open(io.BytesIO(isi_file))
        img.verify()
        return img.format in FORMAT_DIIZINKAN
    except Exception:
        return False


# buka gambar dari bytes, putar sesuai EXIF (foto HP sering kebalik)
def buka_dari_bytes(isi_file):
    img = Image.open(io.BytesIO(isi_file))
    return ImageOps.exif_transpose(img).convert("RGB")


# crop manual dari slider, nilainya dalam persen
def crop_manual(img, kiri, kanan, atas, bawah):
    w, h = img.size
    return img.crop((int(w * kiri / 100), int(h * atas / 100), int(w * kanan / 100), int(h * bawah / 100)))


# ubah ke grayscale, gambar yang terlalu besar diperkecil dulu
def buka_gambar(img):
    gray = np.array(img.convert("L"))
    if max(gray.shape) > 2000:
        skala = 2000 / max(gray.shape)
        gray = cv2.resize(gray, None, fx=skala, fy=skala, interpolation=cv2.INTER_AREA)
    return gray


# latar kertas ditebak pakai median blur lalu dibagi, jadi bayangan foto hilang
def ratakan_cahaya(gray):
    latar = cv2.medianBlur(gray, 31)
    return cv2.divide(gray, latar, scale=255)


# cari kotak area yang ada tintanya, sisakan margin 4 piksel
def cari_area_tulisan(gray):
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    tinta = mask > 0
    h, w = gray.shape
    baris = np.where(tinta.sum(axis=1) > max(2, 0.002 * w))[0]
    kolom = np.where(tinta.sum(axis=0) > max(2, 0.002 * h))[0]
    if len(baris) == 0 or len(kolom) == 0:
        return 0, h, 0, w
    y1, y2 = max(0, baris[0] - 4), min(h, baris[-1] + 5)
    x1, x2 = max(0, kolom[0] - 4), min(w, kolom[-1] + 5)
    return y1, y2, x1, x2


# balik warna, kecilkan tanpa merusak rasio, taruh di tengah kanvas hitam 224 x 672
def siapkan_input(crop):
    h, w = crop.shape
    skala = min(TINGGI / h, LEBAR / w)
    th, tw = max(1, round(h * skala)), max(1, round(w * skala))
    cara = cv2.INTER_AREA if skala < 1 else cv2.INTER_LINEAR
    kecil = cv2.resize(255 - crop, (tw, th), interpolation=cara)
    kanvas = np.zeros((TINGGI, LEBAR), dtype=np.uint8)
    atas, kiri = (TINGGI - th) // 2, (LEBAR - tw) // 2
    kanvas[atas:atas + th, kiri:kiri + tw] = kecil
    return kanvas, (atas, kiri, th, tw)


# semua langkah di atas digabung, urutannya sama dengan notebook training
def proses_gambar(img):
    gray = ratakan_cahaya(buka_gambar(img))
    y1, y2, x1, x2 = cari_area_tulisan(gray)
    crop = gray[y1:y2, x1:x2]
    masukan, posisi = siapkan_input(crop)
    return crop, masukan, posisi


# model butuh 3 channel dan ada dimensi batch
def ke_batch(masukan):
    x = np.repeat(masukan[None, :, :, None], 3, axis=-1)
    return x.astype("float32")
