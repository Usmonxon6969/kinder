# Receive message for daily report
import json


async def daily_report(self, event):
    # Send daily report to WebSocket
    await self.send(text_data=json.dumps({
        'type': 'daily_report',
        'report': event['report']
    }))


from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import F
from django.utils import timezone


class InventoryConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time inventory updates
    """

    async def connect(self):
        # Join the inventory group
        await self.channel_layer.group_add(
            "inventory_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the inventory group
        await self.channel_layer.group_discard(
            "inventory_updates",
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        # Log the received message
        print(f"InventoryConsumer received message: {message_type}")

        # Handle different message types
        if message_type == 'get_low_ingredients':
            # Send low ingredients to the client
            low_ingredients = await self.get_low_ingredients()
            await self.send(text_data=json.dumps({
                'type': 'low_ingredients',
                'ingredients': low_ingredients
            }))
        elif message_type == 'inventory_update':
            # Handle simulated inventory update (for testing)
            await self.channel_layer.group_send(
                "inventory_updates",
                {
                    'type': 'inventory_update',
                    'ingredient_id': text_data_json.get('ingredient_id', 0),
                    'ingredient_name': text_data_json.get('ingredient_name', 'Test Ingredient'),
                    'current_quantity': text_data_json.get('current_quantity', 0),
                    'threshold_quantity': text_data_json.get('threshold_quantity', 0),
                    'is_below_threshold': text_data_json.get('is_below_threshold', False)
                }
            )
        elif message_type == 'test_message':
            # Handle test message (for testing WebSocket)
            await self.send(text_data=json.dumps({
                'type': 'test_response',
                'message': f"Received your test message: {text_data_json.get('content', 'No content')}",
                'timestamp': text_data_json.get('timestamp', str(timezone.now()))
            }))

    # Receive message from inventory group
    async def inventory_update(self, event):
        # Send inventory update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'inventory_update',
            'ingredient_id': event['ingredient_id'],
            'ingredient_name': event['ingredient_name'],
            'current_quantity': event['current_quantity'],
            'threshold_quantity': event['threshold_quantity'],
            'is_below_threshold': event['is_below_threshold']
        }))

    # Receive message for low ingredient alert
    async def low_ingredient_alert(self, event):
        # Send low ingredient alert to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'low_ingredient_alert',
            'ingredient_id': event['ingredient_id'],
            'ingredient_name': event['ingredient_name'],
            'current_quantity': event['current_quantity'],
            'threshold_quantity': event['threshold_quantity']
        }))

    @database_sync_to_async
    def get_low_ingredients(self):
        """Get ingredients that are below their threshold"""
        from ingredients.models import Ingredient

        low_ingredients = []
        for ingredient in Ingredient.objects.filter(current_quantity__lt=F('threshold_quantity')):
            low_ingredients.append({
                'id': ingredient.id,
                'name': ingredient.name,
                'current_quantity': ingredient.current_quantity,
                'threshold_quantity': ingredient.threshold_quantity,
                'percentage': round((ingredient.current_quantity / ingredient.threshold_quantity) * 100)
            })

        return low_ingredients


class MealServingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time meal serving updates
    """

    async def connect(self):
        # Join the meal serving group
        await self.channel_layer.group_add(
            "meal_servings",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the meal serving group
        await self.channel_layer.group_discard(
            "meal_servings",
            self.channel_name
        )

    # Receive message from meal serving group
    async def meal_served(self, event):
        # Send meal served update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'meal_served',
            'meal_id': event['meal_id'],
            'meal_name': event['meal_name'],
            'servings': event['servings'],
            'served_by': event['served_by'],
            'timestamp': event['timestamp']
        }))

    # Receive message for available portions update
    async def portions_update(self, event):
        # Send portions update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'portions_update',
            'meal_id': event['meal_id'],
            'meal_name': event['meal_name'],
            'max_portions': event['max_portions']
        }))