import socket

def get_remarkable_ip():
    return "10.11.99.1"

def get_local_ip():
    """Finds the local IP assigned to your machine on the reMarkable USB network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((get_remarkable_ip(), 22))  # Connect to reMarkable's default IP on SSH port
        local_ip = s.getsockname()[0]  # Get the local IP from the socket
    except Exception as e:
        local_ip = "10.11.99.8"  # Default fallback
    finally:
        s.close()
    return local_ip
