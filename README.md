# Laws of Chess

Laws of Chess is a multiplayer, client-server chess game implemented in Python. This game brings special cards to the game to make it more thoughtful and innovative.
The application features a robust server that handles matchmaking, game logic, and concurrent matches, along with separate clients for players and server administrators (Gestores).

## Members of the group
* Gonçalo Arruda - 2024109624
* Hernâni Araújo - 2024111863

## Features

* **Client-Server Architecture**: A dedicated server manages game state, connections, and matchmaking, allowing multiple games to run concurrently.
* **Multiplayer Matchmaking**: Players can join a queue and be automatically matched with an opponent to start a game. It includes "Pulse Checks" to prevent matching with disconnected "ghost" sockets.
* **Innovative Card System**: Adds a unique twist to classic chess with special abilities.
    * **BlockRow**: Temporarily makes an entire row on the board impassable.
    * **Impressment**: Provides a chance to steal an opponent's piece and convert it to your side.
    * **Promotion**: Instantly upgrade one of your pieces.
* **Card Acquisition Minigame**: During a match, players have a random chance to compete in a quick reflex minigame to acquire a random card.
* **Gestor (Administrator) Client**: A separate terminal client for administrators to monitor the server's status, including the number of online players and active games.
* **Complete Chess Logic**: Implements standard chess rules, including piece movements, check, checkmate, stalemate detection, and **En Passant**.
* **Account System**: Players can log into accounts, saving their username for the match.

## Project Structure

The repository is organized into three main components:

* `jogo/servidor/`: Contains all the server-side logic.
    * `maquina/`: The main server entry point (`maquina.py`) that binds sockets and routes new connections.
    * `matches/`: Manages the matchmaking queue (`matchManager.py`) and individual game sessions (`match.py`).
    * `pieces/`: Defines the behavior and movement rules for each chess piece.
    * `cards/`: Implements the logic and turn-based expiration for the special ability cards.
    * `accounts/`: Handles user account data storage (`accounts.json`).
    * `processing_files/`: Manages communication threads (`processa_cliente.py` and `processa_gestor.py`).
* `jogo/cliente/`: The player client application.
* `jogo/gestor/` (Administrator): The administrator client application to query server stats.

## Connections and Architecture

The game relies heavily on TCP Sockets, sending data using a custom protocol that first sends the integer size of the payload, followed by the encoded JSON data or string. 
* **Connection Handoff:** When a player connects, a temporary thread handles their menu navigation. Once they join matchmaking, the socket is handed over to the `MatchManager` and the menu thread terminates. 
* **Pulse Checking:** Before matching two players, the `MatchManager` uses `select.select()` to ping the waiting socket. If it detects a "ghost" connection (a player who closed the game while in the queue), it drops them and waits for a valid opponent.


## Thread Functionalities

The server scales by utilizing multiple threads for different connection scopes:

* `ProcessaCliente`: Responsible for handling a client's pre-game messages (Login and Play). 
    * **Started at:** `maquina.py`, when a new connection is identified as a standard client.
    * **Lifecycle:** If a user selects `play`, this thread passes the socket to the `MatchManager` queue and gracefully exits to save server resources.
* `ProcessaGestor` (Administrator): Responsible for handling the administrator's constant ping requests for server metrics.
    * **Started at:** `maquina.py`, when the connection identifies with the `GESTOR_ID`.
    * **Lifecycle:** Stays alive in a loop, answering `online` and `games` requests until the admin disconnects.
* `Match Thread`: Responsible for handling the complete gameplay loop between two specific players.
    * **Started at:** `MatchManager`, when two active, verified sockets are in the queue. It creates a `Match` instance and starts its `start_game` method in a Daemon thread.

## Game Logic and Rules

Once matched, players are assigned White or Black and exchange names. The `Match` class generates a fresh board map for the specific session.
* **Turn Cycle:** The server sends the board state to both clients, announces whose turn it is, rolls for a minigame, and requests a command (`SELECT` a piece or use `CARDS`).
* **Rule Enforcement:** The server validates if the origin square is valid, calculates all available valid moves, and sends them to the client.
* **En Passant:** Fully tracked on the server. If a Pawn moves two squares, it is temporarily marked as the `EN_PASSANT_TARGET` for that specific turn window.
* **Win Conditions:** After every move, the server evaluates the opponent's King to check if the match status is `ACTIVE`, `CHECK`, `CHECKMATE`, or `STALEMATE`, ending the thread and closing sockets if the game concludes.

## Cards and Minigame

The card system drastically shifts normal chess mechanics.
* **The Minigame:** At the beginning of every turn, there is a 1-in-6 chance (`_minigame_chance_factor = 5`) that a reflex minigame triggers. The server sleeps for a random duration (1-10 seconds) and broadcasts a random lowercase letter. The first player to input that exact letter with the lowest latency wins a random card (BlockRow, Promotion, or Impressment).
* **Card Usage:** A player can type the `CARDS` command instead of moving a piece. Active effects (like `BlockRow`) are stored in `self.active_effects` and will be automatically reverted by the server once their turn duration expires.

## Game Messages / Client Commands

**Pre-Game (Client -> Server):**
* `login`: Prompts for a username to authenticate.
* `play`: Puts the socket into the matchmaking queue.
* `.`: Disconnects.

**In-Game (Server -> Client Protocol):**
* `MOVE` / `WAIT`: The server dictates who is allowed to send input. The waiting player's client gets locked.
* `VALID_SQUARE` / `INVALID_COMMAND`: Validation responses when selecting pieces.
* `OPP: [name]`: Broadcasts the opponent's name at the start.

**In-Game (Client -> Server Protocol):**
* `select`: Tell the server you intend to move a piece. You will provide the piece coordinates.
* `cards`: Tell the server you want to look at your inventory and deploy a card effect.

**Gestor Commands:**
* `online`: Returns the count of connected clients.
* `games`: Returns the length of `active_matches`.