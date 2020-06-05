# Keybaord body - ROW 2
        self.keyWidth = 63
        self.keyHeight = 69


        self.buttonA= PIL.Image.open(path + "imgs/normal_buttons/a.png")
        self.buttonA= self.buttonA.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instA= PIL.ImageTk.PhotoImage(self.buttonA)
        self.lastMsgA = self.keyboardCanvas.create_image(75,120, image=self.instA)

        self.buttonS= PIL.Image.open(path + "imgs/normal_buttons/s.png")
        self.buttonS= self.buttonS.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instS= PIL.ImageTk.PhotoImage(self.buttonS)
        self.lastMsgS = self.keyboardCanvas.create_image(145,120, image=self.instS)
        
        self.buttonD= PIL.Image.open(path + "imgs/normal_buttons/d.png")
        self.buttonD= self.buttonD.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instD= PIL.ImageTk.PhotoImage(self.buttonD)
        self.lastMsgD = self.keyboardCanvas.create_image(215,120, image=self.instD)

        self.buttonF= PIL.Image.open(path + "imgs/normal_buttons/f.png")
        self.buttonF= self.buttonF.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instF= PIL.ImageTk.PhotoImage(self.buttonF)
        self.lastMsgF = self.keyboardCanvas.create_image(285,120, image=self.instF)
        
        self.buttonG= PIL.Image.open(path + "imgs/normal_buttons/g.png")
        self.buttonG= self.buttonG.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instG= PIL.ImageTk.PhotoImage(self.buttonG)
        self.lastMsgG = self.keyboardCanvas.create_image(355,120, image=self.instG)

        self.buttonH= PIL.Image.open(path + "imgs/normal_buttons/h.png")
        self.buttonH= self.buttonH.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instH= PIL.ImageTk.PhotoImage(self.buttonH)
        self.lastMsgH = self.keyboardCanvas.create_image(425,120, image=self.instH)

        self.buttonJ= PIL.Image.open(path + "imgs/normal_buttons/j.png")
        self.buttonJ= self.buttonJ.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instJ= PIL.ImageTk.PhotoImage(self.buttonJ)
        self.lastMsgJ = self.keyboardCanvas.create_image(495,120, image=self.instJ)

        self.buttonK= PIL.Image.open(path + "imgs/normal_buttons/k.png")
        self.buttonK= self.buttonK.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instK= PIL.ImageTk.PhotoImage(self.buttonK)
        self.lastMsgK = self.keyboardCanvas.create_image(565,120, image=self.instK)

        self.buttonL= PIL.Image.open(path + "imgs/normal_buttons/l.png")
        self.buttonL= self.buttonL.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instL= PIL.ImageTk.PhotoImage(self.buttonL)
        self.lastMsgL= self.keyboardCanvas.create_image(635,120, image=self.instL)

        self.buttonÑ= PIL.Image.open(path + "imgs/normal_buttons/ñ.png")
        self.buttonÑ= self.buttonÑ.resize((self.keyWidth,self.keyHeight), PIL.Image.ANTIALIAS)
        self.instÑ= PIL.ImageTk.PhotoImage(self.buttonÑ)
        self.lastMsgÑ= self.keyboardCanvas.create_image(705,120, image=self.instÑ)

        self.buttonRET= PIL.Image.open(path + "imgs/normal_buttons/return.png")
        self.buttonRET= self.buttonRET.resize((100,110), PIL.Image.ANTIALIAS)
        self.instRET= PIL.ImageTk.PhotoImage(self.buttonRET)
        self.lastMsgRET= self.keyboardCanvas.create_image(775,150, image=self.instRET)