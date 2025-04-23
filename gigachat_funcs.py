from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import logging
from config import GIGACHAT_CREDS
from models.gigachat_config import GigachatConfig



# Укажите ключ авторизации, полученный в личном кабинете, в интерфейсе проекта GigaChat API
async def generate_application_description(messages, prompt, access_token):
    print(f"access_token: {access_token}")
    from avito import get_gigachat_key
    print(f"Начало генерации описания. Промпт: {prompt}")
    if not access_token:
        access_token = get_gigachat_key()  # Автоматический запрос токена
        if not access_token:
            raise ValueError("Токен GigaChat не получен!")
    print(prompt)
    payload = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content=prompt
            ),
            Messages(
                role=MessagesRole.USER,
                content=str(messages)
            )
        ],
        temperature=0.7
    )

    async with GigaChat(credentials=access_token, verify_ssl_certs=False,
                        model='GigaChat-2-Pro') as giga:  # , model='GigaChat-2-Pro'
        response = giga.chat(payload)
        print(response.choices[0].message.content)
        return response.choices[0].message.content


logger = logging.getLogger(__name__)

async def call_gigachat_api(history, prompt1, access_token):
    print(f"access_token: {access_token}")
    from avito import get_gigachat_key
    if not access_token:
        access_token = get_gigachat_key()  # Автоматический запрос токена
        if not access_token:
            logger.error("Токен GigaChat не получен!")
            return "Ошибка: отсутствует токен GigaChat."
    """
    Отправляет историю и промпт (prompt1) в GigaChat API и возвращает ответ ассистента.

    :param history: список сообщений [{"role": "user"/"assistant", "content": "..."}]
    :param prompt1: системный промпт для консультанта (строка)
    :param access_token: ключ авторизации GigaChat
    :return: ответ ассистента (строка)
    """

    messages = [Messages(role=MessagesRole.SYSTEM, content=prompt1)]
    for msg in history:
        role = MessagesRole.USER if msg["role"] == "user" else MessagesRole.ASSISTANT
        messages.append(Messages(role=role, content=msg["content"]))

    chat_payload = Chat(messages=messages, temperature=0.7)

    try:
        async with GigaChat(credentials=access_token, verify_ssl_certs=False, model='GigaChat-2-Pro') as giga:
            response = giga.chat(chat_payload)
            logger.info(f"Полный ответ GigaChat: {response}")
            answer = response.choices[0].message.content
            logger.info(f"GigaChat ответ: {answer}")
            return answer
    except Exception as e:
        logger.error(f"Ошибка при вызове GigaChat API: {e}", exc_info=True)
        return "Извините, произошла ошибка при обработке запроса."