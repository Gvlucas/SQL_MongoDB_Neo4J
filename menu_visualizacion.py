import pymysql
import streamlit as st
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd # Para las gráficas lo usamos para procesar resultados SQL
from configuracion import *
from load_data import *

st.set_page_config(page_title="Reviews Dashboard", layout="wide",initial_sidebar_state="expanded")

# Conexión a la BBDD (Ayuda IA para la conexión)
@st.cache_resource
def get_conns():
    conn_sql = pymysql.connect(**MYSQL_CONFIG, cursorclass=pymysql.cursors.DictCursor)
    return conn_sql

@st.cache_resource
def init_mongodb():
    client = MongoClient(MONGO_CONFIG['host'])
    return client[MONGO_CONFIG['database']]

# Ejecutamos para poder trabajar con las conexiones para la hora de hacer las consultas
db_mongo = init_mongodb()
conn = get_conns()

# --- MENÚ LATERAL ---
with st.sidebar:
    st.title("✅ Opciones")
    st.divider()

    # Selector de página/sección
    pagina = st.selectbox(
        "Selecciona una sección",
        ["🏠 Inicio" ,"Evolución Reviews por Años", "Evolución Popularidad Items","Histograma por Nota", "Evolución Temporal por Categoría","Histograma Reviews por Usuario", "Nube de Palabras por Categoría","🌟 Visualización Personalizada","🚪 Salir"]
    )

    st.divider()
    st.caption("Gonzalo Velasco & Lucía Lozano")
    st.caption("© 2026 - ReviewsItems")

st.title("🛍️🗒️ Shopping Items & Reviews 🗒️🛍️")
st.markdown("Análisis en profundidad y gráfico sobre los usuarios y sus reseñas")
st.divider()

mapeo_categorias_mongo = {
        "🎮 Videojuegos": "Videogames",
        "🎵 Música digital":"Music",
        "🎹 Instrumentos musicales": "Instruments",
        "🧸 Juguetes": "Toys_Games",
        }

mapeo_categorias_sql = {
        "🎮 Videojuegos": "video_games",
        "🎵 Música digital": "digital_music",
        "🎹 Instrumentos musicales": "musical_instruments",
        "🧸 Juguetes": "toys_games",
        }

if pagina == "🏠 Inicio":
    pass

# --- LÓGICA DE LAS GRÁFICAS ---
elif pagina == "Evolución Reviews por Años":
    st.subheader("📅 Evolución de Reviews por Año")
    st.markdown("A continuación se muestra  el número de reviews por año en formato histograma")
    cursor = conn.cursor()
    subpagina = st.selectbox(
        "Seleccione una categoría",
        ["📋 Blanc page","🎮 Videojuegos" ,"🎵 Música digital","🎹 Instrumentos musicales","🧸 Juguetes","🌍 Todo"]
    )

    if subpagina != "📋 Blanc page" :
        if subpagina == "🌍 Todo": #Realizamos las consultas para las páginas que no sean Blanc page
            st.write("Mostrando datos de: **TODAS LAS CATEGORÍAS**")
            query = """
                SELECT YEAR(reviewTime) AS año, COUNT(*) AS n_reviews 
                FROM reviews 
                GROUP BY año 
                ORDER BY año
                """
            cursor.execute(query)
        else: #Adaptamos a la categoría, es más eficiente que una página de la página... etc
            categoria = mapeo_categorias_sql[subpagina]
            st.write(f"Mostrando datos de: **{subpagina.upper()}**")
            query = """
                SELECT YEAR(reviewTime) AS año, COUNT(*) AS n_reviews 
                FROM reviews 
                WHERE categoria = %s 
                GROUP BY año 
                ORDER BY año
                """
            cursor.execute(query, (categoria,)) #Ejecutamos query con los argumentos correspondientes
        resultado = cursor.fetchall()

        if resultado:
            df = pd.DataFrame(resultado)
            df['año'] = pd.to_numeric(df['año']) #Convertimos el año a numérico para quitar la ,

            st.dataframe(
                df,
                column_config={
                    "año": st.column_config.NumberColumn("Año", format="%d") #Colocamos el año a la der.
                },
                hide_index= True, #Escondemos el índice que viene por defecto
                use_container_width=True)

            # Creamos la gráfica con Seaborn
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x="año", y="n_reviews", data=df, palette="magma", ax=ax)
            ax.set_title(f"Reviews por año - {subpagina[2:]}")
            ax.set_xlabel("Año")
            ax.set_ylabel("Número de reviews")
            
            st.pyplot(fig)
        else:
            st.info(f"No hay datos disponibles para {subpagina} en la base de datos.")

elif pagina == "Evolución Popularidad Items": #Realizamos lo mismo para las demás consultas
    st.subheader("📉 Evolución Popularidad Items")
    st.markdown("A continuación se muestra la popularidad de los " \
    "artículos en función de la categoría (curva de distribución)")
    cursor = conn.cursor()
    subpagina = st.selectbox(
        "Seleccione una categoría",
        ["📋 Blanc page","🎮 Videojuegos" ,"🎵 Música digital","🎹 Instrumentos musicales","🧸 Juguetes","🌍 Todo"]
    )
    if subpagina != "📋 Blanc page":
        if subpagina == "🌍 Todo":
            st.write("Mostrando datos de: **TODAS LAS CATEGORÍAS**")
            query = """
                SELECT asin, COUNT(*) as n_reviews 
                FROM reviews 
                GROUP BY asin 
                ORDER BY n_reviews DESC
                """
            titulo = "todas las categorías"
            cursor.execute(query)
        else:
            categoria = mapeo_categorias_sql[subpagina]
            st.write(f"Mostrando datos de: **{subpagina.upper()}**")
            query = """
                SELECT asin, COUNT(*) as n_reviews 
                FROM reviews 
                WHERE categoria = %s
                GROUP BY asin 
                ORDER BY n_reviews DESC
                """
            titulo = subpagina[2:]
            cursor.execute(query, (categoria,))
        resultado = cursor.fetchall()

        if resultado:
            df = pd.DataFrame(resultado)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True)

            # Creamos la gráfica con Seaborn
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['n_reviews'], color="#0693f2", linewidth=2)

            ax.set_title(f"Evolución de popularidad de {titulo}")
            ax.set_xlabel("Artículos")
            ax.set_ylabel("Número de reviews")

            ax.grid(True, linestyle='--', alpha=0.5)
            
            st.pyplot(fig)
        else:
            st.info(f"No hay datos disponibles para {subpagina} en la base de datos.")

elif pagina == "Histograma por Nota":
    st.subheader("📊 Histograma por Nota")
    st.markdown("A continuación se muestra el número de reviews " \
    "con dicha nota en formato histograma")
    cursor = conn.cursor()
    subpagina = st.selectbox(
        "Seleccione una opción",
        ["📋 Blanc page","🌐 General" ,"🗃️ Por tipo de artículo","📦 Artículo individual"]
    )

    resultado = None
    titulo = ""

    if subpagina != "📋 Blanc page":
        if subpagina == "🌐 General":
            st.write("Mostrando datos de: **TODAS LAS CATEGORÍAS**")
            query = """
                SELECT overall,COUNT(*) AS n_reviews
                FROM reviews
                GROUP BY overall
                ORDER BY overall 
                """
            titulo = "General"
            cursor.execute(query)
            resultado = cursor.fetchall()
        elif subpagina == "🗃️ Por tipo de artículo" :
            subpagina2 = st.selectbox(
                "Seleccione una categoría",
                ["📋 Blanc page","🎮 Videojuegos" ,"🎵 Música digital","🎹 Instrumentos musicales","🧸 Juguetes"]
            )
            if subpagina2 != "📋 Blanc page":
                categoria = mapeo_categorias_sql[subpagina2]
                st.write(f"Mostrando datos de: **{subpagina2.upper()}**")
                query = """
                    SELECT overall,COUNT(*) AS n_reviews
                    FROM reviews
                    WHERE categoria = %s
                    GROUP BY overall
                    ORDER BY overall 
                    """
                titulo = subpagina2[2:]
                cursor.execute(query, (categoria,))
                resultado = cursor.fetchall()
            else:
                st.stop()
        elif subpagina == "📦 Artículo individual":
            asin_input = st.text_input("Introduce el ID del producto (ej: B00004T9UF):").strip()
            if asin_input:    
                cursor.execute("SELECT COUNT(*) as total FROM Reviews WHERE asin = %s", (asin_input,))
                if cursor.fetchone()['total'] == 0:
                    st.error(f"El producto '{asin_input}' no existe en la base de datos.")
                    st.stop()
            else:
                st.info("Introduce un código ASIN para comenzar la búsqueda.")
                st.stop()                

            st.success(f"✅ **Producto {asin_input} encontrado con éxito.**")
            
            query_datos = """SELECT overall, COUNT(*) as n_reviews
                FROM reviews 
                WHERE asin = %s 
                GROUP BY overall 
                ORDER BY overall 
                """
            titulo = f"Artículo {asin_input}"
            cursor.execute(query_datos, (asin_input,))
            resultado = cursor.fetchall()


        if resultado:
            df = pd.DataFrame(resultado)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True)

            # Creamos la gráfica con Seaborn
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x="overall", y="n_reviews", data=df, palette="viridis", ax=ax)

            ax.set_title(f"Distribución por nota - {titulo}")
            ax.set_xlabel("Nota (1-5)")
            ax.set_ylabel("Número de reviews")
            for container in ax.containers:
                ax.bar_label(container, fmt='%.0f', padding=3)
            st.pyplot(fig)
        else:
            st.info(f"No hay datos disponibles para {subpagina} en la base de datos.")
    

elif pagina == "Evolución Temporal por Categoría":
    st.subheader("📈 Evolución Temporal por Categoría")
    st.markdown("A continuación se muestra el " \
    "crecimiento acumulado del número de reseñas a lo largo del tiempo")
    cursor = conn.cursor()
    subpagina = st.selectbox(
        "Seleccione una categoría",
        ["📋 Blanc page","🎮 Videojuegos" ,"🎵 Música digital","🎹 Instrumentos musicales","🧸 Juguetes"]
    )
    if subpagina != "📋 Blanc page":
        categoria = mapeo_categorias_sql[subpagina]
        st.write(f"Mostrando datos de: **{subpagina.upper()}**")
        query = """
            SELECT reviewTime, COUNT(*) as n_reviews
            FROM reviews 
            WHERE categoria = %s
            GROUP BY reviewTime
            ORDER BY reviewTime ASC
            """
        titulo = subpagina[2:]
        cursor.execute(query,(categoria,))
        resultado = cursor.fetchall()

        if resultado:
            df = pd.DataFrame(resultado)
            #Calculamos la suma acumulativa
            df['reviewTime'] = pd.to_datetime(df['reviewTime'])
            df['acumulado'] = df['n_reviews'].cumsum()
            #Lo pasamos a unix en nanosegundos 
            df['unixTime'] = df['reviewTime'].view('int64') // 10**9
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
                )

            # Creamos la gráfica con Seaborn
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df['unixTime'], df['acumulado'], color="#f206bb", linewidth=2)
            #Pasamos todo a notación científica (por si acaso)
            ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
            ax.set_title(f"Evolución acumulada de {titulo}")
            ax.set_xlabel("Tiempo")
            ax.set_ylabel("Número de reviews hasta el momento")

            ax.grid(True, linestyle='--', alpha=0.5)
            
            st.pyplot(fig)
        else:
            st.info(f"No hay datos disponibles para {subpagina} en la base de datos.")

elif pagina == "Histograma Reviews por Usuario":
    st.subheader("👤 Histograma Reviews por Usuario")
    st.markdown("A continuación se muestra el " \
    "histograma del número de usuarios que ha hecho esa cantidad de reviews")
    cursor = conn.cursor()
    query = """
        SELECT aux.n_reviews, COUNT(aux.reviewerID) AS n_users
        FROM (
        SELECT reviewerID, COUNT(*) AS n_reviews
        FROM reviews
        GROUP BY reviewerID ) AS aux
        GROUP BY aux.n_reviews
        ORDER BY aux.n_reviews ASC
        """
    cursor.execute(query)
    resultado = cursor.fetchall()

    if resultado:
        df = pd.DataFrame(resultado)
        #Filtramos para evitar sobrecargar el sistema
        df_plot = df[df['n_reviews'] <= 50]
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
            )

        # Creamos la gráfica con Seaborn
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x="n_reviews", y="n_users", data=df_plot, palette="viridis", ax=ax)
        ax.set_title(f"Reviews por usuario")
        ax.set_xlabel("Número de reviews")
        ax.set_ylabel("Número de users")
        ax.grid(True, linestyle='--', alpha=0.5)
        
        st.pyplot(fig)
        st.write(f"El número de reviews para el que hay más usuarios: **{df['n_reviews'].iloc[0]}**")
    else:
        st.info(f"No hay datos disponibles en la base de datos.")

elif pagina == "Nube de Palabras por Categoría":
    st.subheader("💭 Nube de Palabras por Categoría")
    st.markdown("A continuación la nube de palabras de aquellas palabras " \
    "más comunes en las reviews")
    subpagina = st.selectbox(
            "Selecciona una categoría para la nube",
            ["🎮 Videojuegos" ,"🎵 Música digital","🎹 Instrumentos musicales","🧸 Juguetes"]
        )
        
    categoria_mongo = mapeo_categorias_mongo[subpagina]
    coleccion = db_mongo[categoria_mongo]
    #Limitamos para no saturar
    cursor_mongo = coleccion.find({}, {"summary": 1, "_id": 0}).limit(2000)
    #Unimos todo el texto para trabajar directamente sobre todo ello entero (Ayuda IA para no saturar )
    texto_completo = " ".join([doc['summary'] for doc in cursor_mongo if doc.get('summary')])

    if texto_completo:
        wordcloud = WordCloud(
            width=800, 
            height=400,
            background_color='white',
            min_word_length=4,
            colormap='magma', 
            min_font_size=10
        ).generate(texto_completo)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear') #Ayuda de IA para la representación
        plt.axis("off")

        st.pyplot(fig)
        
        st.success(f"Nube generada con éxito para {subpagina}")
    else:
        st.warning("No hay suficientes reseñas de texto para esta categoría.")

elif pagina == "🌟 Visualización Personalizada":
    st.subheader("🗺️ Mapa de Calor: Estacionalidad de Reviews")
    st.markdown("A continuación se muestra en qué meses y años se concentra el mayor volumen de reseñas en la plataforma")
    
    cursor = conn.cursor()
    
    subpagina = st.selectbox(
        "Seleccione una categoría para el Mapa de Calor",
        ["📋 Blanc page", "🎮 Videojuegos" ,"🎵 Música digital","🎹 Instrumentos musicales","🧸 Juguetes","🌍 Todo"]
    )
    if subpagina != "📋 Blanc page":
        if subpagina == "🌍 Todo":
            st.write("Mostrando datos de: **TODAS LAS CATEGORÍAS**")
            query = """
                SELECT YEAR(reviewTime) AS año, MONTH(reviewTime) AS mes, COUNT(*) AS total_reseñas
                FROM reviews
                WHERE YEAR(reviewTime) > 2005 
                GROUP BY año, mes
                ORDER BY año, mes
                """
            titulo = "todas las categorías"
            cursor.execute(query)
        else:
            categoria = mapeo_categorias_sql[subpagina]
            st.write(f"Mostrando datos de: **{subpagina.upper()}**")
            query = """
                SELECT YEAR(reviewTime) AS año, MONTH(reviewTime) AS mes, COUNT(*) AS total_reseñas
                FROM reviews
                WHERE categoria = %s AND YEAR(reviewTime) > 2005 
                GROUP BY año, mes
                ORDER BY año, mes
                """
            titulo = subpagina[2:]
            cursor.execute(query, (categoria,))
        resultado = cursor.fetchall()        
        if resultado:
            df = pd.DataFrame(resultado)
            #Mapeamos los nombres para darles un valor categórico
            meses_nombres = {
                1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 
                7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'
            }
            df['mes_nombre'] = df['mes'].map(meses_nombres)
            
            # Pivotamos la tabla: años en x, meses en y
            matriz_heatmap = df.pivot(index='mes_nombre', columns='año', values='total_reseñas')
            
            # Ordenamos los meses correctamente para que no salgan alfabéticamente
            orden_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
            matriz_heatmap = matriz_heatmap.reindex(orden_meses)

            # Dibujamos el Heatmap con Seaborn
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.heatmap(matriz_heatmap, cmap="coolwarm", linewidths=.5, annot=False, ax=ax)

            ax.set_title("Volumen de reseñas por Mes y Año")
            ax.set_xlabel("Año")
            ax.set_ylabel("Mes")
            plt.xticks(rotation=45)
            
            st.pyplot(fig)
        else:
            st.warning("No hay suficientes datos para generar el mapa de calor.")        

elif pagina == "🚪 Salir":
    st.balloons() # Un toque de despedida
    st.header("¡Hasta pronto!")
    st.write("La ejecución del dashboard se ha detenido. Puedes cerrar esta pestaña.")
    
    # Esto detiene cualquier ejecución posterior del script
    st.stop()