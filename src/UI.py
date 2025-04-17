import tkinter as tk
from tkinter import filedialog
import os

def download_videos():
    # קוד ההורדה שלך כאן
    print("מוריד הקלטות...")

root = tk.Tk()
root.title("BGU Tube")

if os.path.exists("../Media/Logo.png"):
    logo = tk.PhotoImage(file="../Media/Logo.png")
    logo = logo.subsample(4, 4)  # Reduce size by half
else:
    print("Error: Logo file not found. Using a placeholder.")
    logo = None

if logo:
    logo_label = tk.Label(root, image=logo)
    logo_label.pack()

btn = tk.Button(root, text="התחל הורדה", command=download_videos)
btn.pack()

root.mainloop()