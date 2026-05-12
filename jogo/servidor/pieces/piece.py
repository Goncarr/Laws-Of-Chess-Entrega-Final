import servidor

class Piece:
    """
    Superclass for the pieces on the board
    """
    def __init__(self, piece: str, current_pos: str):
        """
        :param current_pos:str -  current position of the piece
        :param piece:str - name of the piece
        :param available_moves: list - moves that are valid to be made
        :param self.alive - checks if the piece is alive or not
        :param self.blocked - checks if the piece is blocked by a row

        """
        self.current_pos: str = current_pos
        self.available_moves: list = []
        self.piece: str = piece
        self.alive = True
        self.blocked = False
        self.has_moved = False




