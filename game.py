import curses
from random import randint

# Initialize the screen
stdscr = curses.initscr()
curses.curs_set(0)
sh, sw = stdscr.getmaxyx()
w = curses.newwin(sh, sw, 0, 0)
w.keypad(1)
w.timeout(100)

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

# Game loop
while True:
    next_key = w.getch()
    key = key if next_key == -1 else next_key

    # Check if the snake hits the wall or itself
    if (
        snake[0][0] in [0, sh] or
        snake[0][1] in [0, sw] or
        snake[0] in snake[1:]
    ):
        curses.endwin()
        quit()

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

    # Insert the new head at the beginning of the snake list
    snake.insert(0, new_head)

    # Check if the snake eats the food
    if snake[0] == food:
        score += 1
        food = None
        while food is None:
            nf = [
                randint(1, sh - 1),
                randint(1, sw - 1)
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
