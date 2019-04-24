import argparse
import math
import random
import sys
import runpy
import string

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

def get_seed():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.sample(chars, 6))

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
        20: (3, 170)}

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
        self.d_class = gettype(d_id)[0]

    def new(self):
        self.available -= 1
        if self.d_class == 'basic':
            return Basic(self.d_id)
        elif self.d_class == 'multiplier':
            return Mult(seld.d_id)
        elif self.d_class == 'attack':
            return Attack(self.d_id)
        else:
            return Coin(self.d_id)

    def __str__(self):
        self.available += 1
        return str(self.available - 1) + ' of ' + str(self.new())


class Dice:
    def __init__(self, d_id):
        self.d_id = d_id
        
    def __str__(self):
        d_type, take = gettype(self.d_id)
        return '%s die number %s (ID: %s)' % (d_type, self.d_id - take, self.d_id)

class Shop:
    def __init__(self, action=None):
        if action:
            self.dice = {}
            for i in action:
                self.dice[i] = DiceType(i, action[i])
        else:
            self.dice = {}
            for i in DICE:
                self.dice[i] = DiceType(i, DICE[i][0], DICE[i][1])

    def buy(self, d_id, this):
        this.money -= self.dice[d_id].price
        this.dice.append(self.dice[d_id].new())

    def available(self, d_id):
        return self.dice[d_id].available

    def __str__(self):
        return  '\n'.join(str(self.dice[i]) for i in self.dice)

    def asdict(self):
        ret = {}
        for i in self.dice:
            ret[i] = self.dice[i].available
        return ret


class Basic(Dice):
    likely = [50, 25, 13, 7, 3, 2]
    unlilkely = ([22] * 3) + ([11] * 3)
    equal = [1] * 6

    def choose(self, weights, random):
        pool = []
        for i in range(len(weights)):
            pool += [i+1] * weights[i]
        return random.choice(pool)

    def action(self, random, this):
        if self.d_id == 0:
            this.turn += 1
        elif self.d_id == 1:
            this.turn += self.choose(Basic.likely, random)
        elif self.d_id == 2:
            this.turn += self.choose(Basic.unlikely, random)
        elif self.d_id == 3:
            this.turn += self.choose(Basic.equal, random)
        elif self.d_id == 4:
            this.turn += self.choose(reversed(Basic.unlikely), random)
        elif self.d_id == 5:
            this.turn += self.choose(reversed(Basic.likely), random)
        else:
            this.turn += 6


class Mult(Dice):
    def action(self, random, this):
        r = random.randint(1, 6)
        if self.d_id == 7:
            this.turn *= r//3
        elif self.d_id == 8:
            this.turn *= r//2
        elif self.d_id == 9:
            this.turn *= r
        elif self.d_id == 10:
            this.turn *= r*2
        elif self.d_id == 11:
            this.turn *= r*3

        
class Attack(Dice):
    def action(self, random, this, others):
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
            this.turn += p.turn
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

    def get_action(self, money, dice, shop, turn):
        raise NotImplemented('This bot has no get_action method!')
        return None


class Player:
    def __init__(self, bot, random, index, name):
        self.name = name
        self.money = 5
        self.dice = []
        self.index = index
        self.shield = False
        self.square = False
        self.cube = False
        self.m_rolls = 1
        self.b_rolls = 1
        self.turn = 0
        try:
            if modname in sys.modules:
                del sys.modules[modname]
            botmod = runpy.run_path(bot)
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

    def reset(self):
        self.shield = False
        self.square = False
        self.cube = False
        self.m_rolls = 1
        self.b_rolls = 1
        self.money += self.turn
        self.turn = 0

    def get_action(self, money, dice, shop, turn):
        try:
            action = self.bot.get_action(money, dice, shop, turn)
        except Exception as a:
            print('Error on get_action:', file=sys.stderr)
            print(e, file=sys.stderr)
            self.alive = False
        if isinstance(action, dict):
            return action
        self.alive = True
        return None

    def __str__(self):
        return '%s (%s)' % (self.name, type(self.bot).__name__)


class Game:
    def __init__(self, bots, seed):
        self.random = random.Random(seed)
        self.firstnames = FIRST_NAMES[:]
        self.lastnames = LAST_NAMES[:]
        self.random.shuffle(self.firstnames)
        self.random.shuffle(self.lastnames)
        self.shop = Shop()
        self.bots = []
        n = 0
        for i in bots:
            print('Loading from ' + i + '...')
            p = Player(i, self.getrandom(), n, self.getname())
            if p.alive:
                self.bots.append(p)
                print('Succesfully loaded %s from %s.' % (p, i))
            else:
                self.bots.append(None)
                print('The bot from %s (%s) was unavailable to play today' % (i, p.name))
            n += 1
        self.main()

    def main(self):
        self.turn = 1
        while (self.turn <= 500 and
               max(i.money for i in self.bots) - 200 <
               min(i.money for i in self.bots)):
            self.buy(self.get_actions())
            self.roll()
            self.turn += 1
        for bot in self.bots:
            if bot.alive:
                bot.reset()
        self.over()
                        
    def get_actions(self):
        money = self.get_money()
        dice = self.get_dice()
        actions = {}
        for i in self.bots:
            if i.alive:
                print('Getting action from ' + i + '...')
                action = i.get_action(money, dice, self.shop.asdict(), self.turn)
                actions[i.index] = action
                if not action:
                    print(i + ' was called away for an urgent meeting')
                else:
                    print(i + ' ordered:')
                    print(Shop(action))
        return actions

    def buy(self, actions):
        wanted = {}
        orders = {}
        for n in actions:
            order = actions[n]
            bot = self.bots[n]
            if sum(map(lambda x: DICE[x][1] * order[x], order)) <= self.bots[n].money:
                orders[n] = order
                for d_id in order:
                    if d_id not in wanted:
                        wanted[d_id] = 0
                    wanted[d_id] += order[d_id]
            else:
                print(bot + ' spent to much!', file=sys.stderr)
                print(bot + ' was called away for an urgent meeting')
                bot.alive = False
        blocked = []
        for d_id in wanted:
            if wanted[d_id] > self.shop.asdict()[d_id]:
                print('There are not enough of %s! No one will have any.' % Dice(d_id))
                blocked.append(d_id)
        for n in orders:
            order = orders[n]
            bot = self.bots[n]
            for d_id in order:
                for _ in range(order[d_id]):
                    self.shop.buy(d_id, bot)

    def roll(self):
        basic = {}
        mults = {}
        attks = {}
        coins = {}
        for bot in self.bots:
            if bot.alive:
                bot.reset()
                for l in (basic, mults, attks, coins):
                    l[bot.index] = []
                for die in bot.dice:
                    if isinstance(die, Basic):
                        basic[bot.index].append(die)
                    elif isinstance(die, Mult):
                        mults[bot.index].append(die)
                    elif isinstance(die, Attack):
                        attks[bot.index].append(die)
                    else:
                        coins[bot.index].append(die)
        for n in coins:
            bot = self.bots[n]
            owns = coins[n]
            for coin in owns:
                coin.action(self.random, bot)
        for n in basic:
            bot = self.bots[n]
            owns = basic[n]
            while bot.b_rolls:
                bot.b_rolls -= 1
                for die in owns:
                    die.action(self.random, bot)
        for n in mults:
            bot = self.bots[n]
            owns = mults[n]
            while bot.m_rolls:
                bot.m_rolls -= 1
                for die in owns:
                    die.action(self.random, bot)
        for n in attks:
            bot = self.bots[n]
            owns = mults[n]
            others = [i for i in self.bots if i != bot]
            for die in owns:
                die.action(self.random, bot, others)

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
        return self.firstnames.pop() + ' ' + self.lastnames.pop()

    def over(self):
        print(tabulate([(str(bot), bot.money) for i in self.bots],
                       ['Name', 'Money']))


bots = ['dice_bots/spend_half_on_zeroes.py']
seed = get_seed()
Game(bots, seed)
