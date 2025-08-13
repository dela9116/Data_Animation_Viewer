# fourbar_old_opengl.py
import math
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# -------- Four-bar parameters (units: arbitrary) --------
L1 = 2.0   # Ground (fixed) distance A->D
L2 = 1.0   # Input crank A->B
L3 = 2.2   # Coupler B->C
L4 = 1.8   # Output link C->D

A = (0.0, 0.0)      # Ground left pivot
D = (L1, 0.0)       # Ground right pivot

omega = 1.0         # Crank angular speed (rad/s)
line_w = 3.0

# View extents (simple generous bounds)
PAD = 0.5
XMIN = - (L2 + L3) - PAD
XMAX =  L1 + (L3 + L4) + PAD
YMIN = - (L2 + L3) - PAD
YMAX =   (L2 + L3) + PAD

# Animation state
last_time_ms = 0

def circle_intersection(B, r1, Dp, r2, elbow="up"):
    """
    Intersection of circles:
      center B radius r1, and center Dp radius r2.
    Returns point C. 'elbow' selects which intersection.
    """
    (x0, y0) = B
    (x1, y1) = Dp
    dx = x1 - x0
    dy = y1 - y0
    d = math.hypot(dx, dy)
    # Guard against impossible geometry (numerical safety)
    d = max(1e-9, min(d, r1 + r2))
    d = max(d, abs(r1 - r2))

    a = (r1*r1 - r2*r2 + d*d) / (2*d)
    h_sq = max(r1*r1 - a*a, 0.0)
    h = math.sqrt(h_sq)

    xm = x0 + a * dx / d
    ym = y0 + a * dy / d

    rx = -dy * (h / d)
    ry =  dx * (h / d)

    if elbow == "up":
        return (xm + rx, ym + ry)
    else:
        return (xm - rx, ym - ry)

def solve_positions(theta2, elbow="up"):
    """
    Given input crank angle theta2 (at A), compute positions of joints:
    A, B, C, D using circle intersection for the coupler/follower.
    """
    Ax, Ay = A
    Dx, Dy = D

    Bx = Ax + L2 * math.cos(theta2)
    By = Ay + L2 * math.sin(theta2)
    B = (Bx, By)

    C = circle_intersection(B, L3, D, L4, elbow=elbow)
    return (A, B, C, D)

# -------- OpenGL/GLUT callbacks --------
def init_gl():
    glClearColor(0.08, 0.08, 0.10, 1.0)
    glDisable(GL_DEPTH_TEST)
    glLineWidth(line_w)
    glPointSize(7.0)

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Keep aspect ratio by adjusting orthographic box
    aspect = w / float(h if h > 0 else 1)
    wx = XMAX - XMIN
    wy = YMAX - YMIN
    world_aspect = wx / wy
    if aspect >= world_aspect:
        # window wider than world -> expand x
        new_wx = wy * aspect
        cx = 0.5 * (XMIN + XMAX)
        glOrtho(cx - new_wx/2, cx + new_wx/2, YMIN, YMAX, -1, 1)
    else:
        # window taller -> expand y
        new_wy = wx / aspect
        cy = 0.5 * (YMIN + YMAX)
        glOrtho(XMIN, XMAX, cy - new_wy/2, cy + new_wy/2, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def draw_link(p0, p1, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_LINES)
    glVertex2f(*p0)
    glVertex2f(*p1)
    glEnd()

def draw_point(p, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    glVertex2f(*p)
    glEnd()

def display():
    global last_time_ms
    glClear(GL_COLOR_BUFFER_BIT)

    # Time -> crank angle
    t_ms = glutGet(GLUT_ELAPSED_TIME)  # milliseconds since GLUT init
    t = 0.001 * t_ms
    theta2 = omega * t

    # Solve positions (pick "elbow up" branch)
    A_, B_, C_, D_ = solve_positions(theta2, elbow="up")

    # Draw ground
    draw_link(A_, D_, 0.7, 0.7, 0.7)

    # Draw links: AB (input), BC (coupler), CD (output)
    draw_link(A_, B_, 1.0, 0.2, 0.2)   # red-ish crank
    draw_link(B_, C_, 0.2, 1.0, 0.2)   # green-ish coupler
    draw_link(C_, D_, 0.2, 0.4, 1.0)   # blue-ish follower

    # Joints
    draw_point(A_, 1, 1, 0)  # yellow-ish
    draw_point(B_, 1, 1, 1)
    draw_point(C_, 1, 1, 1)Q    `               1
    draw_point(D_, 1, 1, 0)

    glutSwapBuffers()

def idle():
    # Trigger redraw; GLUT_ELAPSED_TIME drives motion
    glutPostRedisplay()

def keyboard(key, x, y):
    if key in (b'\x1b', b'q'):  # ESC or q
        sys.exit(0)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(900, 600)
    glutCreateWindow(b"Four-bar Mechanism (Old OpenGL / PyOpenGL + GLUT)")

    init_gl()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)

    glutMainLoop()

if __name__ == "__main__":
    main()
