import pygame
import speech_recognition as sr
import threading
import queue
import re

# ---------------------------------------------------------
# INITIAL SETUP
# ---------------------------------------------------------

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Robot Commander")

clock = pygame.time.Clock()

# ---------------------------------------------------------
# COLORS
# ---------------------------------------------------------

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
LIGHT_BLUE = (225, 240, 255)
BLUE = (50, 120, 255)
DARK_BLUE = (30, 70, 140)
GREEN = (60, 190, 90)
DARK_GREEN = (30, 120, 60)
RED = (220, 70, 70)
ORANGE = (245, 160, 50)
YELLOW = (255, 220, 60)
PURPLE = (150, 80, 200)
GRAY = (120, 120, 120)
LIGHT_GRAY = (245, 245, 245)

# ---------------------------------------------------------
# FONTS
# ---------------------------------------------------------

title_font = pygame.font.SysFont("arial", 32, bold=True)
font = pygame.font.SysFont("arial", 22)
small_font = pygame.font.SysFont("arial", 17)
command_font = pygame.font.SysFont("arial", 20)

# ---------------------------------------------------------
# ROBOT / TARGET
# ---------------------------------------------------------

ROBOT_SIZE = 40
MOVE_STEP = 50

robot = pygame.Rect(70, 120, ROBOT_SIZE, ROBOT_SIZE)

start_position = (70, 120)

target = pygame.Rect(850, 520, 45, 45)

# ---------------------------------------------------------
# OBSTACLES
# ---------------------------------------------------------

obstacles = [
    pygame.Rect(250, 100, 180, 40),
    pygame.Rect(250, 250, 40, 220),
    pygame.Rect(500, 180, 200, 40),
    pygame.Rect(620, 330, 40, 180),
    pygame.Rect(350, 500, 180, 40),
]

# ---------------------------------------------------------
# GAME VARIABLES
# ---------------------------------------------------------

score = 0
target_reached = False

command_text = ""

command_history = []

status_message = "Give the robot a command!"

voice_status = "Press V for voice command"

voice_queue = queue.Queue()

listening = False

# ---------------------------------------------------------
# DRAW BACKGROUND
# ---------------------------------------------------------

def draw_background():

    screen.fill(LIGHT_BLUE)

    # Header
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, WIDTH, 75))

    title = title_font.render(
        "AI ROBOT COMMANDER",
        True,
        WHITE
    )

    screen.blit(title, (25, 18))

    subtitle = small_font.render(
        "Can You Give AI the Right Command?",
        True,
        WHITE
    )

    screen.blit(subtitle, (600, 28))

    # Game area
    pygame.draw.rect(
        screen,
        WHITE,
        (25, 95, 950, 540),
        border_radius=15
    )

    pygame.draw.rect(
        screen,
        DARK_BLUE,
        (25, 95, 950, 540),
        3,
        border_radius=15
    )

# ---------------------------------------------------------
# DRAW OBSTACLES
# ---------------------------------------------------------

def draw_obstacles():

    for obstacle in obstacles:

        pygame.draw.rect(
            screen,
            RED,
            obstacle,
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            (150, 30, 30),
            obstacle,
            3,
            border_radius=6
        )

        # Brick pattern
        for x in range(obstacle.left + 10, obstacle.right, 30):

            pygame.draw.line(
                screen,
                (255, 150, 150),
                (x, obstacle.top),
                (x, obstacle.bottom),
                2
            )

# ---------------------------------------------------------
# DRAW TARGET
# ---------------------------------------------------------

def draw_target():

    pygame.draw.rect(
        screen,
        GREEN,
        target,
        border_radius=10
    )

    target_text = font.render(
        "🎯",
        True,
        BLACK
    )

    screen.blit(
        target_text,
        (target.x + 7, target.y + 8)
    )

# ---------------------------------------------------------
# DRAW ROBOT
# ---------------------------------------------------------

def draw_robot():

    pygame.draw.rect(
        screen,
        BLUE,
        robot,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        DARK_BLUE,
        robot,
        3,
        border_radius=10
    )

    # Robot eyes
    pygame.draw.circle(
        screen,
        WHITE,
        (robot.x + 12, robot.y + 13),
        5
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (robot.x + 28, robot.y + 13),
        5
    )

    # Smile
    pygame.draw.line(
        screen,
        WHITE,
        (robot.x + 12, robot.y + 28),
        (robot.x + 28, robot.y + 28),
        3
    )

# ---------------------------------------------------------
# DRAW START
# ---------------------------------------------------------

def draw_start():

    text = small_font.render(
        "START",
        True,
        DARK_GREEN
    )

    screen.blit(
        text,
        (55, 170)
    )

# ---------------------------------------------------------
# DRAW INFORMATION PANEL
# ---------------------------------------------------------

def draw_panel():

    # Score
    score_text = font.render(
        f"Score: {score}",
        True,
        DARK_BLUE
    )

    screen.blit(
        score_text,
        (45, 650)
    )

    # Status
    status = small_font.render(
        status_message,
        True,
        BLACK
    )

    screen.blit(
        status,
        (220, 652)
    )

# ---------------------------------------------------------
# DRAW COMMAND BOX
# ---------------------------------------------------------

def draw_command_box():

    pygame.draw.rect(
        screen,
        WHITE,
        (45, 585, 650, 42),
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        DARK_BLUE,
        (45, 585, 650, 42),
        2,
        border_radius=8
    )

    text = command_font.render(
        command_text,
        True,
        BLACK
    )

    screen.blit(
        text,
        (55, 594)
    )

    label = small_font.render(
        "Type command + ENTER",
        True,
        GRAY
    )

    screen.blit(
        label,
        (710, 594)
    )

# ---------------------------------------------------------
# DRAW VOICE STATUS
# ---------------------------------------------------------

def draw_voice_status():

    if listening:

        pygame.draw.rect(
            screen,
            ORANGE,
            (700, 585, 250, 42),
            border_radius=8
        )

        text = small_font.render(
            "🎤 Listening...",
            True,
            BLACK
        )

    else:

        pygame.draw.rect(
            screen,
            GREEN,
            (700, 585, 250, 42),
            border_radius=8
        )

        text = small_font.render(
            "🎤 Press V for Voice",
            True,
            BLACK
        )

    screen.blit(
        text,
        (715, 597)
    )

# ---------------------------------------------------------
# COLLISION CHECK
# ---------------------------------------------------------

def valid_position(new_rect):

    # Screen boundaries
    if new_rect.left < 35:
        return False

    if new_rect.right > 965:
        return False

    if new_rect.top < 90:
        return False

    if new_rect.bottom > 635:
        return False

    # Obstacles
    for obstacle in obstacles:

        if new_rect.colliderect(obstacle):

            return False

    return True

# ---------------------------------------------------------
# MOVE ROBOT
# ---------------------------------------------------------

def move_robot(direction, steps=1):

    global score
    global status_message
    global target_reached

    dx = 0
    dy = 0

    if direction == "up":
        dy = -MOVE_STEP

    elif direction == "down":
        dy = MOVE_STEP

    elif direction == "left":
        dx = -MOVE_STEP

    elif direction == "right":
        dx = MOVE_STEP

    for _ in range(steps):

        new_position = robot.copy()

        new_position.x += dx
        new_position.y += dy

        if valid_position(new_position):

            robot.x = new_position.x
            robot.y = new_position.y

        else:

            status_message = "🚫 Blocked! Obstacle or boundary."
            return

    # Target detection
    if robot.colliderect(target):

        if not target_reached:

            score += 100
            target_reached = True

            status_message = "🎉 Target reached! +100 points"

        else:

            status_message = "Target reached!"

    else:

        status_message = f"Robot moved {direction}."

# ---------------------------------------------------------
# NLP COMMAND INTERPRETER
# ---------------------------------------------------------

def interpret_command(command):

    command = command.lower().strip()

    # Remove punctuation
    command = re.sub(r"[^\w\s]", "", command)

    # Number words
    numbers = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10
    }

    steps = 1

    # Find numerical digit
    digit_match = re.search(r"\b(\d+)\b", command)

    if digit_match:

        steps = int(digit_match.group(1))

    else:

        # Find number word
        for word, number in numbers.items():

            if re.search(rf"\b{word}\b", command):

                steps = number
                break

    # Limit steps
    steps = max(1, min(steps, 10))

    # Direction detection

    if any(word in command for word in [
        "forward",
        "up",
        "ahead",
        "move forward"
    ]):

        return "up", steps

    if any(word in command for word in [
        "back",
        "backward",
        "down",
        "reverse"
    ]):

        return "down", steps

    if any(word in command for word in [
        "left",
        "turn left"
    ]):

        return "left", steps

    if any(word in command for word in [
        "right",
        "turn right"
    ]):

        return "right", steps

    return None, 0

# ---------------------------------------------------------
# PROCESS COMMAND
# ---------------------------------------------------------

def process_command(command):

    global status_message

    if not command.strip():
        return

    command_history.insert(
        0,
        command
    )

    if len(command_history) > 6:
        command_history.pop()

    direction, steps = interpret_command(command)

    if direction is None:

        status_message = "❌ I don't understand that command."

        return

    move_robot(
        direction,
        steps
    )

# ---------------------------------------------------------
# DRAW COMMAND HISTORY
# ---------------------------------------------------------

def draw_history():

    panel_x = 710
    panel_y = 120

    title = font.render(
        "Command History",
        True,
        DARK_BLUE
    )

    screen.blit(
        title,
        (panel_x, panel_y)
    )

    y = panel_y + 40

    for command in command_history:

        display_command = command[:23]

        text = small_font.render(
            "• " + display_command,
            True,
            BLACK
        )

        screen.blit(
            text,
            (panel_x, y)
        )

        y += 28

# ---------------------------------------------------------
# VOICE RECOGNITION
# ---------------------------------------------------------

def voice_command():

    global listening

    listening = True

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            status_message_local = "Listening..."

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.7
            )

            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=5
            )

        text = recognizer.recognize_google(
            audio
        )

        voice_queue.put(
            ("success", text)
        )

    except sr.UnknownValueError:

        voice_queue.put(
            ("error", "Sorry, I could not understand the command.")
        )

    except sr.RequestError:

        voice_queue.put(
            ("error", "Speech recognition service unavailable.")
        )

    except Exception as e:

        voice_queue.put(
            ("error", str(e))
        )

    finally:

        listening = False

# ---------------------------------------------------------
# START VOICE THREAD
# ---------------------------------------------------------

def start_voice():

    global listening

    if listening:
        return

    thread = threading.Thread(
        target=voice_command,
        daemon=True
    )

    thread.start()

# ---------------------------------------------------------
# RESET GAME
# ---------------------------------------------------------

def reset_game():

    global score
    global target_reached
    global status_message
    global command_text
    global command_history

    robot.x = start_position[0]
    robot.y = start_position[1]

    score = 0

    target_reached = False

    command_text = ""

    command_history = []

    status_message = "Game reset. Give the robot a command!"

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------

running = True

while running:

    # -----------------------------------------------------
    # CHECK VOICE RESULTS
    # -----------------------------------------------------

    while not voice_queue.empty():

        result_type, result_text = voice_queue.get()

        if result_type == "success":

            command_text = result_text

            status_message = f'Heard: "{result_text}"'

            process_command(
                result_text
            )

        else:

            status_message = result_text

    # -----------------------------------------------------
    # EVENTS
    # -----------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            # Voice
            if event.key == pygame.K_v:

                start_voice()

            # Reset
            elif event.key == pygame.K_r:

                reset_game()

            # Enter typed command
            elif event.key == pygame.K_RETURN:

                process_command(
                    command_text
                )

                command_text = ""

            # Backspace
            elif event.key == pygame.K_BACKSPACE:

                command_text = command_text[:-1]

            # Type command
            else:

                if event.unicode.isprintable():

                    command_text += event.unicode

    # -----------------------------------------------------
    # DRAW
    # -----------------------------------------------------

    draw_background()

    draw_start()

    draw_obstacles()

    draw_target()

    draw_robot()

    draw_history()

    draw_command_box()

    draw_voice_status()

    draw_panel()

    # -----------------------------------------------------
    # FOOTER INSTRUCTIONS
    # -----------------------------------------------------

    instruction = small_font.render(
        "Examples: Go forward two steps | Move right 3 | Turn left | Go backward",
        True,
        DARK_BLUE
    )

    screen.blit(
        instruction,
        (45, 560)
    )

    pygame.display.flip()

    clock.tick(30)

pygame.quit()