import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt



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
    st.title("Visualización interactiva de datos con Streamlit y API REST Countries")
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
            fig, ax = plt.subplots(figsize=(10, 6))

            # Gráfico de línea
            if chart_type == "Línea":

                ax.plot(data.index, data[selected_columns[0]], label=selected_columns[0])
                ax.legend()
                ax.set_title("Gráfico de Línea")
                ax.set_xlabel("Índice")
                ax.set_ylabel("Valor")

            # Gráfico de barras
            elif chart_type == "Barras":
                if len(selected_columns) == 1:
                    ax.bar(data.index, data[selected_columns[0]])
                    ax.set_title("Gráfico de Barras")
                    ax.set_xlabel("Índice")
                    ax.set_ylabel(selected_columns[0])
                else:
                    st.warning("Selecciona solo una columna para un gráfico de barras.")

            # Gráfico de histograma
            elif chart_type == "Histograma":
                for col in selected_columns:
                    ax.hist(data[col].dropna(), bins=20, alpha=0.5, label=col)
                ax.legend()
                ax.set_title("Histograma")
                ax.set_xlabel("Valor")
                ax.set_ylabel("Frecuencia")

            # Gráfico de dispersión
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


import requests
import matplotlib.pyplot as plt

# URL con filtros para reducir el tamaño de la respuesta
url = 'https://restcountries.com/v3.1/all?fields=name,population,area,flag,currencies,languages,capital'

countries_data = []

# Configurar una sesión con reintentos robustos
session = requests.Session()
retries = requests.adapters.Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[500, 502, 503, 504]
)
adapter = requests.adapters.HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

def obtener_datos_pais(pais):
    """Buscar un país y devolver sus datos relevantes."""
    for country in countries_data:
        name = country.get('name', {}).get('common', '')
        if name.lower() == pais.lower():
            population = country.get('population', 0)
            area = country.get('area', 0)
            capital = country.get('capital', ['Desconocida'])[0]
            flag = country.get('flags', {}).get('png', '')
            currencies = country.get('currencies', {})
            languages = country.get('languages', {})
            return {
                "name": name,
                "population": population,
                "area": area,
                "capital": capital,
                "flag": flag,
                "currencies": list(currencies.keys()),
                "languages": list(languages.values())
            }
    return None

# Realiza la solicitud a la API y procesa los datos
try:
    response = session.get(url, timeout=30)
    response.raise_for_status()  # Lanza excepción para errores HTTP
    countries_data = response.json()

    if not countries_data:
        print("No hay datos disponibles. Verifica la API.")
        exit()

except requests.exceptions.RequestException as e:
    print(f"Error durante la solicitud: {e}")
    countries_data = []

# Función para permitir la selección de país y obtener datos
def seleccionar_pais():
    countries_names = [country.get('name', {}).get('common', 'Desconocido') for country in countries_data]
    print("Seleccione un país para obtener información:")
    for idx, country in enumerate(countries_names, 1):
        print(f"{idx}. {country}")

    try:
        opcion = int(input("\nIngrese el número del país (o 0 para salir): "))

        if opcion == 0:
            print("Saliendo del programa.")
            return None

        if 1 <= opcion <= len(countries_names):
            pais_elegido = countries_names[opcion - 1]
            print(f"\nHas seleccionado: {pais_elegido}")
            datos_pais = obtener_datos_pais(pais_elegido)

            if datos_pais:
                print(f"\nDatos de {datos_pais['name']}:")
                print(f"Capital: {datos_pais['capital']}")
                print(f"Población: {datos_pais['population']}")
                print(f"Área: {datos_pais['area']} km²")
                print(f"Monedas: {', '.join(datos_pais['currencies'])}")
                print(f"Idiomas: {', '.join(datos_pais['languages'])}")

                return datos_pais
            else:
                print("No se encontraron datos para este país.")
                return None
        else:
            print("Opción no válida.")
            return None

    except ValueError:
        print("Por favor, ingrese un número válido.")
        return None

# Llamar a la función de selección de país
pais_datos = seleccionar_pais()

# Si se obtuvo información válida del país, crear el gráfico
if pais_datos:
    # Obtener la información del país seleccionado
    nombre_pais = pais_datos['name']
    poblacion = pais_datos['population']
    area = pais_datos['area']
    idiomas = len(pais_datos['languages'])
    monedas = len(pais_datos['currencies'])

    # Crear las categorías y valores
    categorias = ['Población', 'Área (km²)', 'Idiomas', 'Monedas']
    valores = [poblacion, area, idiomas, monedas]

    # Preguntar al usuario qué tipo de gráfico quiere ver
    print("\nSeleccione el tipo de gráfico que desea visualizar:")
    print("1. Gráfico de Barras")
    print("2. Gráfico de Pastel")
    print("3. Gráfico de Líneas")

    try:
        opcion_grafico = int(input("\nIngrese el número del gráfico (1, 2 o 3): "))

        if opcion_grafico == 1:
            # Gráfico de Barras
            plt.figure(figsize=(8, 6))
            barras = plt.bar(categorias, valores, color=['skyblue', 'lightgreen', 'lightcoral', 'gold'])
            for barra in barras:
                yval = barra.get_height()
                plt.text(barra.get_x() + barra.get_width() / 2, yval + 0.02 * yval, int(yval), ha='center', va='bottom')
            plt.title(f"Datos de {nombre_pais}")
            plt.xlabel("Categorías")
            plt.ylabel("Valores")
            plt.show()

        elif opcion_grafico == 2:
            # Gráfico de Pastel
            plt.figure(figsize=(8, 6))
            plt.pie(valores, labels=categorias, autopct='%1.1f%%', colors=['skyblue', 'lightgreen', 'lightcoral', 'gold'])
            plt.title(f"Distribución de datos de {nombre_pais}")
            plt.show()

        elif opcion_grafico == 3:
            # Gráfico de Líneas
            plt.figure(figsize=(8, 6))
            plt.plot(categorias, valores, marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
            plt.title(f"Datos de {nombre_pais} en gráfico de líneas")
            plt.xlabel("Categorías")
            plt.ylabel("Valores")
            plt.grid(True)
            plt.show()

        else:
            print("Opción no válida. Elige 1, 2 o 3.")

    except ValueError:
        print("Por favor, ingrese un número válido para el tipo de gráfico.")
else:
    print("No se seleccionaron datos válidos de un país.")
