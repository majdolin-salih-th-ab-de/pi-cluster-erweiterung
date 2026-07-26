import socket
import threading
import time
import os
from utility import timestamp

EXPECTED_WORKERS = int(os.environ.get("EXPECTED_WORKERS", 1))
worker_addresses = []
worker_lock = threading.Lock()


def worker_listener(host="0.0.0.0", port=5001):
    """Akzeptiert Worker-Verbindungen, begrenzt auf EXPECTED_WORKERS."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"[{timestamp()}][MAIN] Listening on {host}:{port} ...")
        while True:
            conn, addr = server_socket.accept()
            with worker_lock:
                if len(worker_addresses) < EXPECTED_WORKERS:
                    worker_addresses.append((conn, addr))
                    print(
                        f"[{timestamp()}][MAIN] Worker registered {addr} "
                        f"({len(worker_addresses)}/{EXPECTED_WORKERS})"
                    )
                else:
                    print(f"[{timestamp()}][MAIN] Extra worker rejected {addr}")
                    conn.close()


def wait_for_workers():
    """Blockiert, bis EXPECTED_WORKERS registriert sind."""
    print(f"[{timestamp()}][MAIN] Waiting for {EXPECTED_WORKERS} worker(s) ...")
    while True:
        with worker_lock:
            if len(worker_addresses) >= EXPECTED_WORKERS:
                print(f"[{timestamp()}][MAIN] {EXPECTED_WORKERS} worker(s) ready.")
                break
        time.sleep(1)
