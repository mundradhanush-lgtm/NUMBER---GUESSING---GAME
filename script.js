const difficultyLevels = {
    Easy: 20,
    Medium: 15,
    Hard: 10,
    Impossible: 5
};

let secretNumber = null;
let attempts = 0;
let maxAttempts = 0;
let gameActive = false;

const difficulty = document.getElementById("difficulty");
const startButton = document.getElementById("startButton");
const newGameButton = document.getElementById("newGameButton");
const quitButton = document.getElementById("quitButton");
const guessInput = document.getElementById("guessInput");
const guessButton = document.getElementById("guessButton");
const status = document.getElementById("status");
const attemptsLabel = document.getElementById("attempts");
const bestScoreLabel = document.getElementById("bestScore");
const history = document.getElementById("history");

function getScoreKey() {
    return "numberGuessingBest_" + difficulty.value.toLowerCase();
}

function getBestScore() {
    const saved = localStorage.getItem(getScoreKey());
    return saved === null ? null : Number(saved);
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
    history.innerHTML = '<div class="history-placeholder">Your guesses will appear here.</div>';
}

function addHistory(text, className = "") {
    const placeholder = history.querySelector(".history-placeholder");

    if (placeholder) {
        placeholder.remove();
    }

    const item = document.createElement("div");
    item.className = `history-item ${className}`;
    item.textContent = text;
    history.appendChild(item);
    history.scrollTop = history.scrollHeight;
}

function startGame() {
    maxAttempts = difficultyLevels[difficulty.value];
    secretNumber = Math.floor(Math.random() * 1000) + 1;
    attempts = 0;
    gameActive = true;

    difficulty.disabled = true;
    guessInput.disabled = false;
    guessButton.disabled = false;

    guessInput.value = "";
    guessInput.focus();

    clearHistory();

    status.textContent = "Guess the number!";
    attemptsLabel.textContent = `Attempts left: ${maxAttempts}`;
    showBestScore();
}

function finishGame() {
    gameActive = false;
    difficulty.disabled = false;
    guessInput.disabled = true;
    guessButton.disabled = true;
}

function checkGuess() {
    if (!gameActive) {
        alert("Please click START NEW GAME first.");
        return;
    }

    const value = guessInput.value.trim();

    if (value === "") {
        alert("Please enter a number.");
        return;
    }

    const guess = Number(value);

    if (!Number.isInteger(guess) || guess < 1 || guess > 1000) {
        alert("Please enter a whole number between 1 and 1000.");
        guessInput.value = "";
        guessInput.focus();
        return;
    }

    attempts++;
    const remaining = maxAttempts - attempts;

    if (guess === secretNumber) {
        addHistory(`Guess ${attempts}: ${guess}  →  CORRECT!`, "correct");

        const oldBest = getBestScore();
        let message;

        if (oldBest === null || attempts < oldBest) {
            localStorage.setItem(getScoreKey(), String(attempts));
            showBestScore();

            if (oldBest === null) {
                message =
                    `Congratulations! You guessed the number ${secretNumber} in ${attempts} attempts!\n\n` +
                    "NEW BEST SCORE!";
            } else {
                message =
                    `Congratulations! You guessed the number ${secretNumber} in ${attempts} attempts!\n\n` +
                    `Previous Best: ${oldBest} attempts\nNEW BEST SCORE: ${attempts} attempts!`;
            }
        } else {
            showBestScore();
            message =
                `Congratulations! You guessed the number ${secretNumber} in ${attempts} attempts!\n\n` +
                `Best Score: ${oldBest} attempts`;
        }

        status.textContent = "CORRECT! You guessed the number!";
        attemptsLabel.textContent = `Attempts left: ${remaining}`;

        alert(message);
        finishGame();
        return;
    }

    const hint = guess < secretNumber ? "GO HIGHER ⬆" : "GO LOWER ⬇";
    status.textContent = hint;

    addHistory(`Guess ${attempts}: ${guess}  →  ${guess < secretNumber ? "GO HIGHER ⬆" : "GO LOWER ⬇"}`);

    attemptsLabel.textContent = `Attempts left: ${remaining}`;
    guessInput.value = "";
    guessInput.focus();

    if (attempts >= maxAttempts) {
        addHistory(`GAME OVER  →  The number was ${secretNumber}`, "game-over");

        status.textContent = "GAME OVER!";
        attemptsLabel.textContent = "Attempts left: 0";

        alert(`Game Over!\n\nThe number was ${secretNumber}.`);
        finishGame();
    }
}

function resetGame() {
    startGame();
}

function quitGame() {
    const confirmed = confirm("Are you sure you want to quit the game?");

    if (!confirmed) {
        return;
    }

    /*
     * Browsers normally prevent a webpage from closing a tab/window
     * that was not opened by JavaScript. We try window.close() first.
     * If the browser blocks it, about:blank removes the game page.
     */
    window.open("", "_self");
    window.close();

    setTimeout(() => {
        document.body.innerHTML = `
            <div style="
                min-height:100vh;
                display:flex;
                align-items:center;
                justify-content:center;
                text-align:center;
                font-family:Arial,Helvetica,sans-serif;
                background:#1e1e2e;
                color:white;
                padding:30px;
            ">
                <div>
                    <h1>GAME QUIT</h1>
                    <p>You can close this browser tab now.</p>
                </div>
            </div>
        `;
    }, 100);
}

startButton.addEventListener("click", startGame);
newGameButton.addEventListener("click", resetGame);
guessButton.addEventListener("click", checkGuess);
quitButton.addEventListener("click", quitGame);

difficulty.addEventListener("change", showBestScore);

guessInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        checkGuess();
    }
});

showBestScore();
