import pyautogui
import time
import os
from pathlib import Path

# ---------------- CONFIG ----------------
EXPORT_ROOT = Path.home() / "Documents" / "OneNoteExports"
DELAY = 1.5  # delay between actions (adjust if your PC is slow)
# ----------------------------------------

EXPORT_ROOT.mkdir(exist_ok=True)

# Safety: Move mouse to top-left to abort script
pyautogui.FAILSAFE = True

def click_image(img_path, confidence=0.8):
    """Locate an image on screen and click it."""
    location = None
    while location is None:
        location = pyautogui.locateCenterOnScreen(img_path, confidence=confidence)
        time.sleep(0.5)
    pyautogui.click(location)
    time.sleep(DELAY)

def type_text(text):
    pyautogui.write(text, interval=0.05)
    time.sleep(DELAY)

def export_section(section_name):
    """Exports the current section to a PDF file named section_name."""
    # Click File
    click_image('file_tab.png')

    # Click Export
    click_image('export_button.png')

    # Choose Section
    click_image('export_section_option.png')

    # Choose PDF
    click_image('export_pdf_option.png')

    # Click Export button
    click_image('export_final_button.png')

    # Type the save path
    section_folder = EXPORT_ROOT / section_name
    section_folder.mkdir(exist_ok=True)
    save_path = section_folder / f"{section_name}.pdf"
    type_text(str(save_path))
    pyautogui.press('enter')

    # Return to notebook
    click_image('back_to_notebook.png')

def main():
    print("Starting OneNote export script...")
    time.sleep(3)
    print(f"Make sure the notebook you want is open. Exporting sections to: {EXPORT_ROOT}")

    # Get section tabs along top of notebook
    section_tabs = pyautogui.locateAllOnScreen('section_tab.png', confidence=0.8)
    section_positions = [tab.left + tab.width//2 for tab in section_tabs]

    for i, section_x in enumerate(section_positions):
        # Click on section tab
        pyautogui.click(section_x, 50)  # y=50 approx top row
        time.sleep(DELAY)

        section_name = f"Section_{i+1}"  # You can optionally read the section name from OCR
        print(f"Exporting {section_name}...")
        export_section(section_name)

    print("✔ All sections exported!")

if __name__ == "__main__":
    main()
