# Proyek Analisis Data: Dataset Publik E-Commerce
# Nama: Adilah Widiasti
# Email: adilahwidiasti86@gmail.com
# ID Dicoding: olaladilah

# Mengimpor Library yang Diperlukan untuk Dashboard
import pandas as pd

import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Fungsi untuk Mengelompokkan Data Berdasarkan Kota
def get_customer_count_by_city(dataframe):
    city_data = dataframe.groupby(by="customer_city").customer_id.nunique().reset_index()
    city_data.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return city_data

# Fungsi untuk Mengelompokkan Data Berdasarkan Negara Bagian
def get_customer_count_by_state(dataframe):
    state_data = dataframe.groupby(by="customer_state").customer_id.nunique().reset_index()
    state_data.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return state_data

# Fungsi untuk Menghitung Pesanan Bulanan
def get_monthly_orders(dataframe):
    filtered_data = dataframe[dataframe['order_delivered_customer_date'].dt.year == 2018]
    filtered_data.set_index('order_delivered_customer_date', inplace=True)
    monthly_data = filtered_data.resample(rule="M").agg({
          "order_id": "nunique",
          "price": "sum"
    })
    monthly_data.index = monthly_data.index.strftime("%B")
    monthly_data = monthly_data.reset_index()
    monthly_data.rename(columns={
        "order_id": "order_count",
        "price": "total_revenue"
    }, inplace=True)
    return monthly_data

# Fungsi untuk Menghitung Total Penjualan per Kategori Produk
def get_sales_by_product_category(dataframe):
    category_sales = dataframe.groupby(by="product_category_name_english").agg({
        "order_id": "count"
    }).rename(columns={"order_id": "total_sales"}).sort_values(by="total_sales", ascending=False)
    return category_sales

# Fungsi untuk Melakukan Analisis RFM (Recency, Frequency, Monetary)
def perform_rfm_analysis(dataframe):
    rfm_data = dataframe.groupby(by="customer_id", as_index=False).agg({
        "order_delivered_customer_date": "max",
        "order_id": "nunique",
        "price": "sum"
    }).rename(columns={
        "order_delivered_customer_date": "recency_date",
        "order_id": "frequency",
        "price": "monetary"
    })

    rfm_data["recency_date"] = pd.to_datetime(rfm_data["recency_date"])
    latest_date = dataframe["order_delivered_customer_date"].dt.date.max()
    rfm_data["recency"] = rfm_data["recency_date"].dt.date.apply(lambda x: (latest_date - x).days)
    rfm_data.drop(columns="recency_date", axis=1, inplace=True)

    return rfm_data

# Memuat Data dari Berkas CSV yang Sudah Dibersihkan
dataframe = pd.read_csv("dashboard/main_data.csv")

# Mengatur Kolom Tanggal
date_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
dataframe[date_columns] = dataframe[date_columns].apply(pd.to_datetime)

# Menentukan Rentang Tanggal Minimum dan Maksimum
min_date = dataframe["order_purchase_timestamp"].min()
max_date = dataframe["order_purchase_timestamp"].max()

# Membuat Komponen Filter di Sidebar
with st.sidebar:
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date)
    )

# Memfilter Data Berdasarkan Rentang Tanggal yang Dipilih
filtered_data = dataframe[(dataframe["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
                          (dataframe["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# Menghitung Data yang Diperlukan untuk Visualisasi
if not filtered_data.empty:
    city_data = get_customer_count_by_city(filtered_data)
    state_data = get_customer_count_by_state(filtered_data)
    monthly_orders_data = get_monthly_orders(filtered_data)
    product_sales_data = get_sales_by_product_category(filtered_data)
    rfm_data = perform_rfm_analysis(filtered_data)

    # Memasukkan Visualisasi Data ke dalam Dashboard
    # Visualisasi 1: Demografi Pelanggan Berdasarkan Kota dan Negara Bagian
    st.header("Proyek Analisis Data: Dataset Publik E-Commerce :sparkles:")
    st.subheader("Demografi Pelanggan Berdasarkan Kota dan Negara Bagian")

    col1, col2 = st.columns(2)

    with col1:
        colors = ["#D8B0D1", "#D6A8D8", "#FFB6C1", "#D5006D", "#E6A8D7"]
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(
            x="customer_city",
            y="customer_count",
            data=city_data.sort_values(by="customer_count", ascending=False).head(5),
            palette=colors,
            ax=ax
        )
        ax.set_title("Demografi Pelanggan Berdasarkan Kota", loc="center", fontsize=17)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis="x", labelsize=10)
        ax.tick_params(axis="y", labelsize=8)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(
            x="customer_state",
            y="customer_count",
            data=state_data.sort_values(by="customer_count", ascending=False).head(5),
            palette=colors,
            ax=ax
        )
        ax.set_title("Demografi Pelanggan Berdasarkan Negara Bagian", loc="center", fontsize=17)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis="x", labelsize=10)
        ax.tick_params(axis="y", labelsize=8)
        st.pyplot(fig)

    # Visualisasi 2: Performa Penjualan dan Pendapatan Bulanan (2018)
    st.subheader("Performa Penjualan dan Pendapatan Bulanan (2018)")

    col1, col2 = st.columns(2)

    with col1:
        total_orders = monthly_orders_data.order_count.sum()
        st.metric("Performa Penjualan Per Bulan (2018)", value=total_orders)

    with col2:
        total_revenue = format_currency(monthly_orders_data.total_revenue.sum(), "AUD", locale="es_CO")
        st.metric("Kinerja Pendapatan Per Bulan (2018)", value=total_revenue)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        monthly_orders_data["order_delivered_customer_date"],
        monthly_orders_data["order_count"],
        marker="o",
        linewidth=2,
        color="#FF8C00"
    )
    ax.tick_params(axis="y", labelsize=10)
    ax.tick_params(axis="x", labelsize=10)
    st.pyplot(fig)

    # Visualisasi 3: Kategori Produk Terlaris dan Terendah
    st.subheader("Kategori Produk Terlaris dan Terendah")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

    sns.barplot(x="total_sales", y="product_category_name_english", data=product_sales_data.head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Jumlah Penjualan", fontsize=14)
    ax[0].set_title("Kategori Produk Paling Banyak Terjual", loc="center", fontsize=18)
    ax[0].tick_params(axis="y", labelsize=14)
    ax[0].tick_params(axis="x", labelsize=12)

    sns.barplot(x="total_sales", y="product_category_name_english", data=product_sales_data.sort_values(by="total_sales", ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Jumlah Penjualan", fontsize=14)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Kategori Produk Paling Sedikit Terjual", loc="center", fontsize=18)
    ax[1].tick_params(axis="y", labelsize=14)
    ax[1].tick_params(axis="x", labelsize=12)

    st.pyplot(fig)

    # Visualisasi 4: Analisis RFM (Recency, Frequency, Monetary)
    st.subheader("Analisis RFM (Recency, Frequency, Monetary)")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_recency = round(rfm_data.recency.mean(), 1)
        st.metric("Rata-Rata Recency (Hari)", value=avg_recency)

    with col2:
        avg_frequency = round(rfm_data.frequency.mean(), 2)
        st.metric("Rata-Rata Frequency (Transaksi)", value=avg_frequency)

    with col3:
        avg_monetary = format_currency(rfm_data.monetary.mean(), "R$", locale="pt_BR")
        st.metric("Rata-Rata Monetary (Total Pembelanjaan)", value=avg_monetary)

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(38, 10))
    sns.barplot(y="recency", x="customer_id", data=rfm_data.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Customer ID", fontsize=20)
    ax[0].set_title("Recency (Hari)", loc="center", fontsize=22)
    ax[0].tick_params(axis="x", rotation=100, labelsize=18)
    ax[0].tick_params(axis="y", labelsize=15)

    sns.barplot(y="frequency", x="customer_id", data=rfm_data.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Customer ID", fontsize=20)
    ax[1].set_title("Frequency (Transaksi)", loc="center", fontsize=22)
    ax[1].tick_params(axis="x", rotation=90, labelsize=18)
    ax[1].tick_params(axis="y", labelsize=15)

    sns.barplot(y="monetary", x="customer_id", data=rfm_data.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("Customer ID", fontsize=20)
    ax[2].set_title("Monetary (Total Pembelanjaan)", loc="center", fontsize=22)
    ax[2].tick_params(axis="x", rotation=80, labelsize=18)
    ax[2].tick_params(axis="y", labelsize=15)

    st.pyplot(fig)

# Menyertakan Hak Cipta
st.caption("Copyright (c) Adilah Widiasti - 2025")
