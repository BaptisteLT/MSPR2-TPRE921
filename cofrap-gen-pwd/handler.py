import json
import os
import time
import secrets
import string
import base64
import pymysql
import bcrypt
import qrcode
from io import BytesIO

def handle(event, context):
    try:
        # 1. On récupère le "username" envoyé par le frontend
        if not event.body:
            return json.dumps({"error": "Requête vide."})
            
        data = json.loads(event.body.decode('utf-8'))
        username = data.get("username")
        
        if not username:
            return json.dumps({"error": "Le champ 'username' est requis."})

        # 2. On génère le mot de passe complexe de 24 caractères
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        password = ''.join(secrets.choice(alphabet) for i in range(24))

        # 3. On génère le QR Code contenant le mot de passe en clair
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(password)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # On convertit l'image en Base64 pour l'envoyer facilement sur le web
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # 4. On chiffre le mot de passe avant de le stocker (Sécurité !)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 5. On se connecte à la base de données MariaDB via les variables d'environnement
        conn = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor
        )

        # 6. On enregistre le nouvel utilisateur
        with conn.cursor() as cursor:
            gendate = int(time.time()) # Timestamp actuel
            
            # On initialise le MFA à vide, il sera rempli par la fonction cofrap-gen-2fa plus tard
            sql = "INSERT INTO users (username, password, MFA, gendate) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, hashed_password, "", gendate))
        
        conn.commit()
        conn.close()

        # 7. On renvoie le mot de passe en clair et le QR Code au frontend
        return json.dumps({
            "message": "Utilisateur cree avec succes",
            "username": username,
            "password": password,
            "qr_code_base64": qr_base64
        })

    except pymysql.err.IntegrityError:
        return json.dumps({"error": "Cet utilisateur existe deja."})
    except Exception as e:
        return json.dumps({"error": f"Erreur interne : {str(e)}"})