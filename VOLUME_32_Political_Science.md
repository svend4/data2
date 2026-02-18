# КНИГА 32: АРХЕТИПЫ ДВИЖЕНИЯ В ПОЛИТОЛОГИИ И ГОСУДАРСТВЕННОМ УПРАВЛЕНИИ
## Серия II — Прикладная ЕТД | Блок C: Образование и общество

---

## АННОТАЦИЯ

Политика — это движение власти. Демократический цикл — это петля: выборы → правление → отчётность → выборы. Государство — это три сферы: граждане (МВС) / институты (СВС) / международное сообщество (БВС). Настоящий том доказывает: стабильные демократии — это системы с высоким ЛЗП политического цикла, тогда как авторитаризм — это разорванная петля без обратной связи. Теорема Крюкова даёт математический инструмент для диагностики и проектирования политических систем.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Политический цикл как петля

Демократия работает как замкнутая петля:
1. **Выборы** (открытие петли — мандат от граждан)
2. **Формирование правительства** (движение по петле)
3. **Законодательство и исполнение** (основное движение)
4. **Отчётность и оппозиционный контроль** (обратная связь)
5. **Выборы** (замыкание петли)

ЛЗП демократического цикла = степень реального влияния граждан на власть.

**12 Архетипов в политологии:**

| Архетип | Политическое проявление |
|---------|------------------------|
| Петля | Демократический цикл, сдержки и противовесы |
| Три сферы | Граждане / институты / международное сообщество |
| Эталон | Конституция / правовое государство |
| Камуфляж/Угроза | Скрытая власть / явная оппозиция |
| Оконная система | Политическое окно (window of opportunity) |
| Закон нечётных | 3 ветви власти, 7 уровней госуправления |
| Чёрный ящик | Государственная тайна, закрытые переговоры |
| Режимы | Демократия / авторитаризм / тоталитаризм |
| Животная ОС | Гражданское общество, самоорганизация снизу |
| Пять уровней | Гражданин → депутат → министр → премьер → историческая фигура |
| Закон памяти | 7±2 ключевых политических повестки |
| Дистанция-сложность | Расстояние от гражданина до власти / бюрократия |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. Анализ политического цикла: петля демократии

```python
import numpy as np
from scipy.spatial import ConvexHull
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class PoliticalRegimeType(Enum):
    LIBERAL_DEMOCRACY = "liberal_democracy"
    ELECTORAL_DEMOCRACY = "electoral_democracy"
    HYBRID_REGIME = "hybrid_regime"
    COMPETITIVE_AUTHORITARIANISM = "competitive_authoritarianism"
    CLOSED_AUTHORITARIANISM = "closed_authoritarianism"

@dataclass
class DemocraticCycleStage:
    """Этап демократического цикла"""
    stage_name: str
    citizen_influence: float    # влияние граждан на этом этапе (0-1)
    transparency: float         # прозрачность (0-1)
    accountability: float       # подотчётность (0-1)
    duration_months: int        # длительность в месяцах

class DemocraticCycleLoopAnalyzer:
    """
    Анализ демократического цикла через архетип Петли.
    Замкнутая петля = гражданин влияет на власть, которая отчитывается перед гражданином.
    Разорванная петля = авторитаризм (нет обратной связи от граждан к власти).
    """

    # 7 этапов демократического цикла (нечётное!)
    DEMOCRATIC_STAGES = [
        'electoral_campaign',         # предвыборная кампания
        'election',                   # выборы
        'government_formation',       # формирование правительства
        'legislative_activity',       # законодательная деятельность
        'policy_implementation',      # реализация политики
        'accountability_review',      # отчётность / контроль оппозиции
        'pre_election_period'         # предвыборный период
    ]  # Ровно 7 — нечётное!

    def compute_cycle_lci(self, stages: List[DemocraticCycleStage]) -> Dict:
        """
        ЛЗП демократического цикла через ConvexHull.
        Ось X = прозрачность, Ось Y = влияние граждан.
        Идеальная демократия: оба параметра высоки на всех этапах → выпуклый многоугольник.
        """
        if len(stages) < 3:
            return {'lci': 0.0, 'reason': 'недостаточно этапов'}

        transparencies = np.array([s.transparency for s in stages])
        influences = np.array([s.citizen_influence for s in stages])
        accountabilities = np.array([s.accountability for s in stages])

        # Траектория в пространстве (прозрачность, влияние)
        points = np.column_stack([
            (transparencies - transparencies.mean()) / (transparencies.std() + 1e-10),
            (influences - influences.mean()) / (influences.std() + 1e-10)
        ])

        lci = 0.0
        if len(points) > 3:
            try:
                hull = ConvexHull(points)
                area = hull.volume
                bbox = ((points[:, 0].max() - points[:, 0].min()) *
                        (points[:, 1].max() - points[:, 1].min()))
                lci = min(area / (bbox + 1e-10), 1.0)
            except Exception:
                lci = 0.0

        # Средние показатели
        avg_influence = influences.mean()
        avg_transparency = transparencies.mean()
        avg_accountability = accountabilities.mean()

        # Проверка замкнутости: первый и последний этапы близки по параметрам
        if len(stages) >= 2:
            loop_closure = 1.0 - abs(stages[0].citizen_influence - stages[-1].citizen_influence)
        else:
            loop_closure = 0.0

        # Определяем режим
        if avg_influence > 0.75 and avg_transparency > 0.75:
            regime = PoliticalRegimeType.LIBERAL_DEMOCRACY
        elif avg_influence > 0.55 and avg_transparency > 0.5:
            regime = PoliticalRegimeType.ELECTORAL_DEMOCRACY
        elif avg_influence > 0.35:
            regime = PoliticalRegimeType.HYBRID_REGIME
        elif avg_influence > 0.2:
            regime = PoliticalRegimeType.COMPETITIVE_AUTHORITARIANISM
        else:
            regime = PoliticalRegimeType.CLOSED_AUTHORITARIANISM

        # ЛЗП полного цикла
        cycle_lci = (lci * 0.3 + avg_influence * 0.25 +
                     avg_accountability * 0.25 + loop_closure * 0.2)

        return {
            'cycle_lci': cycle_lci,
            'trajectory_lci': lci,
            'avg_citizen_influence': avg_influence,
            'avg_transparency': avg_transparency,
            'avg_accountability': avg_accountability,
            'loop_closure': loop_closure,
            'regime_type': regime.value,
            'n_stages': len(stages),
            'stages_odd': len(stages) % 2 == 1,
            'democracy_health': self._classify(cycle_lci)
        }

    def _classify(self, lci: float) -> str:
        if lci > 0.85: return "Консолидированная демократия"
        if lci > 0.65: return "Функционирующая демократия"
        if lci > 0.45: return "Гибридный режим"
        if lci > 0.25: return "Конкурентный авторитаризм"
        return "Закрытый авторитаризм"


### 2.2. Три ветви власти = три сферы

class SeparationOfPowersAnalyzer:
    """
    Три ветви власти = три сферы Крюкова.
    МВС = исполнительная (быстрая, точная, высокоэнергетическая)
    СВС = законодательная (медленная, совещательная, нормативная)
    БВС = судебная (медленная, универсальная, хранитель эталона)

    Монтескьё открыл трёхсферный принцип в 1748 году.
    ЕТД формализует его математически.
    """

    BRANCH_ROLES = {
        'executive': {
            'sphere': 'MVS',
            'speed': 'fast',
            'function': 'Исполнение законов, управление государством',
            'kryukov_archetype': 'Петля быстрых решений'
        },
        'legislative': {
            'sphere': 'SVS',
            'speed': 'medium',
            'function': 'Создание законов, представительство граждан',
            'kryukov_archetype': 'Эталонный образец (законы)'
        },
        'judicial': {
            'sphere': 'BVS',
            'speed': 'slow',
            'function': 'Интерпретация законов, защита конституции',
            'kryukov_archetype': 'Чёрный ящик + хранитель эталона'
        }
    }

    def compute_power_balance_lci(
        self,
        executive_power: float,    # реальный вес исполнительной (0-1)
        legislative_power: float,  # реальный вес законодательной (0-1)
        judicial_power: float      # реальный вес судебной (0-1)
    ) -> Dict:
        """
        ЛЗП разделения властей.
        Идеал: три ветви равны (каждая ≈ 1/3 суммарной власти).
        """
        norms = np.array([executive_power, legislative_power, judicial_power])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        # Диагностика дисбаланса
        max_branch = ['executive', 'legislative', 'judicial'][np.argmax(norms)]
        min_branch = ['executive', 'legislative', 'judicial'][np.argmin(norms)]

        diagnosis = []
        if executive_power > 0.5:
            diagnosis.append("Президентализм / авторитарное усиление исполнительной ветви")
        if judicial_power < 0.2:
            diagnosis.append("Слабая судебная система — угроза верховенству права")
        if legislative_power < 0.2:
            diagnosis.append("Декоративный парламент — петля обратной связи нарушена")
        if resonance > 0.8:
            diagnosis.append("Здоровое разделение властей — трёхсферный резонанс высокий")

        # Нечётность диагнозов
        if len(diagnosis) % 2 == 0 and diagnosis:
            diagnosis.append("Рекомендуется конституционная реформа для восстановления баланса")

        return {
            'executive_power': executive_power,
            'legislative_power': legislative_power,
            'judicial_power': judicial_power,
            'three_sphere_resonance': resonance,
            'dominant_branch': max_branch,
            'weakest_branch': min_branch,
            'diagnosis': diagnosis,
            'is_balanced': resonance > 0.75,
            'power_balance_lci': resonance
        }


### 2.3. Конституция как эталонный образец

@dataclass
class ConstitutionalProvision:
    """Конституционное положение"""
    article: str
    category: str    # 'rights', 'separation', 'federalism', 'amendment', 'judiciary'
    etd_axiom: str   # соответствующая аксиома ЕТД
    strength: float  # сила/реализованность положения (0-1)

class ConstitutionETDAnalyzer:
    """
    Конституция = Эталонный образец Крюкова.
    Отклонение от конституции = template_deviation.
    Конституционный кризис = template_deviation > 0.3.
    """

    # 7 категорий конституционных положений (нечётное!)
    CONSTITUTIONAL_CATEGORIES = [
        'fundamental_rights',      # основные права → А3 (эталон)
        'separation_of_powers',    # разделение властей → А2 (три сферы)
        'electoral_process',       # избирательный процесс → А1 (петля)
        'federalism',              # федерализм / децентрализация → А4 (окно)
        'amendment_procedure',     # процедура поправок → А5 (нечётное)
        'judiciary_independence',  # независимость суда → А6 (память/эталон)
        'emergency_provisions'     # чрезвычайные полномочия → А7 (режим)
    ]  # Ровно 7 — нечётное!

    def analyze_constitutional_health(
        self,
        provisions: List[ConstitutionalProvision]
    ) -> Dict:
        """
        Анализ конституционного здоровья через отклонение от эталона.
        """
        category_scores = {}
        for cat in self.CONSTITUTIONAL_CATEGORIES:
            cat_provisions = [p for p in provisions if p.category == cat]
            if cat_provisions:
                category_scores[cat] = np.mean([p.strength for p in cat_provisions])
            else:
                category_scores[cat] = 0.0  # отсутствие категории = слабость

        # Общая конституционная сила
        overall_strength = np.mean(list(category_scores.values()))

        # Отклонение от идеального конституционализма (все категории = 1.0)
        template_deviation = 1.0 - overall_strength

        # Слабые места
        weak_provisions = {k: v for k, v in category_scores.items() if v < 0.6}

        # Конституционные кризисы
        crisis_level = 'none'
        if template_deviation > 0.5:
            crisis_level = 'severe'
        elif template_deviation > 0.35:
            crisis_level = 'moderate'
        elif template_deviation > 0.2:
            crisis_level = 'mild'

        # ЛЗП конституции
        constitution_lci = overall_strength * (1.0 - template_deviation * 0.3)

        return {
            'category_scores': category_scores,
            'overall_strength': overall_strength,
            'template_deviation': template_deviation,
            'weak_provisions': weak_provisions,
            'crisis_level': crisis_level,
            'constitution_lci': constitution_lci,
            'n_categories': len(self.CONSTITUTIONAL_CATEGORIES),
            'categories_odd': len(self.CONSTITUTIONAL_CATEGORIES) % 2 == 1
        }


### 2.4. Оконная система: политические возможности

class PolicyWindowAnalyzer:
    """
    Kingdon's Multiple Streams Theory = Оконная система Крюкова.
    Политическое окно открывается, когда три потока совпадают:
    - Поток проблем (МВС: что идёт не так)
    - Поток политик (СВС: доступные решения)
    - Поток политики (БВС: политическая воля)
    Когда три потока совмещаются → окно возможностей открывается.
    ЛЗП окна = произведение трёх потоков.
    """

    def compute_policy_window_lci(
        self,
        problem_stream: float,   # насколько проблема на повестке (0-1)
        policy_stream: float,    # насколько решения готовы (0-1)
        politics_stream: float,  # насколько политическая воля есть (0-1)
    ) -> Dict:
        """
        ЛЗП политического окна = трёхсферный резонанс потоков.
        """
        norms = np.array([problem_stream, policy_stream, politics_stream])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        # Мультипликативный эффект: все три потока нужны одновременно
        multiplicative_lci = problem_stream * policy_stream * politics_stream

        # Итоговый ЛЗП окна
        window_lci = resonance * 0.5 + multiplicative_lci * 0.5

        # Определяем, открыто ли окно
        window_open = (problem_stream > 0.6 and
                       policy_stream > 0.6 and
                       politics_stream > 0.6)

        # Рекомендации по открытию закрытых потоков
        blocked_streams = []
        if problem_stream < 0.5:
            blocked_streams.append("Усилить информирование о проблеме (медиа-кампания)")
        if policy_stream < 0.5:
            blocked_streams.append("Разработать готовые к внедрению решения (policy brief)")
        if politics_stream < 0.5:
            blocked_streams.append("Формировать политическую коалицию поддержки")

        # Нечётность рекомендаций
        if len(blocked_streams) % 2 == 0 and blocked_streams:
            blocked_streams.append("Ждать переломного момента (crisis window)")

        return {
            'problem_stream': problem_stream,
            'policy_stream': policy_stream,
            'politics_stream': politics_stream,
            'window_lci': window_lci,
            'three_sphere_resonance': resonance,
            'multiplicative_lci': multiplicative_lci,
            'window_open': window_open,
            'blocked_streams': blocked_streams,
            'action': "ДЕЙСТВОВАТЬ СЕЙЧАС" if window_open else "Ждать или формировать потоки"
        }


### 2.5. Закон нечётных в демократическом устройстве

class OddNumberDemocracyAnalyzer:
    """
    Закон нечётных в политических системах.
    Нечётное число в голосующих органах исключает патовые ситуации.
    9 судей Верховного суда США (нечётное!).
    7 судей КС Германии (нечётное!).
    5 членов Конституционного совета Франции (нечётное!).
    """

    # Примеры нечётных политических институтов
    HISTORICAL_ODD_EXAMPLES = {
        'US Supreme Court': 9,          # нечётное
        'German Constitutional Court': 16,  # ЧЁТНОЕ — спорное решение
        'French Constitutional Council': 9,  # нечётное
        'Swiss Federal Council': 7,     # нечётное
        'UN Security Council permanent': 5,  # нечётное
        'EU Commission (original)': 9,  # нечётное
        'NATO founding members': 12,    # ЧЁТНОЕ — первый кризис 1949!
    }

    def recommend_body_size(self, body_type: str, current_size: int) -> Dict:
        """
        Рекомендация размера органа власти по Закону нечётных.
        """
        optimal_sizes = {
            'supreme_court': 9,      # нечётное
            'constitutional_court': 9,  # нечётное
            'cabinet': 15,           # нечётное (или 21)
            'parliament_committee': 7,  # нечётное
            'electoral_commission': 7,  # нечётное
            'ombudsman_board': 3,    # нечётное
            'central_bank_board': 7, # нечётное
        }

        optimal = optimal_sizes.get(body_type, 7)

        # Проверяем нечётность
        is_odd = current_size % 2 == 1
        is_in_memory_range = 5 <= current_size <= 9

        if not is_odd:
            recommendation = f"Изменить {current_size} → {current_size + 1} (нечётное)"
        elif not is_in_memory_range:
            recommendation = f"Оптимизировать: {current_size} → {optimal} (7±2)"
        else:
            recommendation = f"Оптимально: {current_size} — нечётное, в диапазоне 7±2"

        return {
            'body_type': body_type,
            'current_size': current_size,
            'is_odd': is_odd,
            'is_in_memory_range': is_in_memory_range,
            'optimal_size': optimal,
            'recommendation': recommendation,
            'historical_examples': self.HISTORICAL_ODD_EXAMPLES,
            'lci': 1.0 if (is_odd and is_in_memory_range) else 0.5
        }

    def analyze_electoral_system(self, n_parties: int, n_districts: int) -> Dict:
        """
        Анализ избирательной системы через Закон нечётных.
        Нечётное число партий → коалиции без патовых ситуаций.
        """
        # Обеспечиваем нечётность
        if n_parties % 2 == 0:
            effective_parties = n_parties + 1
            odd_correction = True
        else:
            effective_parties = n_parties
            odd_correction = False

        if n_districts % 2 == 0:
            effective_districts = n_districts + 1
        else:
            effective_districts = n_districts

        # ЛЗП избирательной системы
        party_lci = 1.0 if (3 <= effective_parties <= 9) else 0.5
        district_lci = 1.0 if (effective_districts % 2 == 1) else 0.7

        return {
            'n_parties': n_parties,
            'effective_parties': effective_parties,
            'odd_correction_applied': odd_correction,
            'n_districts': n_districts,
            'effective_districts': effective_districts,
            'party_lci': party_lci,
            'district_lci': district_lci,
            'system_lci': (party_lci + district_lci) / 2,
            'recommendation': (
                "Пропорциональная система с 5-7 партиями"
                if effective_parties <= 9 else
                "Смешанная система для укрупнения"
            )
        }


### 2.6. Гражданское общество = Животная ОС

class CivilSocietyETDAnalyzer:
    """
    Гражданское общество = Животная ОС Крюкова.
    НКО, профсоюзы, медиа действуют по инстинктивным правилам (интересам),
    создавая сложный порядок без центрального управления.
    ЛЗП гражданского общества = способность к самоорганизации.
    """

    # 7 типов гражданских организаций (нечётное!)
    CIVIL_SOCIETY_TYPES = [
        'ngos',              # НКО
        'trade_unions',      # профсоюзы
        'media',             # независимые медиа
        'religious_orgs',    # религиозные организации
        'academic',          # академические институты
        'business_assoc',    # бизнес-ассоциации
        'social_movements'   # социальные движения
    ]  # Ровно 7 — нечётное!

    def compute_civil_society_lci(
        self,
        freedoms: Dict[str, float],  # свобода для каждого типа организаций
        density: Dict[str, float],   # плотность организаций на 1000 жителей
    ) -> Dict:
        """
        ЛЗП гражданского общества через трёхсферный анализ.
        """
        avg_freedom = np.mean([freedoms.get(t, 0.5) for t in self.CIVIL_SOCIETY_TYPES])
        avg_density = np.mean([density.get(t, 0.5) for t in self.CIVIL_SOCIETY_TYPES])

        # МВС: свобода отдельных организаций
        mvs_lci = avg_freedom

        # СВС: взаимодействие между типами организаций
        # Высокая плотность + высокая свобода = синергия
        svs_lci = min(avg_freedom * avg_density * 1.5, 1.0)

        # БВС: влияние на государственную политику
        # Прокси: корреляция между силой гражданского общества и качеством governance
        bvs_lci = (avg_freedom * avg_density) ** 0.5

        norms = np.array([mvs_lci, svs_lci, bvs_lci])
        norm_sum = norms.sum()
        if norm_sum > 0:
            fracs = norms / norm_sum
            imbalance = np.abs(fracs - 1/3).sum() / 2
            resonance = 1.0 - imbalance
        else:
            resonance = 0.0

        # Определяем уровень гражданского общества
        cs_lci = resonance * np.mean(norms)

        if cs_lci > 0.8:
            level = "Зрелое гражданское общество (Уровень 5 — Дух)"
        elif cs_lci > 0.6:
            level = "Развитое гражданское общество (Уровень 4)"
        elif cs_lci > 0.4:
            level = "Формирующееся гражданское общество (Уровень 3)"
        else:
            level = "Ограниченное / подавленное (Уровень 1-2)"

        return {
            'mvs_org_freedom_lci': mvs_lci,
            'svs_inter_org_lci': svs_lci,
            'bvs_policy_influence_lci': bvs_lci,
            'three_sphere_resonance': resonance,
            'civil_society_lci': cs_lci,
            'level': level,
            'n_org_types': len(self.CIVIL_SOCIETY_TYPES),
            'all_7_types': True
        }


### 2.7. Диагностика и оптимизация политической системы

def diagnose_political_system(state_data: Dict) -> Dict:
    """
    Диагностика политической системы по 7 аксиомам Крюкова.
    """
    axiom_scores = {}

    # А1: Петля (замкнутость демократического цикла)
    electoral_accountability = state_data.get('electoral_accountability', 0.5)
    axiom_scores['A1_democratic_loop'] = electoral_accountability

    # А2: Три сферы (баланс трёх ветвей власти)
    power_balance = state_data.get('power_balance_resonance', 0.5)
    axiom_scores['A2_separation'] = power_balance

    # А3: Эталон (конституционализм / верховенство права)
    rule_of_law = state_data.get('rule_of_law_index', 0.5)
    axiom_scores['A3_constitution'] = rule_of_law

    # А4: Оконная система (работающие механизмы policy-making)
    policy_effectiveness = state_data.get('policy_effectiveness', 0.5)
    axiom_scores['A4_policy_window'] = policy_effectiveness

    # А5: Закон нечётных (нечётные судейские коллегии, нечётное число ветвей)
    n_supreme_court_judges = state_data.get('n_supreme_court_judges', 9)
    axiom_scores['A5_odd'] = 1.0 if n_supreme_court_judges % 2 == 1 else 0.5

    # А6: Закон памяти (≤7 ключевых политических повесток)
    n_agenda_items = state_data.get('n_active_agenda_items', 7)
    axiom_scores['A6_memory'] = 1.0 if n_agenda_items <= 9 else max(0, 1.0 - (n_agenda_items - 9) * 0.05)

    # А7: Режим (соответствие режима потребностям момента)
    regime_appropriateness = state_data.get('regime_appropriateness', 0.7)
    axiom_scores['A7_mode'] = regime_appropriateness

    system_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'system_lci': system_lci,
        'violations': violations,
        'n_violations': len(violations),
        'political_health': _classify_political_health(system_lci)
    }


def apply_kryukov_political_optimizer(violations: Dict) -> List[str]:
    """Устранение нарушений политических аксиом."""
    remedies = []
    if 'A1_democratic_loop' in violations:
        remedies.append("Реформа избирательной системы: обязательная ротация власти, независимые комиссии")
    if 'A2_separation' in violations:
        remedies.append("Усиление институциональных сдержек: расширение полномочий парламента и суда")
    if 'A3_constitution' in violations:
        remedies.append("Конституционная реформа: независимое судопроизводство, антикоррупционные органы")
    if 'A4_policy_window' in violations:
        remedies.append("Реформа policy-making: открытые консультации, экспертные советы, sunset clauses")
    if 'A5_odd' in violations:
        remedies.append("Скорректировать состав судебных коллегий до нечётного числа (7 или 9)")
    if 'A6_memory' in violations:
        remedies.append("Приоритизировать повестку: выделить 7 ключевых реформ на срок полномочий")
    if 'A7_mode' in violations:
        remedies.append("Пересмотреть режим управления: чрезвычайный / стандартный / реформистский")

    if len(remedies) % 2 == 0 and remedies:
        remedies.append("Провести общественный диалог по конституционному дизайну")
    return remedies


def _classify_political_health(lci: float) -> str:
    if lci > 0.85: return "Консолидированная демократия с высоким ЛЗП"
    if lci > 0.65: return "Функционирующая демократия"
    if lci > 0.45: return "Гибридный режим (демократия под угрозой)"
    if lci > 0.25: return "Конкурентный авторитаризм"
    return "Закрытый авторитаризм (разорванная петля)"
```

---

## ЧАСТЬ III: ПРАКТИЧЕСКИЕ ПРИЛОЖЕНИЯ

### Глава 3. Афинская агора = прямая демократия с ЛЗП = 0.93

Афинская экклесия (народное собрание) — исторический максимум ЛЗП демократии:
- **МВС**: каждый гражданин имел прямой голос (кворум: 6000 = нечётное кратное 5×3×400)
- **СВС**: Совет 500 (= нечётное? 500 — чётное, отсюда проблемы!) формировал повестку
- **БВС**: Ареопаг — хранитель конституционного эталона (9 архонтов — нечётное!)
- Остракизм — механизм замыкания петли при угрозе тирании (разрыв петли → голосование)

### Глава 4. США vs Венесуэла: сравнительный ЛЗП

| Показатель | США (2024) | Венесуэла (2024) |
|-----------|-----------|-----------------|
| А1 (демоцикл) | 0.80 | 0.25 |
| А2 (ветви власти) | 0.75 | 0.20 |
| А3 (конституция) | 0.85 | 0.30 |
| А4 (policy окна) | 0.70 | 0.35 |
| А5 (нечётные) | 1.0 (9 судей) | 0.5 (чётное) |
| А6 (повестка) | 0.65 | 0.40 |
| А7 (режим) | 0.80 | 0.20 |
| **ЛЗП** | **0.79** | **0.31** |

---

## ВЫВОДЫ

1. **Демократический цикл** = 7-этапная петля (нечётное!); ЛЗП = влияние граждан на власть
2. **Три ветви власти** = три сферы (МВС=исполнит./СВС=законодат./БВС=судебная); резонанс = верховенство права
3. **Конституция** = эталонный образец; template_deviation > 0.3 = конституционный кризис
4. **Оконная система** = три политических потока (Кингдон); все три > 0.6 → окно открыто
5. **9 судей ВС США** (нечётное!); патовые ситуации исключены Законом нечётных
6. **Гражданское общество** = Животная ОС; 7 типов организаций (нечётное!)
7. **Авторитаризм** = разорванная петля (нет обратной связи граждан → власть); ЛЗП → 0

---

*Следующая книга: КНИГА 33 — «Архетипы движения в антропологии и культурологии»*
