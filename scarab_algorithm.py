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

    # 8. Training plan with symbol counts per quarter
    print("\n--- Annual Training Plan (Kryukov) ---")
    for q, info in TRAINING_PLAN.items():
        available = sum(1 for s in range(64) if get_group(s) in info['groups'])
        print(f"  {q}: {info['name']:35s} | kata={info['kata_length']} "
              f"| groups={info['groups']} | {available} symbols")

    # 9. Graph statistics
    print("\n--- Alphabet Graph Statistics ---")
    all_64 = list(range(64))
    total_edges = 0
    for sym in all_64:
        neighbors = get_neighbors(sym, max_changes=2)
        total_edges += len(neighbors)
    total_edges //= 2
    print(f"  Nodes: {len(all_64)} base + {len(HALF_SYMBOLS)} half = "
          f"{len(all_64) + len(HALF_SYMBOLS)}")
    print(f"  Edges (<=2 changes): {total_edges} | "
          f"Avg degree: {2*total_edges/len(all_64):.1f} | "
          f"Density: {2*total_edges/(64*63):.3f}")
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
    print(f"  Diameter (from empty): {max_dist} | "
          f"Miller's law: 7+/-2 -> {max_dist} is within range!")

    print("\n" + "=" * 60)
    print("Complete. MSA: 76 symbols x 4 ChVS = 304 states ~ 310 ETD volumes.")
