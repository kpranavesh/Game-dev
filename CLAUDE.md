# CLAUDE.md — Game Dev Workspace

_Built for Vandita's birthday — April 10, 2026._
_Desktop/laptop game. Solo build. Claude Code + Python._

---

## The Game

**Title:** TBD
**Genre:** TBD
**One-liner:** TBD

<!-- Fill this in as the idea solidifies -->

---

## About Vandita (Player Profile)

- Wife. Works in ML.
- [ ] Favorite things / interests:
- [ ] Humor style:
- [ ] Games she's played or enjoyed:
- [ ] Inside jokes or references to include:
- [ ] Things that would make her laugh:
- [ ] Things that would make her feel seen:

---

## Game Concept

<!-- Describe the core loop, win condition, and feel of the game -->

**Core mechanic:**

**Win condition:**

**Tone:** (funny / heartfelt / chaotic / puzzle-y / etc.)

**Personalization hooks:** (how Vandita's personality shows up in the game)

---

## Tech Stack

- **Language:** Python
- **Game library:** Pygame (default — change if needed)
- **Assets:** Custom drawn / free asset packs / AI-generated
- **Distribution:** Packaged as standalone executable (PyInstaller)
- **Target OS:** macOS / Windows

---

## Folder Structure

```
Game-dev/
├── CLAUDE.md                  ← this file
├── docs/
│   └── game-design.md         ← full game design doc (GDD)
├── assets/
│   ├── images/                ← sprites, backgrounds, UI
│   ├── sounds/                ← music, SFX
│   └── fonts/                 ← custom fonts
├── src/
│   ├── main.py                ← entry point
│   ├── game.py                ← core game loop
│   ├── scenes/                ← title screen, gameplay, end screen
│   ├── entities/              ← player, NPCs, objects
│   └── utils/                 ← helpers, constants, config
├── levels/                    ← level data / maps
├── requirements.txt
└── .gitignore
```

---

## Build Timeline

**Deadline: April 10, 2026** (~6 weeks)

| Week | Goal |
|------|------|
| Week 1 | Finalize game design doc. Core mechanic working. |
| Week 2 | Art style decided. Basic assets in. Level 1 playable. |
| Week 3 | Full game loop working (start → play → end screen). |
| Week 4 | Personalization layer complete (Vandita-specific content). |
| Week 5 | Polish — sound, animations, feel. |
| Week 6 | Packaging + final playtesting. Wrap it. |

---

## Design Principles

- **Personal > polished.** A glitchy game with 10 inside jokes beats a smooth generic one.
- **Short is better.** Target 5–15 minutes of play. She shouldn't need a tutorial.
- **She should laugh at least once in the first 30 seconds.**
- **End screen matters most.** Whatever the game, the ending should be a moment — not just "you win."

---

## Code Conventions

- One file per scene (`title_screen.py`, `gameplay.py`, `end_screen.py`)
- Constants in `utils/constants.py`
- No inline magic numbers
- `python src/main.py` always starts the game
