# Gesture Control System (AI Spotify Controller)

**Computer Vision Project • Group 8**

![Computer Vision Project](https://img.shields.io/badge/Computer_Vision-Project-blue?style=for-the-badge\&logo=opencv) ![Python](https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge\&logo=python) ![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange?style=for-the-badge\&logo=tensorflow) ![Flask](https://img.shields.io/badge/Flask-Web_App-green?style=for-the-badge\&logo=flask)

Aplikasi pengontrol musik berbasis web yang menggunakan **Computer Vision** dan **Artificial Intelligence (AI)** untuk mendeteksi gerakan tangan pengguna melalui webcam secara real-time. Dibangun dengan antarmuka modern (Dark Mode) yang mirip Spotify.

---

## Ringkasan

Aplikasi ini mendeteksi gesture tangan (real-time) menggunakan MediaPipe + model AI (TensorFlow/Keras) untuk mengontrol pemutaran musik: play, pause, next, prev, dan pengaturan volume (pinch). UI web responsif menampilkan visual feedback dan tutorial overlay agar interaksi lebih aman dan intuitif.

Repo: `https://github.com/Udang-Lari/Computer_Vision_AoL.git`

---

## Fitur Utama

* **Real-time Hand Tracking**: MediaPipe untuk deteksi landmark tangan dengan presisi.
* **Custom AI Model**: Deep Learning (TensorFlow/Keras) untuk mengenali 5 gesture.
* **Smart Volume Control**: Logika hibrida (AI + geometri) untuk pengaturan volume lewat gesture pinch.
* **Visual Feedback**: Loading bar visual saat gesture terdeteksi (mengurangi false positive).
* **Modern UI**: Tema Dark Mode, cover album otomatis, dan tutorial overlay.

---

## Panduan Gesture

Sistem mengenali 5 perintah utama:

|                  Gesture                 | Perintah   | Deskripsi                                           |
| :--------------------------------------: | :--------- | :-------------------------------------------------- |
|          🖐️ **5 Jari Terbuka**          | **PLAY**   | Memulai pemutaran lagu.                             |
|        ✊ **Kepalan + Kelingking**        | **PAUSE**  | Menghentikan lagu sementara.                        |
|     🤏 **Cubit (Jempol & Telunjuk)**     | **VOLUME** | Atur volume; jarak dekat → mute, jarak jauh → 100%. |
|          ✌️ **Huruf V (2 jari)**         | **NEXT**   | Putar lagu selanjutnya.                             |
| 🤟 **Angka 3 (telunjuk, tengah, manis)** | **PREV**   | Putar lagu sebelumnya.                              |

---

## Cara Merekam Data Baru (Data Collection)

Jika ingin melatih ulang model AI agar lebih akurat mengenali gesture tangan, ikuti langkah berikut.

### 1. Jalankan Script Perekam

Pastikan Anda berada di environment yang sesuai.

```bash
# Mac: gunakan environment cv_data
# Windows: gunakan environment utama
python collect_data.py
```

### 2. Instruksi Perekaman Gesture

Setelah script dijalankan, jendela kamera akan terbuka.
Tahan tombol keyboard berikut sambil menggerakkan tangan di depan kamera:

| Tombol | Gesture | Fungsi                                                                  |
| -----: | :------ | :---------------------------------------------------------------------- |
|  **0** | IDLE    | Gerakan acak atau diam (penting agar AI mengenali kondisi non-perintah) |
|  **1** | PAUSE   | Kepalan tangan + kelingking                                                         |
|  **2** | PLAY    | Lima jari terbuka                                                       |
|  **3** | NEXT    | Gesture huruf V (peace)                                                 |
|  **4** | PREV    | Tiga jari terbuka                                                       |

---

### Tips Perekaman

* Rekam **±500–1000 data per gesture** untuk hasil yang lebih stabil
* Variasikan posisi tangan:

  * Kiri / kanan
  * Jarak dekat / jauh
  * Sudut kamera berbeda
* Tekan tombol **`Q`** untuk menyimpan data dan keluar dari aplikasi
  
---

## Struktur Project & Dependencies

Project dibagi menjadi **3 modul/kernel** untuk menghindari bentrokan library (penting di Mac Apple Silicon).

### Modul 1 - Pengumpulan Data (`collect_data.py`)

* **Environment:** `cv_data`
* **Library:** OpenCV, MediaPipe, NumPy
* **Fungsi:** Menangkap frame webcam, mengekstrak koordinat landmark tangan, menyimpan ke `gesture_data.csv`

* Modul 1.5 - Pembersihan & Editing Dataset (edit_file_csv.ipynb)
* **Environment:** cv_data
* **Library:** Pandas
* **Fungsi:** Membersihkan dataset gesture dengan menghapus label tertentu sebelum pengambilan data ulang, serta menghasilkan file CSV baru yang siap digunakan untuk training berikutnya.

### Modul 2 - Training AI (`train_model.py`)

* **Environment:** `cv_train`
* **Library:** TensorFlow, Pandas, Scikit-Learn, NumPy
* **Fungsi:** Membaca CSV, preprocessing, melatih Neural Network, output `gesture_model.h5`

### Modul 3 - Aplikasi Utama (`main.py`)

* **Environment:** `cv_final`
* **Library:** Flask, OpenCV, MediaPipe, TensorFlow, NumPy
* **Fungsi:** Menjalankan web server + inference model + UI interaktif
* **Default URL:** `http://127.0.0.1:5001`

---

## Cara Install & Menjalankan

### 1) Clone repository

```bash
git clone https://github.com/Udang-Lari/Computer_Vision_AoL.git
cd Computer_Vision_AoL
```

---

### Opsi A - Pengguna Windows (All-in-One)

Windows biasanya bisa menjalankan semua script dalam satu environment.

```bash
pip install -r requirements.txt
python main.py
```

---

### Opsi B - Pengguna Mac (M1/M2/M3) - *Direkomendasikan: Pisah environment (Conda)*

> Untuk menghindari konflik TensorFlow / MediaPipe.

**1. Buat & aktifkan environment untuk training**

```bash
conda create -n cv_train python=3.9 -y
conda activate cv_train
pip install -r requirements_train.txt   # (jika ada file terpisah) atau pip install -r requirements.txt
python train_model.py
# Output: gesture_model.h5
```

**2. Jalankan aplikasi utama**

```bash
conda create -n cv_final python=3.9 -y
conda activate cv_final
pip install -r requirements.txt
python main.py
```

> Jika `requirements.txt` berisi semua dependency, pastikan environment yang digunakan kompatibel (khususnya TensorFlow dan MediaPipe).

---

## Struktur Folder (contoh)

```
CV_FINAL/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── music/
│   ├── covers/
│   └── tutorial/
│
├── templates/
│   └── index.html
│
├── collect_data.py
├── train_model.py
├── main.py
├── gesture_data.csv
├── gesture_model.h5
├── requirements.txt
└── README.md
```

---

## Best Practices & Catatan

* Simpan `gesture_model.h5` yang sudah dilatih untuk deployment, jangan latih model di runtime produksi.
* Sertakan tutorial overlay di UI ketika user pertama kali mengakses untuk mengurangi false-positive.
* Dokumentasikan versi Python & versi library di `requirements.txt` agar reproduktif.

---

## Authors

* **Group 8:**
  - AKMAL HENDRIAN MALIK
  - KENNETH NATHANAEL YUWONO
  - NICHOLAS TRISTAN
  - LOUIS RUISANI
* Repo: `https://github.com/Udang-Lari/Computer_Vision_AoL.git`
