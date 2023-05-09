import pygame
import numpy as np
import random
from numba import njit

pygame.init()
pygame.font.init()
pygame.mixer.init()
FONT = pygame.font.SysFont("comicsans", 30)
WIDTH, HEIGHT = 1280, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE, pygame.DOUBLEBUF)
pygame.display.set_caption("Game of Life")

CELL_NUMBER = 1000

rows = 125
cols = 100
grid = np.zeros((rows, cols))
ages = np.zeros((rows, cols))
paused = False

@njit
def count_neighbors(grid, row, col):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            r = (row + i + rows) % rows
            c = (col + j + cols) % cols
            count += grid[r][c]
    return count

@njit
def update(grid, ages):
    new_grid = np.zeros((rows, cols))
    new_ages = np.zeros((rows, cols))
    for row in range(rows):
        for col in range(cols):
            count = count_neighbors(grid, row, col)
            if grid[row][col] == 1:
                if count < 2 or count > 3:
                    new_grid[row][col] = 0
                    new_ages[row][col] = 0
                else:
                    new_grid[row][col] = 1
                    new_ages[row][col] = ages[row][col] + 1
            else:
                if count == 3:
                    new_grid[row][col] = 1
                    new_ages[row][col] = 1
                else:
                    new_ages[row][col] = 0
    return new_grid, new_ages

def draw_grid(generations_count):
    cell_width = WIDTH // cols
    cell_height = HEIGHT // rows
    grid_width = cell_width * cols
    grid_height = cell_height * rows

    colors = [
        (0, 255, 0),
        (255, 0, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (255, 165, 0),
        (128, 0, 128)
    ]

    for row in range(rows):
        for col in range(cols):
            x = col * cell_width
            y = row * cell_height
            if grid[row][col] == 1:
                age_group = int(min(ages[row][col] // 10, len(colors) - 1)) # Convert age_group to an integer
                color = colors[age_group]
                pygame.draw.rect(screen, color, (x, y, cell_width - 1, cell_height - 1))
            else:
                pygame.draw.rect(screen, (0, 0, 0), (x, y, cell_width - 1, cell_height - 1))
                

def handle_mouse_click(x, y):
    try:
        col = x // (WIDTH // cols)
        row = y // (HEIGHT // rows)
        grid[row][col] = not grid[row][col]
    except IndexError:
        print("Error: Click was outside the grid")
paused_time = 0
text_displayed = False
generations_count = 0
frame_count = 0
def draw_text():
    global paused_time
    global text_displayed
    if not paused:
        paused_time = 0
        if not text_displayed:
            font = pygame.font.SysFont("comicsans", 30)
            text = font.render("Press SPACE to pause and start placing cells with your mouse", True, (255, 255, 255))
            screen.blit(text, (10, 10))
            text = font.render("'R' restarts the cells and 'ESC' quits", True, (255, 255, 255))
            screen.blit(text, (10, 40))
            text = font.render("'B' places {} random cells on the board".format(CELL_NUMBER), True, (255, 255, 255))
            screen.blit(text, (10, 70))
    else:
        if not text_displayed:
            paused_time += clock.tick(30)
            alpha = max(0, 125 - paused_time // 10)
            if alpha == 0:
                text_displayed = True
            font = pygame.font.SysFont("comicsans", 30)
            text = font.render("Press SPACE to pause and start placing cells with your mouse", True, (255, 255, 255))
            text.set_alpha(alpha)
            screen.blit(text, (10, 10))
            text = font.render("'R' restarts the cells and 'ESC' quits", True, (255, 255, 255))
            text.set_alpha(alpha)
            screen.blit(text, (10, 40))
            text = font.render("'B' places {} random cells on the board".format(CELL_NUMBER), True, (255, 255, 255))
            text.set_alpha(alpha)
            screen.blit(text, (10, 70))

def place_random_cells(grid, num_cells):
    new_grid = grid.copy()
    for _ in range(num_cells):
        row = random.randint(0, rows - 1)
        col = random.randint(0, cols - 1)
        new_grid[row][col] = 1
    return new_grid

def draw_game_data(generations_count):
    alive_cells = int(np.sum(grid))
    dead_cells = rows * cols - alive_cells
    font = pygame.font.SysFont("comicsans", 30)
    text = font.render("Generations: {}".format(generations_count), True, (255, 255, 255))
    screen.blit(text, (10, HEIGHT - 70))
    text = font.render("Alive cells: {}".format(alive_cells), True, (255, 255, 255))
    screen.blit(text, (10, HEIGHT - 40))
    text = font.render("Dead cells: {}".format(dead_cells), True, (255, 255, 255))
    screen.blit(text, (10, HEIGHT - 10))


clock = pygame.time.Clock()
run = True
while run:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                grid.fill(0)
            elif event.key == pygame.K_b: # Press 'b' to place random cells
                grid = place_random_cells(grid, CELL_NUMBER)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            handle_mouse_click(x, y)

    if pygame.mouse.get_pressed()[0]:
        x, y = pygame.mouse.get_pos()
        handle_mouse_click(x, y)

    screen.fill((0, 0, 0))
    draw_grid(generations_count)
    draw_text()
    
    if not paused:
        frame_count += 10
        if frame_count % 1 == 0:
            generations_count += 1
            frame_count = 0
            grid, ages = update(grid, ages) # Unpack the returned tuple and provide ages as an argument

    draw_game_data(generations_count) # Move this function call outside the if not paused block

    pygame.display.update()


pygame.quit()


