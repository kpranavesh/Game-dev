# CLAUDE.md — Game Dev Workspace

_Built for Vandita's birthday — April 10, 2026._
_Desktop/laptop game. Solo build. Claude Code + Python._

---

## The Game

**Title:** TBD (working title: *Us: The Game*)
**Genre:** Narrative mini-game anthology / casual adventure
**One-liner:** A 10-level re-enactment of how Krishna and Vandita met, fell in love, and built a life together — played as a birthday gift.

---

## About Vandita (Player Profile)

- Wife. Works in ML.
- **Games she loves:** Overcooked, It Takes Two — cozy, charming, story-driven, slightly chaotic
- **Tone she responds to:** Warm + funny. Heartfelt but not sappy. Self-aware humor works.
- **What will make her laugh:** References to real moments, Krishna being portrayed accurately (flawed, loveable), Beans being a main character
- **What will make her feel seen:** The small details — the real story told right, not a generic love story
- **Inside jokes / references to fill in:**
  - [ ] How they matched on Hinge (details?)
  - [ ] First date location / what happened
  - [ ] How Krishna asked her to be his girlfriend
  - [ ] Friend group details
  - [ ] Family intro moments
  - [ ] Move-in chaos
  - [ ] The proposal story
  - [ ] Wedding details
  - [ ] Beans — breed, personality, funny habits

---

## Game Concept

**Format:** 10 levels, each a short self-contained mini-game with its own mechanic. Shared visual style and characters throughout. Plays like a love letter disguised as a game.

**Tone:** Warm, funny, slightly chaotic — Overcooked energy but no stress. She should smile constantly and cry a little at the end.

**Win condition:** Complete all 10 levels and unlock a final cutscene / message.

**Personalization hooks:** Real names, real places, real moments. Beans as a recurring character. krishna portrayed as himself — charming but a little ridiculous.

---

## Levels

4-5 levels about Vandita. 3 levels about their life together.

| # | Title | About | Mechanic | Status |
|---|-------|-------|----------|--------|
| 1 | **Swipe Right** | Together | Swipe left/right on Hinge profiles — find Krishna among decoys | ✅ Built |
| 2 | **Good Girl, Beans** | Vandita — her border collie | Simon Says: watch command sequence, repeat it | ✅ Built |
| 3 | **Yarn Crisis** | Vandita — crocheting | Catch falling yarn balls, don't let Beans steal them | 🔒 Next |
| 4 | **Code & Deploy** | Vandita — Reddit SWE | Spot the bug in the PR before it goes to prod | 🔒 |
| 5 | **Beans at the Park** | Vandita + Beans | Border collie fetch chaos — throw the ball, Beans retrieves | 🔒 |
| 6 | **Will You Be Mine?** | Together | Dialogue choice puzzle — pick exactly the right words | 🔒 |
| 7 | **The Proposal** | Together | Set up the perfect scene — arrange all the pieces | 🔒 |
| 8 | **Home** | Together | Place family photos, unlock the ending cutscene | 🔒 |

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
