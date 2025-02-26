# # consumers.py
#first version
from channels.generic.websocket import AsyncWebsocketConsumer
# consumers.py
from .models import Message
# from django.contrib.auth.models import User
from channels.db import database_sync_to_async 
from django.db.models import Q
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Connected
from user_managemanet.models import CustomUser  #changer user avec 
# from django.contrib.auth.models import User 

from channels.db import database_sync_to_async
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver = self.scope['url_route']['kwargs']['receiver'] 
        self.sender = self.scope['url_route']['kwargs']['sender']
        
    
        self.group_name = f'chat_{self.sender}_{self.receiver}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        previous_messages = await self.get_previous_messages()
        await self.send(text_data=json.dumps({
            'type': 'previous_messages',
            'messages': previous_messages
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        senderj = data.get('senderj')
        reciever = data.get('reciever')
        authuser = data.get('authuser')

        # Create and save a new message
        messages = Message(
            sender=await database_sync_to_async(CustomUser.objects.get)(id=senderj),
            receiver=await database_sync_to_async(CustomUser.objects.get)(id=reciever),
            content=message
        )
        await database_sync_to_async(messages.save)()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'senderj': senderj,
                'reciever': reciever,
                'authuser': authuser
            }
        )

    async def chat_message(self, event):
        message = event['message']
        senderj = event['senderj']
        authuser = event['authuser']
        reciever = event['reciever']
        await self.send(text_data=json.dumps({
            'message': message,
            'senderj': senderj,
            'authuser': authuser,
            'reciever': reciever
        }))

    async def get_previous_messages(self):

        messages = await database_sync_to_async(list)(
            Message.objects.filter(
                (Q(sender=self.sender) & Q(receiver=self.receiver)) | 
                (Q(sender=self.receiver) & Q(receiver=self.sender))
            ).order_by('timestamp') 
        )

        return await database_sync_to_async(lambda: [
            {
                'message': msg.content,
                'senderj': msg.sender.id,
                'reciever': msg.receiver.id,
                'authuser': msg.sender.username 
            }
            for msg in messages
        ])()





# class SecondConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.group_name = 'connected'
#         self.sender = None
#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()
#         print("WebSocket connection accepted")

#     async def disconnect(self, close_code):
#         if self.sender:
#             await self.channel_layer.group_send(self.group_name, {
#                 'type': 'chat_message',
#                 'sender': self.sender,
#                 'status': 'disconnected',
#             })
#         print(f"WebSocket connection closed with code: {close_code}")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         self.sender = data.get('sender')
#         status = data.get('status')

#         print(f"Received: {self.sender}, Status: {status}")  # Use self.sender
#         employee = Employee(name=name, position=position, salary=salary);
#         await database_sync_to_async(employee.save)();
#         await self.channel_layer.group_send(self.group_name, {
#             'type': 'chat_message',
#             'sender': self.sender,  # Use self.sender
#             'status': status,
#         })

#     async def chat_message(self, event):
#         sender = event['sender']
#         status = event['status']
#         await self.send(text_data=json.dumps({
#             'sender': sender,
#             'status': status,
#         }))



# class SecondConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.group_name = 'connected'
#         sender = data.get('sender')
#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()
#         print("WebSocket connection accepted")

#     async def disconnect(self, close_code):
#         if self.sender:
#             await self.channel_layer.group_send(self.group_name, {
#                 'type': 'chat_message',  # Specify the type to handle in chat_message
#                 'sender': self.sender,
#                 'status': 'disconnected',
#             })
#         print(f"WebSocket connection closed with code: {close_code}")
        

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         sender = data.get('sender')
#         status = data.get('status')

#         print(f"Received: {sender}, Status: {status}")

#         await self.channel_layer.group_send(self.group_name, {
#             'type': 'chat_message',
#             'sender': sender,
#             'status': status,
#         })

#     async def chat_message(self, event):
#         sender = event['sender']
#         status = event['status']
#         await self.send(text_data=json.dumps({
#             'sender': sender,
#             'status': status,
#         }))

class SecondConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'connected'
        self.sender = None
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print("WebSocket connection accepted")

    async def disconnect(self, close_code):
        if self.sender:
            await self.remove_connected_user(self.sender)
            connected_users = await self.get_connected_users()
            await self.channel_layer.group_send(self.group_name, {
                'type': 'chat_message',
                'sender': self.sender,
                'status': 'disconnected',
                'connected_users': connected_users
            })
        print(f"WebSocket connection closed with code: {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        self.sender = data.get('sender')
        status = data.get('status')

        print(f"Received: {self.sender}, Status: {status}")

        connected = Connected(
            connected=await database_sync_to_async(CustomUser.objects.get)(id=self.sender),
        )
        
        await database_sync_to_async(connected.save)()
        connected_users = await self.get_connected_users()
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat_message',
            'sender': self.sender,
            'status': status,
            'connected_users': connected_users 
        })

    async def chat_message(self, event):
        sender = event['sender']
        status = event['status']
        connected_users = event.get('connected_users', [])

        await self.send(text_data=json.dumps({
            'sender': sender,
            'status': status,
            'connected_users': connected_users
        }))

    async def get_connected_users(self):
        connected_users = await database_sync_to_async(list)(
            Connected.objects.all().select_related('connected').order_by('timestamp')
        )

        return await database_sync_to_async(lambda: [
            {
                'user_id': conn.connected.id,
                'username': conn.connected.username,
                'timestamp': conn.timestamp.isoformat()
            }
            for conn in connected_users
        ])()
    async def remove_connected_user(self, user_id):
        # Fetch the last connected user by sorting in descending order by the timestamp
        last_connected = await database_sync_to_async(
            lambda: Connected.objects.filter(connected_id=user_id).order_by('-timestamp').first()
        )()

        if last_connected:
            # Delete the last connected user for this user_id
            await database_sync_to_async(last_connected.delete)()














class ChatNotification(AsyncWebsocketConsumer):
    async def connect(self):
        print("chatnotificationhh");
        self.receiver = self.scope['url_route']['kwargs']['receiver']
        self.group_name = f'chat_{self.receiver}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = data.get('sender')
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'sender': sender
            }
        )

    async def chat_message(self, event):
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'sender': sender,
        }))