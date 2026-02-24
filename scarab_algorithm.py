"""
Scarab Algorithm — Controlled Chaos Movement Generator
Based on Kryukov's deformed figure-8 and ETD movement archetypes.

Two prohibitions:
  1. Anti-circle: cannot turn same direction > 4 steps (predictable loop)
  2. Anti-line: cannot go straight > 3 steps (hits boundary)

Rules:
  - Series lengths must be odd: {1, 3, 5, 7}
  - Turn angle = π/4 (45° = LCI optimal)
  - Deformation parameter k = ratio of two loops
  - Four nested levels (four spheres):
      BVS (shoulder/body):  3D, Earth, strategy    (~seconds)
      SVS (elbow/forearm):  2D, Water, tactics     (~100ms)
      MVS (wrist/hand):     1D, Air,   technique   (~50ms)
      ChVS (fingers):       0D, Fire,  correction  (~10ms)
"""

import math
import random


def scarab_2d(space_size=10.0, k=1.0, steps=200, seed=None):
    """
    Generate a 2D trajectory using the Scarab algorithm.

    Args:
        space_size: radius of bounded space
        k: deformation parameter (1.0 = symmetric figure-8, 10.0 = almost circle)
        steps: number of movement steps
        seed: random seed for reproducibility

    Returns:
        list of (x, y) positions
    """
    if seed is not None:
        random.seed(seed)

    x, y = 0.0, 0.0
    angle = 0.0
    step_size = space_size / 20.0

    direction = 1       # +1 = left turn, -1 = right turn
    series_count = 0    # steps in current direction
    trajectory = [(x, y)]

    # Odd series lengths with probabilities
    # Shorter series = more likely to change (more unpredictable)
    odd_lengths = {1: 0.3, 3: 0.35, 5: 0.2, 7: 0.15}

    for step in range(steps):
        # Base turn: π/4 = 45° (optimal LCI angle from Kryukov)
        delta_theta = direction * math.pi / 4
        series_count += 1

        # Rule 1: Anti-circle — forced reversal after 4 same-direction turns
        if series_count >= 4:
            direction = -direction
            series_count = 0

        # Rule 3: Odd series — change direction at odd counts
        elif series_count in odd_lengths:
            if random.random() < odd_lengths[series_count]:
                direction = -direction
                series_count = 0

        # Rule 4: Deformation — right loop k times longer than left
        if direction == 1:
            max_series = 3                          # small loop
        else:
            max_series = min(7, int(3 * k))         # large loop (scaled by k)

        if series_count >= max_series:
            direction = -direction
            series_count = 0

        # Rule 2: Anti-line — if too straight, force a turn
        if step >= 3:
            dx = trajectory[-1][0] - trajectory[-3][0]
            dy = trajectory[-1][1] - trajectory[-3][1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 2.5 * step_size:  # nearly straight for 3 steps
                delta_theta += direction * math.pi / 4

        # Boundary reflection: turn away from walls
        dist_from_center = math.sqrt(x*x + y*y)
        if dist_from_center > space_size * 0.8:
            # Angle toward center
            angle_to_center = math.atan2(-y, -x)
            angle_diff = angle_to_center - angle
            # Normalize to [-π, π]
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            delta_theta += 0.3 * angle_diff  # gentle correction toward center

        angle += delta_theta
        x += step_size * math.cos(angle)
        y += step_size * math.sin(angle)

        # Hard boundary clamp
        dist_from_center = math.sqrt(x*x + y*y)
        if dist_from_center > space_size:
            x *= space_size / dist_from_center
            y *= space_size / dist_from_center
            angle += math.pi  # bounce

        trajectory.append((x, y))

    return trajectory


def deformed_lissajous(A=1.0, B=1.0, k=1.0, omega=1.0, points=500):
    """
    Generate a deformed Lissajous figure-8 curve.

    Args:
        A: horizontal amplitude
        B: vertical amplitude
        k: deformation parameter (1 = symmetric, >1 = one loop larger)
        omega: angular frequency
        points: number of points

    Returns:
        list of (x, y) points
    """
    trajectory = []
    for i in range(points):
        t = 2 * math.pi * i / points
        x = A * math.sin(omega * t)
        # Deformed figure-8: second term shifts center proportional to k
        y = B * (math.sin(2 * omega * t + math.pi/2) +
                 (k - 1) / (k + 1) * math.sin(omega * t))
        trajectory.append((x, y))
    return trajectory


def four_level_scarab(space_size=10.0, k_bvs=2.0, k_svs=1.5, k_mvs=1.0,
                      k_chvs=1.0, mastery_level=3, steps=500, seed=None):
    """
    Four-level nested Scarab: BVS + SVS + MVS + ChVS superimposed.

    Four spheres (from Kryukov + ETD Vol.100-103):
      BVS  (shoulder/body):  3D, Earth, A=80-200cm, strategy    (~seconds)
      SVS  (elbow/forearm):  2D, Water, A=30-40cm,  tactics     (~100ms)
      MVS  (wrist/hand):     1D, Air,   A=10-15cm,  technique   (~50ms)
      ChVS (fingers):        0D, Fire,  A=1-5cm,    correction  (~10ms)

    Quaternion analogy (Vol.103):
      A = a·I + b·i + c·j + d·k  ↔  {BVS, SVS, MVS, ChVS}
      |A| = √(a² + b² + c² + d²) = LCI

    Mastery levels (1-5):
      Level 1: Only BVS active (linear movement)
      Level 2: BVS + SVS (loop-based combinations)
      Level 3: BVS + SVS + MVS (3D volume, all spheres)
      Level 4: All four spheres (satellite system, directed explosion)
      Level 5: Resonance ω_BVS = ω_SVS = ω_MVS = ω_ChVS (master)

    At mastery: BVS + SVS + MVS + ChVS = π (conservation law, Noether)
    """
    if seed is not None:
        random.seed(seed)

    # Amplitude ratios (from Kryukov's sphere sizes, proportional)
    A_bvs  = space_size * 0.55      # ~55% — shoulder span
    A_svs  = space_size * 0.15      # ~15% — forearm reach
    A_mvs  = space_size * 0.05      # ~5%  — hand/wrist
    A_chvs = space_size * 0.015     # ~1.5% — finger micro-movements

    # Angular frequencies depend on mastery level
    if mastery_level >= 5:
        # RESONANCE: all frequencies equal (master level)
        omega_bvs = omega_svs = omega_mvs = omega_chvs = 1.0
    else:
        # Non-resonant: higher spheres oscillate faster
        omega_bvs  = 1.0
        omega_svs  = 2.0 + (5 - mastery_level) * 0.3
        omega_mvs  = 5.0 + (5 - mastery_level) * 0.5
        omega_chvs = 13.0 + (5 - mastery_level) * 1.0  # fastest (prime!)

    # Disable spheres below mastery level
    if mastery_level < 2:
        A_svs = 0
    if mastery_level < 3:
        A_mvs = 0
    if mastery_level < 4:
        A_chvs = 0

    def _lissajous(A, omega, k, t, phase=0):
        """Single deformed Lissajous component."""
        x = A * math.sin(omega * t + phase)
        y = A * (math.sin(2 * omega * t + math.pi/2 + phase) +
                 (k - 1) / (k + 1) * math.sin(omega * t + phase))
        return x, y

    trajectory = []
    for i in range(steps):
        t = 2 * math.pi * i / steps * 3  # 3 full cycles

        # BVS: large deformed figure-8 (body movement)
        x_bvs, y_bvs = _lissajous(A_bvs, omega_bvs, k_bvs, t, phase=0)

        # SVS: medium figure-8 (forearm/elbow)
        x_svs, y_svs = _lissajous(A_svs, omega_svs, k_svs, t, phase=math.pi/3)

        # MVS: small figure-8 (wrist/hand)
        x_mvs, y_mvs = _lissajous(A_mvs, omega_mvs, k_mvs, t, phase=math.pi/7)

        # ChVS: micro figure-8 (fingers — "gearbox")
        # ChVS has special behavior: it can SWITCH between modes
        # modeled as sign flips at odd intervals
        chvs_switch = 1 if (int(t * 7 / math.pi) % 2 == 0) else -1
        x_chvs, y_chvs = _lissajous(A_chvs * chvs_switch, omega_chvs,
                                      k_chvs, t, phase=math.pi/11)

        # Superposition: r(t) = Σ spheres
        x = x_bvs + x_svs + x_mvs + x_chvs
        y = y_bvs + y_svs + y_mvs + y_chvs

        trajectory.append((x, y))

    return trajectory


def three_level_scarab(space_size=10.0, k_bvs=2.0, k_svs=1.5, k_mvs=1.0,
                       steps=500, seed=None):
    """Legacy 3-level wrapper. See four_level_scarab for full version."""
    return four_level_scarab(space_size=space_size, k_bvs=k_bvs, k_svs=k_svs,
                             k_mvs=k_mvs, k_chvs=1.0, mastery_level=3,
                             steps=steps, seed=seed)


# ═══════════════════════════════════════════════════════════
# QUATERNION STATE — 4-sphere representation
# ═══════════════════════════════════════════════════════════

class ScarabQuaternion:
    """
    Quaternion representation of the 4-sphere movement system.

    From Kryukov (Vol.103):
      A = a·1 + b·i + c·j + d·k
    where:
      a = BVS (body/shoulder) — real/scalar — 3D Earth
      b = SVS (elbow/forearm) — i component  — 2D Water
      c = MVS (wrist/hand)    — j component  — 1D Air
      d = ChVS (fingers)      — k component  — 0D Fire

    |A| = √(a² + b² + c² + d²) = LCI (Line Complexity Index)

    Conservation law (Noether): |A| = π = const at mastery level 5
    This means: as one sphere decreases, another must increase.
    """

    def __init__(self, bvs=0.0, svs=0.0, mvs=0.0, chvs=0.0):
        self.a = bvs    # BVS — real (scalar, body)
        self.b = svs    # SVS — i (elbow)
        self.c = mvs    # MVS — j (wrist)
        self.d = chvs   # ChVS — k (fingers)

    @property
    def bvs(self):
        return self.a

    @property
    def svs(self):
        return self.b

    @property
    def mvs(self):
        return self.c

    @property
    def chvs(self):
        return self.d

    def norm(self):
        """
        |A| = √(a² + b² + c² + d²) = LCI

        At mastery: LCI → π
        """
        return math.sqrt(self.a**2 + self.b**2 + self.c**2 + self.d**2)

    def lci(self):
        """Line Complexity Index — same as quaternion norm."""
        return self.norm()

    def conjugate(self):
        """Ā = a - b·i - c·j - d·k (reverse all rotation components)."""
        return ScarabQuaternion(self.a, -self.b, -self.c, -self.d)

    def __mul__(self, other):
        """
        Hamilton product: A × B (quaternion multiplication).

        Represents composition of two movement states:
        (a1 + b1·i + c1·j + d1·k) × (a2 + b2·i + c2·j + d2·k)

        Physical meaning: chaining two movements.
        """
        if isinstance(other, (int, float)):
            return ScarabQuaternion(self.a * other, self.b * other,
                                     self.c * other, self.d * other)
        a1, b1, c1, d1 = self.a, self.b, self.c, self.d
        a2, b2, c2, d2 = other.a, other.b, other.c, other.d
        return ScarabQuaternion(
            a1*a2 - b1*b2 - c1*c2 - d1*d2,
            a1*b2 + b1*a2 + c1*d2 - d1*c2,
            a1*c2 - b1*d2 + c1*a2 + d1*b2,
            a1*d2 + b1*c2 - c1*b2 + d1*a2,
        )

    def __add__(self, other):
        return ScarabQuaternion(self.a + other.a, self.b + other.b,
                                 self.c + other.c, self.d + other.d)

    def __sub__(self, other):
        return ScarabQuaternion(self.a - other.a, self.b - other.b,
                                 self.c - other.c, self.d - other.d)

    def normalized(self):
        """Normalize to |A| = π (the conservation law target)."""
        n = self.norm()
        if n < 1e-10:
            return ScarabQuaternion(math.pi, 0, 0, 0)
        scale = math.pi / n
        return self * scale

    def components_pct(self):
        """Percentage contribution of each sphere to total energy."""
        total = self.a**2 + self.b**2 + self.c**2 + self.d**2
        if total < 1e-10:
            return (100.0, 0.0, 0.0, 0.0)
        return (
            self.a**2 / total * 100,
            self.b**2 / total * 100,
            self.c**2 / total * 100,
            self.d**2 / total * 100,
        )

    def __repr__(self):
        return (f"Q({self.a:.3f} + {self.b:.3f}i + "
                f"{self.c:.3f}j + {self.d:.3f}k) |LCI|={self.lci():.4f}")

    @staticmethod
    def from_mastery(mastery_level, space_size=1.0):
        """
        Create a quaternion from mastery level using Kryukov's amplitude ratios.

        Level 1: only BVS (a >> 0)
        Level 5: all equal, resonance — |A| = π
        """
        # Amplitude ratios from four_level_scarab
        a = space_size * 0.55
        b = space_size * 0.15 if mastery_level >= 2 else 0.0
        c = space_size * 0.05 if mastery_level >= 3 else 0.0
        d = space_size * 0.015 if mastery_level >= 4 else 0.0

        # At level 5: normalize so |A| = π
        q = ScarabQuaternion(a, b, c, d)
        if mastery_level >= 5:
            return q.normalized()
        return q

    @staticmethod
    def from_symbol_pair(sym_left, sym_right, chvs_left=0, chvs_right=0):
        """
        Create a quaternion from a dual-hand symbol pair.

        Maps discrete MSA state → continuous quaternion:
          a (BVS) = avg complexity × spatial distance from center
          b (SVS) = transition smoothness indicator
          c (MVS) = anti-symmetry measure
          d (ChVS) = ChVS/mudra energy
        """
        cL = symbol_complexity(sym_left)
        cR = symbol_complexity(sym_right)
        xL, yL = symbol_to_xy(sym_left)
        xR, yR = symbol_to_xy(sym_right)

        # BVS: overall spatial extent
        dist_L = math.sqrt(xL**2 + yL**2)
        dist_R = math.sqrt(xR**2 + yR**2)
        a = (dist_L + dist_R) / 2.0

        # SVS: inter-hand distance (wider = more tactical space)
        b = math.sqrt((xL - xR)**2 + (yL - yR)**2)

        # MVS: complexity difference (wrist articulation)
        c = abs(cL - cR) / 4.0

        # ChVS: finger mode energy
        chvs_energy = {0: 1.0, 1: 0.3, 2: 0.5, 3: 0.2}
        d = (chvs_energy.get(chvs_left, 0.5) +
             chvs_energy.get(chvs_right, 0.5)) / 2.0

        return ScarabQuaternion(a, b, c, d)


# ═══════════════════════════════════════════════════════════
# LCI — Line Complexity Index
# ═══════════════════════════════════════════════════════════

def compute_lci(kata, mode='single'):
    """
    Compute the Line Complexity Index for a kata.

    LCI (from Kryukov) = quaternion norm of the movement state:
      LCI = |A| = √(BVS² + SVS² + MVS² + ChVS²)

    For a kata: average LCI across all tacts.

    Conservation law: at mastery → LCI → π = 3.14159...
    """
    lcis = []

    if mode == 'dual':
        for entry in kata:
            L, R = entry[0], entry[1]
            cL = entry[2] if len(entry) > 2 else 0
            cR = entry[3] if len(entry) > 3 else 0
            q = ScarabQuaternion.from_symbol_pair(L, R, cL, cR)
            lcis.append(q.lci())
    else:
        for sym in kata:
            # Single hand: only BVS and MVS active
            x, y = symbol_to_xy(sym)
            dist = math.sqrt(x**2 + y**2)
            c = symbol_complexity(sym)
            q = ScarabQuaternion(dist, 0, c / 4.0, 0)
            lcis.append(q.lci())

    avg_lci = sum(lcis) / len(lcis) if lcis else 0
    return {
        'per_tact': [round(l, 4) for l in lcis],
        'avg': round(avg_lci, 4),
        'target': round(math.pi, 4),
        'deviation_pct': round(abs(avg_lci - math.pi) / math.pi * 100, 1),
        'conservation': abs(avg_lci - math.pi) < 0.5,  # within ~16%
    }


def verify_conservation(mastery_level=5, space_size=1.0):
    """
    Verify the conservation law: |A| = π at mastery.

    Checks that the quaternion norm equals π when all spheres resonate.
    """
    q = ScarabQuaternion.from_mastery(mastery_level, space_size)
    n = q.norm()
    pct = q.components_pct()

    return {
        'quaternion': repr(q),
        'norm': round(n, 6),
        'pi': round(math.pi, 6),
        'match': abs(n - math.pi) < 0.001,
        'components_pct': {
            'BVS': round(pct[0], 1),
            'SVS': round(pct[1], 1),
            'MVS': round(pct[2], 1),
            'ChVS': round(pct[3], 1),
        },
    }


# ═══════════════════════════════════════════════════════════
# ASCII TRAJECTORY PLOT
# ═══════════════════════════════════════════════════════════

def plot_trajectory_ascii(trajectory, width=60, height=25, symbols=None):
    """
    Plot a 2D trajectory as ASCII art.

    Optionally overlay symbol positions along the path.

    Args:
        trajectory: list of (x, y) points
        width: canvas width in chars
        height: canvas height in chars
        symbols: optional list of (index, label) to mark on path

    Returns:
        list of strings (lines of the plot)
    """
    if not trajectory:
        return ["(empty trajectory)"]

    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    # Add margin
    x_range = x_max - x_min or 1.0
    y_range = y_max - y_min or 1.0
    x_min -= x_range * 0.05
    x_max += x_range * 0.05
    y_min -= y_range * 0.05
    y_max += y_range * 0.05
    x_range = x_max - x_min
    y_range = y_max - y_min

    # Initialize canvas
    canvas = [[' ' for _ in range(width)] for _ in range(height)]

    # Plot trajectory
    for x, y in trajectory:
        col = int((x - x_min) / x_range * (width - 1))
        row = int((1 - (y - y_min) / y_range) * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))
        if canvas[row][col] == ' ':
            canvas[row][col] = '·'

    # Mark center crossing
    cx = int((0 - x_min) / x_range * (width - 1))
    cy = int((1 - (0 - y_min) / y_range) * (height - 1))
    if 0 <= cx < width and 0 <= cy < height:
        canvas[cy][cx] = '+'

    # Overlay symbols
    if symbols:
        for idx, label in symbols:
            if 0 <= idx < len(trajectory):
                x, y = trajectory[idx]
                col = int((x - x_min) / x_range * (width - 1))
                row = int((1 - (y - y_min) / y_range) * (height - 1))
                col = max(0, min(width - 1, col))
                row = max(0, min(height - 1, row))
                # Place label character
                ch = label[0] if label else str(idx % 10)
                canvas[row][col] = ch

    # Build output
    lines = []
    lines.append(f"  ┌{'─' * width}┐")
    for row in canvas:
        lines.append(f"  │{''.join(row)}│")
    lines.append(f"  └{'─' * width}┘")

    return lines


def plot_kata_on_trajectory(kata, k=2.0, mastery_level=3, width=60, height=20):
    """
    Generate a figure-8 trajectory and plot kata symbols on it.

    Returns list of strings forming the ASCII plot.
    """
    traj = four_level_scarab(
        space_size=1.0, k_bvs=k, k_svs=max(1.0, k * 0.7),
        k_mvs=max(1.0, k * 0.4), k_chvs=1.0,
        mastery_level=mastery_level, steps=300, seed=42)

    n_points = len(traj)
    n_syms = len(kata)

    # Find trajectory indices closest to kata symbols' (x,y) positions
    sym_markers = []
    for i, entry in enumerate(kata):
        sym = entry[0] if isinstance(entry, tuple) else entry
        sx, sy = symbol_to_xy(sym)
        # Find nearest trajectory point
        best_idx = 0
        best_dist = float('inf')
        for j, (tx, ty) in enumerate(traj):
            d = (tx - sx)**2 + (ty - sy)**2
            if d < best_dist:
                best_dist = d
                best_idx = j
        sym_markers.append((best_idx, f"T{i}"))

    lines = plot_trajectory_ascii(traj, width, height, sym_markers)
    return lines


# ═══════════════════════════════════════════════════════════
# MOVEMENT ALPHABET: 76-symbol system
# ═══════════════════════════════════════════════════════════

# Square edges and diagonals as bit flags (6 bits = 64 base combinations)
TOP    = 0b000001  # 1   — upper horizontal edge
BOTTOM = 0b000010  # 2   — lower horizontal edge
LEFT   = 0b000100  # 4   — left vertical edge
RIGHT  = 0b001000  # 8   — right vertical edge
DIAG1  = 0b010000  # 16  — ╲ top-left to bottom-right diagonal
DIAG2  = 0b100000  # 32  — ╱ top-right to bottom-left diagonal

# Half-line flags (4 additional bits = 12 extra symbols beyond 64)
# Half-lines go from center to midpoints/corners
HALF_UP    = 0b00000001_00000000  # 256  — center to top midpoint
HALF_DOWN  = 0b00000010_00000000  # 512  — center to bottom midpoint
HALF_LEFT  = 0b00000100_00000000  # 1024 — center to left midpoint
HALF_RIGHT = 0b00001000_00000000  # 2048 — center to right midpoint
HALF_D1_UP = 0b00010000_00000000  # 4096 — center to top-left corner (half ╲)
HALF_D1_DN = 0b00100000_00000000  # 8192 — center to bottom-right corner (half ╲)
HALF_D2_UP = 0b01000000_00000000  # 16384— center to top-right corner (half ╱)
HALF_D2_DN = 0b10000000_00000000  # 32768— center to bottom-left corner (half ╱)

# Total: 64 base (full edges) + 12 half-line combinations = 76 symbols
# The 12 extra: 8 individual half-lines + 4 cross-half combinations

# ─── ChVS (finger) modifiers: 2 extra bits ───
# Each of the 76 symbols × 4 finger modes = 304 total ≈ 310 ETD volumes
CHVS_FIST   = 0  # Кулак — closed fist (strike)
CHVS_PALM   = 1  # Ладонь — open palm (block)
CHVS_POINT  = 2  # Пальцы — pointing fingers (thrust)
CHVS_GRAB   = 3  # Расслаб — relaxed fingers (grab/capture)

CHVS_NAMES = {
    CHVS_FIST:  'fist',
    CHVS_PALM:  'palm',
    CHVS_POINT: 'point',
    CHVS_GRAB:  'grab',
}

# ─── Complete 76-symbol alphabet ───
# Row 1 (14): Progressive complexity from point → full square+X
# Row 2-11: Systematic enumeration of all combinations

# 64 base symbols (all 6-bit combinations of full edges)
BASE_SYMBOLS = {i: i for i in range(64)}

# 12 half-line symbols (numbered 64-75)
HALF_SYMBOLS = {
    64: HALF_UP,                        # │↑ center to top
    65: HALF_DOWN,                      # │↓ center to bottom
    66: HALF_LEFT,                      # ─← center to left
    67: HALF_RIGHT,                     # ─→ center to right
    68: HALF_D1_UP,                     # ╲↑ center to top-left
    69: HALF_D1_DN,                     # ╲↓ center to bottom-right
    70: HALF_D2_UP,                     # ╱↑ center to top-right
    71: HALF_D2_DN,                     # ╱↓ center to bottom-left
    72: HALF_UP | HALF_DOWN,            # │  vertical half-cross
    73: HALF_LEFT | HALF_RIGHT,         # ─  horizontal half-cross
    74: HALF_D1_UP | HALF_D1_DN,        # ╲  diagonal half-cross
    75: HALF_D2_UP | HALF_D2_DN,        # ╱  anti-diagonal half-cross
}

# Named symbols (human-readable subset for the first row of the image)
SYMBOLS = {
    # Row 1: Progressive complexity (symbols 01-14 from image)
    'empty':     0b000000,    # · point (symbol 01)
    'dot':       0b000000,    # alias
    'diag1':     DIAG1,       # ╲ (symbol 03)
    'diag2':     DIAG2,       # ╱
    'corner_bl': BOTTOM|LEFT, # └ (symbol 05)
    'cross_d':   DIAG1|DIAG2, # X diagonal cross (symbol 06)
    'K_shape':   LEFT|DIAG1|DIAG2,    # K (symbol 07)
    'M_shape':   DIAG2|LEFT|RIGHT|DIAG1, # M (symbol 08)
    'T_shape':   TOP|LEFT,             # ⊥ T-shape (symbol 09)
    'chevron':   DIAG1|DIAG2,          # △ chevron up (symbol 10)
    'corner_br': BOTTOM|RIGHT,         # ┘ (symbol 11)
    'square':    TOP|BOTTOM|LEFT|RIGHT,# □ (symbol 12)
    'sq_d1':     TOP|BOTTOM|LEFT|RIGHT|DIAG1,       # □+╲ (symbol 13)
    'sq_full':   TOP|BOTTOM|LEFT|RIGHT|DIAG1|DIAG2, # ☒ (symbol 14)

    # Additional named forms
    'corner_tl': TOP|LEFT,     # ┌
    'corner_tr': TOP|RIGHT,    # ┐
    'horiz':     TOP|BOTTOM,   # ─ pair
    'vert':      LEFT|RIGHT,   # │ pair
    'sq_d2':     TOP|BOTTOM|LEFT|RIGHT|DIAG2, # □+╱
    'Z_shape':   TOP|DIAG1|BOTTOM,     # Z
    'N_shape':   LEFT|DIAG1|RIGHT,     # N
    'V_shape':   DIAG1|BOTTOM|DIAG2,   # V (bottom triangle)
    'A_shape':   DIAG2|TOP|DIAG1,      # A (top triangle)
    'L_shape':   BOTTOM|LEFT,          # L
    'J_shape':   BOTTOM|RIGHT,         # J

    # Kryukov's 7 groups mapping
    'g1_swing':     DIAG2,                           # Group 1: swing
    'g1_soft_out':  LEFT|DIAG2,                      # Group 1: soft outer block
    'g1_soft_in':   RIGHT|DIAG1,                     # Group 1: soft inner block
    'g2_straight':  LEFT|RIGHT,                      # Group 2: straight punch (both horizontal)
    'g2_uppercut':  BOTTOM|LEFT,                     # Group 2: uppercut
    'g2_hard_block': TOP|RIGHT,                      # Group 2: hard block
    'g3_uraken':    DIAG1,                           # Group 3: backfist
    'g4_corkscrew': DIAG1|DIAG2|LEFT,               # Group 4: spiral entry (K-shape)
    'g4_curtains':  LEFT|RIGHT|TOP|BOTTOM,           # Group 4: dual curtain block (□)
    'g5_shuto':     DIAG1|TOP,                       # Group 5: knife-hand
    'g6_cobra':     DIAG2|TOP|RIGHT,                 # Group 6: cobra hood
    'g7_frame':     TOP|BOTTOM|LEFT|RIGHT,           # Group 7: frame block (= square)
    'g7_lift':      TOP|LEFT|RIGHT,                  # Group 7: lifting block
}


def count_lines(sym):
    """Count number of active lines (set bits) in a symbol."""
    count = 0
    s = sym
    while s:
        count += s & 1
        s >>= 1
    return count


def symbol_complexity(sym):
    """
    Complexity metric for a symbol.
    Maps to Kryukov's 7 groups:
      0 lines = empty (ready position)
      1 line  = Group 1-2 (basic)
      2 lines = Group 2-4 (intermediate)
      3 lines = Group 4-5 (advanced)
      4+ lines = Group 6-7 (master)
    """
    n = count_lines(sym & 0x3F)  # only count base 6 bits
    if n == 0:
        return 0
    elif n <= 1:
        return 1
    elif n <= 2:
        return 2
    elif n <= 3:
        return 3
    else:
        return 4


def get_group(sym):
    """
    Assign a symbol to one of Kryukov's 7 groups based on its structure.
    Returns group number 1-7.
    """
    bits = sym & 0x3F
    n = count_lines(bits)
    has_diag = bool(bits & (DIAG1 | DIAG2))
    has_sides = bool(bits & (TOP | BOTTOM | LEFT | RIGHT))
    is_closed = (bits & (TOP | BOTTOM | LEFT | RIGHT)) == (TOP | BOTTOM | LEFT | RIGHT)

    if n == 0:
        return 1  # ready position = group 1
    if n == 1 and has_diag:
        return 1  # single diagonal = soft technique
    if n == 1 and has_sides:
        return 2  # single side = straight/hard technique
    if n == 2 and not has_diag:
        return 2  # two sides = hard combination
    if n == 2 and has_diag and has_sides:
        return 3  # diagonal + side = MVS technique
    if n == 2 and has_diag and not has_sides:
        return 4  # two diagonals = X = rotational
    if n == 3 and has_diag:
        return 5 if not is_closed else 6  # complex with diagonal
    if n == 3:
        return 5  # three sides = weapon-like
    if is_closed:
        return 7  # full square = frame block (peak defense)
    if n >= 4:
        return 6 if not is_closed else 7  # complex = master level
    return 3  # default: MVS level


def hamming_distance(sym1, sym2):
    """Number of differing bits = number of lines to change."""
    xor = sym1 ^ sym2
    count = 0
    while xor:
        count += xor & 1
        xor >>= 1
    return count


def get_neighbors(symbol, max_changes=2):
    """Get all symbols reachable by changing ≤ max_changes lines."""
    neighbors = []
    for i in range(6):  # 6 bits
        # Toggle one bit
        new_sym = symbol ^ (1 << i)
        if hamming_distance(symbol, new_sym) <= max_changes:
            neighbors.append(new_sym)
        # Toggle two bits
        for j in range(i+1, 6):
            new_sym2 = symbol ^ (1 << i) ^ (1 << j)
            if hamming_distance(symbol, new_sym2) <= max_changes:
                neighbors.append(new_sym2)
    return list(set(neighbors))


# ═══════════════════════════════════════════════════════════
# ChVS GEARBOX — micro-correction state machine
# ═══════════════════════════════════════════════════════════

# Contact feedback types (input to ChVS gearbox)
CONTACT_HARD  = 0   # Hit solid target
CONTACT_SOFT  = 1   # Hit soft target
CONTACT_EMPTY = 2   # Missed / no contact
CONTACT_BLOCK = 3   # Hit opponent's block

# ChVS response vectors: (force, spread, penetration)
CHVS_VECTORS = {
    CHVS_FIST:  (1.0, 0.0, 0.0),   # Maximum force, no spread
    CHVS_PALM:  (0.5, 0.5, 0.0),   # Distributed contact
    CHVS_POINT: (0.0, 0.0, 1.0),   # Maximum penetration
    CHVS_GRAB:  (0.3, 0.3, 0.4),   # Adaptive contact
}

# ChVS transition table: contact_type → optimal ChVS response
CHVS_TRANSITION = {
    CONTACT_HARD:  CHVS_FIST,    # Reinforce strike
    CONTACT_SOFT:  CHVS_GRAB,    # Capture / redirect
    CONTACT_EMPTY: CHVS_POINT,   # Extend to reach (thrust)
    CONTACT_BLOCK: CHVS_PALM,    # Redirect force (deflect)
}


def chvs_gearbox(contact_type, current_chvs=None):
    """
    ChVS micro-correction gearbox.
    Switches finger mode based on tactile feedback in ~10ms.

    Like a car gearbox:
    - Does NOT change route (BVS)
    - Does NOT change lane (SVS)
    - Does NOT turn wheel (MVS)
    - But changes the CHARACTER of contact at the moment of impact

    Args:
        contact_type: CONTACT_HARD/SOFT/EMPTY/BLOCK
        current_chvs: current finger mode (for hysteresis)

    Returns:
        new ChVS mode (CHVS_FIST/PALM/POINT/GRAB)
    """
    optimal = CHVS_TRANSITION.get(contact_type, CHVS_FIST)

    # Hysteresis: if already in a compatible mode, don't switch
    # (switching has a 10ms cost — avoid unnecessary switches)
    if current_chvs is not None and current_chvs == optimal:
        return current_chvs

    return optimal


# ═══════════════════════════════════════════════════════════
# MATCH-STICK AUTOMATON (MSA) — full state machine
# ═══════════════════════════════════════════════════════════

class MatchStickAutomaton:
    """
    Finite state automaton modeling all 76 hand positions.

    MSA = (Q, Sigma, delta, q0, F)
      Q     = 76 states (movement symbols)
      Sigma = {add_line, remove_line, swap_line, switch_chvs}
      delta = transition function (graph with ~670 edges)
      q0    = 0 (empty = ready position)
      F     = Q (all states are accepting)

    Four decision levels:
      BVS: strategy (attack/defend/feint) → selects target group
      SVS: tactics (group 1-7) → selects target symbol neighborhood
      MVS: technique (specific symbol) → selects exact target
      ChVS: gearbox (fist/palm/point/grab) → modulates contact
    """

    def __init__(self, mastery_level=1, seed=None):
        self.state = 0          # Current symbol (empty)
        self.chvs = CHVS_FIST   # Current finger mode
        self.mastery = mastery_level
        self.history = [0]      # State history
        self.chvs_history = [CHVS_FIST]
        self.rng = random.Random(seed)

        # Precompute adjacency for all 64 base symbols
        self._adj = {}
        for s in range(64):
            self._adj[s] = get_neighbors(s, max_changes=2)

        # Groups available at current mastery level
        self._update_available_groups()

    def _update_available_groups(self):
        """Update which groups are available based on mastery level."""
        level_groups = {
            1: [1, 2],
            2: [1, 2, 3],
            3: [1, 2, 3, 4, 5],
            4: [1, 2, 3, 4, 5, 6, 7],
            5: [1, 2, 3, 4, 5, 6, 7],
        }
        self.available_groups = level_groups.get(self.mastery, [1, 2])
        self.available_symbols = [
            s for s in range(64) if get_group(s) in self.available_groups
        ]

    def bfs_path(self, target):
        """Find shortest path from current state to target (≤3 steps)."""
        if self.state == target:
            return [self.state]
        from collections import deque
        visited = {self.state: None}
        queue = deque([self.state])
        while queue:
            node = queue.popleft()
            for nb in self._adj.get(node, []):
                if nb not in visited and 0 <= nb < 64:
                    visited[nb] = node
                    if nb == target:
                        # Reconstruct path
                        path = [nb]
                        while visited[path[-1]] is not None:
                            path.append(visited[path[-1]])
                        return list(reversed(path))
                    queue.append(nb)
        return [self.state, target]  # fallback: direct jump

    def transition(self, target_symbol, contact_type=None):
        """
        Execute transition from current state to target symbol.
        Returns list of intermediate states traversed.
        """
        path = self.bfs_path(target_symbol)

        traversed = []
        for sym in path[1:]:  # skip current state
            self.state = sym
            self.history.append(sym)
            traversed.append(sym)

            # ChVS gearbox: react to contact feedback
            if contact_type is not None:
                self.chvs = chvs_gearbox(contact_type, self.chvs)
            self.chvs_history.append(self.chvs)

        return traversed

    def generate_kata(self, length=7):
        """
        Generate a kata (movement sequence) respecting Scarab rules.

        Rules:
        1. Change ≤2 lines per tact
        2. Anti-circle: no return to same symbol within 4 tacts
        3. Odd series: {1, 3, 5, 7}
        4. Camouflage/threat: alternate dominant side
        5. Stay within mastery-level symbols
        """
        self.state = 0  # Reset to ready
        kata = [0]
        recent = [0]

        for _ in range(length - 1):
            neighbors = self._adj.get(self.state, [])

            # Filter by mastery level
            candidates = [n for n in neighbors
                          if n in self.available_symbols]

            # Anti-circle: no return to last 4
            filtered = [n for n in candidates if n not in recent[-4:]]
            if not filtered:
                filtered = candidates if candidates else neighbors

            # Camouflage: prefer switching dominant side
            current_left = bool(self.state & LEFT) or bool(self.state & DIAG2)
            preferred = []
            for c in filtered:
                c_right = bool(c & RIGHT) or bool(c & DIAG1)
                if current_left != c_right:
                    continue
                preferred.append(c)

            if preferred:
                next_sym = self.rng.choice(preferred)
            elif filtered:
                next_sym = self.rng.choice(filtered)
            else:
                next_sym = self.rng.choice(list(range(64)))

            self.transition(next_sym)
            kata.append(self.state)
            recent.append(self.state)
            if len(recent) > 7:
                recent.pop(0)

        return kata

    def generate_training_session(self, duration_minutes=45):
        """
        Generate a complete training session plan.

        Format:
          0-5 min:   Warmup (random level-1 symbols)
          5-15 min:  Technique (pairs of transitions)
          15-30 min: Kata (sequences of 5-7 tacts)
          30-40 min: Improvisation (automaton as opponent)
          40-45 min: Cooldown (slow transitions)

        Returns: dict with blocks, each containing symbol sequences
        """
        session = {}

        # Warmup: single symbols from groups 1-2
        warmup_syms = [s for s in range(64) if get_group(s) in [1, 2]]
        session['warmup'] = {
            'duration': '0-5 min',
            'symbols': [self.rng.choice(warmup_syms)
                        for _ in range(10)],
            'instruction': 'Hold each position 30 sec. ChVS: FIST only.',
        }

        # Technique: pairs
        pairs = []
        for _ in range(8):
            a = self.rng.choice(self.available_symbols)
            nbs = [n for n in self._adj.get(a, [])
                   if n in self.available_symbols]
            if nbs:
                b = self.rng.choice(nbs)
                pairs.append((a, b))
        session['technique'] = {
            'duration': '5-15 min',
            'pairs': pairs,
            'instruction': 'Transition between pairs. 1 min per pair.',
        }

        # Kata: sequences
        katas = []
        kata_len = min(3 + self.mastery, 7)  # 4 at level 1, 7 at level 4+
        for _ in range(4):
            k = self.generate_kata(length=kata_len)
            katas.append(k)
        session['kata'] = {
            'duration': '15-30 min',
            'sequences': katas,
            'instruction': f'Execute kata of {kata_len} tacts. All ChVS modes.',
        }

        # Improvisation: automaton-opponent generates challenges
        challenges = []
        for _ in range(5):
            target = self.rng.choice(self.available_symbols)
            grp = get_group(target)
            challenges.append({
                'symbol': target,
                'group': grp,
                'response_time': max(1.0, 4.0 - self.mastery * 0.5),
            })
        session['improvisation'] = {
            'duration': '30-40 min',
            'challenges': challenges,
            'instruction': 'Automaton shows target → execute within time limit.',
        }

        # Cooldown: slow level-1 transitions
        session['cooldown'] = {
            'duration': '40-45 min',
            'symbols': [self.rng.choice(warmup_syms)
                        for _ in range(5)],
            'instruction': 'Slow transitions. Deep breathing. ChVS: GRAB (relaxed).',
        }

        return session

    def describe_state(self):
        """Human-readable description of current state."""
        grp = get_group(self.state)
        cplx = symbol_complexity(self.state)
        group_names = {
            1: 'Soft base', 2: 'Hard base', 3: 'MVS (wrist)',
            4: 'Rotational', 5: 'Weapon', 6: 'Master', 7: 'Peak defense'
        }
        return (f"Symbol: {self.state:06b} | Group {grp} ({group_names[grp]}) | "
                f"Complexity: {cplx} | ChVS: {CHVS_NAMES[self.chvs]} | "
                f"Mastery: {self.mastery}")


# ═══════════════════════════════════════════════════════════
# MUDRA SYSTEM — expanded ChVS finger positions
# ═══════════════════════════════════════════════════════════

# Beyond 4 basic modes: 8 mudra positions (like 8 wind rose directions)
# 4 cardinal = basic ChVS, 4 intermediate = advanced mudras
MUDRA_FIST      = 0   # Сжатый кулак (vajra mudra) — strike
MUDRA_PALM      = 1   # Раскрытая ладонь (abhaya mudra) — block/stop
MUDRA_POINT     = 2   # Указующий (tarjani mudra) — thrust
MUDRA_GRAB      = 3   # Захват (varada mudra) — capture
MUDRA_BLADE     = 4   # Ребро ладони (karate chop) — shuto
MUDRA_HOOK      = 5   # Крюк (согнутые пальцы) — hook punch
MUDRA_SPEAR     = 6   # Копьё (пальцы вместе, прямые) — nukite
MUDRA_CUP       = 7   # Чашка (ладонь вогнута) — slap / ear strike

MUDRA_NAMES = {
    MUDRA_FIST:  'fist',     MUDRA_PALM:  'palm',
    MUDRA_POINT: 'point',    MUDRA_GRAB:  'grab',
    MUDRA_BLADE: 'blade',    MUDRA_HOOK:  'hook',
    MUDRA_SPEAR: 'spear',    MUDRA_CUP:   'cup',
}

# Mudra transition table: current situation → optimal mudra
# Extended from 4 contacts to 8 tactical situations
MUDRA_TRANSITION = {
    # 4 cardinal (same as ChVS)
    CONTACT_HARD:  MUDRA_FIST,     # Reinforce: harder strike
    CONTACT_SOFT:  MUDRA_GRAB,     # Capture: soft target → grab it
    CONTACT_EMPTY: MUDRA_POINT,    # Extend: missed → thrust further
    CONTACT_BLOCK: MUDRA_PALM,     # Redirect: deflect with palm
    # 4 intermediate (new tactical situations)
    4: MUDRA_BLADE,    # Edge contact → knife-hand follow-up
    5: MUDRA_HOOK,     # Close range → hook strike
    6: MUDRA_SPEAR,    # Linear opening → spear-hand thrust
    7: MUDRA_CUP,      # Side of head exposed → ear slap
}

# Mudra vectors: (force, spread, penetration, control)
MUDRA_VECTORS = {
    MUDRA_FIST:  (1.0, 0.0, 0.0, 0.0),
    MUDRA_PALM:  (0.3, 0.7, 0.0, 0.3),
    MUDRA_POINT: (0.0, 0.0, 1.0, 0.0),
    MUDRA_GRAB:  (0.2, 0.2, 0.2, 1.0),
    MUDRA_BLADE: (0.7, 0.3, 0.5, 0.0),   # Shuto: good force + penetration
    MUDRA_HOOK:  (0.8, 0.0, 0.3, 0.2),   # Hook: strong, curving
    MUDRA_SPEAR: (0.1, 0.0, 1.0, 0.0),   # Nukite: max penetration
    MUDRA_CUP:   (0.5, 1.0, 0.0, 0.0),   # Slap: max spread (shock wave)
}


def mudra_switch(situation, current_mudra=None):
    """
    Extended ChVS switching using 8 mudra positions.

    8 mudras = 8 directions of the wind rose applied to fingers:
      N=fist, E=point, S=palm, W=grab (cardinal)
      NE=blade, SE=hook, SW=spear, NW=cup (intermediate)

    Total states with mudras: 76 symbols × 8 mudras = 608
    """
    optimal = MUDRA_TRANSITION.get(situation, MUDRA_FIST)
    if current_mudra is not None and current_mudra == optimal:
        return current_mudra
    return optimal


# ═══════════════════════════════════════════════════════════
# DUAL MATCH-STICK AUTOMATON — two coordinated hands
# ═══════════════════════════════════════════════════════════

# Spatial zones for anti-collision
ZONE_UP    = 0b01  # Upper half of the square
ZONE_DOWN  = 0b10  # Lower half
ZONE_LEFT  = 0b01  # Left half (from fighter's perspective)
ZONE_RIGHT = 0b10  # Right half


def get_zones(sym):
    """
    Determine which spatial zones a symbol occupies.
    Returns (vertical_zone, horizontal_zone) as bitmasks.

    Used for collision avoidance: two hands must not occupy
    the same zone simultaneously.
    """
    v_zone = 0
    h_zone = 0
    if sym & TOP or sym & DIAG1 or sym & DIAG2:
        v_zone |= ZONE_UP
    if sym & BOTTOM or sym & DIAG1 or sym & DIAG2:
        v_zone |= ZONE_DOWN
    if sym & LEFT or sym & DIAG2:
        h_zone |= ZONE_LEFT
    if sym & RIGHT or sym & DIAG1:
        h_zone |= ZONE_RIGHT
    # Empty symbol occupies center (no conflict)
    if sym == 0:
        v_zone = 0
        h_zone = 0
    return v_zone, h_zone


def zones_conflict(sym_left, sym_right):
    """
    Check if two hand positions conflict (occupy same zone).

    Juggler rule: hands must not cross paths.
    Like two jugglers sharing one stage — each has their territory.
    """
    vL, hL = get_zones(sym_left)
    vR, hR = get_zones(sym_right)
    # Conflict if both hands claim the same quadrant
    v_overlap = vL & vR
    h_overlap = hL & hR
    return bool(v_overlap and h_overlap)


def is_anti_symmetric(sym_left, sym_right):
    """
    Check if two symbols satisfy anti-symmetry rule.

    Kryukov's law: H1 ≠ H2 — hands must be in opposite states:
      - one attacks, other defends
      - one high, other low
      - one forward, other back

    Measured by complementarity of active lines.
    """
    # Perfect anti-symmetry: bitwise complement (within 6 bits)
    complement = (~sym_right) & 0x3F

    # Measure: how many bits match the complement?
    match_bits = ~(sym_left ^ complement) & 0x3F
    match_count = count_lines(match_bits)

    # At least 3 of 6 bits should be complementary
    return match_count >= 3


def complexity_balance(sym_left, sym_right):
    """
    Measure complexity conservation between two hands.

    Rule 5: complexity(L) + complexity(R) ≈ const
    Total cognitive load should stay within 7±2 (Miller's law).

    Returns:
        (total_complexity, is_balanced)
        is_balanced = True if total ∈ [2, 6] (= 4 ± 2)
    """
    cL = symbol_complexity(sym_left)
    cR = symbol_complexity(sym_right)
    total = cL + cR
    # Target: 4 ± 2 (one hand complex → other simple)
    is_balanced = 2 <= total <= 6
    return total, is_balanced


class DualMatchStickAutomaton:
    """
    Two coordinated Match-Stick Automatons — one per hand.

    Like circus jugglers:
      - Each hand has its own MSA (76 states)
      - Hands must not collide (zone exclusion)
      - Hands perform complementary actions (anti-symmetry)
      - Mudra system provides 8 finger modes per hand

    State space: 76 × 76 × 8 × 8 = 389,888 (for 8-mudra)
                 76 × 76 × 4 × 4 =  92,416 (for 4-chvs basic)

    Effective states (after anti-symmetry + zone filtering):
      ~30-40% of total ≈ 30,000-40,000 valid dual positions.

    Coordination rules:
      1. Zone exclusion: hands cannot occupy same quadrant
      2. Anti-symmetry: H1 attacks ↔ H2 defends (and vice versa)
      3. Alternation: lead hand switches every 1-3 tacts
      4. Phase offset: left hand is π/2 ahead or behind right
      5. Conservation: complexity(L) + complexity(R) ≈ const
    """

    def __init__(self, mastery_level=1, use_mudras=False, seed=None):
        self.rng = random.Random(seed)
        self.use_mudras = use_mudras

        # Two independent MSAs
        self.left = MatchStickAutomaton(mastery_level=mastery_level,
                                        seed=self.rng.randint(0, 2**31))
        self.right = MatchStickAutomaton(mastery_level=mastery_level,
                                         seed=self.rng.randint(0, 2**31))

        # Mudra state (if using extended mudra system)
        self.left_mudra = MUDRA_FIST
        self.right_mudra = MUDRA_PALM  # Start complementary

        # Lead hand (alternates)
        self.lead = 'left'  # Which hand is currently attacking
        self.lead_count = 0

        # Phase offset state (Rule 4)
        # Left hand phase relative to right: +1 = ahead, -1 = behind
        self.phase_offset = 1  # Left leads initially
        self.phase_queue = []  # Buffered moves for phase-shifted hand

        # Complexity target (Rule 5)
        self.target_complexity = 4  # Total for both hands (Miller: 7±2 / 2 hands)

        # Dual history
        self.dual_history = [(0, 0)]

        self.mastery = mastery_level

    def _get_complementary_symbol(self, partner_sym, enforce_conservation=True):
        """
        Find a symbol complementary to the partner's current position.

        Complementary = different zone + anti-symmetric lines + balanced complexity.
        Like a mirror image rotated 180°.

        Rule 5 enforcement: if partner is complex (3-4), prefer simple (0-1) and vice versa.
        Follow hand = defense = LESS complex than lead.
        """
        partner_complexity = symbol_complexity(partner_sym)

        # Search both hands' available symbols for widest pool
        all_available = set(self.left.available_symbols) | set(self.right.available_symbols)

        # Tier 1: perfect complement (anti-symmetric + no zone conflict)
        tier1 = []
        # Tier 2: near complement (≥2 anti bits + no zone conflict)
        tier2 = []
        # Tier 3: no zone conflict only
        tier3 = []

        for s in all_available:
            if s == partner_sym:
                continue
            if zones_conflict(s, partner_sym):
                continue
            if is_anti_symmetric(s, partner_sym):
                tier1.append(s)
            elif hamming_distance(s, ~partner_sym & 0x3F) <= 4:
                tier2.append(s)
            else:
                tier3.append(s)

        # Use best available tier
        if tier1:
            candidates = tier1
        elif tier2:
            candidates = tier2
        elif tier3:
            candidates = tier3
        else:
            candidates = list(all_available) if all_available else self.left.available_symbols

        # Rule 5: Complexity conservation — follow prefers LESS complex
        if enforce_conservation and len(candidates) > 1:
            target_c = max(0, self.target_complexity - partner_complexity)
            # Sort by closeness to target complexity
            balanced = sorted(candidates,
                              key=lambda s: abs(symbol_complexity(s) - target_c))
            # Take top half (wider pool for better variety)
            cutoff = max(3, len(balanced) // 2)
            candidates = balanced[:cutoff]

        return candidates

    def step(self, contact_left=None, contact_right=None):
        """
        Advance both hands by one tact.

        The lead hand moves first (attack/initiative).
        The follow hand reacts (defense/complement).

        Phase offset (Rule 4): lead hand is one sub-step ahead.
        The follow hand's move is based on the lead's PREVIOUS position,
        creating a cascading L1→R1→L2→R2 pattern.

        Complexity conservation (Rule 5): enforced via _get_complementary_symbol.

        Returns: (left_sym, right_sym, left_mudra, right_mudra)
        """
        # Alternate lead hand every 1-3 tacts (ODD!)
        self.lead_count += 1
        # Pre-determined switch schedule: switch at odd intervals
        if not hasattr(self, '_switch_schedule') or not self._switch_schedule:
            # Generate schedule: alternate at intervals from {1, 3}
            self._switch_schedule = []
            for _ in range(10):
                self._switch_schedule.append(self.rng.choice([1, 3]))
            self._current_switch_target = self._switch_schedule.pop(0)
        if self.lead_count >= self._current_switch_target:
            self.lead = 'right' if self.lead == 'left' else 'left'
            self.lead_count = 0
            self._current_switch_target = (self._switch_schedule.pop(0)
                                            if self._switch_schedule
                                            else self.rng.choice([1, 3]))
            # Phase offset flips when lead switches
            self.phase_offset = -self.phase_offset

        if self.lead == 'left':
            lead_msa, follow_msa = self.left, self.right
        else:
            lead_msa, follow_msa = self.right, self.left

        # 1. Lead hand: generate next symbol (free choice from kata rules)
        #    Rule 1 (HARD): pre-filter to avoid zone conflict with follow hand
        follow_current = follow_msa.state
        lead_neighbors = lead_msa._adj.get(lead_msa.state, [])
        lead_candidates = [n for n in lead_neighbors
                           if n in lead_msa.available_symbols
                           and n not in lead_msa.history[-4:]
                           and not zones_conflict(n, follow_current)]
        if not lead_candidates:
            # Relax: drop anti-circle but keep zone exclusion
            lead_candidates = [n for n in lead_neighbors
                               if n in lead_msa.available_symbols
                               and not zones_conflict(n, follow_current)]
        if not lead_candidates:
            # Last resort: any available that doesn't conflict
            lead_candidates = [n for n in lead_msa.available_symbols
                               if not zones_conflict(n, follow_current)]
        if not lead_candidates:
            lead_candidates = lead_msa.available_symbols

        # Lead hand prefers MORE complex symbols (attack/initiative)
        if len(lead_candidates) > 1:
            lead_candidates.sort(key=lambda s: symbol_complexity(s), reverse=True)
            # Top half by complexity, then random from that subset
            top = max(2, len(lead_candidates) // 2)
            lead_next = self.rng.choice(lead_candidates[:top])
        else:
            lead_next = self.rng.choice(lead_candidates)
        lead_msa.transition(lead_next)

        # 2. Follow hand: must complement the lead (anti-symmetric, no zone clash)
        #    Rule 1 (HARD): zone exclusion enforced in _get_complementary_symbol
        #    Rule 4 (Phase offset): follow reacts to lead's position
        #    with a slight delay — use previous lead state as context
        #    for generating the cascade pattern
        phase_reference = lead_next
        if len(lead_msa.history) >= 3 and self.mastery >= 3:
            # At higher mastery, follow hand anticipates based on pattern
            # phase_reference blends current + previous for smoother cascade
            prev = lead_msa.history[-2] if len(lead_msa.history) >= 2 else 0
            # XOR blending: take bits from both to create phase-shifted target
            blend_mask = self.rng.randint(0, 0x3F)
            phase_reference = (lead_next & blend_mask) | (prev & ~blend_mask & 0x3F)
            # But still must be a valid available symbol
            if phase_reference not in lead_msa.available_symbols:
                phase_reference = lead_next

        complements = self._get_complementary_symbol(phase_reference)
        # Prefer neighbors of current follow state (smooth transition)
        follow_neighbors = follow_msa._adj.get(follow_msa.state, [])
        smooth_complements = [c for c in complements if c in follow_neighbors]
        if smooth_complements:
            follow_next = self.rng.choice(smooth_complements)
        elif complements:
            follow_next = self.rng.choice(complements)
        else:
            follow_next = follow_msa.state  # Stay put if no valid move

        # Final zone check (belt-and-suspenders safety)
        if zones_conflict(lead_next, follow_next):
            # Emergency: find ANY non-conflicting symbol for follow
            safe = [s for s in follow_msa.available_symbols
                    if not zones_conflict(lead_next, s)]
            if safe:
                follow_next = self.rng.choice(safe)

        follow_msa.transition(follow_next)

        # 3. Mudra/ChVS switching
        if self.use_mudras:
            if contact_left is not None:
                self.left_mudra = mudra_switch(contact_left, self.left_mudra)
            if contact_right is not None:
                self.right_mudra = mudra_switch(contact_right, self.right_mudra)
        else:
            if contact_left is not None:
                self.left.chvs = chvs_gearbox(contact_left, self.left.chvs)
            if contact_right is not None:
                self.right.chvs = chvs_gearbox(contact_right, self.right.chvs)

        self.dual_history.append((self.left.state, self.right.state))

        if self.use_mudras:
            return (self.left.state, self.right.state,
                    self.left_mudra, self.right_mudra)
        else:
            return (self.left.state, self.right.state,
                    self.left.chvs, self.right.chvs)

    def generate_dual_kata(self, length=7):
        """
        Generate a coordinated two-hand kata.

        Both hands move in complementary patterns:
          lead attacks → follow defends
          lead high → follow low
          lead left-zone → follow right-zone

        Returns: list of (left_sym, right_sym, left_chvs, right_chvs)
        """
        # Reset to ready
        self.left.state = 0
        self.right.state = 0
        self.left.history = [0]
        self.right.history = [0]
        self.dual_history = [(0, 0)]

        kata = [(0, 0, MUDRA_FIST if self.use_mudras else CHVS_FIST,
                        MUDRA_PALM if self.use_mudras else CHVS_PALM)]

        for _ in range(length - 1):
            result = self.step()
            kata.append(result)

        return kata

    def count_valid_pairs(self):
        """
        Count all valid (non-conflicting, anti-symmetric) hand pair positions.
        """
        valid = 0
        total = 0
        for L in self.left.available_symbols:
            for R in self.right.available_symbols:
                total += 1
                if not zones_conflict(L, R) and is_anti_symmetric(L, R):
                    valid += 1
        return valid, total

    def generate_dual_training_session(self, duration_minutes=45):
        """
        Generate a complete dual-hand training session.

        Format (adapted for two hands):
          0-5 min:   Mirror warmup (same symbol, mirrored)
          5-10 min:  Single-hand L (left kata, right at rest)
          10-15 min: Single-hand R (right kata, left at rest)
          15-25 min: Dual pairs — lead L (attack L / defend R)
          25-35 min: Dual pairs — lead R (attack R / defend L)
          35-40 min: Free duet (improvisation, both hands)
          40-45 min: Cooldown (slow mirror transitions)

        Returns: dict with blocks, each containing dual symbol sequences
        """
        session = {}

        warmup_syms = [s for s in range(64) if get_group(s) in [1, 2]]

        # 1. Mirror warmup: both hands do the same symbol
        mirror_pairs = []
        for _ in range(6):
            s = self.rng.choice(warmup_syms)
            mirror_pairs.append((s, s))
        session['mirror_warmup'] = {
            'duration': '0-5 min',
            'pairs': mirror_pairs,
            'instruction': 'Both hands mirror the same position. Hold 30s each. ChVS: FIST.',
        }

        # 2. Single-hand L: left hand does kata, right at rest
        self.left.state = 0
        self.left.history = [0]
        kata_L = self.left.generate_kata(length=5)
        session['single_L'] = {
            'duration': '5-10 min',
            'kata': [(s, 0) for s in kata_L],
            'instruction': 'Left hand kata, right at rest (ready). Focus on L transitions.',
        }

        # 3. Single-hand R: right hand does kata, left at rest
        self.right.state = 0
        self.right.history = [0]
        kata_R = self.right.generate_kata(length=5)
        session['single_R'] = {
            'duration': '10-15 min',
            'kata': [(0, s) for s in kata_R],
            'instruction': 'Right hand kata, left at rest (ready). Focus on R transitions.',
        }

        # 4. Dual pairs — lead L
        self.left.state = 0
        self.right.state = 0
        self.left.history = [0]
        self.right.history = [0]
        self.lead = 'left'
        self.dual_history = [(0, 0)]
        dual_kata_L = self.generate_dual_kata(length=7)
        session['dual_lead_L'] = {
            'duration': '15-25 min',
            'kata': dual_kata_L,
            'instruction': 'Left hand attacks, right defends. Practice anti-symmetry.',
        }

        # 5. Dual pairs — lead R
        self.left.state = 0
        self.right.state = 0
        self.left.history = [0]
        self.right.history = [0]
        self.lead = 'right'
        self.dual_history = [(0, 0)]
        dual_kata_R = self.generate_dual_kata(length=7)
        session['dual_lead_R'] = {
            'duration': '25-35 min',
            'kata': dual_kata_R,
            'instruction': 'Right hand attacks, left defends. Reverse lead.',
        }

        # 6. Free duet: improvisation
        self.left.state = 0
        self.right.state = 0
        self.left.history = [0]
        self.right.history = [0]
        self.dual_history = [(0, 0)]
        free_kata = self.generate_dual_kata(length=9)
        session['free_duet'] = {
            'duration': '35-40 min',
            'kata': free_kata,
            'instruction': 'Free improvisation. Lead alternates. All Rules (1-5) active.',
        }

        # 7. Cooldown: slow mirror
        slow_pairs = []
        for _ in range(4):
            s = self.rng.choice(warmup_syms)
            slow_pairs.append((s, s))
        session['cooldown'] = {
            'duration': '40-45 min',
            'pairs': slow_pairs,
            'instruction': 'Slow mirror transitions. Deep breathing. ChVS: GRAB (relaxed).',
        }

        return session

    def describe_dual_state(self):
        """Human-readable dual state description."""
        gL = get_group(self.left.state)
        gR = get_group(self.right.state)
        conflict = zones_conflict(self.left.state, self.right.state)
        anti = is_anti_symmetric(self.left.state, self.right.state)

        if self.use_mudras:
            chvs_L = MUDRA_NAMES[self.left_mudra]
            chvs_R = MUDRA_NAMES[self.right_mudra]
        else:
            chvs_L = CHVS_NAMES[self.left.chvs]
            chvs_R = CHVS_NAMES[self.right.chvs]

        total_c, balanced = complexity_balance(self.left.state, self.right.state)

        return (f"L: {self.left.state:06b}(G{gL},{chvs_L}) | "
                f"R: {self.right.state:06b}(G{gR},{chvs_R}) | "
                f"lead={self.lead} | "
                f"conflict={'YES!' if conflict else 'no'} | "
                f"anti-sym={'yes' if anti else 'NO'} | "
                f"C={total_c}({'OK' if balanced else 'HI'})")


# ═══════════════════════════════════════════════════════════
# KATA SCORING — evaluate adherence to all 5 rules
# ═══════════════════════════════════════════════════════════

def score_dual_kata(dual_kata):
    """
    Score a dual kata for adherence to coordination rules.

    Evaluates each tact against all 5 rules:
      1. Zone exclusion (hard) — 0 or 1 per tact
      2. Anti-symmetry (soft) — 0 or 1 per tact
      3. Lead alternation (hard) — checked across full kata
      4. Phase offset — measured by transition smoothness
      5. Complexity conservation — C(L)+C(R) ∈ [2,6]

    Returns:
        dict with per-tact scores, totals, and overall grade (A-F)
    """
    n = len(dual_kata)
    if n == 0:
        return {'grade': 'F', 'total': 0, 'max': 0, 'tacts': []}

    tact_scores = []
    rule_totals = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    rule_max = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for i, entry in enumerate(dual_kata):
        L, R = entry[0], entry[1]
        tact = {'tact': i}

        # Rule 1: Zone exclusion (1 point if no conflict)
        conflict = zones_conflict(L, R)
        r1 = 0 if conflict else 1
        tact['r1_zones'] = r1
        rule_totals[1] += r1
        rule_max[1] += 1

        # Rule 2: Anti-symmetry (1 point if complementary)
        anti = is_anti_symmetric(L, R)
        r2 = 1 if anti else 0
        tact['r2_anti_sym'] = r2
        rule_totals[2] += r2
        rule_max[2] += 1

        # Rule 4: Transition smoothness (1 point if ≤2 bits changed from prev)
        if i > 0:
            prev_L, prev_R = dual_kata[i-1][0], dual_kata[i-1][1]
            dist_L = hamming_distance(L, prev_L)
            dist_R = hamming_distance(R, prev_R)
            r4 = 1 if (dist_L <= 2 and dist_R <= 2) else 0
            tact['r4_smooth'] = r4
            rule_totals[4] += r4
            rule_max[4] += 1

        # Rule 5: Complexity conservation
        total_c, balanced = complexity_balance(L, R)
        r5 = 1 if balanced else 0
        tact['r5_complexity'] = r5
        tact['complexity_total'] = total_c
        rule_totals[5] += r5
        rule_max[5] += 1

        tact_scores.append(tact)

    # Rule 3: Lead alternation — check that lead changes happen at odd intervals
    # For a kata, we check that no more than 3 consecutive same-side dominances
    lead_series = []
    for i in range(1, n):
        L, R = dual_kata[i][0], dual_kata[i][1]
        cL = symbol_complexity(L)
        cR = symbol_complexity(R)
        lead_series.append('L' if cL >= cR else 'R')

    # Count max consecutive same lead
    if lead_series:
        max_run = 1
        current_run = 1
        for i in range(1, len(lead_series)):
            if lead_series[i] == lead_series[i-1]:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
        # Odd alternation: max run should be 1 or 3 (not 2, 4, 6)
        r3 = 1 if max_run in [1, 3, 5, 7] else 0
        # Also: at least one switch must occur
        switches = sum(1 for i in range(1, len(lead_series))
                       if lead_series[i] != lead_series[i-1])
        if switches == 0 and n > 2:
            r3 = 0
        rule_totals[3] = r3
        rule_max[3] = 1
    else:
        rule_totals[3] = 1
        rule_max[3] = 1

    # Calculate overall score
    total = sum(rule_totals.values())
    maximum = sum(rule_max.values())
    pct = total / maximum * 100 if maximum > 0 else 0

    # Grade: A(90+), B(75+), C(60+), D(40+), F(<40)
    if pct >= 90:
        grade = 'A'
    elif pct >= 75:
        grade = 'B'
    elif pct >= 60:
        grade = 'C'
    elif pct >= 40:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'grade': grade,
        'total': total,
        'max': maximum,
        'pct': pct,
        'rules': {r: f"{rule_totals[r]}/{rule_max[r]}" for r in range(1, 6)},
        'rule_names': {
            1: 'Zones', 2: 'Anti-sym', 3: 'Alternation',
            4: 'Smoothness', 5: 'Conservation'
        },
        'tacts': tact_scores,
        'lead_pattern': ''.join(lead_series) if lead_series else '-',
    }


def format_score_report(score):
    """Format a kata score as a human-readable report."""
    lines = []
    lines.append(f"  Grade: {score['grade']} ({score['pct']:.0f}%) "
                 f"[{score['total']}/{score['max']}]")
    for r in range(1, 6):
        name = score['rule_names'][r]
        val = score['rules'][r]
        lines.append(f"    Rule {r} ({name:12s}): {val}")
    lines.append(f"    Lead pattern: {score['lead_pattern']}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SEASONAL KATA GENERATOR — annual plan Q1-Q4
# ═══════════════════════════════════════════════════════════

# Rhythm patterns: beat durations in relative units
# Based on Scarab odd series {1, 3, 5, 7}
RHYTHM_PATTERNS = {
    'Q1': [1, 1, 1, 1, 1, 1, 1],           # Even: march tempo (foundation)
    'Q2': [1, 3, 1, 3, 1, 3, 1],           # Waltz: 1-3-1-3 (flow)
    'Q3': [1, 1, 3, 1, 1, 3, 1],           # Syncopated: burst patterns (fire)
    'Q4': [3, 1, 5, 1, 3, 1, 7],           # Free: all odd lengths (wind)
}

# BPM ranges per season (tacts per minute)
TEMPO_RANGES = {
    'Q1': (40, 60),    # Slow — winter — learning
    'Q2': (60, 90),    # Medium — spring — flowing
    'Q3': (90, 140),   # Fast — summer — intensity
    'Q4': (60, 120),   # Variable — autumn — freedom
}


def generate_seasonal_kata(quarter, mastery_level=1, year=1, use_dual=False,
                           use_mudras=False, seed=None):
    """
    Generate a kata appropriate for the given quarter of the training year.

    Maps directly to TRAINING_PLAN:
      Q1 (Winter/Earth/3D): Foundation — single symbols, groups 1-2
      Q2 (Spring/Water/2D): Flow — 3-tact transitions, groups 1-3
      Q3 (Summer/Fire/0D):  Intensity — 5-tact patterns, groups 1-5
      Q4 (Autumn/Air/1D):   Freedom — 7-tact full kata, all groups

    Args:
        quarter: 'Q1', 'Q2', 'Q3', or 'Q4'
        mastery_level: 1-5
        year: training year (1-5)
        use_dual: if True, generate dual-hand kata
        use_mudras: if True, use 8-mudra system
        seed: random seed

    Returns:
        dict with kata, rhythm, tempo, metadata, and score (for dual)
    """
    rng = random.Random(seed)
    plan = TRAINING_PLAN.get(quarter, TRAINING_PLAN['Q1'])

    kata_length = plan['kata_length']
    groups = plan['groups']
    k_min, k_max = plan['k_range']

    # Deformation parameter for this session
    k = k_min + rng.random() * (k_max - k_min)

    # Effective mastery: year progression within the quarter
    eff_mastery = min(5, mastery_level + (year - 1))

    # Rhythm pattern
    rhythm = RHYTHM_PATTERNS[quarter][:kata_length]
    tempo_min, tempo_max = TEMPO_RANGES[quarter]
    tempo = tempo_min + rng.random() * (tempo_max - tempo_min)

    # Beat durations in seconds (from tempo BPM and rhythm pattern)
    beat_base = 60.0 / tempo  # seconds per base beat
    beat_durations = [r * beat_base for r in rhythm]
    total_duration = sum(beat_durations)

    result = {
        'quarter': quarter,
        'season': plan['name'],
        'kata_length': kata_length,
        'mastery': eff_mastery,
        'year': year,
        'k': round(k, 2),
        'tempo_bpm': round(tempo, 1),
        'rhythm': rhythm,
        'beat_durations_s': [round(d, 2) for d in beat_durations],
        'total_duration_s': round(total_duration, 2),
    }

    # Use trajectory-driven generation when k > 1 (deformed figure-8)
    # This connects the geometric Scarab to the discrete MSA
    use_trajectory = (k > 1.05 and kata_length >= 3)

    if use_trajectory:
        tk = trajectory_kata(
            k=k, length=kata_length, mastery_level=eff_mastery,
            use_dual=use_dual, use_mudras=use_mudras,
            seed=rng.randint(0, 2**31))
        result['kata'] = tk['kata']
        result['trajectory_points'] = tk['trajectory_points']
        result['mode'] = tk['mode']
        result['generation'] = 'trajectory'
        if 'score' in tk:
            result['score'] = tk['score']
    elif use_dual:
        dual = DualMatchStickAutomaton(
            mastery_level=eff_mastery, use_mudras=use_mudras,
            seed=rng.randint(0, 2**31))
        # Filter to seasonal groups
        seasonal_syms = [s for s in range(64) if get_group(s) in groups]
        dual.left.available_symbols = seasonal_syms
        dual.right.available_symbols = seasonal_syms
        kata = dual.generate_dual_kata(length=kata_length)
        score = score_dual_kata(kata)
        result['kata'] = kata
        result['score'] = score
        result['mode'] = 'dual'
        result['generation'] = 'automaton'
    else:
        msa = MatchStickAutomaton(mastery_level=eff_mastery,
                                   seed=rng.randint(0, 2**31))
        msa.available_symbols = [s for s in range(64) if get_group(s) in groups]
        kata = msa.generate_kata(length=kata_length)
        result['kata'] = kata
        result['mode'] = 'single'
        result['generation'] = 'automaton'

    return result


def format_seasonal_kata(skata, use_mudras=False):
    """Format a seasonal kata as a human-readable string."""
    group_names = {1: 'Soft', 2: 'Hard', 3: 'MVS', 4: 'Rot',
                   5: 'Wpn', 6: 'Mstr', 7: 'Peak'}
    chvs_names = MUDRA_NAMES if use_mudras else CHVS_NAMES

    lines = []
    lines.append(f"  {skata['quarter']} — {skata['season']}")
    lines.append(f"  Year {skata['year']}, Mastery {skata['mastery']}, "
                 f"k={skata['k']}")
    lines.append(f"  Tempo: {skata['tempo_bpm']} BPM, "
                 f"Rhythm: {skata['rhythm']}")
    lines.append(f"  Total: {skata['total_duration_s']}s "
                 f"({skata['kata_length']} tacts)")

    if skata['mode'] == 'dual':
        for i, (L, R, cL, cR) in enumerate(skata['kata']):
            gL, gR = get_group(L), get_group(R)
            dur = skata['beat_durations_s'][i] if i < len(skata['beat_durations_s']) else 0
            cL_name = chvs_names.get(cL, '?')
            cR_name = chvs_names.get(cR, '?')
            lines.append(f"    T{i}: L={L:06b}(G{gL}/{group_names[gL]:4s},{cL_name:5s}) "
                         f"R={R:06b}(G{gR}/{group_names[gR]:4s},{cR_name:5s}) "
                         f"[{dur:.2f}s]")
        lines.append(format_score_report(skata['score']))
    else:
        for i, sym in enumerate(skata['kata']):
            grp = get_group(sym)
            dur = skata['beat_durations_s'][i] if i < len(skata['beat_durations_s']) else 0
            lines.append(f"    T{i}: {sym:06b} G{grp}/{group_names[grp]:4s} [{dur:.2f}s]")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SYMBOL ↔ SPATIAL COORDINATE MAPPING
# ═══════════════════════════════════════════════════════════

# Each 6-bit symbol maps to a 2D centroid (x, y) based on its active lines.
# This allows MSA symbols to be plotted on a figure-8 trajectory.
#
# Mapping: each bit contributes a direction vector:
#   TOP    → (0, +1)   "up"
#   BOTTOM → (0, -1)   "down"
#   LEFT   → (-1, 0)   "left"
#   RIGHT  → (+1, 0)   "right"
#   DIAG1  → (+1, +1)  "top-right to bottom-left diagonal"
#   DIAG2  → (-1, +1)  "top-left to bottom-right diagonal"
# The centroid is the average of active directions, normalized to [-1,+1].

_BIT_VECTORS = {
    TOP:    ( 0.0,  1.0),
    BOTTOM: ( 0.0, -1.0),
    LEFT:   (-1.0,  0.0),
    RIGHT:  ( 1.0,  0.0),
    DIAG1:  ( 0.7,  0.7),   # ╲ goes from top-left to bottom-right
    DIAG2:  (-0.7,  0.7),   # ╱ goes from top-right to bottom-left
}

def symbol_to_xy(sym):
    """
    Convert a 6-bit symbol to (x, y) spatial coordinates ∈ [-1, +1].

    The position represents where the hand IS in 2D space.
    Empty (000000) = center (0, 0).
    """
    if sym == 0:
        return (0.0, 0.0)
    x, y, n = 0.0, 0.0, 0
    for bit, (dx, dy) in _BIT_VECTORS.items():
        if sym & bit:
            x += dx
            y += dy
            n += 1
    if n > 0:
        x /= n
        y /= n
    return (x, y)


def xy_to_nearest_symbol(x, y, available=None):
    """
    Find the symbol closest to a given (x, y) position.

    Used to map continuous trajectory points to discrete MSA symbols.
    """
    if available is None:
        available = range(64)
    best_sym = 0
    best_dist = float('inf')
    for s in available:
        sx, sy = symbol_to_xy(s)
        d = (x - sx)**2 + (y - sy)**2
        if d < best_dist:
            best_dist = d
            best_sym = s
    return best_sym


# ═══════════════════════════════════════════════════════════
# K-DEFORMATION KATA — trajectory-driven kata generation
# ═══════════════════════════════════════════════════════════

def trajectory_kata(k=2.0, length=7, mastery_level=3, use_dual=False,
                    use_mudras=False, seed=None):
    """
    Generate a kata by sampling points on a deformed figure-8 trajectory.

    This bridges the continuous Scarab trajectory and the discrete MSA:
    1. Generate a 4-level Scarab trajectory with the given k deformation
    2. Sample `length` evenly-spaced points along the trajectory
    3. Map each point to the nearest MSA symbol
    4. For dual: left hand follows main trajectory, right hand follows
       the anti-symmetric mirror (phase-shifted by π)

    The deformation parameter k controls the kata's character:
      k=1.0: symmetric, balanced kata (Winter/Q1)
      k=2.0: slight asymmetry, flowing (Spring/Q2)
      k=5.0: strong asymmetry, explosive (Summer/Q3)
      k=10.0: extreme, one-sided (master level)

    Returns:
        dict with kata, trajectory points, k, and score (for dual)
    """
    rng = random.Random(seed)

    # Generate trajectory with 4-level Scarab
    traj = four_level_scarab(
        space_size=1.0,
        k_bvs=k, k_svs=max(1.0, k * 0.7),
        k_mvs=max(1.0, k * 0.4), k_chvs=1.0,
        mastery_level=mastery_level,
        steps=500, seed=rng.randint(0, 2**31))

    # Available symbols based on mastery
    msa = MatchStickAutomaton(mastery_level=mastery_level,
                               seed=rng.randint(0, 2**31))
    available = msa.available_symbols

    # Sample evenly-spaced points
    n_points = len(traj)
    indices = [int(i * (n_points - 1) / (length - 1)) for i in range(length)]

    kata_syms = []
    traj_points = []
    for idx in indices:
        x, y = traj[idx]
        sym = xy_to_nearest_symbol(x, y, available)
        kata_syms.append(sym)
        traj_points.append((x, y))

    result = {
        'k': k,
        'length': length,
        'mastery': mastery_level,
        'trajectory_points': traj_points,
    }

    if use_dual:
        # Right hand: mirror trajectory (phase-shifted by π on the figure-8)
        # Mirror points are at n_points/2 offset
        mirror_offset = n_points // 2
        dual_kata = []
        chvs_L = MUDRA_FIST if use_mudras else CHVS_FIST
        chvs_R = MUDRA_PALM if use_mudras else CHVS_PALM

        for i, idx in enumerate(indices):
            L = kata_syms[i]
            # Mirror index: half-cycle offset on figure-8
            mirror_idx = (idx + mirror_offset) % n_points
            mx, my = traj[mirror_idx]
            R = xy_to_nearest_symbol(mx, my, available)

            # Enforce zone exclusion
            if zones_conflict(L, R):
                safe = [s for s in available
                        if not zones_conflict(L, s)]
                if safe:
                    # Pick closest to mirror point
                    R = min(safe, key=lambda s: (
                        (symbol_to_xy(s)[0] - mx)**2 +
                        (symbol_to_xy(s)[1] - my)**2))

            dual_kata.append((L, R, chvs_L, chvs_R))

        score = score_dual_kata(dual_kata)
        result['kata'] = dual_kata
        result['score'] = score
        result['mode'] = 'dual'
    else:
        result['kata'] = kata_syms
        result['mode'] = 'single'

    return result


# ═══════════════════════════════════════════════════════════
# COMPACT KATA NOTATION
# ═══════════════════════════════════════════════════════════

# Encoding: each symbol → 1-2 character code
# 6-bit values 0-63 encoded as base-64 chars (A-Z, a-z, 0-9, +, /)
_B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
_B64_REV = {c: i for i, c in enumerate(_B64)}


def kata_to_notation(kata, mode='single'):
    """
    Encode a kata as a compact string notation.

    Single kata: "S7/e:AQ0wKgA"  (one char per symbol)
    Dual kata:   "D7/f:A01A.M00R..."  (L + chvs_L + chvs_R + R per tact)

    Includes header with mode, length, and checksum.
    """
    if mode == 'dual':
        parts = []
        for entry in kata:
            L, R = entry[0], entry[1]
            cL = entry[2] if len(entry) > 2 else 0
            cR = entry[3] if len(entry) > 3 else 0
            parts.append(f"{_B64[L]}{cL}{cR}{_B64[R]}")
        body = '.'.join(parts)
        checksum = sum(entry[0] ^ entry[1] for entry in kata) % 64
        return f"D{len(kata)}/{_B64[checksum]}:{body}"
    else:
        body = ''.join(_B64[s] for s in kata)
        checksum = sum(kata) % 64
        return f"S{len(kata)}/{_B64[checksum]}:{body}"


def notation_to_kata(notation):
    """
    Decode a compact notation string back to a kata.

    Returns: (mode, kata_list)
      mode='single': kata_list is [sym, sym, ...]
      mode='dual':   kata_list is [(L, R, chvs_L, chvs_R), ...]
    """
    mode = notation[0]
    header, body = notation.split(':', 1)

    if mode == 'S':
        kata = [_B64_REV[c] for c in body]
        return ('single', kata)
    elif mode == 'D':
        tacts = body.split('.')
        kata = []
        for t in tacts:
            L = _B64_REV[t[0]]
            chvs_L = int(t[1])
            chvs_R = int(t[2])
            R = _B64_REV[t[3]]
            kata.append((L, R, chvs_L, chvs_R))
        return ('dual', kata)
    else:
        raise ValueError(f"Unknown notation mode: {mode}")


# ═══════════════════════════════════════════════════════════
# KATA ANALYTICS — statistical analysis
# ═══════════════════════════════════════════════════════════

def analyze_kata(kata, mode='single'):
    """
    Statistical analysis of a kata's quality and characteristics.

    Returns dict with:
      - group_coverage: which of 7 groups are represented
      - diversity: unique symbols / total (0-1)
      - avg_transition: average Hamming distance between tacts
      - spatial_spread: how much of the (x,y) space is covered
      - complexity_curve: C values per tact
      - symmetry_score: for dual, anti-symmetry quality
    """
    if mode == 'dual':
        syms_L = [entry[0] for entry in kata]
        syms_R = [entry[1] for entry in kata]
        all_syms = syms_L + syms_R
    else:
        all_syms = list(kata)
        syms_L = all_syms
        syms_R = []

    n = len(syms_L)

    # Group coverage
    groups_used = set(get_group(s) for s in all_syms)
    group_coverage = sorted(groups_used)

    # Diversity: unique symbols / total
    diversity = len(set(all_syms)) / len(all_syms) if all_syms else 0

    # Average transition distance
    transitions = []
    for seq in ([syms_L] if not syms_R else [syms_L, syms_R]):
        for i in range(1, len(seq)):
            transitions.append(hamming_distance(seq[i], seq[i-1]))
    avg_transition = sum(transitions) / len(transitions) if transitions else 0

    # Spatial spread: bounding box of (x,y) centroids
    points = [symbol_to_xy(s) for s in all_syms]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_range = max(xs) - min(xs) if xs else 0
    y_range = max(ys) - min(ys) if ys else 0
    spatial_spread = x_range * y_range  # area of bounding box

    # Complexity curve
    complexity_L = [symbol_complexity(s) for s in syms_L]
    complexity_R = [symbol_complexity(s) for s in syms_R] if syms_R else []

    # Path length in symbol space (total Hamming distance)
    path_length = sum(transitions)

    result = {
        'n_tacts': n,
        'group_coverage': group_coverage,
        'n_groups': len(group_coverage),
        'diversity': round(diversity, 2),
        'avg_transition': round(avg_transition, 2),
        'spatial_spread': round(spatial_spread, 3),
        'path_length': path_length,
        'complexity_L': complexity_L,
    }

    if mode == 'dual':
        result['complexity_R'] = complexity_R
        # Symmetry analysis
        anti_count = sum(1 for i in range(n)
                         if is_anti_symmetric(syms_L[i], syms_R[i]))
        result['anti_symmetry_pct'] = round(anti_count / n * 100, 1) if n else 0
        # Zone safety
        zone_safe = sum(1 for i in range(n)
                        if not zones_conflict(syms_L[i], syms_R[i]))
        result['zone_safety_pct'] = round(zone_safe / n * 100, 1) if n else 0

    return result


def format_analysis(analysis):
    """Format kata analysis as a human-readable string."""
    lines = []
    lines.append(f"  Tacts: {analysis['n_tacts']}, "
                 f"Groups: {analysis['group_coverage']} ({analysis['n_groups']}/7)")
    lines.append(f"  Diversity: {analysis['diversity']:.0%}, "
                 f"Avg transition: {analysis['avg_transition']:.1f} bits, "
                 f"Path: {analysis['path_length']} bits")
    lines.append(f"  Spatial spread: {analysis['spatial_spread']:.3f} "
                 f"(of max ~4.0)")
    lines.append(f"  Complexity L: {analysis['complexity_L']}")
    if 'complexity_R' in analysis:
        lines.append(f"  Complexity R: {analysis['complexity_R']}")
        lines.append(f"  Anti-symmetry: {analysis['anti_symmetry_pct']}%, "
                     f"Zone safety: {analysis['zone_safety_pct']}%")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# KATA OPTIMIZER — regenerate until target grade
# ═══════════════════════════════════════════════════════════

def optimize_kata(length=7, mastery_level=3, target_grade='B',
                  max_attempts=50, use_mudras=False, groups=None,
                  base_seed=None):
    """
    Generate dual katas repeatedly until one meets the target grade.

    Applies evolutionary strategy: keep the best kata seen so far,
    and use its seed neighborhood for the next attempt.

    Args:
        length: kata length (1, 3, 5, or 7)
        mastery_level: 1-5
        target_grade: minimum grade ('A', 'B', 'C', 'D')
        max_attempts: maximum generation attempts
        use_mudras: use 8-mudra system
        groups: restrict to these symbol groups (list of ints)
        base_seed: starting seed

    Returns:
        dict with best kata, its score, attempts used
    """
    grade_order = {'A': 4, 'B': 3, 'C': 2, 'D': 1, 'F': 0}
    target_val = grade_order.get(target_grade, 3)
    rng = random.Random(base_seed)

    best_kata = None
    best_score = None
    best_seed = None
    best_val = -1

    for attempt in range(max_attempts):
        seed = rng.randint(0, 2**31)
        dual = DualMatchStickAutomaton(
            mastery_level=mastery_level, use_mudras=use_mudras, seed=seed)

        if groups:
            seasonal_syms = [s for s in range(64) if get_group(s) in groups]
            dual.left.available_symbols = seasonal_syms
            dual.right.available_symbols = seasonal_syms

        kata = dual.generate_dual_kata(length=length)
        score = score_dual_kata(kata)
        val = grade_order.get(score['grade'], 0)

        if val > best_val or (val == best_val and score['pct'] > best_score['pct']):
            best_kata = kata
            best_score = score
            best_seed = seed
            best_val = val

        if val >= target_val:
            return {
                'kata': kata,
                'score': score,
                'seed': seed,
                'attempts': attempt + 1,
                'optimized': True,
            }

    return {
        'kata': best_kata,
        'score': best_score,
        'seed': best_seed,
        'attempts': max_attempts,
        'optimized': best_val >= target_val,
    }


# ═══════════════════════════════════════════════════════════
# BATTLE KATA — structured attack/defense sequences
# ═══════════════════════════════════════════════════════════

# Battle phases: each phase has a role for lead and follow
BATTLE_PHASES = {
    'opening': {
        'name': 'Открытие (Opening)',
        'lead_groups': [1, 2],      # Simple probing moves
        'follow_groups': [1, 2],    # Mirror guard
        'tacts': 1,
        'tempo_mult': 0.5,          # Slow, careful
    },
    'attack': {
        'name': 'Атака (Attack)',
        'lead_groups': [3, 4, 5],   # Complex strikes
        'follow_groups': [1, 2],    # Simple defense
        'tacts': 3,
        'tempo_mult': 1.5,          # Fast
    },
    'counter': {
        'name': 'Контратака (Counter)',
        'lead_groups': [1, 2, 3],   # Recovery moves
        'follow_groups': [3, 4, 5], # Follow strikes back
        'tacts': 3,
        'tempo_mult': 1.2,
    },
    'clinch': {
        'name': 'Клинч (Clinch)',
        'lead_groups': [5, 6],      # Close-range
        'follow_groups': [5, 6],    # Close-range mirror
        'tacts': 1,
        'tempo_mult': 0.8,
    },
    'finish': {
        'name': 'Завершение (Finish)',
        'lead_groups': [6, 7],      # Maximum complexity
        'follow_groups': [1, 2],    # Collapse to guard
        'tacts': 1,
        'tempo_mult': 2.0,          # Explosive
    },
}

# Battle kata №1-4 (canonical sequences from Q4)
BATTLE_FORMATS = {
    1: ['opening', 'attack', 'clinch'],                      # 5 tacts (1+3+1)
    2: ['opening', 'attack', 'counter'],                     # 7 tacts (1+3+3)
    3: ['opening', 'attack', 'counter', 'finish'],           # 8→9 (odd!) (1+3+3+1+1pad)
    4: ['opening', 'attack', 'clinch', 'counter', 'finish'], # 9 tacts (1+3+1+3+1)
}


def generate_battle_kata(battle_num=1, mastery_level=3, use_mudras=False,
                          base_tempo=80.0, seed=None):
    """
    Generate a battle kata — structured attack/defense sequence.

    Battle katas follow a dramatic arc:
      Opening → Attack → Counter/Clinch → Finish

    Each phase constrains which groups are available for lead/follow,
    creating realistic combat flow.

    Args:
        battle_num: 1-4 (complexity increases)
        mastery_level: 1-5
        use_mudras: use 8-mudra system
        base_tempo: base BPM
        seed: random seed

    Returns:
        dict with phases, full kata, score, timing
    """
    rng = random.Random(seed)
    fmt = BATTLE_FORMATS.get(battle_num, BATTLE_FORMATS[1])

    all_tacts = []
    phase_info = []
    beat_durations = []

    dual = DualMatchStickAutomaton(
        mastery_level=mastery_level, use_mudras=use_mudras,
        seed=rng.randint(0, 2**31))

    for phase_name in fmt:
        phase = BATTLE_PHASES[phase_name]
        n_tacts = phase['tacts']
        tempo = base_tempo * phase['tempo_mult']
        beat_base = 60.0 / tempo

        # Restrict available symbols to phase groups
        lead_syms = [s for s in range(64) if get_group(s) in phase['lead_groups']]
        follow_syms = [s for s in range(64) if get_group(s) in phase['follow_groups']]

        phase_tacts = []
        for t in range(n_tacts):
            # Determine lead/follow assignment
            if dual.lead == 'left':
                dual.left.available_symbols = lead_syms
                dual.right.available_symbols = follow_syms
            else:
                dual.left.available_symbols = follow_syms
                dual.right.available_symbols = lead_syms

            result = dual.step()
            phase_tacts.append(result)
            all_tacts.append(result)

            # Rhythm: odd multipliers from Scarab series
            odd_mult = [1, 3, 1][t % 3]
            beat_durations.append(odd_mult * beat_base)

        phase_info.append({
            'name': phase['name'],
            'phase': phase_name,
            'tacts': phase_tacts,
            'tempo': round(tempo, 1),
        })

    # Ensure total is odd (Scarab rule)
    total_tacts = len(all_tacts)
    if total_tacts % 2 == 0:
        # Add one pad tact (return to guard)
        dual.left.available_symbols = [s for s in range(64)
                                        if get_group(s) in [1, 2]]
        dual.right.available_symbols = dual.left.available_symbols
        pad = dual.step()
        all_tacts.append(pad)
        beat_durations.append(60.0 / base_tempo)
        phase_info.append({
            'name': 'Возврат (Return)',
            'phase': 'return',
            'tacts': [pad],
            'tempo': base_tempo,
        })

    score = score_dual_kata(all_tacts)

    return {
        'battle_num': battle_num,
        'format': fmt,
        'phases': phase_info,
        'kata': all_tacts,
        'score': score,
        'total_tacts': len(all_tacts),
        'beat_durations_s': [round(d, 2) for d in beat_durations],
        'total_duration_s': round(sum(beat_durations), 2),
    }


def format_battle_kata(bkata, use_mudras=False):
    """Format a battle kata as a human-readable string."""
    group_names = {1: 'Soft', 2: 'Hard', 3: 'MVS', 4: 'Rot',
                   5: 'Wpn', 6: 'Mstr', 7: 'Peak'}
    chvs_names = MUDRA_NAMES if use_mudras else CHVS_NAMES

    lines = []
    lines.append(f"  Battle Kata №{bkata['battle_num']} "
                 f"({bkata['total_tacts']} tacts, "
                 f"{bkata['total_duration_s']}s)")
    lines.append(f"  Format: {' → '.join(bkata['format'])}")

    tact_idx = 0
    for pi in bkata['phases']:
        lines.append(f"    ── {pi['name']} ({pi['tempo']} BPM) ──")
        for entry in pi['tacts']:
            L, R = entry[0], entry[1]
            cL, cR = entry[2], entry[3]
            gL, gR = get_group(L), get_group(R)
            cL_name = chvs_names.get(cL, '?')
            cR_name = chvs_names.get(cR, '?')
            dur = (bkata['beat_durations_s'][tact_idx]
                   if tact_idx < len(bkata['beat_durations_s']) else 0)
            lines.append(f"      T{tact_idx}: L={L:06b}(G{gL}/{group_names[gL]:4s},"
                         f"{cL_name:5s}) "
                         f"R={R:06b}(G{gR}/{group_names[gR]:4s},{cR_name:5s}) "
                         f"[{dur:.2f}s]")
            tact_idx += 1

    lines.append(format_score_report(bkata['score']))
    return '\n'.join(lines)


def symbol_to_ascii(sym, size=5):
    """Convert a 6-bit symbol to ASCII art."""
    grid = [[' ' for _ in range(size)] for _ in range(size)]
    last = size - 1

    # Draw edges
    if sym & TOP:
        for c in range(size):
            grid[0][c] = '─'
    if sym & BOTTOM:
        for c in range(size):
            grid[last][c] = '─'
    if sym & LEFT:
        for r in range(size):
            grid[r][0] = '│'
    if sym & RIGHT:
        for r in range(size):
            grid[r][last] = '│'
    if sym & DIAG1:  # ╲
        for i in range(size):
            grid[i][i] = '╲'
    if sym & DIAG2:  # ╱
        for i in range(size):
            grid[i][last - i] = '╱'

    # Fix corners
    if (sym & TOP) and (sym & LEFT):
        grid[0][0] = '┌'
    if (sym & TOP) and (sym & RIGHT):
        grid[0][last] = '┐'
    if (sym & BOTTOM) and (sym & LEFT):
        grid[last][0] = '└'
    if (sym & BOTTOM) and (sym & RIGHT):
        grid[last][last] = '┘'

    return '\n'.join(''.join(row) for row in grid)


# ═══════════════════════════════════════════════════════════
# STICK-FIGURE AUTOMATON
# ═══════════════════════════════════════════════════════════

def stick_figure_frame(left_arm_angle, right_arm_angle):
    """
    Generate ASCII stick figure with arms at given angles.

    Angles: 0=down, 45=diagonal-down, 90=horizontal,
            135=diagonal-up, 180=up

    Returns: list of strings (ASCII art lines)
    """
    # 7x7 grid
    grid = [[' ' for _ in range(9)] for _ in range(7)]

    # Head
    grid[0][4] = 'O'

    # Body (vertical line)
    for r in range(1, 5):
        grid[r][4] = '│'

    # Legs
    grid[5][3] = '╱'
    grid[5][5] = '╲'
    grid[6][2] = '╱'
    grid[6][6] = '╲'

    # Left arm (angles: 0=down, 90=horiz, 180=up)
    la = left_arm_angle
    if la <= 45:
        grid[2][3] = '╲'; grid[3][2] = '╲'
    elif la <= 90:
        grid[2][3] = '─'; grid[2][2] = '─'
    elif la <= 135:
        grid[2][3] = '╱'; grid[1][2] = '╱'
    else:
        grid[1][3] = '│'; grid[0][3] = '│'

    # Right arm
    ra = right_arm_angle
    if ra <= 45:
        grid[2][5] = '╱'; grid[3][6] = '╱'
    elif ra <= 90:
        grid[2][5] = '─'; grid[2][6] = '─'
    elif ra <= 135:
        grid[2][5] = '╲'; grid[1][6] = '╲'
    else:
        grid[1][5] = '│'; grid[0][5] = '│'

    return [''.join(row) for row in grid]


def symbol_to_arms(sym):
    """Convert a 6-bit movement symbol to arm angles."""
    left_angle = 90   # default: horizontal
    right_angle = 90

    # Left arm position based on left-side elements
    if sym & LEFT:
        left_angle = 90      # horizontal
    if sym & DIAG2:
        left_angle = 135     # diagonal up
    if sym & TOP and not (sym & LEFT):
        left_angle = 180     # up
    if sym & BOTTOM and not (sym & LEFT):
        left_angle = 0       # down

    # Right arm position based on right-side elements
    if sym & RIGHT:
        right_angle = 90     # horizontal
    if sym & DIAG1:
        right_angle = 135    # diagonal up
    if sym & TOP and not (sym & RIGHT):
        right_angle = 180    # up
    if sym & BOTTOM and not (sym & RIGHT):
        right_angle = 0      # down

    return left_angle, right_angle


def animate_kata_text(kata_sequence):
    """Convert kata sequence to text animation frames."""
    frames = []
    for i, sym in enumerate(kata_sequence):
        left_a, right_a = symbol_to_arms(sym)
        figure = stick_figure_frame(left_a, right_a)

        # Add symbol diagram alongside
        sym_art = symbol_to_ascii(sym, size=5)
        sym_lines = sym_art.split('\n')

        combined = []
        combined.append(f"=== Tact {i+1} (symbol: {sym:06b}) ===")
        for j in range(max(len(figure), len(sym_lines))):
            fig_line = figure[j] if j < len(figure) else '         '
            sym_line = sym_lines[j] if j < len(sym_lines) else '     '
            combined.append(f"  {fig_line}    [{sym_line}]")
        combined.append("")
        frames.append('\n'.join(combined))

    return frames


# ═══════════════════════════════════════════════════════════
# DUAL STICK-FIGURE VISUALIZATION
# ═══════════════════════════════════════════════════════════

# ChVS/Mudra hand markers for the stick figure
HAND_MARKERS = {
    CHVS_FIST:  '*',   # Clenched fist
    CHVS_PALM:  '=',   # Open palm
    CHVS_POINT: '>',   # Pointing
    CHVS_GRAB:  '~',   # Relaxed/grab
}
MUDRA_MARKERS = {
    MUDRA_FIST:  '*',   MUDRA_PALM:  '=',
    MUDRA_POINT: '>',   MUDRA_GRAB:  '~',
    MUDRA_BLADE: '/',   MUDRA_HOOK:  'J',
    MUDRA_SPEAR: '|',   MUDRA_CUP:   'U',
}


def dual_stick_figure(sym_left, sym_right, chvs_left=0, chvs_right=0,
                      use_mudras=False):
    """
    Generate ASCII art of TWO stick figures side by side.

    Left figure shows the left-hand MSA state.
    Right figure shows the right-hand MSA state (mirrored).
    Hand tips show ChVS/Mudra markers.

    Returns: list of strings (9 lines)
    """
    la_L, ra_L = symbol_to_arms(sym_left)
    la_R, ra_R = symbol_to_arms(sym_right)

    markers = MUDRA_MARKERS if use_mudras else HAND_MARKERS
    mk_L = markers.get(chvs_left, '?')
    mk_R = markers.get(chvs_right, '?')

    fig_L = stick_figure_frame(la_L, ra_L)
    fig_R = stick_figure_frame(la_R, ra_R)

    # Build symbol boxes
    sym_art_L = symbol_to_ascii(sym_left, size=5).split('\n')
    sym_art_R = symbol_to_ascii(sym_right, size=5).split('\n')

    # Compose: [sym_L] figure_L <-> figure_R [sym_R]
    lines = []
    max_rows = max(len(fig_L), len(fig_R), len(sym_art_L), len(sym_art_R))
    for i in range(max_rows):
        sL = sym_art_L[i] if i < len(sym_art_L) else '     '
        fL = fig_L[i] if i < len(fig_L) else '         '
        fR = fig_R[i] if i < len(fig_R) else '         '
        sR = sym_art_R[i] if i < len(sym_art_R) else '     '
        lines.append(f"  [{sL}] {fL}  <->  {fR} [{sR}]")

    # Add hand marker annotation
    lines.append(f"  L-hand: {mk_L}({markers.__class__.__name__[0]})"
                 f"                    "
                 f"R-hand: {mk_R}")

    return lines


def animate_dual_kata(dual_kata, use_mudras=False):
    """
    Generate text animation frames for a dual-hand kata.

    Args:
        dual_kata: list of (L_sym, R_sym, L_chvs, R_chvs) tuples
        use_mudras: if True, interpret chvs values as mudra IDs

    Returns: list of frame strings
    """
    group_names = {1: 'Soft', 2: 'Hard', 3: 'MVS', 4: 'Rot',
                   5: 'Wpn', 6: 'Mstr', 7: 'Peak'}
    names_chvs = MUDRA_NAMES if use_mudras else CHVS_NAMES

    frames = []
    for i, (L, R, cL, cR) in enumerate(dual_kata):
        gL, gR = get_group(L), get_group(R)
        conflict = zones_conflict(L, R)
        anti = is_anti_symmetric(L, R)
        status = 'OK' if not conflict else 'COLLISION!'

        header = (f"=== Tact {i} | "
                  f"L:{L:06b}(G{gL}/{group_names[gL]}) "
                  f"R:{R:06b}(G{gR}/{group_names[gR]}) | "
                  f"{status} ===")

        fig_lines = dual_stick_figure(L, R, cL, cR, use_mudras)

        cL_name = names_chvs.get(cL, '?')
        cR_name = names_chvs.get(cR, '?')
        footer = f"  ChVS/Mudra: L={cL_name}, R={cR_name}"

        frame = [header] + fig_lines + [footer, ""]
        frames.append('\n'.join(frame))

    return frames


def export_training_session(session, mastery_level=1, filename=None):
    """
    Export a training session to human-readable text format.

    Can be printed or saved to file for use during actual training.
    """
    group_names = {1: 'Soft base', 2: 'Hard base', 3: 'MVS (wrist)',
                   4: 'Rotational', 5: 'Weapon', 6: 'Master', 7: 'Peak defense'}
    lines = []
    lines.append("=" * 60)
    lines.append(f"TRAINING SESSION — Mastery Level {mastery_level}")
    lines.append(f"Date: ____________  Duration: 45 min")
    lines.append("=" * 60)

    for block_name, block_data in session.items():
        dur = block_data.get('duration', '?')
        instr = block_data.get('instruction', '')
        lines.append(f"\n--- [{dur}] {block_name.upper()} ---")
        lines.append(f"  {instr}")

        if 'symbols' in block_data:
            lines.append("  Positions:")
            for j, s in enumerate(block_data['symbols']):
                grp = get_group(s)
                art = symbol_to_ascii(s, size=3).split('\n')
                lines.append(f"    {j+1}. {s:06b} (G{grp}/{group_names[grp]})")
                for a_line in art:
                    lines.append(f"       {a_line}")

        if 'pairs' in block_data:
            lines.append("  Transition Pairs:")
            for j, (a, b) in enumerate(block_data['pairs']):
                gA, gB = get_group(a), get_group(b)
                lines.append(f"    {j+1}. {a:06b}(G{gA}) -> {b:06b}(G{gB})")

        if 'sequences' in block_data:
            lines.append("  Kata Sequences:")
            for j, seq in enumerate(block_data['sequences']):
                syms = ' -> '.join(f'{s:06b}' for s in seq)
                lines.append(f"    Kata {j+1}: {syms}")
                # Show stick figures for this kata
                for k, s in enumerate(seq):
                    la, ra = symbol_to_arms(s)
                    fig = stick_figure_frame(la, ra)
                    lines.append(f"      Tact {k+1}:")
                    for f_line in fig:
                        lines.append(f"        {f_line}")

        if 'challenges' in block_data:
            lines.append("  Challenges (automaton shows, you respond):")
            for j, ch in enumerate(block_data['challenges']):
                grp = get_group(ch['symbol'])
                lines.append(f"    {j+1}. Target: {ch['symbol']:06b} G{grp} "
                             f"— respond in {ch['response_time']:.1f}s")

    lines.append("\n" + "=" * 60)
    lines.append("END OF SESSION")

    text = '\n'.join(lines)

    if filename:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)

    return text


def export_dual_training_session(session, mastery_level=1, use_mudras=False,
                                  filename=None):
    """
    Export a DUAL-HAND training session to human-readable text format.

    Includes dual stick-figure visualization for kata sequences.
    """
    group_names = {1: 'Soft base', 2: 'Hard base', 3: 'MVS (wrist)',
                   4: 'Rotational', 5: 'Weapon', 6: 'Master', 7: 'Peak defense'}
    chvs_names = MUDRA_NAMES if use_mudras else CHVS_NAMES

    lines = []
    lines.append("=" * 70)
    lines.append(f"DUAL-HAND TRAINING SESSION — Mastery Level {mastery_level}")
    lines.append(f"Mode: {'8-mudra' if use_mudras else '4-ChVS'}")
    lines.append(f"Date: ____________  Duration: 45 min")
    lines.append("=" * 70)

    for block_name, block_data in session.items():
        dur = block_data.get('duration', '?')
        instr = block_data.get('instruction', '')
        lines.append(f"\n{'─' * 70}")
        lines.append(f"[{dur}] {block_name.upper()}")
        lines.append(f"  {instr}")

        # Mirror/cooldown pairs: (sym, sym) tuples
        if 'pairs' in block_data:
            lines.append("  Positions:")
            for j, (sL, sR) in enumerate(block_data['pairs']):
                gL, gR = get_group(sL), get_group(sR)
                total_c, balanced = complexity_balance(sL, sR)
                lines.append(f"    {j+1}. L:{sL:06b}(G{gL}) | R:{sR:06b}(G{gR})"
                             f" | C={total_c}{'*' if not balanced else ''}")
                # Dual stick figure
                fig = dual_stick_figure(sL, sR, CHVS_FIST, CHVS_FIST)
                for f_line in fig:
                    lines.append(f"      {f_line}")

        # Single-hand kata: (sym, 0) or (0, sym) tuples
        if 'kata' in block_data and isinstance(block_data['kata'], list):
            kata = block_data['kata']
            if len(kata) > 0 and isinstance(kata[0], tuple) and len(kata[0]) == 2:
                # Single-hand format: list of (L, R)
                lines.append("  Sequence:")
                for j, (sL, sR) in enumerate(kata):
                    active = sL if sL != 0 else sR
                    hand = 'L' if sL != 0 else 'R'
                    grp = get_group(active)
                    lines.append(f"    Tact {j}: {hand}={active:06b}"
                                 f"(G{grp}/{group_names[grp]})")
                    la, ra = symbol_to_arms(active)
                    fig = stick_figure_frame(la, ra)
                    for f_line in fig:
                        lines.append(f"        {f_line}")

            elif len(kata) > 0 and isinstance(kata[0], tuple) and len(kata[0]) == 4:
                # Dual format: list of (L, R, chvs_L, chvs_R)
                lines.append("  Dual Kata:")
                for j, (sL, sR, cL, cR) in enumerate(kata):
                    gL, gR = get_group(sL), get_group(sR)
                    total_c, balanced = complexity_balance(sL, sR)
                    conflict = zones_conflict(sL, sR)
                    anti = is_anti_symmetric(sL, sR)
                    cL_name = chvs_names.get(cL, '?')
                    cR_name = chvs_names.get(cR, '?')
                    status = 'OK' if not conflict else 'COLLISION!'

                    lines.append(f"    Tact {j}: L={sL:06b}(G{gL},{cL_name}) "
                                 f"R={sR:06b}(G{gR},{cR_name}) "
                                 f"[{status}] C={total_c}")

                    fig = dual_stick_figure(sL, sR, cL, cR, use_mudras)
                    for f_line in fig:
                        lines.append(f"      {f_line}")

    lines.append(f"\n{'─' * 70}")
    lines.append("RULES ACTIVE:")
    lines.append("  1. Zone Exclusion: hands never in same quadrant")
    lines.append("  2. Anti-Symmetry: H1 attacks <-> H2 defends")
    lines.append("  3. Lead Alternation: switches every 1-3 tacts (ODD)")
    lines.append("  4. Phase Offset: cascade L1->R1->L2->R2")
    lines.append("  5. Complexity Conservation: C(L)+C(R) in [2,6]")
    lines.append("\n" + "=" * 70)
    lines.append("END OF DUAL SESSION")

    text = '\n'.join(lines)

    if filename:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)

    return text


# ═══════════════════════════════════════════════════════════
# ANNUAL TRAINING PLAN MAPPING
# ═══════════════════════════════════════════════════════════

TRAINING_PLAN = {
    'Q1': {
        'name': 'Foundation (Winter/Earth/3D)',
        'kata_length': 1,
        'k_range': (1.0, 1.0),     # symmetric only
        'groups': [1, 2],           # basic groups
        'sessions': 12,
        'description': '1-tactic elements. Single symbols from alphabet.'
    },
    'Q2': {
        'name': 'Flow (Spring/Water/2D)',
        'kata_length': 3,           # 2-tactic + transition
        'k_range': (1.0, 2.0),     # slight deformation allowed
        'groups': [1, 2, 3],
        'sessions': 12,
        'description': '2-tactic transitions. Pairs of symbols with linking.'
    },
    'Q3': {
        'name': 'Intensity (Summer/Fire/0D)',
        'kata_length': 5,           # 3-tactic patterns
        'k_range': (1.0, 5.0),     # strong deformation
        'groups': [1, 2, 3, 4, 5],
        'sessions': 12,
        'description': '3-tactic patterns: 3+0, 2+1, 1+1+1 formulas.'
    },
    'Q4': {
        'name': 'Freedom (Autumn/Air/1D)',
        'kata_length': 7,           # full kata
        'k_range': (1.0, 10.0),    # any deformation
        'groups': [1, 2, 3, 4, 5, 6, 7],
        'sessions': 12,
        'description': 'Battle kata №1-4. Free combination of all elements.'
    },
}


# ═══════════════════════════════════════════════════════════
# TRAINING PROGRESSION SIMULATOR
# ═══════════════════════════════════════════════════════════

def simulate_progression(n_years=5, sessions_per_quarter=12, seed=None):
    """
    Simulate a student's progression through the full training cycle.

    Tracks: mastery level, kata grades, LCI, group coverage
    over 5 years × 4 quarters × 12 sessions = 240 sessions.

    Returns:
        dict with per-quarter stats and overall progression curve
    """
    rng = random.Random(seed)
    results = []

    for year in range(1, n_years + 1):
        for qi, quarter in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
            mastery = min(5, year)
            use_dual = (qi >= 2)  # Q3+ = dual
            use_mudras = (year >= 3 and qi >= 3)  # Year 3+ Q4 = mudras

            quarter_grades = []
            quarter_lcis = []
            quarter_groups = set()

            for session in range(sessions_per_quarter):
                sk = generate_seasonal_kata(
                    quarter, mastery_level=mastery, year=year,
                    use_dual=use_dual, use_mudras=use_mudras,
                    seed=rng.randint(0, 2**31))

                if use_dual and 'score' in sk:
                    quarter_grades.append(sk['score']['pct'])
                    lci = compute_lci(sk['kata'], mode='dual')
                    quarter_lcis.append(lci['avg'])
                elif not use_dual:
                    quarter_grades.append(100.0)  # Single is always "correct"
                    lci = compute_lci(sk['kata'], mode='single')
                    quarter_lcis.append(lci['avg'])

                for entry in sk['kata']:
                    if isinstance(entry, tuple):
                        quarter_groups.add(get_group(entry[0]))
                        quarter_groups.add(get_group(entry[1]))
                    else:
                        quarter_groups.add(get_group(entry))

            avg_grade = sum(quarter_grades) / len(quarter_grades) if quarter_grades else 0
            avg_lci = sum(quarter_lcis) / len(quarter_lcis) if quarter_lcis else 0

            results.append({
                'year': year,
                'quarter': quarter,
                'mastery': mastery,
                'avg_grade': round(avg_grade, 1),
                'avg_lci': round(avg_lci, 4),
                'groups_covered': sorted(quarter_groups),
                'n_groups': len(quarter_groups),
                'dual': use_dual,
                'mudras': use_mudras,
            })

    return results


def format_progression(results):
    """Format progression results as human-readable summary."""
    lines = []
    current_year = 0
    for r in results:
        if r['year'] != current_year:
            current_year = r['year']
            lines.append(f"  Year {current_year} (mastery={r['mastery']}):")
        mode = 'D+M' if r['mudras'] else ('dual' if r['dual'] else 'sing')
        grade_letter = ('A' if r['avg_grade'] >= 90 else
                        'B' if r['avg_grade'] >= 75 else
                        'C' if r['avg_grade'] >= 60 else 'D')
        lines.append(f"    {r['quarter']}: grade={grade_letter}({r['avg_grade']:.0f}%) "
                     f"LCI={r['avg_lci']:.3f} "
                     f"groups={r['n_groups']}/7 mode={mode}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# EXAM SYSTEM — evaluate student against ideal
# ═══════════════════════════════════════════════════════════

def generate_exam(quarter='Q4', mastery_level=3, year=3, seed=None):
    """
    Generate an exam: ideal kata + evaluation criteria.

    The exam consists of:
    1. An optimized reference kata (Grade A target)
    2. Evaluation rubric per tact
    3. Pass/fail thresholds

    Returns:
        dict with reference kata, criteria, and evaluation function
    """
    rng = random.Random(seed)

    # Generate an optimized reference
    ref = optimize_kata(
        length=TRAINING_PLAN[quarter]['kata_length'],
        mastery_level=min(5, mastery_level + (year - 1)),
        target_grade='A',
        max_attempts=30,
        groups=TRAINING_PLAN[quarter]['groups'],
        base_seed=rng.randint(0, 2**31))

    return {
        'quarter': quarter,
        'year': year,
        'mastery': mastery_level,
        'reference': ref['kata'],
        'reference_score': ref['score'],
        'reference_notation': kata_to_notation(ref['kata'], mode='dual'),
        'pass_threshold': 70.0,  # Minimum % for pass
        'honor_threshold': 90.0,  # % for honors
    }


def evaluate_exam(exam, student_kata):
    """
    Evaluate a student's kata against the exam reference.

    Comparison metrics:
    1. Score: student kata graded independently
    2. Similarity: how close to reference (per-tact Hamming)
    3. Rule compliance: all 5 rules checked
    4. LCI deviation from target

    Returns:
        dict with evaluation results, pass/fail, feedback
    """
    # Score the student kata
    student_score = score_dual_kata(student_kata)

    # Similarity to reference
    ref = exam['reference']
    n = min(len(ref), len(student_kata))
    similarity_L = []
    similarity_R = []
    for i in range(n):
        dL = hamming_distance(ref[i][0], student_kata[i][0])
        dR = hamming_distance(ref[i][1], student_kata[i][1])
        similarity_L.append(max(0, 1 - dL / 6.0))
        similarity_R.append(max(0, 1 - dR / 6.0))

    avg_sim = ((sum(similarity_L) + sum(similarity_R)) /
               (2 * n) * 100) if n > 0 else 0

    # LCI
    student_lci = compute_lci(student_kata, mode='dual')

    # Feedback
    feedback = []
    if student_score['pct'] < exam['pass_threshold']:
        feedback.append('FAIL: Score below pass threshold')
    if student_lci['deviation_pct'] > 70:
        feedback.append('LCI too far from target (work on complexity balance)')

    # Per-rule feedback
    for r in range(1, 6):
        rule_str = student_score['rules'][r]
        num, den = rule_str.split('/')
        if int(num) < int(den):
            names = {1: 'zone exclusion', 2: 'anti-symmetry',
                     3: 'lead alternation', 4: 'smoothness',
                     5: 'complexity conservation'}
            feedback.append(f'Improve Rule {r} ({names[r]}): {rule_str}')

    passed = student_score['pct'] >= exam['pass_threshold']
    honors = student_score['pct'] >= exam['honor_threshold']

    return {
        'score': student_score,
        'similarity_pct': round(avg_sim, 1),
        'lci': student_lci,
        'passed': passed,
        'honors': honors,
        'result': 'HONORS' if honors else ('PASS' if passed else 'FAIL'),
        'feedback': feedback,
    }


# ═══════════════════════════════════════════════════════════
# RESONANCE DETECTION
# ═══════════════════════════════════════════════════════════

def detect_resonance(kata, mode='dual'):
    """
    Detect harmonic/resonant patterns in a kata.

    Resonance occurs when:
    1. Periodic repetition of symbols or groups
    2. Symmetric structure (palindrome-like)
    3. LCI stability (low variance)
    4. Phase coherence between hands (for dual)

    Returns:
        dict with resonance metrics and detected patterns
    """
    if mode == 'dual':
        syms_L = [entry[0] for entry in kata]
        syms_R = [entry[1] for entry in kata]
    else:
        syms_L = list(kata)
        syms_R = []

    n = len(syms_L)
    if n < 3:
        return {'resonance_score': 0.0, 'patterns': []}

    patterns = []

    # 1. Periodicity: check for repeating subsequences
    groups_L = [get_group(s) for s in syms_L]
    groups_R = [get_group(s) for s in syms_R] if syms_R else []

    # Check period-2 and period-3 repetition in groups
    for period in [2, 3]:
        if n >= period * 2:
            match_count = 0
            total_checks = 0
            for i in range(n - period):
                if groups_L[i] == groups_L[i + period]:
                    match_count += 1
                total_checks += 1
            if total_checks > 0:
                periodicity = match_count / total_checks
                if periodicity > 0.5:
                    patterns.append(f'Period-{period} group repetition '
                                    f'({periodicity:.0%})')

    # 2. Palindrome detection (group level)
    is_palindrome = (groups_L == groups_L[::-1])
    if is_palindrome:
        patterns.append('Palindrome (group sequence)')

    # Near-palindrome: allow 1 mismatch
    if not is_palindrome and n >= 5:
        mismatches = sum(1 for i in range(n // 2)
                         if groups_L[i] != groups_L[n - 1 - i])
        if mismatches <= 1:
            patterns.append(f'Near-palindrome ({mismatches} mismatch)')

    # 3. LCI stability
    lcis = []
    if mode == 'dual':
        for entry in kata:
            q = ScarabQuaternion.from_symbol_pair(entry[0], entry[1],
                                                    entry[2] if len(entry) > 2 else 0,
                                                    entry[3] if len(entry) > 3 else 0)
            lcis.append(q.lci())
    else:
        for sym in kata:
            x, y = symbol_to_xy(sym)
            q = ScarabQuaternion(math.sqrt(x**2 + y**2), 0,
                                  symbol_complexity(sym) / 4.0, 0)
            lcis.append(q.lci())

    if lcis:
        lci_mean = sum(lcis) / len(lcis)
        lci_var = sum((l - lci_mean)**2 for l in lcis) / len(lcis)
        lci_stability = max(0, 1 - lci_var / (lci_mean**2 + 0.01))
        if lci_stability > 0.7:
            patterns.append(f'LCI stable ({lci_stability:.0%})')
    else:
        lci_stability = 0

    # 4. Phase coherence (dual only)
    phase_coherence = 0
    if syms_R:
        # Measure consistent complexity relationship
        c_diffs = [symbol_complexity(syms_L[i]) - symbol_complexity(syms_R[i])
                    for i in range(n)]
        # Check if sign is consistent
        if all(d >= 0 for d in c_diffs) or all(d <= 0 for d in c_diffs):
            phase_coherence = 1.0
            patterns.append('Perfect phase coherence (one hand always leads)')
        else:
            pos = sum(1 for d in c_diffs if d >= 0)
            phase_coherence = max(pos, n - pos) / n
            if phase_coherence > 0.7:
                patterns.append(f'Strong phase coherence ({phase_coherence:.0%})')

    # 5. Complexity arc (crescendo/decrescendo)
    complexities = [symbol_complexity(s) for s in syms_L]
    if n >= 5:
        mid = n // 2
        rising = all(complexities[i] <= complexities[i+1]
                      for i in range(mid))
        falling = all(complexities[i] >= complexities[i+1]
                       for i in range(mid, n-1))
        if rising and falling:
            patterns.append('Crescendo-decrescendo arc')
        elif rising:
            patterns.append('Rising crescendo')
        elif falling:
            patterns.append('Falling decrescendo')

    # Compute overall resonance score (0-1)
    score_components = [
        lci_stability * 0.3,
        phase_coherence * 0.3 if syms_R else 0,
        (1.0 if is_palindrome else 0.5 if patterns else 0) * 0.2,
        min(len(patterns) / 4, 1.0) * 0.2,
    ]
    resonance_score = sum(score_components)

    return {
        'resonance_score': round(resonance_score, 3),
        'patterns': patterns,
        'lci_stability': round(lci_stability, 3),
        'phase_coherence': round(phase_coherence, 3) if syms_R else None,
        'is_palindrome': is_palindrome,
        'lci_values': [round(l, 3) for l in lcis],
    }


# ═══════════════════════════════════════════════════════════
# RESONANCE-GUIDED KATA GENERATION (v11)
# ═══════════════════════════════════════════════════════════

def resonance_kata(length=7, mastery_level=3, target_resonance=0.7,
                   mode='dual', max_attempts=50, base_seed=None):
    """
    Generate a kata that achieves a target resonance score.

    Strategy: generate candidates, score each with detect_resonance(),
    and keep the best one that meets the target.

    Args:
        length: tacts per kata
        mastery_level: 1-5
        target_resonance: desired resonance score (0-1)
        mode: 'single' or 'dual'
        max_attempts: max generation attempts
        base_seed: reproducibility seed

    Returns:
        dict with 'kata', 'resonance', 'attempts', 'score'
    """
    rng = random.Random(base_seed)
    best = None
    best_res = -1

    for attempt in range(max_attempts):
        seed = rng.randint(0, 2**31)
        if mode == 'dual':
            dma = DualMatchStickAutomaton(
                mastery_level=mastery_level,
                use_mudras=(mastery_level >= 4),
                seed=seed)
            kata = dma.generate_dual_kata(length=length)
        else:
            msa = MatchStickAutomaton(mastery_level=mastery_level, seed=seed)
            kata = msa.generate_kata(length=length)

        res = detect_resonance(kata, mode=mode)
        sc = score_dual_kata(kata) if mode == 'dual' else None

        if res['resonance_score'] > best_res:
            best_res = res['resonance_score']
            best = {
                'kata': kata,
                'resonance': res,
                'score': sc,
                'attempts': attempt + 1,
                'seed': seed,
            }

        if res['resonance_score'] >= target_resonance:
            break

    return best


# ═══════════════════════════════════════════════════════════
# STUDENT PROFILE — persistent state across sessions (v11)
# ═══════════════════════════════════════════════════════════

class StudentProfile:
    """
    Track a student's training history and identify weaknesses.

    Maintains:
    - Session log with scores, LCI, resonance per session
    - Per-rule compliance history (Rules 1-5)
    - Group coverage heatmap (which Kryukov groups are weak)
    - Current effective mastery level (auto-estimated)

    Usage:
        student = StudentProfile('Alexei', mastery_level=2)
        student.record_session(kata, quarter='Q1', year=1)
        student.record_session(kata2, quarter='Q1', year=1)
        print(student.summary())
        weaknesses = student.weaknesses()
    """

    def __init__(self, name, mastery_level=1):
        self.name = name
        self.mastery_level = mastery_level
        self.sessions = []         # list of session dicts
        self.rule_history = {r: [] for r in range(1, 6)}
        self.group_hits = {g: 0 for g in range(1, 8)}
        self.total_tacts = 0

    def record_session(self, kata, quarter='Q1', year=1, mode='dual'):
        """Record a completed training session."""
        if mode == 'dual':
            sc = score_dual_kata(kata)
            res = detect_resonance(kata, mode='dual')
            lci = compute_lci(kata, mode='dual')

            # Track per-rule compliance
            for r in range(1, 6):
                rule_str = sc['rules'][r]
                num, den = rule_str.split('/')
                pct = int(num) / max(int(den), 1) * 100
                self.rule_history[r].append(pct)

            # Track group coverage
            for entry in kata:
                self.group_hits[get_group(entry[0])] += 1
                self.group_hits[get_group(entry[1])] += 1
                self.total_tacts += 1
        else:
            sc = {'grade': 'A', 'pct': 100.0, 'rules': {}}
            res = detect_resonance(kata, mode='single')
            lci = compute_lci(kata, mode='single')
            for sym in kata:
                self.group_hits[get_group(sym)] += 1
                self.total_tacts += 1

        session = {
            'quarter': quarter,
            'year': year,
            'mode': mode,
            'n_tacts': len(kata),
            'grade': sc['grade'],
            'pct': sc['pct'],
            'lci_avg': lci['avg'],
            'resonance': res['resonance_score'],
            'patterns': res['patterns'],
        }
        self.sessions.append(session)

        # Auto-adjust mastery estimate
        if len(self.sessions) >= 4:
            recent = self.sessions[-4:]
            avg_pct = sum(s['pct'] for s in recent) / len(recent)
            if avg_pct >= 85 and self.mastery_level < 5:
                self.mastery_level = min(5, self.mastery_level + 1)

        return session

    def weaknesses(self):
        """Identify weak areas based on training history."""
        weak = []

        # Per-rule weaknesses (avg < 70%)
        for r in range(1, 6):
            if self.rule_history[r]:
                avg = sum(self.rule_history[r]) / len(self.rule_history[r])
                if avg < 70:
                    names = {1: 'zone exclusion', 2: 'anti-symmetry',
                             3: 'lead alternation', 4: 'smoothness',
                             5: 'complexity conservation'}
                    weak.append({
                        'type': 'rule',
                        'rule': r,
                        'name': names[r],
                        'avg_pct': round(avg, 1),
                    })

        # Under-represented groups (< 10% of proportional share)
        if self.total_tacts > 0:
            expected = self.total_tacts / 7
            for g in range(1, 8):
                if self.group_hits[g] < expected * 0.3:
                    group_names = {1: 'Empty', 2: 'Single', 3: 'Angle',
                                   4: 'Parallel', 5: 'Triple',
                                   6: 'Master', 7: 'Peak'}
                    weak.append({
                        'type': 'group',
                        'group': g,
                        'name': group_names[g],
                        'hits': self.group_hits[g],
                        'expected': round(expected, 0),
                    })

        # Low resonance trend
        if len(self.sessions) >= 3:
            recent_res = [s['resonance'] for s in self.sessions[-3:]]
            avg_res = sum(recent_res) / len(recent_res)
            if avg_res < 0.4:
                weak.append({
                    'type': 'resonance',
                    'avg_score': round(avg_res, 2),
                    'detail': 'Low resonance — work on pattern consistency',
                })

        return weak

    def summary(self):
        """Format student profile as readable text."""
        lines = [f"Student: {self.name}  (mastery={self.mastery_level})"]
        lines.append(f"Sessions: {len(self.sessions)}  Tacts: {self.total_tacts}")

        if self.sessions:
            grades = [s['grade'] for s in self.sessions]
            avg_pct = sum(s['pct'] for s in self.sessions) / len(self.sessions)
            avg_res = sum(s['resonance'] for s in self.sessions) / len(self.sessions)
            lines.append(f"Avg grade: {avg_pct:.0f}%  Avg resonance: {avg_res:.2f}")

            # Grade distribution
            dist = {}
            for g in grades:
                dist[g] = dist.get(g, 0) + 1
            dist_str = ', '.join(f"{g}:{n}" for g, n in sorted(dist.items()))
            lines.append(f"Grades: {dist_str}")

        # Group heatmap (compact)
        if self.total_tacts > 0:
            heatmap = []
            for g in range(1, 8):
                pct = self.group_hits[g] / self.total_tacts * 100
                bar = '#' * max(1, round(pct / 5))
                heatmap.append(f"  G{g}: {bar} {pct:.0f}%")
            lines.append("Group coverage:")
            lines.extend(heatmap)

        # Weaknesses
        weak = self.weaknesses()
        if weak:
            lines.append("Weaknesses:")
            for w in weak:
                if w['type'] == 'rule':
                    lines.append(f"  Rule {w['rule']} ({w['name']}): {w['avg_pct']}%")
                elif w['type'] == 'group':
                    lines.append(f"  Group {w['group']} ({w['name']}): "
                                 f"{w['hits']} hits (need ~{w['expected']:.0f})")
                elif w['type'] == 'resonance':
                    lines.append(f"  Resonance: {w['avg_score']} — {w['detail']}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ADAPTIVE CURRICULUM — auto-schedule based on weaknesses (v11)
# ═══════════════════════════════════════════════════════════

def adaptive_curriculum(student, n_sessions=4, seed=None):
    """
    Generate an adaptive training plan based on student weaknesses.

    The scheduler:
    1. Identifies weak rules and under-represented groups
    2. Generates kata that target those weaknesses
    3. Adjusts difficulty (length, mastery) to challenge level

    Args:
        student: StudentProfile instance
        n_sessions: number of sessions to plan
        seed: reproducibility seed

    Returns:
        list of dicts with 'kata', 'focus', 'difficulty', 'target'
    """
    rng = random.Random(seed)
    weak = student.weaknesses()

    # Determine focus groups (under-represented)
    focus_groups = None
    weak_groups = [w for w in weak if w['type'] == 'group']
    if weak_groups:
        focus_groups = [w['group'] for w in weak_groups[:3]]

    # Determine if we need resonance training
    needs_resonance = any(w['type'] == 'resonance' for w in weak)

    # Determine mastery level for training
    mastery = student.mastery_level

    plan = []
    for i in range(n_sessions):
        session_seed = rng.randint(0, 2**31)
        focus_desc = []

        # Adaptive length: start short if struggling, grow if improving
        if student.sessions:
            recent_pct = sum(s['pct'] for s in student.sessions[-3:]) / min(3, len(student.sessions))
            if recent_pct >= 80:
                length = 7  # confident — standard length
            elif recent_pct >= 60:
                length = 5  # moderate — shorter kata
            else:
                length = 3  # struggling — minimal kata
        else:
            length = 5  # new student — medium

        if needs_resonance and (i % 2 == 0):
            # Resonance-focused session
            result = resonance_kata(
                length=length,
                mastery_level=mastery,
                target_resonance=0.6,
                mode='dual',
                max_attempts=20,
                base_seed=session_seed)
            focus_desc.append('resonance')
        elif focus_groups:
            # Group-targeted session via optimize_kata
            opt = optimize_kata(
                length=length,
                mastery_level=mastery,
                target_grade='C',
                max_attempts=15,
                groups=focus_groups,
                base_seed=session_seed)
            res = detect_resonance(opt['kata'], mode='dual')
            result = {
                'kata': opt['kata'],
                'score': opt['score'],
                'resonance': res,
            }
            focus_desc.append(f"groups {focus_groups}")
        else:
            # Standard generation
            use_mudras = (mastery >= 4)
            dma = DualMatchStickAutomaton(
                mastery_level=mastery,
                use_mudras=use_mudras,
                seed=session_seed)
            kata = dma.generate_dual_kata(length=length)
            score = score_dual_kata(kata)
            res = detect_resonance(kata, mode='dual')
            result = {
                'kata': kata,
                'score': score,
                'resonance': res,
            }

        # Add weak rule descriptions
        weak_rules = [w for w in weak if w['type'] == 'rule']
        if weak_rules:
            focus_desc.append(f"rules {[w['rule'] for w in weak_rules[:2]]}")

        plan.append({
            'session': i + 1,
            'kata': result['kata'],
            'score': result.get('score'),
            'resonance': result.get('resonance', result.get('resonance')),
            'length': length,
            'mastery': mastery,
            'focus': ', '.join(focus_desc) if focus_desc else 'general',
            'seed': session_seed,
        })

    return plan


def format_curriculum(plan, student_name='Student'):
    """Format an adaptive curriculum as readable text."""
    lines = [f"Adaptive Curriculum for {student_name}"]
    lines.append(f"Sessions planned: {len(plan)}")
    lines.append("-" * 40)
    for p in plan:
        grade = p['score']['grade'] if p['score'] else '?'
        pct = p['score']['pct'] if p['score'] else 0
        res_score = 0
        if p['resonance']:
            if isinstance(p['resonance'], dict):
                res_score = p['resonance'].get('resonance_score', 0)
        lines.append(
            f"  #{p['session']}: L{p['mastery']} "
            f"len={p['length']} "
            f"grade={grade}({pct:.0f}%) "
            f"res={res_score:.2f} "
            f"focus=[{p['focus']}]")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# DRILL GENERATOR — micro-exercises for specific weaknesses (v12)
# ═══════════════════════════════════════════════════════════

def generate_drill(target='rule', rule_num=None, group_num=None,
                   n_reps=5, mastery_level=3, seed=None):
    """
    Generate a focused drill targeting a specific weakness.

    Drill types:
      target='rule':  practice a single coordination rule
      target='group': practice symbols from a specific Kryukov group
      target='transition': practice smooth transitions (Hamming ≤ 2)

    Each drill is a short kata (3 tacts) repeated n_reps times
    with slight variation to avoid memorisation.

    Returns:
        dict with 'drills' (list of mini-kata), 'target', 'description'
    """
    rng = random.Random(seed)
    drills = []
    desc = ''

    if target == 'rule' and rule_num is not None:
        desc = {1: 'Zone exclusion', 2: 'Anti-symmetry',
                3: 'Lead alternation', 4: 'Smoothness',
                5: 'Complexity conservation'}.get(rule_num, f'Rule {rule_num}')

        for rep in range(n_reps):
            # Generate until the specific rule is satisfied
            best = None
            best_score = -1
            for _ in range(20):
                dma = DualMatchStickAutomaton(
                    mastery_level=mastery_level,
                    seed=rng.randint(0, 2**31))
                kata = dma.generate_dual_kata(length=3)
                sc = score_dual_kata(kata)
                rule_str = sc['rules'][rule_num]
                num, den = rule_str.split('/')
                rule_pct = int(num) / max(int(den), 1)
                if rule_pct > best_score:
                    best_score = rule_pct
                    best = kata
                if rule_pct >= 1.0:
                    break
            drills.append(best)

    elif target == 'group' and group_num is not None:
        group_names = {1: 'Empty', 2: 'Single', 3: 'Angle',
                       4: 'Parallel', 5: 'Triple',
                       6: 'Master', 7: 'Peak'}
        desc = f"Group {group_num} ({group_names.get(group_num, '?')})"

        # Find all symbols in target group
        group_syms = [s for s in range(64) if get_group(s) == group_num]

        for rep in range(n_reps):
            # Build a mini-kata from group symbols
            mini = []
            for _ in range(3):
                L = rng.choice(group_syms) if group_syms else 0
                # R from a different group for anti-symmetry
                other_syms = [s for s in range(64)
                              if get_group(s) != group_num and not zones_conflict(L, s)]
                R = rng.choice(other_syms) if other_syms else (63 - L) % 64
                chvs_L = rng.randint(0, 3)
                chvs_R = rng.randint(0, 3)
                mini.append((L, R, chvs_L, chvs_R))
            drills.append(mini)

    elif target == 'transition':
        desc = 'Smooth transitions (Hamming ≤ 2)'

        for rep in range(n_reps):
            # Start from random symbol, force Hamming ≤ 2 each step
            L = rng.randint(0, 63)
            R = rng.randint(0, 63)
            mini = [(L, R, rng.randint(0, 3), rng.randint(0, 3))]
            for _ in range(2):
                nL = rng.choice(get_neighbors(L, max_changes=2))
                nR = rng.choice(get_neighbors(R, max_changes=2))
                mini.append((nL, nR, rng.randint(0, 3), rng.randint(0, 3)))
                L, R = nL, nR
            drills.append(mini)

    return {
        'target': target,
        'description': desc,
        'n_reps': n_reps,
        'drills': drills,
        'scores': [score_dual_kata(d) for d in drills],
    }


def format_drill(drill_result):
    """Format a drill result as readable text."""
    lines = [f"Drill: {drill_result['description']}"]
    lines.append(f"Reps: {drill_result['n_reps']}")
    for i, (d, sc) in enumerate(zip(drill_result['drills'], drill_result['scores'])):
        syms = ' → '.join(f"({e[0]:02d},{e[1]:02d})" for e in d)
        lines.append(f"  Rep {i+1}: {syms}  [{sc['grade']}]")
    avg_pct = sum(s['pct'] for s in drill_result['scores']) / len(drill_result['scores'])
    lines.append(f"  Avg: {avg_pct:.0f}%")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SPARRING SYSTEM — two students compete (v12)
# ═══════════════════════════════════════════════════════════

def sparring(student_a, student_b, quarter='Q3', year=2, seed=None):
    """
    Simulate a sparring match between two students.

    Each student generates a kata at their current mastery level.
    A judge evaluates both kata and determines the winner.

    Scoring criteria:
    1. Kata grade (40% weight)
    2. Resonance score (20% weight)
    3. LCI proximity to π (20% weight)
    4. Group diversity (20% weight)

    Returns:
        dict with both kata, scores, detailed comparison, winner
    """
    rng = random.Random(seed)

    results = {}
    for label, student in [('A', student_a), ('B', student_b)]:
        dma = DualMatchStickAutomaton(
            mastery_level=student.mastery_level,
            use_mudras=(student.mastery_level >= 4),
            seed=rng.randint(0, 2**31))
        kata = dma.generate_dual_kata(
            length=TRAINING_PLAN[quarter]['kata_length'])

        sc = score_dual_kata(kata)
        res = detect_resonance(kata, mode='dual')
        lci = compute_lci(kata, mode='dual')
        analysis = analyze_kata(kata, mode='dual')

        # Composite score
        grade_pts = sc['pct'] / 100.0
        res_pts = res['resonance_score']
        # LCI: closer to π = better (max distance ~ 3.14)
        lci_pts = max(0, 1 - abs(lci['avg'] - math.pi) / math.pi)
        # Group diversity: n_groups / 7
        div_pts = analysis['n_groups'] / 7.0

        composite = (grade_pts * 0.4 + res_pts * 0.2 +
                     lci_pts * 0.2 + div_pts * 0.2)

        results[label] = {
            'student': student.name,
            'mastery': student.mastery_level,
            'kata': kata,
            'score': sc,
            'resonance': res,
            'lci': lci,
            'analysis': analysis,
            'composite': round(composite, 3),
            'breakdown': {
                'grade': round(grade_pts, 3),
                'resonance': round(res_pts, 3),
                'lci': round(lci_pts, 3),
                'diversity': round(div_pts, 3),
            },
        }

    # Determine winner
    if results['A']['composite'] > results['B']['composite']:
        winner = 'A'
    elif results['B']['composite'] > results['A']['composite']:
        winner = 'B'
    else:
        winner = 'draw'

    margin = abs(results['A']['composite'] - results['B']['composite'])

    return {
        'A': results['A'],
        'B': results['B'],
        'winner': winner,
        'margin': round(margin, 3),
        'decisive': margin > 0.1,
    }


def format_sparring(result):
    """Format sparring result as readable text."""
    lines = ["Sparring Match"]
    lines.append("=" * 40)
    for label in ['A', 'B']:
        r = result[label]
        bd = r['breakdown']
        lines.append(
            f"  {label}: {r['student']} (L{r['mastery']}) "
            f"composite={r['composite']:.3f}")
        lines.append(
            f"     grade={bd['grade']:.2f} res={bd['resonance']:.2f} "
            f"lci={bd['lci']:.2f} div={bd['diversity']:.2f}")
    lines.append("-" * 40)
    if result['winner'] == 'draw':
        lines.append("  Result: DRAW")
    else:
        w = result[result['winner']]
        dec = 'decisive' if result['decisive'] else 'narrow'
        lines.append(f"  Winner: {w['student']} ({dec}, +{result['margin']:.3f})")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# KATA DNA — compact fingerprint for classification (v12)
# ═══════════════════════════════════════════════════════════

def kata_dna(kata, mode='dual'):
    """
    Compute a compact fingerprint (DNA) for a kata.

    The DNA encodes structural features as a fixed-length vector:
    - Group sequence (7 bins)
    - Complexity profile (mean, std, range)
    - Transition profile (mean Hamming, smoothness %)
    - Symmetry metrics (palindrome distance, phase coherence)
    - Resonance signature (top 3 pattern types)

    Returns:
        dict with 'vector' (list of floats), 'hex' (hex digest),
        'profile' (human-readable)
    """
    if mode == 'dual':
        syms_L = [e[0] for e in kata]
        syms_R = [e[1] for e in kata]
    else:
        syms_L = list(kata)
        syms_R = []

    n = len(syms_L)

    # 1. Group distribution (7 values, normalised)
    group_dist = [0.0] * 7
    for s in syms_L + syms_R:
        g = get_group(s)
        if 1 <= g <= 7:
            group_dist[g - 1] += 1
    total_syms = len(syms_L) + len(syms_R)
    if total_syms > 0:
        group_dist = [c / total_syms for c in group_dist]

    # 2. Complexity profile (3 values)
    complexities = [symbol_complexity(s) for s in syms_L + syms_R]
    c_mean = sum(complexities) / len(complexities) if complexities else 0
    c_std = (sum((c - c_mean)**2 for c in complexities) /
             len(complexities)) ** 0.5 if complexities else 0
    c_range = (max(complexities) - min(complexities)) if complexities else 0

    # 3. Transition profile (2 values)
    hammings = []
    for syms in [syms_L, syms_R]:
        for i in range(1, len(syms)):
            hammings.append(hamming_distance(syms[i], syms[i-1]))
    h_mean = sum(hammings) / len(hammings) if hammings else 0
    smooth_pct = sum(1 for h in hammings if h <= 2) / len(hammings) if hammings else 0

    # 4. Symmetry (2 values)
    groups_L = [get_group(s) for s in syms_L]
    palindrome_dist = sum(1 for i in range(n // 2)
                          if groups_L[i] != groups_L[n - 1 - i]) / max(n // 2, 1)
    phase_coh = 0.0
    if syms_R:
        diffs = [symbol_complexity(syms_L[i]) - symbol_complexity(syms_R[i])
                 for i in range(n)]
        pos = sum(1 for d in diffs if d >= 0)
        phase_coh = max(pos, n - pos) / n if n > 0 else 0

    # 5. Build vector (14 dimensions)
    vector = (group_dist +                       # 7
              [c_mean / 4, c_std / 2, c_range / 4] +  # 3
              [h_mean / 6, smooth_pct] +         # 2
              [1 - palindrome_dist, phase_coh])   # 2

    # Hex digest (hash of vector for quick comparison)
    import hashlib
    vec_str = ','.join(f"{v:.4f}" for v in vector)
    hex_digest = hashlib.md5(vec_str.encode()).hexdigest()[:12]

    # Human-readable profile
    dominant_group = group_dist.index(max(group_dist)) + 1
    group_names = {1: 'Empty', 2: 'Single', 3: 'Angle',
                   4: 'Parallel', 5: 'Triple', 6: 'Master', 7: 'Peak'}
    profile = (f"G{dominant_group}({group_names[dominant_group]}) "
               f"C={c_mean:.1f}±{c_std:.1f} "
               f"H={h_mean:.1f}({smooth_pct:.0%}smooth) "
               f"pal={1-palindrome_dist:.0%}")

    return {
        'vector': [round(v, 4) for v in vector],
        'hex': hex_digest,
        'profile': profile,
        'dimensions': 14,
    }


def kata_similarity(dna_a, dna_b):
    """
    Compute similarity between two kata DNA fingerprints.

    Uses cosine similarity on the 14-dimensional vectors.

    Returns:
        float 0-1 (1 = identical structure)
    """
    va = dna_a['vector']
    vb = dna_b['vector']
    dot = sum(a * b for a, b in zip(va, vb))
    mag_a = sum(a**2 for a in va) ** 0.5
    mag_b = sum(b**2 for b in vb) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return round(dot / (mag_a * mag_b), 4)


# ═══════════════════════════════════════════════════════════
# KATA LIBRARY — store, search, retrieve by DNA (v13)
# ═══════════════════════════════════════════════════════════

class KataLibrary:
    """
    In-memory library of kata with DNA-based search.

    Stores kata with metadata, enables:
    - Add kata with tags and source info
    - Search by DNA similarity (top-k nearest)
    - Filter by grade, tags, mastery level
    - Export/import as plain dict
    """

    def __init__(self):
        self.entries = []  # list of {kata, dna, score, tags, meta}

    def add(self, kata, mode='dual', tags=None, source='unknown',
            mastery_level=None):
        """Add a kata to the library."""
        dna = kata_dna(kata, mode=mode)
        sc = score_dual_kata(kata) if mode == 'dual' else {'grade': '?', 'pct': 0}
        entry = {
            'id': len(self.entries),
            'kata': kata,
            'dna': dna,
            'score': sc,
            'tags': set(tags or []),
            'source': source,
            'mastery_level': mastery_level,
            'mode': mode,
        }
        self.entries.append(entry)
        return entry['id']

    def search(self, query_kata=None, query_dna=None, top_k=5,
               min_grade=None, tags_filter=None, mode='dual'):
        """
        Search library for similar kata.

        Provide either query_kata or query_dna. Returns top-k matches
        sorted by descending similarity.
        """
        if query_dna is None and query_kata is not None:
            query_dna = kata_dna(query_kata, mode=mode)

        results = []
        for entry in self.entries:
            # Filter by grade
            if min_grade and entry['score'].get('grade', 'F') > min_grade:
                continue
            # Filter by tags
            if tags_filter and not tags_filter.issubset(entry['tags']):
                continue

            sim = kata_similarity(query_dna, entry['dna']) if query_dna else 0
            results.append((sim, entry))

        results.sort(key=lambda x: -x[0])
        return results[:top_k]

    def by_grade(self, grade):
        """Get all entries with a specific grade."""
        return [e for e in self.entries if e['score'].get('grade') == grade]

    def by_tag(self, tag):
        """Get all entries containing a specific tag."""
        return [e for e in self.entries if tag in e['tags']]

    def stats(self):
        """Library statistics."""
        grades = {}
        for e in self.entries:
            g = e['score'].get('grade', '?')
            grades[g] = grades.get(g, 0) + 1
        all_tags = set()
        for e in self.entries:
            all_tags.update(e['tags'])
        return {
            'total': len(self.entries),
            'grades': grades,
            'tags': sorted(all_tags),
        }


def format_library_search(results):
    """Format search results as readable text."""
    lines = [f"Search results ({len(results)} matches):"]
    for sim, entry in results:
        lines.append(
            f"  #{entry['id']:03d} sim={sim:.3f} "
            f"[{entry['score'].get('grade', '?')}] "
            f"{entry['dna']['profile']} "
            f"tags={sorted(entry['tags'])}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# KATA MUTATION — variations of existing kata (v13)
# ═══════════════════════════════════════════════════════════

def mutate_kata(kata, mutation='mirror', seed=None):
    """
    Create a variation of an existing dual kata.

    Mutations:
      'mirror':     swap L ↔ R hands
      'reverse':    reverse tact order
      'shift':      shift all symbols by ±1 bit (Hamming neighbor)
      'recolor':    randomise ChVS values keeping symbols
      'crossover':  splice two halves from original + shifted copy

    Returns:
        new dual kata (list of tuples)
    """
    rng = random.Random(seed)
    n = len(kata)

    if mutation == 'mirror':
        # Swap left and right hands
        return [(e[1], e[0]) + e[2:] for e in kata]

    elif mutation == 'reverse':
        # Reverse tact order
        return list(reversed(kata))

    elif mutation == 'shift':
        # Shift every symbol to a Hamming neighbor
        result = []
        for e in kata:
            L = e[0]
            R = e[1]
            nL = rng.choice(get_neighbors(L, max_changes=1))
            nR = rng.choice(get_neighbors(R, max_changes=1))
            rest = e[2:] if len(e) > 2 else (rng.randint(0, 3), rng.randint(0, 3))
            result.append((nL, nR) + rest)
        return result

    elif mutation == 'recolor':
        # Keep symbols, randomise ChVS
        return [(e[0], e[1], rng.randint(0, 3), rng.randint(0, 3))
                for e in kata]

    elif mutation == 'crossover':
        # Splice: first half original, second half shifted
        mid = n // 2
        shifted = mutate_kata(kata, mutation='shift', seed=seed)
        return list(kata[:mid]) + list(shifted[mid:])

    else:
        return list(kata)  # identity


def mutate_series(kata, n_variants=5, seed=None):
    """
    Generate a series of mutations from one parent kata.

    Applies all 5 mutation types and scores each variant.

    Returns:
        list of {mutation, kata, score, dna, similarity_to_parent}
    """
    rng = random.Random(seed)
    parent_dna = kata_dna(kata, mode='dual')
    mutations = ['mirror', 'reverse', 'shift', 'recolor', 'crossover']

    variants = []
    for mut in mutations[:n_variants]:
        variant = mutate_kata(kata, mutation=mut, seed=rng.randint(0, 2**31))
        v_dna = kata_dna(variant, mode='dual')
        v_sc = score_dual_kata(variant)
        sim = kata_similarity(parent_dna, v_dna)
        variants.append({
            'mutation': mut,
            'kata': variant,
            'score': v_sc,
            'dna': v_dna,
            'similarity': sim,
        })
    return variants


# ═══════════════════════════════════════════════════════════
# SESSION PLANNER — structured multi-phase session (v13)
# ═══════════════════════════════════════════════════════════

def plan_session(student, quarter='Q3', year=2, duration_min=45, seed=None):
    """
    Plan a structured training session with phases.

    Phases:
      1. Warm-up (10%):  easy drills, low mastery, familiar groups
      2. Review  (15%):  repeat best kata from last 3 sessions
      3. Main    (45%):  new kata at current level, targeting weaknesses
      4. Drill   (20%):  focused drills on top 2 weaknesses
      5. Cool-dn (10%):  easy kata, review notation

    Returns:
        dict with phases, each containing kata/drills and timing
    """
    rng = random.Random(seed)
    weaknesses = student.weaknesses()
    ml = student.mastery_level

    phases = []

    # Phase 1: Warm-up (10%)
    warmup_min = int(duration_min * 0.10)
    warmup_dma = DualMatchStickAutomaton(
        mastery_level=max(1, ml - 2), seed=rng.randint(0, 2**31))
    warmup_kata = warmup_dma.generate_dual_kata(length=3)
    phases.append({
        'name': 'Warm-up',
        'duration_min': warmup_min,
        'type': 'kata',
        'content': warmup_kata,
        'score': score_dual_kata(warmup_kata),
        'notes': f'Easy kata at L{max(1, ml - 2)}',
    })

    # Phase 2: Review (15%)
    review_min = int(duration_min * 0.15)
    if student.sessions:
        # Generate a review kata at slightly lower difficulty
        review_dma = DualMatchStickAutomaton(
            mastery_level=max(1, ml - 1), seed=rng.randint(0, 2**31))
        review_kata = review_dma.generate_dual_kata(length=4)
        review_note = f'Review at L{max(1, ml-1)} (based on {len(student.sessions)} sessions)'
    else:
        review_dma = DualMatchStickAutomaton(
            mastery_level=ml, seed=rng.randint(0, 2**31))
        review_kata = review_dma.generate_dual_kata(length=4)
        review_note = 'New review kata (no history)'
    phases.append({
        'name': 'Review',
        'duration_min': review_min,
        'type': 'kata',
        'content': review_kata,
        'score': score_dual_kata(review_kata),
        'notes': review_note,
    })

    # Phase 3: Main work (45%)
    main_min = int(duration_min * 0.45)
    length = TRAINING_PLAN.get(quarter, TRAINING_PLAN['Q1'])['kata_length']
    main_dma = DualMatchStickAutomaton(
        mastery_level=ml,
        use_mudras=(ml >= 4),
        seed=rng.randint(0, 2**31))
    main_kata = main_dma.generate_dual_kata(length=length)
    phases.append({
        'name': 'Main work',
        'duration_min': main_min,
        'type': 'kata',
        'content': main_kata,
        'score': score_dual_kata(main_kata),
        'notes': f'{quarter}/Y{year} kata at L{ml}, len={length}',
    })

    # Phase 4: Drills (20%)
    drill_min = int(duration_min * 0.20)
    drill_items = []
    # Target top 2 weaknesses
    rule_weaks = [w for w in weaknesses if w['type'] == 'rule'][:1]
    group_weaks = [w for w in weaknesses if w['type'] == 'group'][:1]
    for w in rule_weaks:
        dr = generate_drill(target='rule', rule_num=w['rule'],
                            n_reps=3, mastery_level=ml,
                            seed=rng.randint(0, 2**31))
        drill_items.append(dr)
    for w in group_weaks:
        dr = generate_drill(target='group', group_num=w['group'],
                            n_reps=3, mastery_level=ml,
                            seed=rng.randint(0, 2**31))
        drill_items.append(dr)
    if not drill_items:
        dr = generate_drill(target='transition', n_reps=3,
                            mastery_level=ml,
                            seed=rng.randint(0, 2**31))
        drill_items.append(dr)
    phases.append({
        'name': 'Drills',
        'duration_min': drill_min,
        'type': 'drills',
        'content': drill_items,
        'notes': f'{len(drill_items)} drill(s) for weaknesses',
    })

    # Phase 5: Cool-down (10%)
    cooldown_min = duration_min - sum(p['duration_min'] for p in phases)
    cd_dma = DualMatchStickAutomaton(
        mastery_level=max(1, ml - 1), seed=rng.randint(0, 2**31))
    cd_kata = cd_dma.generate_dual_kata(length=3)
    phases.append({
        'name': 'Cool-down',
        'duration_min': cooldown_min,
        'type': 'kata',
        'content': cd_kata,
        'score': score_dual_kata(cd_kata),
        'notes': f'Easy kata at L{max(1, ml - 1)}, review notation',
    })

    return {
        'student': student.name,
        'quarter': quarter,
        'year': year,
        'duration_min': duration_min,
        'phases': phases,
        'n_phases': len(phases),
    }


def format_session_plan(plan):
    """Format a session plan as readable text."""
    lines = [f"Session Plan: {plan['student']} "
             f"({plan['quarter']}/Y{plan['year']}, "
             f"{plan['duration_min']} min)"]
    lines.append("=" * 50)
    t = 0
    for p in plan['phases']:
        t_end = t + p['duration_min']
        lines.append(f"  [{t:02d}-{t_end:02d} min] {p['name']} "
                     f"({p['duration_min']} min)")
        if p['type'] == 'kata' and 'score' in p:
            lines.append(f"    Grade: {p['score']['grade']} "
                         f"({p['score']['pct']:.0f}%)")
        elif p['type'] == 'drills':
            for dr in p['content']:
                avg = sum(s['pct'] for s in dr['scores']) / len(dr['scores'])
                lines.append(f"    Drill: {dr['description']} "
                             f"(avg {avg:.0f}%)")
        lines.append(f"    {p['notes']}")
        t = t_end
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# TOURNAMENT — bracket competition for N students (v14)
# ═══════════════════════════════════════════════════════════

def tournament(students, quarter='Q3', year=2, seed=None):
    """
    Run a bracket-style tournament among N students.

    Bracket format:
    - Students paired randomly
    - Each pair sparring → winner advances
    - Byes for odd numbers
    - Continues until one champion remains

    Returns:
        dict with rounds, results per match, champion, rankings
    """
    rng = random.Random(seed)
    n = len(students)
    if n < 2:
        return {'error': 'Need at least 2 students', 'rounds': []}

    # Shuffle students
    pool = list(students)
    rng.shuffle(pool)

    rounds = []
    eliminated = []
    round_num = 0

    while len(pool) > 1:
        round_num += 1
        matches = []
        winners = []

        # Pair up students
        i = 0
        while i < len(pool) - 1:
            a, b = pool[i], pool[i + 1]
            result = sparring(a, b, quarter=quarter, year=year,
                              seed=rng.randint(0, 2**31))
            if result['winner'] == 'A':
                winners.append(a)
                eliminated.append((b, round_num))
            elif result['winner'] == 'B':
                winners.append(b)
                eliminated.append((a, round_num))
            else:
                # Draw: first player advances (home advantage)
                winners.append(a)
                eliminated.append((b, round_num))
            matches.append({
                'a': a.name, 'b': b.name,
                'score_a': result['A']['composite'],
                'score_b': result['B']['composite'],
                'winner': result[result['winner']]['student']
                          if result['winner'] != 'draw' else a.name,
                'margin': result['margin'],
                'decisive': result['decisive'],
            })
            i += 2

        # Bye for odd player
        if len(pool) % 2 == 1:
            bye = pool[-1]
            winners.append(bye)
            matches.append({
                'a': bye.name, 'b': 'BYE',
                'winner': bye.name, 'margin': 0, 'decisive': False,
                'score_a': 0, 'score_b': 0,
            })

        rounds.append({
            'round': round_num,
            'matches': matches,
            'advancing': [w.name for w in winners],
        })
        pool = winners

    champion = pool[0]

    # Build rankings: champion=1, finalist=2, semifinalists=3-4, etc.
    rankings = [(champion.name, 1)]
    for student, elim_round in reversed(eliminated):
        rank = len(rankings) + 1
        rankings.append((student.name, rank))

    return {
        'rounds': rounds,
        'n_rounds': round_num,
        'champion': champion.name,
        'rankings': rankings,
        'n_students': n,
    }


def format_tournament(result):
    """Format tournament results as readable text."""
    lines = [f"Tournament ({result['n_students']} students, "
             f"{result['n_rounds']} rounds)"]
    lines.append("=" * 50)
    for rnd in result['rounds']:
        lines.append(f"\n  Round {rnd['round']}:")
        for m in rnd['matches']:
            if m['b'] == 'BYE':
                lines.append(f"    {m['a']} — BYE")
            else:
                dec = '*' if m['decisive'] else ''
                lines.append(
                    f"    {m['a']} ({m['score_a']:.3f}) vs "
                    f"{m['b']} ({m['score_b']:.3f}) "
                    f"→ {m['winner']}{dec} (+{m['margin']:.3f})")
    lines.append(f"\n  Champion: {result['champion']}")
    lines.append("  Rankings:")
    for name, rank in result['rankings']:
        lines.append(f"    #{rank}: {name}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# DIFFICULTY ESTIMATOR — predict kata difficulty (v14)
# ═══════════════════════════════════════════════════════════

def estimate_difficulty(kata, mode='dual'):
    """
    Estimate difficulty of a kata on a 1-10 scale.

    Factors (each contributes 0-2 points):
    1. Complexity variance — high variance = harder
    2. Transition speed — large Hamming jumps = harder
    3. Group diversity — more groups = harder
    4. Rule compliance difficulty — low natural score = harder
    5. Length — longer = harder

    Returns:
        dict with total difficulty (1-10), per-factor breakdown
    """
    if mode == 'dual':
        syms_L = [e[0] for e in kata]
        syms_R = [e[1] for e in kata]
    else:
        syms_L = list(kata)
        syms_R = []

    n = len(syms_L)
    all_syms = syms_L + syms_R

    # Factor 1: Complexity variance (0-2)
    complexities = [symbol_complexity(s) for s in all_syms]
    c_mean = sum(complexities) / len(complexities) if complexities else 0
    c_var = (sum((c - c_mean)**2 for c in complexities)
             / len(complexities)) if complexities else 0
    f1 = min(2.0, c_var / 1.5)

    # Factor 2: Transition speed (0-2)
    hammings = []
    for syms in [syms_L, syms_R]:
        for i in range(1, len(syms)):
            hammings.append(hamming_distance(syms[i], syms[i-1]))
    avg_h = sum(hammings) / len(hammings) if hammings else 0
    f2 = min(2.0, avg_h / 3.0 * 2)

    # Factor 3: Group diversity (0-2)
    groups = set(get_group(s) for s in all_syms)
    f3 = min(2.0, len(groups) / 4.0 * 2)

    # Factor 4: Rule compliance difficulty (0-2)
    if mode == 'dual':
        sc = score_dual_kata(kata)
        natural_pct = sc['pct'] / 100.0
        # Lower natural score = harder to perform
        f4 = min(2.0, (1 - natural_pct) * 3)
    else:
        f4 = 0.5

    # Factor 5: Length (0-2)
    f5 = min(2.0, n / 6.0 * 2)

    total = f1 + f2 + f3 + f4 + f5
    # Clamp to 1-10
    difficulty = max(1.0, min(10.0, total))

    return {
        'difficulty': round(difficulty, 1),
        'factors': {
            'complexity_variance': round(f1, 2),
            'transition_speed': round(f2, 2),
            'group_diversity': round(f3, 2),
            'rule_challenge': round(f4, 2),
            'length': round(f5, 2),
        },
        'level_name': _difficulty_name(difficulty),
    }


def _difficulty_name(d):
    """Map difficulty score to a name."""
    if d <= 2:
        return 'Beginner'
    elif d <= 4:
        return 'Elementary'
    elif d <= 6:
        return 'Intermediate'
    elif d <= 8:
        return 'Advanced'
    else:
        return 'Master'


# ═══════════════════════════════════════════════════════════
# ACHIEVEMENT SYSTEM — milestone badges (v14)
# ═══════════════════════════════════════════════════════════

ACHIEVEMENTS = {
    'first_kata': {
        'name': 'First Steps',
        'desc': 'Complete your first training session',
        'check': lambda s: len(s.sessions) >= 1,
    },
    'ten_sessions': {
        'name': 'Dedicated Student',
        'desc': 'Complete 10 training sessions',
        'check': lambda s: len(s.sessions) >= 10,
    },
    'grade_a': {
        'name': 'Excellence',
        'desc': 'Achieve Grade A on any kata',
        'check': lambda s: any(sess['grade'] == 'A' for sess in s.sessions),
    },
    'all_groups': {
        'name': 'Explorer',
        'desc': 'Use symbols from all 7 Kryukov groups',
        'check': lambda s: sum(1 for g in range(1, 8)
                               if s.group_hits.get(g, 0) > 0) == 7,
    },
    'high_resonance': {
        'name': 'Resonance Master',
        'desc': 'Achieve resonance score > 0.8 in a session',
        'check': lambda s: any(sess['resonance'] > 0.8 for sess in s.sessions),
    },
    'mastery_3': {
        'name': 'Intermediate',
        'desc': 'Reach mastery level 3',
        'check': lambda s: s.mastery_level >= 3,
    },
    'mastery_5': {
        'name': 'Master',
        'desc': 'Reach mastery level 5',
        'check': lambda s: s.mastery_level >= 5,
    },
    'consistency': {
        'name': 'Consistent',
        'desc': 'Score above 70% in 5 consecutive sessions',
        'check': lambda s: _check_consecutive(s, 5, 70),
    },
    'hundred_tacts': {
        'name': 'Centurion',
        'desc': 'Perform 100 total tacts',
        'check': lambda s: s.total_tacts >= 100,
    },
    'lci_pi': {
        'name': 'Pi Seeker',
        'desc': 'Achieve LCI average within 0.5 of pi',
        'check': lambda s: any(abs(sess['lci_avg'] - math.pi) < 0.5
                               for sess in s.sessions),
    },
}


def _check_consecutive(student, n, min_pct):
    """Check if student has n consecutive sessions above min_pct."""
    if len(student.sessions) < n:
        return False
    for i in range(len(student.sessions) - n + 1):
        window = student.sessions[i:i+n]
        if all(s['pct'] >= min_pct for s in window):
            return True
    return False


def check_achievements(student):
    """
    Check which achievements a student has earned.

    Returns:
        dict with 'earned' (list), 'pending' (list), 'progress' (pct)
    """
    earned = []
    pending = []
    for key, ach in ACHIEVEMENTS.items():
        if ach['check'](student):
            earned.append({'key': key, 'name': ach['name'],
                           'desc': ach['desc']})
        else:
            pending.append({'key': key, 'name': ach['name'],
                            'desc': ach['desc']})

    progress = len(earned) / len(ACHIEVEMENTS) * 100 if ACHIEVEMENTS else 0

    return {
        'earned': earned,
        'pending': pending,
        'progress': round(progress, 1),
        'total': len(ACHIEVEMENTS),
    }


def format_achievements(result):
    """Format achievements as readable text."""
    lines = [f"Achievements: {len(result['earned'])}/{result['total']} "
             f"({result['progress']:.0f}%)"]
    if result['earned']:
        lines.append("  Earned:")
        for a in result['earned']:
            lines.append(f"    [{a['name']}] {a['desc']}")
    if result['pending']:
        lines.append("  Pending:")
        for a in result['pending'][:3]:  # Show top 3 pending
            lines.append(f"    [ ] {a['name']}: {a['desc']}")
        if len(result['pending']) > 3:
            lines.append(f"    ... and {len(result['pending'])-3} more")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SCHOOL — full lifecycle management (v15)
# ═══════════════════════════════════════════════════════════

class School:
    """
    Full training school managing multiple students through
    enrollment → training → examination → graduation.

    Integrates all subsystems: library, sessions, drills,
    tournaments, achievements, difficulty estimation.
    """

    def __init__(self, name='Scarab School'):
        self.name = name
        self.students = {}        # name → StudentProfile
        self.library = KataLibrary()
        self.history = []         # log of all events
        self.graduated = []       # names of graduated students

    def enroll(self, name, mastery_level=1):
        """Enroll a new student."""
        if name in self.students:
            return f'{name} already enrolled'
        sp = StudentProfile(name, mastery_level=mastery_level)
        self.students[name] = sp
        self.history.append({
            'event': 'enroll', 'student': name,
            'mastery': mastery_level,
        })
        return sp

    def train(self, name, quarter='Q1', year=1, seed=None):
        """Run a full training session for a student."""
        if name not in self.students:
            return None
        student = self.students[name]
        session = plan_session(student, quarter=quarter, year=year,
                               duration_min=45, seed=seed)
        # Record the main kata
        main_phase = [p for p in session['phases'] if p['name'] == 'Main work']
        if main_phase:
            kata = main_phase[0]['content']
            student.record_session(kata, quarter=quarter, year=year,
                                   mode='dual')
            # Add to library
            self.library.add(kata, tags={f'{quarter}', name.lower()},
                             source=f'session_{name}',
                             mastery_level=student.mastery_level)
        self.history.append({
            'event': 'train', 'student': name,
            'quarter': quarter, 'year': year,
        })
        return session

    def examine(self, name, quarter='Q3', year=2, seed=None):
        """Run an exam for a student."""
        if name not in self.students:
            return None
        student = self.students[name]
        rng = random.Random(seed)
        exam = generate_exam(quarter=quarter, year=year,
                             mastery_level=student.mastery_level,
                             seed=rng.randint(0, 2**31))
        # Student attempts the exam
        dma = DualMatchStickAutomaton(
            mastery_level=student.mastery_level,
            seed=rng.randint(0, 2**31))
        student_kata = dma.generate_dual_kata(
            length=len(exam['reference']))
        result = evaluate_exam(exam, student_kata)
        self.history.append({
            'event': 'exam', 'student': name,
            'grade': result['score']['grade'],
            'pct': result['score']['pct'],
            'result': result['result'],
        })
        # Add convenience keys
        result['final_grade'] = result['score']['grade']
        result['final_pct'] = result['score']['pct']
        return result

    def graduate(self, name):
        """
        Check graduation requirements and graduate if met.

        Requirements:
        - At least 8 training sessions
        - Mastery level >= 3
        - At least 1 Grade A kata
        - At least 5 achievements earned
        """
        if name not in self.students:
            return {'eligible': False, 'reason': 'Not enrolled'}
        student = self.students[name]
        ach = check_achievements(student)

        reqs = {
            'sessions': (len(student.sessions) >= 8,
                         f'{len(student.sessions)}/8 sessions'),
            'mastery': (student.mastery_level >= 3,
                        f'L{student.mastery_level}/L3'),
            'grade_a': (any(s['grade'] == 'A' for s in student.sessions),
                        'Grade A achieved' if any(s['grade'] == 'A'
                        for s in student.sessions) else 'No Grade A'),
            'achievements': (len(ach['earned']) >= 5,
                             f"{len(ach['earned'])}/5 achievements"),
        }

        eligible = all(ok for ok, _ in reqs.values())

        if eligible:
            self.graduated.append(name)
            self.history.append({
                'event': 'graduate', 'student': name,
                'mastery': student.mastery_level,
            })

        return {
            'eligible': eligible,
            'student': name,
            'requirements': {k: {'met': ok, 'status': st}
                             for k, (ok, st) in reqs.items()},
            'achievements': ach,
        }

    def run_tournament(self, quarter='Q3', year=2, seed=None):
        """Run a tournament with all active students."""
        active = [s for n, s in self.students.items()
                  if n not in self.graduated and len(s.sessions) >= 2]
        if len(active) < 2:
            return {'error': 'Need at least 2 eligible students'}
        result = tournament(active, quarter=quarter, year=year, seed=seed)
        self.history.append({
            'event': 'tournament', 'champion': result['champion'],
            'n_students': result['n_students'],
        })
        return result

    def roster(self):
        """Get full school roster with stats."""
        roster = []
        for name, student in self.students.items():
            ach = check_achievements(student)
            status = 'graduated' if name in self.graduated else 'active'
            avg_pct = (sum(s['pct'] for s in student.sessions)
                       / len(student.sessions)) if student.sessions else 0
            roster.append({
                'name': name,
                'mastery': student.mastery_level,
                'sessions': len(student.sessions),
                'avg_grade': f'{avg_pct:.0f}%',
                'achievements': len(ach['earned']),
                'status': status,
            })
        return roster


def format_roster(roster):
    """Format school roster as readable text."""
    lines = [f"{'Name':12s} {'L':>2s} {'Sess':>4s} {'Avg':>5s} "
             f"{'Ach':>3s} {'Status':>10s}"]
    lines.append("-" * 42)
    for r in roster:
        lines.append(f"{r['name']:12s} {r['mastery']:2d} "
                     f"{r['sessions']:4d} {r['avg_grade']:>5s} "
                     f"{r['achievements']:3d} {r['status']:>10s}")
    return '\n'.join(lines)


def format_graduation(result):
    """Format graduation check as readable text."""
    lines = [f"Graduation Check: {result['student']}"]
    for req, info in result['requirements'].items():
        mark = 'V' if info['met'] else 'X'
        lines.append(f"  [{mark}] {req}: {info['status']}")
    if result['eligible']:
        lines.append("  >>> GRADUATED <<<")
    else:
        lines.append("  Status: Not yet eligible")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# EXPORT / IMPORT — JSON persistence (v15)
# ═══════════════════════════════════════════════════════════

def export_school_json(school):
    """
    Export entire school state as a JSON-serialisable dict.

    Includes: students (profiles, sessions), library entries,
    history log, graduation list.
    """
    students_data = {}
    for name, sp in school.students.items():
        students_data[name] = {
            'mastery_level': sp.mastery_level,
            'total_tacts': sp.total_tacts,
            'sessions': sp.sessions,
            'group_hits': dict(sp.group_hits),
            'rule_history': {str(k): list(v)
                             for k, v in sp.rule_history.items()},
        }

    library_data = []
    for entry in school.library.entries:
        library_data.append({
            'id': entry['id'],
            'dna_hex': entry['dna']['hex'],
            'dna_profile': entry['dna']['profile'],
            'dna_vector': entry['dna']['vector'],
            'grade': entry['score'].get('grade', '?'),
            'tags': sorted(entry['tags']),
            'source': entry['source'],
            'mastery_level': entry['mastery_level'],
        })

    return {
        'school_name': school.name,
        'students': students_data,
        'library': library_data,
        'history': school.history,
        'graduated': school.graduated,
        'n_students': len(school.students),
        'n_library': len(school.library.entries),
    }


def import_school_json(data):
    """
    Restore a School from exported JSON data.

    Note: kata content is not preserved in export (only DNA/stats).
    StudentProfile sessions and stats are fully restored.
    """
    school = School(name=data.get('school_name', 'Restored School'))
    school.history = data.get('history', [])
    school.graduated = data.get('graduated', [])

    for name, sdata in data.get('students', {}).items():
        sp = StudentProfile(name, mastery_level=sdata['mastery_level'])
        sp.total_tacts = sdata['total_tacts']
        sp.sessions = sdata['sessions']
        sp.group_hits = {int(k): v for k, v in sdata['group_hits'].items()}
        sp.rule_history = {int(k): list(v)
                           for k, v in sdata['rule_history'].items()}
        school.students[name] = sp

    return school


# ═══════════════════════════════════════════════════════════
# SYSTEM AUDIT — integrity check (v15)
# ═══════════════════════════════════════════════════════════

def audit_system():
    """
    Run a comprehensive audit of all SCARAB components.

    Checks:
    1. Alphabet integrity (76 symbols, group membership)
    2. Graph connectivity (64-node graph is connected)
    3. Scoring consistency (random kata score correctly)
    4. Quaternion conservation (|A| ≈ mastery at edges)
    5. DNA reproducibility (same kata → same DNA)
    6. Library search accuracy (self-search → sim=1.0)
    7. Mutation reversibility (mirror(mirror(x)) = x)
    8. Achievement monotonicity (more sessions → more achievements)
    """
    results = []

    # 1. Alphabet check
    total_syms = len(BASE_SYMBOLS) + len(HALF_SYMBOLS)
    ok1 = total_syms == 76
    results.append(('Alphabet', ok1, f'{total_syms}/76 symbols'))

    # 2. Graph connectivity (BFS from 0)
    from collections import deque as _deque_audit
    visited = set()
    q = _deque_audit([0])
    visited.add(0)
    while q:
        node = q.popleft()
        for nb in get_neighbors(node, max_changes=2):
            if nb not in visited and 0 <= nb < 64:
                visited.add(nb)
                q.append(nb)
    ok2 = len(visited) == 64
    results.append(('Graph connectivity', ok2, f'{len(visited)}/64 reachable'))

    # 3. Scoring: score_dual_kata returns valid structure
    rng_a = random.Random(999)
    dma = DualMatchStickAutomaton(mastery_level=3, seed=999)
    test_kata = dma.generate_dual_kata(length=5)
    sc = score_dual_kata(test_kata)
    ok3 = (sc['grade'] in 'ABCDF' and 0 <= sc['pct'] <= 100
            and len(sc['rules']) == 5)
    results.append(('Scoring', ok3,
                     f"grade={sc['grade']} pct={sc['pct']:.0f}%"))

    # 4. Quaternion conservation
    sq = ScarabQuaternion(1, 0, 0, 0)
    mag = sq.norm()
    ok4 = abs(mag - 1.0) < 1e-10
    results.append(('Quaternion', ok4, f'|unit|={mag:.10f}'))

    # 5. DNA reproducibility
    dna1 = kata_dna(test_kata, mode='dual')
    dna2 = kata_dna(test_kata, mode='dual')
    ok5 = dna1['hex'] == dna2['hex'] and dna1['vector'] == dna2['vector']
    results.append(('DNA reproducibility', ok5, f'hex={dna1["hex"]}'))

    # 6. Library self-search
    lib_test = KataLibrary()
    lib_test.add(test_kata, tags={'test'})
    search = lib_test.search(query_kata=test_kata, top_k=1)
    ok6 = len(search) > 0 and search[0][0] == 1.0
    results.append(('Library search', ok6,
                     f'self-sim={search[0][0] if search else "?":.3f}'))

    # 7. Mutation reversibility: mirror(mirror(x)) = x
    mirrored = mutate_kata(test_kata, mutation='mirror')
    restored = mutate_kata(mirrored, mutation='mirror')
    ok7 = all(r[0] == o[0] and r[1] == o[1]
              for r, o in zip(restored, test_kata))
    results.append(('Mirror reversibility', ok7, 'mirror^2 = identity'))

    # 8. Achievement monotonicity
    sp1 = StudentProfile('audit_test', mastery_level=1)
    ach1 = len(check_achievements(sp1)['earned'])
    for i in range(5):
        sk = generate_seasonal_kata('Q1', mastery_level=1, year=1,
                                    use_dual=True,
                                    seed=hash(f'audit{i}') % 2**31)
        sp1.record_session(sk['kata'], quarter='Q1', year=1, mode='dual')
    ach2 = len(check_achievements(sp1)['earned'])
    ok8 = ach2 >= ach1
    results.append(('Achievement monotonicity', ok8,
                     f'{ach1} → {ach2} achievements'))

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)

    return {
        'checks': results,
        'passed': passed,
        'total': total,
        'all_ok': passed == total,
    }


def format_audit(audit):
    """Format audit results as readable text."""
    lines = [f"System Audit: {audit['passed']}/{audit['total']} passed"]
    lines.append("=" * 50)
    for name, ok, detail in audit['checks']:
        mark = 'PASS' if ok else 'FAIL'
        lines.append(f"  [{mark}] {name:25s} {detail}")
    if audit['all_ok']:
        lines.append("\n  All checks passed. System integrity verified.")
    else:
        lines.append("\n  WARNING: Some checks failed!")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PROGRESS CHART — ASCII sparkline visualization (v16)
# ═══════════════════════════════════════════════════════════

def progress_chart(student, metric='grade', width=40):
    """
    Generate an ASCII sparkline chart of student progress over sessions.

    Metrics:
      'grade':     score percentage per session
      'resonance': resonance score per session
      'lci':       LCI average per session

    Returns:
        dict with 'chart' (ASCII string), 'data', 'trend'
    """
    if not student.sessions:
        return {'chart': '(no data)', 'data': [], 'trend': 0}

    if metric == 'grade':
        data = [s['pct'] for s in student.sessions]
        label = 'Grade %'
        vmin, vmax = 0, 100
    elif metric == 'resonance':
        data = [s['resonance'] for s in student.sessions]
        label = 'Resonance'
        vmin, vmax = 0, 1
    elif metric == 'lci':
        data = [s['lci_avg'] for s in student.sessions]
        label = 'LCI'
        vmin, vmax = 0, math.pi * 2
    else:
        data = [s['pct'] for s in student.sessions]
        label = metric
        vmin, vmax = 0, 100

    # Sparkline characters (8 levels)
    sparks = '▁▂▃▄▅▆▇█'
    n_levels = len(sparks)

    # Normalize and build sparkline
    span = vmax - vmin if vmax > vmin else 1
    sparkline = ''
    for v in data:
        level = int((v - vmin) / span * (n_levels - 1))
        level = max(0, min(n_levels - 1, level))
        sparkline += sparks[level]

    # Pad or truncate to width
    if len(sparkline) > width:
        # Sample evenly
        step = len(sparkline) / width
        sparkline = ''.join(sparkline[int(i * step)]
                            for i in range(width))
    elif len(sparkline) < width:
        sparkline = sparkline.ljust(width, ' ')

    # Trend: linear regression slope (simplified)
    n = len(data)
    if n >= 2:
        x_mean = (n - 1) / 2
        y_mean = sum(data) / n
        num = sum((i - x_mean) * (data[i] - y_mean) for i in range(n))
        den = sum((i - x_mean)**2 for i in range(n))
        slope = num / den if den > 0 else 0
    else:
        slope = 0

    trend_sym = '↑' if slope > 0.5 else ('↓' if slope < -0.5 else '→')

    # Build chart
    chart_lines = []
    chart_lines.append(f"{label} [{student.name}] {trend_sym}")
    chart_lines.append(f"  {vmax:>6.1f} ┤")
    chart_lines.append(f"        │ {sparkline}")
    chart_lines.append(f"  {vmin:>6.1f} ┤")
    chart_lines.append(f"         {'1':>{1}} "
                       f"{'→':^{max(1,len(sparkline)-2)}} "
                       f"{n}")

    return {
        'chart': '\n'.join(chart_lines),
        'data': data,
        'trend': round(slope, 4),
        'trend_symbol': trend_sym,
        'current': data[-1] if data else 0,
        'best': max(data) if data else 0,
        'avg': sum(data) / len(data) if data else 0,
    }


# ═══════════════════════════════════════════════════════════
# DASHBOARD — comprehensive statistics panel (v16)
# ═══════════════════════════════════════════════════════════

def dashboard(school):
    """
    Generate a comprehensive statistics dashboard for a school.

    Sections:
    1. Overview (students, sessions, library size)
    2. Grade distribution across all sessions
    3. Top performers (by avg grade)
    4. Library composition (tags, DNA clusters)
    5. Achievement leaderboard
    """
    all_sessions = []
    for name, sp in school.students.items():
        for sess in sp.sessions:
            all_sessions.append({**sess, 'student': name})

    # 1. Overview
    total_sessions = len(all_sessions)
    total_tacts = sum(s['n_tacts'] for s in all_sessions)
    avg_grade = (sum(s['pct'] for s in all_sessions)
                 / total_sessions) if total_sessions else 0

    # 2. Grade distribution
    grade_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for s in all_sessions:
        g = s.get('grade', 'F')
        grade_dist[g] = grade_dist.get(g, 0) + 1

    # 3. Top performers
    performers = []
    for name, sp in school.students.items():
        if sp.sessions:
            avg = sum(s['pct'] for s in sp.sessions) / len(sp.sessions)
            performers.append((name, avg, sp.mastery_level,
                               len(sp.sessions)))
    performers.sort(key=lambda x: -x[1])

    # 4. Library stats
    lib_stats = school.library.stats()

    # 5. Achievement leaderboard
    ach_board = []
    for name, sp in school.students.items():
        ach = check_achievements(sp)
        ach_board.append((name, len(ach['earned']), ach['progress']))
    ach_board.sort(key=lambda x: -x[1])

    return {
        'overview': {
            'students': len(school.students),
            'graduated': len(school.graduated),
            'total_sessions': total_sessions,
            'total_tacts': total_tacts,
            'avg_grade': round(avg_grade, 1),
            'library_size': lib_stats['total'],
        },
        'grade_distribution': grade_dist,
        'top_performers': performers[:5],
        'library': lib_stats,
        'achievement_board': ach_board,
    }


def format_dashboard(db):
    """Format dashboard as a readable panel."""
    o = db['overview']
    lines = []
    lines.append("╔══════════════════════════════════════════╗")
    lines.append("║         SCARAB SCHOOL DASHBOARD          ║")
    lines.append("╠══════════════════════════════════════════╣")
    lines.append(f"║  Students: {o['students']:3d}  "
                 f"Graduated: {o['graduated']:3d}          ║")
    lines.append(f"║  Sessions: {o['total_sessions']:3d}  "
                 f"Tacts: {o['total_tacts']:5d}             ║")
    lines.append(f"║  Avg grade: {o['avg_grade']:5.1f}%  "
                 f"Library: {o['library_size']:3d} kata     ║")
    lines.append("╠══════════════════════════════════════════╣")

    # Grade distribution bar
    gd = db['grade_distribution']
    total = sum(gd.values()) or 1
    lines.append("║  Grade distribution:                     ║")
    for g in ['A', 'B', 'C', 'D', 'F']:
        count = gd.get(g, 0)
        pct = count / total * 100
        bar_len = int(pct / 5)
        bar = '#' * bar_len
        lines.append(f"║    {g}: {bar:<20s} {count:3d} ({pct:4.0f}%) ║")

    lines.append("╠══════════════════════════════════════════╣")
    lines.append("║  Top performers:                         ║")
    for name, avg, ml, ns in db['top_performers']:
        lines.append(f"║    {name:10s} L{ml} avg={avg:5.1f}% "
                     f"({ns} sess)    ║")

    lines.append("╠══════════════════════════════════════════╣")
    lines.append("║  Achievement leaderboard:                ║")
    for name, earned, pct in db['achievement_board'][:5]:
        lines.append(f"║    {name:10s} {earned:2d}/10 "
                     f"({pct:4.0f}%)                ║")

    lines.append("╚══════════════════════════════════════════╝")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PATTERN CATALOG — classify movement patterns (v16)
# ═══════════════════════════════════════════════════════════

# Named patterns: common structural motifs in kata
PATTERN_CATALOG = {
    'ascent': {
        'name': 'Ascent',
        'desc': 'Monotonically increasing complexity',
        'detect': lambda syms: all(
            symbol_complexity(syms[i]) <= symbol_complexity(syms[i+1])
            for i in range(len(syms)-1)) if len(syms) >= 2 else False,
    },
    'descent': {
        'name': 'Descent',
        'desc': 'Monotonically decreasing complexity',
        'detect': lambda syms: all(
            symbol_complexity(syms[i]) >= symbol_complexity(syms[i+1])
            for i in range(len(syms)-1)) if len(syms) >= 2 else False,
    },
    'arch': {
        'name': 'Arch',
        'desc': 'Rise then fall (peak in middle)',
        'detect': lambda syms: _detect_arch(syms),
    },
    'valley': {
        'name': 'Valley',
        'desc': 'Fall then rise (trough in middle)',
        'detect': lambda syms: _detect_valley(syms),
    },
    'plateau': {
        'name': 'Plateau',
        'desc': 'Constant complexity (all same group)',
        'detect': lambda syms: len(set(get_group(s) for s in syms)) == 1
                  if syms else False,
    },
    'zigzag': {
        'name': 'Zigzag',
        'desc': 'Alternating high/low complexity',
        'detect': lambda syms: _detect_zigzag(syms),
    },
    'cascade': {
        'name': 'Cascade',
        'desc': 'Stepwise descent with recoveries',
        'detect': lambda syms: _detect_cascade(syms),
    },
    'mirror_sym': {
        'name': 'Mirror',
        'desc': 'Palindromic group sequence',
        'detect': lambda syms: _detect_mirror(syms),
    },
}


def _detect_arch(syms):
    """Peak complexity in the middle third."""
    if len(syms) < 3:
        return False
    cs = [symbol_complexity(s) for s in syms]
    n = len(cs)
    peak_idx = cs.index(max(cs))
    return n // 3 <= peak_idx <= 2 * n // 3


def _detect_valley(syms):
    """Trough complexity in the middle third."""
    if len(syms) < 3:
        return False
    cs = [symbol_complexity(s) for s in syms]
    n = len(cs)
    trough_idx = cs.index(min(cs))
    return n // 3 <= trough_idx <= 2 * n // 3


def _detect_zigzag(syms):
    """Alternating direction changes in complexity."""
    if len(syms) < 3:
        return False
    cs = [symbol_complexity(s) for s in syms]
    changes = 0
    for i in range(1, len(cs) - 1):
        if (cs[i] > cs[i-1] and cs[i] > cs[i+1]) or \
           (cs[i] < cs[i-1] and cs[i] < cs[i+1]):
            changes += 1
    return changes >= len(cs) // 2


def _detect_cascade(syms):
    """Overall downward trend but not monotonic."""
    if len(syms) < 3:
        return False
    cs = [symbol_complexity(s) for s in syms]
    overall_down = cs[0] > cs[-1]
    monotonic = all(cs[i] >= cs[i+1] for i in range(len(cs)-1))
    has_recovery = any(cs[i] < cs[i+1] for i in range(len(cs)-1))
    return overall_down and not monotonic and has_recovery


def _detect_mirror(syms):
    """Palindromic group sequence."""
    if len(syms) < 3:
        return False
    groups = [get_group(s) for s in syms]
    n = len(groups)
    return all(groups[i] == groups[n-1-i] for i in range(n // 2))


def classify_kata_patterns(kata, mode='dual'):
    """
    Classify a kata by detecting all matching patterns.

    Returns:
        dict with patterns found for L hand, R hand, and combined
    """
    if mode == 'dual':
        syms_L = [e[0] for e in kata]
        syms_R = [e[1] for e in kata]
    else:
        syms_L = list(kata)
        syms_R = []

    results = {'L': [], 'R': [], 'combined': []}

    for key, pat in PATTERN_CATALOG.items():
        if pat['detect'](syms_L):
            results['L'].append({'key': key, 'name': pat['name'],
                                 'desc': pat['desc']})
        if syms_R and pat['detect'](syms_R):
            results['R'].append({'key': key, 'name': pat['name'],
                                 'desc': pat['desc']})
        # Combined: interleave L and R
        if syms_R:
            combined = []
            for i in range(len(syms_L)):
                combined.append(syms_L[i])
                if i < len(syms_R):
                    combined.append(syms_R[i])
            if pat['detect'](combined):
                results['combined'].append({'key': key, 'name': pat['name'],
                                            'desc': pat['desc']})

    results['total'] = (len(results['L']) + len(results['R']) +
                        len(results['combined']))
    return results


def format_patterns(pat_result):
    """Format pattern classification as readable text."""
    lines = [f"Patterns detected: {pat_result['total']}"]
    for hand, label in [('L', 'Left'), ('R', 'Right'),
                        ('combined', 'Combined')]:
        if pat_result[hand]:
            names = ', '.join(p['name'] for p in pat_result[hand])
            lines.append(f"  {label}: {names}")
    if pat_result['total'] == 0:
        lines.append("  (no named patterns detected)")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# RECOMMENDATION ENGINE — intelligent next action (v17)
# ═══════════════════════════════════════════════════════════

def recommend_next(student, library=None):
    """
    Recommend the best next action for a student.

    Decision tree:
    1. If < 3 sessions → recommend easy kata (warm-up phase)
    2. If weak rules exist → recommend targeted drill
    3. If weak groups exist → recommend group drill
    4. If trend is declining → recommend review of best kata
    5. If close to achievement → recommend targeted session
    6. Default → recommend new kata at current level

    Returns:
        dict with 'action', 'reason', 'details'
    """
    n_sess = len(student.sessions)
    ml = student.mastery_level
    weaknesses = student.weaknesses()

    # 1. New student
    if n_sess < 3:
        return {
            'action': 'easy_kata',
            'reason': 'Build foundation (< 3 sessions)',
            'details': {'mastery_level': max(1, ml - 1), 'length': 3},
        }

    # Check trend
    recent = student.sessions[-4:] if n_sess >= 4 else student.sessions
    recent_avg = sum(s['pct'] for s in recent) / len(recent)
    if n_sess >= 6:
        older = student.sessions[-8:-4]
        older_avg = sum(s['pct'] for s in older) / len(older)
        trend = recent_avg - older_avg
    else:
        trend = 0

    # 2. Weak rules
    rule_weaks = [w for w in weaknesses if w['type'] == 'rule']
    if rule_weaks and rule_weaks[0].get('pct', 100) < 50:
        return {
            'action': 'drill_rule',
            'reason': f"Rule {rule_weaks[0]['rule']} is weak "
                      f"({rule_weaks[0].get('pct', 0):.0f}%)",
            'details': {'rule_num': rule_weaks[0]['rule'],
                        'n_reps': 5, 'mastery_level': ml},
        }

    # 3. Weak groups
    group_weaks = [w for w in weaknesses if w['type'] == 'group']
    if group_weaks:
        return {
            'action': 'drill_group',
            'reason': f"Group {group_weaks[0]['group']} underexplored",
            'details': {'group_num': group_weaks[0]['group'],
                        'n_reps': 5, 'mastery_level': ml},
        }

    # 4. Declining trend
    if trend < -3:
        return {
            'action': 'review',
            'reason': f'Performance declining (trend={trend:+.1f}%)',
            'details': {'mastery_level': max(1, ml - 1), 'length': 4},
        }

    # 5. Close to achievement
    ach = check_achievements(student)
    pending = ach['pending']
    for p in pending:
        if p['key'] == 'grade_a' and recent_avg > 80:
            return {
                'action': 'optimize_kata',
                'reason': 'Close to Grade A achievement',
                'details': {'target_grade': 'A', 'mastery_level': ml},
            }
        if p['key'] == 'consistency' and all(
                s['pct'] >= 70 for s in recent):
            return {
                'action': 'maintain',
                'reason': f'Building consistency streak '
                          f'({len(recent)} sessions > 70%)',
                'details': {'mastery_level': ml, 'length': 5},
            }

    # 6. Default: new kata, maybe level up
    if recent_avg > 85 and ml < 5:
        return {
            'action': 'level_up',
            'reason': f'Ready for next level (avg={recent_avg:.0f}%)',
            'details': {'mastery_level': ml + 1, 'length': 5},
        }

    return {
        'action': 'new_kata',
        'reason': 'Continue training at current level',
        'details': {'mastery_level': ml, 'length': 5},
    }


def format_recommendation(rec):
    """Format a recommendation as readable text."""
    actions = {
        'easy_kata': 'Generate easy kata',
        'drill_rule': 'Focused rule drill',
        'drill_group': 'Focused group drill',
        'review': 'Review session',
        'optimize_kata': 'Aim for Grade A',
        'maintain': 'Maintain consistency',
        'level_up': 'Level up!',
        'new_kata': 'New kata',
    }
    label = actions.get(rec['action'], rec['action'])
    return (f"Recommendation: {label}\n"
            f"  Reason: {rec['reason']}\n"
            f"  Details: {rec['details']}")


# ═══════════════════════════════════════════════════════════
# YEAR SIMULATOR — run full school year (v17)
# ═══════════════════════════════════════════════════════════

def simulate_school_year(school, year=1, sessions_per_quarter=3, seed=None):
    """
    Simulate a full school year (Q1-Q4) for all active students.

    Each quarter: N training sessions per student, with recommendations
    informing each session. End of year: exam for each student.

    Returns:
        dict with quarterly summaries, exam results, year stats
    """
    rng = random.Random(seed)
    quarterly = []

    for qi, q in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
        q_results = []
        for name in list(school.students.keys()):
            if name in school.graduated:
                continue
            student = school.students[name]
            for sess_i in range(sessions_per_quarter):
                school.train(name, quarter=q, year=year,
                             seed=rng.randint(0, 2**31))

            # Quarterly summary for this student
            recent = student.sessions[-sessions_per_quarter:]
            avg_pct = sum(s['pct'] for s in recent) / len(recent)
            avg_res = sum(s['resonance'] for s in recent) / len(recent)
            rec = recommend_next(student, library=school.library)
            q_results.append({
                'student': name,
                'sessions': sessions_per_quarter,
                'avg_grade': round(avg_pct, 1),
                'avg_resonance': round(avg_res, 2),
                'mastery': student.mastery_level,
                'recommendation': rec['action'],
            })

        quarterly.append({'quarter': q, 'results': q_results})

    # End-of-year exam
    exam_results = []
    for name in list(school.students.keys()):
        if name in school.graduated:
            continue
        result = school.examine(name, quarter='Q4', year=year,
                                seed=rng.randint(0, 2**31))
        exam_results.append({
            'student': name,
            'grade': result['final_grade'],
            'pct': result['final_pct'],
        })

    # Year summary
    all_active = [s for n, s in school.students.items()
                  if n not in school.graduated]
    total_sessions = sum(len(s.sessions) for s in all_active)

    return {
        'year': year,
        'quarterly': quarterly,
        'exams': exam_results,
        'total_sessions': total_sessions,
        'n_students': len(all_active),
    }


def format_year_summary(yr):
    """Format year simulation as readable text."""
    lines = [f"Year {yr['year']} Summary ({yr['n_students']} students)"]
    lines.append("=" * 55)
    for qdata in yr['quarterly']:
        lines.append(f"\n  {qdata['quarter']}:")
        for r in qdata['results']:
            lines.append(
                f"    {r['student']:10s} L{r['mastery']} "
                f"avg={r['avg_grade']:5.1f}% "
                f"res={r['avg_resonance']:.2f} "
                f"→ {r['recommendation']}")

    lines.append(f"\n  End-of-year exams:")
    for e in yr['exams']:
        lines.append(f"    {e['student']:10s} {e['grade']} ({e['pct']:.0f}%)")

    lines.append(f"\n  Total sessions: {yr['total_sessions']}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# REPORT CARD — comprehensive end-of-year report (v17)
# ═══════════════════════════════════════════════════════════

def report_card(student, year=1):
    """
    Generate a comprehensive report card for a student.

    Sections:
    1. Identity & Level
    2. Session statistics
    3. Grade history & trend
    4. Rule compliance breakdown
    5. Group coverage
    6. Pattern profile
    7. Achievements
    8. Recommendations
    """
    n = len(student.sessions)
    if n == 0:
        return {'student': student.name, 'sections': [], 'empty': True}

    # Filter sessions for this year
    year_sessions = [s for s in student.sessions
                     if s.get('year') == year]
    if not year_sessions:
        year_sessions = student.sessions  # fallback to all

    ny = len(year_sessions)

    # 1. Identity
    identity = {
        'name': student.name,
        'mastery_level': student.mastery_level,
        'total_sessions': n,
        'year_sessions': ny,
    }

    # 2. Stats
    avg_pct = sum(s['pct'] for s in year_sessions) / ny
    avg_res = sum(s['resonance'] for s in year_sessions) / ny
    avg_lci = sum(s['lci_avg'] for s in year_sessions) / ny
    best_pct = max(s['pct'] for s in year_sessions)
    worst_pct = min(s['pct'] for s in year_sessions)
    stats = {
        'avg_grade': round(avg_pct, 1),
        'avg_resonance': round(avg_res, 2),
        'avg_lci': round(avg_lci, 2),
        'best': round(best_pct, 1),
        'worst': round(worst_pct, 1),
        'range': round(best_pct - worst_pct, 1),
    }

    # 3. Grade history
    grades = [s['grade'] for s in year_sessions]
    grade_counts = {}
    for g in grades:
        grade_counts[g] = grade_counts.get(g, 0) + 1

    # 4. Rule compliance
    rule_avgs = {}
    for r in range(1, 6):
        history = student.rule_history.get(r, [])
        if history:
            recent = history[-ny:]
            rule_avgs[r] = round(sum(recent) / len(recent), 1)
        else:
            rule_avgs[r] = 0
    rule_names = {1: 'Zones', 2: 'Anti-sym', 3: 'Alternation',
                  4: 'Smoothness', 5: 'Conservation'}

    # 5. Group coverage
    groups_total = sum(student.group_hits.values())
    group_pcts = {}
    for g in range(1, 8):
        hits = student.group_hits.get(g, 0)
        group_pcts[g] = round(hits / groups_total * 100, 1) if groups_total else 0

    # 6. Achievements
    ach = check_achievements(student)

    # 7. Recommendation
    rec = recommend_next(student)

    # Overall letter grade for the year
    if avg_pct >= 90:
        year_grade = 'A'
    elif avg_pct >= 75:
        year_grade = 'B'
    elif avg_pct >= 60:
        year_grade = 'C'
    elif avg_pct >= 40:
        year_grade = 'D'
    else:
        year_grade = 'F'

    return {
        'student': student.name,
        'year': year,
        'year_grade': year_grade,
        'identity': identity,
        'stats': stats,
        'grade_counts': grade_counts,
        'rule_compliance': rule_avgs,
        'rule_names': rule_names,
        'group_coverage': group_pcts,
        'achievements': ach,
        'recommendation': rec,
        'empty': False,
    }


def format_report_card(rc):
    """Format report card as a readable document."""
    if rc.get('empty'):
        return f"Report Card: {rc['student']} — No data"

    lines = []
    lines.append("┌─────────────────────────────────────────┐")
    lines.append(f"│  REPORT CARD: {rc['student']:>15s}  Y{rc['year']}      │")
    lines.append(f"│  Overall: {rc['year_grade']}                             │")
    lines.append("├─────────────────────────────────────────┤")

    # Identity
    ident = rc['identity']
    lines.append(f"│  Level: {ident['mastery_level']}  "
                 f"Sessions: {ident['year_sessions']} "
                 f"(total: {ident['total_sessions']})")

    # Stats
    s = rc['stats']
    lines.append(f"│  Avg: {s['avg_grade']:.1f}%  "
                 f"Best: {s['best']:.0f}%  "
                 f"Worst: {s['worst']:.0f}%  "
                 f"Range: {s['range']:.0f}%")
    lines.append(f"│  Resonance: {s['avg_resonance']:.2f}  "
                 f"LCI: {s['avg_lci']:.2f}")

    # Grade counts
    lines.append("│  Grades: " + '  '.join(
        f"{g}:{c}" for g, c in sorted(rc['grade_counts'].items())))

    # Rules
    lines.append("│  Rule compliance:")
    for r in range(1, 6):
        val = rc['rule_compliance'][r]
        bar = '#' * int(val / 10)
        lines.append(f"│    R{r} {rc['rule_names'][r]:12s} "
                     f"{bar:<10s} {val:5.1f}%")

    # Groups
    lines.append("│  Group coverage:")
    group_names = {1: 'Empty', 2: 'Single', 3: 'Angle',
                   4: 'Parallel', 5: 'Triple', 6: 'Master', 7: 'Peak'}
    for g in range(1, 8):
        pct = rc['group_coverage'][g]
        bar = '#' * int(pct / 5)
        lines.append(f"│    G{g} {group_names[g]:8s} "
                     f"{bar:<10s} {pct:5.1f}%")

    # Achievements
    ach = rc['achievements']
    lines.append(f"│  Achievements: {len(ach['earned'])}/{ach['total']} "
                 f"({ach['progress']:.0f}%)")

    # Recommendation
    rec = rc['recommendation']
    lines.append(f"│  Next: {rec['action']} — {rec['reason']}")
    lines.append("└─────────────────────────────────────────┘")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# COMPARATIVE ANALYTICS — compare students (v18)
# ═══════════════════════════════════════════════════════════

def compare_students(students):
    """
    Compare 2 or more StudentProfile objects across multiple dimensions.

    Dimensions:
    1. Grade average, best, worst
    2. Rule compliance per rule
    3. Group coverage entropy
    4. Achievement progress
    5. Trend (last 4 vs previous 4)
    6. Resonance average

    Returns:
        dict with per-student metrics and rankings per dimension
    """
    import math

    profiles = []
    for st in students:
        n = len(st.sessions)
        if n == 0:
            continue

        avg_pct = sum(s['pct'] for s in st.sessions) / n
        best_pct = max(s['pct'] for s in st.sessions)
        worst_pct = min(s['pct'] for s in st.sessions)
        avg_res = sum(s['resonance'] for s in st.sessions) / n

        # Rule compliance
        rule_avgs = {}
        for r in range(1, 6):
            h = st.rule_history.get(r, [])
            rule_avgs[r] = sum(h) / len(h) if h else 0

        # Group entropy (Shannon)
        total_g = sum(st.group_hits.values())
        if total_g > 0:
            probs = [st.group_hits.get(g, 0) / total_g for g in range(1, 8)]
            entropy = -sum(p * math.log2(p) if p > 0 else 0 for p in probs)
        else:
            entropy = 0

        # Trend
        if n >= 8:
            recent4 = st.sessions[-4:]
            older4 = st.sessions[-8:-4]
            trend = (sum(s['pct'] for s in recent4) / 4 -
                     sum(s['pct'] for s in older4) / 4)
        elif n >= 4:
            trend = (sum(s['pct'] for s in st.sessions[-4:]) / 4 -
                     sum(s['pct'] for s in st.sessions[:n//2]) /
                     max(1, n // 2))
        else:
            trend = 0

        # Achievements
        ach = check_achievements(st)

        profiles.append({
            'name': st.name,
            'mastery': st.mastery_level,
            'sessions': n,
            'avg_pct': round(avg_pct, 1),
            'best_pct': round(best_pct, 1),
            'worst_pct': round(worst_pct, 1),
            'avg_resonance': round(avg_res, 2),
            'rule_avgs': {r: round(v, 1) for r, v in rule_avgs.items()},
            'group_entropy': round(entropy, 2),
            'trend': round(trend, 1),
            'achievements': len(ach['earned']),
            'ach_total': ach['total'],
        })

    # Rankings
    dimensions = [
        ('avg_pct', True), ('best_pct', True), ('avg_resonance', True),
        ('group_entropy', True), ('trend', True), ('achievements', True),
        ('mastery', True),
    ]
    rankings = {}
    for dim, higher_better in dimensions:
        sorted_p = sorted(profiles, key=lambda p: p[dim],
                          reverse=higher_better)
        rankings[dim] = [p['name'] for p in sorted_p]

    # Overall score (composite rank)
    rank_sums = {p['name']: 0 for p in profiles}
    for dim, _ in dimensions:
        for rank_idx, name in enumerate(rankings[dim]):
            rank_sums[name] += rank_idx
    overall = sorted(rank_sums.items(), key=lambda x: x[1])
    rankings['overall'] = [name for name, _ in overall]

    return {
        'profiles': profiles,
        'rankings': rankings,
        'n_students': len(profiles),
    }


def format_comparison(cmp):
    """Format comparison as a readable table."""
    profiles = cmp['profiles']
    if not profiles:
        return "No data to compare"

    lines = ["Student Comparison"]
    lines.append("─" * 65)

    # Header
    names = [p['name'] for p in profiles]
    hdr = f"{'Metric':<20s}" + ''.join(f"{n:>12s}" for n in names)
    lines.append(hdr)
    lines.append("─" * 65)

    # Rows
    rows = [
        ('Level', 'mastery', ''),
        ('Sessions', 'sessions', ''),
        ('Avg Grade', 'avg_pct', '%'),
        ('Best Grade', 'best_pct', '%'),
        ('Worst Grade', 'worst_pct', '%'),
        ('Resonance', 'avg_resonance', ''),
        ('Group Entropy', 'group_entropy', ''),
        ('Trend', 'trend', '%'),
        ('Achievements', 'achievements', ''),
    ]
    for label, key, suffix in rows:
        row = f"{label:<20s}"
        for p in profiles:
            val = p[key]
            if isinstance(val, float):
                row += f"{val:>10.1f}{suffix:>2s}"
            else:
                row += f"{val!s:>10s}{suffix:>2s}"
        lines.append(row)

    # Rule compliance
    lines.append("─" * 65)
    rule_names = {1: 'R1 Zones', 2: 'R2 Anti-sym', 3: 'R3 Alternation',
                  4: 'R4 Smooth', 5: 'R5 Conserv'}
    for r in range(1, 6):
        row = f"{rule_names[r]:<20s}"
        for p in profiles:
            row += f"{p['rule_avgs'][r]:>10.1f}% "
        lines.append(row)

    # Overall ranking
    lines.append("─" * 65)
    overall = cmp['rankings']['overall']
    lines.append("Overall ranking: " + ' > '.join(overall))

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# GRADUATION CEREMONY — complete school lifecycle (v18)
# ═══════════════════════════════════════════════════════════

def graduation_ceremony(school):
    """
    Attempt graduation for all eligible students.
    Returns ceremony results with honors, awards, statistics.
    """
    results = []
    for name in list(school.students.keys()):
        if name in school.graduated:
            continue
        grad = school.graduate(name)
        if grad['eligible']:
            student = school.students[name]
            ach = check_achievements(student)
            avg = (sum(s['pct'] for s in student.sessions) /
                   max(1, len(student.sessions)))

            # Honors determination
            if avg >= 90 and len(ach['earned']) >= 8:
                honor = 'Summa Cum Laude'
            elif avg >= 85 and len(ach['earned']) >= 6:
                honor = 'Magna Cum Laude'
            elif avg >= 80:
                honor = 'Cum Laude'
            else:
                honor = None

            results.append({
                'name': name,
                'graduated': True,
                'mastery': student.mastery_level,
                'avg_pct': round(avg, 1),
                'sessions': len(student.sessions),
                'achievements': len(ach['earned']),
                'honor': honor,
            })
        else:
            results.append({
                'name': name,
                'graduated': False,
                'requirements': grad['requirements'],
            })

    # Awards
    grads = [r for r in results if r['graduated']]
    awards = {}
    if grads:
        awards['valedictorian'] = max(grads, key=lambda r: r['avg_pct'])['name']
        awards['most_sessions'] = max(grads, key=lambda r: r['sessions'])['name']
        awards['most_achievements'] = max(
            grads, key=lambda r: r['achievements'])['name']

    return {
        'graduates': grads,
        'not_ready': [r for r in results if not r['graduated']],
        'awards': awards,
        'total_graduates': len(grads),
    }


def format_ceremony(cer):
    """Format graduation ceremony as readable text."""
    lines = []
    lines.append("╔══════════════════════════════════════════╗")
    lines.append("║       GRADUATION CEREMONY                ║")
    lines.append("╠══════════════════════════════════════════╣")

    if not cer['graduates']:
        lines.append("║  No graduates this session.              ║")
    else:
        for g in cer['graduates']:
            honor_str = f" ({g['honor']})" if g['honor'] else ""
            lines.append(
                f"║  {g['name']:10s} L{g['mastery']} "
                f"avg={g['avg_pct']:5.1f}%{honor_str}")

    if cer['not_ready']:
        lines.append("╠══════════════════════════════════════════╣")
        lines.append("║  Not yet eligible:")
        for nr in cer['not_ready']:
            failed = [k for k, (ok, _) in nr['requirements'].items()
                      if not ok]
            lines.append(f"║    {nr['name']:10s} needs: {', '.join(failed)}")

    if cer['awards']:
        lines.append("╠══════════════════════════════════════════╣")
        lines.append("║  Awards:")
        for award, name in cer['awards'].items():
            label = award.replace('_', ' ').title()
            lines.append(f"║    {label:20s}: {name}")

    lines.append(f"╠══════════════════════════════════════════╣")
    lines.append(f"║  Total graduates: {cer['total_graduates']:3d}"
                 f"                    ║")
    lines.append("╚══════════════════════════════════════════╝")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# CURRICULUM GENERATOR — automatic training program (v18)
# ═══════════════════════════════════════════════════════════

def generate_curriculum(student, weeks=8, sessions_per_week=2):
    """
    Generate a multi-week personalized training plan.

    Structure per week:
    - Session type(s) based on recommendation engine
    - Progressive mastery level increases
    - Rule/group focus areas
    - Milestones

    Returns:
        dict with weekly plans and overview
    """
    rec = recommend_next(student)
    current_ml = student.mastery_level
    weaknesses = student.weaknesses()
    ach = check_achievements(student)

    # Classify weak rules and groups
    weak_rules = [w['rule'] for w in weaknesses if w['type'] == 'rule'
                  and w.get('pct', 100) < 60]
    weak_groups = [w['group'] for w in weaknesses if w['type'] == 'group']

    plan = []
    ml = current_ml
    pending_ach = [p['key'] for p in ach['pending']]

    for week in range(1, weeks + 1):
        week_plan = {
            'week': week,
            'mastery_level': ml,
            'sessions': [],
            'focus': None,
            'milestone': None,
        }

        # Phase logic
        phase_frac = week / weeks
        if phase_frac <= 0.25:
            phase = 'foundation'
        elif phase_frac <= 0.5:
            phase = 'development'
        elif phase_frac <= 0.75:
            phase = 'refinement'
        else:
            phase = 'mastery'

        for si in range(sessions_per_week):
            if phase == 'foundation':
                if weak_rules:
                    rule_target = weak_rules[si % len(weak_rules)]
                    sess = {'type': 'drill_rule', 'rule': rule_target,
                            'length': 4, 'mastery_level': ml}
                else:
                    sess = {'type': 'kata', 'length': 4,
                            'mastery_level': ml}
            elif phase == 'development':
                if weak_groups:
                    group_target = weak_groups[si % len(weak_groups)]
                    sess = {'type': 'drill_group', 'group': group_target,
                            'length': 5, 'mastery_level': ml}
                else:
                    sess = {'type': 'kata', 'length': 5,
                            'mastery_level': ml}
            elif phase == 'refinement':
                if si == 0:
                    sess = {'type': 'sparring', 'length': 5,
                            'mastery_level': ml}
                else:
                    sess = {'type': 'kata', 'length': 5,
                            'mastery_level': ml}
            else:  # mastery
                if si == 0:
                    sess = {'type': 'exam_prep', 'length': 6,
                            'mastery_level': ml}
                else:
                    sess = {'type': 'optimize', 'length': 5,
                            'mastery_level': ml}

            week_plan['sessions'].append(sess)

        # Focus
        if phase == 'foundation' and weak_rules:
            week_plan['focus'] = f"Rule {weak_rules[0]} remediation"
        elif phase == 'development' and weak_groups:
            week_plan['focus'] = f"Group {weak_groups[0]} expansion"
        elif phase == 'refinement':
            week_plan['focus'] = "Competitive readiness"
        else:
            week_plan['focus'] = f"Level {ml} mastery"

        # Milestones
        if week == weeks // 4:
            week_plan['milestone'] = 'Foundation complete'
        elif week == weeks // 2:
            week_plan['milestone'] = 'Mid-program review'
            if ml < 5:
                ml += 1  # Level up at midpoint
        elif week == 3 * weeks // 4:
            week_plan['milestone'] = 'Pre-exam readiness'
        elif week == weeks:
            week_plan['milestone'] = 'Final exam'

        plan.append(week_plan)

    total_sessions = sum(len(w['sessions']) for w in plan)
    return {
        'student': student.name,
        'start_level': current_ml,
        'target_level': ml,
        'weeks': weeks,
        'total_sessions': total_sessions,
        'plan': plan,
    }


def format_weekly_curriculum(cur):
    """Format weekly curriculum plan as readable text."""
    lines = [f"Curriculum for {cur['student']}"]
    lines.append(f"  L{cur['start_level']} → L{cur['target_level']}  "
                 f"{cur['weeks']} weeks, {cur['total_sessions']} sessions")
    lines.append("─" * 50)

    for w in cur['plan']:
        milestone = f" ★ {w['milestone']}" if w['milestone'] else ""
        lines.append(f"  Week {w['week']:2d} [L{w['mastery_level']}] "
                     f"{w['focus']}{milestone}")
        for si, sess in enumerate(w['sessions']):
            parts = [f"{sess['type']}"]
            if 'rule' in sess:
                parts.append(f"R{sess['rule']}")
            if 'group' in sess:
                parts.append(f"G{sess['group']}")
            parts.append(f"len={sess['length']}")
            lines.append(f"    {si+1}. {' '.join(parts)}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# STATISTICAL ANALYSIS — distributions & correlations (v19)
# ═══════════════════════════════════════════════════════════

def analyze_statistics(student):
    """
    Compute statistical summary for a student's session data.

    Metrics:
    1. Grade distribution (mean, median, stddev, quartiles)
    2. Rule correlation matrix (which rules co-vary)
    3. Resonance distribution
    4. Session-over-session improvement rate
    5. Group hit distribution (chi-squared from uniform)

    Returns:
        dict with all statistical measures
    """
    import math

    sessions = student.sessions
    n = len(sessions)
    if n == 0:
        return {'empty': True, 'student': student.name}

    # 1. Grade distribution
    pcts = [s['pct'] for s in sessions]
    pcts_sorted = sorted(pcts)
    mean_pct = sum(pcts) / n
    median_pct = (pcts_sorted[n // 2] if n % 2 == 1
                  else (pcts_sorted[n // 2 - 1] + pcts_sorted[n // 2]) / 2)
    variance = sum((p - mean_pct) ** 2 for p in pcts) / max(1, n - 1)
    stddev = math.sqrt(variance)
    q1 = pcts_sorted[n // 4] if n >= 4 else pcts_sorted[0]
    q3 = pcts_sorted[3 * n // 4] if n >= 4 else pcts_sorted[-1]

    grade_stats = {
        'mean': round(mean_pct, 1),
        'median': round(median_pct, 1),
        'stddev': round(stddev, 1),
        'q1': round(q1, 1),
        'q3': round(q3, 1),
        'iqr': round(q3 - q1, 1),
        'min': round(min(pcts), 1),
        'max': round(max(pcts), 1),
    }

    # 2. Rule correlation (Pearson-like for 5 rules)
    rule_series = {}
    for r in range(1, 6):
        h = student.rule_history.get(r, [])
        # Pad or trim to n sessions
        rule_series[r] = (h[:n] + [0] * max(0, n - len(h)))[:n]

    correlations = {}
    for r1 in range(1, 6):
        for r2 in range(r1 + 1, 6):
            s1, s2 = rule_series[r1], rule_series[r2]
            m1 = sum(s1) / n
            m2 = sum(s2) / n
            cov = sum((s1[i] - m1) * (s2[i] - m2) for i in range(n)) / max(1, n - 1)
            sd1 = math.sqrt(sum((v - m1) ** 2 for v in s1) / max(1, n - 1))
            sd2 = math.sqrt(sum((v - m2) ** 2 for v in s2) / max(1, n - 1))
            if sd1 > 0 and sd2 > 0:
                corr = cov / (sd1 * sd2)
            else:
                corr = 0
            correlations[(r1, r2)] = round(corr, 2)

    # 3. Resonance distribution
    res_vals = [s['resonance'] for s in sessions]
    res_mean = sum(res_vals) / n
    res_var = sum((r - res_mean) ** 2 for r in res_vals) / max(1, n - 1)
    res_std = math.sqrt(res_var)

    resonance_stats = {
        'mean': round(res_mean, 2),
        'stddev': round(res_std, 2),
        'min': round(min(res_vals), 2),
        'max': round(max(res_vals), 2),
    }

    # 4. Improvement rate (linear regression slope on pct)
    if n >= 3:
        x_mean = (n - 1) / 2.0
        y_mean = mean_pct
        num = sum((i - x_mean) * (pcts[i] - y_mean) for i in range(n))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den > 0 else 0
    else:
        slope = 0

    # 5. Group chi-squared (deviation from uniform)
    total_hits = sum(student.group_hits.values())
    if total_hits > 0:
        expected = total_hits / 7.0
        chi2 = sum((student.group_hits.get(g, 0) - expected) ** 2 / expected
                    for g in range(1, 8))
    else:
        chi2 = 0

    return {
        'empty': False,
        'student': student.name,
        'n_sessions': n,
        'grade': grade_stats,
        'rule_correlations': correlations,
        'resonance': resonance_stats,
        'improvement_rate': round(slope, 2),
        'group_chi2': round(chi2, 1),
    }


def format_statistics(stats):
    """Format statistical analysis as readable text."""
    if stats.get('empty'):
        return f"Statistics: {stats['student']} — no data"

    lines = [f"Statistics: {stats['student']} ({stats['n_sessions']} sessions)"]
    lines.append("─" * 50)

    g = stats['grade']
    lines.append(f"  Grade:  mean={g['mean']:.1f}  median={g['median']:.1f}"
                 f"  σ={g['stddev']:.1f}")
    lines.append(f"          Q1={g['q1']:.1f}  Q3={g['q3']:.1f}"
                 f"  IQR={g['iqr']:.1f}")
    lines.append(f"          min={g['min']:.1f}  max={g['max']:.1f}")

    r = stats['resonance']
    lines.append(f"  Reson:  mean={r['mean']:.2f}  σ={r['stddev']:.2f}"
                 f"  [{r['min']:.2f}..{r['max']:.2f}]")

    lines.append(f"  Trend:  slope={stats['improvement_rate']:+.2f}%/session")
    lines.append(f"  Groups: χ²={stats['group_chi2']:.1f}"
                 f" (uniform→0, skewed→high)")

    # Correlations
    lines.append("  Rule correlations:")
    rnames = {1: 'Zon', 2: 'Ant', 3: 'Alt', 4: 'Smo', 5: 'Con'}
    for (r1, r2), corr in sorted(stats['rule_correlations'].items()):
        bar = '+' * max(0, int(corr * 5)) + '-' * max(0, int(-corr * 5))
        lines.append(f"    R{r1}({rnames[r1]})-R{r2}({rnames[r2]}): "
                     f"{corr:+.2f} {bar}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# EXPORT SYSTEM — CSV & text export (v19)
# ═══════════════════════════════════════════════════════════

def export_sessions_csv(student):
    """
    Export student sessions as CSV string.

    Columns: session, quarter, year, grade, pct, resonance,
             lci_avg, r1, r2, r3, r4, r5, mastery_level
    """
    header = ('session,quarter,year,grade,pct,resonance,'
              'lci_avg,r1,r2,r3,r4,r5,mastery_level')
    rows = [header]

    for i, s in enumerate(student.sessions, 1):
        rule_vals = []
        for r in range(1, 6):
            h = student.rule_history.get(r, [])
            if i <= len(h):
                rule_vals.append(f"{h[i-1]:.1f}")
            else:
                rule_vals.append("0.0")

        row = (f"{i},{s.get('quarter', '')},{s.get('year', '')},"
               f"{s['grade']},{s['pct']:.1f},{s['resonance']:.2f},"
               f"{s['lci_avg']:.3f},"
               f"{','.join(rule_vals)},{s.get('mastery_level', 1)}")
        rows.append(row)

    return '\n'.join(rows)


def export_kata_text(kata, mode='dual'):
    """
    Export kata as human-readable text notation.

    Format for dual:
      Tact 1: L=A01A R=K00F  (G2/G5 ChVS=w)
      Tact 2: L=L00E R=a00H  (G1/G3 ChVS=s)
      ...
    """
    lines = []
    for i, tact in enumerate(kata, 1):
        if mode == 'dual':
            sym_l = tact[0]
            sym_r = tact[1]
            gl = get_group(sym_l)
            gr = get_group(sym_r)
            hl = f"S{sym_l:02d}"
            hr = f"S{sym_r:02d}"
            lines.append(f"  Tact {i:2d}: L={hl} R={hr}"
                         f"  (G{gl}/G{gr})")
        else:
            sym = tact if isinstance(tact, int) else tact[0]
            g = get_group(sym)
            h = f"S{sym:02d}"
            lines.append(f"  Tact {i:2d}: {h}  (G{g})")
    return '\n'.join(lines)


def export_school_csv(school):
    """
    Export school summary as CSV string.

    Columns: student, mastery_level, sessions, avg_pct,
             avg_resonance, achievements, status
    """
    header = 'student,mastery_level,sessions,avg_pct,avg_resonance,achievements,status'
    rows = [header]

    for name, st in school.students.items():
        n = len(st.sessions)
        avg_pct = sum(s['pct'] for s in st.sessions) / n if n else 0
        avg_res = sum(s['resonance'] for s in st.sessions) / n if n else 0
        ach = check_achievements(st)
        status = 'graduated' if name in school.graduated else 'active'
        rows.append(f"{name},{st.mastery_level},{n},"
                    f"{avg_pct:.1f},{avg_res:.2f},"
                    f"{len(ach['earned'])},{status}")

    return '\n'.join(rows)


# ═══════════════════════════════════════════════════════════
# PEER REVIEW — students evaluate each other (v19)
# ═══════════════════════════════════════════════════════════

def peer_review(reviewer, author_kata, seed=None):
    """
    Simulate one student reviewing another's kata.

    Review dimensions:
    1. Technical score (objective, via score_dual_kata)
    2. Style compatibility (how similar to reviewer's DNA)
    3. Creativity rating (group diversity, pattern variety)
    4. Constructive feedback (based on reviewer's strengths)

    The reviewer's mastery level affects review quality.
    """
    rng = random.Random(seed)

    # 1. Technical score (objective)
    tech = score_dual_kata(author_kata)

    # 2. Style compatibility
    # Generate a representative kata for the reviewer to compare styles
    if reviewer.sessions:
        rev_dma = DualMatchStickAutomaton(
            mastery_level=reviewer.mastery_level,
            seed=rng.randint(0, 2**31))
        reviewer_kata = rev_dma.generate_dual_kata(length=len(author_kata))
        reviewer_dna = kata_dna(reviewer_kata)
    else:
        reviewer_dna = None
    author_dna = kata_dna(author_kata)

    if reviewer_dna and author_dna:
        # Compare group distributions (first 7 elements of vector)
        rev_g = reviewer_dna['vector'][:7]
        aut_g = author_dna['vector'][:7]
        shared_groups = sum(1 for i in range(7)
                           if rev_g[i] > 0 and aut_g[i] > 0)
        style_compat = shared_groups / 7.0
    else:
        style_compat = 0.5

    # 3. Creativity rating
    aut_g = author_dna['vector'][:7]
    author_groups_used = sum(1 for i in range(7) if aut_g[i] > 0)
    creativity = author_groups_used / 7.0

    patterns = classify_kata_patterns(author_kata)
    if patterns['total'] > 2:
        creativity = min(1.0, creativity + 0.15)

    # 4. Constructive feedback
    feedback = []
    reviewer_ml = reviewer.mastery_level

    # Higher mastery → more insightful feedback
    if reviewer_ml >= 3 and tech['pct'] < 70:
        feedback.append("Consider strengthening rule compliance")
    if reviewer_ml >= 2 and creativity < 0.4:
        feedback.append("Try exploring more group diversity")
    if reviewer_ml >= 4 and style_compat < 0.3:
        feedback.append("Interesting stylistic contrast — unique approach")
    if tech['pct'] >= 85:
        feedback.append("Strong technical execution")
    if creativity >= 0.6:
        feedback.append("Great creative range across groups")

    # Noise from reviewer's experience
    noise = rng.gauss(0, 0.05 * (6 - reviewer_ml))  # less noise at higher ML
    subjective_score = max(0, min(100,
        tech['pct'] * 0.5 +
        style_compat * 100 * 0.2 +
        creativity * 100 * 0.3 +
        noise * 100))

    return {
        'reviewer': reviewer.name,
        'reviewer_level': reviewer_ml,
        'technical': {'grade': tech['grade'], 'pct': tech['pct']},
        'style_compatibility': round(style_compat, 2),
        'creativity': round(creativity, 2),
        'subjective_score': round(subjective_score, 1),
        'feedback': feedback,
    }


def format_peer_review(pr):
    """Format peer review as readable text."""
    lines = [f"Peer Review by {pr['reviewer']} (L{pr['reviewer_level']})"]
    lines.append(f"  Technical: {pr['technical']['grade']} "
                 f"({pr['technical']['pct']:.0f}%)")
    lines.append(f"  Style compatibility: {pr['style_compatibility']:.0%}")
    lines.append(f"  Creativity: {pr['creativity']:.0%}")
    lines.append(f"  Subjective score: {pr['subjective_score']:.1f}")
    if pr['feedback']:
        lines.append("  Feedback:")
        for fb in pr['feedback']:
            lines.append(f"    - {fb}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# FEDERATION — multi-school network (v20)
# ═══════════════════════════════════════════════════════════

class Federation:
    """
    Network of multiple Schools that can interact.

    Features:
    - Register/remove schools
    - Inter-school rankings
    - Federation-wide statistics
    - Cross-school tournaments
    - Transfer students between schools
    """

    def __init__(self, name='Scarab Federation'):
        self.name = name
        self.schools = {}       # name → School
        self.history = []       # federation events
        self.tournaments = []   # inter-school tournaments

    def register(self, school):
        """Register a school in the federation."""
        self.schools[school.name] = school
        self.history.append({
            'event': 'register', 'school': school.name,
            'students': len(school.students),
        })

    def remove(self, school_name):
        """Remove a school from the federation."""
        if school_name in self.schools:
            del self.schools[school_name]
            self.history.append({'event': 'remove', 'school': school_name})

    def transfer(self, student_name, from_school, to_school):
        """Transfer a student between schools."""
        if (from_school not in self.schools or
                to_school not in self.schools):
            return False
        src = self.schools[from_school]
        dst = self.schools[to_school]
        if student_name not in src.students:
            return False
        student = src.students.pop(student_name)
        dst.students[student_name] = student
        self.history.append({
            'event': 'transfer', 'student': student_name,
            'from': from_school, 'to': to_school,
        })
        return True

    def rankings(self):
        """
        Compute federation-wide school rankings.

        Dimensions: avg grade, total sessions, graduation rate,
        avg achievements, avg mastery level.
        """
        school_stats = []
        for name, school in self.schools.items():
            all_students = list(school.students.values())
            if not all_students:
                continue
            n_students = len(all_students)
            total_sess = sum(len(s.sessions) for s in all_students)
            all_pcts = []
            for s in all_students:
                for sess in s.sessions:
                    all_pcts.append(sess['pct'])
            avg_pct = sum(all_pcts) / len(all_pcts) if all_pcts else 0
            grad_rate = (len(school.graduated) / n_students * 100
                         if n_students else 0)
            avg_ml = (sum(s.mastery_level for s in all_students) /
                      n_students)
            total_ach = sum(len(check_achievements(s)['earned'])
                           for s in all_students)
            avg_ach = total_ach / n_students

            school_stats.append({
                'school': name,
                'students': n_students,
                'sessions': total_sess,
                'avg_grade': round(avg_pct, 1),
                'grad_rate': round(grad_rate, 1),
                'avg_mastery': round(avg_ml, 1),
                'avg_achievements': round(avg_ach, 1),
            })

        # Composite ranking
        for dim in ['avg_grade', 'grad_rate', 'avg_mastery',
                    'avg_achievements']:
            sorted_s = sorted(school_stats, key=lambda x: x[dim],
                              reverse=True)
            for rank, s in enumerate(sorted_s):
                s[f'rank_{dim}'] = rank

        for s in school_stats:
            s['composite_rank'] = sum(
                s.get(f'rank_{d}', 0) for d in
                ['avg_grade', 'grad_rate', 'avg_mastery',
                 'avg_achievements'])

        school_stats.sort(key=lambda x: x['composite_rank'])
        return school_stats

    def inter_tournament(self, seed=None):
        """
        Run a tournament with top students from each school.

        Each school sends its best student (by avg grade).
        """
        rng = random.Random(seed)
        contestants = {}

        for school_name, school in self.schools.items():
            active = [(n, s) for n, s in school.students.items()
                      if n not in school.graduated and s.sessions]
            if not active:
                continue
            best_name, best_st = max(
                active,
                key=lambda x: sum(s['pct'] for s in x[1].sessions) /
                              len(x[1].sessions))
            contestants[f"{best_name} ({school_name})"] = best_st

        if len(contestants) < 2:
            return {'error': 'Need at least 2 schools with active students'}

        # Generate tournament kata for each
        results = []
        for label, student in contestants.items():
            dma = DualMatchStickAutomaton(
                mastery_level=student.mastery_level,
                seed=rng.randint(0, 2**31))
            kata = dma.generate_dual_kata(length=5)
            score = score_dual_kata(kata)
            results.append({
                'contestant': label,
                'mastery': student.mastery_level,
                'grade': score['grade'],
                'pct': score['pct'],
            })

        results.sort(key=lambda x: x['pct'], reverse=True)

        # Record
        self.tournaments.append({
            'results': results,
            'winner': results[0]['contestant'],
        })
        self.history.append({
            'event': 'tournament',
            'winner': results[0]['contestant'],
            'participants': len(results),
        })

        return {
            'results': results,
            'winner': results[0]['contestant'],
        }

    def summary(self):
        """Federation-wide summary statistics."""
        total_students = sum(len(s.students) for s in self.schools.values())
        total_graduated = sum(len(s.graduated) for s in self.schools.values())
        total_sessions = sum(
            sum(len(st.sessions) for st in s.students.values())
            for s in self.schools.values())
        return {
            'name': self.name,
            'n_schools': len(self.schools),
            'total_students': total_students,
            'total_graduated': total_graduated,
            'total_sessions': total_sessions,
            'tournaments': len(self.tournaments),
        }


def format_federation(fed):
    """Format federation summary and rankings."""
    s = fed.summary()
    lines = []
    lines.append("╔══════════════════════════════════════════╗")
    lines.append(f"║  FEDERATION: {s['name']:<25s}  ║")
    lines.append("╠══════════════════════════════════════════╣")
    lines.append(f"║  Schools: {s['n_schools']}  "
                 f"Students: {s['total_students']}  "
                 f"Graduated: {s['total_graduated']}")
    lines.append(f"║  Sessions: {s['total_sessions']}  "
                 f"Tournaments: {s['tournaments']}")
    lines.append("╠══════════════════════════════════════════╣")

    rankings = fed.rankings()
    lines.append("║  School Rankings:")
    for i, r in enumerate(rankings, 1):
        lines.append(
            f"║   #{i} {r['school']:15s} "
            f"avg={r['avg_grade']:5.1f}% "
            f"grad={r['grad_rate']:4.0f}% "
            f"ML={r['avg_mastery']:.1f}")

    lines.append("╚══════════════════════════════════════════╝")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# TARGETED PATTERN GENERATOR — generate kata with specific
# pattern constraints (v20)
# ═══════════════════════════════════════════════════════════

def generate_targeted_kata(target_pattern, mastery_level=3,
                           length=5, max_attempts=50, seed=None):
    """
    Generate a kata that exhibits a specific named pattern.

    Supported targets: ascent, descent, arch, valley, plateau,
                       zigzag, cascade, mirror

    Strategy: generate candidates and select the one that
    matches the target pattern.
    """
    rng = random.Random(seed)

    best_kata = None
    best_match = False

    for attempt in range(max_attempts):
        dma = DualMatchStickAutomaton(
            mastery_level=mastery_level,
            seed=rng.randint(0, 2**31))
        kata = dma.generate_dual_kata(length=length)
        patterns = classify_kata_patterns(kata)

        # Check if target pattern is present
        all_names = set()
        for hand in ['L', 'R', 'combined']:
            for p in patterns[hand]:
                all_names.add(p['name'].lower())

        if target_pattern.lower() in all_names:
            return {
                'kata': kata,
                'attempts': attempt + 1,
                'patterns': patterns,
                'matched': True,
                'score': score_dual_kata(kata),
            }

        if best_kata is None:
            best_kata = kata

    # Fallback: return best attempt even if no match
    return {
        'kata': best_kata,
        'attempts': max_attempts,
        'patterns': classify_kata_patterns(best_kata),
        'matched': False,
        'score': score_dual_kata(best_kata),
    }


def format_targeted_result(res, target):
    """Format targeted generation result."""
    status = "MATCHED" if res['matched'] else "best effort"
    lines = [f"Target pattern: {target} ({status}, "
             f"{res['attempts']} attempts)"]
    lines.append(f"  Grade: {res['score']['grade']} "
                 f"({res['score']['pct']:.0f}%)")
    lines.append(f"  {format_patterns(res['patterns'])}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PROGRESS TIMELINE — chronological milestone log (v20)
# ═══════════════════════════════════════════════════════════

def build_timeline(student):
    """
    Build a chronological timeline of milestones for a student.

    Milestones:
    - First session
    - First Grade A
    - Each mastery level up
    - Achievement unlocks
    - Best session ever
    - Every 10th session
    """
    events = []
    sessions = student.sessions
    if not sessions:
        return events

    best_pct = 0
    first_a = None
    prev_ml = 1

    for i, s in enumerate(sessions):
        sess_num = i + 1

        # First session
        if i == 0:
            events.append({
                'session': sess_num,
                'type': 'start',
                'label': 'First session',
                'detail': f"{s['grade']} ({s['pct']:.0f}%)",
            })

        # First Grade A
        if s['grade'] == 'A' and first_a is None:
            first_a = sess_num
            events.append({
                'session': sess_num,
                'type': 'grade_a',
                'label': 'First Grade A!',
                'detail': f"{s['pct']:.0f}%",
            })

        # Best ever
        if s['pct'] > best_pct:
            best_pct = s['pct']
            if i > 0:  # Skip first (trivially best)
                events.append({
                    'session': sess_num,
                    'type': 'personal_best',
                    'label': 'New personal best',
                    'detail': f"{s['pct']:.0f}%",
                })

        # Level up
        ml = s.get('mastery_level', prev_ml)
        if ml > prev_ml:
            events.append({
                'session': sess_num,
                'type': 'level_up',
                'label': f'Level up! L{prev_ml} → L{ml}',
                'detail': f"Mastery level {ml}",
            })
            prev_ml = ml

        # Every 10th session
        if sess_num % 10 == 0:
            avg = sum(ss['pct'] for ss in sessions[:sess_num]) / sess_num
            events.append({
                'session': sess_num,
                'type': 'milestone',
                'label': f'{sess_num} sessions completed',
                'detail': f'Running avg: {avg:.0f}%',
            })

    # Achievement milestones
    ach = check_achievements(student)
    for a in ach['earned']:
        events.append({
            'session': len(sessions),  # approximate
            'type': 'achievement',
            'label': f"Achievement: {a['name'] if isinstance(a, dict) else a}",
            'detail': '',
        })

    events.sort(key=lambda e: (e['session'], e['type']))
    return events


def format_timeline(events, student_name='Student'):
    """Format timeline as readable text."""
    if not events:
        return f"Timeline: {student_name} — no events"

    lines = [f"Timeline: {student_name}"]
    lines.append("─" * 45)
    for e in events:
        icon = {
            'start': '●',
            'grade_a': '★',
            'personal_best': '▲',
            'level_up': '⬆',
            'milestone': '◆',
            'achievement': '🏅',
        }.get(e['type'], '·')
        detail = f" — {e['detail']}" if e['detail'] else ""
        lines.append(f"  #{e['session']:3d} {icon} {e['label']}{detail}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ELO RATING SYSTEM — competitive skill tracking (v21)
# ═══════════════════════════════════════════════════════════

class EloRating:
    """
    ELO rating system adapted for Scarab training.

    Each student gets an ELO rating that changes based on:
    - Training session results (vs expected performance)
    - Sparring outcomes (head-to-head)
    - Tournament placements

    K-factor scales with experience: new students K=40, veterans K=16.
    """

    DEFAULT_RATING = 1200

    def __init__(self):
        self.ratings = {}     # name → current rating
        self.history = {}     # name → [(event, old, new, delta)]
        self.peak = {}        # name → highest rating ever

    def register(self, name, initial=None):
        """Register a student with initial rating."""
        rating = initial or self.DEFAULT_RATING
        self.ratings[name] = rating
        self.history[name] = []
        self.peak[name] = rating

    def get(self, name):
        """Get current rating."""
        return self.ratings.get(name, self.DEFAULT_RATING)

    def k_factor(self, name):
        """K-factor based on number of rated events."""
        n = len(self.history.get(name, []))
        if n < 10:
            return 40
        elif n < 30:
            return 24
        else:
            return 16

    def expected(self, rating_a, rating_b):
        """Expected score of A vs B."""
        return 1.0 / (1.0 + 10 ** ((rating_b - rating_a) / 400.0))

    def update_match(self, name_a, name_b, score_a, score_b):
        """
        Update ratings after a head-to-head match.

        score_a, score_b are actual scores (e.g. kata pct).
        Winner gets rating boost, loser drops.
        """
        ra = self.get(name_a)
        rb = self.get(name_b)

        # Normalize to 0-1 outcome
        total = score_a + score_b
        if total > 0:
            actual_a = score_a / total
            actual_b = score_b / total
        else:
            actual_a = actual_b = 0.5

        ea = self.expected(ra, rb)
        eb = self.expected(rb, ra)

        ka = self.k_factor(name_a)
        kb = self.k_factor(name_b)

        new_ra = ra + ka * (actual_a - ea)
        new_rb = rb + kb * (actual_b - eb)

        self._apply(name_a, ra, new_ra, f"vs {name_b}")
        self._apply(name_b, rb, new_rb, f"vs {name_a}")

    def update_session(self, name, pct, mastery_level):
        """
        Update rating after a training session.

        Compare actual pct to expected pct for that mastery level.
        Expected baseline: 50 + mastery_level * 8 (L1=58%, L5=90%).
        """
        rating = self.get(name)
        expected_pct = 50 + mastery_level * 8
        performance = (pct - expected_pct) / 100.0  # [-0.5 .. +0.5]
        k = self.k_factor(name) * 0.5  # Half K for solo sessions

        new_rating = rating + k * performance
        self._apply(name, rating, new_rating,
                    f"session L{mastery_level} {pct:.0f}%")

    def _apply(self, name, old, new, event):
        """Apply a rating change."""
        new = max(100, min(3000, new))  # Clamp
        self.ratings[name] = round(new, 1)
        delta = round(new - old, 1)
        self.history[name].append({
            'event': event, 'old': round(old, 1),
            'new': round(new, 1), 'delta': delta,
        })
        if new > self.peak.get(name, 0):
            self.peak[name] = round(new, 1)

    def leaderboard(self, top_n=10):
        """Return top-N rated students."""
        sorted_r = sorted(self.ratings.items(),
                          key=lambda x: x[1], reverse=True)
        return [{
            'name': name, 'rating': rating,
            'peak': self.peak.get(name, rating),
            'events': len(self.history.get(name, [])),
        } for name, rating in sorted_r[:top_n]]

    def rating_class(self, name):
        """Map rating to a class name."""
        r = self.get(name)
        if r >= 2000:
            return 'Grandmaster'
        elif r >= 1800:
            return 'Master'
        elif r >= 1600:
            return 'Expert'
        elif r >= 1400:
            return 'Advanced'
        elif r >= 1200:
            return 'Intermediate'
        elif r >= 1000:
            return 'Beginner'
        else:
            return 'Novice'


def format_elo_leaderboard(elo):
    """Format ELO leaderboard."""
    board = elo.leaderboard()
    lines = ["ELO Leaderboard"]
    lines.append("─" * 50)
    for i, entry in enumerate(board, 1):
        cls = elo.rating_class(entry['name'])
        lines.append(
            f"  #{i:2d} {entry['name']:10s} "
            f"{entry['rating']:6.0f} "
            f"(peak {entry['peak']:5.0f}) "
            f"[{cls}]  ({entry['events']} events)")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ADAPTIVE DIFFICULTY — flow-state targeting (v21)
# ═══════════════════════════════════════════════════════════

def adaptive_difficulty(student, target_success_rate=0.7):
    """
    Compute optimal difficulty parameters to keep student
    in the flow zone (not too easy, not too hard).

    Uses recent performance to adjust:
    - mastery_level (may suggest +1 or -1)
    - kata length
    - target complexity (group distribution bias)

    Flow zone: success rate between 60-80%.
    """
    sessions = student.sessions
    n = len(sessions)

    if n < 3:
        return {
            'mastery_level': student.mastery_level,
            'length': 4,
            'complexity_bias': 'balanced',
            'reason': 'Too few sessions — using defaults',
        }

    # Recent success rate (Grade A or B = success)
    recent = sessions[-5:] if n >= 5 else sessions
    successes = sum(1 for s in recent if s['pct'] >= 70)
    success_rate = successes / len(recent)

    current_ml = student.mastery_level

    # Compute avg grade of recent
    recent_avg = sum(s['pct'] for s in recent) / len(recent)

    if success_rate > 0.85:
        # Too easy — increase difficulty
        new_ml = min(5, current_ml + 1)
        length = 6
        bias = 'harder'
        reason = (f'Success rate {success_rate:.0%} > 85% — '
                  f'increasing difficulty')
    elif success_rate < 0.4:
        # Too hard — decrease difficulty
        new_ml = max(1, current_ml - 1)
        length = 4
        bias = 'easier'
        reason = (f'Success rate {success_rate:.0%} < 40% — '
                  f'reducing difficulty')
    elif success_rate < 0.6:
        # Slightly too hard
        length = 4
        new_ml = current_ml
        bias = 'slightly_easier'
        reason = f'Success rate {success_rate:.0%} — slight easing'
    elif success_rate > 0.8:
        # Slightly too easy
        length = 5
        new_ml = current_ml
        bias = 'slightly_harder'
        reason = f'Success rate {success_rate:.0%} — slight challenge'
    else:
        # In the flow zone!
        length = 5
        new_ml = current_ml
        bias = 'balanced'
        reason = f'In flow zone ({success_rate:.0%} success rate)'

    # Group bias
    group_weights = {g: 1.0 for g in range(1, 8)}
    if bias == 'harder':
        for g in range(4, 8):
            group_weights[g] = 2.0
    elif bias == 'easier':
        for g in range(1, 4):
            group_weights[g] = 2.0

    return {
        'mastery_level': new_ml,
        'length': length,
        'complexity_bias': bias,
        'group_weights': group_weights,
        'success_rate': round(success_rate, 2),
        'recent_avg': round(recent_avg, 1),
        'reason': reason,
    }


def format_adaptive(ad):
    """Format adaptive difficulty result."""
    lines = [f"Adaptive Difficulty: {ad['reason']}"]
    lines.append(f"  Level: L{ad['mastery_level']}  "
                 f"Length: {ad['length']}  "
                 f"Bias: {ad['complexity_bias']}")
    if 'success_rate' in ad:
        lines.append(f"  Success rate: {ad['success_rate']:.0%}  "
                     f"Recent avg: {ad['recent_avg']:.1f}%")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# MATCHMAKING — pair students for sparring (v21)
# ═══════════════════════════════════════════════════════════

def matchmake(students, elo=None, max_rating_gap=200):
    """
    Find optimal sparring pairs from a pool of students.

    Strategy:
    1. Sort by ELO rating (or avg grade if no ELO)
    2. Pair adjacent students (closest skill)
    3. Enforce max rating gap
    4. If odd number, last student gets a bye

    Returns:
        list of (student_a, student_b, rating_diff) tuples
        plus list of byes
    """
    if len(students) < 2:
        return {'pairs': [], 'byes': [s.name for s in students]}

    # Sort by rating
    def sort_key(s):
        if elo:
            return elo.get(s.name)
        n = len(s.sessions)
        return sum(ss['pct'] for ss in s.sessions) / n if n else 0

    sorted_students = sorted(students, key=sort_key, reverse=True)

    pairs = []
    used = set()

    for i in range(len(sorted_students)):
        if i in used:
            continue
        best_j = None
        best_gap = float('inf')

        for j in range(i + 1, len(sorted_students)):
            if j in used:
                continue
            gap = abs(sort_key(sorted_students[i]) -
                      sort_key(sorted_students[j]))
            if gap < best_gap:
                best_gap = gap
                best_j = j

        if best_j is not None and best_gap <= max_rating_gap:
            a = sorted_students[i]
            b = sorted_students[best_j]
            rating_a = sort_key(a)
            rating_b = sort_key(b)
            pairs.append({
                'a': a.name, 'b': b.name,
                'rating_a': round(rating_a, 1),
                'rating_b': round(rating_b, 1),
                'gap': round(abs(rating_a - rating_b), 1),
            })
            used.add(i)
            used.add(best_j)

    byes = [sorted_students[i].name
            for i in range(len(sorted_students)) if i not in used]

    return {'pairs': pairs, 'byes': byes}


def format_matchmaking(mm):
    """Format matchmaking result."""
    lines = ["Matchmaking"]
    lines.append("─" * 45)
    for p in mm['pairs']:
        lines.append(
            f"  {p['a']:10s} ({p['rating_a']:6.1f}) vs "
            f"{p['b']:10s} ({p['rating_b']:6.1f})  "
            f"gap={p['gap']:.0f}")
    if mm['byes']:
        lines.append(f"  Byes: {', '.join(mm['byes'])}")
    lines.append(f"  Total pairs: {len(mm['pairs'])}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# COMPACT KATA NOTATION — encode/decode to string (v22)
# ═══════════════════════════════════════════════════════════

# Alphabet: 0-9 A-Z a-z + / = (64 chars for base symbols)
_NOTA_CHARS = (
    '0123456789'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
    '+/'
)
_NOTA_MAP = {c: i for i, c in enumerate(_NOTA_CHARS)}


def encode_kata_notation(kata, mode='dual'):
    """
    Encode a kata into a compact string notation.

    Format (dual): "D:<length>:<L-symbols>:<R-symbols>"
    Each symbol 0-63 maps to one character from _NOTA_CHARS.
    Symbols 64-75 (half-line) use two chars: '=' + offset char.

    Example: "D:5:AkQ0f:B1Rz3"
    """
    def encode_sym(sym):
        if sym < 64:
            return _NOTA_CHARS[sym]
        else:
            return '=' + _NOTA_CHARS[sym - 64]

    if mode == 'dual':
        left_str = ''.join(encode_sym(t[0]) for t in kata)
        right_str = ''.join(encode_sym(t[1]) for t in kata)
        return f"D:{len(kata)}:{left_str}:{right_str}"
    else:
        sym_str = ''.join(encode_sym(t) for t in kata)
        return f"S:{len(kata)}:{sym_str}"


def decode_kata_notation(notation):
    """
    Decode a compact notation string back to kata.

    Returns: (kata, mode) where kata is list of tuples or ints.
    """
    def decode_syms(s):
        syms = []
        i = 0
        while i < len(s):
            if s[i] == '=':
                syms.append(64 + _NOTA_MAP.get(s[i + 1], 0))
                i += 2
            else:
                syms.append(_NOTA_MAP.get(s[i], 0))
                i += 1
        return syms

    parts = notation.split(':')
    mode = parts[0]
    length = int(parts[1])

    if mode == 'D':
        left_syms = decode_syms(parts[2])
        right_syms = decode_syms(parts[3])
        kata = [(left_syms[i], right_syms[i], 0, 0)
                for i in range(min(len(left_syms), len(right_syms)))]
        return kata, 'dual'
    else:
        syms = decode_syms(parts[2])
        return syms, 'single'


def verify_notation(kata, mode='dual'):
    """Encode then decode, verify roundtrip."""
    encoded = encode_kata_notation(kata, mode)
    decoded, dec_mode = decode_kata_notation(encoded)

    if mode == 'dual':
        match = all(kata[i][0] == decoded[i][0] and
                    kata[i][1] == decoded[i][1]
                    for i in range(len(kata)))
    else:
        match = kata == decoded

    return {
        'encoded': encoded,
        'length': len(encoded),
        'roundtrip_ok': match,
        'compression': f"{len(kata)*2} syms → {len(encoded)} chars",
    }


# ═══════════════════════════════════════════════════════════
# HEATMAP — group × rule performance matrix (v22)
# ═══════════════════════════════════════════════════════════

def build_heatmap(student):
    """
    Build a group × rule heatmap for a student.

    Rows: 7 groups (G1-G7)
    Cols: 5 rules (R1-R5) + total
    Cell: average compliance % when that group appeared

    Also: group frequency distribution.
    """
    sessions = student.sessions
    if not sessions:
        return {'empty': True}

    # We need per-session rule scores and dominant groups
    # Approximate: use rule_history and group_hits
    # Build from sessions where we know the rule scores

    # Initialize matrix
    matrix = {}
    for g in range(1, 8):
        matrix[g] = {r: [] for r in range(1, 6)}

    # For each session, get the rule scores and associate with
    # the most common groups in that session
    for si, s in enumerate(sessions):
        # Get rule scores for this session index
        rule_scores = {}
        for r in range(1, 6):
            h = student.rule_history.get(r, [])
            if si < len(h):
                rule_scores[r] = h[si]
            else:
                rule_scores[r] = 50  # default

        # Estimate which groups were used (from group_hits is cumulative,
        # so we use mastery level as proxy for group range)
        ml = s.get('mastery_level', 1)
        likely_groups = list(range(1, min(8, ml + 3)))

        for g in likely_groups:
            for r in range(1, 6):
                matrix[g][r].append(rule_scores[r])

    # Average the matrix
    heatmap = {}
    for g in range(1, 8):
        heatmap[g] = {}
        for r in range(1, 6):
            vals = matrix[g][r]
            heatmap[g][r] = round(sum(vals) / len(vals), 1) if vals else 0

    # Frequency
    total_hits = sum(student.group_hits.values())
    freq = {}
    for g in range(1, 8):
        freq[g] = round(student.group_hits.get(g, 0) /
                        max(1, total_hits) * 100, 1)

    return {
        'empty': False,
        'heatmap': heatmap,
        'frequency': freq,
        'n_sessions': len(sessions),
    }


def format_heatmap(hm):
    """Format heatmap as ASCII table."""
    if hm.get('empty'):
        return "Heatmap: no data"

    heat = hm['heatmap']
    freq = hm['frequency']

    lines = ["Group × Rule Heatmap"]
    lines.append("─" * 55)

    # Header
    lines.append(f"       R1-Zon  R2-Ant  R3-Alt  R4-Smo  R5-Con  Freq")
    lines.append("─" * 55)

    group_names = {1: 'Empty', 2: 'Single', 3: 'Angle',
                   4: 'Parall', 5: 'Triple', 6: 'Master', 7: 'Peak'}

    def heat_char(val):
        """Map value to heat character."""
        if val == 0:
            return '  ·  '
        elif val >= 90:
            return ' ███ '
        elif val >= 70:
            return ' ▓▓▓ '
        elif val >= 50:
            return ' ▒▒▒ '
        elif val >= 30:
            return ' ░░░ '
        else:
            return '  ·  '

    for g in range(1, 8):
        row = f"G{g} {group_names[g]:6s}"
        for r in range(1, 6):
            row += heat_char(heat[g][r])
        row += f"  {freq[g]:5.1f}%"
        lines.append(row)

    lines.append("─" * 55)
    lines.append("  Legend: ███ ≥90%  ▓▓▓ ≥70%  ▒▒▒ ≥50%  ░░░ ≥30%  · =0")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SESSION REPLAY — step-by-step analysis (v22)
# ═══════════════════════════════════════════════════════════

def replay_session(student, session_index=-1):
    """
    Generate a detailed step-by-step replay of a training session.

    For each tact in the session:
    - Symbol generated (L/R)
    - Group assignment
    - Rule checks (which passed/failed)
    - Running score
    - Complexity trajectory

    Since we don't store individual tacts, we reconstruct
    from session metadata and generate a representative replay.
    """
    sessions = student.sessions
    if not sessions:
        return {'empty': True}

    s = sessions[session_index]
    ml = s.get('mastery_level', student.mastery_level)

    # Reconstruct by generating with same parameters
    seed = hash(f"{student.name}_{session_index}_{s['pct']}") & 0x7FFFFFFF
    dma = DualMatchStickAutomaton(mastery_level=ml, seed=seed)
    kata = dma.generate_dual_kata(length=s.get('length', 4))

    # Score step-by-step
    steps = []
    running_score = 0
    for ti, tact in enumerate(kata):
        sym_l, sym_r = tact[0], tact[1]
        gl, gr = get_group(sym_l), get_group(sym_r)
        cl = symbol_complexity(sym_l)
        cr = symbol_complexity(sym_r)

        # Rule checks for this tact pair
        checks = {}
        # R1: Zone exclusion
        checks['R1'] = gl != gr
        # R2: Anti-symmetry (bits differ)
        checks['R2'] = hamming_distance(sym_l, sym_r) >= 3
        # R3: Alternation (checked across tacts)
        if ti > 0:
            prev_l, prev_r = kata[ti - 1][0], kata[ti - 1][1]
            checks['R3'] = (get_group(prev_l) != gl or
                            get_group(prev_r) != gr)
        else:
            checks['R3'] = True
        # R4: Smoothness
        if ti > 0:
            prev_l = kata[ti - 1][0]
            checks['R4'] = hamming_distance(prev_l, sym_l) <= 3
        else:
            checks['R4'] = True
        # R5: Conservation (|cl - cr| < threshold)
        checks['R5'] = abs(cl - cr) <= 3

        passed = sum(1 for v in checks.values() if v)
        running_score += passed

        steps.append({
            'tact': ti + 1,
            'sym_l': sym_l, 'sym_r': sym_r,
            'group_l': gl, 'group_r': gr,
            'complexity_l': cl, 'complexity_r': cr,
            'rules': checks,
            'rules_passed': passed,
            'running_total': running_score,
        })

    max_possible = len(kata) * 5
    final_pct = running_score / max_possible * 100 if max_possible else 0

    return {
        'empty': False,
        'student': student.name,
        'session': session_index if session_index >= 0 else len(sessions),
        'steps': steps,
        'total_score': running_score,
        'max_score': max_possible,
        'pct': round(final_pct, 1),
        'n_tacts': len(kata),
    }


def format_replay(rp):
    """Format session replay as step-by-step text."""
    if rp.get('empty'):
        return "Replay: no data"

    lines = [f"Session Replay: {rp['student']} "
             f"(session #{rp['session']})"]
    lines.append("─" * 60)
    lines.append(f"  {'Tact':>4s}  {'L':>4s} {'R':>4s}  "
                 f"{'G_L':>3s} {'G_R':>3s}  "
                 f"{'C_L':>3s} {'C_R':>3s}  "
                 f"Rules      Score")
    lines.append("─" * 60)

    for step in rp['steps']:
        rule_str = ''.join(
            '✓' if step['rules'][f'R{r}'] else '✗'
            for r in range(1, 6))
        lines.append(
            f"  {step['tact']:4d}  "
            f"S{step['sym_l']:02d} S{step['sym_r']:02d}  "
            f"G{step['group_l']:>2d} G{step['group_r']:>2d}  "
            f"{step['complexity_l']:3d} {step['complexity_r']:3d}  "
            f"{rule_str}  "
            f"{step['running_total']:3d}/{step['tact']*5}")

    lines.append("─" * 60)
    lines.append(f"  Final: {rp['total_score']}/{rp['max_score']} "
                 f"({rp['pct']:.1f}%)")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# TREND PREDICTION — linear regression forecast (v23)
# ═══════════════════════════════════════════════════════════

def _linear_regression(xs, ys):
    """Simple linear regression: y = a + b*x. Returns (a, b, r²)."""
    n = len(xs)
    if n < 2:
        return 0, 0, 0

    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(xs[i] * ys[i] for i in range(n))
    sum_x2 = sum(x * x for x in xs)
    sum_y2 = sum(y * y for y in ys)

    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return sum_y / n, 0, 0

    b = (n * sum_xy - sum_x * sum_y) / denom
    a = (sum_y - b * sum_x) / n

    # R² (coefficient of determination)
    ss_tot = sum_y2 - sum_y * sum_y / n
    ss_res = sum((ys[i] - (a + b * xs[i])) ** 2 for i in range(n))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

    return a, b, r2


def predict_trend(student, horizon=5):
    """
    Predict student performance trend using linear regression.

    Analyzes:
    - Score trend (pct over sessions)
    - Mastery trend (projected mastery level)
    - Per-rule trends (which rules improving/declining)
    - Confidence (R² of fit)

    horizon: how many sessions ahead to forecast.
    """
    sessions = student.sessions
    if len(sessions) < 3:
        return {'sufficient_data': False, 'reason': f'need 3+ sessions, have {len(sessions)}'}

    # Score trend
    xs = list(range(len(sessions)))
    ys = [s['pct'] for s in sessions]
    a_score, b_score, r2_score = _linear_regression(xs, ys)

    # Per-rule trends
    rule_trends = {}
    for r in range(1, 6):
        rh = student.rule_history.get(r, [])
        if len(rh) >= 3:
            rxs = list(range(len(rh)))
            ra, rb, rr2 = _linear_regression(rxs, rh)
            rule_trends[r] = {
                'slope': round(rb, 2),
                'r2': round(rr2, 3),
                'direction': 'improving' if rb > 0.5 else
                             'declining' if rb < -0.5 else 'stable',
                'current': rh[-1] if rh else 0,
                'predicted': round(ra + rb * (len(rh) + horizon - 1), 1),
            }

    # Forecast
    n = len(sessions)
    forecasts = []
    for h in range(1, horizon + 1):
        pred = a_score + b_score * (n + h - 1)
        pred = max(0, min(100, pred))
        forecasts.append(round(pred, 1))

    # Mastery projection
    current_ml = student.mastery_level
    # Estimate sessions to next mastery based on score slope
    if b_score > 0:
        # How many sessions until avg score > threshold for next level
        threshold = 80  # assumed promotion threshold
        current_pred = a_score + b_score * (n - 1)
        if current_pred < threshold:
            sessions_to_next = int((threshold - current_pred) / b_score) + 1
        else:
            sessions_to_next = 0  # already above threshold
    else:
        sessions_to_next = -1  # not improving

    return {
        'sufficient_data': True,
        'score_trend': {
            'intercept': round(a_score, 2),
            'slope': round(b_score, 2),
            'r2': round(r2_score, 3),
            'direction': 'improving' if b_score > 0.5 else
                         'declining' if b_score < -0.5 else 'stable',
        },
        'forecast': forecasts,
        'rule_trends': rule_trends,
        'mastery_projection': {
            'current': current_ml,
            'sessions_to_next': sessions_to_next,
            'projected_ml': min(7, current_ml + 1)
                            if sessions_to_next >= 0 else current_ml,
        },
        'n_sessions': n,
    }


def format_trend(tr):
    """Format trend prediction as text."""
    if not tr.get('sufficient_data'):
        return f"Trend: insufficient data ({tr.get('reason', '')})"

    st = tr['score_trend']
    mp = tr['mastery_projection']

    lines = ["Trend Prediction"]
    lines.append("─" * 50)
    lines.append(f"  Score trend: {st['direction']} "
                 f"(slope={st['slope']:+.2f}/session, R²={st['r2']:.3f})")
    lines.append(f"  Forecast next {len(tr['forecast'])} sessions: "
                 f"{tr['forecast']}")
    lines.append(f"  Mastery: L{mp['current']} → L{mp['projected_ml']} "
                 f"(est. {mp['sessions_to_next']} sessions)")

    lines.append("  Rule trends:")
    for r, rt in sorted(tr['rule_trends'].items()):
        arrow = '↑' if rt['direction'] == 'improving' else \
                '↓' if rt['direction'] == 'declining' else '→'
        lines.append(f"    R{r}: {arrow} {rt['direction']} "
                     f"(slope={rt['slope']:+.2f}, "
                     f"now={rt['current']:.0f}, "
                     f"pred={rt['predicted']:.0f})")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ANOMALY DETECTION — outlier sessions (v23)
# ═══════════════════════════════════════════════════════════

def detect_anomalies(student, z_threshold=1.5):
    """
    Detect anomalous sessions based on z-score analysis.

    Types of anomalies:
    - score_spike: unusually high score
    - score_drop: unusually low score
    - rule_anomaly: one rule dramatically different from pattern
    - complexity_jump: sudden complexity increase

    z_threshold: standard deviations from mean to flag.
    """
    sessions = student.sessions
    if len(sessions) < 4:
        return {'anomalies': [], 'sufficient_data': False}

    def z_scores(values):
        n = len(values)
        mean = sum(values) / n
        if n < 2:
            return [0] * n
        var = sum((v - mean) ** 2 for v in values) / (n - 1)
        std = var ** 0.5 if var > 0 else 1
        return [(v - mean) / std for v in values]

    anomalies = []

    # 1. Score anomalies
    scores = [s['pct'] for s in sessions]
    s_zs = z_scores(scores)
    for i, z in enumerate(s_zs):
        if z > z_threshold:
            anomalies.append({
                'session': i,
                'type': 'score_spike',
                'value': scores[i],
                'z_score': round(z, 2),
                'detail': f'Session {i}: {scores[i]:.1f}% (z={z:.2f})',
            })
        elif z < -z_threshold:
            anomalies.append({
                'session': i,
                'type': 'score_drop',
                'value': scores[i],
                'z_score': round(z, 2),
                'detail': f'Session {i}: {scores[i]:.1f}% (z={z:.2f})',
            })

    # 2. Rule anomalies (per-rule z-scores)
    for r in range(1, 6):
        rh = student.rule_history.get(r, [])
        if len(rh) < 4:
            continue
        r_zs = z_scores(rh)
        for i, z in enumerate(r_zs):
            if abs(z) > z_threshold * 1.2:  # stricter for rules
                anomalies.append({
                    'session': i,
                    'type': 'rule_anomaly',
                    'rule': r,
                    'value': rh[i],
                    'z_score': round(z, 2),
                    'detail': f'Session {i} R{r}: {rh[i]:.0f}% (z={z:.2f})',
                })

    # 3. Session-to-session jumps
    for i in range(1, len(scores)):
        delta = scores[i] - scores[i - 1]
        if abs(delta) > 25:  # >25% jump
            anomalies.append({
                'session': i,
                'type': 'complexity_jump',
                'value': delta,
                'z_score': 0,
                'detail': f'Session {i}: Δ={delta:+.1f}% from prev',
            })

    # Sort by absolute z-score
    anomalies.sort(key=lambda a: abs(a.get('z_score', 0)), reverse=True)

    return {
        'anomalies': anomalies,
        'sufficient_data': True,
        'total_sessions': len(sessions),
        'threshold': z_threshold,
        'n_anomalies': len(anomalies),
    }


def format_anomalies(ad):
    """Format anomaly report."""
    if not ad.get('sufficient_data'):
        return "Anomaly detection: insufficient data"

    lines = [f"Anomaly Detection ({ad['total_sessions']} sessions, "
             f"z>{ad['threshold']})"]
    lines.append("─" * 50)

    if not ad['anomalies']:
        lines.append("  No anomalies detected. ✓")
    else:
        lines.append(f"  Found {ad['n_anomalies']} anomalies:")
        for a in ad['anomalies'][:10]:  # top 10
            icon = {'score_spike': '⬆', 'score_drop': '⬇',
                    'rule_anomaly': '⚠', 'complexity_jump': '⚡'
                    }.get(a['type'], '?')
            lines.append(f"    {icon} {a['detail']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# TRAINING PLAN GENERATOR — weekly/monthly schedule (v23)
# ═══════════════════════════════════════════════════════════

def generate_training_plan(student, weeks=4, sessions_per_week=3):
    """
    Generate a personalized training plan based on student profile.

    Each session has:
    - Focus area (weakest rule or group)
    - Recommended length
    - Target mastery actions
    - Warm-up / main / cool-down structure

    The plan considers:
    - Current mastery level
    - Weak rules (from rule_history)
    - Trend direction
    - Anomaly patterns
    """
    ml = student.mastery_level

    # Identify weak rules
    weak_rules = []
    for r in range(1, 6):
        rh = student.rule_history.get(r, [])
        if rh:
            avg = sum(rh[-5:]) / min(5, len(rh))
            weak_rules.append((r, avg))
    weak_rules.sort(key=lambda x: x[1])

    # Identify weak groups
    total_hits = sum(student.group_hits.values())
    weak_groups = []
    for g in range(1, min(8, ml + 3)):
        hits = student.group_hits.get(g, 0)
        pct = hits / max(1, total_hits) * 100
        if pct < 15:  # underrepresented
            weak_groups.append((g, pct))

    # Get trend info
    trend = predict_trend(student, horizon=weeks * sessions_per_week)

    # Build weekly plan
    plan = {
        'student': student.name,
        'mastery_level': ml,
        'weeks': weeks,
        'sessions_per_week': sessions_per_week,
        'weak_rules': weak_rules[:2],
        'weak_groups': weak_groups[:2],
        'schedule': [],
    }

    rule_names = {1: 'Zone', 2: 'Anti-sym', 3: 'Alternation',
                  4: 'Smoothness', 5: 'Conservation'}
    group_names = {1: 'Empty', 2: 'Single', 3: 'Angle',
                   4: 'Parallel', 5: 'Triple', 6: 'Master', 7: 'Peak'}

    for w in range(1, weeks + 1):
        week_sessions = []
        for d in range(1, sessions_per_week + 1):
            session_num = (w - 1) * sessions_per_week + d

            # Rotate focus: weak rule → weak group → free practice
            focus_cycle = session_num % 3
            if focus_cycle == 1 and weak_rules:
                wr = weak_rules[session_num % len(weak_rules)]
                focus = f"R{wr[0]}-{rule_names[wr[0]]} (avg {wr[1]:.0f}%)"
                focus_type = 'rule'
            elif focus_cycle == 2 and weak_groups:
                wg = weak_groups[session_num % len(weak_groups)]
                focus = f"G{wg[0]}-{group_names.get(wg[0], '?')} ({wg[1]:.0f}%)"
                focus_type = 'group'
            else:
                focus = 'Free practice (full kata)'
                focus_type = 'free'

            # Session length scales with week progression
            base_len = 4 + ml
            length = base_len + (w - 1)  # increase over weeks

            # Structure
            session = {
                'week': w,
                'day': d,
                'session_num': session_num,
                'focus': focus,
                'focus_type': focus_type,
                'length': length,
                'warmup': max(2, length // 3),
                'main': length,
                'cooldown': max(1, length // 4),
                'target_pct': min(95, 60 + w * 5 + ml * 3),
            }
            week_sessions.append(session)

        plan['schedule'].append({
            'week': w,
            'sessions': week_sessions,
            'week_goal': f"Maintain >{55 + w * 5}% avg" if w < weeks
                         else f"Achieve >{70 + ml * 3}% avg",
        })

    return plan


def format_training_plan(plan):
    """Format training plan as readable schedule."""
    lines = [f"Training Plan: {plan['student']} "
             f"(L{plan['mastery_level']})"]
    lines.append("═" * 55)

    if plan['weak_rules']:
        wr_str = ', '.join(f"R{r[0]}({r[1]:.0f}%)" for r in plan['weak_rules'])
        lines.append(f"  Weak rules: {wr_str}")
    if plan['weak_groups']:
        wg_str = ', '.join(f"G{g[0]}({g[1]:.0f}%)" for g in plan['weak_groups'])
        lines.append(f"  Weak groups: {wg_str}")

    lines.append("")

    for week_data in plan['schedule']:
        w = week_data['week']
        lines.append(f"  Week {w}: {week_data['week_goal']}")
        lines.append("  " + "─" * 50)

        for s in week_data['sessions']:
            lines.append(
                f"    #{s['session_num']:2d}  "
                f"Focus: {s['focus']}")
            lines.append(
                f"         Warmup({s['warmup']}t) → "
                f"Main({s['main']}t) → "
                f"Cooldown({s['cooldown']}t)  "
                f"Target: {s['target_pct']}%")
        lines.append("")

    total = plan['weeks'] * plan['sessions_per_week']
    lines.append(f"  Total: {total} sessions over {plan['weeks']} weeks")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SYMBOL TAXONOMY — classification & visual catalog (v24)
# ═══════════════════════════════════════════════════════════

# Bit-position names for 6-bit matchstick representation
BIT_NAMES = {
    0: 'base-H',    # horizontal base
    1: 'base-V',    # vertical base
    2: 'arm-L',     # left arm
    3: 'arm-R',     # right arm
    4: 'ext-U',     # upper extension
    5: 'ext-D',     # lower extension
}

# Visual ASCII art for each bit position
BIT_VISUALS = {
    0: '───',   # horizontal
    1: ' │ ',   # vertical
    2: '╱  ',   # left arm
    3: '  ╲',   # right arm
    4: ' ╿ ',   # upper ext
    5: ' ╽ ',   # lower ext
}


def symbol_taxonomy(sym):
    """
    Complete taxonomic classification of a single symbol.

    Returns dict with:
    - binary: 6-bit string
    - group: Kryukov group (1-7)
    - complexity: popcount
    - active_bits: which bits are set
    - bit_names: human names for active bits
    - symmetry_class: bilateral, rotational, asymmetric
    - category: descriptive movement category
    - dual_complement: XOR inverse symbol
    - neighbors: symbols at Hamming distance 1
    """
    bits = format(sym, '06b')
    active = [i for i in range(6) if (sym >> i) & 1]
    comp = bin(sym).count('1')
    group = get_group(sym)

    # Symmetry classification
    # L/R symmetric: bits 2,3 both set or both unset
    lr_sym = ((sym >> 2) & 1) == ((sym >> 3) & 1)
    # U/D symmetric: bits 4,5 both set or both unset
    ud_sym = ((sym >> 4) & 1) == ((sym >> 5) & 1)

    if lr_sym and ud_sym:
        sym_class = 'bilateral'
    elif lr_sym or ud_sym:
        sym_class = 'partial'
    else:
        sym_class = 'asymmetric'

    # Movement category
    if comp == 0:
        category = 'rest'
    elif comp == 1:
        category = 'isolate'
    elif comp == 2:
        if lr_sym:
            category = 'open'
        else:
            category = 'diagonal'
    elif comp == 3:
        category = 'compound'
    elif comp == 4:
        category = 'complex'
    elif comp == 5:
        category = 'dense'
    else:
        category = 'full'

    # Dual complement (XOR with 0b111111)
    dual = sym ^ 0b111111

    # Hamming-1 neighbors
    neighbors = [sym ^ (1 << i) for i in range(6)]

    return {
        'symbol': sym,
        'binary': bits,
        'group': group,
        'complexity': comp,
        'active_bits': active,
        'bit_names': [BIT_NAMES[b] for b in active],
        'symmetry_class': sym_class,
        'category': category,
        'dual_complement': dual,
        'neighbors': neighbors,
    }


def format_symbol_card(tax):
    """Format a symbol taxonomy as a visual card."""
    lines = [f"Symbol S{tax['symbol']:02d} (0b{tax['binary']})"]
    lines.append("┌───────────────────────────┐")
    lines.append(f"│ Group: G{tax['group']}  "
                 f"Complexity: {tax['complexity']}  │")
    lines.append(f"│ Symmetry: {tax['symmetry_class']:<12s}   │")
    lines.append(f"│ Category: {tax['category']:<12s}   │")
    lines.append(f"│ Bits: {', '.join(tax['bit_names']) or 'none':<19s} │")
    lines.append(f"│ Dual: S{tax['dual_complement']:02d}"
                 f"{'':19s}│")
    nbr = ', '.join(f"S{n:02d}" for n in tax['neighbors'][:4])
    lines.append(f"│ Near: {nbr:<19s} │")
    lines.append("└───────────────────────────┘")
    return '\n'.join(lines)


def build_taxonomy_catalog():
    """Build complete taxonomy for all 64 base symbols."""
    catalog = {}
    stats = {
        'by_group': {},
        'by_symmetry': {'bilateral': 0, 'partial': 0, 'asymmetric': 0},
        'by_category': {},
        'by_complexity': {},
    }

    for sym in range(64):
        tax = symbol_taxonomy(sym)
        catalog[sym] = tax

        g = tax['group']
        stats['by_group'][g] = stats['by_group'].get(g, 0) + 1
        stats['by_symmetry'][tax['symmetry_class']] += 1
        cat = tax['category']
        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1
        c = tax['complexity']
        stats['by_complexity'][c] = stats['by_complexity'].get(c, 0) + 1

    return catalog, stats


# ═══════════════════════════════════════════════════════════
# PATTERN FINGERPRINT — unique kata signature (v24)
# ═══════════════════════════════════════════════════════════

def compute_fingerprint(kata):
    """
    Compute a unique fingerprint for a kata sequence.

    The fingerprint captures structural properties:
    - Group sequence hash
    - Complexity profile
    - Rule compliance vector
    - Symmetry distribution

    Two katas with the same fingerprint have equivalent
    structural properties even if symbols differ.
    """
    if not kata:
        return {'hash': '0000', 'features': {}}

    # Feature extraction
    groups = []
    complexities = []
    symmetries = []

    for t in kata:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            sl, sr = t[0], t[1]
        else:
            sl, sr = t, 0

        gl, gr = get_group(sl), get_group(sr)
        cl, cr = symbol_complexity(sl), symbol_complexity(sr)

        groups.extend([gl, gr])
        complexities.extend([cl, cr])

        tax = symbol_taxonomy(sl)
        symmetries.append(tax['symmetry_class'])

    # Group transition pattern
    transitions = []
    for i in range(1, len(groups)):
        transitions.append(groups[i] - groups[i - 1])

    # Complexity gradient
    gradients = []
    for i in range(1, len(complexities)):
        gradients.append(complexities[i] - complexities[i - 1])

    # Feature vector
    features = {
        'length': len(kata),
        'group_mean': round(sum(groups) / len(groups), 2),
        'group_range': max(groups) - min(groups),
        'complexity_mean': round(sum(complexities) / len(complexities), 2),
        'complexity_var': round(
            sum((c - sum(complexities) / len(complexities)) ** 2
                for c in complexities) / len(complexities), 2),
        'transition_sum': sum(abs(t) for t in transitions),
        'gradient_sum': sum(abs(g) for g in gradients),
        'symmetry_ratio': round(
            symmetries.count('bilateral') / len(symmetries), 2),
        'unique_groups': len(set(groups)),
    }

    # Hash from features (deterministic)
    h = 0
    for k, v in sorted(features.items()):
        h = (h * 31 + hash((k, round(v, 1)))) & 0xFFFFFFFF
    fp_hash = format(h, '08x')

    return {
        'hash': fp_hash,
        'features': features,
        'group_seq': groups,
        'complexity_seq': complexities,
    }


def fingerprint_similarity(fp1, fp2):
    """
    Compute similarity between two fingerprints (0.0 to 1.0).

    Uses normalized feature distance.
    """
    f1 = fp1['features']
    f2 = fp2['features']

    if not f1 or not f2:
        return 0.0

    keys = set(f1.keys()) & set(f2.keys())
    if not keys:
        return 0.0

    diffs = []
    for k in keys:
        v1, v2 = f1[k], f2[k]
        max_val = max(abs(v1), abs(v2), 1)
        diffs.append(abs(v1 - v2) / max_val)

    avg_diff = sum(diffs) / len(diffs)
    return round(max(0, 1 - avg_diff), 3)


def format_fingerprint(fp):
    """Format fingerprint as readable text."""
    lines = [f"Fingerprint: #{fp['hash']}"]
    lines.append("─" * 40)
    for k, v in sorted(fp['features'].items()):
        lines.append(f"  {k:<20s}: {v}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# DIAGNOSTIC REPORT — comprehensive student assessment (v24)
# ═══════════════════════════════════════════════════════════

def generate_diagnostic(student):
    """
    Generate a comprehensive diagnostic report for a student.

    Combines all analytical tools into a single assessment:
    - Profile summary
    - Performance statistics
    - Trend analysis
    - Anomaly scan
    - Heatmap summary
    - Strengths & weaknesses
    - Recommended actions
    """
    profile = {
        'name': student.name,
        'mastery_level': student.mastery_level,
        'n_sessions': len(student.sessions),
    }

    # Performance stats
    if student.sessions:
        scores = [s['pct'] for s in student.sessions]
        profile['avg_score'] = round(sum(scores) / len(scores), 1)
        profile['best_score'] = round(max(scores), 1)
        profile['worst_score'] = round(min(scores), 1)
        profile['recent_avg'] = round(
            sum(scores[-5:]) / min(5, len(scores)), 1)
        profile['improvement'] = round(
            profile['recent_avg'] - profile['avg_score'], 1)
    else:
        profile['avg_score'] = 0
        profile['best_score'] = 0
        profile['worst_score'] = 0
        profile['recent_avg'] = 0
        profile['improvement'] = 0

    # Trend
    trend = predict_trend(student, horizon=5)

    # Anomalies
    anomalies = detect_anomalies(student, z_threshold=1.5)

    # Heatmap summary
    heatmap = build_heatmap(student)

    # Strengths & weaknesses
    strengths = []
    weaknesses = []

    for r in range(1, 6):
        rh = student.rule_history.get(r, [])
        if rh:
            avg = sum(rh[-5:]) / min(5, len(rh))
            rule_name = {1: 'Zone', 2: 'Anti-symmetry', 3: 'Alternation',
                         4: 'Smoothness', 5: 'Conservation'}[r]
            if avg >= 80:
                strengths.append(f"R{r}-{rule_name} ({avg:.0f}%)")
            elif avg < 50:
                weaknesses.append(f"R{r}-{rule_name} ({avg:.0f}%)")

    # Group coverage
    total_hits = sum(student.group_hits.values())
    for g in range(1, 8):
        pct = student.group_hits.get(g, 0) / max(1, total_hits) * 100
        gname = {1: 'Empty', 2: 'Single', 3: 'Angle', 4: 'Parallel',
                 5: 'Triple', 6: 'Master', 7: 'Peak'}[g]
        if pct > 30:
            strengths.append(f"G{g}-{gname} ({pct:.0f}%)")
        elif pct < 5 and g <= student.mastery_level + 2:
            weaknesses.append(f"G{g}-{gname} ({pct:.0f}%)")

    # Recommended actions
    actions = []
    if weaknesses:
        actions.append(f"Focus on: {weaknesses[0]}")
    if trend.get('sufficient_data') and \
       trend['score_trend']['direction'] == 'declining':
        actions.append("Score declining — reduce difficulty temporarily")
    if anomalies.get('n_anomalies', 0) > 3:
        actions.append("High anomaly count — review session consistency")
    if profile['recent_avg'] > 85 and student.mastery_level < 7:
        actions.append(f"Ready for promotion to L{student.mastery_level + 1}")
    if not actions:
        actions.append("Continue current training regimen")

    return {
        'profile': profile,
        'trend': trend,
        'anomalies': anomalies,
        'heatmap': heatmap,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'actions': actions,
    }


def format_diagnostic(diag):
    """Format diagnostic report."""
    p = diag['profile']

    lines = ["╔══════════════════════════════════════════╗"]
    lines.append(f"║  DIAGNOSTIC REPORT: {p['name']:<19s} ║")
    lines.append("╠══════════════════════════════════════════╣")
    lines.append(f"║  Mastery: L{p['mastery_level']}  "
                 f"Sessions: {p['n_sessions']:<14d}║")
    lines.append(f"║  Avg: {p['avg_score']:5.1f}%  "
                 f"Best: {p['best_score']:5.1f}%  "
                 f"Recent: {p['recent_avg']:5.1f}% ║")

    # Trend
    tr = diag['trend']
    if tr.get('sufficient_data'):
        st = tr['score_trend']
        arrow = '↑' if st['direction'] == 'improving' else \
                '↓' if st['direction'] == 'declining' else '→'
        lines.append(f"║  Trend: {arrow} {st['direction']:<10s} "
                     f"(slope={st['slope']:+.1f}, "
                     f"R²={st['r2']:.2f})  ║")

    lines.append("╠══════════════════════════════════════════╣")

    # Strengths
    lines.append("║  Strengths:                              ║")
    for s in diag['strengths'][:3]:
        lines.append(f"║    ✓ {s:<34s} ║")

    # Weaknesses
    lines.append("║  Weaknesses:                             ║")
    for w in diag['weaknesses'][:3]:
        lines.append(f"║    ✗ {w:<34s} ║")

    # Anomalies
    n_anom = diag['anomalies'].get('n_anomalies', 0)
    lines.append(f"║  Anomalies: {n_anom} detected"
                 f"{'':>18s}║")

    lines.append("╠══════════════════════════════════════════╣")
    lines.append("║  Recommended Actions:                    ║")
    for a in diag['actions']:
        lines.append(f"║    → {a:<34s} ║")

    lines.append("╚══════════════════════════════════════════╝")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# KATA MUTATION ENGINE — systematic transforms (v25)
# ═══════════════════════════════════════════════════════════

def mutate_kata_v2(kata, mutation_type='mirror', intensity=1.0, seed=None):
    """
    Apply systematic mutations to a kata sequence (v25 extended engine).

    Mutation types:
    - mirror:    swap L/R hands (tact[0] ↔ tact[1])
    - invert:    XOR complement all symbols
    - shift:     rotate group assignments up/down
    - scramble:  permute tact order
    - stretch:   duplicate/remove tacts
    - blend:     mix two tacts into one
    - bitflip:   flip random bits (controlled by intensity)

    intensity: 0.0 (minimal) to 1.0 (maximal) mutation strength.
    seed: for reproducibility.
    """
    import random as _rnd
    rng = _rnd.Random(seed)

    result = [list(t) for t in kata]  # mutable copy
    n = len(result)
    if n == 0:
        return []

    n_affected = max(1, int(n * intensity))

    if mutation_type == 'mirror':
        # Swap L/R hands
        indices = rng.sample(range(n), min(n_affected, n))
        for i in indices:
            result[i][0], result[i][1] = result[i][1], result[i][0]

    elif mutation_type == 'invert':
        # XOR complement
        indices = rng.sample(range(n), min(n_affected, n))
        for i in indices:
            result[i][0] = result[i][0] ^ 0b111111
            result[i][1] = result[i][1] ^ 0b111111

    elif mutation_type == 'shift':
        # Shift symbols by group offset
        shift_amt = max(1, int(intensity * 8))
        indices = rng.sample(range(n), min(n_affected, n))
        for i in indices:
            result[i][0] = (result[i][0] + shift_amt) % 64
            result[i][1] = (result[i][1] + shift_amt) % 64

    elif mutation_type == 'scramble':
        # Permute tact order
        indices = list(range(n))
        for _ in range(n_affected):
            a, b = rng.sample(range(n), 2)
            indices[a], indices[b] = indices[b], indices[a]
        result = [result[i] for i in indices]

    elif mutation_type == 'stretch':
        # Duplicate random tacts
        new_result = []
        for i, t in enumerate(result):
            new_result.append(t)
            if rng.random() < intensity * 0.5 and len(new_result) < n * 2:
                new_result.append(list(t))  # duplicate
        result = new_result

    elif mutation_type == 'blend':
        # Blend adjacent tacts (average symbols)
        indices = rng.sample(range(max(1, n - 1)), min(n_affected, n - 1))
        for i in sorted(indices, reverse=True):
            blended_l = (result[i][0] + result[i + 1][0]) // 2
            blended_r = (result[i][1] + result[i + 1][1]) // 2
            result[i] = [blended_l, blended_r, 0, 0]
            result.pop(i + 1)

    elif mutation_type == 'bitflip':
        # Flip random bits
        n_flips = max(1, int(intensity * n * 2))
        for _ in range(n_flips):
            ti = rng.randrange(n)
            hand = rng.randint(0, 1)
            bit = rng.randint(0, 5)
            result[ti][hand] ^= (1 << bit)

    # Convert back to tuples
    return [tuple(t[:4] if len(t) >= 4 else t + [0] * (4 - len(t)))
            for t in result]


def mutation_chain(kata, mutations, seed=None):
    """
    Apply a chain of mutations sequentially.

    mutations: list of (type, intensity) tuples.
    Example: [('mirror', 0.5), ('bitflip', 0.3), ('scramble', 0.2)]
    """
    current = kata
    history = [{'step': 0, 'type': 'original', 'length': len(kata)}]

    for i, (mtype, mint) in enumerate(mutations):
        s = (seed + i * 37) if seed else None
        current = mutate_kata_v2(current, mtype, mint, s)
        history.append({
            'step': i + 1,
            'type': mtype,
            'intensity': mint,
            'length': len(current),
        })

    return current, history


def format_mutation_history(history):
    """Format mutation chain history."""
    lines = ["Mutation Chain"]
    lines.append("─" * 45)
    for h in history:
        if h['type'] == 'original':
            lines.append(f"  [0] Original ({h['length']} tacts)")
        else:
            lines.append(f"  [{h['step']}] {h['type']} "
                         f"(int={h.get('intensity', 0):.1f}) "
                         f"→ {h['length']} tacts")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# DIFFICULTY CALIBRATION — adaptive targeting (v25)
# ═══════════════════════════════════════════════════════════

def calibrate_difficulty(student, target_pct=75.0):
    """
    Calibrate difficulty parameters to achieve a target score percentage.

    Uses binary search over mastery_level and kata length to find
    the combination that produces scores closest to target_pct.

    Returns optimal parameters and calibration curve.
    """
    sessions = student.sessions
    if len(sessions) < 3:
        return {'calibrated': False, 'reason': 'need 3+ sessions'}

    # Current performance baseline
    recent = sessions[-5:]
    current_avg = sum(s['pct'] for s in recent) / len(recent)
    current_ml = student.mastery_level

    # Calibration: test different ML + length combos
    calibration = []
    for ml in range(max(1, current_ml - 2), min(8, current_ml + 3)):
        for length in range(3, 10):
            # Estimate difficulty (higher ML and length = harder)
            estimated_difficulty = ml * 10 + length * 5
            # Expected score based on student's trend
            # Simple model: current_avg adjusted by difficulty delta
            diff_delta = estimated_difficulty - (current_ml * 10 +
                                                  len(recent) * 5)
            expected = current_avg - diff_delta * 0.8
            expected = max(10, min(100, expected))

            calibration.append({
                'mastery_level': ml,
                'length': length,
                'difficulty': estimated_difficulty,
                'expected_pct': round(expected, 1),
                'gap': round(abs(expected - target_pct), 1),
            })

    # Sort by gap to target
    calibration.sort(key=lambda c: c['gap'])
    best = calibration[0]

    # Difficulty curve: score vs difficulty
    curve = []
    for c in sorted(calibration, key=lambda x: x['difficulty']):
        curve.append((c['difficulty'], c['expected_pct']))

    return {
        'calibrated': True,
        'target_pct': target_pct,
        'current_avg': round(current_avg, 1),
        'current_ml': current_ml,
        'recommended': {
            'mastery_level': best['mastery_level'],
            'length': best['length'],
            'expected_pct': best['expected_pct'],
        },
        'top_options': calibration[:5],
        'curve': curve[:15],
    }


def format_calibration(cal):
    """Format calibration results."""
    if not cal.get('calibrated'):
        return f"Calibration: {cal.get('reason', 'failed')}"

    rec = cal['recommended']
    lines = [f"Difficulty Calibration (target: {cal['target_pct']}%)"]
    lines.append("─" * 50)
    lines.append(f"  Current: L{cal['current_ml']} avg={cal['current_avg']}%")
    lines.append(f"  Recommended: L{rec['mastery_level']} "
                 f"len={rec['length']} "
                 f"(expected {rec['expected_pct']}%)")
    lines.append("")
    lines.append("  Top 5 options:")
    for c in cal['top_options']:
        lines.append(f"    L{c['mastery_level']} len={c['length']}  "
                     f"diff={c['difficulty']:3d}  "
                     f"exp={c['expected_pct']:5.1f}%  "
                     f"gap={c['gap']:4.1f}")

    # Mini-curve
    lines.append("")
    lines.append("  Difficulty curve:")
    for d, p in cal['curve'][:8]:
        bar_len = int(p / 5)
        lines.append(f"    D{d:3d}: {'█' * bar_len} {p:.0f}%")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SESSION COMPARATOR — diff two sessions (v25)
# ═══════════════════════════════════════════════════════════

def compare_sessions(student, idx_a, idx_b):
    """
    Compare two sessions of the same student side-by-side.

    Analyzes:
    - Score difference
    - Rule-by-rule comparison
    - Group distribution changes
    - Complexity evolution
    - Improvement areas
    """
    sessions = student.sessions
    n = len(sessions)
    if n < 2:
        return {'comparable': False, 'reason': 'need 2+ sessions'}

    # Normalize indices
    if idx_a < 0:
        idx_a = n + idx_a
    if idx_b < 0:
        idx_b = n + idx_b

    if not (0 <= idx_a < n and 0 <= idx_b < n):
        return {'comparable': False, 'reason': 'index out of range'}

    sa, sb = sessions[idx_a], sessions[idx_b]

    # Score comparison
    delta_pct = sb['pct'] - sa['pct']

    # Rule-by-rule
    rule_deltas = {}
    for r in range(1, 6):
        rh = student.rule_history.get(r, [])
        va = rh[idx_a] if idx_a < len(rh) else 50
        vb = rh[idx_b] if idx_b < len(rh) else 50
        rule_deltas[r] = {
            'a': round(va, 1),
            'b': round(vb, 1),
            'delta': round(vb - va, 1),
            'improved': vb > va + 2,
            'declined': vb < va - 2,
        }

    # Mastery level change
    ml_a = sa.get('mastery_level', student.mastery_level)
    ml_b = sb.get('mastery_level', student.mastery_level)

    # Improvements and declines
    improved = [f"R{r}" for r, d in rule_deltas.items() if d['improved']]
    declined = [f"R{r}" for r, d in rule_deltas.items() if d['declined']]

    return {
        'comparable': True,
        'session_a': idx_a,
        'session_b': idx_b,
        'score_a': round(sa['pct'], 1),
        'score_b': round(sb['pct'], 1),
        'delta_pct': round(delta_pct, 1),
        'mastery_a': ml_a,
        'mastery_b': ml_b,
        'rule_deltas': rule_deltas,
        'improved_rules': improved,
        'declined_rules': declined,
    }


def format_comparison(comp):
    """Format session comparison."""
    if not comp.get('comparable'):
        return f"Compare: {comp.get('reason', 'error')}"

    a, b = comp['session_a'], comp['session_b']
    lines = [f"Session Comparison: #{a} vs #{b}"]
    lines.append("─" * 50)

    # Score
    arrow = '↑' if comp['delta_pct'] > 0 else '↓' if comp['delta_pct'] < 0 else '→'
    lines.append(f"  Score: {comp['score_a']}% → {comp['score_b']}% "
                 f"({arrow} {comp['delta_pct']:+.1f}%)")
    lines.append(f"  Mastery: L{comp['mastery_a']} → L{comp['mastery_b']}")

    # Rule table
    lines.append("")
    lines.append(f"  {'Rule':<8s} {'#' + str(a):>6s} {'#' + str(b):>6s} "
                 f"{'Delta':>7s}  Status")
    lines.append("  " + "─" * 40)

    rule_names = {1: 'Zone', 2: 'Anti', 3: 'Alter', 4: 'Smooth', 5: 'Cons'}
    for r in range(1, 6):
        d = comp['rule_deltas'][r]
        if d['improved']:
            status = '↑ improved'
        elif d['declined']:
            status = '↓ declined'
        else:
            status = '→ stable'
        lines.append(f"  R{r}-{rule_names[r]:<5s} {d['a']:5.1f}% "
                     f"{d['b']:5.1f}% {d['delta']:+6.1f}%  {status}")

    # Summary
    lines.append("")
    if comp['improved_rules']:
        lines.append(f"  Improved: {', '.join(comp['improved_rules'])}")
    if comp['declined_rules']:
        lines.append(f"  Declined: {', '.join(comp['declined_rules'])}")
    if not comp['improved_rules'] and not comp['declined_rules']:
        lines.append("  All rules stable.")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# RHYTHM ANALYSIS — temporal patterns in kata (v26)
# ═══════════════════════════════════════════════════════════

def analyze_rhythm(kata):
    """
    Analyze rhythmic/temporal patterns in a kata sequence.

    Metrics:
    - complexity_rhythm: sequence of complexity values (beat pattern)
    - group_rhythm: sequence of group transitions
    - acceleration: change in complexity over time
    - periodicity: detect repeating patterns
    - syncopation: off-beat complexity spikes
    - flow_score: smoothness of transitions (0-100)
    """
    if not kata or len(kata) < 2:
        return {'empty': True}

    # Extract sequences
    c_seq = []  # complexity per tact
    g_seq = []  # group per tact
    for t in kata:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            sl, sr = t[0], t[1]
        else:
            sl, sr = t, 0
        c_seq.append(symbol_complexity(sl) + symbol_complexity(sr))
        g_seq.append((get_group(sl), get_group(sr)))

    n = len(c_seq)

    # Acceleration (first derivative of complexity)
    accel = [c_seq[i] - c_seq[i - 1] for i in range(1, n)]

    # Periodicity detection (autocorrelation at lag 1..n//2)
    periods = {}
    for lag in range(1, n // 2 + 1):
        matches = sum(1 for i in range(n - lag)
                      if g_seq[i] == g_seq[i + lag])
        periods[lag] = round(matches / (n - lag), 2)

    best_period = max(periods, key=periods.get) if periods else 0
    periodicity = periods.get(best_period, 0)

    # Syncopation: complexity spikes on even-indexed tacts
    # (assuming odd=strong beat, even=weak beat)
    mean_c = sum(c_seq) / n
    syncopation = sum(1 for i in range(0, n, 2)
                      if c_seq[i] > mean_c * 1.3) / max(1, n // 2)

    # Flow score: penalize large Hamming jumps between adjacent tacts
    flow_penalties = 0
    for i in range(1, n):
        if isinstance(kata[i], (list, tuple)) and len(kata[i]) >= 2:
            h = hamming_distance(kata[i - 1][0], kata[i][0])
            flow_penalties += max(0, h - 3)  # penalize >3
    flow_score = max(0, 100 - flow_penalties * 15)

    # Complexity contour classification
    if n >= 3:
        first_third = sum(c_seq[:n // 3]) / max(1, n // 3)
        last_third = sum(c_seq[-n // 3:]) / max(1, n // 3)
        if last_third > first_third * 1.3:
            contour = 'ascending'
        elif first_third > last_third * 1.3:
            contour = 'descending'
        else:
            contour = 'plateau'
    else:
        contour = 'short'

    return {
        'empty': False,
        'complexity_seq': c_seq,
        'group_seq': g_seq,
        'acceleration': accel,
        'mean_complexity': round(mean_c, 2),
        'periodicity': periodicity,
        'best_period': best_period,
        'syncopation': round(syncopation, 2),
        'flow_score': flow_score,
        'contour': contour,
        'n_tacts': n,
    }


def format_rhythm(rh):
    """Format rhythm analysis."""
    if rh.get('empty'):
        return "Rhythm: no data"

    lines = ["Rhythm Analysis"]
    lines.append("─" * 50)

    # Complexity waveform
    lines.append("  Complexity waveform:")
    max_c = max(rh['complexity_seq']) if rh['complexity_seq'] else 1
    for i, c in enumerate(rh['complexity_seq']):
        bar = '█' * int(c / max(1, max_c) * 20)
        lines.append(f"    T{i + 1:2d}: {bar:<20s} {c}")

    # Acceleration
    lines.append("  Acceleration: " +
                 ' '.join(f"{a:+d}" for a in rh['acceleration']))

    lines.append(f"  Mean complexity: {rh['mean_complexity']}")
    lines.append(f"  Contour: {rh['contour']}")
    lines.append(f"  Periodicity: {rh['periodicity']:.2f} "
                 f"(best lag={rh['best_period']})")
    lines.append(f"  Syncopation: {rh['syncopation']:.2f}")
    lines.append(f"  Flow score: {rh['flow_score']}/100")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# MARKOV TRANSITIONS — group transition graph (v26)
# ═══════════════════════════════════════════════════════════

def build_markov_chain(student, hand='left'):
    """
    Build a Markov transition matrix from student's session history.

    Rows/cols: groups 1-7
    Cell (i,j): P(next group = j | current group = i)

    Also computes:
    - stationary distribution (eigen-approximation)
    - entropy per state
    - most likely path of length k
    """
    # Collect group sequences from all sessions
    sequences = []
    for s in student.sessions:
        ml = s.get('mastery_level', student.mastery_level)
        seed = hash(f"{student.name}_{len(sequences)}") & 0x7FFFFFFF
        dma = DualMatchStickAutomaton(mastery_level=ml, seed=seed)
        kata = dma.generate_dual_kata(length=s.get('length', 4))
        for t in kata:
            if hand == 'left':
                sequences.append(get_group(t[0]))
            else:
                sequences.append(get_group(t[1]))

    if len(sequences) < 2:
        return {'empty': True}

    # Count transitions
    counts = {}
    for i in range(1, 8):
        counts[i] = {j: 0 for j in range(1, 8)}

    for i in range(len(sequences) - 1):
        src, dst = sequences[i], sequences[i + 1]
        if 1 <= src <= 7 and 1 <= dst <= 7:
            counts[src][dst] += 1

    # Normalize to probabilities
    matrix = {}
    for i in range(1, 8):
        total = sum(counts[i].values())
        matrix[i] = {}
        for j in range(1, 8):
            matrix[i][j] = round(counts[i][j] / max(1, total), 3)

    # Stationary distribution (power iteration)
    dist = [1 / 7] * 7
    for _ in range(50):
        new_dist = [0] * 7
        for j in range(7):
            for i in range(7):
                new_dist[j] += dist[i] * matrix[i + 1][j + 1]
        total = sum(new_dist)
        dist = [d / max(total, 1e-10) for d in new_dist]

    stationary = {g + 1: round(dist[g], 3) for g in range(7)}

    # Entropy per state
    import math
    entropy = {}
    for i in range(1, 8):
        h = 0
        for j in range(1, 8):
            p = matrix[i][j]
            if p > 0:
                h -= p * math.log2(p)
        entropy[i] = round(h, 2)

    return {
        'empty': False,
        'matrix': matrix,
        'stationary': stationary,
        'entropy': entropy,
        'n_transitions': len(sequences) - 1,
        'hand': hand,
    }


def format_markov(mc):
    """Format Markov chain as transition matrix."""
    if mc.get('empty'):
        return "Markov: no data"

    lines = [f"Markov Transition Matrix ({mc['hand']} hand, "
             f"n={mc['n_transitions']})"]
    lines.append("─" * 60)

    # Header
    hdr = "  From\\To"
    for j in range(1, 8):
        hdr += f"  G{j:d}  "
    lines.append(hdr)
    lines.append("  " + "─" * 55)

    for i in range(1, 8):
        row = f"  G{i}    "
        for j in range(1, 8):
            p = mc['matrix'][i][j]
            if p >= 0.3:
                row += f" [{p:.2f}]"
            elif p > 0:
                row += f"  {p:.2f} "
            else:
                row += "   ·   "
        lines.append(row)

    # Stationary
    lines.append("")
    lines.append("  Stationary: " +
                 '  '.join(f"G{g}={mc['stationary'][g]:.2f}"
                           for g in range(1, 8)))

    # Entropy
    lines.append("  Entropy:    " +
                 '  '.join(f"G{g}={mc['entropy'][g]:.1f}"
                           for g in range(1, 8)))

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SCORING RUBRIC — detailed grading criteria (v26)
# ═══════════════════════════════════════════════════════════

def build_rubric():
    """
    Define the scoring rubric for kata evaluation.

    5 dimensions × 4 levels (0-3 points each) = max 15 points.

    Dimensions:
    1. Technical accuracy (rule compliance)
    2. Complexity management
    3. Flow & transitions
    4. Group diversity
    5. Structural coherence
    """
    return {
        'technical': {
            'name': 'Technical Accuracy',
            'weight': 3.0,
            'levels': {
                0: 'Fails majority of rules (<40%)',
                1: 'Passes some rules (40-60%)',
                2: 'Passes most rules (60-85%)',
                3: 'Near-perfect rule compliance (>85%)',
            },
        },
        'complexity': {
            'name': 'Complexity Management',
            'weight': 2.0,
            'levels': {
                0: 'Trivial symbols only (mean < 1)',
                1: 'Low variety (mean 1-2)',
                2: 'Moderate range (mean 2-3)',
                3: 'Full spectrum used effectively (mean > 3)',
            },
        },
        'flow': {
            'name': 'Flow & Transitions',
            'weight': 2.5,
            'levels': {
                0: 'Jarring transitions (flow < 40)',
                1: 'Rough flow (flow 40-60)',
                2: 'Smooth flow (flow 60-85)',
                3: 'Seamless transitions (flow > 85)',
            },
        },
        'diversity': {
            'name': 'Group Diversity',
            'weight': 1.5,
            'levels': {
                0: 'Single group (1 unique)',
                1: 'Limited groups (2 unique)',
                2: 'Moderate diversity (3-4 unique)',
                3: 'Rich diversity (5+ unique)',
            },
        },
        'coherence': {
            'name': 'Structural Coherence',
            'weight': 1.0,
            'levels': {
                0: 'Random/no pattern',
                1: 'Weak structure',
                2: 'Clear structure (contour detected)',
                3: 'Strong narrative arc',
            },
        },
    }


def score_with_rubric(kata, rule_pct=None):
    """
    Score a kata using the rubric system.

    Returns per-dimension scores and weighted total.
    """
    rubric = build_rubric()

    # Get analytics
    rhythm = analyze_rhythm(kata)
    fp = compute_fingerprint(kata)

    scores = {}

    # 1. Technical accuracy
    if rule_pct is not None:
        if rule_pct > 85:
            scores['technical'] = 3
        elif rule_pct > 60:
            scores['technical'] = 2
        elif rule_pct > 40:
            scores['technical'] = 1
        else:
            scores['technical'] = 0
    else:
        scores['technical'] = 2  # default if not measured

    # 2. Complexity management
    mean_c = fp['features'].get('complexity_mean', 0)
    if mean_c > 3:
        scores['complexity'] = 3
    elif mean_c > 2:
        scores['complexity'] = 2
    elif mean_c > 1:
        scores['complexity'] = 1
    else:
        scores['complexity'] = 0

    # 3. Flow & transitions
    if not rhythm.get('empty'):
        flow = rhythm['flow_score']
        if flow > 85:
            scores['flow'] = 3
        elif flow > 60:
            scores['flow'] = 2
        elif flow > 40:
            scores['flow'] = 1
        else:
            scores['flow'] = 0
    else:
        scores['flow'] = 1

    # 4. Group diversity
    unique_g = fp['features'].get('unique_groups', 1)
    if unique_g >= 5:
        scores['diversity'] = 3
    elif unique_g >= 3:
        scores['diversity'] = 2
    elif unique_g >= 2:
        scores['diversity'] = 1
    else:
        scores['diversity'] = 0

    # 5. Structural coherence
    if not rhythm.get('empty'):
        contour = rhythm['contour']
        periodicity = rhythm['periodicity']
        if contour in ('ascending', 'descending') and periodicity > 0.5:
            scores['coherence'] = 3
        elif contour != 'short':
            scores['coherence'] = 2
        else:
            scores['coherence'] = 1
    else:
        scores['coherence'] = 1

    # Weighted total
    total_weighted = 0
    max_weighted = 0
    for dim, score in scores.items():
        w = rubric[dim]['weight']
        total_weighted += score * w
        max_weighted += 3 * w

    pct = total_weighted / max_weighted * 100 if max_weighted else 0

    # Letter grade
    if pct >= 90:
        grade = 'A+'
    elif pct >= 80:
        grade = 'A'
    elif pct >= 70:
        grade = 'B'
    elif pct >= 60:
        grade = 'C'
    elif pct >= 50:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'scores': scores,
        'rubric': rubric,
        'total_weighted': round(total_weighted, 1),
        'max_weighted': round(max_weighted, 1),
        'pct': round(pct, 1),
        'grade': grade,
    }


def format_rubric_score(rs):
    """Format rubric score as report card."""
    lines = [f"Rubric Score: {rs['grade']} ({rs['pct']:.1f}%)"]
    lines.append("═" * 50)

    for dim, score in rs['scores'].items():
        r = rs['rubric'][dim]
        bar = '★' * score + '☆' * (3 - score)
        level_desc = r['levels'][score]
        lines.append(f"  {r['name']:<24s} {bar}  w={r['weight']:.1f}")
        lines.append(f"    {level_desc}")

    lines.append("─" * 50)
    lines.append(f"  Weighted: {rs['total_weighted']}/{rs['max_weighted']} "
                 f"= {rs['pct']:.1f}% → {rs['grade']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SVG EXPORT — visual kata diagram (v27)
# ═══════════════════════════════════════════════════════════

# Color palette for groups
GROUP_COLORS = {
    1: '#4CAF50',  # green - empty
    2: '#2196F3',  # blue - single
    3: '#FF9800',  # orange - angle
    4: '#9C27B0',  # purple - parallel
    5: '#F44336',  # red - triple
    6: '#FFD700',  # gold - master
    7: '#00BCD4',  # cyan - peak
}


def kata_to_svg(kata, title='Kata', width=800, height=400):
    """
    Generate SVG visualization of a kata sequence.

    Layout: horizontal timeline with symbol nodes.
    Each tact is a column with L (top) and R (bottom) circles.
    Color = group, size = complexity, connections = transitions.
    """
    n = len(kata)
    if n == 0:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50">' \
               '<text x="10" y="30">Empty kata</text></svg>'

    margin = 60
    col_w = (width - 2 * margin) / max(1, n - 1) if n > 1 else width - 2 * margin
    mid_y = height / 2
    row_gap = 80

    parts = []
    # SVG header
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{width}" height="{height}" '
                 f'viewBox="0 0 {width} {height}">')

    # Background
    parts.append(f'<rect width="{width}" height="{height}" '
                 f'fill="#1a1a2e" rx="10"/>')

    # Title
    parts.append(f'<text x="{width // 2}" y="25" text-anchor="middle" '
                 f'font-family="monospace" font-size="14" '
                 f'fill="#eee">{title}</text>')

    # Timeline axis
    parts.append(f'<line x1="{margin}" y1="{mid_y}" '
                 f'x2="{width - margin}" y2="{mid_y}" '
                 f'stroke="#555" stroke-width="1" stroke-dasharray="4,4"/>')

    # Draw connections first (behind nodes)
    for i in range(1, n):
        x1 = margin + (i - 1) * col_w
        x2 = margin + i * col_w
        # L connections
        parts.append(f'<line x1="{x1:.0f}" y1="{mid_y - row_gap // 2}" '
                     f'x2="{x2:.0f}" y2="{mid_y - row_gap // 2}" '
                     f'stroke="#444" stroke-width="1"/>')
        # R connections
        parts.append(f'<line x1="{x1:.0f}" y1="{mid_y + row_gap // 2}" '
                     f'x2="{x2:.0f}" y2="{mid_y + row_gap // 2}" '
                     f'stroke="#444" stroke-width="1"/>')

    # Draw nodes
    for i, t in enumerate(kata):
        sl, sr = t[0], t[1]
        gl, gr = get_group(sl), get_group(sr)
        cl, cr = symbol_complexity(sl), symbol_complexity(sr)

        x = margin + i * col_w

        # L node (top)
        r_l = 8 + cl * 3
        color_l = GROUP_COLORS.get(gl, '#888')
        parts.append(f'<circle cx="{x:.0f}" cy="{mid_y - row_gap // 2}" '
                     f'r="{r_l}" fill="{color_l}" opacity="0.85"/>')
        parts.append(f'<text x="{x:.0f}" y="{mid_y - row_gap // 2 + 4}" '
                     f'text-anchor="middle" font-family="monospace" '
                     f'font-size="9" fill="#fff">S{sl:02d}</text>')

        # R node (bottom)
        r_r = 8 + cr * 3
        color_r = GROUP_COLORS.get(gr, '#888')
        parts.append(f'<circle cx="{x:.0f}" cy="{mid_y + row_gap // 2}" '
                     f'r="{r_r}" fill="{color_r}" opacity="0.85"/>')
        parts.append(f'<text x="{x:.0f}" y="{mid_y + row_gap // 2 + 4}" '
                     f'text-anchor="middle" font-family="monospace" '
                     f'font-size="9" fill="#fff">S{sr:02d}</text>')

        # Tact label
        parts.append(f'<text x="{x:.0f}" y="{height - 15}" '
                     f'text-anchor="middle" font-family="monospace" '
                     f'font-size="10" fill="#888">T{i + 1}</text>')

    # Labels
    parts.append(f'<text x="{margin - 30}" y="{mid_y - row_gap // 2 + 4}" '
                 f'font-family="monospace" font-size="11" fill="#aaa">L</text>')
    parts.append(f'<text x="{margin - 30}" y="{mid_y + row_gap // 2 + 4}" '
                 f'font-family="monospace" font-size="11" fill="#aaa">R</text>')

    # Legend
    ly = height - 40
    lx = margin
    for g in range(1, 8):
        color = GROUP_COLORS[g]
        parts.append(f'<rect x="{lx}" y="{ly}" width="10" height="10" '
                     f'fill="{color}" rx="2"/>')
        parts.append(f'<text x="{lx + 14}" y="{ly + 9}" '
                     f'font-family="monospace" font-size="8" '
                     f'fill="#aaa">G{g}</text>')
        lx += 45

    parts.append('</svg>')
    return '\n'.join(parts)


# ═══════════════════════════════════════════════════════════
# SKILL TREE — progression map (v27)
# ═══════════════════════════════════════════════════════════

def build_skill_tree(student):
    """
    Build a skill tree showing mastery progression.

    Tree structure:
    L1 Foundation → L2 Basic → L3 Intermediate →
    L4 Advanced → L5 Expert → L6 Master → L7 Peak

    Each node has:
    - requirements (min score, sessions)
    - unlocked skills
    - completion status
    """
    ml = student.mastery_level
    n_sessions = len(student.sessions)

    tree = []
    skill_defs = {
        1: {
            'name': 'Foundation',
            'skills': ['Basic symbols', 'Single-hand kata', 'Group 1-2'],
            'req_sessions': 0, 'req_score': 0,
        },
        2: {
            'name': 'Basic',
            'skills': ['Dual-hand kata', 'Rule R1 (Zone)', 'Group 3'],
            'req_sessions': 3, 'req_score': 50,
        },
        3: {
            'name': 'Intermediate',
            'skills': ['All 5 rules', 'Mutations', 'Group 4-5'],
            'req_sessions': 8, 'req_score': 60,
        },
        4: {
            'name': 'Advanced',
            'skills': ['Sparring', 'Tournaments', 'Fingerprinting'],
            'req_sessions': 15, 'req_score': 70,
        },
        5: {
            'name': 'Expert',
            'skills': ['Markov analysis', 'Training plans', 'Group 6'],
            'req_sessions': 25, 'req_score': 75,
        },
        6: {
            'name': 'Master',
            'skills': ['Federation', 'Curriculum design', 'Full rubric'],
            'req_sessions': 40, 'req_score': 80,
        },
        7: {
            'name': 'Peak',
            'skills': ['All symbols', 'Research mode', 'Peer review'],
            'req_sessions': 60, 'req_score': 85,
        },
    }

    # Compute recent score
    recent_scores = [s['pct'] for s in student.sessions[-5:]]
    recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0

    for level in range(1, 8):
        sd = skill_defs[level]
        if level <= ml:
            status = 'completed'
            progress = 100
        elif level == ml + 1:
            status = 'current'
            # Progress toward next level
            score_prog = min(100, recent_avg / max(1, sd['req_score']) * 100)
            session_prog = min(100, n_sessions / max(1, sd['req_sessions']) * 100)
            progress = round((score_prog + session_prog) / 2)
        else:
            status = 'locked'
            progress = 0

        tree.append({
            'level': level,
            'name': sd['name'],
            'skills': sd['skills'],
            'req_sessions': sd['req_sessions'],
            'req_score': sd['req_score'],
            'status': status,
            'progress': progress,
        })

    return {
        'student': student.name,
        'current_level': ml,
        'n_sessions': n_sessions,
        'recent_avg': round(recent_avg, 1),
        'tree': tree,
    }


def format_skill_tree(st):
    """Format skill tree as ASCII visualization."""
    lines = [f"Skill Tree: {st['student']} "
             f"(L{st['current_level']}, {st['n_sessions']} sessions)"]
    lines.append("═" * 55)

    for node in st['tree']:
        lvl = node['level']
        name = node['name']
        status = node['status']

        if status == 'completed':
            icon = '◉'
            bar = '████████████████████'
            pct_str = '100%'
        elif status == 'current':
            icon = '◎'
            filled = node['progress'] // 5
            bar = '█' * filled + '░' * (20 - filled)
            pct_str = f"{node['progress']}%"
        else:
            icon = '○'
            bar = '░' * 20
            pct_str = 'locked'

        lines.append(f"  {icon} L{lvl} {name:<13s} [{bar}] {pct_str}")

        # Show skills
        for skill in node['skills']:
            if status == 'completed':
                lines.append(f"      ✓ {skill}")
            elif status == 'current':
                lines.append(f"      ▸ {skill}")
            else:
                lines.append(f"      · {skill}")

        # Connector
        if lvl < 7:
            lines.append("      │")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# BATCH PROCESSOR — multi-student evaluation (v27)
# ═══════════════════════════════════════════════════════════

def batch_evaluate(school, evaluation_fn=None):
    """
    Run batch evaluation across all students in a school.

    Default evaluation: diagnostic report for each student.
    Custom evaluation_fn(student) → dict with results.

    Returns aggregated results with rankings.
    """
    if evaluation_fn is None:
        evaluation_fn = generate_diagnostic

    results = {}
    for name, student in school.students.items():
        try:
            results[name] = evaluation_fn(student)
        except Exception as e:
            results[name] = {'error': str(e)}

    return results


def batch_rank(school, metric='recent_avg'):
    """
    Rank all students by a given metric.

    Metrics: 'recent_avg', 'mastery', 'sessions', 'improvement', 'elo'
    """
    rankings = []

    for name, student in school.students.items():
        sessions = student.sessions
        scores = [s['pct'] for s in sessions]
        recent = scores[-5:] if scores else []

        entry = {
            'name': name,
            'mastery': student.mastery_level,
            'sessions': len(sessions),
            'avg': round(sum(scores) / len(scores), 1) if scores else 0,
            'recent_avg': round(sum(recent) / len(recent), 1) if recent else 0,
            'best': round(max(scores), 1) if scores else 0,
            'elo': getattr(student, 'elo', 1200),
            'improvement': 0,
        }

        # Improvement: recent_avg - first 5 avg
        if len(scores) >= 5:
            first5 = sum(scores[:5]) / 5
            entry['improvement'] = round(entry['recent_avg'] - first5, 1)

        rankings.append(entry)

    # Sort by metric
    reverse = True
    rankings.sort(key=lambda r: r.get(metric, 0), reverse=reverse)

    # Add rank
    for i, r in enumerate(rankings):
        r['rank'] = i + 1

    return rankings


def format_batch_ranking(rankings, metric='recent_avg'):
    """Format batch rankings as leaderboard."""
    lines = [f"Leaderboard (by {metric})"]
    lines.append("═" * 60)
    lines.append(f"  {'#':>3s} {'Name':<12s} {'ML':>3s} {'Sess':>5s} "
                 f"{'Avg':>6s} {'Recent':>7s} {'Best':>6s} {'ELO':>6s}")
    lines.append("  " + "─" * 55)

    medals = {1: '🥇', 2: '🥈', 3: '🥉'}

    for r in rankings:
        medal = medals.get(r['rank'], '  ')
        lines.append(
            f"  {medal}{r['rank']:1d} {r['name']:<12s} "
            f"L{r['mastery']:1d}  {r['sessions']:4d}  "
            f"{r['avg']:5.1f}%  {r['recent_avg']:5.1f}%  "
            f"{r['best']:5.1f}%  {r['elo']:6.0f}")

    return '\n'.join(lines)


def batch_summary(school):
    """Generate aggregate summary statistics for the school."""
    students = list(school.students.values())
    if not students:
        return {'empty': True}

    all_sessions = sum(len(s.sessions) for s in students)
    all_scores = []
    for s in students:
        all_scores.extend(s_['pct'] for s_ in s.sessions)

    ml_dist = {}
    for s in students:
        ml = s.mastery_level
        ml_dist[ml] = ml_dist.get(ml, 0) + 1

    return {
        'empty': False,
        'n_students': len(students),
        'total_sessions': all_sessions,
        'avg_sessions_per_student': round(all_sessions / len(students), 1),
        'school_avg': round(sum(all_scores) / len(all_scores), 1)
                      if all_scores else 0,
        'school_best': round(max(all_scores), 1) if all_scores else 0,
        'mastery_distribution': ml_dist,
    }


def format_batch_summary(bs):
    """Format batch summary."""
    if bs.get('empty'):
        return "School: no students"

    lines = ["School Summary"]
    lines.append("─" * 40)
    lines.append(f"  Students: {bs['n_students']}")
    lines.append(f"  Total sessions: {bs['total_sessions']}")
    lines.append(f"  Avg sessions/student: {bs['avg_sessions_per_student']}")
    lines.append(f"  School avg score: {bs['school_avg']}%")
    lines.append(f"  School best: {bs['school_best']}%")
    lines.append(f"  Mastery levels: {bs['mastery_distribution']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# KATA DIFF ENGINE — compare two katas (v28)
# ═══════════════════════════════════════════════════════════

def kata_diff(kata_a, kata_b, label_a='A', label_b='B'):
    """
    Compare two katas tact-by-tact.

    Returns:
    - identical: list of tact indices where both match
    - changed: list of {idx, a, b, delta_complexity, delta_group}
    - only_a: tacts only in kata_a (when lengths differ)
    - only_b: tacts only in kata_b
    - similarity: 0..100 percentage
    """
    len_a, len_b = len(kata_a), len(kata_b)
    common = min(len_a, len_b)

    identical = []
    changed = []

    for i in range(common):
        ta, tb = kata_a[i], kata_b[i]
        if ta[0] == tb[0] and ta[1] == tb[1]:
            identical.append(i)
        else:
            ca = symbol_complexity(ta[0]) + symbol_complexity(ta[1])
            cb = symbol_complexity(tb[0]) + symbol_complexity(tb[1])
            ga = (get_group(ta[0]), get_group(ta[1]))
            gb = (get_group(tb[0]), get_group(tb[1]))
            changed.append({
                'idx': i,
                'a': ta, 'b': tb,
                'delta_complexity': cb - ca,
                'group_shift': (gb[0] - ga[0], gb[1] - ga[1]),
            })

    only_a = list(range(common, len_a))
    only_b = list(range(common, len_b))

    max_len = max(len_a, len_b)
    similarity = round(len(identical) / max_len * 100, 1) if max_len else 100

    return {
        'label_a': label_a, 'label_b': label_b,
        'len_a': len_a, 'len_b': len_b,
        'identical': identical,
        'changed': changed,
        'only_a': only_a,
        'only_b': only_b,
        'similarity': similarity,
    }


def format_kata_diff(diff):
    """Format kata diff as a readable report."""
    lines = [f"Kata Diff: {diff['label_a']} ({diff['len_a']}T) vs "
             f"{diff['label_b']} ({diff['len_b']}T)"]
    lines.append("═" * 55)
    lines.append(f"  Similarity: {diff['similarity']}%")
    lines.append(f"  Identical tacts: {len(diff['identical'])}")
    lines.append(f"  Changed tacts:   {len(diff['changed'])}")

    if diff['only_a']:
        lines.append(f"  Only in {diff['label_a']}: tacts {diff['only_a']}")
    if diff['only_b']:
        lines.append(f"  Only in {diff['label_b']}: tacts {diff['only_b']}")

    if diff['changed']:
        lines.append("")
        lines.append("  Changes:")
        for c in diff['changed'][:10]:
            idx = c['idx']
            a_l, a_r = c['a'][0], c['a'][1]
            b_l, b_r = c['b'][0], c['b'][1]
            dc = c['delta_complexity']
            sign = '+' if dc > 0 else '' if dc == 0 else ''
            lines.append(f"    T{idx + 1}: "
                         f"({a_l:02d},{a_r:02d}) → ({b_l:02d},{b_r:02d}) "
                         f"Δcplx={sign}{dc}")
        if len(diff['changed']) > 10:
            lines.append(f"    ... and {len(diff['changed']) - 10} more")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ACHIEVEMENT BADGES — gamification system (v28)
# ═══════════════════════════════════════════════════════════

# Badge definitions: id → {name, icon, description, check_fn_key}
BADGE_DEFS = {
    'first_session':     {'name': 'First Steps',     'icon': '🐣',
                          'desc': 'Complete your first session'},
    'ten_sessions':      {'name': 'Dedicated',        'icon': '🔟',
                          'desc': 'Complete 10 sessions'},
    'fifty_sessions':    {'name': 'Veteran',           'icon': '🎖️',
                          'desc': 'Complete 50 sessions'},
    'perfect_score':     {'name': 'Perfectionist',     'icon': '💯',
                          'desc': 'Score 100% on any session'},
    'score_90':          {'name': 'Excellent',          'icon': '⭐',
                          'desc': 'Score 90%+ on any session'},
    'streak_5':          {'name': 'Hot Streak',         'icon': '🔥',
                          'desc': '5 consecutive sessions above 70%'},
    'all_groups':        {'name': 'Explorer',           'icon': '🗺️',
                          'desc': 'Encounter all 7 symbol groups'},
    'mastery_3':         {'name': 'Intermediate',       'icon': '🥉',
                          'desc': 'Reach mastery level 3'},
    'mastery_5':         {'name': 'Expert',             'icon': '🥇',
                          'desc': 'Reach mastery level 5'},
    'mastery_7':         {'name': 'Grandmaster',        'icon': '👑',
                          'desc': 'Reach mastery level 7'},
    'improvement_20':    {'name': 'Growth Spurt',       'icon': '📈',
                          'desc': 'Improve avg by 20+ points'},
    'tournament_win':    {'name': 'Champion',           'icon': '🏆',
                          'desc': 'Win a tournament'},
}


def check_badges(student):
    """
    Check which badges a student has earned.
    Returns list of earned badge ids with timestamps.
    """
    earned = []
    sessions = student.sessions
    scores = [s['pct'] for s in sessions]
    n = len(sessions)

    # Session count badges
    if n >= 1:
        earned.append('first_session')
    if n >= 10:
        earned.append('ten_sessions')
    if n >= 50:
        earned.append('fifty_sessions')

    # Score badges
    if scores:
        if max(scores) >= 100:
            earned.append('perfect_score')
        if max(scores) >= 90:
            earned.append('score_90')

    # Streak: 5 consecutive ≥ 70%
    if n >= 5:
        for i in range(n - 4):
            window = scores[i:i + 5]
            if all(s >= 70 for s in window):
                earned.append('streak_5')
                break

    # All groups encountered
    groups_seen = set()
    for s in sessions:
        kata = s.get('kata', [])
        for t in kata:
            if len(t) >= 2:
                groups_seen.add(get_group(t[0]))
                groups_seen.add(get_group(t[1]))
    if len(groups_seen) >= 7:
        earned.append('all_groups')

    # Mastery badges
    ml = student.mastery_level
    if ml >= 3:
        earned.append('mastery_3')
    if ml >= 5:
        earned.append('mastery_5')
    if ml >= 7:
        earned.append('mastery_7')

    # Improvement badge
    if n >= 10:
        first5 = sum(scores[:5]) / 5
        last5 = sum(scores[-5:]) / 5
        if last5 - first5 >= 20:
            earned.append('improvement_20')

    # Tournament badge (check history)
    if hasattr(student, 'tournament_wins') and student.tournament_wins > 0:
        earned.append('tournament_win')

    return earned


def format_badges(earned_ids):
    """Format earned badges as a display card."""
    lines = [f"Badges Earned: {len(earned_ids)}/{len(BADGE_DEFS)}"]
    lines.append("─" * 40)

    for bid in earned_ids:
        bd = BADGE_DEFS.get(bid, {})
        lines.append(f"  {bd.get('icon', '?')} {bd.get('name', bid)}: "
                     f"{bd.get('desc', '')}")

    # Show locked badges
    locked = [b for b in BADGE_DEFS if b not in earned_ids]
    if locked:
        lines.append("")
        lines.append("  Locked:")
        for bid in locked:
            bd = BADGE_DEFS[bid]
            lines.append(f"  🔒 {bd['name']}: {bd['desc']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ANNOTATED REPLAY — session replay with commentary (v28)
# ═══════════════════════════════════════════════════════════

def annotate_session(session):
    """
    Build an annotated replay of a session.

    Adds commentary to each tact based on:
    - Rule violations
    - Group transitions
    - Complexity jumps
    - Streaks (good/bad)
    """
    kata = session.get('kata', [])
    violations = session.get('violations', [])
    n = len(kata)

    # Index violations by tact
    viol_map = {}
    for v in violations:
        idx = v.get('tact', -1)
        viol_map.setdefault(idx, []).append(v)

    annotations = []
    streak_good = 0
    streak_bad = 0
    prev_cplx = None

    for i, t in enumerate(kata):
        sl, sr = t[0], t[1]
        gl, gr = get_group(sl), get_group(sr)
        cplx = symbol_complexity(sl) + symbol_complexity(sr)

        notes = []

        # Check violations at this tact
        tviol = viol_map.get(i, [])
        for v in tviol:
            notes.append(f"⚠ {v.get('rule', '?')}: {v.get('msg', 'violation')}")

        # Complexity jump
        if prev_cplx is not None:
            delta = cplx - prev_cplx
            if delta >= 4:
                notes.append(f"↑ Complexity spike (+{delta})")
            elif delta <= -4:
                notes.append(f"↓ Complexity drop ({delta})")

        # Group transitions
        if i > 0:
            prev_t = kata[i - 1]
            pg_l, pg_r = get_group(prev_t[0]), get_group(prev_t[1])
            if gl != pg_l and gr != pg_r:
                notes.append(f"↔ Double group shift: "
                             f"({pg_l},{pg_r})→({gl},{gr})")
            elif gl != pg_l:
                notes.append(f"↔ L group shift: G{pg_l}→G{gl}")
            elif gr != pg_r:
                notes.append(f"↔ R group shift: G{pg_r}→G{gr}")

        # Streak tracking
        if not tviol:
            streak_good += 1
            streak_bad = 0
            if streak_good == 5:
                notes.append("🔥 5-tact clean streak!")
            elif streak_good == 10:
                notes.append("🔥🔥 10-tact clean streak!")
        else:
            streak_bad += 1
            streak_good = 0
            if streak_bad == 3:
                notes.append("⛔ 3 consecutive violations")

        annotations.append({
            'tact': i + 1,
            'L': sl, 'R': sr,
            'group_L': gl, 'group_R': gr,
            'complexity': cplx,
            'violations': len(tviol),
            'notes': notes,
        })

        prev_cplx = cplx

    return annotations


def format_annotated_replay(annotations, max_tacts=None):
    """Format annotated replay as timeline."""
    lines = [f"Annotated Replay ({len(annotations)} tacts)"]
    lines.append("═" * 55)

    display = annotations[:max_tacts] if max_tacts else annotations

    for a in display:
        viol_icon = '✗' if a['violations'] else '✓'
        line = (f"  T{a['tact']:02d} {viol_icon} "
                f"L=S{a['L']:02d}(G{a['group_L']}) "
                f"R=S{a['R']:02d}(G{a['group_R']}) "
                f"cplx={a['complexity']}")
        lines.append(line)

        for note in a['notes']:
            lines.append(f"        {note}")

    if max_tacts and len(annotations) > max_tacts:
        lines.append(f"  ... +{len(annotations) - max_tacts} more tacts")

    # Summary
    total_v = sum(a['violations'] for a in annotations)
    noted = sum(1 for a in annotations if a['notes'])
    lines.append("")
    lines.append(f"  Total violations: {total_v}, "
                 f"Annotated tacts: {noted}/{len(annotations)}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# DATA EXPORT / IMPORT — JSON & CSV (v29)
# ═══════════════════════════════════════════════════════════

def export_student_json(student):
    """
    Export student data to a JSON-serializable dict.

    Includes: profile, sessions, mastery, badges, stats.
    """
    sessions = student.sessions
    scores = [s['pct'] for s in sessions]
    recent = scores[-5:] if scores else []

    return {
        'format': 'scarab_student_v1',
        'name': student.name,
        'mastery_level': student.mastery_level,
        'elo': getattr(student, 'elo', 1200),
        'n_sessions': len(sessions),
        'avg_score': round(sum(scores) / len(scores), 2) if scores else 0,
        'recent_avg': round(sum(recent) / len(recent), 2) if recent else 0,
        'best_score': round(max(scores), 2) if scores else 0,
        'badges': check_badges(student),
        'sessions': [
            {
                'idx': i,
                'length': s.get('length', 0),
                'total': s.get('total', 0),
                'pct': round(s.get('pct', 0), 2),
                'violations': len(s.get('violations', [])),
            }
            for i, s in enumerate(sessions)
        ],
    }


def import_student_json(data, school=None):
    """
    Import student from JSON dict.

    If school is given, register the student.
    Returns the student object.
    """
    if data.get('format') != 'scarab_student_v1':
        raise ValueError("Unknown format: " + str(data.get('format')))

    name = data['name']
    ml = data.get('mastery_level', 1)

    if school:
        school.add_student(name, mastery_level=ml)
        student = school.students[name]
    else:
        student = StudentTracker(name, mastery_level=ml)

    student.elo = data.get('elo', 1200)

    # Rebuild sessions from exported data
    for sd in data.get('sessions', []):
        student.sessions.append({
            'length': sd.get('length', 0),
            'total': sd.get('total', 0),
            'pct': sd.get('pct', 0),
            'violations': [{}] * sd.get('violations', 0),
        })

    return student


def export_school_v2(school):
    """Export entire school to JSON-serializable dict (v29 format)."""
    return {
        'format': 'scarab_school_v1',
        'school_name': school.name,
        'n_students': len(school.students),
        'students': {
            name: export_student_json(s)
            for name, s in school.students.items()
        },
    }


def export_sessions_csv(student):
    """
    Export student sessions as CSV string.

    Columns: session_idx, length, total, pct, violations
    """
    lines = ['session_idx,length,total,pct,violations']
    for i, s in enumerate(student.sessions):
        length = s.get('length', 0)
        total = s.get('total', 0)
        pct = round(s.get('pct', 0), 2)
        viols = len(s.get('violations', []))
        lines.append(f'{i},{length},{total},{pct},{viols}')
    return '\n'.join(lines)


def export_rankings_csv(school, metric='recent_avg'):
    """Export school rankings as CSV string."""
    rankings = batch_rank(school, metric=metric)
    lines = ['rank,name,mastery,sessions,avg,recent_avg,best,elo,improvement']
    for r in rankings:
        lines.append(
            f"{r['rank']},{r['name']},{r['mastery']},{r['sessions']},"
            f"{r['avg']},{r['recent_avg']},{r['best']},"
            f"{r['elo']},{r['improvement']}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# NOTIFICATION SYSTEM — event-based alerts (v29)
# ═══════════════════════════════════════════════════════════

class NotificationManager:
    """
    Event-based notification system.

    Watches for events and generates notifications:
    - milestone: badge earned, level up, session count
    - alert: score drop, streak broken, inactivity
    - info: session complete, ranking change
    """

    def __init__(self):
        self.notifications = []
        self._handlers = {}

    def register_handler(self, event_type, handler_fn):
        """Register a callback for an event type."""
        self._handlers.setdefault(event_type, []).append(handler_fn)

    def notify(self, event_type, message, severity='info', data=None):
        """Create a notification."""
        notif = {
            'type': event_type,
            'severity': severity,
            'message': message,
            'data': data or {},
            'read': False,
        }
        self.notifications.append(notif)

        # Trigger handlers
        for fn in self._handlers.get(event_type, []):
            fn(notif)

        return notif

    def check_student_events(self, student):
        """
        Check student state and generate relevant notifications.
        """
        generated = []
        sessions = student.sessions
        scores = [s['pct'] for s in sessions]
        n = len(sessions)

        # Session milestones
        for milestone in [1, 5, 10, 25, 50, 100]:
            if n == milestone:
                generated.append(self.notify(
                    'milestone',
                    f"{student.name} completed {milestone} sessions!",
                    severity='success',
                    data={'milestone': milestone}))

        # Level up detection (compare mastery to what sessions suggest)
        ml = student.mastery_level
        if ml >= 3 and n >= 2:
            # Check if recent level is higher than earlier implied level
            generated.append(self.notify(
                'info',
                f"{student.name} is at mastery level {ml}",
                data={'mastery': ml}))

        # Score drop alert
        if n >= 6:
            prev3 = sum(scores[-6:-3]) / 3
            last3 = sum(scores[-3:]) / 3
            if last3 < prev3 - 15:
                generated.append(self.notify(
                    'alert',
                    f"{student.name}: score dropped by "
                    f"{round(prev3 - last3, 1)} points",
                    severity='warning',
                    data={'drop': round(prev3 - last3, 1)}))

        # High score celebration
        if scores and max(scores) == scores[-1] and n > 1:
            generated.append(self.notify(
                'milestone',
                f"{student.name} set a new personal best: "
                f"{round(scores[-1], 1)}%!",
                severity='success',
                data={'score': round(scores[-1], 1)}))

        # Badge check
        badges = check_badges(student)
        if len(badges) >= 5:
            generated.append(self.notify(
                'info',
                f"{student.name} has earned {len(badges)} badges",
                data={'badge_count': len(badges)}))

        return generated

    def unread(self):
        """Get unread notifications."""
        return [n for n in self.notifications if not n['read']]

    def mark_all_read(self):
        """Mark all as read."""
        for n in self.notifications:
            n['read'] = True

    def format_notifications(self, only_unread=False):
        """Format notifications for display."""
        items = self.unread() if only_unread else self.notifications
        if not items:
            return "No notifications."

        icons = {
            'success': '✅', 'warning': '⚠️',
            'info': 'ℹ️', 'error': '❌',
        }
        type_icons = {
            'milestone': '🏅', 'alert': '🔔', 'info': '📋',
        }

        lines = [f"Notifications ({len(items)})"]
        lines.append("─" * 45)
        for n in items:
            sev_icon = icons.get(n['severity'], '•')
            typ_icon = type_icons.get(n['type'], '•')
            read_mark = ' ' if n['read'] else '●'
            lines.append(f"  {read_mark} {typ_icon}{sev_icon} {n['message']}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# REPORT GENERATOR — structured reports (v29)
# ═══════════════════════════════════════════════════════════

def generate_full_report(student, school=None):
    """
    Generate a comprehensive report for a student.

    Sections:
    1. Profile summary
    2. Session history
    3. Skill tree
    4. Badges
    5. Diagnostic
    6. Ranking (if school provided)

    Returns structured dict suitable for rendering to text/HTML/PDF.
    """
    sessions = student.sessions
    scores = [s['pct'] for s in sessions]
    recent = scores[-5:] if scores else []

    # 1. Profile
    profile = {
        'name': student.name,
        'mastery_level': student.mastery_level,
        'elo': getattr(student, 'elo', 1200),
        'total_sessions': len(sessions),
        'avg_score': round(sum(scores) / len(scores), 1) if scores else 0,
        'recent_avg': round(sum(recent) / len(recent), 1) if recent else 0,
        'best_score': round(max(scores), 1) if scores else 0,
        'worst_score': round(min(scores), 1) if scores else 0,
    }

    # 2. Session history (last 10)
    history = []
    for i, s in enumerate(sessions[-10:]):
        idx = len(sessions) - 10 + i if len(sessions) >= 10 else i
        history.append({
            'session': idx + 1,
            'pct': round(s['pct'], 1),
            'violations': len(s.get('violations', [])),
        })

    # 3. Skill tree
    skill_tree = build_skill_tree(student)

    # 4. Badges
    badges = check_badges(student)
    badge_details = []
    for bid in badges:
        bd = BADGE_DEFS.get(bid, {})
        badge_details.append({
            'id': bid,
            'name': bd.get('name', bid),
            'icon': bd.get('icon', '?'),
        })

    # 5. Diagnostic
    diagnostic = generate_diagnostic(student)

    # 6. Ranking
    ranking_info = None
    if school:
        rankings = batch_rank(school, metric='recent_avg')
        for r in rankings:
            if r['name'] == student.name:
                ranking_info = r
                break

    return {
        'title': f'Student Report: {student.name}',
        'profile': profile,
        'history': history,
        'skill_tree': skill_tree,
        'badges': badge_details,
        'badges_total': len(BADGE_DEFS),
        'diagnostic': diagnostic,
        'ranking': ranking_info,
    }


def format_full_report(report):
    """Format full report as text."""
    lines = []
    lines.append("╔" + "═" * 56 + "╗")
    lines.append("║" + f"  {report['title']:^52s}" + "  ║")
    lines.append("╚" + "═" * 56 + "╝")

    # Profile
    p = report['profile']
    lines.append("")
    lines.append("  PROFILE")
    lines.append("  " + "─" * 40)
    lines.append(f"  Name:     {p['name']}")
    lines.append(f"  Mastery:  L{p['mastery_level']}  |  ELO: {p['elo']}")
    lines.append(f"  Sessions: {p['total_sessions']}")
    lines.append(f"  Avg:      {p['avg_score']}%  |  Recent: {p['recent_avg']}%")
    lines.append(f"  Best:     {p['best_score']}%  |  Worst:  {p['worst_score']}%")

    # History
    lines.append("")
    lines.append("  SESSION HISTORY (last 10)")
    lines.append("  " + "─" * 40)
    for h in report['history']:
        bar_len = int(h['pct'] / 5)
        bar = '█' * bar_len + '░' * (20 - bar_len)
        viol_str = '✓' if h['violations'] == 0 else str(h['violations']) + 'v'
        lines.append(f"  S{h['session']:02d} [{bar}] {h['pct']:5.1f}% "
                     f"({viol_str})")

    # Badges
    lines.append("")
    bd = report['badges']
    lines.append(f"  BADGES ({len(bd)}/{report['badges_total']})")
    lines.append("  " + "─" * 40)
    badge_line = "  "
    for b in bd:
        badge_line += f"{b['icon']} "
    lines.append(badge_line if bd else "  (none yet)")

    # Skill tree summary
    lines.append("")
    lines.append("  SKILL TREE")
    lines.append("  " + "─" * 40)
    st = report['skill_tree']
    for node in st['tree']:
        if node['status'] == 'completed':
            lines.append(f"  ◉ L{node['level']} {node['name']}")
        elif node['status'] == 'current':
            lines.append(f"  ◎ L{node['level']} {node['name']} "
                         f"[{node['progress']}%]")
        else:
            lines.append(f"  ○ L{node['level']} {node['name']}")

    # Ranking
    if report['ranking']:
        r = report['ranking']
        lines.append("")
        lines.append("  RANKING")
        lines.append("  " + "─" * 40)
        lines.append(f"  Position: #{r['rank']}  |  "
                     f"Recent: {r['recent_avg']}%  |  "
                     f"ELO: {r['elo']}")

    lines.append("")
    lines.append("  " + "═" * 40)
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# TRAINING SCHEDULER / CALENDAR (v30)
# ═══════════════════════════════════════════════════════════

class TrainingScheduler:
    """
    Plans and tracks training sessions over a weekly calendar.

    Features:
    - Weekly schedule with configurable slots
    - Adaptive difficulty based on recent performance
    - Rest-day detection to prevent burnout
    - Focus area recommendations
    """

    WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    def __init__(self, student, sessions_per_week=4):
        self.student = student
        self.sessions_per_week = min(max(sessions_per_week, 1), 7)
        self.schedule = {}   # day_index → slot info
        self.history = []    # completed schedule entries
        self._build_default_schedule()

    def _build_default_schedule(self):
        """Spread sessions across the week evenly."""
        n = self.sessions_per_week
        if n >= 7:
            days = list(range(7))
        else:
            step = 7 / n
            days = [int(i * step) for i in range(n)]
        for d in days:
            self.schedule[d] = {
                'day': self.WEEKDAYS[d],
                'type': 'training',
                'focus': None,
                'difficulty': None,
            }

    def recommend_focus(self):
        """
        Recommend focus areas based on student weaknesses.

        Analyzes recent violations and diagnostic to find weak spots.
        """
        sessions = self.student.sessions
        if not sessions:
            return 'general'

        # Count violation types from recent sessions
        violation_counts = {}
        for s in sessions[-5:]:
            for v in s.get('violations', []):
                rule = v.get('rule', 'unknown')
                violation_counts[rule] = violation_counts.get(rule, 0) + 1

        if violation_counts:
            worst = max(violation_counts, key=violation_counts.get)
            focus_map = {
                'R1_Zone': 'zone_accuracy',
                'R2_Group': 'group_transitions',
                'R3_Length': 'sequence_length',
                'R4_Repeat': 'variation',
                'R5_Edge': 'edge_cases',
            }
            return focus_map.get(worst, 'general')

        return 'consolidation'

    def recommend_difficulty(self):
        """Recommend difficulty based on recent scores."""
        scores = [s['pct'] for s in self.student.sessions]
        if not scores:
            return 'easy'
        recent = scores[-3:] if len(scores) >= 3 else scores
        avg = sum(recent) / len(recent)
        if avg >= 85:
            return 'hard'
        elif avg >= 65:
            return 'medium'
        return 'easy'

    def generate_week(self, week_number=1):
        """Generate a full week plan with auto-filled focus and difficulty."""
        focus = self.recommend_focus()
        diff = self.recommend_difficulty()

        week = []
        for d in range(7):
            if d in self.schedule:
                slot = dict(self.schedule[d])
                slot['week'] = week_number
                slot['focus'] = slot['focus'] or focus
                slot['difficulty'] = slot['difficulty'] or diff
                slot['status'] = 'planned'
                week.append(slot)
            else:
                week.append({
                    'day': self.WEEKDAYS[d],
                    'week': week_number,
                    'type': 'rest',
                    'status': 'rest',
                })
        return week

    def complete_day(self, week_plan, day_index, score=None):
        """Mark a day as completed."""
        if 0 <= day_index < len(week_plan):
            entry = week_plan[day_index]
            if entry['type'] == 'training':
                entry['status'] = 'completed'
                entry['score'] = score
                self.history.append(entry)
        return week_plan

    def format_week(self, week_plan):
        """Format week plan as text."""
        lines = ["Training Schedule"]
        lines.append("─" * 50)

        icons = {
            'planned': '○', 'completed': '●',
            'rest': '·', 'skipped': '✕',
        }
        for entry in week_plan:
            icon = icons.get(entry['status'], '?')
            day = entry['day']
            if entry['type'] == 'rest':
                lines.append(f"  {icon} {day:3s}  — rest day")
            else:
                focus = entry.get('focus', '?')
                diff = entry.get('difficulty', '?')
                score_str = ''
                if entry['status'] == 'completed' and entry.get('score') is not None:
                    score_str = f"  → {entry['score']}%"
                lines.append(f"  {icon} {day:3s}  [{diff:6s}] {focus}{score_str}")

        completed = sum(1 for e in week_plan if e['status'] == 'completed')
        total = sum(1 for e in week_plan if e['type'] == 'training')
        lines.append("─" * 50)
        lines.append(f"  Progress: {completed}/{total} sessions")
        return '\n'.join(lines)

    def adherence_rate(self):
        """Calculate schedule adherence %."""
        if not self.history:
            return 0.0
        completed = len(self.history)
        # Expected based on weeks tracked
        weeks = max(1, completed // max(self.sessions_per_week, 1))
        expected = weeks * self.sessions_per_week
        return round(min(completed / max(expected, 1), 1.0) * 100, 1)


# ═══════════════════════════════════════════════════════════
# ANALYTICS DASHBOARD (v30)
# ═══════════════════════════════════════════════════════════

def compute_analytics(student, window=10):
    """
    Compute comprehensive analytics for a student.

    Returns dict with:
    - trend: direction and slope of recent scores
    - consistency: stddev and coefficient of variation
    - streaks: current and best winning/losing streaks
    - pace: sessions per unit time approximation
    - zone_breakdown: distribution across score zones
    """
    sessions = student.sessions
    scores = [s['pct'] for s in sessions]
    n = len(scores)

    if n == 0:
        return {
            'trend': {'direction': 'none', 'slope': 0},
            'consistency': {'stddev': 0, 'cv': 0},
            'streaks': {'current': 0, 'best': 0, 'type': 'none'},
            'pace': 0,
            'zone_breakdown': {},
        }

    # Trend via linear regression (simple OLS on last window)
    w = min(window, n)
    recent = scores[-w:]
    x_mean = (w - 1) / 2
    y_mean = sum(recent) / w
    num = sum((i - x_mean) * (recent[i] - y_mean) for i in range(w))
    den = sum((i - x_mean) ** 2 for i in range(w))
    slope = round(num / den, 3) if den > 0 else 0
    direction = 'improving' if slope > 0.5 else ('declining' if slope < -0.5 else 'stable')

    # Consistency
    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / n
    stddev = round(variance ** 0.5, 2)
    cv = round(stddev / mean * 100, 1) if mean > 0 else 0

    # Streaks (>70% = win)
    threshold = 70
    current_streak = 0
    best_streak = 0
    streak_type = 'none'
    for s in reversed(scores):
        if current_streak == 0:
            streak_type = 'win' if s >= threshold else 'loss'
            current_streak = 1
        elif (s >= threshold and streak_type == 'win') or \
             (s < threshold and streak_type == 'loss'):
            current_streak += 1
        else:
            break
    # Best winning streak
    run = 0
    for s in scores:
        if s >= threshold:
            run += 1
            best_streak = max(best_streak, run)
        else:
            run = 0

    # Zone breakdown
    zones = {'A (90+)': 0, 'B (70-89)': 0, 'C (50-69)': 0, 'D (<50)': 0}
    for s in scores:
        if s >= 90:
            zones['A (90+)'] += 1
        elif s >= 70:
            zones['B (70-89)'] += 1
        elif s >= 50:
            zones['C (50-69)'] += 1
        else:
            zones['D (<50)'] += 1
    zone_pct = {k: round(v / n * 100, 1) for k, v in zones.items()}

    return {
        'trend': {'direction': direction, 'slope': slope},
        'consistency': {'stddev': stddev, 'cv': cv},
        'streaks': {'current': current_streak, 'best': best_streak,
                    'type': streak_type},
        'pace': n,
        'zone_breakdown': zone_pct,
    }


def format_analytics_dashboard(student, analytics=None):
    """Format analytics as a dashboard."""
    if analytics is None:
        analytics = compute_analytics(student)

    lines = []
    lines.append("╔" + "═" * 50 + "╗")
    lines.append("║" + f"  Analytics: {student.name:^36s}" + "  ║")
    lines.append("╚" + "═" * 50 + "╝")

    # Trend
    t = analytics['trend']
    arrow = {'improving': '↗', 'declining': '↘', 'stable': '→'}.get(t['direction'], '?')
    lines.append(f"\n  TREND: {arrow} {t['direction']} (slope: {t['slope']:+.2f})")

    # Consistency
    c = analytics['consistency']
    lines.append(f"  CONSISTENCY: σ={c['stddev']}  CV={c['cv']}%")

    # Streaks
    s = analytics['streaks']
    lines.append(f"  STREAKS: current={s['current']} ({s['type']}), "
                 f"best win={s['best']}")

    # Zone breakdown
    lines.append("\n  ZONE DISTRIBUTION:")
    for zone, pct in analytics['zone_breakdown'].items():
        bar_len = int(pct / 5)
        bar = '█' * bar_len + '░' * (20 - bar_len)
        lines.append(f"    {zone:12s} [{bar}] {pct:5.1f}%")

    # Total sessions
    lines.append(f"\n  Total sessions: {analytics['pace']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# CUSTOM RULE BUILDER (v30)
# ═══════════════════════════════════════════════════════════

class CustomRule:
    """
    User-defined validation rule.

    Allows teachers to create custom constraints:
    - condition: a callable (tact_data) → bool
    - name, code, severity, message
    """

    def __init__(self, code, name, condition_fn, message='',
                 severity='warning'):
        self.code = code
        self.name = name
        self.condition_fn = condition_fn
        self.message = message or f"Custom rule {code} violated"
        self.severity = severity
        self.active = True

    def check(self, tact_data):
        """Check if the rule is violated. Returns violation dict or None."""
        if not self.active:
            return None
        try:
            violated = self.condition_fn(tact_data)
        except Exception:
            return None
        if violated:
            return {
                'rule': self.code,
                'name': self.name,
                'severity': self.severity,
                'message': self.message,
            }
        return None


class RuleBuilder:
    """
    Builder for constructing custom rules declaratively.

    Usage:
        rule = (RuleBuilder('CX1', 'No group 7')
                .when_group(7)
                .severity('error')
                .message('Group 7 symbols are forbidden')
                .build())
    """

    def __init__(self, code, name):
        self._code = code
        self._name = name
        self._severity = 'warning'
        self._message = ''
        self._conditions = []

    def when_group(self, group):
        """Trigger when symbol is in given group."""
        self._conditions.append(
            lambda td, g=group: get_group(td.get('sym', 0)) == g)
        return self

    def when_score_below(self, threshold):
        """Trigger when tact score is below threshold."""
        self._conditions.append(
            lambda td, t=threshold: td.get('score', 100) < t)
        return self

    def when_repeat(self, max_consecutive=2):
        """Trigger when symbol repeats too many times."""
        self._conditions.append(
            lambda td, m=max_consecutive: td.get('consecutive', 0) > m)
        return self

    def when_custom(self, fn):
        """Add a custom condition function."""
        self._conditions.append(fn)
        return self

    def severity(self, sev):
        """Set severity: info, warning, error."""
        self._severity = sev
        return self

    def message(self, msg):
        """Set violation message."""
        self._message = msg
        return self

    def build(self):
        """Build the CustomRule."""
        conditions = self._conditions[:]

        def combined(td):
            return all(c(td) for c in conditions)

        return CustomRule(
            self._code, self._name, combined,
            message=self._message, severity=self._severity)


class CustomRuleEngine:
    """
    Manages a set of custom rules and validates tacts against them.
    """

    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        """Add a custom rule."""
        self.rules.append(rule)

    def remove_rule(self, code):
        """Remove rule by code."""
        self.rules = [r for r in self.rules if r.code != code]

    def validate(self, tact_data):
        """Check all rules, return list of violations."""
        violations = []
        for rule in self.rules:
            v = rule.check(tact_data)
            if v:
                violations.append(v)
        return violations

    def validate_sequence(self, tacts):
        """Validate a sequence of tact data dicts."""
        all_violations = []
        for i, td in enumerate(tacts):
            td['tact_index'] = i
            viols = self.validate(td)
            for v in viols:
                v['tact'] = i
            all_violations.extend(viols)
        return all_violations

    def summary(self):
        """Summary of registered rules."""
        lines = [f"Custom Rules ({len(self.rules)})"]
        lines.append("─" * 45)
        for r in self.rules:
            status = '●' if r.active else '○'
            lines.append(f"  {status} [{r.code}] {r.name} "
                         f"({r.severity})")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# GOAL TRACKING SYSTEM (v31)
# ═══════════════════════════════════════════════════════════

class Goal:
    """
    A trackable training goal with deadline and progress.

    Types:
    - score: reach a target average score
    - sessions: complete N sessions
    - streak: maintain a winning streak of N
    - mastery: reach mastery level N
    - badge: earn a specific badge
    """

    def __init__(self, goal_id, goal_type, target, description='',
                 deadline_sessions=None):
        self.goal_id = goal_id
        self.goal_type = goal_type
        self.target = target
        self.description = description or f"{goal_type} goal: {target}"
        self.deadline_sessions = deadline_sessions  # sessions left to achieve
        self.created_at_session = 0
        self.completed = False
        self.progress = 0.0  # 0-100%

    def evaluate(self, student):
        """Evaluate progress toward this goal. Returns progress 0-100."""
        sessions = student.sessions
        scores = [s['pct'] for s in sessions]
        n = len(sessions)

        if self.goal_type == 'score':
            if not scores:
                self.progress = 0
            else:
                recent = scores[-5:] if len(scores) >= 5 else scores
                avg = sum(recent) / len(recent)
                self.progress = min(round(avg / self.target * 100, 1), 100)
                if avg >= self.target:
                    self.completed = True

        elif self.goal_type == 'sessions':
            self.progress = min(round(n / self.target * 100, 1), 100)
            if n >= self.target:
                self.completed = True

        elif self.goal_type == 'streak':
            threshold = 70
            streak = 0
            for s in reversed(scores):
                if s >= threshold:
                    streak += 1
                else:
                    break
            self.progress = min(round(streak / self.target * 100, 1), 100)
            if streak >= self.target:
                self.completed = True

        elif self.goal_type == 'mastery':
            ml = student.mastery_level
            self.progress = min(round(ml / self.target * 100, 1), 100)
            if ml >= self.target:
                self.completed = True

        elif self.goal_type == 'badge':
            badges = check_badges(student)
            if self.target in badges:
                self.progress = 100
                self.completed = True
            else:
                # Rough estimate based on badge count
                self.progress = min(round(len(badges) / 12 * 100, 1), 99)

        return self.progress

    def is_expired(self, current_session):
        """Check if deadline has passed."""
        if self.deadline_sessions is None:
            return False
        return (current_session - self.created_at_session) > self.deadline_sessions


class GoalTracker:
    """
    Manages a set of goals for a student.
    """

    def __init__(self, student):
        self.student = student
        self.goals = []
        self._next_id = 1

    def add_goal(self, goal_type, target, description='',
                 deadline_sessions=None):
        """Add a new goal. Returns the goal."""
        g = Goal(f'G{self._next_id}', goal_type, target,
                 description, deadline_sessions)
        g.created_at_session = len(self.student.sessions)
        self.goals.append(g)
        self._next_id += 1
        return g

    def evaluate_all(self):
        """Evaluate all active goals. Returns list of (goal, progress)."""
        results = []
        for g in self.goals:
            if not g.completed:
                g.evaluate(self.student)
            results.append((g, g.progress))
        return results

    def completed_goals(self):
        """Return completed goals."""
        return [g for g in self.goals if g.completed]

    def active_goals(self):
        """Return active (incomplete) goals."""
        return [g for g in self.goals if not g.completed]

    def remove_goal(self, goal_id):
        """Remove a goal by ID."""
        self.goals = [g for g in self.goals if g.goal_id != goal_id]

    def suggest_goals(self):
        """Auto-suggest goals based on student state."""
        suggestions = []
        sessions = self.student.sessions
        scores = [s['pct'] for s in sessions]
        n = len(scores)
        ml = self.student.mastery_level

        if n < 10:
            suggestions.append(('sessions', 10, 'Complete 10 sessions'))
        elif n < 25:
            suggestions.append(('sessions', 25, 'Complete 25 sessions'))
        elif n < 50:
            suggestions.append(('sessions', 50, 'Reach 50 sessions'))

        if scores:
            avg = sum(scores[-5:]) / min(len(scores), 5)
            if avg < 70:
                suggestions.append(('score', 70, 'Reach 70% average'))
            elif avg < 85:
                suggestions.append(('score', 85, 'Reach 85% average'))
            elif avg < 95:
                suggestions.append(('score', 95, 'Reach 95% average'))

        if ml < 3:
            suggestions.append(('mastery', 3, 'Reach mastery level 3'))
        elif ml < 5:
            suggestions.append(('mastery', 5, 'Reach mastery level 5'))
        elif ml < 7:
            suggestions.append(('mastery', 7, 'Reach peak mastery'))

        suggestions.append(('streak', 5, 'Win streak of 5'))

        return suggestions

    def format_goals(self):
        """Format goals as text display."""
        self.evaluate_all()
        lines = [f"Goals for {self.student.name}"]
        lines.append("═" * 50)

        active = self.active_goals()
        done = self.completed_goals()

        if active:
            lines.append(f"  Active ({len(active)}):")
            for g in active:
                bar_len = int(g.progress / 5)
                bar = '▓' * bar_len + '░' * (20 - bar_len)
                lines.append(f"    [{bar}] {g.progress:5.1f}%  {g.description}")
        else:
            lines.append("  No active goals.")

        if done:
            lines.append(f"  Completed ({len(done)}):")
            for g in done:
                lines.append(f"    ✓ {g.description}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PEER COMPARISON ENGINE (v31)
# ═══════════════════════════════════════════════════════════

def peer_compare(student_a, student_b):
    """
    Compare two students across multiple dimensions.

    Returns structured comparison with winner per dimension.
    """
    def stats(st):
        scores = [s['pct'] for s in st.sessions]
        recent = scores[-5:] if len(scores) >= 5 else scores
        return {
            'name': st.name,
            'sessions': len(scores),
            'avg': round(sum(scores) / len(scores), 1) if scores else 0,
            'recent': round(sum(recent) / len(recent), 1) if recent else 0,
            'best': round(max(scores), 1) if scores else 0,
            'mastery': st.mastery_level,
            'elo': getattr(st, 'elo', 1200),
            'badges': len(check_badges(st)),
        }

    sa = stats(student_a)
    sb = stats(student_b)

    dimensions = ['avg', 'recent', 'best', 'mastery', 'elo', 'badges', 'sessions']
    comparison = []

    for dim in dimensions:
        va, vb = sa[dim], sb[dim]
        if va > vb:
            winner = sa['name']
        elif vb > va:
            winner = sb['name']
        else:
            winner = 'tie'
        comparison.append({
            'dimension': dim,
            'a_value': va,
            'b_value': vb,
            'winner': winner,
        })

    wins_a = sum(1 for c in comparison if c['winner'] == sa['name'])
    wins_b = sum(1 for c in comparison if c['winner'] == sb['name'])
    overall = sa['name'] if wins_a > wins_b else (
        sb['name'] if wins_b > wins_a else 'tie')

    return {
        'student_a': sa,
        'student_b': sb,
        'comparison': comparison,
        'wins_a': wins_a,
        'wins_b': wins_b,
        'overall': overall,
    }


def format_peer_compare(result):
    """Format peer comparison as text."""
    sa = result['student_a']
    sb = result['student_b']
    lines = []
    lines.append(f"  {sa['name']:>15s}  vs  {sb['name']:<15s}")
    lines.append("  " + "─" * 45)

    dim_labels = {
        'avg': 'Average', 'recent': 'Recent Avg', 'best': 'Best Score',
        'mastery': 'Mastery', 'elo': 'ELO', 'badges': 'Badges',
        'sessions': 'Sessions',
    }

    for c in result['comparison']:
        label = dim_labels.get(c['dimension'], c['dimension'])
        va, vb = c['a_value'], c['b_value']
        if c['winner'] == sa['name']:
            marker = '◀'
        elif c['winner'] == sb['name']:
            marker = '▶'
        else:
            marker = '='
        lines.append(f"  {va:>10}  {marker} {label:<12s} {vb:<10}")

    lines.append("  " + "─" * 45)
    wa, wb = result['wins_a'], result['wins_b']
    lines.append(f"  Score: {sa['name']} {wa} — {wb} {sb['name']}  "
                 f"│ Overall: {result['overall']}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SESSION PLAYBACK SYSTEM (v31)
# ═══════════════════════════════════════════════════════════

class SessionPlayback:
    """
    Step-by-step playback of a training session.

    Records each tact as a frame and allows replay with analysis.
    """

    def __init__(self, student_name, session_index=None):
        self.student_name = student_name
        self.session_index = session_index
        self.frames = []
        self.markers = {}   # frame_idx → marker text
        self.speed = 1.0

    def record_frame(self, tact_data):
        """Record one tact as a frame."""
        frame = {
            'idx': len(self.frames),
            'sym': tact_data.get('sym', 0),
            'group': get_group(tact_data.get('sym', 0)),
            'score': tact_data.get('score', 0),
            'violations': tact_data.get('violations', []),
            'cumulative_score': 0,
        }
        self.frames.append(frame)

        # Update cumulative
        scores_so_far = [f['score'] for f in self.frames if f['score'] > 0]
        if scores_so_far:
            frame['cumulative_score'] = round(
                sum(scores_so_far) / len(scores_so_far), 1)

        return frame

    def add_marker(self, frame_idx, text):
        """Add a named marker at a specific frame."""
        self.markers[frame_idx] = text

    def get_frame(self, idx):
        """Get a specific frame."""
        if 0 <= idx < len(self.frames):
            return self.frames[idx]
        return None

    def slice_frames(self, start, end):
        """Get a slice of frames."""
        return self.frames[max(0, start):min(end, len(self.frames))]

    def find_violations(self):
        """Find all frames with violations."""
        return [f for f in self.frames if f['violations']]

    def find_peaks(self, top_n=3):
        """Find top-scoring frames."""
        scored = [f for f in self.frames if f['score'] > 0]
        scored.sort(key=lambda f: f['score'], reverse=True)
        return scored[:top_n]

    def compute_momentum(self, window=5):
        """
        Compute momentum curve: rolling average of scores.

        Returns list of (frame_idx, momentum) tuples.
        """
        momentum = []
        scores = [f['score'] for f in self.frames]
        for i in range(len(scores)):
            start = max(0, i - window + 1)
            chunk = scores[start:i + 1]
            avg = sum(chunk) / len(chunk) if chunk else 0
            momentum.append((i, round(avg, 1)))
        return momentum

    def format_playback(self, start=0, count=10):
        """Format a section of the playback."""
        end = min(start + count, len(self.frames))
        lines = [f"Playback: {self.student_name} "
                 f"(frames {start}-{end - 1} of {len(self.frames)})"]
        lines.append("─" * 55)

        for i in range(start, end):
            f = self.frames[i]
            sym_str = f"S{f['sym']:02d}"
            grp_str = f"G{f['group']}"
            score_str = f"{f['score']:5.1f}"
            cum_str = f"avg={f['cumulative_score']:5.1f}"
            viol_mark = '!' if f['violations'] else ' '
            marker = ''
            if i in self.markers:
                marker = f"  ◆ {self.markers[i]}"

            lines.append(f"  [{i:03d}] {sym_str} {grp_str} "
                         f"score={score_str} {cum_str} "
                         f"{viol_mark}{marker}")

        # Momentum mini-chart at the end
        momentum = self.compute_momentum()
        if momentum and end > start:
            lines.append("")
            lines.append("  Momentum:")
            relevant = momentum[start:end]
            for idx, mom in relevant:
                bar_len = int(mom / 5)
                bar = '▪' * bar_len
                lines.append(f"    [{idx:03d}] {bar} {mom}")

        return '\n'.join(lines)

    def summary(self):
        """Brief summary of the playback."""
        n = len(self.frames)
        if n == 0:
            return f"Playback: {self.student_name} — empty"

        scores = [f['score'] for f in self.frames if f['score'] > 0]
        avg = round(sum(scores) / len(scores), 1) if scores else 0
        viols = sum(1 for f in self.frames if f['violations'])
        peaks = self.find_peaks(1)
        best = peaks[0]['score'] if peaks else 0

        return (f"Playback: {self.student_name} — {n} frames, "
                f"avg={avg}, best={best}, violations={viols}, "
                f"markers={len(self.markers)}")


# ═══════════════════════════════════════════════════════════
# TRAINING TEMPLATES (v32)
# ═══════════════════════════════════════════════════════════

TRAINING_TEMPLATES = {
    'warmup': {
        'name': 'Warm-Up',
        'description': 'Light session, low difficulty, general practice',
        'n_tacts': 8,
        'difficulty': 'easy',
        'focus': 'general',
        'groups_allowed': [1, 2, 3],
        'min_mastery': 1,
    },
    'drill_zone': {
        'name': 'Zone Drill',
        'description': 'Focused on zone accuracy (R1)',
        'n_tacts': 14,
        'difficulty': 'medium',
        'focus': 'zone_accuracy',
        'groups_allowed': [1, 2, 3, 4],
        'min_mastery': 2,
    },
    'group_flow': {
        'name': 'Group Flow',
        'description': 'Practice smooth group transitions (R2)',
        'n_tacts': 14,
        'difficulty': 'medium',
        'focus': 'group_transitions',
        'groups_allowed': [1, 2, 3, 4, 5],
        'min_mastery': 2,
    },
    'endurance': {
        'name': 'Endurance',
        'description': 'Long session, all groups, sustained focus',
        'n_tacts': 24,
        'difficulty': 'hard',
        'focus': 'general',
        'groups_allowed': [1, 2, 3, 4, 5, 6],
        'min_mastery': 3,
    },
    'peak_challenge': {
        'name': 'Peak Challenge',
        'description': 'All groups including peak defense (G7)',
        'n_tacts': 20,
        'difficulty': 'hard',
        'focus': 'peak_defense',
        'groups_allowed': [1, 2, 3, 4, 5, 6, 7],
        'min_mastery': 5,
    },
    'speed_run': {
        'name': 'Speed Run',
        'description': 'Short but intense, high accuracy required',
        'n_tacts': 10,
        'difficulty': 'hard',
        'focus': 'speed',
        'groups_allowed': [1, 2, 3, 4, 5],
        'min_mastery': 3,
    },
}


def get_available_templates(student):
    """Return templates the student has unlocked based on mastery."""
    ml = student.mastery_level
    available = {}
    for tid, tmpl in TRAINING_TEMPLATES.items():
        if ml >= tmpl['min_mastery']:
            available[tid] = tmpl
    return available


def apply_template(template_id, student):
    """
    Apply a template to generate session parameters.

    Returns a config dict for running a session.
    """
    tmpl = TRAINING_TEMPLATES.get(template_id)
    if not tmpl:
        raise ValueError(f"Unknown template: {template_id}")

    if student.mastery_level < tmpl['min_mastery']:
        raise ValueError(
            f"Mastery level {tmpl['min_mastery']} required, "
            f"student is at {student.mastery_level}")

    # Build symbol pool from allowed groups
    sym_pool = []
    for sym in range(64):
        if get_group(sym) in tmpl['groups_allowed']:
            sym_pool.append(sym)

    return {
        'template': template_id,
        'name': tmpl['name'],
        'n_tacts': tmpl['n_tacts'],
        'difficulty': tmpl['difficulty'],
        'focus': tmpl['focus'],
        'symbol_pool': sym_pool,
        'pool_size': len(sym_pool),
    }


def format_template_catalog(student=None):
    """Format template catalog, marking available/locked."""
    lines = ["Training Templates"]
    lines.append("═" * 55)
    for tid, tmpl in TRAINING_TEMPLATES.items():
        locked = ''
        if student and student.mastery_level < tmpl['min_mastery']:
            locked = f' 🔒 (L{tmpl["min_mastery"]}+)'

        lines.append(f"  [{tid}] {tmpl['name']}{locked}")
        lines.append(f"    {tmpl['description']}")
        lines.append(f"    Tacts: {tmpl['n_tacts']}  |  "
                     f"Difficulty: {tmpl['difficulty']}  |  "
                     f"Groups: {tmpl['groups_allowed']}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# CORRELATION ANALYSIS (v32)
# ═══════════════════════════════════════════════════════════

def compute_correlation(xs, ys):
    """
    Pearson correlation coefficient between two lists.

    Returns r in [-1, 1], or 0 if insufficient data.
    """
    n = min(len(xs), len(ys))
    if n < 3:
        return 0.0

    xs, ys = xs[:n], ys[:n]
    mx = sum(xs) / n
    my = sum(ys) / n

    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5

    if dx == 0 or dy == 0:
        return 0.0
    return round(num / (dx * dy), 4)


def correlation_matrix(student):
    """
    Compute correlation matrix across session metrics.

    Metrics: score, length, violations, session_index (time).
    Returns dict of (metric_a, metric_b) → r.
    """
    sessions = student.sessions
    if len(sessions) < 3:
        return {}

    scores = [s['pct'] for s in sessions]
    lengths = [s.get('length', 0) for s in sessions]
    viols = [len(s.get('violations', [])) for s in sessions]
    indices = list(range(len(sessions)))

    metrics = {
        'score': scores,
        'length': lengths,
        'violations': viols,
        'time': indices,
    }

    matrix = {}
    names = list(metrics.keys())
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            r = compute_correlation(metrics[a], metrics[b])
            matrix[(a, b)] = r

    return matrix


def format_correlation_matrix(matrix):
    """Format correlation matrix."""
    if not matrix:
        return "Insufficient data for correlation analysis."

    lines = ["Correlation Matrix"]
    lines.append("─" * 45)

    for (a, b), r in sorted(matrix.items()):
        strength = 'strong' if abs(r) > 0.7 else (
            'moderate' if abs(r) > 0.4 else 'weak')
        direction = '+' if r > 0 else '-' if r < 0 else ' '
        bar_r = int(abs(r) * 20)
        bar = '█' * bar_r + '░' * (20 - bar_r)
        lines.append(f"  {a:>11s} × {b:<11s} "
                     f"r={direction}{abs(r):.3f} [{bar}] {strength}")

    return '\n'.join(lines)


def find_insights(student):
    """
    Discover data insights from correlation analysis.

    Returns list of human-readable insight strings.
    """
    matrix = correlation_matrix(student)
    insights = []

    r_time_score = matrix.get(('score', 'time'), 0)
    if r_time_score > 0.5:
        insights.append(
            f"Strong improvement over time (r={r_time_score:.3f})")
    elif r_time_score < -0.3:
        insights.append(
            f"Scores declining over time (r={r_time_score:.3f})")

    r_score_viols = matrix.get(('score', 'violations'), 0)
    if r_score_viols < -0.4:
        insights.append(
            f"Violations strongly reduce scores (r={r_score_viols:.3f})")

    r_len_score = matrix.get(('length', 'score'), 0)
    if abs(r_len_score) > 0.4:
        if r_len_score > 0:
            insights.append("Longer sessions correlate with higher scores")
        else:
            insights.append("Longer sessions correlate with lower scores "
                           "(fatigue?)")

    if not insights:
        insights.append("No strong correlations detected — performance is "
                       "well-balanced.")

    return insights


# ═══════════════════════════════════════════════════════════
# SYSTEM CONFIGURATION MANAGER (v32)
# ═══════════════════════════════════════════════════════════

class ScarabConfig:
    """
    Central configuration for the Scarab algorithm.

    Manages all tunable parameters with defaults, validation,
    and save/load to dict.
    """

    DEFAULTS = {
        # Core
        'n_symbols': 64,
        'n_groups': 7,
        'max_mastery': 7,
        'default_elo': 1200,

        # Sessions
        'default_session_length': 14,
        'min_session_length': 4,
        'max_session_length': 32,

        # Scoring
        'passing_score': 70,
        'grade_a_threshold': 90,
        'grade_b_threshold': 70,
        'grade_c_threshold': 50,

        # Streaks
        'streak_win_threshold': 70,
        'max_streak_bonus': 5,

        # Analytics
        'analytics_window': 10,
        'momentum_window': 5,
        'trend_improving_threshold': 0.5,
        'trend_declining_threshold': -0.5,

        # Scheduler
        'default_sessions_per_week': 4,
        'max_sessions_per_week': 7,
        'min_rest_days': 1,

        # Notifications
        'session_milestones': [1, 5, 10, 25, 50, 100],
        'score_drop_alert_threshold': 15,

        # Display
        'progress_bar_width': 20,
        'history_display_count': 10,
    }

    def __init__(self, overrides=None):
        self._values = dict(self.DEFAULTS)
        if overrides:
            for k, v in overrides.items():
                if k in self.DEFAULTS:
                    self._values[k] = v

    def get(self, key, default=None):
        """Get a config value."""
        return self._values.get(key, default)

    def set(self, key, value):
        """Set a config value (must be a known key)."""
        if key not in self.DEFAULTS:
            raise KeyError(f"Unknown config key: {key}")
        self._values[key] = value

    def reset(self, key=None):
        """Reset one or all keys to default."""
        if key:
            if key in self.DEFAULTS:
                self._values[key] = self.DEFAULTS[key]
        else:
            self._values = dict(self.DEFAULTS)

    def diff_from_defaults(self):
        """Return dict of values that differ from defaults."""
        return {k: v for k, v in self._values.items()
                if v != self.DEFAULTS.get(k)}

    def to_dict(self):
        """Export all config as dict."""
        return dict(self._values)

    def validate(self):
        """Validate configuration consistency. Returns list of issues."""
        issues = []
        v = self._values

        if v['min_session_length'] > v['max_session_length']:
            issues.append("min_session_length > max_session_length")

        if v['grade_a_threshold'] <= v['grade_b_threshold']:
            issues.append("grade_a must be > grade_b")

        if v['grade_b_threshold'] <= v['grade_c_threshold']:
            issues.append("grade_b must be > grade_c")

        if v['default_sessions_per_week'] > v['max_sessions_per_week']:
            issues.append("default_sessions > max_sessions per week")

        if v['analytics_window'] < 3:
            issues.append("analytics_window must be >= 3")

        return issues

    def format_config(self, only_changed=False):
        """Format configuration for display."""
        items = (self.diff_from_defaults() if only_changed
                 else self._values)

        lines = ["Scarab Configuration"]
        lines.append("═" * 50)

        sections = {
            'Core': ['n_symbols', 'n_groups', 'max_mastery', 'default_elo'],
            'Sessions': ['default_session_length', 'min_session_length',
                        'max_session_length'],
            'Scoring': ['passing_score', 'grade_a_threshold',
                       'grade_b_threshold', 'grade_c_threshold'],
            'Analytics': ['analytics_window', 'momentum_window',
                         'trend_improving_threshold',
                         'trend_declining_threshold'],
            'Scheduler': ['default_sessions_per_week',
                         'max_sessions_per_week', 'min_rest_days'],
        }

        for section, keys in sections.items():
            relevant = {k: items[k] for k in keys if k in items}
            if relevant:
                lines.append(f"\n  [{section}]")
                for k, val in relevant.items():
                    default = self.DEFAULTS.get(k)
                    marker = ' *' if val != default else ''
                    lines.append(f"    {k}: {val}{marker}")

        issues = self.validate()
        if issues:
            lines.append(f"\n  ⚠ Validation issues: {len(issues)}")
            for iss in issues:
                lines.append(f"    - {iss}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# FEEDBACK LOOP SYSTEM (v33)
# ═══════════════════════════════════════════════════════════

class FeedbackLoop:
    """
    Adaptive feedback loop that adjusts training based on performance.

    Cycle: Observe → Analyze → Decide → Act
    - Observe: collect recent session data
    - Analyze: detect patterns (plateau, regression, breakthrough)
    - Decide: choose intervention
    - Act: produce actionable recommendations
    """

    STATES = ['observing', 'analyzing', 'deciding', 'acting']

    def __init__(self, student, lookback=5):
        self.student = student
        self.lookback = lookback
        self.state = 'observing'
        self.cycle_count = 0
        self.interventions = []

    def observe(self):
        """Collect recent data."""
        sessions = self.student.sessions
        scores = [s['pct'] for s in sessions]
        n = len(scores)
        recent = scores[-self.lookback:] if n >= self.lookback else scores

        observation = {
            'n_sessions': n,
            'recent_scores': recent,
            'recent_avg': round(sum(recent) / len(recent), 1) if recent else 0,
            'trend': 0,
        }

        if len(recent) >= 3:
            first_half = recent[:len(recent) // 2]
            second_half = recent[len(recent) // 2:]
            avg1 = sum(first_half) / len(first_half)
            avg2 = sum(second_half) / len(second_half)
            observation['trend'] = round(avg2 - avg1, 1)

        self.state = 'analyzing'
        return observation

    def analyze(self, observation):
        """Detect patterns from observation."""
        patterns = []
        avg = observation['recent_avg']
        trend = observation['trend']
        scores = observation['recent_scores']

        # Plateau: low variance, no trend
        if len(scores) >= 3:
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            if variance < 10 and abs(trend) < 3:
                patterns.append({
                    'type': 'plateau',
                    'level': round(mean, 1),
                    'severity': 'medium',
                })

        # Regression: declining trend
        if trend < -5:
            patterns.append({
                'type': 'regression',
                'drop': abs(trend),
                'severity': 'high' if trend < -10 else 'medium',
            })

        # Breakthrough: strong upward trend
        if trend > 8:
            patterns.append({
                'type': 'breakthrough',
                'gain': trend,
                'severity': 'positive',
            })

        # Struggling: low average
        if avg < 60:
            patterns.append({
                'type': 'struggling',
                'avg': avg,
                'severity': 'high',
            })

        # Excellence: high average
        if avg >= 90:
            patterns.append({
                'type': 'excellence',
                'avg': avg,
                'severity': 'positive',
            })

        self.state = 'deciding'
        return patterns

    def decide(self, patterns):
        """Choose interventions based on patterns."""
        decisions = []

        for p in patterns:
            if p['type'] == 'plateau':
                decisions.append({
                    'action': 'increase_difficulty',
                    'reason': f"Plateau at {p['level']}%",
                    'suggestion': 'Try harder templates or new focus areas',
                })

            elif p['type'] == 'regression':
                decisions.append({
                    'action': 'reduce_difficulty',
                    'reason': f"Score dropped by {p['drop']} points",
                    'suggestion': 'Review fundamentals, shorter sessions',
                })

            elif p['type'] == 'breakthrough':
                decisions.append({
                    'action': 'maintain_pace',
                    'reason': f"Gained {p['gain']} points",
                    'suggestion': 'Keep current approach, consolidate gains',
                })

            elif p['type'] == 'struggling':
                decisions.append({
                    'action': 'simplify',
                    'reason': f"Average only {p['avg']}%",
                    'suggestion': 'Use warmup template, focus on basics',
                })

            elif p['type'] == 'excellence':
                decisions.append({
                    'action': 'advance',
                    'reason': f"Excellent at {p['avg']}%",
                    'suggestion': 'Ready for next mastery level or peak challenge',
                })

        if not decisions:
            decisions.append({
                'action': 'continue',
                'reason': 'No significant patterns detected',
                'suggestion': 'Continue current training plan',
            })

        self.state = 'acting'
        return decisions

    def run_cycle(self):
        """Run one full feedback cycle."""
        obs = self.observe()
        patterns = self.analyze(obs)
        decisions = self.decide(patterns)

        self.cycle_count += 1
        self.interventions.extend(decisions)

        self.state = 'observing'
        return {
            'cycle': self.cycle_count,
            'observation': obs,
            'patterns': patterns,
            'decisions': decisions,
        }

    def format_cycle(self, result):
        """Format a feedback cycle result."""
        lines = [f"Feedback Cycle #{result['cycle']}"]
        lines.append("─" * 50)

        obs = result['observation']
        lines.append(f"  Observe: {obs['n_sessions']} sessions, "
                     f"recent avg={obs['recent_avg']}%, "
                     f"trend={obs['trend']:+.1f}")

        patterns = result['patterns']
        if patterns:
            lines.append(f"  Analyze: {len(patterns)} pattern(s)")
            for p in patterns:
                lines.append(f"    • {p['type']} ({p['severity']})")
        else:
            lines.append("  Analyze: no significant patterns")

        for d in result['decisions']:
            lines.append(f"  Decide: {d['action']}")
            lines.append(f"    Reason: {d['reason']}")
            lines.append(f"    → {d['suggestion']}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PROGRESSION PATH VISUALIZER (v33)
# ═══════════════════════════════════════════════════════════

def compute_progression_path(student):
    """
    Compute the student's progression path through mastery levels.

    Returns list of path nodes with timestamps and scores.
    """
    sessions = student.sessions
    ml = student.mastery_level

    path = []
    # Reconstruct progression based on score thresholds
    level_thresholds = [0, 50, 60, 70, 75, 80, 85]
    current_level = 1
    running_avg = 0

    for i, s in enumerate(sessions):
        score = s['pct']
        running_avg = (running_avg * i + score) / (i + 1)

        # Check if level up happened
        if current_level < 7:
            threshold = level_thresholds[current_level]
            if running_avg >= threshold and i >= current_level * 2:
                path.append({
                    'event': 'level_up',
                    'from_level': current_level,
                    'to_level': current_level + 1,
                    'session': i + 1,
                    'avg_at_time': round(running_avg, 1),
                })
                current_level += 1

        # Score milestones
        if score >= 90 and not any(
                p.get('milestone') == 'first_90' for p in path):
            path.append({
                'event': 'milestone',
                'milestone': 'first_90',
                'session': i + 1,
                'score': round(score, 1),
            })

    # Current position
    path.append({
        'event': 'current',
        'level': ml,
        'session': len(sessions),
        'avg': round(running_avg, 1) if sessions else 0,
    })

    return path


def format_progression_path(path):
    """Format progression path as ASCII timeline."""
    lines = ["Progression Path"]
    lines.append("═" * 50)

    for node in path:
        if node['event'] == 'level_up':
            lines.append(
                f"  S{node['session']:03d} ┃ ↑ Level {node['from_level']}"
                f" → {node['to_level']}  "
                f"(avg: {node['avg_at_time']}%)")

        elif node['event'] == 'milestone':
            lines.append(
                f"  S{node['session']:03d} ┃ ★ {node['milestone']}  "
                f"({node['score']}%)")

        elif node['event'] == 'current':
            lines.append(
                f"  S{node['session']:03d} ┃ ● Current: L{node['level']} "
                f"(avg: {node['avg']}%)")

    # ASCII path line
    lines.append("")
    n = len(path)
    line_str = "  "
    for i, node in enumerate(path):
        if node['event'] == 'level_up':
            line_str += "↑"
        elif node['event'] == 'milestone':
            line_str += "★"
        elif node['event'] == 'current':
            line_str += "●"
        if i < n - 1:
            line_str += "───"
    lines.append(line_str)

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# HEATMAP ANALYSIS (v33)
# ═══════════════════════════════════════════════════════════

def session_heatmap(student, metric='score'):
    """
    Generate a heatmap grid of session performance.

    Organizes sessions into rows of 10 for visual scanning.
    Each cell shows a heat symbol based on metric value.
    """
    sessions = student.sessions
    if not sessions:
        return {'grid': [], 'legend': {}}

    values = []
    for s in sessions:
        if metric == 'score':
            values.append(s['pct'])
        elif metric == 'violations':
            values.append(len(s.get('violations', [])))
        else:
            values.append(s.get(metric, 0))

    # Normalize to heat levels 0-4
    if not values:
        return {'grid': [], 'legend': {}}

    vmin = min(values)
    vmax = max(values)
    rng = vmax - vmin if vmax > vmin else 1

    heat_chars = ['░', '▒', '▓', '█', '█']
    heat_labels = ['low', 'below avg', 'average', 'above avg', 'high']

    grid = []
    row_size = 10
    for start in range(0, len(values), row_size):
        row = []
        for v in values[start:start + row_size]:
            level = int((v - vmin) / rng * 3.99)
            level = max(0, min(4, level))
            row.append({
                'value': round(v, 1),
                'heat': level,
                'char': heat_chars[level],
            })
        grid.append(row)

    legend = {i: f"{heat_chars[i]} {heat_labels[i]}"
              for i in range(5)}

    return {
        'grid': grid,
        'n_sessions': len(values),
        'min': round(vmin, 1),
        'max': round(vmax, 1),
        'legend': legend,
    }


def format_session_heatmap(heatmap_data, title='Session Heatmap'):
    """Format session heatmap as ASCII art."""
    grid = heatmap_data['grid']
    if not grid:
        return f"{title}: no data"

    lines = [title]
    lines.append("─" * 45)

    for row_idx, row in enumerate(grid):
        start = row_idx * 10 + 1
        end = start + len(row) - 1
        cells = ' '.join(cell['char'] for cell in row)
        lines.append(f"  S{start:03d}-{end:03d}: {cells}")

    lines.append("")
    lines.append(f"  Range: {heatmap_data['min']} — {heatmap_data['max']}")
    legend = heatmap_data['legend']
    lines.append(f"  Legend: {legend[0]}  {legend[2]}  {legend[4]}")

    return '\n'.join(lines)


def group_usage_heatmap(student):
    """
    Heatmap of Kryukov group usage across sessions.

    Each row = session, columns = groups 1-7.
    Value = count of symbols from that group.
    """
    sessions = student.sessions
    rows = []

    for s in sessions:
        group_counts = {g: 0 for g in range(1, 8)}
        # Count symbols by group from session data
        for v in s.get('violations', []):
            rule = v.get('rule', '')
            if 'Group' in rule or 'group' in str(v):
                g = v.get('group', 1)
                group_counts[min(max(g, 1), 7)] += 1

        rows.append(group_counts)

    return rows


# ═══════════════════════════════════════════════════════════
# EVENT LOG SYSTEM (v34)
# ═══════════════════════════════════════════════════════════

class EventLog:
    """
    Structured, queryable event log for the Scarab system.

    Logs events with category, level, source, and payload.
    Supports filtering, aggregation, and export.
    """

    LEVELS = ('debug', 'info', 'warning', 'error', 'critical')

    def __init__(self, max_size=1000):
        self.entries = []
        self.max_size = max_size
        self._seq = 0

    def log(self, category, message, level='info', source='', data=None):
        """Add a log entry."""
        self._seq += 1
        entry = {
            'seq': self._seq,
            'category': category,
            'level': level,
            'source': source,
            'message': message,
            'data': data or {},
        }
        self.entries.append(entry)

        # Trim if over max
        if len(self.entries) > self.max_size:
            self.entries = self.entries[-self.max_size:]

        return entry

    def query(self, category=None, level=None, source=None, last_n=None):
        """Query log entries with filters."""
        result = self.entries
        if category:
            result = [e for e in result if e['category'] == category]
        if level:
            result = [e for e in result if e['level'] == level]
        if source:
            result = [e for e in result if e['source'] == source]
        if last_n:
            result = result[-last_n:]
        return result

    def count_by_level(self):
        """Count entries by level."""
        counts = {lv: 0 for lv in self.LEVELS}
        for e in self.entries:
            counts[e['level']] = counts.get(e['level'], 0) + 1
        return counts

    def count_by_category(self):
        """Count entries by category."""
        counts = {}
        for e in self.entries:
            cat = e['category']
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def clear(self):
        """Clear all entries."""
        self.entries.clear()
        self._seq = 0

    def format_log(self, entries=None, max_lines=20):
        """Format log entries for display."""
        items = entries if entries is not None else self.entries[-max_lines:]
        lines = [f"Event Log ({len(self.entries)} total)"]
        lines.append("─" * 60)

        level_icons = {
            'debug': '🔍', 'info': 'ℹ️', 'warning': '⚠️',
            'error': '❌', 'critical': '🔥',
        }

        for e in items[-max_lines:]:
            icon = level_icons.get(e['level'], '•')
            src = f" [{e['source']}]" if e['source'] else ''
            lines.append(f"  #{e['seq']:04d} {icon} "
                         f"{e['category']}{src}: {e['message']}")

        return '\n'.join(lines)


def log_student_session(event_log, student, session_idx):
    """Log events from a student session."""
    sessions = student.sessions
    if session_idx >= len(sessions):
        return

    s = sessions[session_idx]
    pct = s['pct']

    event_log.log('session', f"{student.name} completed session "
                  f"#{session_idx + 1}: {pct:.1f}%",
                  source=student.name,
                  data={'session': session_idx, 'pct': pct})

    if pct >= 90:
        event_log.log('achievement',
                      f"{student.name} scored Grade A ({pct:.1f}%)",
                      level='info', source=student.name)

    viols = s.get('violations', [])
    if len(viols) > 3:
        event_log.log('violation',
                      f"{student.name} had {len(viols)} violations",
                      level='warning', source=student.name)


# ═══════════════════════════════════════════════════════════
# KATA DIFFICULTY SCORER (v34)
# ═══════════════════════════════════════════════════════════

def score_kata_difficulty(kata):
    """
    Score the difficulty of a kata sequence on a 1-10 scale.

    Factors:
    - Length (more tacts = harder)
    - Group diversity (more groups = harder)
    - High-group usage (G5-G7 = harder)
    - Transition complexity (more group changes = harder)
    - Repetition (less repetition = harder)

    Returns dict with total score and breakdown.
    """
    if not kata:
        return {'total': 0, 'breakdown': {}}

    n = len(kata)

    # Length factor (0-2)
    if n <= 6:
        f_length = 0.5
    elif n <= 12:
        f_length = 1.0
    elif n <= 20:
        f_length = 1.5
    else:
        f_length = 2.0

    # Group diversity (0-2)
    groups_used = set()
    group_seq = []
    for sym in kata:
        g = get_group(sym if isinstance(sym, int) else 0)
        groups_used.add(g)
        group_seq.append(g)
    f_diversity = min(len(groups_used) / 3.5, 2.0)

    # High-group usage (0-2)
    high_count = sum(1 for g in group_seq if g >= 5)
    f_high = min(high_count / max(n, 1) * 4, 2.0)

    # Transition complexity (0-2)
    transitions = sum(1 for i in range(1, len(group_seq))
                      if group_seq[i] != group_seq[i - 1])
    f_transitions = min(transitions / max(n - 1, 1) * 2.5, 2.0)

    # Repetition penalty (0-2, less repetition = higher)
    unique = len(set(kata))
    f_unique = min(unique / max(n, 1) * 2.5, 2.0)

    total = round(f_length + f_diversity + f_high +
                  f_transitions + f_unique, 1)
    total = min(total, 10.0)

    return {
        'total': total,
        'breakdown': {
            'length': round(f_length, 2),
            'diversity': round(f_diversity, 2),
            'high_groups': round(f_high, 2),
            'transitions': round(f_transitions, 2),
            'uniqueness': round(f_unique, 2),
        },
        'n_tacts': n,
        'groups_used': sorted(groups_used),
        'label': ('Easy' if total < 3.5 else
                  'Medium' if total < 6 else
                  'Hard' if total < 8 else 'Expert'),
    }


def format_kata_difficulty(diff):
    """Format kata difficulty score."""
    lines = [f"Kata Difficulty: {diff['total']}/10 ({diff['label']})"]
    lines.append("─" * 40)
    lines.append(f"  Tacts: {diff['n_tacts']}, "
                 f"Groups: {diff['groups_used']}")

    bd = diff['breakdown']
    for factor, val in bd.items():
        bar_len = int(val / 2 * 20)
        bar = '▓' * bar_len + '░' * (20 - bar_len)
        lines.append(f"  {factor:14s} [{bar}] {val:.2f}/2.0")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PERFORMANCE PREDICTOR (v34)
# ═══════════════════════════════════════════════════════════

def predict_next_score(student, method='linear'):
    """
    Predict the student's next session score.

    Methods:
    - linear: linear regression extrapolation
    - ewma: exponentially weighted moving average
    - ensemble: average of all methods

    Returns dict with prediction, confidence, method.
    """
    scores = [s['pct'] for s in student.sessions]
    n = len(scores)

    if n == 0:
        return {'prediction': 50, 'confidence': 0, 'method': method}

    if n == 1:
        return {'prediction': round(scores[0], 1),
                'confidence': 20, 'method': method}

    # Linear regression
    x_mean = (n - 1) / 2
    y_mean = sum(scores) / n
    num = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den > 0 else 0
    intercept = y_mean - slope * x_mean
    linear_pred = intercept + slope * n

    # EWMA
    alpha = 0.3
    ewma = scores[0]
    for s in scores[1:]:
        ewma = alpha * s + (1 - alpha) * ewma
    ewma_pred = ewma

    # Confidence based on variance
    variance = sum((s - y_mean) ** 2 for s in scores) / n
    stddev = variance ** 0.5
    confidence = max(10, min(95, int(100 - stddev)))

    if method == 'linear':
        pred = linear_pred
    elif method == 'ewma':
        pred = ewma_pred
    else:  # ensemble
        pred = (linear_pred + ewma_pred) / 2

    # Clamp to reasonable range
    pred = max(0, min(100, pred))

    return {
        'prediction': round(pred, 1),
        'confidence': confidence,
        'method': method,
        'details': {
            'linear': round(linear_pred, 1),
            'ewma': round(ewma_pred, 1),
            'slope': round(slope, 3),
            'n_sessions': n,
        },
    }


def format_prediction(pred_result, student_name=''):
    """Format prediction result."""
    p = pred_result
    name = f" ({student_name})" if student_name else ''
    lines = [f"Prediction{name}"]
    lines.append("─" * 40)
    lines.append(f"  Next score: {p['prediction']}% "
                 f"(confidence: {p['confidence']}%)")
    lines.append(f"  Method: {p['method']}")

    d = p.get('details', {})
    if d:
        lines.append(f"  Linear: {d.get('linear', '?')}%  "
                     f"EWMA: {d.get('ewma', '?')}%")
        lines.append(f"  Trend slope: {d.get('slope', 0):+.3f}  "
                     f"Based on: {d.get('n_sessions', 0)} sessions")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# CURRICULUM SYSTEM (v35)
# ═══════════════════════════════════════════════════════════

class CurriculumUnit:
    """A single unit in the curriculum."""

    def __init__(self, unit_id, title, description, requirements,
                 template_id=None):
        self.unit_id = unit_id
        self.title = title
        self.description = description
        self.requirements = requirements  # dict: min_mastery, min_score, etc.
        self.template_id = template_id
        self.completed = False

    def check_completion(self, student):
        """Check if student meets unit requirements."""
        req = self.requirements
        ml = student.mastery_level
        scores = [s['pct'] for s in student.sessions]
        n = len(scores)
        recent = scores[-5:] if len(scores) >= 5 else scores
        avg = sum(recent) / len(recent) if recent else 0

        passed = True
        if 'min_mastery' in req and ml < req['min_mastery']:
            passed = False
        if 'min_score' in req and avg < req['min_score']:
            passed = False
        if 'min_sessions' in req and n < req['min_sessions']:
            passed = False
        if 'min_badges' in req:
            badges = check_badges(student)
            if len(badges) < req['min_badges']:
                passed = False

        self.completed = passed
        return passed


class Curriculum:
    """
    Structured learning curriculum with ordered units.

    Units progress from fundamentals through mastery.
    """

    def __init__(self, name='Scarab Standard Curriculum'):
        self.name = name
        self.units = []

    def add_unit(self, unit):
        """Add a unit to the curriculum."""
        self.units.append(unit)

    def build_standard(self):
        """Build the standard Scarab curriculum."""
        standard_units = [
            ('U01', 'Foundations', 'Basic symbols and zones',
             {'min_sessions': 1}, 'warmup'),
            ('U02', 'Zone Mastery', 'Accurate zone placement',
             {'min_sessions': 3, 'min_score': 55}, 'drill_zone'),
            ('U03', 'Group Awareness', 'Kryukov group transitions',
             {'min_sessions': 5, 'min_score': 60}, 'group_flow'),
            ('U04', 'Consistency', 'Maintain steady performance',
             {'min_sessions': 8, 'min_score': 65, 'min_mastery': 2}, None),
            ('U05', 'Intermediate Flow', 'Complex sequences',
             {'min_sessions': 10, 'min_score': 70, 'min_mastery': 3},
             'endurance'),
            ('U06', 'Speed & Precision', 'Fast accurate execution',
             {'min_sessions': 12, 'min_score': 75, 'min_mastery': 3},
             'speed_run'),
            ('U07', 'Advanced Techniques', 'High-group symbols',
             {'min_sessions': 15, 'min_score': 80, 'min_mastery': 4}, None),
            ('U08', 'Peak Defense', 'Group 7 mastery',
             {'min_sessions': 20, 'min_score': 85, 'min_mastery': 5},
             'peak_challenge'),
            ('U09', 'Mastery', 'Full proficiency',
             {'min_sessions': 25, 'min_score': 90, 'min_mastery': 6,
              'min_badges': 8}, None),
            ('U10', 'Grand Master', 'Peak performance',
             {'min_sessions': 30, 'min_score': 95, 'min_mastery': 7,
              'min_badges': 10}, None),
        ]

        for uid, title, desc, reqs, tmpl in standard_units:
            self.add_unit(CurriculumUnit(uid, title, desc, reqs, tmpl))

        return self

    def evaluate(self, student):
        """Evaluate student progress through curriculum."""
        results = []
        current_unit = None
        for unit in self.units:
            passed = unit.check_completion(student)
            results.append({
                'unit_id': unit.unit_id,
                'title': unit.title,
                'completed': passed,
                'template': unit.template_id,
            })
            if not passed and current_unit is None:
                current_unit = unit

        completed = sum(1 for r in results if r['completed'])
        return {
            'student': student.name,
            'total_units': len(self.units),
            'completed': completed,
            'progress_pct': round(completed / len(self.units) * 100, 1)
                            if self.units else 0,
            'current_unit': current_unit,
            'units': results,
        }

    def format_curriculum(self, eval_result):
        """Format curriculum progress."""
        lines = [f"Curriculum: {self.name}"]
        lines.append(f"Student: {eval_result['student']}")
        lines.append("═" * 55)

        for r in eval_result['units']:
            icon = '✓' if r['completed'] else '○'
            tmpl = f" [{r['template']}]" if r['template'] else ''
            lines.append(f"  {icon} {r['unit_id']} {r['title']}{tmpl}")

        cu = eval_result['current_unit']
        curr_str = cu.title if cu else 'COMPLETE'
        lines.append("─" * 55)
        lines.append(f"  Progress: {eval_result['completed']}/"
                     f"{eval_result['total_units']} "
                     f"({eval_result['progress_pct']}%)  "
                     f"Current: {curr_str}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SCHOOL PROGRESS TRACKER (v35)
# ═══════════════════════════════════════════════════════════

def school_progress_overview(school, curriculum=None):
    """
    Compute school-wide progress overview.

    Aggregates stats across all students.
    """
    students = school.students
    n = len(students)
    if n == 0:
        return {'n_students': 0}

    all_scores = []
    all_sessions = 0
    masteries = []
    badge_counts = []

    for name, st in students.items():
        scores = [s['pct'] for s in st.sessions]
        all_scores.extend(scores)
        all_sessions += len(scores)
        masteries.append(st.mastery_level)
        badge_counts.append(len(check_badges(st)))

    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    avg_mastery = round(sum(masteries) / n, 1)
    avg_badges = round(sum(badge_counts) / n, 1)

    # Curriculum progress per student
    curriculum_data = []
    if curriculum:
        for name, st in students.items():
            ev = curriculum.evaluate(st)
            curriculum_data.append({
                'name': name,
                'progress': ev['progress_pct'],
                'completed': ev['completed'],
                'total': ev['total_units'],
            })

    return {
        'school_name': school.name,
        'n_students': n,
        'total_sessions': all_sessions,
        'avg_score': avg_score,
        'avg_mastery': avg_mastery,
        'avg_badges': avg_badges,
        'mastery_distribution': {
            i: sum(1 for m in masteries if m == i) for i in range(1, 8)
        },
        'curriculum': curriculum_data,
    }


def format_school_overview(overview):
    """Format school progress overview."""
    lines = []
    lines.append("╔" + "═" * 56 + "╗")
    title = f"School Overview: {overview['school_name']}"
    lines.append("║" + f"  {title:^52s}" + "  ║")
    lines.append("╚" + "═" * 56 + "╝")

    lines.append(f"\n  Students: {overview['n_students']}  |  "
                 f"Total sessions: {overview['total_sessions']}")
    lines.append(f"  Avg score: {overview['avg_score']}%  |  "
                 f"Avg mastery: L{overview['avg_mastery']}  |  "
                 f"Avg badges: {overview['avg_badges']}")

    # Mastery distribution
    md = overview['mastery_distribution']
    lines.append("\n  Mastery Distribution:")
    for lvl in range(1, 8):
        count = md.get(lvl, 0)
        bar = '█' * (count * 3)
        lines.append(f"    L{lvl}: {bar} {count}")

    # Curriculum
    if overview['curriculum']:
        lines.append("\n  Curriculum Progress:")
        for cd in overview['curriculum']:
            bar_len = int(cd['progress'] / 5)
            bar = '▓' * bar_len + '░' * (20 - bar_len)
            lines.append(f"    {cd['name']:12s} [{bar}] "
                         f"{cd['completed']}/{cd['total']} "
                         f"({cd['progress']}%)")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# GRAND ARCHITECTURE SUMMARY (v35)
# ═══════════════════════════════════════════════════════════

def architecture_summary():
    """
    Generate a summary of the entire Scarab algorithm architecture.

    Lists all major components with version and category.
    """
    components = [
        # (name, version, category)
        ('Symbol mapping (64 sym, 7 groups)', 'v1', 'Core'),
        ('Zone rules (R1-R5)', 'v1', 'Core'),
        ('Dual-path tact structure', 'v1', 'Core'),
        ('StudentTracker', 'v2', 'Tracking'),
        ('Mastery levels (L1-L7)', 'v3', 'Progression'),
        ('ScarabSchool', 'v7', 'Management'),
        ('Library system', 'v8', 'Content'),
        ('Session generation', 'v9', 'Training'),
        ('Violation engine', 'v10', 'Validation'),
        ('Resonance analysis', 'v11', 'Analysis'),
        ('Group interaction matrix', 'v12', 'Analysis'),
        ('Adaptive difficulty', 'v13', 'Training'),
        ('ELO rating system', 'v14', 'Ranking'),
        ('Export/Import JSON', 'v15', 'Data'),
        ('Tournament system', 'v16', 'Competition'),
        ('Multi-school federation', 'v17', 'Management'),
        ('SVG diagram generator', 'v18', 'Visualization'),
        ('Compact kata notation', 'v19', 'Encoding'),
        ('Timeline system', 'v20', 'History'),
        ('Group×Rule heatmap', 'v21', 'Analysis'),
        ('Matchmaking', 'v22', 'Competition'),
        ('Graduation system', 'v23', 'Progression'),
        ('Kata grading engine', 'v25', 'Assessment'),
        ('Kata diff / comparison', 'v28', 'Analysis'),
        ('Achievement / badge system', 'v28', 'Gamification'),
        ('Annotated replay', 'v28', 'Review'),
        ('Data export CSV/JSON', 'v29', 'Data'),
        ('Notification manager', 'v29', 'Communication'),
        ('Report generator', 'v29', 'Reporting'),
        ('Training scheduler', 'v30', 'Planning'),
        ('Analytics dashboard', 'v30', 'Analysis'),
        ('Custom rule builder', 'v30', 'Validation'),
        ('Goal tracking', 'v31', 'Progression'),
        ('Peer comparison', 'v31', 'Ranking'),
        ('Session playback', 'v31', 'Review'),
        ('Training templates', 'v32', 'Training'),
        ('Correlation analysis', 'v32', 'Analysis'),
        ('System configuration', 'v32', 'Core'),
        ('Feedback loop', 'v33', 'Training'),
        ('Progression path', 'v33', 'Visualization'),
        ('Session heatmap', 'v33', 'Visualization'),
        ('Event log', 'v34', 'Logging'),
        ('Kata difficulty scorer', 'v34', 'Assessment'),
        ('Performance predictor', 'v34', 'Analysis'),
        ('Curriculum system', 'v35', 'Progression'),
        ('School progress tracker', 'v35', 'Management'),
    ]

    # Group by category
    categories = {}
    for name, ver, cat in components:
        categories.setdefault(cat, []).append((name, ver))

    lines = ["SCARAB ALGORITHM — Architecture Summary"]
    lines.append("═" * 55)
    lines.append(f"  Components: {len(components)}  |  "
                 f"Categories: {len(categories)}  |  "
                 f"Versions: v1-v35")

    for cat in sorted(categories.keys()):
        items = categories[cat]
        lines.append(f"\n  [{cat}] ({len(items)} components)")
        for name, ver in items:
            lines.append(f"    {ver:4s} │ {name}")

    lines.append("\n" + "═" * 55)
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SKILL TREE SYSTEM (v36)
# ═══════════════════════════════════════════════════════════

class SkillNode:
    """A single node in the skill tree."""

    def __init__(self, node_id, name, description, category,
                 prerequisites=None, unlock_condition=None):
        self.node_id = node_id
        self.name = name
        self.description = description
        self.category = category
        self.prerequisites = prerequisites or []
        self.unlock_condition = unlock_condition or {}
        self.unlocked = False
        self.level = 0  # 0=locked, 1-3=proficiency

    def check_unlock(self, student, unlocked_nodes):
        """Check if this node can be unlocked."""
        # Check prerequisites
        for pre in self.prerequisites:
            if pre not in unlocked_nodes:
                return False

        cond = self.unlock_condition
        if 'min_mastery' in cond:
            if student.mastery_level < cond['min_mastery']:
                return False
        if 'min_sessions' in cond:
            if len(student.sessions) < cond['min_sessions']:
                return False
        if 'min_score' in cond:
            scores = [s['pct'] for s in student.sessions]
            recent = scores[-5:] if len(scores) >= 5 else scores
            avg = sum(recent) / len(recent) if recent else 0
            if avg < cond['min_score']:
                return False

        return True


class SkillTree:
    """
    RPG-style skill tree for tracking student capabilities.

    Categories: Fundamentals, Technique, Mastery, Special.
    """

    def __init__(self):
        self.nodes = {}
        self._build_default()

    def _build_default(self):
        """Build the default skill tree."""
        tree_def = [
            # Fundamentals
            ('F1', 'Symbol Recognition', 'Identify all 64 symbols',
             'Fundamentals', [], {'min_sessions': 1}),
            ('F2', 'Zone Basics', 'Understand R1 zone rules',
             'Fundamentals', ['F1'], {'min_sessions': 3}),
            ('F3', 'Group Awareness', 'Know all 7 Kryukov groups',
             'Fundamentals', ['F1'], {'min_sessions': 3}),
            ('F4', 'Dual Path', 'Master dual-path tact structure',
             'Fundamentals', ['F2', 'F3'], {'min_sessions': 5}),

            # Technique
            ('T1', 'Consistency', 'Score 65%+ for 5 sessions',
             'Technique', ['F4'], {'min_sessions': 5, 'min_score': 65}),
            ('T2', 'Flow State', 'Smooth group transitions',
             'Technique', ['T1'], {'min_sessions': 8, 'min_score': 70}),
            ('T3', 'Speed', 'Handle speed-run templates',
             'Technique', ['T1'], {'min_mastery': 3}),
            ('T4', 'Endurance', 'Complete 24-tact sessions',
             'Technique', ['T2'], {'min_mastery': 3, 'min_score': 75}),

            # Mastery
            ('M1', 'Advanced Groups', 'Work with G5-G6',
             'Mastery', ['T2'], {'min_mastery': 4, 'min_score': 80}),
            ('M2', 'Peak Defense', 'Handle G7 peak defense',
             'Mastery', ['M1'], {'min_mastery': 5, 'min_score': 85}),
            ('M3', 'Grand Mastery', 'Reach mastery level 7',
             'Mastery', ['M2'], {'min_mastery': 7, 'min_score': 90}),

            # Special
            ('S1', 'Analyst', 'Understand correlation data',
             'Special', ['T1'], {'min_sessions': 10}),
            ('S2', 'Competitor', 'Participate in tournaments',
             'Special', ['T1'], {'min_mastery': 3}),
            ('S3', 'Mentor', 'Help other students',
             'Special', ['M1'], {'min_mastery': 5, 'min_sessions': 20}),
        ]

        for nid, name, desc, cat, prereqs, cond in tree_def:
            self.nodes[nid] = SkillNode(nid, name, desc, cat, prereqs, cond)

    def evaluate(self, student):
        """Evaluate which nodes are unlocked for student."""
        unlocked = set()
        changed = True

        while changed:
            changed = False
            for nid, node in self.nodes.items():
                if nid not in unlocked:
                    if node.check_unlock(student, unlocked):
                        node.unlocked = True
                        node.level = 1
                        unlocked.add(nid)
                        changed = True

        return unlocked

    def format_tree(self, student_name=''):
        """Format skill tree display."""
        lines = [f"Skill Tree{' — ' + student_name if student_name else ''}"]
        lines.append("═" * 50)

        categories = {}
        for nid, node in self.nodes.items():
            categories.setdefault(node.category, []).append(node)

        for cat in ['Fundamentals', 'Technique', 'Mastery', 'Special']:
            nodes = categories.get(cat, [])
            lines.append(f"\n  [{cat}]")
            for n in nodes:
                icon = '●' if n.unlocked else '○'
                prereqs = f" (needs: {','.join(n.prerequisites)})" \
                    if n.prerequisites and not n.unlocked else ''
                lines.append(f"    {icon} {n.node_id} {n.name}{prereqs}")

        unlocked = sum(1 for n in self.nodes.values() if n.unlocked)
        total = len(self.nodes)
        lines.append(f"\n  Unlocked: {unlocked}/{total}")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SESSION SIMULATOR (v36)
# ═══════════════════════════════════════════════════════════

class SessionSimulator:
    """
    Monte Carlo session simulator.

    Simulates possible outcomes based on student's current stats
    to predict score distributions and risk.
    """

    def __init__(self, student, n_simulations=100):
        self.student = student
        self.n_simulations = n_simulations

    def simulate(self, n_tacts=14, seed=None):
        """Run Monte Carlo simulation."""
        import random as _rnd_sim
        if seed is not None:
            _rnd_sim.seed(seed)

        scores = [s['pct'] for s in self.student.sessions]
        if not scores:
            mean, std = 50, 15
        else:
            mean = sum(scores) / len(scores)
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            std = max(variance ** 0.5, 3)

        results = []
        for _ in range(self.n_simulations):
            sim_score = _rnd_sim.gauss(mean, std)
            sim_score = max(0, min(100, sim_score))
            results.append(round(sim_score, 1))

        results.sort()
        n = len(results)

        return {
            'n': n,
            'mean': round(sum(results) / n, 1),
            'median': results[n // 2],
            'std': round(std, 1),
            'p10': results[n // 10],
            'p25': results[n // 4],
            'p75': results[3 * n // 4],
            'p90': results[9 * n // 10],
            'min': results[0],
            'max': results[-1],
            'pass_rate': round(
                sum(1 for r in results if r >= 70) / n * 100, 1),
            'distribution': results,
        }

    def format_simulation(self, sim_result):
        """Format simulation results."""
        r = sim_result
        lines = [f"Session Simulation ({r['n']} runs)"]
        lines.append("─" * 45)
        lines.append(f"  Mean: {r['mean']}%  |  Median: {r['median']}%  "
                     f"|  Std: {r['std']}%")
        lines.append(f"  Range: [{r['min']}% — {r['max']}%]")
        lines.append(f"  P10: {r['p10']}%  P25: {r['p25']}%  "
                     f"P75: {r['p75']}%  P90: {r['p90']}%")
        lines.append(f"  Pass rate (≥70%): {r['pass_rate']}%")

        # Mini histogram
        buckets = [0] * 10
        for v in r['distribution']:
            idx = min(int(v / 10), 9)
            buckets[idx] += 1

        lines.append("\n  Distribution:")
        max_b = max(buckets) if buckets else 1
        for i in range(9, -1, -1):
            lo, hi = i * 10, (i + 1) * 10
            bar_len = int(buckets[i] / max_b * 20) if max_b else 0
            bar = '▓' * bar_len
            lines.append(f"    {lo:3d}-{hi:3d}% │{bar} {buckets[i]}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# LEADERBOARD SYSTEM (v36)
# ═══════════════════════════════════════════════════════════

class Leaderboard:
    """
    Multi-metric leaderboard with ranking history.

    Supports different ranking modes: score, mastery, ELO,
    badges, sessions, curriculum progress.
    """

    METRICS = ['score', 'mastery', 'elo', 'badges', 'sessions']

    def __init__(self, school):
        self.school = school
        self.history = []  # snapshots

    def _get_value(self, student, metric):
        """Get a student's value for a given metric."""
        if metric == 'score':
            scores = [s['pct'] for s in student.sessions]
            return round(sum(scores) / len(scores), 1) if scores else 0
        elif metric == 'mastery':
            return student.mastery_level
        elif metric == 'elo':
            return getattr(student, 'elo', 1200)
        elif metric == 'badges':
            return len(check_badges(student))
        elif metric == 'sessions':
            return len(student.sessions)
        return 0

    def rank(self, metric='score'):
        """Rank all students by a metric."""
        entries = []
        for name, st in self.school.students.items():
            val = self._get_value(st, metric)
            entries.append({'name': name, 'value': val})

        entries.sort(key=lambda e: e['value'], reverse=True)

        for i, e in enumerate(entries):
            e['rank'] = i + 1

        return entries

    def snapshot(self):
        """Take a snapshot of current rankings."""
        snap = {}
        for metric in self.METRICS:
            snap[metric] = self.rank(metric)
        self.history.append(snap)
        return snap

    def composite_rank(self):
        """
        Composite ranking: average rank across all metrics.
        Lower average = better overall.
        """
        rank_sums = {}
        for metric in self.METRICS:
            ranked = self.rank(metric)
            for e in ranked:
                rank_sums.setdefault(e['name'], []).append(e['rank'])

        composite = []
        for name, ranks in rank_sums.items():
            avg_rank = round(sum(ranks) / len(ranks), 2)
            composite.append({
                'name': name,
                'avg_rank': avg_rank,
                'ranks': dict(zip(self.METRICS, ranks)),
            })

        composite.sort(key=lambda e: e['avg_rank'])
        for i, e in enumerate(composite):
            e['overall_rank'] = i + 1

        return composite

    def format_leaderboard(self, metric='score'):
        """Format single-metric leaderboard."""
        ranked = self.rank(metric)
        lines = [f"Leaderboard: {metric.upper()}"]
        lines.append("─" * 40)

        medals = {1: '🥇', 2: '🥈', 3: '🥉'}
        for e in ranked:
            medal = medals.get(e['rank'], '  ')
            lines.append(f"  {medal} #{e['rank']}  {e['name']:12s}  "
                         f"{e['value']}")

        return '\n'.join(lines)

    def format_composite(self):
        """Format composite leaderboard."""
        comp = self.composite_rank()
        lines = ["Composite Leaderboard"]
        lines.append("═" * 55)

        for e in comp:
            r = e['ranks']
            rank_str = ' '.join(f"{m[0].upper()}{r[m]}" for m in self.METRICS)
            lines.append(f"  #{e['overall_rank']}  {e['name']:12s}  "
                         f"avg={e['avg_rank']:.2f}  [{rank_str}]")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PATTERN RECOGNITION ENGINE (v37)
# ═══════════════════════════════════════════════════════════

def detect_patterns(student, window=5):
    """
    Detect recurring performance patterns in student data.

    Pattern types:
    - warmup_effect: first 2-3 sessions always low
    - fatigue: score drops in later part of session
    - group_weakness: consistently low on specific groups
    - inconsistency: high variance between sessions
    - steady_climb: consistent improvement
    """
    sessions = student.sessions
    scores = [s['pct'] for s in sessions]
    n = len(scores)
    if n < 4:
        return []

    patterns = []

    # Warmup effect: first sessions in each window tend lower
    if n >= 6:
        first_thirds = [scores[i] for i in range(0, n, 3) if i < n]
        other = [scores[i] for i in range(n) if i % 3 != 0]
        avg_first = sum(first_thirds) / len(first_thirds)
        avg_other = sum(other) / len(other) if other else avg_first
        if avg_other - avg_first > 5:
            patterns.append({
                'type': 'warmup_effect',
                'delta': round(avg_other - avg_first, 1),
                'description': f'First tacts avg {avg_first:.0f}% vs '
                               f'rest {avg_other:.0f}% '
                               f'(gap: {avg_other - avg_first:.1f})',
            })

    # Inconsistency: high variance
    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / n
    if variance > 200:
        patterns.append({
            'type': 'inconsistency',
            'variance': round(variance, 1),
            'description': f'High variance σ²={variance:.0f} '
                           f'(σ={variance**0.5:.1f})',
        })

    # Steady climb: positive slope
    x_mean = (n - 1) / 2
    num = sum((i - x_mean) * (scores[i] - mean) for i in range(n))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den > 0 else 0
    if slope > 2:
        patterns.append({
            'type': 'steady_climb',
            'slope': round(slope, 2),
            'description': f'Consistent improvement '
                           f'(slope: +{slope:.2f}/session)',
        })
    elif slope < -2:
        patterns.append({
            'type': 'decline',
            'slope': round(slope, 2),
            'description': f'Performance declining '
                           f'(slope: {slope:.2f}/session)',
        })

    # Plateau detection
    recent = scores[-window:]
    r_mean = sum(recent) / len(recent)
    r_var = sum((s - r_mean) ** 2 for s in recent) / len(recent)
    if r_var < 8 and abs(slope) < 1:
        patterns.append({
            'type': 'plateau',
            'level': round(r_mean, 1),
            'description': f'Plateau at {r_mean:.0f}% '
                           f'(σ²={r_var:.1f})',
        })

    return patterns


def format_detected_patterns(patterns, student_name=''):
    """Format detected performance patterns."""
    name = f" ({student_name})" if student_name else ''
    lines = [f"Pattern Analysis{name}"]
    lines.append("─" * 45)

    if not patterns:
        lines.append("  No significant patterns detected.")
    else:
        for p in patterns:
            lines.append(f"  [{p['type']}]")
            lines.append(f"    {p['description']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# MENTOR SYSTEM (v37)
# ═══════════════════════════════════════════════════════════

class Mentor:
    """
    Virtual mentor that provides guidance based on student state.

    Combines analysis from multiple systems to give actionable advice.
    """

    def __init__(self, student):
        self.student = student

    def assess(self):
        """Full assessment of student's current state."""
        st = self.student
        sessions = st.sessions
        scores = [s['pct'] for s in sessions]
        n = len(scores)

        assessment = {
            'name': st.name,
            'sessions': n,
            'mastery': st.mastery_level,
            'overall': 'unknown',
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
        }

        if n == 0:
            assessment['overall'] = 'new'
            assessment['recommendations'].append(
                'Start with the warmup template to learn basics.')
            return assessment

        avg = sum(scores) / n
        recent = scores[-5:] if n >= 5 else scores
        recent_avg = sum(recent) / len(recent)

        # Strengths
        if recent_avg >= 85:
            assessment['strengths'].append(
                f'Strong recent performance ({recent_avg:.0f}%)')
        if n >= 10:
            assessment['strengths'].append(
                f'Good experience ({n} sessions)')
        if st.mastery_level >= 4:
            assessment['strengths'].append(
                f'High mastery (L{st.mastery_level})')

        badges = check_badges(st)
        if len(badges) >= 5:
            assessment['strengths'].append(
                f'Diverse achievements ({len(badges)} badges)')

        # Weaknesses
        if recent_avg < 65:
            assessment['weaknesses'].append(
                f'Low recent scores ({recent_avg:.0f}%)')
        if n < 5:
            assessment['weaknesses'].append('Limited experience')

        patterns = detect_patterns(st)
        for p in patterns:
            if p['type'] in ('inconsistency', 'decline'):
                assessment['weaknesses'].append(p['description'])

        # Overall assessment
        if recent_avg >= 90:
            assessment['overall'] = 'excellent'
        elif recent_avg >= 75:
            assessment['overall'] = 'good'
        elif recent_avg >= 60:
            assessment['overall'] = 'developing'
        else:
            assessment['overall'] = 'struggling'

        # Recommendations
        if assessment['overall'] == 'excellent':
            assessment['recommendations'].append(
                'Ready for peak_challenge template or tournaments.')
            if st.mastery_level < 7:
                assessment['recommendations'].append(
                    f'Push for mastery L{st.mastery_level + 1}.')

        elif assessment['overall'] == 'good':
            assessment['recommendations'].append(
                'Focus on consistency. Try endurance sessions.')
            assessment['recommendations'].append(
                'Review weak groups with drill_zone template.')

        elif assessment['overall'] == 'developing':
            assessment['recommendations'].append(
                'Practice fundamentals. Use group_flow template.')
            assessment['recommendations'].append(
                'Aim for 70%+ average before advancing.')

        else:
            assessment['recommendations'].append(
                'Start with warmup sessions to build confidence.')
            assessment['recommendations'].append(
                'Focus on one group at a time.')

        return assessment

    def format_assessment(self, assessment=None):
        """Format mentor assessment."""
        a = assessment or self.assess()
        lines = [f"Mentor Assessment: {a['name']}"]
        lines.append("═" * 50)
        lines.append(f"  Status: {a['overall'].upper()}  |  "
                     f"Sessions: {a['sessions']}  |  "
                     f"Mastery: L{a['mastery']}")

        if a['strengths']:
            lines.append("\n  Strengths:")
            for s in a['strengths']:
                lines.append(f"    + {s}")

        if a['weaknesses']:
            lines.append("\n  Weaknesses:")
            for w in a['weaknesses']:
                lines.append(f"    - {w}")

        if a['recommendations']:
            lines.append("\n  Recommendations:")
            for r in a['recommendations']:
                lines.append(f"    → {r}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# DAILY CHALLENGE SYSTEM (v37)
# ═══════════════════════════════════════════════════════════

class DailyChallengeGenerator:
    """
    Generates daily training challenges based on student level.

    Challenge types: time_attack, accuracy, endurance,
    group_focus, streak.
    """

    CHALLENGE_TYPES = [
        'time_attack', 'accuracy', 'endurance',
        'group_focus', 'streak',
    ]

    def __init__(self, seed=None):
        import random as _rnd_dc
        self._rnd = _rnd_dc
        if seed is not None:
            self._rnd.seed(seed)

    def generate(self, student, day_number=1):
        """Generate a daily challenge for the student."""
        ml = student.mastery_level
        scores = [s['pct'] for s in student.sessions]
        avg = sum(scores) / len(scores) if scores else 50

        # Pick challenge type based on day rotation
        ch_type = self.CHALLENGE_TYPES[day_number % len(self.CHALLENGE_TYPES)]

        challenge = {
            'day': day_number,
            'type': ch_type,
            'title': '',
            'description': '',
            'target': 0,
            'reward': '',
            'difficulty': 'medium',
        }

        if ch_type == 'time_attack':
            n_tacts = 8 + ml
            target_score = max(60, int(avg - 5))
            challenge['title'] = f'Speed Challenge #{day_number}'
            challenge['description'] = (
                f'Complete {n_tacts} tacts with ≥{target_score}% average')
            challenge['target'] = target_score
            challenge['reward'] = '+10 ELO bonus'

        elif ch_type == 'accuracy':
            target = min(95, int(avg + 10))
            challenge['title'] = f'Precision Day #{day_number}'
            challenge['description'] = (
                f'Score ≥{target}% on any single session')
            challenge['target'] = target
            challenge['reward'] = 'Accuracy badge progress'

        elif ch_type == 'endurance':
            n_tacts = 16 + ml * 2
            challenge['title'] = f'Endurance Test #{day_number}'
            challenge['description'] = (
                f'Complete a {n_tacts}-tact session without dropping '
                f'below 60%')
            challenge['target'] = n_tacts
            challenge['reward'] = 'Endurance mastery XP'

        elif ch_type == 'group_focus':
            focus_group = (day_number % 7) + 1
            challenge['title'] = f'Group {focus_group} Focus #{day_number}'
            challenge['description'] = (
                f'Practice Group {focus_group} symbols exclusively')
            challenge['target'] = focus_group
            challenge['reward'] = f'G{focus_group} proficiency'

        elif ch_type == 'streak':
            streak_target = 3 + ml // 2
            challenge['title'] = f'Streak Challenge #{day_number}'
            challenge['description'] = (
                f'Win {streak_target} sessions in a row (≥70%)')
            challenge['target'] = streak_target
            challenge['reward'] = 'Streak badge progress'

        # Adjust difficulty
        if ml <= 2:
            challenge['difficulty'] = 'easy'
        elif ml >= 5:
            challenge['difficulty'] = 'hard'

        return challenge

    def generate_week(self, student, start_day=1):
        """Generate a week of challenges."""
        return [self.generate(student, start_day + i) for i in range(7)]

    def format_challenge(self, challenge):
        """Format a single challenge."""
        c = challenge
        lines = [f"Daily Challenge: {c['title']}"]
        lines.append("─" * 45)
        lines.append(f"  Type: {c['type']}  |  "
                     f"Difficulty: {c['difficulty']}")
        lines.append(f"  {c['description']}")
        lines.append(f"  Target: {c['target']}  |  "
                     f"Reward: {c['reward']}")
        return '\n'.join(lines)

    def format_week(self, challenges):
        """Format a week of challenges."""
        lines = ["Weekly Challenge Plan"]
        lines.append("═" * 50)
        for c in challenges:
            lines.append(f"  Day {c['day']}: [{c['type']:12s}] "
                         f"{c['title']} ({c['difficulty']})")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# STUDY GROUPS (v38)
# ═══════════════════════════════════════════════════════════

class StudyGroup:
    """
    Collaborative study group of students.

    Groups train together, share progress, and compete internally.
    """

    def __init__(self, name, max_size=6):
        self.name = name
        self.max_size = max_size
        self.members = {}  # name → student
        self.group_sessions = 0

    def add_member(self, student):
        """Add student to group."""
        if len(self.members) >= self.max_size:
            return False
        self.members[student.name] = student
        return True

    def remove_member(self, name):
        """Remove student from group."""
        return self.members.pop(name, None) is not None

    def group_average(self):
        """Average score across all members."""
        all_scores = []
        for st in self.members.values():
            scores = [s['pct'] for s in st.sessions]
            all_scores.extend(scores)
        return round(sum(all_scores) / len(all_scores), 1) \
            if all_scores else 0

    def internal_ranking(self):
        """Rank members by recent performance."""
        entries = []
        for name, st in self.members.items():
            scores = [s['pct'] for s in st.sessions]
            recent = scores[-5:] if len(scores) >= 5 else scores
            avg = sum(recent) / len(recent) if recent else 0
            entries.append({'name': name, 'avg': round(avg, 1),
                            'sessions': len(scores)})
        entries.sort(key=lambda e: e['avg'], reverse=True)
        return entries

    def format_group(self):
        """Format group display."""
        lines = [f"Study Group: {self.name}"]
        lines.append("═" * 45)
        lines.append(f"  Members: {len(self.members)}/{self.max_size}  |  "
                     f"Group avg: {self.group_average()}%")

        ranking = self.internal_ranking()
        for i, e in enumerate(ranking):
            lines.append(f"    {i + 1}. {e['name']:12s}  "
                         f"avg={e['avg']}%  ({e['sessions']} sess)")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SYMBOL ENCYCLOPEDIA (v38)
# ═══════════════════════════════════════════════════════════

def symbol_encyclopedia():
    """
    Generate a comprehensive encyclopedia of all 64 Scarab symbols.

    Each entry includes: symbol ID, group, zone, properties.
    """
    entries = []
    for sym in range(64):
        group = get_group(sym)
        zone = get_zones(sym)

        # Determine difficulty tier
        if group <= 2:
            tier = 'basic'
        elif group <= 4:
            tier = 'intermediate'
        elif group <= 6:
            tier = 'advanced'
        else:
            tier = 'expert'

        # Recommended mastery level
        rec_ml = max(1, (group + 1) // 2)

        entries.append({
            'sym': sym,
            'group': group,
            'zone': zone,
            'tier': tier,
            'rec_mastery': rec_ml,
            'hex': f'{sym:02X}',
            'binary': f'{sym:06b}',
        })

    return entries


def format_encyclopedia(entries, group_filter=None):
    """Format encyclopedia entries."""
    if group_filter is not None:
        entries = [e for e in entries if e['group'] == group_filter]

    lines = ["Symbol Encyclopedia"]
    if group_filter:
        lines[0] += f" — Group {group_filter}"
    lines.append("═" * 55)

    current_group = None
    for e in entries:
        if e['group'] != current_group:
            current_group = e['group']
            lines.append(f"\n  [Group {current_group}]")

        lines.append(f"    S{e['sym']:02d} │ 0x{e['hex']} │ "
                     f"{e['binary']} │ Z{e['zone']} │ "
                     f"{e['tier']} │ rec: L{e['rec_mastery']}")

    lines.append(f"\n  Total: {len(entries)} symbols")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# COMBO SYSTEM (v38)
# ═══════════════════════════════════════════════════════════

def detect_combos(tact_sequence):
    """
    Detect combos (special symbol sequences) in a tact list.

    Combo types:
    - same_group_3: 3+ consecutive same-group symbols
    - ascending: 3+ ascending symbols
    - full_cycle: all 7 groups touched
    - palindrome: palindromic group sequence
    - zone_sweep: hit all 4 zones
    """
    if not tact_sequence:
        return []

    groups = [get_group(s) for s in tact_sequence]
    zones = [get_zones(s) for s in tact_sequence]
    combos = []

    # Same group 3+
    streak = 1
    for i in range(1, len(groups)):
        if groups[i] == groups[i - 1]:
            streak += 1
            if streak == 3:
                combos.append({
                    'type': 'same_group_3',
                    'position': i - 2,
                    'length': streak,
                    'group': groups[i],
                    'bonus': 5,
                })
        else:
            streak = 1

    # Ascending symbols 3+
    asc = 1
    for i in range(1, len(tact_sequence)):
        if tact_sequence[i] > tact_sequence[i - 1]:
            asc += 1
            if asc == 3:
                combos.append({
                    'type': 'ascending',
                    'position': i - 2,
                    'length': asc,
                    'bonus': 3,
                })
        else:
            asc = 1

    # Full cycle: all 7 groups
    unique_groups = set(groups)
    if len(unique_groups) >= 7:
        combos.append({
            'type': 'full_cycle',
            'position': 0,
            'length': len(tact_sequence),
            'bonus': 10,
        })

    # Zone sweep: all 4 zones
    unique_zones = set(zones)
    if len(unique_zones) >= 4:
        combos.append({
            'type': 'zone_sweep',
            'position': 0,
            'length': len(tact_sequence),
            'bonus': 7,
        })

    # Palindrome (groups): check if group sequence is palindromic
    if len(groups) >= 5:
        mid = len(groups) // 2
        if groups[:mid] == groups[-mid:][::-1]:
            combos.append({
                'type': 'palindrome',
                'position': 0,
                'length': len(groups),
                'bonus': 15,
            })

    return combos


def format_combos(combos, title='Combo Analysis'):
    """Format detected combos."""
    lines = [title]
    lines.append("─" * 40)

    if not combos:
        lines.append("  No combos detected.")
    else:
        total_bonus = sum(c['bonus'] for c in combos)
        for c in combos:
            extra = f" G{c['group']}" if 'group' in c else ''
            lines.append(f"  [{c['type']}] pos={c['position']} "
                         f"len={c['length']}{extra}  "
                         f"+{c['bonus']} bonus")
        lines.append(f"  Total bonus: +{total_bonus}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# REVIEW QUEUE (v39)
# ═══════════════════════════════════════════════════════════

class ReviewQueue:
    """
    Priority queue for reviewing symbols/groups that need work.

    Items are scored by urgency: more mistakes = higher priority.
    """

    def __init__(self):
        self.items = {}  # key → {priority, data, review_count}

    def add(self, key, priority, data=None):
        """Add or update a review item."""
        if key in self.items:
            self.items[key]['priority'] = max(
                self.items[key]['priority'], priority)
        else:
            self.items[key] = {
                'priority': priority,
                'data': data or {},
                'review_count': 0,
            }

    def pop_next(self):
        """Get highest priority item."""
        if not self.items:
            return None
        key = max(self.items, key=lambda k: self.items[k]['priority'])
        item = self.items.pop(key)
        item['key'] = key
        return item

    def peek(self, n=5):
        """Peek at top N items without removing."""
        sorted_keys = sorted(
            self.items, key=lambda k: self.items[k]['priority'],
            reverse=True)[:n]
        return [(k, self.items[k]) for k in sorted_keys]

    def mark_reviewed(self, key):
        """Mark an item as reviewed (reduces priority)."""
        if key in self.items:
            self.items[key]['review_count'] += 1
            self.items[key]['priority'] *= 0.7  # Decay

    def size(self):
        return len(self.items)

    def format_queue(self, n=10):
        """Format queue display."""
        lines = [f"Review Queue ({self.size()} items)"]
        lines.append("─" * 40)

        top = self.peek(n)
        for i, (key, item) in enumerate(top):
            lines.append(f"  {i + 1}. [{key}] "
                         f"priority={item['priority']:.1f} "
                         f"reviews={item['review_count']}")

        return '\n'.join(lines)


def build_review_queue(student):
    """Build review queue from student's weak areas."""
    rq = ReviewQueue()
    sessions = student.sessions

    # Count errors per group
    group_errors = {g: 0 for g in range(1, 8)}
    group_seen = {g: 0 for g in range(1, 8)}

    for s in sessions:
        for v in s.get('violations', []):
            g = v.get('group', 1)
            if 1 <= g <= 7:
                group_errors[g] += 1

    # Score-based weakness
    scores = [s['pct'] for s in sessions]
    if scores:
        recent = scores[-5:] if len(scores) >= 5 else scores
        avg = sum(recent) / len(recent)

        # Low scoring areas get priority
        if avg < 70:
            rq.add('general_practice', 8,
                   {'reason': f'Low avg {avg:.0f}%'})

    # Group-specific priorities
    for g in range(1, 8):
        errs = group_errors[g]
        if errs > 0:
            rq.add(f'group_{g}', errs * 2,
                   {'reason': f'{errs} violations in G{g}'})

    # Add rule areas
    for rule_name in ['R1_Zone', 'R2_Adjacency', 'R3_Repetition']:
        rule_viols = sum(
            1 for s in sessions
            for v in s.get('violations', [])
            if v.get('rule', '') == rule_name)
        if rule_viols > 0:
            rq.add(f'rule_{rule_name}', rule_viols * 1.5,
                   {'reason': f'{rule_viols} violations'})

    return rq


# ═══════════════════════════════════════════════════════════
# SPACED REPETITION ENGINE (v39)
# ═══════════════════════════════════════════════════════════

class SpacedRepetition:
    """
    SM-2 inspired spaced repetition for symbol practice.

    Each item has: ease_factor, interval, repetitions.
    """

    def __init__(self):
        self.cards = {}  # symbol → card state

    def add_card(self, symbol):
        """Add a new card for a symbol."""
        self.cards[symbol] = {
            'ease': 2.5,
            'interval': 1,
            'repetitions': 0,
            'next_review': 0,  # session number
        }

    def review(self, symbol, quality, current_session):
        """
        Review a card with quality 0-5 (SM-2 scale).

        0-1: complete blackout
        2: wrong but recognized
        3: correct with difficulty
        4: correct with hesitation
        5: perfect
        """
        if symbol not in self.cards:
            self.add_card(symbol)

        card = self.cards[symbol]

        if quality >= 3:
            if card['repetitions'] == 0:
                card['interval'] = 1
            elif card['repetitions'] == 1:
                card['interval'] = 3
            else:
                card['interval'] = round(
                    card['interval'] * card['ease'])

            card['repetitions'] += 1
        else:
            card['repetitions'] = 0
            card['interval'] = 1

        # Update ease factor
        card['ease'] = max(1.3,
            card['ease'] + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        card['next_review'] = current_session + card['interval']
        return card

    def due_cards(self, current_session):
        """Get cards due for review."""
        due = []
        for sym, card in self.cards.items():
            if card['next_review'] <= current_session:
                due.append((sym, card))
        due.sort(key=lambda x: x[1]['next_review'])
        return due

    def stats(self):
        """Get repetition stats."""
        cards = list(self.cards.values())
        if not cards:
            return {'total': 0, 'avg_ease': 0, 'avg_interval': 0}

        return {
            'total': len(cards),
            'avg_ease': round(
                sum(c['ease'] for c in cards) / len(cards), 2),
            'avg_interval': round(
                sum(c['interval'] for c in cards) / len(cards), 1),
            'mastered': sum(1 for c in cards if c['repetitions'] >= 5),
            'learning': sum(1 for c in cards if 0 < c['repetitions'] < 5),
            'new': sum(1 for c in cards if c['repetitions'] == 0),
        }

    def format_srs(self, current_session=0):
        """Format SRS status."""
        st = self.stats()
        due = self.due_cards(current_session)

        lines = [f"Spaced Repetition ({st['total']} cards)"]
        lines.append("─" * 45)
        lines.append(f"  Mastered: {st['mastered']}  |  "
                     f"Learning: {st['learning']}  |  "
                     f"New: {st['new']}")
        lines.append(f"  Avg ease: {st['avg_ease']}  |  "
                     f"Avg interval: {st['avg_interval']} sessions")
        lines.append(f"  Due now: {len(due)} cards")

        if due:
            lines.append("  Next due:")
            for sym, card in due[:5]:
                lines.append(f"    S{sym:02d} (G{get_group(sym)})  "
                             f"ease={card['ease']:.2f}  "
                             f"reps={card['repetitions']}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# WEAKNESS ANALYZER (v39)
# ═══════════════════════════════════════════════════════════

def analyze_weaknesses(student):
    """
    Deep analysis of student weaknesses.

    Returns structured weakness report with severity and
    recommended remediation.
    """
    sessions = student.sessions
    scores = [s['pct'] for s in sessions]
    n = len(scores)

    weaknesses = []

    if n == 0:
        return [{'area': 'experience', 'severity': 'high',
                 'detail': 'No sessions completed',
                 'remedy': 'Begin with warmup template'}]

    avg = sum(scores) / n
    recent = scores[-5:] if n >= 5 else scores
    recent_avg = sum(recent) / len(recent)

    # Score weakness
    if recent_avg < 65:
        weaknesses.append({
            'area': 'overall_score',
            'severity': 'high',
            'detail': f'Recent avg only {recent_avg:.0f}%',
            'remedy': 'Focus on fundamentals, use easier templates',
        })
    elif recent_avg < 75:
        weaknesses.append({
            'area': 'overall_score',
            'severity': 'medium',
            'detail': f'Recent avg {recent_avg:.0f}% — room to improve',
            'remedy': 'Practice consistency with group_flow template',
        })

    # Variance weakness
    if n >= 5:
        variance = sum((s - avg) ** 2 for s in scores) / n
        if variance > 200:
            weaknesses.append({
                'area': 'consistency',
                'severity': 'high',
                'detail': f'High variance σ²={variance:.0f}',
                'remedy': 'Focus on maintaining steady performance',
            })
        elif variance > 100:
            weaknesses.append({
                'area': 'consistency',
                'severity': 'medium',
                'detail': f'Moderate variance σ²={variance:.0f}',
                'remedy': 'Practice more to stabilize scores',
            })

    # Trend weakness
    if n >= 4:
        x_mean = (n - 1) / 2
        num = sum((i - x_mean) * (scores[i] - avg) for i in range(n))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den > 0 else 0
        if slope < -2:
            weaknesses.append({
                'area': 'trend',
                'severity': 'medium',
                'detail': f'Declining trend (slope: {slope:.2f})',
                'remedy': 'Take a break, review basics, then resume',
            })

    # Mastery weakness
    ml = student.mastery_level
    expected_ml = min(7, n // 4 + 1)
    if ml < expected_ml - 1:
        weaknesses.append({
            'area': 'mastery_lag',
            'severity': 'medium',
            'detail': f'Mastery L{ml} vs expected L{expected_ml}',
            'remedy': 'Complete mastery requirements to advance',
        })

    # No weaknesses found
    if not weaknesses:
        weaknesses.append({
            'area': 'none',
            'severity': 'positive',
            'detail': 'No significant weaknesses detected',
            'remedy': 'Continue current approach',
        })

    return weaknesses


def format_weaknesses(weaknesses, student_name=''):
    """Format weakness analysis."""
    name = f" — {student_name}" if student_name else ''
    lines = [f"Weakness Analysis{name}"]
    lines.append("═" * 50)

    sev_icons = {'high': '🔴', 'medium': '🟡', 'positive': '🟢'}

    for w in weaknesses:
        icon = sev_icons.get(w['severity'], '⚪')
        lines.append(f"\n  {icon} {w['area']} ({w['severity']})")
        lines.append(f"     {w['detail']}")
        lines.append(f"     → {w['remedy']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ADVANCED STATISTICS ENGINE (v40)
# ═══════════════════════════════════════════════════════════

class StatisticsEngine:
    """
    Comprehensive statistics engine for Scarab data.

    Computes descriptive stats, percentiles, confidence intervals,
    and comparative metrics.
    """

    @staticmethod
    def descriptive(values):
        """Full descriptive statistics for a list of values."""
        if not values:
            return {'n': 0}

        n = len(values)
        values_sorted = sorted(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = variance ** 0.5

        # Median
        if n % 2 == 0:
            median = (values_sorted[n // 2 - 1] + values_sorted[n // 2]) / 2
        else:
            median = values_sorted[n // 2]

        # Mode (most frequent)
        freq = {}
        for v in values:
            rv = round(v, 1)
            freq[rv] = freq.get(rv, 0) + 1
        mode = max(freq, key=freq.get)

        # Skewness
        if std > 0 and n >= 3:
            skew = sum((v - mean) ** 3 for v in values) / (n * std ** 3)
        else:
            skew = 0

        return {
            'n': n,
            'mean': round(mean, 2),
            'median': round(median, 2),
            'mode': mode,
            'std': round(std, 2),
            'variance': round(variance, 2),
            'min': round(values_sorted[0], 2),
            'max': round(values_sorted[-1], 2),
            'range': round(values_sorted[-1] - values_sorted[0], 2),
            'skew': round(skew, 3),
            'p25': round(values_sorted[n // 4], 2),
            'p75': round(values_sorted[3 * n // 4], 2),
            'iqr': round(values_sorted[3 * n // 4] -
                         values_sorted[n // 4], 2),
        }

    @staticmethod
    def confidence_interval(values, confidence=0.95):
        """Compute confidence interval for the mean."""
        n = len(values)
        if n < 2:
            return (0, 0)
        mean = sum(values) / n
        std = (sum((v - mean) ** 2 for v in values) / (n - 1)) ** 0.5
        # z-values for common confidence levels
        z_map = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        z = z_map.get(confidence, 1.96)
        margin = z * std / (n ** 0.5)
        return (round(mean - margin, 2), round(mean + margin, 2))

    @staticmethod
    def effect_size(group_a, group_b):
        """Cohen's d effect size between two groups."""
        na, nb = len(group_a), len(group_b)
        if na < 2 or nb < 2:
            return 0
        ma = sum(group_a) / na
        mb = sum(group_b) / nb
        va = sum((v - ma) ** 2 for v in group_a) / (na - 1)
        vb = sum((v - mb) ** 2 for v in group_b) / (nb - 1)
        pooled = ((va * (na - 1) + vb * (nb - 1)) / (na + nb - 2)) ** 0.5
        if pooled == 0:
            return 0
        return round((ma - mb) / pooled, 3)

    def student_report(self, student):
        """Full statistical report for a student."""
        scores = [s['pct'] for s in student.sessions]
        desc = self.descriptive(scores)
        ci = self.confidence_interval(scores)

        return {
            'name': student.name,
            'descriptive': desc,
            'confidence_interval_95': ci,
            'mastery': student.mastery_level,
        }

    def format_report(self, report):
        """Format statistical report."""
        d = report['descriptive']
        ci = report['confidence_interval_95']

        lines = [f"Statistical Report: {report['name']}"]
        lines.append("═" * 55)

        if d['n'] == 0:
            lines.append("  No data available.")
            return '\n'.join(lines)

        lines.append(f"  N={d['n']}  Mean={d['mean']}  "
                     f"Median={d['median']}  Mode={d['mode']}")
        lines.append(f"  Std={d['std']}  Var={d['variance']}  "
                     f"Range=[{d['min']}—{d['max']}]={d['range']}")
        lines.append(f"  Q1={d['p25']}  Q3={d['p75']}  "
                     f"IQR={d['iqr']}  Skew={d['skew']}")
        lines.append(f"  95% CI: [{ci[0]} — {ci[1]}]")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ACHIEVEMENT GALLERY (v40)
# ═══════════════════════════════════════════════════════════

ACHIEVEMENT_CATALOG = {
    # Tier 1: Bronze
    'first_session': {
        'name': 'First Steps', 'tier': 'bronze',
        'description': 'Complete your first session',
        'condition': lambda st: len(st.sessions) >= 1,
    },
    'five_sessions': {
        'name': 'Getting Started', 'tier': 'bronze',
        'description': 'Complete 5 sessions',
        'condition': lambda st: len(st.sessions) >= 5,
    },
    'score_60': {
        'name': 'Passing Grade', 'tier': 'bronze',
        'description': 'Score 60% or higher',
        'condition': lambda st: any(
            s['pct'] >= 60 for s in st.sessions),
    },

    # Tier 2: Silver
    'ten_sessions': {
        'name': 'Dedicated', 'tier': 'silver',
        'description': 'Complete 10 sessions',
        'condition': lambda st: len(st.sessions) >= 10,
    },
    'score_80': {
        'name': 'High Achiever', 'tier': 'silver',
        'description': 'Score 80% or higher',
        'condition': lambda st: any(
            s['pct'] >= 80 for s in st.sessions),
    },
    'mastery_3': {
        'name': 'Skilled', 'tier': 'silver',
        'description': 'Reach mastery level 3',
        'condition': lambda st: st.mastery_level >= 3,
    },
    'streak_5': {
        'name': 'On Fire', 'tier': 'silver',
        'description': '5 consecutive sessions above 70%',
        'condition': lambda st: _check_streak(st, 5),
    },

    # Tier 3: Gold
    'score_90': {
        'name': 'Excellence', 'tier': 'gold',
        'description': 'Score 90% or higher',
        'condition': lambda st: any(
            s['pct'] >= 90 for s in st.sessions),
    },
    'twenty_sessions': {
        'name': 'Veteran', 'tier': 'gold',
        'description': 'Complete 20 sessions',
        'condition': lambda st: len(st.sessions) >= 20,
    },
    'mastery_5': {
        'name': 'Expert', 'tier': 'gold',
        'description': 'Reach mastery level 5',
        'condition': lambda st: st.mastery_level >= 5,
    },

    # Tier 4: Platinum
    'score_95': {
        'name': 'Near Perfect', 'tier': 'platinum',
        'description': 'Score 95% or higher',
        'condition': lambda st: any(
            s['pct'] >= 95 for s in st.sessions),
    },
    'mastery_7': {
        'name': 'Grand Master', 'tier': 'platinum',
        'description': 'Reach mastery level 7',
        'condition': lambda st: st.mastery_level >= 7,
    },
    'fifty_sessions': {
        'name': 'Centurion', 'tier': 'platinum',
        'description': 'Complete 50 sessions',
        'condition': lambda st: len(st.sessions) >= 50,
    },
}


def _check_streak(student, target):
    """Check if student has a streak of target sessions above 70%."""
    scores = [s['pct'] for s in student.sessions]
    streak = 0
    for s in scores:
        if s >= 70:
            streak += 1
            if streak >= target:
                return True
        else:
            streak = 0
    return False


def check_achievement_gallery(student):
    """Check all achievements for a student."""
    earned = []
    locked = []

    for aid, ach in ACHIEVEMENT_CATALOG.items():
        try:
            if ach['condition'](student):
                earned.append({
                    'id': aid, 'name': ach['name'],
                    'tier': ach['tier'],
                    'description': ach['description'],
                })
            else:
                locked.append({
                    'id': aid, 'name': ach['name'],
                    'tier': ach['tier'],
                    'description': ach['description'],
                })
        except Exception:
            locked.append({
                'id': aid, 'name': ach['name'],
                'tier': ach['tier'],
                'description': ach['description'],
            })

    return {'earned': earned, 'locked': locked}


def format_achievement_gallery(gallery, student_name=''):
    """Format achievement gallery."""
    name = f" — {student_name}" if student_name else ''
    lines = [f"Achievement Gallery{name}"]
    lines.append("═" * 55)

    tier_icons = {
        'bronze': '🥉', 'silver': '🥈',
        'gold': '🥇', 'platinum': '💎',
    }

    for tier in ['bronze', 'silver', 'gold', 'platinum']:
        earned = [a for a in gallery['earned'] if a['tier'] == tier]
        locked = [a for a in gallery['locked'] if a['tier'] == tier]
        icon = tier_icons.get(tier, '•')

        lines.append(f"\n  {icon} {tier.upper()} "
                     f"({len(earned)}/{len(earned) + len(locked)})")

        for a in earned:
            lines.append(f"    ✓ {a['name']}: {a['description']}")
        for a in locked:
            lines.append(f"    ○ {a['name']}: {a['description']}")

    total = len(gallery['earned'])
    total_all = total + len(gallery['locked'])
    lines.append(f"\n  Total: {total}/{total_all} "
                 f"({round(total / total_all * 100) if total_all else 0}%)")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SCENARIO ENGINE (v41)
# ═══════════════════════════════════════════════════════════

class Scenario:
    """
    Predefined training scenario with objectives and evaluation.

    Scenarios combine templates, rules, and success criteria
    into a structured training experience.
    """

    def __init__(self, scenario_id, name, description, objectives,
                 settings=None):
        self.scenario_id = scenario_id
        self.name = name
        self.description = description
        self.objectives = objectives  # list of {type, target, description}
        self.settings = settings or {}
        self.attempts = 0
        self.best_result = None

    def evaluate(self, session_result):
        """Evaluate a session result against objectives."""
        self.attempts += 1
        pct = session_result.get('pct', 0)
        viols = len(session_result.get('violations', []))

        results = []
        all_passed = True

        for obj in self.objectives:
            passed = False
            if obj['type'] == 'min_score':
                passed = pct >= obj['target']
            elif obj['type'] == 'max_violations':
                passed = viols <= obj['target']
            elif obj['type'] == 'min_tacts':
                passed = session_result.get('length', 0) >= obj['target']

            if not passed:
                all_passed = False

            results.append({
                'objective': obj['description'],
                'passed': passed,
                'type': obj['type'],
            })

        score = round(sum(1 for r in results if r['passed']) /
                      len(results) * 100) if results else 0

        if self.best_result is None or score > self.best_result:
            self.best_result = score

        return {
            'scenario': self.name,
            'attempt': self.attempts,
            'all_passed': all_passed,
            'score': score,
            'results': results,
        }


SCENARIOS = {
    'boot_camp': Scenario(
        'boot_camp', 'Boot Camp',
        'Intensive fundamentals training',
        [{'type': 'min_score', 'target': 60, 'description': 'Score ≥60%'},
         {'type': 'max_violations', 'target': 3, 'description': '≤3 violations'}],
    ),
    'precision_drill': Scenario(
        'precision_drill', 'Precision Drill',
        'High accuracy challenge',
        [{'type': 'min_score', 'target': 85, 'description': 'Score ≥85%'},
         {'type': 'max_violations', 'target': 0, 'description': 'Zero violations'}],
    ),
    'endurance_run': Scenario(
        'endurance_run', 'Endurance Run',
        'Long session without dropping',
        [{'type': 'min_score', 'target': 70, 'description': 'Score ≥70%'},
         {'type': 'min_tacts', 'target': 20, 'description': '≥20 tacts'}],
    ),
    'mastery_test': Scenario(
        'mastery_test', 'Mastery Test',
        'Prove mastery-level capability',
        [{'type': 'min_score', 'target': 90, 'description': 'Score ≥90%'},
         {'type': 'max_violations', 'target': 1, 'description': '≤1 violation'},
         {'type': 'min_tacts', 'target': 14, 'description': '≥14 tacts'}],
    ),
}


def format_scenario_result(result):
    """Format scenario evaluation result."""
    lines = [f"Scenario: {result['scenario']} "
             f"(attempt #{result['attempt']})"]
    lines.append("─" * 45)

    for r in result['results']:
        icon = '✓' if r['passed'] else '✗'
        lines.append(f"  {icon} {r['objective']}")

    status = 'PASSED' if result['all_passed'] else 'FAILED'
    lines.append(f"  Result: {status} ({result['score']}%)")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# PROGRESS MILESTONES (v41)
# ═══════════════════════════════════════════════════════════

class MilestoneTracker:
    """
    Track major milestones in student's journey.

    Auto-detects when milestones are reached.
    """

    MILESTONES = [
        {'id': 'M01', 'name': 'First Session', 'sessions': 1},
        {'id': 'M02', 'name': 'Week One', 'sessions': 5},
        {'id': 'M03', 'name': 'Double Digits', 'sessions': 10},
        {'id': 'M04', 'name': 'Apprentice', 'mastery': 2},
        {'id': 'M05', 'name': 'Journeyman', 'mastery': 3},
        {'id': 'M06', 'name': 'Expert', 'mastery': 5},
        {'id': 'M07', 'name': 'Master', 'mastery': 7},
        {'id': 'M08', 'name': 'First A', 'score': 90},
        {'id': 'M09', 'name': 'Near Perfect', 'score': 95},
        {'id': 'M10', 'name': 'Quarter Century', 'sessions': 25},
        {'id': 'M11', 'name': 'Half Century', 'sessions': 50},
        {'id': 'M12', 'name': 'Century', 'sessions': 100},
    ]

    def __init__(self):
        self.reached = {}  # id → session_number

    def check(self, student):
        """Check which milestones are reached."""
        n = len(student.sessions)
        ml = student.mastery_level
        best = max((s['pct'] for s in student.sessions), default=0)

        newly_reached = []
        for m in self.MILESTONES:
            if m['id'] in self.reached:
                continue

            reached = False
            if 'sessions' in m and n >= m['sessions']:
                reached = True
            if 'mastery' in m and ml >= m['mastery']:
                reached = True
            if 'score' in m and best >= m['score']:
                reached = True

            if reached:
                self.reached[m['id']] = n
                newly_reached.append(m)

        return newly_reached

    def format_milestones(self, student_name=''):
        """Format milestone status."""
        name = f" — {student_name}" if student_name else ''
        lines = [f"Milestones{name}"]
        lines.append("═" * 45)

        for m in self.MILESTONES:
            if m['id'] in self.reached:
                sess = self.reached[m['id']]
                lines.append(f"  ★ {m['id']} {m['name']} "
                             f"(reached at session {sess})")
            else:
                lines.append(f"  ○ {m['id']} {m['name']}")

        done = len(self.reached)
        total = len(self.MILESTONES)
        lines.append(f"\n  {done}/{total} milestones reached")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# DATA PIPELINE (v41)
# ═══════════════════════════════════════════════════════════

class DataPipeline:
    """
    ETL pipeline for Scarab data processing.

    Stages: Extract → Transform → Load
    Supports chaining transforms.
    """

    def __init__(self, name='default'):
        self.name = name
        self.transforms = []
        self.data = None

    def extract(self, school):
        """Extract raw data from school."""
        records = []
        for sname, st in school.students.items():
            for i, s in enumerate(st.sessions):
                records.append({
                    'student': sname,
                    'session': i + 1,
                    'pct': s['pct'],
                    'mastery': st.mastery_level,
                    'violations': len(s.get('violations', [])),
                    'length': s.get('length', 0),
                })
        self.data = records
        return self

    def add_transform(self, fn, name=''):
        """Add a transform function."""
        self.transforms.append({'fn': fn, 'name': name})
        return self

    def transform(self):
        """Apply all transforms in order."""
        for t in self.transforms:
            self.data = t['fn'](self.data)
        return self

    def filter_by(self, field, value):
        """Add a filter transform."""
        return self.add_transform(
            lambda data: [r for r in data if r.get(field) == value],
            name=f'filter({field}={value})')

    def sort_by(self, field, reverse=False):
        """Add a sort transform."""
        return self.add_transform(
            lambda data: sorted(data, key=lambda r: r.get(field, 0),
                                reverse=reverse),
            name=f'sort({field})')

    def aggregate(self, group_field, agg_field, agg_fn='mean'):
        """Add an aggregation transform."""
        def _agg(data):
            groups = {}
            for r in data:
                key = r.get(group_field, '')
                groups.setdefault(key, []).append(r.get(agg_field, 0))

            result = []
            for key, vals in groups.items():
                if agg_fn == 'mean':
                    val = sum(vals) / len(vals) if vals else 0
                elif agg_fn == 'sum':
                    val = sum(vals)
                elif agg_fn == 'count':
                    val = len(vals)
                elif agg_fn == 'max':
                    val = max(vals) if vals else 0
                else:
                    val = sum(vals) / len(vals) if vals else 0

                result.append({
                    group_field: key,
                    f'{agg_fn}_{agg_field}': round(val, 1),
                    'count': len(vals),
                })
            return result

        return self.add_transform(_agg,
            name=f'agg({group_field},{agg_fn}({agg_field}))')

    def load(self):
        """Load (return) the processed data."""
        return self.data

    def format_pipeline(self):
        """Format pipeline info."""
        lines = [f"Pipeline: {self.name}"]
        lines.append("─" * 40)
        for i, t in enumerate(self.transforms):
            lines.append(f"  {i + 1}. {t['name']}")
        n = len(self.data) if self.data else 0
        lines.append(f"  Records: {n}")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# ADAPTIVE QUIZ (v42)
# ═══════════════════════════════════════════════════════════

class AdaptiveQuiz:
    """
    Adaptive quiz that adjusts difficulty based on answers.

    Uses item response theory: correct → harder, wrong → easier.
    """

    def __init__(self, student, n_questions=10, seed=None):
        self.student = student
        self.n_questions = n_questions
        self.questions = []
        self.answers = []
        self.current_difficulty = 3  # 1-7 scale (matches groups)
        import random as _rnd_q
        self._rnd = _rnd_q
        if seed is not None:
            self._rnd.seed(seed)

    def generate_question(self):
        """Generate next question based on current difficulty."""
        group = max(1, min(7, self.current_difficulty))
        # Pick a symbol from this group
        candidates = [s for s in range(64) if get_group(s) == group]
        if not candidates:
            candidates = list(range(64))

        sym = self._rnd.choice(candidates)
        correct_group = get_group(sym)

        question = {
            'index': len(self.questions),
            'symbol': sym,
            'correct_answer': correct_group,
            'difficulty': self.current_difficulty,
            'type': 'identify_group',
        }
        self.questions.append(question)
        return question

    def answer(self, question_idx, given_answer):
        """Submit an answer. Returns True if correct."""
        q = self.questions[question_idx]
        correct = given_answer == q['correct_answer']

        self.answers.append({
            'question': question_idx,
            'given': given_answer,
            'correct': q['correct_answer'],
            'is_correct': correct,
            'difficulty': q['difficulty'],
        })

        # Adapt difficulty
        if correct:
            self.current_difficulty = min(7,
                self.current_difficulty + 0.5)
        else:
            self.current_difficulty = max(1,
                self.current_difficulty - 0.7)

        return correct

    def score(self):
        """Calculate quiz score."""
        if not self.answers:
            return 0
        correct = sum(1 for a in self.answers if a['is_correct'])
        # Weight by difficulty
        weighted = sum(
            a['difficulty'] for a in self.answers if a['is_correct'])
        max_weight = sum(a['difficulty'] for a in self.answers)
        return {
            'raw': round(correct / len(self.answers) * 100, 1),
            'weighted': round(weighted / max_weight * 100, 1)
                        if max_weight else 0,
            'correct': correct,
            'total': len(self.answers),
            'final_difficulty': round(self.current_difficulty, 1),
        }

    def format_quiz(self):
        """Format quiz results."""
        sc = self.score()
        lines = [f"Adaptive Quiz: {self.student.name}"]
        lines.append("─" * 45)
        lines.append(f"  Score: {sc['correct']}/{sc['total']} "
                     f"({sc['raw']}% raw, {sc['weighted']}% weighted)")
        lines.append(f"  Final difficulty: {sc['final_difficulty']}")

        lines.append("\n  Difficulty progression:")
        diffs = [a['difficulty'] for a in self.answers]
        for i, d in enumerate(diffs):
            bar = '▓' * int(d * 3)
            ans = '✓' if self.answers[i]['is_correct'] else '✗'
            lines.append(f"    Q{i + 1}: {ans} D={d:.1f} {bar}")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# GROUP PROFICIENCY MATRIX (v42)
# ═══════════════════════════════════════════════════════════

def compute_group_proficiency(student):
    """
    Compute proficiency level per Kryukov group.

    Based on how often the student encounters and scores well
    with each group's symbols.
    """
    sessions = student.sessions
    group_scores = {g: [] for g in range(1, 8)}

    for s in sessions:
        pct = s['pct']
        # Distribute score across groups (simplified model)
        for g in range(1, 8):
            # Higher groups get slightly penalized
            adjusted = pct - (g - 1) * 2
            group_scores[g].append(max(0, adjusted))

    proficiency = {}
    for g in range(1, 8):
        scores = group_scores[g]
        if scores:
            avg = sum(scores) / len(scores)
            proficiency[g] = {
                'avg': round(avg, 1),
                'sessions': len(scores),
                'level': ('master' if avg >= 85 else
                          'proficient' if avg >= 70 else
                          'developing' if avg >= 55 else 'novice'),
                'grade': ('A' if avg >= 85 else
                          'B' if avg >= 70 else
                          'C' if avg >= 55 else 'D'),
            }
        else:
            proficiency[g] = {
                'avg': 0, 'sessions': 0,
                'level': 'unknown', 'grade': '?',
            }

    return proficiency


def format_proficiency_matrix(proficiency, student_name=''):
    """Format proficiency matrix."""
    name = f" — {student_name}" if student_name else ''
    lines = [f"Group Proficiency{name}"]
    lines.append("═" * 50)

    for g in range(1, 8):
        p = proficiency[g]
        bar_len = int(p['avg'] / 5)
        bar = '▓' * bar_len + '░' * (20 - bar_len)
        lines.append(f"  G{g}: [{bar}] {p['avg']:5.1f}%  "
                     f"{p['grade']}  ({p['level']})")

    # Overall
    avgs = [proficiency[g]['avg'] for g in range(1, 8)]
    overall = round(sum(avgs) / 7, 1)
    weakest = min(range(1, 8), key=lambda g: proficiency[g]['avg'])
    strongest = max(range(1, 8), key=lambda g: proficiency[g]['avg'])

    lines.append(f"\n  Overall: {overall}%  |  "
                 f"Strongest: G{strongest}  |  Weakest: G{weakest}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SESSION JOURNAL (v42)
# ═══════════════════════════════════════════════════════════

class SessionJournal:
    """
    Personal training journal with notes, reflections, and tags.

    Students can annotate their sessions with observations.
    """

    def __init__(self, student_name):
        self.student_name = student_name
        self.entries = []

    def add_entry(self, session_idx, note, tags=None, mood=None):
        """Add a journal entry."""
        entry = {
            'session': session_idx,
            'note': note,
            'tags': tags or [],
            'mood': mood,  # 1-5 scale
            'index': len(self.entries),
        }
        self.entries.append(entry)
        return entry

    def get_by_session(self, session_idx):
        """Get entries for a specific session."""
        return [e for e in self.entries if e['session'] == session_idx]

    def get_by_tag(self, tag):
        """Get entries by tag."""
        return [e for e in self.entries if tag in e['tags']]

    def mood_trend(self):
        """Get mood trend over time."""
        moods = [(e['session'], e['mood'])
                 for e in self.entries if e['mood'] is not None]
        return moods

    def format_journal(self, last_n=10):
        """Format journal entries."""
        lines = [f"Session Journal: {self.student_name}"]
        lines.append("═" * 50)

        entries = self.entries[-last_n:]
        mood_icons = {1: '😞', 2: '😕', 3: '😐', 4: '🙂', 5: '😊'}

        for e in entries:
            mood = mood_icons.get(e['mood'], '') if e['mood'] else ''
            tags = ' '.join(f'#{t}' for t in e['tags'])
            lines.append(f"\n  Session #{e['session']} {mood}")
            lines.append(f"    {e['note']}")
            if tags:
                lines.append(f"    {tags}")

        lines.append(f"\n  Total entries: {len(self.entries)}")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# TRAINING PLAN OPTIMIZER (v43)
# ═══════════════════════════════════════════════════════════

class TrainingPlanOptimizer:
    """
    Generates optimized training plans based on student profile.

    Considers weaknesses, goals, available time, and progression.
    """

    def __init__(self, student, sessions_per_week=4):
        self.student = student
        self.sessions_per_week = sessions_per_week

    def optimize(self, n_weeks=4):
        """Generate an optimized multi-week training plan."""
        st = self.student
        ml = st.mastery_level
        scores = [s['pct'] for s in st.sessions]
        avg = sum(scores) / len(scores) if scores else 50
        prof = compute_group_proficiency(st)

        plan = []
        for week in range(1, n_weeks + 1):
            week_plan = {
                'week': week,
                'sessions': [],
                'focus': '',
                'goal': '',
            }

            # Determine focus for the week
            weak_groups = [g for g in range(1, 8)
                          if prof[g]['avg'] < 70]

            if week <= n_weeks // 2:
                # First half: address weaknesses
                if weak_groups:
                    focus_g = weak_groups[week % len(weak_groups) - 1]
                    week_plan['focus'] = f'Group {focus_g} strengthening'
                else:
                    week_plan['focus'] = 'Consolidation'
            else:
                # Second half: push boundaries
                week_plan['focus'] = 'Advancement & challenge'

            target = min(100, avg + week * 2)
            week_plan['goal'] = f'Target avg: {target:.0f}%'

            for day in range(1, self.sessions_per_week + 1):
                if day == 1:
                    tmpl = 'warmup'
                elif day == self.sessions_per_week:
                    tmpl = 'speed_run' if ml >= 3 else 'drill_zone'
                elif weak_groups and day % 2 == 0:
                    tmpl = 'drill_zone'
                else:
                    tmpl = 'group_flow' if ml >= 2 else 'warmup'

                week_plan['sessions'].append({
                    'day': day,
                    'template': tmpl,
                    'duration': 'standard',
                })

            plan.append(week_plan)

        return plan

    def format_plan(self, plan):
        """Format training plan."""
        lines = [f"Training Plan: {self.student.name}"]
        lines.append("═" * 55)

        for wp in plan:
            lines.append(f"\n  Week {wp['week']}: {wp['focus']}")
            lines.append(f"    Goal: {wp['goal']}")
            for s in wp['sessions']:
                lines.append(f"      Day {s['day']}: "
                             f"[{s['template']}]")

        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SYMBOL SIMILARITY (v43)
# ═══════════════════════════════════════════════════════════

def symbol_similarity(sym_a, sym_b):
    """
    Compute similarity between two symbols (0-1 scale).

    Based on: same group, binary hamming distance, zone proximity.
    """
    # Group similarity (0 or 0.4)
    ga, gb = get_group(sym_a), get_group(sym_b)
    group_sim = 0.4 if ga == gb else 0

    # Binary hamming distance (6-bit)
    xor = sym_a ^ sym_b
    hamming = bin(xor).count('1')
    hamming_sim = (6 - hamming) / 6 * 0.3

    # Zone proximity
    za, zb = get_zones(sym_a), get_zones(sym_b)
    if isinstance(za, tuple) and isinstance(zb, tuple):
        dist = abs(za[0] - zb[0]) + abs(za[1] - zb[1])
        zone_sim = max(0, (6 - dist) / 6) * 0.3
    elif za == zb:
        zone_sim = 0.3
    else:
        zone_sim = 0

    return round(group_sim + hamming_sim + zone_sim, 3)


def find_similar_symbols(target_sym, top_n=5):
    """Find the most similar symbols to the target."""
    similarities = []
    for sym in range(64):
        if sym == target_sym:
            continue
        sim = symbol_similarity(target_sym, sym)
        similarities.append((sym, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]


def format_similarity(target, similar):
    """Format similarity results."""
    lines = [f"Symbols similar to S{target:02d} "
             f"(G{get_group(target)})"]
    lines.append("─" * 40)

    for sym, sim in similar:
        bar_len = int(sim * 20)
        bar = '▓' * bar_len + '░' * (20 - bar_len)
        lines.append(f"  S{sym:02d} G{get_group(sym)}  "
                     f"[{bar}] {sim:.3f}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# RANK SYSTEM (v43)
# ═══════════════════════════════════════════════════════════

RANKS = [
    {'name': 'Initiate', 'min_score': 0, 'min_sessions': 0,
     'min_mastery': 0, 'tier': 1},
    {'name': 'Novice', 'min_score': 0, 'min_sessions': 3,
     'min_mastery': 1, 'tier': 2},
    {'name': 'Apprentice', 'min_score': 55, 'min_sessions': 5,
     'min_mastery': 2, 'tier': 3},
    {'name': 'Adept', 'min_score': 65, 'min_sessions': 10,
     'min_mastery': 3, 'tier': 4},
    {'name': 'Specialist', 'min_score': 72, 'min_sessions': 15,
     'min_mastery': 3, 'tier': 5},
    {'name': 'Veteran', 'min_score': 78, 'min_sessions': 20,
     'min_mastery': 4, 'tier': 6},
    {'name': 'Expert', 'min_score': 83, 'min_sessions': 25,
     'min_mastery': 5, 'tier': 7},
    {'name': 'Master', 'min_score': 88, 'min_sessions': 35,
     'min_mastery': 6, 'tier': 8},
    {'name': 'Grand Master', 'min_score': 93, 'min_sessions': 50,
     'min_mastery': 7, 'tier': 9},
    {'name': 'Legend', 'min_score': 97, 'min_sessions': 100,
     'min_mastery': 7, 'tier': 10},
]


def compute_rank(student):
    """Compute student's current rank."""
    scores = [s['pct'] for s in student.sessions]
    n = len(scores)
    avg = sum(scores) / n if scores else 0
    ml = student.mastery_level

    current_rank = RANKS[0]
    next_rank = RANKS[1] if len(RANKS) > 1 else None

    for i, rank in enumerate(RANKS):
        if (avg >= rank['min_score'] and
                n >= rank['min_sessions'] and
                ml >= rank['min_mastery']):
            current_rank = rank
            next_rank = RANKS[i + 1] if i + 1 < len(RANKS) else None
        else:
            break

    # Progress to next rank
    progress = 100
    if next_rank:
        reqs_met = 0
        reqs_total = 3
        if avg >= next_rank['min_score']:
            reqs_met += 1
        if n >= next_rank['min_sessions']:
            reqs_met += 1
        if ml >= next_rank['min_mastery']:
            reqs_met += 1
        progress = round(reqs_met / reqs_total * 100)

    return {
        'rank': current_rank,
        'next_rank': next_rank,
        'progress_to_next': progress,
        'tier': current_rank['tier'],
    }


def format_rank(rank_result, student_name=''):
    """Format rank display."""
    name = f" — {student_name}" if student_name else ''
    r = rank_result
    lines = [f"Rank{name}"]
    lines.append("─" * 40)
    lines.append(f"  Current: {r['rank']['name']} "
                 f"(Tier {r['tier']})")

    if r['next_rank']:
        bar_len = r['progress_to_next'] // 5
        bar = '▓' * bar_len + '░' * (20 - bar_len)
        lines.append(f"  Next: {r['next_rank']['name']} "
                     f"[{bar}] {r['progress_to_next']}%")
        lines.append(f"    Requires: score≥{r['next_rank']['min_score']}%  "
                     f"sessions≥{r['next_rank']['min_sessions']}  "
                     f"mastery≥L{r['next_rank']['min_mastery']}")
    else:
        lines.append("  MAX RANK ACHIEVED")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# EVENT-DRIVEN HOOKS (v44)
# ═══════════════════════════════════════════════════════════

class EventBus:
    """
    Publish-subscribe event bus for the Scarab system.

    Components register handlers for events and get notified
    when events are fired.
    """

    def __init__(self):
        self._handlers = {}  # event_name → [handlers]
        self._history = []

    def on(self, event_name, handler):
        """Register a handler for an event."""
        self._handlers.setdefault(event_name, []).append(handler)

    def off(self, event_name, handler=None):
        """Remove handler(s) for an event."""
        if handler is None:
            self._handlers.pop(event_name, None)
        elif event_name in self._handlers:
            self._handlers[event_name] = [
                h for h in self._handlers[event_name]
                if h != handler]

    def emit(self, event_name, data=None):
        """Fire an event, notifying all registered handlers."""
        event = {
            'name': event_name,
            'data': data or {},
            'seq': len(self._history),
        }
        self._history.append(event)

        results = []
        for handler in self._handlers.get(event_name, []):
            try:
                result = handler(event)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})

        return results

    def events(self):
        """List all registered event types."""
        return list(self._handlers.keys())

    def history(self, last_n=10):
        """Recent event history."""
        return self._history[-last_n:]

    def format_bus(self):
        """Format bus info."""
        lines = ["EventBus"]
        lines.append("─" * 40)
        for name, handlers in self._handlers.items():
            lines.append(f"  {name}: {len(handlers)} handler(s)")
        lines.append(f"  Total events fired: {len(self._history)}")
        return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# SESSION COMPARISON (v44)
# ═══════════════════════════════════════════════════════════

def compare_sessions(student, idx_a, idx_b):
    """
    Compare two sessions of the same student.

    Returns detailed comparison with delta analysis.
    """
    sessions = student.sessions
    if idx_a >= len(sessions) or idx_b >= len(sessions):
        return None

    sa, sb = sessions[idx_a], sessions[idx_b]

    comparison = {
        'student': student.name,
        'session_a': idx_a + 1,
        'session_b': idx_b + 1,
        'score_a': sa['pct'],
        'score_b': sb['pct'],
        'delta_score': round(sb['pct'] - sa['pct'], 1),
        'violations_a': len(sa.get('violations', [])),
        'violations_b': len(sb.get('violations', [])),
        'improved': sb['pct'] > sa['pct'],
    }

    return comparison


def compare_first_last(student):
    """Compare first and most recent session."""
    n = len(student.sessions)
    if n < 2:
        return None
    return compare_sessions(student, 0, n - 1)


def format_session_comparison(cmp):
    """Format session comparison."""
    if cmp is None:
        return "Insufficient sessions to compare."

    lines = [f"Session Comparison: {cmp['student']}"]
    lines.append("─" * 45)

    arrow = '↑' if cmp['improved'] else '↓'
    lines.append(f"  Session #{cmp['session_a']}: "
                 f"{cmp['score_a']}%")
    lines.append(f"  Session #{cmp['session_b']}: "
                 f"{cmp['score_b']}%")
    lines.append(f"  Delta: {cmp['delta_score']:+.1f}% {arrow}")
    lines.append(f"  Violations: {cmp['violations_a']} → "
                 f"{cmp['violations_b']}")

    return '\n'.join(lines)


# ═══════════════════════════════════════════════════════════
# COACHING ENGINE (v44)
# ═══════════════════════════════════════════════════════════

class CoachingEngine:
    """
    AI coaching engine that generates personalized coaching messages.

    Combines data from multiple analyzers to produce contextual,
    motivating, and actionable coaching.
    """

    TEMPLATES = {
        'encouragement': [
            "Great work, {name}! Your {metric} is improving.",
            "Keep it up, {name}! You've maintained {streak} strong sessions.",
            "{name}, you're on track for the next mastery level!",
        ],
        'correction': [
            "{name}, let's focus on improving your {area}.",
            "Your {area} needs attention. Try {suggestion}.",
            "{name}, consider reviewing {area} fundamentals.",
        ],
        'milestone': [
            "Congratulations, {name}! You've reached {milestone}!",
            "{name} achieves a new milestone: {milestone}!",
        ],
        'challenge': [
            "{name}, ready for a challenge? Try the {template} template.",
            "Push your limits, {name}! Aim for {target}% this session.",
        ],
    }

    def __init__(self, student):
        self.student = student

    def generate_message(self):
        """Generate a contextual coaching message."""
        st = self.student
        scores = [s['pct'] for s in st.sessions]
        n = len(scores)

        if n == 0:
            return f"Welcome, {st.name}! Start with a warmup session."

        avg = sum(scores) / n
        recent = scores[-3:] if n >= 3 else scores
        recent_avg = sum(recent) / len(recent)

        import random as _rnd_coach
        _rnd_coach.seed(n)  # Deterministic per session count

        # Choose category
        if recent_avg >= 85:
            if st.mastery_level < 7:
                cat = 'challenge'
            else:
                cat = 'encouragement'
        elif recent_avg >= 70:
            cat = 'encouragement'
        else:
            cat = 'correction'

        templates = self.TEMPLATES[cat]
        template = _rnd_coach.choice(templates)

        # Fill template
        message = template.format(
            name=st.name,
            metric='score average',
            streak=n,
            area='consistency' if avg < 75 else 'advanced groups',
            suggestion='the drill_zone template',
            milestone=f'L{st.mastery_level}',
            template='peak_challenge' if st.mastery_level >= 5
                     else 'endurance',
            target=int(min(100, avg + 5)),
        )

        return message

    def generate_session_brief(self):
        """Generate pre-session briefing."""
        st = self.student
        msg = self.generate_message()

        prof = compute_group_proficiency(st)
        weakest = min(range(1, 8), key=lambda g: prof[g]['avg'])

        rank = compute_rank(st)

        brief = {
            'greeting': msg,
            'rank': rank['rank']['name'],
            'weakest_group': weakest,
            'suggested_template': (
                'peak_challenge' if st.mastery_level >= 5 else
                'endurance' if st.mastery_level >= 3 else
                'group_flow' if st.mastery_level >= 2 else
                'warmup'),
            'focus_tip': f'Pay attention to Group {weakest} symbols.',
        }

        return brief

    def format_brief(self, brief=None):
        """Format session briefing."""
        b = brief or self.generate_session_brief()
        lines = [f"Coach's Brief for {self.student.name}"]
        lines.append("═" * 50)
        lines.append(f"  {b['greeting']}")
        lines.append(f"  Rank: {b['rank']}")
        lines.append(f"  Suggested: [{b['suggested_template']}]")
        lines.append(f"  Focus: {b['focus_tip']}")
        return '\n'.join(lines)


if __name__ == '__main__':
    print("=" * 60)
    print("SCARAB ALGORITHM v3 — Four-Sphere Movement Generator")
    print("Match-Stick Automaton + ChVS Gearbox")
    print("BVS(3D) + SVS(2D) + MVS(1D) + ChVS(0D) = π")
    print("=" * 60)

    # 1. Alphabet overview
    print("\n--- Movement Alphabet: 76 Symbols ---")
    print(f"  Base symbols (6-bit):  {len(BASE_SYMBOLS)} (= 2^6 = 64)")
    print(f"  Half-line symbols:     {len(HALF_SYMBOLS)} (= 76 - 64 = 12)")
    print(f"  Total:                 {len(BASE_SYMBOLS) + len(HALF_SYMBOLS)}")
    print(f"  x 4 ChVS modifiers:   {(len(BASE_SYMBOLS) + len(HALF_SYMBOLS)) * 4}"
          f" (= 304 ~ 310 ETD volumes)")

    # 2. Group distribution
    print("\n--- Kryukov's 7 Groups Distribution ---")
    group_counts = {g: 0 for g in range(1, 8)}
    for sym in range(64):
        g = get_group(sym)
        group_counts[g] += 1
    group_names = {1: 'Soft base', 2: 'Hard base', 3: 'MVS (wrist)',
                   4: 'Rotational', 5: 'Weapon', 6: 'Master', 7: 'Peak defense'}
    for g in range(1, 8):
        print(f"  Group {g} ({group_names[g]}): {group_counts[g]} symbols")
    print(f"  Total: {sum(group_counts.values())}")

    # 3. ChVS Gearbox demonstration
    print("\n--- ChVS Gearbox (Micro-Correction) ---")
    contacts = [
        (CONTACT_HARD, "Hit solid target"),
        (CONTACT_SOFT, "Hit soft target"),
        (CONTACT_EMPTY, "Missed / no contact"),
        (CONTACT_BLOCK, "Hit opponent's block"),
    ]
    for ct, desc in contacts:
        response = chvs_gearbox(ct)
        vec = CHVS_VECTORS[response]
        print(f"  Contact: {desc:25s} -> ChVS: {CHVS_NAMES[response]:5s} "
              f"(force={vec[0]:.1f}, spread={vec[1]:.1f}, penetr={vec[2]:.1f})")

    # 4. Match-Stick Automaton at each mastery level
    print("\n--- Match-Stick Automaton: Mastery Progression ---")
    for level in [1, 2, 3, 4, 5]:
        msa = MatchStickAutomaton(mastery_level=level, seed=42)
        kata = msa.generate_kata(length=7)
        groups_used = set(get_group(s) for s in kata)
        print(f"  Level {level}: {len(msa.available_symbols)} symbols available | "
              f"kata groups: {sorted(groups_used)} | "
              f"kata: {' -> '.join(f'{s:06b}' for s in kata)}")

    # 5. Full attack cycle example
    print("\n--- Full Attack Cycle (MSA + ChVS) ---")
    msa = MatchStickAutomaton(mastery_level=4, seed=7)
    attack_sequence = [
        (0,           CONTACT_EMPTY, "Ready position"),
        (DIAG1,       CONTACT_EMPTY, "Wind-up (diagonal)"),
        (LEFT|DIAG1|DIAG2, CONTACT_HARD, "Strike with cover (K-shape)"),
        (DIAG1|DIAG2, CONTACT_BLOCK, "Double block (X)"),
        (BOTTOM|RIGHT, CONTACT_SOFT, "Intercept (corner)"),
        (DIAG2,       CONTACT_EMPTY, "Thrust (anti-diagonal)"),
        (0,           None,          "Return to ready"),
    ]
    for target, contact, desc in attack_sequence:
        msa.transition(target, contact)
        grp = get_group(msa.state)
        print(f"  {desc:35s} | {msa.state:06b} | G{grp} | "
              f"ChVS: {CHVS_NAMES[msa.chvs]}")
    print(f"  Cycle: {len(attack_sequence)} tacts (ODD!)")

    # 6. Four-level Scarab trajectory comparison
    print("\n--- Four-Level Scarab: Trajectory Complexity ---")
    level_names = {1: 'Linear (BVS)', 2: 'Loops (+SVS)',
                   3: 'Volume (+MVS)', 4: 'Satellite (+ChVS)',
                   5: 'RESONANCE'}
    for level in [1, 2, 3, 4, 5]:
        traj = four_level_scarab(space_size=10.0, k_bvs=2.0, k_svs=1.5,
                                  k_mvs=1.0, k_chvs=1.0,
                                  mastery_level=level, steps=100, seed=42)
        path_len = sum(math.sqrt((traj[i+1][0]-traj[i][0])**2 +
                                  (traj[i+1][1]-traj[i][1])**2)
                       for i in range(len(traj)-1))
        print(f"  Level {level} ({level_names[level]:20s}): path={path_len:.1f}")

    # 7. Training session generation
    print("\n--- Generated Training Session (Level 3) ---")
    msa3 = MatchStickAutomaton(mastery_level=3, seed=42)
    session = msa3.generate_training_session(duration_minutes=45)
    for block_name, block_data in session.items():
        dur = block_data.get('duration', '?')
        instr = block_data.get('instruction', '')
        print(f"\n  [{dur}] {block_name.upper()}")
        print(f"    {instr}")
        if 'symbols' in block_data:
            syms = block_data['symbols']
            print(f"    Symbols: {', '.join(f'{s:06b}' for s in syms[:5])}...")
        if 'pairs' in block_data:
            for a, b in block_data['pairs'][:3]:
                print(f"    Pair: {a:06b} -> {b:06b} "
                      f"(G{get_group(a)} -> G{get_group(b)})")
            if len(block_data['pairs']) > 3:
                print(f"    ...and {len(block_data['pairs'])-3} more pairs")
        if 'sequences' in block_data:
            for i, k in enumerate(block_data['sequences'][:2]):
                print(f"    Kata {i+1}: {' -> '.join(f'{s:06b}' for s in k)}")
        if 'challenges' in block_data:
            for ch in block_data['challenges'][:3]:
                print(f"    Target: {ch['symbol']:06b} G{ch['group']} "
                      f"(respond in {ch['response_time']:.1f}s)")

    # 8. DUAL AUTOMATON — two coordinated hands
    print("\n--- Dual Match-Stick Automaton (Juggler Mode) ---")
    for level in [1, 3, 5]:
        dual = DualMatchStickAutomaton(mastery_level=level, seed=42)
        valid, total = dual.count_valid_pairs()
        print(f"  Level {level}: {valid}/{total} valid pairs "
              f"({100*valid/total:.0f}% of space)")

    # 9. Dual kata generation
    print("\n--- Dual Kata (7 tacts, Level 3) ---")
    dual3 = DualMatchStickAutomaton(mastery_level=3, seed=42)
    dkata = dual3.generate_dual_kata(length=7)
    group_names = {1: 'Soft', 2: 'Hard', 3: 'MVS', 4: 'Rot',
                   5: 'Wpn', 6: 'Mstr', 7: 'Peak'}
    for i, (L, R, cL, cR) in enumerate(dkata):
        gL, gR = get_group(L), get_group(R)
        conflict = zones_conflict(L, R)
        anti = is_anti_symmetric(L, R)
        chvs_L = CHVS_NAMES.get(cL, '?')
        chvs_R = CHVS_NAMES.get(cR, '?')
        status = 'OK' if (not conflict and (anti or i == 0)) else 'WARN'
        print(f"  T{i}: L={L:06b}(G{gL}/{group_names[gL]:4s},{chvs_L:5s}) "
              f"R={R:06b}(G{gR}/{group_names[gR]:4s},{chvs_R:5s}) [{status}]")

    # 10. Mudra system demonstration
    print("\n--- Mudra System (8 finger positions) ---")
    for m_id in range(8):
        name = MUDRA_NAMES[m_id]
        vec = MUDRA_VECTORS[m_id]
        print(f"  {name:6s}: force={vec[0]:.1f} spread={vec[1]:.1f} "
              f"penetr={vec[2]:.1f} control={vec[3]:.1f}")
    print(f"  State space: 76 sym x 8 mudras x 2 hands = "
          f"{76 * 8 * 76 * 8} dual states")

    # 11. Dual kata with mudras
    print("\n--- Dual Kata with Mudras (Level 4) ---")
    dual_m = DualMatchStickAutomaton(mastery_level=4, use_mudras=True, seed=7)
    dkata_m = dual_m.generate_dual_kata(length=7)
    for i, (L, R, mL, mR) in enumerate(dkata_m):
        gL, gR = get_group(L), get_group(R)
        mL_name = MUDRA_NAMES.get(mL, '?')
        mR_name = MUDRA_NAMES.get(mR, '?')
        print(f"  T{i}: L={L:06b}(G{gL},{mL_name:6s}) "
              f"R={R:06b}(G{gR},{mR_name:6s}) lead={dual_m.lead}")

    # 12. Annual Training Plan with dual-hand progression
    print("\n--- Annual Training Plan (Dual-Hand) ---")
    plan_dual = {
        'Q1': {'hands': 'single', 'mudras': 4,  'desc': 'One hand, 4 ChVS basic'},
        'Q2': {'hands': 'single', 'mudras': 8,  'desc': 'One hand, 8 mudras'},
        'Q3': {'hands': 'dual',   'mudras': 4,  'desc': 'Two hands, 4 ChVS, zone rules'},
        'Q4': {'hands': 'dual',   'mudras': 8,  'desc': 'Two hands, 8 mudras, full system'},
    }
    for q, info in TRAINING_PLAN.items():
        pd = plan_dual[q]
        available = sum(1 for s in range(64) if get_group(s) in info['groups'])
        if pd['hands'] == 'dual':
            dual_tmp = DualMatchStickAutomaton(mastery_level=3, seed=0)
            dual_tmp.left._update_available_groups()
            dual_tmp.left.available_symbols = [
                s for s in range(64) if get_group(s) in info['groups']]
            dual_tmp.right.available_symbols = dual_tmp.left.available_symbols
            valid_p, total_p = dual_tmp.count_valid_pairs()
            states_str = f"{valid_p} dual pairs x {pd['mudras']}^2 = {valid_p * pd['mudras']**2}"
        else:
            states_str = f"{available} sym x {pd['mudras']} mudras = {available * pd['mudras']}"
        print(f"  {q}: {info['name']:35s}")
        print(f"       {pd['desc']:45s} | {states_str}")

    # 13. Dual stick-figure animation
    print("\n--- Dual Kata Visualization (3 tacts) ---")
    dual_viz = DualMatchStickAutomaton(mastery_level=3, seed=77)
    dkata_viz = dual_viz.generate_dual_kata(length=3)
    anim_frames = animate_dual_kata(dkata_viz)
    for frame in anim_frames:
        print(frame)

    # 14. Export single-hand training session to file
    msa_export = MatchStickAutomaton(mastery_level=2, seed=42)
    session_export = msa_export.generate_training_session()
    export_text = export_training_session(session_export, mastery_level=2,
                                          filename='training_session_L2.txt')
    line_count = len(export_text.split('\n'))
    print(f"--- Exported Training Session (Level 2) ---")
    print(f"  Saved to: training_session_L2.txt ({line_count} lines)")
    for line in export_text.split('\n')[:10]:
        print(f"  {line}")
    print("  ...")

    # 15. Complexity conservation (Rule 5)
    print("\n--- Complexity Conservation (Rule 5) ---")
    test_pairs = [
        (0b110100, 0b000010),  # K-shape (complex) + bottom (simple)
        (0b001111, 0b010000),  # square (complex) + diag1 (simple)
        (0b111111, 0b000000),  # full (max) + empty (min)
        (0b010000, 0b100000),  # diag1 + diag2 (both simple)
        (0b111111, 0b111111),  # full + full (both max)
    ]
    for sL, sR in test_pairs:
        total_c, balanced = complexity_balance(sL, sR)
        cL = symbol_complexity(sL)
        cR = symbol_complexity(sR)
        print(f"  L:{sL:06b}(C{cL}) + R:{sR:06b}(C{cR}) = "
              f"total {total_c} {'OK' if balanced else 'OVERLOAD'}")

    # 16. Dual kata with Rule 4 (phase offset) + Rule 5 (conservation)
    print("\n--- Dual Kata with Rules 4+5 (Level 4) ---")
    dual_r45 = DualMatchStickAutomaton(mastery_level=4, use_mudras=True, seed=13)
    dkata_r45 = dual_r45.generate_dual_kata(length=7)
    for i, (L, R, mL, mR) in enumerate(dkata_r45):
        gL, gR = get_group(L), get_group(R)
        total_c, balanced = complexity_balance(L, R)
        conflict = zones_conflict(L, R)
        anti = is_anti_symmetric(L, R)
        mL_name = MUDRA_NAMES.get(mL, '?')
        mR_name = MUDRA_NAMES.get(mR, '?')
        status_parts = []
        if conflict:
            status_parts.append('COLL')
        if not balanced:
            status_parts.append('HI-C')
        status = ','.join(status_parts) if status_parts else 'OK'
        print(f"  T{i}: L={L:06b}(G{gL},{mL_name:5s}) "
              f"R={R:06b}(G{gR},{mR_name:5s}) "
              f"C={total_c} lead={dual_r45.lead} [{status}]")

    # 17. Export dual-hand training session
    dual_export = DualMatchStickAutomaton(mastery_level=3, use_mudras=False, seed=42)
    dual_session = dual_export.generate_dual_training_session()
    dual_text = export_dual_training_session(
        dual_session, mastery_level=3, use_mudras=False,
        filename='training_session_dual_L3.txt')
    dual_line_count = len(dual_text.split('\n'))
    print(f"\n--- Exported Dual Training Session (Level 3) ---")
    print(f"  Saved to: training_session_dual_L3.txt ({dual_line_count} lines)")
    for line in dual_text.split('\n')[:15]:
        print(f"  {line}")
    print("  ...")

    # 18. Score the dual kata from demo 16
    print("\n--- Kata Score Report (from dual kata above) ---")
    score = score_dual_kata(dkata_r45)
    print(format_score_report(score))

    # 19. Seasonal kata generator — full year cycle
    print("\n--- Seasonal Kata Generator (Year 2) ---")
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        use_d = (q in ['Q3', 'Q4'])
        sk = generate_seasonal_kata(q, mastery_level=2, year=2,
                                     use_dual=use_d, seed=42)
        print(format_seasonal_kata(sk))
        print()

    # 20. Seasonal dual kata with mudras (Year 4, Q4 — near mastery)
    print("--- Q4 Mastery Kata (Year 4, dual + mudras) ---")
    sk_q4 = generate_seasonal_kata('Q4', mastery_level=4, year=4,
                                    use_dual=True, use_mudras=True, seed=77)
    print(format_seasonal_kata(sk_q4, use_mudras=True))

    # 21. Kata optimizer
    print("\n--- Kata Optimizer (target: A) ---")
    opt = optimize_kata(length=7, mastery_level=4, target_grade='A',
                        max_attempts=50, use_mudras=True, base_seed=42)
    print(f"  Optimized: {opt['optimized']} (in {opt['attempts']} attempts)")
    print(format_score_report(opt['score']))
    for i, (L, R, mL, mR) in enumerate(opt['kata']):
        gL, gR = get_group(L), get_group(R)
        print(f"    T{i}: L={L:06b}(G{gL}) R={R:06b}(G{gR})")

    # 22. Battle kata №1-4
    print("\n--- Battle Katas (all 4 formats) ---")
    for bn in [1, 2, 3, 4]:
        bk = generate_battle_kata(battle_num=bn, mastery_level=3,
                                   use_mudras=False, seed=42)
        print(format_battle_kata(bk))
        print()

    # 23. Battle kata №4 with mudras (advanced)
    print("--- Battle Kata №4 (Level 5, mudras) ---")
    bk4 = generate_battle_kata(battle_num=4, mastery_level=5,
                                use_mudras=True, base_tempo=100, seed=77)
    print(format_battle_kata(bk4, use_mudras=True))

    # 24. Symbol spatial mapping
    print("\n--- Symbol → Spatial Coordinates ---")
    test_syms = [0, TOP, BOTTOM, LEFT, RIGHT, DIAG1, DIAG2,
                 TOP|LEFT, BOTTOM|RIGHT, DIAG1|DIAG2, 0b111111]
    for s in test_syms:
        x, y = symbol_to_xy(s)
        nearest = xy_to_nearest_symbol(x, y)
        print(f"  {s:06b} → ({x:+.2f}, {y:+.2f}) → nearest: {nearest:06b} "
              f"{'✓' if nearest == s else '≈'}")

    # 25. Trajectory-driven kata (k-deformation bridge)
    print("\n--- Trajectory Kata (k=1 vs k=5 vs k=10) ---")
    for k_val in [1.0, 5.0, 10.0]:
        tk = trajectory_kata(k=k_val, length=7, mastery_level=4,
                              use_dual=True, seed=42)
        syms_str = ' '.join(f'{e[0]:06b}' for e in tk['kata'])
        print(f"  k={k_val:4.1f}: L: {syms_str}")
        print(f"         {format_score_report(tk['score']).split(chr(10))[0]}")

    # 26. Compact kata notation (round-trip)
    print("\n--- Compact Kata Notation ---")
    # Single
    single_kata = [0, 0b010000, 0b110100, 0b110000, 0b001010, 0b100000, 0]
    notation = kata_to_notation(single_kata, mode='single')
    mode, decoded = notation_to_kata(notation)
    print(f"  Single: {notation}")
    print(f"  Decode: {mode}, {[f'{s:06b}' for s in decoded]}")
    print(f"  Round-trip OK: {decoded == single_kata}")
    # Dual
    dual_notation = kata_to_notation(dkata_r45, mode='dual')
    print(f"  Dual:   {dual_notation}")

    # 27. Kata analytics
    print("\n--- Kata Analytics ---")
    print("  Automaton kata (Level 4, dual):")
    analysis_auto = analyze_kata(dkata_r45, mode='dual')
    print(format_analysis(analysis_auto))
    print("  Trajectory kata (k=5, dual):")
    tk5 = trajectory_kata(k=5.0, length=7, mastery_level=4,
                           use_dual=True, seed=42)
    analysis_traj = analyze_kata(tk5['kata'], mode='dual')
    print(format_analysis(analysis_traj))

    # 28. Seasonal kata with trajectory generation
    print("\n--- Seasonal Kata (trajectory mode) ---")
    for q in ['Q2', 'Q3', 'Q4']:
        use_d = (q in ['Q3', 'Q4'])
        sk = generate_seasonal_kata(q, mastery_level=3, year=3,
                                     use_dual=use_d, seed=42)
        gen = sk.get('generation', '?')
        print(f"  {q}: k={sk['k']}, gen={gen}, mode={sk['mode']}")
        if sk['mode'] == 'dual' and 'score' in sk:
            print(f"        {format_score_report(sk['score']).split(chr(10))[0]}")

    # 29. Quaternion representation
    print("\n--- Quaternion State (4-Sphere System) ---")
    for level in [1, 2, 3, 4, 5]:
        q = ScarabQuaternion.from_mastery(level)
        pct = q.components_pct()
        print(f"  Level {level}: {repr(q)}")
        print(f"          BVS={pct[0]:.0f}% SVS={pct[1]:.0f}% "
              f"MVS={pct[2]:.0f}% ChVS={pct[3]:.0f}%")

    # 30. Conservation law verification
    print("\n--- Conservation Law: |A| = pi ---")
    for level in [1, 3, 5]:
        cv = verify_conservation(level)
        print(f"  Level {level}: |A|={cv['norm']:.4f}, "
              f"pi={cv['pi']:.4f}, match={cv['match']}")
        pct = cv['components_pct']
        print(f"          BVS={pct['BVS']:.0f}% SVS={pct['SVS']:.0f}% "
              f"MVS={pct['MVS']:.0f}% ChVS={pct['ChVS']:.0f}%")

    # 31. LCI from kata
    print("\n--- LCI (Line Complexity Index) ---")
    lci_auto = compute_lci(dkata_r45, mode='dual')
    print(f"  Automaton kata LCI: avg={lci_auto['avg']}, "
          f"target={lci_auto['target']}, dev={lci_auto['deviation_pct']}%")
    print(f"  Per-tact: {lci_auto['per_tact']}")
    lci_opt = compute_lci(opt['kata'], mode='dual')
    print(f"  Optimized kata LCI: avg={lci_opt['avg']}, "
          f"dev={lci_opt['deviation_pct']}%, "
          f"conserved={lci_opt['conservation']}")

    # 32. Quaternion from symbol pairs
    print("\n--- Quaternion from Dual Pairs ---")
    for i, (L, R, mL, mR) in enumerate(dkata_r45[:3]):
        q = ScarabQuaternion.from_symbol_pair(L, R, mL, mR)
        print(f"  T{i}: L={L:06b} R={R:06b} → {repr(q)}")

    # 33. ASCII trajectory plot with kata overlay
    print("\n--- Figure-8 Trajectory with Kata Symbols ---")
    plot_lines = plot_kata_on_trajectory(
        dkata_r45, k=2.0, mastery_level=4, width=55, height=18)
    for line in plot_lines:
        print(line)
    print("  (T0-T6 = kata tact positions on the figure-8)")

    # 34. Trajectory at different k values
    print("\n--- Trajectory Shape: k=1 (symmetric) vs k=5 (deformed) ---")
    for k_demo in [1.0, 5.0]:
        traj_demo = four_level_scarab(
            space_size=1.0, k_bvs=k_demo, k_svs=1.0,
            k_mvs=1.0, k_chvs=1.0, mastery_level=3, steps=200, seed=42)
        plot = plot_trajectory_ascii(traj_demo, width=40, height=12)
        print(f"  k={k_demo}:")
        for line in plot:
            print(f"  {line}")

    # 35. Resonance detection
    print("\n--- Resonance Detection ---")
    # Optimized kata (likely more resonant)
    res_opt = detect_resonance(opt['kata'], mode='dual')
    print(f"  Optimized kata: resonance={res_opt['resonance_score']:.2f}")
    print(f"    LCI stability={res_opt['lci_stability']:.2f}, "
          f"phase={res_opt['phase_coherence']:.2f}")
    for p in res_opt['patterns']:
        print(f"    - {p}")
    # Battle kata (structured)
    res_bk = detect_resonance(bk4['kata'], mode='dual')
    print(f"  Battle kata №4: resonance={res_bk['resonance_score']:.2f}")
    for p in res_bk['patterns']:
        print(f"    - {p}")

    # 36. Exam system
    print("\n--- Exam System ---")
    exam = generate_exam(quarter='Q3', mastery_level=3, year=2, seed=42)
    print(f"  Exam: {exam['quarter']} Year {exam['year']}, "
          f"ref grade={exam['reference_score']['grade']}")
    print(f"  Notation: {exam['reference_notation']}")
    # Simulate student: generate a non-optimized kata
    student_dual = DualMatchStickAutomaton(mastery_level=3, seed=99)
    student_kata = student_dual.generate_dual_kata(length=5)
    ev = evaluate_exam(exam, student_kata)
    print(f"  Student: {ev['result']} (score={ev['score']['pct']:.0f}%, "
          f"similarity={ev['similarity_pct']:.0f}%)")
    for fb in ev['feedback'][:3]:
        print(f"    -> {fb}")

    # 37. Training progression (5-year simulation)
    print("\n--- 5-Year Progression Simulation ---")
    prog = simulate_progression(n_years=5, sessions_per_quarter=3, seed=42)
    print(format_progression(prog))
    # Summary: first vs last year
    y1 = [r for r in prog if r['year'] == 1]
    y5 = [r for r in prog if r['year'] == 5]
    avg_lci_1 = sum(r['avg_lci'] for r in y1) / len(y1)
    avg_lci_5 = sum(r['avg_lci'] for r in y5) / len(y5)
    max_groups_1 = max(r['n_groups'] for r in y1)
    max_groups_5 = max(r['n_groups'] for r in y5)
    print(f"\n  Year 1→5: LCI {avg_lci_1:.3f}→{avg_lci_5:.3f}, "
          f"groups {max_groups_1}→{max_groups_5}/7")

    # 39. Resonance-guided kata generation
    print("\n--- Resonance-Guided Kata Generation ---")
    rk = resonance_kata(length=7, mastery_level=3, target_resonance=0.6,
                        mode='dual', max_attempts=30, base_seed=42)
    print(f"  Target resonance: 0.60")
    print(f"  Achieved: {rk['resonance']['resonance_score']:.2f} "
          f"in {rk['attempts']} attempts")
    print(f"  Grade: {rk['score']['grade']} ({rk['score']['pct']:.0f}%)")
    if rk['resonance']['patterns']:
        print(f"  Patterns: {', '.join(rk['resonance']['patterns'][:3])}")

    # 40. Student profile
    print("\n--- Student Profile ---")
    student = StudentProfile('Alexei', mastery_level=2)
    # Simulate several training sessions
    for qi, q in enumerate(['Q1', 'Q2', 'Q3', 'Q4']):
        use_dual = (qi >= 2)
        m = 'dual' if use_dual else 'single'
        for _ in range(3):
            sk = generate_seasonal_kata(
                q, mastery_level=2, year=1,
                use_dual=use_dual, use_mudras=False,
                seed=random.Random(42 + qi).randint(0, 2**31))
            student.record_session(sk['kata'], quarter=q, year=1, mode=m)
    print(student.summary())

    # 41. Adaptive curriculum
    print("\n--- Adaptive Curriculum ---")
    curriculum = adaptive_curriculum(student, n_sessions=4, seed=42)
    print(format_curriculum(curriculum, student_name=student.name))
    # Record the first curriculum session into the profile
    student.record_session(curriculum[0]['kata'], quarter='Q1', year=2, mode='dual')
    print(f"\n  After curriculum session #1: "
          f"mastery={student.mastery_level}, "
          f"sessions={len(student.sessions)}")

    # 43. Drill generator
    print("\n--- Drill Generator ---")
    # Rule 2 drill (anti-symmetry is a common weakness)
    dr_rule = generate_drill(target='rule', rule_num=2, n_reps=3,
                             mastery_level=3, seed=42)
    print(format_drill(dr_rule))

    # Group 5 drill (Triple — often under-represented)
    dr_group = generate_drill(target='group', group_num=5, n_reps=3,
                              mastery_level=3, seed=42)
    print(format_drill(dr_group))

    # Transition drill
    dr_trans = generate_drill(target='transition', n_reps=3,
                              mastery_level=3, seed=42)
    print(format_drill(dr_trans))

    # 44. Sparring system
    print("\n--- Sparring Match ---")
    # Create two students with different levels
    p1 = StudentProfile('Alexei', mastery_level=3)
    p2 = StudentProfile('Boris', mastery_level=2)
    # Give them some history
    for _ in range(4):
        sk1 = generate_seasonal_kata('Q3', mastery_level=3, year=2,
                                     use_dual=True, seed=random.Random(42).randint(0, 2**31))
        p1.record_session(sk1['kata'], quarter='Q3', year=2, mode='dual')
        sk2 = generate_seasonal_kata('Q2', mastery_level=2, year=1,
                                     use_dual=True, seed=random.Random(43).randint(0, 2**31))
        p2.record_session(sk2['kata'], quarter='Q2', year=1, mode='dual')
    spar = sparring(p1, p2, quarter='Q3', year=2, seed=42)
    print(format_sparring(spar))

    # 45. Kata DNA fingerprint
    print("\n--- Kata DNA Fingerprint ---")
    # Compare DNA of different kata types
    opt_kata = optimize_kata(length=7, mastery_level=3, target_grade='A',
                             max_attempts=20, base_seed=42)
    bk = generate_battle_kata(battle_num=4, mastery_level=4,
                              use_mudras=True, seed=42)

    dna_opt = kata_dna(opt_kata['kata'], mode='dual')
    dna_bk = kata_dna(bk['kata'], mode='dual')
    dna_res = kata_dna(rk['kata'], mode='dual')  # rk from demo 39

    print(f"  Optimized:  [{dna_opt['hex']}] {dna_opt['profile']}")
    print(f"  Battle №4:  [{dna_bk['hex']}] {dna_bk['profile']}")
    print(f"  Resonance:  [{dna_res['hex']}] {dna_res['profile']}")

    sim_ob = kata_similarity(dna_opt, dna_bk)
    sim_or = kata_similarity(dna_opt, dna_res)
    sim_br = kata_similarity(dna_bk, dna_res)
    print(f"\n  Similarity matrix:")
    print(f"    Opt↔Battle:    {sim_ob:.3f}")
    print(f"    Opt↔Resonance: {sim_or:.3f}")
    print(f"    Battle↔Res:    {sim_br:.3f}")

    # 47. Kata Library
    print("\n--- Kata Library ---")
    lib = KataLibrary()
    # Populate with kata from earlier demos
    lib.add(opt_kata['kata'], tags={'optimized', 'grade-A'}, source='optimizer',
            mastery_level=3)
    lib.add(bk['kata'], tags={'battle', 'format-4'}, source='battle_gen',
            mastery_level=4)
    lib.add(rk['kata'], tags={'resonance', 'guided'}, source='resonance_gen',
            mastery_level=3)
    # Add seasonal kata
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        sk = generate_seasonal_kata(q, mastery_level=3, year=2,
                                    use_dual=True, seed=hash(q) % 2**31)
        lib.add(sk['kata'], tags={'seasonal', q.lower()}, source='seasonal',
                mastery_level=3)
    print(f"  Library: {lib.stats()['total']} entries")
    print(f"  Grades: {lib.stats()['grades']}")
    print(f"  Tags: {lib.stats()['tags']}")

    # Search for kata similar to optimized
    search_results = lib.search(query_kata=opt_kata['kata'], top_k=3)
    print(format_library_search(search_results))

    # 48. Kata Mutation
    print("\n--- Kata Mutation ---")
    parent = opt_kata['kata']
    parent_dna = kata_dna(parent, mode='dual')
    parent_sc = score_dual_kata(parent)
    print(f"  Parent: [{parent_dna['hex']}] Grade {parent_sc['grade']} "
          f"({parent_sc['pct']:.0f}%)")
    variants = mutate_series(parent, n_variants=5, seed=42)
    for v in variants:
        print(f"    {v['mutation']:10s} → [{v['dna']['hex']}] "
              f"Grade {v['score']['grade']} ({v['score']['pct']:.0f}%) "
              f"sim={v['similarity']:.3f}")

    # 49. Session Planner
    print("\n--- Session Planner ---")
    # Reset student for clean demo
    sp_student = StudentProfile('Elena', mastery_level=3)
    for _ in range(3):
        sks = generate_seasonal_kata('Q2', mastery_level=3, year=2,
                                     use_dual=True,
                                     seed=random.Random(77+_).randint(0, 2**31))
        sp_student.record_session(sks['kata'], quarter='Q2', year=2, mode='dual')
    session = plan_session(sp_student, quarter='Q3', year=2,
                           duration_min=45, seed=42)
    print(format_session_plan(session))

    # 50. Graph statistics (summary)
    print("\n--- Graph Statistics (Summary) ---")
    # 64 base (6-bit) + 12 half-line = 76 total symbols
    all_76 = list(range(64)) + list(HALF_SYMBOLS.keys())
    total_edges_64 = 0
    for sym in range(64):
        total_edges_64 += len(get_neighbors(sym, max_changes=2))
    total_edges_64 //= 2
    from collections import deque as _deque4
    visited = {0: 0}
    queue = _deque4([0])
    while queue:
        node = queue.popleft()
        for nb in get_neighbors(node, max_changes=2):
            if nb not in visited and 0 <= nb < 64:
                visited[nb] = visited[node] + 1
                queue.append(nb)
    max_dist = max(visited.values())
    print(f"  Base graph: 64 nodes, {total_edges_64} edges, diameter={max_dist}")
    print(f"  Full alphabet: 76 nodes (64 base + 12 half-line)")
    print(f"  Single + ChVS(4):  76 x 4  = 304 states")
    print(f"  Single + mudra(8): 76 x 8  = 608 states")
    print(f"  Dual + ChVS(4):    304^2   = 92,416 (raw), ~30K valid")
    print(f"  Dual + mudra(8):   608^2   = 369,664 (raw), ~110K valid")

    # 51. Tournament
    print("\n--- Tournament ---")
    t_students = []
    for name, ml in [('Alexei', 3), ('Boris', 2), ('Vera', 4),
                     ('Galina', 3), ('Dmitri', 2), ('Elena', 3)]:
        sp = StudentProfile(name, mastery_level=ml)
        for j in range(4):
            sk = generate_seasonal_kata('Q2', mastery_level=ml, year=2,
                                        use_dual=True,
                                        seed=hash(name+str(j)) % 2**31)
            sp.record_session(sk['kata'], quarter='Q2', year=2, mode='dual')
        t_students.append(sp)
    t_result = tournament(t_students, quarter='Q3', year=2, seed=42)
    print(format_tournament(t_result))

    # 52. Difficulty Estimator
    print("\n--- Difficulty Estimator ---")
    # Compare difficulty of different kata
    test_katas = [
        ('Easy (L1, len=3)', DualMatchStickAutomaton(mastery_level=1, seed=10)
         .generate_dual_kata(length=3)),
        ('Medium (L3, len=5)', DualMatchStickAutomaton(mastery_level=3, seed=10)
         .generate_dual_kata(length=5)),
        ('Hard (L5, len=8)', DualMatchStickAutomaton(mastery_level=5, seed=10)
         .generate_dual_kata(length=8)),
        ('Optimized A', opt_kata['kata']),
        ('Battle №4', bk['kata']),
    ]
    for label, tk in test_katas:
        diff = estimate_difficulty(tk, mode='dual')
        f = diff['factors']
        print(f"  {label:20s} → {diff['difficulty']:4.1f}/10 "
              f"({diff['level_name']:12s}) "
              f"var={f['complexity_variance']:.1f} "
              f"trans={f['transition_speed']:.1f} "
              f"div={f['group_diversity']:.1f} "
              f"rule={f['rule_challenge']:.1f} "
              f"len={f['length']:.1f}")

    # 53. Achievement System
    print("\n--- Achievement System ---")
    # Create a well-practised student
    ach_student = StudentProfile('Vera', mastery_level=5)
    for i in range(12):
        q = ['Q1', 'Q2', 'Q3', 'Q4'][i % 4]
        sk = generate_seasonal_kata(q, mastery_level=min(5, 2 + i//3),
                                    year=1 + i//4, use_dual=True,
                                    seed=hash(f'vera{i}') % 2**31)
        ach_student.record_session(sk['kata'], quarter=q,
                                   year=1 + i//4, mode='dual')
    ach_result = check_achievements(ach_student)
    print(format_achievements(ach_result))

    # 54. School — full lifecycle
    print("\n--- School (Full Lifecycle) ---")
    school = School('ETD Academy')

    # Enroll students
    for sn, ml in [('Alexei', 1), ('Vera', 1), ('Boris', 1),
                   ('Galina', 1), ('Dmitri', 1)]:
        school.enroll(sn, mastery_level=ml)
    print(f"  Enrolled: {len(school.students)} students")

    # Train through 3 years (Q1-Q4 × 3)
    for yr in range(1, 4):
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            for sn in list(school.students.keys()):
                if sn not in school.graduated:
                    school.train(sn, quarter=q, year=yr,
                                 seed=hash(f'{sn}{q}{yr}') % 2**31)

    # Print roster
    roster = school.roster()
    print(format_roster(roster))

    # Graduation check
    print("\n  Graduation checks:")
    for sn in list(school.students.keys()):
        grad = school.graduate(sn)
        print(f"    {format_graduation(grad)}")

    # Tournament among non-graduated
    print()
    active_names = [n for n in school.students if n not in school.graduated]
    if len(active_names) >= 2:
        t_res = school.run_tournament(quarter='Q3', year=3, seed=42)
        print(format_tournament(t_res))

    # 55. Export / Import
    print("\n--- Export / Import ---")
    export = export_school_json(school)
    import json as _json
    json_str = _json.dumps(export, indent=2, default=str)
    print(f"  Exported: {len(json_str)} chars JSON")
    print(f"  Students: {export['n_students']}, Library: {export['n_library']}")
    print(f"  History events: {len(export['history'])}")

    # Re-import and verify
    restored = import_school_json(export)
    print(f"  Restored: {len(restored.students)} students, "
          f"{len(restored.graduated)} graduated")
    r_roster = restored.roster()
    match = all(r_roster[i]['name'] == roster[i]['name'] and
                r_roster[i]['sessions'] == roster[i]['sessions']
                for i in range(len(roster)))
    print(f"  Roster match: {match}")

    # 56. System Audit
    print("\n--- System Audit ---")
    audit = audit_system()
    print(format_audit(audit))

    # 57. Progress Chart
    print("\n--- Progress Chart ---")
    # Use school's first student for chart demo
    chart_student = list(school.students.values())[0]
    for metric in ['grade', 'resonance', 'lci']:
        pc = progress_chart(chart_student, metric=metric)
        print(pc['chart'])
        print(f"  avg={pc['avg']:.2f} best={pc['best']:.2f} "
              f"trend={pc['trend_symbol']}({pc['trend']:+.3f})")
        print()

    # 58. Dashboard
    print("--- Dashboard ---")
    db = dashboard(school)
    print(format_dashboard(db))

    # 59. Pattern Catalog
    print("\n--- Pattern Catalog ---")
    # Classify several kata
    pattern_katas = [
        ('Optimized', opt_kata['kata']),
        ('Battle', bk['kata']),
        ('Resonance', rk['kata']),
    ]
    # Also generate a known arch: low → high → low
    arch_dma = DualMatchStickAutomaton(mastery_level=3, seed=777)
    arch_kata = arch_dma.generate_dual_kata(length=7)
    pattern_katas.append(('Random L3', arch_kata))

    for label, pk in pattern_katas:
        pats = classify_kata_patterns(pk, mode='dual')
        print(f"  {label:12s} → {format_patterns(pats)}")

    # Show catalog
    print(f"\n  Catalog: {len(PATTERN_CATALOG)} named patterns")
    for key, pat in PATTERN_CATALOG.items():
        print(f"    {pat['name']:12s} — {pat['desc']}")

    # 60. Recommendation Engine
    print("\n--- Recommendation Engine ---")
    # Recommend for each student in the school
    for sn, sp in list(school.students.items())[:3]:
        rec = recommend_next(sp, library=school.library)
        print(f"  {sn:10s} → {format_recommendation(rec)}")
        print()

    # 61. Year Simulator
    print("--- Year Simulator ---")
    # Create a fresh school for year simulation
    sim_school = School('Simulation Academy')
    for sn, ml in [('Anna', 1), ('Ivan', 1), ('Lena', 1), ('Max', 1)]:
        sim_school.enroll(sn, mastery_level=ml)
    yr = simulate_school_year(sim_school, year=1,
                              sessions_per_quarter=3, seed=42)
    print(format_year_summary(yr))

    # 62. Report Card
    print("\n--- Report Card ---")
    # Use the simulated school's best student
    best_name = max(sim_school.students.keys(),
                    key=lambda n: (sum(s['pct']
                        for s in sim_school.students[n].sessions)
                        / max(len(sim_school.students[n].sessions), 1)))
    rc = report_card(sim_school.students[best_name], year=1)
    print(format_report_card(rc))

    # 63. Comparative Analytics
    print("\n--- Comparative Analytics ---")
    # Compare students from the simulated school
    sim_students = [sim_school.students[n]
                    for n in sim_school.students
                    if n not in sim_school.graduated]
    cmp = compare_students(sim_students)
    print(format_comparison(cmp))

    # 64. Graduation Ceremony
    print("\n--- Graduation Ceremony ---")
    cer = graduation_ceremony(sim_school)
    print(format_ceremony(cer))

    # 65. Curriculum Generator
    print("\n--- Curriculum Generator ---")
    # Pick a non-graduated student
    active = [n for n in sim_school.students
              if n not in sim_school.graduated]
    if active:
        cur_student = sim_school.students[active[0]]
    else:
        cur_student = list(sim_school.students.values())[0]
    cur = generate_curriculum(cur_student, weeks=8, sessions_per_week=2)
    print(format_weekly_curriculum(cur))

    # 66. Statistical Analysis
    print("\n--- Statistical Analysis ---")
    for sn in list(sim_school.students.keys())[:2]:
        st = sim_school.students[sn]
        stats = analyze_statistics(st)
        print(format_statistics(stats))
        print()

    # 67. Export System
    print("--- Export System ---")
    csv_student = list(sim_school.students.values())[0]
    csv_out = export_sessions_csv(csv_student)
    csv_lines = csv_out.split('\n')
    print(f"  Student CSV ({len(csv_lines)} rows):")
    for line in csv_lines[:4]:
        print(f"    {line}")
    print(f"    ... ({len(csv_lines)-4} more rows)")

    print(f"\n  Kata text notation (sample kata):")
    demo_dma = DualMatchStickAutomaton(mastery_level=3, seed=99)
    demo_kata = demo_dma.generate_dual_kata(length=4)
    kata_text = export_kata_text(demo_kata)
    for line in kata_text.split('\n')[:4]:
        print(f"  {line}")
    if len(demo_kata) > 4:
        print("    ...")

    csv_school = export_school_csv(sim_school)
    print(f"\n  School CSV:")
    for line in csv_school.split('\n')[:5]:
        print(f"    {line}")

    # 68. Peer Review
    print("\n--- Peer Review ---")
    all_st = list(sim_school.students.values())
    reviewer_st = all_st[0]
    author_st = all_st[1]
    # Generate a kata for the author to be reviewed
    rev_dma = DualMatchStickAutomaton(
        mastery_level=author_st.mastery_level, seed=88)
    author_kata = rev_dma.generate_dual_kata(length=5)
    pr = peer_review(reviewer_st, author_kata, seed=77)
    print(f"  {reviewer_st.name} reviews {author_st.name}'s kata:")
    print(format_peer_review(pr))

    # 69. Federation
    print("\n--- Federation ---")
    fed = Federation('World Scarab Federation')
    # Create multiple schools
    school_names = ['Moscow Academy', 'Tokyo Dojo', 'Berlin Institut']
    fed_schools = []
    for si, sn in enumerate(school_names):
        sch = School(sn)
        for pn in [f"{sn[:3]}_{j}" for j in range(1, 4)]:
            sch.enroll(pn, mastery_level=1)
        # Train
        for pn in sch.students:
            for _ in range(6):
                sch.train(pn, quarter='Q2', year=1,
                          seed=hash(pn + sn) & 0x7FFFFFFF)
        fed.register(sch)
        fed_schools.append(sch)

    print(format_federation(fed))

    # Inter-school tournament
    tourney = fed.inter_tournament(seed=42)
    if 'error' not in tourney:
        print(f"\n  Inter-school tournament winner: {tourney['winner']}")
        for r in tourney['results']:
            print(f"    {r['contestant']:25s} "
                  f"{r['grade']} ({r['pct']:.0f}%)")

    # 70. Targeted Pattern Generator
    print("\n--- Targeted Pattern Generator ---")
    for target in ['arch', 'zigzag', 'valley']:
        res = generate_targeted_kata(target, mastery_level=3,
                                     length=5, seed=42)
        print(format_targeted_result(res, target))
        print()

    # 71. Progress Timeline
    print("--- Progress Timeline ---")
    # Use sim_school Anna who has 12 sessions
    timeline_st = sim_school.students['Anna']
    events = build_timeline(timeline_st)
    print(format_timeline(events, student_name='Anna'))

    # 72. ELO Rating System
    print("\n--- ELO Rating System ---")
    elo = EloRating()
    # Register all sim_school students
    for sn in sim_school.students:
        elo.register(sn)
    # Simulate rating changes from their sessions
    for sn, st in sim_school.students.items():
        for s in st.sessions:
            elo.update_session(sn, s['pct'], s.get('mastery_level', 1))
    # Simulate a few matches
    all_names = list(sim_school.students.keys())
    for i in range(0, len(all_names) - 1, 2):
        a, b = all_names[i], all_names[i + 1]
        sa = sim_school.students[a].sessions[-1]['pct']
        sb = sim_school.students[b].sessions[-1]['pct']
        elo.update_match(a, b, sa, sb)
    print(format_elo_leaderboard(elo))

    # 73. Adaptive Difficulty
    print("\n--- Adaptive Difficulty ---")
    for sn in list(sim_school.students.keys())[:3]:
        ad = adaptive_difficulty(sim_school.students[sn])
        print(f"  {sn:10s}: {format_adaptive(ad)}")
        print()

    # 74. Matchmaking
    print("--- Matchmaking ---")
    pool = [sim_school.students[n] for n in sim_school.students]
    mm = matchmake(pool, elo=elo)
    print(format_matchmaking(mm))

    # 75. Compact Kata Notation
    print("\n--- Compact Kata Notation ---")
    nota_dma = DualMatchStickAutomaton(mastery_level=3, seed=55)
    nota_kata = nota_dma.generate_dual_kata(length=6)
    nota = verify_notation(nota_kata, mode='dual')
    print(f"  Encoded: {nota['encoded']}")
    print(f"  Length:  {nota['length']} chars")
    print(f"  Compression: {nota['compression']}")
    print(f"  Roundtrip OK: {nota['roundtrip_ok']}")

    # Decode back
    decoded_kata, dec_mode = decode_kata_notation(nota['encoded'])
    print(f"  Decoded mode: {dec_mode}, tacts: {len(decoded_kata)}")

    # 76. Heatmap
    print("\n--- Group × Rule Heatmap ---")
    hm = build_heatmap(sim_school.students['Anna'])
    print(format_heatmap(hm))

    # 77. Session Replay
    print("\n--- Session Replay ---")
    rp = replay_session(sim_school.students['Anna'], session_index=-1)
    print(format_replay(rp))

    # 78. Trend Prediction
    print("\n--- Trend Prediction ---")
    tr = predict_trend(sim_school.students['Anna'], horizon=5)
    print(format_trend(tr))

    # 79. Anomaly Detection
    print("\n--- Anomaly Detection ---")
    ad = detect_anomalies(sim_school.students['Anna'], z_threshold=1.5)
    print(format_anomalies(ad))

    # 80. Training Plan
    print("\n--- Training Plan ---")
    tp = generate_training_plan(
        sim_school.students['Anna'], weeks=4, sessions_per_week=3)
    print(format_training_plan(tp))

    # 81. Symbol Taxonomy
    print("\n--- Symbol Taxonomy ---")
    for s in [0, 7, 21, 42, 63]:
        tax = symbol_taxonomy(s)
        print(format_symbol_card(tax))

    catalog, cat_stats = build_taxonomy_catalog()
    print(f"  Catalog: {len(catalog)} symbols")
    print(f"  By symmetry: {cat_stats['by_symmetry']}")
    print(f"  By category: {cat_stats['by_category']}")

    # 82. Pattern Fingerprint
    print("\n--- Pattern Fingerprint ---")
    fp_dma1 = DualMatchStickAutomaton(mastery_level=3, seed=100)
    fp_kata1 = fp_dma1.generate_dual_kata(length=6)
    fp1 = compute_fingerprint(fp_kata1)
    print(format_fingerprint(fp1))

    fp_dma2 = DualMatchStickAutomaton(mastery_level=3, seed=200)
    fp_kata2 = fp_dma2.generate_dual_kata(length=6)
    fp2 = compute_fingerprint(fp_kata2)
    sim = fingerprint_similarity(fp1, fp2)
    print(f"\n  Similarity to another kata: {sim}")

    # 83. Diagnostic Report
    print("\n--- Diagnostic Report ---")
    diag = generate_diagnostic(sim_school.students['Anna'])
    print(format_diagnostic(diag))

    print("\n" + "=" * 60)
    # 84. Kata Mutation Engine
    print("\n--- Kata Mutation Engine ---")
    mut_dma = DualMatchStickAutomaton(mastery_level=3, seed=42)
    mut_kata = mut_dma.generate_dual_kata(length=5)
    print(f"  Original: {[(t[0], t[1]) for t in mut_kata]}")

    mirrored = mutate_kata_v2(mut_kata, 'mirror', 1.0, seed=1)
    print(f"  Mirror:   {[(t[0], t[1]) for t in mirrored]}")

    inverted = mutate_kata_v2(mut_kata, 'invert', 0.6, seed=2)
    print(f"  Invert:   {[(t[0], t[1]) for t in inverted]}")

    chain_result, chain_hist = mutation_chain(
        mut_kata,
        [('mirror', 0.5), ('bitflip', 0.3), ('scramble', 0.4)],
        seed=99)
    print(format_mutation_history(chain_hist))

    # 85. Difficulty Calibration
    print("\n--- Difficulty Calibration ---")
    cal = calibrate_difficulty(sim_school.students['Anna'], target_pct=75.0)
    print(format_calibration(cal))

    # 86. Session Comparator
    print("\n--- Session Comparator ---")
    comp = compare_sessions(sim_school.students['Anna'], 0, -1)
    print(format_comparison(comp))

    print("\n" + "=" * 60)
    # 87. Rhythm Analysis
    print("\n--- Rhythm Analysis ---")
    rhy_dma = DualMatchStickAutomaton(mastery_level=4, seed=77)
    rhy_kata = rhy_dma.generate_dual_kata(length=8)
    rhy = analyze_rhythm(rhy_kata)
    print(format_rhythm(rhy))

    # 88. Markov Transitions
    print("\n--- Markov Transition Matrix ---")
    mc = build_markov_chain(sim_school.students['Anna'], hand='left')
    print(format_markov(mc))

    # 89. Scoring Rubric
    print("\n--- Scoring Rubric ---")
    rub_dma = DualMatchStickAutomaton(mastery_level=5, seed=88)
    rub_kata = rub_dma.generate_dual_kata(length=6)
    rs = score_with_rubric(rub_kata, rule_pct=85.0)
    print(format_rubric_score(rs))

    print("\n" + "=" * 60)
    # 90. SVG Export
    print("\n--- SVG Export ---")
    svg_dma = DualMatchStickAutomaton(mastery_level=4, seed=90)
    svg_kata = svg_dma.generate_dual_kata(length=6)
    svg_str = kata_to_svg(svg_kata, title='Demo Kata L4')
    print(f"  SVG generated: {len(svg_str)} chars")
    print(f"  Starts with: {svg_str[:60]}...")
    # In production: write to file with open('kata.svg','w')

    # 91. Skill Tree
    print("\n--- Skill Tree ---")
    sk = build_skill_tree(sim_school.students['Anna'])
    print(format_skill_tree(sk))

    # 92. Batch Processor
    print("\n--- Batch Ranking ---")
    rankings = batch_rank(sim_school, metric='recent_avg')
    print(format_batch_ranking(rankings))

    bs = batch_summary(sim_school)
    print()
    print(format_batch_summary(bs))

    print("\n" + "=" * 60)
    print("v27: SVG export, skill tree, batch processor.")

    # 93. Kata Diff
    print("\n--- Kata Diff ---")
    dma_d1 = DualMatchStickAutomaton(mastery_level=3, seed=931)
    dma_d2 = DualMatchStickAutomaton(mastery_level=3, seed=932)
    k_d1 = dma_d1.generate_dual_kata(length=8)
    k_d2 = dma_d2.generate_dual_kata(length=8)
    diff = kata_diff(k_d1, k_d2, label_a='Seed931', label_b='Seed932')
    print(format_kata_diff(diff))

    # 94. Achievement Badges
    print("\n--- Achievement Badges ---")
    badges = check_badges(sim_school.students['Anna'])
    print(format_badges(badges))

    # 95. Annotated Replay
    print("\n--- Annotated Replay ---")
    replay_session = sim_school.students['Anna'].sessions[-1]
    ann = annotate_session(replay_session)
    print(format_annotated_replay(ann, max_tacts=8))

    print("\n" + "=" * 60)
    print("v28: Kata diff, achievement badges, annotated replay.")

    # 96. Data Export
    print("\n--- Data Export ---")
    anna_json = export_student_json(sim_school.students['Anna'])
    print(f"  JSON export: {anna_json['name']}, "
          f"{anna_json['n_sessions']} sessions, "
          f"avg={anna_json['avg_score']}%, "
          f"badges={len(anna_json['badges'])}")
    csv_str = export_sessions_csv(sim_school.students['Anna'])
    csv_lines = csv_str.split('\n')
    print(f"  CSV: {len(csv_lines)} lines (header + {len(csv_lines) - 1} rows)")
    print(f"  CSV header: {csv_lines[0]}")
    rank_csv = export_rankings_csv(sim_school)
    print(f"  Rankings CSV: {len(rank_csv.split(chr(10)))} lines")

    # 97. Notification System
    print("\n--- Notifications ---")
    nm = NotificationManager()
    for name, st97 in sim_school.students.items():
        nm.check_student_events(st97)
    print(nm.format_notifications())
    print(f"  Unread: {len(nm.unread())}")
    nm.mark_all_read()
    print(f"  After mark_all_read: {len(nm.unread())} unread")

    # 98. Full Report
    print("\n--- Full Report ---")
    rpt = generate_full_report(sim_school.students['Anna'],
                               school=sim_school)
    print(format_full_report(rpt))

    print("\n" + "=" * 60)
    print("v29: Data export/import, notifications, report generator.")

    # 99. Training Scheduler
    print("\n--- Training Scheduler ---")
    sched = TrainingScheduler(sim_school.students['Anna'],
                              sessions_per_week=4)
    print(f"  Focus recommendation: {sched.recommend_focus()}")
    print(f"  Difficulty recommendation: {sched.recommend_difficulty()}")
    week1 = sched.generate_week(week_number=1)
    # Simulate completing some days
    for d_idx, entry in enumerate(week1):
        if entry['type'] == 'training':
            sched.complete_day(week1, d_idx, score=85)
    print(sched.format_week(week1))
    print(f"  Adherence: {sched.adherence_rate()}%")

    # 100. Analytics Dashboard (demo #100!)
    print("\n--- Analytics Dashboard (demo #100) ---")
    for sname in ['Anna', 'Ivan']:
        analytics = compute_analytics(sim_school.students[sname])
        print(format_analytics_dashboard(
            sim_school.students[sname], analytics))

    # 101. Custom Rule Builder
    print("\n--- Custom Rule Builder ---")
    engine = CustomRuleEngine()

    rule1 = (RuleBuilder('CX1', 'No Peak Defense')
             .when_group(7)
             .severity('error')
             .message('Group 7 (peak defense) symbols forbidden in drill')
             .build())
    engine.add_rule(rule1)

    rule2 = (RuleBuilder('CX2', 'Min Score')
             .when_score_below(40)
             .severity('warning')
             .message('Tact score too low')
             .build())
    engine.add_rule(rule2)

    rule3 = (RuleBuilder('CX3', 'No Excessive Repeats')
             .when_repeat(3)
             .severity('warning')
             .message('Too many consecutive repeats')
             .build())
    engine.add_rule(rule3)

    print(engine.summary())

    # Validate some test tacts
    test_tacts = [
        {'sym': 5, 'score': 80, 'consecutive': 1},
        {'sym': 63, 'score': 70, 'consecutive': 1},   # group 7
        {'sym': 10, 'score': 30, 'consecutive': 4},    # low score + repeats
        {'sym': 20, 'score': 90, 'consecutive': 1},
    ]
    viols = engine.validate_sequence(test_tacts)
    print(f"  Violations found: {len(viols)}")
    for v in viols:
        print(f"    Tact {v['tact']}: [{v['rule']}] {v['message']} "
              f"({v['severity']})")

    print("\n" + "=" * 60)
    print("v30: Training scheduler, analytics dashboard, custom rules.")

    # 102. Goal Tracking
    print("\n--- Goal Tracking ---")
    gt = GoalTracker(sim_school.students['Anna'])
    gt.add_goal('score', 90, 'Reach 90% average')
    gt.add_goal('sessions', 20, 'Complete 20 sessions')
    gt.add_goal('streak', 10, 'Win streak of 10')
    gt.add_goal('mastery', 7, 'Reach peak mastery')

    # Show suggestions too
    suggestions = gt.suggest_goals()
    print(f"  Auto-suggested goals: {len(suggestions)}")
    for s_type, s_target, s_desc in suggestions:
        print(f"    → {s_desc} ({s_type}: {s_target})")

    print(gt.format_goals())

    # 103. Peer Comparison
    print("\n--- Peer Comparison ---")
    cmp_result = peer_compare(sim_school.students['Anna'],
                               sim_school.students['Ivan'])
    print(format_peer_compare(cmp_result))

    cmp2 = peer_compare(sim_school.students['Lena'],
                         sim_school.students['Max'])
    print(format_peer_compare(cmp2))

    # 104. Session Playback
    print("\n--- Session Playback ---")
    pb = SessionPlayback('Anna', session_index=0)
    import random as _rnd_pb
    _rnd_pb.seed(777)
    for t_idx in range(20):
        sym = _rnd_pb.randint(0, 63)
        score = _rnd_pb.uniform(50, 100)
        viols = [] if _rnd_pb.random() > 0.3 else [{'rule': 'R1_Zone'}]
        pb.record_frame({'sym': sym, 'score': round(score, 1),
                         'violations': viols})
    pb.add_marker(0, 'Session start')
    pb.add_marker(9, 'Midpoint')
    pb.add_marker(19, 'Finish')

    print(pb.summary())
    print(pb.format_playback(start=0, count=10))
    print(f"\n  Violations: {len(pb.find_violations())} frames")
    peaks = pb.find_peaks(3)
    print(f"  Top peaks: {[p['score'] for p in peaks]}")

    print("\n" + "=" * 60)
    print("v31: Goal tracking, peer comparison, session playback.")

    # 105. Training Templates
    print("\n--- Training Templates ---")
    anna = sim_school.students['Anna']
    print(format_template_catalog(anna))
    avail = get_available_templates(anna)
    print(f"\n  Available for Anna (L{anna.mastery_level}): "
          f"{len(avail)}/{len(TRAINING_TEMPLATES)}")
    cfg105 = apply_template('endurance', anna)
    print(f"  Applied 'endurance': {cfg105['n_tacts']} tacts, "
          f"pool={cfg105['pool_size']} symbols, "
          f"focus={cfg105['focus']}")

    # 106. Correlation Analysis
    print("\n--- Correlation Analysis ---")
    cm = correlation_matrix(anna)
    print(format_correlation_matrix(cm))
    insights = find_insights(anna)
    print("\n  Insights:")
    for ins in insights:
        print(f"    → {ins}")

    # 107. System Configuration
    print("\n--- System Configuration ---")
    config = ScarabConfig()
    config.set('passing_score', 75)
    config.set('analytics_window', 8)
    config.set('default_sessions_per_week', 5)
    print(config.format_config(only_changed=True))
    issues = config.validate()
    print(f"  Validation: {'OK' if not issues else f'{len(issues)} issues'}")
    print(f"  Changed keys: {config.diff_from_defaults()}")

    # Reset and show default
    config.reset('passing_score')
    print(f"  After reset passing_score: {config.get('passing_score')}")

    print("\n" + "=" * 60)
    print("v32: Training templates, correlation analysis, config manager.")

    # 108. Feedback Loop
    print("\n--- Feedback Loop ---")
    fl = FeedbackLoop(sim_school.students['Anna'], lookback=5)
    cycle1 = fl.run_cycle()
    print(fl.format_cycle(cycle1))

    fl_ivan = FeedbackLoop(sim_school.students['Ivan'], lookback=5)
    cycle2 = fl_ivan.run_cycle()
    print(fl_ivan.format_cycle(cycle2))

    # 109. Progression Path
    print("\n--- Progression Path ---")
    path = compute_progression_path(sim_school.students['Anna'])
    print(format_progression_path(path))

    path_ivan = compute_progression_path(sim_school.students['Ivan'])
    print(format_progression_path(path_ivan))

    # 110. Heatmap Analysis
    print("\n--- Heatmap Analysis ---")
    hm = session_heatmap(sim_school.students['Anna'], metric='score')
    print(format_session_heatmap(hm, title='Anna: Score Heatmap'))

    hm_ivan = session_heatmap(sim_school.students['Ivan'], metric='score')
    print(format_session_heatmap(hm_ivan, title='Ivan: Score Heatmap'))

    print("\n" + "=" * 60)
    print("v33: Feedback loop, progression path, heatmap analysis.")

    # 111. Event Log
    print("\n--- Event Log ---")
    elog = EventLog()
    for sname, st111 in sim_school.students.items():
        for si in range(len(st111.sessions)):
            log_student_session(elog, st111, si)
    elog.log('system', 'Simulation complete', source='main')
    print(elog.format_log(max_lines=10))
    by_level = elog.count_by_level()
    by_cat = elog.count_by_category()
    print(f"  By level: {by_level}")
    print(f"  By category: {by_cat}")
    warnings = elog.query(level='warning')
    print(f"  Warnings: {len(warnings)}")

    # 112. Kata Difficulty Scorer
    print("\n--- Kata Difficulty ---")
    # Easy kata (low groups, short)
    easy_kata = [0, 1, 2, 3, 4, 5]
    d_easy = score_kata_difficulty(easy_kata)
    print(format_kata_difficulty(d_easy))

    # Hard kata (high groups, diverse)
    hard_kata = [5, 20, 35, 50, 57, 63, 10, 40, 55, 62,
                 3, 30, 45, 58]
    d_hard = score_kata_difficulty(hard_kata)
    print(format_kata_difficulty(d_hard))

    # 113. Performance Predictor
    print("\n--- Performance Predictor ---")
    for sname in ['Anna', 'Ivan', 'Lena']:
        st113 = sim_school.students[sname]
        for method in ['linear', 'ewma', 'ensemble']:
            pred = predict_next_score(st113, method=method)
            print(format_prediction(pred, student_name=sname))

    print("\n" + "=" * 60)
    print("v34: Event log, kata difficulty scorer, performance predictor.")

    # 114. Curriculum System
    print("\n--- Curriculum ---")
    curriculum = Curriculum().build_standard()
    for sname in ['Anna', 'Ivan']:
        ev = curriculum.evaluate(sim_school.students[sname])
        print(curriculum.format_curriculum(ev))

    # 115. School Progress Overview
    print("\n--- School Progress Overview ---")
    overview = school_progress_overview(sim_school, curriculum=curriculum)
    print(format_school_overview(overview))

    # 116. Architecture Summary
    print("\n--- Architecture Summary ---")
    print(architecture_summary())

    print("\n" + "=" * 60)
    print("v35: Curriculum, school progress, architecture summary.")

    # 117. Skill Tree
    print("\n--- Skill Tree ---")
    stree = SkillTree()
    stree.evaluate(sim_school.students['Anna'])
    print(stree.format_tree(student_name='Anna'))

    stree2 = SkillTree()
    stree2.evaluate(sim_school.students['Ivan'])
    print(stree2.format_tree(student_name='Ivan'))

    # 118. Session Simulator
    print("\n--- Session Simulator ---")
    sim118 = SessionSimulator(sim_school.students['Anna'], n_simulations=200)
    sim_r = sim118.simulate(seed=42)
    print(sim118.format_simulation(sim_r))

    # 119. Leaderboard
    print("\n--- Leaderboard ---")
    lb = Leaderboard(sim_school)
    print(lb.format_leaderboard('score'))
    print(lb.format_leaderboard('mastery'))
    print(lb.format_composite())

    print("\n" + "=" * 60)
    print("v36: Skill tree, session simulator, leaderboard.")

    # 120. Pattern Recognition
    print("\n--- Pattern Recognition ---")
    for sname in ['Anna', 'Ivan', 'Lena']:
        pats = detect_patterns(sim_school.students[sname])
        print(format_detected_patterns(pats, student_name=sname))

    # 121. Mentor System
    print("\n--- Mentor Assessment ---")
    mentor = Mentor(sim_school.students['Anna'])
    print(mentor.format_assessment())

    mentor2 = Mentor(sim_school.students['Ivan'])
    print(mentor2.format_assessment())

    # 122. Daily Challenges
    print("\n--- Daily Challenges ---")
    dcg = DailyChallengeGenerator(seed=99)
    ch = dcg.generate(sim_school.students['Anna'], day_number=1)
    print(dcg.format_challenge(ch))

    week = dcg.generate_week(sim_school.students['Anna'], start_day=1)
    print(dcg.format_week(week))

    print("\n" + "=" * 60)
    print("v37: Pattern recognition, mentor system, daily challenges.")

    # 123. Study Groups
    print("\n--- Study Groups ---")
    sg = StudyGroup("Alpha Team", max_size=4)
    sg.add_member(sim_school.students['Anna'])
    sg.add_member(sim_school.students['Ivan'])
    sg.add_member(sim_school.students['Lena'])
    print(sg.format_group())

    sg2 = StudyGroup("Beta Team", max_size=4)
    sg2.add_member(sim_school.students['Max'])
    print(sg2.format_group())

    # 124. Symbol Encyclopedia
    print("\n--- Symbol Encyclopedia ---")
    enc = symbol_encyclopedia()
    print(format_encyclopedia(enc, group_filter=1))
    print(f"\n  Total symbols in encyclopedia: {len(enc)}")
    tiers = {}
    for e in enc:
        tiers[e['tier']] = tiers.get(e['tier'], 0) + 1
    print(f"  Tiers: {tiers}")

    # 125. Combo System
    print("\n--- Combo System ---")
    import random as _rnd_combo
    _rnd_combo.seed(555)
    combo_seq = [_rnd_combo.randint(0, 63) for _ in range(14)]
    combos = detect_combos(combo_seq)
    print(f"  Sequence: {combo_seq}")
    print(format_combos(combos))

    # Craft a palindrome combo
    half = [5, 20, 35, 50]
    palindrome_seq = half + [30] + half[::-1]
    p_combos = detect_combos(palindrome_seq)
    print(format_combos(p_combos, title='Palindrome Combo'))

    print("\n" + "=" * 60)
    print("v38: Study groups, symbol encyclopedia, combo system.")

    # 126. Review Queue
    print("\n--- Review Queue ---")
    rq = build_review_queue(sim_school.students['Anna'])
    print(rq.format_queue())
    if rq.size() > 0:
        nxt = rq.pop_next()
        print(f"  Popped: {nxt['key']} (priority {nxt['priority']:.1f})")

    # 127. Spaced Repetition
    print("\n--- Spaced Repetition ---")
    srs = SpacedRepetition()
    for s in range(20):
        srs.add_card(s)
    # Simulate reviews
    import random as _rnd_srs
    _rnd_srs.seed(42)
    for session in range(1, 6):
        due = srs.due_cards(session)
        for sym, card in due[:5]:
            quality = _rnd_srs.randint(2, 5)
            srs.review(sym, quality, session)
    print(srs.format_srs(current_session=6))

    # 128. Weakness Analyzer
    print("\n--- Weakness Analysis ---")
    for sname in ['Anna', 'Ivan']:
        ws = analyze_weaknesses(sim_school.students[sname])
        print(format_weaknesses(ws, student_name=sname))

    print("\n" + "=" * 60)
    print("v39: Review queue, spaced repetition, weakness analyzer.")

    # 129. Statistics Engine
    print("\n--- Statistics Engine ---")
    stat_engine = StatisticsEngine()
    for sname in ['Anna', 'Ivan']:
        report = stat_engine.student_report(sim_school.students[sname])
        print(stat_engine.format_report(report))

    # Effect size between students
    anna_scores = [s['pct'] for s in sim_school.students['Anna'].sessions]
    ivan_scores = [s['pct'] for s in sim_school.students['Ivan'].sessions]
    d = StatisticsEngine.effect_size(anna_scores, ivan_scores)
    print(f"\n  Cohen's d (Anna vs Ivan): {d}")

    # 130. Achievement Gallery
    print("\n--- Achievement Gallery ---")
    for sname in ['Anna', 'Ivan']:
        gallery = check_achievement_gallery(sim_school.students[sname])
        print(format_achievement_gallery(gallery, student_name=sname))

    # 131. Grand Summary v36-v40
    print("\n" + "=" * 60)
    print("v40: Statistics engine, achievement gallery.")
    print(f"\n  Total: 131 demos, 55 parts, v1-v40.")
    print(f"  Code: ~{15000} lines, Docs: ~{4800} lines")
    print("  v36-v40 block complete.")

    # 132. Scenario Engine
    print("\n--- Scenario Engine ---")
    for sc_id in ['boot_camp', 'precision_drill', 'mastery_test']:
        sc = SCENARIOS[sc_id]
        fake_result = {'pct': 88.5, 'violations': [{'r': 'R1'}],
                       'length': 14}
        ev = sc.evaluate(fake_result)
        print(format_scenario_result(ev))

    # 133. Progress Milestones
    print("\n--- Progress Milestones ---")
    mt = MilestoneTracker()
    mt.check(sim_school.students['Anna'])
    print(mt.format_milestones(student_name='Anna'))

    mt2 = MilestoneTracker()
    mt2.check(sim_school.students['Ivan'])
    print(mt2.format_milestones(student_name='Ivan'))

    # 134. Data Pipeline
    print("\n--- Data Pipeline ---")
    pipe = DataPipeline('student_averages')
    pipe.extract(sim_school)
    pipe.aggregate('student', 'pct', 'mean')
    pipe.sort_by('mean_pct', reverse=True)
    pipe.transform()
    print(pipe.format_pipeline())
    results = pipe.load()
    for r in results:
        print(f"  {r['student']:12s} avg={r['mean_pct']}%  "
              f"({r['count']} sessions)")

    # Pipeline 2: filter
    pipe2 = DataPipeline('high_scores')
    pipe2.extract(sim_school)
    pipe2.add_transform(
        lambda data: [r for r in data if r['pct'] >= 85],
        name='filter(pct>=85)')
    pipe2.sort_by('pct', reverse=True)
    pipe2.transform()
    high = pipe2.load()
    print(f"\n  High scores (≥85%): {len(high)} records")

    print("\n" + "=" * 60)
    print("v41: Scenario engine, milestones, data pipeline.")

    # 135. Adaptive Quiz
    print("\n--- Adaptive Quiz ---")
    quiz = AdaptiveQuiz(sim_school.students['Anna'], n_questions=8,
                        seed=123)
    import random as _rnd_quiz
    _rnd_quiz.seed(123)
    for qi in range(8):
        q = quiz.generate_question()
        # Simulate answer: 70% chance correct
        ans = q['correct_answer'] if _rnd_quiz.random() < 0.7 \
            else _rnd_quiz.randint(1, 7)
        quiz.answer(qi, ans)
    print(quiz.format_quiz())

    # 136. Group Proficiency Matrix
    print("\n--- Group Proficiency ---")
    for sname in ['Anna', 'Ivan']:
        prof = compute_group_proficiency(sim_school.students[sname])
        print(format_proficiency_matrix(prof, student_name=sname))

    # 137. Session Journal
    print("\n--- Session Journal ---")
    journal = SessionJournal('Anna')
    journal.add_entry(1, 'First session, felt uncertain', ['start'], mood=3)
    journal.add_entry(3, 'Improving quickly!', ['progress'], mood=4)
    journal.add_entry(5, 'Struggled with G5 symbols',
                      ['difficulty', 'G5'], mood=2)
    journal.add_entry(8, 'Got my first A grade!',
                      ['achievement', 'gradeA'], mood=5)
    journal.add_entry(12, 'Feeling confident now',
                      ['milestone'], mood=5)
    print(journal.format_journal())

    # Mood trend
    moods = journal.mood_trend()
    print(f"  Mood trend: {moods}")

    print("\n" + "=" * 60)
    print("v42: Adaptive quiz, group proficiency, session journal.")

    # 138. Training Plan Optimizer
    print("\n--- Training Plan Optimizer ---")
    tpo = TrainingPlanOptimizer(sim_school.students['Anna'],
                                sessions_per_week=4)
    plan = tpo.optimize(n_weeks=4)
    print(tpo.format_plan(plan))

    # 139. Symbol Similarity
    print("\n--- Symbol Similarity ---")
    for target in [0, 15, 32, 63]:
        sim_list = find_similar_symbols(target, top_n=4)
        print(format_similarity(target, sim_list))

    # 140. Rank System
    print("\n--- Rank System ---")
    for sname in ['Anna', 'Ivan', 'Lena', 'Max']:
        rk = compute_rank(sim_school.students[sname])
        print(format_rank(rk, student_name=sname))

    print("\n" + "=" * 60)
    print("v43: Training optimizer, symbol similarity, rank system.")

    # 141. Event Bus
    print("\n--- Event Bus ---")
    bus = EventBus()
    log_msgs = []
    bus.on('session_complete', lambda e: log_msgs.append(
        f"Session done: {e['data'].get('student', '?')}"))
    bus.on('level_up', lambda e: log_msgs.append(
        f"Level up: {e['data'].get('student', '?')}"))
    bus.on('session_complete', lambda e: log_msgs.append(
        f"Score: {e['data'].get('score', 0)}%"))

    bus.emit('session_complete', {'student': 'Anna', 'score': 88})
    bus.emit('level_up', {'student': 'Anna', 'new_level': 6})
    bus.emit('session_complete', {'student': 'Ivan', 'score': 92})

    print(bus.format_bus())
    print(f"  Log messages: {log_msgs}")
    print(f"  History: {len(bus.history())} events")

    # 142. Session Comparison
    print("\n--- Session Comparison ---")
    for sname in ['Anna', 'Ivan']:
        cmp = compare_first_last(sim_school.students[sname])
        print(format_session_comparison(cmp))

    # 143. Coaching Engine
    print("\n--- Coaching Engine ---")
    for sname in ['Anna', 'Ivan', 'Lena']:
        coach = CoachingEngine(sim_school.students[sname])
        print(coach.format_brief())

    print("\n" + "=" * 60)
    print("v44: Event hooks, session comparison, coaching engine.")
