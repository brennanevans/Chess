import pygame

pygame.init()
clock = pygame.time.Clock()

class Pieces():
    def __init__(self,row:int,col:int,colour:str):
        self.row = row
        self.col = col
        self.colour = colour
        
        _cols = ["A","B","C","D","E","F","G","H"]
        self.notation = _cols[col] + str(row+1)

        # Reset self.moves to [] for every piece on one team when they make their move
        # Moves that their pieces can make only change then and can be recalculated on their turn
        # This reduces need for recalculation each time a piece is pressed
        self.moves = []
    
    def __repr__(self):
        return str(type(self).__name__) + ":" + self.notation
    
    def _addIfLegal(self,row,col,capturesOnly=False):
        if row<0 or row>7 or col<0 or col>7:
            return False
        if board.grid[row][col] != None:
            if board.grid[row][col].colour != self.colour:
                self.moves.append((row,col))
            return False
        else:
            if capturesOnly:
                return False
            self.moves.append((row,col))
            return True
    
    def _getHorizontalMoves(self,maxMovement=7):
        # -1 and +1s on self.col/self.row are so pieces doesn't see themselves
        #  as an untakeable piece and break out of the loop
        minHorizontal = max(-1,self.col-maxMovement)
        for column in range(self.col-1,minHorizontal-1,-1):
            if not self._addIfLegal(self.row,column):
                break
        
        maxHorizontal = min(8,self.col+maxMovement)
        for column in range(self.col+1,maxHorizontal+1):
            if not self._addIfLegal(self.row,column):
                break
    
    def _getVerticalMoves(self,maxMovement=7):
        minVertical = max(-1,self.row-maxMovement)
        for row in range(self.row-1,minVertical-1,-1):
            if not self._addIfLegal(row,self.col):
                break

        maxVertical = min(8,self.row+maxMovement)
        for row in range(self.row+1,maxVertical+1):
            if not self._addIfLegal(row,self.col):
                break

    def _getDiagonalMoves(self,maxMovement=7,capturesOnly=False):
        # maxMovement=7 for bishop,queen,rook, 2 for pawn first move, 
        # 1 for King and pawn taking/2nd move+
        minHorizontal = max(-1,self.col-maxMovement)
        maxHorizontal = min(8,self.col+maxMovement)
        minVertical = max(-1,self.row-maxMovement)
        maxVertical = min(8,self.row+maxMovement)
        
        # "Down Left" means row value and column value both decreasing,
        #  however, depending on the colour of the piece, this may actually
        #  be calculating Up Right on the board.

        row = self.row-1
        column = self.col-1
        while row>=minVertical and column>=minHorizontal: # "Down Left"
            if not self._addIfLegal(row,column,capturesOnly):
                break
            row -=1
            column-=1

        row = self.row-1
        column = self.col+1
        while row>=minVertical and column<=maxHorizontal: # "Down Right"
            if not self._addIfLegal(row,column,capturesOnly):
                break
            row -=1
            column+=1

        row = self.row+1
        column = self.col-1
        while row<=maxVertical and column>=minHorizontal:# "Up Left"
            if not self._addIfLegal(row,column,capturesOnly):
                break
            row+=1
            column-=1

        row = self.row+1
        column = self.col+1
        while row<=maxVertical  and column<=maxHorizontal:# "Up Right"
            if not self._addIfLegal(row,column,capturesOnly):
                break
            row+=1
            column+=1

class King(Pieces):
    def __init__(self,row:int,col:int,colour:str):
        super().__init__(row, col, colour)
        self.inCheck = False

    def getMoves(self):
        if self.moves == []:
            self._getHorizontalMoves(1)
            self._getVerticalMoves(1)
            self._getDiagonalMoves(1)

        return self.moves

class Queen(Pieces):
    def __init__(self,row:int,col:int,colour:str):
        super().__init__(row, col, colour)
    
    def getMoves(self):
        if self.moves == []:
            self._getHorizontalMoves()
            self._getVerticalMoves()
            self._getDiagonalMoves()

        return self.moves

class Rook(Pieces):
    def __init__(self,row:int,col:int,colour:str):
        super().__init__(row, col, colour)

    def getMoves(self):
        if self.moves == []:
            self._getHorizontalMoves()
            self._getVerticalMoves()

        return self.moves
        

class Bishop(Pieces):
    def __init__(self,row:int,col:int,colour:str):
        super().__init__(row, col, colour)
    
    def getMoves(self):
        if self.moves == []:
            self._getDiagonalMoves()
        
        return self.moves

class Knight(Pieces):
    def __init__(self,row:int,col:int,colour:str):
        super().__init__(row, col, colour)

class Pawn(Pieces):
    def __init__(self,row:int,col:int,colour:str):
        super().__init__(row, col, colour)
        self.firstMove = True

    def getMoves(self):
        if self.moves == []:
            if self.firstMove:
                self._getVerticalMoves(2)
            else:
                self._getVerticalMoves(1)
            self._getDiagonalMoves(1,True)

        return self.moves

class GameBoard():
    def __init__(self):
        self.grid = [[None]*8]*8

        for rowIndex in range(len(self.grid)):
            colour = "Black" if rowIndex > 1 else "White"
            if rowIndex in [0,7]:
                self.grid[rowIndex] = [Rook(rowIndex,0,colour)
                                       ,Knight(rowIndex,1,colour)
                                       ,Bishop(rowIndex,2,colour)
                                       ,Queen(rowIndex,3,colour)
                                       ,King(rowIndex,4,colour)
                                       ,Bishop(rowIndex,5,colour)
                                       ,Knight(rowIndex,6,colour)
                                       ,Rook(rowIndex,7,colour)]
                
            elif rowIndex in [1,6]:
                self.grid[rowIndex] = []
                for i in range(8):
                    self.grid[rowIndex].append(Pawn(rowIndex,i,colour))

    def __repr__(self):
        # Note, the return string is not fully aligned. This is intended as the
        # string representation of the board is for debugging purposes only.
        # To view the board properly the GUI should be used.
        stringRepresentation = ""
        for row in self.grid:
            stringRepresentation += str(row) + "\n"
        
        return stringRepresentation

board = GameBoard()
print(board)
print(board.grid[1][3].getMoves())






def main(screenWidth=500,screenHeight=500):
    #screen must be a square for chess 
    #temp
    gameScreen = pygame.display.set_mode((screenWidth,screenHeight))

    running = True
    while running:
        x,y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame.display.update()
        clock.tick(20)

    pygame.quit()

if __name__ == "__main__":
    main()

# En Passant, knight moves and castling currently unconsidered



# Make all games seperate repositories 
# Game launcher isn't very difficult (just calls main on each file with possible inputs), dont need as a project


# Also want to try to make opponent - either learn how to make a chess ai (preferred as more impressive) 
# or connect to stockfish in some way
# Or both??

#Make AI in a seperate file in same repository