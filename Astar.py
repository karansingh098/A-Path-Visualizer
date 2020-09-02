import math
import pygame
from queue import PriorityQueue
pygame.init()

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

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

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        # all nodes start out as white in the grid, has not been looked at
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return (self.row, self.col)

    def is_closed(self):
        # red color indicates that the node has already been looked at
        return self.color == RED

    def is_open(self):
        # green color indicates it is open to look at
        return self.color == GREEN
    
    def is_barrier(self):
        # black color indicates barrier
        return self.color == BLACK
    
    def is_start(self):
        # orange color is start node
        return self.color == ORANGE
    
    def is_end(self):
        # turquoise color is end node
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
        # square grid
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # checking if row exists and if neighboring node is not a barrier
        # down
        if self.row < self.total_rows - 1 and not grid[self.row+1][self.col].is_barrier():
            self.neighbors.append(grid[self.row+1][self.col])
        # up
        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():
            self.neighbors.append(grid[self.row-1][self.col])
        # left
        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():
            self.neighbors.append(grid[self.row][self.col-1])
        # right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col+1].is_barrier():
            self.neighbors.append(grid[self.row][self.col+1])

# Manhattan distance(Shortest L), since you can't move diagonally in grid
def h_func(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def reconstruct_path(came_from, current, draw, start):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
    if current == start:
        current.make_start()

# taking draw function as a parameter
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    # inserting initial start node into the queue
    # parameters: f score, count to break ties, start is the node itself
    open_set.put((0, count, start))

    # dictionary keeping track of node relationships
    came_from = {}

    # creating g_score dictionary, node-g_score pairs
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0

    # creating f_score dictionary, node-f_score pairs
    f_score = {node: float("inf") for row in grid for node in row}
    # estimate of how far the end node is from the start
    f_score[start] = h_func(start.get_pos(), end.get_pos())

    # keep track of which items are and arent in the priority queue
    open_set_hash = {start}

    # algorithm runs until finding best path or if set is empty, path does not exist
    while not open_set.empty():
        # allowing user to quit in the middle of the algorithm
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # getting the minimum f_score node from the priority queue
        # synchronizing with hash table by removing the node
        current = open_set.get()[2]
        open_set_hash.remove(current)

        # shortest path found
        if current == end:
            reconstruct_path(came_from, end, draw, start)
            end.make_end()
            return True

        
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            # if better path was found, update
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h_func(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    # makes node green
                    neighbor.make_open()

        draw()
        # if node is not the start, and has been considered, close it
        if current != start:
            # makes node red
            current.make_closed()
        
    # path not found
    return False


# parameter width is width of grid
def make_grid(rows, width):
    grid = []
    node_width = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, node_width, rows)
            grid[i].append(node)

    return grid

def draw_grid(win, rows, width):
    node_width = width // rows
    for i in range(rows):
        # horizontal grid lines
        pygame.draw.line(win, GREY, (0, i * node_width), (width, i * node_width))

    for j in range(rows):
        # vertical grid lines
        pygame.draw.line(win, GREY, (j * node_width, 0), (j * node_width, width))

def draw(win, grid, rows, width):
    # draws white window every frame
    win.fill(WHITE)

    # loop through all nodes to draw them every frame
    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    # update display every frame
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    node_width = width // rows
    x, y = pos

    row = x // node_width
    col = y // node_width

    return (row, col)

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    # starting and ending nodes
    start = None
    end = None

    # variable to check status of program
    run = True
    started = False
    
    while run:
        draw(win, grid, ROWS, width)
        # checking for user events
        for event in pygame.event.get():
            # checking to see if X in corner of window is clicked
            if event.type == pygame.QUIT:
                run = False

            # if user clicked left mouse button
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                # getting node in 2-D list that was clicked on
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                # making sure that the start and end nodes are created
                if not start and node != end:
                    start = node
                    start.make_start()
                # making sure start and end cannot be on top of each other
                elif not end and end != start:
                    end = node
                    end.make_end()
                # if not start or end, then the node is a barrier
                elif node != start and node != end:
                    node.make_barrier()

            #if user clicked right mouse button
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                # getting node in 2-D list that was clicked on
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            # when user presses space bar, start the path finding algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    # anonymous function used to call draw within the algorithm function
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS,width)
    pygame.quit()

main(WIN, WIDTH)
