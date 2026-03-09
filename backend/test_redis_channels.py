#!/usr/bin/env python
"""
Quick test script to verify Redis channel layer is working.
"""
import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bicare360.settings.dev')
django.setup()

from channels.layers import get_channel_layer

async def test_redis_channel_layer():
    """Test Redis channel layer send/receive"""
    channel_layer = get_channel_layer()
    
    print("Testing Redis Channel Layer...")
    print(f"Backend: {channel_layer.__class__.__name__}")
    
    # Test sending and receiving a message
    test_channel = "test_channel"
    test_message = {
        "type": "test.message",
        "text": "Hello from Redis!",
    }
    
    # Send message
    await channel_layer.send(test_channel, test_message)
    print(f"✓ Sent message to {test_channel}")
    
    # Receive message  
    received = await channel_layer.receive(test_channel)
    print(f"✓ Received message: {received}")
    
    if received == test_message:
        print("\n✅ Redis Channel Layer is working perfectly!")
        return True
    else:
        print("\n❌ Message mismatch!")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_redis_channel_layer())
    exit(0 if result else 1)
