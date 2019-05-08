import random
from collections import defaultdict
from ps4formatting import format_user, number_emojis, pretty_players

class Stats:
    scrub = "scrub"
    class Towerfall:
        headhunters = "towerfall.headhunters"
        lastmanstanding = "towerfall.lastmanstanding"
        teams = "towerfall.teams"

    class Fifa:
        win = "fifa.win"
        win_pens = "fifa.win_pens"

    class Foosball:
        win_1 = "foosball.win_1"
        win_2 = "foosball.win_2"
        win_3 = "foosball.win_3"

    @staticmethod
    def pretty(stat):
        return pretty[stat] if stat in pretty else stat

pretty = {
    Stats.scrub: "Scrub",
    Stats.Towerfall.headhunters: "Headhunters",
    Stats.Towerfall.lastmanstanding: "Survival",
    Stats.Towerfall.teams: "Teams",
    Stats.Fifa.win: "Win",
    Stats.Fifa.win_pens: "Pens",
    Stats.Foosball.win_1: "Win",
    Stats.Foosball.win_2: "Win",
    Stats.Foosball.win_3: "Win",
}

def channel_is_towerfall(channel):
    return "towerfall" in channel or "_test" in channel

def channel_is_fifa(channel):
    return "fifa" in channel

def channel_is_foosball(channel):
    return "line-of-glory" in channel

def should_suggest_teams(channel):
    return channel_is_fifa(channel) or channel_is_towerfall(channel)

def limit_game_to_single_win(channel):
    return channel_is_fifa(channel)

class Fixture:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2

    def __str__(self):
        return "{} and {} vs. {} and {}".format(
            format_user(self.team1[0]),
            format_user(self.team1[1]),
            format_user(self.team2[0]),
            format_user(self.team2[1])
        )

def foosball_fixtures(players):
    # 4 players, 3 fixtures
    # abcd -> ab-cd, ac-bd, ad-bc
    if len(players) != 4:
        return None

    a, b, c, d = players

    return [
        Fixture((a, b), (c, d)),
        Fixture((a, c), (b, d)),
        Fixture((a, d), (b, c)),
    ]

def suggest_teams(game):
    if not should_suggest_teams(game.channel):
        return None

    if len(game.players) <= 2:
        return None

    split = game.players[:]
    random.shuffle(split)

    team1 = split[:len(split)/2]
    team2 = split[len(split)/2:]

    return "Team 1: {}\nTeam 2: {}".format(pretty_players(team1), pretty_players(team2))

def emoji_numberify(s, i):
    return ":{}: {}".format(number_emojis[i], s)

def scrub_entry(player, i):
    return emoji_numberify(format_user(player), i)

def vote_message(game):
    if channel_is_towerfall(game.channel):
        return ("Game open for ranking:\n"
            + "  Scrub of the match: {}\n"
            + "  Headhunters winner (:skull_and_crossbones:)\n"
            + "  Last man standing (:bomb:)\n"
            + "  Team deathmatch (:v:)\n"
        ).format(
            ", ".join([scrub_entry(player, i) for i, player in enumerate(game.players)])
        )

    if channel_is_fifa(game.channel):
        return ("Game open for ranking:\n"
            + "  Scrub of the match: {}\n"
            + "  Winner: :soccer:\n"
            + "  Winner (on penalties): :goal_net:\n"
        ).format(
            ", ".join([scrub_entry(player, i) for i, player in enumerate(game.players)])
        )

    if channel_is_foosball(game.channel):
        fixtures = foosball_fixtures(game.players)
        if fixtures:
            return (
                "Fixtures:\n{}"
            ).format(
                "\n".join(emoji_numberify(fixture, i) for i, fixture in enumerate(fixtures))
            )

    return None

def gametype_from_channel(channel):
    if channel_is_foosball(channel):
        return "foosball"
    return "ps4"

def channel_statmap(channel):
    if channel_is_towerfall(channel):
        return {
            "headhunters": Stats.Towerfall.headhunters,
            "skull_and_crossbones": Stats.Towerfall.headhunters,
            "crossed_swords": Stats.Towerfall.headhunters,
            "last-man-standing": Stats.Towerfall.lastmanstanding,
            "bomb": Stats.Towerfall.lastmanstanding,
            "team-deathmatch": Stats.Towerfall.teams,
            "man_and_woman_holding_hands": Stats.Towerfall.teams,
            "man-man-boy-boy": Stats.Towerfall.teams,
            "couple": Stats.Towerfall.teams,
            "v": Stats.Towerfall.teams,
            "handshake": Stats.Towerfall.teams,
        }

    if channel_is_fifa(channel):
        return {
            "soccer": Stats.Fifa.win,
            "goal_net": Stats.Fifa.win_pens,
        }

    if channel_is_foosball(channel):
        return {
            number_emojis[0]: Stats.Foosball.win_1,
            number_emojis[1]: Stats.Foosball.win_2,
            number_emojis[2]: Stats.Foosball.win_3,
        }

    return None
