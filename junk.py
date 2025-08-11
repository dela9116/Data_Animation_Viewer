from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


# Map temperature to RGB
def temp_to_rgb(temp, tmin, tmax):
    # Normalize 0..1
    t = (temp - tmin) / (tmax - tmin)
    t = max(0.0, min(1.0, t))

    # Control points
    p0, p1, p2, p3, p4 = 0.0, 0.25, 0.5, 0.75, 1.0
    c0 = (0.0, 0.0, 1.0)  # blue
    c1 = (0.0, 1.0, 1.0)  # cyan
    c2 = (0.0, 1.0, 0.0)  # green
    c3 = (1.0, 1.0, 0.0)  # yellow
    c4 = (1.0, 0.0, 0.0)  # red

    if t <= p1:
        alpha = (t - p0) / (p1 - p0)
        return tuple(c0[i] + alpha * (c1[i] - c0[i]) for i in range(3))
    elif t <= p2:
        alpha = (t - p1) / (p2 - p1)
        return tuple(c1[i] + alpha * (c2[i] - c1[i]) for i in range(3))
    elif t <= p3:
        alpha = (t - p2) / (p3 - p2)
        return tuple(c2[i] + alpha * (c3[i] - c2[i]) for i in range(3))
    else:
        alpha = (t - p3) / (p4 - p3)
        return tuple(c3[i] + alpha * (c4[i] - c3[i]) for i in range(3))


def draw_shaded_rectangle_oldgl(temp_tl, temp_tr, temp_br, temp_bl, tmin=None, tmax=None):
    # Decide min/max
    temps = [temp_tl, temp_tr, temp_br, temp_bl]
    if tmin is None:
        tmin = min(temps)
    if tmax is None:
        tmax = max(temps)

    glBegin(GL_QUADS)

    # Top-left
    glColor3f(*temp_to_rgb(temp_tl, tmin, tmax))
    glVertex2f(-0.9, 0.9)

    # Top-right
    glColor3f(*temp_to_rgb(temp_tr, tmin, tmax))
    glVertex2f(0.9, 0.9)

    # Bottom-right
    glColor3f(*temp_to_rgb(temp_br, tmin, tmax))
    glVertex2f(0.9, -0.9)

    # Bottom-left
    glColor3f(*temp_to_rgb(temp_bl, tmin, tmax))
    glVertex2f(-0.9, -0.9)

    glEnd()


# --- Minimal GLUT demo ---
def main():
    def display():
        glClear(GL_COLOR_BUFFER_BIT)
        draw_shaded_rectangle_oldgl(0, 37, 50, 12, tmin=0, tmax=50)
        glFlush()

    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"Old OpenGL Shaded Rectangle")
    glClearColor(0.9, 0.9, 0.9, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1, 1, -1, 1)
    glutDisplayFunc(display)
    glutMainLoop()


if __name__ == "__main__":
    main()
