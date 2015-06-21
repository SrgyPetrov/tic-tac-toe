# import random


class PlayField(object):

    def __init__(self):
        self.cells = [''] * 9

    def all_equal(self, items):
        return not items or items == [items[0]] * len(items)

    def get_opponent(self, player):
        return 'x' if player == 'o' else 'o'

    def get_winner(self):
        winning_rows = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
                        [0, 3, 6], [1, 4, 7], [2, 5, 8],
                        [0, 4, 8], [2, 4, 6]]

        for row in winning_rows:
            if self.cells[row[0]] != '' and self.all_equal([self.cells[i] for i in row]):
                return self.cells[row[0]]
        return ''

    def get_valid_moves(self, moves_to_check=range(9)):
        return [pos for pos in moves_to_check if self.cells[pos] == '']

    def is_game_over(self):
        return self.get_winner() or not self.get_valid_moves()

    def make_move(self, move, player):
        self.cells[move] = player

    def undo_move(self, move):
        self.make_move(move, '')

    # def get_random_move(self, moves):
    #     """ Gets a random valid move from the list, returns None if there is no valid moves """
    #     possible_moves = self.get_valid_moves(moves_to_check=moves)

    #     if len(possible_moves) != 0:
    #         return random.choice(possible_moves)
    #     else:
    #         return None