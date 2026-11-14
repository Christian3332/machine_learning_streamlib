import json
import time

import numpy as np
import streamlit as st
import keras

from utils.config import FILE_MODEL, FILE_KELAS, NAMA_MODEL, TINGGI, LEBAR, AMBANG_DIKENALI
from utils.preprocess import proses_gambar, ke_batch
from utils.gradcam import hitung_heatmap, buat_overlay


def model_tersedia():
    return FILE_MODEL.exists() and FILE_KELAS.exists()


# model cukup dimuat sekali, setelah itu disimpan di cache Streamlit
# prediksi pertama biasanya lambat, jadi dipanaskan dulu pakai gambar kosong
@st.cache_resource(show_spinner="Memuat model ConvNeXtTiny...")
def muat_model():
    model = keras.models.load_model(FILE_MODEL, compile=False)
    kelas = json.loads(FILE_KELAS.read_text())
    if model.output_shape[-1] != len(kelas):
        raise ValueError("Jumlah kelas di model tidak sama dengan kelas.json, cek lagi file di folder model/")
    model.predict(np.zeros((1, TINGGI, LEBAR, 3), dtype="float32"), verbose=0)
    return model, kelas


def identifikasi(img):
    model, kelas = muat_model()

    # preprocessing + prediksi, waktunya dihitung
    mulai = time.perf_counter()
    crop, masukan, posisi = proses_gambar(img)
    x = ke_batch(masukan)
    prob = model.predict(x, verbose=0)[0]
    waktu = time.perf_counter() - mulai

    # ambil 3 teratas, cek lolos ambang atau tidak
    urutan = np.argsort(prob)[::-1][:3]
    top = [{"penulis": kelas[i], "confidence": float(prob[i])} for i in urutan]
    dikenali = top[0]["confidence"] >= AMBANG_DIKENALI

    # Grad-CAM untuk kelas dengan confidence tertinggi
    cam = hitung_heatmap(model, x, int(urutan[0]))
    overlay = buat_overlay(cam, crop, posisi)

    hasil = {
        "status": "dikenali" if dikenali else "tidak_dikenali",
        "penulis": top[0]["penulis"] if dikenali else None,
        "confidence": top[0]["confidence"],
        "top": top,
        "ambang": AMBANG_DIKENALI,
        "waktu_prediksi": waktu,
        "model": NAMA_MODEL,
    }
    return hasil, crop, overlay
