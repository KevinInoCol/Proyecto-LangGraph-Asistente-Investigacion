# utils/enviar_correo.py

from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

# Obtenemos las credenciales desde el .env
APP_PASSWORD_GMAIL = os.getenv("APP_PASSWORD_GMAIL")
CORREO_REMITENTE = os.getenv("EMAIL_REMITENTE")
CORREO_DESTINO = os.getenv("EMAIL_RECIPIENT") # Usaremos el mismo nombre de variable que antes

def send_notification_email_smtp():
    """
    Crea y envía un correo de notificación usando SMTP y una Contraseña de Aplicación.
    """
    # Verificamos que todas las variables de entorno necesarias existan
    if not all([APP_PASSWORD_GMAIL, CORREO_REMITENTE, CORREO_DESTINO]):
        print("ERROR: Faltan variables de entorno (APP_PASSWORD_GMAIL, EMAIL_REMITENTE, EMAIL_RECIPIENT). No se puede enviar el correo.")
        return

    print("---PREPARANDO CORREO DE NOTIFICACIÓN (vía SMTP)---")

    try:
        # El mensaje es fijo, como en tu solicitud original
        mensaje_fijo = (
            "Tenemos un paper de Motion Retargeting, lo puedes leer en nuestros artículos de Notion "
            "o puedes consultar respecto de él y muchos otros papers más en nuestro sistema de consultas: "
            "www.consultasmotionretargeting.com"
        )

        email = EmailMessage()
        email["From"] = CORREO_REMITENTE
        email["To"] = CORREO_DESTINO
        email["Subject"] = "Nuevo Paper de Motion Retargeting Disponible"
        email.set_content(mensaje_fijo)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(CORREO_REMITENTE, APP_PASSWORD_GMAIL)
            smtp.send_message(email)
        
        print(f"Correo enviado con éxito a {CORREO_DESTINO} usando SMTP.")

    except Exception as e:
        print(f"Ocurrió un error al enviar el correo con SMTP: {e}")