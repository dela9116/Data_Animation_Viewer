from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window dimensions
width, height = 1000, 200

def draw_gradient_rectangle():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Set up orthographic projection for 2D
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)

    drawTemperatureColorBar(100, 800, 80, 120)

    glutSwapBuffers()

def drawTemperatureColorBar(xmin,xmax,ymin,ymax):

    deltaX = (xmax-xmin)/4
    glBegin(GL_QUADS)
    # Define the gradient colors (left to right: blue to red)
    glColor3f(0.0, 0.0, 1.0)  # Blue
    glVertex2f(100, ymin)  # Bottom-left
    glVertex2f(100, ymax)  # Top-left

    glColor3f(0.0, 1.0, 1.0)  # Red
    glVertex2f(xmin+deltaX, ymax)  # Top-right
    glVertex2f(xmin+deltaX, ymin)  # Bottom-right
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 1.0)  # Blue
    glVertex2f(xmin+deltaX, ymin)  # Bottom-left
    glVertex2f(xmin+deltaX, ymax)  # Top-left

    glColor3f(0.0, 1.0, 0.0)  # Red
    glVertex2f(xmin+2*deltaX, ymax)  # Top-right
    glVertex2f(xmin+2*deltaX, ymin)  # Bottom-right
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)  # Blue
    glVertex2f(xmin+2*deltaX, ymin)  # Bottom-left
    glVertex2f(xmin+2*deltaX, ymax)  # Top-left

    glColor3f(1.0, 1.0, 0.0)  # Red
    glVertex2f(xmin+3*deltaX, ymax)  # Top-right
    glVertex2f(xmin+3*deltaX, ymin)  # Bottom-right
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(1.0, 1.0, 0.0)  # Blue
    glVertex2f(xmin+3*deltaX, ymin)  # Bottom-left
    glVertex2f(xmin+3*deltaX, ymax)  # Top-left

    glColor3f(1.0, 0.0, 0.0)  # Red
    glVertex2f(xmin+4*deltaX, ymax)  # Top-right
    glVertex2f(xmin+4*deltaX, ymin)  # Bottom-right
    glEnd()


def temperature_to_rgb(temp, t_min, t_max):
    """
    Maps a temperature value to an RGB color.
    Blue = t_min, Green = middle, Red = t_max
    """
    if t_min >= t_max:
        raise ValueError("t_min must be less than t_max")

    # Normalize temperature to range [0, 1]
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

    return (r, g, b)



def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Horizontal Rectangle with Color Gradient")
    glutDisplayFunc(draw_gradient_rectangle)
    glutIdleFunc(draw_gradient_rectangle)
    glutMainLoop()

if __name__ == "__main__":
    main()