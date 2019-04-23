# Rules
You have recently taken a job at Lucky & Co, as a professional dice roller, and need to make as much money as you can! (of course). You will be paid exactly what you roll, $1 for a 1, $2 for a 2 etc. Where's the fun in that? Well, these aren't ordinary dice: starting with $5 in your bank, you must purchase new dice, which will all be rolled each turn. There are many different types of dice, all with different probabilities of rolling the different numbers. Every turn, you take a look at what the dices have done for you, then decide what to invest in. But beware! You have many rivals, all with the same aim in mind, and there are only so many dice in the shop...

## The Dice (StC)
There are many types of dice, which can be split into the following categories:
### Basic Earners
20 of each are available, they are simply rolled and their value is added to the total points:
```none
╔════╦═════════════════════╦═══════╦═════╦════╦════╦════╦════╦═════╗
║ ID ║     Description     ║ Price ║  1  ║ 2  ║ 3  ║ 4  ║ 5  ║  6  ║
╠════╬═════════════════════╬═══════╬═════╬════╬════╬════╬════╬═════╣
║  0 ║ Rolls a 1           ║     1 ║ 100 ║  0 ║  0 ║  0 ║  0 ║   0 ║
║  1 ║ Likely to be low    ║     3 ║  50 ║ 25 ║ 13 ║  7 ║  3 ║   2 ║
║  2 ║ Unlikely to be high ║     6 ║  22 ║ 22 ║ 22 ║ 11 ║ 11 ║  11 ║
║  3 ║ Even chances        ║     9 ║  17 ║ 17 ║ 17 ║ 17 ║ 17 ║  17 ║
║  4 ║ Unlikely to be low  ║    12 ║  11 ║ 11 ║ 11 ║ 22 ║ 22 ║  22 ║
║  5 ║ Likely to be high   ║    16 ║   2 ║  3 ║  7 ║ 13 ║ 25 ║  50 ║
║  6 ║ Rolls a 6           ║    21 ║   0 ║  0 ║  0 ║  0 ║  0 ║ 100 ║
╚════╩═════════════════════╩═══════╩═════╩════╩════╩════╩════╩═════╝
```
### Multipliers
These multiply the points gained by the basic dice by something between 0.33 and 18... 10 of each are available. `r` represents what it rolled, each outcome (1-6) is equally likely:
```none
╔════╦═════════════════╦═══════╗
║ ID ║   Description   ║ Price ║
╠════╬═════════════════╬═══════╣
║  7 ║ Multiply by r/3 ║    10 ║
║  8 ║ Multiply by r/2 ║    13 ║
║  9 ║ Multiply by r   ║    22 ║
║ 10 ║ Multiply by r*2 ║    34 ║
║ 11 ║ Multiply by r*3 ║    50 ║
╚════╩═════════════════╩═══════╝
```
### Attacks
These dice, with 10 of each available, are what makes the game truly interesting. They handle user interaction: each has a set action that it applies to one other random player (except 16):
```none
╔════╦══════════════════════════════════╦═══════╗
║ ID ║              Action              ║ Price ║
╠════╬══════════════════════════════════╬═══════╣
║ 12 ║ See below (too long)             ║    35 ║
║ 13 ║ They get 10 less (not below 0)   ║    45 ║
║ 14 ║ Like 12, but you get the points  ║    60 ║
║ 15 ║ They get 25 less (not below 0)   ║    60 ║
║ 16 ║ Like 14, but you get the points  ║    90 ║
╚════╩══════════════════════════════════╩═══════╝
```
12: A fair dice, the value of which is subtracted from every other users' basic dice roll (not below 0).
### Coins
Miscellaneous other bonuses and actions, each with a 50% chance of happening. There are only 3 of each available:
```none
╔════╦═══════════════════════════════════════════╦═══════╗
║ ID ║                Description                ║ Price ║
╠════╬═══════════════════════════════════════════╬═══════╣
║ 17 ║ Protects you from attacks                 ║    65 ║
║ 18 ║ Roll every basic die again                ║    90 ║
║ 19 ║ Roll every basic and multiplier die again ║   110 ║
║ 20 ║ Square your score                         ║   120 ║
║ 21 ║ Cube your score                           ║   170 ║
╚════╩═══════════════════════════════════════════╩═══════╝
```

## How the dice fall
When working out the points for a round:

 - Every players' coins are flipped. The results are remembered.
 - Every players' basic dice are rolled (as many times as specified by coins). The total of the results for each player is that players' points for this round
 - Every players' multiplier dice are rolled (with extra rolls). Each multiplication is applied on top of the previous one.
 - Any squaring or cubing is applied.
 - For every players' attack dice, a random other player is chosen for each. Unless that player had a shield, the appropriate action is taken.

## A game
A game lasts until first place is 200 points ahead of second place, or until 500 rounds have been played. There are 7 people in each game, who each start with just $5. Every round, each player submits a list of dice that they want to buy. If they ask for a dice that isn't there, ask to pay more than they have, or returns an otherwise invalid move, they do not buy anything that round. If more people ask for a dice than there are of that dice, no-one gets it. After every bot has given their move, and all orders have been resolved, the points for the round are calculated as above, and then added to the total score of each bot. At this point, the win condition is tested. 1st place gets 7 points, second gets 6 and so on. If two players are joined in, for example, 3rd place, they both get 5 points, but the next bot/s get only 3.

## A tournament
In a tournament:

 1. If there are more than 7 bots, the bots will be divided into groups of 7 to play until every bot has played an equal number of games, and there are 7 bots which have a higher total score than the rest.
 2. The top 7 bots play games until one has 50 more points than second place. 
 3. `2` is repeated for all the other groups of seven, and then the leftover bots. Now every bot knows its rightful place!

I will run a tournament every day if possible, which it hopefully will be.

## Coding
You will write a Python class that inherits from `Bot`, and implements `get_orders`, which must accept the following parameters:

 - `money` - how much money each player has (a `tuple` of `int`s)
 - `dice` - what dices each player has (a `tuple` of `tuple`s of `int`s)
 - `index` - your index in the money and dice `tuple`s (an `int`)`
 - `shop` - how many of each dice the shop has (a `dict` of `int: int` pairs)  

Dice are represented in the above by their ID. You may also implement `__init__ (self, random)`, where random is a `random.Random` object, which is the only access to randomness that you are allowed, that is, if I were to run your code again with the same argument to `random` and the same calls to `get_orders`, I would receive the same results. You may also implement any other utility functions you wish. You may not store information between games (already banned but let's do it explicitly), and you may not mess with the controller. You may not team up (how could you?) or use any other competitor's code without significant changes without their permission. You may not programmatically invoke another competitor's code, because that could get circular...
