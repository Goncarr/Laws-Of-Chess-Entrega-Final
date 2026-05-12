import servidor
from servidor.pieces.bishop import Bishop
from servidor.cards.card import Card
from servidor.pieces.king import King
from servidor.pieces.knight import Knight
from servidor.pieces.pawn import Pawn
from servidor.pieces.piece import Piece
from servidor.pieces.queen import Queen
from servidor.pieces.rook import Rook


class Promotion(Card):
    """
    This card lets you increase the level of one of your pieces to a piece of higher value,
    excluding the queen and king.
    Each piece has a specific rank they can go to, which goes in this order:
    pawn -> bishop/knight -> rook -> queen
    """
    def __init__(self, name: str):
        super().__init__(name)

    def effect(self, piece_coordinates: str, evol: str, board: list[list]):
        current_x = servidor.letter.index(piece_coordinates[0])
        current_y = 8 - int(piece_coordinates[1])

        old_piece:Piece = board[current_y][current_x]
        print(old_piece.piece)
        color = old_piece.piece[0]
        new_piece = None

        #Queens and kings cannot be upgraded
        if isinstance(old_piece, Queen) or isinstance(old_piece.piece, King):
            print("You can't upgrade a queen or king!")
            return False

        # Check which piece it needs to upgrade to
        elif isinstance(old_piece,Pawn):
            match evol.lower():
                case "knight":
                    new_piece = Knight(f"{color}T", piece_coordinates)
                case "bishop":
                    new_piece = Bishop(f"{color}B", piece_coordinates)

        elif isinstance(old_piece,Bishop) or isinstance(old_piece, Knight):
            new_piece = Rook(f"{color}R", piece_coordinates)

        elif isinstance(old_piece, Rook):
                new_piece = Queen(f"{color}Q", piece_coordinates)


        if new_piece is None:
            print("This piece does not exist!")
            return False

        #check which colors board needs to make changes
        if new_piece:
            if old_piece.piece[0] == "w":
                servidor.DEFAULT_WHITE_BOARD_MAP[old_piece.piece].remove(old_piece)
                servidor.DEFAULT_WHITE_BOARD_MAP[new_piece.piece].append(new_piece)
            else:
                servidor.DEFAULT_BLACK_BOARD_MAP[old_piece.piece].remove(old_piece)
                servidor.DEFAULT_BLACK_BOARD_MAP[new_piece.piece].append(new_piece)

            return True

        return False