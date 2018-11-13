import sys
from collections import defaultdict

from Functional import find

from PS4HistoricGame import PS4HistoricGame

SAVE_FILE = "ps4-stats.txt"

class PS4History:
    def __init__(self):
        self.games = None
        self.load()

    def __iter__(self):
        return self.games.__iter__()

    def save(self):
        try:
            with open(SAVE_FILE, "w") as f: # open as "w" since we rewrite the whole thing
                for g in self.games:
                    print >>f, "game {} {} {}".format(
                        g.message_timestamp,
                        g.channel,
                        ",".join(g.players))

                    for statkey, users in g.stats.iteritems():
                        if len(users):
                            print >>f, "stat {} {}".format(statkey, ",".join(users))
        except IOError:
            print >>sys.stderr, "exception saving state: {}".format(e)

    def load(self):
        games = []
        try:
            with open(SAVE_FILE, "r") as f:
                current_game = None
                for line in iter(f.readline, ""):
                    line = line.rstrip("\n")
                    tokens = line.split(" ")

                    if tokens[0] == "game":
                        message_timestamp = tokens[1]
                        channel = tokens[2]
                        players = tokens[3].split(",")
                        current_game = PS4HistoricGame(message_timestamp, players, channel)
                        games.append(current_game)
                    elif tokens[0] == "stat":
                        if not current_game:
                            continue
                        key = tokens[1]
                        users = filter(len, tokens[2].split(","))
                        current_game.stats[key] = users
                    else:
                        print >>sys.stderr, "unknown {} line \"{}\"".format(SAVE_FILE, line)
        except IOError:
            pass
        self.games = games

    def add_game(self, game):
        if find(lambda g: g.message_timestamp == game.message.timestamp, self.games):
            return
        self.games.append(game.to_historic())
        self.save()

    def find_game(self, gametime):
        return find(lambda g: g.message_timestamp == gametime, self.games)

    def register_stat(self, gametime, user, removed, stat):
        historic_game = self.find_game(gametime)
        if historic_game is None:
            return False

        statdict = historic_game.stats
        if stat not in statdict:
            statdict[stat] = []

        if removed:
            try:
                statdict[stat].remove(user)
            except ValueError:
                pass
        else:
            statdict[stat].append(user)

        self.save()
        return True

    def summary_stats(self, channel, name = None, since = None):
        stats = defaultdict(lambda: defaultdict(int))

        def allow_user(u):
            return name is None or u == name

        for game in self:
            if channel and game.channel != channel:
                continue
            if since and game.message_timestamp < since:
                continue
            for statkey, users in game.stats.iteritems():
                for u in users:
                    if allow_user(u):
                        stats[u][statkey] += 1
                        stats[u]["Total"] += 1

        return stats # { user: { total: int, [stat]: int ... }, ... }
