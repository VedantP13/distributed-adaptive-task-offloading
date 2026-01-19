from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import threading
import time
import os

# Start with an empty list
WORKER_NODES = []

def register_worker(worker_url):
    """
    Allows a worker to register itself with the load balancer.
    """
    if worker_url not in WORKER_NODES:
        WORKER_NODES.append(worker_url)
        return True
    return False

def get_best_worker():
    """
    Queries all registered workers and returns the one with the lowest CPU usage.
    """
    if not WORKER_NODES:
        return None

    best_worker_url = None
    lowest_cpu = 100.0

    # Iterate over a copy of the list
    for url in WORKER_NODES[:]: 
        try:
            worker = xmlrpc.client.ServerProxy(url)
            stats = worker.get_health()
            
            if stats['cpu'] < lowest_cpu:
                lowest_cpu = stats['cpu']
                best_worker_url = url
                
        except Exception:
            # If unreachable, remove from list
            if url in WORKER_NODES:
                WORKER_NODES.remove(url)

    return best_worker_url

def distribute_task(n):
    """
    Attempts to offload the task with retries.
    """
    max_retries = 3
    attempts = 0

    while attempts < max_retries:
        target_worker_url = get_best_worker()

        if not target_worker_url:
            return {"error": "No workers available"}

        try:
            worker = xmlrpc.client.ServerProxy(target_worker_url)
            result = worker.execute_task(n)
            result['node_id'] = target_worker_url 
            return result
            
        except Exception:
            if target_worker_url in WORKER_NODES:
                WORKER_NODES.remove(target_worker_url)
            attempts += 1
    
    return {"error": "All attempts to complete the task failed."}

def print_dashboard():
    """
    Background thread to print system status.
    """
    while True:
        # Clear screen (cls for Windows, clear for Unix)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("========================================")
        print("      DISTRIBUTED SYSTEM MONITOR        ")
        print("========================================")
        print(f"Active Workers: {len(WORKER_NODES)}")
        print("----------------------------------------")
        print(f"{'Worker URL':<25} | {'Status':<10}")
        print("----------------------------------------")
        
        if not WORKER_NODES:
            print("No workers connected.")
        
        for url in WORKER_NODES:
            print(f"{url:<25} | Online")
            
        print("----------------------------------------")
        print("Load Balancer running on port 9000...")
        print("Waiting for client tasks (Ctrl+C to stop)")
        
        # Refresh every 2 seconds
        time.sleep(2)

def start_load_balancer(port=9000):
    server = SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True, logRequests=False)
    
    # Register functions
    server.register_function(distribute_task, "execute_task")
    server.register_function(register_worker, "register_worker")
    
    # Start the dashboard in a separate thread
    dashboard_thread = threading.Thread(target=print_dashboard, daemon=True)
    dashboard_thread.start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLoad Balancer stopping...")

if __name__ == "__main__":
    start_load_balancer()