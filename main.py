import pygame
import math
from queue import PriorityQueue

pygame.font.init()

WIDTH = 800;
WIN = pygame.display.set_mode((WIDTH, WIDTH));
pygame.display.set_caption("A* Path Finding Algorithm")
textfont = pygame.font.SysFont("monospace", 50);

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TURQUOISE
    
    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #Checking if spot downward is empty
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #Checking if spot upward is empty
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): #Checking if spot rightward is empty
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #Checking if spot leftward is empty
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def draw_text(text): 
    textTBD = textfont.render(text, 1, BLACK)
    text_rect= textTBD.get_rect(center=(WIDTH // 2, WIDTH // 2))
    WIN.blit(textTBD, text_rect)
    pygame.display.update()
    
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0 #Will store paths of equal f scores, and will be used to track priority in queue 
    open_set = PriorityQueue() #Create a priority queue under variable name open_set, finds the minimum element (built for that)
    open_set.put((0, count, start)) #open_set starts with one node which is start in position 1
    came_from = {} #came_from dictionary represents node we came from during the traversal
    g_score = {spot: float("inf") for row in grid for spot in row} #g_score stores the shortest distance from node spot to another spot
    g_score[start] = 0 #start node = 0
    f_score = {spot: float("inf") for row in grid for spot in row} #f_score stores the shortest distance from node spot to another node spot
    f_score[start] = h(start.get_pos(), end.get_pos()) #f_score for start uses function h to calculate the distance between nodes

    open_set_hash = {start} #dict that tells us whats in the open_set

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #while the open set is empty quit the game

        current = open_set.get()[2] #current stores the node associated with the minimum element
        open_set_hash.remove(current) 
        #Remove that node from the open set hash which basically 
        #stores the open_set in a more accessible structure

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True
        # If the the node in current is equal to node end, it means we have found the shortest path and ends
        
        for neighbor in current.neighbors: #looking at neighbors if current does not equal end to find the path
            temp_g_score = g_score[current] + 1
            # temp_g_score stores the g_score to that node in the iteration (plus 1 which includes that node as well)

            if temp_g_score < g_score[neighbor]: #so if the temp_g_score is less than g_score of the neighboring nodes, its the better path
                came_from[neighbor] = current #update that path in the dict
                g_score[neighbor] = temp_g_score #the g_score of the path to that node changes
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos()) # the f_score of the path to that node also changes
                if neighbor not in open_set_hash: #
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
                    # if that neighbouring node is not in the open_set_hash dict, it is added to the "path"
        
        draw()

        if current != start:
            current.make_closed()
            #Nodes essentially turn red when start node does not meet end node

    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    
    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows 
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(win, width):
    ROWS = 50
    
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True

    while run:
        draw(win, grid, ROWS, width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]: # left mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # right mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()

main(WIN, WIDTH)


