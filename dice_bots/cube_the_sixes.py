from __main__ import Bot

class CubeTheSixes(Bot):
    def get_action(self, money, dice, shop, turn):
        if money[self.index] > 170 and money[self.index] < 250:
            return {20: 1}
        if money[self.index] < 54:
            return {0: money[self.index] // 2}
        return {6: money[self.index] // 54}
