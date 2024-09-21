from typing import List, Union, Dict
from aiogram import Bot, types
from utils.log import logger

tracked_messages: List[Dict[str, Union[int, bool]]] = []

class MessageManager:
    @staticmethod
    async def add_message(message: types.Message, is_outgoing: bool = True):
        tracked_messages.append({
            "id": message.message_id, 
            "chat_id": message.chat.id, 
            "is_outgoing": is_outgoing
        })

    @staticmethod
    async def clear_messages(bot: Bot):
        
        for msg in tracked_messages:
            try:
                await bot.delete_message(chat_id=msg["chat_id"], message_id=msg["id"])
            except Exception as e:
                logger.error(f"Error deleting message {msg['id']}: {str(e)}")

        tracked_messages.clear()