import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os
import folium
from streamlit_folium import st_folium


# -----------------------
# Config & Load Model + Encoder
# -----------------------
st.set_page_config(page_title="🚨 Dashboard Sensor Pertambangan", layout="wide")
model = joblib.load("model_sensor.pkl")
le = joblib.load("label_encoder.pkl")

# -----------------------
# Definisi Lokasi Tambang
# -----------------------
lokasi_tambang = {
    "Grasberg Open Pit": {"lat": -4.05602, "lon": 137.11320},
    "DMLZ": {"lat": -4.06790, "lon": 137.11050},
    "DOZ": {"lat": -4.07800, "lon": 137.11700},
    "Big Gossan": {"lat": -4.07080, "lon": 137.10460},
    "Kucing Liar": {"lat": -4.04900, "lon": 137.12700},
    "Batu Hijau (NTB)": {"lat": -8.2000, "lon": 117.5000},
    "Tambang Martabe (Sumut)": {"lat": 1.6000, "lon": 99.2000},
    "Adaro (Kalsel)": {"lat": -2.7000, "lon": 115.4300},
    "KPC (Kaltim)": {"lat": 0.5600, "lon": 117.5600},
    "Pongkor (Jabar)": {"lat": -6.5580, "lon": 106.5826}
}

# -----------------------
# File CSV Data Sensor
# -----------------------
CSV_PATH = "sensor_data.csv"
if not os.path.exists(CSV_PATH):
    pd.DataFrame(columns=["timestamp", "lokasi", "getaran", "suhu", "tekanan", "kelembapan", "status"])\
        .to_csv(CSV_PATH, index=False)

# Load data
data = pd.read_csv(CSV_PATH)
if "timestamp" in data.columns and not data["timestamp"].isnull().all():
    try:
        data["timestamp"] = pd.to_datetime(data["timestamp"])
    except Exception:
        pass

# -----------------------
# Fungsi Kirim Email Alert
# -----------------------
def send_email_alert(getaran, suhu, tekanan, kelembapan, timestamp):
    sender_email = "ilham030918@gmail.com"
    app_password = "lpilewfghbkiobps"
    receiver_email = "ilham030918@gmail.com"
    subject = "🚨 ALERT BAHAYA Sensor"

    body = f"""
PERHATIAN‼️

Status: *BAHAYA*
Waktu: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Getaran: {getaran} g
Suhu: {suhu} °C
Tekanan: {tekanan} bar
Kelembapan: {kelembapan} %

Segera lakukan pemeriksaan!
"""
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        return True, "✅ Email BAHAYA berhasil dikirim."
    except Exception as e:
        return False, f"❌ Gagal mengirim email: {e}"

# -----------------------
# Fungsi Warna Status
# -----------------------
def warna_status(s):
    if pd.isna(s):
        return "gray"
    s = str(s).lower()
    if s.startswith("bahaya"):
        return "red"
    elif "perlu" in s:
        return "orange"
    else:
        return "green"

# -----------------------
# Session State Default
# -----------------------
if "lokasi" not in st.session_state:
    st.session_state.lokasi = sorted(list(lokasi_tambang.keys()))[0]

if "getaran" not in st.session_state:
    st.session_state.getaran = 0.5
if "suhu" not in st.session_state:
    st.session_state.suhu = 35
if "tekanan" not in st.session_state:
    st.session_state.tekanan = 1.2
if "kelembapan" not in st.session_state:
    st.session_state.kelembapan = 45

# -----------------------
# Header: Judul + Waktu + Refresh
# -----------------------
col_a, col_b = st.columns([2,3])
with col_a:
    st.title("🚨 Dashboard Sensor Pertambangan")
with col_b:
   import streamlit as st
import sys

with col_b:
    st.markdown(f"**Waktu sekarang:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.button("🔄 Refresh waktu"):
        # Restart aplikasi dengan keluar dan panggil ulang skrip
        sys.exit()



st.markdown("---")

# -----------------------
# Input Data Sensor + Lokasi (Kiri)
# + Status Terakhir Lokasi (Kanan)
# -----------------------
left, right = st.columns([3,2])

with left:
    st.subheader("Masukkan Data Sensor")
    st.session_state.getaran = st.slider("Getaran (g)", 0.0, 2.0, st.session_state.getaran, 0.1)
    st.session_state.suhu = st.slider("Suhu (°C)", 0, 100, st.session_state.suhu, 1)
    st.session_state.tekanan = st.slider("Tekanan (Bar)", 0.0, 5.0, st.session_state.tekanan, 0.1)
    st.session_state.kelembapan = st.slider("Kelembapan (%)", 0, 100, st.session_state.kelembapan, 1)

    st.subheader("Pilih Lokasi")
    st.session_state.lokasi = st.selectbox(
        "🏭 Lokasi Tambang", 
        sorted(lokasi_tambang.keys()), 
        index=sorted(lokasi_tambang.keys()).index(st.session_state.lokasi)
    )

    if st.button("🔍 Prediksi & Simpan ke CSV"):
        features_df = pd.DataFrame([{
            "getaran": st.session_state.getaran,
            "suhu": st.session_state.suhu,
            "tekanan": st.session_state.tekanan,
            "kelembapan": st.session_state.kelembapan
        }])
        pred = model.predict(features_df)
        status_now = le.inverse_transform(pred)[0]
        ts = datetime.now()

        new_row = {
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "lokasi": st.session_state.lokasi,
            "getaran": st.session_state.getaran,
            "suhu": st.session_state.suhu,
            "tekanan": st.session_state.tekanan,
            "kelembapan": st.session_state.kelembapan,
            "status": status_now
        }

        # Reload dan append untuk mengurangi race condition
        df_all = pd.read_csv(CSV_PATH)
        df_all = pd.concat([df_all, pd.DataFrame([new_row])], ignore_index=True)
        df_all.to_csv(CSV_PATH, index=False)

        st.success(f"Prediksi: **{status_now}** — Data tersimpan untuk lokasi **{st.session_state.lokasi}**.")

        if str(status_now).lower().startswith("bahaya"):
            st.markdown(
                """
                <audio autoplay>
                <source src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" type="audio/mpeg">
                </audio>
                """,
                unsafe_allow_html=True
            )
            ok, msg = send_email_alert(
                st.session_state.getaran, 
                st.session_state.suhu, 
                st.session_state.tekanan, 
                st.session_state.kelembapan, 
                ts
            )
            if ok:
                st.info(msg)
            else:
                st.error(msg)

with right:
    st.subheader("Status Terakhir (Lokasi terpilih)")
    data = pd.read_csv(CSV_PATH)
    if "timestamp" in data.columns:
        try:
            data["timestamp"] = pd.to_datetime(data["timestamp"])
        except Exception:
            pass

    data_lokasi = data[data["lokasi"] == st.session_state.lokasi].copy()
    if not data_lokasi.empty:
        last = data_lokasi.sort_values("timestamp").iloc[-1]
        st.write(f"**Lokasi:** {last['lokasi']}")
        st.write(f"**Waktu:** {last['timestamp']}")
        st.write(f"**Status:** {last['status']}")
        st.write(f"Getaran: {last['getaran']} g")
        st.write(f"Suhu: {last['suhu']} °C")
        st.write(f"Tekanan: {last['tekanan']} bar")
        st.write(f"Kelembapan: {last['kelembapan']} %")
    else:
        st.info("Belum ada data untuk lokasi terpilih. Tekan 'Prediksi & Simpan' untuk menambahkan data.")

st.markdown("---")

# -----------------------
# Forecast & Grafik Historis per Lokasi
# -----------------------
st.header("📅 Prediksi Tren & Grafik Historis (per lokasi)")

data = pd.read_csv(CSV_PATH)
if "timestamp" in data.columns:
    try:
        data["timestamp"] = pd.to_datetime(data["timestamp"])
    except Exception:
        pass

lok = st.session_state.lokasi
df_loc = data[data["lokasi"] == lok].sort_values("timestamp").reset_index(drop=True)

sensor_for_forecast = st.selectbox("Pilih sensor untuk forecasting/grafik:", ("getaran", "suhu", "tekanan", "kelembapan"))

if df_loc.shape[0] >= 5:
    X = np.arange(len(df_loc)).reshape(-1, 1)
    y = df_loc[sensor_for_forecast].astype(float).values
    lr = LinearRegression().fit(X, y)

    future_X = np.arange(len(df_loc), len(df_loc) + 50).reshape(-1, 1)
    future_y = lr.predict(future_X)

    batas_map = {"getaran": 1.5, "suhu": 80, "tekanan": 4.0, "kelembapan": 90}
    batas = batas_map[sensor_for_forecast]
    crossing_idx = next((i for i, v in enumerate(future_y) if v >= batas), None)

    col1, col2 = st.columns(2)
    col1.metric("Data Titik", f"{len(df_loc)} titik")
    if crossing_idx is not None:
        col2.warning(f"Perkiraan melewati batas dalam {crossing_idx} jam")
    else:
        col2.success("Aman dalam 50 jam ke depan")

    fig, ax = plt.subplots()
    ax.plot(df_loc["timestamp"], y, marker="o", label="Historis")
    ax.plot(pd.date_range(df_loc["timestamp"].iloc[-1], periods=50, freq="H"), future_y, linestyle="--", label="Forecast")
    ax.axhline(batas, color="red", linestyle=":", label="Threshold")
    ax.set_xlabel("Waktu")
    ax.set_ylabel(sensor_for_forecast.capitalize())
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("Butuh minimal 5 titik data historis per lokasi untuk membuat prediksi tren.")

st.markdown("---")

# -----------------------
# Grafik Semua Sensor untuk Lokasi Terpilih
# -----------------------
st.header(f"📈 Tren Semua Sensor — {lok}")

if not df_loc.empty:
    fig2, ax2 = plt.subplots(figsize=(8,4))
    colors = {"getaran":"orange","suhu":"red","tekanan":"blue","kelembapan":"green"}
    for col in ["getaran","suhu","tekanan","kelembapan"]:
        ax2.plot(df_loc["timestamp"], df_loc[col].astype(float), marker="o", label=col.capitalize(), color=colors[col])
    ax2.set_xlabel("Waktu")
    ax2.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig2)
else:
    st.info("Belum ada data historis untuk lokasi ini.")

st.dataframe(df_loc.tail(20))

st.markdown("---")

# -----------------------
# Peta Lokasi dengan Status Terakhir
# -----------------------
st.header("📍 Peta Lokasi Tambang (status terakhir per lokasi)")

data_all = pd.read_csv(CSV_PATH)
if "timestamp" in data_all.columns:
    try:
        data_all["timestamp"] = pd.to_datetime(data_all["timestamp"])
    except Exception:
        pass

latest = data_all.sort_values("timestamp").groupby("lokasi").tail(1).set_index("lokasi")

map_center = [-2.5, 117.0]
m = folium.Map(location=map_center, zoom_start=5)

for name, info in lokasi_tambang.items():
    lat = info["lat"]
    lon = info["lon"]
    if name in latest.index:
        s = latest.loc[name, "status"]
        ts = latest.loc[name, "timestamp"]
        popup = f"<b>{name}</b><br>Status: {s}<br>Waktu: {ts}"
        color = warna_status(s)
    else:
        popup = f"<b>{name}</b><br>Status: (belum ada data)"
        color = "gray"
    folium.Marker(
        [lat, lon],
        popup=popup,
        icon=folium.Icon(color=color, icon="industry", prefix='fa')
    ).add_to(m)

st_folium(m, width=900, height=500)

st.markdown("---")


# -----------------------
# Footer
# -----------------------
footer_style = """
<style>
.footer {
    margin-top: 50px;
    padding: 20px 10px;
    text-align: center;
    color: #888888;
    font-size: 14px;
    border-top: 1px solid #e6e6e6;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.footer a {
    color: #1f77b4;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>
"""

footer_html = f"""
<div class="footer">
    🚧 Dashboard Sensor Pertambangan &mdash; dibuat oleh <strong>Ilhamdi Taufik</strong><br>
    Sebagai proyek pengembangan dan monitoring sensor tambang menggunakan AI & Data Visualization.<br>
    © {datetime.now().year} Ilhamdi Taufik. Semua hak cipta dilindungi.
</div>
"""

st.markdown(footer_style + footer_html, unsafe_allow_html=True)
