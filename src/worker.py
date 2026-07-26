import socket
import os
from shared import monte_carlo_pi
import time

MAIN_HOST = os.environ.get("MAIN_HOST", "main")
MAIN_PORT = int(os.environ.get("MAIN_PORT", 5001))


def register_with_main():
    """
    Registriert den Worker beim Main und bleibt dauerhaft verbunden,
    um wiederholt Aufgaben (Sample-Anzahlen) zu empfangen.
    """
    while True:
        try:
            print(f"[{timestamp()}][WORKER] Verbinde mit {MAIN_HOST}:{MAIN_PORT} ...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((MAIN_HOST, MAIN_PORT))
                print(f"[{timestamp()}][WORKER] Erfolgreich beim Main registriert.")
                while True:
                    data = s.recv(1024)
                    if not data:
                        print(
                            f"[{timestamp()}][WORKER] Verbindung vom Main geschlossen. Neu verbinden."
                        )
                        break  # Raus aus innerer while-Schleife -> Neu verbinden
                    num_samples_str = data.decode("utf-8").strip()
                    try:
                        num_samples = int(num_samples_str)
                    except ValueError:
                        print(
                            f"[{timestamp()}][WORKER] Ungültige Aufgabe empfangen: {num_samples_str}"
                        )
                        continue

                    print(
                        f"[{timestamp()}][WORKER] Aufgabe empfangen: {num_samples} Samples."
                    )
                    start_calc = time.time()
                    inside_circle = monte_carlo_pi(num_samples, raw=True)
                    end_calc = time.time()

                    s.sendall(str(inside_circle).encode("utf-8"))
                    calc_time = end_calc - start_calc
                    print(
                        f"[{timestamp()}][WORKER] Ergebnis gesendet: {inside_circle} Treffer "
                        f"(Dauer: {calc_time:.3f} s)"
                    )
        except Exception as e:
            print(
                f"[{timestamp()}][WORKER] Fehler bei Verbindung oder Aufgabenverarbeitung: {e}"
            )
            time.sleep(5)  # Kurz warten und erneut versuchen


def timestamp():
    """Einfaches Zeit-Format für Logs."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


if __name__ == "__main__":
    register_with_main()
