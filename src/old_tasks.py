import time
import sys # <--- New import

def execute_matrix_multiplication(n):
    print(f"⚙️  Starting Matrix Multiplication (Size: {n}x{n})...")
    
    # --- CHAOS MODE START ---
    # If the client asks for size 500, we simulate a crash after 2 seconds
    if n == 500:
        print("💥 SIMULATING FAILURE! This node is crashing in 2 seconds...")
        time.sleep(2)
        print("☠️  Node Died.")
        sys.exit(1) # Kill the process completely
    # --- CHAOS MODE END ---

    start_time = time.time()
    
    # ... (rest of your matrix code remains the same)
    matrix_a = [[i for i in range(n)] for _ in range(n)]
    matrix_b = [[j for j in range(n)] for _ in range(n)]
    result = [[0 for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] += matrix_a[i][k] * matrix_b[k][j]

    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Task Completed in {duration:.2f} seconds.")
    
    return {
        "status": "success",
        "matrix_size": n,
        "duration_seconds": duration,
        "node_id": "Worker_Node" 
    }