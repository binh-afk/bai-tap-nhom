class Board:
    def __init__(self):
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

    def move_piece(self, sr, sc, er, ec):
        self.board[er][ec] = self.board[sr][sc]
        self.board[sr][sc] = "--"

    def get_piece(self, row, col):
        return self.board[row][col]