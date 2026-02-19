# КНИГА 18: АРХЕТИПЫ ДВИЖЕНИЯ В НЕЙРОФАРМАКОЛОГИИ

## «Петли нейромедиаторов: как мозг создаёт замкнутые контуры сигнализации»

**Серия:** «Архетипы движения» | **Том 18 из 20**
**Автор:** На основе системы Крюкова — Тотальная Боевая Система

---

## АННОТАЦИЯ

Нейрофармакология изучает, как химические вещества изменяют работу нервной системы. В этой книге мы покажем, что все фундаментальные процессы нейромедиаторной передачи — это не хаотичная биохимия, а строго структурированная система из 12 архетипов движения. Синаптическая петля (выброс → рецепция → обратный захват) — это Архетип Петли. Три уровня нейронной организации (синапс / ансамбль / сеть) — это Архетип Трёх Сфер. Нейропластичность — это Архетип Мастер-шаблона. Фармакологическое вмешательство всегда направлено на изменение одного или нескольких архетипов.

---

## ГЛАВА 1: СИНАПТИЧЕСКАЯ ПЕТЛЯ

### 1.1 Петля как фундаментальная единица нейротрансмиссии

Каждый синаптический цикл — идеальная петля:

```
Синтез медиатора → Упаковка в везикулы → Выброс в щель →
Связывание с рецептором → Биологический эффект →
Инактивация (обратный захват / деградация) → Возврат к синтезу
```

**Индекс замыкания петли (LCI) синапса:**
- LCI = 1.0: все медиаторы захватываются обратно (дофамин, норадреналин)
- LCI = 0.5: частичная инактивация (глутамат в щели)
- LCI ≈ 0.0: однократное использование (NO, эндоканнабиноиды — диффузия без захвата)

### 1.2 Математическая модель синаптической петли

```python
import numpy as np
from scipy.integrate import odeint
from scipy.spatial import ConvexHull
import torch
import torch.nn as nn
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class NeurotransmitterType(Enum):
    DOPAMINE = "dopamine"
    SEROTONIN = "serotonin"
    GABA = "gaba"
    GLUTAMATE = "glutamate"
    ACETYLCHOLINE = "acetylcholine"
    NOREPINEPHRINE = "norepinephrine"
    ENDOCANNABINOID = "endocannabinoid"

@dataclass
class SynapticParameters:
    """Параметры синаптической петли."""
    synthesis_rate: float      # k_syn: скорость синтеза медиатора
    vesicle_fill_rate: float   # k_fill: скорость заполнения везикул
    release_probability: float # p_release: вероятность квантального выброса
    reuptake_rate: float       # k_reup: скорость обратного захвата
    degradation_rate: float    # k_deg: скорость деградации в щели
    receptor_density: float    # N_R: плотность рецепторов
    receptor_affinity: float   # K_d: константа диссоциации

class SynapticLoopAnalyzer:
    """
    Анализатор синаптической петли через архетипы Крюкова.
    Основная идея: синапс = петля с тремя сферами (пре-/пост-/ретроградная).
    """

    # Параметры типичных синапсов
    SYNAPSE_PARAMS = {
        NeurotransmitterType.DOPAMINE: SynapticParameters(
            synthesis_rate=0.5, vesicle_fill_rate=2.0,
            release_probability=0.3, reuptake_rate=0.8,
            degradation_rate=0.2, receptor_density=1000,
            receptor_affinity=1e-9
        ),
        NeurotransmitterType.SEROTONIN: SynapticParameters(
            synthesis_rate=0.3, vesicle_fill_rate=1.5,
            release_probability=0.25, reuptake_rate=0.6,
            degradation_rate=0.15, receptor_density=800,
            receptor_affinity=2e-9
        ),
        NeurotransmitterType.GABA: SynapticParameters(
            synthesis_rate=1.0, vesicle_fill_rate=3.0,
            release_probability=0.4, reuptake_rate=1.2,
            degradation_rate=0.3, receptor_density=2000,
            receptor_affinity=5e-8
        ),
        NeurotransmitterType.GLUTAMATE: SynapticParameters(
            synthesis_rate=1.5, vesicle_fill_rate=4.0,
            release_probability=0.5, reuptake_rate=1.5,
            degradation_rate=0.5, receptor_density=3000,
            receptor_affinity=1e-6
        ),
    }

    def __init__(self, nt_type: NeurotransmitterType):
        self.nt_type = nt_type
        self.params = self.SYNAPSE_PARAMS.get(nt_type,
            self.SYNAPSE_PARAMS[NeurotransmitterType.DOPAMINE])

    def simulate_cycle(self, t_max: float = 50.0, n_points: int = 1000,
                       drug_reuptake_inhibition: float = 0.0,
                       drug_release_enhancement: float = 0.0) -> Dict:
        """
        Моделирование синаптического цикла (ОДУ).

        Состояния: [V] — медиатор в везикулах, [C] — в щели, [R] — занятые рецепторы.
        """
        p = self.params
        k_reup = p.reuptake_rate * (1.0 - drug_reuptake_inhibition)
        p_release = min(1.0, p.release_probability * (1.0 + drug_release_enhancement))

        def equations(state, t):
            V, C, R = state
            # Синтез → везикулы
            dV = p.synthesis_rate - p_release * V - p.vesicle_fill_rate * 0.1 * V
            # Выброс из везикул → щель, инактивация из щели
            dC = p_release * V - k_reup * C - p.degradation_rate * C
            # Связывание с рецепторами
            free_receptors = p.receptor_density - R
            dR = (C * free_receptors / p.receptor_affinity /
                  (1 + C / p.receptor_affinity)) - 0.1 * R
            return [dV, dC, dR]

        t = np.linspace(0, t_max, n_points)
        initial = [10.0, 0.1, 0.0]
        solution = odeint(equations, initial, t)

        V_traj, C_traj, R_traj = solution.T

        # LCI через фазовый портрет (V, C)
        phase_points = np.column_stack([V_traj, C_traj])
        lci = self._compute_lci(phase_points)

        # Резонанс: сбалансированность выброса и обратного захвата
        release_flux = np.mean(p_release * V_traj)
        reuptake_flux = np.mean(k_reup * C_traj)
        resonance = 1.0 - abs(release_flux - reuptake_flux) / max(release_flux, reuptake_flux, 1e-10)

        # Пиковая концентрация в щели
        peak_concentration = np.max(C_traj)

        # Время до пика
        peak_time = t[np.argmax(C_traj)]

        return {
            'lci': round(lci, 3),
            'resonance': round(resonance, 3),
            'peak_concentration': round(peak_concentration, 4),
            'peak_time': round(peak_time, 2),
            'mean_receptor_occupancy': round(np.mean(R_traj) / p.receptor_density, 3),
            'V_trajectory': V_traj,
            'C_trajectory': C_traj,
            'R_trajectory': R_traj,
            't': t,
        }

    def _compute_lci(self, points: np.ndarray) -> float:
        """LCI через ConvexHull фазового портрета."""
        if len(points) < 4:
            return 0.0
        try:
            hull = ConvexHull(points)
            hull_area = hull.volume  # В 2D volume = площадь
        except Exception:
            return 0.0

        x_range = points[:, 0].max() - points[:, 0].min()
        y_range = points[:, 1].max() - points[:, 1].min()
        bbox_area = max(x_range * y_range, 1e-10)

        return min(1.0, hull_area / bbox_area)

    def analyze_drug_effect(self, drug_params: Dict) -> Dict:
        """
        Анализ фармакологического вмешательства.
        drug_params: {reuptake_inhibition, release_enhancement, receptor_block}
        """
        baseline = self.simulate_cycle()
        drug_effect = self.simulate_cycle(
            drug_reuptake_inhibition=drug_params.get('reuptake_inhibition', 0.0),
            drug_release_enhancement=drug_params.get('release_enhancement', 0.0),
        )

        return {
            'baseline_lci': baseline['lci'],
            'drug_lci': drug_effect['lci'],
            'lci_change': round(drug_effect['lci'] - baseline['lci'], 3),
            'baseline_resonance': baseline['resonance'],
            'drug_resonance': drug_effect['resonance'],
            'resonance_change': round(drug_effect['resonance'] - baseline['resonance'], 3),
            'peak_concentration_ratio': round(
                drug_effect['peak_concentration'] / max(baseline['peak_concentration'], 1e-10), 3),
            'interpretation': self._interpret_drug_effect(baseline, drug_effect),
        }

    def _interpret_drug_effect(self, baseline: Dict, drug: Dict) -> str:
        """Интерпретация через архетипы Крюкова."""
        lci_change = drug['lci'] - baseline['lci']
        res_change = drug['resonance'] - baseline['resonance']

        if lci_change > 0.1 and res_change > 0.05:
            return "Усиление петли + восстановление резонанса (терапевтическое окно)"
        elif lci_change > 0.1 and res_change < -0.05:
            return "Усиление петли + нарушение резонанса (риск зависимости)"
        elif lci_change < -0.1:
            return "Размыкание петли (снижение нейротрансмиссии)"
        else:
            return "Умеренная модуляция (поддерживающая терапия)"


# Демонстрация
dopamine_analyzer = SynapticLoopAnalyzer(NeurotransmitterType.DOPAMINE)

# СИОЗС-подобный эффект (ингибирование обратного захвата серотонина)
ssri_effect = dopamine_analyzer.analyze_drug_effect({
    'reuptake_inhibition': 0.7,   # 70% блокада транспортёра
    'release_enhancement': 0.0,
})
print(f"SSRI-подобный эффект:")
print(f"  LCI: {ssri_effect['baseline_lci']} → {ssri_effect['drug_lci']} "
      f"(Δ={ssri_effect['lci_change']:+.3f})")
print(f"  Резонанс: {ssri_effect['baseline_resonance']} → {ssri_effect['drug_resonance']} "
      f"(Δ={ssri_effect['resonance_change']:+.3f})")
print(f"  Интерпретация: {ssri_effect['interpretation']}")
```

---

## ГЛАВА 2: ТРИ СФЕРЫ НЕЙРОННОЙ ОРГАНИЗАЦИИ

### 2.1 МВС/СВС/БВС мозга

| Сфера | Масштаб | Структуры | Временной диапазон |
|-------|---------|-----------|---------------------|
| **МВС** (микро) | Синапс → нейрон | Дендриты, шипики, аксонные бутоны | мс–с |
| **СВС** (средняя) | Ансамбль → колонка | Локальные цепи, minicolumn | с–мин |
| **БВС** (макро) | Сеть → система | Коры, лимбика, базальные ганглии | мин–часы |

### 2.2 Трёхсферный анализатор нейронных сетей мозга

```python
class BrainThreeSphereAnalyzer:
    """
    Анализатор трёх сфер нейронной организации мозга.
    МВС = синаптический уровень, СВС = ансамблевый, БВС = сетевой.
    """

    # Нейромедиаторные системы и их сферы
    NT_SPHERES = {
        'dopamine': {
            'mvs': 'D1/D2 рецепторы на шипиках дендритов',
            'svs': 'Стриатальные проекционные нейроны',
            'bvs': 'Мезолимбический / мезокортикальный пути',
            'function': 'Вознаграждение, мотивация, движение',
        },
        'serotonin': {
            'mvs': '5-HT рецепторы (14 подтипов)',
            'svs': 'Рафе-ядра → таламус',
            'bvs': 'Серотонинергическая система всего мозга',
            'function': 'Настроение, сон, аппетит',
        },
        'gaba': {
            'mvs': 'GABA-A/B рецепторы (ионотропные/метаботропные)',
            'svs': 'Интернейроны коры (PV, SST, VIP)',
            'bvs': 'Тормозные ворота (inhibitory gating)',
            'function': 'Торможение, тревога, осцилляции',
        },
        'glutamate': {
            'mvs': 'AMPA/NMDA/mGluR рецепторы',
            'svs': 'Возбудительные пирамидальные сети',
            'bvs': 'Кортикальные сети, синаптическая пластичность',
            'function': 'Возбуждение, обучение, LTP/LTD',
        },
        'acetylcholine': {
            'mvs': 'мАХР/нАХР рецепторы',
            'svs': 'Холинергические интернейроны стриатума',
            'bvs': 'Базальные ядра Мейнерта → кора',
            'function': 'Внимание, память, нейромодуляция',
        },
    }

    def compute_sphere_resonance(self, eeg_data: Dict[str, np.ndarray],
                                  sampling_rate: float = 256.0) -> Dict:
        """
        Резонанс трёх сфер по частотам ЭЭГ:
        МВС = гамма (>30 Гц), СВС = альфа/бета (8-30 Гц), БВС = дельта/тета (0.5-8 Гц).
        """
        from scipy import signal as sp_signal

        results = {}
        for channel, data in eeg_data.items():
            freqs, psd = sp_signal.welch(data, fs=sampling_rate, nperseg=256)

            # Мощность в каждой сфере
            def band_power(f_low, f_high):
                mask = (freqs >= f_low) & (freqs < f_high)
                return np.trapz(psd[mask], freqs[mask])

            mvs_power = band_power(30, 100)   # Гамма = синаптическая активность
            svs_power = band_power(8, 30)     # Альфа+Бета = ансамблевая
            bvs_power = band_power(0.5, 8)    # Дельта+Тета = сетевая

            total = mvs_power + svs_power + bvs_power + 1e-10
            mvs_frac = mvs_power / total
            svs_frac = svs_power / total
            bvs_frac = bvs_power / total

            # Резонанс = равномерность распределения (1/3 - 1/3 - 1/3)
            ideal = 1/3
            imbalance = (abs(mvs_frac - ideal) +
                         abs(svs_frac - ideal) +
                         abs(bvs_frac - ideal)) / 2
            resonance = 1.0 - imbalance

            results[channel] = {
                'mvs_power_fraction': round(mvs_frac, 3),
                'svs_power_fraction': round(svs_frac, 3),
                'bvs_power_fraction': round(bvs_frac, 3),
                'sphere_resonance': round(resonance, 3),
                'dominant_sphere': ['MVS', 'SVS', 'BVS'][
                    np.argmax([mvs_frac, svs_frac, bvs_frac])],
            }
        return results

    def detect_pathological_patterns(self, sphere_resonance: Dict) -> List[str]:
        """
        Диагностика паттернов по архетипам Крюкова.
        Доминирование одной сферы = патология.
        """
        diagnoses = []
        for channel, data in sphere_resonance.items():
            mvs = data['mvs_power_fraction']
            svs = data['svs_power_fraction']
            bvs = data['bvs_power_fraction']
            res = data['sphere_resonance']

            if mvs > 0.6:
                diagnoses.append(f"{channel}: Гиперактивность МВС "
                                 f"(эпилептиформная активность, тревога)")
            elif bvs > 0.6:
                diagnoses.append(f"{channel}: Доминирование БВС "
                                 f"(депрессия, нарушения сознания)")
            elif svs < 0.15:
                diagnoses.append(f"{channel}: Дефицит СВС "
                                 f"(нарушение исполнительных функций, ADHD)")

            if res < 0.5:
                diagnoses.append(f"{channel}: Нарушение резонанса сфер "
                                 f"(дисрегуляция нейромодуляции)")

        return diagnoses if diagnoses else ["Паттерн в норме — резонанс сфер сохранён"]
```

---

## ГЛАВА 3: НЕЙРОПЛАСТИЧНОСТЬ КАК МАСТЕР-ШАБЛОН

### 3.1 LTP/LTD — петля обучения

Долговременное потенцирование (LTP) и депрессия (LTD) — это реализация Мастер-шаблона (ОБД) в синапсах:

**ОБД нейропластичности:**
1. **Базовый паттерн** = базовый синаптический вес (AMPA-рецепторы)
2. **Отклонение** = паттерн активации (совпадение / несовпадение)
3. **Действие** = LTP (усиление) или LTD (ослабление)

**Правило Хебба**: «Нейроны, которые активируются вместе, связываются вместе» = петля ко-активации (LCI → 1.0).

```python
class NeuroplasticityAnalyzer:
    """
    Анализатор нейропластичности через архетипы Крюкова.
    Реализует правило STDP (Spike-Timing-Dependent Plasticity).
    """

    def __init__(self, tau_plus: float = 20.0, tau_minus: float = 20.0,
                 A_plus: float = 0.01, A_minus: float = 0.0105):
        """
        STDP параметры:
        tau_plus/minus: временные константы (мс)
        A_plus/minus: амплитуды LTP/LTD
        """
        self.tau_plus = tau_plus
        self.tau_minus = tau_minus
        self.A_plus = A_plus
        self.A_minus = A_minus

    def compute_stdp_weight_change(self,
                                    pre_spike_times: np.ndarray,
                                    post_spike_times: np.ndarray) -> Dict:
        """
        Вычисление изменения синаптического веса по STDP.
        Пара спайков = одна итерация петли обучения.
        """
        total_dw = 0.0
        ltp_events = 0
        ltd_events = 0

        for t_post in post_spike_times:
            for t_pre in pre_spike_times:
                dt = t_post - t_pre  # Δt > 0: пост после пре → LTP

                if dt > 0:
                    # LTP: пре предшествует пост (каузальная петля)
                    dw = self.A_plus * np.exp(-dt / self.tau_plus)
                    total_dw += dw
                    ltp_events += 1
                elif dt < 0:
                    # LTD: пост предшествует пре (антикаузальная петля)
                    dw = -self.A_minus * np.exp(dt / self.tau_minus)
                    total_dw += dw
                    ltd_events += 1

        # LCI пластичности: баланс LTP vs LTD
        if ltp_events + ltd_events > 0:
            lci_plasticity = ltp_events / (ltp_events + ltd_events)
        else:
            lci_plasticity = 0.5

        # Резонанс: оптимальный баланс LTP/LTD ≈ 1:1
        if ltd_events > 0:
            ltp_ltd_ratio = ltp_events / ltd_events
            resonance = 1.0 - abs(np.log(max(ltp_ltd_ratio, 0.01))) / 5.0
            resonance = max(0.0, min(1.0, resonance))
        else:
            resonance = 0.0  # Только LTP — дисбаланс

        return {
            'total_weight_change': round(total_dw, 6),
            'ltp_events': ltp_events,
            'ltd_events': ltd_events,
            'lci_plasticity': round(lci_plasticity, 3),
            'ltp_ltd_resonance': round(resonance, 3),
            'plasticity_state': self._classify_plasticity(total_dw, resonance),
        }

    def _classify_plasticity(self, dw: float, resonance: float) -> str:
        """Классификация состояния пластичности."""
        if dw > 0.05 and resonance > 0.7:
            return "Адаптивное обучение (LTP доминирует, резонанс высокий)"
        elif dw < -0.05 and resonance > 0.7:
            return "Адаптивное забывание (LTD доминирует, резонанс высокий)"
        elif abs(dw) > 0.05 and resonance < 0.3:
            return "Патологическая пластичность (дисбаланс LTP/LTD)"
        else:
            return "Гомеостатическая пластичность (равновесие)"

    def simulate_hebbian_assembly(self, n_neurons: int,
                                   n_stimuli: int = 100,
                                   correlation: float = 0.7) -> Dict:
        """
        Симуляция хеббианской сборки (ансамбль Хебба).
        Нейроны, активирующиеся вместе → петля с LCI → 1.0.
        """
        # Нечётное число нейронов (закон нечётности)
        if n_neurons % 2 == 0:
            n_neurons += 1

        weights = np.random.uniform(0.1, 0.3, (n_neurons, n_neurons))
        np.fill_diagonal(weights, 0)  # Нет самосвязей

        weight_history = [weights.copy()]

        for _ in range(n_stimuli):
            # Генерация коррелированных паттернов активации
            base_pattern = np.random.binomial(1, 0.3, n_neurons)
            activations = np.array([
                1 if (base_pattern[i] == 1 and np.random.random() < correlation)
                     or np.random.random() < 0.05
                else 0
                for i in range(n_neurons)
            ], dtype=float)

            # Хеббианское обновление: Δw_ij = η * x_i * x_j
            eta = 0.01
            dw = eta * np.outer(activations, activations)
            np.fill_diagonal(dw, 0)

            # Затухание (закон использования / неиспользования)
            weights = weights * 0.99 + dw

            # Нормализация (гомеостатическая пластичность)
            row_sums = weights.sum(axis=1, keepdims=True)
            row_sums = np.where(row_sums > 0, row_sums, 1)
            weights = weights / row_sums

            weight_history.append(weights.copy())

        # LCI итогового веса: структурированность матрицы
        final_weights = weight_history[-1]
        # Спектральный LCI: отношение первого к сумме всех собственных значений
        eigenvalues = np.abs(np.linalg.eigvals(final_weights))
        eigenvalues_sorted = np.sort(eigenvalues)[::-1]
        spectral_lci = eigenvalues_sorted[0] / (eigenvalues_sorted.sum() + 1e-10)

        return {
            'n_neurons': n_neurons,
            'spectral_lci': round(spectral_lci, 3),
            'weight_variance': round(np.var(final_weights), 5),
            'assembly_formed': spectral_lci > 0.5,
            'n_stimuli': n_stimuli,
        }
```

---

## ГЛАВА 4: АРХЕТИПЫ ПСИХИАТРИЧЕСКИХ РАССТРОЙСТВ

### 4.1 Расстройства как нарушения архетипов движения

| Расстройство | Нарушенный архетип | Фармакологическая коррекция |
|-------------|-------------------|---------------------------|
| Депрессия | Разомкнутая петля серотонина | СИОЗС (закрыть петлю) |
| Тревога | Гиперактивная петля (LCI>>1) | ГАМК-агонисты (снизить LCI) |
| Шизофрения | Разрыв трёх сфер | Антипсихотики (D2-блокада) |
| СДВГ | Нарушение МВС/СВС резонанса | Метилфенидат (усилить резонанс) |
| Болезнь Паркинсона | Разомкнутая петля дофамина | L-DOPA (восстановить медиатор) |
| Эпилепсия | Суперзамкнутая петля (LCI→∞) | Антиконвульсанты (разомкнуть) |
| Болезнь Альцгеймера | Деградация мастер-шаблона (LTP→0) | Ингибиторы АХЭ (поддержать ОБД) |

### 4.2 Диагностический классификатор

```python
class PsychiatricArchetypeClassifier:
    """
    Классификатор психиатрических паттернов через архетипы Крюкова.
    Вход: нейрохимические и ЭЭГ показатели.
    Выход: нарушенный архетип + рекомендации.
    """

    DISORDER_PROFILES = {
        'depression': {
            'serotonin_lci': (0.1, 0.4),      # Низкий LCI серотонина
            'dopamine_lci': (0.2, 0.5),        # Снижен дофамин
            'bvs_eeg_fraction': (0.5, 1.0),   # Доминирование медленных волн
            'ltp_ltd_ratio': (0.0, 0.5),       # LTD > LTP (синаптическое ослабление)
            'archetype_broken': 'Петля (разомкнутая серотониновая система)',
            'treatment': 'СИОЗС + психотерапия (восстановление петли)',
        },
        'anxiety': {
            'gaba_lci': (0.0, 0.3),            # Дефицит ГАМК (слабое торможение)
            'norepinephrine_lci': (0.7, 1.0), # Гиперактивность НА
            'mvs_eeg_fraction': (0.5, 1.0),   # Гамма-гиперактивность
            'archetype_broken': 'Петля (гиперзамкнутая НА-система, слабая ГАМК-петля)',
            'treatment': 'Бензодиазепины / ГАМК-агонисты (нормализация петли)',
        },
        'schizophrenia': {
            'dopamine_lci': (0.7, 1.0),        # Гиперактивность дофамина
            'sphere_resonance': (0.0, 0.4),    # Нарушение резонанса сфер
            'archetype_broken': 'Три сферы (разрыв МВС-СВС-БВС интеграции)',
            'treatment': 'Антипсихотики D2-блокада (восстановление резонанса)',
        },
        'adhd': {
            'dopamine_lci': (0.1, 0.4),        # Низкий дофамин в PFC
            'norepinephrine_lci': (0.1, 0.4), # Низкий НА в PFC
            'svs_eeg_fraction': (0.0, 0.2),   # Дефицит бета-ритма
            'archetype_broken': 'Резонанс МВС/СВС (нарушение исполнительного контроля)',
            'treatment': 'Метилфенидат / амфетамин (усиление DA/НА резонанса)',
        },
        'parkinson': {
            'dopamine_lci': (0.0, 0.2),        # Критически низкий дофамин
            'motor_loop_lci': (0.0, 0.3),     # Разомкнута моторная петля
            'bvs_eeg_fraction': (0.5, 1.0),   # Медленные волны в моторной коре
            'archetype_broken': 'Петля (разомкнутая нигростриатная дофаминовая петля)',
            'treatment': 'L-DOPA + ингибиторы МАО (восстановление медиатора в петле)',
        },
    }

    def classify(self, biomarkers: Dict) -> List[Dict]:
        """
        Классификация расстройства по биомаркерам.
        Биомаркеры: {nt_lci, sphere_resonance, eeg_fractions, ltp_ltd_ratio}.
        """
        matches = []

        for disorder, profile in self.DISORDER_PROFILES.items():
            score = 0
            total_criteria = 0

            for criterion, (low, high) in profile.items():
                if criterion in ('archetype_broken', 'treatment'):
                    continue
                total_criteria += 1
                value = biomarkers.get(criterion)
                if value is not None and low <= value <= high:
                    score += 1

            if total_criteria > 0:
                match_score = score / total_criteria
                if match_score >= 0.5:  # Совпадение ≥ 50% критериев
                    matches.append({
                        'disorder': disorder,
                        'match_score': round(match_score, 3),
                        'archetype_broken': profile['archetype_broken'],
                        'treatment': profile['treatment'],
                    })

        # Сортировка по степени совпадения
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches


# Пример использования
classifier = PsychiatricArchetypeClassifier()
patient_biomarkers = {
    'serotonin_lci': 0.25,
    'dopamine_lci': 0.35,
    'bvs_eeg_fraction': 0.65,
    'ltp_ltd_ratio': 0.4,
    'sphere_resonance': 0.55,
}
diagnoses = classifier.classify(patient_biomarkers)
for d in diagnoses:
    print(f"{d['disorder']}: совпадение {d['match_score']:.0%}")
    print(f"  Нарушен архетип: {d['archetype_broken']}")
    print(f"  Лечение: {d['treatment']}\n")
```

---

## ГЛАВА 5: ФАРМАКОДИНАМИКА КАК АРХЕТИП МАСКИРОВКИ/УГРОЗЫ

### 5.1 Доза-ответ как петля с камуфляжем

Кривая доза-ответ (J-кривая, U-образная) — это проявление Архетипа Камуфляж/Угроза:

- **Малые дозы** = камуфляж (слабый сигнал, рецептор не различает)
- **Средние дозы** = оптимальный сигнал (резонанс)
- **Высокие дозы** = угроза (токсичность, десенситизация)

```python
class PharmacodynamicsAnalyzer:
    """
    Анализ фармакодинамики через архетипы Крюкова.
    Кривая доза-ответ = петля с зонами камуфляжа и угрозы.
    """

    def compute_dose_response_archetype(self,
                                         doses: np.ndarray,
                                         responses: np.ndarray) -> Dict:
        """
        Анализ кривой доза-ответ.
        Выявление зон: камуфляж / терапевтическое окно / угроза.
        """
        # Нормализация
        doses_norm = doses / doses.max()
        responses_norm = responses / max(responses.max(), 1e-10)

        # Поиск порогов
        threshold_low_idx = np.argmax(responses_norm > 0.1)   # Порог камуфляжа
        threshold_high_idx = np.argmax(responses_norm > 0.9)  # Порог насыщения
        toxic_idx = np.argmax(responses_norm < responses_norm[threshold_high_idx] * 0.7
                              if threshold_high_idx < len(responses_norm) - 1
                              else np.zeros_like(responses_norm, dtype=bool))

        ec50_idx = np.argmin(np.abs(responses_norm - 0.5))
        ec50 = doses[ec50_idx]

        # Терапевтический индекс (TD50/ED50)
        therapeutic_index = doses[-1] / ec50 if ec50 > 0 else float('inf')

        # LCI кривой доза-ответ (через фазовый портрет)
        phase_points = np.column_stack([doses_norm, responses_norm])
        lci = self._compute_lci_curve(phase_points)

        # Зоны архетипа Камуфляж/Угроза
        zones = {
            'camouflage_zone': (doses[0], doses[min(threshold_low_idx, len(doses)-1)]),
            'therapeutic_window': (doses[min(threshold_low_idx, len(doses)-1)],
                                    doses[min(threshold_high_idx, len(doses)-1)]),
            'threat_zone': (doses[min(threshold_high_idx, len(doses)-1)], doses[-1]),
        }

        return {
            'ec50': round(ec50, 4),
            'therapeutic_index': round(therapeutic_index, 2),
            'curve_lci': round(lci, 3),
            'zones': zones,
            'receptor_occupancy_at_ec50': 0.5,
            'archetype_interpretation': self._interpret_curve(therapeutic_index, lci),
        }

    def _compute_lci_curve(self, points: np.ndarray) -> float:
        """LCI параметрической кривой."""
        if len(points) < 4:
            return 0.0
        try:
            hull = ConvexHull(points)
            hull_area = hull.volume
            x_range = points[:, 0].max() - points[:, 0].min()
            y_range = points[:, 1].max() - points[:, 1].min()
            bbox_area = max(x_range * y_range, 1e-10)
            return min(1.0, hull_area / bbox_area)
        except Exception:
            return 0.0

    def _interpret_curve(self, ti: float, lci: float) -> str:
        if ti > 10 and lci > 0.6:
            return "Широкое терапевтическое окно, высокая замкнутость петли — безопасный препарат"
        elif ti < 3:
            return "Узкое терапевтическое окно — зоны камуфляжа и угрозы близко"
        elif lci < 0.3:
            return "Линейная кривая — предсказуемый ответ, умеренный риск"
        else:
            return "Стандартный профиль безопасности"


class DrugInteractionLoopAnalyzer:
    """
    Анализ лекарственных взаимодействий как взаимодействие петель.
    Синергизм = резонанс петель. Антагонизм = деструктивная интерференция.
    """

    def analyze_combination(self, drug_a_lci: float, drug_b_lci: float,
                             shared_target_fraction: float) -> Dict:
        """
        Анализ комбинации двух препаратов.
        shared_target_fraction: доля общих мишеней (0=разные, 1=одинаковые).
        """
        # Если петли действуют на одну мишень — интерференция
        if shared_target_fraction > 0.7:
            # Синергизм: петли резонируют
            combined_lci = min(1.0, (drug_a_lci + drug_b_lci) * shared_target_fraction)
            interaction_type = "Синергизм (резонанс петель)"
            safety_flag = combined_lci > 0.85
        elif shared_target_fraction < 0.3:
            # Аддитивность: независимые петли
            combined_lci = (drug_a_lci + drug_b_lci) / 2
            interaction_type = "Аддитивность (независимые петли)"
            safety_flag = False
        else:
            # Антагонизм: разные точки приложения
            combined_lci = abs(drug_a_lci - drug_b_lci)
            interaction_type = "Антагонизм (деструктивная интерференция)"
            safety_flag = combined_lci < 0.2

        return {
            'combined_lci': round(combined_lci, 3),
            'interaction_type': interaction_type,
            'safety_warning': safety_flag,
            'recommendation': (
                "Снизить дозы при комбинации!" if safety_flag and combined_lci > 0.85
                else "Мониторинг эффективности" if safety_flag
                else "Стандартное дозирование"
            ),
        }
```

---

## ГЛАВА 6: ПЯТЬ УРОВНЕЙ МАСТЕРСТВА В НЕЙРОФАРМАКОЛОГИИ

```
УРОВЕНЬ 1 — ЭЛЕМЕНТЫ:      Знание отдельных медиаторов и рецепторов
УРОВЕНЬ 2 — СХЕМЫ:         Понимание синаптических петель и путей
УРОВЕНЬ 3 — ПОСЛЕДОВАТЕЛЬНОСТИ: Фармакокинетика и фармакодинамика во времени
УРОВЕНЬ 4 — ОБРАЗЫ:        Восприятие трёхсферной нейрохимии как единой системы
УРОВЕНЬ 5 — ДУХ:           Интуитивное создание нейропротекторных стратегий
```

### 6.1 Нейрохимический оптимизатор

```python
class NeurochemicalOptimizer:
    """
    Оптимизатор нейрохимического баланса.
    Цель: максимизировать резонанс всех нейромедиаторных петель одновременно.
    Реализует принцип: система достигает максимума при одновременном выполнении всех 7 аксиом.
    """

    INTERVENTIONS = {
        'ssri': {'serotonin_lci': +0.4, 'dopamine_lci': +0.05, 'gaba_lci': +0.1},
        'snri': {'serotonin_lci': +0.35, 'norepinephrine_lci': +0.3, 'dopamine_lci': +0.1},
        'antipsychotic': {'dopamine_lci': -0.3, 'serotonin_lci': +0.1, 'sphere_resonance': +0.2},
        'benzodiazepine': {'gaba_lci': +0.5, 'norepinephrine_lci': -0.2, 'anxiety_lci': -0.4},
        'methylphenidate': {'dopamine_lci': +0.3, 'norepinephrine_lci': +0.3, 'svs_eeg': +0.2},
        'levodopa': {'dopamine_lci': +0.6, 'motor_loop_lci': +0.5},
        'acetylcholinesterase_inhibitor': {'acetylcholine_lci': +0.4, 'ltp_rate': +0.2},
        'lithium': {'sphere_resonance': +0.15, 'gaba_lci': +0.1, 'glutamate_lci': -0.15},
        'ketamine': {'glutamate_nmda_lci': -0.3, 'glutamate_ampa_lci': +0.4, 'ltp_rate': +0.3},
    }

    def optimize_treatment(self, patient_profile: Dict,
                           target_biomarkers: Dict,
                           max_drugs: int = 3) -> List[Dict]:
        """
        Подбор оптимальной комбинации препаратов.
        Закон нечётности: max_drugs ∈ {1, 3, 5}.
        """
        if max_drugs % 2 == 0:
            max_drugs += 1  # Закон нечётности

        # Оценка каждого вмешательства
        ranked_interventions = []

        for drug, effects in self.INTERVENTIONS.items():
            # Симулируем эффект препарата
            updated_profile = dict(patient_profile)
            for biomarker, delta in effects.items():
                current = updated_profile.get(biomarker, 0.5)
                updated_profile[biomarker] = max(0.0, min(1.0, current + delta))

            # Считаем расстояние до целевых биомаркеров
            distance = sum(
                abs(updated_profile.get(bm, 0.5) - target)
                for bm, target in target_biomarkers.items()
            )

            # Резонанс: насколько препарат приближает к балансу сфер
            nt_values = [
                updated_profile.get('serotonin_lci', 0.5),
                updated_profile.get('dopamine_lci', 0.5),
                updated_profile.get('gaba_lci', 0.5),
                updated_profile.get('glutamate_lci', 0.5),
            ]
            balance = 1.0 - np.std(nt_values)

            score = balance / (distance + 0.1)

            ranked_interventions.append({
                'drug': drug,
                'score': round(score, 3),
                'balance_improvement': round(balance, 3),
                'target_distance': round(distance, 3),
            })

        ranked_interventions.sort(key=lambda x: x['score'], reverse=True)

        # Возвращаем топ-N (нечётное число)
        n = min(max_drugs, len(ranked_interventions))
        if n % 2 == 0:
            n -= 1
        n = max(1, n)

        return ranked_interventions[:n]


# Пример: оптимизация для пациента с депрессией
optimizer = NeurochemicalOptimizer()
depressed_patient = {
    'serotonin_lci': 0.2,
    'dopamine_lci': 0.3,
    'gaba_lci': 0.4,
    'sphere_resonance': 0.4,
    'ltp_ltd_ratio': 0.3,
}
target = {
    'serotonin_lci': 0.7,
    'dopamine_lci': 0.6,
    'sphere_resonance': 0.75,
}
recommendations = optimizer.optimize_treatment(depressed_patient, target, max_drugs=3)
print("Рекомендованные вмешательства:")
for i, rec in enumerate(recommendations, 1):
    print(f"  {i}. {rec['drug']}: оценка {rec['score']}, "
          f"баланс {rec['balance_improvement']}")
```

---

## ГЛАВА 7: ТЕОРЕМА КРЮКОВА В НЕЙРОФАРМАКОЛОГИИ

**Условия максимальной нейрохимической эффективности:**

1. **Петля замкнута** — все нейромедиаторные петли завершены (обратный захват работает)
2. **Три сферы резонируют** — синапс/ансамбль/сеть работают в гармонии
3. **Мастер-шаблон сохранён** — LTP/LTD баланс поддерживает пластичность
4. **Маскировка/угроза различима** — доза в терапевтическом окне
5. **Закон нечётности** — оптимальные фармакологические комбинации нечётны (1, 3, 5 препаратов)
6. **Закон памяти** — мозг удерживает ≤ 9 фармакологических воздействий одновременно
7. **Режим адаптирован** — нейромедиаторная система в режиме АДАПТИВНЫЙ

**При выполнении всех 7 условий — нейрохимический гомеостаз максимален.**

---

## ЗАКЛЮЧЕНИЕ

Нейрофармакология через призму архетипов Крюкова раскрывается как точная наука о движении химических сигналов в замкнутых контурах. Каждый синапс — это петля. Каждая нейронная сеть — это три сферы в резонансе. Каждое лекарственное вмешательство — это попытка восстановить нарушенный архетип.

Ключевые инсайты:
- **Синаптический LCI** определяет эффективность нейротрансмиссии
- **Резонанс трёх сфер** (синапс/ансамбль/сеть) = психическое здоровье
- **STDP** = механизм обновления мастер-шаблона
- **Кривая доза-ответ** = архетип Камуфляж/Угроза в действии
- **Психиатрические расстройства** = специфические нарушения архетипов

---

*Следующая книга: КНИГА 19 — «Архетипы движения в социальных сетях»*

**© Серия «Архетипы движения» | Том 18**
