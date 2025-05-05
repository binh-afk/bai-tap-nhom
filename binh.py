import pygame
import sys
import os

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
LIGHT_COLOR = (20, 139, 4)
DARK_COLOR = (255, 245, 238)
HIGHLIGHT_COLOR = (0, 255, 0, 100)

class ChessGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.pieces_images = {}
        self.board = []
        self.selected_square = None
        self.player_clicks = []
        self.current_player = "white"
        self.white_time = 300
        self.black_time = 300
        self.last_time_update = pygame.time.get_ticks()
        self.font = pygame.font.SysFont("Arial", 24)
        self.load_images()
        self.init_board()

    def load_images(self):
        pieces = [
            'black_bishop', 'black_king', 'black_knight', 'black_pawn',
            'black_queen', 'black_rook', 'white_bishop', 'white_king',
            'white_knight', 'white_pawn', 'white_queen', 'white_rook'
        ]
        for piece in pieces:
            try:
                path = f'{piece}.png'
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Image not found: {path}")
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
                self.pieces_images[piece] = image
            except Exception as e:
                print(f"Error loading {piece}: {e}")
                surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                surf.fill((255, 0, 0))
                self.pieces_images[piece] = surf

    def init_board(self):
        self.board = [
            ["black_rook", "black_knight", "black_bishop", "black_queen", "black_king", "black_bishop", "black_knight", "black_rook"],
            ["black_pawn"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["white_pawn"] * 8,
            ["white_rook", "white_knight", "white_bishop", "white_queen", "white_king", "white_bishop", "white_knight", "white_rook"]
        ]

    def ask_time_input(self):
        input_text = ""
        active = True
        while active:
            self.screen.fill((30, 30, 30))
            prompt = self.font.render("Nhap thoi gian moi ben (giây), sau đo nhan Enter:", True, (255, 255, 255))
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
                            self.white_time = seconds
                            self.black_time = seconds
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
        if self.current_player == "white":
            self.white_time -= elapsed
            if self.white_time <= 0:
                self.end_game("Black wins by timeout!")
        else:
            self.black_time -= elapsed
            if self.black_time <= 0:
                self.end_game("White wins by timeout!")
        self.last_time_update = now

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = LIGHT_COLOR if (row + col) % 2 == 0 else DARK_COLOR
                pygame.draw.rect(self.screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != "--":
                    self.screen.blit(self.pieces_images[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

        if self.selected_square:
            row, col = self.selected_square
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill(HIGHLIGHT_COLOR)
            self.screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    def draw_timers(self):
        white = self.font.render(f"White: {int(self.white_time)}s", True, (255, 255, 255))
        black = self.font.render(f"Black: {int(self.black_time)}s", True, (0, 0, 0))
        self.screen.blit(white, (10, HEIGHT - 30))
        self.screen.blit(black, (10, 10))

    def end_game(self, message):
        self.running = False
        self.screen.fill((0, 0, 0))
        text = self.font.render(message, True, (255, 255, 255))
        self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(4000)
        pygame.quit()
        sys.exit()

    def is_valid_move(self, sr, sc, er, ec, piece):
        if "pawn" in piece:
            return self.is_valid_pawn_move(sr, sc, er, ec, piece)
        elif "knight" in piece:
            return (abs(sr - er), abs(sc - ec)) in [(2, 1), (1, 2)]
        elif "bishop" in piece:
            return self.is_valid_bishop_move(sr, sc, er, ec)
        elif "rook" in piece:
            return self.is_valid_rook_move(sr, sc, er, ec)
        elif "queen" in piece:
            return self.is_valid_queen_move(sr, sc, er, ec)
        elif "king" in piece:
            return max(abs(sr - er), abs(sc - ec)) == 1
        return False

    def is_valid_pawn_move(self, sr, sc, er, ec, piece):
        direction = -1 if "white" in piece else 1
        start_row = 6 if "white" in piece else 1
        if sc == ec:
            if self.board[er][ec] == "--":
                if er - sr == direction:
                    return True
                if sr == start_row and er - sr == 2 * direction and self.board[sr + direction][sc] == "--":
                    return True
        elif abs(ec - sc) == 1 and er - sr == direction:
            target = self.board[er][ec]
            if target != "--" and ("white" in piece) != ("white" in target):
                return True
        return False

    def is_valid_bishop_move(self, sr, sc, er, ec):
        if abs(sr - er) != abs(sc - ec): return False
        step_r = 1 if er > sr else -1
        step_c = 1 if ec > sc else -1
        for i in range(1, abs(sr - er)):
            if self.board[sr + i * step_r][sc + i * step_c] != "--":
                return False
        return True

    def is_valid_rook_move(self, sr, sc, er, ec):
        if sr != er and sc != ec: return False
        if sr == er:
            step = 1 if ec > sc else -1
            for c in range(sc + step, ec, step):
                if self.board[sr][c] != "--":
                    return False
        else:
            step = 1 if er > sr else -1
            for r in range(sr + step, er, step):
                if self.board[r][sc] != "--":
                    return False
        return True

    def is_valid_queen_move(self, sr, sc, er, ec):
        return self.is_valid_bishop_move(sr, sc, er, ec) or self.is_valid_rook_move(sr, sc, er, ec)

    def handle_click(self, row, col):
        if self.selected_square == (row, col):
            self.selected_square = None
            self.player_clicks = []
        else:
            if not self.selected_square and self.board[row][col] != "--" and self.current_player in self.board[row][col]:
                self.selected_square = (row, col)
                self.player_clicks = [(row, col)]
            elif self.selected_square:
                self.player_clicks.append((row, col))

        if len(self.player_clicks) == 2:
            sr, sc = self.player_clicks[0]
            er, ec = self.player_clicks[1]
            piece = self.board[sr][sc]
            dest = self.board[er][ec]
            if self.is_valid_move(sr, sc, er, ec, piece):
                if dest == "--" or self.current_player not in dest:
                    self.board[er][ec] = piece
                    self.board[sr][sc] = "--"
                    self.current_player = "black" if self.current_player == "white" else "white"
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