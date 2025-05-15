# AI_Quoridor_game_project

An intelligent and interactive 4-player version of the strategic board game **Quoridor**, built with Python and Tkinter. This project demonstrates **Minimax algorithm with Alpha-Beta pruning** in a dynamic, adversarial, multi-agent environment.

---

## 🎮 Game Description

**Quoridor** is a pathfinding strategy game where players race to reach the opposite side of the board while placing walls to block opponents — without completely trapping them. Our version enhances this classic:

- 🧩 **Supports 1–4 players** (Human or AI-controlled)
- 🧱 **Wall placement logic** with ghost preview, validation, and visual feedback
- 🔁 **Turn-based logic** with “my turn” indicators
- 🧠 **AI decision-making** using Minimax with Alpha-Beta pruning
- ⏱️ **Real-time timer** and wall counters for each player

---

## 🧑‍💻 How to Play

- 🔵 **Move**: Click an adjacent cell to move your pawn.
- 🧱 **Place Walls**:
  - Press `H` for **horizontal** wall mode
  - Press `V` for **vertical** wall mode
  - Click to place wall along cell boundary
- ❌ Press `ESC` to exit wall mode
- 🏁 First player to reach their **goal side** wins!

> You must **not block all paths** with your wall placement.

---

## 🚀 Getting Started

### 📦 Requirements

- Python 3.8+
- Tkinter (usually bundled with Python)

### ▶️ Run the Game

```bash
python quoridor_gui.py
