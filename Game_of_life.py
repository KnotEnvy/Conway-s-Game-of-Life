import pygame
import numpy as np

pygame.init()
pygame.font.init()
pygame.mixer.init()
FONT = pygame.font.SysFont("comicsans", 30)
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE, pygame.DOUBLEBUF)
pygame.display.set_caption("Game of Life")

rows = 80
cols = 100
grid = np.zeros((rows, cols))
paused = False

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

def update(grid):
    new_grid = np.zeros((rows, cols))
    for row in range(rows):
        for col in range(cols):
            count = count_neighbors(grid, row, col)
            if grid[row][col] == 1:
                if count < 2 or count > 3:
                    new_grid[row][col] = 0
                else:
                    new_grid[row][col] = 1
            else:
                if count == 3:
                    new_grid[row][col] = 1
    return new_grid

def draw_grid():
    cell_width = WIDTH // cols
    cell_height = HEIGHT // rows
    grid_width = cell_width * cols
    grid_height = cell_height * rows

    for row in range(rows):
        for col in range(cols):
            x = col * cell_width
            y = row * cell_height
            if grid[row][col] == 1:
                color = (0, 255, 0)
            else:
                color = (0, 0, 0)
            pygame.draw.rect(screen, color, (x, y, cell_width - 1, cell_height - 1))
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, grid_width - 1, grid_height - 1), 1)

def handle_mouse_click(x, y):
    try:
        col = x // (WIDTH // cols)
        row = y // (HEIGHT // rows)
        grid[row][col] = not grid[row][col]
    except IndexError:
        print("Error: Click was outside the grid")

clock = pygame.time.Clock()

run = True
while run:
    clock.tick(5)
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            handle_mouse_click(x, y)

    if pygame.mouse.get_pressed()[0]:
        x, y = pygame.mouse.get_pos()
        handle_mouse_click(x, y)

    screen.fill((0, 0, 0))
    draw_grid()
    if not paused:
        grid = update(grid)

    pygame.display.update()


pygame.quit()


