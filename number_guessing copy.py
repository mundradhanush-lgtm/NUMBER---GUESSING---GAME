import math
import random
import struct
import subprocess
import sys
import tempfile
import threading
import wave
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


# =========================================================
# COLOURS
# =========================================================

BG = "#08111f"
HEADER = "#111d31"
CARD = "#17263b"
INPUT_BG = "#0d1929"
BORDER = "#304863"

TEXT = "#f5f7fb"
MUTED = "#aebdcb"

GOLD = "#f3c45d"
GOLD_LIGHT = "#fff0ae"
GOLD_SHADOW = "#6a4105"

BLUE = "#3e8ec5"
BLUE_DARK = "#24658f"

GREEN = "#3aa66d"
GREEN_DARK = "#26764c"

RED = "#c65d62"
YELLOW = "#f1b84d"

# Added: visible button text on macOS
BUTTON_TEXT = "#142033"
BUTTON_TEXT_DISABLED = "#4b5d70"


# =========================================================
# 3D TEXT LABEL
# =========================================================

class EmbossedLabel(tk.Canvas):
    """
    Draws text several times to create a small 3D effect.
    """

    def __init__(self,parent,text,font,bg,fg=TEXT,shadow="#05080d",highlight=None,width=250,height=35,anchor="center"):
        super().__init__(
            parent,
            bg=bg,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0
        )

        self.text = text
        self.font = font
        self.fg = fg
        self.shadow = shadow
        self.highlight = highlight
        self.label_width = width
        self.label_height = height
        self.anchor = anchor

        self.draw_text()

    def draw_text(self):
        self.delete("all")

        if self.anchor == "w":
            x = 8
        else:
            x = self.label_width // 2

        y = self.label_height // 2

        self.create_text(
            x + 3,
            y + 3,
            text=self.text,
            font=self.font,
            fill=self.shadow,
            anchor=self.anchor
        )

        self.create_text(
            x,
            y,
            text=self.text,
            font=self.font,
            fill=self.fg,
            anchor=self.anchor
        )

        if self.highlight:
            self.create_text(
                x,
                y - 1,
                text=self.text,
                font=self.font,
                fill=self.highlight,
                anchor=self.anchor
            )

    def set_text(self, text):
        self.text = text
        self.draw_text()

    def set_colour(self, colour):
        self.fg = colour
        self.draw_text()


# =========================================================
# SOUND SYSTEM
# =========================================================

class GameSounds:
    """
    Creates two small WAV sound files automatically:
    a pleasant win sound and a losing sound.
    """

    def __init__(self):
        self.sound_folder = Path(
            tempfile.gettempdir()
        ) / "number_guessing_game_sounds"

        self.sound_folder.mkdir(
            exist_ok=True
        )

        self.win_sound = self.sound_folder / "win.wav"
        self.lose_sound = self.sound_folder / "lose.wav"

        self.create_sounds()

    def create_sounds(self):
        if not self.win_sound.exists():
            self.make_wav(
                self.win_sound,
                [
                    (523.25, 0.16),
                    (659.25, 0.16),
                    (783.99, 0.28),
                ]
            )

        if not self.lose_sound.exists():
            self.make_wav(
                self.lose_sound,
                [
                    (392.00, 0.20),
                    (329.63, 0.20),
                    (261.63, 0.35),
                ]
            )

    def make_wav(self, file_path, notes):
        sample_rate = 44100
        volume = 0.35
        frames = bytearray()

        for frequency, duration in notes:
            total_samples = int(sample_rate * duration)

            for index in range(total_samples):
                fade_in = min(
                    1,
                    index / max(1, sample_rate * 0.02)
                )

                fade_out = min(
                    1,
                    (total_samples - index) /
                    max(1, sample_rate * 0.04)
                )

                envelope = min(fade_in, fade_out)

                value = int(
                    32767
                    * volume
                    * envelope
                    * math.sin(
                        2 * math.pi * frequency
                        * index / sample_rate
                    )
                )

                frames.extend(
                    struct.pack("<h", value)
                )

        with wave.open(str(file_path), "w") as sound_file:
            sound_file.setnchannels(1)
            sound_file.setsampwidth(2)
            sound_file.setframerate(sample_rate)
            sound_file.writeframes(frames)

    def play(self, sound_file):
        thread = threading.Thread(
            target=self.play_in_background,
            args=(sound_file,),
            daemon=True
        )

        thread.start()

    def play_in_background(self, sound_file):
        try:
            if sys.platform == "darwin":
                subprocess.Popen(
                    ["/usr/bin/afplay", str(sound_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            elif sys.platform.startswith("win"):
                import winsound

                winsound.PlaySound(
                    str(sound_file),
                    winsound.SND_FILENAME
                    | winsound.SND_ASYNC
                )

            else:
                subprocess.Popen(
                    ["aplay", str(sound_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

        except Exception:
            pass

    def play_win(self):
        self.play(self.win_sound)

    def play_lose(self):
        self.play(self.lose_sound)


# =========================================================
# MAIN GAME
# =========================================================

class NumberGuessingGame:

    def __init__(self):
        self.difficulty_levels = {
            "Easy": 20,
            "Medium": 15,
            "Hard": 10,
            "Impossible": 5
        }

        self.hint_attempt_requirements={
            "Easy" : 10,
            "Medium" : 8,
            "Hard" : 5,
            "Impossible" : 2
        }

        self.secret_number = None
        self.attempts = 0
        self.max_attempts = 20
        self.hint_used = False

        self.sounds = GameSounds()

        self.build_gui()

    # =====================================================
    # BEST SCORE
    # =====================================================

    def score_file(self):
        difficulty = self.difficulty_var.get().lower()

        return Path(
            f"best_score_{difficulty}.txt"
        )

    def get_best_score(self):
        try:
            content = self.score_file().read_text().strip()

            if content:
                return int(content)

        except (FileNotFoundError, ValueError):
            pass

        return None

    def update_best_score(self):
        old_best = self.get_best_score()

        if old_best is None or self.attempts < old_best:
            self.score_file().write_text(
                str(self.attempts)
            )

            return True, old_best, self.attempts

        return False, old_best, old_best

    # =====================================================
    # HINTS
    # =====================================================

    def get_hint(self):
        difficulty = self.difficulty_var.get()

        if difficulty == "Easy":
            if self.secret_number % 2 == 0:
                return "The secret number is an even number."
            else:
                return "The secret number is an odd number."

        if difficulty == "Medium":
            lower = (
                self.secret_number // 100
            ) * 100

            upper = lower + 99

            if lower == 0:
                lower = 1

            if upper > 1000:
                upper = 1000

            return (
                f"The number is between "
                f"{lower} and {upper}."
            )

        if difficulty == "Hard":
            digit_sum = sum(
                int(digit)
                for digit in str(self.secret_number)
            )

            return (
                f"The sum of its digits is "
                f"{digit_sum}."
            )

        last_digit = self.secret_number % 10

        return (
            f"The last digit of the number is "
            f"{last_digit}."
        )

    def show_hint(self):
        if self.secret_number is None:
            messagebox.showwarning(
                "Start a game",
                "Start a new game before using a hint."
            )
            return

        minimum_attempts = self.hint_attempt_requirements[
            self.difficulty_var.get()
        ]

        if self.attempts < minimum_attempts:
            messagebox.showwarning(
                "Hint locked",
                f"You can use a hint after "
                f"{minimum_attempts} attempts."
            )
            return

        if self.hint_used:
            messagebox.showinfo(
                "Hint already used",
                "You only get one hint per game."
            )
            return

        hint = self.get_hint()

        self.hint_used = True
        self.hint_button.config(
            state="disabled"
        )

        messagebox.showinfo(
            "Your hint",
            hint
        )

        self.status_label.set_text(
            "HINT USED\n"
            "Keep guessing!"
        )
        self.status_label.set_colour(
            "#9ddcf7"
        )

    # =====================================================
    # GAME FUNCTIONS
    # =====================================================

    def start_game(self):
        difficulty = self.difficulty_var.get()

        self.max_attempts = self.difficulty_levels[
            difficulty
        ]

        self.secret_number = random.randint(
            1,
            1000
        )

        self.attempts = 0
        self.hint_used = False

        self.guess_entry.config(
            state="normal"
        )

        self.guess_button.config(
            state="normal"
        )

        self.hint_button.config(
            state="disabled"
        )

        self.difficulty_menu.config(
            state="disabled"
        )

        self.guess_entry.delete(
            0,
            tk.END
        )

        self.history_list.delete(
            0,
            tk.END
        )

        self.status_label.set_text(
            "I picked a secret number.\n"
            "Start guessing!"
        )

        self.status_label.set_colour(
            TEXT
        )

        self.attempts_label.set_text(
            f"Attempts left: {self.max_attempts}"
        )

        best = self.get_best_score()

        if best is None:
            self.best_score_label.set_text(
                "Best Score: No score yet"
            )
        else:
            self.best_score_label.set_text(
                f"Best Score: {best} attempts"
            )

        self.guess_entry.focus_set()

    def check_guess(self):
        if self.secret_number is None:
            messagebox.showwarning(
                "Start a game",
                "Click START NEW GAME first."
            )
            return

        guess_text = self.guess_entry.get().strip()

        try:
            guess = int(guess_text)

        except ValueError:
            messagebox.showwarning(
                "Invalid input",
                "Please type a whole number."
            )

            self.guess_entry.delete(
                0,
                tk.END
            )

            self.guess_entry.focus_set()
            return

        if guess < 1 or guess > 1000:
            messagebox.showwarning(
                "Invalid number",
                "Your guess must be between 1 and 1000."
            )

            self.guess_entry.delete(
                0,
                tk.END
            )

            self.guess_entry.focus_set()
            return

        self.attempts += 1

        remaining = (
            self.max_attempts - self.attempts
        )

        if guess == self.secret_number:
            self.add_history(
                f"Guess {self.attempts}: {guess}  —  CORRECT! 🎉"
            )

            self.sounds.play_win()

            is_new_best, old_best, new_best = (
                self.update_best_score()
            )

            self.status_label.set_text(
                f"CORRECT! 🎉\n"
                f"You found it in {self.attempts} attempts."
            )

            self.status_label.set_colour(
                "#7ce6aa"
            )

            if is_new_best:
                self.best_score_label.set_text(
                    f"Best Score: {new_best} attempts"
                )

                messagebox.showinfo(
                    "New Best Score!",
                    f"You guessed {self.secret_number} "
                    f"in {self.attempts} attempts.\n\n"
                    f"New best score: "
                    f"{new_best} attempts!"
                )

            else:
                messagebox.showinfo(
                    "You Won!",
                    f"You guessed the number "
                    f"{self.secret_number} in "
                    f"{self.attempts} attempts!"
                )

            self.end_game()
            return

        if guess < self.secret_number:
            result = "GO HIGHER ⬆️"

            self.status_label.set_text(
                "GO HIGHER ⬆️"
            )

            self.status_label.set_colour(
                YELLOW
            )

        else:
            result = "GO LOWER ⬇️"

            self.status_label.set_text(
                "GO LOWER ⬇️"
            )

            self.status_label.set_colour(
                YELLOW
            )

        self.add_history(
            f"Guess {self.attempts}: {guess}  —  {result}"
        )

        self.attempts_label.set_text(
            f"Attempts left: {remaining}"
        )

        minimum_attempts = self.hint_attempt_requirements[
            self.difficulty_var.get()
        ]

        if self.attempts >= minimum_attempts and not self.hint_used:
            self.hint_button.config(
                state="normal"
            )

        self.guess_entry.delete(
            0,
            tk.END
        )

        self.guess_entry.focus_set()

        if self.attempts >= self.max_attempts:
            self.add_history(
                f"GAME OVER  —  Number was "
                f"{self.secret_number}"
            )

            self.sounds.play_lose()

            self.status_label.set_text(
                f"GAME OVER 😔\n"
                f"The number was {self.secret_number}."
            )

            self.status_label.set_colour(
                "#ff9aa1"
            )

            self.attempts_label.set_text(
                "Attempts left: 0"
            )

            messagebox.showinfo(
                "Game Over",
                f"You used all attempts.\n\n"
                f"The secret number was "
                f"{self.secret_number}."
            )

            self.end_game()

    def add_history(self, text):
        self.history_list.insert(
            tk.END,
            text
        )

        self.history_list.see(
            tk.END
        )

    def end_game(self):
        self.secret_number = None

        self.guess_entry.config(
            state="disabled"
        )

        self.guess_button.config(
            state="disabled"
        )

        self.hint_button.config(
            state="disabled"
        )

        self.difficulty_menu.config(
            state="normal"
        )

    def quit_game(self):
        self.root.destroy()

    def submit_guess(self, event):
        if str(self.guess_button["state"]) == "normal":
            self.check_guess()

    # =====================================================
    # GUI
    # =====================================================

    def build_gui(self):
        self.root = tk.Tk()

        self.root.title(
            "Number Guessing Game"
        )

        self.root.configure(
            bg=BG
        )

        self.root.geometry(
            "1040x680"
        )

        self.root.minsize(
            880,
            590
        )

        self.root.update_idletasks()

        x = (
            self.root.winfo_screenwidth() - 1040
        ) // 2

        y = (
            self.root.winfo_screenheight() - 680
        ) // 2

        self.root.geometry(
            f"1040x680+{x}+{y}"
        )

        self.root.grid_columnconfigure(
            0,
            weight=1
        )

        self.root.grid_rowconfigure(
            1,
            weight=1
        )

        header_frame = tk.Frame(
            self.root,
            bg=HEADER,
            height=108
        )

        header_frame.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        header_frame.grid_propagate(False)

        heading = EmbossedLabel(
            header_frame,
            text="NUMBER GUESSING GAME",
            font=("Arial", 28, "bold"),
            bg=HEADER,
            fg=GOLD,
            shadow=GOLD_SHADOW,
            highlight=GOLD_LIGHT,
            width=900,
            height=55
        )

        heading.pack(
            pady=(14, 0)
        )

        subheading = EmbossedLabel(
            header_frame,
            text="Can you find the secret number?",
            font=("Arial", 12, "bold"),
            bg=HEADER,
            fg="#d8e4ef",
            shadow="#05080d",
            width=500,
            height=28
        )

        subheading.pack()

        self.hint_button = tk.Button(
            header_frame,
            text="HINT 💡",
            font=("Arial", 10, "bold"),
            command=self.show_hint,
            bg="#6d4d17",
            fg=BUTTON_TEXT,
            activebackground="#987126",
            activeforeground=BUTTON_TEXT,
            disabledforeground=BUTTON_TEXT_DISABLED,
            relief="raised",
            bd=3,
            cursor="hand2",
            padx=14,
            pady=7,
            state="disabled"
        )

        self.hint_button.place(
            relx=1,
            x=-22,
            y=19,
            anchor="ne"
        )

        main_frame = tk.Frame(
            self.root,
            bg=BG
        )

        main_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=28,
            pady=24
        )

        main_frame.grid_columnconfigure(
            0,
            minsize=340
        )

        main_frame.grid_columnconfigure(
            1,
            weight=1
        )

        main_frame.grid_rowconfigure(
            0,
            weight=1
        )

        left_frame = tk.Frame(
            main_frame,
            bg=CARD,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        left_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 18)
        )

        left_frame.grid_columnconfigure(
            0,
            weight=1
        )

        controls_title = EmbossedLabel(
            left_frame,
            text="GAME CONTROLS",
            font=("Arial", 15, "bold"),
            bg=CARD,
            fg=TEXT,
            shadow="#080d16",
            width=290,
            height=35
        )

        controls_title.grid(
            row=0,
            column=0,
            pady=(22, 11)
        )

        difficulty_label = EmbossedLabel(
            left_frame,
            text="DIFFICULTY",
            font=("Arial", 10, "bold"),
            bg=CARD,
            fg=MUTED,
            shadow="#080d16",
            width=270,
            height=25,
            anchor="w"
        )

        difficulty_label.grid(
            row=1,
            column=0,
            padx=28
        )

        self.difficulty_var = tk.StringVar(
            value="Easy"
        )

        self.difficulty_menu = tk.OptionMenu(
            left_frame,
            self.difficulty_var,
            *self.difficulty_levels.keys()
        )

        self.difficulty_menu.config(
            font=("Arial", 12, "bold"),
            bg=INPUT_BG,
            fg=TEXT,
            activebackground="#203853",
            activeforeground=TEXT,
            width=17,
            bd=0,
            highlightthickness=0
        )

        self.difficulty_menu["menu"].config(
            bg=INPUT_BG,
            fg=TEXT,
            activebackground=BLUE,
            activeforeground="white",
            font=("Arial", 12)
        )

        self.difficulty_menu.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=28,
            pady=(4, 11)
        )

        start_button = tk.Button(
            left_frame,
            text="START NEW GAME",
            font=("Arial", 11, "bold"),
            command=self.start_game,
            bg=GREEN,
            fg=BUTTON_TEXT,
            activebackground=GREEN_DARK,
            activeforeground=BUTTON_TEXT,
            relief="raised",
            bd=3,
            cursor="hand2",
            padx=12,
            pady=9
        )

        start_button.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=28,
            pady=(0, 16)
        )

        self.status_label = EmbossedLabel(
            left_frame,
            text=(
                "Choose a difficulty and\n"
                "start a new game."
            ),
            font=("Arial", 11, "bold"),
            bg=INPUT_BG,
            fg=TEXT,
            shadow="#05080d",
            width=280,
            height=70
        )

        self.status_label.grid(
            row=4,
            column=0,
            pady=(0, 11)
        )

        self.attempts_label = EmbossedLabel(
            left_frame,
            text="Attempts left: 0",
            font=("Arial", 13, "bold"),
            bg=CARD,
            fg=YELLOW,
            shadow="#090d13",
            width=280,
            height=30
        )

        self.attempts_label.grid(
            row=5,
            column=0,
            pady=(0, 2)
        )

        self.best_score_label = EmbossedLabel(
            left_frame,
            text="Best Score: No score yet",
            font=("Arial", 11, "bold"),
            bg=CARD,
            fg="#7ce6aa",
            shadow="#090d13",
            width=280,
            height=30
        )

        self.best_score_label.grid(
            row=6,
            column=0,
            pady=(0, 13)
        )

        guess_label = EmbossedLabel(
            left_frame,
            text="YOUR GUESS",
            font=("Arial", 10, "bold"),
            bg=CARD,
            fg=MUTED,
            shadow="#080d16",
            width=270,
            height=25,
            anchor="w"
        )

        guess_label.grid(
            row=7,
            column=0,
            padx=28
        )

        self.guess_entry = tk.Entry(
            left_frame,
            font=("Arial", 19, "bold"),
            justify="center",
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground="white",
            disabledbackground="#dce5ef",
            disabledforeground="#31465c",
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=BLUE
        )

        self.guess_entry.grid(
            row=8,
            column=0,
            sticky="ew",
            padx=28,
            pady=(5, 8),
            ipady=8
        )

        self.guess_entry.config(
            state="disabled"
        )

        self.guess_button = tk.Button(
            left_frame,
            text="CHECK GUESS",
            font=("Arial", 11, "bold"),
            command=self.check_guess,
            bg=BLUE,
            fg=BUTTON_TEXT,
            activebackground=BLUE_DARK,
            activeforeground=BUTTON_TEXT,
            disabledforeground=BUTTON_TEXT_DISABLED,
            relief="raised",
            bd=3,
            cursor="hand2",
            padx=12,
            pady=9,
            state="disabled"
        )

        self.guess_button.grid(
            row=9,
            column=0,
            sticky="ew",
            padx=28,
            pady=(0, 22)
        )

        history_frame = tk.Frame(
            main_frame,
            bg=CARD,
            highlightthickness=1,
            highlightbackground=BORDER
        )

        history_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        history_frame.grid_rowconfigure(
            1,
            weight=1
        )

        history_frame.grid_columnconfigure(
            0,
            weight=1
        )

        history_title = EmbossedLabel(
            history_frame,
            text="GUESS HISTORY",
            font=("Arial", 16, "bold"),
            bg=CARD,
            fg=TEXT,
            shadow="#080d16",
            width=500,
            height=42,
            anchor="w"
        )

        history_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=24,
            pady=(18, 9)
        )

        self.history_list = tk.Listbox(
            history_frame,
            font=("Arial", 13, "bold"),
            bg=INPUT_BG,
            fg=TEXT,
            selectbackground="#315d81",
            selectforeground="white",
            activestyle="none",
            relief="flat",
            highlightthickness=0,
            borderwidth=0
        )

        self.history_list.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(24, 0),
            pady=(0, 24)
        )

        scrollbar = tk.Scrollbar(
            history_frame,
            command=self.history_list.yview
        )

        scrollbar.grid(
            row=1,
            column=1,
            sticky="ns",
            padx=(8, 24),
            pady=(0, 24)
        )

        self.history_list.config(
            yscrollcommand=scrollbar.set
        )

        footer = tk.Frame(
            self.root,
            bg=BG
        )

        footer.grid(
            row=2,
            column=0,
            pady=(0, 20)
        )

        new_game_button = tk.Button(
            footer,
            text="NEW GAME",
            font=("Arial", 10, "bold"),
            command=self.start_game,
            bg="#263e58",
            fg=BUTTON_TEXT,
            activebackground="#365875",
            activeforeground=BUTTON_TEXT,
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=22,
            pady=8
        )

        new_game_button.grid(
            row=0,
            column=0,
            padx=7
        )

        quit_button = tk.Button(
            footer,
            text="QUIT",
            font=("Arial", 10, "bold"),
            command=self.quit_game,
            bg="#512f3a",
            fg=BUTTON_TEXT,
            activebackground=RED,
            activeforeground=BUTTON_TEXT,
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=22,
            pady=8
        )

        quit_button.grid(
            row=0,
            column=1,
            padx=7
        )

        self.root.bind(
            "<Return>",
            self.submit_guess
        )


# =========================================================
# START PROGRAM
# =========================================================

game = NumberGuessingGame()

game.root.mainloop()