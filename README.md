# Wheel of Fortune 🎡

A Python-based desktop application inspired by the classic "Wheel of Fortune" game. Built with Tkinter and Pygame, this version features a custom diacritic engine designed specifically to handle the Romanian alphabet smoothly.

## Features
* **Smart Diacritic Mapping:** Typing a base letter automatically reveals its associated Romanian diacritics (e.g., typing `A` reveals `A`, `Ă`, and `Â`).
* **Dynamic Board:** The UI automatically scales the font and grid size to fit long phrases on the screen.
* **Multimedia Support:** Plays sound effects for correct and incorrect guesses, and displays a custom background image between rounds.
* **Failsafe Design:** The app will continue to run smoothly even if image or sound files are missing from the directory.

## File Structure
* `app.py`: The main application script.
* `phrases.txt`: A text file containing the phrases to be guessed (one phrase per line).
* `wheel.jpg`: The background image displayed between rounds.
* `reveal.wav`: Sound effect played when a correct letter is guessed.
* `wrong.wav`: Sound effect played when an incorrect letter is guessed.

## Prerequisites
Make sure you have Python 3 installed. You will also need to install the required external libraries:

```bash
pip install pygame pillow
```

## How to Run
1. Clone or download this repository.
2. Open your terminal or command prompt in the project folder.
3. Run the following command:

```bash
python app.py
```

## Controls
* **Keyboard Letters:** Type any letter to guess it.
* **Enter (Return):** Move to the next round / switch between the wheel image and the puzzle board.
* **Number 3:** Instantly reveal the entire phrase (admin cheat code).
