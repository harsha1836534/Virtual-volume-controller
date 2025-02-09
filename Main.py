import cv2 as cv
import time
import numpy as np
import Hand_Tracking_module as htm
import math
import pycaw
from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
wcam,hcam=640,480
cap=cv.VideoCapture(0)
cap.set(3,wcam)
cap.set(4,hcam)
ptime=0
volbar=400
detector=htm.HandDetection()

# code to setup volume
devices=AudioUtilities.GetSpeakers()
interface=devices.Activate(IAudioEndpointVolume._iid_,CLSCTX_ALL,None)
volume=cast(interface,POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volumerange=volume.GetVolumeRange() #(-63.5, 0.0, 0.5) this is the volume range where 0 is higher volume and -63.5 is low 
#volume.SetMasterVolumeLevel(0,None)
minvol=volumerange[0]
maxvol=volumerange[1]
while True:
    success,img=cap.read()

    img=detector.findhands(img)
    lmlist=detector.findposition(img,draw=False)
    if len(lmlist)!=0:
        #print(lmlist[4],lmlist[8])
        x1,y1=lmlist[4][1],lmlist[4][2]
        x2,y2=lmlist[8][1],lmlist[8][2]
        cx,cy=(x1+x2)//2,(y1+y2)//2     #midpoint of the points x1,y1 and x2,y2
        cv.circle(img,(x1,y1),10,(255,0,0),-1)
        cv.circle(img,(x2,y2),10,(255,0,0),-1)
        cv.line(img,(x1,y1),(x2,y2),(255,0,255),2)
        cv.circle(img,(cx,cy),8,(255,0,0),-1)
        length=math.hypot(x2-x1,y2-y1)
        #cv.putText(img,str(int(length)),(cx+10,cy+10),cv.FONT_HERSHEY_COMPLEX,2,(255,0,0),3)
        #hand range is from 29 to 350
        #volume range is from -63.5 to 0
        #now using numpy we should convert the hand range to volume range
        vol=np.interp(length,[29,350],[minvol,maxvol]) # converting the length that is hand range to volume range 
        volbar=np.interp(length,[29,350],[400,150])
        volper=np.interp(length,[29,350],[0,100])
        #print(volume)
        volume.SetMasterVolumeLevel(vol,None)
        #cv.putText(img,f'volume:{int(vol)}',(10,70),cv.FONT_HERSHEY_PLAIN,2,(255,0,255),3)
        if length<=28:
            cv.circle(img,(cx,cy),10,(0,255,0),-1)
        cv.rectangle(img,(50,int(volbar)),(85,400),(0,255,0),-1)
        cv.putText(img,str(int(volper)),(40,140),cv.FONT_HERSHEY_DUPLEX,3,(255,0,0),2)
    ctime=time.time()
    fps=1/(ctime-ptime)
    ptime=ctime
    cv.putText(img,str(int(fps)),(40,50),cv.FONT_HERSHEY_SCRIPT_COMPLEX,1,(255,0,0),2)
    cv.imshow("Image",img)
    if cv.waitKey(2) & 0XFF==ord('q'):
        break
