import asyncio
import logging

import avito

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(avito.start_avito_webhook(avito.handle_webhook_message))
