from home_away_points import calculate_result, create_elo_rating


def update_elo_ranking(old_elo, goals, result, win_probability):
    return old_elo + 30 * goals * (result - win_probability)


elo_rating = create_elo_rating()

home_elo = elo_rating.get("Schalke", 0)
away_elo = elo_rating.get("Hertha", 0)
win_prob = calculate_result(0, 0, home_elo, away_elo)
print(f"Schalke win prob {win_prob}")
print(f"Hertha win prob {(1 - win_prob)}")
print(f"Old Schalke elo {home_elo}")
print(f"Old Schalke elo {update_elo_ranking(home_elo, 1, 1, win_prob)}")