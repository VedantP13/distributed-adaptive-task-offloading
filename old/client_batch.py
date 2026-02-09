import xmlrpc.client
import time
import base64
import os
import sys
import concurrent.futures

# Default configuration
INPUT_FOLDER = "input_images"
OUTPUT_FOLDER = "output_images"

if len(sys.argv) > 1:
    LB_IP = sys.argv[1]
else:
    LB_IP = "127.0.0.1"
    
LOAD_BALANCER_URL = f"http://{LB_IP}:9000"

def process_single_image(filename):
    """
    Function to be run in a separate thread for each image.
    """
    input_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"processed_BATCH_{filename}")
    
    try:
        # Connect to LB (Each thread needs its own connection object)
        lb = xmlrpc.client.ServerProxy(LOAD_BALANCER_URL)
        
        # Read and Encode
        with open(input_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        print(f"➡️ Sending {filename}...")
        
        # Send Request (Filter: BLUR)
        start_time = time.time()
        result = lb.process_image(encoded_string, "BLUR")
        end_time = time.time()
        
        if result.get("status") == "success":
            # Decode and Save
            decoded_image = base64.b64decode(result['image_data'])
            with open(output_path, "wb") as output_file:
                output_file.write(decoded_image)
            return f"✅ {filename} done by {result['node_id']} in {end_time - start_time:.2f}s"
        else:
            return f"❌ {filename} Failed: {result.get('message')}"

    except Exception as e:
        return f"❌ {filename} Error: {str(e)}"

def run_batch_client():
    # 1. Get list of files
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    if not files:
        print("No images found in input_images/")
        return

    print(f"🚀 Starting Batch Processing of {len(files)} images...")
    print(f"Connecting to Load Balancer at {LOAD_BALANCER_URL}")
    
    global_start = time.time()

    # 2. Use ThreadPool to send requests in parallel
    # This simulates a non-blocking client that blasts tasks to the grid
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_single_image, files))

    global_end = time.time()
    total_duration = global_end - global_start

    # 3. Print Report
    print("\n" + "="*40)
    print("       BATCH PROCESSING REPORT       ")
    print("="*40)
    for res in results:
        print(res)
    print("-" * 40)
    print(f"Total Time: {total_duration:.2f} seconds")
    print(f"Average Time per Image: {total_duration / len(files):.2f} seconds")
    print("="*40)

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    run_batch_client()
    