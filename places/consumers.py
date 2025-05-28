import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class UpdateConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from .models import Post, LikeDislike
        await self.channel_layer.group_add("updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("updates", self.channel_name)

    async def send_update(self, event):
        # event["message"] должен быть сериализуемым в JSON
        await self.send(text_data=json.dumps(event["message"]))


class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("WebSocket connected")
        await self.channel_layer.group_add('posts', self.channel_name)
        await self.accept()
        self.ping_task = asyncio.create_task(self.send_ping())

    async def disconnect(self, close_code):
        logger.info("WebSocket disconnected")
        if hasattr(self, 'ping_task'):
            self.ping_task.cancel()
        await self.channel_layer.group_discard('posts', self.channel_name)

    async def send_ping(self):
        while True:
            await asyncio.sleep(30)
            await self.send(text_data=json.dumps({'action': 'ping'}))
            logger.info("Sent ping")

    async def like_dislike_update(self, event):
        logger.info(f"Sending like/dislike update to client: {event}")
        await self.send(text_data=json.dumps({
            'action': 'like_dislike_update',
            'update': event['update']
        }))
