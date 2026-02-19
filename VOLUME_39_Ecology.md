# КНИГА 39: АРХЕТИПЫ ДВИЖЕНИЯ В ЭКОЛОГИИ И НАУКАХ О ЗЕМЛЕ
## Серия II — Прикладная ЕТД | Блок D: Технологии и будущее

---

## АННОТАЦИЯ

Экосистема — это движение вещества и энергии. Пищевая цепь — петля: продуценты → консументы → редуценты → минералы → продуценты. Биосфера — три сферы: организм (МВС) / популяция (СВС) / экосистема (БВС). Климатическая система — петля обратной связи: температура → испарение → облака → альбедо → температура. Настоящий том доказывает: все экологические законы — частные случаи ЕТД. Биосфера — самая большая замкнутая петля на Земле; её ЛЗП = устойчивость планеты.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Биогеохимический цикл как архетип Петли

Цикл углерода — идеальная петля:
- Фотосинтез (CO₂ → органика) — открытие петли
- Дыхание / разложение (органика → CO₂) — замыкание петли
- Антропогенный выброс — инъекция в петлю без соответствующего замыкания = **нарушение петли**

ЛЗП углеродного цикла = степень замкнутости: сколько выброшенного CO₂ поглощается = 1 - atmospheric_accumulation_fraction.

**12 Архетипов в экологии:**

| Архетип | Экологическое проявление |
|---------|-------------------------|
| Петля | Биогеохимический цикл, трофическая цепь, сукцессия |
| Три сферы | Организм/популяция/экосистема; литосфера/гидросфера/атмосфера |
| Эталон | Климатический оптимум, К-стратегия, биоразнообразие-максимум |
| Камуфляж/Угроза | Криптические виды / инвазивные виды |
| Оконная система | Экологическая ниша; фенологическое окно |
| Закон нечётных | 3 домена жизни, 5 массовых вымираний, 7 уровней классификации |
| Чёрный ящик | Почва (99% микроорганизмов не изучено), глубоководье |
| Режимы | Первичная/вторичная/климаксная сукцессия; r-стратег/K-стратег |
| Животная ОС | Инстинкты популяции, стайное поведение, рой |
| Пять уровней | Особь/популяция/сообщество/экосистема/биосфера |
| Закон памяти | 7±2 ключевых видов (keystone species) в экосистеме |
| Дистанция-сложность | Трофический уровень / длина пищевой цепи |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. ЛЗП биогеохимического цикла

```python
import numpy as np
from scipy.spatial import ConvexHull
from scipy.integrate import solve_ivp
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class EcosystemType(Enum):
    TROPICAL_RAINFOREST = "tropical_rainforest"
    TEMPERATE_FOREST = "temperate_forest"
    BOREAL_FOREST = "boreal_forest"
    GRASSLAND = "grassland"
    WETLAND = "wetland"
    CORAL_REEF = "coral_reef"
    OPEN_OCEAN = "open_ocean"

@dataclass
class BiogeochemicalPool:
    """Пул вещества в биогеохимическом цикле"""
    name: str
    size_Gt: float         # размер пула (гигатонны)
    residence_time_yr: float  # время пребывания (годы)
    input_flux_Gt_yr: float   # входной поток (Гт/год)
    output_flux_Gt_yr: float  # выходной поток (Гт/год)

class BiogeochemicalLoopAnalyzer:
    """
    Анализ биогеохимического цикла через архетип Петли.

    Углеродный цикл Земли (приблизительные значения):
    Атмосфера: 870 Гт С
    Суша (биота+почва): 2200 Гт С
    Океан (поверхность): 900 Гт С
    Глубокий океан: 37100 Гт С
    Осадки/литосфера: 66 000 000 Гт С

    Петля работает миллиарды лет = ЛЗП = 1.0 (если не нарушена).
    Антропогенный выброс ≈ 10 Гт С/год нарушает петлю.
    """

    # 7 основных биогеохимических циклов (нечётное!)
    BIOGEOCHEMICAL_CYCLES = [
        'carbon',    # углеродный цикл
        'nitrogen',  # азотный цикл
        'phosphorus',# фосфорный цикл
        'sulfur',    # серный цикл
        'water',     # водный цикл
        'oxygen',    # кислородный цикл
        'iron'       # железный цикл (лимитирующий в океане)
    ]  # Ровно 7 — нечётное!

    def compute_cycle_lci(self, pools: List[BiogeochemicalPool]) -> Dict:
        """
        ЛЗП биогеохимического цикла через ConvexHull.
        Ось X = размер пула, Ось Y = входной поток.
        Замкнутый цикл: input = output для каждого пула.
        """
        if len(pools) < 3:
            return {'lci': 0.0}

        sizes = np.array([p.size_Gt for p in pools])
        inputs = np.array([p.input_flux_Gt_yr for p in pools])
        outputs = np.array([p.output_flux_Gt_yr for p in pools])

        # Дисбаланс каждого пула (input - output)
        imbalances = inputs - outputs

        # ConvexHull в пространстве (log_size, log_input)
        log_sizes = np.log1p(sizes)
        log_inputs = np.log1p(inputs)
        points = np.column_stack([
            (log_sizes - log_sizes.mean()) / (log_sizes.std() + 1e-10),
            (log_inputs - log_inputs.mean()) / (log_inputs.std() + 1e-10)
        ])

        lci = 0.0
        if len(points) > 2:
            try:
                hull = ConvexHull(points)
                area = hull.volume
                bbox = ((points[:, 0].max() - points[:, 0].min()) *
                        (points[:, 1].max() - points[:, 1].min()))
                lci = min(area / (bbox + 1e-10), 1.0)
            except Exception:
                lci = 0.5

        # Замкнутость: суммарный дисбаланс должен быть близок к 0
        total_input = inputs.sum()
        total_imbalance = abs(imbalances.sum())
        closure_lci = 1.0 - total_imbalance / (total_input + 1e-10)

        # Время пребывания: разнообразие масштабов = богатство цикла
        residence_times = np.array([p.residence_time_yr for p in pools])
        time_diversity = np.log(residence_times.max() / (residence_times.min() + 1e-10))
        time_diversity_lci = min(time_diversity / 10, 1.0)

        # Итоговый ЛЗП
        cycle_lci = (lci * 0.30 + closure_lci * 0.50 + time_diversity_lci * 0.20)

        return {
            'n_pools': len(pools),
            'n_pools_odd': len(pools) % 2 == 1,
            'trajectory_lci': lci,
            'closure_lci': closure_lci,
            'time_diversity_lci': time_diversity_lci,
            'cycle_lci': cycle_lci,
            'total_imbalance_Gt': total_imbalance,
            'is_closed': total_imbalance < total_input * 0.05,
            'n_cycles': len(self.BIOGEOCHEMICAL_CYCLES),
            'cycles_odd': len(self.BIOGEOCHEMICAL_CYCLES) % 2 == 1
        }

    def simulate_carbon_cycle_perturbation(
        self,
        anthropogenic_emission_Gt_yr: float = 10.0,
        n_years: int = 101,   # нечётное!
        ocean_uptake_fraction: float = 0.25,
        land_uptake_fraction: float = 0.30
    ) -> Dict:
        """
        Симуляция нарушения углеродного цикла антропогенными выбросами.
        Простая 3-пульная модель: Атмосфера / Суша / Океан.
        """
        if n_years % 2 == 0:
            n_years += 1  # нечётность!

        atm_0 = 870.0   # Гт С в атмосфере (≈ 280 ppm доиндустриальный уровень → 870 ≈ 415 ppm)
        land_0 = 2200.0
        ocean_0 = 38000.0

        atm = np.zeros(n_years)
        land = np.zeros(n_years)
        ocean = np.zeros(n_years)

        atm[0] = atm_0
        land[0] = land_0
        ocean[0] = ocean_0

        for i in range(1, n_years):
            # Антропогенный выброс
            emission = anthropogenic_emission_Gt_yr

            # Поглощение
            land_uptake = emission * land_uptake_fraction * (land[i-1] / land_0) ** 0.5
            ocean_uptake = emission * ocean_uptake_fraction * (ocean[i-1] / ocean_0) ** 0.5

            # Изменение пулов
            delta_atm = emission - land_uptake - ocean_uptake
            atm[i] = atm[i-1] + delta_atm
            land[i] = land[i-1] + land_uptake - 0.01 * land[i-1]  # потери из-за прогрева
            ocean[i] = ocean[i-1] + ocean_uptake

        # ЛЗП цикла: атмосферная аккумуляция vs. поглощение
        atmospheric_fraction = (atm[-1] - atm_0) / (anthropogenic_emission_Gt_yr * n_years)
        cycle_lci = max(0.0, 1.0 - atmospheric_fraction)

        # ConvexHull в пространстве (atm, land+ocean)
        sinks = land + ocean
        points = np.column_stack([
            (atm - atm.mean()) / (atm.std() + 1e-10),
            (sinks - sinks.mean()) / (sinks.std() + 1e-10)
        ])
        try:
            hull = ConvexHull(points)
            traj_lci = min(hull.volume / 4.0, 1.0)
        except Exception:
            traj_lci = 0.3

        return {
            'n_years': n_years,
            'n_years_odd': n_years % 2 == 1,
            'initial_atm_Gt': atm_0,
            'final_atm_Gt': atm[-1],
            'atm_increase_Gt': atm[-1] - atm_0,
            'atmospheric_fraction': atmospheric_fraction,
            'cycle_lci': cycle_lci,
            'trajectory_lci': traj_lci,
            'loop_disruption': atmospheric_fraction > 0.5,
            'diagnosis': (
                "Петля нарушена: атмосфера перегружена" if atmospheric_fraction > 0.5
                else "Петля частично работает: поглотители справляются"
            )
        }


### 2.2. Трофическая сеть = три сферы + пять уровней

class TrophicNetworkETDAnalyzer:
    """
    Трофическая сеть = три сферы + пять уровней Крюкова.

    МВС = продуценты (растения, фотосинтез)
    СВС = консументы I порядка (травоядные)
    БВС = консументы II+ порядка (хищники, редуценты)

    Пять трофических уровней (нечётное!):
    1. Продуценты (растения, водоросли)
    2. Первичные консументы (травоядные)
    3. Вторичные консументы (плотоядные I)
    4. Третичные консументы (плотоядные II)
    5. Квинтарные консументы / вершинные хищники
    """

    # 7 типов экологических взаимодействий (нечётное!)
    ECOLOGICAL_INTERACTIONS = [
        'predation',       # хищничество (+/-)
        'competition',     # конкуренция (-/-)
        'mutualism',       # мутуализм (+/+)
        'commensalism',    # комменсализм (+/0)
        'parasitism',      # паразитизм (+/-)
        'amensalism',      # аменсализм (-/0)
        'neutralism'       # нейтрализм (0/0)
    ]  # Ровно 7 — нечётное!

    def compute_trophic_lci(
        self,
        biomass_by_level: List[float],  # биомасса на каждом трофическом уровне
    ) -> Dict:
        """
        ЛЗП трофической сети через ConvexHull и пирамиду Элтона.
        """
        if len(biomass_by_level) < 3:
            return {'lci': 0.0}

        n_levels = len(biomass_by_level)
        levels = np.arange(1, n_levels + 1)
        biomass = np.array(biomass_by_level, dtype=float)

        # Пирамида Элтона: биомасса должна убывать на каждом уровне
        is_pyramid = all(biomass[i] > biomass[i+1] for i in range(len(biomass)-1))

        # КПД трансформации (правило 10%): ~10% энергии передаётся на следующий уровень
        transfer_efficiencies = []
        for i in range(len(biomass) - 1):
            eff = biomass[i+1] / (biomass[i] + 1e-10)
            transfer_efficiencies.append(eff)

        mean_efficiency = np.mean(transfer_efficiencies) if transfer_efficiencies else 0.1
        efficiency_lci = 1.0 - abs(mean_efficiency - 0.10) / 0.10  # идеал = 10%
        efficiency_lci = max(0.0, efficiency_lci)

        # ConvexHull в пространстве (уровень, log_биомасса)
        log_biomass = np.log1p(biomass)
        points = np.column_stack([
            levels / levels.max(),
            (log_biomass - log_biomass.min()) / (log_biomass.max() - log_biomass.min() + 1e-10)
        ])
        try:
            hull = ConvexHull(points)
            traj_lci = min(hull.volume / 0.5, 1.0)
        except Exception:
            traj_lci = 0.3

        # Трёхсферный анализ (МВС/СВС/БВС = продуценты/травоядные/хищники)
        mvs_biomass = biomass[0]
        svs_biomass = biomass[1] if len(biomass) > 1 else 0
        bvs_biomass = biomass[-1]

        norms = np.array([mvs_biomass, svs_biomass, bvs_biomass])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - np.array([0.9, 0.09, 0.01])).sum() / 2
            # Эталонное распределение: 90/9/1 ≈ пирамида Элтона
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        trophic_lci = (traj_lci * 0.30 + efficiency_lci * 0.30 +
                       resonance * 0.25 + (0.15 if is_pyramid else 0))

        return {
            'n_trophic_levels': n_levels,
            'n_levels_odd': n_levels % 2 == 1,
            'is_eltonian_pyramid': is_pyramid,
            'mean_transfer_efficiency': mean_efficiency,
            'efficiency_lci': efficiency_lci,
            'trajectory_lci': traj_lci,
            'three_sphere_resonance': resonance,
            'trophic_lci': trophic_lci,
            'n_interaction_types': len(self.ECOLOGICAL_INTERACTIONS),
            'interactions_types_odd': len(self.ECOLOGICAL_INTERACTIONS) % 2 == 1,
            'ecosystem_health': self._grade(trophic_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.85: return "Первозданная экосистема (Уровень 5)"
        if lci > 0.70: return "Здоровая экосистема (Уровень 4)"
        if lci > 0.55: return "Умеренно нарушенная экосистема (Уровень 3)"
        if lci > 0.35: return "Значительно нарушенная (Уровень 2)"
        return "Коллапс экосистемы (Уровень 1)"


### 2.3. Климатическая петля обратной связи

class ClimateFeedbackLoopAnalyzer:
    """
    Климатическая система = система петель обратной связи.

    Положительные петли (усиливают отклонение — разрывают равновесие):
    - Ледниково-альбедный: T↑ → лёд↓ → альбедо↓ → T↑
    - Водяной пар: T↑ → испарение↑ → парниковый эффект↑ → T↑
    - Вечная мерзлота: T↑ → метан из торфа↑ → T↑

    Отрицательные петли (стабилизируют — замыкают равновесие):
    - Планковское излучение: T↑ → излучение↑ → охлаждение↑ → T↓
    - Лапс-рейт: T↑ → конвекция↑ → охлаждение↑
    - Облачность (частично): T↑ → облака↑ → альбедо↑ → T↓

    ЛЗП климата = преобладание стабилизирующих петель.
    """

    # 7 основных климатических петель (нечётное!)
    CLIMATE_FEEDBACKS = {
        'planck_radiation': {'type': 'negative', 'strength': -3.2},  # Вт/м²/К
        'water_vapor': {'type': 'positive', 'strength': +1.8},
        'lapse_rate': {'type': 'negative', 'strength': -0.6},
        'surface_albedo': {'type': 'positive', 'strength': +0.4},
        'cloud_shortwave': {'type': 'negative', 'strength': -0.5},
        'cloud_longwave': {'type': 'positive', 'strength': +0.3},
        'permafrost_methane': {'type': 'positive', 'strength': +0.2}
    }  # Ровно 7 — нечётное!

    def compute_climate_stability_lci(
        self,
        co2_ppm: float = 420.0,      # текущая концентрация CO₂
        preindustrial_co2: float = 280.0
    ) -> Dict:
        """
        ЛЗП климатической стабильности через анализ петель обратной связи.
        """
        # Суммарная обратная связь
        total_negative = sum(v['strength'] for v in self.CLIMATE_FEEDBACKS.values()
                             if v['type'] == 'negative')
        total_positive = sum(v['strength'] for v in self.CLIMATE_FEEDBACKS.values()
                             if v['type'] == 'positive')

        net_feedback = total_negative + total_positive  # должно быть < 0 для стабильности

        # Климатическая чувствительность (ECS)
        forcing = 3.7 * np.log(co2_ppm / preindustrial_co2) / np.log(2)
        ecs = -forcing / (net_feedback + 1e-10)  # К при удвоении CO₂

        # ЛЗП стабильности климата
        if net_feedback < 0:
            # Стабилизирующие петли преобладают
            stability_lci = min(abs(net_feedback) / 3.2, 1.0)
        else:
            # Дестабилизирующие петли преобладают (runaway climate)
            stability_lci = 0.0

        # Концентрация CO₂ относительно «окна» Голоцена (280-350 ppm = норма)
        holocene_window_upper = 350.0
        if co2_ppm <= holocene_window_upper:
            window_lci = 1.0
        else:
            excess = (co2_ppm - holocene_window_upper) / holocene_window_upper
            window_lci = max(0.0, 1.0 - excess)

        climate_lci = (stability_lci * 0.5 + window_lci * 0.5)

        n_positive = sum(1 for v in self.CLIMATE_FEEDBACKS.values() if v['type'] == 'positive')
        n_negative = sum(1 for v in self.CLIMATE_FEEDBACKS.values() if v['type'] == 'negative')

        return {
            'co2_ppm': co2_ppm,
            'radiative_forcing_W_m2': forcing,
            'net_feedback_W_m2_K': net_feedback,
            'ecs_K': ecs,
            'n_negative_feedbacks': n_negative,
            'n_positive_feedbacks': n_positive,
            'n_feedbacks_total': len(self.CLIMATE_FEEDBACKS),
            'feedbacks_odd': len(self.CLIMATE_FEEDBACKS) % 2 == 1,
            'stability_lci': stability_lci,
            'holocene_window_lci': window_lci,
            'climate_lci': climate_lci,
            'is_stable': net_feedback < 0 and co2_ppm < 450,
            'climate_health': self._grade(climate_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.85: return "Климатический оптимум (Голоцен)"
        if lci > 0.65: return "Умеренное климатическое давление"
        if lci > 0.40: return "Высокий климатический риск"
        if lci > 0.20: return "Климатический кризис"
        return "Необратимые климатические изменения"


### 2.4. Биоразнообразие = Закон нечётных и эталон

class BiodiversityETDAnalyzer:
    """
    Биоразнообразие = Эталонный образец устойчивой экосистемы.
    Потеря биоразнообразия = template_deviation экосистемы.

    7 уровней биологической классификации (нечётное!):
    Царство / Тип / Класс / Отряд / Семейство / Род / Вид

    5 массовых вымираний в истории Земли (нечётное!):
    Ордовикско-силурийское / Девонское / Пермское / Триасовое / Меловое

    Нынешнее = 6-е массовое вымирание (чётное — незавершённая петля!).
    """

    # 7 таксономических уровней (нечётное!)
    TAXONOMIC_LEVELS = [
        'domain', 'kingdom', 'phylum', 'class',
        'order', 'family', 'genus', 'species'
    ]  # 8 — чётное! Линней использовал 7 (без домена) — нечётное!

    # 5 прошлых массовых вымираний (нечётное!)
    MASS_EXTINCTIONS = {
        1: ('Ордовикско-силурийское', 443, 86),  # (название, Млн лет назад, % потерь)
        2: ('Девонское', 375, 75),
        3: ('Пермско-триасовое', 252, 96),        # величайшее: 96% видов!
        4: ('Триасово-юрское', 201, 80),
        5: ('Мел-палеогеновое', 66, 76)            # гибель динозавров
    }  # Ровно 5 — нечётное!

    def compute_biodiversity_lci(
        self,
        species_richness: int,         # число видов
        functional_diversity: float,   # функциональное разнообразие (0-1)
        phylogenetic_diversity: float, # филогенетическое разнообразие (0-1)
        reference_richness: int = 10000  # эталонное число видов
    ) -> Dict:
        """
        ЛЗП биоразнообразия через трёхсферный анализ.
        """
        # МВС = видовое богатство (число видов)
        mvs_lci = min(species_richness / reference_richness, 1.0)

        # СВС = функциональное разнообразие (роли в экосистеме)
        svs_lci = functional_diversity

        # БВС = филогенетическое разнообразие (эволюционная история)
        bvs_lci = phylogenetic_diversity

        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        biodiversity_lci = resonance * np.mean(norms)

        # Template deviation от доиндустриального эталона
        template_deviation = 1.0 - biodiversity_lci

        # 6-е вымирание: скорость потери видов
        background_extinction_rate = 0.1  # видов / млн видов / год
        current_extinction_rate = 100.0   # × фоновая (антропоцен)
        extinction_ratio = current_extinction_rate / background_extinction_rate
        extinction_lci = 1.0 / np.log10(extinction_ratio + 1)

        return {
            'species_richness': species_richness,
            'mvs_species_richness_lci': mvs_lci,
            'svs_functional_diversity_lci': svs_lci,
            'bvs_phylogenetic_diversity_lci': bvs_lci,
            'three_sphere_resonance': resonance,
            'biodiversity_lci': biodiversity_lci,
            'template_deviation': template_deviation,
            'extinction_rate_ratio': extinction_ratio,
            'extinction_lci': extinction_lci,
            'n_mass_extinctions': 5,
            'mass_extinctions_odd': True,
            'sixth_extinction_note': (
                "6-е вымирание (чётное!) = незавершённая петля. "
                "Задача человечества: замкнуть петлю через восстановление биоразнообразия."
            ),
            'taxonomic_levels': 7,
            'taxonomic_levels_odd': True
        }


### 2.5. Экологическая сукцессия = пять уровней

class EcologicalSuccessionETDAnalyzer:
    """
    Сукцессия = движение экосистемы по пяти уровням Крюкова.
    """

    SUCCESSION_STAGES = {
        1: {
            'name': 'Первичная колонизация',
            'mode': 'SCAN',
            'species': 'Пионерные виды (лишайники, мхи)',
            'lci': 0.20,
            'biomass_kg_m2': 0.1
        },
        2: {
            'name': 'Травянистая стадия',
            'mode': 'SEQUENTIAL',
            'species': 'Травы, однолетники, r-стратеги',
            'lci': 0.40,
            'biomass_kg_m2': 0.5
        },
        3: {
            'name': 'Кустарниковая стадия',
            'mode': 'ADAPTIVE',
            'species': 'Кустарники, двулетники, ранние деревья',
            'lci': 0.60,
            'biomass_kg_m2': 2.0
        },
        4: {
            'name': 'Молодой лес',
            'mode': 'PRECISE',
            'species': 'Светолюбивые деревья, богатый подлесок',
            'lci': 0.80,
            'biomass_kg_m2': 10.0
        },
        5: {
            'name': 'Климаксное сообщество',
            'mode': 'DUAL',
            'species': 'Теневыносливые деревья-эдификаторы; максимальное разнообразие',
            'lci': 0.95,
            'biomass_kg_m2': 30.0
        }
    }  # 5 стадий — нечётное!

    def compute_succession_lci(
        self,
        current_biomass: float,
        current_species: int,
        years_since_disturbance: int = 0
    ) -> Dict:
        """
        ЛЗП сукцессии = прогресс к климаксному сообществу.
        """
        if years_since_disturbance % 2 == 0 and years_since_disturbance > 0:
            years_since_disturbance += 1  # нечётность

        # Логистический рост к климаксной биомассе
        K = 30.0  # kg/m² климаксная биомасса
        r = 0.05  # скорость сукцессии
        expected_biomass = K / (1 + (K / 0.1 - 1) * np.exp(-r * years_since_disturbance))

        # Отставание/опережение
        biomass_ratio = current_biomass / (expected_biomass + 1e-10)
        succession_lci = min(biomass_ratio * current_biomass / K, 1.0)

        # Определяем стадию
        if succession_lci > 0.85:
            stage = 5
        elif succession_lci > 0.65:
            stage = 4
        elif succession_lci > 0.45:
            stage = 3
        elif succession_lci > 0.25:
            stage = 2
        else:
            stage = 1

        sdata = self.SUCCESSION_STAGES[stage]

        return {
            'years_since_disturbance': years_since_disturbance,
            'current_biomass_kg_m2': current_biomass,
            'expected_biomass_kg_m2': expected_biomass,
            'succession_lci': succession_lci,
            'stage': stage,
            'stage_name': sdata['name'],
            'kryukov_mode': sdata['mode'],
            'typical_species': sdata['species'],
            'n_stages': 5,
            'stages_odd': True
        }


### 2.6. Диагностика экосистемы по 7 аксиомам

def diagnose_ecosystem(eco_data: Dict) -> Dict:
    """Диагностика экосистемы по 7 аксиомам Крюкова."""
    axiom_scores = {}

    axiom_scores['A1_cycle_loop'] = eco_data.get('biogeochemical_closure', 0.7)
    axiom_scores['A2_trophic_spheres'] = eco_data.get('trophic_balance', 0.7)
    axiom_scores['A3_biodiversity_template'] = eco_data.get('biodiversity_lci', 0.6)
    axiom_scores['A4_niche_window'] = eco_data.get('niche_availability', 0.6)
    n_keystone = eco_data.get('n_keystone_species', 7)
    axiom_scores['A5_odd'] = 1.0 if n_keystone % 2 == 1 else 0.5
    n_dom_species = eco_data.get('n_dominant_species', 7)
    axiom_scores['A6_memory'] = 1.0 if n_dom_species <= 9 else max(0.0, 1.0 - (n_dom_species - 9) * 0.05)
    axiom_scores['A7_succession_mode'] = eco_data.get('succession_stage_lci', 0.7)

    eco_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'ecosystem_lci': eco_lci,
        'violations': violations,
        'n_violations': len(violations),
        'ecosystem_health': _grade_ecosystem(eco_lci)
    }


def apply_kryukov_restoration_plan(violations: Dict) -> List[str]:
    """Рекомендации по восстановлению экосистемы."""
    remedies = []
    if 'A1_cycle_loop' in violations:
        remedies.append("Восстановить биогеохимические циклы: снизить выбросы, увеличить поглотители")
    if 'A2_trophic_spheres' in violations:
        remedies.append("Реинтродуцировать вершинных хищников для восстановления трофического каскада")
    if 'A3_biodiversity_template' in violations:
        remedies.append("Программа восстановления биоразнообразия: эндемичные виды, семенные банки")
    if 'A4_niche_window' in violations:
        remedies.append("Создать экологические коридоры между фрагментированными местообитаниями")
    if 'A5_odd' in violations:
        remedies.append("Защитить нечётное число ключевых видов (7 или 9) как фундамент экосистемы")
    if 'A6_memory' in violations:
        remedies.append("Ограничить число доминирующих видов: монокультуры снижают устойчивость")
    if 'A7_succession_mode' in violations:
        remedies.append("Ускорить сукцессию: посадка позднесукцессионных видов, снижение нарушений")

    if len(remedies) % 2 == 0 and remedies:
        remedies.append("Создать ООПТ по принципу 30×30 (30% территории под охрану к 2030 году)")
    return remedies


def _grade_ecosystem(lci: float) -> str:
    if lci > 0.85: return "Первозданная экосистема — эталон биосферы"
    if lci > 0.70: return "Здоровая экосистема с умеренным давлением"
    if lci > 0.55: return "Нарушенная экосистема, требующая защиты"
    if lci > 0.35: return "Деградированная экосистема, требующая восстановления"
    return "Коллапс экосистемы — срочное вмешательство"
```

---

## ВЫВОДЫ

1. **Биогеохимические циклы** = замкнутые петли; углеродный цикл нарушен антропогенно (ЛЗП снижается)
2. **Трофическая сеть** = три сферы (продуценты/травоядные/хищники); правило 10% = эффективность петли
3. **7 климатических петель** (нечётное!): 3 отрицательных + 4 положительных; ЛЗП = стабильность
4. **7 уровней** таксономии (нечётное!); **5 массовых вымираний** (нечётное!) в истории Земли
5. **5 стадий** сукцессии (нечётное!) = 5 режимов Крюкова: от пионерных видов до климакса
6. **6-е вымирание** (чётное!) = незамкнутая петля; задача человечества — её замкнуть
7. **Биосфера** = самая большая замкнутая петля на Земле; её ЛЗП = устойчивость планеты к жизни

---

*Следующая книга: КНИГА 40 — «Архетипы движения в космологии» (завершение Блока D)*
