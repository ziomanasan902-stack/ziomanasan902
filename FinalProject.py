import tkinter as tk
import random
import json
import os

# -------------------- Constants --------------------
CELL, COLS, ROWS = 20, 25, 20
W, H = COLS * CELL, ROWS * CELL
HIGH_SCORE_FILE = "highscore.json"

# -------------------- Snake Class --------------------
class Snake:
    def __init__(self, start_pos):
        self._segments = [start_pos, (start_pos[0]-1, start_pos[1]), (start_pos[0]-2, start_pos[1])]
        self._direction = (1, 0)
        self._next_direction = (1, 0)

    @property
    def segments(self):
        return self._segments

    def change_direction(self, d):
        # Prevent reversing
        if (d[0]+self._direction[0], d[1]+self._direction[1]) != (0,0):
            self._next_direction = d

    def move(self):
        self._direction = self._next_direction
        hx, hy = self._segments[0]
        nx, ny = hx + self._direction[0], hy + self._direction[1]
        new_head = (nx, ny)
        # Check collision with walls or self
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS or new_head in self._segments:
            return False
        self._segments.insert(0, new_head)
        return True

    def grow(self):
        # No need to remove tail to grow
        pass

    def trim_tail(self):
        self._segments.pop()

# -------------------- Food Class --------------------
class Food:
    def __init__(self, snake):
        self.snake_ref = snake
        self.position = self.spawn()

    def spawn(self):
        while True:
            f = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
            if f not in self.snake_ref.segments:
                return f

# -------------------- Game Class --------------------
class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)
        self.root.config(bg="#111")

        self.score = 0
        self.high_score = 0
        self.alive = False
        self.job = None

        # Load high score
        self.load_high_score()

        # GUI elements
        self.score_var = tk.StringVar(value=f"Score: 0 | High Score: {self.high_score}")
        tk.Label(root, textvariable=self.score_var, bg="#111", fg="#00ff88",
                 font=("Courier New", 13, "bold"), pady=6).pack()

        self.canvas = tk.Canvas(root, width=W, height=H, bg="#0d0d0d",
                                highlightthickness=1, highlightbackground="#00ff88")
        self.canvas.pack(padx=10, pady=(0, 10))

        # Bind keys
        self.root.bind("<KeyPress>", self.key)

        self.canvas.create_text(W//2, H//2, text="SNAKE\nSPACE to start",
                                fill="#00ff88", font=("Courier New", 18, "bold"), justify="center")

    # -------------------- High Score Persistence --------------------
    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
            except:
                self.high_score = 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump({"high_score": self.high_score}, f)

    # -------------------- Game Start --------------------
    def start(self):
        if self.job:
            self.root.after_cancel(self.job)
        cx, cy = COLS//2, ROWS//2
        self.snake = Snake((cx, cy))
        self.food = Food(self.snake)
        self.score = 0
        self.alive = True
        self.update_score()
        self.loop()

    # -------------------- Game Loop --------------------
    def loop(self):
        if not self.snake.move():
            self.alive = False
            self.save_high_score()
            self.canvas.create_text(W//2, H//2,
                                    text=f"GAME OVER\nScore: {self.score}\nSPACE to restart",
                                    fill="#00ff88", font=("Courier New", 16, "bold"), justify="center")
            return

        # Check if snake eats food
        if self.snake.segments[0] == self.food.position:
            self.score += 10
            self.update_score()
            self.food = Food(self.snake)
            self.snake.grow()
        else:
            self.snake.trim_tail()

        self.draw()
        speed = max(60, 130 - self.score)
        self.job = self.root.after(speed, self.loop)

    # -------------------- Drawing --------------------
    def draw(self):
        self.canvas.delete("all")
        # Grid lines
        for x in range(0, W, CELL): self.canvas.create_line(x, 0, x, H, fill="#111111")
        for y in range(0, H, CELL): self.canvas.create_line(0, y, W, y, fill="#111111")
        # Draw food
        fx, fy = self.food.position
        self.canvas.create_oval(fx*CELL+3, fy*CELL+3, fx*CELL+CELL-3, fy*CELL+CELL-3, fill="#ff4466", outline="")
        # Draw snake
        for i, (sx, sy) in enumerate(self.snake.segments):
            color = "#00ff88" if i == 0 else "#00aa55"
            self.canvas.create_rectangle(sx*CELL+1, sy*CELL+1, sx*CELL+CELL-1, sy*CELL+CELL-1, fill=color, outline="")

    # -------------------- Score Update --------------------
    def update_score(self):
        self.score_var.set(f"Score: {self.score} | High Score: {self.high_score}")

    # -------------------- Key Press Handler --------------------
    def key(self, e):
        dirs = {"Up":(0,-1),"Down":(0,1),"Left":(-1,0),"Right":(1,0),
                "w":(0,-1),"s":(0,1),"a":(-1,0),"d":(1,0)}
        if e.keysym in dirs:
            self.snake.change_direction(dirs[e.keysym])
        if e.keysym == "space" and not self.alive:
            self.start()

# -------------------- Main --------------------
if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()