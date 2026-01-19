import xmlrpc.client
import time

def run_client():
    print("Connecting to Load Balancer at localhost:9000...")
    
    # Connect to the Load Balancer, NOT the worker directly
    lb = xmlrpc.client.ServerProxy("http://localhost:9000/")
    
    try:
        matrix_size = 400
        print(f"Requesting task execution (Matrix Size: {matrix_size})...")
        print("Waiting for response...")

        start_time = time.time()
        
        # The Load Balancer will determine who runs this
        result = lb.execute_task(matrix_size)
        
        total_time = time.time() - start_time

        print("Task Finished.")
        print(f"Result returned from Node: {result['node_id']}")
        print(f"Computation time: {result['duration_seconds']:.4f}s")
        print(f"Total round-trip time: {total_time:.4f}s")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Run the client multiple times to see if it picks different workers
    # (You can manually run this script repeatedly)
    run_client()