# ============================================================
#  RUN OR DONT IT - procedural sound synthesis
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
#
#  Generates the default WAVs on first launch (pure Python, no deps).
#  Any file you drop into assets/sounds overrides these.
# ============================================================
import math
import os
import random
import struct
import wave

RATE = 22050


def _write(path, samples, rate=RATE):
    clamped = [max(-1.0, min(1.0, s)) for s in samples]
    with wave.open(path, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes(b''.join(struct.pack('<h', int(s * 32000)) for s in clamped))


def _loop_crossfade(samples, seconds=0.5):
    """Blend the tail into the head so the loop has no audible seam."""
    fade = int(RATE * seconds)
    if len(samples) > fade * 2:
        for i in range(fade):
            a = i / fade
            samples[-fade + i] = samples[-fade + i] * a + samples[i] * (1 - a)
    return samples


def gen_ambience(path):
    n = int(RATE * 10)
    rng = random.Random(7)
    out = []
    for i in range(n):
        t = i / RATE
        rumble = 0.12 * math.sin(2 * math.pi * 32 * t) * (0.6 + 0.4 * math.sin(2 * math.pi * 0.05 * t))
        wind = 0.06 * (rng.random() * 2 - 1) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.03 * t))
        out.append(rumble + wind)
    _write(path, _loop_crossfade(out))


def gen_heartbeat(path):
    n = int(RATE * 1.1)
    out = [0.0] * n
    for start, amp in ((0.0, 1.0), (0.34, 0.75)):
        s = int(start * RATE)
        for i in range(int(0.16 * RATE)):
            t = i / RATE
            env = math.exp(-t * 22)
            out[s + i] += amp * env * math.sin(2 * math.pi * 52 * t)
    _write(path, _loop_crossfade(out, 0.2))


def gen_footstep(path):
    n = int(RATE * 0.11)
    rng = random.Random(3)
    out = []
    for i in range(n):
        t = i / RATE
        env = math.exp(-t * 38)
        noise = rng.random() * 2 - 1
        thump = 0.5 * math.sin(2 * math.pi * 78 * t)
        out.append(env * (0.7 * noise + thump))
    _write(path, out)


def gen_slide(path):
    n = int(RATE * 0.45)
    rng = random.Random(5)
    out = []
    prev = 0.0
    for i in range(n):
        t = i / RATE
        env = math.sin(min(1.0, t / 0.45) * math.pi)
        prev = prev * 0.88 + (rng.random() * 2 - 1) * 0.12   # low-passed noise = whoosh
        out.append(env * prev * 1.5)
    _write(path, out)


def gen_scream(path):
    n = int(RATE * 1.6)
    rng = random.Random(11)
    out = []
    for i in range(n):
        t = i / RATE
        f = 780 - 420 * (t / 1.6) + 40 * math.sin(2 * math.pi * 6 * t)
        env = min(1.0, t * 8) * math.exp(-t * 1.1)
        raw = math.sin(2 * math.pi * f * t)
        dist = math.copysign(abs(raw) ** 0.6, raw)   # distortion
        noise = (rng.random() * 2 - 1) * 0.35
        out.append(env * (0.8 * dist + noise))
    _write(path, out)


def gen_jumpscare(path):
    n = int(RATE * 1.1)
    rng = random.Random(13)
    out = []
    for i in range(n):
        t = i / RATE
        boom = 0.9 * math.exp(-t * 4) * math.sin(2 * math.pi * 46 * t)
        screech = 0.0
        if t < 0.5:
            f = max(40.0, 1500 - 2600 * t)
            raw = math.sin(2 * math.pi * f * t)
            screech = 0.8 * math.exp(-t * 5) * math.copysign(abs(raw) ** 0.5, raw)
        burst = 1.0 * math.exp(-t * 16) * (rng.random() * 2 - 1)
        out.append(max(-1.0, min(1.0, boom + screech + burst)))
    _write(path, out)


def gen_hide(path):
    n = int(RATE * 0.5)
    out = []
    for i in range(n):
        t = i / RATE
        thud = math.exp(-t * 14) * math.sin(2 * math.pi * 70 * t) * 0.8
        creak = 0.2 * math.sin(2 * math.pi * (300 - 240 * t) * t) if t < 0.3 else 0.0
        out.append(thud + creak)
    _write(path, out)


_GENERATORS = {
    'ambience.wav': gen_ambience,
    'heartbeat.wav': gen_heartbeat,
    'footstep.wav': gen_footstep,
    'slide.wav': gen_slide,
    'scream.wav': gen_scream,
    'jumpscare.wav': gen_jumpscare,
    'hide.wav': gen_hide,
}


def ensure_all(folder):
    os.makedirs(folder, exist_ok=True)
    for name, fn in _GENERATORS.items():
        p = os.path.join(folder, name)
        if not os.path.exists(p):
            fn(p)
