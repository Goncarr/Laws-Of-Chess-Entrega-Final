
#----- Connection information -----#

PORT = 35000
SERVER_ADDRESS = "localhost"

#----- Client-Server Commands -----#

COMMAND_SIZE = 9
INT_SIZE = 8
END_OP = "stop     "
PLAY   = "play     " # client chooses to enter the queue to play
MOVE   = "move     " # it's the player's turn to play
WAIT   = "wait     " # it's the other player's turn
SELECT = "select   " # player decides to select something
EMPTY =  "empty    " # notifies if the square is empty
OPPO_COL = "oppo_col " # notifies if the piece that is trying to move it's not theirs
VALID_SQUARE = "valid_sqr" # valid square with a piece to move
INVALID_COMMAND = "invalid  " # notifies if the command wasn't a valid one
CHECK = "check    " # notifies the player is in check
CHECKMATE = "checkmate" # notifies that the game has come to a checkmate
STALEMATE = "stalemate" # notifies that the game has come to a stalemate
CARDS = "cards    " # allows the player to select cards
NORMALTURN = "normturn " # hidden value that notifies a normal turn
CARDMINIGAME = "cardmgame" # hidden value that notifies a turn with a card minigame
CLIENTE_ID = "clienteid" # identifies the connection as a CLIENT
LOGIN = "login    " # allows the client to log in


# ----