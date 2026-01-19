# Distributed Adaptive Task Offloading System

A lightweight distributed computing framework in Python that enables resource-constrained "Client" nodes to offload computationally intensive tasks (like Matrix Multiplication) to a grid of "Worker" nodes.

## 🚀 Key Features
* **Dynamic Discovery:** Workers automatically register with the Load Balancer upon startup.
* **Smart Load Balancing:** Tasks are routed to the node with the lowest CPU usage.
* **Fault Tolerance:** Automatic failover reroutes tasks if a worker crashes during execution.
* **Real-time Dashboard:** Live console interface showing active nodes and their status.
* **Low Latency:** Optimized RPC communication with <20ms network overhead.

## 🛠️ Tech Stack
* **Python 3.x**
* **XML-RPC** (Standard Library) for internode communication.
* **Psutil** for real-time hardware monitoring.

## ⚡ How to Run
1. **Start the Load Balancer:**
   `python src/load_balancer.py`
2. **Start Workers (in separate terminals):**
   `python src/worker.py 8000`
   `python src/worker.py 8001`
3. **Run Client Task:**
   `python src/client.py`