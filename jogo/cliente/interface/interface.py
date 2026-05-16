import cliente
import json
import socket
import time
import threading
import sys
import os

try:
    import pygame
except ImportError:
    raise SystemExit("pygame is required: pip install pygame")

# Window Dimensions & Layout
WINDOW_W, WINDOW_H = 1000, 800
SQUARE = 70  # Shrunk to 70 to fit perfectly between the top and bottom panels
BOARD_X, BOARD_Y = 40, 120  # X shifted to 40 to center the board under the panels

# Colors
C_LIGHT = (221, 221, 196)
C_DARK = (118, 149, 84)
C_SELECT = (220, 50, 50)
C_MOVE = (106, 135, 66)
C_CHECK = (220, 50, 50)
C_BG = (40, 40, 40)
C_BORDER = (86, 117, 52)

LETTERS = list("abcdefgh")


def draw_rrect(surf, color, rect, radius=10):
    pygame.draw.rect(surf, color, pygame.Rect(rect), border_radius=radius)


class Interface:
    def __init__(self):
        self.connection = socket.socket()
        self.connection.connect((cliente.SERVER_ADDRESS, cliente.PORT))

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Laws of Chess")
        self.clock_tick = pygame.time.Clock()

        self._load_assets()

        # game state
        self.board_data = None
        self.selected_sq = None
        self.legal_moves = []
        self.status_msg = ""
        self.turn_msg = ""
        self.opponent_name = "Opponent"
        self.is_my_turn = False
        self.game_over = False
        self.in_check = False
        self.cards = []
        self.log = []

        self.minigame_active = False
        self.minigame_letter = ""
        self.minigame_start = 0.0
        self.minigame_prompt = ""
        self.minigame_answer = None

        self.screen_state = "menu"  # "menu" | "waiting" | "game"

        self.login_active = False
        self.login_name = ""
        self.login_result = ""

        self._net_lock = threading.Lock()

        # sync primitives
        self._action_choice = None
        self._piece_selection = None
        self._dest_selection = None
        self._card_chosen = None
        self._input_text = ""
        self._input_prompt = ""
        self._input_ready = True

        self.card_buttons = []
        self.move_button = None

    def _load_assets(self):
        # Fonts
        try:
            self.font_lg = pygame.font.Font('interface/font/Pixeltype.ttf', 100)
            self.font_md = pygame.font.Font('interface/font/Pixeltype.ttf', 50)
            self.font_sm = pygame.font.Font('interface/font/Pixeltype.ttf', 40)
            self.font_xs = pygame.font.Font('interface/font/Pixeltype.ttf', 25)
        except Exception:
            self.font_lg = pygame.font.SysFont('Arial', 46)
            self.font_md = pygame.font.SysFont('Arial', 26)
            self.font_sm = pygame.font.SysFont('Arial', 18)
            self.font_xs = pygame.font.SysFont('Arial', 14)

        # Helper to load and scale images gracefully
        def load_scale(path, size):
            try:
                return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
            except:
                s = pygame.Surface(size, pygame.SRCALPHA)
                s.fill((150, 150, 150, 128))
                return s

        # Chess Pieces - scaled to fit within the 70x70 squares
        self.piece_images = {
            "wK": load_scale('interface/assets/images/white_king.png', (70, 70)),
            "wQ": load_scale('interface/assets/images/white_queen.png', (70, 70)),
            "wR": load_scale('interface/assets/images/white_rook.png', (70, 70)),
            "wB": load_scale('interface/assets/images/white_bishop.png', (70, 70)),
            "wT": load_scale('interface/assets/images/white_knight.png', (70, 70)),
            "wP": load_scale('interface/assets/images/white_pawn.png', (55, 55)),
            "bK": load_scale('interface/assets/images/black_king.png', (70, 70)),
            "bQ": load_scale('interface/assets/images/black_queen.png', (70, 70)),
            "bR": load_scale('interface/assets/images/black_rook.png', (70, 70)),
            "bB": load_scale('interface/assets/images/black_bishop.png', (70, 70)),
            "bT": load_scale('interface/assets/images/black_knight.png', (70, 70)),
            "bP": load_scale('interface/assets/images/black_pawn.png', (55, 55))
        }

        # Cards
        self.card_images = {
            "BlockRow": load_scale('interface/assets/images/card_BlockRow.png', (95, 145)),
            "Impressment": load_scale('interface/assets/images/card_Impressment.png', (95, 145)),
            "Promotion": load_scale('interface/assets/images/card_Promotion.png', (95, 145))
        }
        self.empty_card = pygame.Surface((95, 145))
        self.empty_card.fill((200, 200, 200))
        pygame.draw.rect(self.empty_card, (86, 117, 52), self.empty_card.get_rect(), 2)

        # UI Elements
        try:
            player_raw = pygame.image.load('interface/images/player_logo.png').convert_alpha()
            self.player_image = pygame.transform.rotozoom(player_raw, 0, 0.18)
            clock_raw = pygame.image.load('interface/images/clock.png').convert_alpha()
            self.clock_img = pygame.transform.rotozoom(clock_raw, 0, 0.18)
        except Exception:
            self.player_image = pygame.Surface((100, 100))
            self.clock_img = pygame.Surface((80, 80))

    # socket functions
    def receive_int(self, conn, n):
        d = b""
        while len(d) < n:
            c = conn.recv(n - len(d))
            if not c: raise ConnectionError("closed")
            d += c
        return int.from_bytes(d, 'big', signed=True)

    def send_int(self, conn, v, n):
        conn.send(v.to_bytes(n, 'big', signed=True))

    def receive_str(self, conn, n):
        d = b""
        while len(d) < n:
            c = conn.recv(n - len(d))
            if not c: raise ConnectionError("closed")
            d += c
        return d.decode()

    def send_str(self, conn, v):
        conn.send(v.encode())

    def send_object(self, conn, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_int(conn, len(data), cliente.INT_SIZE)
        conn.send(data)

    def receive_object(self, conn):
        sz = self.receive_int(conn, cliente.INT_SIZE)
        d = b""
        while len(d) < sz:
            c = conn.recv(sz - len(d))
            if not c: raise ConnectionError("closed")
            d += c
        return json.loads(d.decode('utf-8'))

    # log
    def _log(self, msg):
        self.log.append(str(msg))
        if len(self.log) > 10: self.log.pop(0)

    # waiting functions
    def _wait(self, attr):
        while True:
            time.sleep(0.04)
            with self._net_lock:
                v = getattr(self, attr)
                if v is not None:
                    setattr(self, attr, None)
                    return v

    def _wait_input(self, prompt):
        with self._net_lock:
            self._input_text = ""
            self._input_prompt = prompt
            self._input_ready = False
        while True:
            time.sleep(0.04)
            with self._net_lock:
                if self._input_ready:
                    v = self._input_text
                    self._input_prompt = ""
                    return v

    def _wait_minigame(self):
        self.minigame_answer = None
        while True:
            time.sleep(0.04)
            with self._net_lock:
                if self.minigame_answer is not None:
                    return self.minigame_answer

    # coordinate
    def _px_to_sq(self, px, py):
        if BOARD_X <= px < BOARD_X + (8 * SQUARE) and BOARD_Y <= py < BOARD_Y + (8 * SQUARE):
            col = (px - BOARD_X) // SQUARE
            row = (py - BOARD_Y) // SQUARE
            return f"{LETTERS[col]}{8 - row}"
        return None

    def _move_set(self):
        return {f"{m[0]}{m[1]}" for m in self.legal_moves}

    # game thread
    def _play_thread(self):
        try:
            # 1. Catch "PLEASE WAIT"
            self._log(self.receive_object(self.connection))

            # 2. Catch "Welcome"
            self._log(self.receive_object(self.connection))

            # 3. Catch the Opponent's Name
            opp_msg = self.receive_object(self.connection)
            if isinstance(opp_msg, str) and opp_msg.startswith("OPP: "):
                with self._net_lock:
                    self.opponent_name = opp_msg.replace("OPP: ", "")
            else:
                self._log(opp_msg)

            # NOW we are safely synced up to receive the board!
            while True:
                board = self.receive_object(self.connection)
                with self._net_lock:
                    self.board_data = board

                turn = self.receive_object(self.connection)
                with self._net_lock:
                    self.turn_msg = turn
                self._log(turn)

                mg = self.receive_object(self.connection)
                if mg == cliente.CARDMINIGAME:
                    self._log(self.receive_object(self.connection))
                    self._log(self.receive_object(self.connection))
                    msg = self.receive_object(self.connection)
                    letter = msg.split()[-1].rstrip("!")
                    with self._net_lock:
                        self.minigame_letter = letter
                        self.minigame_prompt = msg
                        self.minigame_active = True
                        self.minigame_start = time.time()

                    answer = self._wait_minigame()
                    self.send_object(self.connection, answer)

                    mg_result = self.receive_object(self.connection)
                    self._log(mg_result)

                    # FIX 1: Auto-update the UI slots instantly by reading the result!
                    with self._net_lock:
                        for c_name in ["BlockRow", "Promotion", "Impressment"]:
                            if c_name in mg_result:
                                self.cards.append(c_name)
                                break
                        self.minigame_active = False

                directive = self.receive_str(self.connection, cliente.COMMAND_SIZE)
                if directive == cliente.MOVE:
                    with self._net_lock:
                        self.is_my_turn = True
                        self.status_msg = "Your turn - select piece"
                    self._do_choices()
                    with self._net_lock:
                        self.is_my_turn = False
                elif directive == cliente.WAIT:
                    with self._net_lock:
                        self.status_msg = "Waiting for opponent..."

                stats = self.receive_object(self.connection)
                with self._net_lock:
                    self.in_check = False
                if stats == cliente.CHECK:
                    self._log("King is in Check!")
                    with self._net_lock:
                        self.in_check = True
                elif stats == cliente.CHECKMATE:
                    self._log("Checkmate! Game over.")
                    with self._net_lock:
                        self.game_over = True
                        self.status_msg = "CHECKMATE - game over"
                    break
                elif stats == cliente.STALEMATE:
                    self._log("Stalemate! Game over.")
                    with self._net_lock:
                        self.game_over = True
                        self.status_msg = "STALEMATE - game over"
                    break

        except (ConnectionResetError, ConnectionError, OSError) as e:
            self._log(f"Connection error: {e}")
            with self._net_lock:
                self.status_msg = "Connection lost"

    def _do_choices(self):
        while True:
            action = self._wait("_action_choice")

            if action == "select":
                self.send_str(self.connection, cliente.SELECT)
                piece_sq = self._wait("_piece_selection")
                self.send_object(self.connection, piece_sq)
                status = self.receive_object(self.connection)

                if status == cliente.EMPTY:
                    self._log("Empty square.")
                    with self._net_lock:
                        self.status_msg = "Empty square - try again"
                elif status == cliente.OPPO_COL:
                    self._log("Not your piece.")
                    with self._net_lock:
                        self.status_msg = "Not your piece - try again"
                elif status == cliente.VALID_SQUARE:
                    self.send_str(self.connection, cliente.MOVE)
                    moves = self.receive_object(self.connection)
                    with self._net_lock:
                        self.selected_sq = piece_sq
                        self.legal_moves = moves
                        self.status_msg = "Select destination"
                    dest = self._wait("_dest_selection")
                    with self._net_lock:
                        self.selected_sq = None
                        self.legal_moves = []
                    self.send_object(self.connection, dest)
                    return




            elif action == "cards":

                self.send_str(self.connection, cliente.CARDS)

                cards_list = self.receive_object(self.connection)

                with self._net_lock:
                    self.cards = cards_list

                choice = self._wait("_card_chosen")

                self.send_object(self.connection, choice)

                # Safeguard in case of desync

                if 0 <= choice < len(cards_list):

                    card_name = cards_list[choice]

                    if card_name == "BlockRow":

                        row_str = self._wait_input("Block which row? (1-8)")

                        try:

                            row_int = int(row_str)

                        except ValueError:

                            row_int = 1

                        self.send_object(self.connection, row_int)


                    elif card_name == "Promotion":

                        piece = self._wait_input("Piece to promote (e.g. e2)")

                        evol = self._wait_input("Promote to (knight/bishop/rook/queen)")

                        self.send_object(self.connection, piece)

                        self.send_object(self.connection, evol)


                    elif card_name == "Impressment":

                        piece = self._wait_input("Enemy piece to steal (e.g. d5)")

                        self.send_object(self.connection, piece)

                    # FIX: Delete the card from the UI immediately so it disappears!

                    with self._net_lock:

                        self.cards.pop(choice)


                else:

                    self._log("That card slot is empty!")

                return

    # draw functions
    def _draw_board(self):
        legal = self._move_set()
        check_sq = None
        if self.in_check and self.board_data:
            clr = "w" if "White" in self.turn_msg else "b"
            for r, row in enumerate(self.board_data):
                for c, cell in enumerate(row):
                    if cell and f"{clr}K" in cell:
                        check_sq = f"{LETTERS[c]}{8 - r}"

        for row in range(8):
            for col in range(8):
                x = BOARD_X + col * SQUARE
                y = BOARD_Y + row * SQUARE
                sq = f"{LETTERS[col]}{8 - row}"
                color = C_DARK if (row + col) % 2 == 1 else C_LIGHT
                pygame.draw.rect(self.screen, color, (x, y, SQUARE, SQUARE))
                pygame.draw.rect(self.screen, C_BORDER, (x, y, SQUARE, SQUARE), 2)

                # Highlights
                if sq == self.selected_sq:
                    pygame.draw.rect(self.screen, C_SELECT, [x + 1, y + 1, SQUARE - 2, SQUARE - 2], 3)
                elif sq in legal:
                    s = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
                    s.fill((*C_MOVE, 120))
                    self.screen.blit(s, (x, y))
                elif sq == check_sq:
                    s = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
                    s.fill((*C_CHECK, 140))
                    self.screen.blit(s, (x, y))

                # Render Image
                if self.board_data:
                    cell = self.board_data[row][col]
                    if cell and cell not in ("--", "XX", ""):
                        img = self.piece_images.get(cell)
                        if img:
                            img_rect = img.get_rect(center=(x + SQUARE // 2, y + SQUARE // 2))
                            self.screen.blit(img, img_rect)

    def _draw_panel(self):
        mouse = pygame.mouse.get_pos()

        # player 1 (Top)
        pygame.draw.rect(self.screen, C_LIGHT, (0, 0, 640, 120))
        pygame.draw.rect(self.screen, C_BORDER, (0, 0, 640, 120), 2)
        p1_name = self.font_md.render(self.opponent_name, False, (0, 0, 0))
        self.screen.blit(self.player_image, (0, 0))
        self.screen.blit(p1_name, (130, 45))

        # player 2 (Bottom)
        pygame.draw.rect(self.screen, C_LIGHT, (0, 680, 640, 120))
        pygame.draw.rect(self.screen, C_BORDER, (0, 680, 640, 120), 2)
        p2_name_str = self.login_name if self.login_name else 'You'
        p2_name = self.font_md.render(p2_name_str, False, (0, 0, 0))
        self.screen.blit(self.player_image, (0, 680))
        self.screen.blit(p2_name, (130, 725))

        # timer box (Top Right)
        pygame.draw.rect(self.screen, C_LIGHT, (640, 0, 360, 120))
        pygame.draw.rect(self.screen, C_BORDER, (640, 0, 360, 120), 2)
        self.screen.blit(self.clock_img, (660, 13))
        self.screen.blit(self.font_sm.render(self.turn_msg[:26], True, (0, 0, 0)), (770, 20))
        self.screen.blit(self.font_sm.render(self.status_msg[:26], True, (200, 50, 50)), (770, 60))

        # log box (Middle Right)
        pygame.draw.rect(self.screen, C_LIGHT, (640, 120, 360, 300))
        pygame.draw.rect(self.screen, C_BORDER, (640, 120, 360, 300), 2)
        self.screen.blit(self.font_md.render("LOG", True, (0, 0, 0)), (655, 130))
        pygame.draw.line(self.screen, (0, 0, 0), (655, 170), (980, 170), 2)
        for k, line in enumerate(self.log[-8:]):
            self.screen.blit(self.font_sm.render(line[:30], True, (40, 40, 40)), (655, 180 + k * 28))

            # cards box (Bottom Right)
            pygame.draw.rect(self.screen, C_LIGHT, (640, 420, 360, 380))
            pygame.draw.rect(self.screen, C_BORDER, (640, 420, 360, 380), 2)
            self.screen.blit(self.font_md.render("YOUR CARDS", True, (0, 0, 0)), (655, 435))
            pygame.draw.line(self.screen, (0, 0, 0), (655, 475), (980, 475), 2)

            self.card_buttons = []

            # ALWAYS draw 3 slots so the user has something to click
            for k in range(3):
                card_x = 655 + (k * 105)
                card_y = 500
                btn = pygame.Rect(card_x, card_y, 95, 145)

                hov = btn.collidepoint(mouse) and self.is_my_turn
                y_offset = -15 if hov else 0

                # If we happen to know the card, draw it. Otherwise, draw an empty/mystery slot.
                if k < len(self.cards):
                    card_name = self.cards[k]
                    img = self.card_images.get(card_name, self.empty_card)
                else:
                    img = self.empty_card

                self.screen.blit(img, (card_x, card_y + y_offset))

                if hov:
                    pygame.draw.rect(self.screen, (100, 180, 255),
                                     [card_x - 2, card_y + y_offset - 2, 99, 149], 3, border_radius=5)

                self.card_buttons.append((btn, k))

        # Move button (Bottom inside Cards Box)
        if self.is_my_turn:
            btn = pygame.Rect(660, 720, 320, 50)
            hov = btn.collidepoint(mouse)
            draw_rrect(self.screen, (150, 180, 150) if hov else (86, 117, 52), btn, 8)
            lbl = self.font_md.render("Make Move", True, (255, 255, 255))
            self.screen.blit(lbl, (btn.centerx - lbl.get_width() // 2, btn.centery - lbl.get_height() // 2))
            self.move_button = btn
        else:
            self.move_button = None

    def _draw_minigame(self):
        s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))

        # Painel ainda maior (800x400) e centrado no ecrã (O ecrã total tem 1000x800)
        box_w, box_h = 900, 400
        box = pygame.Rect(WINDOW_W // 2 - box_w // 2, WINDOW_H // 2 - box_h // 2, box_w, box_h)

        draw_rrect(self.screen, (55, 55, 55), box, 14)
        pygame.draw.rect(self.screen, (212, 175, 55), box, 2, border_radius=14)

        # Textos ajustados com espaçamento proporcional e fontes maiores para melhor leitura
        for i, (text, font, color, dy) in enumerate([
            ("Card Minigame!", self.font_lg, (212, 175, 55), 40),  # Título maior
            (self.minigame_prompt, self.font_lg, (230, 230, 230), 140),  # Letra pedida
            ("Press the key on your keyboard!", self.font_md, (100, 180, 255), 250),  # Instrução
            (f"Elapsed: {time.time() - self.minigame_start:.2f}s", self.font_md, (200, 200, 100), 320),  # Tempo
        ]):
            surf = font.render(text, True, color)
            self.screen.blit(surf, (box.centerx - surf.get_width() // 2, box.y + dy))

    def _draw_input(self):
        prompt = self._input_prompt
        s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, 0))

        # Painel aumentado para 650x200 para o texto da Promotion caber facilmente
        box_w, box_h = 650, 200
        box = pygame.Rect(WINDOW_W // 2 - box_w // 2, WINDOW_H // 2 - box_h // 2, box_w, box_h)

        draw_rrect(self.screen, (221, 221, 196), box, 12)
        pygame.draw.rect(self.screen, (86, 117, 52), box, 2, border_radius=12)

        # Texto da Prompt (ex: "Promote to...") centrado
        prompt_surf = self.font_md.render(prompt, True, (0, 0, 0))
        self.screen.blit(prompt_surf, (box.centerx - prompt_surf.get_width() // 2, box.y + 25))

        # Caixa branca onde o texto é digitado
        field_w, field_h = 550, 50
        field = pygame.Rect(box.centerx - field_w // 2, box.y + 85, field_w, field_h)
        draw_rrect(self.screen, (255, 255, 255), field, 6)
        pygame.draw.rect(self.screen, (86, 117, 52), field, 2, border_radius=6)

        # Texto que o jogador está a escrever
        input_surf = self.font_md.render(self._input_text + "|", True, (0, 0, 0))
        self.screen.blit(input_surf, (field.x + 15, field.y + 10))

        # Texto de ajuda "Press Enter..." centrado na parte de baixo
        help_surf = self.font_xs.render("Press Enter to confirm", True, (100, 100, 100))
        self.screen.blit(help_surf, (box.centerx - help_surf.get_width() // 2, box.y + 155))

    def _draw_menu(self):
        self.screen.fill(C_BG)
        mouse = pygame.mouse.get_pos()

        t = self.font_lg.render("Laws of Chess", True, (212, 175, 55))
        self.screen.blit(t, (WINDOW_W // 2 - t.get_width() // 2, 150))

        self._mb_play = pygame.Rect(WINDOW_W // 2 - 130, 300, 260, 50)
        self._mb_login = pygame.Rect(WINDOW_W // 2 - 130, 380, 260, 50)
        self._mb_quit = pygame.Rect(WINDOW_W // 2 - 130, 460, 260, 50)

        for btn, label, base in [
            (self._mb_play, "Play", (230, 230, 230)),
            (self._mb_login, "Login", (230, 230, 230)),
            (self._mb_quit, "Quit", (230, 230, 230)),
        ]:
            hov = btn.collidepoint(mouse)
            color = (100, 180, 255) if hov and label != "Quit" else ((220, 50, 50) if hov else base)

            lbl = self.font_md.render(label, True, color)
            self.screen.blit(lbl, (btn.centerx - lbl.get_width() // 2, btn.centery - lbl.get_height() // 2))

        if self.login_result:
            r = self.font_sm.render(self.login_result, True, (100, 180, 255))
            self.screen.blit(r, (WINDOW_W // 2 - r.get_width() // 2, 540))

        if self.login_active:
            self._draw_input_overlay("Enter your account name:")

    def _draw_input_overlay(self, prompt):
        s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (0, 0))
        box = pygame.Rect(WINDOW_W // 2 - 200, WINDOW_H // 2 - 70, 400, 140)
        draw_rrect(self.screen, (221, 221, 196), box, 12)
        pygame.draw.rect(self.screen, (86, 117, 52), box, 2, border_radius=12)
        self.screen.blit(self.font_md.render(prompt, True, (0, 0, 0)), (box.x + 16, box.y + 16))
        field = pygame.Rect(box.x + 16, box.y + 55, 370, 34)
        draw_rrect(self.screen, (255, 255, 255), field, 6)
        pygame.draw.rect(self.screen, (86, 117, 52), field, 2, border_radius=6)
        self.screen.blit(self.font_md.render(self.login_name + "|", True, (0, 0, 0)), (field.x + 8, field.y + 5))
        self.screen.blit(self.font_xs.render("Press Enter to confirm", True, (100, 100, 100)),
                         (box.x + 16, box.y + 108))

    def _draw_waiting(self):
        self.screen.fill(C_BG)

        # Check if the network thread reported a lost connection
        if self.status_msg == "Connection lost":
            m = self.font_md.render("Connection to server lost. Please restart.", True, (220, 50, 50))
        else:
            m = self.font_lg.render("Waiting for opponent...", True, (100, 180, 255))

        self.screen.blit(m, (WINDOW_W // 2 - m.get_width() // 2, WINDOW_H // 2 - 30))
    def _draw_game(self):
        self.screen.fill(C_BG)
        self._draw_board()
        self._draw_panel()
        if self.minigame_active:
            self._draw_minigame()
        elif self._input_prompt and not self._input_ready:
            self._draw_input()
        if self.game_over:
            s = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150))
            self.screen.blit(s, (0, 0))
            go = self.font_lg.render("GAME OVER", True, (212, 175, 55))
            sm = self.font_md.render(self.status_msg, True, (255, 255, 255))
            self.screen.blit(go, (WINDOW_W // 2 - go.get_width() // 2, WINDOW_H // 2 - 40))
            self.screen.blit(sm, (WINDOW_W // 2 - sm.get_width() // 2, WINDOW_H // 2 + 20))

    # event handlers
    def _handle_menu(self, ev):
        if ev.type == pygame.QUIT: self._quit()
        if self.login_active:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    self._do_login(self.login_name)
                    self.login_active = False
                elif ev.key == pygame.K_BACKSPACE:
                    self.login_name = self.login_name[:-1]
                else:
                    self.login_name += ev.unicode
            return
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self._mb_play.collidepoint(ev.pos):
                self.send_str(self.connection, cliente.PLAY)
                self.screen_state = "waiting"
                threading.Thread(target=self._play_thread, daemon=True).start()
            elif self._mb_login.collidepoint(ev.pos):
                self.login_active = True
                self.login_name = ""
            elif self._mb_quit.collidepoint(ev.pos):
                self._quit()

    def _handle_game(self, ev):
        if ev.type == pygame.QUIT: self._quit()

        if self.minigame_active:
            if ev.type == pygame.KEYDOWN and ev.unicode:
                with self._net_lock:
                    self.minigame_answer = [ev.unicode, time.time() - self.minigame_start]
            return

        if self._input_prompt and not self._input_ready:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    with self._net_lock:
                        self._input_ready = True
                elif ev.key == pygame.K_BACKSPACE:
                    with self._net_lock:
                        self._input_text = self._input_text[:-1]
                else:
                    with self._net_lock:
                        self._input_text += ev.unicode
            return

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            pos = ev.pos

            # card buttons
            for btn, idx in self.card_buttons:
                if btn.collidepoint(pos) and self.is_my_turn:
                    # FIX 2: Only trigger the server if the slot ACTUALLY has a card in it!
                    if idx < len(self.cards):
                        with self._net_lock:
                            self._action_choice = "cards"
                            self._card_chosen = idx
                        return
                    else:
                        with self._net_lock:
                            self.status_msg = "Slot empty! Play a minigame to win cards."
                        return

            if self.move_button and self.move_button.collidepoint(pos) and self.is_my_turn:
                with self._net_lock:
                    self._action_choice = "select"
                return

            if self.is_my_turn:
                sq = self._px_to_sq(*pos)
                if sq is None: return
                legal = self._move_set()

                if self.selected_sq is None:
                    with self._net_lock:
                        if self._action_choice is None:
                            self._action_choice = "select"
                        self._piece_selection = sq
                else:
                    if sq in legal:
                        with self._net_lock:
                            self._dest_selection = sq
                    elif sq == self.selected_sq:
                        with self._net_lock:
                            self._dest_selection = sq
                    else:
                        with self._net_lock:
                            self.status_msg = "Touch-move! Pick a valid square."

    def _do_login(self, name):
        try:
            self.send_str(self.connection, cliente.LOGIN)
            self.send_object(self.connection, name)
            result = self.receive_object(self.connection)
            self.login_result = result
            self._log(result)
        except Exception as e:
            self.login_result = f"Error: {e}"

    def _quit(self):
        try:
            self.send_str(self.connection, cliente.END_OP)
        except:
            pass
        self.connection.close()
        pygame.quit()
        sys.exit()

    def execute(self):
        self.send_str(self.connection, cliente.CLIENTE_ID)

        self._mb_play = pygame.Rect(0, 0, 0, 0)
        self._mb_login = pygame.Rect(0, 0, 0, 0)
        self._mb_quit = pygame.Rect(0, 0, 0, 0)

        while True:
            for ev in pygame.event.get():
                if self.screen_state == "menu":
                    self._handle_menu(ev)
                else:
                    self._handle_game(ev)

            if self.screen_state == "waiting" and self.board_data is not None:
                self.screen_state = "game"

            if self.screen_state == "menu":
                self._draw_menu()
            elif self.screen_state == "waiting":
                self._draw_waiting()
            else:
                self._draw_game()

            pygame.display.flip()
            self.clock_tick.tick(60)