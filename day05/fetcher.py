from typing import List, Tuple
import random


# (flag_emoji, country_name)
COUNTRIES = [
    ("🇺🇸", "United States"),
    ("🇬🇧", "United Kingdom"),
    ("🇯🇵", "Japan"),
    ("🇮🇹", "Italy"),
    ("🇫🇷", "France"),
    ("🇩🇪", "Germany"),
    ("🇨🇦", "Canada"),
    ("🇦🇺", "Australia"),
    ("🇮🇳", "India"),
    ("🇧🇷", "Brazil"),
    ("🇲🇪", "Mexico"),
    ("🇮🇪", "Ireland"),
    ("🇪🇸", "Spain"),
    ("🇰🇷", "South Korea"),
    ("🇳🇿", "New Zealand"),
    ("🇳🇱", "Netherlands"),
    ("🇸🇪", "Sweden"),
    ("🇳🇴", "Norway"),
    ("🇨🇭", "Switzerland"),
    ("🇦🇷", "Argentina"),
    ("🇲🇨", "Monaco"),
    ("🇬🇷", "Greece"),
    ("🇷🇺", "Russia"),
    ("🇵🇱", "Poland"),
    ("🇳🇮", "Nicaragua"),
    ("🇵🇾", "Paraguay"),
    ("🇹🇭", "Thailand"),
    ("🇻🇳", "Vietnam"),
    ("🇵🇭", "Philippines"),
    ("🇷🇴", "Romania"),
]


def get_countries() -> List[Tuple[str, str]]:
    """Return a list of all countries as (flag_emoji, country_name) tuples."""
    return COUNTRIES.copy()


def sample_game_round(num_choices: int = 4) -> Tuple[str, str, List[str]]:
    """Generate a game round: return (correct_flag, correct_name, wrong_options).
    
    Args:
        num_choices: total number of answer choices (default 4, including the correct one)
    
    Returns:
        (flag, correct_country_name, list_of_wrong_country_names)
    """
    # Pick correct country
    flag, correct_name = random.choice(COUNTRIES)
    
    # Pick wrong options (different country names)
    wrong_countries = [c for c in COUNTRIES if c[1] != correct_name]
    wrong_names = [c[1] for c in random.sample(wrong_countries, min(num_choices - 1, len(wrong_countries)))]
    
    return flag, correct_name, wrong_names
