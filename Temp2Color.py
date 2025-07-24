def temperature_to_rgb(temp, t_min, t_max):
    """
    Maps a temperature to an RGB color.
    Blue → Cyan → Green → Yellow → Red
    RGB values are floats between 0.0 and 1.0.
    """
    if t_min >= t_max:
        raise ValueError("t_min must be less than t_max")

    # Normalize temperature to range [0.0, 1.0]
    t_norm = (temp - t_min) / (t_max - t_min)

    if t_norm <= 0.25:
        # Blue (0,0,1) → Cyan (0,1,1)
        ratio = t_norm / 0.25
        r = 0.0
        g = ratio
        b = 1.0

    elif t_norm <= 0.5:
        # Cyan (0,1,1) → Green (0,1,0)
        ratio = (t_norm - 0.25) / 0.25
        r = 0.0
        g = 1.0
        b = 1.0 - ratio

    elif t_norm <= 0.75:
        # Green (0,1,0) → Yellow (1,1,0)
        ratio = (t_norm - 0.5) / 0.25
        r = ratio
        g = 1.0
        b = 0.0

    else:
        # Yellow (1,1,0) → Red (1,0,0)
        ratio = (t_norm - 0.75) / 0.25
        r = 1.0
        g = 1.0 - ratio
        b = 0.0

    return (round(r, 3), round(g, 3), round(b, 3))


# Example usage
if __name__ == "__main__":
    t_min = 0
    t_max = 100
    for t in range(t_min, t_max + 1, 10):
        rgb = temperature_to_rgb(t, t_min, t_max)
        print(f"Temperature: {t}°C → RGB: {rgb}")
