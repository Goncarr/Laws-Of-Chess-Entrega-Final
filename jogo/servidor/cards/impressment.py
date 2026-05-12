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

    def effect(self, piece_coordinates: str, board: list[list]):

        current_x = servidor.letter.index(piece_coordinates[0])
        current_y = 8- int(piece_coordinates[1])

        #dictionary with odds of each piece
        piece_type = {
            "P": 0,
            "T": 6,
            "B": 6,
            "R": 14,
            "Q": 20,
        }

        #recieves the cooridnates of the captured piece
        impressed_piece:Piece = board[current_y][current_x]

        chance = randint(0, piece_type[impressed_piece.piece[1]])
        print(chance)
        print(piece_type[impressed_piece.piece[1]])

        #if it was uncussessful, returns a message
        if chance != 0:
            print("Failed at capturing the enemy piece!")
        else:
            #checks the color of the captured piece and replaces the color it belongs to
            if impressed_piece.piece[0] == "w":
                servidor.DEFAULT_WHITE_BOARD_MAP[impressed_piece.piece].remove(impressed_piece)
                impressed_piece.piece = impressed_piece.piece.replace("w","b")
                print(impressed_piece.piece)
                servidor.DEFAULT_BLACK_BOARD_MAP[impressed_piece.piece].append(impressed_piece)
            else:
                servidor.DEFAULT_BLACK_BOARD_MAP[impressed_piece.piece].remove(impressed_piece)
                impressed_piece.piece = impressed_piece.piece.replace("b","w")
                print(impressed_piece.piece)
                servidor.DEFAULT_WHITE_BOARD_MAP[impressed_piece.piece].append(impressed_piece)










