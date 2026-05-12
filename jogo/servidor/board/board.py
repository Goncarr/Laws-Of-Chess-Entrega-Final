import servidor
from servidor.pieces.piece import Piece

class Board:
    def __init__(self):
        self.board: list = []

    def create_board(self):
        self.board = [0] * 8

        for collumn in range(len(self.board)):
            self.board[collumn] = ["  "] * 8

    """_summary_
        This function inserts the pieces onto the board

        @parametros
        board:list - 8 by 8 matrix resembling the board
        white_pieces:dict - dictionary for white pieces
        black_pieces:dict - dictionary for black pieces
    """
    def put_pieces(self, white_pieces: dict[str, list[Piece]], black_pieces: dict):
        for piece, squares in white_pieces.items():
            for square in squares:
                piece_pos = square.current_pos
                x, y = servidor.letter.index(piece_pos[0]), 8 - int(piece_pos[1])
                self.board[y][x] = square
        for piece, squares in black_pieces.items():
            for square in squares:
                piece_pos = square.current_pos
                x, y = servidor.letter.index(piece_pos[0]), 8 - int(piece_pos[1])
                self.board[y][x] = square

    def print_board(self):
        for i, row in enumerate(self.board):
            print(8 - i, end=": ")
            for j, col in enumerate(row):
                if col == "  " or col == "XX":
                    print(col, end=" ")
                else:
                    print(col.piece, end=" ")
            print("\n")
        print(
            " " * 3 + "a" + " " * 2 + "b" + " " * 2 + "c" + " " * 2 + "d" + " " * 2 + "e" + " " * 2 + "f" + " " * 2 + "g" + " " * 2 + "h")

    def simple_print_board(self):
        serializable_matrix = []
        for row in self.board:
            row_data = []
            for col in row:
                if isinstance(col, str):
                    row_data.append(col.strip() if col.strip() else "--")
                else:
                    row_data.append(col.piece)
            serializable_matrix.append(row_data)
        return serializable_matrix
