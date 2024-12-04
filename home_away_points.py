import pandas as pd

df = pd.read_csv("fduk_bundesliga_21_22.csv")
scale = 100


def update_points(team, points_dict, points_to_add):
    if team in points_dict:
        points_dict[team] += points_to_add
    else:
        points_dict[team] = points_to_add


def get_additional_home_points():
    home_points = {}
    away_points = {}

    for _, row in df.iterrows():
        if row['FTR'] == 'H':
            update_points(row['HomeTeam'], home_points, 3)
            update_points(row['AwayTeam'], away_points, 0)
        elif row['FTR'] == 'A':
            update_points(row['HomeTeam'], home_points, 0)
            update_points(row['AwayTeam'], away_points, 3)
        elif row['FTR'] == 'D':
            update_points(row['HomeTeam'], home_points, 1)
            update_points(row['AwayTeam'], away_points, 1)

    results_df = pd.DataFrame({
        'Team': list(home_points.keys()),
        'Home Points': list(home_points.values()),
        'Away Points': [away_points.get(team, 0) for team in home_points.keys()]
    })

    results_df['Total Points'] = results_df['Home Points'] + results_df['Away Points']
    results_df['Home/Total'] = results_df['Home Points'] / results_df['Total Points']
    results_df['Additional Home Points'] = (results_df['Home/Total'] - results_df['Home/Total'].mean()) * scale
    team_points_dict = results_df.set_index('Team')['Additional Home Points'].to_dict()
    return team_points_dict


if __name__ == "__main__":
    get_additional_home_points()
