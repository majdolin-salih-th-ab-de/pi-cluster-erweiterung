import re
import os
import time
import subprocess
import matplotlib.pyplot as plt

COMPOSE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "docker-compose.yaml"
)

WORKER_COUNTS = [6, 12, 18, 24, 30]
FIXED_SAMPLES = 10_000_000


def update_compose(n_workers):
    with open(COMPOSE_FILE, "r") as f:
        content = f.read()
    content = re.sub(r"replicas:\s*\d+", f"replicas: {n_workers // 6}", content)
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

    os.system("docker compose down")
    os.system("docker compose up -d")

    print("[SCALE] Warte 30 Sekunden...")
    time.sleep(30)

    proc = subprocess.run(
        ["docker", "exec", "cluster_main", "python", "-c",
         f"""
import sys
sys.path.insert(0, '/src')
from worker_manager import wait_for_workers
from distribution import distribute_work
import time

wait_for_workers()
time.sleep(2)

import time as t
start = t.perf_counter()
pi = distribute_work({FIXED_SAMPLES})
end = t.perf_counter()

dur = end - start
sps = {FIXED_SAMPLES} / dur
print(f'SPS:{{sps:.0f}}')
"""],
        capture_output=True, text=True, timeout=300
    )

    output = proc.stdout.strip()
    sps = 0
    for line in output.split('\n'):
        if 'SPS:' in line:
            try:
                sps = float(line.split('SPS:')[1].strip())
            except:
                pass

    print(f"[SCALE] {n} Workers → {sps:,.0f} Samples/s")
    results.append({"workers": n, "sps": sps})

# Summary
print("\n=== ERGEBNISSE ===")
print("Workers | Samples/s")
print("-" * 30)
for r in results:
    print(f"{r['workers']:>7} | {r['sps']:>14,.0f}")

# Plot
workers = [r["workers"] for r in results]
speeds = [r["sps"] for r in results]

max_speed = max(speeds)
max_workers = workers[speeds.index(max_speed)]

plt.figure(figsize=(10, 6))
plt.plot(workers, speeds, marker="o", color="blue", label="Gemessen")
plt.axvline(x=max_workers, color="red", linestyle="--",
            label=f"Kipppunkt: {max_workers} Worker")
plt.xlabel("Anzahl Worker")
plt.ylabel("Samples/s")
plt.title("Amdahl's Law - Skalierungsanalyse (6 VMs)")
plt.grid(True)
plt.legend()

os.makedirs("output", exist_ok=True)
plt.savefig("output/scale_results_vm.png")
print("[PLOT] Gespeichert: output/scale_results_vm.png")