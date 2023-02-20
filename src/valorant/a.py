# IssouBotValorantBot
from threading import Thread

import mss                                                                                  # Pour le screenshot
import PIL.ImageGrab
import PIL.Image
import numpy as np
from cv2 import cv2                                                         #Computer Vision
import time                                                                 #Pour calculd de fps
import serial                                                               #Pour le mouvement de sourie
import keyboard


###SETUP###
GameScreenSizeW, GameScreenSizeH = (PIL.ImageGrab.grab().size)           #Taille de l'ecran
CenterBox = 200 #Box d'analyse au centre de l'ecran
ARDUINO = serial.Serial("COM3",9600)
# ARDUINO = None
CoefSpeedMouse = 1                                                             #Coeficient de vitesse de la sourie
###########

###DETECT###
MIN_RED = 195
MAX_RED = 255
MIN_GREEN = 40
MAX_GREEN = 160
MIN_BLUE = 195
MAX_BLUE = 255
############

TOGGLE_KEY = "alt + space"                                          # Pour allumer le triggerbot


###STATS###
def nothing(e):
    pass
scanFPS = 0
ProcessFPS = 0
NbDetectPoint = 0
###########

###STATES###
COMPUTERVISION = False
COMPUTERVISION_FULLVIEW = False
ENEMY_DETECTER = False
AUTOAIM = False
############

def GetFrame():
    """
        Retourne l'image du jeu
    """
    with mss.mss() as sct:
        bbox = (int(GameScreenSizeW/2-CenterBox), int(GameScreenSizeH/2-CenterBox), int(GameScreenSizeW/2+CenterBox), int(GameScreenSizeH/2+CenterBox))
        sct_img = sct.grab(bbox)
        return PIL.Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

##########THREAD DEF##########
def Detector():
    global MIN_RED
    global MAX_RED
    global MIN_GREEN
    global MAX_GREEN
    global MIN_BLUE
    global MAX_BLUE
    global screen
    global targets
    global scanFPS
    ScanLoopTime = time.time()                                                  #On prend le temps actuel pour le compteur de fps
    while 1:
        screen = np.array(GetFrame())                                                         #On prend une capture d'ecran du jeux
        #On applique un masque avec les condition de chaque couleur, et chaque pixel sera ensuite un True False en fonction de la couleur
        mask = (screen[:,:,2]>=MIN_RED) & (screen[:,:,2]<=MAX_RED) & (screen[:,:,1]>=MIN_GREEN) & (screen[:,:,1]<=MAX_GREEN) & (screen[:,:,0]>=MIN_BLUE) & (screen[:,:,0]<=MAX_BLUE)
        temp = np.where(mask==True)                                                 #Coordonnée [[Y1,Y2,...],[X1,X2,...]] de chaque pixel correspondant a l'intevalle de couleur
        targets[0] = temp[1]                                                        #On definie les points X
        targets[1] = temp[0]                                                        #On definie les points Y
        scanFPS = 1/(time.time()-ScanLoopTime)                                      #On calcul le nombre de FPS
        ScanLoopTime = time.time()                                                  #On met a jour le temps actuel pour le compteur de fps
##############################

#####VARIABLES#####
screen = []                                                                 #Ecran de jeux
targets = [[],[]]                                                           #Liste des pixels rouge de l'ennemis [[x1,x2],[y1,y2]]
if COMPUTERVISION:
    cv2.namedWindow("IBG")                                                      #On cree la fenetre
    cv2.resizeWindow("IBG",GameScreenSizeW,GameScreenSizeH)                     #On definie la taille de la fenetre
    cv2.createTrackbar('ScanFPS','IBG', 0, 120, nothing)                        #Nombre de FPS du scan
    cv2.createTrackbar('ProcessFPS','IBG', 0, 60, nothing)                      #Nombre de FPS du process (AIM et ComputerVision)
###################


def MoveMouse(prmOffSetX,prmOffSetY):
    ARDUINO.write(bytes(str(prmOffSetX)+";"+str(prmOffSetY), 'utf-8'))
def GetEnemyPos(prmCibles):
    """
    cible : liste des points de la couleurs
    Retourne un point de visé
    """
    aimX = (GameScreenSizeW / 2)                                                #On prend la position X du viseur
    aimY = (GameScreenSizeH / 2)                                                #On prend la position Y du viseur
    # return [prmCibles[0][0]-aimX,0]
    # return [prmCibles[0][0]-aimX,prmCibles[1][0]-aimY]

    #Normalisation de [[x1,x2,x3],[y1,y2,y3]] en [[x1,y1],[x2,y2]]

    pointList = []                                                              #Normalisation des points en [[x,y],[x2,y2]]

    ####Normalisation#### en [[x,y],[x2,y2]]
    for i in range(len(prmCibles[0])):                                          #Pour chaque points
        pointList.append([prmCibles[0][i],prmCibles[1][i]])                         #Normalisation du points en [[x,y],[x2,y2]]
    #####################

    Cible = [0,0]                                                               #Cible
    for i in range(len(pointList)):                                             #Pour chaque points
        Cible[0] += pointList[i][0]                                                 #On ajoute le X du nouveau point 
        Cible[1] += pointList[i][1]                                                 #On ajoute le Y du nouveau point 
    Cible[0] = Cible[0]/len(pointList)                                          #Moyenne des points du cluster en X
    Cible[1] = Cible[1]/len(pointList)                                          #Moyenne des points du cluster en Y
    aimX = (GameScreenSizeW / 2)                                                #On prend la position X du viseur
    aimY = (GameScreenSizeH / 2)                                                #On prend la position Y du viseur
    enemyOffsetX = Cible[0] - aimX                                              #On calcul le deplacement X a effectuer
    enemyOffsetY = Cible[1] - aimY                                              #On calcul le deplacement Y a effectuer
    return [enemyOffsetX,enemyOffsetY]
    


#####SET THREAD#####
detectThread = Thread(target=Detector,args=())
detectThread.start()
####################



ProcessLoopTime = time.time()                                               #On prend le temps actuel pour le compteur de fps
while 1:                                                                    #Boucle infinie
    if ENEMY_DETECTER:
        if(targets[0] != []):                                                       #Si il y a des enemies
            mouseMove = GetEnemyPos(targets.copy())                                     #On récupere la position de visé pour l'enemie
        else:                                                                       #Sinon
            mouseMove = [0,0]                                                           #Pas de déplacement

    if COMPUTERVISION:                                                          #Si la vision d'ordinateur
        displayScreen = screen                                                      #On fait une copie de l'ecran
        if COMPUTERVISION_FULLVIEW:                                                 #Si on doit afficher tout les points de detection
            cible = targets[:]                                                          #On fait une copie des points actuel par valeur et pas par reference
            for z in range(len(cible[0])):                                              #Pour chaque point de detection
                x = cible[0][z]                                                             #On recupere le point X
                y = cible[1][z]                                                             #On recupere le point Y
                cv2.rectangle(displayScreen,(x,y),(x+1,y+1),(0,0,0),3)                      #On trace le rectangle
        else:                                                                       #Sinon
            aimX = (GameScreenSizeW / 2)                                                #On prend la position X du viseur
            aimY = (GameScreenSizeH / 2)                                                #On prend la position Y du viseur
            x = mouseMove[0] + aimX                                                     #On recupere le premier point X
            y = mouseMove[1] + aimY                                                     #On recupere le premier point Y
            cv2.rectangle(displayScreen,(x,y),(x+1,y+1),(0,0,0),3)                      #On trace le rectangle
        
        if displayScreen != []:                                                     #Si l'ecran est definie
            cv2.setTrackbarPos('ScanFPS', 'IBG', int(scanFPS))                               #On affiche la bar des FPS
            cv2.setTrackbarPos('ProcessFPS', 'IBG', int(ProcessFPS))                         #On affiche la bar des ProcessFPS
            cv2.imshow("IBG", displayScreen)                                            #On affiche l'ecran
        if cv2.waitKey(1) & 0xFF == ord('q'):                                       #On attend le retour
            break                                                                       #On arrete l'affichage
        ProcessFPS = 1/(time.time()-ProcessLoopTime)                                #On calcul le nombre de FPS
        ProcessLoopTime = time.time()                                               #On met a jour le temps actuel pour le compteur de fps

    #SHOOT
    if AUTOAIM:                                                                 #Si visé auto
        # MoveMouse(mouseMove[0],mouseMove[1])                                        #On donne le deplacement a l'arduino
        MoveMouse(mouseMove[0]*CoefSpeedMouse,mouseMove[1]*CoefSpeedMouse)                                #On donne le deplacement a l'arduino
        print("Move : "+str(mouseMove[0]*CoefSpeedMouse)+";"+str(mouseMove[1]*CoefSpeedMouse))

    # if keyboard.is_pressed(TOGGLE_KEY):
    #     AUTOAIM = not AUTOAIM
    #     print("Detecting :", AUTOAIM)
    #     while keyboard.is_pressed(TOGGLE_KEY):
    #         pass

    if keyboard.is_pressed("n"):
        MoveMouse(5000,5000)
        print("Move : 5000;5000")
        while keyboard.is_pressed("n"):
            pass