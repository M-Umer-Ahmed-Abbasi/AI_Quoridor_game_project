import tkinter as tk
from tkinter import messagebox, simpledialog
from quoridor_game import QuoridorGame
import time

cellSize = 40
boardSize = 13
wallThickness = 8

class QuoridorInterface:
    def __init__(self, root, humanPlayers):
        self.root = root
        self.root.title("Quoridor Game")
        self.game = QuoridorGame(humanPlayers)
        self.canvas = tk.Canvas(root, width=cellSize*boardSize + wallThickness*2,
                                height=cellSize*boardSize + wallThickness*2 + 50, bg='white')
        self.canvas.pack()
        self.selectedCell = None
        self.wallMode = None
        self.ghostWall = None
        self.hoverCell = None
        self.startTime = time.time()

        self.turnLabel = tk.Label(root, text="", font=("Helvetica", 12))
        self.turnLabel.pack(pady=5)

        self.instructions = tk.Label(root, text="Press 'H' or 'V' to enter wall mode. Click to place. ESC to cancel.", font=("Helvetica", 10))
        self.instructions.pack()

        self.timerLabel = tk.Label(root, text="", font=("Helvetica", 10))
        self.timerLabel.pack()

        self.helpBtn = tk.Button(root, text="?", command=self.showInstructions, font=("Helvetica", 12))
        self.helpBtn.pack(pady=5)

        self.canvas.bind("<Button-1>", self.handleClick)
        self.canvas.bind("<Motion>", self.handleHover)
        self.root.bind("<KeyPress-h>", lambda e: self.setWallMode('h'))
        self.root.bind("<KeyPress-v>", lambda e: self.setWallMode('v'))
        self.root.bind("<Escape>", lambda e: self.setWallMode(None))

        self.drawBoard()
        self.updateTurnInfo()
        self.updateTimer()
        self.root.after(500, self.aiPlay)

    def setWallMode(self, mode):
        self.wallMode = mode
        self.selectedCell = None
        self.ghostWall = None
        self.hoverCell = None
        self.updateTurnInfo()
        self.drawBoard()

    def showInstructions(self):
        msg = (
            "📜 How to Play Quoridor (4-Player Edition):\n\n"
            "🎯 Objective:\nReach the opposite side of the board before your opponents.\n\n"
            "🚶 Movement:\n- On your turn, move your pawn to an adjacent cell.\n- You can jump over adjacent players if the cell behind them is empty.\n- If blocked, you may move diagonally.\n\n"
            "🧱 Walls:\n- Press 'H' (horizontal) or 'V' (vertical) to enter wall placement mode.\n- Walls must not block all paths for any player.\n- You have a limited number of walls.\n\n"
            "🔁 Turns:\n- Players take turns in clockwise order (Player 1 to 4).\n- You’ll see ‘my turn’ next to your pawn when it’s your move.\n\n"
            "🎮 Game made by:\n- Muhammad Umer Ahmed Abbasi (22K-4599)\n- Jawwad Ahmed (22K-4648)\n- Muhammad Talha Asim (22K-4589)\nSection: BCS-6C | Course: AI\n"
        )
        messagebox.showinfo("How to Play", msg)

    def handleClick(self, event):
        x = (event.x - wallThickness) // cellSize
        y = (event.y - wallThickness) // cellSize
        if 0 <= x < boardSize and 0 <= y < boardSize:
            self.selectedCell = (x, y)
            if self.wallMode:
                self.tryWallPlacement(event.x, event.y)
            else:
                self.tryPlayerMove(x, y)
            self.drawBoard()

    def handleHover(self, event):
        x = (event.x - wallThickness) // cellSize
        y = (event.y - wallThickness) // cellSize
        if not self.wallMode:
            self.hoverCell = (x, y)
        else:
            self.ghostWall = None
            offsetX = (event.x - wallThickness) % cellSize
            offsetY = (event.y - wallThickness) % cellSize
            if self.wallMode == 'h' and offsetY > cellSize // 2:
                y += 1
            if self.wallMode == 'v' and offsetX > cellSize // 2:
                x += 1
            self.ghostWall = (self.wallMode, x, y)
        self.drawBoard()

    def tryPlayerMove(self, x, y):
        currentPlayer = self.game.activeTurn
        if self.game.players[currentPlayer]['type'] == 'human':
            if (x, y) in self.game.getLegalMoves(currentPlayer):
                self.game.players[currentPlayer]['pos'] = (x, y)
                if self.game.checkWin(currentPlayer):
                    self.drawBoard()
                    messagebox.showinfo("Game Over", f"Player {currentPlayer} wins!")
                    self.root.quit()
                    return
                self.advanceTurn()

    def tryWallPlacement(self, px, py):
        x = (px - wallThickness) // cellSize
        y = (py - wallThickness) // cellSize
        offsetX = (px - wallThickness) % cellSize
        offsetY = (py - wallThickness) % cellSize
        if self.wallMode == 'h' and offsetY > cellSize // 2:
            y += 1
        if self.wallMode == 'v' and offsetX > cellSize // 2:
            x += 1

        currentPlayer = self.game.activeTurn
        if self.game.players[currentPlayer]['type'] == 'human':
            if self.game.isWallValid(self.wallMode, x, y):
                self.game.applyMove(currentPlayer, ('wall', (self.wallMode, x, y)))
                self.wallMode = None
                self.ghostWall = None
                self.selectedCell = None
                if self.game.checkWin(currentPlayer):
                    self.drawBoard()
                    messagebox.showinfo("Game Over", f"Player {currentPlayer} wins!")
                    self.root.quit()
                    return
                self.advanceTurn()
            else:
                messagebox.showwarning("Invalid Wall", "Wall cannot be placed here.")

    def aiPlay(self):
        currentPlayer = self.game.activeTurn
        if self.game.players[currentPlayer]['type'] == 'ai':
            move = self.game.aiAgents[currentPlayer].getBestAction(self.game)
            if move is None:
                messagebox.showwarning("AI Error", f"Player {currentPlayer} has no valid moves!")
                self.advanceTurn()
                return
            self.game.applyMove(currentPlayer, move)
            if self.game.checkWin(currentPlayer):
                self.drawBoard()
                messagebox.showinfo("Game Over", f"Player {currentPlayer} wins!")
                self.root.quit()
                return
            self.advanceTurn()

    def advanceTurn(self):
        self.game.activeTurn = self.game.activeTurn % 4 + 1
        self.selectedCell = None
        self.wallMode = None
        self.ghostWall = None
        self.hoverCell = None
        self.drawBoard()
        self.updateTurnInfo()
        self.root.after(500, self.aiPlay)

    def updateTurnInfo(self):
        currentPlayer = self.game.activeTurn
        playerType = self.game.players[currentPlayer]['type']
        wallNote = f" | Wall Mode: {'Horizontal' if self.wallMode == 'h' else 'Vertical' if self.wallMode == 'v' else 'OFF'}"
        self.turnLabel.config(text=f"Player {currentPlayer}'s turn ({playerType.upper()}){wallNote}")

    def updateTimer(self):
        elapsed = int(time.time() - self.startTime)
        mins, secs = divmod(elapsed, 60)
        self.timerLabel.config(text=f"Time Elapsed: {mins:02}:{secs:02}")
        self.root.after(1000, self.updateTimer)

    def drawBoard(self):
        self.canvas.delete("all")
        for i in range(boardSize):
            for j in range(boardSize):
                x0 = i * cellSize + wallThickness
                y0 = j * cellSize + wallThickness
                x1 = x0 + cellSize
                y1 = y0 + cellSize
                fill = "white"
                if self.selectedCell == (i, j) and self.wallMode:
                    fill = "lightyellow"
                elif self.hoverCell == (i, j) and not self.wallMode:
                    currentPlayer = self.game.activeTurn
                    if self.game.players[currentPlayer]['type'] == 'human':
                        if (i, j) in self.game.getLegalMoves(currentPlayer):
                            fill = "#ccffcc"
                        else:
                            fill = "#ffcccc"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="black")

        for pid, pdata in self.game.players.items():
            x, y = pdata['pos']
            x0 = x * cellSize + wallThickness + cellSize//4
            y0 = y * cellSize + wallThickness + cellSize//4
            x1 = x0 + cellSize//2
            y1 = y0 + cellSize//2
            color = ["blue", "red", "green", "orange"][pid - 1]
            self.canvas.create_oval(x0, y0, x1, y1, fill=color)

            wx = x * cellSize + wallThickness + cellSize//2
            wy = y * cellSize + wallThickness + cellSize + 2
            self.canvas.create_text(wx, wy, text=f"W: {pdata['walls']}", fill=color, font=("Helvetica", 9))

            if pid == self.game.activeTurn and pdata['type'] == 'human':
                self.canvas.create_text(wx, wy + 12, text="my turn", fill=color, font=("Helvetica", 8, "italic"))

        for (ori, x, y) in self.game.horizontalWalls:
            x0 = x * cellSize + wallThickness
            y0 = y * cellSize + wallThickness + cellSize - wallThickness // 2
            x1 = x0 + cellSize
            y1 = y0 + wallThickness
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="saddlebrown")

        for (ori, x, y) in self.game.verticalWalls:
            x0 = x * cellSize + wallThickness + cellSize - wallThickness // 2
            y0 = y * cellSize + wallThickness
            x1 = x0 + wallThickness
            y1 = y0 + cellSize
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="saddlebrown")

        if self.ghostWall and self.wallMode:
            ori, x, y = self.ghostWall
            color = "#deb887"
            if ori == 'h':
                x0 = x * cellSize + wallThickness
                y0 = y * cellSize + wallThickness + cellSize - wallThickness // 2
                x1 = x0 + cellSize
                y1 = y0 + wallThickness
            else:
                x0 = x * cellSize + wallThickness + cellSize - wallThickness // 2
                y0 = y * cellSize + wallThickness
                x1 = x0 + wallThickness
                y1 = y0 + cellSize
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, stipple="gray50")

if __name__ == "__main__":
    root = tk.Tk()
    numHumans = simpledialog.askinteger("Choose Players", "Enter number of human players (1-4):", minvalue=1, maxvalue=4)
    humanPlayers = list(range(1, numHumans + 1))
    app = QuoridorInterface(root, humanPlayers)
    root.mainloop()
