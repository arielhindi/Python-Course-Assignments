"""Tkinter GUI for the Day05 flag guessing game.

Run with:
    python -m day05.ui

The GUI shows a country flag emoji and four button options for country names.
The player clicks the correct country name. The game continues until they
click Stop, which shows the final score.
"""
import tkinter as tk
from tkinter import messagebox
import random

try:
    from .game_logic import GameState
except Exception:
    from day05.game_logic import GameState


class FlagGuessingApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Flag Guesser — Guess the Country!")
        root.geometry("500x400")

        self.state = GameState()
        self.choice_buttons = []

        # Title
        title = tk.Label(root, text="Guess the Country", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)

        # Flag display (large)
        self.flag_label = tk.Label(root, text="🚩", font=("Arial", 100))
        self.flag_label.grid(row=1, column=0, columnspan=2, pady=20)

        # Choice buttons grid
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Status
        self.status = tk.Label(root, text="Rounds: 0 | Correct: 0", font=("Arial", 12))
        self.status.grid(row=3, column=0, columnspan=2, pady=10)

        # Stop button
        self.stop_btn = tk.Button(root, text="Stop and Show Score", command=self.stop_game)
        self.stop_btn.grid(row=4, column=0, columnspan=2, pady=10)

        # Show first round
        self.show_next()

    def show_next(self):
        """Load and display the next flag round."""
        result = self.state.next_round()
        if result is None:
            messagebox.showerror("Error", "Could not load countries data.")
            return
        
        flag, choices = result
        self.flag_label.config(text=flag)
        
        # Clear old buttons
        for btn in self.choice_buttons:
            btn.destroy()
        self.choice_buttons.clear()

        # Create new buttons for each choice, randomly positioned
        for i, choice in enumerate(choices):
            btn = tk.Button(
                self.button_frame,
                text=choice,
                font=("Arial", 11),
                width=20,
                command=lambda c=choice: self.submit(c)
            )
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5)
            self.choice_buttons.append(btn)

        self.update_status()

    def submit(self, country_name: str):
        """Submit a guess."""
        try:
            is_correct = self.state.submit_guess(country_name)
        except RuntimeError:
            messagebox.showwarning("No active round", "No active flag to guess.")
            return

        if is_correct:
            messagebox.showinfo("Correct!", f"✓ That's right — {country_name}!")
        else:
            messagebox.showinfo("Wrong", f"✗ Incorrect. Try the next flag!")
        
        self.update_status()
        self.show_next()

    def update_status(self):
        """Update the status label with current score."""
        self.status.config(
            text=f"Rounds: {self.state.total_rounds} | Correct: {self.state.correct}"
        )

    def stop_game(self):
        """End the game and show final score."""
        pct = (
            round(100 * self.state.correct / self.state.total_rounds)
            if self.state.total_rounds > 0
            else 0
        )
        msg = (
            f"Final Score\n\n"
            f"Correct: {self.state.correct} out of {self.state.total_rounds}\n"
            f"Accuracy: {pct}%"
        )
        messagebox.showinfo("Game Over", msg)
        self.root.quit()


def main():
    root = tk.Tk()
    app = FlagGuessingApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
