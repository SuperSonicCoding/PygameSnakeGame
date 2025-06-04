import sys, pygame, random
from pygame import draw, Color, font, Rect, time

# Used to initialize everything for pygame.
pygame.init()

# Size of screen
size = width, height = 400, 425

# Size of grid
gridSize = width, height = 400, 400

# Difference vertically between size and gridSize, used so that grid will always be at bottom of screen
diff = size[1] - gridSize[1]

# White color
white = Color(255, 255, 255)

# Red color
red = Color(255, 0, 0)

# Green color
green = Color(0, 150, 0)

# Dark Green color
darkGreen = Color(0, 100, 0)

# Black color
black = Color(0 , 0, 0)

# Direction of snake
direction = [0, 0]

# Queued directions after button presses are made of arrow keys
queued_direction = direction.copy()

# Most recent positions of the snake head. This will be used so that the tail can follow the head
positions = []

# Each square of the snake excluding the head is within this list
#   Each square contains the Rectangle and current index within positions it should be reading off of
snake = []

# Speed of snake
#   The speed has to be a multiple of 20 so that the turning work with grid!!!
SPEED = 4

# Initial tail length. To be used when starting and restarting the game.
INITIAL_TAIL_LENGTH = 3

# Body increase on each apple.
INC_BODY = 1

# Number score will increase on each apple.
INC_SCORE = 1

# Initializes Screen surface
screen = pygame.display.set_mode(size)

# Status of apple on screen
appleSpawn = False

# Boolean for snake spawn
snakeSpawn = False

# Interval for grid
interval = size[0] / 20

# Square for drawing apple and snake pieces
square = interval, interval

# True if lost, false if haven't lost yet
lose = False

# True if won, false if haven't won yet
win = False

# Score during game
score = 0

# Tail length variable that will be increased by 1 each time an apple is collected
tailLength = INITIAL_TAIL_LENGTH

# Arrow key booleans
downKey = False
upKey = False
rightKey = False
leftKey = False

# Makes the end screen
#   title - text at top of end screen
#   question - yes or no question to be asked at end screen related to trying again (ex: "Try Again?")
def endScreenMaker(title, question):
    end = Rect(0, 0, size[0] / 2, size[1] / 4)
    end.center = (size[0] / 2, size[1] / 2)
    draw.rect(screen, white, end)
    endText = fontObj.render(title, False, black)
    finalScore = fontObj.render(f"Score: {score}", False, black)
    questionStatement = fontObj.render(question, False, black)
    yes = fontObj.render("Yes", False, black)
    no = fontObj.render("No", False, black)
    screen.blit(endText, textToRect(endText, end.center, end.top))
    screen.blit(finalScore, textToRect(finalScore, end.center, end.top + diff))
    screen.blit(questionStatement, textToRect(questionStatement, end.center, end.top + diff * 2))
    yesRect = textToRect(endText, end.center, end.top + diff * 3, end.left + diff)
    screen.blit(yes, yesRect)
    noRect = textToRect(endText, end.center, end.top + diff * 3, end.left + diff * 6)
    screen.blit(no, noRect)
    return yesRect, noRect

# Method for turning text to a Rectangle
#   This method was created to make placing text on screen easier by having the option of editing the center position.
#   text - text to be converted to a rectangle
#   center - coordinates for center of new rectangle
#   top - coordinates for top of new rectangle
#   left - coordinates for left of new rectangle
def textToRect(text, center, top, left=-1):
    rect = text.get_rect()
    rect.center = center
    rect.top = top
    if left != -1:
        rect.left = left
    return rect

# Restarts the game
def restart():
    # This line must be here to show that we want to edit the global variables. If not here, it will assume I am making new local variables.
    global lose, snakeSpawn, appleSpawn, direction, queued_direction, score, tailLength, positions
    lose = False
    snakeSpawn = False
    appleSpawn = False
    direction = [0, 0]
    queued_direction = direction.copy()
    score = 0
    tailLength = INITIAL_TAIL_LENGTH
    positions = []

# Game will run till the user quits
while True:
    # Caps the number of frames the game is. Without this the snake will move really fast... too fast.
    clockObj = pygame.time.Clock()
    clockObj.tick(60)

    # Used for when the player uses the red X on the top right. Need this loop for any while loop in PYGAME... I think.
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    
    # Have to fill it with black each time and redraw everything. That is how we get animation.
    screen.fill(black)

    # Creating the score header that states the current score of the game.
    fontObj = pygame.font.SysFont("Arial", 18)
    scoreText = fontObj.render(f"Score: {score}", False, white)
    screen.blit(scoreText, (0, 0))
    
    # Draws the grid based on interval and uses diff to put it at the bottom of the screen.
    for i in range(0, 20):
        draw.line(screen, white, [interval * i, diff], [interval * i, gridSize[1] + diff]) # vertical lines
        draw.line(screen, white, [0, interval * i + diff], [gridSize[0], interval * i + diff]) # horizontal lines

    # Spawns in the snake head. Only occurs when starting or restarting the game.
    if not snakeSpawn:
        # The snake head will be put in a random position.
        snakeCoords = random.randrange(0, gridSize[0], int(interval)), random.randrange(diff, gridSize[1] + diff, int(interval))
        snakeHead = Rect(snakeCoords, square)
        snakeSpawn = True

    # Creates new cooridnates for apple if not on screen from start or being taken by snake.
    if not appleSpawn:
        appleCoords = random.randrange(0, gridSize[0], int(interval)), random.randrange(diff, gridSize[1] + diff, int(interval))
        # If apple spawns on top of snake head or snake body, redo coordinates.
        while appleCoords == snakeCoords or list(appleCoords) in positions:
            appleCoords = random.randrange(0, gridSize[0], int(interval)), random.randrange(diff, gridSize[1] + diff, int(interval))
        appleSpawn = True

    # Makes apple and draws it onto the screen.
    apple = Rect(appleCoords, square)
    draw.rect(screen, red, apple)

    # Movement of snake
    # Boolean list of the keys that were pressed
    keys = pygame.key.get_pressed()
    # This variable is the exact coordinates starting on the top left of the grid. Used for turning.
    gridCoords = snakeHead.left, snakeHead.top - diff
    # Queues the changed direction depending on which key was pressed.
    if keys[pygame.K_DOWN]:
        queued_direction = [0, SPEED]
    elif keys[pygame.K_UP]:
        queued_direction = [0, -SPEED]
    elif keys[pygame.K_RIGHT]:
        queued_direction = [SPEED, 0]
    elif keys[pygame.K_LEFT]:
        queued_direction = [-SPEED, 0]
    # If the snake head is directly within a square, then change the direction to the queued direction.
    if gridCoords[0] % interval == 0 and gridCoords[1] % interval == 0:
        direction = queued_direction.copy()
    # Move the snake in the direction specified.
    snakeHead.move_ip(direction)

    # Handles when the snake head collides with the snake body.
    if list(snakeHead.topleft) in positions:
        lose = True

    # Adds to the recent position list only if the snake head is moving.
    if (direction[0] != 0 or direction[1] != 0):
        # Had to add diff to grid coords again for accurate placement
        positions.append([gridCoords[0], gridCoords[1] + diff])

    # Handles when the snake head reaches outside the grid / collides with the edges of the grid.
    if gridCoords[0] < 0 or gridCoords[0] > size[0] - 15 or gridCoords[1] < 0 or gridCoords[1] + 40 > size[1]:
        lose = True
            
    # Handles collision with apple
    if snakeHead.colliderect(apple):
        appleSpawn = False
        score += INC_SCORE
        tailLength += INC_BODY

    # Draws the snake head after it has spawned in or moved.
    draw.rect(screen, green, snakeHead)

    # Handles the body
    # Used to determine the indexes of each square in snake body.
    skip = int(interval / SPEED)
    # If the snake has started moving and the body of the snake isn't as long as what the tailLength specfies.
    if len(positions) > 0 and tailLength > len(snake):
        # Creates a new snake body square to add to snake list.
        snakeBody = Rect(positions[0], square)
        draw.rect(screen, darkGreen, snakeBody)
        body = {'body': snakeBody, 'index': 0 + len(snake) * skip}
        snake.append(body)
    #  For each snake body square in snake, draw it at the position that is specified by that specfic square's index.
    for i in snake:
        if len(positions) > i['index']:
            i['body'].topleft = positions[i['index']]
            # print(positions)
            draw.rect(screen, darkGreen, i['body'])
    # If length of positions exceeds the amount necessary for all of the current snake body squares, start popping from 0.
    if len(positions) >= skip * tailLength:
        positions.pop(0)

    if lose:
        # Makes the losing screen
        yesOrNo = endScreenMaker("You Lose!", "Try again?")
    
    # Handles unexpected win
    if tailLength == interval * interval - 1:
        yesOrNo = endScreenMaker("You Win!", "Play again?")

    # Shows changes.
    pygame.display.flip()

    # Handles the losing screen after it is made.
    while lose:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        # Boolean list of mouse buttons pressed.
        mouse = pygame.mouse.get_pressed()
        # If left click is pressed.
        if mouse[0]:
            # Get position of mouse at time of left click.
            pos = pygame.mouse.get_pos()
            # If hovering over 'Yes', restart the game.
            if yesOrNo[0].collidepoint(pos):
                restart()
            # If hovering over 'No', stop the game.
            if yesOrNo[1].collidepoint(pos):
                sys.exit()
    
    # Handles the winning screen after it is made.
    while win:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        mouse = pygame.mouse.get_pressed()
        if mouse[0]:
            pos = pygame.mouse.get_pos()
            if yesOrNo[0].collidepoint(pos):
                restart()
            if yesOrNo[1].collidepoint(pos):
                sys.exit()



    
# Goals:
#   Make other python files for current things (such as grid and snake body) and import them.

