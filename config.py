import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')
ROOT_USER_IDS = os.environ.get('ROOT_USER_ID')
AVITO_CLIENT_ID = os.environ.get('AVITO_CLIENT_ID')
AVITO_CLIENT_SECRET = os.environ.get('AVITO_CLIENT_SECRET')
DOCKER_API_URL = os.environ.get('DOCKER_API_URL')
DOCKER_CONTAINER_NAME = os.environ.get('DOCKER_CONTAINER_NAME')
GIGACHAT_CREDS = os.environ.get('GIGACHAT_CREDS')

# Webhook settings
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')  # ngrok URL или ваш сервер
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
ROBOKASSA_PATH = '/result-payment'

# Web server settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 3001
