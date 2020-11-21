import pygame
import os
import numpy as np
import math


__author__ = "Dominik Ficek"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Dominik Ficek"
__email__ = "dominik.ficek@email.cz"


RESOLUTION = 512, 512
PIECES_PER_PLAYER = 8
PIECE_SQUARE_RATIO = 0.35
PLAY_SQUARES = 'white'
IMG_URL = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icon.png')


class Piece:
    def __init__(self):
        self.pos = (None, None)
        self.rank = 'None'

    def __eq__(self, other):
        return True if other is not None and self.pos == other.pos else False


class Player:
    def __init__(self, num_pieces, color, selected_color,
                 king_color=pygame.Color(200, 0, 0),
                 selected_king_color=pygame.Color(255, 0, 0)):
        self.pieces = list()
        self.color = color
        self.color_selected = selected_color
        self.color_king = king_color
        self.color_king_selected = selected_king_color
        for i in range(num_pieces):
            self.pieces.append(Piece())

    def has_piece(self, pos):
        for piece in self.pieces:
            if piece.pos == pos:
                return True


class Checkers:
    def __init__(self):
        self._running = True
        self.size = \
            RESOLUTION[0] if RESOLUTION[0] < RESOLUTION[1] else RESOLUTION[1]
        self._display_surf = None
        self.font = None
        # cursor
        self.cursor_position = (0, 0)
        self.drag = False
        # grid
        self.cols, self.rows = 8, 8
        self.square_size = int(self.size / 8)
        self.board = None
        # pieces
        self.player1 = None
        self.player2 = None
        # movement
        self.turn = 'p1'
        self.selected = None
        # game logic
        self.finished = False
        self.win_msg = None

    def init(self):
        pygame.init()
        self.font = pygame.font.SysFont(None, 35)
        # display init
        self._display_surf = pygame.display.set_mode(
            (self.size, self.size), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf.fill(pygame.Color(255, 255, 255))
        pygame.display.set_caption("Checkers by FicekD")

        # icon init
        # self._icon = pygame.image.load(IMG_URL)
        # pygame.display.set_icon(self._icon)

        # grid init
        self.board = np.full(
            (self.rows, self.cols, 4), pygame.Color(0, 0, 0))
        for row in range(self.rows):
            for col in range(self.cols):
                if ((row % 2 == 0 and col % 2 == 0) or
                        (row % 2 == 1 and col % 2 == 1)):
                    self.board[col, row] = pygame.Color(255, 255, 255)

        # pieces init
        self.player1 = Player(PIECES_PER_PLAYER,
                              pygame.Color(0, 200, 0),
                              pygame.Color(0, 255, 0))
        self.player2 = Player(PIECES_PER_PLAYER,
                              pygame.Color(0, 0, 200),
                              pygame.Color(0, 0, 255))
        for i in range(PIECES_PER_PLAYER):
            if PLAY_SQUARES == 'black':
                y = math.ceil((i + 1) / 4)
                self.player1.pieces[i].pos = (2*((i % 4) + 1) if y % 2 == 1
                                              else 2*((i % 4) + 1) - 1, y)
                y = 9 - y
                self.player2.pieces[i].pos = (2*((i % 4) + 1) if y % 2 == 1
                                              else 2*((i % 4) + 1) - 1, y)
            else:
                y = math.ceil((i + 1) / 4)
                self.player1.pieces[i].pos = (2*((i % 4) + 1) if y % 2 == 0
                                              else 2*((i % 4) + 1) - 1, y)
                y = 9 - y
                self.player2.pieces[i].pos = (2*((i % 4) + 1) if y % 2 == 0
                                              else 2*((i % 4) + 1) - 1, y)
            self.player1.pieces[i].rank = 'pawn'
            self.player2.pieces[i].rank = 'pawn'
        # board state init
        self.finished = False
        self.win_msg = 'Player 1 wins!'
        self.turn = 'p1'
        self.selected = None

    def on_event(self, event):
        event_type = event.type
        # exit program
        if event_type == pygame.QUIT:
            self._running = False
        # if game is finished wait for ESC to re-init
        elif self.finished and event_type == pygame.KEYDOWN \
                and event.key == 27:
            self.init()
        # mouse down
        elif not self.finished and event_type == pygame.MOUSEBUTTONDOWN:
            # clicked square
            square = (math.ceil(event.pos[0]/self.square_size),
                      math.ceil(event.pos[1]/self.square_size))
            # selecting a piece - player 1
            if self.turn == 'p1' and self.selected is None:
                for piece in self.player1.pieces:
                    if piece.pos == square:
                        self.selected = piece
            # selecting a piece - player 2
            elif self.turn == 'p2' and self.selected is None:
                for piece in self.player2.pieces:
                    if piece.pos == square:
                        self.selected = piece
            # if already selected
            elif self.selected is not None:
                # check for reselection - player 1
                if self.turn == 'p1':
                    for piece in self.player1.pieces:
                        if piece.pos == square:
                            self.selected = piece
                            return
                    else:
                        if self.player2.has_piece(square):
                            return
                # check for reselection - player 2
                elif self.turn == 'p2':
                    for piece in self.player2.pieces:
                        if piece.pos == square:
                            self.selected = piece
                            return
                    else:
                        if self.player1.has_piece(square):
                            return
                # not reselecting -> trying to move selected piece
                # calculate distance from selected to desired
                dist = distance(self.selected.pos, square)
                # lower than one means not diagonal, check diagonality
                if dist < 1 or not is_diag(square, self.selected.pos):
                    return
                # if selected is pawn
                if self.selected.rank == 'pawn':
                    if self.turn == 'p1' and self.selected.pos[1] > square[1]:
                        return
                    if self.turn == 'p2' and self.selected.pos[1] < square[1]:
                        return
                    # distance of one square diagonaly
                    if dist > math.sqrt(2):
                        # distance just over one square
                        if dist > 2*math.sqrt(2):
                            return
                        # get position of middle square
                        middle = (int(self.selected.pos[0]/2 + square[0]/2),
                                  int(self.selected.pos[1]/2 + square[1]/2))
                        # check if middle square is occupied by enemy piece
                        if self.turn == 'p1':
                            if self.selected.pos[1] > square[1]:
                                return
                            for piece in self.player2.pieces:
                                if piece.pos == middle:
                                    self.player2.pieces.remove(piece)
                                    break
                            else:
                                return
                        else:
                            for piece in self.player1.pieces:
                                if piece.pos == middle:
                                    self.player1.pieces.remove(piece)
                                    break
                            else:
                                return
                # if selected is king
                if self.selected.rank == 'king':
                    # construct list of squares between selected squares
                    middle = list()
                    # physically upper and lower squares
                    # (higher/lower y values)
                    upper, lower = (self.selected.pos, square) \
                        if self.selected.pos[1] > square[1] \
                        else (square, self.selected.pos)
                    # check if movement is from left to right or otherwise
                    rate = 1 if upper[0] > lower[0] else -1
                    # iteratively substract from upper square
                    # till get lower square
                    pos = (upper[0] - rate, upper[1] - 1)
                    while pos != lower:
                        middle.append(pos)
                        pos = (pos[0] - rate, pos[1] - 1)
                    # check if there's one or more pieces in path
                    found = None
                    if self.turn == 'p1':
                        for piece in self.player2.pieces:
                            if piece.pos in middle:
                                # found second piece in path ->
                                # terminate movement
                                if found is not None:
                                    return
                                # found first piece
                                else:
                                    found = piece
                        # if one piece is found remove it
                        if found is not None:
                            self.player2.pieces.remove(found)
                    # same for player 2
                    else:
                        for piece in self.player1.pieces:
                            if piece.pos in middle:
                                if found is not None:
                                    return
                                else:
                                    found = piece
                        if found is not None:
                            self.player1.pieces.remove(found)
                # update position
                self.selected.pos = square
                # check for promotion
                if self.turn == 'p1' and self.selected.rank == 'pawn' and \
                        self.selected.pos[1] == 8:
                    self.selected.rank = 'king'
                elif self.turn == 'p2' and self.selected.rank == 'pawn' and \
                        self.selected.pos[1] == 1:
                    self.selected.rank = 'king'
                # unselect
                self.selected = None
                # swap turn
                self.turn = 'p2' if self.turn == 'p1' else 'p1'

    def render(self):
        # if game is finished dont render board and pieces
        if self.finished:
            pygame.display.update()
            return
        # render board
        for row in range(self.rows):
            for col in range(self.cols):
                pygame.draw.rect(self._display_surf, self.board[col, row],
                                 (self.square_size*col, self.square_size*row,
                                 self.square_size*col+self.square_size,
                                 self.square_size*row+self.square_size))
        # render pieces
        for piece in self.player1.pieces:
            # render all pieces
            color = self.player1.color_selected if piece == \
                self.selected else self.player1.color
            pygame.draw.circle(self._display_surf, color,
                               (int((piece.pos[0]-0.5) *
                                    self.square_size),
                                int((piece.pos[1]-0.5) *
                                    self.square_size)),
                               int(PIECE_SQUARE_RATIO * self.square_size))
            # if piece is king render its middle circle identifier
            if piece.rank == 'king':
                color = self.player1.color_king_selected \
                    if piece == self.selected \
                    else self.player1.color_king
                pygame.draw.circle(self._display_surf, color,
                                   (int((piece.pos[0]-0.5) *
                                        self.square_size),
                                    int((piece.pos[1]-0.5) *
                                        self.square_size)),
                                   int(PIECE_SQUARE_RATIO * self.square_size
                                       * 0.5))
        # render player 2's pieces (same as player 1)
        for piece in self.player2.pieces:
            color = self.player2.color_selected if piece == \
                self.selected else self.player2.color
            pygame.draw.circle(self._display_surf, color,
                               (int((piece.pos[0]-0.5) *
                                    self.square_size),
                                int((piece.pos[1]-0.5) *
                                    self.square_size)),
                               int(PIECE_SQUARE_RATIO * self.square_size))
            if piece.rank == 'king':
                color = self.player2.color_king_selected \
                    if piece == self.selected \
                    else self.player2.color_king
                pygame.draw.circle(self._display_surf, color,
                                   (int((piece.pos[0]-0.5) *
                                        self.square_size),
                                    int((piece.pos[1]-0.5) *
                                        self.square_size)),
                                   int(PIECE_SQUARE_RATIO * self.square_size
                                       * 0.5))
        pygame.display.update()

    def check_win(self):
        # check if someone is out of pieces if so claim game as finished
        if len(self.player1.pieces) == 0:
            self.finished = True
            self.win_msg = 'Player 2 wins!'
        elif len(self.player2.pieces) == 0:
            self.finished = True
            self.win_msg = 'Player 1 wins!'
        # if game is finished render ending screen
        if self.finished:
            center = int(self.size/2)
            pygame.draw.rect(self._display_surf, pygame.Color(255, 0, 0),
                             pygame.Rect(center-220, center-110, 440, 220))
            pygame.draw.rect(self._display_surf, pygame.Color(255, 255, 255),
                             pygame.Rect(center-215, center-105, 430, 210))
            text = self.font.render(self.win_msg, True, pygame.Color(0, 0, 0))
            text_rect = text.get_rect(center=((center, center - 20)))
            self._display_surf.blit(text, text_rect)
            text = self.font.render('Press ESC key to start new game',
                                    True, pygame.Color(0, 0, 0))
            text_rect = text.get_rect(center=((center, center + 20)))
            self._display_surf.blit(text, text_rect)

    def cleanup(self):
        pygame.quit()

    def execute(self):
        self.init()
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
            self.render()
            self.check_win()
        self.cleanup()


def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def valid(pos, board):
    if np.array_equal(board[pos[1]-1, pos[0]-1], np.array([0, 0, 0, 255])):
        return True if PLAY_SQUARES == 'black' else False


def is_diag(p1, p2):
    return True if (p1[0] - p2[0])**2 == (p1[1] - p2[1])**2 else False


def main():
    app = Checkers()
    app.execute()


if __name__ == '__main__':
    main()
