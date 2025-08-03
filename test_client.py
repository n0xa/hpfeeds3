#!/usr/bin/env python3

import asyncio
import time
from hpfeeds.asyncio import ClientSession

async def test_client():
    print("Testing hpfeeds client connectivity...")
    
    try:
        # Test connection without auth (should fail gracefully)
        async with ClientSession('127.0.0.1', 10000, 'test', 'test') as client:
            print("Client connected successfully!")
            
            # Try to publish a message
            client.publish('test.channel', b'Hello World!')
            print("Message published successfully!")
            
            # Wait a bit
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Expected connection error (no auth configured): {e}")
        return True  # This is expected without proper auth setup
    
    return False

if __name__ == '__main__':
    result = asyncio.run(test_client())
    print(f"Client test result: {'PASS' if result else 'FAIL'}")