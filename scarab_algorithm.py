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
    print("v24: Symbol taxonomy, fingerprinting, diagnostic reports.")
