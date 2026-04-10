"""
Programmatic sound effects for Us: The Game.
All sounds generated via numpy + pygame.sndarray. No external files.
"""
import math
import numpy as np

try:
    import pygame
    import pygame.sndarray
    _SOUND_AVAILABLE = True
except ImportError:
    _SOUND_AVAILABLE = False

SAMPLE_RATE = 44100


def _ensure_mixer():
    if not _SOUND_AVAILABLE:
        return False
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        return True
    except Exception:
        return False


def _tone(freq: float, duration: float, volume: float = 0.3,
          wave: str = "sine", fade_out: float = 0.0) -> "pygame.mixer.Sound":
    """Generate a pure tone."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, dtype=np.float64)

    if wave == "sine":
        data = np.sin(2 * math.pi * freq * t)
    elif wave == "square":
        data = np.sign(np.sin(2 * math.pi * freq * t))
    elif wave == "triangle":
        data = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    else:
        data = np.sin(2 * math.pi * freq * t)

    # Envelope: quick attack, optional fade out
    env = np.ones(n)
    attack = min(int(0.005 * SAMPLE_RATE), n)
    env[:attack] = np.linspace(0, 1, attack)
    if fade_out > 0:
        fade_n = min(int(fade_out * SAMPLE_RATE), n)
        env[-fade_n:] = np.linspace(1, 0, fade_n)

    data = data * env * volume
    samples = (data * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)


def _sweep(f_start: float, f_end: float, duration: float,
           volume: float = 0.3, wave: str = "sine") -> "pygame.mixer.Sound":
    """Frequency sweep (pitch bend)."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, dtype=np.float64)
    freqs = np.linspace(f_start, f_end, n)
    phase = np.cumsum(2 * math.pi * freqs / SAMPLE_RATE)

    if wave == "sine":
        data = np.sin(phase)
    elif wave == "square":
        data = np.sign(np.sin(phase))
    else:
        data = np.sin(phase)

    # Envelope with fade out
    env = np.ones(n)
    attack = min(int(0.005 * SAMPLE_RATE), n)
    env[:attack] = np.linspace(0, 1, attack)
    fade_n = int(n * 0.3)
    env[-fade_n:] = np.linspace(1, 0, fade_n)

    data = data * env * volume
    samples = (data * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)


def _noise(duration: float, volume: float = 0.2,
           fade_in: float = 0.0, fade_out: float = 0.0) -> "pygame.mixer.Sound":
    """White noise with envelope."""
    n = int(SAMPLE_RATE * duration)
    data = np.random.uniform(-1, 1, n)

    env = np.ones(n)
    if fade_in > 0:
        fi = min(int(fade_in * SAMPLE_RATE), n)
        env[:fi] = np.linspace(0, 1, fi)
    if fade_out > 0:
        fo = min(int(fade_out * SAMPLE_RATE), n)
        env[-fo:] = np.linspace(1, 0, fo)

    data = data * env * volume
    samples = (data * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)


def _chord(freqs: list, duration: float, volume: float = 0.3,
           fade_out: float = 0.0) -> "pygame.mixer.Sound":
    """Multiple tones layered."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, dtype=np.float64)
    data = np.zeros(n)
    for f in freqs:
        data += np.sin(2 * math.pi * f * t)
    data = data / len(freqs)

    env = np.ones(n)
    attack = min(int(0.008 * SAMPLE_RATE), n)
    env[:attack] = np.linspace(0, 1, attack)
    if fade_out > 0:
        fo = min(int(fade_out * SAMPLE_RATE), n)
        env[-fo:] = np.linspace(1, 0, fo)

    data = data * env * volume
    samples = (data * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)


def _sequence(notes: list, note_dur: float, volume: float = 0.3) -> "pygame.mixer.Sound":
    """Play notes in sequence (arpeggio)."""
    parts = []
    for freq in notes:
        n = int(SAMPLE_RATE * note_dur)
        t = np.linspace(0, note_dur, n, dtype=np.float64)
        data = np.sin(2 * math.pi * freq * t)
        env = np.ones(n)
        fade = int(n * 0.3)
        env[-fade:] = np.linspace(1, 0, fade)
        parts.append(data * env)
    combined = np.concatenate(parts) * volume
    samples = (combined * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(samples)


class _NullSound:
    """Silent fallback if mixer fails."""
    def play(self): pass
    def set_volume(self, v): pass


class SFX:
    """All game sound effects, generated once at init."""
    def __init__(self):
        if not _ensure_mixer():
            self._null_init()
            return
        try:
            self._build_sounds()
        except Exception:
            self._null_init()

    def _null_init(self):
        null = _NullSound()
        for name in ["swipe", "match", "boop", "boop_sit", "boop_down",
                      "boop_middle", "boop_free", "chomp", "success", "fail",
                      "pop", "woof", "jump", "hit", "pickup", "interact",
                      "pour", "splash", "heartbeat", "celebrate"]:
            setattr(self, name, null)

    def _build_sounds(self):
        # Swipe: quick whoosh down
        self.swipe = _sweep(800, 200, 0.15, volume=0.25)

        # Match: happy rising chord
        self.match = _sequence([523, 659, 784, 1047], 0.12, volume=0.35)

        # Command sounds - each one feels like the action
        self.boop = _tone(440, 0.1, volume=0.2, wave="sine", fade_out=0.06)

        # SIT: short whistle (rising sweep, airy)
        self.boop_sit = _sweep(600, 1200, 0.15, volume=0.2, wave="sine")

        # DOWN: soft plop/thud (low tone with quick decay)
        n = int(SAMPLE_RATE * 0.15)
        t = np.linspace(0, 0.15, n, dtype=np.float64)
        plop = np.sin(2 * math.pi * 120 * t) * 0.6 + np.sin(2 * math.pi * 80 * t) * 0.4
        env = np.exp(-t * 20)  # fast decay
        plop = (plop * env * 0.3 * 32767).astype(np.int16)
        self.boop_down = pygame.sndarray.make_sound(plop)

        # MIDDLE: tippy-tap paws (3 quick clicks)
        tap_parts = []
        for i in range(3):
            click_n = int(SAMPLE_RATE * 0.03)
            click_t = np.linspace(0, 0.03, click_n, dtype=np.float64)
            click = np.sin(2 * math.pi * (800 + i * 100) * click_t) * np.exp(-click_t * 60)
            tap_parts.append(click)
            if i < 2:
                gap = np.zeros(int(SAMPLE_RATE * 0.05))
                tap_parts.append(gap)
        tap_data = np.concatenate(tap_parts) * 0.25
        tap_samples = (tap_data * 32767).astype(np.int16)
        self.boop_middle = pygame.sndarray.make_sound(tap_samples)

        # FREE button press: simple happy tone (before eating)
        self.boop_free = _tone(659, 0.1, volume=0.2, wave="sine", fade_out=0.06)

        # FREE eating: real dog slurp sound from file
        import os
        slurp_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "sounds", "dog_slurp.mp3"
        )
        if os.path.exists(slurp_path):
            self.chomp = pygame.mixer.Sound(slurp_path)
            self.chomp.set_volume(0.5)
        else:
            self.chomp = _tone(659, 0.1, volume=0.2, wave="sine", fade_out=0.06)

        # Success: ascending chime (C-E-G)
        self.success = _sequence([523, 659, 784], 0.15, volume=0.35)

        # Fail: descending buzz
        self.fail = _sweep(400, 150, 0.3, volume=0.25, wave="square")

        # Pop: quick sine burst
        self.pop = _tone(880, 0.06, volume=0.25, fade_out=0.04)

        # Woof: noise burst shaped like a bark
        n = int(SAMPLE_RATE * 0.12)
        t = np.linspace(0, 0.12, n, dtype=np.float64)
        bark = np.sin(2 * math.pi * 250 * t) * 0.5 + np.random.uniform(-0.3, 0.3, n)
        env = np.ones(n)
        env[:int(n * 0.1)] = np.linspace(0, 1, int(n * 0.1))
        env[int(n * 0.4):] = np.linspace(1, 0, n - int(n * 0.4))
        bark = (bark * env * 0.3 * 32767).astype(np.int16)
        self.woof = pygame.sndarray.make_sound(bark)

        # Jump: rising sweep
        self.jump = _sweep(250, 600, 0.12, volume=0.2)

        # Hit: thud
        self.hit = _sweep(200, 80, 0.15, volume=0.3, wave="square")

        # Pickup: sparkle ding
        self.pickup = _tone(1200, 0.1, volume=0.2, fade_out=0.06)

        # Interact: soft chime
        self.interact = _chord([660, 880], 0.2, volume=0.25, fade_out=0.15)

        # Pour: filtered noise (like liquid)
        self.pour = _noise(1.5, volume=0.12, fade_in=0.2, fade_out=0.3)

        # Splash: short noise burst
        self.splash = _noise(0.2, volume=0.25, fade_out=0.15)

        # Heartbeat: low double pulse
        beat1 = _tone(60, 0.08, volume=0.35, wave="sine", fade_out=0.05)
        # We'll just use a single pulse, played twice by the caller
        self.heartbeat = beat1

        # Celebrate: rising sweep + sparkle
        self.celebrate = _sequence([523, 659, 784, 1047, 1318], 0.1, volume=0.4)


# Global singleton - lazy init
sfx: SFX = None


def init_sounds():
    global sfx
    sfx = SFX()


def get_sfx() -> SFX:
    global sfx
    if sfx is None:
        init_sounds()
    return sfx
