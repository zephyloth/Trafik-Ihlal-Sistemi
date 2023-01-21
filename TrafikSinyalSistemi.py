import os
import cv2
import numpy as np

class SinyalBilgisi:
   def __init__(self, OrjinX, OrjinY, Yaricap, Renk):
     self.OrjinX = OrjinX
     self.OrjinY = OrjinY
     self.Yaricap = Yaricap
     self.Renk = Renk

class TrafikSinyalSistemi:
	
    def TrafikCizgisiGoster(self, Goruntu, Nokta1, Nokta2 , Renk):
      cv2.line(Goruntu, (Nokta1[0], Nokta1[1] - 10),(Nokta2[0],Nokta2[1] - 10), Renk, 1)            
      cv2.line(Goruntu, (Nokta1[0],Nokta1[1]), (Nokta2[0],Nokta2[1]), Renk, 3)
      cv2.line(Goruntu, (Nokta1[0],Nokta1[1] + 10),(Nokta2[0],Nokta2[1] + 10), Renk, 1)

    def RenkOrtalamasiAl(self, Goruntu, X, Y, Yaricap):
      h, s = 0.0, 1.0
      GoruntuSiniri = Goruntu.shape

      for ry in range(Yaricap * -1, Yaricap):
        for rx in range(Yaricap * -1, Yaricap):
          if (Y + ry) >= GoruntuSiniri[0] or (X + rx) >= GoruntuSiniri[1]:
            continue

          h += Goruntu[Y + ry, X + rx]
          s += 1  
      return h / s

    def TrafikIsigiGoster(self, Goruntu):
      HSVGoruntu = cv2.cvtColor(Goruntu, cv2.COLOR_BGR2HSV)
      #cv2.imshow("HSV",hsv)

      Kirmizi_Alt1 = np.array([0,100,100])
      Kirmizi_Ust1 = np.array([0,255,255])
      Kirmizi_Alt2 = np.array([170,100,100])  
      Kirmizi_Ust2 = np.array([180,255,255])
    
      Yesil_Alt = np.array([40,50,50])
      Yesil_Ust = np.array([90,255,255])
      
      Sari_Alt1 = np.array([15,150,150])
      Sari_Ust1 = np.array([35,255,255])  
      Sari_Alt2 = np.array([1,100,100])
      Sari_Ust2 = np.array([14,255,255])

      Maske_K1 = cv2.inRange(HSVGoruntu, Kirmizi_Alt1, Kirmizi_Ust1)
      Maske_K2 = cv2.inRange(HSVGoruntu, Kirmizi_Alt2, Kirmizi_Ust2)
      Maske_Y = cv2.inRange(HSVGoruntu, Yesil_Alt, Yesil_Ust)
      Maske_S1 = cv2.inRange(HSVGoruntu, Sari_Alt1, Sari_Ust1)
      Maske_S2 = cv2.inRange(HSVGoruntu, Sari_Alt2, Sari_Ust2)
      Maske_K = cv2.add(Maske_K1, Maske_K2)
      Maske_S = cv2.add(Maske_S1, Maske_S2)

      #cv2.imshow("Maske_K",Maske_K)
      #cv2.imshow("Maske_S",Maske_S)
      GoruntuSiniri = Goruntu.shape
 
      KirmiziDaireler = cv2.HoughCircles(Maske_K, cv2.HOUGH_GRADIENT, 1, 80, param1=75, param2=5, minRadius=0, maxRadius=30)
      YesilDaireler = cv2.HoughCircles(Maske_Y, cv2.HOUGH_GRADIENT, 1, 60,param1=50, param2=10, minRadius=0, maxRadius=30)
      SariDaireler = cv2.HoughCircles(Maske_S, cv2.HOUGH_GRADIENT, 1, 30,param1=50, param2=5, minRadius=0, maxRadius=30)

      if KirmiziDaireler is not None:
        KirmiziDaireler = np.uint16(np.around(KirmiziDaireler))
        for Daire in KirmiziDaireler[0, :]:
          OrtRenk = self.RenkOrtalamasiAl(Maske_K, Daire[0], Daire[1], Daire[2])
          if OrtRenk > 30:
            return SinyalBilgisi(Daire[0], Daire[1], Daire[2], "k")

      elif YesilDaireler is not None:   
        YesilDaireler = np.uint16(np.around(YesilDaireler))
        for Daire in YesilDaireler[0, :]: 
          OrtRenk = self.RenkOrtalamasiAl(Maske_Y, Daire[0], Daire[1], Daire[2])
          if OrtRenk > 30:
            return SinyalBilgisi(Daire[0], Daire[1], Daire[2], "y")
    
      elif SariDaireler is not None:
        SariDaireler = np.uint16(np.around(SariDaireler))
        for Daire in SariDaireler[0, :]:       
          OrtRenk = self.RenkOrtalamasiAl(Maske_S, Daire[0], Daire[1], Daire[2])
          if OrtRenk > 30:
            return SinyalBilgisi(Daire[0], Daire[1], Daire[2], "s") 