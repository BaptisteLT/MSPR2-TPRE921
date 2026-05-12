import json
import os
import base64
import pymysql
import pyotp
import qrcode
from io import BytesIO
from cryptography.fernet import Fernet

# Clé de chiffrement statique pour le PoC (32 bytes en base64)
FERNET_KEY = base64.urlsafe_b64encode(b'COFRAP_SECRET_KEY_12345678901234')

def handle(event, context):
    try:
        if not event.body:
            return json.dumps({"error": "Requête vide."})
            
        data = json.loads(event.body.decode('utf-8'))
        username = data.get("username")
        
        if not username:
            return json.dumps({"error": "Le champ 'username' est requis."})

        # 1. Génération du secret 2FA (TOTP)
        secret = pyotp.random_base32()
        
        # 2. Création de l'URL pour Google Authenticator et du QR Code
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name="COFRAP")
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # 3. Chiffrement du secret avant stockage en base
        cipher_suite = Fernet(FERNET_KEY)
        encrypted_secret = cipher_suite.encrypt(secret.encode('utf-8')).decode('utf-8')

        # 4. Enregistrement en base de données (Update de l'utilisateur existant)
        conn = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            database=os.environ.get("DB_NAME"),
            cursorclass=pymysql.cursors.DictCursor
        )

        with conn.cursor() as cursor:
            sql = "UPDATE users SET MFA = %s WHERE username = %s"
            cursor.execute(sql, (encrypted_secret, username))
        
        conn.commit()
        conn.close()

        # 5. On retourne le QR Code au frontend
        return json.dumps({
            "message": "2FA genere avec succes",
            "username": username,
            "qr_code_2fa_base64": qr_base64
        })

    except Exception as e:
        return json.dumps({"error": f"Erreur interne : {str(e)}"})