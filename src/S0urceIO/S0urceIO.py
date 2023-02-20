import pyautogui
import time
import os
from PIL import Image
from dataclasses import dataclass
import numpy as np

CMD_POS = (612, 835)
CMD_SIZE = (400, 30)

@dataclass
class Word:
    word: str = None
    image: np.ndarray = None

wordList: list[Word] = []

def DisplayArea(nbTime: int = 10):
    for i in range(nbTime):
        pyautogui.moveTo(CMD_POS[0], CMD_POS[1])
        time.sleep(0.1)
        pyautogui.moveTo(CMD_POS[0] + CMD_SIZE[0], CMD_POS[1] + CMD_SIZE[1])
        time.sleep(0.1)
    return

def TakeScreenShot() -> np.ndarray:
    return np.asarray(pyautogui.screenshot(region=(CMD_POS[0], CMD_POS[1], CMD_SIZE[0], CMD_SIZE[1])))

def GetWordList() -> list[Word]:
    # lecture des fichiers du dossier images, le nom du fichier est le mot et l'image est un npz
    for file in os.listdir("images"):
        word = Word()
        word.word = file.split(".")[0]
        word.image = np.load("images/" + file)
        wordList.append(word)
    return wordList

def GetWordFromImage(image: np.ndarray) -> str:
    # recherche du mot le plus proche, si pas de mot, retourne None
    for word in wordList:
        if np.array_equal(image, word.image):
            return word.word
    return None

def GetWord() -> str:
    image = TakeScreenShot()
    return GetWordFromImage(image)

def DisplayImage(image: np.ndarray):
    img = Image.fromarray(image)
    img.show()
    return

def TypeWord(word: str):
    pyautogui.click(CMD_POS[0], CMD_POS[1]+70)
    pyautogui.typewrite(word)
    pyautogui.press("enter")
    return

def SaveWord(word: str, image: np.ndarray):
    np.save("images/" + word + ".npz", image)
    return


print("S0urceIO.py setup")
DisplayArea()
while True:
    print("Check cmd area, please move the green square at the cursor position")
    pyautogui.moveTo(CMD_POS[0], CMD_POS[1])
    confirm = input("Good ? (y/n) ")
    if confirm == "y":
        break
    else:
        print("Reset mouse position")

print("Setup word list")
wordList = GetWordList()

print("Setup done")

print("LET'S HACK !")
while True:
    print(GetWord())
    word = GetWordFromImage(TakeScreenShot())
    if word != None:
        print(word)
        if word == "NULL" or word == "END":
            print("NULL word found, skipping")
        else:
            TypeWord(word)
    else:
        print("No word found")
        image = TakeScreenShot()
        # DisplayImage(image)
        word = input("Enter the word: ")
        SaveWord(word, image)
        wordList.append(Word(word, image))
        print("Word saved")
    time.sleep(0.5)
