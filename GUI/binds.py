from tkinter import * 
import PIL.Image, PIL.ImageTk
import cv2
import platform
import os

def onObjectClick(event):                  
    print ('Clicked', event.x, event.y, event.widget)
    print (event.widget.find_closest(event.x, event.y))   

# Define the type of dash to be used ("\" or "/") depending on OS. # <-- Final GUI change
if platform.system() == "Windows":
    dash = "\\"
else:
    dash = "/"
# Establish main path for files # <-- Final GUI change
path = dash.join(os.path.realpath(__file__).split(dash)[:-1]) + dash
print(f"[INFO] Main path is: {path}")


root = Tk()
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
#root.overrideredirect(1)
root.focus_set() # <-- move focus to this widget
canv = Canvas(root, width=root.winfo_screenheight(), height=root.winfo_screenheight())
obj1 = canv.create_text(50, 30, text='Click me one')
obj2 = canv.create_text(50, 70, text='Click me two')

# Positive Detection Icon (PNG)
img= PIL.Image.open(path + "imgs/detection.png")
img= img.resize((120,120), PIL.Image.ANTIALIAS)
img= PIL.ImageTk.PhotoImage(img)

Img = canv.create_image(100,100, image=img)

canv.tag_bind(obj1, '<Button-1>', onObjectClick)        
canv.tag_bind(obj2, '<Button-1>', onObjectClick)
canv.tag_bind(Img, '<Button-1>', onObjectClick)        
canv.pack()
root.mainloop()