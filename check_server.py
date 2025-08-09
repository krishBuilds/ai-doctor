import subprocess
import time
import requests
import sys

def start_server_and_test():
    print("Starting Django server...")
    
    # Start Django server in background
    server_process = subprocess.Popen([
        sys.executable, 'manage.py', 'runserver', '127.0.0.1:8000'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment for server to start
    time.sleep(3)
    
    try:
        # Test if server is responding
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"[SUCCESS] Server is running! Status: {response.status_code}")
        print(f"Response length: {len(response.text)} characters")
        print("\nServer accessible at: http://127.0.0.1:8000/")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Server not accessible: {e}")
        return False
    finally:
        # Stop the server
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    success = start_server_and_test()
    sys.exit(0 if success else 1)