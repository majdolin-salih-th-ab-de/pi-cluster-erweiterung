import threading
import time
from utility import timestamp
from worker_manager import worker_addresses, worker_lock


def distribute_work(total_samples):
    """Verteilt total_samples auf Worker, sammelt Ergebnisse und berechnet Pi."""
    with worker_lock:
        if not worker_addresses:
            print(f"[{timestamp()}][MAIN] No workers available.")
            return None

    print(f"[{timestamp()}][MAIN] Computing with {len(worker_addresses)} worker(s).")
    start = time.perf_counter()
    per_worker = total_samples // len(worker_addresses)
    total_hits_list = []
    hits_lock = threading.Lock()

    def handle_worker(conn, addr):
        try:
            conn.sendall(str(per_worker).encode("utf-8"))
            data = conn.recv(1024)
            if not data:
                raise ConnectionError("No data from worker.")
            result = int(data.decode("utf-8"))
            with hits_lock:
                total_hits_list.append(result)
            print(f"[{timestamp()}][MAIN] Worker {addr} => {result}")
        except Exception as e:
            print(f"[{timestamp()}][MAIN] Error {addr}: {e}")
            with worker_lock:
                if (conn, addr) in worker_addresses:
                    worker_addresses.remove((conn, addr))
            conn.close()

    threads = []
    with worker_lock:
        active_workers = list(worker_addresses)

    for conn, addr in active_workers:
        t = threading.Thread(target=handle_worker, args=(conn, addr))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    n_ok = len(total_hits_list)
    effective_samples = per_worker * n_ok
    duration = time.perf_counter() - start

    if effective_samples > 0:
        pi_approx = 4.0 * sum(total_hits_list) / effective_samples
        sps = effective_samples / duration if duration else 0
        print(f"[{timestamp()}][MAIN] Pi ≈ {pi_approx:.15f}")
        print(f"[{timestamp()}][MAIN] Duration: {duration:.3f}s")
        print(f"[{timestamp()}][MAIN] Effective: {effective_samples}, SPS: {sps:.1f}\n")
        return pi_approx
    else:
        print(f"[{timestamp()}][MAIN] No successful worker responses.\n")
        return None
