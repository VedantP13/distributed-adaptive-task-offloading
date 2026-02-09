import sys
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import monitor # Keep this import if you still use it elsewhere, otherwise it's optional now
import tasks  
import socket
import psutil
import os

# --- 1. SETUP PROCESS MONITORING ---
# Get the specific process ID of THIS worker script
CURRENT_PROCESS = psutil.Process(os.getpid())
# Call it once to initialize the counter (first call always returns 0.0)
CURRENT_PROCESS.cpu_percent()

def get_health():
    """
    Returns the CPU usage of THIS SPECIFIC WORKER SCRIPT only.
    This fixes the graph issue where all localhost workers showed the same line.
    """
    try:
        # interval=None is non-blocking (returns usage since last call)
        # / psutil.cpu_count() normalizes it so 100% = 1 full core usage
        cpu_usage = CURRENT_PROCESS.cpu_percent(interval=None) / psutil.cpu_count()
        
        # Ensure we don't return crazy high numbers, cap visual at 100%
        display_cpu = min(round(cpu_usage * 10, 1), 100.0) 
        # Note: multiplied by 10 to make the graph more visible for small tasks, 
        # or remove *10 for strict accuracy. For demos, scaling up small usage looks better.
        
        return {
            "cpu": display_cpu,
            "ram": psutil.virtual_memory().percent
        }
    except:
        return {"cpu": 0, "ram": 0}

# Allow command line argument for port and LB IP
if len(sys.argv) > 1:
    PORT = int(sys.argv[1])
else:
    PORT = 8000

if len(sys.argv) > 2:
    LB_IP = sys.argv[2]
else:
    LB_IP = "127.0.0.1"

def register_with_load_balancer(worker_port, lb_ip):
    """
    Registers this worker with the Load Balancer at the specific IP.
    """
    lb_url = f"http://{lb_ip}:9000"
    
    try:
        # Get local IP
        hostname = socket.gethostname()
        my_ip = socket.gethostbyname(hostname)
        
        # If testing on localhost, force 127.0.0.1, otherwise use LAN IP
        if lb_ip == "127.0.0.1":
            my_ip = "127.0.0.1"
            
        my_url = f"http://{my_ip}:{worker_port}"
        
        print(f"🔗 Attempting to register {my_url} with LB at {lb_url}...")
        
        lb = xmlrpc.client.ServerProxy(lb_url)
        lb.register_worker(my_url)
        print(f"✅ Successfully registered!")
        
    except Exception as e:
        print(f"⚠️ Could not register: {e}")
        print("   (Is the Load Balancer running?)")

def start_worker(port, lb_ip):
    # 1. Register
    register_with_load_balancer(port, lb_ip)

    # 2. Start Server
    # 0.0.0.0 allows connections from external laptops
    server = SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True, logRequests=False)
    print(f"🚀 Worker running on port {port}...")
    
    # --- REGISTER FUNCTIONS ---
    
    # NEW: Register the process-specific health check
    server.register_function(get_health, "get_health")
    
    # Register Matrix Task (Old)
    server.register_function(tasks.execute_matrix_multiplication, "execute_task")
    
    # Register Image Task 
    server.register_function(tasks.apply_image_filter, "process_image")
    
    # Register Password Cracker
    server.register_function(tasks.crack_password_range, "crack_password")

    print("✅ Waiting for instructions...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Worker stopping...")

if __name__ == "__main__":
    start_worker(PORT, LB_IP)