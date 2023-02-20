#Pour les modules comme IBLearning faire un telechargement depuis le répo et ne pas le laisser
# https://www.youtube.com/watch?v=3K_79W-RlXc

#METTRE UN DELAI ENTRE CLICK CAR SINON WINDOWS BUG

import keyboard
import time
import ctypes
import numpy as np
import PIL.ImageGrab
import PIL.Image
import winsound
import mss                                                          # Pour le screenshot
import os

TOGGLE_KEY = "alt + space"                                          # Pour allumer le triggerbot

#Vitesse de la réactivité du bot
REACTIVITY_MODE_SLOW = 0
REACTIVITY_MODE_MIDDLE = 1
REACTIVITY_MODE_FAST = 2
REACTIVITY_MODE_INSTANT = 3

#Delait entre click
CLICK_DELAY_SLOW = 2
CLICK_DELAY_MIDDLE = 1
CLICK_DELAY_FAST = 0.5
CLICK_DELAY_INSTANT = 0

#Mode de couleur de detection du bot
COLOR_MODE_YELLOW = 0
COLOR_MODE_RED = 1
COLOR_MODE_PURPLE = 2

#Couleur de detection du bot
COLOR_YELLOW = (255, 255, 100)
COLOR_RED = (255, 100, 100)
COLOR_PURPLE = (250, 100, 250)

class Valorant:
    SCREEN_HEIGHT, SCREEN_WIDTH = (PIL.ImageGrab.grab().size)           #Taille de l'ecran
    PURPLE_R, PURPLE_G, PURPLE_B = (250, 100, 250)                      #Spectre de couleur detectable
    TOLERANCE = 60                                                      #Tolerance de couleur
    GRABZONE = 5                                                        #Box au centre de l'ecran pour savoir si un joueur est dans notre viseur

    clickDelay = CLICK_DELAY_INSTANT
    reactivityMode = REACTIVITY_MODE_INSTANT                            #Vitesse de la réactivité du bot
    colorMode = COLOR_MODE_PURPLE                                       #Couleur de detection
    fps = 0                                                             #Vitesse de detection

    detecting: bool = False

    def __init__(self) -> None:
        """
            Aimbot valorant
            Requis ARDUINO LEONARDO
        """
        pass

    def Start(self) -> None:
        """
            Démarrage du bot
        """
        self.Run()

        return

    def Run(self) -> None:
        """
            Boucle principale du bot
        """
        while True:
            if keyboard.is_pressed(TOGGLE_KEY):
                self.detecting = not self.detecting
                print("Detecting :", self.detecting)
                winsound.Beep(440, 75)
                winsound.Beep(700, 100)
                while keyboard.is_pressed(TOGGLE_KEY):
                    pass
            if self.detecting:
                if self.Detect():
                    if self.reactivityMode == 0:
                        time.sleep(0.5)
                    if self.reactivityMode == 1:
                        time.sleep(0.25)
                    if self.reactivityMode == 2:
                        time.sleep(0.12)
                    if self.reactivityMode == 3:
                        pass
                    self.Click()
                    time.sleep(self.clickDelay)
        return

    def Detect(self) -> bool:
        """
            Detection d'enemie au niveau du curseur
        """
        startTime = time.time()
        frame = self.GetFrame()
        for x in range(0, self.GRABZONE*2):
            for y in range(0, self.GRABZONE*2):
                r, g, b = frame.getpixel((x,y))
                if self.CheckColor(r, g, b):
                    return True
        self.fps = int((time.time() - startTime)*1000)
        return False

    def GetFrame(self):
        """
            Retourne l'image du jeu
        """
        with mss.mss() as sct:
            bbox = (int(self.SCREEN_HEIGHT/2-self.GRABZONE), int(self.SCREEN_WIDTH/2-self.GRABZONE), int(self.SCREEN_HEIGHT/2+self.GRABZONE), int(self.SCREEN_WIDTH/2+self.GRABZONE))
            sct_img = sct.grab(bbox)
            return PIL.Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
    def CheckColor(self, r, g ,b) -> bool:
        """
            Si la couleur correspond selon la tolerance
        """
        return self.PURPLE_R - self.TOLERANCE < r < self.PURPLE_R + self.TOLERANCE and self.PURPLE_G - self.TOLERANCE < g < self.PURPLE_G + self.TOLERANCE and self.PURPLE_B - self.TOLERANCE < b < self.PURPLE_B + self.TOLERANCE
    def Click(self) -> None:
        """
            Execution d'un click
        """
        ctypes.windll.user32.mouse_event(2, 0, 0, 0,0)
        time.sleep(0.25)
        ctypes.windll.user32.mouse_event(4, 0, 0, 0,0)
        return

    def PrintBotConfig(self) -> None:
        """
            Affichage des informations de la configuration du bot
        """
        os.system("cls")
        print("Config du bot")
        print("Taille de l'ecran: " + str(self.SCREEN_HEIGHT) + "x" + str(self.SCREEN_WIDTH))
        print("Couleur de la detection: " + str(self.PURPLE_R) + "x" + str(self.PURPLE_G) + "x" + str(self.PURPLE_B))
        print("Tolerance de la couleur: " + str(self.TOLERANCE))
        print("Mode de detection: " + str(self.reactivityMode))
        print("Couleur de detection: " + str(self.colorMode))
        print("Vitesse de la detection: " + str(self.fps))
        print("")
        return

valorant = Valorant()
winsound.Beep(200, 200)
valorant.Start()

#webcam