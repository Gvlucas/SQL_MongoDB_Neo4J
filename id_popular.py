import pymysql
from configuracion import *

def conexion_mysql():
    """Crea una conexion con MySQL"""
    conexion_mysql = pymysql.connect(
        host=MYSQL_CONFIG['host'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database']
    )
    return conexion_mysql

def articulos_populares(conexion,categoria:str)->list:
    """Ordena los articulos más populares de una categoría"""
    cursor=conexion.cursor()
    query="""SELECT asin, COUNT(*) AS total FROM Reviews
    WHERE categoria = %s
    GROUP BY asin
    ORDER BY total DESC"""
    cursor.execute(query,(categoria,))
    t_resultado=cursor.fetchall()
    resultado=[]
    for t in t_resultado:
        resultado.append(t[0])
    return resultado

def articulos_id(conexion,categoria: str,id: str)->list:
    """Devuelve los articulos de una categoría que un usuario ha evaluado"""
    cursor=conexion.cursor()
    query="""SELECT asin FROM Reviews
    WHERE reviewerID = %s AND categoria = %s"""
    cursor.execute(query,(id,categoria))
    t_resultado=cursor.fetchall()
    resultado=[]
    for t in t_resultado:
        resultado.append(t[0])
    return resultado

def mas_populares(populares:list,id_articulos:list)-> list:
    """Compara los articulos más populares con los evaluados por un usuario"""
    resultado=[]
    for p in populares: #Recorremos la lista populares y nos quedamos con los 10 primeros elementos que no esten en id_articulos
        if p not in id_articulos:
            resultado.append(p)
        if len(resultado)==10:
            break
    
    return resultado

def comprobar_id(conexion):
    """Permite elegir un id de usuario"""
    id=()
    sql="""SELECT reviewerID
        FROM Reviews
        WHERE reviewerID=%s"""
    cursor=conexion.cursor()
    while id==():
        id=input("Introduce el id:")
        cursor.execute(sql,(id,))
        id=cursor.fetchall()
    return id[0][0]

def elegir_categoria():
    """Permite elegir una de las categorías diponibles"""
    print("""1. Videojuegos
2. Música digital
3. Instrumentos musicales
4. Juguetes""")
    categoria=input("Elige: ")
    while categoria not in ["1","2","3","4"]: #Pedimos el input hasta que la respuesta sea correcta
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
    return categoria

if __name__ == "__main__":
    conexion=conexion_mysql()
    categoria=elegir_categoria()
    id=comprobar_id(conexion)
    articulos=articulos_populares(conexion,categoria)
    id_articulos=articulos_id(conexion,categoria,id)
    print(mas_populares(articulos,id_articulos))
