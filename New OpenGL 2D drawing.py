import sys
import math
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PyQt5.QtGui import QSurfaceFormat
#from PyQt5.QtOpenGL import QOpenGLWidget
from OpenGL import GL

# ---------- Shaders ----------
VERT_SRC = """
#version 330 core
layout (location = 0) in vec2 aPos;
void main() {
    gl_Position = vec4(aPos, 0.0, 1.0);
}
"""

FRAG_SRC = """
#version 330 core
out vec4 FragColor;
uniform vec3 uColor;
void main() {
    FragColor = vec4(uColor, 1.0);
}
"""

def compile_shader(src, shader_type):
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, src)
    GL.glCompileShader(shader)
    if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
        raise RuntimeError(GL.glGetShaderInfoLog(shader).decode())
    return shader

def link_program(vs, fs):
    prog = GL.glCreateProgram()
    GL.glAttachShader(prog, vs)
    GL.glAttachShader(prog, fs)
    GL.glLinkProgram(prog)
    if not GL.glGetProgramiv(prog, GL.GL_LINK_STATUS):
        raise RuntimeError(GL.glGetProgramInfoLog(prog).decode())
    GL.glDetachShader(prog, vs)
    GL.glDetachShader(prog, fs)
    GL.glDeleteShader(vs)
    GL.glDeleteShader(fs)
    return prog

def make_vao_from_xy(pts_xy):
    vao = GL.glGenVertexArrays(1)
    vbo = GL.glGenBuffers(1)
    GL.glBindVertexArray(vao)
    arr = np.array(pts_xy, dtype=np.float32)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, arr.nbytes, arr, GL.GL_STATIC_DRAW)
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, None)
    GL.glBindVertexArray(0)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    return vao, vbo, len(arr) // 2

def make_box_outline(minx, miny, maxx, maxy):
    return [
        minx, miny,
        maxx, miny,
        maxx, maxy,
        minx, maxy
    ]

def make_circle(cx, cy, r, segments=128):
    pts = [cx, cy]
    for i in range(segments + 1):
        theta = 2.0 * math.pi * i / segments
        pts.extend([cx + r * math.cos(theta), cy + r * math.sin(theta)])
    return pts

# ---------- QOpenGLWidget ----------
class MyGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.program = None
        self.uColor_loc = None
        self.vao_box = self.vbo_box = self.count_box = None
        self.vao_circle = self.vbo_circle = self.count_circle = None

    def initializeGL(self):
        # Compile shaders
        vs = compile_shader(VERT_SRC, GL.GL_VERTEX_SHADER)
        fs = compile_shader(FRAG_SRC, GL.GL_FRAGMENT_SHADER)
        self.program = link_program(vs, fs)
        self.uColor_loc = GL.glGetUniformLocation(self.program, "uColor")

        # Geometry
        box_pts = make_box_outline(-0.7, -0.5, 0.7, 0.5)
        circle_pts = make_circle(0.0, 0.0, 0.3, 180)

        self.vao_box, self.vbo_box, self.count_box = make_vao_from_xy(box_pts)
        self.vao_circle, self.vbo_circle, self.count_circle = make_vao_from_xy(circle_pts)

        GL.glClearColor(0.1, 0.1, 0.12, 1.0)
        #GL.glLineWidth(3.0)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glUseProgram(self.program)

        # Yellow filled circle
        GL.glUniform3f(self.uColor_loc, 1.0, 1.0, 0.0)
        GL.glBindVertexArray(self.vao_circle)
        GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, self.count_circle)

        # Red rectangle outline
        GL.glUniform3f(self.uColor_loc, 1.0, 0.0, 0.0)
        GL.glBindVertexArray(self.vao_box)
        GL.glDrawArrays(GL.GL_LINE_LOOP, 0, self.count_box)

        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

    def resizeGL(self, w, h):
        GL.glViewport(0, 0, w, h)

# ---------- Main window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 OpenGL - Red Box + Yellow Circle")
        self.resize(800, 600)
        self.gl_widget = MyGLWidget()
        self.setCentralWidget(self.gl_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Request modern OpenGL 3.3 core
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    QSurfaceFormat.setDefaultFormat(fmt)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
