import numpy as np
from scipy.optimize import fsolve
from math import sin, cos, atan2, sqrt, pi

#------- calculation of static forces in the Drone Launcher Deployment linkage -----
#------- this might also be useful for other fourbar linkages, but you must confirm it!!!!
#Link-12 angle -1.340 degrees

Fy=850 #in the freebody and equations, DOWN was POSITIVE!!!

# non-moving points 1 and 3
x1, y1 = 4.260, 13.538
x3, y3 = 96.757, -4.723

#moving points  2  4  and F
x2, y2 =3.844,    105.604
x4, y4 = 107.371,     98.758
xf, yf = -32.582,    102.549

#------------------ no changes needed after this line ---------------

#a useful conversion
DtoR = pi/180.0
RtoD = 1/DtoR

#define the 4 angles that changes as the mechanism moves
th12 = atan2(y2-y1,x2-x1);    th34 = atan2(y4-y3,x4-x3)
th24 = atan2(y4-y2,x4-x2); th2F = atan2(yf-y2,xf-x2)
th31 = atan2(y1-y3,x1-x3)
#print(th12*RtoD,th34*RtoD,th24*RtoD,th2F*RtoD,th31*RtoD)

#define constant lengths and angles and the applied force
# (they don't change as the mechanism moves)
L12 = sqrt( (x2-x1)**2 + (y2-y1)**2); L34 = sqrt( (x4-x3)**2 + (y4-y3)**2)
L24 = sqrt( (x4-x2)**2 + (y4-y2)**2); L31 = sqrt( (x1-x3)**2 + (y1-y3)**2)
L2F =sqrt( (xf-x2)**2 + (yf-y2)**2) ; L3Fx = xf - x3
#print(L12,L34,L24,L31, L2F, L3Fx)

def equations(guesses):
    M,f1x,f1y,f2x,f2y,f3x,f3y,f4x,f4y = guesses
    return  [ # a List of all the EXPRESSIONS to drive to zero
              # for an n-equation and n-unknown problem

        f1x + f2x,  #forces and moments on link 12
        f1y + f2y,
        M - f2x*L12*sin(th12) + f2y*L12*cos(th12),

        f3x + f4x,  #forces and moments on link 34
        f3y + f4y,
        -f4x*L34*sin(th34) + f4y*L34*cos(th34),

        -f2x-f4x,  #forces and moments on link 24
        -f2y - f4y - Fy,
        -Fy*L2F*cos(th2F) +f4x*L24*sin(th24) -f4y*L24*cos(th24)
    ]
answer = fsolve(equations, [0,0,0,0,0,0,0,0,0])
# print(answer)
# print()

M,f1x,f1y,f2x,f2y,f3x,f3y,f4x,f4y = answer
print(" M = ", M)
print(" f1x = ",f1x, " f1y = ", f1y)
print(" f2x = ",f2x, " f2y = ", f2y)
print(" f3x = ",f3x, " f3y = ", f3y)
print(" f4x = ",f4x, " f4y = ", f4y)
print()
print("Sanity check - Sum Fx,  Sum Fy, Sum Moments about Joint 3")

# Now do an important SANITY CHECK - necessary but not sufficient!!!
# Looking at only EXTERNAL forces, check the sum of all external forces
# and the sum moments at JOINT-3.  All three answer should be ZERO
print(-Fy + f1y + f3y)
print(f1x + f3x)
print( M - f1x*L31*sin(th31) + f1y*L31*cos(th31) - Fy*L3Fx )
print("")

def alignForcesToLink(p1x,p1y,p2x,p2y,fx,fy):
    link = np.array([p2x-p1x, p2y-p1y],dtype=float) #use numpy to use the dot product below
    force = np.array([fx,fy],dtype=float)
    linkperp = np.array([-(p2y-p1y), p2x-p1x]) #rotate 90 degrees ccw
    linkmag = sqrt(link[0]**2 + link[1]**2)
    forcemag = sqrt(fx**2 + fy**2)
    forceAlong = np.dot(force,link)/linkmag #use vector dot product to get the component
    forcePerpendicular = np.dot(force,linkperp)/linkmag #use vector dot product to get the component
    return forceAlong, forcePerpendicular

forceAlong,forcePerpendicular = alignForcesToLink(x1,y1,x2,y2,f2x,f2y) #force 2 on link 12
print(f"link12 length is: {L12:.2f}")
print(f"force2 aligned with the link12: {forceAlong:.1f} and the force perpendicular is: {forcePerpendicular:.1f}")
print(f"the perpendicular force's moment about point 1 is: {L12*forcePerpendicular:.2f} ")

forceAlong,forcePerpendicular = alignForcesToLink(x3,y3,x4,y4,f4x,f4y) #force 4 on link 34
print(f"link34 length is: {L34:.2f}")
print(f"force4 aligned with the link34: {forceAlong:.1f} and the force perpendicular is: {forcePerpendicular:.1f}")


pass






