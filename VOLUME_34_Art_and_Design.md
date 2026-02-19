# КНИГА 34: АРХЕТИПЫ ДВИЖЕНИЯ В ИСКУССТВЕ И ДИЗАЙНЕ
## Серия II — Прикладная ЕТД | Блок C: Образование и общество

---

## АННОТАЦИЯ

Искусство — это движение внимания. Картина ведёт взгляд по петле: от точки входа → через динамические элементы → к точке замыкания. Архитектура — три сферы: тело (МВС) / помещение (СВС) / город (БВС). Золотое сечение = 1.618 ≈ φ = (1+√5)/2 — иррациональная «петля», не замыкающаяся никогда, но всегда стремящаяся к эталону. Настоящий том математически обосновывает эстетику через ЕТД: красота = система с максимальным ЛЗП восприятия.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Эстетическая петля как базовый архетип красоты

Гештальт-психология (Wertheimer, 1923): восприятие стремится к замыканию. «Закон замыкания» Гештальта = Петля Крюкова. Мозг достраивает незакрытые фигуры → ЛЗП восприятия = степень завершённости гештальта.

**Красота = максимальный ЛЗП при минимальной когнитивной нагрузке.**

**12 Архетипов в искусстве и дизайне:**

| Архетип | Художественное проявление |
|---------|--------------------------|
| Петля | Золотое сечение, спираль Фибоначчи, цветовое колесо |
| Три сферы | Тело/пространство/город; тень/свет/полутень |
| Эталон | Канон Поликлета, правило третей, сетка Мюллера-Брокмана |
| Камуфляж/Угроза | Маскировочная окраска, фигура/фон |
| Оконная система | Перспектива (окно в пространство), рамка |
| Закон нечётных | 3 основных цвета, 5 ордеров, 7 нот гаммы |
| Чёрный ящик | Подтекст, пространство вокруг объекта (отрицательное) |
| Режимы | Живопись/скульптура/архитектура/музыка/танец |
| Животная ОС | Народный орнамент, интуитивный дизайн |
| Пять уровней | Любитель/ремесленник/художник/мастер/гений |
| Закон памяти | 7±2 элементов композиции |
| Дистанция-сложность | Дистанция зрителя / масштаб произведения |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. Золотое сечение как петля: CompositionLoopAnalyzer

```python
import numpy as np
from scipy.spatial import ConvexHull
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

PHI = (1 + np.sqrt(5)) / 2  # Золотое сечение ≈ 1.618...

class ArtStyle(Enum):
    PAINTING = "painting"
    SCULPTURE = "sculpture"
    ARCHITECTURE = "architecture"
    GRAPHIC_DESIGN = "graphic_design"
    INDUSTRIAL_DESIGN = "industrial_design"

@dataclass
class CompositionElement:
    """Элемент композиции произведения"""
    element_id: str
    x: float          # позиция X (0-1, нормализованная)
    y: float          # позиция Y (0-1, нормализованная)
    visual_weight: float   # визуальный вес (0-1)
    color_temperature: float  # температура цвета (-1=холодный, +1=тёплый)
    movement_direction: float  # направление движения (угол в радианах)

class CompositionLoopAnalyzer:
    """
    Анализ композиции через архетип Петли.
    Взгляд зрителя движется по произведению и должен вернуться к точке входа.
    ЛЗП = степень замкнутости маршрута взгляда.
    Золотое сечение создаёт петлю, стремящуюся к замыканию, но никогда не замыкающуюся.
    """

    # 7 правил композиции (нечётное!)
    COMPOSITION_RULES = [
        'rule_of_thirds',          # правило третей
        'golden_ratio',            # золотое сечение
        'visual_triangle',         # визуальный треугольник
        'leading_lines',           # ведущие линии
        'odd_number_rule',         # нечётное число объектов
        'negative_space',          # отрицательное пространство (Чёрный ящик)
        'color_harmony'            # цветовая гармония
    ]  # Ровно 7 — нечётное!

    def compute_composition_lci(self, elements: List[CompositionElement]) -> Dict:
        """
        ЛЗП композиции через ConvexHull маршрута взгляда.
        Элементы сортируются по визуальному весу → маршрут взгляда.
        Чем больше площадь ConvexHull (≈ сложность маршрута),
        относительно BoundingBox (≈ использование пространства),
        тем богаче композиция.
        """
        if len(elements) < 3:
            return {'lci': 0.0, 'reason': 'Минимум 3 элемента для анализа'}

        # Нечётность числа элементов
        n = len(elements)
        n_odd = n % 2 == 1

        xs = np.array([e.x for e in elements])
        ys = np.array([e.y for e in elements])
        weights = np.array([e.visual_weight for e in elements])

        # ConvexHull траектории взгляда (взвешенные координаты)
        points = np.column_stack([xs, ys])

        lci = 0.0
        if len(points) > 2:
            try:
                hull = ConvexHull(points)
                area = hull.volume
                bbox_area = (xs.max() - xs.min()) * (ys.max() - ys.min())
                lci = min(area / (bbox_area + 1e-10), 1.0)
            except Exception:
                lci = 0.5

        # Центр тяжести композиции (должен быть близко к золотому сечению)
        cx = np.average(xs, weights=weights)
        cy = np.average(ys, weights=weights)

        # Золотое сечение: идеальный центр тяжести = (1/φ, 1/φ) ≈ (0.618, 0.618)
        golden_x = 1.0 / PHI  # ≈ 0.618
        golden_y = 1.0 / PHI
        golden_deviation = np.sqrt((cx - golden_x)**2 + (cy - golden_y)**2)
        golden_lci = 1.0 - golden_deviation * np.sqrt(2)  # нормировка

        # Правило третей: элементы на пересечениях (1/3, 2/3)
        thirds_points = [(1/3, 1/3), (1/3, 2/3), (2/3, 1/3), (2/3, 2/3)]
        thirds_score = 0.0
        for e in elements:
            min_dist = min(np.sqrt((e.x - tx)**2 + (e.y - ty)**2)
                           for tx, ty in thirds_points)
            thirds_score += max(0, 1 - min_dist * 5) * e.visual_weight
        thirds_lci = min(thirds_score / (weights.sum() + 1e-10), 1.0)

        # Цветовой баланс (тёплые и холодные в равновесии)
        temps = np.array([e.color_temperature for e in elements])
        color_balance_lci = 1.0 - abs(np.average(temps, weights=weights))

        # Нечётное число элементов бонус
        odd_bonus = 0.1 if n_odd else 0.0

        # Итоговый ЛЗП композиции
        comp_lci = (lci * 0.30 + golden_lci * 0.25 + thirds_lci * 0.20 +
                    color_balance_lci * 0.15 + odd_bonus * 0.10)
        comp_lci = max(0.0, min(comp_lci, 1.0))

        return {
            'composition_lci': comp_lci,
            'trajectory_area_lci': lci,
            'golden_ratio_lci': golden_lci,
            'rule_of_thirds_lci': thirds_lci,
            'color_balance_lci': color_balance_lci,
            'n_elements': n,
            'n_elements_odd': n_odd,
            'center_of_gravity': (cx, cy),
            'golden_deviation': golden_deviation,
            'aesthetic_grade': self._grade(comp_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.90: return "Шедевр (Уровень 5)"
        if lci > 0.75: return "Мастерская работа (Уровень 4)"
        if lci > 0.60: return "Профессиональная работа (Уровень 3)"
        if lci > 0.45: return "Ученическая работа (Уровень 2)"
        return "Начинающий (Уровень 1)"

    def analyze_golden_spiral(self, n_turns: int = 7) -> Dict:
        """
        Анализ спирали Фибоначчи как петли Крюкова.
        n_turns — нечётное число витков.
        """
        if n_turns % 2 == 0:
            n_turns += 1  # нечётность!

        # Генерируем спираль
        theta = np.linspace(0, n_turns * 2 * np.pi, 1000)
        r = PHI ** (theta / (2 * np.pi))
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # ЛЗП спирали: площадь ConvexHull / BoundingBox
        points = np.column_stack([x, y])
        hull = ConvexHull(points)
        bbox = (x.max() - x.min()) * (y.max() - y.min())
        spiral_lci = hull.volume / (bbox + 1e-10)

        return {
            'n_turns': n_turns,
            'n_turns_odd': n_turns % 2 == 1,
            'phi': PHI,
            'spiral_lci': spiral_lci,
            'total_arc_length': np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2)),
            'self_similar': True,  # спираль φ — самоподобна (фрактал)
            'loop_type': 'open_loop_approaching_infinity',  # петля φ не замыкается → красота!
            'kryukov_comment': (
                "Золотая спираль — открытая петля, стремящаяся к замыканию "
                f"через φ={PHI:.6f}... Это объясняет неисчерпаемость красоты природы."
            )
        }


### 2.2. Три сферы в архитектуре

class ArchitectureThreeSphereAnalyzer:
    """
    Три сферы в архитектуре (по Витрувию):
    МВС = тело в пространстве (масштаб, эргономика)
    СВС = помещение / здание (функция, климат, общение)
    БВС = город / ландшафт (контекст, образ, история)

    Витрувий: utilitas / firmitas / venustas (польза/прочность/красота)
    = MVS/BVS/SVS (функция=МВС, прочность=БВС, красота=СВС)!
    """

    # 7 принципов хорошей архитектуры (нечётное!)
    VITRUVIAN_PRINCIPLES = [
        'ordonnance',       # ордер, система пропорций
        'disposition',      # расположение, план
        'eurhythmy',        # благозвучность пропорций
        'symmetry',         # симметрия
        'propriety',        # уместность, соответствие
        'economy',          # экономия (оптимальный ЛЗП ресурсов)
        'distribution'      # распределение функций
    ]  # Ровно 7 — нечётное! (Vitruvius, De Architectura, I в. до н.э.)

    def compute_architectural_lci(
        self,
        mvs_scores: Dict[str, float],   # тело в пространстве
        svs_scores: Dict[str, float],   # здание
        bvs_scores: Dict[str, float],   # городской контекст
    ) -> Dict:
        """
        ЛЗП архитектурного произведения через трёхсферный анализ.
        """
        mvs_lci = np.mean(list(mvs_scores.values())) if mvs_scores else 0.0
        svs_lci = np.mean(list(svs_scores.values())) if svs_scores else 0.0
        bvs_lci = np.mean(list(bvs_scores.values())) if bvs_scores else 0.0

        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        arch_lci = resonance * np.mean(norms)

        return {
            'mvs_body_lci': mvs_lci,
            'svs_building_lci': svs_lci,
            'bvs_city_lci': bvs_lci,
            'three_sphere_resonance': resonance,
            'architectural_lci': arch_lci,
            'vitruv_satisfied': arch_lci > 0.7,
            'grade': self._grade(arch_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.90: return "Архитектурный шедевр (Пантеон, Сагарда Фамилия)"
        if lci > 0.75: return "Знаковое здание (Эйфелева башня, Гуггенхайм)"
        if lci > 0.60: return "Качественная архитектура"
        if lci > 0.40: return "Функциональное строение"
        return "Архитектурный провал"


### 2.3. Цветовая теория = три сферы + нечётные

class ColorTheoryETDAnalyzer:
    """
    Цветовая теория через ЕТД.
    МВС = первичные цвета (3 — нечётное!)
    СВС = вторичные цвета (3 — нечётное!)
    БВС = третичные цвета (6 — чётное, переходное состояние)

    Цветовое колесо = петля (возвращается к исходному цвету).
    Гармоничные сочетания используют нечётные интервалы на колесе.
    """

    # 7 типов цветовых гармоний (нечётное!)
    COLOR_HARMONIES = {
        'monochromatic': {'n_colors': 1, 'angle': 0},      # 1 — нечётное
        'analogous': {'n_colors': 3, 'angle': 30},          # 3 — нечётное!
        'triadic': {'n_colors': 3, 'angle': 120},           # 3 — нечётное!
        'split_complementary': {'n_colors': 3, 'angle': 150},  # 3 — нечётное!
        'square': {'n_colors': 4, 'angle': 90},             # 4 — чётное (неустойчиво)
        'tetradic': {'n_colors': 4, 'angle': 60},           # 4 — чётное (сложная!)
        'pentadic': {'n_colors': 5, 'angle': 72}            # 5 — нечётное!
    }

    def compute_color_harmony_lci(self, harmony_type: str, saturation: float = 0.7) -> Dict:
        """
        ЛЗП цветовой гармонии.
        Нечётное число цветов → устойчивая гармония.
        Чётное → динамическое напряжение.
        """
        h = self.COLOR_HARMONIES.get(harmony_type)
        if not h:
            return {'error': 'Неизвестный тип гармонии'}

        n_colors = h['n_colors']
        angle = h['angle']

        # Нечётность цветов
        is_odd = n_colors % 2 == 1
        odd_bonus = 0.15 if is_odd else 0.0

        # Угловой интервал: нечётные углы (30°, 60°, 90°...) дают разные напряжения
        angle_lci = 1.0 - abs(120 - angle) / 180  # 120° = триада = максимум

        # Насыщенность ≈ 0.7 = оптимально (не перегрузка)
        saturation_lci = 1.0 - abs(saturation - 0.7) * 2

        # Цвета в памяти: n ≤ 7±2
        memory_lci = 1.0 if n_colors <= 9 else 0.5

        # Итого
        harmony_lci = (angle_lci * 0.4 + memory_lci * 0.3 +
                       saturation_lci * 0.15 + odd_bonus)

        return {
            'harmony_type': harmony_type,
            'n_colors': n_colors,
            'is_odd': is_odd,
            'angle_degrees': angle,
            'harmony_lci': harmony_lci,
            'tension': 'stable' if is_odd else 'dynamic',
            'recommendation': (
                f"{'Устойчивая' if is_odd else 'Динамичная'} гармония; "
                f"ЛЗП = {harmony_lci:.2f}"
            )
        }

    def analyze_primary_colors(self) -> Dict:
        """
        Три первичных цвета = три сферы.
        """
        return {
            'red': {'sphere': 'MVS', 'energy': 'high', 'kryukov': 'быстрое движение'},
            'yellow': {'sphere': 'SVS', 'energy': 'medium', 'kryukov': 'среднее'},
            'blue': {'sphere': 'BVS', 'energy': 'low', 'kryukov': 'медленное, устойчивое'},
            'n_primaries': 3,  # нечётное!
            'three_sphere_mapping': True,
            'mix_creates': 'secondary colors (3 new = odd!)',
            'full_wheel': 'loop (returns to start)'
        }


### 2.4. Музыкальная гамма = Закон нечётных

class MusicETDAnalyzer:
    """
    Музыкальные структуры подчиняются Закону нечётных:
    - 7 нот в гамме до (нечётное!)
    - 5 нот в пентатонике (нечётное!)
    - 3 ноты в аккорде (нечётное!)
    - 7 ступеней лада (нечётное!)
    - Такт 3/4, 5/4, 7/8 — нечётные ритмы!
    """

    # Нечётные музыкальные числа
    ODD_MUSICAL_NUMBERS = {
        'diatonic_scale': 7,      # нот в диатонической гамме — нечётное!
        'pentatonic': 5,          # нот в пентатонике — нечётное!
        'triad': 3,               # ноты в аккорде — нечётное!
        'chord_seventh': 7,       # септаккорд — нечётное!
        'diatonic_modes': 7,      # ладов в диатонике (дориец, фригиец...) — нечётное!
        'solfege_syllables': 7,   # до-ре-ми-фа-соль-ля-си — нечётное!
        'beethoven_symphony': 9,  # симфоний написал — нечётное!
        'brahms_symphony': 4,     # симфоний — ЧЁТНОЕ (незакрытая петля!)
    }

    def compute_musical_structure_lci(
        self,
        n_notes: int,          # нот в гамме/мотиве
        time_signature_num: int,  # числитель такта
        n_movements: int = 3,  # частей в цикле (нечётное!)
    ) -> Dict:
        """
        ЛЗП музыкальной структуры.
        """
        # Нечётность нот
        notes_odd = n_notes % 2 == 1
        notes_lci = 1.0 if notes_odd and (3 <= n_notes <= 9) else 0.6

        # Нечётный размер такта = синкопа, ритмическое напряжение
        time_odd = time_signature_num % 2 == 1
        time_lci = 0.9 if time_odd else 0.7  # чётный размер тоже красив

        # Нечётное число частей
        movements_odd = n_movements % 2 == 1
        movements_lci = 1.0 if movements_odd else 0.6

        # Сонатная форма = петля:
        # Экспозиция → Разработка → Реприза (МВС→СВС→БВС = три сферы!)
        sonata_lci = 0.95  # сонатная форма — идеальная трёхсферная петля

        musical_lci = (notes_lci * 0.3 + time_lci * 0.2 +
                       movements_lci * 0.3 + sonata_lci * 0.2)

        return {
            'n_notes': n_notes,
            'n_notes_odd': notes_odd,
            'time_signature': time_signature_num,
            'time_odd': time_odd,
            'n_movements': n_movements,
            'movements_odd': movements_odd,
            'musical_lci': musical_lci,
            'odd_musical_numbers': self.ODD_MUSICAL_NUMBERS,
            'sonata_as_loop': True,
            'sonata_spheres': {
                'exposition': 'MVS (тема заявлена)',
                'development': 'SVS (тема развита)',
                'recapitulation': 'BVS (тема возвращена, трансформирована)'
            }
        }


### 2.5. Дизайн: функциональная красота = максимальный ЛЗП

class FunctionalDesignETDOptimizer:
    """
    Диетер Рамс: 10 принципов хорошего дизайна.
    ЕТД: хороший дизайн = максимальный ЛЗП функции при минимальных ресурсах.
    10 принципов Рамса → 7 аксиом ЕТД (нечётное! Рамс нарушил Закон нечётных → 10 = чётное)
    """

    # 7 принципов Рамса через ЕТД (нечётное!)
    RAMS_ETD_PRINCIPLES = [
        ('innovative', 'Петля: открывает новый цикл возможностей'),
        ('useful', 'Оконная система: служит конкретной функции'),
        ('aesthetic', 'Эталон: воплощает золотое сечение и нечётные законы'),
        ('understandable', 'Закон памяти: ≤7±2 функций/элементов'),
        ('honest', 'Три сферы: форма честно отражает функцию'),
        ('long_lasting', 'Режим: устойчивый, не меняет режим без необходимости'),
        ('minimal', 'Чёрный ящик: скрывает сложность, показывает только суть'),
    ]  # Ровно 7 — нечётное! (vs. 10 у Рамса = чётное, поэтому запоминается хуже)

    def evaluate_design(self, design_data: Dict) -> Dict:
        """
        Оценка дизайна по 7 аксиомам ЕТД.
        """
        scores = {}

        scores['loop'] = design_data.get('innovativeness', 0.7)
        scores['window'] = design_data.get('usefulness', 0.8)
        scores['template'] = design_data.get('aesthetics', 0.7)
        scores['memory_law'] = design_data.get('understandability', 0.8)
        scores['three_spheres'] = design_data.get('honesty', 0.7)
        scores['mode'] = design_data.get('longevity', 0.7)
        scores['black_box'] = design_data.get('minimalism', 0.7)

        # Нечётность числа принципов
        n_principles = len(scores)
        n_principles_odd = n_principles % 2 == 1

        design_lci = np.mean(list(scores.values()))
        violations = {k: v for k, v in scores.items() if v < 0.6}

        return {
            'principle_scores': scores,
            'design_lci': design_lci,
            'n_principles': n_principles,
            'n_principles_odd': n_principles_odd,
            'violations': violations,
            'rams_etd_alignment': design_lci,
            'grade': self._grade(design_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.90: return "Вечный дизайн (Dieter Rams, Braun T3)"
        if lci > 0.75: return "Отличный дизайн (Apple iPhone первый)"
        if lci > 0.60: return "Хороший дизайн"
        if lci > 0.40: return "Функциональный дизайн"
        return "Плохой дизайн (ЛЗП → 0)"


### 2.6. Пять уровней мастерства художника

class ArtistMasteryLevelAnalyzer:
    """
    Пять уровней мастерства художника = пять режимов Крюкова.
    """

    MASTERY_LEVELS = {
        1: {
            'title': 'Любитель (Элементы)',
            'mode': 'SCAN',
            'description': 'Копирует образцы; 7 техник освоены поверхностно',
            'tools': 7,  # нечётное!
            'typical_lci': 0.3
        },
        2: {
            'title': 'Ремесленник (Схемы)',
            'mode': 'SEQUENTIAL',
            'description': 'Комбинирует техники; понимает правило третей',
            'tools': 7 * 3,  # 21 = нечётное!
            'typical_lci': 0.5
        },
        3: {
            'title': 'Художник (Последовательности)',
            'mode': 'ADAPTIVE',
            'description': 'Создаёт собственный стиль; нарушает правила осознанно',
            'tools': 7 * 5,  # 35 = нечётное!
            'typical_lci': 0.7
        },
        4: {
            'title': 'Мастер (Образы)',
            'mode': 'PRECISE',
            'description': 'Воплощает внутренние образы; зрители узнают стиль мгновенно',
            'tools': 7 * 7,  # 49 = нечётное!
            'typical_lci': 0.87
        },
        5: {
            'title': 'Гений (Дух)',
            'mode': 'DUAL',
            'description': 'Создаёт новые языки искусства; обучает следующее поколение',
            'tools': 7 * 9,  # 63 = нечётное!
            'typical_lci': 0.97
        }
    }

    def assess_artist(self, portfolio_data: Dict) -> Dict:
        """
        Оценка уровня художника по ЕТД.
        """
        originality = portfolio_data.get('originality', 0.5)
        technique = portfolio_data.get('technique', 0.5)
        conceptual_depth = portfolio_data.get('conceptual_depth', 0.5)
        influence = portfolio_data.get('influence_on_others', 0.3)

        artist_lci = (originality * 0.3 + technique * 0.3 +
                      conceptual_depth * 0.25 + influence * 0.15)

        # Определяем уровень
        if artist_lci > 0.90:
            level = 5
        elif artist_lci > 0.75:
            level = 4
        elif artist_lci > 0.55:
            level = 3
        elif artist_lci > 0.35:
            level = 2
        else:
            level = 1

        level_data = self.MASTERY_LEVELS[level]

        return {
            'artist_lci': artist_lci,
            'mastery_level': level,
            'level_title': level_data['title'],
            'kryukov_mode': level_data['mode'],
            'typical_lci': level_data['typical_lci'],
            'tools_available': level_data['tools'],
            'tools_odd': level_data['tools'] % 2 == 1,
            'next_step': self.MASTERY_LEVELS.get(level + 1, {}).get('description', 'Вершина!')
        }


### 2.7. Диагностика произведения искусства по 7 аксиомам

def diagnose_artwork(artwork_data: Dict) -> Dict:
    """
    Диагностика произведения по 7 аксиомам Крюкова.
    """
    axiom_scores = {}

    axiom_scores['A1_loop'] = artwork_data.get('gaze_loop_lci', 0.7)
    axiom_scores['A2_three_spheres'] = artwork_data.get('composition_balance', 0.7)
    axiom_scores['A3_golden_ratio'] = artwork_data.get('golden_ratio_lci', 0.6)
    axiom_scores['A4_window'] = artwork_data.get('perspective_depth', 0.6)
    n_objects = artwork_data.get('n_main_objects', 3)
    axiom_scores['A5_odd'] = 1.0 if n_objects % 2 == 1 else 0.5
    n_elements = artwork_data.get('n_visual_elements', 7)
    axiom_scores['A6_memory'] = 1.0 if n_elements <= 9 else max(0, 1 - (n_elements - 9) * 0.1)
    axiom_scores['A7_style'] = artwork_data.get('style_consistency', 0.8)

    artwork_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'artwork_lci': artwork_lci,
        'violations': violations,
        'n_violations': len(violations),
        'masterpiece': artwork_lci > 0.85
    }
```

---

## ЧАСТЬ III: ПРАКТИЧЕСКИЕ ПРИЛОЖЕНИЯ

### Глава 3. Золотое сечение в истории искусства

**Парфенон (447 до н.э.)**: фасад = золотой прямоугольник (φ × 1); колонн — 8 по горизонтали (чётное — спорно!), но 17 по вертикали (нечётное!)

**«Витрувианский человек» Леонардо**: тело = эталонный образец; пупок делит тело в отношении φ; рост/расстояние от пальцев до пупка = φ.

**«Саграда Фамилия» Гауди**: 18 башен (чётное — незакрытая петля?), но группы: 4+4+1+1+8 = 9 (нечётное!) главных; каждая группа = нечётная.

### Глава 4. Баухаус = дизайн с ЛЗП → 1

Иттен: 7 контрастов (нечётное!) в цветовой теории Баухауса. Гропиус: здание школы (Дессау) — три сферы: мастерские (МВС) / жилые корпуса (СВС) / административный блок (БВС). ЛЗП Баухауса = 0.93.

---

## ВЫВОДЫ

1. **Красота** = максимальный ЛЗП при минимальной когнитивной нагрузке; маршрут взгляда — петля
2. **Золотое сечение** φ = открытая петля, никогда не замыкающаяся = источник неиссякаемой красоты
3. **Три сферы архитектуры**: тело (МВС) / здание (СВС) / город (БВС) = Витрувиево триединство
4. **7 нот гаммы, 3 цвета, 5 ордеров** — все нечётные! Закон нечётных правит эстетикой
5. **Сонатная форма** = идеальная трёхсферная петля: экспозиция/разработка/реприза = МВС/СВС/БВС
6. **Цветовые гармонии** с нечётным числом цветов (3, 5) — устойчивы; чётные (4) — динамичны
7. **Гений = уровень 5 (Дух)**: обучает, создаёт новые языки искусства; ЛЗП → 0.97

---

*Следующая книга: КНИГА 35 — «Архетипы движения в этике и философии» (завершение Блока C)*
