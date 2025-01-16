import pygame
import sys
import time

from minesweeper import Minesweeper, MinesweeperAI


def determine_mode(HEIGHT, WIDTH, MINES):
    if HEIGHT == 9 and WIDTH == 9 and 1 <= MINES <= 10:
        return 1
    elif HEIGHT == 16 and WIDTH == 16 and 1 <= MINES <= 40:
        return 2
    elif HEIGHT == 30 and WIDTH == 16 and 1 <= MINES <= 99:
        return 3
    elif HEIGHT <= 30 and WIDTH <= 24 and 1 <= MINES <= (HEIGHT - 1) * (WIDTH - 1):
        return 4

use_mines_map = input("是否要使用自訂的炸彈地圖?(Y/N)")

if use_mines_map == "Y":
    mines_map_path = input("請輸入炸彈地圖檔案位置：")

    # 從檔案中讀取地雷位置
    with open(mines_map_path, 'r') as file:
        lines = file.readlines()
        HEIGHT, WIDTH, MINES = map(int, lines[0].split())
        mines_positions = list(map(int, lines[1].split()))
        mode = determine_mode(HEIGHT, WIDTH, MINES)

elif use_mines_map == "N":
    # 模式選擇
    while True:
        print("請選擇一個模式：")
        print("0: 退出")
        print("1: 初學者模式 (9x9, 1 ≤ M ≤ 10)")
        print("2: 中級模式 (16x16, 1 ≤ M ≤ 40)")
        print("3: 專家模式 (30x16, 1 ≤ M ≤ 99)")
        print("4: 自訂模式 (H, W, 1 ≤ M ≤ (H-1)*(W-1))")
        
        mode = int(input("輸入模式 (0-4): "))

        if mode == 0:
            sys.exit()  # 退出程式
        elif mode == 1:
            HEIGHT, WIDTH, MINES = 9, 9, int(input("請輸入地雷數量 (1-10): "))
        elif mode == 2:
            HEIGHT, WIDTH, MINES = 16, 16, int(input("請輸入地雷數量 (1-40): "))
        elif mode == 3:
            HEIGHT, WIDTH, MINES = 30, 16, int(input("請輸入地雷數量 (1-99): "))
        elif mode == 4:
            HEIGHT = int(input("請輸入高度 (最大30): "))
            WIDTH = int(input("請輸入寬度 (最大24): "))
            MINES = int(input(f"請輸入地雷數量 (1-{(HEIGHT-1)*(WIDTH-1)}): "))
        else:
            print("無效的模式，請重新選擇。")
            continue
        break

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
PINK = (255, 192, 203)
RED = (255, 0, 0)

# Create game(依據模式更改畫面大小)
pygame.init()
if mode == 1:
    size = width, height = 600, 400
elif mode == 2:
    size = width, height = 900, 600
elif mode == 3:
    size = width, height = 1200, 800
elif mode == 4:
    size = width, height = 1200, 800
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))
mine_red = pygame.image.load("assets/images/mine-red.png")
mine_red = pygame.transform.scale(mine_red, (cell_size, cell_size))

# Detonated mine
mine_detonated = None

# Create game and AI agent
if use_mines_map == "Y":
    game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, use_random=False, mines_positions=mines_positions)
else:
    game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, use_random=True, mines_positions=None)
ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
lost = False

# Show instructions initially
instructions = True

# Autoplay game
autoplay = False
autoplaySpeed = 0.3
makeAiMove = False

# Show Safe and Mine Cells
showInference = False

while True:

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)

    # Show game instructions
    if instructions:

        # Title
        title = largeFont.render("Play Minesweeper", True, WHITE)
        titleRect = title.get_rect()
        titleRect.center = ((width / 2), 50)
        screen.blit(title, titleRect)

        # Rules
        rules = [
            "Click a cell to reveal it.",
            "Right-click a cell to mark it as a mine.",
            "Mark all mines successfully to win!"
        ]
        for i, rule in enumerate(rules):
            line = smallFont.render(rule, True, WHITE)
            lineRect = line.get_rect()
            lineRect.center = ((width / 2), 150 + 30 * i)
            screen.blit(line, lineRect)

        # Play game button
        buttonRect = pygame.Rect((width / 4), (3 / 4) * height, width / 2, 50)
        buttonText = mediumFont.render("Play Game", True, BLACK)
        buttonTextRect = buttonText.get_rect()
        buttonTextRect.center = buttonRect.center
        pygame.draw.rect(screen, WHITE, buttonRect)
        screen.blit(buttonText, buttonTextRect)

        # Check if play button clicked
        click, _, _ = pygame.mouse.get_pressed()
        if click == 1:
            mouse = pygame.mouse.get_pos()
            if buttonRect.collidepoint(mouse):
                instructions = False
                time.sleep(0.3)

        pygame.display.flip()
        continue

    # Draw board
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            # Add a mine, flag, or number if needed
            if game.is_mine((i, j)) and lost:
                if (i,j) == mine_detonated:
                    screen.blit(mine_red, rect)
                else:
                    screen.blit(mine, rect)
            elif (i, j) in flags:
                screen.blit(flag, rect)
            elif (i, j) in revealed:
                neighbors = smallFont.render(
                    str(game.nearby_mines((i, j))),
                    True, BLACK
                )
                neighborsTextRect = neighbors.get_rect()
                neighborsTextRect.center = rect.center
                screen.blit(neighbors, neighborsTextRect)
            elif (i, j) in ai.safes and showInference:
                pygame.draw.rect(screen, PINK, rect)
                pygame.draw.rect(screen, WHITE, rect, 3)
            elif (i, j) in ai.mines and showInference:
                pygame.draw.rect(screen, RED, rect)
                pygame.draw.rect(screen, WHITE, rect, 3)
            row.append(rect)
        cells.append(row)

    # Autoplay Button
    autoplayBtn = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    bText = "Autoplay" if not autoplay else "Stop"
    buttonText = mediumFont.render(bText, True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = autoplayBtn.center
    pygame.draw.rect(screen, WHITE, autoplayBtn)
    screen.blit(buttonText, buttonRect)

    # AI Move button
    aiButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING + 70,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("AI Move", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    if not autoplay:
        pygame.draw.rect(screen, WHITE, aiButton)
        screen.blit(buttonText, buttonRect)

    # Reset button
    resetButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING + 140,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Reset", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    if not autoplay:
        pygame.draw.rect(screen, WHITE, resetButton)
        screen.blit(buttonText, buttonRect)

    # Display text
    text = "Lost" if lost else "Won" if game.mines == flags else ""
    text = mediumFont.render(text, True, WHITE)
    textRect = text.get_rect()
    textRect.center = ((5 / 6) * width, BOARD_PADDING + 232)
    screen.blit(text, textRect)

    # Show Safes and Mines button
    safesMinesButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, BOARD_PADDING + 280,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    bText = "Show Inference" if not showInference else "Hide Inference"
    buttonText = smallFont.render(bText, True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = safesMinesButton.center
    if not autoplay:
        pygame.draw.rect(screen, WHITE, safesMinesButton)
        screen.blit(buttonText, buttonRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Check for a right-click to toggle flagging
    if right == 1 and not lost and not autoplay:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    if (i, j) in flags:
                        flags.remove((i, j))
                    else:
                        flags.add((i, j))
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # If Autoplay button clicked, toggle autoplay
        if autoplayBtn.collidepoint(mouse):
            if not lost:
                autoplay = not autoplay
            else:
                autoplay = False
            time.sleep(0.2)
            continue

        # If AI button clicked, make an AI move
        elif aiButton.collidepoint(mouse) and not lost:
            makeAiMove = True
            time.sleep(0.2)

        # Reset game state
        elif resetButton.collidepoint(mouse):

            if use_mines_map == "Y":
                game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, use_random=False, mines_positions=mines_positions)
            else:
                game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES, use_random=True, mines_positions=None)
            ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed = set()
            flags = set()
            lost = False
            mine_detonated = None
            continue

        # If Inference button clicked, toggle showInference
        elif safesMinesButton.collidepoint(mouse):
            showInference = not showInference
            time.sleep(0.2)

        # User-made move
        elif not lost:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # If autoplay, make move with AI
    if autoplay or makeAiMove:
        if makeAiMove:
            makeAiMove = False
        move = ai.make_safe_move()
        if move is None:
            move = ai.make_random_move()
            if move is None:
                flags = ai.mines.copy()
                print("No moves left to make.")
                autoplay = False
            else:
                print("No known safe moves, AI making random move.")
        else:
            print("AI making safe move.")

        # Add delay for autoplay
        if autoplay:
            time.sleep(autoplaySpeed)

    # Make move and update AI knowledge
    if move:
        if game.is_mine(move):
            lost = True
            mine_detonated = move
            autoplay = False
        else:
            nearby = game.nearby_mines(move)
            revealed.add(move)
            ai.add_knowledge(move, nearby)

    pygame.display.flip()
