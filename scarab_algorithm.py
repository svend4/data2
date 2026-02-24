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
        """
        partner_complexity = symbol_complexity(partner_sym)

        candidates = []
        for s in self.left.available_symbols:
            if s == partner_sym:
                continue
            if zones_conflict(s, partner_sym):
                continue
            if is_anti_symmetric(s, partner_sym):
                candidates.append(s)

        # If no perfect complement, relax to just no-conflict
        if not candidates:
            candidates = [s for s in self.left.available_symbols
                          if not zones_conflict(s, partner_sym) and s != partner_sym]

        if not candidates:
            candidates = self.left.available_symbols

        # Rule 5: Complexity conservation — prefer balanced pairs
        if enforce_conservation and len(candidates) > 1:
            target_c = max(0, self.target_complexity - partner_complexity)
            # Sort by closeness to target complexity
            balanced = sorted(candidates,
                              key=lambda s: abs(symbol_complexity(s) - target_c))
            # Take top third (allow some variety)
            cutoff = max(3, len(balanced) // 3)
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
        switch_at = self.rng.choice([1, 3])
        if self.lead_count >= switch_at:
            self.lead = 'right' if self.lead == 'left' else 'left'
            self.lead_count = 0
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

    if use_dual:
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
    else:
        msa = MatchStickAutomaton(mastery_level=eff_mastery,
                                   seed=rng.randint(0, 2**31))
        msa.available_symbols = [s for s in range(64) if get_group(s) in groups]
        kata = msa.generate_kata(length=kata_length)
        result['kata'] = kata
        result['mode'] = 'single'

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


def generate_kata(length=7, start_symbol=None, seed=None):
    """
    Generate a movement sequence (kata) using alphabet transitions.

    Rules:
    - Change ≤ 2 lines per step
    - Anti-circle: no return to same symbol within 4 steps
    - Odd series lengths: {1, 3, 5, 7}
    - Camouflage/threat: alternate dominant side
    """
    if seed is not None:
        random.seed(seed)

    if start_symbol is None:
        start_symbol = 0b000000  # empty / ready position

    sequence = [start_symbol]
    recent = [start_symbol]

    for step in range(length - 1):
        neighbors = get_neighbors(sequence[-1], max_changes=2)

        # Filter: anti-circle (no return to recent 4)
        candidates = [n for n in neighbors if n not in recent[-4:]]

        if not candidates:
            candidates = neighbors  # fallback

        # Preference: alternate symmetry (camouflage/threat)
        current = sequence[-1]
        current_left = bool(current & LEFT) or bool(current & DIAG2)

        # Prefer symbols that shift dominance to other side
        preferred = []
        for c in candidates:
            c_right = bool(c & RIGHT) or bool(c & DIAG1)
            if current_left and c_right:
                preferred.append(c)
            elif not current_left and not c_right:
                preferred.append(c)

        if preferred:
            next_sym = random.choice(preferred)
        else:
            next_sym = random.choice(candidates)

        sequence.append(next_sym)
        recent.append(next_sym)
        if len(recent) > 7:
            recent.pop(0)

    return sequence


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
# DEMO / MAIN
# ═══════════════════════════════════════════════════════════

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

    # 21. Graph statistics (summary)
    print("\n--- Graph Statistics (Summary) ---")
    all_64 = list(range(64))
    total_edges = 0
    for sym in all_64:
        total_edges += len(get_neighbors(sym, max_changes=2))
    total_edges //= 2
    from collections import deque as _deque
    visited = {0: 0}
    queue = _deque([0])
    while queue:
        node = queue.popleft()
        for nb in get_neighbors(node, max_changes=2):
            if nb not in visited and 0 <= nb < 64:
                visited[nb] = visited[node] + 1
                queue.append(nb)
    max_dist = max(visited.values())
    print(f"  Single hand: 76 nodes, {total_edges} edges, diameter={max_dist}")
    print(f"  Single + ChVS(4):  76 x 4  = 304 states")
    print(f"  Single + mudra(8): 76 x 8  = 608 states")
    print(f"  Dual + ChVS(4):    304^2   = 92,416 (raw), ~30K valid")
    print(f"  Dual + mudra(8):   608^2   = 369,664 (raw), ~110K valid")

    print("\n" + "=" * 60)
    print("v6: Scoring system, seasonal kata generator,")
    print("    hard zone enforcement, rhythm/tempo patterns.")
