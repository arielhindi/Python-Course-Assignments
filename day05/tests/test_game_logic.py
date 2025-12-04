import pytest

from day05.game_logic import GameState


def test_game_state_basic():
    """Test basic GameState initialization and round generation."""
    gs = GameState()
    assert gs.total_rounds == 0
    assert gs.correct == 0

    # Generate a round (should NOT increment total_rounds yet)
    result = gs.next_round()
    assert result is not None
    flag, choices = result
    assert isinstance(flag, str) and len(flag) > 0  # emoji
    assert isinstance(choices, list) and len(choices) == 4
    assert gs.total_rounds == 0  # Still 0 because no guess submitted


def test_game_state_guess_correct():
    """Test submitting a correct guess."""
    gs = GameState()
    
    # Generate a round
    result = gs.next_round()
    assert result is not None
    flag, choices = result
    assert gs.total_rounds == 0  # Not incremented yet
    
    # Get the correct country name from the current state
    assert gs.current is not None
    _, correct_name, _ = gs.current
    
    # Submit correct guess
    is_correct = gs.submit_guess(correct_name)
    assert is_correct is True
    assert gs.correct == 1
    assert gs.total_rounds == 1  # Incremented on submit


def test_game_state_guess_wrong():
    """Test submitting an incorrect guess."""
    gs = GameState()
    
    # Generate a round
    result = gs.next_round()
    assert result is not None
    assert gs.total_rounds == 0  # Not incremented yet
    
    # Get the correct answer
    assert gs.current is not None
    _, correct_name, wrong_options = gs.current
    
    # Submit a wrong guess
    is_correct = gs.submit_guess(wrong_options[0])
    assert is_correct is False
    assert gs.correct == 0
    assert gs.total_rounds == 1  # Incremented on submit


def test_game_state_no_active_round():
    """Test that submitting without an active round raises RuntimeError."""
    gs = GameState()
    
    with pytest.raises(RuntimeError):
        gs.submit_guess("United States")


def test_game_state_stop_mid_round():
    """Test stopping the game without submitting a guess for the current round."""
    gs = GameState()
    
    # Generate a round
    gs.next_round()
    assert gs.total_rounds == 0
    
    # Stop without submitting
    # total_rounds should still be 0, correct should be 0
    assert gs.total_rounds == 0
    assert gs.correct == 0

