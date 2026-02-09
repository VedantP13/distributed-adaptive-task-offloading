import xmlrpc.client
import time
import base64
import os
import sys

# Default to localhost, but allow command line arg for IP
if len(sys.argv) > 1:
    LB_IP = sys.argv[1]
else:
    LB_IP = "127.0.0.1"

LOAD_BALANCER_URL = f"http://{LB_IP}:9000"
INPUT_FOLDER = "input_images"
OUTPUT_FOLDER = "output_images"

def run_image_client(filename="test.jpg", filter_type="BLUR"):
    input_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, f"processed_{filter_type}_{filename}")

    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return

    print(f"Connecting to Load Balancer at {LOAD_BALANCER_URL}...")
    lb = xmlrpc.client.ServerProxy(LOAD_BALANCER_URL)

    try:
        # 1. Read and Encode Image
        print(f"Reading {filename}...")
        with open(input_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        print(f"Sending image ({len(encoded_string)} bytes) for {filter_type}...")
        start_time = time.time()
        
        # 2. Send to Load Balancer
        result = lb.process_image(encoded_string, filter_type)
        
        # 3. Decode and Save Result
        if result.get("status") == "success":
            decoded_image = base64.b64decode(result['image_data'])
            
            with open(output_path, "wb") as output_file:
                output_file.write(decoded_image)
                
            total_time = time.time() - start_time
            print("\nSUCCESS! Task Finished.")
            print(f"Processed by Node: {result['node_id']}")
            print(f"Computation Time:  {result['duration_seconds']:.4f}s")
            print(f"Total Round Trip:  {total_time:.4f}s")
            print(f"Image saved to:    {output_path}")
        else:
            print("Task Failed:", result.get("message"))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure folders exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        
    run_image_client("test.jpg", "BLUR")