#!/usr/bin/env python3

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

async def test_external_connection(host, port, ident, secret, channels):
    """Test connecting to external hpfeeds server"""
    try:
        from hpfeeds.asyncio import ClientSession
        
        log.info(f"Connecting to external server: {host}:{port}")
        log.info(f"Using ident: {ident}")
        log.info(f"Subscribing to channels: {', '.join(channels)}")
        
        async with ClientSession(host, port, ident, secret) as client:
            log.info("✅ Connected successfully to external server!")
            
            # Subscribe to channels
            for channel in channels:
                client.subscribe(channel)
                log.info(f"✅ Subscribed to channel: {channel}")
            
            # Listen for messages for a short time
            message_count = 0
            start_time = datetime.now()
            
            log.info("Listening for messages for 10 seconds...")
            
            async for identifier, channel, payload in client:
                message_count += 1
                log.info(f"📨 Message #{message_count}: {channel} from {identifier} ({len(payload)} bytes)")
                
                # Show first few messages in detail
                if message_count <= 3:
                    try:
                        payload_preview = payload[:100].decode('utf-8', errors='replace')
                        log.info(f"   Preview: {payload_preview}...")
                    except:
                        log.info(f"   Binary payload: {payload[:50].hex()}...")
                
                # Test for 10 seconds or 10 messages max
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > 10 or message_count >= 10:
                    break
            
            log.info(f"✅ Received {message_count} messages in {elapsed:.1f} seconds")
            return True
            
    except Exception as e:
        log.error(f"❌ External connection failed: {e}")
        return False

async def test_local_broker():
    """Test our local broker can start and accept connections"""
    try:
        from hpfeeds.broker.auth.sqlite import Authenticator
        from hpfeeds.broker.server import Server
        
        log.info("Testing local broker startup...")
        
        # Use our SQLite auth
        auth = Authenticator('sqlite.db')
        
        # Create server
        server = Server(
            auth=auth,
            bind='127.0.0.1:10001',  # Use different port to avoid conflicts
            exporter=None  # No metrics for testing
        )
        
        # Start server in background
        server_task = asyncio.create_task(server.serve_forever())
        
        # Wait a moment for startup
        await asyncio.sleep(1)
        
        log.info("✅ Local broker started successfully")
        
        # Test connection to our broker
        from hpfeeds.asyncio import ClientSession
        
        async with ClientSession('127.0.0.1', 10001, 'test', 'secret') as client:
            log.info("✅ Connected to local broker!")
            
            # Publish a test message
            client.publish('test.channel', b'Hello from test!')
            log.info("✅ Published test message")
            
            # Subscribe and try to receive
            client.subscribe('test.channel')
            log.info("✅ Subscribed to test channel")
        
        # Clean shutdown
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        
        return True
        
    except Exception as e:
        log.error(f"❌ Local broker test failed: {e}")
        return False

def main():
    if len(sys.argv) < 5:
        print("Usage: python bridge_test.py <host> <port> <ident> <secret> [channel1,channel2,...]")
        print("Example: python bridge_test.py hpfeeds.honeycloud.net 20000 myident mysecret dionaea.capture,cowrie.sessions")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    ident = sys.argv[3]
    secret = sys.argv[4]
    channels = sys.argv[5].split(',') if len(sys.argv) > 5 else ['dionaea.capture']
    
    async def run_tests():
        log.info("=== hpfeeds3 External Server Test ===")
        
        # Test 1: Connect to external server
        external_ok = await test_external_connection(host, port, ident, secret, channels)
        
        # Test 2: Test our local broker
        local_ok = await test_local_broker()
        
        log.info("=== Test Results ===")
        log.info(f"External server connection: {'✅ PASS' if external_ok else '❌ FAIL'}")
        log.info(f"Local broker functionality: {'✅ PASS' if local_ok else '❌ FAIL'}")
        
        if external_ok and local_ok:
            log.info("🎉 All tests passed! hpfeeds3 is working correctly!")
            return True
        else:
            log.error("❌ Some tests failed")
            return False
    
    return asyncio.run(run_tests())

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)