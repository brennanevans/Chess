import pygame

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

class Pieces():
    blackPieces = []
    blackKing = None
    whitePieces = []
    whiteKing = None

    def __init__(self,square,colour:str):
        self.row = square.row
        self.col = square.col
        self.square = square

        self.colour = colour
        
        self._updateNotation()

        # Reset self.moves to [] for every piece on one team when they make their move
        # Moves that their pieces can make only change then and can be recalculated on their turn
        # This reduces need for recalculation each time a piece is pressed
        self.moves = []

        imagePath = "Assets/" + self.colour + "Pieces/" + str(type(self).__name__) + self.colour + ".png"
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.smoothscale(self.image,(50,50))


        if self.colour == "White":
            Pieces.whitePieces.append(self)
            if isinstance(self, King):
                Pieces.whiteKing = self
        else:
            Pieces.blackPieces.append(self)
            if isinstance(self, King):
                Pieces.blackKing = self
    
    def __repr__(self):
        return str(type(self).__name__) + ":" + self.notation
    
    def _updateNotation(self):
        _cols = ["A","B","C","D","E","F","G","H"]
        self.notation = _cols[self.col] + str(self.row+1)
    
    def _addIfLegal(self,row,col,capturesOnly=False,capturesForbidden=False):
        if row<0 or row>7 or col<0 or col>7:
            return False
        
        destination = board.squareGrid[row][col]
        destinationPiece = destination.piece
        
        if self.colour == "Black":
            currentKing = Pieces.blackKing
        else:
            currentKing = Pieces.whiteKing

        # # Test if moving piece will create/not alleviate check
        # self.square.piece = None
        # destination.piece = self
        # if currentKing._calculateInCheck():
        #     self.square.piece = self
        #     destination.piece = destinationPiece
        #     return False
        # self.square.piece = self
        # destination.piece = destinationPiece

        if destinationPiece != None:
            if destinationPiece.colour != self.colour:
                if not capturesForbidden:
                    self.moves.append(destination)
            return False
        else:
            if capturesOnly:
                return False
            self.moves.append(destination)
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

    def _getDiagonalMoves(self,maxMovement=7):
        # maxMovement=7 for bishop,queen,rook and 1 for King
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
            if not self._addIfLegal(row,column):
                break
            row -=1
            column-=1

        row = self.row-1
        column = self.col+1
        while row>=minVertical and column<=maxHorizontal: # "Down Right"
            if not self._addIfLegal(row,column):
                break
            row -=1
            column+=1

        row = self.row+1
        column = self.col-1
        while row<=maxVertical and column>=minHorizontal:# "Up Left"
            if not self._addIfLegal(row,column):
                break
            row+=1
            column-=1

        row = self.row+1
        column = self.col+1
        while row<=maxVertical  and column<=maxHorizontal:# "Up Right"
            if not self._addIfLegal(row,column):
                break
            row+=1
            column+=1

    def move(self,square):
        global board
        board.currentPiece = None

        if square in self.moves:
            if isinstance(self,Pawn):
                self.firstMove = False
                if abs(self.row-square.row) == 2:
                    self.justMovedTwo = True
                else:
                    self.justMovedTwo = False
            
            board.squareGrid[self.row][self.col].piece = None
            board._update()

            square.piece = self
            self.row = square.row
            self.col = square.col
            board._update()

            self._updateNotation()
            

            for row in board.squareGrid:
                for square in row:
                    if square.piece != None:
                        square.piece.moves = []

            return True
        else:
            return False

    def remove(self):
        if self.colour == "White":
            Pieces.whitePieces.remove(self)
        else:
            Pieces.blackPieces.remove(self)

class King(Pieces):
    def __init__(self,square,colour:str):
        super().__init__(square, colour)
        self.inCheck = False

    def getMoves(self):
        if self.moves == []:
            self._getHorizontalMoves(1)
            self._getVerticalMoves(1)
            self._getDiagonalMoves(1)

        return self.moves
    
    def _calculateInCheck(self):
        if self.colour == "White":
            opponentPieces = Pieces.blackPieces
        else:
            opponentPieces = Pieces.whitePieces

        for piece in opponentPieces:
            if self.square in piece.getMoves(False):
                self.inCheck = True
                return True
            
        self.inCheck = False
        return False

class Queen(Pieces):
    def __init__(self,square,colour:str):
        super().__init__(square, colour)
    
    def getMoves(self):
        if self.moves == []:
            self._getHorizontalMoves()
            self._getVerticalMoves()
            self._getDiagonalMoves()

        return self.moves

class Rook(Pieces):
    def __init__(self,square,colour:str):
        super().__init__(square, colour)

    def getMoves(self):
        if self.moves == []:
            self._getHorizontalMoves()
            self._getVerticalMoves()

        return self.moves
        

class Bishop(Pieces):
    def __init__(self,square,colour:str):
        super().__init__(square, colour)
    
    def getMoves(self):
        if self.moves == []:
            self._getDiagonalMoves()
        
        return self.moves

class Knight(Pieces):
    def __init__(self,square,colour:str):
        super().__init__(square, colour)

    def getMoves(self):
        if self.moves == []:
            possibleOffsets = [(1,-2),(1,2),(-1,-2),(-1,2),(2,-1),(2,1),(-2,-1),(-2,1)]

            for offsets in possibleOffsets:
                self._addIfLegal(self.row+offsets[0],self.col+offsets[1])

        return self.moves

class Pawn(Pieces):
    def __init__(self,square,colour:str):
        super().__init__(square, colour)
        self.firstMove = True
        self.justMovedTwo = False

    def getMoves(self):
        if self.moves == []:
            # Decided to bypass vertical and horizonal move functions for pawns as they move so differently to other pieces

            # Black pawns move down board so row indexes decrease rather than increase
            if self.colour == "Black":
                scale = -1
            else:
                scale = 1

            #Vertical moves - can only possibly move two if can move one
            if self._addIfLegal(self.row+1*scale,self.col,capturesForbidden=True):
                if self.firstMove:
                    self._addIfLegal(self.row+2*scale,self.col,capturesForbidden=True)

            # Taking moves
            self._addIfLegal(self.row+1*scale,self.col+1,capturesOnly=True)
            self._addIfLegal(self.row+1*scale,self.col-1,capturesOnly=True)

            # En passant
            adjacentPieces = []
            if self.col != 0:
                adjacentPieces.append(board.squareGrid[self.row][self.col-1].piece)
            if self.col != 7:
                adjacentPieces.append(board.squareGrid[self.row][self.col+1].piece)

            for piece in adjacentPieces:
                if isinstance(piece,Pawn):
                    if piece.justMovedTwo and piece.colour!=self.colour:
                        print(piece.row,piece.col)
                        self.moves.append(board.squareGrid[piece.row+1*scale][piece.col])

        return self.moves
    
class Square():
    def __init__(self,surface:pygame.Surface,row,column,colour):
        self.surface = surface
        self.colour = colour
        self.scaledRect = pygame.Rect(0,0,0,0)

        self.row = row
        self.col = column

        _cols = ["A","B","C","D","E","F","G","H"]
        self.notation = _cols[self.col] + str(self.row+1)

        self.piece = None
        self._hasCircle = False
    
    def __repr__(self):
        return "The square with row index " + str(self.row) + " and column index " + str(self.col)
        

class GameBoard():
    def __init__(self):
        self.currentPiece = None
        self._createBoard()

    # def __repr__(self):
    #     # Note, the return string is not fully aligned. This is intended as the
    #     # string representation of the board is for debugging purposes only.
    #     # To view the board properly the GUI should be used.
    #     stringRepresentation = ""
    #     for row in self.squareGrid:
    #         stringRepresentation += str(row) + "\n"
        
    #     return stringRepresentation
    
    def _createBoard(self):
        self.surface = pygame.Surface((400,400))
        self.squareGrid = []

        currentColour ="#D7BA89"
        for row in range(8):
            squaresRow = []
            for column in range(8):
                square = Square(self.surface.subsurface(column*50,row*50,50,50),row,column,currentColour)
                square.surface.fill(currentColour)

                scale = gameScreen.get_width()/self.surface.get_width()
                size = 50*scale
                square.scaledRect = pygame.Rect(column*size,row*size,size,size)


                squaresRow.append(square)

                currentColour = "#D7BA89" if currentColour == "#56342A" else "#56342A"
            currentColour = "#D7BA89" if currentColour == "#56342A" else "#56342A"

            self.squareGrid.append(squaresRow)

        self._addPieces()
        self._update()

    def _addPieces(self):
        grid = self.squareGrid
        rows = [grid[0],grid[1],grid[6],grid[7]]
        pieceRow = [Rook,Knight,Bishop,King,Queen,Bishop,Knight,Rook]

        for row in rows:
            for square in row:
                colour = "Black" if square.row > 1 else "White"
                if square.row in [0,7]:
                    square.piece = pieceRow[square.col](square,colour)
                else:
                    square.piece = Pawn(square,colour)
    
    def _update(self):
        for row in self.squareGrid:
            for square in row:
                square.surface.fill(square.colour)

                if square.piece != None:
                    square.surface.blit(square.piece.image,square.surface.get_rect())

        if self.currentPiece != None:
            for square in self.currentPiece.moves:            
                pygame.draw.circle(square.surface,"Grey",square.surface.get_rect().center,10)

        pygame.transform.scale(self.surface,gameScreen.get_size(),gameScreen)

    def getSquarePressed(self,x,y):
        for row in self.squareGrid:
            for square in row:
                if square.scaledRect.collidepoint(x,y):
                    return square
                
        return None

def main(screenSize=min(pygame.display.get_desktop_sizes()[0][0]-100,pygame.display.get_desktop_sizes()[0][1]-100)):
    global gameScreen,board,playerColour
    #screen must be a square for chess 
    gameScreen = pygame.display.set_mode((screenSize,screenSize))
    board = GameBoard()
    playerColour = "White"

    running = True
    while running:
        x,y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = board.getSquarePressed(x,y)
                if square == None:
                    break
                
                if board.currentPiece != None and square in board.currentPiece.moves:
                    board.currentPiece.move(square)
                    playerColour = "Black" if playerColour == "White" else "White"
                elif square.piece != None and square.piece.colour == playerColour:
                    square.piece.getMoves()
                    board.currentPiece = square.piece

                    board._update()      
                
        pygame.display.update()
        clock.tick(20)

    pygame.quit()

if __name__ == "__main__":
    main()

# Castling, promoting, check and checkmate currently unconsidered

# Could make screens not require square sizing and pad out extra space with solid colour?
# Might look bad and be better to just force square sizing and non-resizable windows


# Also want to try to make opponent - either learn how to make a chess ai (preferred as more impressive) 
# or connect to stockfish in some way
# Or both??

#Make AI in a seperate file in same repository