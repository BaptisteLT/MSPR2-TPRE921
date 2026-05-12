import json
import os
import time
import base64
import pymysql
import bcrypt
import pyotp
from cryptography.fernet import Fernet

FERNET_KEY = base64.urlsafe_b64encode(b'COFRAP_SECRET_KEY_12345678901234')
SIX_MOIS_EN_SECONDES = 15552000

def handle(event, context):
    try:
        if not event.body:
            return json.dumps({"error": "Requête vide."})
        data = json.loads(event.body.decode('utf-8'))
        username = data.get("username")
        password_clear = data.get("password")
        totp_code = data.get("totp_code")
        
        if not all([username, password_clear, totp_code]):
            return json.dumps({"error": "username, password et totp_code sont requis."})

        conn = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor
        )

        with conn.cursor() as cursor:
            cursor.execute("SELECT password, MFA, gendate, expired FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                conn.close()
                return json.dumps({"error": "Utilisateur non trouve."})

            if user['expired'] == 1:
                conn.close()
                return json.dumps({"error": "Compte expire. Veuillez renouveler vos identifiants."})

            # 1. Vérification de l'ancienneté (6 mois)
            current_time = int(time.time())
            if (current_time - user['gendate']) > SIX_MOIS_EN_SECONDES:
                cursor.execute("UPDATE users SET expired = 1 WHERE username = %s", (username,))
                conn.commit()
                conn.close()
                return json.dumps({"error": "Identifiants expires (plus de 6 mois). Relancez le processus de creation."})

            # 2. Vérification du mot de passe
            hashed_password = user['password'].encode('utf-8')
            if not bcrypt.checkpw(password_clear.encode('utf-8'), hashed_password):
                conn.close()
                return json.dumps({"error": "Mot de passe incorrect."})

            # 3. Vérification du code 2FA
            cipher_suite = Fernet(FERNET_KEY)
            decrypted_secret = cipher_suite.decrypt(user['MFA'].encode('utf-8')).decode('utf-8')
            
            totp = pyotp.TOTP(decrypted_secret)
            if not totp.verify(totp_code):
                conn.close()
                return json.dumps({"error": "Code 2FA incorrect."})

        conn.close()
        return json.dumps({"message": "Authentification reussie ! Bienvenue."})

    except Exception as e:
        return json.dumps({"error": f"Erreur interne : {str(e)}"})