# standard PyQt5 imports
import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QEvent

# standard OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from OpenGL_2D_class import gl2D, gl2DText, gl2DCircle

# the ui created by Designer and pyuic
from DataAnimation_ui import Ui_Dialog

# import the Problem Specific class
from DataProcessorClass_1 import FourbarDesign

import numpy as np


class main_window(QDialog):
    def __init__(self):
        super(main_window, self).__init__()
        self.ui = Ui_Dialog()
        # setup the GUI
        self.ui.setupUi(self)

        # define any data (including object variables) your program might need
        self.myfourbar = None
        self.filename = 'Landing Gear Design.txt'

        # create and setup the GL window object
        self.setupGLWindows()

        # and define any Widget callbacks (buttons, etc) or other necessary setup
        self.assign_widgets()

        # show the GUI
        self.show()

    def assign_widgets(self):  # callbacks for Widgets on your GUI
        self.ui.pushButton_Exit.clicked.connect(self.ExitApp)
        self.ui.pushButton_Animate.clicked.connect(self.StartAnimation)
        self.ui.pushButton_StopAnimation.clicked.connect(self.StopAnimation)
        self.ui.pushButton_PauseResumeAnimation.clicked.connect(self.PauseResumeAnimation)
        self.ui.horizontalSlider_zoom.valueChanged.connect(self.glZoomSlider)
        self.ui.horizontalSlider_frame.valueChanged.connect(self.glFrameSlider)
        self.ui.checkBox_Dragging.stateChanged.connect(self.DraggingOnOff)
        self.ui.checkBox_Construction.stateChanged.connect(self.ConstructionOnOff)
        self.ui.checkBox_ReverseInput.stateChanged.connect(self.ReverseInputAngle)
        self.ui.checkBox_hideLinks.stateChanged.connect(self.HideLinks)
        self.ui.checkBox_showTracepoints.stateChanged.connect(self.ShowTracepoints)
        self.ui.pushButton_GetFourbar.clicked.connect(self.GetFourbar)
        self.ui.pushButton_SwapDrivenLink.clicked.connect(self.SwapLinks)
        #self.ui.pushButton_SaveTorqueFactorFile.clicked.connect(self.SaveTorqueFactorFile)
        self.ui.pushButton_TracepointFile.clicked.connect(self.SaveTracepointFile)

    def GetFourbar(self,filename = False):

        if filename is False:
        # get the filename using the OPEN dialog
            filename = QFileDialog.getOpenFileName()[0]
            if len(filename) == 0:
                no_file()
                return
        self.ui.textEdit_filename.setText(filename)
        app.processEvents()
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        # Read the file
        f1 = open(filename, 'r')  # open the file for reading
        data = f1.readlines()  # read the entire file as a list of strings
        f1.close()  # close the file  ... very important

        self.myfourbar=FourbarDesign()

        #try:
        self.myfourbar.processFourbarData(data)
        fb=self.myfourbar
        self.glwindow1.setViewSize(fb.xmin,fb.xmax,fb.ymin,fb.ymax, allowDistortion=False)

        QApplication.restoreOverrideCursor()
        self.UpdateTextBoxes()
        self.glwindow1.glUpdate()
        #except:
            #QApplication.restoreOverrideCursor()
            #bad_file()
        # if len( fb.forcepoints ) == 0:
        #     self.ui.groupBox_TorqueFactors.setEnabled(False)
        # else:
        #     self.ui.groupBox_TorqueFactors.setEnabled(True)

        self.ui.horizontalSlider_frame.setValue(0)
        self.ui.horizontalSlider_zoom.setValue(100)
        self.setAngleSliderAndText()
        if self.myfourbar.showLinks == True:
            self.ui.checkBox_hideLinks.setChecked(False)
        else:
            self.ui.checkBox_hideLinks.setChecked(True)

        if self.myfourbar.reverseAngle == True:
            self.ui.checkBox_ReverseInput.setChecked(True)
        else:
            self.ui.checkBox_ReverseInput.setChecked(False)

        if self.myfourbar.showTracepoints == True:
            self.ui.checkBox_showTracepoints.setChecked(True)
        else:
            self.ui.checkBox_showTracepoints.setChecked(False)
        if self.myfourbar.showLinks:
            self.StartStopDragging(True)


# Widget callbacks start here

    def SaveTorqueFactorFile(self):
        self.ui.pushButton_SaveTorqueFactorFile.setEnabled(False)
        filename = self.ui.textEdit_filename.toPlainText()
        npoints = int(self.ui.N_precision.text())

        self.myfourbar.WriteTorqueFactorFile(npoints, filename.replace(".txt"," -Torque Factors.txt"))

        self.ui.pushButton_SaveTorqueFactorFile.setEnabled(True)



    def SaveTracepointFile(self):
        self.ui.pushButton_TracepointFile.setEnabled(False)
        filename = self.ui.textEdit_filename.toPlainText()
        npoints = 360

        self.myfourbar.WriteTracepointsFile(filename.replace(".txt"," -Tracepoints.txt"))

        self.ui.pushButton_TracepointFile.setEnabled(True)


    def SwapLinks(self):
        if self.myfourbar is None: return
        self.myfourbar.ConfigureAnimationFrame(0, 120)
        self.myfourbar.fourbar.SwapLinks()
        self.myfourbar.DesignFourbar()
        if self.myfourbar.showLinks:
            self.StartStopDragging(True)
        self.UpdateTextBoxes()
        self.glwindow1.glUpdate()
        self.ui.horizontalSlider_frame.setValue(0)
        self.setAngleSliderAndText()

    def UpdateTextBoxes(self):
        fb=self.myfourbar.fourbar
        self.ui.Position_A0.setText('{:.3f}, {:.3f}'.format(fb.a0x,fb.a0y) )
        self.ui.Position_A.setText('{:.3f}, {:.3f}'.format(fb.ax,fb.ay) )
        self.ui.Position_B0.setText('{:.3f}, {:.3f}'.format(fb.b0x,fb.b0y) )
        self.ui.Position_B.setText('{:.3f}, {:.3f}'.format(fb.bx, fb.by))
        self.ui.Starting_Angle.setText('{:.1f} deg.'.format(fb.theta2start*180/np.pi) )
        self.ui.Ending_Angle.setText('{:.1f} deg.'.format(fb.theta2end*180/np.pi))

    def glZoomSlider(self):  # I used a slider to control GL zooming
        zoomval = float((self.ui.horizontalSlider_zoom.value()) / 200 + .5)
        self.glwindow1.glZoom(zoomval)  # set the zoom value
        self.glwindow1.glUpdate()  # update the GL image


    def glFrameSlider(self):  # I used a slider to control manual animation
        frameval = int(self.ui.horizontalSlider_frame.value())
        self.myfourbar.ConfigureAnimationFrame(frameval, 120)
        self.glwindow1.glUpdate()  # update the GL image
        self.setAngleSliderAndText()
        if frameval == 0:
            if self.myfourbar.showLinks:
                self.StartStopDragging(True)
        else:
            self.StartStopDragging(False)


    def setAngleSliderAndText(self):
        self.ui.textbox_Input_angle.setText('{:.1f}'.format(self.myfourbar.fourbar.th2*180/np.pi))
        th4val = 180 + self.myfourbar.fourbar.th4*180/np.pi
        while th4val > 180:
            th4val -= 360
        while th4val < -180:
            th4val += 360
        self.ui.textbox_Follower_angle.setText('{:.1f}'.format(th4val))



    def DraggingOnOff(self):  # used a checkbox to Enable GL Dragging
        if self.ui.checkBox_Dragging.isChecked():  # start dragging
            self.StartStopDragging(True)  # StartStopDragging is defined below
        else:  # stop dragging
            self.StartStopDragging(False)

    def ConstructionOnOff(self):  # used a checkbox to Enable drawing of construction lines
        if self.ui.checkBox_Construction.isChecked():  # it is on
            self.myfourbar.constructionOn = True  #
        else:  # stop
            self.myfourbar.constructionOn = False  #
        self.glwindow1.glUpdate()

    def HideLinks(self):  # used a checkbox to Enable drawing of construction lines
        if self.ui.checkBox_hideLinks.isChecked():  # it is on
            self.myfourbar.showLinks = False  #
            if self.myfourbar.showLinks == False:
                self.StartStopDragging(False)
        else:  # stop
            self.myfourbar.showLinks = True #
            if self.myfourbar.showLinks == True:
                self.StartStopDragging(True)

        self.glwindow1.glUpdate()


    def ShowTracepoints(self):  # used a checkbox to Enable drawing of construction lines
        if self.ui.checkBox_showTracepoints.isChecked():  # it is on
            self.myfourbar.showTracepoints = True  #
        else:  # stop
            self.myfourbar.showTracepoints = False  #
        self.glwindow1.glUpdate()


    def ReverseInputAngle(self):  # used a checkbox to Enable drawing of construction lines
        if self.ui.checkBox_ReverseInput.isChecked():  # it is on
            self.myfourbar.reverseAngle = True  #
        else:  # stop
            self.myfourbar.reverseAngle = False  #
        self.myfourbar.DesignFourbar()
        self.glwindow1.glUpdate()

    def StartAnimation(self):  # a button to start GL Animation
        self.glwindow1.glStartAnimation(self.AnimationCallback, 120,
                                    reverse=True, repeat=False, reset=True,
                                    RestartDraggingCallback=self.StartStopDragging,
                                    reverseDelayTime=0.5)

    def StopAnimation(self):  # a button to Stop GL Animati0n
        self.glwindow1.glStopAnimation()

    def PauseResumeAnimation(self):  # a button to Resume GL Animation
        self.glwindow1.glPauseResumeAnimation()

    def ExitApp(self):
        app.exit()

    # Essential, but only if using mouse information with GL
    def eventFilter(self, source, event):  # allow GL to handle Mouse Events
        self.glwindow1.glHandleMouseEvents(event)  # let GL handle the event
        return super(QDialog, self).eventFilter(source, event)

    # Setup OpenGL Drawing and Viewing
    def setupGLWindows(self):  # setup all GL windows
        # send it the   GL Widget     and the drawing Callback function
        self.glwindow1 = gl2D(self.ui.openGLWidget, self.DrawingCallback)

        # set the drawing space:    xmin  xmax  ymin   ymax
        self.glwindow1.setViewSize(0,1,0,1, allowDistortion=False)

        # Optional: Setup GL Mouse Functionality
        self.ui.openGLWidget.installEventFilter(self)  # to read mouse events
        self.ui.openGLWidget.setMouseTracking(True)  # to enable mouse events

        # OPTIONAL: to display the mouse location  - the name of the TextBox
        self.glwindow1.glMouseDisplayTextBox(self.ui.MouseLocation)


    def DrawingCallback(self):
        # this is what actually draws the picture
        if self.myfourbar is None: return
        self.myfourbar.DrawPicture()  # drawing is done by the DroneCatcher object

        # if using dragging, let GL show dragging handles
        self.glwindow1.glDraggingShowHandles()


    def AnimationCallback(self, frame, nframes):
        # calculations handled by DroneCapture class
        self.myfourbar.ConfigureAnimationFrame(frame, nframes)
        self.ui.horizontalSlider_frame.setValue(frame)
        # the next line is absolutely required for pause, resume, stop, etc !!!
        app.processEvents()
        pass

    def draggingCallback(self, x, y, draglist, index):
        # calculations handled by DroneCapture class
        self.myfourbar.DraggingListItemChanged(x, y, draglist, index)
        self.UpdateTextBoxes()

    def StartStopDragging(self, start):  # needs problem specific customization!

        if start is True:
            draglist = self.myfourbar.CreateDraggingList()
            near = 0.2  # define an acceptable mouse distance for dragging
            handlesize = (self.myfourbar.xmax - self.myfourbar.xmin)/100
            near = handlesize*handlesize
            self.glwindow1.glStartDragging(self.draggingCallback, draglist, near,
                                           handlesize=handlesize, handlewidth=1, handlecolor=[1, 0, 0])
            self.ui.checkBox_Dragging.setChecked(True)
        elif start is False:
            self.glwindow1.glStopDragging()
            self.ui.checkBox_Dragging.setChecked(False)



def no_file():
    msg = QMessageBox()
    msg.setText('There was no file selected')
    msg.setWindowTitle("No File")
    retval = msg.exec_()
    return None

def bad_file():
    msg = QMessageBox()
    msg.setText('Unable to process the selected file')
    msg.setWindowTitle("Bad File")
    retval = msg.exec_()
    return None


if __name__ == "__main__":
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    main_win = main_window()
    if main_win.filename is  not  None:
        main_win.GetFourbar(main_win.filename)
    sys.exit(app.exec_())
