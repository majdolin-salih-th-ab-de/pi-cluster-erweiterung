import re
import os
import time
import subprocess

COMPOSE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "docker-compose.yaml"
)

WORKER_COUNTS = [1, 2, 3, 4, 6, 8, 10, 12, 16]
FIXED_SAMPLES = 1_000_000


def update_compose(n_workers):
    with open(COMPOSE_FILE, "r") as f:
        content = f.read()
    content = re.sub(r"replicas:\s*\d+", f"replicas: {n_workers}", content)
    content = re.sub(r"EXPECTED_WORKERS=\d+", f"EXPECTED_WORKERS={n_workers}", content)
    with open(COMPOSE_FILE, "w") as f:
        f.write(content)
    print(f"[SCALE] → {n_workers} Workers gesetzt")


results = []

for n in WORKER_COUNTS:
    print(f"\n{'='*50}")
    print(f"[SCALE] Test mit {n} Worker(n)")
    print(f"{'='*50}")

    update_compose(n)

    print("[SCALE] Stoppe Docker...")
    os.system("docker compose down")

    print("[SCALE] Starte Docker...")
    os.system("docker build -t pi_cluster:latest .")
    os.system("docker compose up -d")

    print("[SCALE] Warte 20 Sekunden...")
    time.sleep(20)

    print(f"[SCALE] Starte Messung mit {FIXED_SAMPLES:,} Samples...")
    start = time.perf_counter()

    cmd = (
        f'docker exec cluster_main python -c "'
        f'import sys; sys.path.insert(0, chr(47)+chr(115)+chr(114)+chr(99)); '
        f'from distribution import distribute_work; '
        f'from worker_manager import worker_addresses; '
        f'import time; time.sleep(5); '
        f'result = distribute_work({FIXED_SAMPLES}); '
        f'print(result)"'
    )

    proc = subprocess.run(
        ["docker", "exec", "cluster_main", "python", "-c",
         f"""
import sys, time
sys.path.insert(0, '/src')
from worker_manager import worker_addresses, worker_lock
from distribution import distribute_work
time.sleep(5)
result = distribute_work({FIXED_SAMPLES})
print(f'{{result}}')
"""],
        capture_output=True, text=True, timeout=600
    )

    end = time.perf_counter()
    dur = end - start
    sps = FIXED_SAMPLES / dur

    output = proc.stdout.strip()
    print(f"[SCALE] Output: {output}")
    print(f"[SCALE] {n} Workers → {sps:,.0f} Samples/s | Dauer: {dur:.2f}s")

    results.append({"workers": n, "sps": sps, "dur": dur})

# Summary
print("\n=== ERGEBNISSE ===")
print("Workers | Samples/s")
print("-" * 30)
for r in results:
    print(f"{r['workers']:>7} | {r['sps']:>14,.0f}")

# Plot
import matplotlib.pyplot as plt

workers = [r["workers"] for r in results]
speeds = [r["sps"] for r in results]

plt.figure(figsize=(10, 6))
plt.plot(workers, speeds, marker="o", color="blue", label="Gemessen")
plt.xlabel("Anzahl Worker")
plt.ylabel("Samples/s")
plt.title("Amdahl's Law - Skalierungsanalyse")
plt.grid(True)
plt.legend()

os.makedirs("output", exist_ok=True)
plt.savefig("output/scale_results.png")
print("[PLOT] Gespeichert: output/scale_results.png")
plt.show()