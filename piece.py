class Piece:
    def __init__(self, type, color):
        self.type = type
        self.color = color

    def is_valid_move(self, sr, sc, er, ec, board):
        if self.type == "pawn":
            return self._is_valid_pawn_move(sr, sc, er, ec, board)
        elif self.type == "knight":
            return (abs(sr - er), abs(sc - ec)) in [(2, 1), (1, 2)]
        elif self.type == "bishop":
            return self._is_valid_bishop_move(sr, sc, er, ec, board)
        elif self.type == "rook":
            return self._is_valid_rook_move(sr, sc, er, ec, board)
        elif self.type == "queen":
            return self._is_valid_queen_move(sr, sc, er, ec, board)
        elif self.type == "king":
            return max(abs(sr - er), abs(sc - ec)) == 1
        return False

    def _is_valid_pawn_move(self, sr, sc, er, ec, board):
        direction = -1 if self.color == "white" else 1
        start_row = 6 if self.color == "white" else 1
        if sc == ec and board[er][ec] == "--":
            if er - sr == direction:
                return True
            if sr == start_row and er - sr == 2 * direction and board[sr + direction][sc] == "--":
                return True
        elif abs(ec - sc) == 1 and er - sr == direction:
            target = board[er][ec]
            if target != "--" and (self.color == "white") != ("white" in target):
                return True
        return False

    def _is_valid_bishop_move(self, sr, sc, er, ec, board):
        if abs(sr - er) != abs(sc - ec):
            return False
        step_r = 1 if er > sr else -1
        step_c = 1 if ec > sc else -1
        for i in range(1, abs(sr - er)):
            if board[sr + i * step_r][sc + i * step_c] != "--":
                return False
        return True

    def _is_valid_rook_move(self, sr, sc, er, ec, board):
        if sr != er and sc != ec:
            return False
        if sr == er:
            step = 1 if ec > sc else -1
            for c in range(sc + step, ec, step):
                if board[sr][c] != "--":
                    return False
        else:
            step = 1 if er > sr else -1
            for r in range(sr + step, er, step):
                if board[r][sc] != "--":
                    return False
        return True

    def _is_valid_queen_move(self, sr, sc, er, ec, board):
        return self._is_valid_bishop_move(sr, sc, er, ec, board) or self._is_valid_rook_move(sr, sc, er, ec, board)