from dataclasses import dataclass
import numpy as np
from PIL import Image

import pyautogui
import time
import os


NULL_POS_IMG: str = "img/NULL.jpg"


@dataclass
class Word:
    word: str = None
    image: np.ndarray = None


class SourceIO:
    path: str
    cmdPos: tuple
    cmdSize: tuple

    wordList: list[Word]



    def __init__(self) -> None:
        print("setup")
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.__GetNULLPosition()
        if self.cmdPos == None:
            raise Exception("NULL pos not found")
        self.cmdSize = (400, 30)
        self.__LoadWordList()
        print("setup done")
        return
    
    def __LoadWordList(self) -> None:
        """
            Chargement de la liste des images depuis le dossier IMG
        """
        self.wordList = []
        for file in os.listdir("img"):
            if file.endswith(".jpg"): continue
            word = Word(
                word = file.split('.')[0],
                image = np.load("img/"+file)
            )
            self.wordList.append(word)
        return
    
    def __GetNULLPosition(self) -> None:
        """
        Get typing position
        Returns:
            typing position (x, y), None if not found
        """
        self.cmdPos = pyautogui.locateOnScreen(self.path + "/" + NULL_POS_IMG, confidence=0.9)
        return

    def __TakeScreenshot(self) -> np.ndarray:
        return np.asarray(pyautogui.screenshot(region=(self.cmdPos[0], self.cmdPos[1], self.cmdSize[0], self.cmdSize[1])))

    def __DisplayImage(self, img: np.ndarray) -> None:
        Image.fromarray(img).show()
        return

    def __TypeWord(self, word: str) -> None:
        pyautogui.click(self.cmdPos[0], self.cmdPos[1]+50)
        pyautogui.typewrite(word)
        pyautogui.press("enter")
        return

    def __GetWordFromImage(self, image: np.ndarray) -> str:
        """
            Retourne le mots en fonction de l'image
            Retourne None si pas de mots trouvé
        """
        for word in self.wordList:
            if np.array_equal(image, word.image):
                return word.word
        return None
    
    def __GetWord(self) -> str:
        """
            Récupération d'un mots a partir d'un screenshot
            Retourne None si pas trouvé
        """
        image = self.__TakeScreenshot()
        return self.__GetWordFromImage(image)
    
    def __SaveWord(self, word: Word) -> None:
        """
            Sauvegarde d'un mots dans le dossier img
        """
        np.save("img/"+word.word+".npz", word.image)
        return

    def Run(self) -> None:
        """
        Run SourceIO    
        """
        while 1:
            word = self.__GetWord()
            print(word)
            if word is not None:
                if word == "NULL" or word == "" or word == "END":
                    print("NULL word found, skipping")
                else:
                    self.__TypeWord(word)
            else:
                print("No word found")
                image = self.__TakeScreenshot()
                # self.__DisplayImage(image)
                word = input("Enter the word: ")
                word = Word(word, image)
                self.__SaveWord(word)
                self.wordList.append(word)
                print("Word saved")
            time.sleep(0.5)
        return


if __name__ == "__main__":
    sourceIO = SourceIO()
    sourceIO.Run()
