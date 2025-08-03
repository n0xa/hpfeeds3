#!/usr/bin/env python3

import socket
import time

def test_connection():
    """Test if broker is accepting connections on port 10000"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 10000))
        sock.close()
        
        if result == 0:
            print("✅ Broker is accepting connections on port 10000")
            return True
        else:
            print(f"❌ Connection failed with error code: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == '__main__':
    # First check if anything is listening on port 10000
    import subprocess
    try:
        netstat_result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if ':10000' in netstat_result.stdout:
            print("✅ Something is listening on port 10000")
        else:
            print("❌ Nothing listening on port 10000")
    except:
        pass
    
    test_connection()