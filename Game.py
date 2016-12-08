"""
***************************************************************
FILE: Game.py
AUTHOR: Paige Rossi
PARTNER: none
ASSIGNMENT: Project 7
DATE: November 6, 2016
DESCRIPTION: This is a program that allows the players to play a game of
Scrabble
***************************************************************
"""

import random
from cs110graphics import *

class Board:
    """A class for the game's board"""
    
    def __init__(self, win):
        self._spaces = []
        self._win = win
        self._tile = None
        self._spot = None
        self._turnButton = EndTurn(self._win, self, (600, 75))
        self._resetButton = ResetTurn(self._win, self, (600, 115))
        self._warning = InvalidMove(self, self._win)
        self._turn = 0
        self._playedInTurn = []
        self._allTilesUsed = []
        self._tilesToCount = []
        
        for row in range(15):
            self._spaces.append([])
            for col in range(15):
                space = BoardSpace(self, win, (row * 30 + 30, col * 30 + 30))
                self._spaces[row].append(space)
                
        self._start = self._spaces[7][7]
        self._start.fillColor('#FB8C71')
        
        #Store special spaces for scoring later
                
        self._tripleWords = [self._spaces[0][0], self._spaces[0][7], 
                             self._spaces[0][14], self._spaces[7][0],
                             self._spaces[7][14], self._spaces[14][0],
                             self._spaces[14][7], self._spaces[14][14]]
                             
        self._doubleWords = [self._spaces[1][1], self._spaces[1][13], 
                             self._spaces[2][2], self._spaces[2][12],
                             self._spaces[3][3], self._spaces[3][11],
                             self._spaces[4][4], self._spaces[4][10],
                             self._spaces[10][4], self._spaces[10][10],
                             self._spaces[11][3], self._spaces[11][11],
                             self._spaces[12][2], self._spaces[12][12],
                             self._spaces[13][1], self._spaces[13][13]]
                             
        self._tripleLetters = [self._spaces[1][5], self._spaces[1][9],
                               self._spaces[5][1], self._spaces[5][5],
                               self._spaces[5][9], self._spaces[5][13],
                               self._spaces[9][1], self._spaces[9][5],
                               self._spaces[9][9], self._spaces[9][13],
                               self._spaces[13][5], self._spaces[13][9]]
                               
        self._doubleLetters = [self._spaces[0][3], self._spaces[0][11],
                               self._spaces[2][6], self._spaces[2][8],
                               self._spaces[3][0], self._spaces[3][7],
                               self._spaces[3][14], self._spaces[6][2],
                               self._spaces[6][6], self._spaces[6][8],
                               self._spaces[6][12], self._spaces[7][3],
                               self._spaces[7][11], self._spaces[8][2],
                               self._spaces[8][6], self._spaces[8][8],
                               self._spaces[8][12], self._spaces[11][0],
                               self._spaces[11][7], self._spaces[11][14],
                               self._spaces[12][6], self._spaces[12][8],
                               self._spaces[14][3], self._spaces[14][11]]
                               
    #Set up color and labels of special spaces
    
        for space in self._tripleLetters:
            space.fillColor('#3A5AF9')
            space.setText('TL')
        for space in self._tripleWords:
            space.fillColor('#F44E26')
            space.setText('TW')
        for space in self._doubleLetters:
            space.fillColor('#86CAF9')
            space.setText('DL')
        for space in self._doubleWords:
            space.fillColor('#FB8C71')
            space.setText('DW')
            
        self._allTiles = TileBag(self, self._win)
        self._allPlayers = []
        self._allPlayerTiles = []
        self._allScores = []
        
        self._numberOfPlayers = int(input('Enter the number of players'))
        while self._numberOfPlayers > 4 or self._numberOfPlayers < 2:
            self._numberOfPlayers = int(input('Please enter a number ' \
            + 'between 2 and 4'))
            
        #Set up ways to manage information about each player and turn
        
        for i in range(self._numberOfPlayers):
            name = input("Enter player " + str(i + 1) + "'s name")
            player = Player(self, self._win, name)
            self._allPlayers.append(player)
            self._allPlayerTiles.append(self._allTiles.dealPlayer())
            self._allScores.append(0)
        for i in range(len(self._allPlayerTiles[0])):
            self._allPlayerTiles[0][i].addTo(self._win)
            self._allPlayerTiles[0][i].moveTo((30 + i * 30, 500))
            
        #Set up scoreboards
        
        self._scoreDisplay = []
        for i in range(self._numberOfPlayers):
            name = self._allPlayers[i].getName()
            nameSize = 15
            if len(name) > 9: #fit name to box
                nameSize = 10
            display = DisplayScore(0, (600, (200 + i * 100)), self._win, 
                                   self, name, nameSize)
            self._scoreDisplay.append(display)
            
    def playTile(self):
        """Executes the move of a tile to a spot on the board"""
        
        self._tile.moveTo(self._spot.getCenter())
        self._tile.setBorderColor('black')
        self._playedInTurn.append(self._tile)
        self._tile.deactivate()
        self._tile = None
        self._spot = None
        
    def tileClicked(self, tile):
        """Manages the actions that occur when a tile is clicked"""
        
        self._tile = tile
        if self._tile.getActiveStatus() is False:
            self._tile = None
        
        elif self._tile in self._allPlayerTiles[self._turn]:
            self._tile.setBorderColor('red')
            self._allPlayerTiles[self._turn].remove(self._tile)
        
    def spotClicked(self, spot):
        """Manages the actions that occur when a spot is clicked"""
        
        self._spot = spot
        if self._tile is not None:
            self.playTile()
            
    def resetTurn(self):
        """Allows the player to recall their tiles before finishing their 
        turn in case they make a mistake"""
        
        for tile in self._playedInTurn:
            self._allPlayerTiles[self._turn].append(tile)
            tile.activate()
            
        self._playedInTurn = []
            
        for i in range(len(self._allPlayerTiles[self._turn])):
            self._allPlayerTiles[self._turn][i].moveTo((30 + i * 30, 500))
            
            
    def changeTurn(self):
        """Changes the turn when the "end turn" button is clicked"""
        
        #The next block of code checks to see if a word has been played in an
        #invalid spot (aka not connected to any tiles already played
        
        for tile in self._playedInTurn: 
            self.findScoringTiles(tile, self._playedInTurn, self._allTilesUsed)
        if self._tilesToCount == [] and len(self._allTilesUsed) != 0:
            self._warning.addWarning()
            self.resetTurn()
            return
            
        #Everything after this is for when tile placement is valid

        for i in range(len(self._allPlayerTiles[self._turn])):
            self._allPlayerTiles[self._turn][i].removeFrom(self._win)
        
        self._allTiles.refillTiles(self._allPlayerTiles[self._turn])
        self._allScores[self._turn] += self.score()
        self._scoreDisplay[self._turn].setScore(str
                                                (self._allScores[self._turn]))
        self._turn = (self._turn + 1) % self._numberOfPlayers
        
        for i in range(len(self._allPlayerTiles[self._turn])):
            self._allPlayerTiles[self._turn][i].addTo(self._win)
            self._allPlayerTiles[self._turn][i].moveTo((30 + i * 30, 500))
        
        for tile in self._playedInTurn:
            self._allTilesUsed.append(tile)
            
        self._playedInTurn = []
            
    def score(self):
        """Computes the score of a player at the end of their turn"""
        
        self._tilesToCount = []
            
        for tile in self._playedInTurn:
            self.findScoringTiles(tile, self._playedInTurn, self._allTilesUsed)
            
        scoreThisTurn = 0
        
        for tile in self._tilesToCount:
            self._playedInTurn.append(tile)
        
        if len(self._playedInTurn) == 0:
            return scoreThisTurn
        for i in range(len(self._playedInTurn)):
            scoreThisTurn += self.isSpecialLetter(self._playedInTurn[i])
        
        for i in range(len(self._playedInTurn)):
            if self.isDoubleWord(self._playedInTurn[i]):
                scoreThisTurn = scoreThisTurn * 2
            elif self.isTripleWord(self._playedInTurn[i]):
                scoreThisTurn = scoreThisTurn * 3
            else:
                scoreThisTurn += 0
            
        return scoreThisTurn
    
    def findScoringTiles(self, startTile, tilesPlayed, allTilesUsed):
        """Adds all tiles that need to be scored to the played in turn list"""

        location = startTile.getCenter()
        left = (-30, 0)
        right = (30, 0)
        up = (0, -30)
        down = (0, 30)
        directions = [left, right, up, down]
        
        
        if len(allTilesUsed) == 0: #avoids out of range error for first turn
            return
            
        for tile in allTilesUsed:
            for dx, dy in directions:
                if tile.getCenter() == (location[0] + dx, location[1] + dy) \
                and tile not in tilesPlayed\
                and tile not in self._tilesToCount:
                    self._tilesToCount.append(tile)
                    for item in self.checkDirection(tile, dx, dy, \
                    tilesPlayed, allTilesUsed):
                        self._tilesToCount.append(item)
                    
        
    def checkDirection(self, tile, dx, dy, tilesPlayed, allTilesUsed):
        """Checks for tiles to be scored in the direction in which a scoring
        tile has already been found"""
        
        location = tile.getCenter()
        addTiles = []

        for tile in allTilesUsed:
            if tile.getCenter() == (location[0] + dx, location[1] + dy)\
            and tile not in tilesPlayed\
            and tile not in self._tilesToCount:
                addTiles.append(tile)
                
        return addTiles
        
    #CITE: TA Lia
    #DETAILS: She gave me the idea to create the checkDirection function so that
    #my findScoringTiles function wouldn't have to use recursion in every
    #direction
    
    def isSpecialLetter(self, tile):
        """Tests if the tile is on a double or triple letter space."""
        if self.isDoubleLetter(tile):
            score = tile.getValue() * 2
            
        elif self.isTripleLetter(tile):
            score = tile.getValue() * 3
            
        else:
            score = tile.getValue()
        
        return score
            
    def isTripleWord(self, tile):
        """Returns if a space is a triple word space"""
        tripleWordLocations = []
        for space in self._tripleWords:
            tripleWordLocations.append(space.getCenter())
        if tile.getCenter() in tripleWordLocations:
            index = tripleWordLocations.index(tile.getCenter())
            self._tripleWords.pop(index) #triple word space cannot be reused
            return True
        return False

    def isDoubleWord(self, tile):
        """Returns if a space is a double word space"""
        doubleWordLocations = []
        for space in self._doubleWords:
            doubleWordLocations.append(space.getCenter())
        if tile.getCenter() in doubleWordLocations:
            index = doubleWordLocations.index(tile.getCenter())
            self._doubleWords.pop(index) #double word space cannot be reused
            return True
        return False

    def isTripleLetter(self, tile):
        """Returns if a space is a triple letter space"""
        tripleLetterLocations = []
        for space in self._tripleLetters:
            tripleLetterLocations.append(space.getCenter())
        if tile.getCenter() in tripleLetterLocations:
            index = tripleLetterLocations.index(tile.getCenter())
            self._tripleLetters.pop(index) #triple letter space cannot be reused
            return True
        return False

    def isDoubleLetter(self, tile):
        """Returns if a space is a double letter space"""
        doubleLetterLocations = []
        for space in self._doubleLetters:
            doubleLetterLocations.append(space.getCenter())
        if tile.getCenter() in doubleLetterLocations:
            index = doubleLetterLocations.index(tile.getCenter())
            self._doubleLetters.pop(index) #double letter space cannot be reused
            return True
        return False
    
class BoardSpace(EventHandler):
    """A class for each space on the board"""
    
    def __init__(self, board, win, center):
        EventHandler.__init__(self)
        self._win = win
        self._center = center
        self._board = board
        self._background = Square(30, self._center)
        self._text = Text(' ', (self._center[0], self._center[1] + 5), 15)
        self._background.setFillColor('tan')
        self._background.setBorderColor('black')
        self._win.add(self._background)
        self._win.add(self._text)
        self._background.addHandler(self)
        self._text.addHandler(self)
    
    def fillColor(self, color):
        """Changes the fill color of the space on the board"""
        
        self._background.setFillColor(color)
    
    def getCenter(self):
        """Returns the space's center"""
        
        return self._background.getCenter()
        
    def setText(self, newText):
        """Changes the text that appears on the space"""
        
        self._text.setText(newText)
        
    def handleMouseEnter(self):
        self._background.setDepth(1)
        self._text.setDepth(1)
        self._background.setBorderColor('#40F310')
        
    def handleMouseLeave(self):
        self._background.setBorderColor('black')
    
    def handleMouseRelease(self):
        self._board.spotClicked(self)
        
    
class Tile(EventHandler):
    """A class to create a letter tile"""
    def __init__(self, board, win, center, letter, value):
        EventHandler.__init__(self)
        self._center = center
        self._board = board
        self._letter = letter
        self._value = value
        self._isActive = True
        self._win = win
        self._tile = Square(30, self._center)
        self._tile.setFillColor('#FCF9C6')
        self._label = Text(self._letter, (self._center[0], 
                                          self._center[1] + 5), 15)
        self._pointLabel = Text(self._value, (self._center[0] + 7, 
                                              self._center[1] + 11), 9)
        self._tile.setDepth(0)
        self._label.setDepth(0)
        self._pointLabel.setDepth(0)
        self._label.addHandler(self)
        self._tile.addHandler(self)
        self._pointLabel.addHandler(self)
        
    def getValue(self):
        """Returns the point value of a tile"""
        
        return self._value
    
    def getCenter(self):
        """Returns the center of a tile"""
        
        return self._tile.getCenter()
        
    def moveTo(self, center):
        """Moves a tile to a given center location"""
        self._tile.moveTo((center))
        self._label.moveTo((center[0], center[1] + 5))
        self._pointLabel.moveTo((center[0] + 10, center[1] + 10))
        
    def setBorderColor(self, color):
        """Sets the border color of the tile"""
        
        self._tile.setBorderColor(color)

        
    def addTo(self, win):
        """Adds a tile to a window"""
        win.add(self._tile)
        win.add(self._label)
        win.add(self._pointLabel)
        
    def removeFrom(self, win):
        """Removes a tile from a window"""
        win.remove(self._tile)
        win.remove(self._label)
        win.remove(self._pointLabel)
        
    def handleMouseRelease(self):
        self._board.tileClicked(self)
        
    def deactivate(self):
        """Deactivates a tile so that once it is placed on the board it can no
        longer be moved"""
        
        self._isActive = False
        
    def activate(self):
        """Activates a tile so that it can be moved again"""
        
        self._isActive = True
        
    def getActiveStatus(self):
        """Returns whether or not the tile is active"""
        
        return self._isActive

class TileBag:
    """A class to create and manage all of the tiles necessary to play the
    game"""
    def __init__(self, board, win):
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
                   'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                   'Y', 'Z', ' ']
        frequency = [9, 2, 2, 4, 12, 2, 3, 2, 9, 1, 1, 4, 2, 6, 8, 2, 1, 6, 4,
                     6, 4, 2, 2, 1, 2, 1, 2]
        values = [1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 
                  1, 4, 4, 8, 4, 10, 0]
        self._bag = []
        
        for i in range(len(frequency)):
            for _ in range(frequency[i]):
                tile = Tile(board, win, (0, 0), letters[i], values[i])
                self._bag.append(tile)
        
        self._win = win
        
    def dealPlayer(self):
        """Selects 7 random tiles to go to a player and removes them from the
        bag (list)"""
    
        playerTiles = []
        for _ in range(7):
            pick = self._bag[random.randrange(len(self._bag))]
            playerTiles.append(pick)
            self._bag.remove(pick)
        
        return playerTiles
        
    def refillTiles(self, playerTilesList):
        """Refills the player's tiles at the end of their turn"""
        
        #If there are less than seven tiles left in the bag:
        
        if len(self._bag) <= 7 - len(playerTilesList):
            for _ in range(len(self._bag)):
                pick = self._bag[random.randrange(len(self._bag))]
                playerTilesList.append(pick)
                self._bag.remove(pick)
                
        #If there are no tiles left aka the game is essentially over:
                
        if len(self._bag) == 0: 
            return None
            
        #If it is just a normal turn
        
        for _ in range(7 - len(playerTilesList)):
            pick = self._bag[random.randrange(len(self._bag))]
            playerTilesList.append(pick)
            self._bag.remove(pick)
        
class EndTurn(EventHandler):
    """This is a class for a button to press when it is time to switch turns 
    between players"""
    
    def __init__(self, win, board, center):
        EventHandler.__init__(self)
        self._center = center
        self._board = board
        self._win = win
        self._button = Rectangle(100, 30, self._center)
        self._button.setFillColor('#F44E26')
        self._label = Text('End turn', (self._center[0], 
                                        self._center[1] + 3), 15)
        self._label.setTextColor('white')
        self._button.addHandler(self)
        self._label.addHandler(self)
        self._win.add(self._button)
        self._win.add(self._label)
        
    def handleMouseRelease(self):
        self._board.changeTurn()
        
class DisplayScore:
    """A class that makes a scoreboard display for each player"""
    
    def __init__(self, number, center, win, board, name, nameSize):
        self._board = board
        self._win = win
        self._name = name
        self._nameSize = nameSize
        self._score = str(number)
        self._center = center
        self._display = Square(80, self._center)
        self._display.setFillColor('#86CAF9')
        self._label = Text(self._score, (self._center[0], 
                                         self._center[1] + 18), 30)
        self._nameLabel = Text(self._name, (self._center[0], \
        self._center[1] - 20), self._nameSize)
        self._win.add(self._display)
        self._win.add(self._label)
        self._win.add(self._nameLabel)
        
    def setScore(self, newText):
        """Changes the text that is displayed on the score board."""
        
        self._label.setText(newText)
        
class ResetTurn(EventHandler):
    """This class creates a button that players can press to take back their
    tiles before ending their turn if they make a mistake"""
    
    def __init__(self, win, board, center):
        EventHandler.__init__(self)
        self._win = win
        self._board = board
        self._center = center
        self._button = Rectangle(100, 30, self._center)
        self._button.setFillColor('#3A5AF9')
        self._label = Text('Reset', (self._center[0], self._center[1] + 3), 15)
        self._label.setTextColor('white')
        self._button.addHandler(self)
        self._label.addHandler(self)
        self._win.add(self._button)
        self._win.add(self._label)
    
    def handleMouseRelease(self):
        self._board.resetTurn()
        
class Player:
    """A class to create a player"""
    
    def __init__(self, board, win, name):
        self._board = board
        self._win = win
        self._name = name
        
    def getName(self):
        """Returns the player's name"""
        
        return self._name
        
class InvalidMove(EventHandler):
    """A warning that will appear when a player places tiles in an invalid place
    on the board"""
    
    def __init__(self, board, win):
        EventHandler.__init__(self)
        self._board = board
        self._win = win
        self._sign = Rectangle(300, 100, (200, 200))
        self._sign.setFillColor('black')
        self._warning = Text('Invalid Tile Placement', (200, 203), 25)
        self._warning.setTextColor('white')
        self._ok = Rectangle(50, 20, (320, 230))
        self._ok.setFillColor('white')
        self._okText = Text('ok', (320, 233), 15)
        self._ok.addHandler(self)
        self._okText.addHandler(self)
        
    def addWarning(self):
        """Adds the warning to the screen"""
        
        self._win.add(self._sign)
        self._sign.setDepth(0)
        self._win.add(self._warning)
        self._warning.setDepth(0)
        self._win.add(self._ok)
        self._ok.setDepth(0)
        self._win.add(self._okText)
        self._okText.setDepth(0)
        
    def removeWarning(self):
        """Removes the warning from the screen when clicked"""
    
        self._win.remove(self._sign)
        self._win.remove(self._warning)
        self._win.remove(self._ok)
        self._win.remove(self._okText)
    
    def handleMouseRelease(self):
        self.removeWarning()
    
def setupGame(win):
    """A function to set the game up for play"""
    board = Board(win)
    
StartGraphicsSystem(setupGame, 700, 600)
