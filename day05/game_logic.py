"""Core game logic for the Day05 flag guessing game.

This module provides a GameState class that tracks rounds, score, and
selects countries/flags at random.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import random

try:
    from . import fetcher
except Exception:
    from day05 import fetcher


@dataclass
class GameState:
    """Tracks game state for the flag guesser."""
    total_rounds: int = 0
    correct: int = 0
    current: Optional[Tuple[str, str, List[str]]] = None  # (flag, correct_name, wrong_options)

    def next_round(self) -> Optional[Tuple[str, List[str]]]:
        """Generate the next round and return (flag, list_of_choices).
        
        The list_of_choices includes the correct answer mixed with wrong answers.
        Note: total_rounds is NOT incremented here; it's only incremented when
        a guess is actually submitted.
        Returns None if no data available.
        """
        try:
            flag, correct_name, wrong_names = fetcher.sample_game_round(num_choices=4)
        except Exception:
            return None
        
        # Mix correct name with wrong options
        all_choices = [correct_name] + wrong_names
        random.shuffle(all_choices)
        
        self.current = (flag, correct_name, wrong_names)
        return flag, all_choices

    def submit_guess(self, guess: str) -> bool:
        """Submit a guess (country name). Returns True if correct, False otherwise.
        
        Increments total_rounds when a guess is submitted.
        Raises RuntimeError if no active round.
        """
        if not self.current:
            raise RuntimeError("No active round to guess")
        _, correct_name, _ = self.current
        is_correct = (guess == correct_name)
        if is_correct:
            self.correct += 1
        self.total_rounds += 1  # Only increment when a guess is submitted
        self.current = None  # clear current to avoid double-guess
        return is_correct
