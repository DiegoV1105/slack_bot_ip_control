import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import json
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

slack_token = os.getenv('SLACK_TOKEN')
slack_channel = os.getenv('SLACK_CHANNEL')
digitalocean_token = os.getenv('DIGITALOCEAN_TOKEN')
firewall_id = os.getenv('FIREWALL_ID')
database_id = os.getenv('DATABASE_ID')

slack_client = WebClient(token=slack_token)

processed_messages = set()


def add_database_access(ip):
    url = f"https://api.digitalocean.com/v2/databases/{database_id}/firewall"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {digitalocean_token}"
    }
    data = {
        "rules": [
            {
                "type": "ip_addr",
                "value": ip
            }
        ]
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info("IP agregada correctamente a la base de datos.")
            return True
        else:
            logger.error(f"Error al agregar IP a la base de datos: {response.status_code}, {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con DigitalOcean: {e}")
        return False


def show_help(canal_id):
    try:
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📝 Comandos Disponibles",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Aquí tienes una lista de los comandos que puedes usar:"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• `!actualizar_ip <IP>`\n"
                            "   _Actualiza la IP en las reglas de firewall de DigitalOcean._\n"
                            "   *Ejemplo:* `!actualizar_ip 192.168.1.100`"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• `!ayuda`\n"
                            "   _Muestra esta lista de comandos._"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "💡 Usa estos comandos para gestionar el acceso a tu base de datos."
                    }
                ]
            }
        ]

        slack_client.chat_postMessage(
            channel=canal_id,
            blocks=blocks,
            text="Aquí tienes una lista de los comandos que puedes usar:"
        )
        logger.info("Lista de comandos mostrada.")
    except SlackApiError as e:
        logger.error(f"Error al mostrar la ayuda: {e.response['error']}")


def listen_commands():
    try:
        response = slack_client.conversations_list()
        canal_id = None

        for canal in response["channels"]:
            if canal["id"] == slack_channel:
                canal_id = canal["id"]
                break

        if not canal_id:
            logger.error(f"Canal con ID '{slack_channel}' no encontrado.")
            return

        response = slack_client.conversations_history(channel=canal_id, limit=1)

        logger.debug(f"Respuesta de la API: {response}")

        if not response or "messages" not in response or not response["messages"]:
            logger.error("No se pudieron obtener los mensajes del canal.")
            return

        mensaje = response["messages"][0]
        mensaje_id = mensaje.get("ts")

        if mensaje_id in processed_messages:
            return

        text = mensaje.get("text", "").strip()
        logger.debug(f"Mensaje recibido: {text}")

        if text == "!" or text == "!ayuda":
            show_help(canal_id)
            processed_messages.add(mensaje_id)
        elif text.startswith("!actualizar_ip"):
            ip = text.split(" ")[1]
            if add_database_access(ip):
                slack_client.chat_postMessage(
                    channel=canal_id,
                    text=f"IP actualizada correctamente a: {ip}"
                )
                logger.success(f"IP actualizada correctamente a: {ip}")
            else:
                slack_client.chat_postMessage(
                    channel=canal_id,
                    text=f"Error al actualizar la IP: {ip}"
                )
                logger.error(f"Error al actualizar la IP: {ip}")
            processed_messages.add(mensaje_id)

    except SlackApiError as e:
        logger.error(f"Error en Slack: {e.response['error']}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")


def get_database_id():
    url = "https://api.digitalocean.com/v2/databases"
    headers = {
        "Authorization": f"Bearer {digitalocean_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            databases = response.json().get("databases", [])
            for db in databases:
                print(f"Nombre: {db['name']}, ID: {db['id']}")
            return databases
        else:
            print(f"Error al obtener bases de datos: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con DigitalOcean: {e}")
        return None

if __name__ == "__main__":
    logger.info("Bot iniciado. Esperando comandos...")
    try:
        while True:
            listen_commands()
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Bot detenido manualmente. Saliendo...")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    finally:
        logger.info("Proceso terminado.")
