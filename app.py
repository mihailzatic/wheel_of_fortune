import tkinter as tk
from tkinter import ttk
import pygame
import threading
import time
import textwrap
from PIL import Image, ImageTk

class WheelOfFortuneApp:
    def __init__(self, root, file_path="phrases.txt", image_path="roata.jpg"):
        self.root = root
        self.root.title("Wheel of Fortune")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#000000")

        pygame.mixer.init()
        self.load_sounds()

        self.file_path = file_path
        self.image_path = image_path
        self.load_phrases()
        self.current_round = -1
        self.flashing = False
        self.showing_image = True

        self.letters = set()
        self.revealed_letters = set()
        self.letter_labels = []

        self.create_ui()
        self.display_image()
        
        self.root.bind("<KeyPress>", self.reveal_letter)
        self.root.bind("<Return>", self.next_round)
        self.root.bind("3", self.reveal_entire_phrase)


    def load_sounds(self):
        self.reveal_sound = pygame.mixer.Sound("reveal.wav")
        self.wrong_sound = pygame.mixer.Sound("wrong.wav")

    def load_phrases(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.phrases = [line.rstrip().upper() for line in file if line.strip()]
        except FileNotFoundError:
            self.phrases = ["O FRAZĂ ESTE O SELECȚIE SCURTĂ DE CUVINTE CARE CREEAZĂ UN CONCEPT"]

    def create_ui(self):
        self.frame = tk.Frame(self.root, bg="#000000")
        self.frame.pack(expand=True, fill=tk.BOTH)

    def display_image(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        img = Image.open(self.image_path)
        img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img)

        label = tk.Label(self.frame, image=self.tk_image, bg="#000000")
        label.pack(expand=True, fill=tk.BOTH)

        self.showing_image = True
    
    def display_phrase(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        if self.current_round >= len(self.phrases):
            self.display_image()
            return

        self.letter_labels = []
        self.revealed_letters.clear()
        self.flashing = False
        self.showing_image = False

        phrase = self.phrases[self.current_round]
        self.letters = set(phrase.replace(" ", "").replace(",", "").replace("-", ""))
        wrapped_lines = textwrap.wrap(phrase, width=14)

        board_frame = tk.Frame(self.frame, bg="#000000")
        board_frame.pack(expand=True)

        for line in wrapped_lines:
            line_frame = tk.Frame(board_frame, bg="#000000")
            line_frame.pack()
            row_labels = []
            for char in line:
                if char in " ,-.!?":
                    # Punctuation and spaces
                    color = "#004400"
                    lbl = tk.Label(
                        line_frame,
                        text=char,
                        font=("Arial", 48, "bold"),
                        width=2,
                        height=1,
                        relief="ridge",
                        background=color,
                        foreground="black",
                        padx=10,
                        pady=10
                    )
                else:
                    # Regular letters
                    color = "#00ff00"
                    lbl = tk.Label(
                        line_frame,
                        text="",
                        font=("Arial", 48, "bold"),
                        width=2,
                        height=1,
                        relief="ridge",
                        background=color,
                        foreground="black",
                        padx=10,
                        pady=10
                    )
                lbl.pack(side=tk.LEFT, padx=2, pady=2)
                row_labels.append((char, lbl))
            self.letter_labels.extend(row_labels)

    def reveal_letter(self, event):
        if self.showing_image:
            return

        char = event.char.upper()

        # Ignore non-character keys and special keys
        ignored_keys = {"Alt_L", "Alt_R", "Caps_Lock", "Control_L", "Control_R", 
                        "Shift_L", "Shift_R", "BackSpace", "Tab", "Escape", "Return"}
        if event.keysym in ignored_keys or not char.isalpha() and char not in " ,-.!?":
            return

        if char in self.letters:
            if char not in self.revealed_letters:
                self.revealed_letters.add(char)
                self.reveal_sound.play()
                for letter, lbl in self.letter_labels:
                    if letter == char:
                        lbl.config(text=char, background="#27AE60", foreground="white")
                
                if self.revealed_letters == self.letters:
                    self.start_flashing_effect()
        else:
            if char not in self.revealed_letters:
                self.wrong_sound.play()

    def reveal_entire_phrase(self, event=None):
        if self.showing_image:
            return

        self.revealed_letters = self.letters.copy()
        for letter, lbl in self.letter_labels:
            if letter != " " and letter != ",":
                lbl.config(text=letter, background="#27AE60", foreground="white")
        
        self.start_flashing_effect()

    def start_flashing_effect(self):
        if not self.flashing:
            self.flashing = True
            threading.Thread(target=self.flash_effect, daemon=True).start()

    def flash_effect(self):
        colors = ["yellow", "white"]
        while self.flashing:
            for color in colors:
                for _, lbl in self.letter_labels:
                    lbl.config(background=color, foreground="black")
                self.root.update()
                time.sleep(0.3)

    def next_round(self, event=None):
        self.flashing = False
        pygame.mixer.stop()
        if self.showing_image:
            self.current_round += 1
            self.display_phrase()
        else:
            self.display_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = WheelOfFortuneApp(root, file_path="phrases.txt", image_path="roata.jpg")
    root.mainloop()
