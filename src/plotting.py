import os
from datetime import datetime


def plot_results(results):
    """Erstellt und speichert Plots für Fehler zu π und Samples/s."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[PLOT] matplotlib not installed, skipping.")
        return

    samples = [r["samples"] for r in results]
    errors = [r["error_to_pi"] for r in results]
    speeds = [r["samples_per_sec"] for r in results]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(samples, errors, marker="o")
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_title("Fehler zu π")

    axes[1].plot(samples, speeds, marker="o")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Samples/s")

    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"pi_cluster_test_results_{timestamp}.png"

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "Output")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)

    plt.savefig(file_path)
    print(f"[PLOT] Gespeichert: {file_path}")

    try:
        plt.show()
    except Exception:
        pass


def plot_scaling_results(results):
    """Erstellt Amdahl's Law Kurve - Samples/s vs Worker-Anzahl."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[PLOT] matplotlib not installed, skipping.")
        return

    workers = [r["workers"] for r in results]
    speeds = [r["samples_per_sec"] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(workers, speeds, marker="o", color="blue", label="Gemessen")

    # Kipppunkt finden
    max_speed = max(speeds)
    max_workers = workers[speeds.index(max_speed)]
    ax.axvline(x=max_workers, color="red", linestyle="--",
               label=f"Kipppunkt: {max_workers} Worker")

    ax.set_xlabel("Anzahl Worker")
    ax.set_ylabel("Samples/s")
    ax.set_title("Amdahl's Law - Skalierungsanalyse")
    ax.legend()
    ax.grid(True)

    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"scale_test_results_{timestamp}.png"

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "Output")
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, filename)

    plt.savefig(file_path)
    print(f"[PLOT] Gespeichert: {file_path}")

    try:
        plt.show()
    except Exception:
        pass