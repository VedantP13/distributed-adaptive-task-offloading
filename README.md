# Distributed Compute Grid & Engineering Dashboard

A robust distributed computing framework that offloads computationally intensive tasks—such as batch image processing and cryptographic brute-forcing—to a dynamic grid of worker nodes. It features a real-time "Engineering Dashboard" with live CPU telemetry, centralized logging, and visual task management.

## 🚀 Key Features

### 🖥️ **Centralized Web Dashboard**
* **Dark Mode UI:** Professional, "SpaceX-style" interface for monitoring the grid.
* **Live Telemetry:** Real-time CPU usage graphs for every connected worker node (Chart.js).
* **Integrated Terminal:** A draggable, collapsible system log window streaming events from the backend.

### ⚡ **Distributed Task Execution**
* **Batch Image Processing:**
    * Upload multiple images simultaneously.
    * The Load Balancer distributes them across available workers.
    * Results stream in real-time as workers complete tasks (Blur, Grayscale, etc.).
* **Distributed Password Cracking:**
    * Splits the search space for Alphanumeric passwords (Base-36) across the grid.
    * Supports distributed brute-forcing for passwords of varying lengths.
    * Returns success instantly once any node finds the match.

### ⚙️ **System Architecture**
* **Smart Load Balancing:** Dynamically routes tasks based on node availability and CPU health.
* **Process Isolation:** Workers measure their specific process CPU usage, allowing for accurate monitoring even on a single host.
* **Scalability:** Supports adding new worker nodes dynamically without restarting the system.

## 🛠️ Tech Stack
* **Backend:** Python 3.x, Flask, XML-RPC (Standard Library).
* **Frontend:** HTML5, CSS3 (Grid/Flexbox), JavaScript (Fetch API), Chart.js.
* **System Monitoring:** `psutil` for hardware metrics.
* **Image Processing:** `Pillow (PIL)` for filter applications.

---

## 📦 Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Install Dependencies:**
    ```bash
    pip install flask psutil pillow numpy
    ```

---

## ⚡ How to Run the Grid (The "Power Demo")

You will need **4 separate terminal windows** to simulate the full cluster.

### **Terminal 1: The Load Balancer (The Brain)**
Starts the central server that manages workers and routes tasks.
```bash
python src/load_balancer.py