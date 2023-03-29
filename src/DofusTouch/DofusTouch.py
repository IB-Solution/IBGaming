from dataclasses import dataclass
import pyautogui
import time

MODE_MAP = 0
MODE_FIGHT = 1

@dataclass
class MapEnemyImage:
    enemy1FrontLeft = "img/map/enemy/enemy_1_front_left.jpg"
    enemy1FrontRight = "img/map/enemy/enemy_1_front_right.jpg"
    enemy1BackLeft = "img/map/enemy/enemy_1_back_left.jpg"
    enemy1BackRight = "img/map/enemy/enemy_1_back_right.jpg"

@dataclass
class MapImage:
    enemy: MapEnemyImage = MapEnemyImage()
    trigger: str = "img/map/trigger.jpg"

@dataclass
class BattleEnemyImage:
    enemy1FrontLeft = "img/battle/enemy/enemy_front_left.jpg"
    enemy1FrontRight = "img/battle/enemy/enemy_front_right.jpg"
    enemy1BackLeft = "img/battle/enemy/enemy_back_left.jpg"
    enemy1BackRight = "img/battle/enemy/enemy_back_right.jpg"

@dataclass
class BattleEnemyRangeImage:
    enemy1FrontLeft = "img/battle/enemy_range/enemy_attack_range_front_left.jpg"
    enemy1FrontRight = "img/battle/enemy_range/enemy_attack_range_front_right.jpg"
    enemy1BackLeft = "img/battle/enemy_range/enemy_attack_range_back_left.jpg"
    enemy1BackRight = "img/battle/enemy_range/enemy_attack_range_back_right.jpg"

@dataclass
class BattleImage:
    enemy: BattleEnemyImage = BattleEnemyImage()
    enemyRange: BattleEnemyRangeImage = BattleEnemyRangeImage()
    readyButton: str = "img/battle/ready_button.jpg"
    attackRange: str = "img/battle/attack_range.jpg"
    attackButton: str = "img/battle/attack_button.jpg"
    enemyAttackRange: str = "img/battle/enemy_attack_range.jpg"
    endTurnButton: str = "img/battle/end_turn_button.jpg"

@dataclass
class Images:
    map: MapImage = MapImage()
    battle: BattleImage = BattleImage()




class DofusTouch:
    currentMode: int


    def __init__(self) -> None:
        return
    
    def DetectCurrentMode(self) -> None:
        """
            Detects the current mode of the game
        """
        if pyautogui.locateOnScreen(Images.map.trigger, confidence=0.8):
            self.currentMode = MODE_MAP
        else:
            self.currentMode = MODE_FIGHT        
        return
    
    def CatchEnemy(self) -> None:
        """
            Catch the enemy for the fight
        """
        def LaunchFight(enemyPos) -> None:
            """
                Launch the fight
            """
            center = pyautogui.center(enemyPos)
            pyautogui.click(center.x, center.y, clicks=2, interval=0.25)
            return

        if self.currentMode == MODE_MAP:
            if pyautogui.locateOnScreen(Images.map.enemy.enemy1FrontLeft, confidence=0.8):
                print("Enemy 1 front left")
                LaunchFight(pyautogui.locateOnScreen(Images.map.enemy.enemy1FrontLeft, confidence=0.8))
            elif pyautogui.locateOnScreen(Images.map.enemy.enemy1FrontRight, confidence=0.8):
                print("Enemy 1 front right")
                LaunchFight(pyautogui.locateOnScreen(Images.map.enemy.enemy1FrontRight, confidence=0.8))
            elif pyautogui.locateOnScreen(Images.map.enemy.enemy1BackLeft, confidence=0.8):
                print("Enemy 1 back left")
                LaunchFight(pyautogui.locateOnScreen(Images.map.enemy.enemy1BackLeft, confidence=0.8))
            elif pyautogui.locateOnScreen(Images.map.enemy.enemy1BackRight, confidence=0.8):
                print("Enemy 1 back right")
                LaunchFight(pyautogui.locateOnScreen(Images.map.enemy.enemy1BackRight, confidence=0.8))
            else:
                print("No enemy found")
        return

    def Battle(self) -> None:
        """
            KILL THEM ALL
        """
        while pyautogui.locateOnScreen(Images.battle.readyButton, confidence=0.8):
            print("Waiting for the ready button to appear...")
            pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.readyButton, confidence=0.8)))
            time.sleep(1)

        def IsEnemyInRange() -> bool:
            """
                Returns True if an enemy is in range
            """
            if pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1BackLeft, confidence=0.9):
                return True
            elif pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1BackRight, confidence=0.9):
                return True
            elif pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1FrontLeft, confidence=0.9):
                return True
            elif pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1FrontRight, confidence=0.9):
                return True
            else:
                return False

        def AttackEnemyRange() -> None:
            """
                Attacks the enemy in range
            """
            if pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1BackLeft, confidence=0.8):
                pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1BackLeft, confidence=0.8)))
            elif pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1BackRight, confidence=0.8):
                pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1BackRight, confidence=0.8)))
            elif pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1FrontLeft, confidence=0.8):
                pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1FrontLeft, confidence=0.8)))
            elif pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1FrontRight, confidence=0.8):
                pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.enemyRange.enemy1FrontRight, confidence=0.8)))
            return

        # Tant qu'on est en mode combat
        while self.currentMode == MODE_FIGHT:
            time.sleep(5)
            # Attendre notre tour (si le bouton passer son tour est visible)
            while not pyautogui.locateOnScreen(Images.battle.endTurnButton, confidence=0.8):
                time.sleep(1)
                print("Waiting for our turn...")
            
            # Prendre l'attaque
            print("Taking the attack...")
            pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.attackButton, confidence=0.8)))

            # Si un enemy est dans la range d'attaque
            if IsEnemyInRange():
                print("Enemy in range")
                # Attaquer
                print("Attacking enemy...")
                AttackEnemyRange()
            # Sinon
            else:
                print("No enemy in range")
                # Enlever l'attaque
                pass

                # Regarder l'enemy le plus proche

                # Se déplacer vers lui

                # Attendre 3 secondes

                # Prendre l'attaque

                # Si un enemy est dans la range d'attaque
                    # # Attaquer
                    # AttackEnemyRange()
            
            # Enlever l'attaque
            print("Removing the attack...")
            pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.attackButton, confidence=0.8)))

            # Passer son tour
            print("Passing turn...")
            pyautogui.click(pyautogui.center(pyautogui.locateOnScreen(Images.battle.endTurnButton, confidence=0.8)))

            # Detecter le mode actuel
            print("Detecting current mode...")
            self.DetectCurrentMode()
        
        return

bot: DofusTouch = DofusTouch()
bot.DetectCurrentMode()
bot.CatchEnemy()
while bot.currentMode != MODE_FIGHT:
    bot.DetectCurrentMode()
    time.sleep(1)
    print("Waiting for the fight to start...")

print("LET'S DO THIS")
bot.Battle()
