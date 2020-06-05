# Keybaord body - ROW 3
        self.keyWidth = 63
        self.keyHeight = 69

        self.buttonZ= PIL.Image.open(path + "imgs/normal_buttons/z.png")
        self.buttonZ= self.buttonZ.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instZ= PIL.ImageTk.PhotoImage(self.buttonZ)
        self.lastMsgZ = self.keyboardCanvas.create_image(95,185, image=self.instZ)

        self.buttonX= PIL.Image.open(path + "imgs/normal_buttons/x.png")
        self.buttonX= self.buttonX.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instX= PIL.ImageTk.PhotoImage(self.buttonX)
        self.lastMsgX = self.keyboardCanvas.create_image(165,185, image=self.instX)

        self.buttonC= PIL.Image.open(path + "imgs/normal_buttons/c.png")
        self.buttonC= self.buttonC.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instC= PIL.ImageTk.PhotoImage(self.buttonC)
        self.lastMsgC = self.keyboardCanvas.create_image(235,185, image=self.instC)

        self.buttonV= PIL.Image.open(path + "imgs/normal_buttons/v.png")
        self.buttonV= self.buttonV.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instV= PIL.ImageTk.PhotoImage(self.buttonV)
        self.lastMsgV= self.keyboardCanvas.create_image(305,185, image=self.instV)

        self.buttonB= PIL.Image.open(path + "imgs/normal_buttons/b.png")
        self.buttonB= self.buttonB.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instB= PIL.ImageTk.PhotoImage(self.buttonB)
        self.lastMsgB= self.keyboardCanvas.create_image(375,185, image=self.instB)

        self.buttonN= PIL.Image.open(path + "imgs/normal_buttons/n.png")
        self.buttonN= self.buttonN.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instN= PIL.ImageTk.PhotoImage(self.buttonN)
        self.lastMsgN= self.keyboardCanvas.create_image(445,185, image=self.instN)

        self.buttonM= PIL.Image.open(path + "imgs/normal_buttons/m.png")
        self.buttonM= self.buttonM.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instM= PIL.ImageTk.PhotoImage(self.buttonM)
        self.lastMsgM= self.keyboardCanvas.create_image(515,185, image=self.instM)

        self.buttonCOMM= PIL.Image.open(path + "imgs/normal_buttons/coma.png")
        self.buttonCOMM= self.buttonCOMM.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instCOMM= PIL.ImageTk.PhotoImage(self.buttonCOMM)
        self.lastMsgCOMM= self.keyboardCanvas.create_image(585,185, image=self.instCOMM)

        self.buttonDOT= PIL.Image.open(path + "imgs/normal_buttons/punto.png")
        self.buttonDOT= self.buttonDOT.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instDOT= PIL.ImageTk.PhotoImage(self.buttonDOT)
        self.lastMsgDOT= self.keyboardCanvas.create_image(655,185, image=self.instDOT)