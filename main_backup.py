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

# -----------------------------
# ROBOT
# -----------------------------
robot_x = 80
robot_y = 80
robot_size = 40
speed = 5

# -----------------------------
# TARGET
# -----------------------------
target = pygame.Rect(680, 480, 50, 50)

# -----------------------------
# OBSTACLES
# -----------------------------
obstacles = [
    pygame.Rect(250, 100, 40, 250),
    pygame.Rect(450, 300, 40, 220),
    pygame.Rect(150, 400, 180, 40)
]

# -----------------------------
# SCORE
# -----------------------------
score = 0
target_reached = False

font = pygame.font.Font(None, 36)

# -----------------------------
# GAME LOOP
# -----------------------------
running = True

while running:

    # -------------------------
    # EVENTS
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # -------------------------
    # ROBOT MOVEMENT
    # -------------------------
    keys = pygame.key.get_pressed()

    old_x = robot_x
    old_y = robot_y

    if keys[pygame.K_LEFT]:
        robot_x -= speed

    if keys[pygame.K_RIGHT]:
        robot_x += speed

    if keys[pygame.K_UP]:
        robot_y -= speed

    if keys[pygame.K_DOWN]:
        robot_y += speed

    # -------------------------
    # KEEP ROBOT ON SCREEN
    # -------------------------
    robot_x = max(0, min(WIDTH - robot_size, robot_x))
    robot_y = max(0, min(HEIGHT - robot_size, robot_y))

    robot = pygame.Rect(
        robot_x,
        robot_y,
        robot_size,
        robot_size
    )

    # -------------------------
    # OBSTACLE COLLISION
    # -------------------------
    collision = False

    for obstacle in obstacles:

        if robot.colliderect(obstacle):
            collision = True
            break

    # If collision, return to old position
    if collision:
        robot_x = old_x
        robot_y = old_y

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

    # -------------------------
    # DRAW BACKGROUND
    # -------------------------
    screen.fill(BACKGROUND)

    # -------------------------
    # DRAW OBSTACLES
    # -------------------------
    for obstacle in obstacles:

        pygame.draw.rect(
            screen,
            RED,
            obstacle
        )

    # -------------------------
    # DRAW TARGET
    # -------------------------
    pygame.draw.rect(
        screen,
        GREEN,
        target
    )

    # Target center
    pygame.draw.circle(
        screen,
        WHITE,
        target.center,
        10
    )

    # -------------------------
    # DRAW ROBOT
    # -------------------------
    pygame.draw.rect(
        screen,
        BLUE,
        robot
    )

    # Robot eyes
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
    # SCORE
    # -------------------------
    score_text = font.render(
        f"Score: {score}",
        True,
        BLACK
    )

    screen.blit(
        score_text,
        (20, 20)
    )

    # -------------------------
    # TARGET MESSAGE
    # -------------------------
    if target_reached:

        message = font.render(
            "TARGET REACHED!",
            True,
            GREEN
        )

        screen.blit(
            message,
            (300, 30)
        )

    # -------------------------
    # UPDATE SCREEN
    # -------------------------
    pygame.display.flip()

    clock.tick(60)

pygame.quit()