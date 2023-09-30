import turtle
from typing import Callable
import random

CELL_SIZE = 20

frame_delay_ms = 1000 // 30

GRID_WIDTH = 1600
GRID_HEIGHT = 800

SCREEN_WIDTH = GRID_WIDTH + 30
SCREEN_HEIGHT = GRID_HEIGHT + 90

screen = turtle.getscreen()
screen.colormode(255)
screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
canvas = turtle.getcanvas()
turtle.hideturtle()

def on_motion(event):
    global mouse_x, mouse_y
    mouse_x = event.x - turtle.window_width() / 2
    mouse_y = -event.y + turtle.window_height() / 2

class Player:
    def __init__(self, index, color):
        self.index = index
        self.color = color
        self.name = "Player " + str(index+1)
        self.score = 0

class Item:
    def __init__(self, cx, cy, player: Player):
        self.player = player
        self.color = player.color
        self.valid = True

        self.t = turtle.Turtle()
        self.t.pen(pensize=1, speed=5)
        self.t.color(self.color)
        self.t.hideturtle()
        
        self.conf(cx, cy)


    def conf(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.w = self.cx * CELL_SIZE
        self.h = self.cy * CELL_SIZE
        self.x = 0
        self.y = 0

    def rotate(self):
        self.conf(self.cy, self.cx)
        self.draw_cursor_item()

    def draw_cursor_item(self):
        h = self.h
        w = self.w

        ix = mouse_x -w//2
        iy = mouse_y -h//2

        # print('ix', ix, 'iy', iy, '|', ix / CELL_SIZE, round(ix / CELL_SIZE))

        # ix -= ix % CELL_SIZE
        # iy -= iy % CELL_SIZE

        ix = round(ix / CELL_SIZE) * CELL_SIZE
        iy = round(iy / CELL_SIZE) * CELL_SIZE

        if ix < -GRID_WIDTH//2:
            ix = -GRID_WIDTH//2
        if ix > GRID_WIDTH//2 - w:
            ix = GRID_WIDTH//2 - w

        if iy < -GRID_HEIGHT//2:
            iy = - GRID_HEIGHT//2
        if iy > GRID_HEIGHT//2 - h:
            iy = GRID_HEIGHT//2 - h

        if ix == self.x and iy == self.y:
            return

        self.x = ix
        self.y = iy

        self.validate()

        self.t.clear()
        self.t.penup()
        self.t.pensize(2)

        self.t.color(self.color)

        y = iy

        while y <= iy + h:
            self.t.penup()
            self.t.goto(ix, y)
            self.t.pendown()
            self.t.goto(ix+w, y)
            y += CELL_SIZE
        
        x = ix

        while x <= ix + w:
            self.t.penup()
            self.t.goto(x, iy)
            self.t.pendown()
            self.t.goto(x, iy+h)
            x += CELL_SIZE

            
        self.t.color(self.color)
        self.t.pensize(3)
        self.drawSquare(ix, iy, w, h)
        
        if not self.valid:
            self.t.color(255, 0, 0)
            self.t.pensize(2)
            self.drawSquare(ix+3, iy+3, w-6, h-6)

    def drawSquare(self, ix, iy, w, h):
        self.t.penup()
        self.t.goto(ix, iy)
        self.t.pendown()
        self.t.goto(ix+w, iy)
        self.t.goto(ix+w, iy+h)
        self.t.goto(ix, iy+h)
        self.t.goto(ix, iy)
        self.t.penup()

    def playable(self):
        y = -GRID_HEIGHT//2

        while y < GRID_HEIGHT//2:
            x = -GRID_WIDTH//2
            while x < GRID_WIDTH//2:
                self.x = x
                self.y = y
                self.validate()
                if self.valid:
                    print('found valid position at ', x, y)
                    return True

                x += CELL_SIZE
            y += CELL_SIZE
        
        return False

    def validate(self):
        self.valid = self.isValid()
        
    def isValid(self):
        if self.x < -GRID_WIDTH//2 or self.x > GRID_WIDTH//2 - self.w:
            return False

        if self.y < -GRID_HEIGHT//2 or self.y > GRID_HEIGHT//2 - self.h:
            return False

        # on start of game
        if self.player.score == 0:
            if not self.touchingStartCorner():
             return False

        # verify that no other items are placed here
        if self.intersects():
            return False
        
        # verify that it is adjacent to existing item of current player
        if not self.touchingSamePlayer():
            return False
        
        return True
    
    def touchingStartCorner(self):
        for start_corner in start_corners:
            if self.intersectsLine(Line(start_corner[0], start_corner[1])) or self.intersectsLine(Line(start_corner[1], start_corner[2])):
                return True
            
    def intersectsLine(self, line):
        if line.a.x == self.x or self.x + self.w == line.a.x:
            y_start = line.a.y
            y_end = line.b.y
            if y_start > y_end:
                y_start = line.b.y
                y_end = line.a.y

            if y_start < self.y + self.h and self.y < y_end:
                return True
        
        if line.a.y == self.y or self.y + self.h == line.a.y:
            x_start = line.a.x
            x_end = line.b.x
            if x_start > x_end:
                x_start = line.b.x
                x_end = line.a.x

            if x_start < self.x + self.w and self.x < x_end:
                return True

        return False

    def intersects(self):
        for item in grid_items:
            # print('item x,y', item.x, item.y, ' | self x,y', self.x, self.y, ' w, h:' , self.w, self.h, 'cx, cy:', self.cx, self.cy, ' || item ->', item.x + item.w, ' <- self', self.x, ' ___ self ->', self.x + self.w, ' <- item.x', item.x)
            if item.x < self.x + self.w and self.x < item.x + item.w:
                if item.y < self.y + self.h and self.y < item.y + item.h:
                    return True
        return False
    
    def touchingSamePlayer(self):
        has_placed_items = False
        for item in grid_items:
            if item.player == self.player:
                has_placed_items = True
                if item.x == self.x + self.w or self.x == item.x + item.w:
                    if item.y < self.y + self.h and self.y < item.y + item.h:
                        return True
                if item.y == self.y + self.h or self.y == item.y + item.h:
                    if item.x < self.x + self.w and self.x < item.x + item.w:
                        return True
        if has_placed_items:
            return False
        return True

class Point:
    def __init__(self,x,y):
        self.x=x
        self.y=y

class Line:
    def __init__(self,a,b):
        self.a=a
        self.b=b

players = []

playing_players = []

players_colors = [(121,171,142), (254,201,124), (46,141,223), (117,41,187)]

current_player = None

grid_items = []

current_item = None

rows, cols = (GRID_HEIGHT // CELL_SIZE, GRID_WIDTH // CELL_SIZE)

print('rows', rows)
print('cols', cols)

grid = turtle.Turtle()
grid.hideturtle()

def draw_grid():
    grid.clear()
    grid.pen(pensize=1, speed=11, shown=True)
    grid.color(184,202,225)
    grid.hideturtle()

    h = GRID_HEIGHT
    w = GRID_WIDTH

    y = -h//2

    while y <= h//2:
        grid.penup()
        grid.goto(-w/2, y)
        grid.pendown()
        grid.goto(w/2, y)
        y += CELL_SIZE
    
    x = -w//2

    while x <= w//2:
        grid.penup()
        grid.goto(x, -h//2)
        grid.pendown()
        grid.goto(x, h//2)
        x += CELL_SIZE
    
    screen.update()



start_corners = []

def set_start_corners():
    global start_corners
    offset = CELL_SIZE*6*2

    start_corners = [[], [], [], []]

    start_corners[0].append(Point(-GRID_WIDTH//2, GRID_HEIGHT//2 - offset))
    start_corners[0].append(Point(-GRID_WIDTH//2, GRID_HEIGHT//2))
    start_corners[0].append(Point(-GRID_WIDTH//2 + offset, GRID_HEIGHT//2))

    start_corners[1].append(Point(GRID_WIDTH//2, GRID_HEIGHT//2 - offset))
    start_corners[1].append(Point(GRID_WIDTH//2, GRID_HEIGHT//2))
    start_corners[1].append(Point(GRID_WIDTH//2 - offset, GRID_HEIGHT//2))

    start_corners[2].append(Point(GRID_WIDTH//2, -GRID_HEIGHT//2 + offset))
    start_corners[2].append(Point(GRID_WIDTH//2, -GRID_HEIGHT//2))
    start_corners[2].append(Point(GRID_WIDTH//2 - offset, -GRID_HEIGHT//2))

    start_corners[3].append(Point(-GRID_WIDTH//2, -GRID_HEIGHT//2 + offset))
    start_corners[3].append(Point(-GRID_WIDTH//2, -GRID_HEIGHT//2))
    start_corners[3].append(Point(-GRID_WIDTH//2 + offset, -GRID_HEIGHT//2))
    
    
corner = turtle.Turtle()
corner.hideturtle()

def draw_start_corners():
    corner.clear()
    # corner.color('#38b000')
    corner.color(current_player.color)
    corner.pensize(3)

    for start_corner in start_corners:
        corner.penup()
        corner.goto(start_corner[0].x, start_corner[0].y)
        corner.pendown()
        corner.goto(start_corner[1].x, start_corner[1].y)
        corner.goto(start_corner[2].x, start_corner[2].y)

    corner.penup()
    screen.update()


def remove_start_corner(item):
    global start_corners
    #find which corner matches
    for start_corner in start_corners:
        if item.intersectsLine(Line(start_corner[0], start_corner[1])) or item.intersectsLine(Line(start_corner[1], start_corner[2])):
            start_corners.remove(start_corner)
            break
    
    starting_players = 0

    for player in playing_players:
        if player.score == 0:
            starting_players += 1
    
    if starting_players == 0:
        start_corners = []
        corner.clear()
    

def next_player():
    global current_player
    index = playing_players.index(current_player)
    index += 1
    if index >= len(playing_players):
        index = 0
    current_player = playing_players[index]

def play_next_shape():
    global current_item
    current_item = None

    next_item = Item(random.randint(1,6), random.randint(1,6), current_player)

    # check if the player is able to place this shape
    if not next_item.playable():
        # print('this player has lost!')
        lost_player = current_player
        draw_player_lost(lost_player)
        next_player()
        playing_players.remove(lost_player)
        
        # if only one player left then he won!
        if len(playing_players) == 1:
            # print('player', playing_players[0].index, ' WON!')
            draw_player_win()
            return
        
        play_next_shape()
        return

    def set_next_shape():
        global current_item
        current_item = next_item
    
    screen.ontimer(set_next_shape, 1000)

    draw_player_turn()
    
    draw_start_corners()
    

def try_place_item():
    if current_item and current_item.valid:
        grid_items.append(current_item)
        if current_player.score == 0:
            remove_start_corner(current_item)
        current_player.score += current_item.cx * current_item.cy
        next_player()
        play_next_shape()
        draw_header()


def rotate_item():
    current_item.rotate()


def game_tick():
    # print(mouse_x, mouse_y)
    
    # screen.clear()
    if current_item:
        current_item.draw_cursor_item()

    # screen.update()
    screen.ontimer(game_tick, frame_delay_ms)


header = turtle.Turtle()
header.hideturtle()

def draw_header():
    x = -SCREEN_WIDTH//2 + 15

    FONT_SIZE = 16
    FONT = ('Arial', FONT_SIZE, 'normal')

    header.clear()
    header.hideturtle()
    header.penup()

    for player in players:
        header.goto(x, SCREEN_HEIGHT//2 - 40)
        header.color(player.color)
        header.write(player.name+": "+str(player.score), align='left', font=FONT)
        x += 200


player_win = turtle.Turtle()
player_win.hideturtle()

def draw_player_win():
    won_player = players[0]

    won_player.score += 6*6*4

    for player in players:
        if player.score > won_player.score:
            won_player = player

    player_win.clear()
    player_win.hideturtle()
    player_win.penup()

    FONT_SIZE = 34
    FONT = ('Arial', FONT_SIZE, 'normal')

    player_win.goto(0, 200)
    player_win.color(won_player.color)
    player_win.write(won_player.name+" WINS!", align='center', font=FONT)
    screen.update()


player_turn = turtle.Turtle()
player_turn.hideturtle()

def draw_player_turn():
    player = current_player
    
    player_turn.clear()
    player_turn.hideturtle()
    player_turn.penup()

    FONT_SIZE = 30
    FONT = ('Arial', FONT_SIZE, 'normal')

    player_turn.goto(0, 200)
    player_turn.color(player.color)
    player_turn.write(player.name+"", align='center', font=FONT)
    screen.update()

    screen.ontimer(lambda:player_turn.clear(), 1000)
    

player_lost = turtle.Turtle()
player_lost.hideturtle()

def draw_player_lost(player):
    player_lost.clear()
    player_lost.hideturtle()
    player_lost.penup()

    FONT_SIZE = 30
    FONT = ('Arial', FONT_SIZE, 'normal')

    player_lost.goto(0, 300)
    player_lost.color(player.color)
    player_lost.write(player.name+" Lost!", align='center', font=FONT)
    screen.update()

    screen.ontimer(lambda:player_lost.clear(), 3000)
    


def draw_button(by: int, text: str, onClick: Callable):
    bx = 0
    bw = 200
    bh = 50

    FONT_SIZE = 26
    FONT = ('Arial', FONT_SIZE, 'normal')

    button = turtle.Turtle()
    button.penup()
    button.hideturtle()
    button.goto(bx - bw//2, by - bh//2)
    button.pendown()
    button.goto(bx + bw//2, by - bh//2)
    button.goto(bx + bw//2, by + bh//2)
    button.goto(bx - bw//2, by + bh//2)
    button.goto(bx - bw//2, by - bh//2)
    button.penup()

    buttonText = turtle.Turtle()
    buttonText.penup()
    buttonText.hideturtle()
    buttonText.goto(bx, by -FONT_SIZE/2)
    buttonText.write(text, align='center', font=FONT)

    def handle_click(x, y):
        # print('handle_click',x,y)
        if bx - bw//2 < x and x < bx + bw//2 and by - bh//2 < y and y < by + bh//2:
            # print('button clicked! ', text)
            onClick()
    
    screen.onclick(handle_click, add=True)


def start_game(num_of_players: int):
    global current_player, playing_players
    print('STARTING GAME with ', num_of_players, 'players')
    screen.clear()
    screen.tracer(False)
    screen.colormode(255)

    # add players
    i = 0
    while i < num_of_players:
        players.append(Player(i, players_colors[i]))
        i += 1
    
    playing_players = []
    for player in players:
        playing_players.append(player)

    current_player = playing_players[0]

    draw_grid()

    set_start_corners()

    play_next_shape()

    draw_header()

    game_tick()

    def handle_game_click(x, y):
        try_place_item()

    screen.onclick(handle_game_click, add=True)
    screen.onkey(rotate_item, 'space')
    screen.listen()


screen = turtle.Screen()
screen.tracer(False)
# turtle.tracer(0, 0)

mouse_x, mouse_y = 0, 0

turtle.getcanvas().bind("<Motion>", on_motion)

screen.update()

draw_button(70, '2 Players', lambda: start_game(2))
draw_button(0, '3 Players', lambda: start_game(3))
draw_button(-70, '4 Players', lambda: start_game(4))

screen.mainloop()