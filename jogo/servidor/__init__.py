# Setup for White Pieces
from servidor.pieces.bishop import Bishop
from servidor.pieces.king import King
from servidor.pieces.knight import Knight
from servidor.pieces.pawn import Pawn
from servidor.pieces.queen import Queen
from servidor.pieces.rook import Rook

def get_default_white_map():
    return {
        "wP": [Pawn("wP", "a2"), Pawn("wP", "b2"), Pawn("wP", "c2"), Pawn("wP", "d2"), Pawn("wP", "e2"), Pawn("wP", "f2"), Pawn("wP", "g2"), Pawn("wP", "h2")],
        "wK": [King("wK", "e1")],
        "wR": [Rook("wR", "a1"), Rook("wR", "h1")],
        "wB": [Bishop("wB", "f1"), Bishop("wB", "c1")],
        "wQ": [Queen("wQ", "d1")],
        "wT": [Knight("wT", "b1"), Knight("wT", "g1")]
    }

def get_default_black_map():
    return {
        "bP": [Pawn("bP", "a7"), Pawn("bP", "b7"), Pawn("bP", "c7"), Pawn("bP", "d7"), Pawn("bP", "e7"), Pawn("bP", "f7"), Pawn("bP", "g7"), Pawn("bP", "h7")],
        "bK": [King("bK", "e8")],
        "bR": [Rook("bR", "a8"), Rook("bR", "h8")],
        "bB": [Bishop("bB", "f8"), Bishop("bB", "c8")],
        "bQ": [Queen("bQ", "d8")],
        "bT": [Knight("bT", "b8"), Knight("bT", "g8")]
    }

# Letter checker for board analysis
letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
EN_PASSANT_TARGET = None

#Commands
COMMAND_SIZE = 9
INT_SIZE = 8
END_OP = "stop     "
PLAY   = "play     "
MOVE   = "move     "
WAIT   = "wait     "
SELECT = "select   "
EMPTY =  "empty    "
OPPO_COL = "oppo_col "
VALID_SQUARE = "valid_sqr"
INVALID_COMMAND = "invalid  "
CHECK = "check    "
CHECKMATE = "checkmate"
STALEMATE = "stalemate"
CARDS = "cards    "
NORMALTURN = "normturn "
CARDMINIGAME = "cardmgame"
GESTOR_ID = "gestor_id"
CLIENTE_ID = "clienteid"
LOGIN = "login    "
ACTIVE = "active   "
PORT = 35000
SERVER_ADDRESS = "localhost"