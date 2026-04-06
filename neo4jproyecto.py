from neo4j import GraphDatabase
from configuracion import *
import pymysql
import random

# Autores: Gonzalo Velasco y Lucía Lozano
# Proyecto Bases de Datos - neo4JProyecto.py

N_USUARIOS=30

def conexion_neo4j():
    """Crea una conexion con Neo4J"""
    driver =GraphDatabase.driver(NEO4J_CONFIG["uri"], auth=(NEO4J_CONFIG["user"], NEO4J_CONFIG["password"]))
    return driver

def conexion_mysql():
    """Crea una conexion con MySQL"""
    conexion_mysql = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database']
    )
    return conexion_mysql

def borrar_datos(session):
    """Borra todos los nodos y relaciones existentes."""
    session.run("MATCH (n) DETACH DELETE n")

def top_n_usuarios(conexion:pymysql.connect):
    """Obtiene los n usuarios con más reviews"""
    cursor=conexion.cursor()
    query=f"""
    SELECT reviewerID, COUNT(*) AS total
    FROM Reviews
    GROUP BY reviewerID
    ORDER BY total DESC
    LIMIT {N_USUARIOS}"""
    cursor.execute(query)
    reviewers=[]
    for r in cursor.fetchall():
        reviewers.append(r[0])
    return reviewers

def reviews(conexion: pymysql.connect,reviewerID):
    """Obtiene los datos de las reviews que ha hecho un usuario"""
    cursor=conexion.cursor()
    query="""
    SELECT asin, overall
    FROM Reviews
    WHERE reviewerID = %s"""
    cursor.execute(query,(reviewerID,))
    return cursor.fetchall()

def correlacion_Pearson(u: dict,v: dict):
    """Halla la correlación de Pearson entre dos usuarios"""
    ru=0
    rv=0
    contador=0
    for a in u.keys():
        if a in v.keys():
            ru+=u[a]
            rv+=v[a]
            contador+=1
    if contador==0:
        return None
    ru/=contador
    rv/=contador
    
    numerador=0
    den_u=0
    den_v=0
    for a in u.keys():
        if a in v.keys():
            numerador+=(u[a]-ru)*(v[a]-rv)
            den_u+=(u[a]-ru)**2
            den_v+=(v[a]-rv)**2
    denominador=((den_u**0.5)*(den_v**0.5))
    if denominador==0:
        return None
    corr_pearson=numerador/denominador
    return corr_pearson

def relaciones_neo4j(session,correlaciones):
    """Crea la base de datos en Neo4j"""
    for c in correlaciones:
        query="""MERGE (u:reviewer {id:$u})
        MERGE (v:reviewer {id:$v})
        CREATE (u)-[:CORRELACION {correlacion:$correlacion}]->(v)"""
        session.run(query,u=c[0],v=c[1],correlacion=c[2])

def mas_vecinos(session):
    """Halla al usuario con más vecinos en Neo4j"""
    query="""MATCH (u:reviewer)-[:CORRELACION]->(v)
    RETURN u.id AS usuario, COUNT(v) AS vecinos
    ORDER BY vecinos DESC
    LIMIT 1
    """
    resultado = session.run(query)
    return resultado

def elegir_categoria():
    """Permite elegir una de las categorías diponibles"""
    print("""1. Videojuegos
    2. Música digital
    3. Instrumentos musicales
    4. Juguetes""")
    categoria=input("Elige: ")
    while categoria not in ["1","2","3","4"]:
        print("Categoría incorrecta introduzca el número")
        categoria=input("Elige: ")
    if categoria=="1":
        categoria="video_games"
    elif categoria=="2":
        categoria="digital_music"
    elif categoria=="3":
        categoria="musical_instruments"
    else:
        categoria="toys_games"
    
    n=input("Introduzca el número de artículos: ")
    
    inte=False
    while not inte:
        try:
            int(n)
            inte=True
        except ValueError:
            n=input("Introduzca el número de artículos: ")
    return categoria,n

def asin_categoria(conexion,categoria):
    """Devuelve los valores únicos de la columna asin de una categoría"""
    query="""SELECT DISTINCT asin
    FROM Reviews
    WHERE categoria=%s"""
    cursor=conexion.cursor()
    cursor.execute(query,(categoria,))
    return cursor.fetchall()

def asin_usuarios(conexion: pymysql.connect,lista_asin):
    """Para una lista de artículos devuelve los usuarios, sus notas y la hora de la review."""
    cursor=conexion.cursor()
    query="""SELECT reviewerID,overall,reviewTime
    FROM Reviews
    WHERE asin = %s"""
    dic={}
    for asin in lista_asin:
        cursor.execute(query,(asin,))
        dic[asin]=cursor.fetchall()
    return dic

def asin_neo4j(session,dic: dict):
    """Crea una base de datos en Neo4j con los usuarios y los articulos"""
    query="""MERGE (u:usuario {id:$id})
    MERGE (a:articulo {id:$asinID})
    MERGE (u)-[:REVIEW {hora:$reviewTime, nota:$overall}]->(a)"""
    for asin in dic.keys():
        for t_user in dic[asin]:
            session.run(query,id=t_user[0],asinID=asin,reviewTime=t_user[2],overall=t_user[1])

def cuatrocientos_usuarios(conexion):
    """Busca los 400 primeros usuarios organizados por nombre"""
    query="""SELECT DISTINCT reviewerID, reviewerName
    FROM Reviews
    ORDER BY reviewerName
    LIMIT 400"""
    cursor=conexion.cursor()
    cursor.execute(query)
    t_resultado=cursor.fetchall()
    resultado=[]
    for t in t_resultado:
        resultado.append(t[0])
    return resultado

def dos_categorias(conexion,reviewers):
    """Busca usuarios con reviews en dos o más categorías"""
    cursor=conexion.cursor()
    query="""SELECT reviewerID, categoria,COUNT(DISTINCT asin)
    FROM Reviews
    WHERE reviewerID = %s
    GROUP BY reviewerID, categoria"""
    usu_categorias={}
    for reviewer in reviewers:
        cursor.execute(query,(reviewer,))
        resultado=cursor.fetchall()
        categorias=[]
        for r in resultado:
            categorias.append((r[1],r[2]))
        if len(categorias)>1:
            usu_categorias[reviewer]=categorias
    return usu_categorias

def neo4j_user_category(session,usu_categorias):
    """Crea la base de datos en neo4j que relaciona los usuarios con las categorías que han evaluado"""
    query="""MERGE (u:usuario {id:$id})
    MERGE (c:categoria {nombre:$nombre})
    MERGE (u)-[:REVIEW {total:$total}]->(c)"""
    for u in usu_categorias.keys():
        for c in usu_categorias[u]:
            session.run(query,id=u,nombre=c[0],total=c[1])

def cinco_articulos(conexion):
    """Devuelve los 5 artículos con más reviews pero por debajo de 40"""
    query="""SELECT asin
    FROM Reviews
    GROUP BY asin
    HAVING COUNT(*) < 40
    ORDER BY COUNT(*) DESC
    LIMIT 5"""
    cursor=conexion.cursor()
    cursor.execute(query)
    tresultado=cursor.fetchall()
    resultado=[]
    for t in tresultado:
        resultado.append(t[0])
    return resultado

def articulos_usuario(conexion,articulos):
    query="""SELECT reviewerID
    FROM Reviews
    WHERE asin = %s"""
    usuarios=[]
    articulo_usuario_dic={}
    cursor=conexion.cursor()
    for a in articulos:
        cursor.execute(query,(a,))
        resultado=cursor.fetchall()
        articulo_usuario=[]
        for u in resultado:
            articulo_usuario.append(u[0])
            if u[0] not in usuarios:
                usuarios.append(u[0])
        articulo_usuario_dic[a]=articulo_usuario

    return usuarios,articulo_usuario_dic

def usuario_usuario(conexion,usuarios):
    """Devuelve el número de artículos en común entre dos usuarios"""
    query="""SELECT asin 
    FROM Reviews
    WHERE reviewerID=%s"""
    usuarios_asin={}
    cursor=conexion.cursor()
    for u in usuarios:
        cursor.execute(query,(u,))
        tresultado=cursor.fetchall()
        resultado=[]
        for r in tresultado:
            resultado.append(r[0])
        usuarios_asin[u]=resultado
    
    contador_usuarios=[]
    keys=list(usuarios_asin.keys())
    for i in range(len(keys)):
        for j in range(i+1,len(keys)):
            u=keys[i]
            v=keys[j]
            contador=0
            for a in usuarios_asin[u]:
                if a in usuarios_asin[v]:
                    contador+=1
            contador_usuarios.append((u,v,contador))
    
    return contador_usuarios

def neo4j_articulo_usuario_usuario(session,articulo_usuario_dic,contador_usuarios):
    """Crea la base de datos en Neo4j que relaciona a los usuarios con 5 artículos"""
    query1="""MERGE (u:usuario {id:$id})
    MERGE(a: articulo {asin:$asin})
    MERGE (u)-[:REVIEW]->(a)"""
    query2="""MERGE (u:usuario {id:$id})
    MERGE (v:usuario {id:$id2})
    MERGE (u)-[:COMUN {total:$total}]->(v)"""
    for a in articulo_usuario_dic.keys():
        for u in articulo_usuario_dic[a]:
            session.run(query1,id=u,asin=a)
    
    for t in contador_usuarios:
        session.run(query2,id=t[0],id2=t[1],total=t[2])

if __name__ == "__main__":
    eleccion=0
    while eleccion!=5:
        print("""MENU
-------------------
1.Obtener similitudes entre usuarios y mostrar los enlaces en Neo4J
2.Obtener enlaces entre usuarios y artículos
3.Obtener algunos usuarios que han visto más de un determinado tipo de artículo
4.Artículos populares y artículos en común entre usuarios
5.Salir""")
        try:
            eleccion=int(input("Elija:"))
        except ValueError:
            print("Introduce un número")
            eleccion=0
        conexion=conexion_mysql()
        driver=conexion_neo4j()
        #===================4.1=======================
        if eleccion==1:
            
            reviewers=top_n_usuarios(conexion)
            reviewers_reviews={}
            for id in reviewers:
                l_reviews=reviews(conexion,id)
                dic_overall={}
                for l in l_reviews:
                    dic_overall[l[0]]=l[1]
                reviewers_reviews[id]=dic_overall
            
            correlaciones = []
            for i in range(len(reviewers)):
                for j in range(i+1, len(reviewers)):
                    u = reviewers[i]
                    v = reviewers[j]
                    corr = correlacion_Pearson(reviewers_reviews[u], reviewers_reviews[v])
                    if corr is not None:
                        correlaciones.append((u, v, corr))
            
            
            
            with driver.session() as session:
                borrar_datos(session)
                relaciones_neo4j(session,correlaciones)
                resultado=mas_vecinos(session)
                for r in resultado:
                    print(r)
        #===================4.2=======================
        if eleccion==2:
            categoria,n=elegir_categoria()
            asins_t=asin_categoria(conexion,categoria)
            asins=[]
            for a in asins_t:
                asins.append(a[0])
            aleatorio=random.sample(asins,k=int(n))
            dic=asin_usuarios(conexion,aleatorio)
            with driver.session() as session:
                borrar_datos(session)
                asin_neo4j(session,dic)
                print("Carga de datos completada en Neo4j")
            
        #===================4.3=======================
        if eleccion==3:
            usuarios=cuatrocientos_usuarios(conexion)
            usu_categorias=dos_categorias(conexion,usuarios)
            with driver.session() as session:
                borrar_datos(session)
                neo4j_user_category(session,usu_categorias)
                print("Carga de datos completada en Neo4j")
            stop=input("Cuando quiera continuar presione ENTER:")
        #===================4.4=======================
        if eleccion==4:
            top_articulos=cinco_articulos(conexion)
            usuarios,articulo_usuario_dic=articulos_usuario(conexion,top_articulos)
            en_comun=usuario_usuario(conexion,usuarios)
            with driver.session() as session:
                borrar_datos(session)
                neo4j_articulo_usuario_usuario(session,articulo_usuario_dic,en_comun)
                print("Carga de datos completada en Neo4j")