# 🚨 Dashboard Sensor Pertambangan

Dashboard interaktif untuk monitoring sensor di berbagai lokasi tambang di Indonesia menggunakan Streamlit, machine learning, dan visualisasi data.

## Deskripsi

Project ini merupakan aplikasi dashboard yang dapat digunakan untuk:

- Memasukkan data sensor seperti getaran, suhu, tekanan, dan kelembapan dari berbagai lokasi tambang.
- Memprediksi status kondisi tambang menggunakan model machine learning (Random Forest atau model lain yang telah dilatih).
- Menyimpan data hasil pengukuran dan prediksi ke file CSV.
- Mengirimkan email otomatis sebagai alert jika kondisi sensor menunjukkan status *Bahaya*.
- Menampilkan grafik tren historis sensor dan memproyeksikan forecasting nilai sensor dalam waktu mendatang.
- Memvisualisasikan lokasi tambang dan status terakhir dengan peta interaktif menggunakan Folium.
- Memberikan notifikasi suara dan tampilan status warna sesuai tingkat bahaya.

## Fitur Utama

- Input data sensor real-time dengan slider.
- Prediksi status kondisi tambang berbasis model ML yang sudah dilatih.
- Penyimpanan data sensor dan prediksi ke CSV.
- Pengiriman email alert otomatis saat kondisi berbahaya terdeteksi.
- Grafik historis dan forecasting tren sensor.
- Peta interaktif dengan status warna berdasarkan kondisi sensor.
- UI yang responsif dan mudah digunakan menggunakan Streamlit.

## Teknologi dan Library yang Digunakan

- Python 3.x
- Streamlit (web app interaktif)
- scikit-learn (model machine learning)
- Pandas & NumPy (manipulasi data)
- Matplotlib (visualisasi grafik)
- Folium & streamlit-folium (peta interaktif)
- smtplib (kirim email alert)
- joblib (load model dan label encoder)
