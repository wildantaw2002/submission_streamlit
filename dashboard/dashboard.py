import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Set style seaborn
sns.set(style='dark')

# Helper function untuk menyiapkan data yang dibutuhkan
def create_monthly_rentals_df(df):
    monthly_rentals = df.groupby('mnth', observed=False)['cnt'].sum().reset_index()
    return monthly_rentals

def create_weather_rentals_df(df):
    weather_rentals = df.groupby('weathersit', observed=False)['cnt'].mean().reset_index()
    weather_rentals = weather_rentals.dropna()
    return weather_rentals

# Load data
file_path = "main_data.csv"
if not os.path.exists(file_path):
    # Coba cari di path relatif jika dijalankan dari root
    file_path = "dashboard/main_data.csv"
    if not os.path.exists(file_path):
        st.error("Data main_data.csv tidak ditemukan.")
        st.stop()

day_df = pd.read_csv(file_path)

# Mengatur urutan bulan
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
day_df['mnth'] = pd.Categorical(day_df['mnth'], categories=months, ordered=True)

# Membuat komponen filter di sidebar
with st.sidebar:
    st.title("🚲 Bike Sharing Analytics")
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    st.header("Filter Data")
    
    # Filter Tahun
    year_options = {0: "2011", 1: "2012"}
    selected_year = st.selectbox(
        label="Pilih Tahun",
        options=list(year_options.keys()),
        format_func=lambda x: year_options[x],
        index=1 # default to 2012
    )

    # Filter Musim (Season)
    season_options = ["Semua Musim", "Spring", "Summer", "Fall", "Winter"]
    selected_season = st.selectbox(
        label="Pilih Musim",
        options=season_options,
        index=0 # default Semua
    )

# Memfilter data utama berdasarkan input sidebar
main_df = day_df[day_df['yr'] == selected_year]
if selected_season != "Semua Musim":
    main_df = main_df[main_df['season'] == selected_season]

# Data untuk visualisasi
monthly_rentals_df = create_monthly_rentals_df(main_df)
weather_rentals_df = create_weather_rentals_df(main_df)

# Header utama dashboard
st.header('Bike Sharing Dashboard 🚲')

# Row 1: Metrics
col1, col2 = st.columns(2)

with col1:
    total_rentals = main_df.cnt.sum()
    st.metric("Total Penyewaan Sepeda", value=f"{total_rentals:,}")

with col2:
    avg_rentals = main_df.cnt.mean()
    st.metric("Rata-rata Penyewaan Harian", value=f"{avg_rentals:,.2f}")

st.markdown("---")

# Row 2: Visualisasi Pertanyaan Bisnis 1
st.subheader(f"Tren Penyewaan Sepeda Bulanan ({year_options[selected_year]})")
fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(
    x="mnth", 
    y="cnt",
    data=monthly_rentals_df,
    marker="o", 
    linewidth=2,
    color="#90CAF9",
    ax=ax
)
ax.set_title(f"Total Penyewaan Sepeda per Bulan", loc="center", fontsize=20)
ax.set_ylabel("Total Penyewaan")
ax.set_xlabel("Bulan")
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

st.markdown("---")

# Row 3: Visualisasi Pertanyaan Bisnis 2
st.subheader("Pengaruh Kondisi Cuaca terhadap Rata-rata Penyewaan Harian")
fig, ax = plt.subplots(figsize=(10, 6))

colors = sns.color_palette("Set2")
sns.barplot(
    x="weathersit", 
    y="cnt",
    data=weather_rentals_df,
    palette=colors,
    ax=ax
)
ax.set_title("Rata-rata Penyewaan Harian Berdasarkan Cuaca", loc="center", fontsize=15)
ax.set_ylabel("Rata-rata Penyewaan")
ax.set_xlabel("Kondisi Cuaca")
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

st.markdown("---")

# Row 4: Visualisasi Analisis Lanjutan (Clustering/Binning)
st.subheader("Clustering Kategori Suhu Udara vs Penyewaan Sepeda (Analisis Lanjutan)")

# Data manipulation khusus untuk clustering
main_df['temp_celcius'] = main_df['temp'] * 41

def categorize_temp(temp):
    if temp < 15:
        return 'Dingin (<15°C)'
    elif temp >= 15 and temp < 25:
        return 'Sedang (15°C - 24°C)'
    elif temp >= 25 and temp < 30:
        return 'Hangat (25°C - 29°C)'
    else:
        return 'Panas (>=30°C)'

main_df['temp_category'] = main_df['temp_celcius'].apply(categorize_temp)
temp_clustering = main_df.groupby('temp_category', observed=False)['cnt'].mean().reset_index()

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    x='temp_category', 
    y='cnt', 
    data=temp_clustering, 
    palette='magma', 
    order=['Dingin (<15°C)', 'Sedang (15°C - 24°C)', 'Hangat (25°C - 29°C)', 'Panas (>=30°C)'],
    ax=ax
)
ax.set_title("Rata-rata Penyewaan Berdasarkan Kategori Suhu (Manual Grouping)", loc="center", fontsize=15)
ax.set_ylabel("Rata-rata Penyewaan")
ax.set_xlabel("Kategori Suhu")
ax.tick_params(axis='x', labelsize=12)
st.pyplot(fig)

with st.expander("Lihat Insight Analisis Lanjutan"):
    st.write(
        """
        Melalui teknik pengelompokan **(Binning / Manual Grouping)**, kita mengkategorikan suhu udara (yang sebelumnya telah dinormalisasi) kembali ke dalam satuan Celcius dan membaginya menjadi 4 kategori: Dingin, Sedang, Hangat, dan Panas. 
        
        Dari visualisasi di atas, kita dapat menyimpulkan bahwa minat penyewaan sepeda memuncak saat cuaca terasa Hangat (25°C - 29°C) hingga Panas (>=30°C). Suhu di bawah 15°C (Dingin) secara signifikan menurunkan aktivitas penyewaan.
        """
    )

st.caption("Copyright © Wildan Taufiqurrahman 2026")
