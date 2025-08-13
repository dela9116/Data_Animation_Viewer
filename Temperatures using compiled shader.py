import glfw
from OpenGL.GL import *
import numpy as np

# Vertex shader (passes normalized x to fragment shader)
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec2 position;
layout (location = 1) in float xNorm;

out float xCoord;

void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    xCoord = xNorm;
}
"""


# Fragment shader (color gradient logic using xCoord)
FRAGMENT_SHADER = """
#version 330 core
in float xCoord;
out vec4 FragColor;

void main() {
    vec3 color;

    // Gradient segments with linear interpolation
    if (xCoord < 0.25)
        color = mix(vec3(0.0, 0.0, 1.0), vec3(0.0, 1.0, 1.0), xCoord / 0.25);              // Blue → Cyan
    else if (xCoord < 0.5)
        color = mix(vec3(0.0, 1.0, 1.0), vec3(0.0, 1.0, 0.0), (xCoord - 0.25) / 0.25);     // Cyan → Green
    else if (xCoord < 0.75)
        color = mix(vec3(0.0, 1.0, 0.0), vec3(1.0, 1.0, 0.0), (xCoord - 0.5) / 0.25);     // Green → Yellow
    else
        color = mix(vec3(1.0, 1.0, 0.0), vec3(1.0, 0.0, 0.0), (xCoord - 0.75) / 0.25);     // Yellow → Red

    FragColor = vec4(color, 1.0);
}
"""

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    # Check for compilation errors
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode())
    return shader

def create_shader_program(vertex_src, fragment_src):
    vertex_shader = compile_shader(vertex_src, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_src, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    # Check for linking errors
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program).decode())

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

def main():
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW initialization failed")

    # Create a window
    window = glfw.create_window(900, 200, "Horizontal Gradient Rectangle", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window creation failed")
    glfw.make_context_current(window)

    # Rectangle vertices: x, y, normalized x (0 to 1)
    vertices = np.array([
        -0.9, -0.9, 0.0,
        -0.9,  0.9, 0.25,
         0.9,  0.9, 1.0,
         0.9, -0.9, 0.75
    ], dtype=np.float32)

    indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.uint32)

    # Set up VAO, VBO, EBO
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    # Vertex attributes
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))   # position (x, y)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(8))   # xNorm
    glEnableVertexAttribArray(1)

    # Compile and use shader program
    shader_program = create_shader_program(VERTEX_SHADER, FRAGMENT_SHADER)
    glUseProgram(shader_program)

    # Rendering loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClearColor(0.1, 0.1, 0.1, 1.0)  # background
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader_program)
        glBindVertexArray(VAO)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
