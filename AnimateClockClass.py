import numpy as np
from scipy.optimize import fsolve
import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from OpenGL_2D_class import gl2D, gl2DArrow, gl2DCircle

from HersheyFont import HersheyFont
hf = HersheyFont()



class ClockAnimator():
    def __init__(self):
        self.title = None
        self.radius = None
        self.angles = []
        self.handAngle = 0
        self.framenum = 0
        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        self.allowDistortion = False

        self.numberOfAnimationFrames  = None
        self.AnimDelayTime = 0.02
        self.AnimReverse = False
        self.AnimRepeat = False
        self.AnimReset = True


    def ProcessFileData(self, filename):

        # Read the file
        f1 = open(filename, 'r')  # open the file for reading
        data = f1.readlines()  # read the entire file as a list of strings
        f1.close()  # close the file  ... very important

        for line in data:  # loop over all the lines
            cells = line.strip().replace('(','').replace(')','').split(',')
            keyword = cells[0].strip().lower()

            if keyword == 'title': self.title = cells[1].replace("'", "")
            if keyword == 'window':
                self.xmin, self.xmax, self.ymin, self.ymax = \
                    (float(cells[1]), float(cells[2]), float(cells[3]), float(cells[4]))

            if keyword == 'radius':
                    self.radius = float(cells[1])

            if keyword == 'angles':
                for i in range(1,len(cells)): #loop over all point pairs
                    self.angles.append(float(cells[i]))

        self.ConnectData()


    def ConnectData(self):
        self.numberOfAnimationFrames = len(self.angles)
        self.handAngle = (90 - (self.angles[0])) * np.pi / 180.0

    def DrawPicture(self):
        # this is what actually draws the picture
        # using data to control what is drawn

        # draw the clock outline
        glColor3f(1, 1, 1)
        glLineWidth(6)
        gl2DCircle(0,0,self.radius,False,36)

        size = self.xmax / 8
        # draw the numbers
        glColor3f(0, 0, 0)  #
        glLineWidth(3)
        for i in range(1,13):
            theta = (90 - (360 * i / 12.0) )  * np.pi / 180
            xloc = (self.radius - size) * np.cos(theta)
            yloc = (self.radius - size) * np.sin(theta)
            hf.drawText(str(i), xloc, yloc, center = True, scale=size)

        #draw the second hand
        glColor3f(1, 0, 0)  #
        glLineWidth(12)
        xval = (self.radius - 2*size) * np.cos(self.handAngle)
        yval = (self.radius - 2*size) * np.sin(self.handAngle)
        glBegin(GL_LINES)  # begin drawing connected lines
        glVertex2f(0, 0)
        glVertex2f(xval, yval)
        glEnd()

        xval = (self.radius - 1.7*size) * np.cos(self.handAngle)
        yval = (self.radius - 1.7*size) * np.sin(self.handAngle)
        gl2DArrow(xval,yval,size,(self.handAngle * 180/np.pi), toCenter=True, widthDeg = 40)




    def PrepareNextAnimationFrameData(self, frame, nframes):
        self.handAngle = (90 - (self.angles[frame])) * np.pi / 180.0


