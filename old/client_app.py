import xmlrpc.client
import os
import sys
import time
import base64
import hashlib

# Configuration
INPUT_FOLDER = "input_images"
OUTPUT_FOLDER = "output_images"

# Connect to Load Balancer
if len(sys.argv) > 1:
    LB_IP = sys.argv[1]
else:
    LB_IP = "127.0.0.1"

LB_URL = f"http://{LB_IP}:9000"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    clear_screen()
    print("==========================================")
    print("   DISTRIBUTED COMPUTING CLIENT DASHBOARD ")
    print(f"   Connected to: {LB_URL}")
    print("==========================================")
    print("1. 🖼️  Distributed Image Blur")
    print("2. 🔐 Distributed Password Crack")
    print("3. 🔢 Matrix Multiplication Benchmark")
    print("4. ❌ Exit")
    print("==========================================")
    return input("Select an option (1-4): ")

# --- Feature 1: Image Processing ---
def feature_image_blur():
    print("\n--- Image Processing Mode ---")
    filename = input("Enter filename (e.g., test.jpg): ")
    path = os.path.join(INPUT_FOLDER, filename)
    
    if not os.path.exists(path):
        print("File not found!")
        input("Press Enter to return...")
        return

    try:
        lb = xmlrpc.client.ServerProxy(LB_URL)
        with open(path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        print("Sending to grid...")
        start = time.time()
        result = lb.process_image(img_data, "BLUR")
        duration = time.time() - start
        
        if result.get("status") == "success":
            out_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(result['image_data']))
            print(f"✅ Done! Saved to {out_path}")
            print(f"   Processed by: {result['node_id']}")
            print(f"   Time: {duration:.2f}s")
        else:
            print("❌ Failed.")
            
    except Exception as e:
        print(f"Error: {e}")
    input("Press Enter to return...")

# --- Feature 2: Password Cracking ---
def feature_password_crack():
    print("\n--- Distributed Password Cracker ---")
    print("Simulating a 5-digit PIN crack (00000-99999).")
    pin = input("Enter a numeric PIN to hide (e.g., 54321): ")
    
    if not pin.isdigit():
        print("Please enter digits only.")
        return

    # 1. Generate the 'Secret' Hash locally
    target_hash = hashlib.md5(pin.encode()).hexdigest()
    print(f"🔒 Target MD5 Hash: {target_hash}")
    print("🚀 Distributing search space to workers...")
    
    # We split the search space:
    # Range 0 to 100,000
    # Ideally, we'd split this dynamically, but for now let's just send
    # the whole range to the Load Balancer, or split it manually.
    
    try:
        lb = xmlrpc.client.ServerProxy(LB_URL)
        start = time.time()
        
        # We ask the LB to find a worker for the full range 0-100000
        # In a generic system, the LB would split this up.
        # Here, the chosen worker will loop through it.
        result = lb.crack_password(target_hash, 0, 100000)
        
        duration = time.time() - start
        
        if result.get("status") == "success":
            print(f"\n🔓 PASSWORD CRACKED: {result['password']}")
            print(f"   Cracked by: {result['node_id']}")
            print(f"   Time taken: {duration:.2f}s")
        else:
            print("\n❌ Password not found in range.")
            
    except Exception as e:
        print(f"Error: {e}")
    input("Press Enter to return...")

def main():
    while True:
        choice = show_menu()
        if choice == '1':
            feature_image_blur()
        elif choice == '2':
            feature_password_crack()
        elif choice == '3':
            # You can link your benchmark function here if you want
            print("Running benchmark...")
            # (Optional: import benchmark and run it)
            input("Press Enter...")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid selection.")
            time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    main()