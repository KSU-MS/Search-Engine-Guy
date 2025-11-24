import pyautogui
import time

# Configuration
NUM_SECTIONS = 10  # Change this to the number of sections you have
DELAY_SHORT = 1  # seconds between actions
DELAY_LONG = 3   # seconds for page loads
SECTION_SPACING = 40  # pixels between sections in the navigation

def setup_positions():
    """
    Setup helper to get screen coordinates.
    Run this first to identify where to click.
    """
    print("Move mouse to each position and press Enter:")
    
    print("1. Position mouse over a section in the navigation pane")
    input("Press Enter...")
    section_pos = pyautogui.position()
    print(f"Section position: {section_pos}")
    
    print("2. Position mouse over the 'File' or menu button")
    input("Press Enter...")
    file_menu_pos = pyautogui.position()
    print(f"File menu position: {file_menu_pos}")
    
    print("3. Position mouse over 'Print' option in menu")
    input("Press Enter...")
    print_pos = pyautogui.position()
    print(f"Print position: {print_pos}")
    
    print("4. Position mouse over 'Save as PDF' destination")
    input("Press Enter...")
    pdf_pos = pyautogui.position()
    print(f"PDF destination position: {pdf_pos}")
    
    print("5. Position mouse over 'Save' button")
    input("Press Enter...")
    save_pos = pyautogui.position()
    print(f"Save button position: {save_pos}")
    
    return {
        'section': section_pos,
        'file_menu': file_menu_pos,
        'print': print_pos,
        'pdf_dest': pdf_pos,
        'save': save_pos
    }

def export_section_to_pdf(section_number, positions):
    """
    Export a single section to PDF.
    
    Args:
        section_number: Index of the section (0-based)
        positions: Dictionary of screen positions
    """
    print(f"\nExporting Section {section_number + 1}...")
    
    # Click on the section
    # Adjust y-position based on section index (spacing between sections)
    section_y = positions['section'].y + (section_number * SECTION_SPACING)
    pyautogui.click(positions['section'].x, section_y)
    time.sleep(DELAY_LONG)
    
    # Open File menu (Ctrl+P for print is more reliable)
    print("Opening print dialog...")
    pyautogui.hotkey('ctrl', 'p')
    time.sleep(DELAY_LONG)
    
    # Click on PDF destination
    print("Selecting PDF destination...")
    pyautogui.click(positions['pdf_dest'])
    time.sleep(DELAY_SHORT)
    
    # Click Save
    print("Saving PDF...")
    pyautogui.click(positions['save'])
    time.sleep(DELAY_SHORT)
    
    # Type filename using section number and timestamp
    filename = f"OneNote_Section_{section_number + 1}_{int(time.time())}"
    pyautogui.write(filename, interval=0.05)
    time.sleep(DELAY_SHORT)
    
    # Press Enter to save
    pyautogui.press('enter')
    time.sleep(DELAY_LONG)
    
    print(f"✓ Exported: {filename}.pdf")
    
    # Close any dialogs (press Escape)
    pyautogui.press('esc')
    time.sleep(DELAY_SHORT)

def main():
    """Main execution function."""
    print("OneNote Web to PDF Exporter")
    print("=" * 50)
    print("\nIMPORTANT: Before running the export:")
    print("1. Open OneNote in your web browser")
    print("2. Make sure the notebook is open")
    print("3. Ensure sections are visible in the navigation")
    print(f"4. Set NUM_SECTIONS = {NUM_SECTIONS} (update if needed)")
    print("\nStarting in 5 seconds...")
    print("Press Ctrl+C to cancel")
    time.sleep(5)
    
    # Run setup to get positions
    choice = input("\nRun position setup? (y/n): ")
    if choice.lower() == 'y':
        positions = setup_positions()
    else:
        # Use hardcoded positions (update these with your values)
        print("\nUsing default positions (update these in the script!)")
        positions = {
            'section': pyautogui.Point(100, 200),
            'file_menu': pyautogui.Point(50, 50),
            'print': pyautogui.Point(100, 150),
            'pdf_dest': pyautogui.Point(400, 300),
            'save': pyautogui.Point(600, 500)
        }
    
    # Confirm before starting
    input(f"\nReady to export {NUM_SECTIONS} sections. Press Enter to start...")
    
    # Export each section
    for i in range(NUM_SECTIONS):
        try:
            export_section_to_pdf(i, positions)
        except KeyboardInterrupt:
            print("\n\nExport cancelled by user")
            break
        except Exception as e:
            print(f"Error exporting section {i + 1}: {e}")
            input("Press Enter to continue to next section or Ctrl+C to cancel...")
            continue
    
    print("\n" + "=" * 50)
    print("Export complete!")
    print(f"Exported {NUM_SECTIONS} sections to PDF")

if __name__ == "__main__":
    # Safety feature - move mouse to corner to abort
    pyautogui.FAILSAFE = True
    
    # Uncomment to run setup only
    # setup_positions()
    
    # Run main export
    main()