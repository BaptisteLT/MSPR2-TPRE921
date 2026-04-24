import os
import pymysql

def handle(event, context):
    # Récupération des identifiants depuis le stack.yaml
    db_host = os.environ.get("DB_HOST")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    try:
        # Tentative de connexion à MariaDB
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        # Si on arrive ici, on fait une petite requête pour demander la version
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version;")
            result = cursor.fetchone()

        connection.close()

        return {
            "statusCode": 200,
            "body": f"SUCCÈS ! Connecté à MariaDB (Version: {result['version']}) sur l'hôte {db_host}"
        }

    except Exception as e:
        # Si ça plante, on affiche l'erreur exacte pour pouvoir réparer
        return {
            "statusCode": 500,
            "body": f"ERREUR DE CONNEXION : {str(e)}"
        } 
         
         