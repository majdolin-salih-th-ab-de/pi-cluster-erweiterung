import time
import math
from worker_manager import wait_for_workers, worker_addresses
from distribution import distribute_work
from plotting import plot_results, plot_scaling_results


def automated_test_mode():
    """Führt einen automatischen Testlauf durch."""
    wait_for_workers()
    sample_sizes = [10_000, 100_000, 1_000_000, 10_000_000, 100_000_000, 1_000_000_000]
    results = []

    for i, s in enumerate(sample_sizes, start=1):
        print(f"[AUTO] Test {i}/{len(sample_sizes)}: {s} Samples")
        start = time.perf_counter()
        pi_approx = distribute_work(s)
        end = time.perf_counter()

        if pi_approx is None:
            print("[AUTO] No worker available, stopping.")
            break

        dur = end - start
        sps = s / dur if dur else 0
        err = abs(pi_approx - math.pi)

        results.append(
            {
                "samples": s,
                "pi_approx": pi_approx,
                "duration_s": dur,
                "samples_per_sec": sps,
                "error_to_pi": err,
                "active_workers": len(worker_addresses),
            }
        )

    print_test_summary(results)
    plot_results(results)


def scale_test():
    """Testet automatisch mit verschiedenen Worker-Anzahlen (Amdahl's Law)."""
    worker_counts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 18, 21, 24, 27, 30]
    fixed_samples = 10_000_000
    scaling_results = []

    print("\n=== SCALE TEST (Amdahl's Law) ===")
    print(f"[SCALE] Fixed Samples: {fixed_samples:,}")

    for n_workers in worker_counts:
        print(f"\n[SCALE] Warte auf {n_workers} Worker...")

        timeout = 60
        start_wait = time.time()
        while True:
            current = len(worker_addresses)
            if current >= n_workers:
                break
            if time.time() - start_wait > timeout:
                print(f"[SCALE] Timeout! Nur {current} Worker verfügbar.")
                break
            time.sleep(1)

        if len(worker_addresses) < n_workers:
            continue

        start = time.perf_counter()
        pi_approx = distribute_work(fixed_samples)
        end = time.perf_counter()

        if pi_approx is None:
            continue

        dur = end - start
        sps = fixed_samples / dur if dur else 0

        print(f"[SCALE] {n_workers} Worker → {sps:,.0f} Samples/s")

        scaling_results.append({
            "workers": n_workers,
            "samples_per_sec": sps,
            "duration_s": dur,
            "pi_approx": pi_approx,
        })

    print_scale_summary(scaling_results)
    plot_scaling_results(scaling_results)


def print_test_summary(results):
    print("\n=== TEST SUMMARY ===")
    print(
        "Samples       |   Pi_Approx      |  Dauer(s) |  Samples/s    |  Error_to_pi   | Workers"
    )
    print(
        "----------------------------------------------------------------------------------------"
    )
    for r in results:
        print(
            f"{r['samples']:>12,} | {r['pi_approx']:<16.8f} | {r['duration_s']:>9.3f} | "
            f"{r['samples_per_sec']:>12,.1f} | {r['error_to_pi']:.6e} | {r['active_workers']:>7}"
        )
    print()


def print_scale_summary(results):
    print("\n=== SCALE TEST SUMMARY ===")
    print("Workers |   Samples/s    |  Dauer(s) |  Pi_Approx")
    print("-------------------------------------------------------")
    for r in results:
        print(
            f"{r['workers']:>7} | {r['samples_per_sec']:>14,.0f} | "
            f"{r['duration_s']:>9.3f} | {r['pi_approx']:.8f}"
        )
    print()