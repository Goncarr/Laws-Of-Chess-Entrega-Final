from servidor.cards.card import Card


class BlockRow(Card):
    """
    This card blocks a row selected by the user for 1 turn. If an enemy piece was already located
    on the blocked row, they cannot move until the card effect finishes
    """
    def __init__(self, name: str):
        super().__init__(name)
        self.blocked_row = None

    def effect(self, blocked_row, board: list[list]):
        """
        Blocks a row for one turn

        :param blocked_row: row that will be blocked
        :param board:
        :return:
        """

        self.blocked_row = blocked_row
        for rows in range(8):

            #replaces empty rows with an X
            if board[8-int(blocked_row)][rows] == "  ":
                board[8-int(blocked_row)][rows] = "XX"

            elif board[8-int(blocked_row)][rows] == "XX":
                pass

            else:
                piece = board[8-int(blocked_row)][rows]
                piece.blocked = True

    def revert(self, board, current_turn: int):
        """
        Reverts the effect of the card
        :param board: chess board
        :param current_turn: current turn of the game
        :return:
        """
        print(current_turn >= self.used_turn + 1)
        if current_turn >= self.used_turn + 1:
            for rows in range(8):
                if board[8-int(self.blocked_row)][rows] == "XX":
                    board[8-int(self.blocked_row)][rows] = "  "

                elif board[8-int(self.blocked_row)][rows] == "  ":
                    pass

                else:
                    piece = board[8-int(self.blocked_row)][rows]
                    piece.blocked = False