from random import  randint
import servidor
from servidor.cards.card import Card
from servidor.pieces.piece import Piece

class Impressment(Card):
    """
    This card lets you take one of enemy player pieces to be yours. Depending on what piece it is
    the odds of having success could be higher or lowers (EX: a pawn has an higher chance of beings
    captured than a queen)
    """
    def __init__(self, name: str):
        super().__init__(name)

    def effect(self, piece_coordinates: str, board: list[list], white_map: dict, black_map: dict):
        current_x = servidor.letter.index(piece_coordinates[0])
        current_y = 8 - int(piece_coordinates[1])

        piece_type = {
            "P": 0,
            "T": 6,
            "B": 6,
            "R": 14,
            "Q": 20,
        }

        impressed_piece: Piece = board[current_y][current_x]

        # Validação caso a coordenada esteja vazia
        if impressed_piece == "  ":
            print("Nenhuma peça nessa posição!")
            return False

        chance = randint(0, piece_type[impressed_piece.piece[1]])
        print(chance)

        if chance != 0:
            print("Failed at capturing the enemy piece!")
            return False
        else:
            # Troca de donos usando os dicionários específicos da partida atual
            if impressed_piece.piece[0] == "w":
                white_map[impressed_piece.piece].remove(impressed_piece)
                impressed_piece.piece = impressed_piece.piece.replace("w", "b")
                black_map[impressed_piece.piece].append(impressed_piece)
            else:
                black_map[impressed_piece.piece].remove(impressed_piece)
                impressed_piece.piece = impressed_piece.piece.replace("b", "w")
                white_map[impressed_piece.piece].append(impressed_piece)

            return True