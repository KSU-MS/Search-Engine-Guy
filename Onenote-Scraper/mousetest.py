import pyautogui
import time

print("Moving mouse in 3 seconds...")
time.sleep(3)
pyautogui.moveTo(500, 500, duration=1)
print("Mouse moved!")