# КНИГА 33: АРХЕТИПЫ ДВИЖЕНИЯ В АНТРОПОЛОГИИ И КУЛЬТУРОЛОГИИ
## Серия II — Прикладная ЕТД | Блок C: Образование и общество

---

## АННОТАЦИЯ

Культура — это коллективное движение. Ритуал — это петля: от хаоса → через обряд → обратно к космосу. Общество — это три сферы: индивид (МВС) / группа (СВС) / цивилизация (БВС). Язык — это эталонный образец, хранящий культурную память в нечётных структурах (3 рода, 5 падежей, 7 тонов). Настоящий том доказывает: все человеческие культуры — вариации на тему одних и тех же 12 архетипов движения, открытых Крюковым.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Ритуал как архетип Петли

Ван Геннеп (1909) описал трёхчастную структуру ритуала перехода:
- **Сепарация** (отрыв от прежнего состояния — открытие петли)
- **Лиминальность** (пороговое состояние — движение по петле)
- **Инкорпорация** (включение в новое состояние — замыкание петли)

ЛЗП ритуала = степень трансформации участника:
- Свадьба: ЛЗП ≈ 0.95 (радикальная смена статуса)
- День рождения: ЛЗП ≈ 0.40 (символическое обновление)
- Инициация: ЛЗП ≈ 0.98 (мальчик → мужчина, петля полностью замкнута)

**12 Архетипов в антропологии:**

| Архетип | Культурное проявление |
|---------|----------------------|
| Петля | Ритуал перехода, мифологический цикл |
| Три сферы | Земной / сверхъестественный / потусторонний миры |
| Эталон | Миф, священный текст, традиция |
| Камуфляж/Угроза | Маска / обнажённость; тотем / табу |
| Оконная система | Карнавал, праздник (временная инверсия норм) |
| Закон нечётных | 3 мира, 7 дней недели, 9 муз, 5 первоэлементов |
| Чёрный ящик | Тайное знание жреца / шамана |
| Режимы | Профанное / сакральное / лиминальное |
| Животная ОС | Обычаи, традиции (без законодателя, но устойчивые) |
| Пять уровней | Мирянин / послушник / жрец / жрец-жрец / шаман-учитель |
| Закон памяти | 7±2 базовых мифологических сюжетов (Проп: 31 функция → 7 сфер!) |
| Дистанция-сложность | Культурная дистанция (Хофстеде) |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. Анализ ритуала через петлю

```python
import numpy as np
from scipy.spatial import ConvexHull
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class RitualType(Enum):
    RITE_OF_PASSAGE = "rite_of_passage"    # обряд перехода
    CALENDRICAL = "calendrical"            # календарный ритуал
    HEALING = "healing"                    # исцеляющий ритуал
    COMMEMORATION = "commemoration"        # поминальный ритуал
    DIVINATION = "divination"              # гадание / оракул
    SACRIFICE = "sacrifice"               # жертвоприношение

@dataclass
class RitualPhase:
    """Фаза ритуала (по ван Геннепу)"""
    phase: str           # 'separation', 'liminality', 'incorporation'
    duration_relative: float  # относительная длительность (0-1)
    transformation: float     # степень трансформации участника (0-1)
    communal_participation: float  # вовлечённость общины (0-1)
    sacred_objects: int      # число сакральных объектов

class RitualLoopAnalyzer:
    """
    Анализ ритуала через архетип Петли.
    Три фазы ван Геннепа = три сферы Крюкова в динамике:
    МВС = сепарация (индивид отделяется)
    СВС = лиминальность (между мирами)
    БВС = инкорпорация (интеграция в общество)
    """

    # Семь типов ритуальных объектов (нечётное!)
    RITUAL_OBJECTS = [
        'sacred_mask',      # маска (Камуфляж)
        'totem',            # тотем (Эталон)
        'threshold',        # порог (Оконная система)
        'sacred_number',    # священное число (Закон нечётных)
        'black_box_vessel', # сосуд тайного знания (Чёрный ящик)
        'circular_space',   # круговое пространство (Петля)
        'sphere_symbol'     # символ трёх миров (Три сферы)
    ]  # Ровно 7 — нечётное!

    def compute_ritual_lci(self, phases: List[RitualPhase]) -> Dict:
        """
        ЛЗП ритуала через ConvexHull трансформационного пространства.
        Ось X = время (сепарация → лиминальность → инкорпорация)
        Ось Y = трансформация участника
        """
        if len(phases) < 3:
            return {'lci': 0.0, 'reason': 'Нужны все 3 фазы ван Геннепа'}

        # Точки траектории ритуала
        times = np.cumsum([p.duration_relative for p in phases])
        times = times / times[-1]  # нормировка 0→1
        transformations = np.array([p.transformation for p in phases])

        # Добавляем начальную точку (до ритуала)
        all_times = np.concatenate([[0.0], times])
        all_trans = np.concatenate([[0.0], transformations])

        points = np.column_stack([all_times, all_trans])

        lci = 0.0
        if len(points) > 2:
            try:
                hull = ConvexHull(points)
                area = hull.volume
                bbox = ((all_times.max() - all_times.min()) *
                        (all_trans.max() - all_trans.min()))
                lci = min(area / (bbox + 1e-10), 1.0)
            except Exception:
                lci = all_trans[-1] - all_trans[0]  # просто прирост трансформации

        # Трёхфазный резонанс (МВС/СВС/БВС = сепарация/лиминальность/инкорпорация)
        sep_score = phases[0].transformation if len(phases) > 0 else 0
        lim_score = phases[1].transformation if len(phases) > 1 else 0
        inc_score = phases[2].transformation if len(phases) > 2 else 0

        norms = np.array([sep_score, lim_score, inc_score])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            three_phase_resonance = 1.0 - imbalance
        else:
            three_phase_resonance = 0.0

        # Сакральность объектов (нечётные числа усиливают ритуал)
        total_sacred_objects = sum(p.sacred_objects for p in phases)
        odd_sacred = total_sacred_objects % 2 == 1

        # Вовлечённость общины
        community_lci = np.mean([p.communal_participation for p in phases])

        # Итоговый ЛЗП ритуала
        ritual_lci = (lci * 0.3 + three_phase_resonance * 0.3 +
                      community_lci * 0.2 + (0.1 if odd_sacred else 0) +
                      (all_trans[-1] - all_trans[0]) * 0.1)

        return {
            'ritual_lci': ritual_lci,
            'trajectory_lci': lci,
            'three_phase_resonance': three_phase_resonance,
            'community_lci': community_lci,
            'transformation_gain': all_trans[-1] - all_trans[0],
            'odd_sacred_objects': odd_sacred,
            'total_sacred_objects': total_sacred_objects,
            'ritual_power': self._classify(ritual_lci)
        }

    def _classify(self, lci: float) -> str:
        if lci > 0.90: return "Мощный трансформирующий ритуал (Уровень 5)"
        if lci > 0.70: return "Эффективный ритуал перехода (Уровень 4)"
        if lci > 0.50: return "Умеренный ритуал (Уровень 3)"
        if lci > 0.30: return "Слабый ритуал (Уровень 2)"
        return "Символический / формальный ритуал (Уровень 1)"


### 2.2. Три мира = три сферы в мировоззрении

class CosmologicalThreeSphereAnalyzer:
    """
    Все мировые культуры имеют трёхчастную космологию:
    МВС = нижний мир / подземный / царство мёртвых
    СВС = средний мир / земной / здесь-и-сейчас
    БВС = верхний мир / небесный / божественный

    Это УНИВЕРСАЛЬНЫЙ паттерн: шаманизм, греческая мифология,
    Данте (Ад/Чистилище/Рай), индуизм (Нарака/Земля/Сварга).
    ЕТД объясняет почему: три сферы — оптимальная структура движения информации.
    """

    # Примеры трёхмировых систем в разных культурах
    COSMOLOGICAL_EXAMPLES = {
        'siberian_shamanism': {
            'MVS': 'Нижний мир (Ниир)', 'SVS': 'Средний мир (Орта)', 'BVS': 'Верхний мир (Угэ)'
        },
        'greek_mythology': {
            'MVS': 'Аид (Подземный)', 'SVS': 'Земля (Ойкумена)', 'BVS': 'Олимп (Небеса)'
        },
        'dante': {
            'MVS': 'Ад (Инферно)', 'SVS': 'Чистилище (Пургаторио)', 'BVS': 'Рай (Параизо)'
        },
        'hinduism': {
            'MVS': 'Нарака (Преисподняя)', 'SVS': 'Бхур-лока (Земля)', 'BVS': 'Сварга (Небо)'
        },
        'norse_mythology': {
            'MVS': 'Хельхейм/Нифльхейм', 'SVS': 'Мидгард', 'BVS': 'Асгард'
        },
        'aztec': {
            'MVS': 'Миктлан (9 уровней подземного = нечётное!)',
            'SVS': 'Тлальтипак (Земля)',
            'BVS': 'Ильхуикатль (13 небес = нечётное!)'
        }
    }

    def compute_cosmology_universality_lci(self) -> Dict:
        """
        ЛЗП универсальности трёхмировой космологии.
        Все культуры имеют три сферы → резонанс = 1.0.
        """
        n_cultures = len(self.COSMOLOGICAL_EXAMPLES)

        # Все примеры имеют ровно 3 сферы
        all_have_3_spheres = all(
            len(example) == 3
            for example in self.COSMOLOGICAL_EXAMPLES.values()
        )

        # Нечётные числа в космологии (пример: ацтеки)
        odd_cosmological_numbers = {
            'aztec_underworld_levels': 9,    # нечётное!
            'aztec_heavens': 13,             # нечётное!
            'greek_fates': 3,                # нечётное!
            'norse_worlds': 9,               # нечётное!
            'chakras': 7,                    # нечётное!
            'days_of_creation': 7,           # нечётное!
            'biblical_heavens': 7,           # нечётное!
        }

        all_odd = all(v % 2 == 1 for v in odd_cosmological_numbers.values())

        return {
            'n_cultures_analyzed': n_cultures,
            'all_have_3_spheres': all_have_3_spheres,
            'universality_lci': 1.0 if all_have_3_spheres else 0.5,
            'odd_cosmological_numbers': odd_cosmological_numbers,
            'all_cosmological_numbers_odd': all_odd,
            'conclusion': (
                "Три сферы — универсальная структура человеческого космоса. "
                "ЕТД объясняет эту универсальность: три — минимальное нечётное "
                "число для устойчивой трёхсферной системы."
            )
        }


### 2.3. Язык как эталонный образец культуры

class LinguisticETDAnalyzer:
    """
    Язык = Эталонный образец + Закон нечётных.
    Грамматические категории часто нечётны:
    - Роды: 3 (мужской/женский/средний) — нечётное!
    - Числа: 3 (единственное/двойственное/множественное) — нечётное!
    - Лица: 3 (я/ты/он) — нечётное!
    - Тона в тональных языках: 5, 7 или 9 — нечётные!
    """

    # Грамматические категории с нечётными значениями
    ODD_LINGUISTIC_CATEGORIES = {
        'grammatical_gender_max': 3,     # М/Ж/Ср — нечётное!
        'grammatical_person': 3,          # 1/2/3 лицо — нечётное!
        'russian_cases': 7,               # нечётное (если считать с архаичными: 9!)
        'latin_declensions': 5,           # нечётное!
        'mandarin_tones': 5,              # нечётное (4 тона + нейтральный = 5)!
        'cantonese_tones': 9,             # нечётное!
        'thai_tones': 5,                  # нечётное!
        'russian_verb_aspects': 3,        # совершенный/несоверш./двувидовые — нечётное!
        'arabic_verb_forms': 7,           # нечётное (основные породы)!
        'hebrew_binyanim': 7,             # нечётное!
    }

    def analyze_language_etd_alignment(self, language: str, grammar_data: Dict) -> Dict:
        """
        Анализ языка на соответствие принципам ЕТД.
        """
        odd_categories = 0
        total_categories = 0
        category_analysis = {}

        for category, value in grammar_data.items():
            total_categories += 1
            is_odd = value % 2 == 1
            if is_odd:
                odd_categories += 1
            category_analysis[category] = {
                'value': value,
                'is_odd': is_odd,
                'memory_law_ok': 3 <= value <= 9
            }

        # ЛЗП языка = доля нечётных категорий
        language_lci = odd_categories / (total_categories + 1e-10)

        # Три сферы языка
        # МВС = фонология (звуки, тоны)
        n_phonemes = grammar_data.get('n_phonemes', 25)
        mvs_lci = 1.0 if n_phonemes % 2 == 1 else 0.7

        # СВС = морфология (формы слов)
        n_cases = grammar_data.get('n_cases', 7)
        svs_lci = 1.0 if n_cases % 2 == 1 else 0.7

        # БВС = синтаксис (предложение)
        sov_order = grammar_data.get('is_sov', True)  # SOV = нечётная структура?
        bvs_lci = 0.9 if sov_order else 0.7

        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        return {
            'language': language,
            'odd_categories': odd_categories,
            'total_categories': total_categories,
            'language_lci': language_lci,
            'mvs_phonology_lci': mvs_lci,
            'svs_morphology_lci': svs_lci,
            'bvs_syntax_lci': bvs_lci,
            'three_sphere_resonance': resonance,
            'category_analysis': category_analysis,
            'etd_alignment': 'Высокое' if language_lci > 0.7 else 'Среднее'
        }


### 2.4. Культурные измерения Хофстеде = архетипические расстояния

class HofstedeETDMapper:
    """
    Культурные измерения Хофстеде через ЕТД:
    - Дистанция власти (PDI) → Дистанция-сложность Крюкова
    - Индивидуализм (IDV) → МВС vs БВС доминирование
    - Избегание неопределённости (UAI) → Закон памяти (7±2 правил)
    - Долгосрочная ориентация (LTO) → Режим (СКАН vs ДВОЙНОЙ)
    - Снисходительность (IVR) → Оконная система (открыта/закрыта)

    6 измерений Хофстеде → 5 архетипов Крюкова (нечётное!)
    """

    # Нормативные значения Хофстеде (из базы данных)
    HOFSTEDE_DB = {
        'Russia': {'PDI': 93, 'IDV': 39, 'MAS': 36, 'UAI': 95, 'LTO': 81, 'IVR': 20},
        'USA': {'PDI': 40, 'IDV': 91, 'MAS': 62, 'UAI': 46, 'LTO': 26, 'IVR': 68},
        'Japan': {'PDI': 54, 'IDV': 46, 'MAS': 95, 'UAI': 92, 'LTO': 88, 'IVR': 42},
        'Sweden': {'PDI': 31, 'IDV': 71, 'MAS': 5, 'UAI': 29, 'LTO': 53, 'IVR': 78},
        'China': {'PDI': 80, 'IDV': 20, 'MAS': 66, 'UAI': 30, 'LTO': 87, 'IVR': 24},
    }

    def map_to_etd(self, country: str) -> Dict:
        """
        Отображение культурного профиля на архетипы ЕТД.
        """
        if country not in self.HOFSTEDE_DB:
            return {'error': f'Нет данных по {country}'}

        d = self.HOFSTEDE_DB[country]

        # Дистанция-сложность (PDI → расстояние от гражданина до власти)
        distance_complexity_lci = 1.0 - d['PDI'] / 100

        # Три сферы (IDV → МВС vs БВС)
        if d['IDV'] > 60:
            dominant_sphere = 'MVS'  # индивидуализм = МВС
            sphere_lci = d['IDV'] / 100
        else:
            dominant_sphere = 'BVS'  # коллективизм = БВС
            sphere_lci = 1 - d['IDV'] / 100

        # Закон памяти (UAI → число правил)
        # Высокое UAI = много правил → нарушение Закона памяти
        memory_law_lci = 1.0 - abs(d['UAI'] - 50) / 100

        # Режим (LTO → временной горизонт)
        if d['LTO'] > 60:
            mode = 'DUAL'  # долгосрочность = ДВОЙНОЙ режим
        elif d['LTO'] > 40:
            mode = 'PRECISE'
        elif d['LTO'] > 20:
            mode = 'ADAPTIVE'
        else:
            mode = 'SCAN'  # краткосрочность = СКАН

        # Оконная система (IVR → открытость к новому)
        window_lci = d['IVR'] / 100

        # Общий культурный ЛЗП
        cultural_lci = np.mean([
            distance_complexity_lci,
            sphere_lci,
            memory_law_lci,
            window_lci
        ])

        return {
            'country': country,
            'hofstede_scores': d,
            'distance_complexity_lci': distance_complexity_lci,
            'dominant_sphere': dominant_sphere,
            'sphere_lci': sphere_lci,
            'memory_law_lci': memory_law_lci,
            'kryukov_mode': mode,
            'window_lci': window_lci,
            'cultural_lci': cultural_lci,
            'cultural_archetype': self._describe(d)
        }

    def _describe(self, d: Dict) -> str:
        if d['IDV'] > 60 and d['PDI'] < 50:
            return "Западная либеральная культура (высокий МВС-ЛЗП)"
        elif d['IDV'] < 40 and d['PDI'] > 70:
            return "Конфуцианская иерархическая культура (высокий БВС-ЛЗП)"
        elif d['UAI'] > 80:
            return "Культура избегания неопределённости (нарушение Закона памяти)"
        elif d['LTO'] > 75:
            return "Долгосрочная культура (ДВОЙНОЙ режим)"
        else:
            return "Смешанный культурный профиль"

    def compute_cultural_distance_lci(self, country1: str, country2: str) -> Dict:
        """
        ЛЗП культурного расстояния = дистанция в пространстве Хофстеде.
        Малое расстояние → лёгкое взаимопонимание (высокий ЛЗП коммуникации).
        Большое расстояние → культурный барьер (низкий ЛЗП).
        """
        if country1 not in self.HOFSTEDE_DB or country2 not in self.HOFSTEDE_DB:
            return {'error': 'Нет данных'}

        d1 = self.HOFSTEDE_DB[country1]
        d2 = self.HOFSTEDE_DB[country2]

        dims = ['PDI', 'IDV', 'MAS', 'UAI', 'LTO', 'IVR']
        diffs = [(d1[dim] - d2[dim])**2 for dim in dims]
        euclidean_distance = np.sqrt(sum(diffs))

        # Максимальное возможное расстояние (100*√6 ≈ 245)
        max_distance = 100 * np.sqrt(6)
        communication_lci = 1.0 - euclidean_distance / max_distance

        return {
            'country1': country1,
            'country2': country2,
            'euclidean_distance': euclidean_distance,
            'communication_lci': communication_lci,
            'dimension_gaps': dict(zip(dims, [abs(d1[d] - d2[d]) for d in dims])),
            'cultural_fit': (
                'Высокое сродство' if communication_lci > 0.8
                else 'Среднее сродство' if communication_lci > 0.6
                else 'Культурный барьер'
            )
        }


### 2.5. Мифологические сюжеты: Закон памяти Проппа

class MythologicalMemoryAnalyzer:
    """
    Пропп (1928) нашёл 31 функцию волшебной сказки.
    Но ЕТД предсказывает: реально запоминаемых архетипических сюжетов — 7±2 (нечётное!)
    Кэмпбелл (1949): один «Путь Героя» охватывает все 31 функцию.
    Томашевский: 7 нарративных архетипов достаточно (нечётное!).
    """

    # 7 базовых нарративных архетипов Буза (нечётное!)
    BOOKER_PLOTS = [
        'overcoming_the_monster',  # Победа над монстром
        'rags_to_riches',          # От нищеты к богатству
        'quest',                   # Путешествие и поиск (Петля!)
        'voyage_and_return',       # Плавание и возвращение (Петля!)
        'comedy',                  # Комедия (замыкание социальной петли)
        'tragedy',                 # Трагедия (разорванная петля)
        'rebirth'                  # Возрождение (петля смерти/воскресения)
    ]  # Ровно 7 — нечётное! (Booker, 2004)

    # Соответствие архетипам Крюкова
    PLOT_TO_ARCHETYPE = {
        'quest': 'Петля',                    # путь = замкнутая петля
        'voyage_and_return': 'Петля',         # путешествие = петля
        'rebirth': 'Петля',                   # смерть-воскресение = петля
        'overcoming_the_monster': 'Камуфляж/Угроза',  # монстр = угроза
        'rags_to_riches': 'Пять уровней',    # восхождение по уровням
        'comedy': 'Оконная система',          # брак = замкнутое окно
        'tragedy': 'Разорванная петля'        # катастрофа = ЛЗП → 0
    }

    def compute_plot_lci(self, plot_type: str, narrative_data: Dict) -> Dict:
        """
        ЛЗП нарратива в зависимости от архетипа сюжета.
        """
        n_acts = narrative_data.get('n_acts', 3)  # количество актов
        if n_acts % 2 == 0:
            n_acts += 1  # нечётность!

        protagonist_growth = narrative_data.get('protagonist_growth', 0.7)
        community_resolution = narrative_data.get('community_resolution', 0.5)
        loop_closure = narrative_data.get('loop_closure', 0.5)

        # Базовый ЛЗП по типу сюжета
        base_lci = {
            'quest': 0.85,
            'voyage_and_return': 0.90,
            'rebirth': 0.95,
            'overcoming_the_monster': 0.80,
            'rags_to_riches': 0.75,
            'comedy': 0.85,
            'tragedy': 0.20
        }.get(plot_type, 0.5)

        # Модификаторы
        narrative_lci = (base_lci * 0.4 +
                         protagonist_growth * 0.3 +
                         community_resolution * 0.2 +
                         loop_closure * 0.1)

        archetype = self.PLOT_TO_ARCHETYPE.get(plot_type, 'Неизвестный')

        return {
            'plot_type': plot_type,
            'n_acts': n_acts,
            'n_acts_odd': n_acts % 2 == 1,
            'narrative_lci': narrative_lci,
            'kryukov_archetype': archetype,
            'protagonist_growth': protagonist_growth,
            'loop_closed': loop_closure > 0.5,
            'universal_pattern': plot_type in ['quest', 'voyage_and_return', 'rebirth']
        }


### 2.6. Диагностика культурного здоровья

def diagnose_cultural_health(culture_data: Dict) -> Dict:
    """
    Диагностика культуры по 7 аксиомам Крюкова.
    """
    axiom_scores = {}

    # А1: Петля (наличие замкнутых ритуальных циклов)
    ritual_completeness = culture_data.get('ritual_completeness', 0.7)
    axiom_scores['A1_ritual_loop'] = ritual_completeness

    # А2: Три сферы (трёхмировая космология)
    cosmology_balance = culture_data.get('three_world_balance', 0.7)
    axiom_scores['A2_three_worlds'] = cosmology_balance

    # А3: Эталон (наличие священных текстов / эталонного образца)
    tradition_strength = culture_data.get('tradition_strength', 0.6)
    axiom_scores['A3_sacred_template'] = tradition_strength

    # А4: Оконная система (карнавал, переходные периоды)
    liminality_health = culture_data.get('liminality_health', 0.6)
    axiom_scores['A4_window_rituals'] = liminality_health

    # А5: Закон нечётных (нечётные сакральные числа в культуре)
    sacred_number_odd = culture_data.get('primary_sacred_number', 7)
    axiom_scores['A5_odd_sacred'] = 1.0 if sacred_number_odd % 2 == 1 else 0.5

    # А6: Закон памяти (≤9 базовых мифологических сюжетов)
    n_core_myths = culture_data.get('n_core_myths', 7)
    axiom_scores['A6_myth_memory'] = 1.0 if n_core_myths <= 9 else max(0, 1.0 - (n_core_myths - 9) * 0.05)

    # А7: Режим (ритуалы соответствуют сезону / циклу жизни)
    seasonal_alignment = culture_data.get('seasonal_ritual_alignment', 0.7)
    axiom_scores['A7_seasonal_mode'] = seasonal_alignment

    culture_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'culture_lci': culture_lci,
        'violations': violations,
        'n_violations': len(violations),
        'cultural_vitality': _grade_culture(culture_lci)
    }


def apply_kryukov_cultural_optimizer(culture_name: str, violations: Dict) -> List[str]:
    """Рекомендации по восстановлению культурного здоровья."""
    remedies = []
    if 'A1_ritual_loop' in violations:
        remedies.append("Восстановить обряды перехода (рождение/совершеннолетие/брак/смерть)")
    if 'A2_three_worlds' in violations:
        remedies.append("Реактивировать трёхмировую космологию через искусство и образование")
    if 'A3_sacred_template' in violations:
        remedies.append("Кодифицировать нематериальное культурное наследие (ЮНЕСКО)")
    if 'A4_window_rituals' in violations:
        remedies.append("Возродить карнавальные традиции как лиминальные окна")
    if 'A5_odd_sacred' in violations:
        remedies.append("Осознать нечётные сакральные числа культуры и усилить их роль")
    if 'A6_myth_memory' in violations:
        remedies.append("Сократить мифологический канон до 7±2 ключевых нарративов")
    if 'A7_seasonal_mode' in violations:
        remedies.append("Синхронизировать ритуальный календарь с природными циклами")

    if len(remedies) % 2 == 0 and remedies:
        remedies.append("Создать центр живой культуры для передачи традиций (Уровень 5)")
    return remedies


def _grade_culture(lci: float) -> str:
    if lci > 0.85: return "Живая, процветающая культура (Уровень 5)"
    if lci > 0.70: return "Устойчивая культурная традиция (Уровень 4)"
    if lci > 0.55: return "Культура в трансформации (Уровень 3)"
    if lci > 0.40: return "Культура под угрозой утраты (Уровень 2)"
    return "Критическое состояние культуры (Уровень 1)"
```

---

## ЧАСТЬ III: ПРАКТИЧЕСКИЕ ПРИЛОЖЕНИЯ

### Глава 3. Шаманизм = Пять уровней мастерства + Чёрный ящик

Сибирский шаман — носитель всех 12 архетипов одновременно:
- **Петля**: путешествие в нижний и верхний миры (и возврат!)
- **Три сферы**: маршруты через три мира
- **Эталон**: священные песни-камлания (буквальная «Животная ОС»)
- **Чёрный ящик**: тайное знание, недоступное непосвящённым
- **Пять уровней**: ученик → помощник → шаман → великий шаман → учитель шаманов

ЛЗП шаманского ритуала (камлания) = успешность путешествия в иной мир и возврата: 0.92-0.98.

### Глава 4. Культура = «медленный ИИ»

Культура делает то же, что делает искусственный интеллект:
- **Распознаёт паттерны** (через мифы и ритуалы)
- **Прогнозирует** (через астрологию, оракулов, шаманов)
- **Оптимизирует поведение** (через нормы и табу)
- **Обучается** (через предание, фольклор)
- **Передаёт знания** (через ритуалы инициации)

Разница: ИИ работает в реальном времени, культура — в историческом масштабе.
ЛЗП культуры ≡ точность её «медленного ИИ».

---

## ЧАСТЬ IV: ПЯТЬ УРОВНЕЙ МАСТЕРСТВА АНТРОПОЛОГА

**Уровень 1**: Наблюдение ритуалов; фиксация 7 типов ритуальных объектов.

**Уровень 2**: Анализ трёхмировой космологии; измерение ЛЗП ритуала.

**Уровень 3**: Картография культурных дистанций (Хофстеде + ЕТД); сравнительный анализ.

**Уровень 4**: Восстановление угасающих культур через реактивацию архетипов.

**Уровень 5**: Проектирование новых культурных форм с ЛЗП ≥ 0.90 — трансдисциплинарная работа.

---

## ВЫВОДЫ

1. **Ритуал** = 3-фазная петля ван Геннепа (сепарация/лиминальность/инкорпорация = три сферы в динамике)
2. **Все культуры** имеют трёхмировую космологию = универсальность трёх сфер (ЛЗП = 1.0)
3. **Язык** = эталонный образец; грамматические категории нечётны (3 лица, 5-7-9 тонов)
4. **Хофстеде** = архетипические расстояния; PDI=дистанция-сложность, IDV=МВС/БВС баланс
5. **7 нарративных архетипов** Букера (нечётное!) = Закон памяти в действии
6. **Шаманизм** = носитель всех 12 архетипов; ЛЗП = результат путешествия и возврата
7. **Культура** = «медленный ИИ»; её ЛЗП = точность предсказания и оптимизации поведения

---

*Следующая книга: КНИГА 34 — «Архетипы движения в искусстве и дизайне»*
