from dataclasses import dataclass
from typing import Tuple


@dataclass
class Profile:
    name: str
    age: int
    job: str
    bio: str
    is_krishna: bool
    hair_color: Tuple[int, int, int]
    skin_color: Tuple[int, int, int]
    hair_style: int  # 0-4
    emoji: str


PROFILES = [
    Profile(
        name="Brad",
        age=31,
        job="Crypto Enthusiast 🚀",
        bio='"Number go up. Portfolio go brr."',
        is_krishna=False,
        hair_color=(200, 165, 90),
        skin_color=(250, 215, 178),
        hair_style=2,
        emoji="📈",
    ),
    Profile(
        name="Tyler",
        age=27,
        job="Life Coach & Influencer",
        bio='"I don\'t own a TV. I experience life."',
        is_krishna=False,
        hair_color=(215, 180, 110),
        skin_color=(255, 220, 185),
        hair_style=1,
        emoji="✨",
    ),
    Profile(
        name="Krishna",
        age=28,
        job="Product Manager 📊",
        bio='"Will make you a spreadsheet for our first date."',
        is_krishna=True,
        hair_color=(40, 28, 15),
        skin_color=(200, 158, 115),
        hair_style=4,
        emoji="💡",
    ),
    Profile(
        name="Chad",
        age=29,
        job="Dog Whisperer 🐕",
        bio='"I only date left-handed people. Dealbreaker."',
        is_krishna=False,
        hair_color=(165, 120, 55),
        skin_color=(248, 212, 175),
        hair_style=0,
        emoji="🐾",
    ),
    Profile(
        name="Dev",
        age=30,
        job="Startup Founder",
        bio='"We\'re disrupting the disruption space."',
        is_krishna=False,
        hair_color=(50, 35, 22),
        skin_color=(205, 162, 120),
        hair_style=3,
        emoji="💼",
    ),
]
