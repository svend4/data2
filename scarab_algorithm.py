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
  - Three nested levels: BVS (body), SVS (forearm), MVS (hand)
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


def three_level_scarab(space_size=10.0, k_bvs=2.0, k_svs=1.5, k_mvs=1.0,
                       steps=500, seed=None):
    """
    Three-level nested Scarab: BVS + SVS + MVS superimposed.

    BVS (body):    large loops, A=80-200cm equivalent
    SVS (forearm): medium loops, A=30-40cm equivalent
    MVS (hand):    small loops, A=10-15cm equivalent

    At mastery: ω_BVS = ω_SVS = ω_MVS (resonance)
    """
    if seed is not None:
        random.seed(seed)

    # Amplitude ratios (from Kryukov's sphere sizes)
    A_bvs = space_size * 0.6       # ~60% of space
    A_svs = space_size * 0.15      # ~15% of space
    A_mvs = space_size * 0.05      # ~5% of space

    # Angular frequencies (resonance = all equal)
    omega_bvs = 1.0
    omega_svs = 1.0    # resonance condition
    omega_mvs = 1.0    # resonance condition

    trajectory = []
    for i in range(steps):
        t = 2 * math.pi * i / steps * 3  # 3 full cycles

        # BVS: large deformed figure-8
        x_bvs = A_bvs * math.sin(omega_bvs * t)
        y_bvs = A_bvs * (math.sin(2 * omega_bvs * t + math.pi/2) +
                          (k_bvs - 1) / (k_bvs + 1) * math.sin(omega_bvs * t))

        # SVS: medium figure-8, phase-shifted
        x_svs = A_svs * math.sin(omega_svs * t * 2 + math.pi/3)
        y_svs = A_svs * (math.sin(2 * omega_svs * t * 2 + math.pi/2) +
                          (k_svs - 1) / (k_svs + 1) * math.sin(omega_svs * t * 2))

        # MVS: small figure-8, high frequency
        x_mvs = A_mvs * math.sin(omega_mvs * t * 5 + math.pi/7)
        y_mvs = A_mvs * (math.sin(2 * omega_mvs * t * 5 + math.pi/2) +
                          (k_mvs - 1) / (k_mvs + 1) * math.sin(omega_mvs * t * 5))

        x = x_bvs + x_svs + x_mvs
        y = y_bvs + y_svs + y_mvs

        trajectory.append((x, y))

    return trajectory


# ═══════════════════════════════════════════════════════════
# MOVEMENT ALPHABET: 76-symbol system
# ═══════════════════════════════════════════════════════════

# Square edges and diagonals as bit flags
TOP    = 0b000001  # 1
BOTTOM = 0b000010  # 2
LEFT   = 0b000100  # 4
RIGHT  = 0b001000  # 8
DIAG1  = 0b010000  # 16  (╲ top-left to bottom-right)
DIAG2  = 0b100000  # 32  (╱ top-right to bottom-left)

# Full edges: 6 bits → 2^6 = 64 base combinations
# Plus 12 half-lines → 76 total

# Named symbols (subset)
SYMBOLS = {
    'empty':    0b000000,    # · point (symbol 01)
    'diag1':    DIAG1,       # ╲ (symbol 03)
    'diag2':    DIAG2,       # ╱
    'cross_d':  DIAG1|DIAG2, # X diagonal cross (symbol 06)
    'corner_bl': BOTTOM|LEFT, # └ (symbol 05)
    'corner_br': BOTTOM|RIGHT,# ┘ (symbol 11)
    'corner_tl': TOP|LEFT,    # ┌
    'corner_tr': TOP|RIGHT,   # ┐
    'horiz':    TOP|BOTTOM,   # ─ horizontal pair
    'vert':     LEFT|RIGHT,   # │ vertical pair
    'cross_hv': TOP|BOTTOM|LEFT|RIGHT,  # + (but this is the square □)
    'square':   TOP|BOTTOM|LEFT|RIGHT,  # □ (symbol 12)
    'sq_d1':    TOP|BOTTOM|LEFT|RIGHT|DIAG1,      # □+╲ (symbol 13)
    'sq_d2':    TOP|BOTTOM|LEFT|RIGHT|DIAG2,      # □+╱
    'sq_full':  TOP|BOTTOM|LEFT|RIGHT|DIAG1|DIAG2, # ☒ (symbol 14)
    'K_shape':  LEFT|DIAG1|DIAG2,  # K (symbol 07)
    'M_shape':  LEFT|RIGHT|DIAG1,  # M-like
    'T_shape':  TOP|LEFT,          # ⊥
    'tri_up':   DIAG1|DIAG2,       # △ (alias for cross_d viewed differently)
    'Z_shape':  TOP|DIAG1|BOTTOM,  # Z
    'N_shape':  LEFT|DIAG1|RIGHT,  # N
}


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
    print("SCARAB ALGORITHM — Controlled Chaos Movement Generator")
    print("Based on Kryukov's ETD / Deformed Figure-8")
    print("=" * 60)

    # 1. Deformed Lissajous figures
    print("\n--- Deformed Lissajous (k=1, symmetric) ---")
    traj_sym = deformed_lissajous(k=1.0, points=20)
    for i, (x, y) in enumerate(traj_sym[:10]):
        print(f"  t={i:2d}: ({x:+.3f}, {y:+.3f})")

    print("\n--- Deformed Lissajous (k=5, nevalyashka) ---")
    traj_def = deformed_lissajous(k=5.0, points=20)
    for i, (x, y) in enumerate(traj_def[:10]):
        print(f"  t={i:2d}: ({x:+.3f}, {y:+.3f})")

    # 2. Scarab trajectory
    print("\n--- Scarab 2D (k=2, space=10) ---")
    traj_scarab = scarab_2d(space_size=10.0, k=2.0, steps=20, seed=42)
    for i, (x, y) in enumerate(traj_scarab[:10]):
        print(f"  step {i:2d}: ({x:+.2f}, {y:+.2f})")

    # 3. Symbol display
    print("\n--- Movement Alphabet Symbols ---")
    for name, sym in list(SYMBOLS.items())[:8]:
        print(f"\n  {name} ({sym:06b}):")
        for line in symbol_to_ascii(sym).split('\n'):
            print(f"    {line}")

    # 4. Generate kata
    print("\n--- Generated Kata (7 tacts) ---")
    kata = generate_kata(length=7, seed=42)
    frames = animate_kata_text(kata)
    for frame in frames:
        print(frame)

    # 5. Three-level trajectory
    print("\n--- Three-Level Scarab (BVS+SVS+MVS) ---")
    traj_3 = three_level_scarab(space_size=10.0, k_bvs=3.0, k_svs=1.5,
                                 k_mvs=1.0, steps=20, seed=42)
    for i, (x, y) in enumerate(traj_3[:10]):
        print(f"  step {i:2d}: ({x:+.3f}, {y:+.3f})")

    # 6. Training plan
    print("\n--- Annual Training Plan (Kryukov) ---")
    for q, info in TRAINING_PLAN.items():
        print(f"\n  {q}: {info['name']}")
        print(f"    Kata length: {info['kata_length']} tacts")
        print(f"    Deformation k: {info['k_range'][0]:.1f} - {info['k_range'][1]:.1f}")
        print(f"    Groups: {info['groups']}")
        print(f"    Sessions: {info['sessions']}")
        print(f"    → {info['description']}")

    # 7. Graph statistics
    print("\n--- Alphabet Graph Statistics ---")
    all_64 = list(range(64))  # all 6-bit combinations
    total_edges = 0
    for sym in all_64:
        neighbors = get_neighbors(sym, max_changes=2)
        total_edges += len(neighbors)
    total_edges //= 2  # undirected
    print(f"  Nodes (6-bit symbols): {len(all_64)}")
    print(f"  Edges (≤2 line changes): {total_edges}")
    print(f"  Avg degree: {2 * total_edges / len(all_64):.1f}")
    print(f"  Density: {2 * total_edges / (64 * 63):.3f}")

    print("\n" + "=" * 60)
    print("Complete.")
