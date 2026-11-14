import cv2
import numpy as np
import tensorflow as tf
import keras

from utils.config import TINGGI, LEBAR


# ambil backbone ConvNeXtTiny yang ada di dalam model
def ambil_backbone(model):
    for layer in model.layers:
        if isinstance(layer, keras.Model):
            return layer
    raise ValueError("Backbone ConvNeXtTiny tidak ditemukan di dalam model")


# Grad-CAM: gradien skor kelas terhadap peta fitur terakhir ConvNeXt (7 x 21)
# skornya diambil sebelum softmax supaya gradien tidak hilang saat confidence tinggi
def hitung_heatmap(model, x, indeks_kelas):
    backbone = ambil_backbone(model)
    gap = model.get_layer("gap")
    dense = model.get_layer("prediksi")

    with tf.GradientTape() as tape:
        fitur = backbone(x, training=False)
        tape.watch(fitur)
        logit = tf.matmul(gap(fitur), dense.kernel) + dense.bias
        skor = logit[:, indeks_kelas]

    grad = tape.gradient(skor, fitur)
    bobot = tf.reduce_mean(grad, axis=(1, 2))
    cam = tf.nn.relu(tf.reduce_sum(fitur[0] * bobot[0], axis=-1)).numpy()
    if cam.max() > 0:
        cam = cam / cam.max()
    return cam


# heatmap dibesarkan ke ukuran input, dipotong bagian tulisannya, lalu ditempel di atas hasil crop
def buat_overlay(cam, crop, posisi):
    atas, kiri, tinggi, lebar = posisi
    cam = cv2.resize(cam, (LEBAR, TINGGI))
    cam = cam[atas:atas + tinggi, kiri:kiri + lebar]
    cam = cv2.resize(cam, (crop.shape[1], crop.shape[0]))

    heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
    dasar = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)
    overlay = cv2.addWeighted(dasar, 0.55, heatmap, 0.45, 0)
    return cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
