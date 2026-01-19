import sys
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client # <--- Need this to talk to LB
import monitor
import tasks
import socket

LOAD_BALANCER_URL = "http://127.0.0.1:9000"

def register_with_load_balancer(worker_port):
    """
    Tells the Load Balancer that this worker is active.
    """
    try:
        # Use 127.0.0.1 explicitly
        my_url = f"http://127.0.0.1:{worker_port}"
        
        lb = xmlrpc.client.ServerProxy(LOAD_BALANCER_URL)
        lb.register_worker(my_url)
        print(f"✅ Successfully registered with Load Balancer at {LOAD_BALANCER_URL}")
        
    except ConnectionRefusedError:
        print(f"⚠️ Could not register: Load Balancer at {LOAD_BALANCER_URL} is offline.")

def start_worker(port):
    # 1. Register first
    register_with_load_balancer(port)

    # 2. Then start server
    server = SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True)
    print(f"🚀 Worker running on port {port}...")

    server.register_function(monitor.get_system_stats, "get_health")
    server.register_function(tasks.execute_matrix_multiplication, "execute_task")

    print("✅ Waiting for instructions...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Worker stopping...")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8000
    
    start_worker(port)