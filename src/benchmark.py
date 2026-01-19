import time
import xmlrpc.client
import tasks

# Connect to the Load Balancer
LOAD_BALANCER_URL = "http://127.0.0.1:9000"

def run_benchmark():
    print("--------------------------------------------------")
    print("      PERFORMANCE BENCHMARK: LOCAL vs REMOTE      ")
    print("--------------------------------------------------")
    print(f"{'Matrix Size':<15} | {'Local Time (s)':<15} | {'Remote Time (s)':<15}")
    print("--------------------------------------------------")

    # We will test different matrix sizes to see where offloading becomes useful
    # Small tasks might be slower remotely due to network overhead
    test_sizes = [100, 200, 300, 400]

    for size in test_sizes:
        # 1. Measure Local Execution Time
        start_local = time.time()
        # We call the logic directly from the tasks module
        tasks.execute_matrix_multiplication(size)
        end_local = time.time()
        local_duration = end_local - start_local

        # 2. Measure Remote Execution Time
        start_remote = time.time()
        try:
            lb = xmlrpc.client.ServerProxy(LOAD_BALANCER_URL)
            # The load balancer returns a dictionary with 'duration_seconds'
            # But we want to measure the TOTAL time including network transfer
            lb.execute_task(size)
        except Exception as e:
            print(f"Error during remote execution: {e}")
            return
        
        end_remote = time.time()
        remote_duration = end_remote - start_remote

        # 3. Print Results
        print(f"{size:<15} | {local_duration:<15.4f} | {remote_duration:<15.4f}")

    print("--------------------------------------------------")
    print("Benchmark Complete.")

if __name__ == "__main__":
    run_benchmark()