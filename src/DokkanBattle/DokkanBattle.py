from dataclasses import dataclass
from PIL import Image

import numpy as np

import pyautogui
import pygetwindow
import time
import os

"""
    Ajout d'un ecran:
        - Ajouter un dossier dans img
        - Ajouter un trigger.jpg dans le dossier
        - Ajouter les boutons disponible dans le dossier
        - Ajouter les boutons disponible pour arriver sur l'ecran
"""

@dataclass
class Screen:
    name: str                   # Nom de l'ecran actuel pour le nom du dossier
    trigger: str                # Nom du fichier du trigger
    button: dict[str, str]      # Liste des boutons disponible pour aller sur l'ecran suivant {"screenName": "screenImage"}

class DokkanBattle:
    nbButtonRetry: int = 10     # Nombre de fois que l'on va essayer de cliquer sur un bouton
    filepath: str
    screens: dict[str, Screen]          # Liste des ecrans disponible {"screenName": Screen}

    def __init__(self) -> None:
        print("Setup")
        self.filepath = os.path.dirname(os.path.abspath(__file__))
        self.__LoadScreen()

        print("Done Setup")
        return
    
    def GetMainWindow(self) -> tuple[int, int, int, int]:
        """
            - Retourne la fenetre principale de Dokkan Battle
            - (left, top, width, height)
        """
        print("Getting Main Window")
        window: pygetwindow.Window = pygetwindow.getWindowsWithTitle("MEmu")[0]
        return (window.left, window.top, window.width, window.height)
    
    def __LoadScreen(self) -> None:
        """
            - Liste tout les ecrans disponible dans le dossier Screens
        """
        print("Loading Screens")
        self.screens = {}

        for screen in os.listdir(self.filepath + "/img"):
            newScreen = Screen(screen, self.filepath + "/img/" + screen + "/trigger.jpg", {})
            for nextScreen in os.listdir(self.filepath + "/img/" + screen):
                if nextScreen != "trigger.jpg" and nextScreen.endswith(".jpg"):
                    newScreen.button[nextScreen[2:-4]] = self.filepath + "/img/" + screen + "/" + nextScreen
            self.screens[screen] = newScreen
        
        print("Done Loading Screens")
        return
    
    def GetCurrentScreen(self) -> Screen:
        """
            - Retourne l'ecran actuel
            - Retourne None si aucun ecran n'est detecte
        """
        print("Getting Current Screen")
        for screenName in self.screens:
            if pyautogui.locateOnScreen(self.screens[screenName].trigger, confidence=0.9, region=self.GetMainWindow()) != None:
                return self.screens[screenName]
            time.sleep(1)
        return None
    
    def SearchPaths(self, startScreenName: str, finalScreenName: str, visited: list[str] = None, currentPath: list[str] = None) -> list[list[str]]:
        """
            - Recherche le chemin pour aller de l'ecran startScreenName a l'ecran finalScreenName
            - Param:
                - startScreenName: Nom de l'ecran de depart
                - finalScreenName: Nom de l'ecran d'arrive
                - visited: Liste des ecrans deja visite (récurcivité)
                - currentPath: Liste des chemins deja visite (récurcivité)
            - Retourne 
                - Le chemin pour aller de l'ecran startScreenName a l'ecran finalScreenName [startScreenName, ..., finalScreenName]
                - None si aucun chemin n'est trouve
        """
        print(f"Searching Path : {startScreenName} -> {finalScreenName}")
        if visited == None:
            visited: list[str] = []
        else:
            visited = visited.copy()

        if currentPath == None:
            currentPath: list[str] = []
        else:
            currentPath = currentPath.copy()

        visited.append(startScreenName)
        currentPath.append(startScreenName)
        
        if startScreenName == finalScreenName:
            return [currentPath]

        currentScreen: Screen = self.screens[startScreenName]

        allPath: list[list[str]] = []
        for nextScreenName in currentScreen.button:
            if nextScreenName not in visited:
                newpaths = self.SearchPaths(nextScreenName, finalScreenName, visited, currentPath)
                for newpath in newpaths:
                    allPath.append(newpath)

        return allPath
    
    def GoToScreen(self, screenName: str) -> bool:
        """
            - Va sur l'ecran screenName
            - Param:
                - screenName: Nom de l'ecran
            - Retourne:
                - True si l'ecran a ete trouve et que le bot est dessus
                - False si l'ecran n'a pas ete trouve
        """
        print("Go to Screen")
        currentScreen: Screen = self.GetCurrentScreen()
        if currentScreen == None:
            return False
        
        while currentScreen.name != screenName:
            paths: list[list[str]] = self.SearchPaths(currentScreen.name, screenName)
            if len(paths) == 0:
                return False
            
            path: list[str] = min(paths, key=len)
            print(f"Path found : {path}")
            nextScreenName: str = path[1]

            print(f"Go to {nextScreenName}")
            nextScreen: Screen = self.screens[nextScreenName]
        
            method: str = currentScreen.button[nextScreen.name].split("/")[-1][0]
            if method == "C":   # Clique
                result = self.__Click(currentScreen, nextScreen)
                if not result:
                    return False
            # elif method == "S": # Scroll
            #     result = self.__Scroll(currentScreen, nextScreen)
            #     if not result:
            #         return False
            else:              # Erreur
                print(f"Unknown method {method}")
                return False
            
            
            time.sleep(5)
            while True:
                currentScreen = self.GetCurrentScreen()
                if currentScreen == None:
                    print("Can't find current screen, waiting 5s")
                    time.sleep(5)
                else:
                    break        
        return True
    
    def __Click(self, currentScreen: Screen, nextScreen: Screen) -> bool:
        """
            - Clique sur le bouton
        """
        clicked: bool = False
        for i in range(self.nbButtonRetry):
            result = pyautogui.locateOnScreen(currentScreen.button[nextScreen.name], confidence=0.9, region=self.GetMainWindow())
            if result != None:
                clicked = True
                pyautogui.click(result)
                break
            print(f"Retry {i+1}/{self.nbButtonRetry}")
            time.sleep(1)

        if not clicked:
            print(f"Can't find {nextScreen.name} button")
            return False
        return True
    
    def __Scroll(self, currentScreen: Screen, nextScreen: Screen) -> bool:
        """
            - Scroll jusqu'au bouton
        """
        pass

(
    TASK_START_GAME,
    TASK_GET_GIFT,

    TASK_BATTLE_ECOLE_TORTUE,
    TASK_BATTLE_DEFI_MR_SATAN,
    TASK_BATTLE_AVENTURE_DE_PAN
) = range(5)

class TaskManager:
    """
        Gestionnaire des taches
    """
    bot: DokkanBattle

    def __init__(self) -> None:
        print("Setup Task Manager")
        self.bot = DokkanBattle()
        return
    
    def Run(self, tasks: list[int]) -> None:
        """
            - Execute les taches
            - Param:
                - tasks: Liste des taches a executer
        """
        print("Run Tasks")
        for task in tasks:
            # Start Game
            if task == TASK_START_GAME:
                print("TASK : Start Game")
                self.__StartGame()
            
            # Get Gift
            if task == TASK_GET_GIFT:
                print("TASK : Get Gift")
                self.__GetGift()

            # Battle
            elif task == TASK_BATTLE_ECOLE_TORTUE:
                print("TASK : Battle Ecole Tortue")
                self.__Battle_EcoleTortue()
            elif task == TASK_BATTLE_DEFI_MR_SATAN:
                print("TASK : Battle Defi Mr Satan")
                self.__Battle_DefiMrSatan()
            elif task == TASK_BATTLE_AVENTURE_DE_PAN:
                print("TASK : Battle Aventure de Pan")
                self.__Battle_AventureDePan()
        return
    
    def __ScrollUntilOnScreen(self, button: str) -> bool:
        """
            - Scroll jusqu'a ce que le bouton soit sur l'ecran
            - Scroll vers le bas, une fois en bas, scroll vers le haut, si rien alors return False
            - Pour savoir si on est en bas, on regarde le bouton actuel et si c'est le meme avant et apres le scroll alors on est en bas
        """
        buttonPosRatioLeft, buttonPosRatioTop, buttonPosRatioRight, buttonPosRatioDown = (0.0, 0.66, 1.0, 0.05)

        print("Scroll Until On Screen")
        way: int = 1                # 1 = Scroll vers le bas, -1 = Scroll vers le haut

        lastButton = None
        while True:
            windowLeft, windowTop, windowWidth, windowHeight = self.bot.GetMainWindow()
            result = pyautogui.locateOnScreen(button, confidence=0.9, region=(windowLeft, windowTop, windowWidth, windowHeight))
            if result != None:
                return True
            currentButton = pyautogui.screenshot(region=(int(windowLeft + windowWidth*buttonPosRatioLeft), int(windowTop + windowHeight*buttonPosRatioTop), int(windowLeft + windowWidth*buttonPosRatioRight), int(windowTop + windowHeight*buttonPosRatioDown)))
            
            # Show current and last button
            # currentButton.show()
            # if lastButton != None:
            #     lastButton.show()
            
            if lastButton != None and np.array_equal(currentButton, lastButton):
                if way == 1:
                    way = -1
                else:
                    return False
            lastButton = currentButton
            # On clique, on glisse et on relache
            pyautogui.mouseDown(x=windowLeft+windowWidth/2, y=windowTop+windowHeight/1.5)
            pyautogui.moveTo(x=windowLeft+windowWidth/2, y=windowTop+windowHeight/1.5-100*way, duration=0.5)
            pyautogui.mouseUp()
            time.sleep(1)


    def __StartGame(self) -> None:
        """
            - Lance le jeu
        """
        print("Start Game")
        
        # Si on est sur l'ecran de depart
        while True:
            print("Start Game : Waiting for Start Screen")
            if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/StartupScreen.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                print("Start Screen")
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/StartupScreen.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                break
            time.sleep(1)

        # Si on est sur l'ecran du menu de depart
        while True:
            print("Start Game : Waiting for Start Menu")
            if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/StartupMenu.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                print("Start Menu")
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/StartupMenu.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                break
            time.sleep(1)
        
        # On attend que le chargement soit fini
        while pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/StartupMenuWaitLoading.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
            print("Start Game : Waiting for Loading")
            time.sleep(1)
        
        time.sleep(5)
        # Si il y a une video
        finish = False
        if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/Video.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
            print("Video")
            pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/Video_OK.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
        else:
            print("No Video")
            finish = True

        # Tant que la vidéo n'est pas fini (soit connexion bonus OU ####)
        while not finish:
            time.sleep(5)
            # Si connexion bonus
            if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/ConnexionBonus.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                print("Video finish : Connexion Bonus")
                finish = True
            # Si Info
            elif pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/Info.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                print("Video finish : Info")
                finish = True

        # Si connexion bonus
        if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/ConnexionBonus.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
            print("Connexion Bonus")
            pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/ConnexionBonus_OK.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
            time.sleep(5)

        # Si Info
        while True:
            print("Start Game : Waiting for Info")
            if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/Info.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                print("Info")
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/Info_FERMER.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                break
            time.sleep(1)

        # Si Daily connexion
        if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/DailyConnexion.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
            print("Daily Connexion")
            pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/DailyConnexion_OK.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
            time.sleep(5)

        # Si BonusConnexionInfo
        if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/BonusConnexionInfo.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
            print("Bonus Connexion Info")
            pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/BonusConnexionInfo_FERMER.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
            time.sleep(5)

        # Si POPUP
        while True:
            print("Start Game : Waiting for POPUP")
            if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/POPUP_Cancel.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                print("POPUP")
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/START_GAME/POPUP_Cancel.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                break
            time.sleep(1)
        
        time.sleep(5)
        return
    

    def __GetGift(self) -> None:
        """
            - Recupere les cadeaux
        """
        print("Get Gift")
        self.bot.GoToScreen("Cadeaux")
        button = pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/GET_GIFT/ToutRecevoir.jpg", confidence=0.9, region=self.bot.GetMainWindow())
        if button == None:  # Si il y a pas de cadeaux a recuperer
            return
        pyautogui.click(button)
        time.sleep(5)
        pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/GET_GIFT/OK.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
        time.sleep(5)
        pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/GET_GIFT/OK.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
        return

    #### DEFI - PREPARATION ####
    def __Battle_EcoleTortue(self) -> None:
        """
            - Fait la battle Ecole Tortue dans le mode Evenement_Préparation
        """
        print("Battle Ecole Tortue")
        if self.bot.GoToScreen("Evenement_Preparation"):
            if self.__ScrollUntilOnScreen(self.bot.filepath + "/taskimg/BATTLE_ECOLE_TORTUE/BoutonMission.jpg"):
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_ECOLE_TORTUE/BoutonMission.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_ECOLE_TORTUE/RudeEntrainement.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(1)
                # Si déjà fait
                if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_ECOLE_TORTUE/alreadydone.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                    print("Already done")
                    pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_ECOLE_TORTUE/ok.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                    time.sleep(1)
                    return
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_ECOLE_TORTUE/ZHard.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_ECOLE_TORTUE/Start.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)
                self.__WaitBattle()

            else:
                raise Exception("Can't go to Mission with scroll")
        else:
            raise Exception("Can't go to Evenement_Preparation")
    def __Battle_DefiMrSatan(self) -> None:
        """
            - Fait la battle Defi conte M.Satan dans le mode Evenement_Préparation
        """
        print("Battle Defi Mr Satan")
        if self.bot.GoToScreen("Evenement_Preparation"):
            if self.__ScrollUntilOnScreen(self.bot.filepath + "/taskimg/BATTLE_DEFI_MR_SATAN/BoutonMission.jpg"):
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_DEFI_MR_SATAN/BoutonMission.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_DEFI_MR_SATAN/DefiContreMrSatan.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(1)
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_DEFI_MR_SATAN/ZHard.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_DEFI_MR_SATAN/Start.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)
                self.__WaitBattle()

            else:
                raise Exception("Can't go to Mission with scroll")
        else:
            raise Exception("Can't go to Evenement_Preparation")
    def __Battle_AventureDePan(self) -> None:
        """
            - Fait la battle Aventure de Pan dans le mode Evenement_Préparation
        """
        print("Battle Aventure de Pan")
        if self.bot.GoToScreen("Evenement_Preparation"):
            if self.__ScrollUntilOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/BoutonMission.jpg"):
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/BoutonMission.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)

                # Aventure secrete
                if self.__ScrollUntilOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/AventureSecrete.jpg"):
                    pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/AventureSecrete.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                    time.sleep(1)
                    # Si déjà fait
                    if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/alreadydone.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                        print("Already done")
                        pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/ok.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                        time.sleep(1)
                        return
                    pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/ZHard.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                    time.sleep(5)
                    pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/Start.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                    time.sleep(5)
                    self.__WaitBattle()
                else:
                    raise Exception("Can't go to AventureSecrete with scroll")

                # Aventure secrete continue
                if self.__ScrollUntilOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/AventureContinue.jpg"):
                    pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/AventureContinue.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                    time.sleep(1)
                    # Si déjà fait
                    if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/alreadydone.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                        print("Already done")
                        pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/ok.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                        time.sleep(1)
                        return
                    pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/Super.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                    time.sleep(5)
                    pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/BATTLE_AVENTURE_DE_PAN/Start.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                    time.sleep(5)
                    self.__WaitBattle()
                else:
                    raise Exception("Can't go to AventureContinue with scroll")
            else:
                raise Exception("Can't go to Mission with scroll")
        else:
            raise Exception("Can't go to Evenement_Preparation")





    def __WaitBattle(self) -> None:
        """
            - Attend et gère la fin d'une battle
        """
        while True:
            print("Waiting for end of battle")
            time.sleep(5)
            # Si il y a une monté de niveau
            if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/nextlevel.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/nextlevel.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
                time.sleep(5)
                break
            # Si c'est la fin de la battle
            elif pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/endbattle.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
                break
        
        time.sleep(5)
        # Si il y a une boule de cristal
        if pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/bouledecristal.jpg", confidence=0.9, region=self.bot.GetMainWindow()) != None:
            pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/bouledecristal.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
            time.sleep(5)
            pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/bouledecristal_ok.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
            time.sleep(5)
            pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/bouledecristal_ok.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
            time.sleep(5)

        print("Battle ended")
        time.sleep(5)
        pyautogui.click(pyautogui.locateOnScreen(self.bot.filepath + "/taskimg/WAITBATTLE/ok.jpg", confidence=0.9, region=self.bot.GetMainWindow()))
        time.sleep(5)
        return


# bot: DokkanBattle = DokkanBattle()
# print(bot.GetCurrentScreen())
# print(bot.SearchPaths("Accueil", "Equipe"))
# print(bot.GoToScreen("Cadeaux"))
# print(bot.GoToScreen("Evenement_Defi"))
# print(bot.GoToScreen("Accueil"))

taskmanager: TaskManager = TaskManager()
taskmanager.Run([
    # TASK_START_GAME,
    # TASK_GET_GIFT,
    # TASK_BATTLE_ECOLE_TORTUE,
    # TASK_BATTLE_DEFI_MR_SATAN,
    TASK_BATTLE_AVENTURE_DE_PAN
])