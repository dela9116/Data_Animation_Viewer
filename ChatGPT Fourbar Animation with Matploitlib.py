import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------- Four-bar geometry ----------
# Link lengths
L1 = 2.0   # Ground link (fixed)
L2 = 1.0   # Input crank
L3 = 2.2   # Coupler
L4 = 1.8   # Output link

# Ground pivot coordinates
A = np.array([0.0, 0.0])
D = np.array([L1, 0.0])

# Input crank rotation speed (rad/s)
omega = 1.0

# Time vector
t_max = 8
fps = 60
times = np.linspace(0, t_max, t_max * fps)

# ---------- Position solver ----------
def solve_positions(theta2):
    """
    Given crank angle theta2, solve for theta3 (coupler) and theta4 (follower) angles.
    Uses loop-closure equations.
    """
    # Coordinates of B from crank angle
    Bx = A[0] + L2 * np.cos(theta2)
    By = A[1] + L2 * np.sin(theta2)
    B = np.array([Bx, By])

    # Solve for C using intersection of circles:
    # Circle 1: center B, radius L3
    # Circle 2: center D, radius L4
    dx = D[0] - B[0]
    dy = D[1] - B[1]
    dist = np.hypot(dx, dy)

    # If impossible geometry, clamp
    if dist > (L3 + L4):
        dist = L3 + L4
    if dist < abs(L3 - L4):
        dist = abs(L3 - L4)

    # Circle intersection formula
    a = (L3**2 - L4**2 + dist**2) / (2 * dist)
    h = np.sqrt(max(L3**2 - a**2, 0))
    xm = B[0] + a * dx / dist
    ym = B[1] + a * dy / dist
    rx = -dy * (h / dist)
    ry = dx * (h / dist)

    # Choose "upper" intersection
    Cx = xm + rx
    Cy = ym + ry
    C = np.array([Cx, Cy])

    return A, B, C, D

# ---------- Animation ----------
fig, ax = plt.subplots()
ax.set_aspect('equal', 'box')
ax.set_xlim(-2, L1 + 2)
ax.set_ylim(-2, 2)

# Lines for links
line_AB, = ax.plot([], [], 'ro-', lw=2)  # crank
line_BC, = ax.plot([], [], 'go-', lw=2)  # coupler
line_CD, = ax.plot([], [], 'bo-', lw=2)  # follower
line_DA, = ax.plot([], [], 'ko-', lw=2)  # ground

def init():
    line_AB.set_data([], [])
    line_BC.set_data([], [])
    line_CD.set_data([], [])
    line_DA.set_data([], [])
    return line_AB, line_BC, line_CD, line_DA

def update(frame):
    theta2 = omega * times[frame]
    A, B, C, Dp = solve_positions(theta2)

    line_AB.set_data([A[0], B[0]], [A[1], B[1]])
    line_BC.set_data([B[0], C[0]], [B[1], C[1]])
    line_CD.set_data([C[0], Dp[0]], [C[1], Dp[1]])
    line_DA.set_data([Dp[0], A[0]], [Dp[1], A[1]])

    return line_AB, line_BC, line_CD, line_DA

ani = FuncAnimation(fig, update, frames=len(times), init_func=init,
                    blit=True, interval=1000/fps)

plt.show()
