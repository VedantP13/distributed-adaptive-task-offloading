import sys
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import tasks
import socket
import psutil
import os
import platform  # Needed for OS detection

# --- 1. SETUP PROCESS MONITORING ---
# Get the specific process ID of THIS worker script
CURRENT_PROCESS = psutil.Process(os.getpid())
# Call it once to initialize the counter
CURRENT_PROCESS.cpu_percent()

# --- 2. GATHER STATIC SYSTEM INFO ---
# These are fetched once at startup to send to the dashboard
HOSTNAME = socket.gethostname()
# Example: "Windows 10" or "Linux 5.15..."
OS_NAME = f"{platform.system()} {platform.release()}"
# Example: "AMD64" or "x86_64"
ARCH = platform.machine()

def get_health():
    """
    Returns dynamic health stats + static device info.
    The dashboard uses this to display the 'Server Blades' at the bottom.
    """
    try:
        # Calculate CPU usage for THIS specific script
        cpu_usage = CURRENT_PROCESS.cpu_percent(interval=None) / psutil.cpu_count()
        
        # Scale up slightly for demo visibility (optional, can remove *10 for strict accuracy)
        display_cpu = min(round(cpu_usage * 10, 1), 100.0)
        
        return {
            "cpu": display_cpu,
            "ram": psutil.virtual_memory().percent,
            # NEW: Identity Info for the Dashboard Footer
            "hostname": HOSTNAME,
            "os": OS_NAME,
            "arch": ARCH
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
        
        # If testing on localhost, force 127.0.0.1
        if lb_ip == "127.0.0.1":
            my_ip = "127.0.0.1"
            
        my_url = f"http://{my_ip}:{worker_port}"
        
        print(f"🔗 Attempting to register {my_url} ({HOSTNAME}) with LB at {lb_url}...")
        
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
    server = SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True, logRequests=False)
    print(f"🚀 Worker running on {HOSTNAME} ({OS_NAME}) : {port}...")
    
    # --- REGISTER FUNCTIONS ---
    
    # Register Health Check (Now includes Hostname/OS)
    server.register_function(get_health, "get_health")
    
    # Register Tasks
    server.register_function(tasks.execute_matrix_multiplication, "execute_task")
    server.register_function(tasks.apply_image_filter, "process_image")
    server.register_function(tasks.crack_password_range, "crack_password")

    print("✅ Waiting for instructions...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Worker stopping...")

if __name__ == "__main__":
    start_worker(PORT, LB_IP)