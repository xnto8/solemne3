import streamlit as st
import pandas as pd
import requests



# Configuración inicial
st.set_page_config(page_title="App Multi-páginas", layout="wide")

# Función para cargar datos desde una URL
def load_data(url):
    try:
        # Obtener datos desde la URL
        response = requests.get(url)
        response.raise_for_status()  # Verifica si hubo errores en la solicitud

        # Convertir JSON a DataFrame
        data = pd.json_normalize(response.json())

        # Traducir las columnas al español
        translations = {
            "name.common": "Nombre",
            "name.official": "Nombre Oficial",
            "population": "Población",
            "area": "Área",
            "flag": "Bandera",
            "currencies": "Monedas",
            "languages": "Idiomas",
            "capital": "Capital",
            "region": "Región",
            "subregion": "Subregión",
            "borders": "Fronteras",
            "timezones": "Husos Horarios",
            "demonyms.eng.f": "Gentilicio (Femenino)",
            "demonyms.eng.m": "Gentilicio (Masculino)"
        }
        data.rename(columns=translations, inplace=True)

        # Intentar convertir columnas numéricas
        for col in ["Población", "Área"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")

        return data, None
    except Exception as e:
        return None, str(e)

# Página de inicio
def home():
    st.title("Visualizacion interactiva de datos con streamlit y API REST countries")
    st.write("Usa el menú de la izquierda para navegar entre las secciones.")
    st.write("1. Carga datos desde una URL en la página 'Cargar Datos'.")
    st.write("2. Visualiza gráficos en la página 'Gráficos'.")


# Página para cargar datos
def cargar_datos():
    st.title("Cargar Datos desde una URL")
    default_url = "https://restcountries.com/v3.1/all?fields=name,population,area,flag,currencies,languages,capital,region,subregion,borders,timezones,demonyms"
    url = st.text_input("Introduce la URL de los datos:", value=default_url)
    if st.button("Cargar Datos"):
        if url:
            data, error = load_data(url)
            if error:
                st.error(f"Error al cargar los datos: {error}")
            else:
                st.session_state["data"] = data
                st.success("Datos cargados exitosamente.")
                st.write("Vista previa de los datos:")
                st.dataframe(data)
        else:
            st.warning("Por favor, introduce una URL válida.")

# Página para gráficos
def graficos():
    st.title("Visualización de Gráficos")
    if "data" not in st.session_state:
        st.warning("Primero carga datos en la página 'Cargar Datos'.")
        return

    data = st.session_state["data"]
    numeric_columns = data.select_dtypes(include=["float64", "int64"]).columns

    if numeric_columns.empty:
        st.warning("El dataset no contiene columnas numéricas para graficar.")
        return

    selected_columns = st.multiselect(
        "Selecciona las columnas numéricas para graficar:",
        options=numeric_columns,
        format_func=lambda x: x.replace("_", " ")  # Formato legible
    )

    chart_type = st.selectbox(
        "Selecciona el tipo de gráfico:",
        ["Selecciona una opción", "Línea", "Barras", "Histograma", "Dispersión"],
    )

    if st.button("Generar Gráfico"):
        if selected_columns and chart_type != "Selecciona una opción":
            fig, ax = st.subplots()
            if chart_type == "Línea":
                for col in selected_columns:
                    ax.plot(data.index, data[col], label=col)
                ax.legend()
                ax.set_title("Gráfico de Línea")
            elif chart_type == "Barras":
                if len(selected_columns) == 1:
                    ax.bar(data.index, data[selected_columns[0]])
                    ax.set_title("Gráfico de Barras")
                else:
                    st.warning("Selecciona solo una columna para un gráfico de barras.")
            elif chart_type == "Histograma":
                for col in selected_columns:
                    ax.hist(data[col].dropna(), bins=20, alpha=0.5, label=col)
                ax.legend()
                ax.set_title("Histograma")
            elif chart_type == "Dispersión":
                if len(selected_columns) == 2:
                    ax.scatter(data[selected_columns[0]], data[selected_columns[1]])
                    ax.set_xlabel(selected_columns[0])
                    ax.set_ylabel(selected_columns[1])
                    ax.set_title("Gráfico de Dispersión")
                else:
                    st.warning("Selecciona exactamente dos columnas para un gráfico de dispersión.")
            st.pyplot(fig)
        else:
            st.warning("Por favor, selecciona columnas y un tipo de gráfico.")

# Configuración de navegación
pages = {
    "Inicio": home,
    "Cargar Datos": cargar_datos,
    "Gráficos": graficos,
}

st.sidebar.title("Navegación")
selected_page = st.sidebar.radio("Selecciona una página:", list(pages.keys()))
pages[selected_page]()
