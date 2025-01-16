import os
import glob
import math
import pygame
import time
import statistics
from minesweeper import Minesweeper, MinesweeperAI

# 定義顏色
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)


def draw_board(screen_width, screen_height, screen, game, revealed, mine_detonated, lost):
    # Compute board size
    BOARD_PADDING = 20
    board_width = ((2 / 3) * screen_width) - (BOARD_PADDING * 2)
    board_height = screen_height - (BOARD_PADDING * 2)
    cell_size = int(min(board_width / game.width, board_height / game.height))
    board_origin = (BOARD_PADDING, BOARD_PADDING)

    # Add images
    flag = pygame.image.load("assets/images/flag.png")
    flag = pygame.transform.scale(flag, (cell_size, cell_size))
    mine = pygame.image.load("assets/images/mine.png")
    mine = pygame.transform.scale(mine, (cell_size, cell_size))
    mine_red = pygame.image.load("assets/images/mine-red.png")
    mine_red = pygame.transform.scale(mine_red, (cell_size, cell_size))

    # Fonts
    OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
    smallFont = pygame.font.Font(OPEN_SANS, 20)
    mediumFont = pygame.font.Font(OPEN_SANS, 28)
    largeFont = pygame.font.Font(OPEN_SANS, 40)

    # Draw board
    cells = []
    for i in range(game.height):
        row = []
        for j in range(game.width):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Add a mine or number if needed
            if game.is_mine((i, j)) and lost:
                if (i,j) == mine_detonated:
                    screen.blit(mine_red, rect)
                else:
                    screen.blit(mine, rect)
            elif (i, j) in revealed:
                neighbors = smallFont.render(
                    str(game.nearby_mines((i, j))),
                    True, BLACK
                )
                neighborsTextRect = neighbors.get_rect()
                neighborsTextRect.center = rect.center
                screen.blit(neighbors, neighborsTextRect)
            row.append(rect)
        cells.append(row)

def calculate_entropy(counts, total_cells):
    entropy = 0
    for count in counts:
        if count > 0:
            probability = count / total_cells
            entropy -= probability * math.log2(probability)
    return entropy

def run_minesweeper_entropy_pygame(WIDTH, HEIGHT, mines, SN):
    total_cells = WIDTH * HEIGHT
    total_counts = []
    entropies = []

    # 初始化Pygame
    pygame.init()
    size = width, height = 1200, 800
    screen = pygame.display.set_mode(size)

    for _ in range(SN):
        game = Minesweeper(height=HEIGHT, width=WIDTH, mines=mines)
        ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
        revealed = set()
        lost = False
        mine_detonated = None

        while not lost:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            move = ai.make_safe_move()
            if move is None:
                move = ai.make_random_move()
                if move is None:
                    lost = False
                    break

            row, col = move
            revealed.add(move)

            if game.is_mine((row, col)):
                lost = True
                mine_detonated = move
            else:
                nearby = game.nearby_mines((row, col))
                ai.add_knowledge((row, col), nearby)

            draw_board(width, height, screen, game, revealed, mine_detonated, lost)
            pygame.display.flip()

        # 遊戲結束後，顯示所有地雷，並計算entropy
        counts = [0] * 10
        lost = True
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if game.is_mine((i, j)):
                    counts[9] += 1
                else:
                    nearby = game.nearby_mines((i, j))
                    counts[nearby] += 1
        draw_board(width, height, screen, game, revealed, mine_detonated, lost)
        pygame.display.flip()

        total_counts.append(counts)
        entropy = calculate_entropy(counts, total_cells)
        entropies.append(entropy)

    avg_counts = [sum(col) / len(col) for col in zip(*total_counts)]
    avg_entropy = sum(entropies) / SN
    std_counts = [statistics.stdev(col) for col in zip(*total_counts)]
    std_entropy = statistics.stdev(entropies)

    return total_counts, entropies, avg_counts, avg_entropy, std_counts, std_entropy

def main():
    choice = input("地雷位置? (1:隨機擺設, 2:檔案輸入)：")

    if choice == '1':
        WIDTH, HEIGHT, MINES, SN = map(int, input("地雷板寬度 高度 地雷個數 取樣次數：").split())
        total_counts, entropies, avg_counts, avg_entropy, std_counts, std_entropy = run_minesweeper_entropy_pygame(WIDTH, HEIGHT, MINES, SN)

        filename = f"../7-Entro/Entropy-{WIDTH:02d}-{HEIGHT:02d}-{MINES:03d}-{SN}.txt"
        with open(filename, 'w') as f:
            for i in range(SN):
                f.write(' '.join(f"{count}" for count in total_counts[i]) + f" {entropies[i]:.6f}\n")
            f.write(' '.join(f"{count:.2f}" for count in avg_counts) + f" {avg_entropy:.6f}\n")
            f.write(' '.join(f"{count:.2f}" for count in std_counts) + f" {std_entropy:.4f}\n")

    elif choice == '2':
        level_prefix = input("Game Level (例如: Mine1):")
        mine_positions_folder_path = "../2-Locat/"

        # 搜尋資料夾內符合條件的檔案
        file_pattern = os.path.join(mine_positions_folder_path, f"{level_prefix}*")
        file_list = sorted(glob.glob(file_pattern))

        total_counts = []
        entropies = []

        for file_index, filename in enumerate(file_list, start=1):

            with open(filename, 'r') as f:
                WIDTH, HEIGHT, MINES = map(int, f.readline().split())
                mine_positions = list(map(int, f.readline().split()))

            game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, use_random=False, mines_positions=mine_positions)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

            # 初始化Pygame
            pygame.init()
            size = width, height = 1200, 800
            screen = pygame.display.set_mode(size)

            revealed = set()
            lost = False
            mine_detonated = None

            while not lost:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    
                move = ai.make_safe_move()
                if move is None:
                    move = ai.make_random_move()
                    if move is None:
                        lost = False
                        break

                row, col = move
                revealed.add(move)

                if game.is_mine((row, col)):
                    lost = True
                    mine_detonated = move
                else:
                    nearby = game.nearby_mines((row, col))
                    ai.add_knowledge((row, col), nearby)

                draw_board(width, height, screen, game, revealed, mine_detonated, lost)
                pygame.display.flip()
                time.sleep(0.1)  # 添加延遲以便觀察

            # 遊戲結束後，顯示所有地雷
            counts = [0] * 10
            lost = True
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if game.is_mine((i, j)):
                        counts[9] += 1
                    else:
                        nearby = game.nearby_mines((i, j))
                        counts[nearby] += 1
            draw_board(width, height, screen, game, revealed, mine_detonated, lost)

            pygame.image.save(screen, f"../3-Marke/Mine_{WIDTH}_{HEIGHT}_{MINES}_Mark_{filename[-7:-4]}.png")

            pygame.display.flip()
            time.sleep(1) 

            total_counts.append(counts)
            entropy = calculate_entropy(counts, WIDTH * HEIGHT)
            entropies.append(entropy)

        avg_counts = [sum(col) / len(col) for col in zip(*total_counts)]
        avg_entropy = sum(entropies) / len(file_list)

        output_filename = f"../7-Entro/Entropy-{WIDTH:02d}-{HEIGHT:02d}-{MINES:03d}-{len(file_list)}.txt"
        with open(output_filename, 'w') as f:
            for i in range(len(file_list)):
                f.write(' '.join(f"{count}" for count in total_counts[i]) + f" {entropies[i]:.6f}\n")
            f.write(' '.join(f"{count:.2f}" for count in avg_counts) + f" {avg_entropy:.6f}\n")


if __name__ == "__main__":
    main()