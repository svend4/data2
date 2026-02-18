# КНИГА 44: ЕТД В МЕДИЦИНЕ И ФИЗИОЛОГИИ
## Серия III — Синтез и будущее ЕТД | Прикладные задачи

---

## АННОТАЦИЯ

Организм — это система замкнутых петель. Сердечный цикл, дыхание, гомеостаз, иммунный ответ — все петли. Здоровье = высокий ЛЗП всех физиологических циклов. Болезнь = разорванная или дисритмичная петля. Диагноз = измерение ЛЗП. Лечение = восстановление ЛЗП. Настоящий том применяет математический аппарат Книги 41–43 к медицине: доказывается, что ЕТД даёт единый язык для физиологии, патологии и терапии. Ключевой инсайт: нечётные числа в физиологии (7 шейных позвонков, 5 пальцев, 3 фазы дыхания) — не случайность, а следствие Теоремы Крюкова.

---

## ЧАСТЬ I: ФИЗИОЛОГИЧЕСКИЕ ПЕТЛИ

### Глава 1. Сердечный цикл как идеальная петля

Цикл ЭКГ: P-QRS-T = три сферы сердечного цикла:
- **P-волна** (МВС): деполяризация предсердий — начало петли
- **QRS-комплекс** (СВС): деполяризация желудочков — основное движение
- **T-волна** (БВС): реполяризация — замыкание петли

Нормальный ритм: **60–100 уд/мин** — нечётный диапазон если считать в долях минуты. Оптимум: **70 уд/мин** (нечётное!), **RR-интервал = 857 мс**.

ЛЗП сердечного цикла ≈ 1.0: идеальная замкнутая петля.

**12 Архетипов в медицине:**

| Архетип | Медицинское проявление |
|---------|----------------------|
| Петля | Сердечный цикл, дыхание, гомеостаз |
| Три сферы | Клетка/орган/организм; тело/разум/социум |
| Эталон | Норма (reference range), эталонный показатель |
| Камуфляж/Угроза | Скрытая патология / острый симптом |
| Оконная система | Терапевтическое окно, золотой час, критический период |
| Закон нечётных | 7 шейных позвонков, 5 долей лёгкого, 3 фазы дыхания |
| Чёрный ящик | Бессознательные регуляции, аутоиммунный механизм |
| Режимы | Анаболизм/катаболизм/гомеостаз/воспаление/апоптоз |
| Животная ОС | Иннатный иммунитет, рефлексы |
| Пять уровней | Молекула/клетка/орган/система/организм |
| Закон памяти | 7±2 систем органов в диагнозе |
| Дистанция-сложность | Число шагов от молекулы до симптома |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. ЛЗП сердечного цикла: ЭКГ-анализ

```python
import numpy as np
from scipy.spatial import ConvexHull
from scipy.signal import find_peaks, butter, filtfilt
from scipy.integrate import solve_ivp
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class CardiacRhythm(Enum):
    NORMAL_SINUS = "normal_sinus"
    TACHYCARDIA = "tachycardia"
    BRADYCARDIA = "bradycardia"
    ATRIAL_FIBRILLATION = "atrial_fibrillation"
    VENTRICULAR_FIBRILLATION = "ventricular_fibrillation"
    HEART_BLOCK = "heart_block"

@dataclass
class ECGCycle:
    """Один сердечный цикл по данным ЭКГ"""
    rr_interval_ms: float      # RR-интервал (мс)
    p_duration_ms: float       # длительность P-волны
    qrs_duration_ms: float     # длительность QRS
    qt_interval_ms: float      # QT-интервал
    p_amplitude_mV: float      # амплитуда P-волны
    r_amplitude_mV: float      # амплитуда R-зубца
    t_amplitude_mV: float      # амплитуда T-волны


class ECGLoopAnalyzer:
    """
    Анализ ЭКГ через архетип Петли.
    Нормальный сердечный цикл = идеальная замкнутая петля.
    Аритмии = нарушение замкнутости (ЛЗП < 1).
    """

    # 7 нормативных параметров ЭКГ (нечётное!)
    NORMAL_RANGES = {
        'rr_interval_ms':    (600, 1000),   # 60–100 уд/мин
        'p_duration_ms':     (80,  120),
        'qrs_duration_ms':   (70,  110),
        'qt_interval_ms':    (350, 440),
        'p_amplitude_mV':    (0.1, 0.3),
        'r_amplitude_mV':    (0.5, 2.0),
        't_amplitude_mV':    (0.1, 0.5)
    }  # Ровно 7 — нечётное!

    def compute_ecg_cycle_lci(self, cycle: ECGCycle) -> Dict:
        """
        ЛЗП одного сердечного цикла как отклонение от эталона (А3).
        """
        deviations = {}
        for param, (lo, hi) in self.NORMAL_RANGES.items():
            value = getattr(cycle, param)
            center = (lo + hi) / 2
            half_range = (hi - lo) / 2
            normalized_dev = abs(value - center) / (half_range + 1e-12)
            deviations[param] = min(normalized_dev, 1.0)

        mean_deviation = np.mean(list(deviations.values()))
        cycle_lci = 1.0 - mean_deviation

        # Трёхсферный анализ: P(МВС)/QRS(СВС)/T(БВС)
        p_score = 1.0 - deviations['p_amplitude_mV']
        qrs_score = 1.0 - deviations['qrs_duration_ms']
        t_score = 1.0 - deviations['t_amplitude_mV']

        norms = np.array([p_score, qrs_score, t_score])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            three_sphere_resonance = 1.0 - imbalance
        else:
            three_sphere_resonance = 0.0

        # Определяем ритм
        bpm = 60000 / (cycle.rr_interval_ms + 1e-12)
        if cycle.qrs_duration_ms > 200:
            rhythm = CardiacRhythm.HEART_BLOCK
        elif bpm > 100:
            rhythm = CardiacRhythm.TACHYCARDIA
        elif bpm < 60:
            rhythm = CardiacRhythm.BRADYCARDIA
        else:
            rhythm = CardiacRhythm.NORMAL_SINUS

        return {
            'cycle_lci': cycle_lci,
            'three_sphere_resonance': three_sphere_resonance,
            'p_mvs_lci': p_score,
            'qrs_svs_lci': qrs_score,
            't_bvs_lci': t_score,
            'mean_deviation': mean_deviation,
            'deviations': deviations,
            'bpm': bpm,
            'rhythm': rhythm.value,
            'n_parameters': 7,
            'parameters_odd': True,
            'cardiac_health': self._grade_cardiac(cycle_lci)
        }

    def compute_hrv_lci(
        self,
        rr_intervals_ms: List[float],
        n_bins: int = 7   # нечётное!
    ) -> Dict:
        """
        ЛЗП вариабельности сердечного ритма (ВСР) через ConvexHull Пуанкаре-плота.

        Пуанкаре-плот: точки (RR_n, RR_{n+1}).
        Форма эллипса отражает баланс симпатики/парасимпатики.
        ЛЗП = площадь эллипса / площадь ограничивающего прямоугольника.
        """
        rr = np.array(rr_intervals_ms)
        if len(rr) < 5:
            return {'hrv_lci': 0.0, 'reason': 'Недостаточно RR-интервалов'}

        # Пуанкаре-плот
        x = rr[:-1]   # RR_n
        y = rr[1:]    # RR_{n+1}

        points = np.column_stack([x, y])

        hrv_lci = 0.0
        if len(points) > 2:
            try:
                hull = ConvexHull(points)
                area = hull.volume
                bbox = ((x.max() - x.min()) * (y.max() - y.min()))
                hrv_lci = min(area / (bbox + 1e-12), 1.0)
            except Exception:
                hrv_lci = 0.3

        # Стандартные HRV-метрики
        sdnn = rr.std()         # общая ВСР
        rmssd = np.sqrt(np.mean(np.diff(rr)**2))  # ВСР высокочастотная

        # Нормы: SDNN > 50 мс = здорово, < 20 мс = плохо
        sdnn_lci = min(sdnn / 50.0, 1.0)
        rmssd_lci = min(rmssd / 30.0, 1.0)

        # Нечётное число бинов для гистограммы
        if n_bins % 2 == 0: n_bins += 1

        return {
            'hrv_lci': hrv_lci,
            'sdnn_ms': sdnn,
            'rmssd_ms': rmssd,
            'sdnn_lci': sdnn_lci,
            'rmssd_lci': rmssd_lci,
            'combined_hrv_lci': (hrv_lci + sdnn_lci + rmssd_lci) / 3,
            'n_rr_intervals': len(rr),
            'n_bins_poincare': n_bins,
            'n_bins_odd': n_bins % 2 == 1,
            'autonomic_balance': (
                'Хороший баланс СНС/ПНС' if hrv_lci > 0.5
                else 'Дисбаланс ВНС'
            )
        }

    def _grade_cardiac(self, lci: float) -> str:
        if lci > 0.90: return "Отличное здоровье сердца (Уровень 5)"
        if lci > 0.75: return "Хорошее здоровье сердца (Уровень 4)"
        if lci > 0.55: return "Умеренные отклонения (Уровень 3)"
        if lci > 0.35: return "Клинически значимые отклонения (Уровень 2)"
        return "Критическое состояние (Уровень 1)"


### 2.2. Дыхательный цикл = три сферы + нечётные

class RespiratoryLoopAnalyzer:
    """
    Дыхательный цикл = трёхфазная петля:
    МВС = вдох (инспирация, активная фаза)
    СВС = пауза (аэрогематозный газообмен)
    БВС = выдох (экспирация, пассивная фаза)

    Нормальный ритм: 12–20 дыхательных движений/мин (нечётный диапазон средины = 16? нет)
    Оптимум: 15 дыхательных движений/мин (нечётное!).
    Соотношение вдох/выдох = 1:2 (нечётные доли в простой дроби: 1 и 2 → но 1 нечётное!)
    Фаза вдоха: 1–1.5 сек (нечётная кратность: × 1)
    Фаза выдоха: 2–3 сек (нечётная кратность: × 2-3)
    Пауза: 0.5–1 сек
    """

    # 7 параметров дыхания (нечётное!)
    NORMAL_BREATH_PARAMS = {
        'rate_per_min':      (12, 20),    # ЧД
        'tidal_volume_mL':   (400, 600),  # дыхательный объём
        'insp_time_s':       (1.0, 1.5),  # время вдоха
        'exp_time_s':        (2.0, 3.0),  # время выдоха
        'pause_s':           (0.5, 1.0),  # пауза
        'SpO2_pct':          (95, 100),   # сатурация
        'EtCO2_mmHg':        (35, 45)     # конечный CO₂
    }  # Ровно 7 — нечётное!

    def compute_breath_lci(
        self,
        breath_data: Dict[str, float],
        meditation_mode: bool = False
    ) -> Dict:
        """
        ЛЗП дыхательного цикла.
        В медитации: замедление до 5-7 дых/мин (нечётные!) → ЛЗП возрастает.
        """
        deviations = {}
        for param, (lo, hi) in self.NORMAL_BREATH_PARAMS.items():
            value = breath_data.get(param, (lo + hi) / 2)
            center = (lo + hi) / 2
            half_range = (hi - lo) / 2

            if meditation_mode and param == 'rate_per_min':
                # В медитации норма ниже: 5-7 дых/мин
                center = 6  # нечётный центр!
                half_range = 1.5

            dev = abs(value - center) / (half_range + 1e-12)
            deviations[param] = min(dev, 1.0)

        mean_dev = np.mean(list(deviations.values()))
        breath_lci = 1.0 - mean_dev

        # Трёхфазный резонанс
        rate = breath_data.get('rate_per_min', 15)
        T_cycle = 60.0 / (rate + 1e-12)  # сек на цикл

        insp_t = breath_data.get('insp_time_s', 1.2)
        pause_t = breath_data.get('pause_s', 0.7)
        exp_t = T_cycle - insp_t - pause_t

        norms = np.array([insp_t, pause_t, exp_t])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            # Эталон: вдох:пауза:выдох ≈ 1:0.5:2 (нормированно)
            ideal = np.array([0.333, 0.167, 0.500])
            imbalance = np.abs(fracs - ideal).sum() / 2
            phase_resonance = 1.0 - imbalance
        else:
            phase_resonance = 0.0

        # Нечётность ЧД
        rate_int = int(rate)
        rate_odd = rate_int % 2 == 1

        return {
            'breath_lci': breath_lci,
            'phase_resonance': phase_resonance,
            'insp_fraction': norms[0] / (norms.sum() + 1e-12),
            'exp_fraction': norms[2] / (norms.sum() + 1e-12),
            'deviations': deviations,
            'rate_per_min': rate,
            'rate_odd': rate_odd,
            'meditation_mode': meditation_mode,
            'n_params': 7,
            'params_odd': True,
            'respiratory_health': (
                'Оптимальное дыхание (медитация)' if meditation_mode and breath_lci > 0.7
                else 'Нормальное дыхание' if breath_lci > 0.7
                else 'Нарушение дыхания'
            )
        }


### 2.3. Иммунный ответ = петля с задержкой

class ImmuneResponseLoopAnalyzer:
    """
    Иммунный ответ = петля с задержкой (delayed feedback loop).

    Антиген (открытие петли) → иннатный иммунитет (МВС: быстрый, нечёткий)
    → адаптивный иммунитет (СВС: медленный, точный)
    → клетки памяти (БВС: долговременный, глобальный)
    → элиминация антигена + формирование памяти (замыкание петли)

    ЛЗП иммунного ответа = эффективность элиминации при минимальном аутоиммунном вреде.
    """

    # 5 стадий иммунного ответа (нечётное!)
    IMMUNE_STAGES = [
        ('pathogen_recognition', 'МВС: паттерн-распознавание TLR', 1),    # 1 день
        ('innate_response',      'МВС: воспаление, НК-клетки',     3),    # 3 дня
        ('antigen_presentation', 'СВС: дендритные клетки → Т-клетки', 5), # 5 дней
        ('adaptive_response',    'СВС: клональная экспансия Т/В',   7),   # 7 дней!
        ('memory_formation',     'БВС: клетки памяти, элиминация', 21)    # 21 день!
    ]  # Ровно 5 — нечётное! Дни: 1, 3, 5, 7, 21 — все нечётные!

    def compute_immune_lci(
        self,
        pathogen_load: float,       # 0-1, нагрузка патогена
        innate_response: float,     # 0-1, сила иннатного ответа
        adaptive_response: float,   # 0-1, сила адаптивного ответа
        autoimmune_risk: float      # 0-1, аутоиммунный риск
    ) -> Dict:
        """
        ЛЗП иммунного ответа.
        """
        # Эффективность элиминации
        elimination_lci = min(
            (innate_response + adaptive_response) / (2 * pathogen_load + 1e-12),
            1.0
        )

        # Штраф за аутоиммунитет
        autoimmune_penalty = autoimmune_risk * 0.3

        # Трёхсферный анализ
        mvs_lci = innate_response          # иннатный (МВС)
        svs_lci = adaptive_response        # адаптивный (СВС)
        bvs_lci = 1.0 - autoimmune_risk   # память без аутоиммунитета (БВС)

        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        immune_lci = (elimination_lci - autoimmune_penalty) * resonance
        immune_lci = max(0.0, min(immune_lci, 1.0))

        # Нечётные дни стадий
        stage_days = [s[2] for s in self.IMMUNE_STAGES]
        all_days_odd = all(d % 2 == 1 for d in stage_days)

        return {
            'immune_lci': immune_lci,
            'elimination_lci': elimination_lci,
            'autoimmune_penalty': autoimmune_penalty,
            'mvs_innate_lci': mvs_lci,
            'svs_adaptive_lci': svs_lci,
            'bvs_memory_lci': bvs_lci,
            'three_sphere_resonance': resonance,
            'n_stages': 5,
            'stages_odd': True,
            'stage_days': stage_days,
            'all_days_odd': all_days_odd,
            'immune_grade': self._grade_immune(immune_lci)
        }

    def _grade_immune(self, lci: float) -> str:
        if lci > 0.85: return "Оптимальный иммунитет (стерилизующий)"
        if lci > 0.65: return "Хороший иммунитет"
        if lci > 0.45: return "Сниженный иммунитет"
        if lci > 0.25: return "Иммунодефицит"
        return "Критическая иммунная недостаточность"


### 2.4. Гомеостаз = петля обратной связи по Крюкову

class HomeostasisETDAnalyzer:
    """
    Гомеостаз = отрицательная петля обратной связи:
    отклонение → рецептор → интегратор → эффектор → коррекция → новое измерение

    Примеры: терморегуляция, регуляция гликемии, осморегуляция.

    ЛЗП гомеостаза = 1 - CV (коэффициент вариации параметра).
    Здоровый гомеостаз: CV < 5% → ЛЗП > 0.95.
    """

    # 7 ключевых гомеостатических систем (нечётное!)
    HOMEOSTATIC_SYSTEMS = {
        'temperature': {'norm': 36.6, 'sd': 0.3, 'unit': '°C'},
        'blood_glucose': {'norm': 5.0, 'sd': 0.5, 'unit': 'ммоль/л'},
        'blood_pH': {'norm': 7.40, 'sd': 0.02, 'unit': 'pH'},
        'osmolality': {'norm': 290, 'sd': 5, 'unit': 'мОсм/кг'},
        'heart_rate': {'norm': 70, 'sd': 10, 'unit': 'уд/мин'},  # 70 нечётное!
        'systolic_bp': {'norm': 120, 'sd': 10, 'unit': 'мм рт.ст.'},
        'SpO2': {'norm': 98, 'sd': 1, 'unit': '%'}
    }  # Ровно 7 — нечётное!

    def compute_homeostasis_lci(
        self,
        measurements: Dict[str, List[float]]
    ) -> Dict:
        """
        ЛЗП гомеостаза по 7 системам.
        """
        system_lcis = {}

        for system, params in self.HOMEOSTATIC_SYSTEMS.items():
            values = measurements.get(system, [params['norm']])
            arr = np.array(values)

            # Отклонение от нормы
            norm = params['norm']
            sd_ref = params['sd']
            mean_val = arr.mean()
            std_val = arr.std() if len(arr) > 1 else 0.0

            # ЛЗП = 1 - (|среднее - норма| / sd_ref + std / sd_ref) / 2
            bias = abs(mean_val - norm) / (sd_ref + 1e-12)
            variability = std_val / (sd_ref + 1e-12)
            deviation_score = (bias + variability) / 2
            system_lci = max(0.0, 1.0 - deviation_score * 0.5)

            system_lcis[system] = {
                'lci': system_lci,
                'mean': mean_val,
                'std': std_val,
                'norm': norm,
                'cv_pct': std_val / (mean_val + 1e-12) * 100
            }

        # Суммарный ЛЗП гомеостаза
        overall_lci = np.mean([v['lci'] for v in system_lcis.values()])
        violations = {k: v for k, v in system_lcis.items() if v['lci'] < 0.6}

        return {
            'system_lcis': system_lcis,
            'overall_homeostasis_lci': overall_lci,
            'violations': violations,
            'n_violations': len(violations),
            'n_systems': 7,
            'systems_odd': True,
            'homeostasis_grade': self._grade_homeostasis(overall_lci)
        }

    def _grade_homeostasis(self, lci: float) -> str:
        if lci > 0.90: return "Оптимальный гомеостаз"
        if lci > 0.75: return "Стабильный гомеостаз"
        if lci > 0.55: return "Умеренный дисгомеостаз"
        if lci > 0.35: return "Выраженный дисгомеостаз"
        return "Декомпенсация — критическое состояние"


### 2.5. Терапевтическое окно = оконная система

class TherapeuticWindowETDAnalyzer:
    """
    Терапевтическое окно = Оконная система Крюкова.

    Для каждого лекарства существует окно доз:
    [MEC, MTC] = [минимальная эффективная концентрация, минимальная токсическая]

    МВС = низкие дозы (неэффективно)
    СВС = терапевтический диапазон (оптимально — в окне!)
    БВС = высокие дозы (токсично)

    ЛЗП терапии = время нахождения в терапевтическом окне (% от времени лечения).
    """

    def compute_therapeutic_window_lci(
        self,
        concentration_time_curve: np.ndarray,  # (T, 2): (время, концентрация)
        mec: float,    # минимальная эффективная концентрация
        mtc: float     # минимальная токсическая концентрация
    ) -> Dict:
        """
        ЛЗП терапии = доля времени в окне [MEC, MTC].
        """
        times = concentration_time_curve[:, 0]
        concs = concentration_time_curve[:, 1]

        in_window = (concs >= mec) & (concs < mtc)
        too_low = concs < mec
        too_high = concs >= mtc

        # Доли времени
        window_fraction = in_window.sum() / len(in_window)
        toxic_fraction = too_high.sum() / len(too_high)
        subtherapeutic_fraction = too_low.sum() / len(too_low)

        # ЛЗП терапии
        window_lci = window_fraction

        # Конц. в центре окна = оптимально
        window_center = (mec + mtc) / 2
        in_window_concs = concs[in_window]
        if len(in_window_concs) > 0:
            center_deviation = np.abs(in_window_concs - window_center).mean()
            window_width = (mtc - mec) / 2
            centering_lci = 1.0 - center_deviation / (window_width + 1e-12)
        else:
            centering_lci = 0.0

        therapeutic_lci = (window_fraction * 0.7 + centering_lci * 0.3)

        # Трёхсферный анализ
        mvs_lci = subtherapeutic_fraction   # слишком мало (МВС)
        svs_lci = window_fraction            # в окне (СВС = цель!)
        bvs_lci = 1.0 - toxic_fraction      # не токсично (БВС)

        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        # Идеал: svs=1, mvs=0, bvs=1 → три сферы несимметричны по смыслу
        # Упрощённый резонанс: svs должно доминировать
        resonance = svs_lci * (1.0 - toxic_fraction)

        return {
            'therapeutic_lci': therapeutic_lci,
            'window_fraction': window_fraction,
            'toxic_fraction': toxic_fraction,
            'subtherapeutic_fraction': subtherapeutic_fraction,
            'centering_lci': centering_lci,
            'mvs_subther_lci': mvs_lci,
            'svs_window_lci': svs_lci,
            'bvs_nontoxic_lci': bvs_lci,
            'window_resonance': resonance,
            'mec': mec,
            'mtc': mtc,
            'window_width': mtc - mec,
            'dosing_grade': self._grade_dosing(therapeutic_lci)
        }

    def _grade_dosing(self, lci: float) -> str:
        if lci > 0.85: return "Оптимальная дозировка — максимальный эффект"
        if lci > 0.65: return "Хорошая дозировка"
        if lci > 0.45: return "Субоптимальная дозировка"
        if lci > 0.25: return "Неэффективная или токсичная"
        return "Критическая ошибка дозирования"


### 2.6. Диагностика пациента по 7 аксиомам ЕТД

def diagnose_patient(patient_data: Dict) -> Dict:
    """
    Полный ЕТД-диагноз пациента по 7 аксиомам.
    """
    axiom_scores = {}

    # А1: Петля (ритмичность физиологических циклов)
    axiom_scores['A1_rhythmicity'] = patient_data.get('rhythm_regularity', 0.8)

    # А2: Три сферы (баланс: клетка/орган/организм)
    axiom_scores['A2_level_balance'] = patient_data.get('cellular_organ_organism', 0.7)

    # А3: Эталон (соответствие нормативным показателям)
    axiom_scores['A3_norm_deviation'] = patient_data.get('labs_within_norm', 0.7)

    # А4: Оконная система (своевременность терапии)
    axiom_scores['A4_therapeutic_window'] = patient_data.get('treatment_timeliness', 0.7)

    # А5: Нечётные (нечётные физиологические структуры интактны)
    axiom_scores['A5_odd_structures'] = patient_data.get('odd_structures_intact', 0.9)

    # А6: Закон памяти (≤7 основных диагнозов — коморбидность)
    n_diagnoses = patient_data.get('n_comorbidities', 3)
    axiom_scores['A6_memory'] = 1.0 if n_diagnoses <= 7 else max(0, 1 - (n_diagnoses - 7) * 0.1)

    # А7: Режим (правильный режим лечения для стадии болезни)
    axiom_scores['A7_treatment_mode'] = patient_data.get('treatment_mode_fit', 0.7)

    patient_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'patient_lci': patient_lci,
        'violations': violations,
        'n_violations': len(violations),
        'n_axioms': 7,
        'axioms_odd': True,
        'clinical_grade': _grade_patient(patient_lci),
        'priority_interventions': _recommend_interventions(violations)
    }


def _recommend_interventions(violations: Dict) -> List[str]:
    recs = []
    if 'A1_rhythmicity' in violations:
        recs.append("Восстановить ритмику: ЭКГ-мониторинг, антиаритмическая терапия")
    if 'A2_level_balance' in violations:
        recs.append("Скрининг на уровне клетки (генетика), органа (УЗИ), организма (биохимия)")
    if 'A3_norm_deviation' in violations:
        recs.append("Коррекция ключевых лабораторных отклонений")
    if 'A4_therapeutic_window' in violations:
        recs.append("Оптимизация доз препаратов по ТДМ (терапевтическому мониторингу)")
    if 'A5_odd_structures' in violations:
        recs.append("Проверить интегритет нечётных структур: 7 ШП, 5 пальцев, 3 фазы ЧД")
    if 'A6_memory' in violations:
        recs.append("Пересмотр коморбидности: объединить схожие диагнозы (≤7)")
    if 'A7_treatment_mode' in violations:
        recs.append("Переключить режим терапии: острая/хроническая/реабилитация")

    if len(recs) % 2 == 0 and recs:
        recs.append("Провести мультидисциплинарный консилиум для интегративной оценки")
    return recs


def _grade_patient(lci: float) -> str:
    if lci > 0.90: return "Отличное здоровье (ЛЗП > 0.90)"
    if lci > 0.75: return "Хорошее здоровье (компенсация)"
    if lci > 0.55: return "Субкомпенсация (наблюдение)"
    if lci > 0.35: return "Декомпенсация (активное лечение)"
    return "Критическое состояние (неотложная помощь)"
```

---

## ВЫВОДЫ

1. **Сердечный цикл** = идеальная петля (ЛЗП ≈ 1.0); **7 параметров ЭКГ** (нечётное!)
2. **ВСР** = Пуанкаре-плот → ConvexHull; SDNN > 50 мс = здоровая ВСР
3. **Дыхание** = трёхфазная петля (вдох/пауза/выдох = МВС/СВС/БВС); оптимум **15 дых/мин** (нечётное!)
4. **Иммунный ответ** = 5 стадий (нечётное!) за **1,3,5,7,21 дней** — все нечётные!
5. **Гомеостаз** = отрицательная петля; **7 систем** (нечётное!); оптимум при CV < 5%
6. **Терапевтическое окно** = оконная система; ЛЗП = доля времени в [MEC, MTC]
7. **Полный диагноз** = **7 аксиом** ЕТД; нарушение аксиомы = конкретный терапевтический приоритет

---

*Следующая книга: КНИГА 45 — «ЕТД в музыкальной композиции»*
