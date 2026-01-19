import psutil

# Initialize cpu_percent once so the first call doesn't return 0.0
psutil.cpu_percent(interval=None)

def get_system_stats():
    """
    Fetches real system resources without blocking.
    """
    # interval=None is the key! It returns the usage since the last call immediately.
    cpu_usage = psutil.cpu_percent(interval=None)
    
    memory_info = psutil.virtual_memory()
    ram_usage = memory_info.percent

    stats = {
        "cpu": cpu_usage,
        "ram": ram_usage
    }
    return stats

if __name__ == "__main__":
    print(get_system_stats())