class Player:
    def __init__(self, color, time):
        self.color = color
        self.time = time

    def update_time(self, elapsed):
        self.time -= elapsed
        return self.time <= 0