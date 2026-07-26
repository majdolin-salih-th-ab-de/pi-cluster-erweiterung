import threading
from utility import timestamp
from worker_manager import worker_listener, wait_for_workers
from test_mode import automated_test_mode, scale_test
from distribution import distribute_work


def main_loop():
    print(f"[{timestamp()}][MAIN] Starting main process.")
    t = threading.Thread(target=worker_listener, daemon=True)
    t.start()

    wait_for_workers()

    while True:
        user_input = (
            input(f"\n[{timestamp()}][MAIN] Enter samples or 'auto'/'scale'/'q': ")
            .strip()
            .lower()
        )

        if user_input in ("q", "quit"):
            print(f"[{timestamp()}][MAIN] Exiting.")
            break

        if user_input in ("auto", "test"):
            automated_test_mode()
            continue

        if user_input in ("scale", "scaletest"):
            scale_test()
            continue

        try:
            total_samples = int(user_input)
            if total_samples <= 0:
                print(f"[{timestamp()}][MAIN] Enter a positive number.")
                continue
        except ValueError:
            print(f"[{timestamp()}][MAIN] Invalid input.")
            continue

        print(f"[{timestamp()}][MAIN] Distributing {total_samples} samples.")
        distribute_work(total_samples)

    print(f"[{timestamp()}][MAIN] Main process ended.")


if __name__ == "__main__":
    main_loop()