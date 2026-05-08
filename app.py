import tkinter as tk
import pygame
import threading
import time
import textwrap
from PIL import Image, ImageTk

class WheelOfFortuneApp:
    def __init__(self, root, file_path="phrases.txt", image_path="wheel.jpg"):
        self.root = root
        self.root.title("Wheel of Fortune")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#000000")

        # Cache screen dimensions once instead of querying them repeatedly
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.pixel = tk.PhotoImage(width=1, height=1)

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
        try:
            self.reveal_sound = pygame.mixer.Sound("reveal.wav")
            self.wrong_sound = pygame.mixer.Sound("wrong.wav")
        except FileNotFoundError:
            print("Warning: Sound files not found. Continuing without sound.")
            class DummySound:
                def play(self): pass
            self.reveal_sound = DummySound()
            self.wrong_sound = DummySound()

    def load_phrases(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.phrases = [
                    line.rstrip().upper().replace("Ş", "Ș").replace("Ţ", "Ț") 
                    for line in file if line.strip()
                ]
        except FileNotFoundError:
            self.phrases = ["A PHRASE IS A SHORT SELECTION OF WORDS THAT CREATES A CONCEPT"]

    def create_ui(self):
        self.frame = tk.Frame(self.root, bg="#000000")
        self.frame.pack(expand=True, fill=tk.BOTH)

    def _clear_frame(self):
        """Helper method to remove all widgets from the main frame."""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def display_image(self):
        self._clear_frame()
        
        try:
            img = Image.open(self.image_path)
            img = img.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)

            label = tk.Label(self.frame, image=self.tk_image, bg="#000000")
            label.pack(expand=True, fill=tk.BOTH)
        except FileNotFoundError:
            label = tk.Label(self.frame, text="The image is missing", fg="white", bg="black", font=("Arial", 36))
            label.pack(expand=True)

        self.showing_image = True
    
    def display_phrase(self):
        self._clear_frame()
        
        if self.current_round >= len(self.phrases):
            self.display_image()
            return

        self.letter_labels.clear()
        self.revealed_letters.clear()
        self.flashing = False
        self.showing_image = False

        phrase = self.phrases[self.current_round]
        self.letters = set(char for char in phrase if char.isalpha())

        # Determine wrap width based on phrase length
        if len(phrase) > 60:
            wrap_width = 22
        elif len(phrase) > 42:
            wrap_width = 18
        else:
            wrap_width = 14

        wrapped_lines = textwrap.wrap(phrase, width=wrap_width)

        font_size = 64
        box_size = 100

        # Dynamically scale down font if it doesn't fit the screen
        while font_size > 12:
            box_size = int(font_size * 1.5) + 20 
            max_line_len = max([len(line) for line in wrapped_lines] + [1])
            
            total_width = max_line_len * (box_size + 6) 
            total_height = len(wrapped_lines) * (box_size + 10)
            
            if total_width < self.screen_width * 0.85 and total_height < self.screen_height * 0.80:
                break
            font_size -= 2 

        board_frame = tk.Frame(self.frame, bg="#000000")
        board_frame.pack(expand=True)

        for line in wrapped_lines:
            line_frame = tk.Frame(board_frame, bg="#000000")
            line_frame.pack(pady=5)
            
            for char in line:
                is_alpha = char.isalpha()
                is_space = (char == " ")
                
                # Determine colors and borders based on character type
                bg_color = "#00ff00" if is_alpha else ("#004400" if is_space else "#ffffff")
                relief = "flat" if is_space else "raised"
                border = 0 if is_space else 5
                text_content = "" if is_alpha else char

                lbl = tk.Label(
                    line_frame,
                    text=text_content,
                    image=self.pixel,
                    compound="center",
                    font=("Arial", font_size, "bold"),
                    width=box_size,
                    height=box_size,
                    relief=relief,
                    borderwidth=border,
                    background=bg_color,
                    foreground="black"
                )
                lbl.pack(side=tk.LEFT, padx=3, pady=3, expand=False) 
                
                self.letter_labels.append((char, lbl))

    @staticmethod
    def get_equivalent_chars(char):
        """Returns a set of all Romanian diacritics associated with a base letter."""
        groups = [
            {'A', 'Ă', 'Â'},
            {'I', 'Î'},
            {'S', 'Ș', 'Ş'},
            {'T', 'Ț', 'Ţ'}
        ]
        for group in groups:
            if char in group:
                return group
        return {char}

    def reveal_letter(self, event):
        if self.showing_image:
            return

        char = event.char.upper().replace("Ş", "Ș").replace("Ţ", "Ț")

        if not char or len(char) != 1 or not char.isalpha():
            return

        equiv_chars = self.get_equivalent_chars(char)
        
        match_found = False
        newly_revealed = False

        for eq_char in equiv_chars:
            if eq_char in self.letters:
                match_found = True
                if eq_char not in self.revealed_letters:
                    self.revealed_letters.add(eq_char)
                    newly_revealed = True
                    
                    for letter, lbl in self.letter_labels:
                        if letter == eq_char:
                            lbl.config(text=eq_char, background="#ffffff", foreground="black")

        if newly_revealed:
            self.reveal_sound.play()
            if self.revealed_letters == self.letters:
                self.start_flashing_effect()
        elif not match_found:
            self.wrong_sound.play()

    def reveal_entire_phrase(self, event=None):
        if self.showing_image:
            return

        self.revealed_letters = self.letters.copy()
        for letter, lbl in self.letter_labels:
            if letter.isalpha():
                lbl.config(text=letter, background="#ffffff", foreground="black")
        
        self.start_flashing_effect()

    def start_flashing_effect(self):
        if not self.flashing:
            self.flashing = True
            threading.Thread(target=self.flash_effect, daemon=True).start()

    def flash_effect(self):
        colors = ["#f1c40f", "#ffffff"] 
        while self.flashing:
            for color in colors:
                if not self.flashing:
                    break
                for letter, lbl in self.letter_labels:
                    if letter.isalpha():
                        lbl.config(background=color)
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
    app = WheelOfFortuneApp(root, file_path="phrases.txt", image_path="wheel.jpg")
    root.mainloop()