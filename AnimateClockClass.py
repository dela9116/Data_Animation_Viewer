import numpy as np
from scipy.optimize import fsolve
import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from OpenGL_2D_class import gl2D, gl2DText, gl2DCircle


class Fourbar():

    def __init__(self):
        #fourbar data
        self.a0x = 0
        self.a0y = 0
        self.ax = 0
        self.ay = 0
        self.b0x = 0
        self.b0y = 0
        self.bx = 0
        self.by = 0

        #needed for animation
        self.theta2start = 0
        self.theta2end = 0
        self.th3start = 0
        self.th4start = 0
        self.axstart = 0
        self.aystart = 0
        self.th1 = 0
        self.th2 = 0
        self.th3 = 0
        self.th4 = 0
        self.L1 = 0
        self.L2 = 0
        self.L3 = 0
        self.L4 = 0

    def LengthsAndAngles(self):
        fb=self #shorthand
        fb.L1 = np.sqrt((fb.a0x-fb.b0x)**2 + (fb.a0y-fb.b0y)**2)
        fb.L2 = np.sqrt((fb.a0x-fb.ax)**2 + (fb.a0y-fb.ay)**2)
        fb.L3 = np.sqrt((fb.bx-fb.ax)**2 + (fb.by-fb.ay)**2)
        fb.L4 = np.sqrt((fb.b0x-fb.bx)**2 + (fb.b0y-fb.by)**2)
        fb.th1 = np.arctan2(fb.a0y-fb.b0y , fb.a0x-fb.b0x)
        fb.th2 = np.arctan2(fb.ay-fb.a0y , fb.ax-fb.a0x)
        fb.th3 = np.arctan2(fb.by-fb.ay , fb.bx-fb.ax)
        fb.th4 = np.arctan2(fb.b0y-fb.by , fb.b0x-fb.bx)
        fb.th3start = fb.th3
        fb.th4start = fb.th4
        fb.axstart = fb.ax
        fb.aystart = fb.ay

    def SwapLinks(self):
        fb=self
        (fb.ax, fb.ay, fb.bx, fb.by)= (fb.bx, fb.by, fb.ax, fb.ay)
        (fb.th3, fb.th4) = (fb.th4, fb.th3)
        fb.SolvePositions()



    def SolvePositions(self):
        def func(vals):
            th3,th4 = vals
            xerror=L1*np.cos(th1)+L2*np.cos(th2)+ \
                    L3*np.cos(th3)+L4*np.cos(th4)
            yerror=L1*np.sin(th1)+L2*np.sin(th2)+ \
                    L3*np.sin(th3)+L4*np.sin(th4)
            return xerror, yerror

        L1,L2,L3,L4=self.L1,self.L2,self.L3,self.L4
        th1=self.th1
        th2=self.th2
        (self.th3,self.th4) = fsolve(func,[self.th3,self.th4])
        return

class Geometry():

    def __init__(self):
        # payload data
        self.shape = []
        self.linestylename = None
        self.linestyle = None


class LineStyle():

    def __init__(self):
        self.name = None
        self.rgb = None
        self.stipple = None
        self.width = None

class Construction():
    def __init__(self):
        self.a=0
        self.amid = 0
        self.afinal = 0
        self.b = 0
        self.bmid = 0
        self.bfinal = 0


class FourbarAnimator():
    def __init__(self):
        self.title = None
        self.distance_unit = None
        self.fourbar = None
        self.linestyles = []
        self.payloads = []
        self.boundaries = []
        self.forcepoints = []
        self.tracepoints = []
        self.tracepointLocations = []
        self.tracepointAngles = []
        self.tracepointJoints = []
        self.framenum = 0
        self.p1 = None
        self.p2 = None
        self.p3 = None
        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        self.allowDistortion = False


        self.numberOfAnimationFrames  = 120
        self.AnimDelayTime = 0.01
        self.AnimReverse = True
        self.AnimRepeat = False
        self.AnimReset = False

        self.construction = None
        self.constructionOn=False
        self.reverseAngle = False
        self.showLinks=True
        self.showTracepoints = True



    def ProcessFileData(self, data):
        # from the array of strings, fill the wing dictionary
        self.fourbar = Fourbar()
        fb = self.fourbar
        self.construction = Construction()

        for line in data:  # loop over all the lines

            cells = line.strip().replace('(','').replace(')','').split(',')
            keyword = cells[0].strip().lower()

            if keyword == 'title': self.title = cells[1].replace("'", "")
            if keyword == 'distance_unit': self.dist_unit = cells[1].replace("'", "")

            if keyword == 'window':
                self.xmin, self.xmax, self.ymin, self.ymax = \
                    (float(cells[1]), float(cells[2]), float(cells[3]), float(cells[4]))

            if keyword == 'connections':
                fb.ax, fb.ay, fb.bx, fb.by = \
                    (float(cells[1]), float(cells[2]), float(cells[3]), float(cells[4]))

            if keyword == 'forcepoint':
                name = cells[1].strip()
                fpX = float(cells[2])
                fpY = float(cells[3])
                self.forcepoints.append([name, fpX, fpY])

            if keyword == 'tracepoint':
                name = cells[1].strip()
                fpX = float(cells[2])
                fpY = float(cells[3])
                self.tracepoints.append([name, fpX, fpY])

            if keyword == 'linestyle':
                ls = LineStyle()
                ls.name = cells[1].strip()
                ls.rgb = (float(cells[2]), float(cells[3]), float(cells[4]))
                ls.width = float(cells[5])
                self.linestyles.append(ls)

            if keyword == 'positions':
                self.p1=(float(cells[1]), float(cells[2]))
                self.p2=(float(cells[3]), float(cells[4]), float(cells[5]))
                self.p3=(float(cells[6]), float(cells[7]), float(cells[8]))

            if keyword == 'payload':
                g = Geometry()
                g.name = cells[1]
                g.linestylename = cells[2].strip()

                for i in range(3,len(cells),2): #loop over all point pairs
                    g.shape.append((float(cells[i]), float(cells[i+1])))
                self.payloads.append(g)

            if keyword == 'boundary':
                g = Geometry()
                g.name = cells[1]
                g.linestylename = cells[2].strip()

                for i in range(3,len(cells),2): #loop over all point pairs
                    g.shape.append((float(cells[i]), float(cells[i+1])))
                self.boundaries.append(g)

            if keyword == 'showlinks':
                if cells[1].lower().strip() == "false":
                    self.showLinks = False
                else:
                    self.showLinks = True

            if keyword == 'reversed':
                if cells[1].lower().strip() == "true":
                    self.reverseAngle = True
                else:
                    self.reverseAngle = False

        self.ConnectFourbarData()


    def ConnectFourbarData(self):
        #connect drawing objects  with linestyle information
        default = LineStyle()
        default.name = 'default'
        default.rgb = (0,0,0)
        default.width = 1.0
        for  pl in self.payloads:
            for  ls  in self.linestyles:
                if pl.linestylename == ls.name:
                    pl.linestyle = ls
            if pl.linestyle is None: pl.linestyle = default
        for  b in self.boundaries:
            for  ls  in self.linestyles:
                if b.linestylename == ls.name:
                    b.linestyle = ls
            if b.linestyle is None: b.linestyle = default

        self.DesignFourbar()
        #self.fourbar.LengthsAndAngles()

    def SetToStartingPosition(self):
        #reset the mechanism to the starting position
        fb = self.fourbar
        fb.th2 = fb.theta2start
        fb.th3 = fb.th3start
        fb.th4 = fb.th4start
        fb.SolvePositions()
        fb.ax=fb.a0x+fb.L2*np.cos(fb.th2)
        fb.ay=fb.a0y+fb.L2*np.sin(fb.th2)
        fb.bx=fb.ax+fb.L3*np.cos(fb.th3)
        fb.by=fb.ay+fb.L3*np.sin(fb.th3)


    def DrawPicture(self):
        # this is what actually draws the picture
        # using data to control what is drawn

        if self.fourbar is None: return  #nothing to draw

        fb=self.fourbar

        # Draw the fourbar links

        if self.showLinks:
            #link a0-a
            glColor3f(0.0, 0.0, 00)
            glLineWidth(6)
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            # use GL_LINE for drawing a series of disconnected lines
            glVertex2f(fb.a0x, fb.a0y)
            glVertex2f(fb.ax, fb.ay)
            glEnd()

            #link b0-b
            glColor3f(0.9, 0.9, 0.25)
            glLineWidth(6)
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            # use GL_LINE for drawing a series of disconnected lines
            glVertex2f(fb.b0x, fb.b0y)
            glVertex2f(fb.bx, fb.by)
            glEnd()

            # draw the fourbar joints
            jointsize = float(self.xmax - self.xmin)/100.0
            glLineWidth(1.5)
            glColor3f(0.0, 0, 0)
            gl2DCircle(fb.a0x, fb.a0y, jointsize, fill=True)
            gl2DCircle(fb.b0x, fb.b0y, jointsize, fill=True)
            glColor3f(1.0, 1, 1)
            gl2DCircle(fb.a0x, fb.a0y, 0.8*jointsize, fill=True)
            gl2DCircle(fb.b0x, fb.b0y, 0.8*jointsize, fill=True)
            glColor3f(0.8, 1, 0.5)
            gl2DCircle(fb.ax, fb.ay, 0.5*jointsize, fill=True)
            gl2DCircle(fb.bx, fb.by, 0.5*jointsize, fill=True)

        if self.showTracepoints:
            # draw the tracepoints
            jointsize = float(self.xmax - self.xmin)/100.0
            glLineWidth(1.5)
            glColor3f(0, 1, 1)
            for  tp in range(len(self.tracepoints)):
                x = self.tracepoints[tp][1]
                y = self.tracepoints[tp][2]
                newpoint = transform([[x, y]], fb.ax, fb.ay, (fb.th3 - fb.th3start),
                                               fb.axstart,fb.aystart)
                gl2DCircle(newpoint[0][0],newpoint[0][1] ,jointsize*0.7, fill=True)

            # #draw the moving payload
            # rgb = p.linestyle.rgb
            # glLineWidth(1.5)
            # glColor3f(rgb[0],rgb[1],rgb[2])
            # glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            # pref=self.p1
            # pnew = self.p2
            # for point in transform(p.shape,fb.ax,fb.ay,(fb.th3-fb.th3start),
            #                        fb.axstart,fb.aystart):
            #     glVertex2f(point[0], point[1])
            # glEnd()
            #


        # draw the payloads
        for p in self.payloads:

            glColor3f(0.85,0.85,0.85)
            #draw the untransformed payload (first postion)
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            for point in p.shape:
                glVertex2f(point[0], point[1])
            glEnd()

            #draw the payload in the second postion
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            pref=self.p1
            pnew = self.p2
            for point in transform(p.shape,pnew[0],pnew[1],pnew[2]*np.pi/180,pref[0],pref[1]):
                glVertex2f(point[0], point[1])
            glEnd()

            #draw the payload in the third postion
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            pref=self.p1
            pnew = self.p3
            for point in transform(p.shape,pnew[0],pnew[1],pnew[2]*np.pi/180,pref[0],pref[1]):
                glVertex2f(point[0], point[1])
            glEnd()


            #draw the moving payload
            rgb = p.linestyle.rgb
            glLineWidth(1.5)
            glColor3f(rgb[0],rgb[1],rgb[2])
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            pref=self.p1
            pnew = self.p2
            for point in transform(p.shape,fb.ax,fb.ay,(fb.th3-fb.th3start),
                                   fb.axstart,fb.aystart):
                glVertex2f(point[0], point[1])
            glEnd()


        # draw the boundaries
        for b in self.boundaries:
            rgb = b.linestyle.rgb
            glLineWidth(1.5)
            glColor3f(rgb[0],rgb[1],rgb[2])
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            for point in b.shape:
                glVertex2f(point[0], point[1])
            glEnd()

        # draw the construction lines
        if self.constructionOn is True:
            cs = self.construction
            rgb = [1,0.7,0.7]
            glLineWidth(1.5)
            glColor3f(rgb[0],rgb[1],rgb[2])
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            glVertex2f(fb.a0x, fb.a0y)
            glVertex2f(cs.a[0],cs.a[1])
            glVertex2f(cs.amid[0],cs.amid[1])
            glVertex2f(fb.a0x, fb.a0y)
            glVertex2f(cs.afinal[0],cs.afinal[1])
            glVertex2f(cs.amid[0],cs.amid[1])
            glEnd()

            glColor3f(1,1,1)
            glEnable(GL_LINE_STIPPLE)  # enable a dashed line
            glLineStipple(1, 0x00FF)  # the value for dashed lines
            glBegin(GL_LINE_STRIP)  # begin drawing connected lines
            glVertex2f((cs.a[0]+cs.amid[0])/2,(cs.a[1]+cs.amid[1])/2)
            glVertex2f(fb.a0x, fb.a0y)
            glVertex2f((cs.afinal[0]+cs.amid[0])/2,(cs.afinal[1]+cs.amid[1])/2)
            glEnd()
            glDisable(GL_LINE_STIPPLE)  # disable the dashed line

            circlesize = float(self.xmax - self.xmin)/100.0
            gl2DCircle(cs.a[0],cs.a[1], circlesize, fill=True)
            gl2DCircle(cs.amid[0],cs.amid[1],circlesize,fill= True)
            gl2DCircle(cs.afinal[0],cs.afinal[1],circlesize,fill= True)
            gl2DCircle(fb.a0x, fb.a0y,circlesize,fill= True)
            glColor3f(0,0,0)
            gl2DCircle(fb.a0x, fb.a0y,0.8*circlesize,fill= True)


        return


    def PrepareNextAnimationFrameData(self, frame, nframes):
        fb=self.fourbar
        self.framenum = frame
        if frame == 0: #use the original theta data
            fb.th2 = fb.theta2start
            fb.th3 = fb.th3start
            fb.th4 = fb.th4start
        fb.th2 = fb.theta2start + (fb.theta2end-fb.theta2start) * frame/(nframes-1)
        fb.SolvePositions()
        fb.ax=fb.a0x+fb.L2*np.cos(fb.th2)
        fb.ay=fb.a0y+fb.L2*np.sin(fb.th2)
        fb.bx=fb.ax+fb.L3*np.cos(fb.th3)
        fb.by=fb.ay+fb.L3*np.sin(fb.th3)


    def DesignFourbar(self):
        fb=self.fourbar
        cs = self.construction
        pref =self.p1
        pmid = self.p2
        pfinal = self.p3

        a = [fb.ax, fb.ay]
        amid = transform(a,pmid[0],pmid[1],pmid[2]*np.pi/180,pref[0],pref[1])
        afinal = transform(a,pfinal[0],pfinal[1],pfinal[2]*np.pi/180,pref[0],pref[1])
        a0 = bisect(a,amid,afinal)
        (fb.a0x, fb.a0y) = (a0[0],a0[1])
        fb.theta2start = np.arctan2(a[1]-a0[1], a[0]-a0[0])
        fb.theta2mid = np.arctan2(amid[1]-a0[1], amid[0]-a0[0])
        fb.theta2end = np.arctan2(afinal[1]-a0[1], afinal[0]-a0[0])
        deltamid = fb.theta2mid - fb.theta2start
        deltafinal = fb.theta2end - fb.theta2start
        if np.sign(deltamid) != np.sign(deltafinal):
            if fb.theta2end < 0:
                fb.theta2end += 2*np.pi
            else:
                fb.theta2end -= 2*np.pi
        #end if sign mismatch

        # mag = np.abs(fb.theta2end - fb.theta2start)
        # mag1 = np.abs((fb.theta2end - 2*np.pi) - fb.theta2start)
        # mag2 = np.abs((fb.theta2end + 2*np.pi) - fb.theta2start)
        # if mag1 < mag:
        #     fb.theta2end -= 2*np.pi
        #     mag = mag1
        # if mag2 < mag:
        #     fb.theta2end += 2*np.pi
        #     mag = mag2

        if self.reverseAngle == True:
           fb.theta2end -= 2*np.pi

        b = [fb.bx, fb.by]
        bmid = transform(b,pmid[0],pmid[1],pmid[2]*np.pi/180,pref[0],pref[1])
        bfinal = transform(b,pfinal[0],pfinal[1],pfinal[2]*np.pi/180,pref[0],pref[1])
        b0 = bisect(b,bmid,bfinal)
        (fb.b0x, fb.b0y) = (b0[0],b0[1])

        cs.a=a
        cs.amid = amid
        cs.afinal = afinal
        cs.b = b
        cs.bmid = bmid
        cs.bfinal = bfinal

        fb.LengthsAndAngles()


def bisect(p1,p2,p3):

    def func(vals): #the "root function" for use  with fsolve()
        k1,k2 = vals
        error1 = (c12[0] + k1*r12[0]) - (c13[0] + k2*r13[0])
        error2 = (c12[1] + k1*r12[1]) - (c13[1] + k2*r13[1])
        return (error1, error2)

    #Centers
    c12=np.array([p2[0]+p1[0],p2[1]+p1[1]])/2
    c13=np.array([p3[0]+p1[0],p3[1]+p1[1]])/2
    #Rotated vectors
    r12=np.array([-(p2[1]-p1[1]),p2[0]-p1[0]])
    r13=np.array([-(p3[1]-p1[1]),p3[0]-p1[0]])
    #call fsolve to get k-values that produce an intersection
    k1,k2 = fsolve(func,(1,1))
    bx = c12[0] + k1*r12[0]
    by = c12[1] + k1*r12[1]
    return [bx,by]


def transform(points,xnew,ynew, theta = 0, xref = 0, yref = 0):
    rotate = np.array([[np.cos(theta), np.sin(theta)],
                       [-np.sin(theta), np.cos(theta)]])
    return np.matmul(np.array(points) - (xref,yref),rotate)+ (xnew,ynew)


