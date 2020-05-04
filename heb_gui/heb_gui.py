#Hi 

import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
import PIL.Image, PIL.ImageTk
import cv2
from playsound import playsound
from PIL import Image, ImageTk
from tkinter.ttk import Frame, Label, Style
import pyautogui
#import Tkinter as tk     # python 2
#import tkFont as tkfont  # python 2
path = "C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs"

#"C:\\Users\\Hernan Martinez\\Documents\\Axtel\\1_Projects\\03_HEB\\02_code\\GUI_HEB\\test\\imgs\\"
#suggestions = ["potato","mango","banana"]
prodDB = { "avocado":{"name":"Aguacate","PLU":"2660"},
            "banana":{"name":"Platano","PLU":"2661"},
            "carrot":{"name":"Zanahoria","PLU":"2662"},
            "coriander":{"name":"Cilantro","PLU":"2663"},
            "corn":{"name":"Elote Blanco","PLU":"2664"},
            "cucumber":{"name":"Pepino","PLU":"2665"},
            "goldenapple":{"name":"Manzana Golden","PLU":"2666"},
            "lime":{"name":"Limon","PLU":"2667"},
            "mango":{"name":"Mango","PLU":"2668"},
            "onion":{"name":"Cebolla Blanca","PLU":"2669"},
            "orange":{"name":"Naranja","PLU":"2670"},
            "orangepepper":{"name":"Pimiento Naranja","PLU":"2671"},
            "pineapple":{"name":"Piña","PLU":"2672"},
            "potato":{"name":"Papa","PLU":"2673"},
            "purpleonion":{"name":"Cebolla Morada","PLU":"2674"},
            "redapple":{"name":"Manzana Roja","PLU":"2675"},
            "redpepper":{"name":"Pimiento Rojo","PLU":"2676"},
            "serrano":{"name":"Chile Serrano","PLU":"2677"},
            "tomato":{"name":"Tomate","PLU":"2678"},
            "zucchini":{"name":"Calabacita","PLU":"2679"}}
prodDict = {
            0:{"name":"avocado", "PLU":"XXXX", "path":"C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/avocado.png"},
            1:{"name":"avocado", "PLU":"XXXX", "path":"C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/avocado.png"},
            2:{"name":"avocado", "PLU":"XXXX", "path":"C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/avocado.png"}
}
class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        global suggestions
        #suggestions = ["potato","mango","banana"]
        self.attributes("-toolwindow",1)
        self.resizable(0,0)
        self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        self.overrideredirect(1)
        self.focus_set() # <-- move focus to this widget
        self.bind("<Escape>", lambda e: self.close_window()) # <-- close everything
        self.bind("p", lambda f: self.changeSuggestions()) # <-- change
        # Keyboard Page-Control using binds
        self.bind("1", lambda a: self.show_frame("StartPage"))
        self.bind("2", lambda a: self.show_frame("PageOne"))
        self.bind("3", lambda a: self.show_frame("PageTwo"))
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
    def close_window(self):
        '''Destroy everything'''
        self.destroy()
    def changeSuggestions(self):
        global suggestions
        suggestions = ["avocado","purpleonion","redapple"]

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        global suggestions

        #suggestions = ["potato","mango","banana"]
        tk.Frame.__init__(self, parent)
        self.controller = controller
        #self.suggestions = ["potato","mango","banana"]
        # label = tk.Label(self, text="This is the start page", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)

        # button1 = tk.Button(self, text="Go to Page One",
        #                     command=lambda: controller.show_frame("PageOne"))
        # button2 = tk.Button(self, text="Go to Page Two",
        #                     command=lambda: controller.show_frame("PageTwo"))
        # button1.pack()
        # button2.pack()

        # Detection Variables
        self.counter = 0
        self.ctrLimit = 120
        self.newProdFlg = False
        self.i = 1
        self.template = cv2.imread('imgs/template.png', 0)
        self.detThreshold = .94
        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()
        self.vid = MyVideoCapture(0)

        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open("imgs/transparent.png")
        self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open("imgs/background.jpg")
        self.img2= self.img2.resize((3840,2160), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)
        self.can2 = tk.Canvas(self, width=WIDTH/2, height=HEIGHT, bg='#000000')
        self.can2.place(relx=0.5, rely=0 ,relwidth=1, relheight=1)

        # Videostream container 
        self.vidCont= tk.Button(self.can2, background= "#555555")
        self.vidCont.place(relx=.058, rely= .17, width=720 , height=480)

        # Insert fruit background
        self.can2.create_image(500,500, image=self.img2)

        # Create detection status image container (may change image to indicate detection)
        self.firstImg = self.can2.create_image(100,100, image=self.img)
        
        # Positive Detection Icon
        self.img3= PIL.Image.open("imgs/detection.png")
        self.img3= self.img3.resize((120,120), PIL.Image.ANTIALIAS)
        self.img3= PIL.ImageTk.PhotoImage(self.img3)

        # HEB logo
        self.logoRaw= PIL.Image.open("imgs/logo.png")
        self.logoRaw= self.logoRaw.resize((210,70), PIL.Image.ANTIALIAS)
        self.logo= PIL.ImageTk.PhotoImage(self.logoRaw)
        self.label1= tk.Label(self, background= "#ffffff", image= self.logo)
        self.label1.place (relx=-0.03, rely=.02, relwidth= .2, relheight=.07)
        self.label1.image=self.logo

        # Animated Instructions
        self.anim1Raw= PIL.Image.open("imgs/animation1.jpg")
        self.anim1Raw= self.anim1Raw.resize((350,350), PIL.Image.ANTIALIAS)
        self.anim1= PIL.ImageTk.PhotoImage(self.anim1Raw)
        self.label3= tk.Label(self, background= "#FFFFFF", image= self.anim1) 
        self.label3.place (relx=0.12, rely=.15, relwidth= .26, relheight=.48)
        self.label3.image=self.anim1

        # Instructions 1
        self.inst1Raw= PIL.Image.open("imgs/inst1.png")
        self.inst1Raw= self.inst1Raw.resize((750,100), PIL.Image.ANTIALIAS)
        self.inst1= PIL.ImageTk.PhotoImage(self.inst1Raw)
        self.label2= tk.Label(self, background= "#FFFFFF", image= self.inst1) 
        self.label2.place (relx=0.01, rely=.1, relwidth= .45, relheight=.15)
        self.label2.image=self.inst1

        # Instructions 2
        self.inst2Raw= PIL.Image.open("imgs/inst2.png")
        self.inst2Raw= self.inst2Raw.resize((750,200), PIL.Image.ANTIALIAS)
        self.inst2= PIL.ImageTk.PhotoImage(self.inst2Raw)
        self.label4= tk.Label(self.can, background= "#FFFFFF", image= self.inst2) 
        self.label4.place (relx=0.01, rely=.63, relwidth= .45, relheight=.2)
        self.label4.image=self.inst2

        # Instructions 3 & 4 : Detection message
        self.inst3Raw= PIL.Image.open("imgs/inst3.png")
        self.inst3Raw= self.inst3Raw.resize((300,100), PIL.Image.ANTIALIAS)
        self.inst3= PIL.ImageTk.PhotoImage(self.inst3Raw)
        self.detMsg = self.can2.create_image(300,110, image=self.inst3)
        self.inst4Raw= PIL.Image.open("imgs/inst4.png")
        self.inst4Raw= self.inst4Raw.resize((300,100), PIL.Image.ANTIALIAS)
        self.inst4= PIL.ImageTk.PhotoImage(self.inst4Raw)

        # Instructions 5
        self.inst5Raw= PIL.Image.open("imgs/inst5.png")
        self.inst5Raw= self.inst5Raw.resize((700,300), PIL.Image.ANTIALIAS)
        self.inst5= PIL.ImageTk.PhotoImage(self.inst5Raw)
        self.lastMsg = self.can2.create_image(450,780, image=self.inst5)

        # Update app info
        self.toggleVar = False
        self.update()

    def update(self, *args, **kwargs):
        ret, frame = self.vid.get_frame()
        newImg = cv2.resize(frame,(720,480))
        newImg = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(newImg))
        self.toggleVar = not self.toggleVar
        print(self.toggleVar)

        if ret:
            #print(self.counter)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            res1 = cv2.matchTemplate(gray,self.template,cv2.TM_CCOEFF_NORMED)
            if res1 < self.detThreshold:
                #print("Detecting something...")
                self.counter += 1
                self.can2.itemconfig(self.firstImg, image = self.img3)
                self.can2.itemconfig(self.detMsg, image = self.inst4)
            else:
                self.can2.itemconfig(self.firstImg, image = self.img)
                self.can2.itemconfig(self.detMsg, image = self.inst3)
                self.counter = 0
            if self.counter > self.ctrLimit:
                if self.newProdFlg == False:
                    playsound('press.wav', block=False)
                    #self.vid.__class__release()
                    print("Nuevo producto en bascula")
                    self.newProdFlg = True
                    #cv2.imwrite("C:\\imgs\\full\\image" + str(self.i) + ".png", frame)
                    self.i += 1
                    #self.controller.show_frame("PageOne")
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



class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        global suggestions
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.suggestions = ["potato","mango","banana"]
        self.prodDict = {
            0:{"name":"avocado", "PLU":"XXXX", "path":"C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/avocado.png"},
            1:{"name":"avocado", "PLU":"XXXX", "path":"C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/avocado.png"},
            2:{"name":"avocado", "PLU":"XXXX", "path":"C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/avocado.png"}
        }
        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()
        self.path = path = "C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/"
        # label = tk.Label(self, text="This is page 1", font=controller.title_font)
        # label.pack(side="top", fill="x", pady=10)
        # button = tk.Button(self, text="Go to the start page",
        #                    command=lambda: controller.show_frame("StartPage"))
        # button.pack()

        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open("imgs/transparent.png")
        self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open("imgs/background.jpg")
        self.img2= self.img2.resize((3840,2160), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)
        self.can2 = tk.Canvas(self, width=WIDTH/2, height=HEIGHT, bg='#000000')
        self.can2.place(relx=0.5, rely=0 ,relwidth=1, relheight=1)


        # Insert fruit background
        self.can2.create_image(500,500, image=self.img2)


        # HEB logo
        self.logoRaw= PIL.Image.open("imgs/logo.png")
        self.logoRaw= self.logoRaw.resize((210,70), PIL.Image.ANTIALIAS)
        self.logo= PIL.ImageTk.PhotoImage(self.logoRaw)
        self.label1= tk.Label(self, background= "#ffffff", image= self.logo)
        self.label1.place (relx=-0.03, rely=.02, relwidth= .2, relheight=.07)
        self.label1.image=self.logo


        # self.ins= PIL.Image.open("imgs/instructions.png")
        # self.ins= self.ins.resize((500,350), PIL.Image.ANTIALIAS)
        # self.instructions= PIL.ImageTk.PhotoImage(self.ins)
        # self.label3= tk.Label(self.can, background= "#FFFFFF", image= self.instructions) 
        # self.label3.place (relx=0.02, rely=.23, relwidth= .35, relheight=.55)
        # self.label3.image=self.instructions

        # Instructions 1 P2
        self.uno= PIL.Image.open("imgs/select.png")
        self.uno= self.uno.resize((750,220), PIL.Image.ANTIALIAS)
        self.unore=PIL.ImageTk.PhotoImage(self.uno)
        self.label4= tk.Label(self.can, background="#FFFFFF", image= self.unore)
        self.label4.place(relx=0.02, rely=0.12 ,relwidth=0.4, relheight=.16)
        self.label4.image= self.unore      

        # Animated Instructions P2
        self.anim1Raw= PIL.Image.open("imgs/animation2.png")
        self.anim1Raw= self.anim1Raw.resize((580,380), PIL.Image.ANTIALIAS)
        self.anim1= PIL.ImageTk.PhotoImage(self.anim1Raw)
        self.label3= tk.Label(self, background= "#FFFFFF", image= self.anim1) 
        self.label3.place (relx=0.12, rely=.35, relwidth= .3, relheight=.33)
        self.label3.image=self.anim1

        # Instructions 2 P2
        self.dos= PIL.Image.open("imgs/instructions2P2.png")
        self.dos= self.dos.resize((550,140), PIL.Image.ANTIALIAS)
        self.dosre=PIL.ImageTk.PhotoImage(self.dos)
        self.label4= tk.Label(self.can, background="#FFFFFF", image= self.dosre)
        self.label4.place(relx=0.051, rely=0.65,relwidth=0.45, relheight=.20)
        self.label4.image= self.dosre

        self.prodInfo = self.getProdInfo(self.suggestions,self.prodDict)
        print(self.prodInfo)

        # Main Suggestion
        self.option1= PIL.Image.open(self.prodInfo[0]["path"])
        self.option1= self.option1.resize((270,270), PIL.Image.ANTIALIAS)
        self.option1re=PIL.ImageTk.PhotoImage(self.option1)
        self.label5= tk.Button(self, background="#ffffff", image= self.option1re)
        self.label5.place(relx=0.62, rely=0.04 ,relwidth=0.14, relheight=.24)
        self.label5.image= self.option1re
        self.resultInfo= tk.Label(self, background="#ffffff", text=self.prodInfo[0]["name"] + " \n " + self.prodInfo[0]["PLU"],font = ("Helvetica","21"))
        self.resultInfo.place(relx=0.760, rely=0.04 ,relwidth=0.12, relheight=.24)
        self.resultInfo.image= self.option1re


        self.option2= PIL.Image.open(self.prodInfo[0]["path"])
        self.option2= self.option2.resize((200,200), PIL.Image.ANTIALIAS)
        self.option2re=PIL.ImageTk.PhotoImage(self.option2)
        self.label6= tk.Button(self, background="#ffffff", image= self.option2re, command= lambda: self.changeImg(0))
        self.label6.place(relx=0.61, rely=0.35 ,relwidth=0.08, relheight=.14)
        self.label6.image= self.option2re


        self.option3= PIL.Image.open(self.prodInfo[1]["path"])
        self.option3= self.option3.resize((200,200), PIL.Image.ANTIALIAS)
        self.option3re= PIL.ImageTk.PhotoImage(self.option3)
        self.label7= tk.Button(self, background="#ffffff", image= self.option3re, command= lambda: self.changeImg(1))
        self.label7.place(relx=0.72, rely=0.35,relwidth=0.08, relheight=.14)
        self.label7.image= self.option3re

        self.option4= PIL.Image.open(self.prodInfo[2]["path"])
        self.option4= self.option4.resize((200,200), PIL.Image.ANTIALIAS)
        self.option4re= PIL.ImageTk.PhotoImage(self.option4)
        self.label8= tk.Button(self, background="#ffffff", image= self.option4re, command= lambda: self.changeImg(2))
        self.label8.place(relx=0.83, rely=0.35,relwidth=0.08, relheight=.14)
        self.label8.image= self.option4re


        # Instructions 3 P2
        self.dos= PIL.Image.open("imgs/instructions3P2.png")
        self.dos= self.dos.resize((550,130), PIL.Image.ANTIALIAS)
        self.dosre=PIL.ImageTk.PhotoImage(self.dos)
        self.lastMsg = self.can2.create_image(500,800, image=self.dosre)

        # Finish button
        self.finish= PIL.Image.open("imgs/terminar.png")
        self.finish= self.finish.resize((780,90), PIL.Image.ANTIALIAS)
        self.finishre=PIL.ImageTk.PhotoImage(self.finish)
        self.button5= tk.Button(self, background="#ffffff", image= self.finishre)
        self.button5.place(relx=0.6, rely=0.55 ,relwidth=0.33, relheight=.08)
        self.button5.image= self.finishre

        # Search button
        self.search= PIL.Image.open("imgs/buscar_producto.png")
        self.search= self.search.resize((380,70), PIL.Image.ANTIALIAS)
        self.searchre=PIL.ImageTk.PhotoImage(self.search)
        self.button6= tk.Button(self, background="#ffffff", image= self.searchre)
        self.button6.place(relx=0.66, rely=0.85 ,relwidth=0.20, relheight=.06)
        self.button6.image= self.finishre

    def getProdInfo(self,suggestions,prodDict):
        print(suggestions)

        for i,element in enumerate(suggestions):

            self.prodDict[i]["name"] = prodDB[element]["name"]
            self.prodDict[i]["PLU"] = prodDB[element]["PLU"]
            self.prodDict[i]["path"] = self.path+str(element)+".png"
        return prodDict

    def changeImg(self,imgNo):
        self.option1= PIL.Image.open(self.prodInfo[imgNo]["path"])
        self.option1= self.option1.resize((270,270), PIL.Image.ANTIALIAS)
        self.option1re=PIL.ImageTk.PhotoImage(self.option1)

        self.label5.configure(image=self.option1re)
        self.label5.image = self.option1re
        newText = self.prodInfo[imgNo]["name"] + " \n " + self.prodInfo[imgNo]["PLU"]
        self.resultInfo.configure(text=newText)


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        global suggestions
        tk.Frame.__init__(self, parent)
        HEIGHT = self.master.winfo_screenwidth()
        WIDTH = self.master.winfo_screenheight()
        self.path = path = "C:/Users/lenovo/Documents/pr_asanchez/P01_HEB/GUI/DEMO HEB/heb_gui/imgs/"
        
        
        # Add canvas to frame
        self.can = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), bg='#ffffff')
        self.can.place(relx=0, rely=0 ,relwidth=1, relheight=1)

        ## BACKGROUND
        # Import images
        self.img= PIL.Image.open("imgs/transparent.png")
        self.img= self.img.resize((170,100), PIL.Image.ANTIALIAS)
        self.img= PIL.ImageTk.PhotoImage(self.img)
        self.img2= PIL.Image.open("imgs/background.jpg")
        self.img2= self.img2.resize((3840,2160), PIL.Image.ANTIALIAS)
        self.img2= PIL.ImageTk.PhotoImage(self.img2)
        self.can2 = tk.Canvas(self, width=WIDTH/2, height=HEIGHT, bg='#000000')
        self.can2.place(relx=0.5, rely=0 ,relwidth=1, relheight=1)

        # Insert fruit background
        self.can2.create_image(500,500, image=self.img2)

        # HEB logo
        self.logoRaw= PIL.Image.open("imgs/logo.png")
        self.logoRaw= self.logoRaw.resize((210,70), PIL.Image.ANTIALIAS)
        self.logo= PIL.ImageTk.PhotoImage(self.logoRaw)
        self.label1= tk.Label(self, background= "#ffffff", image= self.logo)
        self.label1.place (relx=-0.03, rely=.02, relwidth= .2, relheight=.07)
        self.label1.image=self.logo

        #Instructions 1 P3
        self.uno= PIL.Image.open("imgs/2.png")
        self.uno= self.uno.resize((750,300), Image.ANTIALIAS)
        self.unore= PIL.ImageTk.PhotoImage(self.uno)
        self.label2= tk.Label(self, background="#FFFFFF", image= self.unore)
        self.label2.place(relx=0.05, rely=0.04, relwidth= 0.25, relheight=.20)
        self.label2.image= self.unore


        #Label- video 
        self.label3= tk.Label(self, background= "#ADADAD")
        self.label3.place(relx=0.12, rely=.35, relwidth= .3, relheight=.33)


        #Instructions 2 P3
        self.dos= PIL.Image.open("imgs/recuerda.png")
        self.dos= self.dos.resize((750,300), Image.ANTIALIAS)
        self.dosre= PIL.ImageTk.PhotoImage(self.dos)
        self.label3= tk.Label(self, background="#FFFFFF", image= self.dosre)
        self.label3.place(relx=0.05, rely=0.65 ,relwidth=0.39, relheight=.15)
        self.label3.image= self.dosre

        self.e1= tk.Entry(self, bd= 1, background="#FFFFFF", foreground="#505050")
        self.e1.place(relx=0.550, rely=0.20,relwidth=0.40, relheight=0.06)

        # Instructions 3 P3
        self.dos= PIL.Image.open("imgs/buscar.png")
        self.dos= self.dos.resize((400,100), PIL.Image.ANTIALIAS)
        self.dosre=PIL.ImageTk.PhotoImage(self.dos)
        self.lastMsg = self.can2.create_image(500,130, image=self.dosre)
        

        # Search button
        self.next= PIL.Image.open("imgs/Siguiente.jpg")
        self.next= self.next.resize((300,60), PIL.Image.ANTIALIAS)
        self.nextre=PIL.ImageTk.PhotoImage(self.next)
        self.button1= tk.Button(self, background="#ffffff", image= self.nextre)
        self.button1.place(relx=0.66, rely=0.55 ,relwidth=0.20, relheight=.06)
        self.button1.image= self.nextre

        


        """self.controller = controller
        label = tk.Label(self, text="This is page 2", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()"""




class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

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