from collections import defaultdict

import pandas as pd

from home_away_points import calculate_result, create_elo_rating, SCALE, update_points


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

df = pd.read_csv("fduk_bundesliga_21_22.csv")
home_points = defaultdict(int)
away_points = defaultdict(int)

for _, row in df.iterrows():
    if row['FTR'] == 'H':
        update_points(row['HomeTeam'], home_points, 3)
    elif row['FTR'] == 'A':
        update_points(row['AwayTeam'], away_points, 3)
    elif row['FTR'] == 'D':
        update_points(row['HomeTeam'], home_points, 1)
        update_points(row['AwayTeam'], away_points, 1)

results_df = pd.DataFrame({
    'Team': list(home_points.keys()),
    'Home Points': list(home_points.values()),
    'Away Points': [away_points[team] for team in home_points.keys()]
})

results_df['Total Points'] = results_df['Home Points'] + results_df['Away Points']
results_df['Home/Total'] = results_df['Home Points'] / results_df['Total Points']
results_df['Away/Total'] = results_df['Away Points'] / results_df['Total Points']
results_df['Bonus Home Points'] = (results_df['Home/Total'] - results_df['Home/Total'].mean()) * SCALE
results_df['Bonus Away Points'] = (results_df['Away/Total'] - results_df['Away/Total'].mean()) * SCALE
results_df[['Team', 'Bonus Home Points']].to_excel("bonus_points.xlsx")


df = pd.DataFrame(list(create_elo_rating().items()), columns=['Team', 'Score'])
df.to_excel("elo_points.xlsx")