import pygame
pygame.init()
pygame.font.init()

clock = pygame.time.Clock()

class Pieces:
    """
    Piece objects are chess pieces each with information about themselves.

    Pieces is used to get any information involving the chess pieces currently on
    the board. This includes both information about individual pieces via 
    objects, as well as collections of pieces.

    Attributes:
        pieceDict(dict): The keys are the piece colours and the values are the
          lists of pieces of that colour.

        kingDict(dict): The keys are the piece colours and the values are the
          Piece objects of the colour with the name "King".

        selectedPiece(Piece): The currently selected piece.
        currentColour(str): The colour of the pieces of the current player.
        currentPieces(list): The pieces belonging to the current player.
        opponentColour(str): The colour of the pieces of the other player.
        opponentPieces(list): The pieces belonging to the other player.
    """
    pieceDict = {"Black":[],"White":[]}
    kingDict = {}

    selectedPiece = None
    
    currentColour = "White"
    currentPieces = pieceDict[currentColour]

    opponentColour = "Black"
    opponentPieces = pieceDict[opponentColour]
    

    def __init__(self,name:str,square,colour:str):
        """
        Creates a piece based on the parameters passed.

        Args:
            name: The type of piece to be created, e.g. Pawn.
            square(Square): The square object on which the piece is currently
              located.
            colour: The colour of the piece.

        Raises:
            ValueError: If the name parameter is not a valid piece type.
        

        """ 
        name = name.capitalize()

        self.name = name
        self.square = square
        self.colour = colour
        self.moves = []
        
        # self.movements = [hor,ver,diag]
        match name:
            case "King":
                self.movements = [1,1,1]
                self.hasMoved = False
                Pieces.kingDict[self.colour] = self
            case "Pawn":
                # ver reduces to 1 after 1 move
                self.movements = [0,2,1]
                self.twoTurn = -1 
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
        Pieces.pieceDict[self.colour].append(self)

    @property
    def row(self):
        """The current row of the square that the piece is on."""
        return self.square.row

    @property
    def col(self):
        """The current column of the square that the piece is on."""
        return self.square.col
    
    def _createImage(self):
        """
        Loads the image for this piece and scales it to an appropriate size.
        """
        imagePath = f"Assets/{self.colour}Pieces/{self.name}{self.colour}.png"
        self.image = pygame.image.load(imagePath)
        self.image = pygame.transform.smoothscale(self.image,(50,50))
    
    def __repr__(self):
        return self.name + ":" + self._getNotation()
        
    def _getNotation(self):
        cols = ["A","B","C","D","E","F","G","H"]
        return cols[self.col] + str(self.row+1)

    
    def _getMoveSubset(self,rowEnd:int,colEnd:int,rowStep:int,colStep:int,capturesOnly=False,noCaptures=False):
        """
        Helper method that gets all the possible moves between 2 points.

        This method is used to simplify the logic of the other methods
        involving getting moves. The moves returned by this method INCLUDE
        those that would result in the King being taken as this is handled
        by a seperate method.

        Possible here refers to whether the move is allowed by all other rules
        of chess such as the inability to take one's own pieces, or move
        through pieces.
        
        Args:
            rowEnd: The index of the final row to check in board.grid.
            colEnd: The index of the final column to check in board.grid.
            rowStep: The amount to increment or decrement row indices.
            colStep: The amount to increment or decremenet column indicies.
            capturesOnly: True if should only allow moves which take a piece,
              else False.
            noCaptures: True if shouldn't allow moves which take a piece, else 
              False.

        Returns:
            list: All the possible moves between the 2 points.
        """
        moveSubset = []
        # This is to prevent pawns moving backwards
        if self.row == rowEnd and self.col == colEnd:
            return []
        
        # Needed so piece doesn't see itself and break out of loop
        row = self.row + rowStep
        col = self.col + colStep
        while True:
            if row == rowEnd and rowStep != 0:
                break
            elif col == colEnd and colStep != 0:
                break

            square = board.grid[row][col]

            if square.piece == None and not capturesOnly:
                moveSubset.append(square)
            elif square.piece == None and capturesOnly:
                break

            elif square.piece.colour != self.colour and not noCaptures:
                moveSubset.append(square)
                break
            else:
                break

            row += rowStep
            col += colStep

        return moveSubset

    def _getHorizontalMoves(self):
        """
        Gets all the horizontal moves self can make, ignoring check.
    
        Returns:
            list: All the possible horizontal moves.
        """
        moves = []

        # -1 and +1 as range has exclusive stop
        maxHorizontal = min(7,self.col+self.movements[0])+1
        minHorizontal = max(0,self.col-self.movements[0])-1

        #Check larger Column values - right from perspective of Black
        moves.extend(self._getMoveSubset(self.row,maxHorizontal,0,1))

        #Check smaller Column values
        moves.extend(self._getMoveSubset(self.row,minHorizontal,0,-1))

        return moves

    def _getVerticalMoves(self):
        """
        Gets all the vertical moves self can make, ignoring check.
    
        Returns:
            list: All the possible vertical moves.
        """
        moves = []

        # -1 and +1 as range has exclusive stop
        minVertical = max(0,self.row-self.movements[1])-1
        maxVertical = min(7,self.row+self.movements[1])+1

        # Dissallows pawns from moving backwards
        if self.name == "Pawn" and self.colour == "White":
            minVertical = self.row-1
        elif self.name == "Pawn" and self.colour == "Black":
            maxVertical = self.row+1

        #Check larger Row values - down from perspective of Black
        moves.extend(self._getMoveSubset(maxVertical,self.col,1,0,noCaptures=(self.name=="Pawn")))

        #Check smaller Row values
        moves.extend(self._getMoveSubset(minVertical,self.col,-1,0,noCaptures=(self.name=="Pawn")))

        return moves

    def _getDiagonalMoves(self):
        """
        Gets all the diagonal moves self can make, ignoring check.
    
        Returns:
            list: All the possible diagonal moves.
        """
        moves = []
        
        minHorizontal = max(0,self.col-self.movements[2])-1
        maxHorizontal = min(7,self.col+self.movements[2])+1
        minVertical = max(0,self.row-self.movements[2])-1
        maxVertical = min(7,self.row+self.movements[2])+1

        # Dissallows pawns from moving backwards
        if self.name == "Pawn" and self.colour == "White":
            minVertical = self.row-1
        elif self.name == "Pawn" and self.colour == "Black":
            maxVertical = self.row+1
        
        # "Down Left" means down left from perspective of Black pieces

        # "Up Left"
        moves.extend(self._getMoveSubset(minVertical,minHorizontal,-1,-1,capturesOnly=(self.name=="Pawn")))

        # "Up Right"
        moves.extend(self._getMoveSubset(minVertical,maxHorizontal,-1,1,capturesOnly=(self.name=="Pawn")))

        # "Down Left"
        moves.extend(self._getMoveSubset(maxVertical,minHorizontal,1,-1,capturesOnly=(self.name=="Pawn")))

        # "Down Right"
        moves.extend(self._getMoveSubset(maxVertical,maxHorizontal,1,1,capturesOnly=(self.name=="Pawn")))

        return moves

    def _getKnightMoves(self):
        """
        Gets all the possible knight moves self can make, ignoring check.
        
        Returns:
            list: All the possible knight moves.
        """
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
        """
        Gets all the possible En Passant moves self can make, ignoring check.

        En Passant is a special movement type for Pawns in chess. It requires
        an opponent's pawn to have moved 2 spaces and land horizontally 
        adjacent to it. More information can be found here:
        https://en.wikipedia.org/wiki/En_passant
        
        Returns:
            list: All the possible En Passant moves.
        """
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
        """
        Gets all the possible Castling moves self can make.

        Castling is a special movement type for Kings with specific 
        requirements which can be found here: 
        https://en.wikipedia.org/wiki/Castling

        Note this method, unlike the other get_*Moves methods DOES NOT return 
        any moves that would result in the current King ending in (or moving 
        through) check.

        Returns:
            list: All the possible Castling moves.
        """
        moves = []

        pieces = Pieces.pieceDict[self.colour]
        opponentPieces = Pieces.pieceDict["White"] if self.colour == "Black" else Pieces.pieceDict["Black"]

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

    def _getPossibleMoves(self,ignoreCastle=False):
        """
        Gets all the possible moves that self can make, ignoring check.

        Args:
            ignoreCastle: Whether or not Castling should be considered.

        Returns:
            list: All the Square objects representing possible moves self can
              make, potentially excluding Castling.
        """
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

    def _noCheckMoves(self,possibleMoves:list):
        """
        Gets all the moves from possibleMoves not resulting in Checkmate.

        This method returns all the moves from possibleMoves that wouldn't
        leave the current player's King available to be taken next turn as
        these moves can not be made in chess.

        Args:
            possibleMoves: All the Square objects that represent moves self
              could make that could potentially be legal.

        Returns:
            list: All the Square objects that represent moves self can make
              not resulting in Checkmate for the King of their own colour.
        """
        validMoves = []

        # Test if own king in check if move is taken
        currentKing = Pieces.kingDict[self.colour]
        opponentPieces = Pieces.opponentPieces
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

            elif enPassantPiece != None: # Put En Passanted piece back
                opponentPieces.append(enPassantPiece)
                enPassantSquare.piece = enPassantPiece

            if not invalid:
                validMoves.append(move)

        return validMoves

    def getMoves(self):
        """
        Gets all the legal moves self can make.

        Legal here refers to moves which follow ALL the rules of chess. 
        Examples of illegal moves include: moves that would take a piece of 
        the same colour as self, moves that would result in the current King
        being under attack ect.

        Returns:
            list: All the legal moves self can make.

        """
        possibleMoves = self._getPossibleMoves()
        validMoves = self._noCheckMoves(possibleMoves)

        self.moves = validMoves
        return validMoves


    def moveTo(self,destination):
        """
        Moves self to a specified square.

        This method will update self.square and destination.piece provided
        destination is in self's legal moves. It also handles the removal of
        any pieces including those indirectly taken in En Passant.

        If the move is determined to be castling a King, it will also move the
        complementing rook to the correct location.
        
        Args:
            destination(Square): The square the piece should be moved to.

        Returns:
            boolean: True if the move is legal, else False.
        """
        if destination not in self.getMoves():
            return False
        
        # Set max vertical movement to 1
        if self.name == "Pawn":
            self.movements[1] = 1

            if abs(self.row-destination.row) == 2:
                self.twoTurn = turn
            
            #En passant - piece not landed on so can't be removed normally
            rowOffset = self.row-destination.row
            colOffset = self.col-destination.col
            if rowOffset != 0 and colOffset != 0 and destination.piece == None:
                Pieces.opponentPieces.remove(board.grid[destination.row+rowOffset][destination.col].piece)
                board.grid[destination.row+rowOffset][destination.col].piece = None

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
            Pieces.pieceDict[Pieces.opponentColour].remove(destination.piece)
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
    
    def _displayOptions(row:int,col:int,colour:str):
        #TODO does this belong more in GameBoard??
        """
        Displays the options for promotion on the screen.

        Args:
            row: The row of the piece to be promoted.
            col: The column of the piece to be promoted.
            colour: The colour of the piece to be promoted.

        Returns:
            list: All the Square objects temporarily containing the promotion
              options.
        """
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
        """
        Replaces self with a new Piece object.

        This method halts program running until a promotion choice is made 
        and will update all necessary parameters with the new Piece object.
        """
        if self.name != "Pawn":
            raise ValueError("Can only promote pawns")
        
        # Show GUI screen for selecting which piece to choose
        options = Pieces._displayOptions(self.row,self.col,self.colour)
        pieceCol = ["Queen","Knight","Rook","Bishop"]
        chosenPromotion = ""

        # Halt program and listen for events until selection is made
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
        Pieces.pieceDict[self.colour].remove(self)
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
    

def getGameStatus():
    inCheck = False
    noMoves = True

    currentKing = Pieces.kingDict[Pieces.currentColour]
    
    for piece in Pieces.opponentPieces:
        if currentKing.square in piece._getPossibleMoves():
            inCheck = True
            break
            
    for piece in Pieces.currentPieces:
        if piece.getMoves() != []:
            noMoves = False
            break

    if noMoves and inCheck:
        return "Checkmate"
    elif noMoves:
        return "Stalemate"
    else:
        return "Normal"

def displayEndScreen(status):
    font = pygame.font.SysFont("Arial",50)

    if status == "Checkmate":
        colour = "White" if Pieces.currentColour == "Black" else "Black"
        text = f"Checkmate, {colour} Wins!!"
    else:
        text = "Stalemate."


    textbox = pygame.font.Font.render(font,text,False,"Black","White")
    pygame.draw.rect(textbox,"Black",textbox.get_rect(),1)
    
    x = (gameScreen.get_rect().width - textbox.get_width()) / 2
    y = (gameScreen.get_rect().height - textbox.get_height()) / 2
    
    gameScreen.blit(textbox,(x,y))

    pygame.display.update()
    pygame.time.wait(1000)

def updateTurn():
    global turn
    turn += 1

    for piece in Pieces.currentPieces:
        piece.moves = []

    Pieces.currentColour = "White" if Pieces.currentColour == "Black" else "Black"
    Pieces.opponentColour = "Black" if Pieces.currentColour == "White" else "White"
    Pieces.currentPieces = Pieces.pieceDict[Pieces.currentColour]
    Pieces.opponentPieces = Pieces.pieceDict[Pieces.opponentColour]
    
    status = getGameStatus()
    
    if status != "Normal":
        displayEndScreen(status)


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
                
                if Pieces.selectedPiece != None:
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

# Could make screens not require square sizing and pad out extra space with solid colour?
# Might look bad and be better to just force square sizing and non-resizable windows


# Also want to try to make opponent - either learn how to make a chess ai (preferred as more impressive) 
# or connect to stockfish in some way
# Or both??

#Make AI in a seperate file in same repository