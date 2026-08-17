const difficultyLevels = {
    Easy: 20,
    Medium: 15,
    Hard: 10,
    Impossible: 5
};

let secretNumber = null;
let attempts = 0;
let maxAttempts = difficultyLevels.Easy;
let gameActive = false;

const difficulty = document.getElementById("difficulty");
const startButton = document.getElementById("startButton");
const newGameButton = document.getElementById("newGameButton");
const resetScoresButton = document.getElementById("resetScoresButton");
const guessInput = document.getElementById("guessInput");
const guessButton = document.getElementById("guessButton");
const status = document.getElementById("status");
const attemptsLabel = document.getElementById("attempts");
const bestScoreLabel = document.getElementById("bestScore");
const history = document.getElementById("history");

function scoreKey() {
    return `numberGuessingBest_${difficulty.value.toLowerCase()}`;
}

function getBestScore() {
    const saved = localStorage.getItem(scoreKey());
    return saved === null ? null : Number(saved);
}

function updateBestScore() {
    const oldBest = getBestScore();

    if (oldBest === null || attempts < oldBest) {
        localStorage.setItem(scoreKey(), String(attempts));
        return {
            isNewBest: true,
            oldBest,
            newBest: attempts
        };
    }

    return {
        isNewBest: false,
        oldBest,
        newBest: oldBest
    };
}

function showBestScore() {
    const best = getBestScore();

    if (best === null) {
        bestScoreLabel.textContent = "Best Score: No score yet";
    } else {
        bestScoreLabel.textContent = `Best Score: ${best} attempts`;
    }
}

function clearHistory() {
    history.innerHTML = '<div class="empty-history">Your guesses will appear here.</div>';
}

function addHistory(text, className = "") {
    const empty = history.querySelector(".empty-history");
    if (empty) {
        empty.remove();
    }

    const item = document.createElement("div");
    item.className = `history-item ${className}`.trim();
    item.textContent = text;
    history.appendChild(item);
    history.scrollTop = history.scrollHeight;
}

function startGame() {
    maxAttempts = difficultyLevels[difficulty.value];
    secretNumber = Math.floor(Math.random() * 1000) + 1;
    attempts = 0;
    gameActive = true;

    guessInput.disabled = false;
    guessButton.disabled = false;
    difficulty.disabled = true;

    guessInput.value = "";
    guessInput.focus();

    clearHistory();

    status.innerHTML =
        `I've chosen a number between 1 and 1000.<br>You have ${maxAttempts} attempts!`;

    attemptsLabel.textContent = `Attempts left: ${maxAttempts}`;
    showBestScore();
}

function endGame() {
    gameActive = false;
    guessInput.disabled = true;
    guessButton.disabled = true;
    difficulty.disabled = false;
}

function checkGuess() {
    if (!gameActive) {
        alert("Please click START NEW GAME first.");
        return;
    }

    const guessText = guessInput.value.trim();

    if (guessText === "") {
        alert("Please enter a valid whole number.");
        return;
    }

    const guess = Number(guessText);

    if (!Number.isInteger(guess)) {
        alert("Please enter a valid whole number.");
        guessInput.value = "";
        guessInput.focus();
        return;
    }

    if (guess < 1 || guess > 1000) {
        alert("Please enter a number between 1 and 1000.");
        guessInput.value = "";
        guessInput.focus();
        return;
    }

    attempts += 1;
    const remaining = maxAttempts - attempts;

    if (guess === secretNumber) {
        addHistory(`Guess ${attempts}: ${guess} → CORRECT!`, "correct");

        const score = updateBestScore();
        showBestScore();

        if (score.isNewBest) {
            if (score.oldBest === null) {
                status.innerHTML =
                    `CORRECT!<br>You guessed it in ${attempts} attempts!<br>NEW BEST SCORE!`;

                alert(
                    `You guessed the number ${secretNumber} in ${attempts} attempts!\n\n` +
                    `NEW BEST SCORE: ${score.newBest} attempts`
                );
            } else {
                status.innerHTML =
                    `CORRECT!<br>You guessed it in ${attempts} attempts!<br>NEW BEST SCORE!`;

                alert(
                    `You guessed the number ${secretNumber} in ${attempts} attempts!\n\n` +
                    `Previous Best: ${score.oldBest} attempts\n\n` +
                    `NEW BEST: ${score.newBest} attempts`
                );
            }
        } else {
            status.innerHTML =
                `CORRECT!<br>You guessed it in ${attempts} attempts.`;

            alert(
                `You guessed the number ${secretNumber} in ${attempts} attempts!\n\n` +
                `Best Score: ${score.oldBest} attempts`
            );
        }

        endGame();
        return;
    }

    const result = guess < secretNumber ? "GO HIGHER" : "GO LOWER";
    const arrow = guess < secretNumber ? "⬆" : "⬇";

    status.textContent = `${result} ${arrow}`;

    addHistory(`Guess ${attempts}: ${guess} → ${result}`);

    attemptsLabel.textContent = `Attempts left: ${remaining}`;

    guessInput.value = "";
    guessInput.focus();

    if (attempts >= maxAttempts) {
        addHistory(`GAME OVER → The number was ${secretNumber}`, "game-over");

        status.innerHTML = `GAME OVER<br>The number was ${secretNumber}.`;
        attemptsLabel.textContent = "Attempts left: 0";

        alert(
            `You used all ${maxAttempts} attempts.\n\n` +
            `The number was ${secretNumber}.`
        );

        endGame();
    }
}

function resetBestScores() {
    const confirmed = confirm(
        "Reset all saved best scores for Easy, Medium, Hard and Impossible?"
    );

    if (!confirmed) {
        return;
    }

    Object.keys(difficultyLevels).forEach(level => {
        localStorage.removeItem(`numberGuessingBest_${level.toLowerCase()}`);
    });

    showBestScore();
    status.innerHTML = "Best scores have been reset.<br>Start a new game!";
}

difficulty.addEventListener("change", showBestScore);
startButton.addEventListener("click", startGame);
newGameButton.addEventListener("click", startGame);
guessButton.addEventListener("click", checkGuess);
resetScoresButton.addEventListener("click", resetBestScores);

guessInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        checkGuess();
    }
});

showBestScore();
