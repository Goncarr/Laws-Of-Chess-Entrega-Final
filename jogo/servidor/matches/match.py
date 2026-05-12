import json
import random
import socket
import threading
import time
import string
import servidor
from servidor.board.board import Board
from servidor.cards.blockRow import BlockRow
from servidor.cards.impressment import Impressment
from servidor.cards.promotion import Promotion
from servidor.pieces.pawn import Pawn


class Match:
    def __init__(self, active_matches, player_white, white_name, player_black, black_name):
        self.active_matches = active_matches
        self.white = player_white
        self.black = player_black
        self.white_name = white_name
        self.black_name = black_name
        self.white_cards = []
        self.black_cards = []
        self.active_effects = []
        self.status = None
        self.player_turn = 0
        self._lock = threading.Lock()

    # ---------------------- interaction with sockets ------------------------------

    def receive_int(self, connect: socket.socket, n_bytes: int) -> int:
        data = b""
        while len(data) < n_bytes:
            chunk = connect.recv(n_bytes - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return int.from_bytes(data, byteorder='big', signed=True)

    def send_int(self, connect: socket.socket, value: int, n_bytes: int) -> None:
        connect.send(value.to_bytes(n_bytes, byteorder="big", signed=True))

    def receive_str(self, connect, n_bytes: int) -> str:
        data = b""
        while len(data) < n_bytes:
            chunk = connect.recv(n_bytes - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return data.decode()

    def send_str(self, connect, value: str) -> None:
        connect.send(value.encode())

    def send_object(self, connection, obj) -> None:
        """1º: envia tamanho, 2º: envia dados."""
        data = json.dumps(obj).encode('utf-8')
        size = len(data)
        self.send_int(connection, size, servidor.INT_SIZE)
        connection.send(data)

    def receive_object(self, connection):
        """1º: lê tamanho, 2º: lê dados."""
        size = self.receive_int(connection, servidor.INT_SIZE)
        data = b""
        while len(data) < size:
            chunk = connection.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Connection closed before all data received")
            data += chunk
        return json.loads(data.decode('utf-8'))

    # ---------------------- match logic ------------------------------

    def _broadcast(self, message) -> None:
        """Sends a message to both players."""
        self.send_object(self.white, message)
        self.send_object(self.black, message)

    def _current_player(self):
        """Defines which player plays (White always starts in this case)"""
        return self.white if self.player_turn % 2 == 0 else self.black

    def _current_cards(self, color = None):
        """Defines which player plays (White always starts in this case)"""
        if color == "w":
            return self.white_cards
        elif color == "b":
            return self.black_cards

        return self.white_cards if self.player_turn % 2 == 0 else self.black_cards

    def _simple_current_cards(self):
        """Defines which player plays (White always starts in this case)"""
        simple_cards = []
        for card in self._current_cards():
            simple_cards.append(card.name)
        return simple_cards

    def _current_color(self) -> str:
        """Identifies the color of the grids piece"""
        return "w" if self.player_turn % 2 == 0 else "b"

    def _clear_en_passant(self, color: str) -> None:
        if servidor.EN_PASSANT_TARGET and servidor.EN_PASSANT_TARGET.piece[0] != color:
            servidor.EN_PASSANT_TARGET = None

    def _notify_turn(self) -> None:
        """Sends a message to both clients indicating which player is playing currently"""
        label = "White" if self._current_color() == "w" else "Black"
        self._broadcast(f"It's {label}'s turn!")

    def _move(self, current, color, board):
        # coordinates of the piece
        piece_coord = self.receive_object(current)
        print(f"[DEBUG] Received piece_coord: {repr(piece_coord)}")

        x = servidor.letter.index(piece_coord[0])
        y = 8 - int(piece_coord[1])
        origin_sq = board.board[y][x]

        # Updating the player with the square's status
        if origin_sq == "  ":
            self.send_object(current, servidor.EMPTY)
            return False
        if origin_sq.piece[0] != color:
            self.send_object(current, servidor.OPPO_COL)
            return False

        self.send_object(current, servidor.VALID_SQUARE)
        print(f"[DEBUG] Sent VALID_SQUARE, waiting for MOVE command")

        # Player selects the space to move onto
        command = self.receive_str(current, servidor.COMMAND_SIZE)
        print(f"[DEBUG] Received move command: {repr(command)}")

        if command != servidor.MOVE:
            self.send_object(current, servidor.INVALID_COMMAND)
            return False

        origin_sq.check_available_moves(board.board)
        moves = origin_sq.available_moves
        self.send_object(current, moves)

        dest_coord = self.receive_object(current)
        print(f"[DEBUG] Received destination: {repr(dest_coord)}")

        dx = dest_coord[0]  # Ex: f
        dy = int(dest_coord[1])  # Ex: 5
        origin_sq.move(origin_sq, [dx, dy], board.board)

        self._clear_en_passant(color)
        if isinstance(origin_sq, Pawn) and origin_sq.just_moved_two:
            servidor.EN_PASSANT_TARGET = origin_sq

        return True

    def _use_cards(self, current, board):
        self.send_object(current, self._simple_current_cards())  # Sends cards to player
        card_use_index = self.receive_object(current)  # Receives player's choice
        print(self._current_cards())
        card_use = self._current_cards()[card_use_index]
        if card_use.name == "BlockRow":
            row = self.receive_object(current)
            card_use.use_card(self.player_turn)
            card_use.effect(row, board.board)
            self.active_effects.append(card_use)
            self._current_cards().pop(card_use_index)
        elif card_use.name == "Impressment":
            piece = self.receive_object(current)
            card_use.effect(piece, board.board)
            self._current_cards().pop(card_use_index)

        elif card_use.name == "Promotion":
            piece = self.receive_object(current)
            promotion = self.receive_object(current)
            card_use.effect(piece, promotion, board.board)
            self._current_cards().pop(card_use_index)
            board.put_pieces(self.white_map, self.black_map)

        self._clear_en_passant(self._current_color())

    def _card_minigame(self):
        blockrow = BlockRow("BlockRow")
        promotion = Promotion("Promotion")
        impressment = Impressment("Impressment")
        cards = [blockrow, promotion, impressment]
        card = random.choice(cards)
        self._broadcast("The card minigame is about to happen. Be wary of a button press.")
        self._broadcast(f"The winning player receives {card.name} card!")
        time.sleep(random.randint(1, 10))
        alphabet = list(string.ascii_lowercase)
        letter = random.choice(alphabet)
        self._broadcast(f"The letter you must send is {letter}!")

        white_input, white_time = self.receive_object(self.white)
        black_input, black_time = self.receive_object(self.black)
        print(white_input)
        print(letter)
        print(letter == black_input)
        print(white_time > black_time)

        if white_input != letter and black_input != letter:
            self._broadcast("Both players missed the input!")
            return

        if ((white_time < black_time and white_input == letter)
                or (white_time > black_time and black_input != letter)):

            # Send the specific card name ONLY to the winner so their UI updates
            self.send_object(self.white, f"You won {card.name}!")
            self.send_object(self.black, "Opponent won the card!")
            self._current_cards("w").append(card)

        elif ((white_time > black_time and black_input == letter)
              or (white_time < black_time and white_input != letter)):

            # Send the specific card name ONLY to the winner so their UI updates
            self.send_object(self.black, f"You won {card.name}!")
            self.send_object(self.white, "Opponent won the card!")
            self._current_cards("b").append(card)
        else:
            self._broadcast("It's a tie! No one receives a card!")

    def _request_command(self, board: Board):
        """Request for the current player to indicate a piece to move"""
        current = self._current_player()
        color = self._current_color()
        waiting = self.black if color == "w" else self.white

        self.send_str(current, servidor.MOVE)
        self.send_str(waiting, servidor.WAIT)

        while True:
            # Verifies if player wants to select a piece
            # (Later this will include card selection or forfeit)
            command = self.receive_str(current, servidor.COMMAND_SIZE)
            print(f"[DEBUG] command={repr(command)}")

            if command == servidor.SELECT:
                valid_move = self._move(current, color, board)
                if valid_move:
                    return

            elif command == servidor.CARDS:
                self._use_cards(current, board)
                return  # <--- ADD THIS RETURN STATEMENT TO END THE TURN!

            else:
                self.send_object(current, servidor.INVALID_COMMAND)
                continue

    def start_game(self) -> None:
        try:
            # Welcoming and server print
            self._broadcast("Welcome")
            print(f"Match started: {self.white_name} vs {self.black_name}")

            # Tell White who Black is, and Black who White is
            self.send_object(self.white, f"OPP: {self.black_name}")
            self.send_object(self.black, f"OPP: {self.white_name}")

            # Generate FRESH piece sets for this specific match
            self.white_map = servidor.get_default_white_map()
            self.black_map = servidor.get_default_black_map()

            # Prints out the board with the pieces already inserted
            board = Board()
            board.create_board()
            board.put_pieces(self.white_map, self.black_map)

            while True:
                # Extract the specific kings from this match's map
                white_king = self.white_map["wK"][0]
                black_king = self.black_map["bK"][0]

                # Checks which king is checked/checkmated
                check_king = white_king if self.player_turn % 2 == 1 else black_king

                # Send board and turn message
                self._broadcast(board.simple_print_board())
                self._notify_turn()

                # Card acquiring minigame
                chance = random.randint(0,2)
                if chance == 0:
                    self._broadcast(servidor.CARDMINIGAME)
                    self._card_minigame()
                else:
                    self._broadcast(servidor.NORMALTURN)

                # Send directive (MOVE/WAIT) and process the move
                self._request_command(board)

                # Verifying in what condition the king is
                statistics = servidor.ACTIVE

                if check_king.is_checkmate(board.board) == 1:
                    statistics = servidor.CHECKMATE
                elif check_king.is_checkmate(board.board) == 2:
                    statistics = servidor.STALEMATE
                elif check_king.is_in_check(board.board):
                    statistics = servidor.CHECK

                # Updating clients of the conditions of the game
                self._broadcast(statistics)

                if statistics in (servidor.CHECKMATE, servidor.STALEMATE):
                    break  # Game finishes

                for card in self.active_effects:
                    card.revert(board.board, self.player_turn)
                    print(self.player_turn)
                    print(card.used_turn)

                self.player_turn += 1

    # These conditions verify if something wrong came with any of the players
    # connections
        except (ConnectionResetError, ConnectionError, OSError) as e:
            print(f"Match ended due to connection error: {e}")
        finally:
            self._close_connections()
            with self._lock:
                # Add this 'in' check to prevent a fatal ValueError crash!
                if self in self.active_matches:
                    self.active_matches.remove(self)

    def _close_connections(self) -> None:
        for conn in (self.white, self.black):
            try:
                conn.close()
            except OSError:
                pass

