from tkinter import *
from tkinter import ttk
import cv2
import imutils
from PIL import Image,ImageTk
from threading import Thread
import time
from tkintermapview import TkinterMapView
import math
import serial.tools.list_ports as p
from telemetri.yer_istasyonu import haberleşme
import torch
import torchvision.transforms as transforms
import numpy as np
class Arayuz():
    def __init__(self):
        self.haber = haberleşme()
        self.connect_control = 0
        self.win = Tk()
        self.win.geometry("1530x785+0+0")
        self.win.config(bg="#1e1e1e")
        self.win.title("ALFA TEAM")
        #self.win.iconbitmap("image/alfaicon.ico")

        #--------------------------
        self.connectf = Frame(self.win, bg="black", highlightthickness=1, highlightbackground="dark gray")
        self.connectf.place(relx=0.0066, rely=0.0066, relwidth=0.9868, relheight=0.0764)

        #alfa = Image.open("image/alfalogo.jpg")
        #alfa = alfa.resize((80, 80), Image.Resampling.LANCZOS)
        #alfa = ImageTk.PhotoImage(alfa)
        #Label(self.connectf, image=alfa, border=0).pack(expand=True)

        self.valuest = ["tcp:127.0.0.1:5762"]
        self.ctype = ttk.Combobox(self.connectf,values=self.valuest, width=10, postcommand = self.com_update)
        self.ctype.place(relx=0.8, rely=0.3)

        
        valuesb = ["115200", "57600"]
        self.cbaud = ttk.Combobox(self.connectf,values=valuesb, width=10)
        self.cbaud.place(relx=0.86, rely=0.3)
        
        dc = Image.open('image/DC.jpg')
        dc = dc.resize((60, 60), Image.Resampling.LANCZOS)
        self.dc = ImageTk.PhotoImage(dc)
        c = Image.open('image/C.jpg')
        c = c.resize((60, 60), Image.Resampling.LANCZOS)
        self.c = ImageTk.PhotoImage(c)
        self.cbutton = Button(self.connectf, image=self.dc, command=self.connectF, cursor="hand2",border=0)#,  width=8,  height=3
        self.cbutton.place(relx=0.92, rely=0, width=60, height=60)
        self.dcLabel = Label(self.connectf, text="Dis\nconnect", bg="black", fg="dark gray")
        self.dcLabel.place(relx=0.96, rely=0.18)
        
        #----------------------------
        self.mapf = Frame(self.win, bg="black", border=0, highlightthickness=1, highlightbackground="dark gray")
        self.mapf.place(relx=0.0066, rely=0.093, relwidth=0.3702 ,relheight=0.44)

        self.mapWidget = TkinterMapView(self.mapf, corner_radius=0)
        self.mapWidget.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=CENTER)
        self.mapWidget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.mapWidget.set_position(40.18745923245608, 29.128789221766276)  # marker=True
        
        #---------------------------------------------------------------------------------------------------------------
        self.maininfof = Frame(self.win, bg="yellow")
        self.maininfof.place(relx=0.0066, rely=0.545, relwidth=0.3702, relheight=0.44)
        #infos------------------
        infoF = Frame(self.maininfof, bg="#191714", highlightthickness=1, highlightbackground="dark gray")
        infoF.place(x=0, y=0, relheight=1, relwidth=0.5)
        
        info11 = Frame(infoF, bg="#191714")
        info11.place(relx=0.0, rely=0.0,relwidth=0.5,relheight=0.33)
        info12 = Frame(infoF, bg="#191714")
        info12.place(relx=0.5, rely=0.0,relwidth=0.5,relheight=0.33)
        info21 = Frame(infoF, bg="#191714")
        info21.place(relx=0.0, rely=0.33,relwidth=0.5,relheight=0.33)
        info22 = Frame(infoF, bg="#191714")
        info22.place(relx=0.5, rely=0.33,relwidth=0.5,relheight=0.33)
        info31 = Frame(infoF, bg="#191714")
        info31.place(relx=0.0, rely=0.66,relwidth=0.5,relheight=0.33)
        info32 = Frame(infoF, bg="#191714")
        info32.place(relx=0.5, rely=0.66,relwidth=0.5,relheight=0.33)

        Label(info11, bg="#191714", fg="dark gray").pack(fill="none")
        Label(info11, text="Altitude(m)", font=("Arial", 11) , bg="#191714", fg="dark gray").pack(fill="none")
        self.label11 = Label(info11, text="00.00", font=("Arial", 25) , bg="#191714", fg="dark gray")
        self.label11.pack(fill="none")

        Label(info12, bg="#191714", fg="dark gray").pack(fill="none")
        Label(info12, text="Altitude(m)", font=("Arial", 11) , bg="#191714", fg="dark gray").pack(fill="none")
        self.label12 = Label(info12, text="00.00", font=("Arial", 25) , bg="#191714", fg="dark gray")
        self.label12.pack(fill="none")

        Label(info21, bg="#191714", fg="dark gray").pack(fill="none")
        Label(info21, text="Altitude(m)", font=("Arial", 11) , bg="#191714", fg="dark gray").pack(fill="none")
        self.label21 = Label(info21, text="00.00", font=("Arial", 25) , bg="#191714", fg="dark gray")
        self.label21.pack(fill="none")

        Label(info22, bg="#191714", fg="dark gray").pack(fill="none")
        Label(info22, text="Altitude(m)", font=("Arial", 11) , bg="#191714", fg="dark gray").pack(fill="none")
        self.label22 = Label(info22, text="00.00", font=("Arial", 25) , bg="#191714", fg="dark gray")
        self.label22.pack(fill="none")

        Label(info31, bg="#191714", fg="dark gray").pack(fill="none")
        Label(info31, text="Altitude(m)", font=("Arial", 11) , bg="#191714", fg="dark gray").pack(fill="none")
        self.label31 = Label(info31, text="00.00", font=("Arial", 25) , bg="#191714", fg="dark gray")
        self.label31.pack(fill="none")

        Label(info32, bg="#191714", fg="dark gray").pack(fill="none")
        Label(info32, text="Altitude(m)", font=("Arial", 11) , bg="#191714", fg="dark gray").pack(fill="none")
        self.label32 = Label(info32, text="00.00", font=("Arial", 25) , bg="#191714", fg="dark gray")
        self.label32.pack(fill="none")


        #commands------------------
        commands = Frame(self.maininfof, bg="#191714", highlightthickness=1, highlightbackground="dark gray")
        commands.place(relx=0.5, y=0, relwidth=0.5, relheight=1)
        
        Label(commands,bg="#191714", text="COMMANDS", fg="dark gray", font=("Arial", 14)).place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.15)

        valueswp = ["0","1","2","3","4","5","6","7","8","9","10"]
        self.wptype = ttk.Combobox(commands,values=valueswp, width=10, postcommand=self.wp_update)
        self.wptype.place(relx=0.05, rely=0.25, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.366, rely=0.25, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.682, rely=0.25, relwidth=0.266, relheight=0.1)
        valuesmode = ["AUTO", "GUIDED", "QRTL", "QLOITER", "QSTABILIZE", "QHOVER"]
        self.modetype = ttk.Combobox(commands,values=valuesmode, width=10)
        self.modetype.place(relx=0.05, rely=0.4, relwidth=0.266, relheight=0.1)
        Button(commands,command=self.haber.gonder).place(relx=0.366, rely=0.4, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.682, rely=0.4, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.05, rely=0.55, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.366, rely=0.55, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.682, rely=0.55, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.05, rely=0.7, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.366, rely=0.7, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.682, rely=0.7, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.05, rely=0.85, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.366, rely=0.85, relwidth=0.266, relheight=0.1)
        Button(commands).place(relx=0.682, rely=0.85, relwidth=0.266, relheight=0.1)



        #---------------------------------------------------------------------------------------------------
        self.camf = Frame(self.win, bg="black", highlightthickness=1, highlightbackground="dark gray")
        self.camf.place(relx=0.3834, rely=0.093, relwidth=0.61, relheight=0.892)

        self.speedCanvas = Canvas(self.camf)
        self.speedCanvas.place(relx=0.025, rely=0.35, relwidth=0.04, relheight=0.3)

        self.altCanvas = Canvas(self.camf)
        self.altCanvas.place(relx=0.935, rely=0.35, relwidth=0.04, relheight=0.3)

        Frame(self.camf).place(relx=0.025, rely=0.66, relwidth=0.08, relheight=0.03)
        Frame(self.camf).place(relx=0.025, rely=0.7, relwidth=0.08, relheight=0.03)

        Frame(self.camf).place(relx=0.895, rely=0.66, relwidth=0.08, relheight=0.03)
        Frame(self.camf).place(relx=0.895, rely=0.7, relwidth=0.08, relheight=0.03)
        self.win.mainloop()

    def com_update(self):
        baglanti = self.portlar()
        if baglanti in self.valuest:
            pass
        else:
            self.valuest.append(baglanti)
        self.ctype["values"] = self.valuest
        self.ctype.update()

    def wp_update(self):
        pass

    def connectF(self):
        ctype = self.ctype.get()
        if self.connect_control == 0:
            if "com" in ctype:
				self.haber.gonder("baglan",ctype)
                self.cbutton.config(image=self.c)
                self.connect_control = 1
                self.dcLabel.destroy()
                self.cLabel = Label(self.connectf, text="Connect", bg="black", fg="dark gray")
                self.cLabel.place(relx=0.96, rely=0.3)
                Thread(target=self.mapMarker).start()
                #Thread(target=self.camF).start()
                
            else:
                cbaud = int(self.cbaud.get())
                self.haber.gonder("baglan",ctype)
                self.cbutton.config(image=self.c)
                self.connect_control = 1
                self.dcLabel.destroy()
                self.cLabel = Label(self.connectf, text="Connect", bg="black", fg="dark gray")
                self.cLabel.place(relx=0.96, rely=0.3)
                Thread(target=self.mapMarker).start()
                #Thread(target=self.camF).start()
        else:
            self.connect_control = 0
            self.iha.close()
            self.dcLabel = Label(self.connectf, text="Dis\nconnect", bg="black", fg="dark gray")
            self.dcLabel.place(relx=0.96, rely=0.18)
            self.cbutton.config(image=self.dc)
    
    def mapMarker(self):
        self.ucak = Image.open("image/plane.png")
        ucak1 = self.ucak.resize((60,60))
        ucak1 = ImageTk.PhotoImage(ucak1)
        home_loc = self.data_gsc.request_home_pos()
        self.marker = self.mapWidget.set_marker(home_loc.latitude / 1e7, home_loc.longitude / 1e7, icon=ucak1)
        while True:
            if self.connect_control == 1:
                rotate = self.ucak.rotate(-float(self.data_gsc.vfr_hud().heading))
                resize = rotate.resize((60, 60))
                ucak = ImageTk.PhotoImage(resize)
                # -------------------
                self.marker.delete()
                loc = str(self.haber.loc).split(",")
                self.marker = self.mapWidget.set_marker(float(loc[0][4::]),
                                                        float(loc[1][4::]),
                                                        icon=ucak)
                
                self.label11.config(text=str(self.haber.flightmode))
                self.label12.config(text=self.haber.heading)
                self.label21.config(text=float(float(loc[0][4::])))
                self.label22.config(text=float(float(loc[1][4::])))
                self.label31.config(text=self.haber.groundspeed)
                self.label32.config(text=self.haber.next_wp)

                time.sleep(0.2)
            else:
                self.marker.delete()

                self.label11.config(text="00.00")
                self.label12.config(text="00.00")
                self.label21.config(text="00.00")
                self.label22.config(text="00.00")
                self.label31.config(text="00.00")
                self.label32.config(text="00.00")
                break
    
    def camF(self):
        self.video = Label(self.camf, bg="black")
        self.video.pack()        
        while (True):
            if self.connect_control == 1:
                frame = self.haber.goruntu()
                #frame = cv2.imread("image/ucus.png")
                sizex=int((self.win.winfo_width())*0.61)
                sizey=int((self.win.winfo_height()*0.892))
                frame = imutils.resize(frame, width=sizex)
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
                
                pitchsayi = self.iha.attitude.pitch
                pitchsayi = int(-((pitchsayi) * 180) / (3.14159265359))#pitch aci cinsinde oldu
                y1 = int(sizey/2)#resmin y ekseninde orta noktası
                a = (y1*0.95)/30#0.95 yapınca 0.05 üstten boşluk bıraktık. 30 bölmek kalan alanı 30 parçaya böldü
                y1 = int(y1 - (a*(pitchsayi)))#a
                x = int(sizex/2)#x ekseninde orta nokta
                
                roll = float(self.iha.attitude.roll)
                roll = int((roll * 180) / (3.14159265359))
                
                if roll > 0:
                    aci = roll
                    yr = int(float(math.tan(math.radians(aci))) * 70)# 50 demek çizginin soldan orta noktasına x ekseninde 50 pikselolduğu
                    baslangic = (x-70, y1+yr)
                    bitis = (x+70, y1-yr)
                    cv2.line(img, baslangic, bitis, (0,0,0),1)

                elif roll < 0:
                    roll = int(-roll)
                    aci = roll
                    yr = int(float(math.tan(math.radians(aci))) * 70)
                    baslangic = (x-70, y1-yr)
                    bitis = (x+70, y1+yr)
                    cv2.line(img, baslangic, bitis, (0,0,0),1)
                
                elif roll == 0:
                    baslangic = (x-70, y1)
                    bitis = (x+70, y1)
                    cv2.line(img, baslangic, bitis, (0,0,0),1)

                
                #orta nokta çizgisi
                orta_nok = (int(sizex/2), int(sizey/2))
                yro = int(float(math.tan(math.radians(30))) * 50)
                cv2.line(img, (orta_nok[0]-350, orta_nok[1]), (orta_nok[0]-290, orta_nok[1]), (255,0,0),1)
                cv2.line(img, (orta_nok[0]+290, orta_nok[1]), (orta_nok[0]+350, orta_nok[1]), (255,0,0),1)

                cv2.line(img, (orta_nok[0]-50, orta_nok[1]+yro), (orta_nok[0], orta_nok[1]), (255,0,0),2)
                cv2.line(img, (orta_nok[0], orta_nok[1]), (orta_nok[0] + 50, orta_nok[1]+yro), (255,0,0),2)
                cv2.putText(img, str(-pitchsayi), (x-1, y1+15), cv2.FONT_HERSHEY_SIMPLEX , 1, (255, 0, 0), 1, cv2.LINE_AA)


                img = Image.fromarray(img)
                image = ImageTk.PhotoImage(image=img)
                self.video.configure(image=image)
                self.video.image = image
            else:
                self.video.destroy()
                break
    
    def camİnfo(self):
        
        while True:
            pass
    
    def portlar(self):
        baglanti = None
        port = p.comports()
        a = len(port)
        for i in range(0,a):
            #tüm portlar listelenirken COM5 portu varsa baglanti değişkenine atanır ve döngü sonlanır
            if  "COM8" in str(port[i]):
                baglanti = str(port[i])
                baglanti = baglanti.split('-')
                baglanti = baglanti[0]
                baglanti = baglanti.lower()
                return baglanti