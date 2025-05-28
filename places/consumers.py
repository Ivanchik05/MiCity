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
        await self.channel_layer.group_add('posts', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('posts', self.channel_name)

    async def like_dislike_update(self, event):
        await self.send(text_data=json.dumps({
            'action': 'like_dislike_update',
            'update': event['update']
        }))