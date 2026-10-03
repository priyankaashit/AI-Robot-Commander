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
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 25)
message_font = pygame.font.Font(None, 34)

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
# COMMAND SYSTEM
# -----------------------------
command = ""
message = "Type a command and press ENTER"

# -----------------------------
# MOVE ROBOT
# -----------------------------
def move_robot(dx, dy):

    global robot_x, robot_y

    old_x = robot_x
    old_y = robot_y

    robot_x += dx
    robot_y += dy

    # Keep robot inside screen
    robot_x = max(0, min(WIDTH - robot_size, robot_x))
    robot_y = max(70, min(HEIGHT - robot_size, robot_y))

    robot = pygame.Rect(
        robot_x,
        robot_y,
        robot_size,
        robot_size
    )

    # Check obstacle collision
    for obstacle in obstacles:

        if robot.colliderect(obstacle):

            robot_x = old_x
            robot_y = old_y

            return False

    return True


# -----------------------------
# COMMAND INTERPRETER
# -----------------------------
def process_command(text):

    global score
    global target_reached
    global message

    text = text.lower().strip()

    if text == "move right":
        if move_robot(speed, 0):
            message = "Command accepted: Moving right"
        else:
            message = "Blocked by obstacle!"

    elif text == "move left":
        if move_robot(-speed, 0):
            message = "Command accepted: Moving left"
        else:
            message = "Blocked by obstacle!"

    elif text == "move up":
        if move_robot(0, -speed):
            message = "Command accepted: Moving up"
        else:
            message = "Blocked by obstacle!"

    elif text == "move down":
        if move_robot(0, speed):
            message = "Command accepted: Moving down"
        else:
            message = "Blocked by obstacle!"

    else:
        message = "Invalid command!"


# -----------------------------
# GAME LOOP
# -----------------------------
running = True

while running:

    for event in pygame.event.get():

        # Quit
        if event.type == pygame.QUIT:
            running = False

        # Keyboard input
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
    # TARGET DETECTION
    # -------------------------
    if robot.colliderect(target):

        if not target_reached:

            score += 100
            target_reached = True
            message = "TARGET REACHED! +100 points"

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
        (30, 520, 740, 45)
    )

    pygame.draw.rect(
        screen,
        DARK_BLUE,
        (30, 520, 740, 45),
        2
    )

    command_text = font.render(
        "Command: " + command,
        True,
        BLACK
    )

    screen.blit(
        command_text,
        (40, 530)
    )

    # -------------------------
    # STATUS MESSAGE
    # -------------------------
    status_text = small_font.render(
        message,
        True,
        DARK_BLUE
    )

    screen.blit(
        status_text,
        (30, 85)
    )

    # -------------------------
    # HELP
    # -------------------------
    help_text = small_font.render(
        "Try: move right | move left | move up | move down",
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