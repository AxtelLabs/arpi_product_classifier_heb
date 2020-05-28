#Import imaging and system libraries 
from PIL import Image
import os.path, sys
import glob
import cv2
import random
from PIL import Image
import os.path, sys
import numpy
from playsound import playsound
import time
from feedback import App
#from preprocessing import tiles

#list1 = tiles(img)


font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (20,450)
fontScale              = 1
fontColor              = (0,0,255)
lineType               = 2

counter = 0
ctrLimit = 80
newProdFlg = False

# Import background template
template = cv2.imread('template.png', 0)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,720)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
i = 1
while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    res1 = cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
   # res1 = str(res1)
    # cv2.putText(frame,res1, 
    #     bottomLeftCornerOfText, 
    #     font, 
    #     fontScale,
    #     fontColor,
    #     lineType)

    if res1 < 0.90:
        playsound('press.wav', block=False)
        #print("Nuevo producto en bascula")
        print("Detecting something...")
        counter += 1
    else:
        counter = 0
    if counter > ctrLimit:
        if newProdFlg == False:
            playsound('press.wav', block=False)

            print("Nuevo producto en bascula")
            newProdFlg = True
            cv2.imwrite("C:\\imgs\\full\\image" + str(i) + ".png", frame)
            i += 1
            #app = App("holi")
        else:
            pass
        cv2.putText(frame,"Product Detected", 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            lineType)
    else:
        newProdFlg = False
    cv2.imshow('window',frame)




    inputkey = cv2.waitKey(1) & 0xFF
    if inputkey == ord('q'):
        break
    elif inputkey == ord('s'):
         cv2.imwrite("template.png", frame)
         print("Template saved.")
cap.release()
cv2.destroyAllWindows()
