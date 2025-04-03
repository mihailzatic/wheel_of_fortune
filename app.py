import sys
import threading
import time
import textwrap
import pygame  # For sound effects

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class WheelOfFortuneApp(QMainWindow):
    def __init__(self, file_path="phrases.txt", image_path="roata.jpg"):
        super().__init__()
        self.setWindowTitle("Wheel of Fortune")
        self.showFullScreen()  # Full-screen mode
        self.setStyleSheet("background-color: black;")
        
        # Initialize pygame for sound effects
        pygame.mixer.init()
        self.load_sounds()
        
        self.file_path = file_path
        self.image_path = image_path
        self.load_phrases()
        self.current_round = -1  # Start with image first
        self.flashing = False  # Controls flashing animation
        self.showing_image = True  # Controls when image is displayed

        self.letters = set()
        self.revealed_letters = set()
        self.letter_labels = []  # List of tuples: (character, QLabel)

        # Set up the central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.display_image()  # Show image first

    def load_sounds(self):
        """Loads sound effects."""
        self.reveal_sound = pygame.mixer.Sound("reveal.wav")
        self.wrong_sound = pygame.mixer.Sound("wrong.wav")

    def load_phrases(self):
        """Reads phrases from the text file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.phrases = [line.rstrip().upper() for line in file if line.strip()]
        except FileNotFoundError:
            self.phrases = ["O FRAZĂ ESTE O SELECȚIE SCURTĂ DE CUVINTE CARE CREEAZĂ UN CONCEPT"]

    def display_image(self):
        """Displays the image before the next round starts."""
        self.clear_layout()
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(self.image_path)
        
        # Resize pixmap to fit the screen while keeping aspect ratio
        screen_rect = QApplication.desktop().screenGeometry()
        pixmap = pixmap.scaled(screen_rect.width(), screen_rect.height(),
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        self.layout.addWidget(label)
        self.showing_image = True

    def display_phrase(self):
        """Displays the current phrase in a grid-like layout."""
        self.clear_layout()
        if self.current_round >= len(self.phrases):
            self.display_image()  # Show image instead of "Game Over"
            return

        self.letter_labels = []
        self.revealed_letters.clear()
        self.flashing = False
        self.showing_image = False

        phrase = self.phrases[self.current_round]
        # Unique letters (excluding spaces and commas)
        self.letters = set(phrase.replace(" ", "").replace(",", ""))
        wrapped_lines = textwrap.wrap(phrase, width=14)

        board_widget = QWidget()
        board_layout = QVBoxLayout(board_widget)
        board_layout.setAlignment(Qt.AlignCenter)

        for line in wrapped_lines:
            line_widget = QWidget()
            line_layout = QHBoxLayout(line_widget)
            for char in line:
                # For spaces, we display the space; for commas, display immediately.
                display_text = "" if char not in " ," else char
                lbl = QLabel(display_text)
                lbl.setFixedSize(60, 60)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Arial", 24, QFont.Bold))
                if char == " ":
                    lbl.setStyleSheet("background-color: #004400; color: black; border: 1px solid white;")
                else:
                    lbl.setStyleSheet("background-color: #00ff00; color: black; border: 1px solid white;")
                line_layout.addWidget(lbl)
                self.letter_labels.append((char, lbl))
            board_layout.addWidget(line_widget)
        self.layout.addWidget(board_widget)

    def clear_layout(self):
        """Removes all widgets from the layout."""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def keyPressEvent(self, event):
        # Check for Enter key to trigger the next round
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.next_round()
            return

        # Ignore key presses when image is displayed
        if self.showing_image:
            return

        # Read the character from the event; this should support diacritice
        char = event.text().upper()

        # Immediately reveal commas
        if char == ",":
            for letter, lbl in self.letter_labels:
                if letter == ",":
                    lbl.setStyleSheet("background-color: #27AE60; color: white; border: 1px solid white;")
            return

        if char in self.letters:
            if char not in self.revealed_letters:
                self.revealed_letters.add(char)
                self.reveal_sound.play()
                for letter, lbl in self.letter_labels:
                    if letter == char:
                        lbl.setText(char)
                        lbl.setStyleSheet("background-color: #27AE60; color: white; border: 1px solid white;")
                if self.revealed_letters == self.letters:
                    self.start_flashing_effect()
        else:
            self.wrong_sound.play()

    def start_flashing_effect(self):
        """Starts a flashing effect to indicate puzzle completion."""
        if not self.flashing:
            self.flashing = True
            threading.Thread(target=self.flash_effect, daemon=True).start()

    def flash_effect(self):
        colors = ["yellow", "white"]
        while self.flashing:
            for color in colors:
                for _, lbl in self.letter_labels:
                    lbl.setStyleSheet(f"background-color: {color}; color: black; border: 1px solid white;")
                time.sleep(0.3)

    def next_round(self):
        """Moves to the next phrase or displays the image."""
        self.flashing = False
        pygame.mixer.stop()
        if self.showing_image:
            self.current_round += 1
            self.display_phrase()
        else:
            self.display_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WheelOfFortuneApp(file_path="phrases.txt", image_path="roata.jpg")
    window.show()
    sys.exit(app.exec_())
