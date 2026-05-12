from servidor.pieces.piece import Piece
from servidor.pieces.queen import Queen
import servidor

class Pawn(Piece):
    def __init__(self,piece:str, current_pos):
        super().__init__(piece,current_pos)
        self.number_of_turns = 0
        self.just_moved_two = False

    def check_available_moves(self, board: list[list]):
        """
        Checks which moves are valid to be made by the piece

        :param board: chess board
        """
        self.available_moves = []

        if self.blocked:
            return

        #defines if the piece is going upward or downward
        direction = 1 if "w" in self.piece else -1

        #gets the x and y of the selected piece
        current_x = self.current_pos[0]
        current_x_id = servidor.letter.index(current_x)
        current_y = int(self.current_pos[1])

        next_y = current_y + direction
        if 1 <= next_y <= 8:
            if board[8 - next_y][current_x_id] == "  ":
                self.available_moves.append([current_x, next_y])

                next_y_2 = current_y + (2 * direction)
                if self.number_of_turns == 0 and 1 <= next_y_2 <= 8:
                    if board[8 - next_y_2][current_x_id] == "  ":
                        self.available_moves.append([current_x, next_y_2])

        for offset in [-1, 1]:
            target_idx_x = current_x_id + offset
            target_y_val = current_y + direction

            if 0 <= target_idx_x <= 7 and 1 <= target_y_val <= 8:
                target_char_x = servidor.letter[target_idx_x]
                target_piece = board[8 - target_y_val][target_idx_x]

                if target_piece != "  " and target_piece != "XX":
                    color = "w" if "w" in self.piece else "b"
                    if color not in target_piece.piece[0]:
                        self.available_moves.append([target_char_x, target_y_val])

        # en passant
        en_passant_target = servidor.EN_PASSANT_TARGET
        if en_passant_target and en_passant_target.piece[0] != self.piece[0]:
            target_x_id = servidor.letter.index(en_passant_target.current_pos[0])
            if abs(target_x_id - current_x_id) == 1 and int(en_passant_target.current_pos[1]) == current_y:
                landing_y = current_y + direction
                if 1 <= landing_y <= 8:
                    landing_square = board[8 - landing_y][target_x_id]
                    if landing_square == "  ":
                        self.available_moves.append([servidor.letter[target_x_id], landing_y])


    def move(self, piece: Piece, move_requested:str, board:list):
        """
        Makes a move if it's a valid one

        :param piece: piece to be moved
        :param move_requested: move that was requested to be made
        :param board: chess borad
        :return:
        """
        current_x, current_y = servidor.letter.index(self.current_pos[0]), 8 - int(self.current_pos[1])
        old_rank = int(self.current_pos[1])
        move_x, move_y = move_requested[0], int(move_requested[1])
        print(self.available_moves)
        move = [move_x, move_y]
        print(move)
        if move in self.available_moves:
            print("Move in dict")
            move[0] = servidor.letter.index(move[0])
            double_step = abs(move[1] - old_rank) == 2
            print(move)
            # en passant capture
            destination_row = 8 - move[1]
            if move[0] != current_x and board[destination_row][move[0]] == "  ":
                board[current_y][move[0]] = "  "
            board[current_y][current_x] = "  "
            promotion_rank = 8 if "w" in self.piece else 1
            if move[1] == promotion_rank:
                color = self.piece[0]
                board[destination_row][move[0]] = Queen(f"{color}Q", move_requested)
                self.alive = False
            else:
                board[destination_row][move[0]] = piece
                self.current_pos = move_requested
            self.number_of_turns += 1
            self.just_moved_two = double_step
            self.has_moved = True
            return self.just_moved_two
