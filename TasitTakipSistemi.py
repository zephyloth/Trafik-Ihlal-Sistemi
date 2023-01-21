import math

class TasitAlanBilgisi:
   def __init__(self, LokX, LokY, Genislik, Uzunluk, ID):
     self.LokX = LokX
     self.LokY = LokY
     self.Genislik = Genislik
     self.Uzunluk = Uzunluk
     self.ID = ID

class TasitTakipSistemi:
    def __init__(self):
        # Store the center positions of the objects
        self.TasitLokasyonlari = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.TasitIDSayaci = 0

    def Guncelle(self, GoruntuBilgileri):
        # Objects boxes and ids
        TasitAlanBilgileri = []

        # Get center point of new object
        for Dortgen in GoruntuBilgileri:
            x, y, w, h = Dortgen
            OrtaX = x + (w // 2)
            OrtaY = y + (h // 2)

            # Find out if that object was detected already
            TasitKayitli  = False
            for ID, Lokasyon in self.TasitLokasyonlari.items():
                Uzaklik = math.hypot(OrtaX - Lokasyon[0], OrtaY - Lokasyon[1])

                if Uzaklik < 140:
                    self.TasitLokasyonlari[ID] = (OrtaX, OrtaY)
                    TasitAlanBilgileri.append(TasitAlanBilgisi(x, y, w, h, ID))
                    TasitKayitli = True
                    break

            # New object is detected we assign the ID to that object
            if TasitKayitli is False:
                self.TasitLokasyonlari[self.TasitIDSayaci] = (OrtaX, OrtaY)
                TasitAlanBilgileri.append(TasitAlanBilgisi(x, y, w, h, self.TasitIDSayaci))
                self.TasitIDSayaci += 1

        # Clean the dictionary by center points to remove IDS not used anymore
        GuncelTasitLokasyonlari = {}
        for tasitAlanBilgisi in TasitAlanBilgileri:
            GuncelTasitLokasyonlari[tasitAlanBilgisi.ID] = self.TasitLokasyonlari[tasitAlanBilgisi.ID]

        # Update dictionary with IDs not used removed
        self.TasitLokasyonlari = GuncelTasitLokasyonlari.copy()
        return TasitAlanBilgileri


