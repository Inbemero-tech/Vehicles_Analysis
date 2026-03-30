# ============================================
# 🚗📊 Exploración y Análisis del Mercado Automotriz
# ============================================

import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ==============================
# CONFIGURACIÓN INICIAL
# ==============================
st.set_page_config(
    page_title="Análisis de Vehículos en Venta - EE. UU.",
    layout="wide",
    page_icon="🚗"
)

st.title("🚗 Análisis de Vehículos en Venta en EE. UU.")
st.markdown("""
Explora los datos de vehículos en venta, filtra por tipo o condición, 
y analiza las tendencias de precios, kilometraje y más.
""")

# ==============================
# CARGA DE DATOS
# ==============================


@st.cache_data
def load_data():
    try:
        df = pd.read_csv("./data/vehicles_us_clean.csv")
        st.success("✅ Datos cargados correctamente")
        return df
    except FileNotFoundError:
        st.error(
            "❌ No se encontró el archivo 'vehicles_us_clean.csv'. Verifica la ruta.")
        return pd.DataFrame()


df = load_data()
if df.empty:
    st.stop()

# ==============================
# SIDEBAR DE FILTROS
# ==============================
st.sidebar.header("🔍 Filtros de Exploración")

type_filter = st.sidebar.multiselect(
    "Tipo de vehículo:",
    options=df["type"].unique(),
    default=df["type"].unique()
)

condition_filter = st.sidebar.multiselect(
    "Condición:",
    options=df["condition"].unique(),
    default=df["condition"].unique()
)

filtered_df = df[
    (df["type"].isin(type_filter)) &
    (df["condition"].isin(condition_filter))
]

year_range = st.sidebar.slider(
    "Rango de años:",
    int(df["model_year"].min()),
    int(df["model_year"].max()),
    (int(df["model_year"].min()),
     int(df["model_year"].max())))

price_range = st.sidebar.slider(
    "Rango de precios:",
    int(df["price"].min()),
    int(df["price"].max()),
    (int(df["price"].min()),
     int(df["price"].max())))


# ==============================
# RESUMEN GENERAL DEL MERCADO
# ==============================
st.header("📊 Resumen general del mercado")
st.markdown("Los indicadores muestran una visión rápida del estado actual del mercado con base en los filtros aplicados.")

filtered_df = df[
    (df["type"].isin(type_filter)) &
    (df["condition"].isin(condition_filter)) &
    (df["model_year"].between(year_range[0], year_range[1])) &
    (df["price"].between(price_range[0], price_range[1]))
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Vehículos disponibles", len(filtered_df))
col2.metric("Precio promedio", f"${filtered_df['price'].mean():,.0f}")
col3.metric("Año promedio", int(filtered_df["model_year"].mean()))
col4.metric("Km promedio", f"{filtered_df['odometer'].mean():,.0f}")

# ==============================
# PREPARACIÓN DE DATOS PARA VISUALIZACIÓN
# ==============================

# Creamos una copia para no afectar los filtros originales
df_visualizacion = filtered_df.copy()

# Usamos fillna(0) por si quedó algún nulo perdido y luego mapeamos
df_visualizacion["is_4wd"] = df_visualizacion["is_4wd"].map(
    {1.0: "Sí", 0.0: "No", 1: "Sí", 0: "No"})

# Crea un diccionario de mapeo
columnas_espanol = {
    "price": "Precio",
    "model_year": "Año del Modelo",
    "model": "Modelo",
    "condition": "Condición",
    "cylinders": "Cilindros",
    "fuel": "Combustible",
    "odometer": "Kilometraje (millas)",
    "transmission": "Transmisión",
    "type": "Tipo",
    "paint_color": "Color",
    "is_4wd": "¿Es 4x4?",
    "date_posted": "Fecha de Publicación",
    "days_listed": "Días en Venta"
}

# Aplicamos el renombramiento al filtered_df antes de mostrarlo
df_visualizacion = df_visualizacion.rename(columns=columnas_espanol)

# ==============================
# TABLA INTERACTIVA COMPLETA
# ==============================
st.markdown("## 📋 Conjunto de Datos Completo")
st.markdown("""
Puedes desplazarte horizontal y verticalmente para explorar todos los registros disponibles.
Usa los filtros en la barra lateral para actualizar la tabla en tiempo real.
""")

# Mostramos toda la tabla con scroll
st.dataframe(
    df_visualizacion,
    column_config={
        "Precio": st.column_config.NumberColumn(format="$%d"),
    },
    use_container_width=True,
    height=400
)

# ==============================
# SECCIÓN: VISUALIZACIONES
# ==============================
st.header("📊 Visualizaciones")
st.markdown("Analiza la distribución de precios, la relación entre año y kilometraje, y los promedios por tipo de vehículo.")

tab1, tab2, tab3 = st.tabs(
    ["💰 Distribución de precios", "📅 Año del modelo vs Precio", "🚙 Precio promedio por tipo"])

# --- Histograma de precios ---
with tab1:
    st.markdown("""
    El siguiente histograma muestra cómo se distribuyen los precios de los vehículos filtrados. 
    Permite observar concentraciones de valores y detectar posibles outliers.
    """)
    fig_price = px.histogram(
        filtered_df, x="price", nbins=50, color_discrete_sequence=["#76b5c5"]
    )
    fig_price.update_layout(xaxis_title="Precio (USD)",
                            yaxis_title="Frecuencia")
    st.plotly_chart(fig_price, use_container_width=True)
    st.info("📊 *La mayoría de los vehículos se concentran en el rango de precios bajos a medios, con una minoría que representa autos de lujo o nuevos.*")

# --- Gráfico de dispersión ---
with tab2:
    st.markdown("""
    Cada punto representa un vehículo. 
    Podrás notar cómo los precios tienden a disminuir a medida que el kilometraje aumenta.
    """)
    fig_scatter = px.scatter(
        filtered_df,
        x="odometer",
        y="price",
        color="type",
        hover_data=["model_year", "condition"],
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_scatter.update_layout(
        xaxis_title="Kilometraje (millas)", yaxis_title="Precio (USD)")
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.info("🚘 *En general, los vehículos más recientes tienen precios más altos, mientras que el kilometraje elevado tiende a reducir su valor.*")

# --- Gráfico de barras ---
with tab3:
    st.markdown("""
    Este gráfico de barras muestra el precio promedio de los vehículos según su tipo. 
    Permite comparar rápidamente qué tipos de vehículos son más costosos en promedio.
    """)
    avg_price_type = filtered_df.groupby("type")["price"].mean().reset_index()
    fig_bar = px.bar(
        avg_price_type,
        x="type",
        y="price",
        color="type",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_bar.update_layout(
        xaxis_title="Tipo de vehículo", yaxis_title="Precio promedio (USD)")
    st.plotly_chart(fig_bar, use_container_width=True)
    st.info("🧩 *Los tipos de vehículos más costosos suelen ser SUV y camionetas, mientras que los sedanes y compactos dominan el segmento más económico.*")

# ==============================
# SECCIÓN: ANÁLISIS CORRELACIONAL
# ==============================
st.markdown("## 🔍 Análisis Correlacional")

st.markdown("""
El mapa de calor muestra las relaciones entre las variables numéricas.\n 
Los valores cercanos a 1 o -1 indican relaciones fuertes (positivas o negativas).\n
Ejemplos:
- Precio y Año del modelo: Positiva (vehículos más nuevos tienden a ser más caros)
- Precio y Kilometraje: Negativa (mayor kilometraje suele reducir el precio)
""")

corr = filtered_df[["price", "model_year", "odometer", "days_listed"]].corr()
corr.columns = ["Precio", "Año Modelo", "Kilometraje", "Días Publicado"]
corr.index = ["Precio", "Año Modelo", "Kilometraje", "Días Publicado"]

fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
st.pyplot(fig)

# ==============================
# SECCIÓN: SIMULADOR DE PRECIO
# ==============================
st.markdown("## 🎯 Simulador de Precio Estimado")

st.markdown("""
Usa los controles para simular un precio estimado de venta basado en el año, 
kilometraje y tipo de vehículo.
""")

col1, col2, col3 = st.columns(3)

with col1:
    year = st.slider("Año del modelo", int(
        df["model_year"].min()), int(df["model_year"].max()), 2015)

with col2:
    odometer = st.slider("Kilometraje (millas)", 0, int(
        df["odometer"].max()), 60000, step=5000)

with col3:
    vehicle_type = st.selectbox("Tipo de vehículo", df["type"].unique())

# Modelo simple para simulación de precio
base_price = df["price"].mean()
price_est = base_price + \
    (year - df["model_year"].mean()) * 150 - (odometer / 1000) * 20

st.metric(
    label=f"💵 Precio estimado para un {vehicle_type}", value=f"${price_est:,.0f} USD")


# ==============================
# PIE DE PÁGINA
# ==============================
st.markdown("---")
st.caption("""
    Aplicación desarrollada para análisis exploratorio de datos de vehículos - Proyecto académico 🧠 \n
    Desarrollado por **Inti Romero** \n
    GitHub: [https://github.com/Inbemero-tech]
    """)
