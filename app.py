import tkinter as tk
from tkinter import ttk
import pygame  # For sound effects
import threading
import time
import textwrap
from PIL import Image, ImageTk  # For displaying images

class WheelOfFortuneApp:
    def __init__(self, root, file_path="phrases.txt", image_path="roata.jpg"):
        self.root = root
        self.root.title("Wheel of Fortune")
        self.root.attributes("-fullscreen", True)  # Full-screen mode
        self.root.configure(bg="#000000")  # Dark background

        pygame.mixer.init()  # Initialize pygame for sounds
        self.load_sounds()

        self.file_path = file_path
        self.image_path = image_path
        self.load_phrases()
        self.current_round = -1  # Start with image first
        self.flashing = False  # Controls flashing animation
        self.showing_image = True  # Controls when image is displayed

        self.letters = set()
        self.revealed_letters = set()
        self.letter_labels = []

        self.create_ui()
        self.display_image()  # Show image first
        
        self.root.bind("<KeyPress>", self.reveal_letter)  # Detect key presses
        self.root.bind("<Return>", self.next_round)  # Enter key for next round

    def load_sounds(self):
        """Loads sound effects."""
        self.reveal_sound = pygame.mixer.Sound("reveal.wav")  # Letter reveal sound
        self.wrong_sound = pygame.mixer.Sound("wrong.wav")  # Wrong letter sound

    def load_phrases(self):
        """Reads phrases from the text file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.phrases = [line.rstrip().upper() for line in file if line.strip()]
        except FileNotFoundError:
            self.phrases = ["O FRAZĂ ESTE O SELECȚIE SCURTĂ DE CUVINTE CARE CREEAZĂ UN CONCEPT"]

    def create_ui(self):
        """Creates the UI layout."""
        self.frame = tk.Frame(self.root, bg="#000000")
        self.frame.pack(expand=True, fill=tk.BOTH)

    def display_image(self):
        """Displays the image before the next round starts."""
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        img = Image.open(self.image_path)
        img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(img)

        label = tk.Label(self.frame, image=self.tk_image, bg="#000000")
        label.pack(expand=True, fill=tk.BOTH)

        self.showing_image = True  # Image is being displayed
    
    def display_phrase(self):
        """Displays the current phrase in a Wheel of Fortune style grid."""
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        if self.current_round >= len(self.phrases):
            self.display_image()  # Show image instead of "Game Over"
            return

        self.letter_labels = []
        self.revealed_letters.clear()
        self.flashing = False
        self.showing_image = False

        phrase = self.phrases[self.current_round]
        self.letters = set(phrase.replace(" ", ""))  # Unique letters
        wrapped_lines = textwrap.wrap(phrase, width=14)  # Ensures multiple rows

        board_frame = tk.Frame(self.frame, bg="#000000")
        board_frame.pack(expand=True)

        for line in wrapped_lines:
            line_frame = tk.Frame(board_frame, bg="#000000")
            line_frame.pack()
            row_labels = []
            for char in line:
                color = "#004400" if char == " " else "#00ff00"  # Dark green for spaces
                lbl = tk.Label(
                    line_frame,
                    text="" if char != " " else " ",
                    font=("Arial", 48, "bold"),
                    width=2,
                    height=1,
                    relief="ridge",
                    background=color,  # Different background for spaces
                    foreground="black",
                    padx=10,
                    pady=10
                )
                lbl.pack(side=tk.LEFT, padx=2, pady=2)
                row_labels.append((char, lbl))
            self.letter_labels.extend(row_labels)

    def reveal_letter(self, event):
        """Reveals letters when pressed and checks if the phrase is fully revealed."""
        if self.showing_image:
            return  # Ignore key presses when image is displayed

        # Map keys 1 and 2 to ș and ț
        key_map = {"1": "Ș", "2": "Ț"}
        char = key_map.get(event.char, event.char)  # Map key if applicable

        romanian_map = {"ă": "Ă", "â": "Â", "î": "Î", "ș": "Ș", "ț": "Ț", "Ă": "Ă", "Â": "Â", "Î": "Î", "Ș": "Ș", "Ț": "Ț"}
        char = romanian_map.get(char, char).upper()  # Convert to uppercase if needed

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
                self.wrong_sound.play()  # Play sound for incorrect letter

    def start_flashing_effect(self):
        """Starts the flashing effect when the puzzle is solved."""
        if not self.flashing:
            self.flashing = True
            threading.Thread(target=self.flash_effect, daemon=True).start()

    def flash_effect(self):
        """Flashes letters to indicate completion."""
        colors = ["yellow", "white"]
        while self.flashing:
            for color in colors:
                for _, lbl in self.letter_labels:
                    lbl.config(background=color, foreground="black")
                self.root.update()
                time.sleep(0.3)

    def next_round(self, event=None):
        """Moves to the next phrase or displays the image."""
        self.flashing = False  # Stop flashing
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
