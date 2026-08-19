import random
import tkinter as tk
from tkinter import messagebox


# =========================================================
# BEST SCORE
# =========================================================

class BestScore:

    def __init__(self, difficulty, attempts):
        self.difficulty = difficulty
        self.attempts = attempts
        self.filename = f"best_score_{difficulty.lower()}.txt"

    def get_best_score(self):
        try:
            with open(self.filename, "r") as f:
                content = f.read().strip()

                if content:
                    return int(content)

        except (FileNotFoundError, ValueError):
            pass

        return None

    def update_best_score(self):

        old_best = self.get_best_score()

        if old_best is None or self.attempts < old_best:

            with open(self.filename, "w") as f:
                f.write(str(self.attempts))

            return True, old_best, self.attempts

        return False, old_best, old_best


# =========================================================
# GAME SETTINGS
# =========================================================

difficulty_levels = {
    "Easy": 20,
    "Medium": 15,
    "Hard": 10,
    "Impossible": 5
}

secret_number = None
attempts = 0
max_attempts = 20


# =========================================================
# START GAME
# =========================================================

def start_game():

    global secret_number
    global attempts
    global max_attempts

    difficulty = difficulty_var.get()

    max_attempts = difficulty_levels[difficulty]

    secret_number = random.randint(1, 1000)

    attempts = 0

    # Enable controls
    guess_entry.config(state="normal")
    guess_button.config(state="normal")

    # Clear guess box
    guess_entry.delete(0, tk.END)

    # Clear history
    history_list.delete(0, tk.END)

    # Reset status
    status_label.config(
        text=(
            "I've chosen a number between 1 and 1000.\n"
            f"You have {max_attempts} attempts!"
        )
    )

    # Reset attempts
    attempts_label.config(
        text=f"Attempts left: {max_attempts}"
    )

    # Get saved best score
    score = BestScore(difficulty, 0)

    best = score.get_best_score()

    if best is None:
        best_score_label.config(
            text="Best Score: No score yet"
        )
    else:
        best_score_label.config(
            text=f"Best Score: {best} attempts"
        )

    # Don't change difficulty while playing
    difficulty_menu.config(
        state="disabled"
    )

    guess_entry.focus()


# =========================================================
# CHECK GUESS
# =========================================================

def check_guess():

    global attempts

    if secret_number is None:

        messagebox.showwarning(
            "Start Game",
            "Please click START NEW GAME first."
        )

        return

    guess_text = guess_entry.get().strip()

    # Check input
    try:
        guess = int(guess_text)

    except ValueError:

        messagebox.showwarning(
            "Invalid Input",
            "Please enter a valid whole number."
        )

        guess_entry.delete(0, tk.END)
        guess_entry.focus()

        return

    # Check range
    if guess < 1 or guess > 1000:

        messagebox.showwarning(
            "Invalid Number",
            "Please enter a number between 1 and 1000."
        )

        guess_entry.delete(0, tk.END)
        guess_entry.focus()

        return

    # Count attempt
    attempts += 1

    remaining = max_attempts - attempts


    # =====================================================
    # CORRECT GUESS
    # =====================================================

    if guess == secret_number:

        history_list.insert(
            tk.END,
            f"Guess {attempts}: {guess}  →  CORRECT!"
        )

        history_list.see(tk.END)

        difficulty = difficulty_var.get()

        score = BestScore(
            difficulty,
            attempts
        )

        is_new_best, old_best, new_best = score.update_best_score()


        if is_new_best:

            best_score_label.config(
                text=f"Best Score: {new_best} attempts"
            )

            if old_best is None:

                status_label.config(
                    text=(
                        f"CORRECT!\n"
                        f"You guessed it in {attempts} attempts!\n"
                        f"NEW BEST SCORE!"
                    )
                )

                messagebox.showinfo(
                    "New Best Score!",
                    (
                        f"You guessed the number "
                        f"{secret_number} in {attempts} attempts!\n\n"
                        f"NEW BEST SCORE: {new_best} attempts"
                    )
                )

            else:

                status_label.config(
                    text=(
                        f"CORRECT!\n"
                        f"You guessed it in {attempts} attempts!\n"
                        f"NEW BEST SCORE!"
                    )
                )

                messagebox.showinfo(
                    "New Best Score!",
                    (
                        f"You guessed the number "
                        f"{secret_number} in {attempts} attempts!\n\n"
                        f"Previous Best: {old_best} attempts\n\n"
                        f"NEW BEST: {new_best} attempts"
                    )
                )

        else:

            best_score_label.config(
                text=f"Best Score: {old_best} attempts"
            )

            status_label.config(
                text=(
                    f"CORRECT!\n"
                    f"You guessed it in {attempts} attempts."
                )
            )

            messagebox.showinfo(
                "You Won!",
                (
                    f"You guessed the number "
                    f"{secret_number} in {attempts} attempts!\n\n"
                    f"Best Score: {old_best} attempts"
                )
            )

        end_game()

        return


    # =====================================================
    # WRONG GUESS
    # =====================================================

    if guess < secret_number:

        result = "GO HIGHER"

        status_label.config(
            text="GO HIGHER ⬆"
        )

    else:

        result = "GO LOWER"

        status_label.config(
            text="GO LOWER ⬇"
        )


    # =====================================================
    # ADD TO GUESS HISTORY
    # =====================================================

    history_list.insert(
        tk.END,
        f"Guess {attempts}: {guess}  →  {result}"
    )

    history_list.see(tk.END)


    # =====================================================
    # UPDATE ATTEMPTS
    # =====================================================

    attempts_label.config(
        text=f"Attempts left: {remaining}"
    )

    # Clear input
    guess_entry.delete(0, tk.END)

    guess_entry.focus()


    # =====================================================
    # GAME OVER
    # =====================================================

    if attempts >= max_attempts:

        history_list.insert(
            tk.END,
            f"GAME OVER → The number was {secret_number}"
        )

        history_list.see(tk.END)

        status_label.config(
            text=(
                f"GAME OVER\n"
                f"The number was {secret_number}."
            )
        )

        attempts_label.config(
            text="Attempts left: 0"
        )

        messagebox.showinfo(
            "Game Over",
            (
                f"You used all {max_attempts} attempts.\n\n"
                f"The number was {secret_number}."
            )
        )

        end_game()


# =========================================================
# END GAME
# =========================================================

def end_game():

    guess_entry.config(
        state="disabled"
    )

    guess_button.config(
        state="disabled"
    )

    difficulty_menu.config(
        state="normal"
    )


# =========================================================
# QUIT
# =========================================================

def quit_game():
    root.destroy()


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "Number Guessing Game"
)

root.configure(
    bg="#1e1e2e"
)


# =========================================================
# MAXIMIZE WINDOW
# =========================================================

try:
    root.state("zoomed")

except tk.TclError:

    try:
        root.attributes("-zoomed", True)

    except tk.TclError:
        pass


# =========================================================
# ROOT GRID
# =========================================================

root.grid_rowconfigure(
    0,
    weight=0
)

root.grid_rowconfigure(
    1,
    weight=1
)

root.grid_rowconfigure(
    2,
    weight=0
)

root.grid_columnconfigure(
    0,
    weight=1
)


# =========================================================
# TITLE AREA
# =========================================================

title_frame = tk.Frame(
    root,
    bg="#1e1e2e"
)

title_frame.grid(
    row=0,
    column=0,
    sticky="ew",
    padx=30,
    pady=(20, 5)
)


title = tk.Label(
    title_frame,
    text="NUMBER GUESSING GAME",
    font=("Helvetica", 34, "bold"),
    bg="#1e1e2e",
    fg="white"
)

title.pack(
    pady=(0, 3)
)


subtitle = tk.Label(
    title_frame,
    text="Can you guess the secret number?",
    font=("Helvetica", 17),
    bg="#1e1e2e",
    fg="#cdd6f4"
)

subtitle.pack()


# =========================================================
# MAIN FRAME
# =========================================================

main_frame = tk.Frame(
    root,
    bg="#1e1e2e"
)

main_frame.grid(
    row=1,
    column=0,
    sticky="nsew",
    padx=50,
    pady=10
)

main_frame.grid_columnconfigure(
    0,
    weight=1
)

main_frame.grid_columnconfigure(
    1,
    weight=2
)

main_frame.grid_rowconfigure(
    0,
    weight=1
)


# =========================================================
# LEFT PANEL
# =========================================================

left_frame = tk.Frame(
    main_frame,
    bg="#28283d"
)

left_frame.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=(0, 15)
)

left_frame.grid_columnconfigure(
    0,
    weight=1
)


# =========================================================
# DIFFICULTY
# =========================================================

difficulty_title = tk.Label(
    left_frame,
    text="DIFFICULTY",
    font=("Helvetica", 17, "bold"),
    bg="#28283d",
    fg="#cdd6f4"
)

difficulty_title.grid(
    row=0,
    column=0,
    pady=(18, 7)
)


difficulty_var = tk.StringVar(
    value="Easy"
)


difficulty_menu = tk.OptionMenu(
    left_frame,
    difficulty_var,
    *difficulty_levels.keys()
)

difficulty_menu.config(
    font=("Helvetica", 15),
    width=15
)

difficulty_menu.grid(
    row=1,
    column=0,
    pady=5
)


# =========================================================
# START BUTTON
# =========================================================

start_button = tk.Button(
    left_frame,
    text="START NEW GAME",
    font=("Helvetica", 14, "bold"),
    command=start_game,
    padx=20,
    pady=9
)

start_button.grid(
    row=2,
    column=0,
    pady=10
)


# =========================================================
# STATUS
# =========================================================

status_label = tk.Label(
    left_frame,
    text=(
        "Guess a number between 1 and 1000!\n"
        "Choose a difficulty and start the game!"
    ),
    font=("Helvetica", 15),
    bg="#28283d",
    fg="white",
    justify="center",
    wraplength=500
)

status_label.grid(
    row=3,
    column=0,
    pady=(5, 7)
)


# =========================================================
# ATTEMPTS LEFT
# =========================================================

attempts_label = tk.Label(
    left_frame,
    text="Attempts left: 0",
    font=("Helvetica", 17, "bold"),
    bg="#28283d",
    fg="#f9e2af"
)

attempts_label.grid(
    row=4,
    column=0,
    pady=4
)


# =========================================================
# BEST SCORE
# =========================================================

best_score_label = tk.Label(
    left_frame,
    text="Best Score: No score yet",
    font=("Helvetica", 15, "bold"),
    bg="#28283d",
    fg="#a6e3a1"
)

best_score_label.grid(
    row=5,
    column=0,
    pady=4
)


# =========================================================
# GUESS ENTRY
# =========================================================

guess_entry = tk.Entry(
    left_frame,
    font=("Helvetica", 21),
    justify="center",
    width=12
)

guess_entry.grid(
    row=6,
    column=0,
    pady=8
)


# =========================================================
# CHECK GUESS
# =========================================================

guess_button = tk.Button(
    left_frame,
    text="CHECK GUESS",
    font=("Helvetica", 14, "bold"),
    command=check_guess,
    padx=25,
    pady=9,
    state="disabled"
)

guess_button.grid(
    row=7,
    column=0,
    pady=(5, 18)
)


# =========================================================
# RIGHT PANEL
# =========================================================

history_frame = tk.Frame(
    main_frame,
    bg="#28283d"
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


# =========================================================
# HISTORY TITLE
# =========================================================

history_title = tk.Label(
    history_frame,
    text="GUESS HISTORY",
    font=("Helvetica", 22, "bold"),
    bg="#28283d",
    fg="white"
)

history_title.grid(
    row=0,
    column=0,
    pady=(18, 12)
)


# =========================================================
# HISTORY LIST
# =========================================================

history_list = tk.Listbox(
    history_frame,
    font=("Helvetica", 16),
    bg="#1e1e2e",
    fg="white",
    selectbackground="#45475a",
    selectforeground="white",
    borderwidth=0,
    highlightthickness=0
)

history_list.grid(
    row=1,
    column=0,
    sticky="nsew",
    padx=30,
    pady=(0, 25)
)


# =========================================================
# BOTTOM BUTTONS
# =========================================================

button_frame = tk.Frame(
    root,
    bg="#1e1e2e"
)

button_frame.grid(
    row=2,
    column=0,
    pady=(5, 15)
)


# =========================================================
# NEW GAME
# =========================================================

new_game_button = tk.Button(
    button_frame,
    text="NEW GAME",
    font=("Helvetica", 13, "bold"),
    command=start_game,
    padx=25,
    pady=9
)

new_game_button.grid(
    row=0,
    column=0,
    padx=10
)


# =========================================================
# QUIT
# =========================================================

quit_button = tk.Button(
    button_frame,
    text="QUIT",
    font=("Helvetica", 13, "bold"),
    command=quit_game,
    padx=25,
    pady=9
)

quit_button.grid(
    row=0,
    column=1,
    padx=10
)


# =========================================================
# ENTER KEY SUPPORT
# =========================================================

root.bind(
    "<Return>",
    lambda event: check_guess()
)


# =========================================================
# RUN GAME
# =========================================================

root.mainloop()