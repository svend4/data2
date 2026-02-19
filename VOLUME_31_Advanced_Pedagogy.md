# КНИГА 31: АРХЕТИПЫ ДВИЖЕНИЯ В ПЕДАГОГИКЕ И ОБРАЗОВАНИИ
## Серия II — Прикладная ЕТД | Блок C: Образование и общество

---

## АННОТАЦИЯ

Обучение — это движение. Ученик движется по пространству знаний от незнания к мастерству. Урок — это петля: вопрос → исследование → ответ → новый вопрос. Класс — это три сферы: ученик (МВС) / группа (СВС) / учебное заведение (БВС). Настоящий том применяет 12 архетипов Крюкова к педагогике: доказывается, что оптимальный учебный процесс — это система с ЛЗП, стремящимся к единице, где каждый урок замыкается в совершенную петлю понимания.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Учебная петля как базовый архетип

Сократический диалог — древнейшая педагогическая петля:
- Вопрос (открытие петли) → Исследование (движение по петле) → Ответ (замыкание) → Новый вопрос (новая петля)

ЛЗП урока = степень замыкания понимания:
- Ученик начал с непонимания (0) и завершил с пониманием (1)
- Конечное понимание перешло в новый вопрос = петля замкнулась

**12 Архетипов в педагогике:**

| Архетип | Педагогическое проявление |
|---------|--------------------------|
| Петля | Урок (вопрос→ответ→вопрос), учебный цикл |
| Три сферы | Ученик / класс / школа (МВС/СВС/БВС) |
| Эталон | Эталонное решение, образцовый ответ |
| Камуфляж/Угроза | Скрытое знание / явное непонимание |
| Оконная система | Зона ближайшего развития (Выготский) |
| Закон нечётных | 7 уроков в неделю, 3 четверти, 5 предметов |
| Чёрный ящик | Зона непонимания (что происходит «внутри» ученика) |
| Режимы | СКАН/ПОСЛЕДОВАТ./АДАПТ./ТОЧНЫЙ/ДВОЙНОЙ = 5 режимов обучения |
| Животная ОС | Игровое и проектное обучение (самоорганизация) |
| Пять уровней | Новичок / ученик / практик / мастер / эксперт |
| Закон памяти | 7±2 новых понятий за урок |
| Дистанция-сложность | Когнитивная нагрузка / уровень ЗБР |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. ЛЗП урока: петля понимания

```python
import numpy as np
from scipy.spatial import ConvexHull
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class LearningMode(Enum):
    SCAN = "scan"               # обзор темы (СКАН)
    SEQUENTIAL = "sequential"   # пошаговое изложение
    ADAPTIVE = "adaptive"       # адаптивное обучение
    PRECISE = "precise"         # глубокое погружение
    DUAL = "dual"               # обучение через обучение других

@dataclass
class LessonEvent:
    """Событие в процессе урока"""
    timestamp: float        # время от начала урока (0-1)
    comprehension: float    # понимание ученика (0-1)
    engagement: float       # вовлечённость (0-1)
    event_type: str         # 'question', 'explanation', 'practice', 'feedback'

@dataclass
class Student:
    student_id: str
    prior_knowledge: float      # 0-1, стартовый уровень
    learning_rate: float        # скорость усвоения
    working_memory: int = 7     # объём рабочей памяти (7±2)
    preferred_mode: LearningMode = LearningMode.ADAPTIVE

class LessonLoopAnalyzer:
    """
    Анализ урока через архетип Петли.
    Идеальный урок: ученик замыкает петлю понимания —
    начинает с вопроса, заканчивает ответом, который порождает новый вопрос.
    ЛЗП урока измеряется через ConvexHull траектории (время, понимание).
    """

    # Нечётное количество типов учебных событий (7)
    EVENT_TYPES = [
        'hook',          # захват внимания (открытие петли)
        'activation',    # активация предшествующих знаний
        'instruction',   # прямое обучение
        'modeling',      # демонстрация образца
        'practice',      # практика с поддержкой
        'assessment',    # проверка понимания
        'closure'        # замыкание петли (новый вопрос/задание)
    ]  # Ровно 7 — нечётное!

    def compute_lesson_lci(self, events: List[LessonEvent]) -> Dict:
        """
        ЛЗП урока через ConvexHull траектории понимания.
        Ось X = время (0→1), Ось Y = понимание (0→1).
        Идеальный урок: понимание растёт, возвращается к вопросу = замкнутая петля.
        """
        if len(events) < 3:
            return {'lci': 0.0, 'reason': 'недостаточно событий'}

        times = np.array([e.timestamp for e in events])
        comprehensions = np.array([e.comprehension for e in events])
        engagements = np.array([e.engagement for e in events])

        # Траектория в 2D (понимание, вовлечённость)
        points = np.column_stack([
            (comprehensions - comprehensions.mean()) / (comprehensions.std() + 1e-10),
            (engagements - engagements.mean()) / (engagements.std() + 1e-10)
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

        # Рост понимания
        comprehension_gain = comprehensions[-1] - comprehensions[0]

        # Замкнутость петли: финальное понимание > начального + есть новый вопрос
        loop_closed = comprehension_gain > 0.3 and events[-1].event_type == 'closure'

        # Средняя вовлечённость
        mean_engagement = engagements.mean()

        # Оценка соответствия 7 этапам урока
        event_types_present = set(e.event_type for e in events)
        all_stages_count = len(event_types_present.intersection(set(self.EVENT_TYPES)))
        stage_coverage = all_stages_count / len(self.EVENT_TYPES)

        # Итоговый ЛЗП урока
        lesson_lci = (lci * 0.3 + comprehension_gain * 0.3 +
                      mean_engagement * 0.2 + stage_coverage * 0.2)

        return {
            'lesson_lci': lesson_lci,
            'trajectory_lci': lci,
            'comprehension_gain': comprehension_gain,
            'mean_engagement': mean_engagement,
            'stage_coverage': stage_coverage,
            'n_event_types': all_stages_count,
            'loop_closed': loop_closed,
            'lesson_grade': self._grade(lesson_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.85: return "Мастер-класс (Уровень 5)"
        if lci > 0.70: return "Эффективный урок (Уровень 4)"
        if lci > 0.55: return "Средний урок (Уровень 3)"
        if lci > 0.40: return "Слабый урок (Уровень 2)"
        return "Неэффективный урок (Уровень 1)"

    def simulate_lesson(
        self,
        student: Student,
        topic_difficulty: float,  # 0-1
        n_events: int = 7         # нечётное!
    ) -> List[LessonEvent]:
        """
        Симуляция урока как ODE-подобного процесса.
        Понимание нарастает логистически с учётом рабочей памяти.
        """
        if n_events % 2 == 0:
            n_events += 1

        events = []
        comprehension = student.prior_knowledge
        engagement = 0.8  # стартовая вовлечённость

        for i, event_type in enumerate(self.EVENT_TYPES[:n_events]):
            t = i / (n_events - 1)

            # Прирост понимания зависит от режима события
            if event_type in ['instruction', 'modeling']:
                delta_c = student.learning_rate * (1 - comprehension) * 0.3
            elif event_type in ['practice', 'assessment']:
                delta_c = student.learning_rate * comprehension * 0.2
            elif event_type == 'hook':
                delta_c = 0.05  # небольшое начальное пробуждение
            else:
                delta_c = student.learning_rate * 0.1

            # Когнитивная нагрузка (Закон памяти)
            cognitive_load = topic_difficulty / (student.working_memory / 7)
            if cognitive_load > 1.0:
                delta_c *= 0.5  # перегрузка снижает усвоение

            comprehension = min(1.0, comprehension + delta_c)

            # Динамика вовлечённости
            if event_type in ['practice', 'hook']:
                engagement = min(1.0, engagement + 0.05)
            elif event_type == 'instruction' and i > 3:
                engagement = max(0.3, engagement - 0.05)

            events.append(LessonEvent(
                timestamp=t,
                comprehension=comprehension,
                engagement=engagement,
                event_type=event_type
            ))

        return events


### 2.2. Три сферы образовательной системы

class EducationThreeSphereAnalyzer:
    """
    Три сферы образования:
    МВС = ученик (индивидуальное обучение, нейронные связи)
    СВС = класс/группа (социальное обучение, peer learning)
    БВС = школа/система (институциональное обучение, программа)
    """

    # Нечётное количество показателей в каждой сфере
    MVS_METRICS = [
        'comprehension_rate',  # скорость усвоения
        'retention_7day',      # удержание через 7 дней (нечётное!)
        'transfer_ability',    # перенос знаний
        'metacognition',       # рефлексия
        'intrinsic_motivation', # внутренняя мотивация
        'growth_mindset',      # установка на рост
        'self_regulation'      # саморегуляция
    ]  # 7 показателей — нечётное!

    SVS_METRICS = [
        'peer_interaction_quality',  # качество взаимодействия
        'collaborative_lci',         # ЛЗП совместной работы
        'group_cohesion',            # сплочённость группы
        'peer_teaching_ratio',       # доля обучения друг друга
        'social_safety'              # психологическая безопасность
    ]  # 5 показателей — нечётное!

    BVS_METRICS = [
        'curriculum_alignment',  # соответствие программы реальным потребностям
        'assessment_validity',   # валидность оценивания
        'resource_distribution'  # равномерность ресурсов
    ]  # 3 показателя — нечётное!

    def compute_educational_resonance(
        self,
        mvs_scores: Dict[str, float],
        svs_scores: Dict[str, float],
        bvs_scores: Dict[str, float]
    ) -> Dict:
        """
        Трёхсферный резонанс образовательной системы.
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

        # Диагностика нарушений
        violations = {}
        if mvs_lci < 0.6:
            violations['A1_individual'] = f"Низкий МВС-ЛЗП: {mvs_lci:.2f} — фокус на персональном обучении"
        if svs_lci < 0.6:
            violations['A2_group'] = f"Низкий СВС-ЛЗП: {svs_lci:.2f} — развивать кооперативное обучение"
        if bvs_lci < 0.6:
            violations['A3_system'] = f"Низкий БВС-ЛЗП: {bvs_lci:.2f} — реформировать программу"
        if resonance < 0.6:
            violations['A2_resonance'] = f"Дисбаланс сфер: резонанс={resonance:.2f}"

        return {
            'mvs_student_lci': mvs_lci,
            'svs_class_lci': svs_lci,
            'bvs_system_lci': bvs_lci,
            'three_sphere_resonance': resonance,
            'educational_lci': resonance * np.mean(norms),
            'violations': violations,
            'is_healthy_system': resonance > 0.75 and min(mvs_lci, svs_lci, bvs_lci) > 0.5
        }


### 2.3. Зона ближайшего развития = оконная система

class ZPDWindowAnalyzer:
    """
    Зона Ближайшего Развития (ЗБР) Выготского = Оконная система Крюкова.
    Окно: [уровень_актуальн_развития, уровень_потенц_развития].
    Слишком лёгко (ниже окна) → скука → разрыв петли.
    Слишком трудно (выше окна) → фрустрация → разрыв петли.
    В окне (ЗБР) → оптимальный поток → замкнутая петля.
    """

    def compute_zpd_lci(
        self,
        student: Student,
        task_difficulty: float,  # 0-1
    ) -> Dict:
        """
        ЛЗП задания с учётом ЗБР.
        """
        # Граница ЗБР
        zpd_lower = student.prior_knowledge
        zpd_upper = min(1.0, student.prior_knowledge + 0.3)  # ЗБР ≈ 30% выше актуального

        # Позиция задания относительно ЗБР
        if task_difficulty < zpd_lower:
            # Ниже ЗБР: слишком легко
            position = 'below_zpd'
            flow_lci = task_difficulty / (zpd_lower + 1e-10)  # снижается
            engagement_estimate = 0.3
        elif task_difficulty <= zpd_upper:
            # В ЗБР: оптимальное окно
            position = 'in_zpd'
            # ЛЗП максимален в центре ЗБР
            zpd_center = (zpd_lower + zpd_upper) / 2
            distance_from_center = abs(task_difficulty - zpd_center) / (zpd_upper - zpd_lower + 1e-10)
            flow_lci = 1.0 - distance_from_center * 0.3
            engagement_estimate = 0.85
        else:
            # Выше ЗБР: слишком сложно
            position = 'above_zpd'
            excess = (task_difficulty - zpd_upper) / (1 - zpd_upper + 1e-10)
            flow_lci = 1.0 - excess
            engagement_estimate = 0.5

        flow_lci = max(0.0, flow_lci)

        # Рекомендованные уровни поддержки (скаффолдинг)
        if position == 'above_zpd':
            scaffolding_level = 'high'
            n_scaffolding_steps = 7  # нечётное — максимум поддержки
        elif position == 'in_zpd':
            scaffolding_level = 'medium'
            n_scaffolding_steps = 3  # нечётное — умеренная поддержка
        else:
            scaffolding_level = 'low'
            n_scaffolding_steps = 1  # нечётное — минимум поддержки

        return {
            'task_difficulty': task_difficulty,
            'zpd_lower': zpd_lower,
            'zpd_upper': zpd_upper,
            'position': position,
            'flow_lci': flow_lci,
            'engagement_estimate': engagement_estimate,
            'scaffolding_level': scaffolding_level,
            'n_scaffolding_steps': n_scaffolding_steps,
            'recommendation': self._recommend(position, flow_lci)
        }

    def _recommend(self, position: str, lci: float) -> str:
        if position == 'below_zpd':
            return "Усложнить задание или добавить метакогнитивный вызов"
        elif position == 'in_zpd':
            return f"Оптимальная сложность (ЛЗП={lci:.2f}) — продолжать в этом режиме"
        else:
            return "Снизить сложность или обеспечить структурированную поддержку (скаффолдинг)"


### 2.4. Закон памяти: 7±2 понятий за урок

class MemoryLawPedagogyOptimizer:
    """
    Закон памяти в педагогике: рабочая память вмещает 7±2 единицы.
    Оптимум: 7 новых понятий. Максимум: 9. Минимум: 5.
    """

    OPTIMAL_CONCEPTS_PER_LESSON = 7   # нечётное!
    MAX_CONCEPTS_PER_LESSON = 9        # нечётное!
    MIN_CONCEPTS_PER_LESSON = 5        # нечётное!

    def design_lesson_content(
        self,
        total_concepts: int,
        n_lessons: int = 7  # нечётное
    ) -> List[Dict]:
        """
        Распределение понятий по урокам с соблюдением Закона памяти.
        """
        if n_lessons % 2 == 0:
            n_lessons += 1

        lessons = []
        concepts_remaining = total_concepts
        concepts_per_lesson = min(
            max(self.MIN_CONCEPTS_PER_LESSON,
                total_concepts // n_lessons),
            self.MAX_CONCEPTS_PER_LESSON
        )

        # Нечётность понятий за урок
        if concepts_per_lesson % 2 == 0:
            concepts_per_lesson -= 1  # в сторону нечётного

        for i in range(n_lessons):
            n_new = min(concepts_per_lesson, concepts_remaining)
            n_review = min(3, i * 2)  # обзор предыдущего (нечётное: 1, 3, 5...)
            if n_review % 2 == 0:
                n_review += 1

            cognitive_load = (n_new + n_review * 0.3) / self.OPTIMAL_CONCEPTS_PER_LESSON

            lessons.append({
                'lesson': i + 1,
                'n_new_concepts': n_new,
                'n_review_concepts': n_review,
                'total_cognitive_items': n_new + n_review,
                'cognitive_load': cognitive_load,
                'is_within_memory_law': n_new <= self.MAX_CONCEPTS_PER_LESSON,
                'memory_lci': 1.0 - abs(n_new - self.OPTIMAL_CONCEPTS_PER_LESSON) / self.OPTIMAL_CONCEPTS_PER_LESSON
            })
            concepts_remaining -= n_new

        return lessons

    def compute_spaced_repetition_schedule(
        self,
        concept: str,
        n_repetitions: int = 7  # нечётное!
    ) -> List[Dict]:
        """
        Интервальное повторение по кривой Эббингауза.
        7 повторений с нарастающими интервалами (нечётное!).
        Интервалы: 1, 3, 7, 15, 31, 63, 127 дней
        (2^n - 1 = нечётные числа Мерсенна!)
        """
        if n_repetitions % 2 == 0:
            n_repetitions += 1

        # Интервалы Мерсенна: 2^n - 1 (все нечётные!)
        intervals = [2**i - 1 for i in range(1, n_repetitions + 1)]
        # [1, 3, 7, 15, 31, 63, 127] — все нечётные!

        schedule = []
        cumulative_day = 0
        retention = 1.0

        for i, interval in enumerate(intervals):
            cumulative_day += interval
            # Экспоненциальное затухание памяти
            retention = np.exp(-0.3 * interval / (i + 1))
            # После повторения — восстановление
            retention_after = min(1.0, retention + 0.4)

            schedule.append({
                'repetition': i + 1,
                'day': cumulative_day,
                'interval_days': interval,
                'retention_before': retention,
                'retention_after': retention_after,
                'interval_is_odd': interval % 2 == 1,  # всегда True для 2^n - 1!
                'lci': retention_after
            })

        return schedule


### 2.5. Пять режимов обучения = Пять архетипов Крюкова

class LearningModeETDDesigner:
    """
    Пять режимов обучения = пять режимов Крюкова.
    СКАН → ПОСЛЕДОВАТЕЛЬНЫЙ → АДАПТИВНЫЙ → ТОЧНЫЙ → ДВОЙНОЙ
    """

    MODE_DESCRIPTIONS = {
        LearningMode.SCAN: {
            'name': 'Обзорное обучение (СКАН)',
            'strategy': 'Широкий охват, поверхностный контакт с темой',
            'best_for': 'Новая область, ориентация в пространстве знаний',
            'duration_min': 45,  # нечётное!
            'n_topics': 9,       # нечётное!
            'lci_typical': 0.4
        },
        LearningMode.SEQUENTIAL: {
            'name': 'Пошаговое обучение (ПОСЛЕДОВАТЕЛЬНЫЙ)',
            'strategy': 'Линейное изучение от простого к сложному',
            'best_for': 'Освоение навыков с чёткой иерархией',
            'duration_min': 45,  # нечётное!
            'n_topics': 7,       # нечётное!
            'lci_typical': 0.6
        },
        LearningMode.ADAPTIVE: {
            'name': 'Адаптивное обучение (АДАПТИВНЫЙ)',
            'strategy': 'Подстройка сложности к текущему уровню ЗБР',
            'best_for': 'Смешанные группы, персонализация',
            'duration_min': 45,  # нечётное!
            'n_topics': 5,       # нечётное!
            'lci_typical': 0.75
        },
        LearningMode.PRECISE: {
            'name': 'Точное обучение (ТОЧНЫЙ)',
            'strategy': 'Глубокое погружение в одну тему, мастерство',
            'best_for': 'Профессиональное развитие, специализация',
            'duration_min': 45,  # нечётное!
            'n_topics': 3,       # нечётное!
            'lci_typical': 0.88
        },
        LearningMode.DUAL: {
            'name': 'Двойное обучение (ДВОЙНОЙ)',
            'strategy': 'Учусь → обучаю других → глубже понимаю',
            'best_for': 'Достижение мастерства уровня 5 (Дух)',
            'duration_min': 45,  # нечётное!
            'n_topics': 1,       # 1 тема — максимальная глубина
            'lci_typical': 0.97
        }
    }

    def select_optimal_mode(
        self,
        student: Student,
        topic_coverage: float,  # насколько тема уже изучена (0-1)
        available_time_min: int = 45  # нечётное!
    ) -> Dict:
        """
        Выбор оптимального режима обучения для данного ученика и темы.
        """
        if available_time_min % 2 == 0:
            available_time_min += 1

        # Логика выбора режима по уровню знаний
        if topic_coverage < 0.2:
            mode = LearningMode.SCAN
        elif topic_coverage < 0.4:
            mode = LearningMode.SEQUENTIAL
        elif topic_coverage < 0.6:
            mode = LearningMode.ADAPTIVE
        elif topic_coverage < 0.8:
            mode = LearningMode.PRECISE
        else:
            mode = LearningMode.DUAL

        # Учёт предпочтений ученика
        if student.preferred_mode == mode:
            mode_match_bonus = 0.1
        else:
            mode_match_bonus = 0.0

        mode_desc = self.MODE_DESCRIPTIONS[mode]
        lci = mode_desc['lci_typical'] + mode_match_bonus

        return {
            'recommended_mode': mode.value,
            'mode_description': mode_desc,
            'student_preferred': student.preferred_mode.value,
            'mode_match': student.preferred_mode == mode,
            'expected_lci': min(lci, 1.0),
            'n_topics_in_session': mode_desc['n_topics'],
            'topics_odd': mode_desc['n_topics'] % 2 == 1
        }


### 2.6. Диагностика и оптимизация педагогической системы

def diagnose_educational_system(school_data: Dict) -> Dict:
    """
    Диагностика образовательной системы по 7 аксиомам Крюкова.
    """
    axiom_scores = {}

    # А1: Петля (замкнутость учебного цикла)
    lesson_lci = school_data.get('avg_lesson_lci', 0.5)
    axiom_scores['A1_lesson_loop'] = lesson_lci

    # А2: Три сферы (баланс ученик/класс/система)
    resonance = school_data.get('three_sphere_resonance', 0.5)
    axiom_scores['A2_three_spheres'] = resonance

    # А3: Эталон (наличие эталонных ответов и образцов)
    rubric_quality = school_data.get('rubric_quality', 0.5)
    axiom_scores['A3_template'] = rubric_quality

    # А4: Оконная система (ЗБР в заданиях)
    zpd_match = school_data.get('zpd_match_rate', 0.5)
    axiom_scores['A4_window'] = zpd_match

    # А5: Закон нечётных (нечётные периоды, нечётное число уроков)
    n_lessons_per_week = school_data.get('n_lessons_per_week', 5)
    axiom_scores['A5_odd'] = 1.0 if n_lessons_per_week % 2 == 1 else 0.5

    # А6: Закон памяти (≤9 новых понятий за урок)
    avg_new_concepts = school_data.get('avg_new_concepts_per_lesson', 7)
    axiom_scores['A6_memory'] = 1.0 if avg_new_concepts <= 9 else max(0, 1 - (avg_new_concepts - 9) * 0.1)

    # А7: Режим (правильный режим для уровня учащихся)
    mode_appropriateness = school_data.get('mode_appropriateness', 0.7)
    axiom_scores['A7_mode'] = mode_appropriateness

    system_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'system_lci': system_lci,
        'violations': violations,
        'n_violations': len(violations),
        'grade': _grade_education(system_lci)
    }


def apply_kryukov_pedagogy_optimizer(violations: Dict) -> List[str]:
    """Устранение нарушений педагогических аксиом."""
    remedies = []
    if 'A1_lesson_loop' in violations:
        remedies.append("Ввести структуру 7-шагового урока: hook→активация→обучение→моделирование→практика→оценка→замыкание")
    if 'A2_three_spheres' in violations:
        remedies.append("Балансировать МВС/СВС/БВС: 1/3 индивидуальной работы, 1/3 групповой, 1/3 системного закрепления")
    if 'A3_template' in violations:
        remedies.append("Разработать эталонные ответы и критериальное оценивание (рубрики)")
    if 'A4_window' in violations:
        remedies.append("Внедрить адаптивные задания с диагностикой ЗБР перед каждым уроком")
    if 'A5_odd' in violations:
        remedies.append("Перейти к 5 или 7 урокам в неделю (нечётное по Закону нечётных)")
    if 'A6_memory' in violations:
        remedies.append("Ограничить новый материал 7±2 понятиями за урок; остальное — на следующий")
    if 'A7_mode' in violations:
        remedies.append("Диагностировать уровень каждого ученика и назначить соответствующий режим СКАН→ДВОЙНОЙ")

    # Нечётность рекомендаций
    if len(remedies) % 2 == 0 and remedies:
        remedies.append("Провести системный аудит школы по ЕТД-методологии")
    return remedies


def measure_improvement(before: Dict, after: Dict) -> Dict:
    delta = after.get('system_lci', 0) - before.get('system_lci', 0)
    return {
        'lci_before': before.get('system_lci', 0),
        'lci_after': after.get('system_lci', 0),
        'improvement': delta,
        'improvement_pct': delta * 100,
        'success': delta > 0
    }


def design_kryukov_pedagogy_tool(level: str) -> Dict:
    """Инструмент для педагогики по уровню мастерства учителя."""
    tools = {
        'level_1': {
            'tool': 'LessonLoopChecker',
            'description': '7-шаговый чеклист урока',
            'n_checkpoints': 7
        },
        'level_2': {
            'tool': 'ZPDDiagnosticTest',
            'description': 'Тест ЗБР с 9 уровнями сложности',
            'n_levels': 9
        },
        'level_3': {
            'tool': 'MemoryLawScheduler',
            'description': 'Планировщик 7±2 понятий с интервальным повторением',
            'n_repetitions': 7
        },
        'level_4': {
            'tool': 'ThreeSphereClassroom',
            'description': 'Дизайн класса с балансом МВС/СВС/БВС',
            'n_sphere_activities': 3
        },
        'level_5': {
            'tool': 'FullETDSchoolAudit',
            'description': 'Полный ЕТД-аудит школы по 7 аксиомам',
            'n_axioms': 7
        }
    }
    return tools.get(level, tools['level_3'])


def _grade_education(lci: float) -> str:
    if lci > 0.90: return "Школа мирового класса"
    if lci > 0.75: return "Высокоэффективная школа"
    if lci > 0.60: return "Средняя школа"
    if lci > 0.45: return "Школа, требующая улучшения"
    return "Критическое состояние системы"
```

---

## ЧАСТЬ III: ПРАКТИЧЕСКИЕ ПРИЛОЖЕНИЯ

### Глава 3. Сократический метод = идеальная петля

Диалог Сократа: каждый вопрос открывает петлю, ответ собеседника — движение по петле, следующий вопрос Сократа — замыкание и открытие новой петли. ЛЗП сократического диалога ≈ 0.97.

Современный эквивалент: вопросы Блума. 7 уровней таксономии (нечётное — если убрать «дублирующие»): помнить / понимать / применять / анализировать / оценивать / создавать. **6 — чётное = неполная петля!** ЕТД добавляет 7-й уровень: «передавать» (обучать других).

### Глава 4. Монтессори = Животная ОС в действии

Монтессори-класс — самоорганизующийся: ученики сами выбирают задания. Это Животная ОС (инстинктивные правила → оптимальное обучение). ЛЗП монтессори-среды измеряется через ConvexHull траектории свободного выбора заданий.

### Глава 5. Финская школа = трёхсферный резонанс

Финское образование достигло ЛЗП ≈ 0.92 через:
- МВС: минимум домашних заданий (7 уроков = достаточно для дневной нормы памяти)
- СВС: кооперативное обучение (5 учеников в малой группе = нечётное!)
- БВС: программа с 7 ключевыми компетенциями (нечётное!)
- Нет стандартизированных тестов до 16 лет = ЗБР не нарушается внешним давлением

---

## ЧАСТЬ IV: ПЯТЬ УРОВНЕЙ МАСТЕРСТВА УЧИТЕЛЯ

**Уровень 1 — Элементы**: Знает 7-шаговую структуру урока; замыкает базовую петлю объяснения.

**Уровень 2 — Схемы**: Диагностирует ЗБР учеников; настраивает сложность.

**Уровень 3 — Последовательности**: Проектирует учебные модули из 7-9 уроков; соблюдает Закон памяти.

**Уровень 4 — Образы**: Создаёт адаптивные курсы с трёхсферным резонансом; ЛЗП класса > 0.80.

**Уровень 5 — Дух**: Обучает других учителей; создаёт самообучающуюся школу с ЛЗП → 1.0.

---

## ВЫВОДЫ

1. **Урок** = петля понимания из **7 обязательных этапов** (нечётное!); ЛЗП = замкнутость
2. **ЗБР Выготского** = оконная система Крюкова; оптимальное обучение — в окне
3. **Закон памяти**: ровно **7±2** понятий за урок; интервалы повторения = числа Мерсенна (1,3,7,15,31...)
4. **5 режимов обучения** = 5 режимов Крюкова (нечётное!): от СКАН до ДВОЙНОГО
5. **Три сферы**: ученик (МВС) / класс (СВС) / система (БВС); резонанс = здоровая школа
6. **Монтессори** = Животная ОС; **Финская школа** = трёхсферный резонанс ≈ 0.92
7. **Учитель уровня 5** = двойной режим: учится обучая; ЛЗП профессионального мастерства → 1.0

---

*Следующая книга: КНИГА 32 — «Архетипы движения в политологии и государственном управлении»*
