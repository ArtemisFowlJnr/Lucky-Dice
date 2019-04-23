import argparse
import math
import random
import sys
import pathlib

try:
    import requests
    from lxml import html
    scraping = True
except ImportError:
    print('Unable to import requests and lxml. Scraping Unavailable.')
    scraping = False

try:
    from tabulate import tabulate
except ImportError:
    print('Unable to import tabulate. Using fallback')
    def tabulate(rows, headers, **_):
        sizes = []
        for i in range(len(rows[0])):
            sizes.append(max(map(lambda x: len(str(x[i]))+1,
                                 rows+[headers])))
        def make_len(val, size, blank):
            val = str(val)
            return val + blank*(size-len(val))
        def line(row, sep='|', blank=' '):
            return sep.join(make_len(row[i], sizes[i], blank)
                            for i in range(len(row)))
        ret = ''
        ret += line(headers) + '\n'
        ret += line(['']*len(sizes), '+', '-') + '\n'
        for i in rows:
            ret += line(i) + '\n'
        return ret    

FIRST_NAMES = ['Artemis', 'Holly', 'Turnball', 'Foaly', 'Domovoi',
               'Juliet', 'Lily', 'Minerva', 'Opal', 'Jon', 'Trouble',
               'Julius', 'Mulch', 'Angeline', 'Chix', 'Briar', 'Arno',
               'Leon', 'Jerbal', 'Mervall', 'Descant', 'Caballine',
               'Doodah', 'Angeline', 'Orion', 'Grub', 'Billy', 'Damon',
               'Loafers', 'Gaspard', 'Qwan', 'No1', 'Qweffor', 'General',
               'Gola', 'Ark', 'Raine', 'Vishby', 'Mikhael', 'Giovanni']

LAST_NAMES = ['Fowl', 'Short', 'Root', 'Butler', 'Frond', 'Paradizo',
              'Koboi', 'Spiro', 'Kelp', 'Diggums', 'Verbil', 'Cudgeon',
              'Blunt', 'Abbot', 'Argon', 'Brill', 'Day', 'Kong', 'Kronski',
              'McGuire', 'Scalene', 'Schweem', 'Jnr.', 'Snr.', 'I', 'II',
              'Sool', 'Vinyáya', 'Vassikin', 'Zito']

DICE = {0: (20, 1),
        1: (20, 5),
        2: (20, 9),
        3: (20, 15),
        4: (20, 21),
        5: (20, 23),
        6: (20, 27),
        7: (10, 35),
        8: (10, 40),
        9: (10, 50),
        10: (10, 60),
        11: (10, 65),
        12: (10, 45),
        13: (10, 60),
        14: (10, 60),
        15: (10, 90),
        16: (3, 65),
        17: (3, 90),
        18: (3, 110),
        19: (3, 120),
        20: (3, 170))

def gettype(d_id):
    if d_id < 7:
        return 'basic', -1
    elif d_id < 12:
        return 'multiplier', 6
    elif d_id < 16:
        return 'attack', 11
    else:
        return 'coin', 15
    

class DiceType:
    def __init__(self, d_id, available=0, price=0):
        self.d_id = d_id
        self.available = available
        self.price = price
        self.d_class = gettype(d_id)

    def new(self):
        if self.available:
            self.availabe -= 1
            if self.d_class == 'basic':
                return Basic(self.d_id)
            elif self.d_class == 'multiplier':
                return Mult(seld.d_id)
            elif self.d_class == 'attack':
                return Attack(self.d_id)
            else:
                return Coin(self.d_id)
        return None

    def __str__(self):
        self.available += 1
        return str(self.available - 1) + ' of ' + str(self.new())


class Dice:
    def __init__(self, d_id):
        self.d_id = d_id
        
    def __str__(self):
        d_type, take = gettype(self.d_id)
        return f'{d_type} die number {self.d_id - take} (ID: {self.d_id})'

class Shop:
    def __init__(self, action=None):
        self.dice = {}
        for i in DICE:
            self.dice[i] = DiceType(i, DICE[i][0], DICE[i][1])
        self.dice = action or self.dice

    def buy(self, d_id, this):
        if this.money < self.dice[d_id].price:
            return None
        this.money -= self.dice[d_id].price
        return self.dice[d_id].new()

    def available(self, d_id):
        return self.dice[d_id].available

    def __str__(self):
        return  '\n'.join(str(self.dice[i]) for i in self.dice)

    def __dict__(self):
        ret = {}
        for i in self.dice:
            ret[i] = i.available
        return ret


class Basic(Dice):
    likely = [50, 25, 13, 7, 3, 2]
    unlilkely = ([22] * 3) + ([11] * 3)
    equal = [1] * 6

    def getval(self, random):
        pool = []
        for i in range(len(weights)):
            pool += [i+1] * weights[i]
        r = random.choice(pool)
        if self.d_id == 0:
            self.getval = lambda r: 1
        elif self.d_id == 1:
            self.getval = lambda r: self.choose(Basic.likely, r)
        elif self.d_id == 2:
            self.getval = lambda r: self.choose(Basic.unlikely, r)
        elif self.d_id == 3:
            self.getval = lambda r: self.choose(Basic.equal, r)
        elif self.d_id == 4:
            self.getval = lambda r: self.choose(reversed(Basic.unlikely), r)
        elif self.d_id == 5:
            self.getval = lambda r: self.choose(reversed(Basic.likely), r)
        elif self.d_id == 6:
            self.getval = lambda r: 6


class Mult(Dice):
    def getval(self, random):
        r = random.randint(1, 6)
        if self.d_id == 7:
            return r/3
        elif self.d_id == 8:
            return r/2
        elif self.d_id == 9:
            return r
        elif self.d_id == 10:
            return r*2
        elif self.d_id == 11:
            return r*3

        
class Attack(Dice):
    def action(self, random, others, this):
        p = random.choice(others)
        if p.shield:
            return
        if self.d_id == 12:
            p.turn //= 2
        elif self.d_id == 13:
            p.turn //= 2
            this.turn += p.turn
        elif self.d_id == 14:
            p.turn = 0
        elif self.d_id == 15:
            this.turn = p.turn
            p.turn = 0


class Coin(Dice):
    def action(self, random, this):
        f = random.randint(0, 1)
        if f:
            return
        if self.d_id == 16:
            this.shield == True
        elif self.d_id == 17:
            this.b_rolls += 1
        elif self.d_id == 18:
            this.b_rolls += 1
            this.m_rolls += 1
        elif self.d_id == 19:
            this.square = True
        elif self.d_id == 20:
            this.cube = True


class Bot: 
    def __init__(self, random, index):
        self.random = random
        self.index = index

    def prepare(self):
        pass

    def get_action(self, money, dice, shop):
        raise NotImplemented('This bot has no get_action method!')
        return None


class Player: ###'this'
    def __init__(self, bot, random, index, name):
        self.name = name
        self.money = 5
        self.dice = []
        self.index = index
        try:
            botmod = __import__(pathlib.Path(bot).resolve().stem)
            for i in vars(botmod).values():
                if isinstance(i, type) and issubclass(i, Bot) and i is not Bot:
                    self.bot = i(random, index)
                    break
            self.bot.prepare()
        except Exception as e:
            print('Error on load:', file=sys.stderr)
            print(e, file=sys.stderr)
            self.alive = False
        else:
            self.alive = True

    def get_action(self, money, dice, shop):
        try:
            action = self.bot.get_action(money, dice, shop)
        except Exception as a:
            print('Error on get_action:', file=sys.stderr)
            print(e, file=sys.stderr)
            self.alive = False
        if isinstance(action, dict):
            return action
        self.alive = True
        return None

    def __str__(self):
        return f'{self.name} ({type(self.bot)})'


class Game:
    def __init__(self, bots, seed):
        self.random = random.Random(seed)
        self.firstnames = FIRST_NAMES[:]
        self.lastnames = LAST_NAMES[:]
        self.random.shuffle(self.firstnames)
        self.random.shuffle(self.lastnames)
        self.bots = {}
        n = 0
        for i in bots:
            print(f'Loading from {i}...')
            p = Player(i, self.getrandom(), n, self.getname())
            if p.alive:
                self.bots.append(p)
                print(f'Succesfully loaded {p} from {i}.')
            else:
                self.bots.append(None)
                print(f'The bot from {i} ({p.name}) was unavailable to play today')
            n += 1
        self.turn = 1
        while (self.turn <= 500 and
               max(i.points for i in self.bots).points - 200 <
               min(i.points for i in self.bots).points):
            self.buy(self.get_actions())
            self.roll()
                        
    def get_actions(self):
        money = self.get_money()
        dice = self.get_dice()
        actions = {}
        for i in self.bots:
            if i.alive:
                print(f'Getting action from {i}...')
                action = i.get_action(money, dice, dict(self.shop))
                actions[i.index] == action
                if not action:
                    print(f'{i} was called away for an urgent meeting')
                else:
                    print(f'{i} ordered:')
                    print(Shop(action))
        return actions

    def buy(self, actions):
        wanted = {}
        orders = {}
        for n in actions:
            order = actions[n]
            bot = self.bots[n]
            if sum(map(lambda x: dice[x] * order[x], order)) <= self.bots[n].money:
                orders[n] = order
                for d_id in order:
                    if d_id not in wanted:
                        wanted[d_id] = 0
                    wanted[d_id] += order[d_id]
            else:
                print(f'{bot} spent to much!', file=sys.stderr)
                print(f'{bot} was called away for an urgent meeting')
                bot.alive = False
        blocked = []
        for d_id in wanted:
            if wanted[d_id] > dict(self.shop)[d_id]:
                print(f'There are not enough of {Dice(d_id)}! No one will have any.')
                blocked.append(d_id)
        for n in orders:
            order = orders[n]
            bot = self.bots[n]
            ###WIP
                

    def get_money(self):
        ret = []
        for i in self.bots:
            if i.alive:
                ret.append(i.money)
            else:
                ret.append(None)
        return tuple(ret)

    def get_dice(self):
        ret = []
        for i in self.bots:
            if i.alive:
                ret.append(tuple(i.dice))
            else:
                ret.append(None)
        return tuple(ret)

    def getrandom(self):
        return random.Random(random.getrandbits(600))

    def getname(self):
        return f'{self.fistnames.pop()} {self.lastnames.pop()}'
