import pygame

pygame.init()

# -----------------------------
# WINDOW
# -----------------------------
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Robot Commander")

clock = pygame.time.Clock()

# -----------------------------
# COLORS
# -----------------------------
BACKGROUND = (240, 240, 240)
BLUE = (50, 120, 255)
GREEN = (50, 200, 80)
RED = (220, 60, 60)
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
YELLOW = (255, 210, 50)
DARK_BLUE = (30, 70, 140)
LIGHT_BLUE = (220, 235, 255)

# -----------------------------
# FONTS
# -----------------------------
title_font = pygame.font.Font(None, 36)
font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 22)
message_font = pygame.font.Font(None, 32)

# -----------------------------
# ROBOT
# -----------------------------
robot_x = 80
robot_y = 100
robot_size = 40
speed = 50

# -----------------------------
# TARGET
# -----------------------------
target = pygame.Rect(680, 480, 50, 50)

# -----------------------------
# OBSTACLES
# -----------------------------
obstacles = [
    pygame.Rect(250, 120, 40, 250),
    pygame.Rect(450, 300, 40, 220),
    pygame.Rect(150, 400, 180, 40)
]

# -----------------------------
# SCORE
# -----------------------------
score = 0
target_reached = False

# -----------------------------
# COMMAND
# -----------------------------
command = ""
message = "Type a command and press ENTER"

# -----------------------------
# HISTORY
# -----------------------------
history = []

# -----------------------------
# PATH
# -----------------------------
path = [(robot_x + robot_size // 2, robot_y + robot_size // 2)]

# -----------------------------
# LEARNING MODE
# -----------------------------
learning_input = "Waiting for command..."
learning_direction = "-"
learning_action = "-"
learning_result = "Waiting..."


# -----------------------------
# MOVE ROBOT
# -----------------------------
def move_robot(dx, dy):

    global robot_x, robot_y

    old_x = robot_x
    old_y = robot_y

    robot_x += dx
    robot_y += dy

    # Keep inside screen
    robot_x = max(0, min(WIDTH - robot_size, robot_x))
    robot_y = max(70, min(HEIGHT - robot_size, robot_y))

    robot = pygame.Rect(
        robot_x,
        robot_y,
        robot_size,
        robot_size
    )

    # Collision check
    for obstacle in obstacles:

        if robot.colliderect(obstacle):

            robot_x = old_x
            robot_y = old_y

            return False

    # Add position to path
    path.append(
        (robot_x + robot_size // 2,
         robot_y + robot_size // 2)
    )

    return True


# -----------------------------
# COMMAND INTERPRETER
# -----------------------------
def process_command(text):

    global message
    global learning_input
    global learning_direction
    global learning_action
    global learning_result

    text = text.lower().strip()

    if not text:
        return

    history.append(text)

    if len(history) > 5:
        history.pop(0)

    # Learning mode input
    learning_input = text
    learning_action = "MOVE"

    # RIGHT
    if "right" in text:

        learning_direction = "RIGHT"

        if move_robot(speed, 0):
            message = "Command accepted: Moving RIGHT"
            learning_result = "Command accepted"
        else:
            message = "Blocked by obstacle!"
            learning_result = "Blocked by obstacle"

    # LEFT
    elif "left" in text:

        learning_direction = "LEFT"

        if move_robot(-speed, 0):
            message = "Command accepted: Moving LEFT"
            learning_result = "Command accepted"
        else:
            message = "Blocked by obstacle!"
            learning_result = "Blocked by obstacle"

    # UP
    elif "up" in text:

        learning_direction = "UP"

        if move_robot(0, -speed):
            message = "Command accepted: Moving UP"
            learning_result = "Command accepted"
        else:
            message = "Blocked by obstacle!"
            learning_result = "Blocked by obstacle"

    # DOWN
    elif "down" in text:

        learning_direction = "DOWN"

        if move_robot(0, speed):
            message = "Command accepted: Moving DOWN"
            learning_result = "Command accepted"
        else:
            message = "Blocked by obstacle!"
            learning_result = "Blocked by obstacle"

    # INVALID
    else:

        learning_direction = "UNKNOWN"
        learning_action = "NONE"
        learning_result = "Invalid command"
        message = "Invalid command!"


# -----------------------------
# GAME LOOP
# -----------------------------
running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:

                if command.strip():
                    process_command(command)
                    command = ""

            elif event.key == pygame.K_BACKSPACE:

                command = command[:-1]

            else:

                if event.unicode.isprintable():
                    command += event.unicode

    # -------------------------
    # ROBOT RECT
    # -------------------------
    robot = pygame.Rect(
        robot_x,
        robot_y,
        robot_size,
        robot_size
    )

    # -------------------------
    # TARGET
    # -------------------------
    if robot.colliderect(target):

        if not target_reached:

            score += 100
            target_reached = True

            message = "TARGET REACHED! +100 points"
            learning_result = "Target reached"


    # -------------------------
    # DRAW BACKGROUND
    # -------------------------
    screen.fill(BACKGROUND)

    # -------------------------
    # TOP BAR
    # -------------------------
    pygame.draw.rect(
        screen,
        DARK_BLUE,
        (0, 0, WIDTH, 70)
    )

    title = title_font.render(
        "AI ROBOT COMMANDER",
        True,
        WHITE
    )

    screen.blit(title, (20, 18))

    score_text = font.render(
        f"Score: {score}",
        True,
        YELLOW
    )

    screen.blit(score_text, (650, 22))

    # -------------------------
    # STATUS
    # -------------------------
    status = small_font.render(
        message,
        True,
        DARK_BLUE
    )

    screen.blit(status, (30, 82))

    # -------------------------
    # PATH
    # -------------------------
    if len(path) > 1:

        pygame.draw.lines(
            screen,
            BLUE,
            False,
            path,
            3
        )

    # -------------------------
    # OBSTACLES
    # -------------------------
    for obstacle in obstacles:

        pygame.draw.rect(
            screen,
            RED,
            obstacle
        )

    # -------------------------
    # TARGET
    # -------------------------
    pygame.draw.rect(
        screen,
        GREEN,
        target
    )

    pygame.draw.circle(
        screen,
        WHITE,
        target.center,
        10
    )

    # -------------------------
    # ROBOT
    # -------------------------
    pygame.draw.rect(
        screen,
        BLUE,
        robot
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (robot_x + 12, robot_y + 12),
        5
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (robot_x + 28, robot_y + 12),
        5
    )

    # -------------------------
    # COMMAND BOX
    # -------------------------
    pygame.draw.rect(
        screen,
        WHITE,
        (30, 515, 500, 45)
    )

    pygame.draw.rect(
        screen,
        DARK_BLUE,
        (30, 515, 500, 45),
        2
    )

    command_text = font.render(
        "Command: " + command,
        True,
        BLACK
    )

    screen.blit(
        command_text,
        (40, 525)
    )

    # -------------------------
    # COMMAND HISTORY
    # -------------------------
    history_title = small_font.render(
        "COMMAND HISTORY",
        True,
        DARK_BLUE
    )

    screen.blit(history_title, (550, 300))

    y = 325

    for item in history:

        history_text = small_font.render(
            "• " + item,
            True,
            BLACK
        )

        screen.blit(
            history_text,
            (550, y)
        )

        y += 23

    # -------------------------
    # LEARNING MODE PANEL
    # -------------------------
    pygame.draw.rect(
        screen,
        LIGHT_BLUE,
        (540, 80, 240, 200)
    )

    pygame.draw.rect(
        screen,
        DARK_BLUE,
        (540, 80, 240, 200),
        2
    )

    learning_title = small_font.render(
        "AI LEARNING MODE",
        True,
        DARK_BLUE
    )

    screen.blit(
        learning_title,
        (555, 95)
    )

    input_text = small_font.render(
        "Input: " + learning_input[:25],
        True,
        BLACK
    )

    screen.blit(input_text, (555, 130))

    direction_text = small_font.render(
        "Direction: " + learning_direction,
        True,
        BLACK
    )

    screen.blit(direction_text, (555, 160))

    action_text = small_font.render(
        "Action: " + learning_action,
        True,
        BLACK
    )

    screen.blit(action_text, (555, 190))

    result_text = small_font.render(
        "Result: " + learning_result[:20],
        True,
        BLACK
    )

    screen.blit(result_text, (555, 220))

    # -------------------------
    # HELP
    # -------------------------
    help_text = small_font.render(
        "Try: go right | move left | robot go up | move down",
        True,
        BLACK
    )

    screen.blit(
        help_text,
        (30, 570)
    )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()