import pygame
import speech_recognition as sr
import threading
import queue
import re
import random

# ============================================================
# AI ROBOT COMMANDER - SKILL EXPO
# ============================================================

pygame.init()

WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI ROBOT COMMANDER - Skill Expo")
clock = pygame.time.Clock()

# Colors
BG = (235, 243, 250)
NAVY = (20, 45, 90)
BLUE = (45, 110, 220)
LIGHT_BLUE = (220, 235, 255)
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GREEN = (40, 180, 90)
DARK_GREEN = (20, 120, 60)
RED = (220, 65, 55)
DARK_RED = (145, 35, 35)
ORANGE = (245, 150, 40)
YELLOW = (255, 220, 60)
GRAY = (110, 120, 135)
LIGHT_GRAY = (225, 230, 235)
CYAN = (50, 190, 210)

# Fonts
font_title = pygame.font.SysFont("arial", 32, bold=True)
font_subtitle = pygame.font.SysFont("arial", 16)
font_big = pygame.font.SysFont("arial", 25, bold=True)
font_medium = pygame.font.SysFont("arial", 19, bold=True)
font_small = pygame.font.SysFont("arial", 15)
font_tiny = pygame.font.SysFont("arial", 12)

# Board coordinates
GAME_LEFT = 35
GAME_TOP = 105
GAME_RIGHT = 760
GAME_BOTTOM = 655
GRID_SIZE = 40

# Smaller robot
ROBOT_W = 26
ROBOT_H = 32
START_X = 80
START_Y = 160
robot_x = START_X
robot_y = START_Y

# Target
target_rect = pygame.Rect(690, 585, 42, 42)

# Maze obstacles. Gaps are intentionally left between barriers.
obstacles = [
    pygame.Rect(160, 120, 32, 112),
    pygame.Rect(240, 200, 160, 32),
    pygame.Rect(440, 120, 32, 112),
    pygame.Rect(520, 200, 120, 32),

    pygame.Rect(120, 280, 120, 32),
    pygame.Rect(320, 280, 32, 120),
    pygame.Rect(440, 320, 160, 32),
    pygame.Rect(640, 280, 32, 120),

    pygame.Rect(160, 400, 32, 112),
    pygame.Rect(240, 440, 160, 32),
    pygame.Rect(480, 400, 32, 112),
    pygame.Rect(560, 480, 120, 32),

    pygame.Rect(280, 560, 120, 32),
    pygame.Rect(400, 520, 32, 72),
]

# Game state
score = 0
command_history = []
status_message = "Give the robot a command!"
voice_status = "VOICE READY"
command_text = ""
target_reached = False
voice_listening = False
voice_queue = queue.Queue()

# Decorative grass/flowers generated once, avoiding walls/start/target.
random.seed(12)
grass_details = []

for _ in range(220):
    gx = random.randint(GAME_LEFT + 8, GAME_RIGHT - 10)
    gy = random.randint(GAME_TOP + 8, GAME_BOTTOM - 10)
    point = (gx, gy)

    if pygame.Rect(48, 122, 90, 85).collidepoint(point):
        continue
    if target_rect.inflate(18, 18).collidepoint(point):
        continue
    if any(wall.inflate(8, 8).collidepoint(point) for wall in obstacles):
        continue

    grass_details.append(
        (gx, gy, random.choice(("grass", "flower", "stone")))
    )


# ============================================================
# DRAWING
# ============================================================

def draw_header():
    pygame.draw.rect(screen, NAVY, (0, 0, WIDTH, 85))
    screen.blit(font_title.render("AI ROBOT COMMANDER", True, WHITE), (35, 16))
    screen.blit(
        font_subtitle.render("Can You Give AI the Right Command?", True, LIGHT_BLUE),
        (37, 53)
    )
    screen.blit(font_big.render("SKILL EXPO", True, YELLOW), (850, 25))


def draw_grass_board():
    board = pygame.Rect(
        GAME_LEFT, GAME_TOP,
        GAME_RIGHT - GAME_LEFT,
        GAME_BOTTOM - GAME_TOP
    )

    pygame.draw.rect(screen, (190, 230, 145), board, border_radius=16)

    # Subtle square grid
    for x in range(GAME_LEFT, GAME_RIGHT, GRID_SIZE):
        pygame.draw.line(
            screen, (165, 215, 125),
            (x, GAME_TOP), (x, GAME_BOTTOM), 1
        )
    for y in range(GAME_TOP, GAME_BOTTOM, GRID_SIZE):
        pygame.draw.line(
            screen, (165, 215, 125),
            (GAME_LEFT, y), (GAME_RIGHT, y), 1
        )

    # Small decorative ground details
    for x, y, kind in grass_details:
        if kind == "grass":
            pygame.draw.line(screen, (50, 135, 55), (x, y + 4), (x - 3, y - 3), 2)
            pygame.draw.line(screen, (60, 150, 60), (x, y + 4), (x + 4, y - 3), 2)
        elif kind == "flower":
            pygame.draw.circle(screen, (255, 255, 240), (x - 2, y), 3)
            pygame.draw.circle(screen, (255, 255, 240), (x + 2, y), 3)
            pygame.draw.circle(screen, (255, 220, 60), (x, y), 2)
        else:
            pygame.draw.ellipse(screen, (125, 135, 130), (x - 4, y - 2, 8, 5))

    pygame.draw.rect(screen, (90, 155, 70), board, 3, border_radius=16)


def draw_start():
    start_rect = pygame.Rect(48, 122, 90, 85)
    pygame.draw.rect(screen, (225, 250, 220), start_rect, border_radius=12)
    pygame.draw.rect(screen, GREEN, start_rect, 2, border_radius=12)
    screen.blit(font_small.render("START", True, DARK_GREEN), (72, 130))


def draw_robot():
    x, y = robot_x, robot_y

    # Shadow
    pygame.draw.ellipse(screen, (120, 160, 100), (x + 2, y + 27, 25, 7))

    # Legs
    pygame.draw.rect(screen, NAVY, (x + 5, y + 24, 6, 8), border_radius=2)
    pygame.draw.rect(screen, NAVY, (x + 16, y + 24, 6, 8), border_radius=2)

    # Arms
    pygame.draw.rect(screen, BLUE, (x - 3, y + 12, 5, 13), border_radius=2)
    pygame.draw.rect(screen, BLUE, (x + 24, y + 12, 5, 13), border_radius=2)

    # Body
    pygame.draw.rect(screen, BLUE, (x + 3, y + 16, 20, 12), border_radius=4)
    pygame.draw.rect(screen, NAVY, (x + 8, y + 19, 10, 6), border_radius=2)
    pygame.draw.circle(screen, GREEN, (x + 13, y + 22), 2)

    # Head
    pygame.draw.rect(screen, LIGHT_BLUE, (x + 2, y + 2, 22, 17), border_radius=5)
    pygame.draw.rect(screen, NAVY, (x + 2, y + 2, 22, 17), 1, border_radius=5)
    pygame.draw.circle(screen, CYAN, (x + 8, y + 9), 2)
    pygame.draw.circle(screen, CYAN, (x + 18, y + 9), 2)

    # Antenna
    pygame.draw.line(screen, NAVY, (x + 13, y + 2), (x + 13, y - 3), 2)
    pygame.draw.circle(screen, ORANGE, (x + 13, y - 4), 3)


def draw_obstacles():
    for wall in obstacles:
        shadow = wall.move(4, 5)
        pygame.draw.rect(screen, (120, 155, 105), shadow, border_radius=5)
        pygame.draw.rect(screen, RED, wall, border_radius=5)
        pygame.draw.rect(screen, DARK_RED, wall, 2, border_radius=5)

        # Brick detail
        if wall.width > wall.height:
            for bx in range(wall.x + 25, wall.right, 35):
                pygame.draw.line(
                    screen, DARK_RED,
                    (bx, wall.y + 3), (bx, wall.bottom - 3), 1
                )
            pygame.draw.line(
                screen, (255, 130, 100),
                (wall.x + 3, wall.y + wall.height // 2),
                (wall.right - 3, wall.y + wall.height // 2), 1
            )
        else:
            for by in range(wall.y + 25, wall.bottom, 30):
                pygame.draw.line(
                    screen, DARK_RED,
                    (wall.x + 3, by), (wall.right - 3, by), 1
                )


def draw_target():
    pygame.draw.rect(screen, (225, 255, 225), target_rect, border_radius=9)
    pygame.draw.rect(screen, GREEN, target_rect, 2, border_radius=9)
    cx, cy = target_rect.center

    pygame.draw.circle(screen, GREEN, (cx, cy), 13)
    pygame.draw.circle(screen, WHITE, (cx, cy), 7)
    pygame.draw.circle(screen, GREEN, (cx, cy), 3)

    pygame.draw.line(screen, DARK_GREEN, (cx + 10, cy - 12), (cx + 10, cy - 28), 2)
    pygame.draw.polygon(
        screen, RED,
        [(cx + 10, cy - 28), (cx + 25, cy - 23), (cx + 10, cy - 18)]
    )
    screen.blit(
        font_tiny.render("TARGET", True, DARK_GREEN),
        (target_rect.x - 2, target_rect.bottom + 3)
    )


def draw_side_panel():
    panel = pygame.Rect(785, 105, 280, 550)
    pygame.draw.rect(screen, WHITE, panel, border_radius=18)
    pygame.draw.rect(screen, LIGHT_GRAY, panel, 2, border_radius=18)

    screen.blit(font_medium.render("SCORE", True, NAVY), (810, 128))
    screen.blit(font_big.render(str(score), True, GREEN), (970, 123))
    screen.blit(font_small.render("LEVEL 2 - MAZE CHALLENGE", True, RED), (810, 164))

    voice_box = pygame.Rect(805, 195, 240, 70)
    pygame.draw.rect(screen, (235, 247, 255), voice_box, border_radius=12)
    pygame.draw.rect(screen, BLUE, voice_box, 2, border_radius=12)
    screen.blit(font_small.render("VOICE COMMAND", True, NAVY), (820, 207))
    voice_color = ORANGE if voice_listening else GREEN
    screen.blit(font_small.render(voice_status, True, voice_color), (820, 233))

    screen.blit(font_medium.render("COMMAND HISTORY", True, NAVY), (810, 285))
    history_box = pygame.Rect(805, 315, 240, 150)
    pygame.draw.rect(screen, (248, 250, 252), history_box, border_radius=10)

    y = 328
    for item in command_history[-6:]:
        shown = item if len(item) <= 28 else item[:25] + "..."
        screen.blit(font_tiny.render("• " + shown, True, BLACK), (815, y))
        y += 22

    screen.blit(font_medium.render("HOW TO PLAY", True, NAVY), (810, 485))
    instructions = [
        "V = Voice command",
        "ENTER = Typed command",
        "R = Reset robot",
        "",
        "Try these commands:",
        "Go forward two steps",
        "Move left one step",
        "Move right three steps",
        "Go backward one step"
    ]
    y = 514
    for line in instructions:
        screen.blit(
            font_tiny.render(line, True, GRAY if not line else BLACK),
            (815, y)
        )
        y += 15


def draw_command_area():
    area = pygame.Rect(35, 675, 1030, 55)
    pygame.draw.rect(screen, WHITE, area, border_radius=12)
    pygame.draw.rect(screen, BLUE, area, 2, border_radius=12)

    screen.blit(font_small.render("COMMAND:", True, NAVY), (50, 692))

    visible_text = command_text[-72:]
    screen.blit(font_small.render(visible_text, True, BLACK), (150, 692))

    status_color = GREEN if target_reached else GRAY
    status = font_tiny.render(status_message, True, status_color)
    screen.blit(status, status.get_rect(right=1045, centery=704))


# ============================================================
# MOVEMENT AND COMMAND INTERPRETATION
# ============================================================

def valid_position(new_x, new_y):
    robot_rect = pygame.Rect(new_x, new_y, ROBOT_W, ROBOT_H)

    if robot_rect.left < GAME_LEFT + 5:
        return False
    if robot_rect.right > GAME_RIGHT - 5:
        return False
    if robot_rect.top < GAME_TOP + 5:
        return False
    if robot_rect.bottom > GAME_BOTTOM - 5:
        return False

    return not any(robot_rect.colliderect(wall) for wall in obstacles)


def move_robot(direction, steps):
    global robot_x, robot_y, score, status_message, target_reached

    steps = max(1, min(10, steps))
    dx, dy = 0, 0

    if direction == "forward":
        dy = -GRID_SIZE
    elif direction == "back":
        dy = GRID_SIZE
    elif direction == "left":
        dx = -GRID_SIZE
    elif direction == "right":
        dx = GRID_SIZE

    moved_any = False

    for _ in range(steps):
        nx = robot_x + dx
        ny = robot_y + dy

        if valid_position(nx, ny):
            robot_x, robot_y = nx, ny
            moved_any = True
        else:
            status_message = "Blocked by an obstacle! Try another direction."
            score = max(0, score - 2)
            return

    if moved_any:
        robot_rect = pygame.Rect(robot_x, robot_y, ROBOT_W, ROBOT_H)
        if robot_rect.colliderect(target_rect):
            if not target_reached:
                score += 100
                target_reached = True
            status_message = "TARGET REACHED! +100"
        else:
            status_message = "Command accepted."


number_words = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


def interpret_command(command):
    text = command.lower().strip()
    text = re.sub(r"[,.!?]", "", text)

    match = re.search(r"\b(\d+)\b", text)
    steps = int(match.group(1)) if match else 1

    if not match:
        for word, number in number_words.items():
            if re.search(r"\b" + word + r"\b", text):
                steps = number
                break

    words = set(text.split())

    if words.intersection({"forward", "up", "ahead", "north"}):
        return "forward", steps
    if words.intersection({"back", "backward", "down", "reverse", "south"}):
        return "back", steps
    if words.intersection({"left", "west"}):
        return "left", steps
    if words.intersection({"right", "east"}):
        return "right", steps

    return None, 0


def process_command(command):
    global status_message

    command = command.strip()
    if not command:
        return

    command_history.append(command)
    direction, steps = interpret_command(command)

    if direction is None:
        status_message = "I didn't understand. Try forward, back, left, or right."
        return

    move_robot(direction, steps)


# ============================================================
# VOICE INPUT
# ============================================================

def listen_for_voice():
    global voice_listening, voice_status

    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            voice_listening = True
            voice_status = "LISTENING..."

            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)

        voice_status = "PROCESSING..."
        spoken_text = recognizer.recognize_google(audio)
        voice_queue.put(spoken_text)
        voice_status = "VOICE READY"

    except sr.WaitTimeoutError:
        voice_status = "NO SPEECH - PRESS V AGAIN"
    except sr.UnknownValueError:
        voice_status = "NOT UNDERSTOOD - TRY AGAIN"
    except sr.RequestError:
        voice_status = "INTERNET ERROR"
    except Exception as error:
        voice_status = "MIC ERROR - CHECK DEVICE"
        print("Voice error:", error)
    finally:
        voice_listening = False


def start_voice():
    if voice_listening:
        return
    threading.Thread(target=listen_for_voice, daemon=True).start()


def reset_game():
    global robot_x, robot_y, score, command_history
    global status_message, command_text, target_reached

    robot_x, robot_y = START_X, START_Y
    score = 0
    command_history = []
    command_text = ""
    target_reached = False
    status_message = "Reset! Find the destination."


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:
    while not voice_queue.empty():
        spoken = voice_queue.get()
        command_text = spoken
        process_command(spoken)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v:
                start_voice()

            elif event.key == pygame.K_r:
                reset_game()

            elif event.key == pygame.K_RETURN:
                if command_text.strip():
                    process_command(command_text)
                    command_text = ""

            elif event.key == pygame.K_BACKSPACE:
                command_text = command_text[:-1]

            elif event.unicode and event.unicode.isprintable():
                command_text += event.unicode

    screen.fill(BG)
    draw_header()
    draw_grass_board()
    draw_start()
    draw_obstacles()
    draw_target()
    draw_robot()
    draw_side_panel()
    draw_command_area()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
