# bracket_config.py

BRACKET_ADVANCEMENT = {
    1: {"winner": {"bracket": 2, "slot": "player1"}, "loser": {"bracket": 5, "slot": "player1"}, "final_rank": None},
    2: {"winner": {"bracket": 3, "slot": "player1"}, "loser": {"bracket": 6, "slot": "player2"}, "final_rank": None},
    5: {"winner": {"bracket": 8, "slot": "player2"}, "loser": None, "final_rank": 8},  # Loser of bracket 5 finishes in 8th place
    6: {"winner": {"bracket": 9, "slot": "player1"}, "loser": None, "final_rank": 7},  # Loser of bracket 6 finishes in 7th place
    # Continue for all brackets
}
