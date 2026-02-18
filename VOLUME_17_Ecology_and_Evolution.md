# КНИГА 17: ЭКОЛОГИЯ И ЭВОЛЮЦИЯ
## «Архетипы движения в живых системах, экосистемах и эволюционных процессах»

### Серия «Архетипы Движения», Книга 17 из 20
### Основано на «Тотальной Системе Боя» В.В. Крюкова

---

## ПРЕДИСЛОВИЕ

Жизнь — это движение, которое само себя поддерживает.

Мышца сокращается в петле. Популяция осциллирует в цикле хищник-жертва. Экосистема пульсирует в петле биогеохимических циклов. Эволюция движется по петле отбора: вариация → отбор → наследование → вариация.

Архетипы Крюкова обнаруживаются на каждом уровне живых систем — не как метафора, а как буквальная кинематика жизни.

---

## ЧАСТЬ I. ЭКОЛОГИЯ КАК КИНЕМАТИКА

### Глава 1. Трофические Циклы как Петли

#### 1.1 Биогеохимические циклы = петли

```
КРУГОВОРОТЫ ВЕЩЕСТВ = ПЕТЛИ КРЮКОВА:

Цикл углерода:
  CO₂ → (фотосинтез) → органика → (дыхание/горение) → CO₂
  Это замкнутая петля! LCI = 1.0 в идеальной экосистеме

  «Разрыв петли» = накопление CO₂ (парниковый эффект):
  Нарушение замкнутости: сжигание ископаемого углерода
  → петля стала однонаправленной → планетарный дисбаланс

Цикл воды (гидрологический):
  Испарение → конденсация → осадки → сток → испарение
  LCI = 1.0 при равновесии
  «Разрыв петли»: обезлесивание → сток растёт → испарение падает
  → Петля разомкнута → опустынивание

Цикл азота:
  N₂ → (фиксация) → NH₃ → нитраты → (денитрификация) → N₂
  Пятичастная петля (нечётно! 5 этапов = нечётная структура)

Цикл фосфора:
  Горные породы → почва → живые организмы → отложения → горные породы
  Длинная петля (миллионы лет): БВС-уровень цикла
```

#### 1.2 Трёхуровневая иерархия сфер в экосистеме

```
ТРИ СФЕРЫ ЭКОСИСТЕМЫ:

МВС (организменный уровень):
  Элемент: особь (Individual)
  Временной горизонт: часы-дни (жизненный цикл)
  Движение: поведение, форма, метаболизм
  LCI организма: цикличность поведения (сон/бодрствование, питание)

СВС (популяционный уровень):
  Элемент: популяция (Population)
  Временной горизонт: годы-десятилетия (популяционная динамика)
  Движение: рост/спад численности, половой отбор, структура
  LCI популяции: цикл хищник-жертва (осциллирует!)

БВС (экосистемный уровень):
  Элемент: сообщество + абиотическая среда
  Временной горизонт: столетия-тысячелетия (сукцессия, климат)
  Движение: сукцессионные смены, климатические циклы, биомы
  LCI экосистемы: климатические циклы Миланковича (41 тыс. лет)
```

#### 1.3 Модель хищник-жертва как резонанс

```python
import numpy as np
from scipy.integrate import odeint

class LotkVolterraResonanceAnalyzer:
    """
    Анализ модели хищник-жертва (Лотка-Вольтерра) через архетипы Крюкова.

    Уравнения:
      dx/dt = αx - βxy   (жертвы: рождение - поедание)
      dy/dt = δxy - γy   (хищники: поедание - гибель)

    Петля: популяции осциллируют в замкнутом цикле (LCI ≈ 1.0)
    Резонанс: частоты осцилляций жертв и хищников совпадают
    """

    def __init__(self, alpha=1.0, beta=0.1, delta=0.075, gamma=1.5):
        """
        alpha: скорость роста жертв
        beta:  скорость выедания
        delta: эффективность конверсии пищи в потомство
        gamma: скорость гибели хищников
        """
        self.alpha = alpha
        self.beta = beta
        self.delta = delta
        self.gamma = gamma

        # Равновесие: x* = γ/δ, y* = α/β
        self.equilibrium_x = gamma / delta
        self.equilibrium_y = alpha / beta

    def simulate(self, x0: float, y0: float,
                 t_max: float = 100, n_points: int = 10000) -> dict:
        """
        Симулировать динамику хищник-жертва.
        Возвращает траекторию и метрики архетипов.
        """
        def lotka_volterra(state, t):
            x, y = state
            dxdt = self.alpha * x - self.beta * x * y
            dydt = self.delta * x * y - self.gamma * y
            return [dxdt, dydt]

        t = np.linspace(0, t_max, n_points)
        solution = odeint(lotka_volterra, [x0, y0], t)
        x_traj = solution[:, 0]
        y_traj = solution[:, 1]

        # LCI фазового портрета (x, y):
        phase_points = np.column_stack([x_traj, y_traj])
        lci = self._compute_lci(phase_points)

        # Резонанс: совпадение периодов осцилляций
        period_x = self._estimate_period(x_traj, t)
        period_y = self._estimate_period(y_traj, t)
        if period_x > 0 and period_y > 0:
            resonance = 1.0 - abs(period_x - period_y) / max(period_x, period_y)
        else:
            resonance = 0.0

        # Закон нечётности: период кратен нечётному числу?
        period_is_odd_multiple = (round(period_x) % 2 == 1) if period_x > 0 else None

        return {
            't': t,
            'prey': x_traj,
            'predator': y_traj,
            'lci': round(lci, 4),
            'period_prey': round(period_x, 2),
            'period_predator': round(period_y, 2),
            'resonance': round(resonance, 4),
            'equilibrium': (round(self.equilibrium_x, 2),
                           round(self.equilibrium_y, 2)),
            'period_is_odd': period_is_odd_multiple,
            'interpretation': self._interpret(lci, resonance)
        }

    def _compute_lci(self, points: np.ndarray) -> float:
        """LCI фазовой траектории."""
        try:
            from scipy.spatial import ConvexHull
            hull = ConvexHull(points)
            hull_area = hull.volume
        except Exception:
            return 0.5

        x_range = points[:, 0].max() - points[:, 0].min()
        y_range = points[:, 1].max() - points[:, 1].min()
        bbox_area = x_range * y_range
        return min(1.0, hull_area / bbox_area) if bbox_area > 0 else 0.0

    def _estimate_period(self, signal: np.ndarray,
                         t: np.ndarray) -> float:
        """Оценить период осцилляции через FFT."""
        fft_vals = np.abs(np.fft.rfft(signal - signal.mean()))
        freqs = np.fft.rfftfreq(len(signal), d=t[1]-t[0])
        if len(freqs) < 2:
            return 0.0
        dominant_freq_idx = np.argmax(fft_vals[1:]) + 1
        dominant_freq = freqs[dominant_freq_idx]
        return 1.0 / dominant_freq if dominant_freq > 0 else 0.0

    def _interpret(self, lci: float, resonance: float) -> str:
        parts = []
        if lci > 0.85:
            parts.append('УСТОЙЧИВЫЙ ЦИКЛ: популяции движутся по замкнутой петле')
        elif lci < 0.3:
            parts.append('КОЛЛАПС: петля разомкнута (вымирание или взрыв численности)')

        if resonance > 0.9:
            parts.append('РЕЗОНАНС: жертвы и хищники осциллируют синхронно')
        elif resonance < 0.5:
            parts.append('АНТИРЕЗОНАНС: несинхронные колебания → нестабильность')

        return '; '.join(parts) if parts else 'Переходный режим'

    def analyze_three_sphere_ecosystem(self,
                                        mvs_pop: np.ndarray,
                                        svs_pop: np.ndarray,
                                        bvs_pop: np.ndarray) -> dict:
        """
        Анализ трёхуровневой трофической цепи:
        МВС (фитопланктон) → СВС (зоопланктон) → БВС (рыба)
        """
        # LCI каждого уровня
        lci_mvs = self._estimate_period(mvs_pop, np.arange(len(mvs_pop)))
        lci_svs = self._estimate_period(svs_pop, np.arange(len(svs_pop)))
        lci_bvs = self._estimate_period(bvs_pop, np.arange(len(bvs_pop)))

        # Резонанс: синхронность периодов трёх уровней
        periods = [p for p in [lci_mvs, lci_svs, lci_bvs] if p > 0]
        if len(periods) >= 2:
            mean_period = np.mean(periods)
            deviations = [abs(p - mean_period) / mean_period for p in periods]
            resonance = 1.0 - np.mean(deviations)
        else:
            resonance = 0.0

        return {
            'period_MVS': round(lci_mvs, 2),
            'period_SVS': round(lci_svs, 2),
            'period_BVS': round(lci_bvs, 2),
            'three_sphere_resonance': round(max(0.0, resonance), 4),
            'ecosystem_health': (
                'РЕЗОНАНС — стабильная экосистема' if resonance > 0.8
                else 'НАРУШЕНИЕ — нестабильная трофическая цепь'
            )
        }
```

---

### Глава 2. Эволюция как Большая Петля

#### 2.1 Эволюционный цикл

```
ЭВОЛЮЦИЯ КАК ПЕТЛЯ КРЮКОВА:

Одна итерация эволюции:
  Вариация (мутация/рекомбинация)
     ↓
  Отбор (выживание и размножение)
     ↓
  Наследование (передача потомкам)
     ↓
  [возврат к Вариации]

Это замкнутая петля! LCI эволюции = 1.0 (популяция «возвращается»
к состоянию с вариацией, но изменённому — как герой романа в точке A')

Параметры эволюционной петли:
  Амплитуда = скорость эволюционных изменений (зависит от мутационного груза)
  Частота = скорость смены поколений
  LCI = стабильность популяции (непрерывность линии)
  Разрыв петли = вымирание (популяция не «возвращается»)

Три уровня эволюции (три сферы):
  МВС: изменения отдельных генов (мутации)
  СВС: изменения популяций (видообразование, дрейф генов)
  БВС: изменения биоты (макроэволюция, вымирания, радиации)

Резонанс эволюции:
  Когда скорости изменений на трёх уровнях синхронны →
  «Эволюционный взрыв» (кембрийский взрыв, адаптивная радиация)
  Когда антирезонанс → эволюционный тупик (живые ископаемые)
```

#### 2.2 Закон нечётности в эволюции

```
НЕЧЁТНОСТЬ В ЭВОЛЮЦИОННЫХ СТРУКТУРАХ:

Число конечностей:
  Насекомые: 6 (= 2×3, нечётное основание) ✓
  Паукообразные: 8 (= 2×4, чётное) — стабильная ниша
  Позвоночные: 4 (= 2×2, чётное) — но 3 основных «вида» конечностей (нечётно!)

Число хромосом (гаплоидный набор n):
  Дрозофила: n=4 (чётное)
  Человек: n=23 (нечётное!) ✓
  Картофель: n=12 (чётное)
  Пшеница: n=21 (нечётное!) ✓
  Гиацинт: n=8 (чётное)

Наблюдение: у «успешных» видов с максимальным биологическим
разнообразием (человек, цветковые растения) n — нечётное!
Гипотеза: нечётный n создаёт «несимметричную» рекомбинацию →
более высокое генетическое разнообразие → быстрая адаптация

Число лепестков цветков:
  Большинство: 3, 5, 8, 13 лепестков (числа Фибоначчи = нечётные!)
  Крестоцветные: 4 лепестка (чётно — стабильная но «простая» стратегия)
  Первоцвет: 5 лепестков ✓ (нечётно)
  Дельфиниум: 5 или 7 ✓

Вывод: нечётные структуры в природе связаны с оптимальными
компромиссами между стабильностью и адаптивностью.
```

---

### Глава 3. Биоразнообразие как Резонанс Ниш

#### 3.1 Экологические ниши = Звери Крюкова

```
ЭКОЛОГИЧЕСКИЕ СТРАТЕГИИ И АРХЕТИПЫ ЗВЕРЕЙ:

r-стратеги (Мышь/Заяц = Тигр-стратегия в экологии):
  Быстрое размножение, много потомков, малая забота
  «Атака» пространства: захватить ресурсы быстро
  Аналог: Тигр-организация (Amazon, агрессивный рост)

K-стратеги (Слон/Кит = Журавль-стратегия):
  Медленное размножение, мало потомков, высокая забота
  «Точность» в ресурсах: один идеальный потомок
  Аналог: Журавль-организация (NASA, Rolex)

Оппортунисты (Ворона/Лиса = Змея-стратегия):
  Адаптивность, широкая ниша, обход любых ограничений
  «Гибкость» к ресурсам: что найдём, то и съедим
  Аналог: Змея-организация (Netflix, стартапы)

Специалисты (Коала/Панда = Богомол-стратегия):
  Глубокая специализация, узкая ниша, «один ресурс»
  «Точечный удар»: один источник пищи, максимальная эффективность
  Аналог: Богомол-организация (hedge fund, нишевый производитель)

Цикл экологического доминирования:
  r-стратеги заполняют пространство быстро (Тигр)
  → Ресурсы исчерпываются → K-стратеги выживают качеством (Журавль)
  → Стабильность → Оппортунисты используют новые ниши (Змея)
  → Циклический баланс (Закон Сильного Справа!)
```

#### 3.2 Биоразнообразие = Резонанс Ниш

```python
class BiodiversityResonanceAnalyzer:
    """
    Анализ биоразнообразия как резонанса экологических ниш.
    """

    def __init__(self, species_data: dict):
        """
        species_data: {species_name: {'abundance': n, 'niche': [traits], 'strategy': str}}
        """
        self.species = species_data
        self.n_species = len(species_data)

    def compute_ecosystem_lci(self) -> float:
        """
        LCI экосистемы: насколько «замкнуты» трофические потоки.

        Высокий LCI: циклическая трофическая сеть (высокая устойчивость)
        Низкий LCI: линейные трофические цепи (уязвимость)
        """
        # Построить трофическую матрицу
        # (упрощённо: кто кого ест)
        n = self.n_species
        species_list = list(self.species.keys())

        # Заглушка: в реальном приложении заполняется из базы данных
        # Используем случайную матрицу для демонстрации
        np.random.seed(42)
        trophic_matrix = np.random.random((n, n)) > 0.7
        np.fill_diagonal(trophic_matrix, 0)  # Никто не ест себя

        # LCI = доля «замкнутых» трофических связей
        # (обратные связи в трофической сети)
        cycles = 0
        total_links = trophic_matrix.sum()

        for i in range(n):
            for j in range(n):
                if trophic_matrix[i, j] and trophic_matrix[j, i]:
                    cycles += 1

        lci = cycles / (total_links + 1e-10)
        return min(1.0, lci * 2)  # Нормализация

    def compute_niche_resonance(self) -> dict:
        """
        Резонанс ниш: насколько экологические стратегии сбалансированы.
        Три сферы:
          МВС = специалисты (узкие ниши)
          СВС = генералисты (средние ниши)
          БВС = оппортунисты (широкие ниши)
        """
        strategy_counts = {'r': 0, 'K': 0, 'opportunist': 0, 'specialist': 0}

        for sp_data in self.species.values():
            strategy = sp_data.get('strategy', 'r')
            if strategy in strategy_counts:
                strategy_counts[strategy] += 1

        total = sum(strategy_counts.values()) or 1

        # Три сферы: МВС = специалисты, СВС = K-стратеги, БВС = r + оппортунисты
        mvs_fraction = strategy_counts['specialist'] / total
        svs_fraction = strategy_counts['K'] / total
        bvs_fraction = (strategy_counts['r'] +
                        strategy_counts['opportunist']) / total

        # Резонанс: идеал = 1/3 каждой сферы (нечётное равновесие)
        ideal = 1.0 / 3.0
        deviation = (abs(mvs_fraction - ideal) +
                     abs(svs_fraction - ideal) +
                     abs(bvs_fraction - ideal))
        resonance = max(0.0, 1.0 - deviation)

        # Shannon Index (стандартная мера биоразнообразия)
        abundances = [sp['abundance'] for sp in self.species.values()
                      if 'abundance' in sp]
        if abundances:
            total_abundance = sum(abundances)
            shannon = -sum(
                (a/total_abundance) * np.log(a/total_abundance + 1e-10)
                for a in abundances)
        else:
            shannon = 0.0

        return {
            'n_species': self.n_species,
            'strategy_distribution': strategy_counts,
            'mvs_fraction': round(mvs_fraction, 3),
            'svs_fraction': round(svs_fraction, 3),
            'bvs_fraction': round(bvs_fraction, 3),
            'niche_resonance': round(resonance, 4),
            'shannon_diversity': round(shannon, 4),
            'ecosystem_lci': round(self.compute_ecosystem_lci(), 4),
            'health_assessment': self._assess_health(resonance, shannon)
        }

    def _assess_health(self, resonance: float, shannon: float) -> str:
        if resonance > 0.75 and shannon > 2.0:
            return 'ЗДОРОВАЯ ЭКОСИСТЕМА: резонанс ниш + высокое разнообразие'
        elif resonance > 0.5:
            return 'УМЕРЕННОЕ ЗДОРОВЬЕ: баланс ниш нарушен частично'
        elif shannon < 1.0:
            return 'КРИЗИС: монокультура или коллапс → низкое разнообразие'
        else:
            return 'НАРУШЕНИЕ БАЛАНСА: несинхронные стратегии → нестабильность'

    def simulate_extinction(self, species_to_remove: str) -> dict:
        """
        Симулировать вымирание вида и оценить изменение резонанса.
        """
        original_resonance = self.compute_niche_resonance()

        # Удалить вид
        modified_species = {k: v for k, v in self.species.items()
                           if k != species_to_remove}
        modified_analyzer = BiodiversityResonanceAnalyzer(modified_species)
        new_resonance = modified_analyzer.compute_niche_resonance()

        resonance_change = (new_resonance['niche_resonance'] -
                           original_resonance['niche_resonance'])

        return {
            'removed_species': species_to_remove,
            'original_resonance': original_resonance['niche_resonance'],
            'new_resonance': new_resonance['niche_resonance'],
            'resonance_change': round(resonance_change, 4),
            'impact': (
                'КРИТИЧНО: потеря ключевого вида — резонанс нарушен'
                if resonance_change < -0.1
                else 'УМЕРЕННО: потеря вида не критична для системы'
                if resonance_change < 0
                else 'ПОЗИТИВНО: инвазивный вид устранён'
            )
        }
```

---

### Глава 4. Сукцессия как Пять Уровней Экосистемы

```
ЭКОЛОГИЧЕСКАЯ СУКЦЕССИЯ = ПЯТЬ УРОВНЕЙ МАСТЕРСТВА ЭКОСИСТЕМЫ:

УРОВЕНЬ 1 — ПИОНЕРНАЯ СТАДИЯ: «Язык элементов»
  Организмы: лишайники, мхи, однолетние травы
  Стратегия: r-стратеги (быстрый захват)
  Структура: простая, малое разнообразие
  «Язык»: отдельные элементы без сложных связей
  Переход: первые двулетники создают почву → новые ниши

УРОВЕНЬ 2 — ЛУГОВАЯ СТАДИЯ: «Язык схем»
  Организмы: многолетние травы, полукустарники
  Стратегия: смесь r и K
  Структура: трофические схемы (травоядные + хищники)
  «Язык»: повторяемые функциональные схемы
  Переход: кусты создают тень → лес становится возможным

УРОВЕНЬ 3 — КУСТАРНИКОВАЯ СТАДИЯ: «Язык систем»
  Организмы: кустарники, молодые деревья
  Стратегия: смешанная
  Структура: многоуровневая, сложные взаимодействия
  «Язык»: системное мышление (кто кому нужен)
  Переход: деревья смыкают кроны → создают «климакс-экосистему»

УРОВЕНЬ 4 — МОЛОДОЙ ЛЕС: «Язык образов»
  Организмы: деревья-пионеры (берёза, осина)
  Структура: ярусность, разделение ниш
  «Язык»: архетипические паттерны (лесная экосистема)
  Переход: тенелюбивые виды заменяют светолюбивых

УРОВЕНЬ 5 — КЛИМАКС (СТАРОВОЗРАСТНОЙ ЛЕС): «Язык ценностей»
  Организмы: дубы, буки, пихты — долгожители
  Структура: максимальная сложность + устойчивость
  «Язык»: самоподдержание без внешних ресурсов (нулевое сукцессионное движение)
  LCI = максимальный: все биогеохимические циклы замкнуты
  Резонанс = максимальный: все трофические уровни синхронны
```

---

## ЧАСТЬ II. ЭВОЛЮЦИОННАЯ ДИНАМИКА

### Глава 5. Коэволюция как Межвидовой Резонанс

```
КОЭВОЛЮЦИЯ = РЕЗОНАНС ДВУХ ЭВОЛЮЦИОННЫХ ЛИНИЙ:

Примеры коэволюции:
  Цветок и опылитель:
    Форма цветка эволюционирует ↔ форма хоботка опылителя эволюционирует
    Резонанс: частота цветения ≈ активность опылителя
    Разрыв резонанса: опылитель вымирает → цветок не размножается

  Хищник и жертва:
    Скорость жертвы растёт → скорость хищника растёт
    «Гонка вооружений» = петля положительной обратной связи
    Стабилизация = достижение нового резонанса

  Паразит и хозяин:
    Вирулентность паразита ↔ иммунитет хозяина
    Нечётный закон: нечётное число «раундов» → один доминирует?
    Нет: система уходит в непрерывную осцилляцию (красная королева)

ГИПОТЕЗА КРАСНОЙ КОРОЛЕВЫ:
  «Вам нужно бежать изо всех сил, чтобы просто оставаться на месте»
  → Эволюция не «прогресс», а ПЕТЛЯ на месте (LCI = 1.0):
  Хозяин приспосабливается → Паразит приспосабливается → Хозяин...
  → Бесконечная замкнутая петля = эволюционный гомеостаз
```

### Глава 6. Экологические Катастрофы как Разрывы Петли

```python
class EcosystemStabilityAnalyzer:
    """
    Анализ устойчивости экосистемы через метрики архетипов.
    """

    def resilience_index(self, ecosystem_state: dict) -> dict:
        """
        Индекс устойчивости экосистемы.
        Основан на трёхсферном резонансе и LCI трофических петель.
        """
        # Собрать метрики
        lci_mvs = ecosystem_state.get('lci_individual_cycles', 0.8)
        lci_svs = ecosystem_state.get('lci_population_cycles', 0.7)
        lci_bvs = ecosystem_state.get('lci_ecosystem_cycles', 0.9)

        niche_resonance = ecosystem_state.get('niche_resonance', 0.6)
        biodiversity_shannon = ecosystem_state.get('shannon_index', 2.5)

        # Трёхсферный резонанс
        lcis = [lci_mvs, lci_svs, lci_bvs]
        sphere_resonance = 1.0 - np.std(lcis) / (np.mean(lcis) + 1e-10)

        # Итоговый индекс устойчивости
        resilience = (
            0.3 * np.mean(lcis) +         # Средний LCI
            0.3 * sphere_resonance +        # Резонанс сфер
            0.2 * niche_resonance +         # Резонанс ниш
            0.2 * min(1.0, biodiversity_shannon / 3.0)  # Нормализованный Shannon
        )

        # Критические пороги
        critical = False
        warnings = []

        if lci_mvs < 0.4:
            warnings.append('КРИТИЧНО: нарушены индивидуальные циклы (МВС)')
            critical = True
        if lci_svs < 0.5:
            warnings.append('КРИТИЧНО: нарушена популяционная динамика (СВС)')
            critical = True
        if lci_bvs < 0.6:
            warnings.append('КРИТИЧНО: нарушены биогеохимические циклы (БВС)')
            critical = True
        if biodiversity_shannon < 1.0:
            warnings.append('МОНОКУЛЬТУРА: потеря разнообразия')
            critical = True

        return {
            'resilience_index': round(resilience, 4),
            'sphere_resonance': round(sphere_resonance, 4),
            'niche_resonance': round(niche_resonance, 4),
            'is_critical': critical,
            'warnings': warnings,
            'status': (
                'УСТОЙЧИВАЯ ЭКОСИСТЕМА' if resilience > 0.7
                else 'УЯЗВИМАЯ ЭКОСИСТЕМА' if resilience > 0.5
                else 'ДЕГРАДИРУЮЩАЯ ЭКОСИСТЕМА'
            ),
            'conservation_priority': (
                'НЕМЕДЛЕННОЕ ВМЕШАТЕЛЬСТВО' if critical
                else 'МОНИТОРИНГ' if resilience < 0.7
                else 'НОРМАЛЬНЫЙ РЕЖИМ'
            )
        }

    def tipping_point_analysis(self,
                                time_series_lci: list,
                                window: int = 10) -> dict:
        """
        Анализ «точки опрокидывания» (tipping point) экосистемы.
        Приближение к tipping point: рост дисперсии и автокорреляции LCI.
        """
        lcis = np.array(time_series_lci)
        n = len(lcis)

        if n < window * 2:
            return {'error': 'Insufficient data'}

        variances = []
        autocorrs = []

        for i in range(window, n):
            window_data = lcis[i-window:i]
            variances.append(np.var(window_data))

            # Автокорреляция лага 1
            if len(window_data) > 1:
                ac = np.corrcoef(window_data[:-1], window_data[1:])[0, 1]
                autocorrs.append(ac if not np.isnan(ac) else 0.0)

        # Тренд дисперсии и автокорреляции
        var_trend = np.polyfit(range(len(variances)), variances, 1)[0]
        ac_trend = np.polyfit(range(len(autocorrs)), autocorrs, 1)[0]

        # Ранние предупреждающие сигналы tipping point:
        # Рост дисперсии И рост автокорреляции
        tipping_risk = 0.0
        if var_trend > 0:
            tipping_risk += 0.5
        if ac_trend > 0:
            tipping_risk += 0.5

        return {
            'variance_trend': round(var_trend, 6),
            'autocorrelation_trend': round(ac_trend, 6),
            'tipping_risk': tipping_risk,
            'current_lci': round(lcis[-1], 4),
            'lci_trend': round(np.polyfit(range(n), lcis, 1)[0], 6),
            'warning': (
                'ВЫСОКИЙ РИСК КОЛЛАПСА: оба индикатора растут'
                if tipping_risk >= 1.0
                else 'УМЕРЕННЫЙ РИСК: один индикатор растёт'
                if tipping_risk >= 0.5
                else 'НИЗКИЙ РИСК: система стабильна'
            )
        }
```

---

## ЗАКЛЮЧЕНИЕ

**Ключевые выводы Книги 17:**

1. **Биогеохимические циклы = петли Крюкова**: круговороты углерода, воды, азота — замкнутые петли с LCI ≈ 1.0. Экологический кризис = разрыв петли (накопление CO₂, опустынивание).

2. **Три сферы экосистемы**: МВС (организмы, часы-дни), СВС (популяции, годы-десятилетия), БВС (экосистемы, века-тысячелетия). Резонанс трёх сфер = устойчивость экосистемы.

3. **Лотка-Вольтерра = петля с резонансом**: популяции хищников и жертв осциллируют в замкнутом цикле. Резонанс = синхронность периодов. LCI ≈ 1.0 = устойчивая система.

4. **Экологические стратегии = звери Крюкова**: r-стратеги (Тигр), K-стратеги (Журавль), оппортунисты (Змея), специалисты (Богомол). Циклическое доминирование воспроизводит «закон сильного справа».

5. **Эволюция = большая петля**: вариация → отбор → наследование → вариация. Нечётный n хромосом у «успешных» видов (человек: n=23, пшеница: n=21).

6. **Сукцессия = пять уровней мастерства**: пионеры (Level 1) → луга → кустарники → молодой лес → климакс (Level 5). Климакс = максимальный LCI + максимальный резонанс.

7. **Коэволюция = межвидовой резонанс**: гонка вооружений хищник-жертва = петля с нарастающей амплитудой. Гипотеза Красной Королевы = петля с LCI = 1.0 (эволюционный гомеостаз).

8. **`LotkVolterraResonanceAnalyzer`**: симуляция + LCI фазового портрета + анализ резонанса трёх трофических уровней.

9. **`EcosystemStabilityAnalyzer`**: индекс устойчивости (трёхсферный резонанс + Shannon), анализ tipping point через рост дисперсии и автокорреляции LCI.

---

*Следующая книга: КНИГА 18 — «Архетипы движения в нейрофармакологии»*

---
*© Серия «Архетипы Движения», Книга 17. Основано на «Тотальной Системе Боя» В.В. Крюкова.*
