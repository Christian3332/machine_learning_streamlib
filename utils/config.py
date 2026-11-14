from pathlib import Path

# lokasi folder di dalam project
FOLDER_UTAMA = Path(__file__).resolve().parent.parent
FOLDER_MODEL = FOLDER_UTAMA / "model"
FOLDER_RIWAYAT = FOLDER_UTAMA / "riwayat"
FOLDER_GAMBAR_RIWAYAT = FOLDER_RIWAYAT / "gambar"
FILE_RIWAYAT = FOLDER_RIWAYAT / "riwayat.json"

# file hasil training dari Colab, taruh semuanya di folder model/
FILE_MODEL = FOLDER_MODEL / "penulis_convnexttiny.keras"
FILE_KELAS = FOLDER_MODEL / "kelas.json"
FILE_METRIK = FOLDER_MODEL / "metrics.json"
FILE_SPLIT = FOLDER_MODEL / "ringkasan_split.json"
FILE_PERBANDINGAN = FOLDER_MODEL / "tabel_perbandingan.csv"
GRAFIK_TRAINING = FOLDER_MODEL / "grafik_training.png"
CONFUSION_MATRIX = FOLDER_MODEL / "confusion_matrix.png"

# harus sama dengan pengaturan di notebook training
NAMA_MODEL = "ConvNeXtTiny"
TINGGI = 224
LEBAR = 672

# confidence di bawah ambang ini dianggap "Tidak Dikenali"
AMBANG_DIKENALI = 0.5

FORMAT_DIIZINKAN = {"JPEG", "PNG", "MPO"}
EKSTENSI_GAMBAR = ["jpg", "jpeg", "png"]
