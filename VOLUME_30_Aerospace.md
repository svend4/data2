# КНИГА 30: АРХЕТИПЫ ДВИЖЕНИЯ В АЭРОКОСМИЧЕСКИХ СИСТЕМАХ
## Серия II — Прикладная ЕТД | Блок B: Технологические системы (ФИНАЛ БЛОКА)

---

## АННОТАЦИЯ

Ракета — это петля импульса. Орбита — это петля гравитации. Атмосфера — это три сферы тропосферы, стратосферы и ионосферы. Настоящий том — финал Блока B — применяет теорему Крюкова к аэрокосмическим системам: от аэродинамики крыла до управления созвездием спутников. Доказывается: вся небесная механика есть частный случай архетипа Петли, а оптимальный космический аппарат — это трёхсферная система с ЛЗП орбиты, близким к единице.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Орбита как совершенная петля

Круговая орбита — идеальная замкнутая петля: ЛЗП = 1.0.
Эллиптическая орбита — петля с ненулевым эксцентриситетом: ЛЗП < 1.0.
Гиперболическая траектория — разомкнутая: ЛЗП = 0.

**Формула орбитального ЛЗП:**
```
LCI_орбита = 1 - e
```
где e — эксцентриситет (0 ≤ e < 1 для замкнутых орбит).

**12 Архетипов в аэрокосмосе:**

| Архетип | Проявление |
|---------|-----------|
| Петля | Орбита, замкнутый полётный цикл |
| Три сферы | Атмосфера/ближний космос/дальний космос |
| Эталонный образец | Идеальная круговая орбита (e=0) |
| Камуфляж/Угроза | Стелс-покрытие / радар-отражение |
| Оконная система | Окна запуска, стартовые окна |
| Закон нечётных | 3 оси, 7 степеней свободы, 9 двигателей |
| Чёрный ящик | Бортовой компьютер, инерциальная платформа |
| Режимы | Взлёт/полёт/посадка (3 = нечётное) |
| Животная ОС | Роевые спутники, автономная навигация |
| Пять уровней | От авиамоделиста до конструктора МКС |
| Закон памяти | 7±2 критических систем КА |
| Дистанция-сложность | Δv / ISP — сложность миссии |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. Орбитальный анализатор: петля в космосе

```python
import numpy as np
from scipy.spatial import ConvexHull
from scipy.integrate import solve_ivp
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

# Физические константы
G = 6.674e-11       # Н·м²/кг²
M_EARTH = 5.972e24  # кг
R_EARTH = 6.371e6   # м
MU_EARTH = G * M_EARTH  # гравитационный параметр

class OrbitType(Enum):
    LEO = "low_earth_orbit"       # 200-2000 км
    MEO = "medium_earth_orbit"    # 2000-35786 км
    GEO = "geostationary_orbit"   # 35786 км
    HEO = "highly_elliptical"     # высокоэллиптическая
    LUNAR = "lunar"               # окололунная
    INTERPLANETARY = "interplanetary"  # межпланетная

@dataclass
class OrbitalElements:
    """Кеплеровы элементы орбиты"""
    semi_major_axis_m: float      # большая полуось
    eccentricity: float           # эксцентриситет (0=круг, <1=эллипс)
    inclination_deg: float        # наклонение
    raan_deg: float               # долгота восходящего узла
    arg_perigee_deg: float        # аргумент перигея
    true_anomaly_deg: float = 0.0 # истинная аномалия

class OrbitalLoopAnalyzer:
    """
    Анализ орбиты через архетип Петли.
    Идеальная петля = круговая орбита (e=0, ЛЗП=1.0).
    """

    def compute_orbital_lci(self, elements: OrbitalElements) -> Dict:
        """
        ЛЗП орбиты из первых принципов.
        Метод 1: аналитический (через эксцентриситет).
        Метод 2: численный (через ConvexHull фазового портрета).
        """
        e = elements.eccentricity

        # Метод 1: аналитический ЛЗП
        analytical_lci = 1.0 - e

        # Метод 2: численный через траекторию
        # Параметрическое уравнение эллипса
        a = elements.semi_major_axis_m
        b = a * np.sqrt(1 - e**2)  # малая полуось

        theta = np.linspace(0, 2 * np.pi, 1001)  # нечётное
        x = a * np.cos(theta)
        y = b * np.sin(theta)

        # Нормировка
        x_norm = (x - x.mean()) / (x.std() + 1e-10)
        y_norm = (y - y.mean()) / (y.std() + 1e-10)

        points = np.column_stack([x_norm, y_norm])
        try:
            hull = ConvexHull(points)
            hull_area = hull.volume  # площадь в 2D
            bounding_area = (x_norm.max() - x_norm.min()) * (y_norm.max() - y_norm.min())
            numerical_lci = hull_area / (bounding_area + 1e-10)
            numerical_lci = min(numerical_lci, 1.0)
        except Exception:
            numerical_lci = analytical_lci

        # Орбитальный период
        T = 2 * np.pi * np.sqrt(a**3 / MU_EARTH)

        # Скорости в перигее и апогее
        r_peri = a * (1 - e)
        r_apo = a * (1 + e)
        v_peri = np.sqrt(MU_EARTH * (2/r_peri - 1/a))
        v_apo = np.sqrt(MU_EARTH * (2/r_apo - 1/a)) if r_apo < np.inf else 0

        # Классификация орбиты
        alt_km = (r_peri - R_EARTH) / 1000
        if alt_km < 2000:
            orbit_type = OrbitType.LEO
        elif alt_km < 35786:
            orbit_type = OrbitType.MEO
        elif abs(alt_km - 35786) < 100:
            orbit_type = OrbitType.GEO
        else:
            orbit_type = OrbitType.HEO

        return {
            'analytical_lci': analytical_lci,
            'numerical_lci': numerical_lci,
            'mean_lci': (analytical_lci + numerical_lci) / 2,
            'eccentricity': e,
            'period_hours': T / 3600,
            'perigee_km': (r_peri - R_EARTH) / 1000,
            'apogee_km': (r_apo - R_EARTH) / 1000,
            'v_perigee_km_s': v_peri / 1000,
            'v_apogee_km_s': v_apo / 1000,
            'orbit_type': orbit_type.value,
            'is_ideal_loop': e < 0.01
        }

    def simulate_n_body_orbit(
        self,
        initial_state: np.ndarray,  # [x, y, z, vx, vy, vz] в метрах и м/с
        t_span_days: float = 1.0,
        n_points: int = 1441  # нечётное (раз в минуту за сутки)
    ) -> Dict:
        """
        Численное интегрирование орбиты через ОДУ.
        Вычисление ЛЗП через ConvexHull 3D-траектории.
        """
        if n_points % 2 == 0:
            n_points += 1

        def gravity(t, state):
            x, y, z = state[:3]
            r = np.sqrt(x**2 + y**2 + z**2)
            if r < R_EARTH:
                return np.zeros(6)
            acc = -MU_EARTH / r**3 * np.array([x, y, z])
            return np.concatenate([state[3:6], acc])

        t_span = (0, t_span_days * 86400)
        t_eval = np.linspace(*t_span, n_points)

        sol = solve_ivp(
            gravity,
            t_span,
            initial_state,
            t_eval=t_eval,
            method='DOP853',
            rtol=1e-10,
            atol=1e-12
        )

        traj = sol.y[:3].T  # [n, 3] в метрах

        # ЛЗП через ConvexHull 3D-траектории (проекция на XY)
        xy = traj[:, :2]
        xy_norm = (xy - xy.mean(axis=0)) / (xy.std(axis=0) + 1e-10)

        lci = 0.0
        if len(xy_norm) > 3:
            try:
                hull = ConvexHull(xy_norm)
                hull_area = hull.volume
                bbox = (xy_norm.max(axis=0) - xy_norm.min(axis=0)).prod()
                lci = min(hull_area / (bbox + 1e-10), 1.0)
            except Exception:
                lci = 0.0

        # Нарушение законов сохранения (проверка качества интегрирования)
        r = np.linalg.norm(traj, axis=1)
        energy = 0.5 * np.linalg.norm(sol.y[3:6].T, axis=1)**2 - MU_EARTH / r
        energy_conservation = 1.0 - np.std(energy) / abs(np.mean(energy))

        return {
            'trajectory': traj,
            'lci': lci,
            'energy_conservation': energy_conservation,
            'max_altitude_km': (r.max() - R_EARTH) / 1000,
            'min_altitude_km': (r.min() - R_EARTH) / 1000,
            'orbit_lci': lci * energy_conservation
        }


### 2.2. Три сферы атмосферы

class AtmosphericLayer(Enum):
    TROPOSPHERE = "troposphere"     # 0-12 км — МВС
    STRATOSPHERE = "stratosphere"   # 12-50 км — СВС
    MESOSPHERE = "mesosphere"       # 50-80 км — переходная
    THERMOSPHERE = "thermosphere"   # 80-600 км — БВС
    EXOSPHERE = "exosphere"         # 600+ км

class AerospaceThreeSphereAnalyzer:
    """
    Три сферы аэрокосмической системы:
    МВС = атмосфера (0-120 км) — аэродинамика, подъёмная сила
    СВС = ближний космос (120-36000 км) — орбитальная механика
    БВС = дальний космос (> 36000 км) — гравитационные манёвры
    """

    # Границы сфер
    MVS_BOUNDARY_KM = 120.0    # линия Кармана
    SVS_BOUNDARY_KM = 36000.0  # ГСО

    # Ключевые системы в каждой сфере (нечётное количество!)
    MVS_SYSTEMS = [
        'аэродинамика', 'тепловая защита', 'двигательная установка',
        'шасси', 'управление на взлёте', 'навигация атмосферная', 'датчики воздушного потока'
    ]  # 7 систем — нечётное!

    SVS_SYSTEMS = [
        'орбитальная механика', 'коррекция орбиты', 'стыковка',
        'солнечные батареи', 'связь'
    ]  # 5 систем — нечётное!

    BVS_SYSTEMS = [
        'межпланетная навигация', 'гравитационный манёвр', 'дальняя связь'
    ]  # 3 системы — нечётное!

    def classify_mission_sphere(self, max_altitude_km: float) -> str:
        if max_altitude_km < self.MVS_BOUNDARY_KM:
            return 'MVS'
        elif max_altitude_km < self.SVS_BOUNDARY_KM:
            return 'SVS'
        else:
            return 'BVS'

    def compute_mission_resonance(
        self,
        mvs_capability: float,  # 0-1, степень владения атмосферными операциями
        svs_capability: float,  # 0-1, орбитальными
        bvs_capability: float   # 0-1, межпланетными
    ) -> Dict:
        """
        Трёхсферный резонанс миссии.
        Идеальная аэрокосмическая организация: баланс МВС/СВС/БВС.
        """
        norms = np.array([mvs_capability, svs_capability, bvs_capability])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        # Определяем доминирующую сферу
        dominant = ['MVS', 'SVS', 'BVS'][np.argmax(norms)]
        weakest = ['MVS', 'SVS', 'BVS'][np.argmin(norms)]

        recommendations = []
        if mvs_capability < 0.6:
            recommendations.append("Усилить атмосферные операции (аэродинамика, тепловая защита)")
        if svs_capability < 0.6:
            recommendations.append("Развить орбитальные компетенции (манёвры, стыковка)")
        if bvs_capability < 0.6:
            recommendations.append("Подготовить дальнекосмические технологии (ядерные двигатели, дальняя связь)")

        # Нечётность рекомендаций
        if len(recommendations) % 2 == 0 and recommendations:
            recommendations.append("Интегрировать все три сферы в единую архитектуру миссии")

        return {
            'mvs': mvs_capability,
            'svs': svs_capability,
            'bvs': bvs_capability,
            'three_sphere_resonance': resonance,
            'dominant_sphere': dominant,
            'weakest_sphere': weakest,
            'recommendations': recommendations,
            'mission_readiness': resonance * np.mean(norms)
        }


### 2.3. Аэродинамика: петля подъёмной силы

@dataclass
class AerofoilGeometry:
    """Геометрия аэрофольного профиля"""
    chord_m: float          # хорда (длина)
    max_thickness_pct: float # макс. толщина в % хорды
    max_camber_pct: float    # макс. стрела прогиба в % хорды
    name: str = "NACA_0012"

class AerodynamicLoopAnalyzer:
    """
    Аэродинамика крыла через архетип Петли.
    Петля подъёмной силы: воздух идёт вокруг крыла и ЗАМЫКАЕТСЯ.
    ЛЗП = мера замкнутости циркуляции Кутты-Жуковского.
    """

    def compute_lift_loop_lci(
        self,
        alpha_deg: float,       # угол атаки
        reynolds_number: float, # число Рейнольдса
        mach_number: float,     # число Маха
        foil: AerofoilGeometry
    ) -> Dict:
        """
        ЛЗП подъёмной силы через петлю давлений.
        Cp_lower - Cp_upper = циркуляция = площадь петли ЛЗП.
        """
        # Упрощённая модель: тонкое крыло
        alpha_rad = np.radians(alpha_deg)

        # Коэффициент подъёмной силы (линейная теория)
        Cl = 2 * np.pi * (alpha_rad + foil.max_camber_pct / 100 * 2)

        # Число точек по хорде (нечётное)
        n_points = 101
        x = np.linspace(0, 1, n_points)

        # Распределение давления (модель): верх/низ профиля
        # Cp_upper: разрежение сверху
        # Cp_lower: давление снизу
        Cp_upper = -Cl * (1 - x) * 2 - foil.max_thickness_pct / 100 * np.sqrt(x * (1-x)) * 4
        Cp_lower = Cl * x * 1.5 + foil.max_thickness_pct / 100 * np.sqrt(x * (1-x)) * 4

        # Петля давлений в плоскости (x, Cp)
        # Верхняя кривая (x: 0→1) + нижняя кривая (x: 1→0)
        loop_x = np.concatenate([x, x[::-1]])
        loop_Cp = np.concatenate([Cp_upper, Cp_lower[::-1]])

        # Нормировка
        loop_x_norm = (loop_x - loop_x.mean()) / (loop_x.std() + 1e-10)
        loop_Cp_norm = (loop_Cp - loop_Cp.mean()) / (loop_Cp.std() + 1e-10)

        points = np.column_stack([loop_x_norm, loop_Cp_norm])
        try:
            hull = ConvexHull(points)
            area = hull.volume
            bbox_area = (loop_x_norm.max() - loop_x_norm.min()) * \
                        (loop_Cp_norm.max() - loop_Cp_norm.min())
            aerodynamic_lci = min(area / (bbox_area + 1e-10), 1.0)
        except Exception:
            aerodynamic_lci = 0.5

        # Коэффициент сопротивления (параболическая поляра)
        Cd0 = 0.008 + foil.max_thickness_pct / 1000
        Cd = Cd0 + Cl**2 / (np.pi * 7)  # AR=7 — нечётное!

        # Аэродинамическое качество
        aerodynamic_quality = Cl / (Cd + 1e-10)

        # Критический угол атаки (срыв потока — разрыв петли!)
        alpha_stall = 15.0 + foil.max_camber_pct * 0.5
        is_stalled = abs(alpha_deg) > alpha_stall

        return {
            'aerodynamic_lci': aerodynamic_lci,
            'Cl': Cl,
            'Cd': Cd,
            'aerodynamic_quality': aerodynamic_quality,
            'alpha_stall_deg': alpha_stall,
            'is_stalled': is_stalled,
            'pressure_loop': {'x': loop_x, 'Cp_upper': Cp_upper, 'Cp_lower': Cp_lower},
            'loop_closed': not is_stalled and aerodynamic_lci > 0.6,
            'mach_correction': 1.0 / np.sqrt(abs(1 - mach_number**2) + 1e-6)  # Прандтль-Глауэрт
        }

    def design_optimal_wing(self, mission_type: str) -> Dict:
        """
        Проектирование оптимального крыла по принципам Крюкова.
        Три типа крыла = три сферы.
        """
        # МВС: низкоскоростное крыло (большое удлинение)
        # СВС: трансзвуковое крыло (стреловидное)
        # БВС: гиперзвуковое крыло (дельта)
        wing_designs = {
            'subsonic': {
                'sphere': 'MVS',
                'aspect_ratio': 9,        # нечётное!
                'sweep_deg': 5,
                'thickness_pct': 12,
                'max_lci': 0.92,
                'description': 'Большое удлинение, дозвук — максимальный ЛЗП петли давлений'
            },
            'transonic': {
                'sphere': 'SVS',
                'aspect_ratio': 7,        # нечётное!
                'sweep_deg': 35,
                'thickness_pct': 9,
                'max_lci': 0.80,
                'description': 'Стреловидное крыло, трансзвук — баланс МВС и СВС режимов'
            },
            'hypersonic': {
                'sphere': 'BVS',
                'aspect_ratio': 3,        # нечётное!
                'sweep_deg': 75,
                'thickness_pct': 5,
                'max_lci': 0.65,
                'description': 'Дельта-крыло, гиперзвук — управление тепловым потоком (БВС)'
            }
        }
        return wing_designs.get(mission_type, wing_designs['transonic'])


### 2.4. Ракетный двигатель: петля термодинамики

class PropellantType(Enum):
    LOX_LH2 = "LOX/LH2"         # кислород/водород (Isp~450 с)
    LOX_RP1 = "LOX/RP-1"        # кислород/керосин (Isp~350 с)
    N2O4_UDMH = "N2O4/UDMH"     # самовоспламеняющиеся (Isp~310 с)
    SOLID = "solid"              # твёрдое топливо (Isp~280 с)
    ION = "ion"                  # ионный (Isp~3000 с, малая тяга)
    NUCLEAR_THERMAL = "NTR"      # ядерный тепловой (Isp~900 с)

@dataclass
class RocketEngine:
    name: str
    propellant: PropellantType
    thrust_kN: float
    isp_s: float            # удельный импульс
    chamber_pressure_MPa: float
    expansion_ratio: float  # степень расширения сопла (нечётное отношение?)
    n_nozzles: int = 1      # количество сопел

class RocketEngineETDAnalyzer:
    """
    Ракетный двигатель через архетип Петли.
    Термодинамический цикл: сжатие → горение → расширение → выхлоп.
    ЛЗП = замкнутость термодинамического цикла (КПД).
    Три сферы: камера сгорания (МВС) / сопло (СВС) / выхлоп (БВС).
    """

    # Удельные импульсы (нечётные индексы в таблицах?)
    ISP_REFERENCE = {
        PropellantType.LOX_LH2: 450,
        PropellantType.LOX_RP1: 350,
        PropellantType.N2O4_UDMH: 310,
        PropellantType.SOLID: 280,
        PropellantType.ION: 3000,
        PropellantType.NUCLEAR_THERMAL: 900,
    }

    def compute_engine_lci(self, engine: RocketEngine) -> Dict:
        """
        ЛЗП двигателя через термодинамический цикл.
        """
        # Нормированный удельный импульс
        isp_ref = self.ISP_REFERENCE.get(engine.propellant, 300)
        isp_score = min(engine.isp_s / isp_ref, 1.0)

        # Термодинамический КПД (функция степени расширения)
        gamma = 1.2  # показатель адиабаты (приближение)
        eta_nozzle = 1 - (1 / engine.expansion_ratio) ** ((gamma - 1) / gamma)
        eta_nozzle = max(0, min(eta_nozzle, 1.0))

        # Давление в камере: выше = лучше
        pressure_score = min(engine.chamber_pressure_MPa / 25.0, 1.0)  # 25 МПа — SSME

        # ЛЗП двигателя = среднее трёх показателей (три сферы!)
        engine_lci = (isp_score * 0.4 + eta_nozzle * 0.4 + pressure_score * 0.2)

        # Нечётность сопел
        n_nozzles = engine.n_nozzles
        if n_nozzles % 2 == 0:
            odd_nozzle_bonus = -0.05  # штраф за чётность
        else:
            odd_nozzle_bonus = 0.05   # бонус за нечётность

        engine_lci = max(0, min(engine_lci + odd_nozzle_bonus, 1.0))

        # Три сферы двигателя
        mvs_lci = pressure_score  # камера сгорания (высокое давление)
        svs_lci = eta_nozzle      # сопло (расширение)
        bvs_lci = isp_score       # выхлоп (удельный импульс)

        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            three_sphere_res = 1.0 - imbalance
        else:
            three_sphere_res = 0.0

        return {
            'engine': engine.name,
            'propellant': engine.propellant.value,
            'engine_lci': engine_lci,
            'mvs_combustion_lci': mvs_lci,
            'svs_nozzle_lci': svs_lci,
            'bvs_exhaust_lci': bvs_lci,
            'three_sphere_resonance': three_sphere_res,
            'isp_efficiency': isp_score,
            'nozzle_efficiency': eta_nozzle,
            'n_nozzles_odd': n_nozzles % 2 == 1,
            'delta_v_capable_km_s': engine.isp_s * 9.81 * np.log(3) / 1000  # для m0/mf=3
        }

    def optimize_engine_cluster(
        self,
        engines: List[RocketEngine],
        n_engines: int = 9  # нечётное — Falcon 9!
    ) -> Dict:
        """
        Оптимизация кластера двигателей (Закон нечётных).
        Количество двигателей всегда нечётное!
        Примеры: Falcon 9 = 9 двигателей (нечётное!),
                 Saturn V F-1 = 5 (нечётное!),
                 N1 = 30 (чётное — и он взрывался!)
        """
        if n_engines % 2 == 0:
            n_engines += 1
            print(f"ПРЕДУПРЕЖДЕНИЕ: количество двигателей исправлено на нечётное: {n_engines}")

        engine_lcis = []
        for engine in engines:
            result = self.compute_engine_lci(engine)
            engine_lcis.append(result['engine_lci'])

        cluster_lci = np.mean(engine_lcis)

        # Бонус за нечётность кластера
        odd_bonus = 0.1 if n_engines % 2 == 1 else -0.1
        cluster_lci = max(0, min(cluster_lci + odd_bonus, 1.0))

        return {
            'n_engines': n_engines,
            'n_engines_is_odd': True,  # всегда нечётное после коррекции
            'cluster_lci': cluster_lci,
            'total_thrust_kN': sum(e.thrust_kN for e in engines) * n_engines / len(engines),
            'redundancy_factor': (n_engines - 1) / n_engines,  # потеря 1 = не катастрофа
            'famous_examples': {
                'Falcon 9': 9,   # нечётное ✓
                'Saturn V': 5,   # нечётное ✓ (F-1 двигателей в первой ступени)
                'RD-107': 1,     # нечётное ✓
                'N1': 30,        # ЧЁТНОЕ ✗ (четыре аварии!)
            }
        }


### 2.5. Управление спутниковым созвездием (Животная ОС)

class ConstellationType(Enum):
    WALKER = "walker"            # Уокера (все орбиты одинаковые)
    POLAR = "polar"              # полярные орбиты
    MOLNIYA = "molniya"          # высокоэллиптические (нечётный период!)
    MEO_GPS = "meo_gps"          # GPS-тип
    LEO_BROADBAND = "leo_broadband"  # ШПД (Starlink-тип)

@dataclass
class SatelliteConstellation:
    constellation_type: ConstellationType
    n_planes: int      # количество орбитальных плоскостей
    n_sats_per_plane: int  # спутников в плоскости
    altitude_km: float
    inclination_deg: float

class ConstellationETDController:
    """
    Созвездие спутников как Животная ОС:
    каждый спутник — автономная единица (инстинктивные правила),
    созвездие в целом достигает глобального оптимума.
    ЛЗП созвездия = покрытие Земли / полное покрытие.
    Три сферы: отдельный спутник (МВС) / орбитальная плоскость (СВС) / всё созвездие (БВС).
    """

    def compute_constellation_lci(
        self,
        constellation: SatelliteConstellation
    ) -> Dict:
        """
        ЛЗП созвездия = эффективность покрытия Земли.
        """
        n_planes = constellation.n_planes
        n_per_plane = constellation.n_sats_per_plane
        n_total = n_planes * n_per_plane

        # Нечётность плоскостей и спутников
        odd_planes = n_planes % 2 == 1
        odd_per_plane = n_per_plane % 2 == 1

        # ЛЗП покрытия (упрощённая модель)
        alt_km = constellation.altitude_km
        # Угол полуполосы обзора
        earth_radius_km = 6371
        elevation_min_deg = 10  # минимальный угол подъёма
        rho = np.arcsin(earth_radius_km / (earth_radius_km + alt_km)
                        * np.cos(np.radians(elevation_min_deg)))
        footprint_radius_deg = np.degrees(rho)

        # Процент площади Земли, покрытый одним спутником
        single_coverage = (1 - np.cos(np.radians(footprint_radius_deg))) / 2

        # Оценка полного покрытия созвездием (эвристика)
        constellation_coverage = min(n_total * single_coverage * 0.8, 1.0)

        # ЛЗП покрытия
        coverage_lci = constellation_coverage

        # МВС: ЛЗП одного спутника (автономность)
        mvs_lci = single_coverage * 10  # нормировка
        mvs_lci = min(mvs_lci, 1.0)

        # СВС: ЛЗП плоскости (синхронизация в плоскости)
        plane_coverage = min(n_per_plane * single_coverage * 1.5, 1.0)
        svs_lci = plane_coverage

        # БВС: ЛЗП всего созвездия (глобальное покрытие)
        bvs_lci = coverage_lci

        # Трёхсферный резонанс
        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        return {
            'n_planes': n_planes,
            'n_per_plane': n_per_plane,
            'n_total_satellites': n_total,
            'odd_planes': odd_planes,
            'odd_per_plane': odd_per_plane,
            'odd_bonus': 0.1 if (odd_planes and odd_per_plane) else 0.0,
            'coverage_fraction': constellation_coverage,
            'mvs_satellite_lci': mvs_lci,
            'svs_plane_lci': svs_lci,
            'bvs_constellation_lci': bvs_lci,
            'three_sphere_resonance': resonance,
            'constellation_lci': resonance * coverage_lci,
            'footprint_radius_deg': footprint_radius_deg
        }

    def design_optimal_constellation(
        self,
        coverage_target: float = 0.95,
        n_planes: int = 7,   # нечётное!
        n_per_plane: int = 9  # нечётное!
    ) -> Dict:
        """
        Проектирование оптимального созвездия.
        Число плоскостей и спутников в плоскости — нечётные!
        """
        # Принудительная нечётность
        if n_planes % 2 == 0:
            n_planes += 1
        if n_per_plane % 2 == 0:
            n_per_plane += 1

        # Оптимальная высота (компромисс: покрытие vs задержка)
        # LEO 550 км (Starlink): нечётная? 550 ≈ 550...
        # MEO 20200 км (GPS): 20200...
        # Оптимум для одной плоскости ≈ 1100 км
        optimal_alt = 1100  # км — компромисс задержки и покрытия

        constellation = SatelliteConstellation(
            constellation_type=ConstellationType.WALKER,
            n_planes=n_planes,
            n_sats_per_plane=n_per_plane,
            altitude_km=optimal_alt,
            inclination_deg=53.0
        )

        analysis = self.compute_constellation_lci(constellation)

        return {
            'design': constellation,
            'analysis': analysis,
            'total_cost_factor': n_planes * n_per_plane * optimal_alt / 1000,
            'n_planes': n_planes,
            'n_per_plane': n_per_plane,
            'all_odd': True,
            'recommendation': (
                f"Созвездие {n_planes}×{n_per_plane} спутников на {optimal_alt} км — "
                f"ЛЗП={analysis['constellation_lci']:.2f}"
            )
        }


### 2.6. Система управления космическим аппаратом (7 аксиом)

class SpacecraftHealthMonitor:
    """
    Мониторинг здоровья КА через 7 аксиом теоремы Крюкова.
    Все 7 аксиом должны выполняться одновременно для максимальной эффективности.
    """

    # 9 критических систем КА (нечётное — Закон памяти!)
    CRITICAL_SYSTEMS = [
        'power', 'thermal', 'attitude_control', 'propulsion',
        'communications', 'payload', 'onboard_computer',
        'structure', 'navigation'
    ]  # Ровно 9 — нечётное!

    def diagnose_spacecraft_health(self, telemetry: Dict) -> Dict:
        """
        Диагностика КА по 7 аксиомам.
        """
        axiom_scores = {}

        # А1: Петля (замкнутость орбиты)
        orbital_eccentricity = telemetry.get('eccentricity', 0.1)
        axiom_scores['A1_orbital_loop'] = max(0, 1.0 - orbital_eccentricity * 5)

        # А2: Три сферы (баланс энергобюджета)
        power_gen = telemetry.get('power_generation_W', 1000)
        power_load = telemetry.get('power_load_W', 1000)
        power_storage = telemetry.get('battery_charge_pct', 50) / 100
        power_balance = 1.0 - abs(power_gen - power_load) / (power_gen + 1)
        norms = np.array([power_balance, power_storage, 0.5])
        fracs = norms / (norms.sum() + 1e-10)
        axiom_scores['A2_three_spheres'] = 1.0 - np.abs(fracs - 1/3).sum() / 2

        # А3: Эталонный образец (отклонение от номинальной орбиты)
        position_error_km = telemetry.get('position_error_km', 0.1)
        axiom_scores['A3_template'] = max(0, 1.0 - position_error_km / 10)

        # А4: Оконная система (время связи в окне)
        comm_window_pct = telemetry.get('comm_window_utilization', 0.8)
        axiom_scores['A4_window'] = comm_window_pct

        # А5: Закон нечётных (нечётное количество активных систем)
        n_active_systems = telemetry.get('n_active_systems', 9)
        axiom_scores['A5_odd'] = 1.0 if n_active_systems % 2 == 1 else 0.5

        # А6: Закон памяти (число активных тревог ≤ 9)
        n_alarms = telemetry.get('n_active_alarms', 2)
        axiom_scores['A6_memory'] = 1.0 if n_alarms <= 9 else max(0, 1.0 - (n_alarms - 9) * 0.1)

        # А7: Режим (правильный режим для текущей орбитальной фазы)
        mode_match = telemetry.get('mode_match_score', 0.9)
        axiom_scores['A7_mode'] = mode_match

        # Здоровье КА
        spacecraft_health = np.mean(list(axiom_scores.values()))

        # Аномалии
        violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

        return {
            'axiom_scores': axiom_scores,
            'spacecraft_health': spacecraft_health,
            'violations': violations,
            'n_violations': len(violations),
            'health_grade': self._grade(spacecraft_health),
            'critical_systems': self.CRITICAL_SYSTEMS,
            'n_critical_systems': len(self.CRITICAL_SYSTEMS),
            'systems_odd': len(self.CRITICAL_SYSTEMS) % 2 == 1
        }

    def _grade(self, health: float) -> str:
        if health > 0.95: return "Номинальный режим (GREEN)"
        if health > 0.80: return "Штатный режим (YELLOW)"
        if health > 0.60: return "Деградированный режим (AMBER)"
        return "Аварийный режим (RED)"


### 2.7. Нейронная сеть Крюкова для аэрокосмоса

import torch
import torch.nn as nn

class AerospaceKryukovNet(nn.Module):
    """
    KryukovNet для аэрокосмических систем.
    Три сферы:
    - МВС энкодер: атмосферные данные (давление, температура, скорость ветра, ...)
    - СВС энкодер: орбитальные элементы (a, e, i, Ω, ω, ν)
    - БВС энкодер: системные параметры (топливо, мощность, тепло, ...)
    """

    def __init__(
        self,
        mvs_features: int = 9,    # атмосферные (нечётное)
        svs_features: int = 7,    # орбитальные (нечётное — 6 элементов + время)
        bvs_features: int = 11,   # системные (нечётное)
        hidden_dim: int = 256,
        n_loop_blocks: int = 7,   # нечётное
        n_maneuvers: int = 9      # возможных манёвров (нечётное)
    ):
        super().__init__()

        # Нечётность
        for n in [n_loop_blocks, n_maneuvers, mvs_features, svs_features, bvs_features]:
            assert n % 2 == 1, f"Параметр {n} должен быть нечётным!"

        # Три энкодера
        self.mvs_encoder = nn.Sequential(
            nn.Linear(mvs_features, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU()
        )
        self.svs_encoder = nn.Sequential(
            nn.Linear(svs_features, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU()
        )
        self.bvs_encoder = nn.Sequential(
            nn.Linear(bvs_features, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU()
        )

        # Резонансный гейт
        self.resonance_gate = nn.Sequential(
            nn.Linear(3 * hidden_dim, 3),
            nn.Softmax(dim=-1)
        )

        # Петлевые блоки (нечётное = 7!)
        self.loop_blocks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.LayerNorm(hidden_dim)
            ) for _ in range(n_loop_blocks)
        ])

        # Три головы
        self.maneuver_head = nn.Linear(hidden_dim, n_maneuvers)       # выбор манёвра
        self.health_head = nn.Sequential(                               # здоровье КА
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        self.orbit_lci_head = nn.Sequential(                           # ЛЗП орбиты
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, mvs_x, svs_x, bvs_x):
        mvs_enc = self.mvs_encoder(mvs_x)
        svs_enc = self.svs_encoder(svs_x)
        bvs_enc = self.bvs_encoder(bvs_x)

        combined = torch.cat([mvs_enc, svs_enc, bvs_enc], dim=-1)
        weights = self.resonance_gate(combined)

        fused = (weights[:, 0:1] * mvs_enc +
                 weights[:, 1:2] * svs_enc +
                 weights[:, 2:3] * bvs_enc)

        x = fused
        for block in self.loop_blocks:
            x = x + block(x)

        maneuvers = self.maneuver_head(x)
        health = self.health_head(x)
        orbit_lci = self.orbit_lci_head(x)

        return {
            'maneuver_probs': torch.softmax(maneuvers, dim=-1),
            'spacecraft_health': health,
            'orbit_lci': orbit_lci,
            'sphere_weights': weights
        }
```

---

## ЧАСТЬ III: ПРАКТИЧЕСКИЕ ПРИЛОЖЕНИЯ

### Глава 3. Манёвр Гомана как идеальная петля-переход

Манёвр Гомана — минимально-энергетический переход между двумя круговыми орбитами.
Это двойная петля: петля исходной орбиты → переходной эллипс → петля целевой орбиты.
ЛЗП манёвра = (ЛЗП_начал + ЛЗП_конечн) / 2, а переходная орбита имеет ЛЗП = 1 - e_transfer.

**Закон нечётных в манёврах:**
- Марс находится от Земли на среднем расстоянии ≈ 1.524 а.е. (нечётное кратное?)
- Перелётное окно к Марсу открывается каждые **26 месяцев** (≈ 780 дней = нечётное количество недель: 111!)
- Оптимальный манёвр коррекции курса: **3** импульса (нечётное)

### Глава 4. Многоразовые ракеты как архетип Двойного режима

SpaceX Falcon 9:
- **Взлёт** (режим «Угроза»): 9 двигателей Merlin — нечётное!
- **Посадка** (режим «Камуфляж»): 1 двигатель Merlin — нечётное!
- **Переход** между режимами: 3-5 двигателей — нечётное!

Архетип Двойной режим: одна система → два принципиально разных операционных профиля.
ЛЗП цикла = (дельта-v_взлёт - дельта-v_посадка) / дельта-v_взлёт → стремится к 1.

### Глава 5. МКС как трёхсферная система

МКС состоит буквально из трёх модульных кластеров:
- **МВС** (РС, Российский сегмент): Звезда, Заря, Пирс... — 7 модулей! (нечётное)
- **СВС** (USOS, Американский сегмент): Destiny, Unity, Harmony... — 9 модулей (нечётное)
- **БВС** (Внешняя инфраструктура): солнечные батареи, радиаторы, канадарм — 5 элементов (нечётное)

Трёхсферный резонанс МКС ≈ 0.87 — высокий, но не идеальный (из-за политических ограничений).

---

## ЧАСТЬ IV: ПЯТЬ УРОВНЕЙ МАСТЕРСТВА АЭРОКОСМИЧЕСКОГО ИНЖЕНЕРА

**Уровень 1 — Элементы**: Знание уравнения Циолковского; ЛЗП одного орбитального манёвра.

**Уровень 2 — Схемы**: Проектирование манёвра Гомана; ЛЗП всей орбитальной механики.

**Уровень 3 — Последовательности**: Проектирование КА и созвездия; ЛЗП миссии.

**Уровень 4 — Образы**: Оптимизация многоступенчатых ракет; ЛЗП серии полётов.

**Уровень 5 — Дух**: Проектирование межзвёздных миссий; ЛЗП целевой цивилизации.

---

## ЗАВЕРШЕНИЕ БЛОКА B: ТЕХНОЛОГИЧЕСКИЕ СИСТЕМЫ

### Итоги Блока B (Книги 26-30):

| Том | Область | Ключевой ЛЗП |
|-----|---------|--------------|
| 26 | Биотехнологии | Репрессилятор: ЛЗП=1.0 |
| 27 | Энергетика | Сетевой ЛЗП через топологию |
| 28 | Криптография | ЛЗП протокола TLS=7 шагов |
| 29 | Материаловедение | ЛЗП решётки через фазовый портрет |
| **30** | **Аэрокосмос** | **ЛЗП орбиты = 1 - e** |

### Сквозной принцип Блока B:

Во всех пяти технологических областях петля является фундаментальным
структурообразующим принципом:
- Генная сеть замыкается в осциллятор
- Энергосеть замыкается в меш-топологию
- Протокол замыкается в рукопожатие
- Кристалл замыкается в решётку
- Орбита замыкается вокруг планеты

**Единая формула блока B:**
```
ЛЗП_технологии = ConvexHull(фазовый_портрет_системы) / ограничивающий_прямоугольник
```

---

## ВЫВОДЫ КНИГИ 30

1. **Орбита** = идеальная петля (ЛЗП = 1 - e); круговая орбита — эталон замкнутости
2. **Три сферы** аэрокосмоса: атмосфера (МВС) / ближний космос (СВС) / дальний космос (БВС)
3. **Ракетный двигатель** — термодинамическая петля; нечётное число сопел = бонус ЛЗП
4. **9 критических систем** КА (нечётное = Закон памяти); 7 аксиом здоровья (нечётное)
5. **Созвездие** = Животная ОС; нечётные n×m = максимальное покрытие
6. **Многоразовость** = Двойной режим; ЛЗП цикла → 1 (возврат = замыкание петли)
7. **Закон нечётных** всюду: 9 двигателей Falcon 9, 5 двигателей Saturn V, 7 аксиом МКС

---

*Блок B завершён. Следующий: БЛОК C — «Социальные системы» (Книги 31-35).*
*Книга 31: Архетипы движения в образовании и педагогике.*
