REPOS LINK https://github.com/LPn2024111863/Laws-of-Chess-Entrega-3

# Laws of Chess

Laws of Chess is a multiplayer, client-server chess game implemented in Python. This game bring special cards to the game to make it more thoughtfull and inovative.
The application features a robust server that handles matchmaking, game logic, and concurrent matches, along with separate clients for players and server administrators.


## Members of the group
* Gonçalo Arruda - 2024109624
* Hernâni Araújo - 2024111863

## Features

*   **Client-Server Architecture**: A dedicated server manages game state, connections, and matchmaking, allowing multiple games to run concurrently.
*   **Multiplayer Matchmaking**: Players can join a queue and be automatically matched with an opponent to start a game.
*   **Innovative Card System**: Adds a unique twist to classic chess with special abilities.
    *   **BlockRow**: Temporarily makes an entire row on the board impassable.
    *   **Impressment**: Provides a chance to steal an opponent's piece and convert it to your side.
    *   **Promotion**: Instantly upgrade one of your pieces (e.g., Pawn to Bishop/Knight, Rook to Queen).
*   **Card Acquisition Minigame**: During a match, players can compete in a quick minigame to acquire the cards.
*   **Administrator Client**: A separate terminal client for administrators to monitor the server's status, including the number of online players and active games.
*   **Complete Chess Logic**: Implements all standard chess rules, including piece movements, check, checkmate, and stalemate detection.
*   **Account System**: Players can log into accounts and the system tracks wins. **This is still under work**


## Project Structure

The repository is organized into three main components:

*   `jogo/servidor/`: Contains all the server-side logic.
    *   `maquina/`: The main server entry point that listens for and handles new connections.
    *   `matches/`: Manages the matchmaking queue (`MatchManager`) and individual game sessions (`Match`).
    *   `pieces/`: Defines the behavior and movement rules for each chess piece.
    *   `cards/`: Implements the logic for the special ability cards.
    *   `accounts/`: Handles user account creation and data storage.
    *   `processing_files/`: Manages communication threads for clients and administrators.
*   `jogo/cliente/`: The player client application.
    *   `interface/`: The command-line interface for players to interact with the game. Also includes a partial implementation of Pygame Interface.
*   `jogo/administrator/`: The administrator client application.
    *   `interface/`: The command-line interface for administrators to query server stats.


## Thread Functionalities

The program is made with three main threads that can be created:

* `ProcessaCliente`: This thread is responsible to handle the client's messages and each thread holds one client, making available the possibility to have many at the same time.
    *   Started at: `maquina`, where the server checks for the client's ID and starts this thread if it corresponds to a client.
      
* `ProcessaAdministrador`: This thread is responsible to handle the administrator's messages and each thread holds one administrator, making available the possibility to have many  at the same time.
   *   Started at: `maquina`, where the server checks for the administrator's ID and starts this thread if ID corresponds to a administrator.   

*  `Start_game`: This thread is responsible to handle the game between two players.  
   *   Started at: `matchManager`, being accessed by `ProcessaCliente`. When a client selects `play`, it is redirected into the matchmaking queue. If it is possible to start a game (there are two players in the queue), the thread starts and the game can begin. If not, the client is prompted to wait and no input can be made until someone joins the queue and the game starts. 

## Pygame Functionalities

To make the game have an interface, the Pygame library had to be implemented, which was implemented in the `jogo/cliente/interface`.

* `Game State`: Some important aspects about the game such as messages, avaiable move visualization and the state of the game (if the player is in the menu, waiting or playing)

* `Drawing Functions`: These functions act as a building tool to make the visual elements on the screen. 
    * `_draw_board` draws the 8 by 8 squared chess board; 
    * `_draw_panel` draws the rectangles that notifies the players about the turns, log messages and cards (to be implemented)
    * `_draw_minigame` draws the minigame information on the screen, in front of the board, displaying how much time has elapsed and the letter to press.
    * `_draw_input` draws the input part of the minigame.
    * `_draw_menu` draws the main menu when a player joins, permiting choosing between joining the matchmaking queue, logging in or quitting the game.
    * `_draw_input_overlay` draws the input for the login name while using the menu.
    * `_draw_waiting` draws the waiting screen while a game is not avaiable to begin.
    * `_draw_game` calls the functions related to drawing each element of the board.

* `Game Handlers`: These functions allow for a better management of the event done while on the menu or the game.
    * `_handle_menu` checks for the player's action and starts the `_play_thread` if the requirements are met.
    * `_handle_game` checks for the events while in a game, such as touching the board, the minigame, cards (to be implemented)

* `Auxiliary Functions`: Other functions that act as helpers for communication or don't fall in the previous categories.
    * `_quit` is called to terminate the connection and exit the pygame.
    * `_do_login` is called to check the result of the login (success or error)
    * `_do_choices` is called to allow communication about the player's moves in a game, either being pieces or cards.
    * `_play_thread` is called to allow communication with the server about the game board and other aspects such as minigames. 

* `execute`: Function that calls the game handlers and also the main drawing functions so the game can run smoothly. It checks for the game's status and acts accordingly to it.

## How to Play

### Player Client Commands

Once the client is running, you can use the following commands:

*   `login`: Prompts for a username to log into an account stored in `accounts.json`.
*   `play`: Enters the matchmaking queue. The server will pair you with the next available player.
*   `.`: Disconnects the client from the server.

**In-Game Commands:**

*   `select`: During your turn, use this command to choose a piece to move. You will be prompted to enter the piece's square (e.g., `e2`) and then the destination square (e.g., `e4`).
*   `cards`: During your turn, use this command to view your available cards and choose one to play.

### Administrator Client Commands

The administrator client provides a simple interface for monitoring the server:

*   `online`: Displays the current number of players connected to the server.
*   `games`: Displays the number of matches currently in progress.
*   `.`: Disconnects the administrator client.


## Next Features and Validations to be implemented

The next steps of this project include:
*   Validation: A revaluation of the code to check for more errors or missing areas that might trigger inconsistencies.
*   Chess Moves: Castling and En Passant will be implemented in the future.
*   Progress Tracking: The accounts will be implemented in more detail so the players can check the wins, losses and win/lose ratio.
*   Cards: New cards will be implemented with new abilities to use during the game!
*   Timer: A timer will be implemented to limit the time the player has to play in a round.
*   Game Modes: Laws of Chess contains currently only the full board of pieces. Further down the project will include situations like mid game or end game so player can enjoy different scenarios.
*   Pygame: Finish Pygame implementation / Seperate this implementation from the main functions in `jogo/cliente/interface` (if possible in the current time avaiable)
*   Administrator: Administrators will have more functionalities regarding the game's status and modifying it. (This will be optional according to time constraints)
