
import streamlit as st

# Definimos la página principal
def pagina_principal():
    st.title("Descripción del Proyecto")
    st.write("Este proyecto tiene como objetivo recopilar y analizar información relevante sobre diversos países del mundo, "
        "incluyendo datos sobre su población, idiomas, densidad, área, territorio, etc. A través de una plataforma digital interactiva.")

# Página para visualización de datos
def visualizacion_datos():
    st.title("Visualización de Datos")
    st.write("Aquí se mostrarán datos relevantes sobre diferentes países.")
    # Aquí puedes añadir más funcionalidades como tablas, mapas, etc.
    # Ejemplo:
    # st.dataframe(df)  # Si tuvieras un dataframe para mostrar

# Página de gráficos interactivos
def graficos_interactivos():
    st.title("Gráficos Interactivos")
    st.write("Esta sección permite interactuar con gráficos sobre diversos parámetros de los países.")
    # Aquí puedes incluir gráficos interactivos con Plotly, Altair, Matplotlib, etc.
    # Ejemplo de un gráfico interactivo:
    # import plotly.express as px
    # fig = px.bar(data_frame=df, x="country", y="population")
    # st.plotly_chart(fig)

# Función principal que gestiona la navegación
def main():
    # Título de la aplicación
    st.title("Aplicación de Análisis de Países del Mundo")

    # Barra lateral para navegación
    st.sidebar.title("Navegación")
    pagina = st.sidebar.selectbox("Selecciona una página", ["Página principal", "Visualización de datos", "Gráficos interactivos"])

    # Redirigir al contenido correspondiente según la página seleccionada
    if pagina == "Página principal":
        pagina_principal()
    elif pagina == "Visualización de datos":
        visualizacion_datos()
    elif pagina == "Gráficos interactivos":
        graficos_interactivos()

if __name__ == "__main__":
    main()
import requests
import matplotlib.pyplot as plt

# URL del archivo JSON en GitHub (asegúrate de reemplazarla por la URL correcta)
url = 'https://raw.githubusercontent.com/usuario/repositorio/ruta_del_archivo/archivo.json'

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

try:
    response = session.get(url, timeout=30)
    response.raise_for_status()  # Lanza excepción para errores HTTP
    countries_data = response.json()

    if not countries_data:
        print("No hay datos disponibles. Verifica el archivo en GitHub.")
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
