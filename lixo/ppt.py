class Game:
    def __init__(self, id):
        self.p1Went = False
        self.p2went = False
        self.ready = False
        self.id = id
        self.move = [None, None]
        self.wins = [0,0]
        self.ties = 0

    def get_player_move(self, p):
        """retorns a move of a player

        Args:
            p (int): [0, 1]

        Returns:
            move
        """
        return self.move[p]
    
    def play(self, player, move):
        self.move[player] = move
        
        if player == 0:
            self.p1Went = True
        else:
            self.p2went = True
    
    def connected(self):
        return self.ready
    
    def bothWent(self):
        return self.p1Went and self.p2went
    
    def winner(self):
        p1 = self.move[0].upper()[0]
        p2 = self.move[1].upper()[0]
        
        winner = -1
        # R P S
        if p1 == "R" and p2 == "P":
            winner = 1
        elif p1 == "R" and p2 == "S":
            winner = 0
        elif p1 == "P" and p2 == "R":
            winner = 0
        elif p1 == "P" and p2 == "S":
            winner = 1
        elif p1 == "S" and p2 == "R":
            winner = 1
        elif p1 == "S" and p2 == "P":
            winner = 0
        
        return winner
    
    def reset(self):
        self.p1Went = False
        self.p2went = False
        
        