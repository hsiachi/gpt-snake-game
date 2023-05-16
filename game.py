import curses
from random import randint

class Snake:
    def __init__(self, window, y, x):
        self.window = window
        self.body = [[y, x], [y, x - 1], [y, x - 2]]
        self.direction = curses.KEY_RIGHT
        self.grow = False

    def move(self):
        head = self.body[0][:]
        if self.direction == curses.KEY_DOWN:
            head[0] += 1
        elif self.direction == curses.KEY_UP:
            head[0] -= 1
        elif self.direction == curses.KEY_LEFT:
            head[1] -= 1
        elif self.direction == curses.KEY_RIGHT:
            head[1] += 1
        self.body.insert(0, head)

        if not self.grow:
            self.window.addch(self.body[-1][0], self.body[-1][1], " ")
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, direction):
        if (
            direction == curses.KEY_DOWN and self.direction != curses.KEY_UP or
            direction == curses.KEY_UP and self.direction != curses.KEY_DOWN or
            direction == curses.KEY_LEFT and self.direction != curses.KEY_RIGHT or
            direction == curses.KEY_RIGHT and self.direction != curses.KEY_LEFT
        ):
            self.direction = direction

    def draw(self):
        for y, x in self.body:
            self.window.addch(y, x, curses.ACS_CKBOARD)

    def collided_with_border(self, sh, sw):
        y, x = self.body[0]
        return y in [0, sh - 1] or x in [0, sw - 1]

    def collided_with_self(self):
        head = self.body[0]
        return head in self.body[1:]

    def ate_food(self, food_position):
        return self.body[0] == food_position

    def grow_snake(self):
        self.grow = True

class Food:
    def __init__(self, window, y, x):
        self.window = window
        self.position = [y, x]

    def generate(self, sh, sw, snake):
        while True:
            y = randint(1, sh - 2)
            x = randint(1, sw - 2)
            if [y, x] not in snake.body:
                break
        self.position = [y, x]

    def draw(self):
        self.window.addch(self.position[0], self.position[1], curses.ACS_PI)

class SnakeGame:
    def __init__(self, window, height, width):
        self.window = window
        self.height = height
        self.width = width
        self.score = 0
        self.paused = False

    def setup(self):
        curses.curs_set(0)
        self.window.keypad(1)
        self.window.timeout(100)
        self.window.border(0)

        # Initialize the snake
        snake_x = self.width // 4
        snake_y = self.height // 2
        self.snake = Snake(self.window, snake_y, snake_x)

        # Initialize the food
        food_x = self.width // 2
        food_y = self.height // 2
        self.food = Food(self.window, food_y, food_x)

    def handle_input(self):
        next_key = self.window.getch()

        # Handle the Space key to pause the game
        if next_key == ord(' '):
            self.paused = not self.paused
            return

        self.snake.change_direction(next_key)

    def update(self):
        if self.paused:
            return True

        self.snake.move()

        # Check if the snake collided with the border
        if self.snake.collided_with_border(self.height, self.width):
            # Wrap the snake to the opposite side
            head = self.snake.body[0]
            if head[0] == 0:
                head[0] = self.height - 2
            elif head[0] == self.height - 1:
                head[0] = 1
            elif head[1] == 0:
                head[1] = self.width - 2
            elif head[1] == self.width - 1:
                head[1] = 1

        # Check if the snake collided with itself
        if self.snake.collided_with_self():
            return False
        # Check if the snake ate the food
        if self.snake.body[0] == self.food.position:
            self.score += 1
            self.snake.body.append(self.snake.body[-1][:])  # Grow the snake
            self.food.generate(self.height, self.width, self.snake)

        return True

    def draw(self):
        self.window.clear()
        self.window.border(0)
        self.food.draw()
        self.snake.draw()
        self.window.addstr(0, self.width // 2 - 4, f"Score: {self.score}")

    def game_loop(self):
        while True:
            self.handle_input()
            if not self.update():
                break
            self.draw()
            self.window.refresh()

    def game_over_screen(self):
        self.window.clear()
        self.window.addstr(self.height // 2, self.width // 2 - 5, "Game Over")
        self.window.addstr(self.height // 2 + 1, self.width // 2 - 8, f"Final Score: {self.score}")
        self.window.refresh()

        # Wait for the Enter key to continue
        while self.window.getch() != ord('\n'):
            pass

    def run(self):
        self.setup()
        self.game_loop()
        self.game_over_screen()

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

def main(stdscr):
    sh, sw = get_user_input(stdscr)
    window = curses.newwin(sh, sw, 0, 0)
    game = SnakeGame(window, sh, sw)
    game.run()

curses.wrapper(main)
