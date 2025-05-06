import pygame
import sys
import os
from board import Board
from piece import Piece
from player import Player

# Định nghĩa các hằng số cho trò chơi
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
LIGHT_COLOR = (20, 139, 4)
DARK_COLOR = (255, 245, 238)
HIGHLIGHT_COLOR = (0, 255, 0, 100)

class ChessGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.pieces_images = {}
        self.board = Board()
        self.selected_square = None
        self.player_clicks = []
        self.white_player = Player("white", 300)
        self.black_player = Player("black", 300)
        self.current_player = self.white_player
        self.last_time_update = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 24)
        self.load_images()
        try:
            # Sử dụng os.path.join để tạo đường dẫn tương đối
            self.move_sound = pygame.mixer.Sound(os.path.join("sounds", "move_sound.wav"))
        except Exception as e:
            print(f"Không thể tải âm thanh di chuyển: {e}")
            self.move_sound = None
        try:
            self.game_over_sound = pygame.mixer.Sound(os.path.join("sounds", "game_over_sound.wav"))
        except Exception as e:
            print(f"Không thể tải âm thanh kết thúc: {e}")
            self.game_over_sound = None

    def load_images(self):
        pieces = [
            'black_bishop', 'black_king', 'black_knight', 'black_pawn',
            'black_queen', 'black_rook', 'white_bishop', 'white_king',
            'white_knight', 'white_pawn', 'white_queen', 'white_rook'
        ]
        for piece in pieces:
            try:
                # Sử dụng os.path.join để tạo đường dẫn tương đối
                path = os.path.join("images", f'{piece}.png')
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Image not found: {path}")
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
                self.pieces_images[piece] = image
            except Exception as e:
                print(f"Error loading {piece}: {e}")
                surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                surf.fill((255, 0, 0))  # Màu đỏ khi lỗi
                self.pieces_images[piece] = surf

    def ask_time_input(self):
        input_text = ""
        active = True
        while active:
            self.screen.fill((30, 30, 30))
            prompt = self.font.render("Nhap thoi gian moi ben (giây), sau do nhan Enter:", True, (255, 255, 255))
            self.screen.blit(prompt, (40, 200))
            text = self.font.render(input_text, True, (255, 255, 0))
            self.screen.blit(text, (40, 250))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            seconds = int(input_text)
                            self.white_player.time = seconds
                            self.black_player.time = seconds
                            active = False
                        except ValueError:
                            input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

    def update_timer(self):
        now = pygame.time.get_ticks()
        elapsed = (now - self.last_time_update) / 1000.0
        if self.current_player.update_time(elapsed):
            winner = "Black" if self.current_player.color == "white" else "White"
            self.end_game(f"{winner} wins by timeout!")
        self.last_time_update = now

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                pygame.draw.rect(self.screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.get_piece(row, col)
                if piece != "--":
                    self.screen.blit(self.pieces_images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

        if self.selected_square:
            row, col = self.selected_square
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill(HIGHLIGHT_COLOR)
            self.screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def draw_timers(self):
        white = self.font.render(f"White: {int(self.white_player.time)}s", True, (255, 255, 255))
        black = self.font.render(f"Black: {int(self.black_player.time)}s", True, (0, 0, 0))
        self.screen.blit(white, (10, HEIGHT - 30))
        self.screen.blit(black, (10, 10))

    def end_game(self, message):
        self.running = False
        self.screen.fill((0, 0, 0))
        text = self.font.render(message, True, (255, 255, 255))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        if self.game_over_sound:
            self.game_over_sound.play()
        pygame.display.flip()
        pygame.time.wait(4000)
        pygame.quit()
        sys.exit()

    def handle_click(self, row, col):
        if self.selected_square == (row, col):
            self.selected_square = None
            self.player_clicks = []
        else:
            if not self.selected_square and self.board.get_piece(row, col) != "--" and self.current_player.color in self.board.get_piece(row, col):
                self.selected_square = (row, col)
                self.player_clicks = [(row, col)]
            elif self.selected_square:
                self.player_clicks.append((row, col))

        if len(self.player_clicks) == 2:
            sr, sc = self.player_clicks[0]
            er, ec = self.player_clicks[1]
            piece = self.board.get_piece(sr, sc)
            dest = self.board.get_piece(er, ec)
            piece_obj = Piece(piece.split("_")[1], piece.split("_")[0])
            if piece_obj.is_valid_move(sr, sc, er, ec, self.board.board):
                if dest == "--" or self.current_player.color not in dest:
                    self.board.move_piece(sr, sc, er, ec)
                    if self.move_sound:
                        self.move_sound.play()
                    self.current_player = self.black_player if self.current_player == self.white_player else self.white_player
            self.selected_square = None
            self.player_clicks = []

    def run(self):
        self.ask_time_input()
        while self.running:
            self.update_timer()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    col, row = pos[0] // SQUARE_SIZE, pos[1] // SQUARE_SIZE
                    self.handle_click(row, col)
            self.draw_board()
            self.draw_pieces()
            self.draw_timers()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()