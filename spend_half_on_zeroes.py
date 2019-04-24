from __main__ import Bot


class SpendHalfOnZeroes(Bot):
    def get_action(self, money, dice, shop, turn):
        return {0: money[self.index] // 2}
