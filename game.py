import curses
from random import randint
from queue import PriorityQueue

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
    def __init__(self, window, use_ai, height, width):
        self.window = window
        self.height = height
        self.width = width
        self.score = 0
        self.paused = False
        self.obstacles = []  # List to store obstacle positions
        self.use_ai = use_ai

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

        # Generate obstacles
        self.generate_obstacles()

    def generate_obstacles(self):
        num_obstacles = min(10, (self.height - 2) * (self.width - 2) // 10)  # Maximum 10% of available cells
        self.obstacles = []
        while len(self.obstacles) < num_obstacles:
            y = randint(1, self.height - 2)
            x = randint(1, self.width - 2)
            if [y, x] not in self.snake.body and [y, x] != self.food.position and [y, x] not in self.obstacles:
                self.obstacles.append([y, x])

    def handle_input(self):
        next_key = self.window.getch()

        # Handle the Space key to pause the game
        if next_key == ord(' '):
            self.paused = not self.paused
            return

        self.snake.change_direction(next_key)

    def get_valid_directions(self):
        valid_directions = []
        head = self.snake.body[0]

        # Check if the snake can move up
        if self.snake.direction != curses.KEY_DOWN and [head[0] - 1, head[1]] not in self.snake.body:
            valid_directions.append(curses.KEY_UP)

        # Check if the snake can move down
        if self.snake.direction != curses.KEY_UP and [head[0] + 1, head[1]] not in self.snake.body:
            valid_directions.append(curses.KEY_DOWN)

        # Check if the snake can move left
        if self.snake.direction != curses.KEY_RIGHT and [head[0], head[1] - 1] not in self.snake.body:
            valid_directions.append(curses.KEY_LEFT)

        # Check if the snake can move right
        if self.snake.direction != curses.KEY_LEFT and [head[0], head[1] + 1] not in self.snake.body:
            valid_directions.append(curses.KEY_RIGHT)

        return valid_directions

    def ai_control_snake(self):
        if not self.food.position or not self.snake.body:
            return

        # Find the shortest path using A* algorithm
        path = self.a_star_pathfinding(tuple(self.snake.body[0]), tuple(self.food.position))
        if path:
            next_pos = path[1]  # The first position in the path is the current position
            head = self.snake.body[0]
            direction = self.get_direction(head, next_pos)
            self.snake.change_direction(direction)

    def get_direction(self, current_pos, next_pos):
        y_diff = current_pos[0] - next_pos[0]
        x_diff = current_pos[1] - next_pos[1]

        if y_diff == 1:  # Move up
            return curses.KEY_UP
        elif y_diff == -1:  # Move down
            return curses.KEY_DOWN
        elif x_diff == 1:  # Move left
            return curses.KEY_LEFT
        elif x_diff == -1:  # Move right
            return curses.KEY_RIGHT

    def heuristic(self, pos1, pos2):
        # Calculate the Manhattan distance as the heuristic
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def a_star_pathfinding(self, start_pos, goal_pos):
        open_set = PriorityQueue()
        open_set.put((0, start_pos))
        came_from = {}
        g_score = {start_pos: 0}
        f_score = {start_pos: self.heuristic(start_pos, goal_pos)}

        while not open_set.empty():
            current = open_set.get()[1]

            if current == goal_pos:
                # Reconstruct the path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                temp_g_score = g_score[current] + 1  # Cost of moving to a neighbor is 1

                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + self.heuristic(neighbor, goal_pos)
                    open_set.put((f_score[neighbor], neighbor))

        return []

    def get_neighbors(self, position):
        neighbors = []
        directions = [
            (0, -1),  # Left
            (0, 1),   # Right
            (-1, 0),  # Up
            (1, 0)    # Down
        ]

        for direction in directions:
            neighbor = (position[0] + direction[0], position[1] + direction[1])
            if self.is_valid_position(neighbor):
                neighbors.append(neighbor)

        return neighbors

    def is_valid_position(self, position):
        # Check if the position is within the game boundaries and not colliding with obstacles or snake body
        if (
            position[0] >= 0 and position[0] < self.height and
            position[1] >= 0 and position[1] < self.width and
            position not in self.obstacles and
            position not in self.snake.body
        ):
            return True
        return False

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
        if self.snake.collided_with_self() or self.snake.body[0] in self.obstacles:
            return False
        # Check if the snake ate the food
        if self.snake.body[0] == self.food.position:
            self.score += 1
            self.snake.body.append(self.snake.body[-1][:])  # Grow the snake
            self.food.generate(self.height, self.width, self.snake)

            # Generate new obstacles after eating the food
            self.generate_obstacles()

        return True

    def draw(self):
        self.window.clear()
        self.window.border(0)
        # Draw obstacles
        for obstacle in self.obstacles:
            self.window.addch(obstacle[0], obstacle[1], "#")
        self.food.draw()
        self.snake.draw()
        self.window.addstr(0, self.width // 2 - 4, f"Score: {self.score}")

    def game_loop(self):
        while True:
            self.handle_input()
            if not self.update():
                break
            if self.use_ai:
                self.ai_control_snake()
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
    stdscr.addstr("Use AI or not? (Y/N)")
    user_input = stdscr.getstr().decode("utf-8")
    use_ai = user_input.lower() == "y"
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

    return use_ai, sh, sw

def main(stdscr):
    use_ai, sh, sw = get_user_input(stdscr)
    window = curses.newwin(sh, sw, 0, 0)
    game = SnakeGame(window, use_ai, sh, sw)
    game.run()

curses.wrapper(main)
