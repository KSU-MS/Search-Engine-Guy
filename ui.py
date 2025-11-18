import tkinter as tk
import search
from tkinter import messagebox

def do_search():
    query = search_box.get("1.0", "end-1c")
    results = search.ui_Search(query)
    messagebox.showinfo(results)

window = tk.Tk()
window.title("Formula Search Thing")
search_text = tk.Label(text="Search:")
search_box = tk.Text(window, height=1, width=50)
search_button = tk.Button(text="⏎", command=do_search())
search_text.grid(row=0, column=0, padx=10, pady=10)
search_box.grid(row=0, column=1, padx=10, pady=10)
search_button.grid(row=0, column=2, padx=10, pady=10)
window.mainloop()