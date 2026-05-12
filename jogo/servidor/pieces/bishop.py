from servidor.pieces.piece import Piece
import servidor

class Bishop(Piece):
    """
    Bishop piece which can only move diagonally
    """
    def __init__(self,piece:str, current_pos):
        super().__init__(piece,current_pos)

    def check_available_moves(self, board: list[list]):
        """
        Checks which moves are valid to be made by the piece

        :param board: chess board
        """

        #clears the old moves
        self.available_moves = []

        if self.blocked:
            return

        #obtains the position x and y of the piece
        current_x = servidor.letter.index(self.current_pos[0])
        current_y = 8 - int(self.current_pos[1])


        #directions the piece can move to
        directions = [
            (-1, -1),
            (1, -1),
            (-1, 1),
            (1, 1)
        ]

        for dy, dx in directions:
            for i in range(1, 8):
                new_y = current_y + (dy * i)
                new_x = current_x + (dx * i)

                if 0 <= new_y < 8 and 0 <= new_x < 8:
                    target = board[new_y][new_x]

                    #if the position is an empty grid, the position is valid
                    if target == "  ":
                        self.available_moves.append([servidor.letter[new_x], 8 - new_y])

                    #if the position is blocked, the move is invalid
                    elif target == "XX":
                        pass

                    else:
                        #if it's an enemy piece, the position is valid
                        if self.piece[0] != target.piece[0]:
                            self.available_moves.append([servidor.letter[new_x], 8 - new_y])

                        break
                else:
                    break


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
        print(self.available_moves)
        move = [move_x, move_y]
        print(move)
        if move in self.available_moves:
            print("Move in dict")
            move[0] = servidor.letter.index(move[0])
            print(move)
            board[current_y][current_x] = "  "
            board[8 - move[1]][move[0]] = piece
            self.current_pos = move_requested