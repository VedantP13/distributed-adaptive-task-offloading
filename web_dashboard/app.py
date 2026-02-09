from flask import Flask, render_template, request, jsonify
import xmlrpc.client
import os
import base64
import hashlib
import time
import datetime
import socket

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)
os.makedirs(os.path.join(app.root_path, RESULT_FOLDER), exist_ok=True)

# Load Balancer URL
# Ensure this matches the IP where load_balancer.py is running
LB_HOST = "127.0.0.1" 
LB_PORT = 9000
LB_URL = f"http://{LB_HOST}:{LB_PORT}"

# Global Log Buffer
SYSTEM_LOGS = []

def log_message(message, level="INFO"):
    """
    Adds a log to the global buffer and prints it to the console.
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "time": timestamp,
        "level": level,
        "message": message
    }
    print(f"[{timestamp}] [{level}] {message}") # Keep printing to VS Code
    SYSTEM_LOGS.append(log_entry)
    # Keep only last 100 logs
    if len(SYSTEM_LOGS) > 100:
        SYSTEM_LOGS.pop(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_logs')
def get_logs():
    return jsonify(SYSTEM_LOGS)

@app.route('/system_status')
def system_status():
    """
    Checks if the Load Balancer is actually reachable.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((LB_HOST, LB_PORT))
        if result == 0:
            return jsonify({"status": "online"})
        else:
            return jsonify({"status": "offline"})
    except:
        return jsonify({"status": "offline"})
    finally:
        sock.close()

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400

    log_message(f"📂 Client uploaded file: {file.filename}", "INFO")

    try:
        # Save locally first
        filepath = os.path.join(app.root_path, UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Encode to Base64
        with open(filepath, "rb") as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')

        log_message(f"🚀 Offloading task to Load Balancer at {LB_URL}...", "NETWORK")
        lb = xmlrpc.client.ServerProxy(LB_URL)
        
        start = time.time()
        # This call blocks until the worker returns
        result = lb.process_image(img_data, "BLUR") 
        duration = time.time() - start

        if result.get("status") == "success":
            out_filename = f"processed_{file.filename}"
            out_path = os.path.join(app.root_path, RESULT_FOLDER, out_filename)
            
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(result['image_data']))
            
            node_id = result.get('node_id', 'Unknown Worker')
            log_message(f"✅ Task Completed by {node_id}", "SUCCESS")
            log_message(f"⏱️ Duration: {duration:.2f}s", "INFO")
            
            return jsonify({
                "status": "success",
                "original_url": f"/static/uploads/{file.filename}",
                "processed_url": f"/static/results/{out_filename}",
                "node": node_id,
                "time": f"{duration:.2f}s"
            })
        else:
            error_msg = result.get('message', 'Unknown error')
            log_message(f"❌ Worker Error: {error_msg}", "ERROR")
            return jsonify({"status": "error", "message": error_msg})

    except Exception as e:
        log_message(f"🔥 Critical System Error: {str(e)}", "CRITICAL")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/crack_password', methods=['POST'])
def crack_password():
    password_input = request.form.get('pin') # Can now be alphanumeric
    
    if not password_input:
        log_message("⚠️ Empty input received", "WARNING")
        return jsonify({"status": "error", "message": "Invalid Input"}), 400

    # 1. Determine Difficulty
    length = len(password_input)
    # 36 chars (a-z, 0-9)
    charset_size = 36 
    # Calculate total combinations: 36^Length
    total_combinations = charset_size ** length

    # Safety Limit for Demo (Don't let them crash it with long passwords)
    if length > 5:
        log_message("⚠️ Password too long for live demo (Max 5 chars)", "WARNING")
        return jsonify({"status": "error", "message": "Demo Limit: Max 5 characters"}), 400

    target_hash = hashlib.md5(password_input.encode()).hexdigest()
    
    log_message(f"🔐 Cracking '{password_input}' (Len: {length})", "INFO")
    log_message(f"📊 Search Space: {total_combinations:,} combinations", "INFO")
    
    try:
        lb = xmlrpc.client.ServerProxy(LB_URL)
        
        log_message("📡 Broadcasting search job to worker grid...", "NETWORK")
        start = time.time()
        
        # Send Total Range (0 to 36^N) AND Length to LB
        result = lb.crack_password(target_hash, 0, total_combinations, length)
        duration = time.time() - start

        if result.get("status") == "success":
            node_id = result.get('node_id', 'Unknown Worker')
            log_message(f"🎉 FOUND: {result['password']}", "SUCCESS")
            log_message(f"🤖 Cracked by: {node_id}", "SUCCESS")
            
            return jsonify({
                "status": "success",
                "pin": result['password'],
                "node": node_id,
                "time": f"{duration:.2f}s"
            })
        else:
            log_message("❌ Search exhaustion. Password not found.", "ERROR")
            return jsonify({"status": "error", "message": "Password not found"})

    except Exception as e:
        log_message(f"🔥 Connection Failed: {str(e)}", "CRITICAL")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/grid_telemetry')
def grid_telemetry():
    """
    Fetches real-time CPU stats from the Load Balancer for the dashboard graph.
    """
    try:
        lb = xmlrpc.client.ServerProxy(LB_URL)
        # Call the new function we added to LB
        data = lb.get_cluster_status()
        return jsonify(data)
    except:
        return jsonify([])

if __name__ == '__main__':
    # Initial log to show it's alive
    log_message("Web Interface initialized. Listening on port 5000...", "SYSTEM")
    app.run(debug=True, port=5000)