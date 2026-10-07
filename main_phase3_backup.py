import pygame
import re
import math
import random

# ============================================================
# AI ROBOT COMMANDER - Colorful Skill Expo Edition
# No external image files required: everything is drawn in pygame.
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1280, 780
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Robot Commander")
clock = pygame.time.Clock()

# ---------- Colors ----------
WHITE = (255, 255, 255)
BLACK = (25, 35, 55)
NAVY = (17, 55, 110)
BLUE = (30, 125, 235)
SKY = (105, 215, 250)
CYAN = (55, 205, 245)
GREEN = (83, 205, 75)
DARK_GREEN = (35, 145, 70)
LIME = (145, 230, 70)
RED = (235, 72, 65)
ORANGE = (255, 150, 55)
YELLOW = (255, 205, 55)
PURPLE = (135, 90, 220)
LIGHT_BLUE = (224, 245, 255)
PANEL = (244, 250, 255)
GRAY = (100, 115, 135)
LIGHT_GRAY = (225, 232, 240)
BRICK = (220, 70, 45)
BRICK_DARK = (155, 48, 38)

font_big = pygame.font.SysFont("arial", 30, bold=True)
font_title = pygame.font.SysFont("arial", 42, bold=True)
font_subtitle = pygame.font.SysFont("arial", 21, bold=True)
font_medium = pygame.font.SysFont("arial", 19, bold=True)
font_small = pygame.font.SysFont("arial", 16)
font_tiny = pygame.font.SysFont("arial", 14)

# ---------- Layout ----------
HEADER_H = 92
LEFT_X, LEFT_W = 25, 275
WORLD_X, WORLD_Y = 320, 120
WORLD_W, WORLD_H = 660, 575
RIGHT_X, RIGHT_W = 1000, 255
INPUT_Y = 710

# ---------- Game grid ----------
ROWS, COLS = 8, 9
CELL = 68
GRID_X = WORLD_X + 25
GRID_Y = WORLD_Y + 35

start_cell = [0, 0]
target_cell = [7, 8]

# Obstacles are grid cells
obstacles = {
    (1, 5), (2, 5), (3, 5),
    (4, 2), (4, 3), (4, 4), (4, 5),
    (5, 7), (6, 7), (3, 7), (2, 7),
}

robot_row, robot_col = start_cell
direction = "right"

score = 0
command_text = ""
history = []
learning_input = "Waiting for command..."
learning_direction = "-"
learning_action = "-"
learning_result = "Waiting..."

message = "Give the robot a command!"
message_timer = 0

# ---------- Drawing helpers ----------
def rounded(surface, rect, color, radius=18, border=None, width=2):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)

def text(txt, x, y, font=font_small, color=BLACK):
    surface = font.render(str(txt), True, color)
    screen.blit(surface, (x, y))
    return surface.get_rect(topleft=(x, y))

def centered(txt, rect, font=font_small, color=BLACK):
    surface = font.render(str(txt), True, color)
    screen.blit(surface, surface.get_rect(center=rect.center))

def draw_gradient_background():
    # Soft blue gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(75 + 70 * t)
        g = int(195 + 35 * t)
        b = int(245 + 10 * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Decorative clouds
    for cx, cy, s in [(70, 135, 1), (1110, 120, 1.2), (1210, 300, .8)]:
        pygame.draw.circle(screen, WHITE, (int(cx), int(cy)), int(25*s))
        pygame.draw.circle(screen, WHITE, (int(cx+30*s), int(cy-10*s)), int(32*s))
        pygame.draw.circle(screen, WHITE, (int(cx+60*s), int(cy)), int(24*s))
        pygame.draw.rect(screen, WHITE,
                         (int(cx-10*s), int(cy), int(80*s), int(25*s)))

def draw_header():
    pygame.draw.rect(screen, NAVY, (0, 0, WIDTH, HEADER_H))
    pygame.draw.rect(screen, BLUE, (0, HEADER_H-7, WIDTH, 7))

    # Small robot logo
    draw_robot(70, 47, 0.55, happy=True)

    text("AI", 125, 25, font_title, YELLOW)
    text("ROBOT COMMANDER", 190, 22, font_title, WHITE)
    text("Can You Give AI the Right Command?", 660, 31, font_subtitle, LIGHT_BLUE)

    # Score pill
    rounded(screen, (1060, 18, 195, 56), (10, 42, 85), 28)
    draw_star(1092, 46, 20, YELLOW)
    text(f"Score: {score}", 1120, 29, font_medium, WHITE)

def draw_star(cx, cy, r, color):
    points = []
    for i in range(10):
        a = -math.pi/2 + i * math.pi/5
        rr = r if i % 2 == 0 else r * .42
        points.append((cx + math.cos(a)*rr, cy + math.sin(a)*rr))
    pygame.draw.polygon(screen, color, points)
    pygame.draw.polygon(screen, (255, 175, 20), points, 2)

def draw_robot(cx, cy, scale=1.0, happy=False):
    # Antenna
    pygame.draw.line(screen, BLACK,
                     (cx, cy-int(55*scale)),
                     (cx, cy-int(80*scale)), max(2, int(4*scale)))
    pygame.draw.circle(screen, ORANGE,
                       (cx, cy-int(83*scale)), int(8*scale))

    # Head
    head = pygame.Rect(
        cx-int(48*scale), cy-int(55*scale),
        int(96*scale), int(70*scale)
    )
    rounded(screen, head, WHITE, int(18*scale), NAVY, max(2, int(3*scale)))

    # Face screen
    face = pygame.Rect(
        cx-int(36*scale), cy-int(43*scale),
        int(72*scale), int(42*scale)
    )
    rounded(screen, face, (20, 45, 85), int(12*scale))

    # Eyes
    pygame.draw.circle(screen, CYAN,
                       (cx-int(20*scale), cy-int(22*scale)),
                       int(7*scale))
    pygame.draw.circle(screen, CYAN,
                       (cx+int(20*scale), cy-int(22*scale)),
                       int(7*scale))

    # Smile
    if happy:
        pygame.draw.arc(screen,
                        CYAN,
                        (cx-int(20*scale), cy-int(12*scale),
                         int(40*scale), int(20*scale)),
                        0.15, math.pi-0.15, max(2, int(3*scale)))

    # Ears
    pygame.draw.circle(screen, BLUE,
                       (cx-int(53*scale), cy-int(15*scale)),
                       int(11*scale))
    pygame.draw.circle(screen, BLUE,
                       (cx+int(53*scale), cy-int(15*scale)),
                       int(11*scale))

    # Body
    body = pygame.Rect(
        cx-int(38*scale), cy+int(17*scale),
        int(76*scale), int(65*scale)
    )
    rounded(screen, body, WHITE, int(15*scale), NAVY, max(2, int(3*scale)))

    # Chest
    pygame.draw.circle(screen, CYAN,
                       (cx, cy+int(48*scale)), int(16*scale))
    pygame.draw.circle(screen, WHITE,
                       (cx, cy+int(48*scale)), int(7*scale))

    # Arms
    pygame.draw.line(screen, BLUE,
                     (cx-int(37*scale), cy+int(28*scale)),
                     (cx-int(58*scale), cy+int(58*scale)),
                     max(4, int(8*scale)))
    pygame.draw.line(screen, BLUE,
                     (cx+int(37*scale), cy+int(28*scale)),
                     (cx+int(58*scale), cy+int(12*scale)),
                     max(4, int(8*scale)))

    # Legs
    pygame.draw.line(screen, NAVY,
                     (cx-int(20*scale), cy+int(78*scale)),
                     (cx-int(28*scale), cy+int(100*scale)),
                     max(4, int(9*scale)))
    pygame.draw.line(screen, NAVY,
                     (cx+int(20*scale), cy+int(78*scale)),
                     (cx+int(28*scale), cy+int(100*scale)),
                     max(4, int(9*scale)))

def draw_panel(x, y, w, h, title_text, color=WHITE):
    rounded(screen, (x, y, w, h), color, 18, (40, 120, 190), 2)
    rounded(screen, (x, y, w, 48), NAVY, 18)
    # square off lower corners of header
    pygame.draw.rect(screen, NAVY, (x, y+25, w, 23))
    text(title_text, x+18, y+12, font_medium, WHITE)

def draw_left_panel():
    # Instruction card
    rounded(screen, (LEFT_X, 115, LEFT_W, 112), LIGHT_BLUE, 18, BLUE, 2)
    draw_robot(62, 168, .42, happy=True)
    text("Type a command", 105, 135, font_medium, NAVY)
    text("and press ENTER", 105, 163, font_medium, NAVY)
    text("Try natural language!", 105, 190, font_small, GRAY)

    # Examples
    draw_panel(LEFT_X, 240, LEFT_W, 190, "💡  Example Commands")
    examples = [
        "Go forward 2 steps",
        "Move right 1 step",
        "Turn left and move 2",
        "Robot go up",
    ]
    for i, item in enumerate(examples):
        pygame.draw.circle(screen, BLUE, (LEFT_X+25, 295+i*31), 4)
        text(item, LEFT_X+38, 285+i*31, font_small, NAVY)

    # Learning mode
    draw_panel(LEFT_X, 445, LEFT_W, 205, "🧠  AI LEARNING MODE")
    text("Input:", LEFT_X+18, 505, font_medium, NAVY)
    text(learning_input[:27], LEFT_X+72, 505, font_small, BLACK)

    text("Direction:", LEFT_X+18, 540, font_medium, NAVY)
    text(learning_direction, LEFT_X+100, 540, font_small, BLACK)

    text("Action:", LEFT_X+18, 575, font_medium, NAVY)
    text(learning_action[:20], LEFT_X+82, 575, font_small, BLACK)

    text("Result:", LEFT_X+18, 610, font_medium, NAVY)
    result_color = DARK_GREEN if "reached" in learning_result.lower() or "moved" in learning_result.lower() else BLACK
    text(learning_result[:25], LEFT_X+80, 610, font_small, result_color)

def draw_right_panel():
    draw_panel(RIGHT_X, 115, RIGHT_W, 350, "📋  COMMAND HISTORY")

    if not history:
        text("No commands yet.", RIGHT_X+20, 180, font_small, GRAY)
        text("Your commands will", RIGHT_X+20, 210, font_small, GRAY)
        text("appear here.", RIGHT_X+20, 235, font_small, GRAY)
    else:
        visible = history[-7:][::-1]
        for i, item in enumerate(visible):
            yy = 175 + i*40
            ok = item["ok"]
            pygame.draw.circle(screen, GREEN if ok else RED,
                               (RIGHT_X+25, yy+10), 11)
            centered("✓" if ok else "×",
                     pygame.Rect(RIGHT_X+16, yy+1, 18, 18),
                     font_tiny, WHITE)
            label = item["text"]
            if len(label) > 25:
                label = label[:22] + "..."
            text(label, RIGHT_X+45, yy-1, font_tiny, BLACK)
            text("OK" if ok else "INVALID",
                 RIGHT_X+45, yy+18, font_tiny,
                 DARK_GREEN if ok else RED)

    # Mascot area
    rounded(screen, (RIGHT_X, 485, RIGHT_W, 205), (220, 247, 255), 20, BLUE, 2)
    draw_robot(RIGHT_X+83, 585, .75, happy=True)

    # Speech bubble
    rounded(screen, (RIGHT_X+105, 510, 135, 70), WHITE, 18, BLUE, 2)
    text("Great!", RIGHT_X+125, 520, font_medium, NAVY)
    text("Keep going!", RIGHT_X+112, 550, font_small, BLUE)

def draw_world():
    # World shadow / frame
    rounded(screen, (WORLD_X, WORLD_Y, WORLD_W, WORLD_H),
            (230, 250, 255), 25, WHITE, 5)

    # Grass
    inner = pygame.Rect(GRID_X-15, GRID_Y-15,
                        COLS*CELL+30, ROWS*CELL+30)
    rounded(screen, inner, (130, 220, 85), 18)

    # Grid
    for r in range(ROWS):
        for c in range(COLS):
            x = GRID_X + c*CELL
            y = GRID_Y + r*CELL
            pygame.draw.rect(screen, (140, 225, 95),
                             (x, y, CELL, CELL))
            pygame.draw.rect(screen, (185, 240, 135),
                             (x, y, CELL, CELL), 1)

    # Decorative grass dots
    random.seed(4)
    for _ in range(50):
        c = random.randrange(COLS)
        r = random.randrange(ROWS)
        x = GRID_X+c*CELL+random.randrange(8, 60)
        y = GRID_Y+r*CELL+random.randrange(8, 60)
        pygame.draw.circle(screen, (105, 195, 75), (x, y), 2)

    # Start tile
    sx = GRID_X + start_cell[1]*CELL
    sy = GRID_Y + start_cell[0]*CELL
    rounded(screen, (sx+5, sy+5, CELL-10, CELL-10),
            (65, 180, 255), 10, WHITE, 3)
    rounded(screen, (sx+2, sy-32, 95, 28), BLUE, 12)
    text("START", sx+18, sy-28, font_small, WHITE)

    # Target tile
    tx = GRID_X + target_cell[1]*CELL
    ty = GRID_Y + target_cell[0]*CELL
    rounded(screen, (tx+5, ty+5, CELL-10, CELL-10),
            (165, 250, 105), 10, WHITE, 3)
    draw_target(tx+CELL//2, ty+CELL//2)

    # Obstacles
    for r, c in obstacles:
        x = GRID_X+c*CELL+7
        y = GRID_Y+r*CELL+7
        draw_brick_wall(x, y, CELL-14, CELL-14)

    # Robot
    rx = GRID_X + robot_col*CELL + CELL//2
    ry = GRID_Y + robot_row*CELL + CELL//2 + 2
    draw_robot(rx, ry, .42, happy=True)

def draw_brick_wall(x, y, w, h):
    rounded(screen, (x+5, y+7, w, h), (105, 70, 55), 7)
    rounded(screen, (x, y, w, h), BRICK, 6, BRICK_DARK, 2)

    brick_h = max(10, h//4)
    for row in range(4):
        yy = y + row*brick_h
        pygame.draw.line(screen, (245, 105, 65),
                         (x+3, yy), (x+w-3, yy), 2)
        offset = 0 if row % 2 == 0 else w//2
        for xx in range(x+offset, x+w, w//2):
            pygame.draw.line(screen, BRICK_DARK,
                             (xx, yy), (xx, yy+brick_h), 2)

def draw_target(cx, cy):
    pygame.draw.line(screen, (70, 55, 45),
                     (cx, cy-30), (cx, cy+22), 5)
    pygame.draw.polygon(screen, RED,
                        [(cx, cy-30), (cx+34, cy-20), (cx, cy-7)])
    pygame.draw.circle(screen, WHITE, (cx+8, cy-19), 8)
    pygame.draw.circle(screen, RED, (cx+8, cy-19), 4)
    pygame.draw.ellipse(screen, DARK_GREEN,
                        (cx-24, cy+18, 48, 14))

def draw_input():
    # Bottom command box
    rounded(screen, (320, INPUT_Y, 920, 58), WHITE, 28, BLUE, 3)

    # Small command icon
    pygame.draw.circle(screen, NAVY, (350, INPUT_Y+29), 17)
    centered(">", pygame.Rect(340, INPUT_Y+19, 20, 20), font_medium, WHITE)

    if command_text:
        text(command_text, 380, INPUT_Y+17, font_medium, BLACK)
    else:
        text("Enter your command here...", 380, INPUT_Y+17,
             font_medium, (145, 160, 180))

    # Enter button
    rounded(screen, (1080, INPUT_Y+5, 150, 48), BLUE, 24)
    text("ENTER", 1122, INPUT_Y+17, font_medium, WHITE)

def show_message(msg, duration=100):
    global message, message_timer
    message = msg
    message_timer = duration

def command_matches(cmd):
    global direction
    cmd = cmd.lower().strip()

    # Find a number; default is 1
    nums = re.findall(r"\d+", cmd)
    steps = int(nums[0]) if nums else 1
    steps = max(1, min(5, steps))

    # Direction
    if any(word in cmd for word in ["right", "east"]):
        move_dir = "right"
    elif any(word in cmd for word in ["left", "west"]):
        move_dir = "left"
    elif any(word in cmd for word in ["up", "north", "forward"]):
        move_dir = "up" if "up" in cmd or "north" in cmd else direction
    elif any(word in cmd for word in ["down", "south", "back"]):
        move_dir = "down"
    else:
        move_dir = None

    if move_dir is None:
        return None

    # A turn command changes the robot's facing direction.
    if "turn" in cmd:
        direction = move_dir

    # "forward" means current facing direction.
    if "forward" in cmd or "ahead" in cmd:
        move_dir = direction

    return move_dir, steps

def try_move(move_dir, steps):
    global robot_row, robot_col

    drdc = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1)
    }
    dr, dc = drdc[move_dir]

    moved = 0

    for _ in range(steps):
        nr = robot_row + dr
        nc = robot_col + dc

        if nr < 0 or nr >= ROWS or nc < 0 or nc >= COLS:
            return moved, "Boundary reached."

        if (nr, nc) in obstacles:
            return moved, "Obstacle ahead."

        robot_row, robot_col = nr, nc
        moved += 1

    return moved, "Moved successfully."

def process_command():
    global score, learning_input, learning_direction
    global learning_action, learning_result

    cmd = command_text.strip()
    if not cmd:
        return

    learning_input = cmd

    parsed = command_matches(cmd)

    if parsed is None:
        learning_direction = "-"
        learning_action = "Invalid command"
        learning_result = "Try: move right 2"
        history.append({"text": cmd, "ok": False})
        score = max(0, score - 1)
        show_message("I didn't understand that command.", 110)
        return

    move_dir, steps = parsed
    learning_direction = move_dir.upper()
    learning_action = f"Move {steps} step(s)"

    moved, result = try_move(move_dir, steps)

    if moved == steps:
        learning_result = "Robot moved!"
        history.append({"text": cmd, "ok": True})
        score += 10
        show_message("Command accepted! 🤖", 100)
    elif moved > 0:
        learning_result = result
        history.append({"text": cmd, "ok": True})
        score += moved * 5
        show_message("Partly completed.", 100)
    else:
        learning_result = result
        history.append({"text": cmd, "ok": False})
        score = max(0, score - 1)
        show_message(result, 100)

    # Target reached
    if [robot_row, robot_col] == target_cell:
        score += 50
        learning_result = "TARGET REACHED!"
        show_message("🎯 TARGET REACHED! +50 BONUS!", 180)

def draw_status_message():
    if message_timer <= 0:
        return
    box = pygame.Rect(WORLD_X+80, WORLD_Y+10, 500, 42)
    rounded(screen, box, (255, 250, 205), 18, ORANGE, 2)
    centered(message, box, font_small, NAVY)

# ---------- Main loop ----------
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_BACKSPACE:
                command_text = command_text[:-1]

            elif event.key == pygame.K_RETURN:
                process_command()
                command_text = ""

            elif event.unicode.isprintable():
                command_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # Click ENTER button
            if 1080 <= mx <= 1230 and INPUT_Y <= my <= INPUT_Y+58:
                process_command()
                command_text = ""

            # Click example commands
            if LEFT_X <= mx <= LEFT_X+LEFT_W and 275 <= my <= 415:
                index = (my - 275) // 31
                examples = [
                    "Go forward 2 steps",
                    "Move right 1 step",
                    "Turn left and move 2",
                    "Robot go up",
                ]
                if 0 <= index < len(examples):
                    command_text = examples[index]

    if message_timer > 0:
        message_timer -= 1

    # ---------- Draw ----------
    draw_gradient_background()
    draw_header()
    draw_left_panel()
    draw_world()
    draw_right_panel()
    draw_status_message()
    draw_input()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
