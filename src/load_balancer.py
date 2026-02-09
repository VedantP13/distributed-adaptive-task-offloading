from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import threading
import time
import os
import concurrent.futures

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
    Attempts to offload the matrix task with retries.
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

def distribute_image_task(image_data, filter_type):
    """
    Finds the best worker and forwards the image processing task.
    """
    max_retries = 3
    attempts = 0

    while attempts < max_retries:
        target_worker_url = get_best_worker()

        if not target_worker_url:
            return {"error": "No workers available"}

        try:
            worker = xmlrpc.client.ServerProxy(target_worker_url)
            result = worker.process_image(image_data, filter_type)
            result['node_id'] = target_worker_url 
            return result
            
        except Exception:
            if target_worker_url in WORKER_NODES:
                WORKER_NODES.remove(target_worker_url)
            attempts += 1
    
    return {"error": "All attempts to complete the task failed."}


def distribute_crack_task(target_hash, start, end, length):
    """
    Splits the cracking job across ALL available workers.
    UPDATED: Now accepts 'length' to pass to workers for Base-36 decoding.
    """
    active_workers = list(WORKER_NODES) # Get snapshot of active workers
    
    if not active_workers:
        return {"error": "No workers available"}
    
    num_workers = len(active_workers)
    total_range = end - start
    step = total_range // num_workers # Divide range by number of workers
    
    futures = []
    # ThreadPool to send requests to all workers simultaneously
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i, worker_url in enumerate(active_workers):
            # Calculate sub-range for this worker
            range_start = start + (i * step)
            # The last worker takes whatever is left (to handle remainders)
            range_end = start + ((i + 1) * step) if i < num_workers - 1 else end
            
            # Submit task to worker (Asynchronous call)
            def call_worker(url, s, e, l):
                try:
                    rpc = xmlrpc.client.ServerProxy(url)
                    # Pass the new 'length' argument (l) to the worker
                    result = rpc.crack_password(target_hash, s, e, l)
                    
                    # Inject the Worker URL here so the client knows who won
                    if result.get("status") == "success":
                        result['node_id'] = url
                        
                    return result
                except:
                    return {"status": "failure"}

            futures.append(executor.submit(call_worker, worker_url, range_start, range_end, length))
            
        # Wait for results
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result.get("status") == "success":
                # If ANY worker finds it, we return success immediately!
                return result

    return {"status": "failure", "message": "Password not found in range"}


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

def get_cluster_status():
    """
    Returns a list of all workers with their current CPU/RAM usage.
    Used by the Web Dashboard for live graphing.
    """
    status_report = []
    
    # Iterate over a copy to avoid modification issues
    for url in WORKER_NODES[:]:
        try:
            worker = xmlrpc.client.ServerProxy(url)
            # We assume the worker has a get_health() function
            stats = worker.get_health() 
            status_report.append({
                "node": url,
                "cpu": stats['cpu'],
                "ram": stats['ram'],
                "status": "online"
            })
        except:
            status_report.append({
                "node": url,
                "cpu": 0,
                "ram": 0,
                "status": "offline"
            })
            
    return status_report


def start_load_balancer(port=9000):
    server = SimpleXMLRPCServer(("0.0.0.0", port), allow_none=True, logRequests=False)
    
    # Register functions
    server.register_function(distribute_task, "execute_task")
    server.register_function(register_worker, "register_worker")
    server.register_function(distribute_image_task, "process_image")
    server.register_function(distribute_crack_task, "crack_password")
    server.register_function(get_cluster_status, "get_cluster_status")

    # Start the dashboard in a separate thread
    dashboard_thread = threading.Thread(target=print_dashboard, daemon=True)
    dashboard_thread.start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLoad Balancer stopping...")

if __name__ == "__main__":
    start_load_balancer()