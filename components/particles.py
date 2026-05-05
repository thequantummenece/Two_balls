"""Particle effects: bursts, confetti, floating bubbles, ball trails."""

import random
import math
from collections import deque
import pygame
from config.settings import PARTICLE_GRAVITY, PARTICLE_DRAG


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "color", "life", "max_life", "size")

    def __init__(self, x, y, vx, vy, color, life, size=3):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = max(1, life)
        self.max_life = self.life
        self.size = size


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_burst(self, x, y, color, count=20, speed=3.0, life=40):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.3, speed)
            c = tuple(max(0, min(255, ch + random.randint(-30, 30))) for ch in color)
            self.particles.append(Particle(
                x, y, math.cos(angle) * spd, math.sin(angle) * spd,
                c, life + random.randint(-10, 10), size=random.randint(2, 5),
            ))

    def emit_confetti(self, w, h, count=60):
        colors = [(255, 105, 180), (0, 100, 255), (0, 255, 100),
                  (255, 255, 0), (255, 140, 0), (180, 100, 255)]
        for _ in range(count):
            self.particles.append(Particle(
                random.uniform(0, w), random.uniform(-40, -5),
                random.uniform(-1.0, 1.0), random.uniform(1.5, 4.0),
                random.choice(colors), random.randint(80, 140), size=random.randint(3, 6),
            ))

    def update(self):
        alive = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += PARTICLE_GRAVITY
            p.vx *= PARTICLE_DRAG
            p.life -= 1
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surface):
        for p in self.particles:
            alpha = max(0.0, p.life / p.max_life)
            r = max(1, int(p.size * alpha))
            color = tuple(max(0, min(255, int(c * alpha))) for c in p.color)
            pygame.draw.circle(surface, color, (int(p.x), int(p.y)), r)

    def clear(self):
        self.particles.clear()


class Bubble:
    __slots__ = ("x", "y", "radius", "vx", "vy", "color", "alpha", "phase")

    def __init__(self, x, y, radius, vx, vy, color, alpha, phase):
        self.x, self.y, self.radius = x, y, radius
        self.vx, self.vy = vx, vy
        self.color, self.alpha, self.phase = color, alpha, phase


class FloatingBubbles:
    COLORS = [(255, 105, 180), (0, 100, 255), (100, 220, 100),
              (100, 180, 255), (255, 100, 100)]

    def __init__(self, w, h, count=25):
        self.respawn_w, self.respawn_h = w, h
        self.bubbles = [self._make(w, h) for _ in range(count)]

    def _make(self, w, h, bottom=False):
        return Bubble(
            random.uniform(0, w),
            (h + random.uniform(0, 20)) if bottom else random.uniform(0, h),
            random.uniform(4, 14), random.uniform(-0.3, 0.3),
            random.uniform(-0.6, -0.15), random.choice(self.COLORS),
            random.uniform(0.15, 0.4), random.uniform(0, 2 * math.pi),
        )

    def resize(self, w, h):
        self.respawn_w, self.respawn_h = w, h

    def update(self, tick):
        for b in self.bubbles:
            b.x += b.vx + math.sin(tick * 0.02 + b.phase) * 0.3
            b.y += b.vy
            if b.y + b.radius < 0:
                n = self._make(self.respawn_w, self.respawn_h, bottom=True)
                b.x, b.y = n.x, n.y

    def draw(self, surface):
        for b in self.bubbles:
            c = tuple(max(0, min(255, int(ch * b.alpha))) for ch in b.color)
            pygame.draw.circle(surface, c, (int(b.x), int(b.y)), int(b.radius))


class BallTrail:
    def __init__(self, color, max_length=12):
        self.color = color
        self.positions = deque(maxlen=max_length)

    def add(self, px, py, radius):
        self.positions.append((px, py, radius))

    def draw(self, surface):
        n = len(self.positions)
        for i, (px, py, radius) in enumerate(self.positions):
            t = (i + 1) / (n + 1)
            blend = 0.15 + 0.25 * t
            color = tuple(max(0, min(255, int(c * blend + 255 * (1 - blend)))) for c in self.color)
            r = max(1, int(radius * (0.5 + 0.5 * t)))
            pygame.draw.circle(surface, color, (px, py), r)

    def clear(self):
        self.positions.clear()
