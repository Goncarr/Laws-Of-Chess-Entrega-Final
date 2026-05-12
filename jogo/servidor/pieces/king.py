import servidor
from servidor.pieces.piece import Piece
from servidor.pieces.rook import Rook

class King(Piece):
    def __init__(self, piece: str, current_pos):
        super().__init__(piece, current_pos)

    def check_available_moves(self, board):
        """
        This method check if the king is blocked and, if not, the squares that it
        can move onto (empty squares or enemy pieces)
        """
        self.available_moves = []

        if self.blocked:
            return

        current_x = servidor.letter.index(self.current_pos[0])
        current_y = 8 - int(self.current_pos[1])

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                tx, ty = current_x + dx, current_y + dy
                if 0 <= tx < 8 and 0 <= ty < 8:
                    target = board[ty][tx]
                    if target == "  " or target.piece[0] != self.piece[0]:
                        if self.is_move_legal(self, [servidor.letter[tx], 8 - ty], board):
                            self.available_moves.append([servidor.letter[tx], 8 - ty])

        # castling
        rank = int(self.current_pos[1])
        row = 8 - rank
        if not self.has_moved and not self.is_in_check(board):
            # king-side castling
            rook_ks = board[row][7]
            if (isinstance(rook_ks, Rook)
                    and rook_ks.piece[0] == self.piece[0]
                    and not rook_ks.has_moved
                    and board[row][5] == "  "
                    and board[row][6] == "  "):
                if self.is_move_legal(self, [servidor.letter[5], rank], board) and self.is_move_legal(self, [servidor.letter[6], rank], board):
                    self.available_moves.append([servidor.letter[6], rank])

            # queen-side castling
            rook_qs = board[row][0]
            if (isinstance(rook_qs, Rook)
                    and rook_qs.piece[0] == self.piece[0]
                    and not rook_qs.has_moved
                    and board[row][1] == "  "
                    and board[row][2] == "  "
                    and board[row][3] == "  "):
                if self.is_move_legal(self, [servidor.letter[3], rank], board) and self.is_move_legal(self, [servidor.letter[2], rank], board):
                    self.available_moves.append([servidor.letter[2], rank])

    def _raw_king_squares(self, king_piece):
        """
        This method checks the positions the king can take without restrictions
        (having a piece there, blocked square)
        """
        squares = []
        kx = servidor.letter.index(king_piece.current_pos[0])
        ky = 8 - int(king_piece.current_pos[1])
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                tx, ty = kx + dx, ky + dy
                if 0 <= tx < 8 and 0 <= ty < 8:
                    squares.append([servidor.letter[tx], 8 - ty])
        return squares

    def _get_attacked_squares(self, board):
        """
        Returns spaces that are attacked by enemy pieces by checking every piece's
        available_moves
        """
        attacked = []
        for line in board:
            for piece in line:
                if piece == "  " or piece == "XX" or piece.piece[0] == self.piece[0]:
                    continue
                if isinstance(piece, King):
                    attacked.extend(self._raw_king_squares(piece))
                else:
                    piece.check_available_moves(board)
                    attacked.extend(piece.available_moves)
        return attacked

    def is_in_check(self, board):
        """
        This method Checks if the king is in an attacked square.
        """
        attacked_squares = self._get_attacked_squares(board)
        king_pos = [self.current_pos[0], int(self.current_pos[1])]
        return king_pos in attacked_squares

    def is_move_legal(self, piece, target_pos, board):
        """
        This method evaluates if the king is safe if a piece moves or itself moves,
        by doing a temporary move then returning to the original
        """
        original_pos = piece.current_pos
        target_x = servidor.letter.index(target_pos[0])
        target_y = 8 - int(target_pos[1])
        original_target_sq = board[target_y][target_x]

        old_x, old_y = servidor.letter.index(original_pos[0]), 8 - int(original_pos[1])
        board[old_y][old_x] = "  "
        board[target_y][target_x] = piece
        piece.current_pos = target_pos[0] + str(target_pos[1])

        in_check = self.is_in_check(board)

        board[old_y][old_x] = piece
        board[target_y][target_x] = original_target_sq
        piece.current_pos = original_pos

        return not in_check

    def is_checkmate(self, board):
        """
        This method verifies the 3 conditions of chess: check, checkmate and stalemate
        CHECK: The king is in a square that will be attacked

        STALEMATE: If it's a player's turn and there are no possible moves to be done,
        a stalemate is issued.

        CHECKMATE: If there are moves that the player can do, but none will defend
        the king from being attacked, a checkmate is issued
        """
        stalemate = True
        for row in board:
            for piece in row:
                if piece != "  " and piece != "XX" and piece.piece[0] == self.piece[0]:
                    piece.check_available_moves(board)
                    if not piece.available_moves:
                        stalemate = False

        if not self.is_in_check(board) and stalemate:
            return 2

        elif not self.is_in_check(board) and not stalemate:
            return False


        for row in board:
            for piece in row:
                if piece != "  " and piece.piece[0] == self.piece[0]:
                    piece.check_available_moves(board)
                    for move in piece.available_moves:
                        if self.is_move_legal(piece, move, board):
                            return False

        return 1

    def move(self, piece: Piece, move_requested: str, board: list):
        """
        Makes a move if it's a valid one

        :param piece: piece to be moved
        :param move_requested: move that was requested to be made
        :param board: chess borad
        :return:
        """
        current_x, current_y = servidor.letter.index(self.current_pos[0]), 8 - int(self.current_pos[1])
        move_x, move_y = move_requested[0], int(move_requested[1])
        move = [move_x, move_y]
        if move in self.available_moves:
            move[0] = servidor.letter.index(move[0])
            if abs(move[0] - current_x) == 2:
                if move[0] > current_x:
                    rook_x = 7
                    rook_dest_x = current_x + 1
                else:
                    rook_x = 0
                    rook_dest_x = current_x - 1
                rook_piece = board[current_y][rook_x]
                board[current_y][rook_x] = "  "
                board[current_y][rook_dest_x] = rook_piece
                if rook_piece != "  " and rook_piece != "XX":
                    rook_piece.current_pos = servidor.letter[rook_dest_x] + str(8 - current_y)
                    rook_piece.has_moved = True
            board[current_y][current_x] = "  "
            board[8 - move[1]][move[0]] = piece
            self.current_pos = move_requested
            self.has_moved = True