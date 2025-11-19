import pyautogui
import time
import os
from pathlib import Path
from PIL import Image
import pytesseract

# ---------------- CONFIG ----------------
EXPORT_ROOT = Path.home() / "Documents" / "OneNoteExports"
DELAY = 1.5  # delay between actions (adjust if needed)
SECTION_Y = 50  # approximate Y coordinate for section tabs
SECTION_HEIGHT = 30  # height of section tab area for OCR
# ----------------------------------------

EXPORT_ROOT.mkdir(exist_ok=True)
pyautogui.FAILSAFE = True

# Update this path if Tesseract is not in your PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
    """Exports the current section to a PDF file named after section_name."""
    click_image('file_tab.png')
    click_image('export_button.png')
    click_image('export_section_option.png')
    click_image('export_pdf_option.png')
    click_image('export_final_button.png')

    # Save path
    section_folder = EXPORT_ROOT / section_name
    section_folder.mkdir(exist_ok=True)
    save_path = section_folder / f"{section_name}.pdf"
    type_text(str(save_path))
    pyautogui.press('enter')

    # Return to notebook
    click_image('back_to_notebook.png')

def read_section_name(x_start, x_end):
    """Take a screenshot of the section tab and use OCR to read its name."""
    screenshot = pyautogui.screenshot(region=(x_start, SECTION_Y, x_end - x_start, SECTION_HEIGHT))
    text = pytesseract.image_to_string(screenshot)
    text = text.strip().replace("\n", "_")  # Clean up OCR result
    if not text:
        text = "UnnamedSection"
    return text

def main():
    print("Starting OneNote export script with OCR section names...")
    time.sleep(3)
    print(f"Make sure the notebook you want is open. Exporting sections to: {EXPORT_ROOT}")

    # Detect section tabs
    section_tabs = list(pyautogui.locateAllOnScreen('section_tab.png', confidence=0.8))
    if not section_tabs:
        print("No section tabs found. Make sure 'section_tab.png' matches your tabs.")
        return

    for tab in section_tabs:
        # Click on the section tab
        pyautogui.click(tab.left + tab.width//2, tab.top + tab.height//2)
        time.sleep(DELAY)

        # Read section name using OCR
        section_name = read_section_name(tab.left, tab.left + tab.width)
        print(f"Exporting section: {section_name}")

        # Export PDF
        export_section(section_name)

    print("✔ All sections exported!")

if __name__ == "__main__":
    main()
