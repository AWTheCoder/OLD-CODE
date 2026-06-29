import pygame
import sys # lets your program interact with the Python system
import random

####### Timer & Systems (A) ######
pygame.init()
pygame.mixer.init()  # turns on pygame's sound system

# Window setup
WIDTH, HEIGHT = 900, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT)) # create game window
pygame.display.set_caption("Dove Hunt")

# Audio Setup
# 1. Loading the sound effects
shoot_sound = pygame.mixer.Sound("sounds/gun_shot.mp3") # loads a sound effect into memory
hit_sound = pygame.mixer.Sound("sounds/bird_shot.wav")

# 2. Loading the background music
pygame.mixer.music.load("sounds/rain_loop.wav")
pygame.mixer.music.play(-1)

# Load backdrop
try:
    backdrop = pygame.image.load("backdrop.png")
    BACKDROP = pygame.transform.scale(backdrop, (WIDTH, HEIGHT))
except pygame.error:
    print("Couldn't find backdrop.")
    sys.exit()

###### Game Logic (G+Y) ######
# Define the missing DOVE variable here and scale it to 60x60
try:
    dove_original = pygame.image.load("dove.png")  # Assumes you have a dove.png image
    DOVE = pygame.transform.scale(dove_original, (90, 90))  # Scales it down so it isn't massive
except pygame.error:
    # Fallback: Creates a white square if the dove is missing
    DOVE = pygame.Surface((60, 60), pygame.SRCALPHA) # backup image
    DOVE.fill((255, 255, 255))
    print("Couldn't find dove.png, using a white square placeholder.")

clock = pygame.time.Clock() # helps control how fast your game runs

###### UI & Scoreboard (Z) ######4
# Scoreboard Variables
player1_score = 0
player2_score = 0

# Timer Variables
game_time = 60
start_time = None # no value assigned yet

# Fonts
title_font = pygame.font.SysFont("Arial", 50, bold=True)

# Timer font
font = pygame.font.SysFont(None, 50)

# Smaller UI font
ui_font = pygame.font.SysFont("Arial", 32)

# Game States
show_instructions = True
game_over = False
running = True

###### Game Logic (G+Y) ######
# Dove Settings
dove_speed = 4
doves = []
spawn_timer = 0
spawn_delay = 2000
HITBOX_SIZE = 30

# Hit Effects
hit_effects = []

FALL_SPEED = 8
FLASH_TIME = 150

# Player Crosshair Settings
crosshair_speed = 7
crosshair_radius = 15

# Player 1 (Red Crosshair)
p1_x, p1_y = 250, HEIGHT // 2
p1_color = (255, 50, 50)

# Player 2 (Blue Crosshair)
p2_x, p2_y = 650, HEIGHT // 2
p2_color = (50, 150, 255)


# Helper function to handle a shot hitting a dove
def check_shot(target_x, target_y, player_name):

    global player1_score, player2_score
    hit = False

    for dove in doves:

        # Smaller hitbox centred inside the 90x90 dove image
        dove_rect = pygame.Rect(
            dove["x"] + (90 - HITBOX_SIZE) // 2,
            dove["y"] + (90 - HITBOX_SIZE) // 2,
            HITBOX_SIZE,
            HITBOX_SIZE
        )

        if dove_rect.collidepoint(target_x, target_y):

            if not dove["hit"]:
                dove["hit"] = True
                dove["hit_time"] = pygame.time.get_ticks()

                if player_name == "Player 1":
                    player1_score += 1
                elif player_name == "Player 2":
                    player2_score += 1

                hit_effects.append({
                    "x": target_x,
                    "y": target_y,
                    "radius": 5,
                    "life": 15
                })

                pygame.mixer.Sound.play(hit_sound)

                print(f"{player_name} Hit a Dove!")
                hit = True

            break

# Main Game Loop
while running:

    # Event Handling
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player1_score = 0
                    player2_score = 0

                    game_over = False
                    show_instructions = True

                    start_time = None

        # Start game with ENTER
        if show_instructions:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    show_instructions = False

                    # Start timer ONLY when game begins
                    start_time = pygame.time.get_ticks()

        # Shooting inputs from the second loop
        if not show_instructions:
            if event.type == pygame.KEYDOWN:

                # Player 1 shoots with SPACE
                if event.key == pygame.K_SPACE:
                    pygame.mixer.Sound.play(shoot_sound)
                    check_shot(p1_x, p1_y, "Player 1")

                # Player 2 shoots with ENTER
                if event.key == pygame.K_RETURN:
                    pygame.mixer.Sound.play(shoot_sound)
                    check_shot(p2_x, p2_y, "Player 2")

    # Continuous keyboard input
    keys = pygame.key.get_pressed()

    # Player 1 Movement (WASD)
    if keys[pygame.K_a]:
        p1_x -= crosshair_speed
    if keys[pygame.K_d]:
        p1_x += crosshair_speed
    if keys[pygame.K_w]:
        p1_y -= crosshair_speed
    if keys[pygame.K_s]:
        p1_y += crosshair_speed

    # Player 2 Movement (Arrow Keys)
    if keys[pygame.K_LEFT]:
        p2_x -= crosshair_speed
    if keys[pygame.K_RIGHT]:
        p2_x += crosshair_speed
    if keys[pygame.K_UP]:
        p2_y -= crosshair_speed
    if keys[pygame.K_DOWN]:
        p2_y += crosshair_speed

    # Keep crosshairs on screen
    p1_x = max(0, min(p1_x, WIDTH))
    p1_y = max(0, min(p1_y, HEIGHT))

    p2_x = max(0, min(p2_x, WIDTH))
    p2_y = max(0, min(p2_y, HEIGHT))

    # Spawn new doves
    if not show_instructions:
        current_time = pygame.time.get_ticks()

        if current_time - spawn_timer > spawn_delay:

            for i in range(4):  # Spawn 4 doves each time

                doves.append({
                    "x": random.randint(50, WIDTH - 110),
                    "y": HEIGHT + random.randint(0, 150),
                    "hit": False,
                    "hit_time": 0
                })

            spawn_timer = current_time

    # Move doves
    for dove in doves[:]:

        if not dove["hit"]:
            dove["y"] -= dove_speed

            if dove["y"] + 60 < 0:
                doves.remove(dove)

        else:
            dove["y"] += FALL_SPEED

            if dove["y"] > HEIGHT:
                doves.remove(dove)

    # UPDATE HIT EFFECTS
    for effect in hit_effects[:]:

        effect["radius"] += 2
        effect["life"] -= 1

        if effect["life"] <= 0:
            hit_effects.remove(effect)

    ###### UI & Scoreboard (Z) ######
    # Drawing Section

    # Draw backdrop
    SCREEN.blit(BACKDROP, (0, 0))

    # Instructions Screen
    if show_instructions:

        title = title_font.render(
            "DOVE HUNT",
            True,
            (255, 255, 255)
        )

        p1 = ui_font.render(
            "Player 1: WASD + SPACE",
            True,
            (255, 255, 255)
        )

        p2 = ui_font.render(
            "Player 2: Arrow Keys + ENTER",
            True,
            (255, 255, 255)
        )

        start = ui_font.render(
            "Press ENTER to Start",
            True,
            (255, 255, 0)
        )

        SCREEN.blit(
            title,
            (WIDTH // 2 - title.get_width() // 2, 150)
        )

        SCREEN.blit(p1, (220, 280))
        SCREEN.blit(p2, (220, 330))
        SCREEN.blit(start, (250, 420))

    else:

        # Timer Default Value
        time_left = 0

        # Timer
        if not game_over:

            # Only compute time if game has started and start_time exists
            if start_time is not None:
                elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

                time_left = max(0,game_time - elapsed_time)

                if time_left <= 0:
                    game_over = True
            # Stop dove spawning here
            # Stop player shooting here
            # Freeze scores here

        else:
            time_left = 0

        # Scoreboard Display
        p1_text = ui_font.render(
            f"Player 1: {player1_score}",
            True,
            (255, 255, 255)
        )

        p2_text = ui_font.render(
            f"Player 2: {player2_score}",
            True,
            (255, 255, 255)
        )

        ###### Timer & Systems (A) ######
        if time_left > 10:
            timer_colour = (255, 255, 255)  # white

        elif time_left > 5:
            timer_colour = (255, 255, 0)  # yellow

        else:
            timer_colour = (255, 0, 0)  # red

        ###### UI & Scoreboard (Z) ######
        timer_text = font.render(
            f"Time: {time_left}",
            True,
            timer_colour
        )

        # Player 1 Score
        SCREEN.blit(p1_text, (20, 20))

        # Player 2 Score
        SCREEN.blit(
            p2_text,
            (WIDTH - p2_text.get_width() - 20, 20)
        )

        # Timer
        SCREEN.blit(
            timer_text,
            (WIDTH // 2 - timer_text.get_width() // 2, 20)
        )

        ###### Timer & Systems (A) ######
        # Game Over Screen
        if game_over:

            if player1_score > player2_score:
                winner = "Player 1 Wins!"

            elif player2_score > player1_score:
                winner = "Player 2 Wins!"

            else:
                winner = "Draw!"

            ###### UI & Scoreboard (Z) ######
            game_over_text = title_font.render(
                "GAME OVER",
                True,
                (255, 0, 0)
            )

            winner_text = ui_font.render(
                winner,
                True,
                (255, 255, 255)
            )

            score1_text = ui_font.render(
                f"Player 1 Score: {player1_score}",
                True,
                (255, 255, 255)
            )

            score2_text = ui_font.render(
                f"Player 2 Score: {player2_score}",
                True,
                (255, 255, 255)
            )

            ###### Timer & Systems (A) ######
            restart_text = ui_font.render(
                "Press R to Play Again",
                True,
                (255, 255, 0)
            )

            ###### UI & Scoreboard (Z) ######
            SCREEN.blit(
                game_over_text,
                (WIDTH // 2 - game_over_text.get_width() // 2, 200)
            )

            SCREEN.blit(
                score1_text,
                (WIDTH // 2 - score1_text.get_width() // 2, 300)
            )

            SCREEN.blit(
                score2_text,
                (WIDTH // 2 - score2_text.get_width() // 2, 350)
            )

            SCREEN.blit(
                winner_text,
                (WIDTH // 2 - winner_text.get_width() // 2, 450)
            )

            SCREEN.blit(
                restart_text,
                (WIDTH // 2 - restart_text.get_width() // 2, 520)
            )

    ###### Game Logic (G+Y) ######
    # Draw Doves
    if not show_instructions:
        for dove in doves:

            if dove["hit"]:

                elapsed = pygame.time.get_ticks() - dove["hit_time"]

                if elapsed < FLASH_TIME:

                    flash = DOVE.copy()

                    red_overlay = pygame.Surface(
                        flash.get_size(),
                        pygame.SRCALPHA
                    )

                    red_overlay.fill((255, 0, 0, 120))

                    flash.blit(red_overlay, (0, 0))

                    SCREEN.blit(
                        flash,
                        (dove["x"], dove["y"])
                    )

                else:
                    SCREEN.blit(
                        DOVE,
                        (dove["x"], dove["y"])
                    )

            else:
                SCREEN.blit(
                    DOVE,
                    (dove["x"], dove["y"])
                )

    # Draw Hit Effects
    for effect in hit_effects:
        pygame.draw.circle(
            SCREEN,
            (255, 255, 0),
            (effect["x"], effect["y"]),
            effect["radius"],
            2
        )

    # Draw Player 1 Crosshair (Red)
    if not show_instructions:
        pygame.draw.circle(
            SCREEN,
            p1_color,
            (p1_x, p1_y),
            crosshair_radius,
            2
        )

        pygame.draw.line(
            SCREEN,
            p1_color,
            (p1_x - 25, p1_y),
            (p1_x + 25, p1_y),
            2
        )

        pygame.draw.line(
            SCREEN,
            p1_color,
            (p1_x, p1_y - 25),
            (p1_x, p1_y + 25),
            2
        )

    # Draw Player 2 Crosshair (Blue)
    if not show_instructions:
        pygame.draw.circle(
            SCREEN,
            p2_color,
            (p2_x, p2_y),
            crosshair_radius,
            2
        )

        pygame.draw.line(
            SCREEN,
            p2_color,
            (p2_x - 25, p2_y),
            (p2_x + 25, p2_y),
            2
        )

        pygame.draw.line(
            SCREEN,
            p2_color,
            (p2_x, p2_y - 25),
            (p2_x, p2_y + 25),
            2
        )

    ###### Timer & Systems (A) ######
    # Update display
    pygame.display.flip()
    clock.tick(60) # run game at max of 60 FPS (frames per sec)

pygame.quit()
sys.exit()