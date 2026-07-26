import random


def monte_carlo_pi(num_samples: int, raw=False) -> float:
    """Berechne Pi über Monte-Carlo-Methode.

    Args:
        num_samples (int): Anzahl der Stichproben.
        raw (bool): Wenn True, gibt die Treffer im Kreis zurück.

    Returns:
        float: Treffer im Kreis (raw=True) oder Pi-Approximation (raw=False).
    """
    inside_circle = 0
    for _ in range(num_samples):
        x = random.random()
        y = random.random()
        if x * x + y * y <= 1.0:
            inside_circle += 1

    if raw:
        return inside_circle  # Treffer im Kreis
    return 4.0 * inside_circle / num_samples
