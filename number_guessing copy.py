import random
class BestScore():
    def __init__(self, difficulty, attempts):
        self.difficulty=difficulty
        self.attempts=attempts
    def update_best_score(self):
        filename=f"best_score_{self.difficulty.lower()}"
        with open(f"{filename}.txt","a") as f:
            pass
        with open(f"{filename}.txt") as f:
            content=f.read()
        if(content==""):
            with open(f"{filename}.txt", "w") as f:
                f.write(str(self.attempts))
                print(f"YOUR BEST SCORE OF {self.difficulty.upper()} LEVEL IS {self.attempts}")
        elif(self.attempts<int(content)):
            with open(f"{filename}.txt", "w") as f:
                f.write(str(self.attempts))
                print(f"YOUR BEST SCORE OF {self.difficulty.upper()} LEVEL IS {self.attempts} AND EARLIER IT WAS {content}")
        else:
            print(f"YOUR BEST SCORE OF {self.difficulty.upper()} LEVEL IS STILL {content}" )

play_again=input("DO YOU WANT TO PLAY THIS GAME? ").capitalize()

difficulty_levels={
    "Easy":20,
    "Medium":15,
    "Hard":10,
    "Impossible":5
    }

while(play_again=="Yes"):
    difficulty=input("ENTER YOUR DIFFICULTY LEVEL-Easy, Medium, Hard, Impossible: ").capitalize()
    if(difficulty not in difficulty_levels):
        print("INVALID DIFFICULTY CHOSEN")
        break
    max_attempts=difficulty_levels[difficulty]
    secret_number=random.randint(1,1000)

    print(f"I HAVE A NUMBER BETWEEN 1-1000. TRY GUESSING IT. YOU ONLY HAVE {max_attempts} CHANCES.")
    attempts=0

    while(attempts<max_attempts):
        try:
            guess=int(input("ENTER YOUR GUESS: "))
        except ValueError:
            print("PLEASE ENTER A VALID NUMBER: ")
            continue
        attempts+=1
        if(guess==secret_number):
            print(f"YOU GUESSED IT CORRECTLY IN {attempts} ATTEMPTS")
            best_score=BestScore(difficulty, attempts)
            best_score.update_best_score()
            break

        elif(guess<secret_number and attempts<max_attempts):
            print("GO HIGHER")
            print(f"{max_attempts-attempts} ATTEMPTS LEFT")

        elif(guess>secret_number and attempts<max_attempts):
            print("GO LOWER")
            print(f"{max_attempts-attempts} ATTEMPTS LEFT")

        if(attempts==max_attempts):
            print(f"YOU HAVE FAILED THE ANSWER WAS {secret_number}")
            break
    play_again=input("DO YOU WANT TO PLAY AGAIN? ").capitalize()