# Distributed Compute Grid & Engineering Dashboard

A robust distributed computing framework that offloads computationally intensive tasks—such as batch image processing and cryptographic brute-forcing—to a dynamic grid of worker nodes. It features a real-time "Engineering Dashboard" with live CPU telemetry, centralized logging, and visual task management.

## Key Features

### Centralized Web Dashboard

* **Dark Mode UI:** Professional, high-contrast interface designed for monitoring grid performance.
* **Live Telemetry:** Real-time CPU usage graphs for every connected worker node using Chart.js.
* **Integrated Terminal:** A draggable, collapsible system log window streaming events directly from the backend.

### Distributed Task Execution

* **Batch Image Processing:**
  * Upload multiple images simultaneously.
  * The Load Balancer intelligently distributes them across available workers.
  * Results stream in real-time as workers complete tasks (Blur, Grayscale, etc.).

* **Distributed Password Cracking:**
  * Splits the search space for Alphanumeric passwords (Base-36) across the grid.
  * Supports distributed brute-forcing for passwords of varying lengths.
  * Returns success instantly once any node finds the match.

### System Architecture

* **Smart Load Balancing:** Dynamically routes tasks based on node availability and CPU health.
* **Process Isolation:** Workers measure their specific process CPU usage, allowing for accurate monitoring even when running multiple workers on a single host.
* **Scalability:** Supports adding new worker nodes dynamically without restarting the system.

## Tech Stack

* **Backend:** Python 3.x, Flask, XML-RPC (Standard Library)
* **Frontend:** HTML5, CSS3 (Grid/Flexbox), JavaScript (Fetch API), Chart.js
* **System Monitoring:** `psutil` for hardware metrics
* **Image Processing:** `Pillow (PIL)` for filter applications

---

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Install Dependencies:**
   ```bash
   pip install flask psutil pillow numpy
   ```

---

## ⚡ How to Run the Grid

You will need **4 separate terminal windows** to simulate the full cluster on a single machine.

### Terminal 1: The Load Balancer

Starts the central server that manages workers and routes tasks.

```bash
python src/load_balancer.py
```

### Terminal 2: Worker Node A

Starts a worker listening on port 8000.

```bash
python src/worker.py 8000
```

### Terminal 3: Worker Node B

Starts a second worker listening on port 8001.

```bash
python src/worker.py 8001
```

### Terminal 4: The Web Dashboard

Starts the Flask web interface.

```bash
cd web_dashboard
python app.py
```

---

## Usage Guide

### Access the Dashboard

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Check Telemetry

Verify that the **Live Cluster Telemetry** graph shows two active lines (Node 8000 & Node 8001). They should be idling near 0%.

### Run Image Batch

1. Navigate to **Batch Image Processing**.
2. Click **Select Files** and choose 5-10 images.
3. Click **INITIALIZE BATCH**.

**Observation:** Watch the result cards appear one by one and the CPU graph spike as tasks are distributed.

### Run Password Crack

1. Navigate to **Cryptographic Brute Force**.
2. Enter a short alphanumeric password (e.g., `abc1` or `test5`).
3. Click **EXECUTE SEARCH**.

**Observation:** The system log will display the search ranges assigned to each worker. Once found, the success message and time taken will appear.

---

## Project Structure

```
├── src/
│   ├── load_balancer.py      # Central server & task distributor
│   ├── worker.py              # Worker node logic & health monitoring
│   └── tasks.py               # Computational tasks (Image/Crack)
├── web_dashboard/
│   ├── app.py                 # Flask backend
│   ├── templates/
│   │   └── index.html         # Dashboard UI
│   └── static/
│       ├── style.css          # Dark mode styling
│       ├── script.js          # Frontend logic & Chart.js config
│       ├── uploads/           # Temp storage for uploaded images
│       └── results/           # Storage for processed images
└── README.md
```

---

## Troubleshooting

### Port Conflicts

If a port (8000, 8001, 9000) is already in use, stop the existing process or change the port number in the respective command.

### Connection Refused

Ensure the Load Balancer (Terminal 1) is running before starting the Workers or the Web Dashboard.

### Graph Flatline

If the graph shows no activity during tasks, ensure you are running the updated `worker.py` that includes process-specific CPU monitoring.