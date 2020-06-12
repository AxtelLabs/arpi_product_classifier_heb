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
from azure.iot.device import IoTHubDeviceClient 
#sys.path.insert(0,r'C:\Users\AxtelUser\Documents\ARPI\avir-cloud-azure-client')
import ScheduleTask
import SendDeviceToCloudMessage as D2C
import warnings # Used to remove tensorflow warnings
import predict_new_single
import predict_new_product
from tensorflow.keras.models import load_model
#from keras.models import load_model
from test import GetDict
import platform # platform.system() prints Linux, Darwin (Mac) or Windows.
import time
import pandas as pd
import getList
import tkstuff_4



# Establish the environment variables
arpi_node_connection_string = os.getenv('ARPI_NODE_CONNECTION_STRING')
ARPI_name = os.getenv("ACC_NAME")
ARPI_path_image_folder = os.getenv('IMG_PATH')
print(ARPI_path_image_folder) 
# schedule_action = os.getenv('ARPI_SCHEDULE_ACTION') # Needed for image upload but not for telemetry
#scheKCdule_arguments = os.getenv('ARPI_SCHEDULE_ARGUMENTS') # Needed for image upload but not for telemetry


# Establish the client strings
client = IoTHubDeviceClient.create_from_connection_string(arpi_node_connection_string)
# Declare schedule task
### ScheduleTask.ScheduleTask().CreateTask(schedule_action,schedule_arguments,"11:31:00")


# Define the type of dash to be used ("\" or "/") depending on OS. # <-- Final GUI change
if platform.system() == "Windows":
    dash = "\\"
else:
    dash = "/"
# Establish main path for files # <-- Final GUI change
path = dash.join(os.path.realpath(__file__).split(dash)[:-1]) + dash
imgPath = path + "imgs" + dash
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
    0:{"name":"aguacate", "PLU":"2661", "path":path + "imgs/aguacate.png"},
    1:{"name":"platano", "PLU":"2671", "path":path + "imgs/platano.png"},
    2:{"name":"cebolla_blanca", "PLU":"2677", "path":path + "imgs/cebolla_blanca.png"}
}

# warnings.filterwarnings('ignore')
model = load_model(path + "local_SGD_test_300.model")
model2 = load_model(path + "local_SGD_PRODUCT_200e.model")
warnings.resetwarnings()

def process_image(image,width,height):
    processedImg = PIL.Image.open(image)
    processedImg = processedImg.resize((width,height), PIL.Image.ANTIALIAS)
    processedImg = PIL.ImageTk.PhotoImage(processedImg)

    return processedImg





class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        global suggestions
        global pathN
        global percentages
        global names
        global feedback
        names = ["None", "None", "None"]
        percentages = [0,0,0]
        pathN = "00023_0"
        feedback = "None"
        self.attributes("-toolwindow",1)
        self.resizable(0,0)
        self.HEIGHT = self.winfo_screenheight()
        self.WIDTH = self.winfo_screenwidth()
        print(self.HEIGHT,self.WIDTH)
        # Establish window size (it will be equal to the screen size)
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.overrideredirect(1)
        self.focus_set() # <-- move focus to this widget


        # Keyboard Page-Control using binds
        self.bind("<Escape>", lambda e: self.close_window()) 
        self.bind("p", lambda f: self.changeSuggestions())
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
        global namesStr

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
        self.detThreshold = .84
        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()
        self.vid = MyVideoCapture(1) # <-- Zchange
        self.newTemplate = None

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
        self.img2= self.img2.resize((2560,1440), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)
        self.can2 = tk.Canvas(self, width=WIDTH/2, height=HEIGHT, bg='#000000')
        self.can2.place(relx=0.5, rely=0 ,relwidth=1, relheight=1)

        # Videostream container 
        self.vidCont= tk.Button(self.can2, background= "#555555", command = lambda: self.controller.show_frame("PageTwo"),borderwidth=0)
        self.vidCont.place(relx=.09, rely= .17, width=640 , height=480)

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
        global pathN
        global percentages
        global client
        global feedback
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
            if (self.counter > self.ctrLimit):

                if self.newProdFlg == False:
                    # playsound(path + "press.wav", block=False) # Zchange
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
                    prod= predict_new_product.singleInference(pathN,model2,i)
                    # if prod[0] == "product":
                    names, percentages, namesStr = predict_new_single.singleInference(pathN, model, i)
                    print(f"[INFO] {names}") # Zchange
                    print(f"[INFO] {percentages}") # Zchange
                    print(f"[INFO] {namesStr}") # Zchange
                    self.i += 1
                    # D2C.SendDeviceToCloudMessage().iothub_client_send_telemetry(client, pathN3, names[0], round(percentages[0],6),names[1], round(percentages[1],6),names[2], round(percentages[2],6),1,feedback)
                    DictReturn = GetDict(names)
                    feedback = DictReturn[0]["PLU"]
                    print("--------")
                    print("[INFO] Dictionary to send:")
                    print(DictReturn)
                    # print("[INFO] Name of file:")
                    # print(pathN + "\n")
                    print("--------")
                    self.controller.frames["PageTwo"].DictReturn = DictReturn 
                    self.controller.frames["PageTwo"].updateImgs() 
                    # self.controller.show_frame("PageTwo") # Zchange 
                    # else:
                    #     pass

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
        global feedback
        global client

     
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


        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open(path + "imgs/transparent.png")
        self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open(path + "imgs/background.jpg")
        self.img2= self.img2.resize((2560,1440), PIL.Image.ANTIALIAS)
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
        self.label5= tk.Button(self, background="#ffffff", image= self.option1re,borderwidth=0)
        self.label5.place(relx=0.62, rely=0.04 ,relwidth=0.14, relheight=.24)
        self.label5.image= self.option1re
        self.resultInfo= tk.Label(self, background="#ffffff", text=self.DictReturn[0]["name"] + " \n " + self.DictReturn[0]["PLU"],font = ("Helvetica","21"))
        self.resultInfo.place(relx=0.760, rely=0.04 ,relwidth=0.12, relheight=.24)
        self.resultInfo.image= self.option1re

        # Suggestion 1 Image
        self.option2= PIL.Image.open(self.DictReturn[0]["path"])
        self.option2= self.option2.resize((200,200), PIL.Image.ANTIALIAS)
        self.option2re=PIL.ImageTk.PhotoImage(self.option2)
        self.label6= tk.Button(self, background="#ffffff", image= self.option2re, command= lambda: self.changeImg(0),borderwidth=0)
        self.label6.place(relx=0.61, rely=0.35 ,relwidth=0.08, relheight=.14)
        self.label6.image= self.option2re

        # Suggestion 2 Image
        self.option3= PIL.Image.open(self.DictReturn[1]["path"])
        self.option3= self.option3.resize((200,200), PIL.Image.ANTIALIAS)
        self.option3re= PIL.ImageTk.PhotoImage(self.option3)
        self.label7= tk.Button(self, background="#ffffff", image= self.option3re, command= lambda: self.changeImg(1),borderwidth=0)
        self.label7.place(relx=0.72, rely=0.35,relwidth=0.08, relheight=.14)
        self.label7.image= self.option3re

        # Suggestion 3 Image
        self.option4= PIL.Image.open(self.DictReturn[2]["path"])
        self.option4= self.option4.resize((200,200), PIL.Image.ANTIALIAS)
        self.option4re= PIL.ImageTk.PhotoImage(self.option4)
        self.label8= tk.Button(self, background="#ffffff", image= self.option4re, command= lambda: self.changeImg(2),borderwidth=0)
        self.label8.place(relx=0.83, rely=0.35,relwidth=0.08, relheight=.14)
        self.label8.image= self.option4re

        # Instructions 3 P2
        self.dos= PIL.Image.open(path + "imgs/instructions3P2.png")
        self.dos= self.dos.resize((550,130), PIL.Image.ANTIALIAS)
        self.dosre=PIL.ImageTk.PhotoImage(self.dos)
        self.lastMsg = self.can2.create_image(500,800, image=self.dosre)


        # Finish image
        self.finish= PIL.Image.open(path + "imgs/finish_button.png")
        self.finish= self.finish.resize((600,100), PIL.Image.ANTIALIAS)
        self.finishre=PIL.ImageTk.PhotoImage(self.finish)
        self.finishMsg = self.can2.create_image(500,640, image=self.finishre)
        # self.can2.tag_bind(self.finishMsg, '<Button-1>', lambda b: self.controller.show_frame("PageOne"))
        self.can2.tag_bind(self.finishMsg, '<Button-1>', lambda b: self.uploadData())

        # Search image
        self.search= PIL.Image.open(path + "imgs/search_button.png")
        self.search= self.search.resize((600,100), PIL.Image.ANTIALIAS)
        self.searchre=PIL.ImageTk.PhotoImage(self.search)
        self.searchMsg = self.can2.create_image(500,1000, image=self.searchre)
        self.can2.tag_bind(self.searchMsg, '<Button-1>', lambda b: self.controller.show_frame("PageThree"))        

    def uploadData(self):
        global DictReturn
        global names 
        global percentages
        global namesStr
        global feedback
        global pathN3
        global client
        # feedback = "onion"
        D2C.SendDeviceToCloudMessage().iothub_client_send_telemetry(client, pathN3, names[0], round(percentages[0],6),names[1], round(percentages[1],6),names[2], round(percentages[2],6),1,feedback)
        self.controller.show_frame("PageOne")

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
        global feedback
        feedback = self.DictReturn[imgNo]["PLU"]
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
        global DictReturn
        global suggestions
        global pathN3
        global client
        global feedback
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.data = pd.read_csv("AbrilHEB.csv")
        self.data = pd.DataFrame(self.data)
        self.HEIGHT = controller.HEIGHT # <-- Final GUI change
        self.WIDTH = controller.WIDTH # <-- Final GUI change
        self.equation = tk.StringVar(value="Inserte nombre del producto aquí...")
        self.returnCounter = 0
        self.returnLimit = 15000
        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()
        self.path = path + "imgs/"
        self.searchResults = tk.StringVar()
        self.searchResults2 = tk.StringVar()
        self.searchResults3 = tk.StringVar()
        self.exp = ""
        self.labelFlag = False
        self.DictReturn = DictReturn

        self.list_of_items = getList.getListOfItems()

        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open(path + "imgs/transparent.png")
        self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open(path + "imgs/background.jpg")
        self.img2= self.img2.resize((2560,1440), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)
        self.can2 = tk.Canvas(self, width=WIDTH/2, height=HEIGHT, bg='#000000')
        self.can2.place(relx=0.5, rely=0 ,relwidth=1, relheight=1)

        # Keyboard Canvas
        self.keyboardCanvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#D2D7DF')
        self.keyboardCanvas.place(relx=0.5, rely=(2/3) ,relwidth=.5, relheight=.4)


        # self.searchBox3 = tk.Label(self.can2, bg ="#D2D7DF", textvariable  = self.searchResults3, font = ("Helvetica","20"), anchor = "w")
        # self.searchBox3.place(relx=0.07, rely=.36 ,relwidth=.35, relheight=.07)

        ### KEYBOARD
        # Row 1
        self.keyWidth = 63
        self.keyHeight = 69

        ## Q
        # -- Images
        self.buttonQ = process_image(imgPath + "normal_buttons/q.png",self.keyWidth,self.keyHeight)
        self.buttonQ_pressed = process_image(imgPath + "normal_buttons/qp.png",self.keyWidth,self.keyHeight)
        self.lastMsgQ= self.keyboardCanvas.create_image(60,60, image=self.buttonQ)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgQ, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgQ, image = self.buttonQ))
        self.keyboardCanvas.tag_bind(self.lastMsgQ, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgQ, image = self.buttonQ_pressed, char = "Q" ))

        ## W
        # -- Images
        self.buttonW = process_image(imgPath + "normal_buttons/w.png",self.keyWidth,self.keyHeight)
        self.buttonW_pressed = process_image(imgPath + "normal_buttons/wp.png",self.keyWidth,self.keyHeight)
        self.lastMsgW= self.keyboardCanvas.create_image(130,60, image=self.buttonW)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgW, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgW, image = self.buttonW))
        self.keyboardCanvas.tag_bind(self.lastMsgW, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgW, image = self.buttonW_pressed, char = "W" ))

        ## E
        # -- Images
        self.buttonE = process_image(imgPath + "normal_buttons/e.png",self.keyWidth,self.keyHeight)
        self.buttonE_pressed = process_image(imgPath + "normal_buttons/ep.png",self.keyWidth,self.keyHeight)
        self.lastMsgE= self.keyboardCanvas.create_image(200,60, image=self.buttonE)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgE, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgE, image = self.buttonE))
        self.keyboardCanvas.tag_bind(self.lastMsgE, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgE, image = self.buttonE_pressed, char = "E" ))

        ## R
        # -- Images
        self.buttonR = process_image(imgPath + "normal_buttons/r.png",self.keyWidth,self.keyHeight)
        self.buttonR_pressed = process_image(imgPath + "normal_buttons/rp.png",self.keyWidth,self.keyHeight)
        self.lastMsgR= self.keyboardCanvas.create_image(270,60, image=self.buttonR)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgR, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgR, image = self.buttonR))
        self.keyboardCanvas.tag_bind(self.lastMsgR, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgR, image = self.buttonR_pressed, char = "R" ))

        ## T
        # -- Images
        self.buttonT = process_image(imgPath + "normal_buttons/t.png",self.keyWidth,self.keyHeight)
        self.buttonT_pressed = process_image(imgPath + "normal_buttons/tp.png",self.keyWidth,self.keyHeight)
        self.lastMsgT= self.keyboardCanvas.create_image(340,60, image=self.buttonT)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgT, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgT, image = self.buttonT))
        self.keyboardCanvas.tag_bind(self.lastMsgT, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgT, image = self.buttonT_pressed, char = "T" ))

        ## Y
        # -- Images
        self.buttonY = process_image(imgPath + "normal_buttons/y.png",self.keyWidth,self.keyHeight)
        self.buttonY_pressed = process_image(imgPath + "normal_buttons/yp.png",self.keyWidth,self.keyHeight)
        self.lastMsgY= self.keyboardCanvas.create_image(410,60, image=self.buttonY)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgY, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgY, image = self.buttonY))
        self.keyboardCanvas.tag_bind(self.lastMsgY, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgY, image = self.buttonY_pressed, char = "Y" ))

        ## U
        # -- Images
        self.buttonU = process_image(imgPath + "normal_buttons/u.png",self.keyWidth,self.keyHeight)
        self.buttonU_pressed = process_image(imgPath + "normal_buttons/up.png",self.keyWidth,self.keyHeight)
        self.lastMsgU= self.keyboardCanvas.create_image(480,60, image=self.buttonU)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgU, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgU, image = self.buttonU))
        self.keyboardCanvas.tag_bind(self.lastMsgU, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgU, image = self.buttonU_pressed, char = "U" ))

        ## I
        # -- Images
        self.buttonI = process_image(imgPath + "normal_buttons/i.png",self.keyWidth,self.keyHeight)
        self.buttonI_pressed = process_image(imgPath + "normal_buttons/ip.png",self.keyWidth,self.keyHeight)
        self.lastMsgI= self.keyboardCanvas.create_image(550,60, image=self.buttonI)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgI, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgI, image = self.buttonI))
        self.keyboardCanvas.tag_bind(self.lastMsgI, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgI, image = self.buttonI_pressed, char = "I" ))

        ## O
        # -- Images
        self.buttonO = process_image(imgPath + "normal_buttons/o.png",self.keyWidth,self.keyHeight)
        self.buttonO_pressed = process_image(imgPath + "normal_buttons/op.png",self.keyWidth,self.keyHeight)
        self.lastMsgO= self.keyboardCanvas.create_image(620,60, image=self.buttonO)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgO, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgO, image = self.buttonO))
        self.keyboardCanvas.tag_bind(self.lastMsgO, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgO, image = self.buttonO_pressed, char = "O" ))

        ## P
        # -- Images
        self.buttonP = process_image(imgPath + "normal_buttons/p.png",self.keyWidth,self.keyHeight)
        self.buttonP_pressed = process_image(imgPath + "normal_buttons/pp.png",self.keyWidth,self.keyHeight)
        self.lastMsgP= self.keyboardCanvas.create_image(690,60, image=self.buttonP)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgP, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgP, image = self.buttonP))
        self.keyboardCanvas.tag_bind(self.lastMsgP, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgP, image = self.buttonP_pressed, char = "P" ))

        ## DEL (BACKSPACE)
        # -- Images
        self.buttonDEL = process_image(imgPath + "normal_buttons/delete.png",158,69)
        self.buttonDEL_pressed = process_image(imgPath + "normal_buttons/deletep.png",158,69)
        self.lastMsgDEL= self.keyboardCanvas.create_image(823,60, image=self.buttonDEL)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgDEL, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgDEL, image = self.buttonDEL))
        self.keyboardCanvas.tag_bind(self.lastMsgDEL, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgDEL, image = self.buttonDEL_pressed, char = "DEL" ))       

        ### ROW 2
        ## A
        # -- Images
        self.buttonA = process_image(imgPath + "normal_buttons/a.png",self.keyWidth,self.keyHeight)
        self.buttonA_pressed = process_image(imgPath + "normal_buttons/ap.png",self.keyWidth,self.keyHeight)
        self.lastMsgA= self.keyboardCanvas.create_image(75,135, image=self.buttonA)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgA, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgA, image = self.buttonA))
        self.keyboardCanvas.tag_bind(self.lastMsgA, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgA, image = self.buttonA_pressed, char = "A" ))
        
        ## S
        # -- Images
        self.buttonS = process_image(imgPath + "normal_buttons/s.png",self.keyWidth,self.keyHeight)
        self.buttonS_pressed = process_image(imgPath + "normal_buttons/sp.png",self.keyWidth,self.keyHeight)
        self.lastMsgS= self.keyboardCanvas.create_image(145,135, image=self.buttonS)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgS, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgS, image = self.buttonS))
        self.keyboardCanvas.tag_bind(self.lastMsgS, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgS, image = self.buttonS_pressed, char = "S" ))

        ## D
        # -- Images
        self.buttonD = process_image(imgPath + "normal_buttons/d.png",self.keyWidth,self.keyHeight)
        self.buttonD_pressed = process_image(imgPath + "normal_buttons/dp.png",self.keyWidth,self.keyHeight)
        self.lastMsgD= self.keyboardCanvas.create_image(215,135, image=self.buttonD)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgD, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgD, image = self.buttonD))
        self.keyboardCanvas.tag_bind(self.lastMsgD, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgD, image = self.buttonD_pressed, char = "D" ))
        
        ## F
        # -- Images
        self.buttonF = process_image(imgPath + "normal_buttons/f.png",self.keyWidth,self.keyHeight)
        self.buttonF_pressed = process_image(imgPath + "normal_buttons/fp.png",self.keyWidth,self.keyHeight)
        self.lastMsgF= self.keyboardCanvas.create_image(285,135, image=self.buttonF)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgF, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgF, image = self.buttonF))
        self.keyboardCanvas.tag_bind(self.lastMsgF, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgF, image = self.buttonF_pressed, char = "F" ))

        ## G
        # -- Images
        self.buttonG = process_image(imgPath + "normal_buttons/g.png",self.keyWidth,self.keyHeight)
        self.buttonG_pressed = process_image(imgPath + "normal_buttons/gp.png",self.keyWidth,self.keyHeight)
        self.lastMsgG= self.keyboardCanvas.create_image(355,135, image=self.buttonG)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgG, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgG, image = self.buttonG))
        self.keyboardCanvas.tag_bind(self.lastMsgG, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgG, image = self.buttonG_pressed, char = "G" ))

        ## H
        # -- Images
        self.buttonH = process_image(imgPath + "normal_buttons/h.png",self.keyWidth,self.keyHeight)
        self.buttonH_pressed = process_image(imgPath + "normal_buttons/hp.png",self.keyWidth,self.keyHeight)
        self.lastMsgH= self.keyboardCanvas.create_image(425,135, image=self.buttonH)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgH, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgH, image = self.buttonH))
        self.keyboardCanvas.tag_bind(self.lastMsgH, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgH, image = self.buttonH_pressed, char = "H" ))

        ## J
        # -- Images
        self.buttonJ = process_image(imgPath + "normal_buttons/j.png",self.keyWidth,self.keyHeight)
        self.buttonJ_pressed = process_image(imgPath + "normal_buttons/jp.png",self.keyWidth,self.keyHeight)
        self.lastMsgJ= self.keyboardCanvas.create_image(495,135, image=self.buttonJ)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgJ, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgJ, image = self.buttonJ))
        self.keyboardCanvas.tag_bind(self.lastMsgJ, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgJ, image = self.buttonJ_pressed, char = "J" ))

        ## K
        # -- Images
        self.buttonK = process_image(imgPath + "normal_buttons/k.png",self.keyWidth,self.keyHeight)
        self.buttonK_pressed = process_image(imgPath + "normal_buttons/kp.png",self.keyWidth,self.keyHeight)
        self.lastMsgK= self.keyboardCanvas.create_image(565,135, image=self.buttonK)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgK, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgK, image = self.buttonK))
        self.keyboardCanvas.tag_bind(self.lastMsgK, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgK, image = self.buttonK_pressed, char = "K" ))
        ## L
        # -- Images
        self.buttonL = process_image(imgPath + "normal_buttons/l.png",self.keyWidth,self.keyHeight)
        self.buttonL_pressed = process_image(imgPath + "normal_buttons/lp.png",self.keyWidth,self.keyHeight)
        self.lastMsgL= self.keyboardCanvas.create_image(635,135, image=self.buttonL)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgL, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgL, image = self.buttonL))
        self.keyboardCanvas.tag_bind(self.lastMsgL, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgL, image = self.buttonL_pressed, char = "L" ))


        ## RET
        # -- Images
        self.buttonRET = process_image(imgPath + "normal_buttons/return.png",205,142)
        self.buttonRET_pressed = process_image(imgPath + "normal_buttons/returnp.png",205,142)
        self.lastMsgRET= self.keyboardCanvas.create_image(798,173, image=self.buttonRET)

        ## Ñ
        # -- Images
        self.buttonÑ = process_image(imgPath + "normal_buttons/ñ.png",self.keyWidth,self.keyHeight)
        self.buttonÑ_pressed = process_image(imgPath + "normal_buttons/ñp.png",self.keyWidth,self.keyHeight)
        self.lastMsgÑ= self.keyboardCanvas.create_image(705,135, image=self.buttonÑ)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgÑ, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgÑ, image = self.buttonÑ))
        self.keyboardCanvas.tag_bind(self.lastMsgÑ, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgÑ, image = self.buttonÑ_pressed, char = "Ñ" ))

        # Row 3

        ## Z
        # -- Images
        self.buttonZ = process_image(imgPath + "normal_buttons/z.png",self.keyWidth,self.keyHeight)
        self.buttonZ_pressed = process_image(imgPath + "normal_buttons/zp.png",self.keyWidth,self.keyHeight)
        self.lastMsgZ= self.keyboardCanvas.create_image(95,210, image=self.buttonZ)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgZ, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgZ, image = self.buttonZ))
        self.keyboardCanvas.tag_bind(self.lastMsgZ, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgZ, image = self.buttonZ_pressed, char = "Z" ))

        ## X
        # -- Images
        self.buttonX = process_image(imgPath + "normal_buttons/x.png",self.keyWidth,self.keyHeight)
        self.buttonX_pressed = process_image(imgPath + "normal_buttons/xp.png",self.keyWidth,self.keyHeight)
        self.lastMsgX= self.keyboardCanvas.create_image(165,210, image=self.buttonX)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgX, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgX, image = self.buttonX))
        self.keyboardCanvas.tag_bind(self.lastMsgX, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgX, image = self.buttonX_pressed, char = "X" ))
        ## C
        # -- Images
        self.buttonC = process_image(imgPath + "normal_buttons/c.png",self.keyWidth,self.keyHeight)
        self.buttonC_pressed = process_image(imgPath + "normal_buttons/cp.png",self.keyWidth,self.keyHeight)
        self.lastMsgC= self.keyboardCanvas.create_image(235,210, image=self.buttonC)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgC, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgC, image = self.buttonC))
        self.keyboardCanvas.tag_bind(self.lastMsgC, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgC, image = self.buttonC_pressed, char = "C" ))

        ## V
        # -- Images
        self.buttonV = process_image(imgPath + "normal_buttons/v.png",self.keyWidth,self.keyHeight)
        self.buttonV_pressed = process_image(imgPath + "normal_buttons/vp.png",self.keyWidth,self.keyHeight)
        self.lastMsgV= self.keyboardCanvas.create_image(305,210, image=self.buttonV)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgV, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgV, image = self.buttonV))
        self.keyboardCanvas.tag_bind(self.lastMsgV, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgV, image = self.buttonV_pressed, char = "V" ))

        ## B
        # -- Images
        self.buttonB = process_image(imgPath + "normal_buttons/b.png",self.keyWidth,self.keyHeight)
        self.buttonB_pressed = process_image(imgPath + "normal_buttons/bp.png",self.keyWidth,self.keyHeight)
        self.lastMsgB= self.keyboardCanvas.create_image(375,210, image=self.buttonB)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgB, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgB, image = self.buttonB))
        self.keyboardCanvas.tag_bind(self.lastMsgB, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgB, image = self.buttonB_pressed, char = "B" ))

        ## N
        # -- Images
        self.buttonN = process_image(imgPath + "normal_buttons/n.png",self.keyWidth,self.keyHeight)
        self.buttonN_pressed = process_image(imgPath + "normal_buttons/np.png",self.keyWidth,self.keyHeight)
        self.lastMsgN= self.keyboardCanvas.create_image(445,210, image=self.buttonN)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgN, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgN, image = self.buttonN))
        self.keyboardCanvas.tag_bind(self.lastMsgN, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgN, image = self.buttonN_pressed, char = "N" ))

        ## M
        # -- Images
        self.buttonM = process_image(imgPath + "normal_buttons/m.png",self.keyWidth,self.keyHeight)
        self.buttonM_pressed = process_image(imgPath + "normal_buttons/mp.png",self.keyWidth,self.keyHeight)
        self.lastMsgM= self.keyboardCanvas.create_image(515,210, image=self.buttonM)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgM, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgM, image = self.buttonM))
        self.keyboardCanvas.tag_bind(self.lastMsgM, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgM, image = self.buttonM_pressed, char = "M" ))


        ## M
        # -- Images
        self.buttonCOMM = process_image(imgPath + "normal_buttons/coma.png",self.keyWidth,self.keyHeight)
        self.buttonCOMM_pressed = process_image(imgPath + "normal_buttons/comap.png",self.keyWidth,self.keyHeight)
        self.lastMsgCOMM= self.keyboardCanvas.create_image(585,210, image=self.buttonCOMM)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgCOMM, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgCOMM, image = self.buttonCOMM))
        self.keyboardCanvas.tag_bind(self.lastMsgCOMM, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgCOMM, image = self.buttonCOMM_pressed, char = "," ))

        ## DOT
        # -- Images
        self.buttonDOT = process_image(imgPath + "normal_buttons/punto.png",self.keyWidth,self.keyHeight)
        self.buttonDOT_pressed = process_image(imgPath + "normal_buttons/puntop.png",self.keyWidth,self.keyHeight)
        self.lastMsgDOT= self.keyboardCanvas.create_image(655,210, image=self.buttonDOT)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgDOT, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgDOT, image = self.buttonDOT))
        self.keyboardCanvas.tag_bind(self.lastMsgDOT, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgDOT, image = self.buttonDOT_pressed, char = "." ))

        ## SPACEBAR
        # -- Images
        self.instSPACE = process_image(imgPath + "normal_buttons/spacebar.png",385,69)
        self.instSPACE_pressed = process_image(imgPath + "normal_buttons/spacep.png",385,69)
        self.lastMsgSPACE= self.keyboardCanvas.create_image(395,285, image=self.instSPACE)
        # -- Binds
        self.keyboardCanvas.tag_bind(self.lastMsgSPACE, '<ButtonRelease-1>', lambda b: self.onObjectRelease(event ='<ButtonRelease-1>', object =self.lastMsgSPACE, image = self.instSPACE))
        self.keyboardCanvas.tag_bind(self.lastMsgSPACE, '<Button-1>', lambda a: self.onObjectClick(event ='<Button-1>', object =self.lastMsgSPACE, image = self.instSPACE_pressed, char = " " ))


        # Insert fruit background
        self.can2.create_image(500,500, image=self.img2)


        # HEB logo
        self.logoRaw= PIL.Image.open(path + "imgs/logo.png")
        self.logoRaw= self.logoRaw.resize((210,70), PIL.Image.ANTIALIAS)
        self.logo= PIL.ImageTk.PhotoImage(self.logoRaw)
        self.label1= tk.Label(self, background= "#ffffff", image= self.logo)
        self.label1.place (relx=-0.03, rely=.02, relwidth= .2, relheight=.07)
        self.label1.image=self.logo

        # Instructions 1 Page3
        # self.uno= PIL.Image.open(path + "imgs/select.PNG")
        self.uno= PIL.Image.open(path + "imgs/P3_buscar.png")
        self.uno= self.uno.resize((600,150), PIL.Image.ANTIALIAS)
        self.unore=PIL.ImageTk.PhotoImage(self.uno)
        self.label4= tk.Label(self.can, background="#FFFFFF", image= self.unore)
        self.label4.place(relx=0.02, rely=0.12 ,relwidth=0.4, relheight=.16)
        self.label4.image= self.unore      

        # Animated Instructions Page3
        self.anim1Raw= PIL.Image.open(path + "imgs/animation3.png")
        self.anim1Raw= self.anim1Raw.resize((580,380), PIL.Image.ANTIALIAS)
        self.anim1= PIL.ImageTk.PhotoImage(self.anim1Raw)
        self.label3= tk.Label(self, background= "#FFFFFF", image= self.anim1) 
        self.label3.place (relx=0.12, rely=.35, relwidth= .3, relheight=.33)
        self.label3.image=self.anim1

        # Search Instructions
        self.search= PIL.Image.open(path + "imgs/buscar.png")
        self.search= self.search.resize((360,100), PIL.Image.ANTIALIAS)
        self.searchre=PIL.ImageTk.PhotoImage(self.search)
        self.searchMsg = self.can2.create_image(200,80, image=self.searchre)


        # Finish image
        self.finish= PIL.Image.open(path + "imgs/finish_button.png")
        self.finish= self.finish.resize((600,100), PIL.Image.ANTIALIAS)
        self.finishre=PIL.ImageTk.PhotoImage(self.finish)
        self.finishMsg = self.can2.create_image(500,640, image=self.finishre)
        # self.can2.tag_bind(self.finishMsg, '<Button-1>', lambda b: self.controller.show_frame("PageOne"))
        self.can2.tag_bind(self.finishMsg, '<Button-1>', lambda b: self.uploadData())

        # Search bar

        combobox_autocomplete = tkstuff_4.Combobox_Autocomplete(self.can2, self.list_of_items, self.equation,highlightthickness=1, font = ("Helvetica","20"))
        combobox_autocomplete.place(relx=0.07, rely=.15 ,relwidth=.35, relheight=.07)

    def uploadData(self):
        global DictReturn
        global names 
        global percentages
        global namesStr
        global feedback
        global pathN3
        global client
        D2C.SendDeviceToCloudMessage().iothub_client_send_telemetry(client, pathN3, names[0], round(percentages[0],6),names[1], round(percentages[1],6),names[2], round(percentages[2],6),1,feedback)
        self.controller.show_frame("PageOne")


    def onObjectClick(self,event,object,image,char):
        self.keyboardCanvas.itemconfig(object, image = image)
        if char == "DEL":
            self.exp = self.exp[:-1]
        else:
            self.exp=self.exp + str(char)
        self.equation.set(self.exp)
        self.action()              
        print (char)

    def onObjectRelease(self,event,object,image):
        self.keyboardCanvas.itemconfig(object, image = image)  

    def action(self):
        global feedback
        self.equation.set(self.exp)
        print(self.equation.get()) 
        x = self.equation.get()
    
        if (self.exp == ""):
            print("variable vacia")
            self.labelFlag=False
        elif (self.exp != "") and (self.labelFlag==False):
 
            combobox_autocomplete = tkstuff_4.Combobox_Autocomplete(self.can2, self.list_of_items, self.equation,highlightthickness=1, font = ("Helvetica","20"))
            combobox_autocomplete.place(relx=0.07, rely=.15 ,relwidth=.35, relheight=.07)
            feedback = combobox_autocomplete.getShownSelection(self)
            print("feedback is", feedback)
            self.labelFlag = True

        elif (self.exp != "") and self.labelFlag==True:

            combobox_autocomplete = tkstuff_4.Combobox_Autocomplete(self.can2, self.list_of_items, self.equation,highlightthickness=1, font = ("Helvetica","20"))
            combobox_autocomplete.place(relx=0.07, rely=.15 ,relwidth=.35, relheight=.07)
            feedback = combobox_autocomplete.getShownSelection(self)
            print("feedback is", feedback)
            self.labelFlag = True
        else:
            pass
        print(self.exp, self.labelFlag)
   
    def press(self, num):

        self.exp=self.exp + str(num)
        self.equation.set(self.exp)
        self.action()

    def update(self, *args, **kwargs):
        #self.returnCounter = self.returnCounter + 10
        if self.returnCounter >= self.returnLimit:
            self.returnCounter = 0
            self.controller.show_frame("PageOne")
        self.delay = 10
        self.after(self.delay, self.update)

class MyVideoCapture:
    def __init__(self, video_source= 1): # Zchange
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)


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
