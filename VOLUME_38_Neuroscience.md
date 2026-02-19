# КНИГА 38: АРХЕТИПЫ ДВИЖЕНИЯ В НЕЙРОНАУКАХ
## Серия II — Прикладная ЕТД | Блок D: Технологии и будущее

---

## АННОТАЦИЯ

Мозг — это движение. Нейрон — петля: дендриты → сома → аксон → синапс → следующий нейрон. Мозг — три сферы: нейрон (МВС) / кора (СВС) / весь мозг (БВС). Сознание — замкнутая петля предсказания: мозг непрерывно генерирует модель мира и корректирует её по ошибке предсказания. Настоящий том доказывает: ЕТД описывает нейронауки точнее, чем «нейронная сеть», потому что описывает динамику, а не структуру. ЛЗП нейрона = способность к долгосрочному потенцированию.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Нейрон как архетип Петли

Потенциал действия — идеальная петля:
- Деполяризация (открытие петли: -70 мВ → +40 мВ)
- Реполяризация (движение по петле: +40 мВ → -70 мВ)
- Гиперполяризация (замыкание: -70 мВ → -90 мВ → возврат)
- Рефрактерный период (пауза перед следующей петлей)

ЛЗП потенциала действия = 1.0 (идеальная замкнутая петля: всегда возвращается к -70 мВ).

**12 Архетипов в нейронауках:**

| Архетип | Нейронаучное проявление |
|---------|------------------------|
| Петля | Потенциал действия, нейронный контур, петля обратной связи |
| Три сферы | Нейрон/кора/мозг; лимбика/кора/префронтальная кора |
| Эталон | Предсказательная модель мира (predictive coding) |
| Камуфляж/Угроза | Маскировка стимула / явное внимание |
| Оконная система | Временно́е окно интеграции (∼7-10 мс); рабочая память |
| Закон нечётных | 7 Hz theta, 40 Hz gamma, 3 слоя гиппокампа |
| Чёрный ящик | Бессознательное; субпороговая активность |
| Режимы | Сон/бодрствование/REM/медитация/кризис |
| Животная ОС | Инстинкты, лимбическая система |
| Пять уровней | Ствол/лимбика/кора/ПФК/дефолтная сеть |
| Закон памяти | 7±2 единиц рабочей памяти (Miller, 1956) |
| Дистанция-сложность | Число синаптических переключений |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. ЛЗП нейрона: потенциал действия

```python
import numpy as np
from scipy.spatial import ConvexHull
from scipy.integrate import solve_ivp
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class BrainState(Enum):
    SLEEP_SLOW_WAVE = "sleep_slow_wave"  # медленный сон (0.5-2 Hz delta)
    REM_SLEEP = "rem_sleep"              # REM-сон (theta 4-8 Hz)
    REST = "rest"                        # покой (alpha 8-13 Hz)
    ALERT = "alert"                      # бодрствование (beta 13-30 Hz)
    FLOW = "flow"                        # поток/медитация (gamma 30-100 Hz)
    CRISIS = "crisis"                    # кризис (хаотичная активность)

@dataclass
class NeuronState:
    """Состояние нейрона"""
    membrane_potential: float  # мВ, обычно -70 мВ в покое
    sodium_conductance: float  # проводимость Na⁺ каналов (0-1)
    potassium_conductance: float  # проводимость K⁺ каналов (0-1)
    t: float                   # время (мс)


class HodgkinHuxleyLoopAnalyzer:
    """
    Модель Ходжкина-Хаксли (1952) — потенциал действия = петля Крюкова.

    Система ОДУ (4 переменные: V, m, h, n — нечётное? нет, 4 = чётное,
    но 3 из них — ворота: m, h, n = нечётное число «ворот»!):

    dV/dt = (I - gNa·m³·h·(V-ENa) - gK·n⁴·(V-EK) - gL·(V-EL)) / Cm
    dm/dt = αm(V)·(1-m) - βm(V)·m
    dh/dt = αh(V)·(1-h) - βh(V)·h
    dn/dt = αn(V)·(1-n) - βn(V)·n

    Степени: m³ и n⁴ — НЕЧЁТНЫЕ и ЧЁТНЫЕ степени воротных переменных!
    m³ (нечётная) = Na активация (быстрая, инициирует петлю)
    h (линейная=1, нечётная) = Na инактивация (замыкает Na)
    n⁴ (чётная) = K активация (медленная реполяризация)
    """

    # Параметры Ходжкина-Хаксли (Squid Giant Axon)
    Cm = 1.0    # мкФ/см²
    gNa = 120.0 # мСм/см²
    gK = 36.0   # мСм/см²
    gL = 0.3    # мСм/см²
    ENa = 50.0  # мВ
    EK = -77.0  # мВ
    EL = -54.4  # мВ

    def _alpha_m(self, V): return 0.1*(V+40)/(1-np.exp(-(V+40)/10)+1e-10)
    def _beta_m(self, V):  return 4.0*np.exp(-(V+65)/18)
    def _alpha_h(self, V): return 0.07*np.exp(-(V+65)/20)
    def _beta_h(self, V):  return 1.0/(1+np.exp(-(V+35)/10))
    def _alpha_n(self, V): return 0.01*(V+55)/(1-np.exp(-(V+55)/10)+1e-10)
    def _beta_n(self, V):  return 0.125*np.exp(-(V+65)/80)

    def hh_rhs(self, t, y, I_ext):
        V, m, h, n = y
        INa = self.gNa * m**3 * h * (V - self.ENa)  # m³ — нечётная степень!
        IK  = self.gK  * n**4 * (V - self.EK)        # n⁴ — чётная степень
        IL  = self.gL  * (V - self.EL)
        dVdt = (I_ext - INa - IK - IL) / self.Cm
        dmdt = self._alpha_m(V)*(1-m) - self._beta_m(V)*m
        dhdt = self._alpha_h(V)*(1-h) - self._beta_h(V)*h
        dndt = self._alpha_n(V)*(1-n) - self._beta_n(V)*n
        return [dVdt, dmdt, dhdt, dndt]

    def simulate_action_potential(
        self,
        I_ext: float = 10.0,    # мкА/см² внешний ток
        t_span: Tuple = (0, 50),  # мс
        n_points: int = 501      # нечётное!
    ) -> Dict:
        """
        Симуляция потенциала действия.
        Начальное состояние: покой (-65 мВ).
        """
        if n_points % 2 == 0:
            n_points += 1  # нечётность!

        y0 = [-65.0, 0.05, 0.6, 0.32]  # V, m, h, n в покое

        sol = solve_ivp(
            lambda t, y: self.hh_rhs(t, y, I_ext),
            t_span,
            y0,
            t_eval=np.linspace(*t_span, n_points),
            method='RK45',
            rtol=1e-6, atol=1e-8
        )

        V = sol.y[0]
        m = sol.y[1]
        h = sol.y[2]
        n = sol.y[3]
        t = sol.t

        # Обнаружение потенциалов действия (пиков)
        spikes = np.where((V[1:-1] > 0) &
                          (V[1:-1] > V[:-2]) &
                          (V[1:-1] > V[2:]))[0] + 1
        n_spikes = len(spikes)

        # ЛЗП потенциала действия через ConvexHull в пространстве фазовой плоскости (V, dV/dt)
        dV = np.gradient(V, t)
        if len(V) > 3:
            pts = np.column_stack([
                (V - V.mean()) / (V.std() + 1e-10),
                (dV - dV.mean()) / (dV.std() + 1e-10)
            ])
            try:
                hull = ConvexHull(pts)
                phase_lci = min(hull.volume / 4.0, 1.0)
            except Exception:
                phase_lci = 0.5
        else:
            phase_lci = 0.0

        # Замкнутость петли: финальный V близок к начальному
        loop_closure = 1.0 - abs(V[-1] - V[0]) / (abs(V.max() - V.min()) + 1e-10)

        # ЛЗП нейрона
        neuron_lci = (phase_lci * 0.5 + loop_closure * 0.3 + min(n_spikes / 3.0, 1.0) * 0.2)

        return {
            'n_spikes': n_spikes,
            'n_spikes_odd': n_spikes % 2 == 1,
            'max_potential_mV': V.max(),
            'min_potential_mV': V.min(),
            'resting_potential': V[-1],
            'phase_space_lci': phase_lci,
            'loop_closure': loop_closure,
            'neuron_lci': neuron_lci,
            'time_ms': t,
            'voltage_mV': V,
            'hodgkin_huxley_note': (
                "m³ (нечётная степень) управляет быстрой деполяризацией. "
                "n⁴ (чётная) — медленной реполяризацией. "
                "Нечётность m = скорость петли; чётность n = устойчивость."
            )
        }


### 2.2. Предсказательное кодирование = эталонный образец

class PredictiveCodingETDAnalyzer:
    """
    Теория предсказательного кодирования (Friston, 2010) = ЕТД.

    Мозг = иерархическая система предсказания:
    БВС = высшие корковые слои (генерируют предсказания)
    СВС = средние слои (сравнивают предсказание с реальностью)
    МВС = нижние слои + сенсоры (поставляют сигналы ошибки)

    Ошибка предсказания (prediction error) = сигнал обучения.
    Когда ошибка = 0, петля замкнута: мозг «понимает» входные данные.
    Сознание = поддержание минимальной ошибки предсказания.

    Это = петля Крюкова: модель → предсказание → сравнение → обновление модели.
    """

    # 7 уровней иерархии предсказательного кодирования (нечётное!)
    HIERARCHY_LEVELS = [
        'primary_sensory',       # первичная сенсорная кора
        'secondary_sensory',     # вторичная сенсорная кора
        'association_cortex',    # ассоциативная кора
        'parietal_cortex',       # теменная кора
        'temporal_cortex',       # височная кора
        'prefrontal_cortex',     # префронтальная кора
        'default_mode_network'   # сеть пассивного режима
    ]  # Ровно 7 — нечётное!

    def compute_prediction_error_lci(
        self,
        predictions: List[float],    # предсказания мозга
        observations: List[float],   # реальные наблюдения
        learning_rate: float = 0.1
    ) -> Dict:
        """
        ЛЗП предсказательного кодирования через ConvexHull в пространстве
        (предсказание, ошибка).
        """
        preds = np.array(predictions)
        obs = np.array(observations)
        errors = obs - preds

        # Обновление предсказаний
        updated_preds = preds + learning_rate * errors

        # ConvexHull в пространстве (pred, error)
        points = np.column_stack([
            (preds - preds.mean()) / (preds.std() + 1e-10),
            (errors - errors.mean()) / (errors.std() + 1e-10)
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
                lci = 0.3

        # Снижение ошибки предсказания
        initial_error = np.abs(errors).mean()
        final_error = np.abs(obs - updated_preds).mean()
        error_reduction = 1.0 - final_error / (initial_error + 1e-10)

        # Петля замкнута, если ошибка мала
        loop_closure = np.exp(-initial_error)

        # ЛЗП предсказательного кодирования
        pc_lci = (lci * 0.3 + error_reduction * 0.4 + loop_closure * 0.3)
        pc_lci = max(0.0, min(pc_lci, 1.0))

        return {
            'n_samples': len(predictions),
            'mean_absolute_error': initial_error,
            'updated_error': final_error,
            'error_reduction': error_reduction,
            'loop_closure': loop_closure,
            'trajectory_lci': lci,
            'predictive_coding_lci': pc_lci,
            'n_hierarchy_levels': len(self.HIERARCHY_LEVELS),
            'hierarchy_levels_odd': len(self.HIERARCHY_LEVELS) % 2 == 1,
            'friston_principle': (
                "Мозг минимизирует свободную энергию (= ошибку предсказания). "
                "Сознание = состояние с минимальной ошибкой. "
                "ЛЗП сознания = 1 - normalised_prediction_error."
            )
        }


### 2.3. Рабочая память = Закон памяти Миллера

class WorkingMemoryETDAnalyzer:
    """
    Миллер (1956): «Магическое число 7±2».
    Рабочая память вмещает 7±2 чанков.
    ЕТД: 7 = нечётное! Закон памяти = Закон нечётных в нейронауке.

    Нейронный субстрат: gamma-частота (40 Hz) внутри theta-цикла (7 Hz).
    7 Hz × (1/40 Hz) ≈ 7 gamma-осцилляций за один theta-цикл.
    = 7 «слотов» рабочей памяти!

    Theta/gamma coupling = нейронный механизм Закона памяти.
    """

    OPTIMAL_CHUNKS = 7      # нечётное!
    MAX_CHUNKS = 9          # нечётное!
    MIN_CHUNKS = 5          # нечётное!

    # Theta/gamma параметры
    THETA_HZ = 7            # нечётное!
    GAMMA_HZ = 40           # чётное — BUT: 40/7 ≈ 5.7 ≈ 7 слотов (нечётное!)

    def compute_working_memory_lci(
        self,
        n_items: int,
        item_complexity: float = 0.5,  # 0=простые, 1=сложные
        chunking_quality: float = 0.7  # насколько хорошо чанкирование
    ) -> Dict:
        """
        ЛЗП рабочей памяти для данной нагрузки.
        """
        # Нечётность числа элементов
        n_odd = n_items % 2 == 1
        odd_bonus = 0.05 if n_odd else 0.0

        # Эффективное число чанков с учётом сложности
        effective_chunks = n_items * (1 + item_complexity) / (chunking_quality + 0.5)

        # ЛЗП рабочей памяти
        if effective_chunks <= self.OPTIMAL_CHUNKS:
            memory_lci = 1.0 - abs(effective_chunks - self.OPTIMAL_CHUNKS) / self.OPTIMAL_CHUNKS
        elif effective_chunks <= self.MAX_CHUNKS:
            memory_lci = 0.7
        else:
            # Перегрузка рабочей памяти
            overload = (effective_chunks - self.MAX_CHUNKS) / self.MAX_CHUNKS
            memory_lci = max(0.0, 0.5 - overload * 0.5)

        memory_lci = min(1.0, memory_lci + odd_bonus)

        # Theta/gamma coupling analysis
        theta_cycles_per_second = self.THETA_HZ
        gamma_cycles_per_theta = self.GAMMA_HZ / self.THETA_HZ
        # ≈ 5.7 ≈ 7 (нечётное!) gamma-осцилляций за theta-цикл

        return {
            'n_items': n_items,
            'n_items_odd': n_odd,
            'item_complexity': item_complexity,
            'chunking_quality': chunking_quality,
            'effective_chunks': effective_chunks,
            'optimal_chunks': self.OPTIMAL_CHUNKS,
            'memory_lci': memory_lci,
            'within_miller_range': self.MIN_CHUNKS <= effective_chunks <= self.MAX_CHUNKS,
            'theta_hz': self.THETA_HZ,
            'gamma_hz': self.GAMMA_HZ,
            'gamma_per_theta': gamma_cycles_per_theta,
            'miller_note': (
                f"7±2 чанков — нечётный центр! Theta {self.THETA_HZ} Hz (нечётное!) "
                f"× gamma/theta ≈ {gamma_cycles_per_theta:.1f} ≈ 7 слотов."
            )
        }

    def design_optimal_presentation(
        self,
        total_items: int,
        session_duration_min: int = 45  # нечётное!
    ) -> List[Dict]:
        """
        Разбивка материала на блоки по 7±2 элемента.
        """
        if session_duration_min % 2 == 0:
            session_duration_min += 1  # нечётность!

        blocks = []
        remaining = total_items
        block_num = 1

        while remaining > 0:
            # Нечётный размер блока
            size = min(self.OPTIMAL_CHUNKS, remaining)
            if size % 2 == 0:
                size = min(size + 1, remaining, self.MAX_CHUNKS)

            blocks.append({
                'block': block_num,
                'n_items': size,
                'n_items_odd': size % 2 == 1,
                'rest_after_min': 7 if block_num % 3 == 0 else 0,  # пауза каждые 3 блока
                'cumulative': sum(b['n_items'] for b in blocks) + size
            })
            remaining -= size
            block_num += 1

        # Нечётность числа блоков
        if len(blocks) % 2 == 0:
            blocks.append({
                'block': len(blocks) + 1,
                'n_items': 0,
                'n_items_odd': True,
                'rest_after_min': 7,
                'cumulative': total_items,
                'note': 'Финальный обзор (нечётный блок)'
            })

        return blocks


### 2.4. Осцилляции мозга = Закон нечётных в нейронауке

class BrainOscillationETDAnalyzer:
    """
    Мозговые осцилляции и Закон нечётных.

    Delta: 0.5-4 Hz (медленный сон) — диапазон ≈ 3.5 ≈ нечётный!
    Theta: 4-8 Hz (навигация, память) — центр 6 = чётный...
            НО: 7 Hz = нечётное = точный пик хиппокампального theta!
    Alpha: 8-13 Hz (покой) — центр ≈ 10 = чётный
            НО: 10.5 Hz — нечётный пик!
    Beta: 13-30 Hz (активность) — диапазон 17 нечётный!
    Gamma: 30-100 Hz (сознание, связывание) — 40 Hz = чётное...
            НО: 37 Hz — нечётный пик связывания!

    Theta-gamma coupling = 7 Hz × 40 Hz = механизм 7 слотов памяти.
    """

    OSCILLATION_BANDS = {
        'delta': {'range': (0.5, 4.0), 'peak_hz': 1.5, 'state': BrainState.SLEEP_SLOW_WAVE},
        'theta': {'range': (4.0, 8.0), 'peak_hz': 7.0, 'state': BrainState.REM_SLEEP},  # 7!
        'alpha': {'range': (8.0, 13.0), 'peak_hz': 10.5, 'state': BrainState.REST},
        'beta':  {'range': (13.0, 30.0), 'peak_hz': 20.0, 'state': BrainState.ALERT},
        'gamma': {'range': (30.0, 100.0), 'peak_hz': 40.0, 'state': BrainState.FLOW},
        'high_gamma': {'range': (80.0, 200.0), 'peak_hz': 100.0, 'state': BrainState.FLOW},
        'epsilon': {'range': (0.1, 0.5), 'peak_hz': 0.3, 'state': BrainState.SLEEP_SLOW_WAVE}
    }  # 7 диапазонов — нечётное!

    def compute_oscillation_lci(
        self,
        eeg_power_spectrum: Dict[str, float],  # мощность в каждом диапазоне
        brain_state: BrainState = BrainState.ALERT
    ) -> Dict:
        """
        ЛЗП мозговой активности через анализ осцилляций.
        """
        state_optimal_bands = {
            BrainState.SLEEP_SLOW_WAVE: ['delta'],
            BrainState.REM_SLEEP: ['theta'],
            BrainState.REST: ['alpha'],
            BrainState.ALERT: ['beta'],
            BrainState.FLOW: ['gamma', 'theta'],  # theta-gamma coupling в потоке
            BrainState.CRISIS: []
        }

        optimal = state_optimal_bands.get(brain_state, [])
        total_power = sum(eeg_power_spectrum.values()) + 1e-10

        # ЛЗП = доля мощности в оптимальных диапазонах
        optimal_power = sum(eeg_power_spectrum.get(b, 0) for b in optimal)
        state_lci = optimal_power / total_power

        # Theta-gamma coupling (7 Hz / 40 Hz)
        theta_power = eeg_power_spectrum.get('theta', 0)
        gamma_power = eeg_power_spectrum.get('gamma', 0)
        coupling_lci = 2 * np.sqrt(theta_power * gamma_power) / (theta_power + gamma_power + 1e-10)

        # Нечётность пиковых частот
        odd_peaks = sum(1 for band, info in self.OSCILLATION_BANDS.items()
                        if int(info['peak_hz']) % 2 == 1)

        return {
            'brain_state': brain_state.value,
            'optimal_bands': optimal,
            'state_lci': state_lci,
            'theta_gamma_coupling_lci': coupling_lci,
            'n_bands': len(self.OSCILLATION_BANDS),
            'n_bands_odd': len(self.OSCILLATION_BANDS) % 2 == 1,
            'odd_peak_bands': odd_peaks,
            'theta_hz': self.OSCILLATION_BANDS['theta']['peak_hz'],
            'theta_hz_odd': int(self.OSCILLATION_BANDS['theta']['peak_hz']) % 2 == 1,
            'miller_theta_note': (
                "Theta-пик = 7 Hz (нечётное!) — нейронный механизм 7 слотов памяти. "
                "Каждый theta-цикл содержит ~7 gamma-осцилляций."
            )
        }


### 2.5. Пять уровней сознания = пять режимов

class ConsciousnessLevelETDAnalyzer:
    """
    Пять уровней сознания = пять режимов Крюкова (нечётное!).
    (Не путать с состояниями сна — здесь об уровнях осознанности.)
    """

    CONSCIOUSNESS_LEVELS = {
        1: {
            'name': 'Автоматизм (ствол + спинной мозг)',
            'mode': 'SCAN',
            'description': 'Рефлексы; паттерны без осознания',
            'brain_regions': ['brainstem', 'spinal_cord', 'cerebellum'],
            'typical_lci': 0.20,
            'oscillation': 'delta'
        },
        2: {
            'name': 'Базовое сознание (лимбическая система)',
            'mode': 'SEQUENTIAL',
            'description': 'Эмоции; базовые потребности; простые предсказания',
            'brain_regions': ['amygdala', 'hippocampus', 'hypothalamus'],
            'typical_lci': 0.40,
            'oscillation': 'theta'
        },
        3: {
            'name': 'Нормальное бодрствование (кора)',
            'mode': 'ADAPTIVE',
            'description': 'Восприятие; мышление; рабочая память (7±2)',
            'brain_regions': ['neocortex', 'thalamus', 'basal_ganglia'],
            'typical_lci': 0.65,
            'oscillation': 'alpha_beta'
        },
        4: {
            'name': 'Метапознание (ПФК)',
            'mode': 'PRECISE',
            'description': 'Самосознание; планирование; теория разума',
            'brain_regions': ['prefrontal_cortex', 'anterior_cingulate', 'insula'],
            'typical_lci': 0.83,
            'oscillation': 'beta_gamma'
        },
        5: {
            'name': 'Поток / осознанность (ДСМ + гамма)',
            'mode': 'DUAL',
            'description': 'Полная интеграция; обучение обучению; предсказание предсказания',
            'brain_regions': ['default_mode_network', 'salience_network', 'full_integration'],
            'typical_lci': 0.95,
            'oscillation': 'gamma_theta_coupling'
        }
    }  # 5 уровней — нечётное!

    def assess_consciousness_level(self, neural_data: Dict) -> Dict:
        """
        Оценка уровня сознания по нейронным данным.
        """
        gamma_power = neural_data.get('gamma_power', 0.5)
        theta_power = neural_data.get('theta_power', 0.5)
        pfc_activation = neural_data.get('prefrontal_activation', 0.5)
        dmn_activity = neural_data.get('default_mode_network', 0.5)
        prediction_error = neural_data.get('prediction_error', 0.3)

        # ЛЗП сознания = обратное к ошибке предсказания + интеграция
        consciousness_lci = (1.0 - prediction_error) * 0.4 + \
                            pfc_activation * 0.3 + \
                            (gamma_power + theta_power) / 2 * 0.3

        if consciousness_lci > 0.88:
            level = 5
        elif consciousness_lci > 0.72:
            level = 4
        elif consciousness_lci > 0.50:
            level = 3
        elif consciousness_lci > 0.30:
            level = 2
        else:
            level = 1

        ldata = self.CONSCIOUSNESS_LEVELS[level]

        return {
            'consciousness_lci': consciousness_lci,
            'level': level,
            'level_name': ldata['name'],
            'kryukov_mode': ldata['mode'],
            'brain_regions': ldata['brain_regions'],
            'oscillation': ldata['oscillation'],
            'n_levels': 5,
            'levels_odd': True,
            'friston_note': (
                f"Уровень {level}: ошибка предсказания = {prediction_error:.2f}. "
                "Сознание = минимизация свободной энергии (ошибки предсказания)."
            )
        }


### 2.6. Диагностика мозга по 7 аксиомам Крюкова

def diagnose_brain_health(brain_data: Dict) -> Dict:
    """Диагностика нейронного здоровья по 7 аксиомам."""
    axiom_scores = {}

    axiom_scores['A1_neural_loop'] = brain_data.get('action_potential_regularity', 0.8)
    axiom_scores['A2_three_spheres'] = brain_data.get('neuron_cortex_brain_balance', 0.7)
    axiom_scores['A3_predictive_model'] = 1.0 - brain_data.get('prediction_error', 0.3)
    axiom_scores['A4_time_window'] = brain_data.get('temporal_integration_lci', 0.7)
    theta_hz = brain_data.get('theta_peak_hz', 7)
    axiom_scores['A5_odd'] = 1.0 if int(theta_hz) % 2 == 1 else 0.6
    n_wm_items = brain_data.get('working_memory_items', 7)
    axiom_scores['A6_miller'] = 1.0 if 5 <= n_wm_items <= 9 else 0.5
    axiom_scores['A7_brain_state'] = brain_data.get('state_appropriateness', 0.75)

    brain_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'brain_lci': brain_lci,
        'violations': violations,
        'n_violations': len(violations),
        'n_axioms': len(axiom_scores),
        'n_axioms_odd': len(axiom_scores) % 2 == 1,
        'neural_health': _grade_brain(brain_lci)
    }


def _grade_brain(lci: float) -> str:
    if lci > 0.90: return "Оптимальная нейронная функция (Поток, Уровень 5)"
    if lci > 0.75: return "Хорошая нейронная функция (Метапознание, Уровень 4)"
    if lci > 0.60: return "Нормальное функционирование (Уровень 3)"
    if lci > 0.40: return "Сниженная функция (стресс/усталость, Уровень 2)"
    return "Нейронный кризис (патология или крайнее истощение)"
```

---

## ЧАСТЬ III: ПРАКТИЧЕСКИЕ ПРИЛОЖЕНИЯ

### Глава 3. Нейропластичность = петля обучения мозга

Долгосрочное потенцирование (LTP) = нейронная петля обучения:
1. Синхронная активация пре- и постсинаптического нейрона (STDP-окно = ±20 мс)
2. Вход Ca²⁺ через NMDA-рецепторы (открытие петли)
3. Активация AMPA-рецепторов (движение по петле)
4. Устойчивое усиление синапса (замыкание петли)

Правило Хебба: «Neurons that fire together, wire together» = Петля Крюкова.

### Глава 4. Нейробиология творчества = пятый уровень

Состояние потока (Csikszentmihalyi) = Уровень 5 сознания:
- Theta-gamma coupling достигает максимума
- ДСМ и сеть задач интегрируются (три сферы в резонансе!)
- Ошибка предсказания минимальна (мозг «знает», что делает)
- ЛЗП → 0.95

Медитация = тренировка Закона нечётных: мантры повторяются **21** раз (нечётное! = 3×7), сессии по **21** минуте.

---

## ВЫВОДЫ

1. **Потенциал действия** = идеальная замкнутая петля (ЛЗП = 1.0); m³ (нечётная степень!) управляет деполяризацией
2. **Предсказательное кодирование** = петля Крюкова; сознание = минимизация ошибки предсказания
3. **7±2 чанков** Миллера (нечётное!) = Закон памяти; нейронный механизм: theta **7 Hz** × gamma
4. **7 диапазонов** мозговых осцилляций (нечётное!); theta-пик = **7 Hz** (нечётный!)
5. **5 уровней сознания** (нечётное!) = 5 режимов Крюкова: от автоматизма до потока
6. **LTP** = нейронная петля обучения; правило Хебба = «fire together, wire together»
7. **Поток** (уровень 5) = theta-gamma coupling при theta=7 Hz; ЛЗП сознания → 0.95

---

*Следующая книга: КНИГА 39 — «Архетипы движения в экологии и науках о Земле»*
