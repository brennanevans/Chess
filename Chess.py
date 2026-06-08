import pygame
pygame.init()
clock = pygame.time.Clock()

class Pieces:
    blackPieces = []
    whitePieces = []
    currentColour = "White"
    selectedPiece = None

    def __init__(self,name,square,colour):
        self.name = name
        self.square = square
        self.colour = colour
        self.moves = []
        
        # self.movements = [hor,ver,diag]
        match name:
            case "King":
                self.movements = [1,1,1]
                self.hasMoved = False
            case "Pawn":
                # ver reduces to 1 after 1 move
                self.movements = [0,2,1]
                self.twoTurn = -10
            case "Knight":
                self.movements = [0,0,0]    
            case "Bishop":
                self.movements = [0,0,7]
            case "Rook":
                self.movements = [7,7,0]
                self.hasMoved = False
            case "Queen":
                self.movements = [7,7,7]
            case _:
                raise ValueError("Invalid Name for Piece Object")

        self._createImage()
        if self.colour == "White":
            Pieces.whitePieces.append(self)
            if self.name == "King":
                Pieces.whiteKing = self
        else:
            Pieces.blackPieces.append(self)
            if self.name == "King":
                Pieces.blackKing = self

    @property
    def row(self):
        return self.square.row

    @property
    def col(self):
        return self.square.col
    
    def _createImage(self):
        imagePath = "Assets/" + self.colour + "Pieces/" + self.name + self.colour + ".png"
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.smoothscale(self.image,(50,50))
    
    def __repr__(self):
        return self.name + ":" + self._getNotation()
        
    def _getNotation(self):
        cols = ["A","B","C","D","E","F","G","H"]
        return cols[self.col] + str(self.row+1)


    def _getHorizontalMoves(self):
        moves = []

        # -1 and +1 as range has exclusive stop
        maxHorizontal = min(7,self.col+self.movements[0])+1
        minHorizontal = max(0,self.col-self.movements[0])-1

        #Check larger Column values - right from perspective of Black
        for colNum in range(self.col+1, maxHorizontal):
            square = board.grid[self.row][colNum]

            if square.piece == None:
                moves.append(square)
            elif square.piece.colour != self.colour:
                moves.append(square)
                break
            else:
                break
        
        #Check smaller Column values
        for colNum in range(self.col-1, minHorizontal,-1):
            square = board.grid[self.row][colNum]

            if square.piece == None:
                moves.append(square)
            elif square.piece.colour != self.colour:
                moves.append(square)
                break
            else:
                break

        return moves

    def _getVerticalMoves(self):
        moves = []

        # -1 and +1 as range has exclusive stop
        minVertical = max(0,self.row-self.movements[1])-1
        maxVertical = min(7,self.row+self.movements[1])+1

        # Dissallows pawns from moving backwards
        if self.name == "Pawn" and self.colour == "White":
            minVertical = self.row
        elif self.name == "Pawn" and self.colour == "Black":
            maxVertical = self.row

        #Check larger Row values - down from perspective of Black
        for rowNum in range(self.row+1, maxVertical):
            square = board.grid[rowNum][self.col]

            if square.piece == None:
                moves.append(square)
            elif square.piece.colour != self.colour and self.name != "Pawn":
                moves.append(square)
                break
            else:
                break
        
        #Check smaller Row values
        for rowNum in range(self.row-1, minVertical, -1):
            square = board.grid[rowNum][self.col]

            if square.piece == None:
                moves.append(square)
            elif square.piece.colour != self.colour and self.name != "Pawn":
                moves.append(square)
                break
            else:
                break

        return moves

    def _getDiagonalMoves(self):
        moves = []
        
        minHorizontal = max(0,self.col-self.movements[2])
        maxHorizontal = min(7,self.col+self.movements[2])
        minVertical = max(0,self.row-self.movements[2])
        maxVertical = min(7,self.row+self.movements[2])

        # Dissallows pawns from moving backwards
        if self.name == "Pawn" and self.colour == "White":
            minVertical = self.row
        elif self.name == "Pawn" and self.colour == "Black":
            maxVertical = self.row
        
        # "Down Left" means down left from perspective of Black pieces

        # "Up Left"
        rowNum = self.row-1
        colNum = self.col-1
        while rowNum>=minVertical and colNum>=minHorizontal:
            square = board.grid[rowNum][colNum]

            if square.piece == None and self.name != "Pawn":
                moves.append(square)
            elif square.piece != None and square.piece.colour != self.colour:
                moves.append(square)
                break
            else:
                break

            rowNum-=1
            colNum-=1

        # "Up Right"
        rowNum = self.row-1
        colNum = self.col+1

        while rowNum>=minVertical and colNum<=maxHorizontal:
            square = board.grid[rowNum][colNum]

            if square.piece == None and self.name != "Pawn":
                moves.append(square)
            elif square.piece != None and square.piece.colour != self.colour:
                moves.append(square)
                break
            else:
                break

            rowNum-=1
            colNum+=1

        # "Down Left"
        rowNum = self.row+1
        colNum = self.col-1
        while rowNum<=maxVertical and colNum>=minHorizontal: 
            square = board.grid[rowNum][colNum]

            if square.piece == None and self.name != "Pawn":
                moves.append(square)
            elif square.piece != None and square.piece.colour != self.colour:
                moves.append(square)
                break
            else:
                break

            rowNum+=1
            colNum-=1

        # "Down Right"
        rowNum = self.row+1
        colNum = self.col+1
        while rowNum<=maxVertical and colNum<=maxHorizontal:
            square = board.grid[rowNum][colNum]

            if square.piece == None and self.name != "Pawn":
                moves.append(square)
            elif square.piece != None and square.piece.colour != self.colour:
                moves.append(square)
                break
            else:
                break

            rowNum+=1
            colNum+=1

        return moves

    def _getKnightMoves(self):
        moves = []
        possibleOffsets = [(1,-2),(1,2),(-1,-2),(-1,2),(2,-1),(2,1),(-2,-1),(-2,1)]
        for offset in possibleOffsets:
            row = self.row + offset[0]
            col = self.col + offset[1]

            if -1 < row < 8 and -1 < col < 8:
                if board.grid[row][col].piece == None or board.grid[row][col].piece.colour != self.colour:
                    moves.append(board.grid[row][col])

        return moves

    def _getEnPassantMoves(self):
        global turn
        moves = []

        adjacentSquares = []
        if self.col+1 < 8:
            adjacentSquares.append(board.grid[self.row][self.col+1])
        
        if self.col -1 > -1:
            adjacentSquares.append(board.grid[self.row][self.col-1])

        value = 1 if self.colour == "White" else -1

        for square in adjacentSquares:
            if square.piece == None:
                continue
            elif square.piece.name != "Pawn" or square.piece.colour == self.colour:
                continue
            elif square.piece.twoTurn == turn-1:
                destinationSquare = board.grid[square.row+value][square.col]
                moves.append(destinationSquare)

        return moves

    def _getCastleMoves(self):
        moves = []

        pieces = Pieces.whitePieces if self.colour == "White" else Pieces.blackPieces
        opponentPieces = Pieces.whitePieces if self.colour == "Black" else Pieces.blackPieces

        attackedSquares = set()

        longRook = None
        shortRook = None
        
        for piece in opponentPieces:
            moveset = set(piece._getPossibleMoves(ignoreCastle = True)) # ignoring check
            attackedSquares = attackedSquares.union(moveset)

        if self.hasMoved or self.square in attackedSquares:
            return []

        for piece in pieces:
            if piece.name == "Rook" and piece.col == 7:
                shortRook = piece
            elif piece.name == "Rook" and piece.col == 0:
                longRook = piece

        # Short castle
        if shortRook != None and not shortRook.hasMoved:
            requiredSquares = [board.grid[self.row][1],board.grid[self.row][2]]
            if set(requiredSquares).intersection(attackedSquares) == set():
                if requiredSquares[0].piece == None and requiredSquares[1].piece == None:
                    moves.append(board.grid[self.row][1])

        # Long castle
        if longRook != None and not longRook.hasMoved:
            requiredSquares = [board.grid[self.row][4],board.grid[self.row][5],board.grid[self.row][6]]
            if set(requiredSquares).intersection(attackedSquares) == set():
                if requiredSquares[0].piece == None and requiredSquares[1].piece == None and requiredSquares[2].piece == None:
                    moves.append(board.grid[self.row][5])

        return moves

    def _getPossibleMoves(self,ignoreCastle=False) -> list:
        possibleMoves = []
        possibleMoves.extend(self._getHorizontalMoves())
        possibleMoves.extend(self._getVerticalMoves())
        possibleMoves.extend(self._getDiagonalMoves())

        if self.name == "Knight":
            possibleMoves.extend(self._getKnightMoves())
        elif self.name == "Pawn":
            possibleMoves.extend(self._getEnPassantMoves())
        elif self.name == "King" and not ignoreCastle:
            possibleMoves.extend(self._getCastleMoves())
        
        return possibleMoves

    def _noCheckMoves(self,possibleMoves):
        validMoves = []

        # Test if own king in check if move is taken
        currentKing = Pieces.whiteKing if Pieces.currentColour == "White" else Pieces.blackKing
        opponentPieces = Pieces.whitePieces if Pieces.currentColour == "Black" else Pieces.blackPieces
        originalLocation = self.square

        for move in possibleMoves:
            invalid = False
            destination = move
            destinationPiece = None
            enPassantPiece = None

            # Remove any piece landed on so don't test if this causes check
            if destination.piece != None:
                destinationPiece = destination.piece
                opponentPieces.remove(destinationPiece)
                destination.piece = None

            elif abs(self.row-destination.row) == 1 and abs(self.col-destination.col) == 1 and self.name == "Pawn":
                #En passant requires own checking as removes piece in unique way
                offset = -1 if self.colour == "White" else 1
                enPassantSquare = board.grid[destination.row+offset][destination.col]
                enPassantPiece = enPassantSquare.piece
                opponentPieces.remove(enPassantPiece)
                enPassantSquare.piece = None

            # Move piece
            self.square.piece = None
            self.square = destination
            self.square.piece = self

            # Check if King can be taken by any pieces
            for piece in opponentPieces:
                opponentMoves = piece._getPossibleMoves() # ignores check
                if currentKing.square in opponentMoves:
                    invalid = True
                    break

            # Move piece back
            self.square.piece = None
            self.square = originalLocation
            self.square.piece = self

            # Put piece taken back
            if destinationPiece != None:
                opponentPieces.append(destinationPiece)
                destination.piece = destinationPiece

            elif enPassantPiece != None: # Put enPassanted piece back
                opponentPieces.append(enPassantPiece)
                enPassantSquare.piece = enPassantPiece

            if not invalid:
                validMoves.append(move)

        return validMoves

    def getMoves(self):
        possibleMoves = self._getPossibleMoves()
        validMoves = self._noCheckMoves(possibleMoves)

        self.moves = validMoves
        return validMoves


    def moveTo(self,destination):
        if destination not in self.moves:
            return False
        
        # Set max vertical movement to 1
        if self.name == "Pawn":
            self.movements[1] = 1

            if abs(self.row-destination.row) == 2:
                self.twoTurn = turn
            
            #En passant - piece not landed on so can't be removed normally
            elif abs(self.row-destination.row) == 1 and abs(self.col-destination.col) == 1 and destination.piece == None:
                if self.colour == "White":
                    Pieces.blackPieces.remove(board.grid[destination.row-1][destination.col].piece)
                    board.grid[destination.row-1][destination.col].piece = None
                else:
                    Pieces.whitePieces.remove(board.grid[destination.row+1][destination.col].piece)
                    board.grid[destination.row+1][destination.col].piece = None

        elif self.name == "Rook":
            self.hasMoved = True # Used to prevent castling if either piece has already moved
        
        elif self.name == "King":
            self.hasMoved = True
            # Castled so need to move rook
            if self.col - destination.col == 2:
                rook = board.grid[self.row][0].piece
                board.grid[self.row][0].piece = None
                board.grid[self.row][2].piece = rook
                rook.square = board.grid[self.row][2]
            elif self.col - destination.col == -2:
                rook = board.grid[self.row][7].piece
                board.grid[self.row][7].piece = None
                board.grid[self.row][4].piece = rook
                rook.square = board.grid[self.row][4]
                


        # Remove any piece landed on
        if destination.piece != None:
            if self.colour == "White":
                Pieces.blackPieces.remove(destination.piece)
            else:
                Pieces.whitePieces.remove(destination.piece)
            destination.piece = None

        # Move piece
        self.square.piece = None
        self.square = destination
        self.square.piece = self

        Pieces.selectedPiece = None

        if self.name == "Pawn" and self.row in [0,7]:
            self.promote()

        board.updateDisplay()
        updateTurn()
        return True
    
    def _displayOptions(row,col,colour):
        promoteSquares = []
        if row == 0:
            for i in range(row,row+4):
                promoteSquares.append(board.grid[i][col])
        else:
            for i in range(row,row-4,-1):
                promoteSquares.append(board.grid[i][col])

        pieceCol = ["Queen","Knight","Rook","Bishop"]
        
        if colour == "White":
            promoteSquares = promoteSquares[::-1] # Reverse direction so same for both colours

        pieceNum = 0
        for square in promoteSquares:
            rect = square.scaledRect
            testSurface = pygame.Surface((rect.w+1,rect.h+1))
            testSurface.fill("#F1F1F1")

            image = pygame.image.load(f"Assets/{colour}Pieces/{pieceCol[pieceNum]}{colour}.png")
            image = pygame.transform.smoothscale(image,(rect.w,rect.h))
            testSurface.blit(image,(0,0))
            gameScreen.blit(testSurface,rect)

            pieceNum+=1

        pygame.display.update()

        return promoteSquares

    def promote(self):
        if self.name != "Pawn":
            raise ValueError("Can only promote pawns")
        
        # Show GUI screen for selecting which piece to choose
        options = Pieces._displayOptions(self.row,self.col,self.colour)
        pieceCol = ["Queen","Knight","Rook","Bishop"]
        chosenPromotion = ""

        optionNotClicked = True
        while optionNotClicked:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x,y = pygame.mouse.get_pos()
                    square = board.getSquarePressed(x,y)
                    if square in options:
                        chosenPromotion = pieceCol[options.index(square)]
                        optionNotClicked = False
                        break


        # Replace piece
        pieces = Pieces.whitePieces if self.colour == "White" else Pieces.blackPieces
        pieces.remove(self)
        self.square.piece = Pieces(chosenPromotion,self.square,self.colour) # Automatically added to pieces

class Square:
    def __init__(self,surface:pygame.Surface,row,column,colour):
        self.surface = surface
        self.scaledRect = pygame.Rect(0,0,0,0)

        self.row = row
        self.col = column

        _cols = ["A","B","C","D","E","F","G","H"]
        self.notation = _cols[self.col] + str(self.row+1)

        self.colour = colour

        self.piece = None
    
    def __repr__(self):
        return "Square(" + self.notation + ")"   


class GameBoard:
    SIZE = 8
    COLOUR1 = "#D7BA89"
    COLOUR2 = "#56342A"

    def __init__(self):
        self.squareSize = 50
        self.boardSize = 400
        self.surface = pygame.Surface((self.boardSize,self.boardSize))

        self.grid = []

        self._createBoard()
        self._addPieces()
        self.updateDisplay()

    def _createBoard(self):
        currentColour = GameBoard.COLOUR1

        for row in range(GameBoard.SIZE):
            squaresRow = []

            for column in range(GameBoard.SIZE):
                x = column * self.squareSize
                y = row * self.squareSize
                square = Square(self.surface.subsurface(x,y,self.squareSize,self.squareSize),row,column,currentColour)
                square.surface.fill(currentColour)

                scaledSize = self.squareSize*gameScreen.get_width()/self.surface.get_width()
                square.scaledRect = pygame.Rect(column*scaledSize,row*scaledSize,scaledSize,scaledSize)

                squaresRow.append(square)

                currentColour = GameBoard.COLOUR1 if currentColour == GameBoard.COLOUR2 else GameBoard.COLOUR2
            currentColour = GameBoard.COLOUR1 if currentColour == GameBoard.COLOUR2 else GameBoard.COLOUR2 # changes at end of row -> checkerboard

            self.grid.append(squaresRow)

    def _addPieces(self):
        rows = [self.grid[0],self.grid[1],self.grid[6],self.grid[7]]
        pieceRow = ["Rook","Knight","Bishop","King","Queen","Bishop","Knight","Rook"]

        for row in rows:
            for square in row:
                colour = "Black" if square.row > 1 else "White"
                if square.row in [0,7]:
                    square.piece = Pieces(pieceRow[square.col],square,colour)
                else:
                    square.piece = Pieces("Pawn",square,colour)
    
    def updateDisplay(self):
        for row in self.grid:
            for square in row:
                square.surface.fill(square.colour) # clear square

                if square.piece != None:
                    square.surface.blit(square.piece.image,square.surface.get_rect())

                if Pieces.selectedPiece != None and square in Pieces.selectedPiece.moves:
                    pygame.draw.circle(square.surface,"Grey",square.surface.get_rect().center,10)

        pygame.transform.scale(self.surface,gameScreen.get_size(),gameScreen)

    def getSquarePressed(self,x,y):
        for row in self.grid:
            for square in row:
                if square.scaledRect.collidepoint(x,y):
                    return square
                
        return None
    

def updateTurn():
    global turn

    turn += 1

    if Pieces.currentColour == "White":
        for piece in Pieces.whitePieces:
            piece.moves = []

        Pieces.currentColour = "Black"

    else:
        for piece in Pieces.blackPieces:
            piece.moves = []

        Pieces.currentColour = "White"

    status = getGameStatus()
    if status == "Checkmate":
        print("Checkmate, " + Pieces.currentColour +" Wins!!")
    elif status == "Stalemate":
        print("Stalemate.")

def getGameStatus():
    inCheck = False
    noMoves = True

    if Pieces.currentColour == "White":
        currentKing = Pieces.whiteKing
        currentPieces = Pieces.whitePieces
        opponentPieces = Pieces.blackPieces
        
    else:
        currentKing = Pieces.blackKing
        currentPieces = Pieces.blackPieces
        opponentPieces = Pieces.whitePieces
    
    for piece in opponentPieces:
        if currentKing.square in piece._getPossibleMoves():
            inCheck = True
            break
            
    for piece in currentPieces:
        if piece.getMoves() != []:
            noMoves = False
            break

    if noMoves and inCheck:
        return "Checkmate"
    elif noMoves:
        return "Stalemate"
    else:
        return "Normal"


def main(screenSize=min(pygame.display.get_desktop_sizes()[0][0]-100,pygame.display.get_desktop_sizes()[0][1]-100)):
    global gameScreen,board,turn

    #screen must be a square for chess 
    gameScreen = pygame.display.set_mode((screenSize,screenSize))
    board = GameBoard()
    turn = 0

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
                
                if Pieces.selectedPiece != None and square in Pieces.selectedPiece.moves:
                    Pieces.selectedPiece.moveTo(square)
                    
                elif square.piece != None and square.piece.colour == Pieces.currentColour:
                    Pieces.selectedPiece = square.piece 
                    Pieces.selectedPiece.getMoves() 
                    board.updateDisplay() # Board updates to show potential moves for selected piece
                
        pygame.display.update()
        clock.tick(20)

    pygame.quit()

if __name__ == "__main__":
    main()

# Need to add promoting - very easy just requires some GUI stuff 

# Need to clean up code

# Could make screens not require square sizing and pad out extra space with solid colour?
# Might look bad and be better to just force square sizing and non-resizable windows


# Also want to try to make opponent - either learn how to make a chess ai (preferred as more impressive) 
# or connect to stockfish in some way
# Or both??

#Make AI in a seperate file in same repository