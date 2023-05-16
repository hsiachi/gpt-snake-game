import curses
from random import randint

def main(stdscr):
    # Get user input for map size
    sh, sw = get_user_input(stdscr)

    # Initialize the screen
    curses.curs_set(0)
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(100)

    # Draw boundary
    w.border(0)

    # Initialize the snake
    snake_x = sw // 4
    snake_y = sh // 2
    snake = [
        [snake_y, snake_x],
        [snake_y, snake_x - 1],
        [snake_y, snake_x - 2]
    ]

    # Initialize the food
    food = [sh // 2, sw // 2]
    w.addch(food[0], food[1], curses.ACS_PI)

    # Initialize the game settings
    key = curses.KEY_RIGHT
    score = 0

    # Initialize the pause status
    paused = False

    # Game loop
    while True:
        next_key = w.getch()

        # Handle the Space key to pause the game
        if next_key == ord(' '):
            paused = not paused
            continue

        key = key if next_key == -1 else next_key

        # Check if the game is paused
        if paused:
            continue

        # Get the dimensions of the game area
        sh, sw = w.getmaxyx()

        # Check if the snake hits the wall or itself
        if (
            snake[0][0] in [0, sh-1] or
            snake[0][1] in [0, sw-1] or
            snake[0] in snake[1:]
        ):
            break

        # Calculate the new head position
        new_head = [snake[0][0], snake[0][1]]

        # Update the head position based on the key
        if key == curses.KEY_DOWN:
            new_head[0] += 1
        if key == curses.KEY_UP:
            new_head[0] -= 1
        if key == curses.KEY_LEFT:
            new_head[1] -= 1
        if key == curses.KEY_RIGHT:
            new_head[1] += 1

        # Check if the head goes beyond the borders
        if new_head[0] == 0:  # Hits the top wall
            new_head[0] = sh - 2
        elif new_head[0] == sh - 1:  # Hits the bottom wall
            new_head[0] = 1
        elif new_head[1] == 0:  # Hits the left wall
            new_head[1] = sw - 2
        elif new_head[1] == sw - 1:  # Hits the right wall
            new_head[1] = 1


        # Insert the new head at the beginning of the snake list
        snake.insert(0, new_head)

        # Check if the snake eats the food
        if snake[0] == food:
            score += 1
            food = None
            while food is None:
                nf = [
                    randint(1, sh - 2),
                    randint(1, sw - 2)
                ]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        # Update the snake body
        w.addch(snake[0][0], snake[0][1], curses.ACS_CKBOARD)

        # Display the score
        w.addstr(0, sw // 2 - 4, f"Score: {score}")

    # Game over screen
    w.clear()
    w.addstr(sh // 2, sw // 2 - 5, "Game Over")
    w.addstr(sh // 2 + 1, sw // 2 - 8, f"Final Score: {score}")
    w.refresh()

    # Wait for the Enter key to continue
    while w.getch() != ord('\n'):
        pass

def get_user_input(stdscr):
    # Get default values
    sh, sw = stdscr.getmaxyx()
    default_height = min(20, sh - 2)
    default_width = min(60, sw - 2)

    # Prompt the user for input
    stdscr.addstr("Enter the size of the map (default: {}x{}): ".format(default_height, default_width))
    user_input = stdscr.getstr().decode("utf-8")

    try:
        if len(user_input) > 0:
            height, width = map(int, user_input.split("x"))
            sh = max(3, min(height, sh))
            sw = max(3, min(width, sw))
        else:
            sh = default_height
            sw = default_width
    except ValueError:
        pass

    return sh, sw

curses.wrapper(main)
