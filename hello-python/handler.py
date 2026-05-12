import os
import pymysql

def get_secret(name):
    """Lit un secret OpenFaaS depuis le système de fichiers."""
    path = f"/var/openfaas/secrets/{name}"
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    return None

def handle(event, context):
    # Variables classiques (non sensibles)
    db_host = os.environ.get("DB_HOST")
    db_user = os.environ.get("DB_USER")
    db_name = os.environ.get("DB_NAME")
    
    # Récupération du mot de passe sécurisé
    # Si le secret n'existe pas, on tente de rabattre sur l'env (pour le debug)
    db_password = get_secret("db-password") or os.environ.get("DB_PASSWORD")

    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5 # Évite d'attendre 30s si la DB est injoignable
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version;")
            result = cursor.fetchone()

        connection.close()

        return {
            "statusCode": 200,
            "body": f"🚀🚀🚀 SUCCEÈS ! Connecté à MariaDB v{result['version']} sur {db_host}"
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"❌ ERREUR DE CONNEXION : {str(e)}"
        }