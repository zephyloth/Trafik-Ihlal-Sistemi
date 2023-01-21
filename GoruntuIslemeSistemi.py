#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import cv2
from TasitTakipSistemi import *
from TrafikSinyalSistemi import *
import tkinter as tk
from tkinter import filedialog
import numpy as np
import time

class TasitTrafikBilgisi:
   IhlalDurumu, TrafikKonumu = 0,0

class GoruntuIslemeSistemi:
  def click_event(self, event, x, y, flags, params):
    if self.Menu != 2 and self.Menu != 3: return
    if event == cv2.EVENT_LBUTTONDOWN:
      self.SeciliNoktalar.append([x,y])
      NoktaSayisi = len(self.SeciliNoktalar)
  

      if NoktaSayisi < 2:
        print(str(NoktaSayisi + 1) + ". Noktayi Seciniz")
      elif NoktaSayisi == 2:
        if self.Menu == 2:
          self.CizgiBaslangic = self.SeciliNoktalar[0]
          self.CizgiBitis = self.SeciliNoktalar[1]  
          print(self.CizgiBaslangic)
        elif self.Menu == 3:
          self.LambaBaslangic = self.SeciliNoktalar[0]
          self.LambaBitis = self.SeciliNoktalar[1]
          print(self.LambaBitis)
          self.SeciliNoktalar.clear()
          self.Menu = -1
 
  TakipSistemi = TasitTakipSistemi()
  SinyalSistemi = TrafikSinyalSistemi()
  
  CizgiBaslangic = [120,250]
  CizgiBitis = [557, 234]
  LambaBaslangic = [240,98]
  LambaBitis = [255, 155]
  
  NesneAlgilayici = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
  
  TrafikIhlalAdet =0 
  TrafikBilgileri = {}
   
  Baslat = 1
  Menu = -1
  SeciliNoktalar = []

  def __init__(self):
    root = tk.Tk()
    root.withdraw()
    self.VideoKayit = cv2.VideoCapture(filedialog.askopenfilename())

  def CizgiDenklemi(self, p, q, a, b):
     z1 = (b[0] - a[0]) * (p[1] - a[1]) - (p[0] - a[0]) * (b[1] - a[1])
     z2 = (b[0] - a[0]) * (q[1] - a[1]) - (q[0] - a[0]) * (b[1] - a[1])
  
     if z1 < 0 and z2 < 0: return 1
     else: return -1
  
     return z1
  
  def KenarliYaziCiz(self, Goruntu, Metin, Koordinat, Buyukluk, Kalinlik, Renk):
    MetinBuyuklugu = cv2.getTextSize(Metin, cv2.FONT_HERSHEY_SIMPLEX, Buyukluk, Kalinlik)
    Koordinat = (Koordinat[0] - MetinBuyuklugu[0][0]//2, Koordinat[1] + MetinBuyuklugu[0][1])
    cv2.putText(Goruntu, Metin, Koordinat, cv2.FONT_HERSHEY_SIMPLEX, Buyukluk, (0,0,0), Kalinlik, cv2.LINE_AA)
    cv2.putText(Goruntu, Metin, Koordinat, cv2.FONT_HERSHEY_SIMPLEX, Buyukluk, Renk, Kalinlik - 2, cv2.LINE_AA)
  
  def TasitlariBul(self, Goruntu):
    Goruntu = self.NesneAlgilayici.apply(Goruntu)
    cv2.imshow("ArkaplanMaske", cv2.bitwise_not(Goruntu))
    _, Goruntu = cv2.threshold(Goruntu, 0, 255, cv2.THRESH_BINARY)
    
    #kernel = np.ones((3,3),np.uint8)
    #dilated = cv2.dilate(Goruntu,kernel,iterations = 1)
    Hatlar, _ = cv2.findContours(Goruntu, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    Dortgenler = []
    for Hat in Hatlar:
        #Hatlarin alanini al 
        Alan = cv2.contourArea(Hat) 
        if Alan > 900:
            #Sinirhatlarini al
            x, y, w, h = cv2.boundingRect(Hat)
            cv2.rectangle(self.Ekran, (x, y), (x + w, y + h), (0, 255, 0), 2)                     
            Dortgenler.append([x, y, w, h])
    return Dortgenler

  def Guncelle(self):
    if self.Menu != 2 and self.Menu != 3: 
      ret, self.Ekran = self.VideoKayit.read()
      
      self.Ekran = cv2.resize(self.Ekran, (780, 640), interpolation = cv2.INTER_NEAREST) 
      EkranBoyut = self.Ekran.shape
      ArkaplanMaske = self.Ekran.copy()

      TrafikIsigiBolge = ArkaplanMaske[self.LambaBaslangic[1]:self.LambaBitis[1], self.LambaBaslangic[0]:self.LambaBitis[0]]
      #ArkaplanMaske[98:155, 240:255]
      #img[y:y+h, x:x+w]
      
      SinyalBilgisi = self.SinyalSistemi.TrafikIsigiGoster(TrafikIsigiBolge)
      Dortgenler = self.TasitlariBul(ArkaplanMaske)
      TasitAlanBilgileri = self.TakipSistemi.Guncelle(Dortgenler)
      for TasitAlanBilgisi in TasitAlanBilgileri:
          x, y, w, h, id = TasitAlanBilgisi.LokX, TasitAlanBilgisi.LokY, TasitAlanBilgisi.Genislik, TasitAlanBilgisi.Uzunluk, TasitAlanBilgisi.ID
      
          KenarA = self.CizgiDenklemi([x,y], [x + w, y], self.CizgiBaslangic, self.CizgiBitis)
          KenarB = self.CizgiDenklemi([x + w, y], [x + w, y + h], self.CizgiBaslangic, self.CizgiBitis)
          KenarC = self.CizgiDenklemi([x + w, y + h], [x, y + h], self.CizgiBaslangic, self.CizgiBitis)
          KenarD = self.CizgiDenklemi([x, y + h], [x,y], self.CizgiBaslangic, self.CizgiBitis)
      
          #1 ihlal Var
          #-1 ihlal yok
          YeniTrafikKonumu = -1   
          if KenarA == 1 and KenarB == 1 and KenarC == 1 and KenarD == 1:
            YeniTrafikKonumu = 1
      
          if id in self.TrafikBilgileri:
            EskiTrafikKonumu = self.TrafikBilgileri[id].TrafikKonumu
            if SinyalBilgisi is not None and SinyalBilgisi.Renk == "k" and EskiTrafikKonumu * YeniTrafikKonumu < 0:
              self.TrafikBilgileri[id].IhlalDurumu = 1
              self.TrafikIhlalAdet = self.TrafikIhlalAdet + 1
          else:
            self.TrafikBilgileri[id] = TasitTrafikBilgisi();
      
          self.TrafikBilgileri[id].TrafikKonumu = YeniTrafikKonumu
          IhlalDurumu = self.TrafikBilgileri[id].IhlalDurumu
      
          self.KenarliYaziCiz(self.Ekran, "Araba No: " + str(id), (x + w//2, y - 45), 0.6, 4, (255,255,255))
          if IhlalDurumu: 
            self.KenarliYaziCiz(self.Ekran, " Ihlal Var", (x + w//2, y- 25), 0.6, 4, (0,0,255))
          else:
            self.KenarliYaziCiz(self.Ekran, " Ihlal Yok", (x + w//2, y- 25), 0.6, 4, (0,255,0))
      
      if SinyalBilgisi is not None:
        if SinyalBilgisi.Renk == "k":
          self.SinyalSistemi.TrafikCizgisiGoster(self.Ekran, self.CizgiBaslangic, self.CizgiBitis, (0,0,255))
          self.KenarliYaziCiz(self.Ekran, 'Kirmizi', (20 + 240 + SinyalBilgisi.OrjinX, 20 + 98 +SinyalBilgisi.OrjinY), 0.7, 4, (0,0,255))
          cv2.circle(self.Ekran, (240 + SinyalBilgisi.OrjinX, 98 + SinyalBilgisi.OrjinY), SinyalBilgisi.Yaricap + 10, (0, 0, 255), 2)
        if SinyalBilgisi.Renk  == "y":
          self.SinyalSistemi.TrafikCizgisiGoster(self.Ekran, self.CizgiBaslangic, self.CizgiBitis, (0,255,0))
          self.KenarliYaziCiz(self.Ekran, 'Yesil', (20 + 240 + SinyalBilgisi.OrjinX, 20 + 98 +SinyalBilgisi.OrjinY), 0.7, 4, (0,255,0))
          cv2.circle(self.Ekran, (240 + SinyalBilgisi.OrjinX, 98 + SinyalBilgisi.OrjinY), SinyalBilgisi.Yaricap + 10, (0, 255, 0), 2)
        if SinyalBilgisi.Renk  == "s":
          self.SinyalSistemi.TrafikCizgisiGoster(self.Ekran, self.CizgiBaslangic, self.CizgiBitis, (0,255,255))
          self.KenarliYaziCiz(self.Ekran, 'Sari', (20 + 240 + SinyalBilgisi.OrjinX, 20 + 98 +SinyalBilgisi.OrjinY), 0.7, 4, (0,255,255))
          cv2.circle(self.Ekran, (240 + SinyalBilgisi.OrjinX, 98 + SinyalBilgisi.OrjinY), SinyalBilgisi.Yaricap + 10, (0, 255, 255), 2) 
      
      for TasitAlanBilgisi in TasitAlanBilgileri:
        x, y, w, h, id = TasitAlanBilgisi.LokX, TasitAlanBilgisi.LokY, TasitAlanBilgisi.Genislik, TasitAlanBilgisi.Uzunluk, TasitAlanBilgisi.ID
        cv2.rectangle(self.Ekran, (x, y), (x + w, y + h), (0, 255, 0, 128), 2) 
  
      if self.TrafikIhlalAdet > 0:
        self.KenarliYaziCiz(self.Ekran, "Trafik Ihlali: {}".format(self.TrafikIhlalAdet), (EkranBoyut[1] //2, 10), 1.3, 5, (0,0,255))
      else:
        self.KenarliYaziCiz(self.Ekran, "Trafik Ihlali: {}".format(self.TrafikIhlalAdet), (EkranBoyut[1] //2, 10), 1.3, 5, (0,255,0))
    
    cv2.imshow("Ekran", self.Ekran)
    cv2.setMouseCallback("Ekran", self.click_event)

    if self.Baslat == 0: 
      cv2.waitKey(-1)
      self.Baslat = 1
    
    Tus = cv2.waitKey(40)
    if Tus == 27: return 1
    if Tus == 109: 
      print("*****[Menu]*****\n")

      print("1-) Kayit Yukle")
      print("2-) Trafik Cizgisi Belirleme")
      print("3-) Trafik Lambasi Belirleme")
 
      Input = input("Menu Seciniz: ")
      if Input != "":
        self.Menu = int(Input)
        if self.Menu == 1:
          root = tk.Tk()
          root.withdraw()
          Uzanti = filedialog.askopenfilename()
          if self.VideoKayit is not None:
            self.VideoKayit.release()
          self.VideoKayit = cv2.VideoCapture(Uzanti)
        elif self.Menu == 2:
          print("1. Noktayi Seciniz")
    return 0

  def SistemiKapa(self):
    self.VideoKayit.release()
    cv2.destroyAllWindows()
    
goruntuIslemeSistemi = GoruntuIslemeSistemi()

print("asdsad")
while True:
  cv2.waitKey(1)
  if goruntuIslemeSistemi.Guncelle() == 1:
    break
goruntuIslemeSistemi.SistemiKapa()