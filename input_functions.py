import tcod
import tcod.event
import time

from enums.game_states import GameStates

from yaml_functions import read_yaml

LOG = False

MOVE_KEYS = {  # key_symbol: (x, y)
    # Arrow keys.
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    #tcod.event.K_PERIOD: (0, 0),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    #tcod.event.K_KP_5: (0, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    #tcod.event.K_CLEAR: (0, 0),  # Numpad `clear` key.
    # Vi Keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}

PLAYER_INPUT = {
    'q':'toggle_light',
    ',':'pickup',
    '.':'rest',
    'i':'show_inventory',
    'd':'drop_inventory',
    'p':'show_character_screen',
    #'1':'toggle_wall',
    #'2':'create_luminary'
}

INVENTORY_INPUT = 'INVENTORY'

class Mouse(tcod.event.EventDispatch[None]):
    def __init__(self):
        self.result = {}
        self.x = 0
        self.y = 0
        self.click = None
        self.get_out = False

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> None:
        x,y = (event.tile.x, event.tile.y)
        if event.button == 1:
            self.click = "L"
        elif event.button == 3:
            self.click = "R"

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        self.x = event.tile.x
        self.y = event.tile.y

class Keyboard(tcod.event.EventDispatch[None]):
    def __init__(self):
        self.result = {}
        self.game_state = None
        self.key_up = True

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        #print(self.game_state)
        if event.sym == tcod.event.K_ESCAPE:
            self.result = {'exit': True}
            self.get_out = True

        elif event.sym == tcod.event.K_F5:
            self.result = {'fullscreen': True}
            self.get_out = True

        elif event.sym in MOVE_KEYS and self.game_state == 'PLAYER_TURN':
            self.cmd_move(*MOVE_KEYS[event.sym])

        elif self.game_state == 'INVENTORY':
            if not event.repeat:
                index = event.sym - ord('a')
                if index >= 0:
                    self.result = {'inventory_index': index}
                    self.get_out = True

        elif event.sym <= 255 and event.sym >= 0 and self.key_list:
            if chr(event.sym) in self.key_list:
                if self.key_up:
                    self.result = {self.key_list.get(chr(event.sym)): True}
                    self.key_up = False
                    self.get_out = True

    def ev_keyup(self, event: tcod.event.KeyUp) -> None:
        self.key_up = True

    def cmd_move(self, x: int, y: int) -> None:
        self.result = {'move': (x, y)}
        self.get_out = True

    def ev_quit(self, event: tcod.event.Quit) -> None:
        """The window close button was clicked or Alt+F$ was pressed."""
        self.result = {'quit': True}
        self.get_out = True

def toggle_fullscreen(context: tcod.context.Context) -> None:
    """Toggle a context window between fullscreen and windowed modes."""
    if not context.sdl_window_p:
        return
    fullscreen = tcod.lib.SDL_GetWindowFlags(context.sdl_window_p) & (
        tcod.lib.SDL_WINDOW_FULLSCREEN | tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP
    )
    tcod.lib.SDL_SetWindowFullscreen(
        context.sdl_window_p,
        0 if fullscreen else tcod.lib.SDL_WINDOW_FULLSCREEN_DESKTOP,
    )

def handle_input_per_state(state, mouse, context, game_state, key_list=None):
    if game_state == GameStates.PLAYERS_TURN:
        return handle_input(state, mouse, context, 'PLAYER_TURN', PLAYER_INPUT)
    elif game_state == GameStates.PLAYER_DEAD or game_state == GameStates.GOOD_ENDING:
        return handle_input(state, mouse, context, 'INVENTORY')
    elif game_state == GameStates.TARGETING:
        return handle_input(state, mouse, context, 'TARGETING')
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_input(state, mouse, context, 'INVENTORY')
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_input(state, mouse, context, 'CHAR_INFO')

    return {}

def handle_input(state, mouse, context, game_state, key_list=None):
    mouse.click = None
    state.get_out = False
    state.game_state = game_state
    state.key_list = key_list

    for event in tcod.event.wait():
        context.convert_event(event)

        state.dispatch(event)
        mouse.dispatch(event)

        if state.get_out:
            return state.result
    return {}


"""
#  # Set tile coordinates for an event.

if event.type == "WINDOWRESIZED":
    console = tcod.Console(*context.recommended_console_size())
if event.type == "TEXTINPUT":
    return event.text
"""