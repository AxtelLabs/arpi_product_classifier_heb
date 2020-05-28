"""
---
HEB ARPI (Alestra Robot Product Inspector)
Alestra april 2020
Axtellabs
Data Science Team -
Israel Melendez
Hernan Martinez
Alondra Sanchez

IoT team
Jesus Briones
Uziel Alonso
---

VEGETABLE AND FRUIT VISUAL CLASSIFIER

The current program utilizes computer vision algorithms
to detect and classify fruits and vegetables from a 
specific selection (20 categories). When something is
detected on the scene (using template matching), the
program uses a CNN (Convolutional Neural Network) to 
classify the image. This result is then presented on
another page, showing a picture of the 3 most probable
products. 
The most probable product of the 3 is shown
as a bigger picture along with its name and PLU (Product
code). The user is then allowed to return to the main 
screen or to proceed to a search page.


"""

# Import libraries
import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter import ttk
import PIL.Image, PIL.ImageTk
import cv2
from playsound import playsound
import uuid
import os
import sys
###from azure.iot.device import IoTHubDeviceClient # <-- Final GUI change
#sys.path.insert(0,r'C:\Users\AxtelUser\Documents\ARPI\avir-cloud-azure-client')
import ScheduleTask
### import SendDeviceToCloudMessage as D2C # <-- Final GUI change
import warnings # Used to remove tensorflow warnings
import predict_new_single
from tensorflow.keras.models import load_model
#from keras.models import load_model
from test import GetDict
import platform # platform.system() prints Linux, Darwin (Mac) or Windows.
import time
import pandas as pd



# Establish the environment variables
arpi_node_connection_string = os.getenv('ARPI_NODE_CONNECTION_STRING')
ARPI_path_image_folder = os.getenv('IMG_PATH')
schedule_action = os.getenv('ARPI_SCHEDULE_ACTION')
schedule_arguments = os.getenv('ARPI_SCHEDULE_ARGUMENTS')


# Establish the client strings
### client = IoTHubDeviceClient.create_from_connection_string(arpi_node_connection_string) # <-- Final GUI change
# Declare schedule task
### ScheduleTask.ScheduleTask().CreateTask(schedule_action,schedule_arguments,"11:31:00") # <-- Final GUI change


# Define the type of dash to be used ("\" or "/") depending on OS. # <-- Final GUI change
if platform.system() == "Windows":
    dash = "\\"
else:
    dash = "/"
# Establish main path for files # <-- Final GUI change
path = dash.join(os.path.realpath(__file__).split(dash)[:-1]) + dash
print(f"[INFO] Main path is: {path}")

# Load product database from csv and save it as a dataframe
data = pd.read_csv(path + "AbrilHEB.csv")
data = pd.DataFrame(data)

# Load template
template = cv2.imread(path + "imgs" + dash + "template.png", 0) # <-- Final GUI change
template = cv2.resize(template, (1920,1080))

# Declare global variables
global namescd
global DictReturn # This dictionary contains the name, plu and image path of top 3 products
suggestions = ["potato","mango","banana"]
names = []
DictReturn= {
    0:{"name":"avocado", "PLU":"2661", "path":path + "imgs/avocado.png"},
    1:{"name":"pineapple", "PLU":"2671", "path":path + "imgs/pineapple.png"},
    2:{"name":"onion", "PLU":"2677", "path":path + "imgs/onion.png"}
}

# warnings.filterwarnings('ignore')
model = load_model(path + "local_SGD_test_300.model")
warnings.resetwarnings()


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        global suggestions
        self.attributes("-toolwindow",1)
        self.resizable(0,0)
        self.HEIGHT = self.winfo_screenheight() # <-- Final GUI change
        self.WIDTH = self.winfo_screenwidth() # <-- Final GUI change
        # Establish window size (it will be equal to the screen size)
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.overrideredirect(1)
        self.focus_set() # <-- move focus to this widget

        # Keyboard Page-Control using binds
        #self.bind("<Escape>", lambda e: self.close_window()) # <-- close everything
        self.bind("<Escape>", lambda e: self.close_window()) # <-- close everything
        self.bind("p", lambda f: self.changeSuggestions()) # <-- change
        self.bind("1", lambda a: self.show_frame("PageOne"))
        self.bind("2", lambda a: self.show_frame("PageTwo"))
        self.bind("3", lambda a: self.show_frame("PageThree"))
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (PageOne, PageTwo, PageThree):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("PageOne")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
    def close_window(self):
        '''Exit program'''
        #sys.exit(0)
        self.destroy()


    def changeSuggestions(self):
        global suggestions
        suggestions = ["avocado","purpleonion","redapple"]

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        global suggestions
        global DictReturn
        global names 
        global percentages

        self.HEIGHT = controller.HEIGHT # <--
        self.WIDTH = controller.WIDTH

        #suggestions = ["potato","mango","banana"]
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Detection Variables
        self.counter = 0
        self.ctrLimit = 50
        self.newProdFlg = False
        self.i = 1
        template = cv2.imread(path + "imgs/template.png", 0)
        self.template = template
        self.detThreshold = .88
        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()
        self.vid = MyVideoCapture(0) # <-- Changed in final version

        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open(path + "imgs/transparent.png")
        #self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)

        self.img= self.img.resize((int(WIDTH/7.5),int(HEIGHT/22)), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open(path + "imgs/background.jpg")
        self.img2= self.img2.resize((3840,2160), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)
        self.can2 = tk.Canvas(self, width=WIDTH/2, height=HEIGHT, bg='#000000')
        self.can2.place(relx=0.5, rely=0 ,relwidth=1, relheight=1)

        # Videostream container 
        self.vidCont= tk.Button(self.can2, background= "#555555", command = lambda: self.controller.show_frame("PageTwo"))
        self.vidCont.place(relx=.058, rely= .17, width=640 , height=480)

        # Insert fruit background
        self.can2.create_image(500,500, image=self.img2)

        # Create detection status image container (may change image to indicate detection)
        self.firstImg = self.can2.create_image(100,100, image=self.img)
        
        # Positive Detection Icon (PNG)
        self.img3= PIL.Image.open(path + "imgs/detection.png")
        self.img3= self.img3.resize((120,120), PIL.Image.ANTIALIAS)
        self.img3= PIL.ImageTk.PhotoImage(self.img3)

        # HEB logo
        self.logoRaw= PIL.Image.open(path + "imgs/logo.png")
        self.logoRaw= self.logoRaw.resize((210,70), PIL.Image.ANTIALIAS)
        self.logo= PIL.ImageTk.PhotoImage(self.logoRaw)
        self.label1= tk.Label(self, background= "#ffffff", image= self.logo)
        self.label1.place (relx=-0.03, rely=.02, relwidth= .2, relheight=.07)
        self.label1.image=self.logo

        # Animated Instructions
        self.anim1Raw= PIL.Image.open(path + "imgs/animation1.jpg")
        self.anim1Raw= self.anim1Raw.resize((350,350), PIL.Image.ANTIALIAS)
        self.anim1= PIL.ImageTk.PhotoImage(self.anim1Raw)
        self.label3= tk.Label(self, background= "#FFFFFF", image= self.anim1) 
        self.label3.place (relx=0.12, rely=.15, relwidth= .26, relheight=.48)
        self.label3.image=self.anim1

        # Instructions 1
        self.inst1Raw= PIL.Image.open(path + "imgs/inst1.png")
        self.inst1Raw= self.inst1Raw.resize((750,100), PIL.Image.ANTIALIAS)
        self.inst1= PIL.ImageTk.PhotoImage(self.inst1Raw)
        self.label2= tk.Label(self, background= "#FFFFFF", image= self.inst1) 
        self.label2.place (relx=0.01, rely=.1, relwidth= .45, relheight=.15)
        self.label2.image=self.inst1

        # Instructions 2
        self.inst2Raw= PIL.Image.open(path + "imgs/inst2.png")
        self.inst2Raw= self.inst2Raw.resize((750,200), PIL.Image.ANTIALIAS)
        self.inst2= PIL.ImageTk.PhotoImage(self.inst2Raw)
        self.label4= tk.Label(self.can, background= "#FFFFFF", image= self.inst2) 
        self.label4.place (relx=0.01, rely=.63, relwidth= .45, relheight=.2)
        self.label4.image=self.inst2

        # Instructions 3 & 4 : Detection message
        self.inst3Raw= PIL.Image.open(path + "imgs/inst3.png")
        self.inst3Raw= self.inst3Raw.resize((300,100), PIL.Image.ANTIALIAS)
        self.inst3= PIL.ImageTk.PhotoImage(self.inst3Raw)
        self.detMsg = self.can2.create_image(300,110, image=self.inst3)
        self.inst4Raw= PIL.Image.open(path + "imgs/inst4.png")
        self.inst4Raw= self.inst4Raw.resize((300,100), PIL.Image.ANTIALIAS)
        self.inst4= PIL.ImageTk.PhotoImage(self.inst4Raw)

        # Instructions 5
        self.inst5Raw= PIL.Image.open(path + "imgs/inst5.png")
        self.inst5Raw= self.inst5Raw.resize((700,300), PIL.Image.ANTIALIAS)
        self.inst5= PIL.ImageTk.PhotoImage(self.inst5Raw)
        self.lastMsg = self.can2.create_image(450,780, image=self.inst5)

        # Update app info
        self.toggleVar = False
        self.update()

    def update(self, *args, **kwargs):
        global names
        global DictReturn
        ret, frame = self.vid.get_frame()
        #newImg = cv2.resize(frame, (640,420))
        newImg = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        self.toggleVar = not self.toggleVar
        
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            res1 = cv2.matchTemplate(gray,self.template,cv2.TM_CCOEFF_NORMED)
            if res1 < self.detThreshold:
                self.counter += 1
                self.can2.itemconfig(self.firstImg, image = self.img3)
                self.can2.itemconfig(self.detMsg, image = self.inst4)
            else:
                self.can2.itemconfig(self.firstImg, image = self.img)
                self.can2.itemconfig(self.detMsg, image = self.inst3)
                self.counter = 0
            if self.counter > self.ctrLimit:
                if self.newProdFlg == False:
                    playsound(path + "press.wav", block=False)
                    self.newProdFlg = True
                    Uid = uuid.uuid1()
                    pathN3 = str(Uid) + "_"+str(self.i)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    i = self.i
                    print("ARPI PATH: ", ARPI_path_image_folder)
                    pathN2 = os.path.join(ARPI_path_image_folder,'full')
                    print("pathn2: ", pathN2)
                    pathN = os.path.join(pathN2,pathN3+".png")
                    print("pathn: ", pathN)
                    cv2.imwrite(pathN, frame)
                    names, percentages, namesStr = predict_new_single.singleInference(pathN, model, i) #<-- Temporarily disabled
                    self.i += 1
                    # D2C.SendDeviceToCloudMessage().iothub_client_send_telemetry(client, pathN3, names[0], round(percentages[0],6),names[1], round(percentages[1],6),names[2], round(percentages[2],6),1)
                    DictReturn = GetDict(names) #<-- Temporarily disabled
                    #print(DictReturn)
                    self.controller.frames["PageTwo"].DictReturn = DictReturn #<-- Temporarily disabled
                    self.controller.frames["PageTwo"].updateImgs() #<-- Temporarily disabled
                    self.controller.show_frame("PageTwo") #<-- Temporarily disabled
                    #self.counter = 0
                else:
                    pass
            else:
                self.newProdFlg = False

        if self.toggleVar == True:
            pass
        else:
            pass

        self.vidCont.configure(image=newImg)
        self.vidCont.image = newImg
        self.delay = 15
        self.after(self.delay, self.update)



class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        global suggestions
        global names
        global DictReturn
        global percentages

     
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        Uid = uuid.uuid1()
        i = 1
        pathN = str(Uid) + str(i) + ".png"
        self.suggestions = names
        
        self.DictReturn = DictReturn


        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()

        self.HEIGHT = controller.HEIGHT # <-- Final GUI change
        self.WIDTH = controller.WIDTH # <-- Final GUI change

        self.path  = path + "imgs/"
        # label = tk.Label(self, text="This is page 1", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        # button = tk.Button(self, text="Go to the start page",
        #                    command=lambda: controller.show_frame("PageOne"))
        # button.pack()

        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open(path + "imgs/transparent.png")
        self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open(path + "imgs/background.jpg")
        self.img2= self.img2.resize((3840,2160), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)
        self.can2 = tk.Canvas(self, width=WIDTH/2, height=HEIGHT, bg='#000000')
        self.can2.place(relx=0.5, rely=0 ,relwidth=1, relheight=1)

        # Insert fruit background
        self.can2.create_image(500,500, image=self.img2)

        # HEB logo
        self.logoRaw= PIL.Image.open(path + "imgs/logo.png")
        self.logoRaw= self.logoRaw.resize((210,70), PIL.Image.ANTIALIAS)
        self.logo= PIL.ImageTk.PhotoImage(self.logoRaw)
        self.label1= tk.Label(self, background= "#ffffff", image= self.logo)
        self.label1.place (relx=-0.03, rely=.02, relwidth= .2, relheight=.07)
        self.label1.image=self.logo

        # Instructions 1 P2
        self.uno= PIL.Image.open(path + "imgs/select.PNG")
        self.uno= self.uno.resize((750,220), PIL.Image.ANTIALIAS)
        self.unore=PIL.ImageTk.PhotoImage(self.uno)
        self.label4= tk.Label(self.can, background="#FFFFFF", image= self.unore)
        self.label4.place(relx=0.02, rely=0.12 ,relwidth=0.4, relheight=.16)
        self.label4.image= self.unore      

        # Animated Instructions P2
        self.anim1Raw= PIL.Image.open(path + "imgs/animation2.png")
        self.anim1Raw= self.anim1Raw.resize((580,380), PIL.Image.ANTIALIAS)
        self.anim1= PIL.ImageTk.PhotoImage(self.anim1Raw)
        self.label3= tk.Label(self, background= "#FFFFFF", image= self.anim1) 
        self.label3.place (relx=0.12, rely=.35, relwidth= .3, relheight=.33)
        self.label3.image=self.anim1

        # Instructions 2 P2
        self.dos= PIL.Image.open(path + "imgs/instructions2P2.png")
        self.dos= self.dos.resize((550,140), PIL.Image.ANTIALIAS)
        self.dosre=PIL.ImageTk.PhotoImage(self.dos)
        self.label4= tk.Label(self.can, background="#FFFFFF", image= self.dosre)
        self.label4.place(relx=0.051, rely=0.65,relwidth=0.45, relheight=.20)
        self.label4.image= self.dosre

        # Main Suggestion
        self.option1= PIL.Image.open(self.DictReturn[0]["path"])
        self.option1= self.option1.resize((270,270), PIL.Image.ANTIALIAS)
        self.option1re=PIL.ImageTk.PhotoImage(self.option1)
        self.label5= tk.Button(self, background="#ffffff", image= self.option1re)
        self.label5.place(relx=0.62, rely=0.04 ,relwidth=0.14, relheight=.24)
        self.label5.image= self.option1re
        self.resultInfo= tk.Label(self, background="#ffffff", text=self.DictReturn[0]["name"] + " \n " + self.DictReturn[0]["PLU"],font = ("Helvetica","21"))
        self.resultInfo.place(relx=0.760, rely=0.04 ,relwidth=0.12, relheight=.24)
        self.resultInfo.image= self.option1re

        # Suggestion 1 Image
        self.option2= PIL.Image.open(self.DictReturn[0]["path"])
        self.option2= self.option2.resize((200,200), PIL.Image.ANTIALIAS)
        self.option2re=PIL.ImageTk.PhotoImage(self.option2)
        self.label6= tk.Button(self, background="#ffffff", image= self.option2re, command= lambda: self.changeImg(0))
        self.label6.place(relx=0.61, rely=0.35 ,relwidth=0.08, relheight=.14)
        self.label6.image= self.option2re

        # Suggestion 2 Image
        self.option3= PIL.Image.open(self.DictReturn[1]["path"])
        self.option3= self.option3.resize((200,200), PIL.Image.ANTIALIAS)
        self.option3re= PIL.ImageTk.PhotoImage(self.option3)
        self.label7= tk.Button(self, background="#ffffff", image= self.option3re, command= lambda: self.changeImg(1))
        self.label7.place(relx=0.72, rely=0.35,relwidth=0.08, relheight=.14)
        self.label7.image= self.option3re

        # Suggestion 3 Image
        self.option4= PIL.Image.open(self.DictReturn[2]["path"])
        self.option4= self.option4.resize((200,200), PIL.Image.ANTIALIAS)
        self.option4re= PIL.ImageTk.PhotoImage(self.option4)
        self.label8= tk.Button(self, background="#ffffff", image= self.option4re, command= lambda: self.changeImg(2))
        self.label8.place(relx=0.83, rely=0.35,relwidth=0.08, relheight=.14)
        self.label8.image= self.option4re

        # Instructions 3 P2
        self.dos= PIL.Image.open(path + "imgs/instructions3P2.png")
        self.dos= self.dos.resize((550,130), PIL.Image.ANTIALIAS)
        self.dosre=PIL.ImageTk.PhotoImage(self.dos)
        self.lastMsg = self.can2.create_image(500,800, image=self.dosre)

        # Finish button
        self.finish= PIL.Image.open(path + "imgs/terminar.png")
        self.finish= self.finish.resize((780,90), PIL.Image.ANTIALIAS)
        self.finishre=PIL.ImageTk.PhotoImage(self.finish)
        self.button5= tk.Button(self, background="#ffffff", image= self.finishre, command=lambda: self.controller.show_frame("PageOne"))
        self.button5.place(relx=0.6, rely=0.55 ,relwidth=0.33, relheight=.08)
        self.button5.image= self.finishre


        # Search button
        self.search= PIL.Image.open(path + "imgs/buscar_producto.png")
        self.search= self.search.resize((380,70), PIL.Image.ANTIALIAS)
        self.searchre=PIL.ImageTk.PhotoImage(self.search)
        self.button6= tk.Button(self, background="#ffffff", image= self.searchre, command=lambda: self.controller.show_frame("PageThree"))
        self.button6.place(relx=0.66, rely=0.85 ,relwidth=0.20, relheight=.06)
        self.button6.image= self.finishre
        

    def updateImgs(self):
        """
        Update the main suggestion (bigger image) as well as the 
        small suggestion images.
        """
        # Main Suggestion
        ## Image
        self.option1= PIL.Image.open(self.DictReturn[0]["path"])
        self.option1= self.option1.resize((270,270), PIL.Image.ANTIALIAS)
        self.option1re=PIL.ImageTk.PhotoImage(self.option1)
        self.label5.configure(image=self.option1re)
        self.label5.image= self.option1re
        ## Text
        self.resultInfo.configure(text=self.DictReturn[0]["name"] + " \n " + self.DictReturn[0]["PLU"], font = ("Helvetica","21") )
        self.resultInfo.text= (self.DictReturn[0]["name"] + " \n " + self.DictReturn[0]["PLU"])
        self.resultInfo.font = ("Helvetica","21")

        # Suggestion 1
        self.option2= PIL.Image.open(self.DictReturn[0]["path"])
        self.option2= self.option2.resize((200,200), PIL.Image.ANTIALIAS)
        self.option2re=PIL.ImageTk.PhotoImage(self.option2)
        self.label6.configure(image=self.option2re)
        self.label6.image= self.option2re

        # Suggestion 2
        self.option3= PIL.Image.open(self.DictReturn[1]["path"])
        self.option3= self.option3.resize((200,200), PIL.Image.ANTIALIAS)
        self.option3re= PIL.ImageTk.PhotoImage(self.option3)
        self.label7.configure(image=self.option3re)
        self.label7.image= self.option3re

        # Suggestion 3
        self.option4= PIL.Image.open(self.DictReturn[2]["path"])
        self.option4= self.option4.resize((200,200), PIL.Image.ANTIALIAS)
        self.option4re= PIL.ImageTk.PhotoImage(self.option4)
        self.label8.configure(image=self.option4re)
        self.label8.image= self.option4re

    def changeImg(self,imgNo):

        self.option1= PIL.Image.open(self.DictReturn[imgNo]["path"])
        self.option1= self.option1.resize((270,270), PIL.Image.ANTIALIAS)
        self.option1re=PIL.ImageTk.PhotoImage(self.option1)

        self.label5.configure(image=self.option1re)
        self.label5.image = self.option1re
        newText = self.DictReturn[imgNo]["name"] + " \n " + self.DictReturn[imgNo]["PLU"]
        self.resultInfo.configure(text=newText)

    def testPrint(self):
        print("Test successful")


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        global suggestions
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.data = pd.read_csv("AbrilHEB.csv")
        self.data = pd.DataFrame(self.data)
        self.HEIGHT = controller.HEIGHT # <-- Final GUI change
        self.WIDTH = controller.WIDTH # <-- Final GUI change
        self.equation = tk.StringVar()
        self.returnCounter = 0
        self.returnLimit = 15000
        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()
        self.path = path + "imgs/"
        self.searchResults = tk.StringVar()
        self.searchResults = ""
        
        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open(path + "imgs/transparent.png")
        self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open(path + "imgs/background.jpg")
        self.img2= self.img2.resize((3840,2160), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)

        # Background canvas (red component)
        self.can2 = tk.Canvas(self, width=WIDTH, height=2*(HEIGHT)/3, bg='#F83E16')
        self.can2.place(relx=0, rely=1/8 ,relwidth=1, relheight=1)

        # Keyboard canvas
        self.can3 = tk.Canvas(self, width=WIDTH, height=(HEIGHT)/2, bg='#ffffff')
        self.can3.place(relx=0, rely=1/2 ,relwidth=1, relheight=.5)


        Dis_entry = tk.Entry(self.can2,state= 'readonly',textvariable = self.equation, font = ("Helvetica","14"))
        Dis_entry.place(relx=0.08, rely=.15 ,relwidth=.4, relheight=.05)

        self.searchBox = tk.Label(self, background="#ffffff", text = self.searchResults, font = ("Helvetica","14"))
        self.searchBox.place(relx=0.55, rely=.14 ,relwidth=.4, relheight=.34)


        
        self.exp = " "
        yPadVal = 10
        xPadVal = 10
        # Keybaord body - ROW 1
        q = tk.Button(self.can3,text = 'Q' ,font=("Helvetica","18"), width = int(8), height = int(3), command = lambda : self.press('Q'))
        q.grid(row = 1 , column = 0, ipadx = xPadVal , ipady = yPadVal)

        w = tk.Button(self.can3,text = 'W' , font=("Helvetica","18"), width = int(8), height = int(3), command = lambda : self.press('W'))
        w.grid(row = 1 , column = 1, ipadx = xPadVal , ipady = yPadVal)

        E = tk.Button(self.can3,text = 'E' ,font=("Helvetica","18"), width = int(8), height = int(3), command = lambda : self.press('E'))
        E.grid(row = 1 , column = 2, ipadx = xPadVal , ipady = yPadVal)

        R = tk.Button(self.can3,text = 'R' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('R'))
        R.grid(row = 1 , column = 3, ipadx = xPadVal , ipady = yPadVal)

        T = tk.Button(self.can3,text = 'T' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('T'))
        T.grid(row = 1 , column = 4, ipadx = xPadVal , ipady = yPadVal)

        Y = tk.Button(self.can3,text = 'Y' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('Y'))
        Y.grid(row = 1 , column = 5, ipadx = xPadVal , ipady = yPadVal)

        U = tk.Button(self.can3,text = 'U' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('U'))
        U.grid(row = 1 , column = 6, ipadx = xPadVal , ipady = yPadVal)

        I = tk.Button(self.can3,text = 'I' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('I'))
        I.grid(row = 1 , column = 7, ipadx = xPadVal , ipady = yPadVal)

        O = tk.Button(self.can3,text = 'O' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('O'))
        O.grid(row = 1 , column = 8, ipadx = xPadVal , ipady = yPadVal)

        P = tk.Button(self.can3,text = 'P' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('P'))
        P.grid(row = 1 , column = 9, ipadx = xPadVal , ipady = yPadVal)


        # Keybaord body - ROW 2
        A = tk.Button(self.can3,text = 'A' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('A'))
        A.grid(row = 2 , column = 0, ipadx = xPadVal , ipady = yPadVal)
        

        S = tk.Button(self.can3,text = 'S' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('S'))
        S.grid(row = 2 , column = 1, ipadx = xPadVal , ipady = yPadVal)

        D = tk.Button(self.can3,text = 'D' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('D'))
        D.grid(row = 2 , column = 2, ipadx = xPadVal , ipady = yPadVal)

        F = tk.Button(self.can3,text = 'F' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('F'))
        F.grid(row = 2 , column = 3, ipadx = xPadVal , ipady = yPadVal)

        G = tk.Button(self.can3,text = 'G' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('G'))
        G.grid(row = 2 , column = 4, ipadx = xPadVal , ipady = yPadVal)

        H = tk.Button(self.can3,text = 'H' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('H'))
        H.grid(row = 2 , column = 5, ipadx = xPadVal , ipady = yPadVal)

        J = tk.Button(self.can3,text = 'J' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('J'))
        J.grid(row = 2 , column = 6, ipadx = xPadVal , ipady = yPadVal)

        K = tk.Button(self.can3,text = 'K' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('K'))
        K.grid(row = 2 , column = 7, ipadx = xPadVal , ipady = yPadVal)

        L = tk.Button(self.can3,text = 'L' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('L'))
        L.grid(row = 2 , column = 8, ipadx = xPadVal , ipady = yPadVal)

        Ñ = tk.Button(self.can3,text = 'Ñ' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('Ñ'))
        Ñ.grid(row = 2 , column = 9, ipadx = xPadVal , ipady = yPadVal)

        # enter = tk.Button(self.can3,text = 'Enter' , width = int(20), height = int(8), command = None)
        # enter.grid(row = 2, column = 10, ipadx = 50 , ipady = 10)

        # Keybaord body - ROW 3
        Z = tk.Button(self.can3,text = 'Z' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('Z'))
        Z.grid(row = 3 , column = 0, ipadx = xPadVal , ipady = yPadVal)


        X = tk.Button(self.can3,text = 'X' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('X'))
        X.grid(row = 3 , column = 1, ipadx = xPadVal , ipady = yPadVal)


        C = tk.Button(self.can3,text = 'C' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('C'))
        C.grid(row = 3 , column = 2, ipadx = xPadVal , ipady = yPadVal)


        V = tk.Button(self.can3,text = 'V' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('V'))
        V.grid(row = 3 , column = 3, ipadx = xPadVal , ipady = yPadVal)

        B = tk.Button(self.can3, text= 'B' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('B'))
        B.grid(row = 3 , column = 4 , ipadx = xPadVal , ipady = yPadVal)


        N = tk.Button(self.can3,text = 'N' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('N'))
        N.grid(row = 3 , column = 5, ipadx = xPadVal , ipady = yPadVal)


        M = tk.Button(self.can3,text = 'M' , font=("Helvetica","18"),width = int(8), height = int(3), command = lambda : self.press('M'))
        M.grid(row = 3 , column = 6, ipadx = xPadVal , ipady = yPadVal)

        clear = tk.Button(self.can3,text = '<- Retroceso' ,font=("Helvetica","16"), width = int(140), height = int(3), command = lambda : self.clear())
        clear.place(relx=0.78, rely=0.01,relwidth=0.2, relheight=.15)

        enter = tk.Button(self.can3,text = "ENTER" ,font=("Helvetica","16"), width = int(140), height = int(3), command = lambda : self.action())
        enter.place(relx=0.78, rely=0.2,relwidth=0.2, relheight=.25)

        space = tk.Button(self.can3,text = 'ESPACIO' ,font=("Helvetica","18"), width = int(140), height = int(3), command = lambda : self.press(' '))
        space.place(relx=0.05, rely=0.7,relwidth=0.6, relheight=.2)

        # space = tk.Button(self.can3,text = 'Space' , width = int(140), height = int(3), command = lambda : self.press(' '))
        # space.grid(row = 5 , columnspan=5, ipadx = 180 , ipady = 5)

        # Insert fruit background
        # self.can2.create_image(500,500, image=self.img2)

        # # Keyboard
        # self.can3 = tk.Canvas(self, width=self.winfo_screenwidth(), height=int(self.winfo_screenheight()/3), bg='#ffffff')
        # self.can3.place(relx=0, rely=int(2/3) ,relwidth=1, relheight=int(1/3))

        # # Keyboard
        # self.can3 = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        # self.can3.place(relx=0, rely=2/3 ,relwidth=1, relheight=1)

        # HEB logo
        self.logoRaw= PIL.Image.open(path + "imgs/logo.png")
        self.logoRaw= self.logoRaw.resize((210,70), PIL.Image.ANTIALIAS)
        self.logo= PIL.ImageTk.PhotoImage(self.logoRaw)
        self.label1= tk.Label(self, background= "#ffffff", image= self.logo)
        self.label1.place (relx=-0.03, rely=.02, relwidth= .2, relheight=.07)
        self.label1.image=self.logo

        # Finish button
        self.finish= PIL.Image.open(path + "imgs/terminar.png")
        self.finish= self.finish.resize((780,90), PIL.Image.ANTIALIAS)
        self.finishre=PIL.ImageTk.PhotoImage(self.finish)
        self.button5= tk.Button(self.can3, background="#ffffff", image= self.finishre, command=lambda: self.controller.show_frame("PageOne"))
        self.button5.place(relx=0.7, rely=0.8 ,relwidth=0.28, relheight=.1)
        self.button5.image= self.finishre
        self.update()

    def press(self, num):
        # pass
        # global exp
        self.exp=self.exp + str(num)
        self.equation.set(self.exp)
    # end 
    def action(self):
        #exp = " Next Line : "
        #print(equation, type(equation))
        self.searchResults = ""
        self.equation.set(self.exp)
        print(self.equation.get()) 
        x = self.equation.get()
        df1 = self.data[self.data['Producto'].str.contains(x,case=False)] 

        print(df1)
        list1 = df1.iloc[:,0].values
        list2 = df1.iloc[:,1].values
        
        for i in range(len(list1)):
            self.searchResults = self.searchResults + str(list1[i]) + " " + str(list2[i]) + "\n"
            print(list1[i], "            ", list2[i])
        self.searchBox.configure(text = self.searchResults)
    def clear(self):
        self.searchResults = ""
        self.searchBox.configure(text = self.searchResults)
        self.exp = " "
        self.equation.set(self.exp)

    def update(self, *args, **kwargs):

        #self.returnCounter = self.returnCounter + 10
        if self.returnCounter >= self.returnLimit:
            self.returnCounter = 0
            self.controller.show_frame("PageOne")
        self.delay = 10
        self.after(self.delay, self.update)
class MyVideoCapture:
    def __init__(self, video_source= 0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
       # self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
       # self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
   
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
    app = App()
    app.mainloop()

else:
    pass
#sys.exit("Program End")




