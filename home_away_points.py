import pandas as pd
import random
from collections import defaultdict

SCALE = 100


def update_points(team, points_dict, points_to_add):
    points_dict[team] += points_to_add


def update_match_points(row, result, points):
    if result == 'H':
        update_points(row['HomeTeam'], points, 3)
    elif result == 'A':
        update_points(row['AwayTeam'], points, 3)
    elif result == 'D':
        update_points(row['HomeTeam'], points, 1)
        update_points(row['AwayTeam'], points, 1)


def get_additional_home_points(df):
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
    results_df['Additional Home Points'] = (results_df['Home/Total'] - results_df['Home/Total'].mean()) * SCALE

    return results_df.set_index('Team')['Additional Home Points'].to_dict()


def create_elo_rating():
    return {
        "Bayern Munich": 1958.18164062,
        "Dortmund": 1799.90466309,
        "Leverkusen": 1794.84973145,
        "RB Leipzig": 1811.68139648,
        "Union Berlin": 1730.94873047,
        "Freiburg": 1718.88098145,
        "FC Koln": 1679.59106445,
        "Mainz": 1680.41052246,
        "Hoffenheim": 1664.32446289,
        "M'gladbach": 1711.80078125,
        "Ein Frankfurt": 1737.85949707,
        "Wolfsburg": 1681.94470215,
        "Bochum": 1613.51037598,
        "Augsburg": 1616.46337891,
        "Stuttgart": 1621.03259277,
        "Hertha": 1589.0,
        "Schalke 04": 1579.00720215,
        "Werder Bremen": 1597.18164062
    }


def create_draw_chance(df):
    draw_ratio = defaultdict(float)
    total_matches = 34

    for _, row in df.iterrows():
        if row['FTR'] == 'D':
            draw_ratio[row['HomeTeam']] += 1
            draw_ratio[row['AwayTeam']] += 1

    for team in draw_ratio:
        draw_ratio[team] /= total_matches

    mean_draw_ratio = sum(draw_ratio.values()) / len(draw_ratio.values())
    for team in create_elo_rating().keys():
        if not team in draw_ratio:
            draw_ratio[team] = mean_draw_ratio

    return draw_ratio


def calculate_result(home_points, away_points, home_elo, away_elo):
    home_value = 100 + home_points + away_points
    dr = home_elo - away_elo
    return 1 / (10 ** ((-dr + home_value) / 400) + 1)


def predict_result(home_win_prob, away_win_prob, draw_prob):
    values = ["H", "A", "D"]
    probabilities = [home_win_prob, away_win_prob, draw_prob]
    return random.choices(values, probabilities)[0]


def elo_change(result, win_probability, goals=1):
    return 30 * goals * (result - win_probability)


def simulate_season(df, team_points, draw_ratio):
    elo_rating = create_elo_rating()
    points = defaultdict(int)

    for _, row in df.iterrows():
        home_points = team_points.get(row['HomeTeam'], 0)
        away_points = -team_points.get(row['AwayTeam'], 0)
        home_elo = elo_rating.get(row['HomeTeam'], 0)
        away_elo = elo_rating.get(row['AwayTeam'], 0)

        win_home_prob = calculate_result(home_points, away_points, home_elo, away_elo)
        win_away_prob = 1 - win_home_prob
        home_draw_rate = draw_ratio.get(row['HomeTeam'], 0)
        away_draw_rate = draw_ratio.get(row['AwayTeam'], 0)
        draw_prob = win_home_prob * home_draw_rate + win_away_prob * away_draw_rate
        win_home_prob -= draw_prob * win_home_prob
        win_away_prob -= draw_prob * win_away_prob
        result = predict_result(win_home_prob, win_away_prob, draw_prob)
        update_match_points(row, result, points)
        home_result_converted = 1 if result == 'H' else 0.5 if result == 'D' else 0
        elo_rating[row['HomeTeam']] += elo_change(home_result_converted, win_home_prob)
        away_result_converted = 1 if result == 'A' else 0.5 if result == 'D' else 0
        elo_rating[row['AwayTeam']] += elo_change(away_result_converted, win_away_prob)

    return points


if __name__ == "__main__":
    df12 = pd.read_csv("fduk_bundesliga_21_22.csv")
    df23 = pd.read_csv("fduk_bundesliga_22_23.csv")

    team_points = get_additional_home_points(df12)
    draw_ratio = create_draw_chance(df12)

    team_points_sum = {team: 0 for team in create_elo_rating().keys()}
    teams_results_definition_list = [range(1), range(4), range(16,18), range(15,16)]
    teams_results_list = [{team: 0 for team in create_elo_rating().keys()} for i in range(len(teams_results_definition_list))]
    iterations = 10000
    for _ in range(iterations):
        points = simulate_season(df23, team_points, draw_ratio)

        sorted_teams = sorted(points.items(), key=lambda k: k[1], reverse=True)
        top_team = sorted_teams[0][0]
        for rang, result in zip(teams_results_definition_list, teams_results_list):
            teams = [sorted_teams[i][0] for i in rang]
            for team in teams:
                result[team] += 1

        for team, pts in points.items():
            team_points_sum[team] += pts

    team_points_avg = {team: round(total_pts / iterations, 2) for team, total_pts in team_points_sum.items()}
    teams_percent_results_list = [
        {team: round((amount / iterations) * 100, 2) for team, amount in team_result.items()} for team_result in teams_results_list
    ]

    sorted_points_avg = sorted(team_points_avg.items(), key=lambda x: x[1], reverse=True)

    data = {
        'Team': list(team_points_avg.keys()),
        'Average Points': list(team_points_avg.values()),
        'Championship (%)': list(teams_percent_results_list[0].values()),
        'Champions League (%)': list(teams_percent_results_list[1].values()),
        'Relegation playoffs (%)': list(teams_percent_results_list[3].values()),
        'Relegation (%)': list(teams_percent_results_list[2].values())
    }

    df = pd.DataFrame(data)
    df_sorted = df.sort_values(by='Average Points', ascending=False)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', False)
    print(df_sorted)

    df_sorted.to_csv('result.csv', index=False)

