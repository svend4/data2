# КНИГА 19: АРХЕТИПЫ ДВИЖЕНИЯ В СОЦИАЛЬНЫХ СЕТЯХ

## «Петли влияния: как информация движется по социальным графам»

**Серия:** «Архетипы движения» | **Том 19 из 20**
**Автор:** На основе системы Крюкова — Тотальная Боевая Система

---

## АННОТАЦИЯ

Социальные сети — не просто платформы коммуникации. Это динамические системы, в которых информация, эмоции и поведение движутся по строго определённым траекториям. В этой книге мы покажем, что все паттерны распространения контента, формирования сообществ и возникновения вирусных явлений описываются 12 архетипами движения Крюкова. Информационная петля (производство → распространение → потребление → обратная связь) — это Архетип Петли. Три уровня социальной организации (личность / группа / общество) — это Архетип Трёх Сфер. Мемы, тренды и нарративы — это Архетип Мастер-шаблона. Анализ социальных сетей через эту призму открывает возможности для создания более здоровых информационных экосистем.

---

## ГЛАВА 1: ИНФОРМАЦИОННАЯ ПЕТЛЯ В СОЦИАЛЬНЫХ СЕТЯХ

### 1.1 Петля распространения контента

Каждый успешный пост описывает идеальную петлю:

```
Создатель создаёт контент → Платформа распределяет →
Аудитория потребляет → Реакция (лайк / шер / комментарий) →
Алгоритм усиливает → Расширенная аудитория → Создатель видит отклик →
Создатель создаёт следующий контент (улучшенный)
```

**LCI контента** = степень замкнутости этой петли:
- LCI = 1.0: вирусный контент (петля полностью замкнута, самоусиливается)
- LCI = 0.5: умеренное распространение (частичная петля)
- LCI ≈ 0.0: контент без отклика (петля не закрылась)

### 1.2 Математическая модель распространения

```python
import numpy as np
from scipy.integrate import odeint
from scipy.spatial import ConvexHull
from scipy import sparse
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional, Set
import torch
import torch.nn as nn
from dataclasses import dataclass
from enum import Enum

class ContentType(Enum):
    NEWS = "news"
    ENTERTAINMENT = "entertainment"
    EDUCATIONAL = "educational"
    EMOTIONAL = "emotional"
    CONTROVERSIAL = "controversial"

@dataclass
class ContentItem:
    """Единица контента в социальной сети."""
    content_id: str
    content_type: ContentType
    initial_quality: float    # 0-1: качество / ценность контента
    emotional_valence: float  # -1 до +1: негативный/позитивный
    novelty: float            # 0-1: новизна
    complexity: float         # 0-1: сложность для понимания

class InformationLoopAnalyzer:
    """
    Анализатор информационных петель в социальных сетях.
    Модель SIR + петлевые архетипы Крюкова.
    """

    def __init__(self, n_nodes: int = 10000, avg_connections: int = 50):
        self.n_nodes = n_nodes
        self.avg_connections = avg_connections

        # Нечётное число узлов (закон нечётности для начального посева)
        self.initial_spreaders = 7  # Закон нечётности

    def simulate_content_spread(self, content: ContentItem,
                                 t_max: float = 30.0,
                                 n_points: int = 300) -> Dict:
        """
        Симуляция распространения контента по модели SIR-Loop.

        S = susceptible (видели но не поделились)
        I = infected (активно распространяют)
        R = recovered (переработали, перестали распространять)
        L = loop_closed (дали обратную связь создателю)
        """
        # Параметры, зависящие от типа контента
        beta = self._compute_transmission_rate(content)
        gamma = self._compute_recovery_rate(content)
        lambda_loop = self._compute_loop_closure_rate(content)

        N = float(self.n_nodes)
        S0 = N - self.initial_spreaders
        I0 = float(self.initial_spreaders)
        R0 = 0.0
        L0 = 0.0

        def sir_loop(state, t):
            S, I, R, L = state
            dS = -beta * S * I / N
            dI = beta * S * I / N - gamma * I
            dR = gamma * I - lambda_loop * R
            dL = lambda_loop * R  # Закрытые петли (лайки, репосты создателю)
            return [dS, dI, dR, dL]

        t = np.linspace(0, t_max, n_points)
        solution = odeint(sir_loop, [S0, I0, R0, L0], t)
        S, I, R, L = solution.T

        # Нормализация
        S /= N; I /= N; R /= N; L /= N

        # LCI: отношение замкнутых петель к общему охвату
        total_reach = 1 - S[-1]  # Доля охваченных
        loop_closure = L[-1]
        lci = loop_closure / max(total_reach, 1e-10)

        # Резонанс: скорость распространения vs скорость обратной связи
        spread_rate = beta * I.max()
        feedback_rate = lambda_loop * R.mean()
        resonance = 1.0 - abs(spread_rate - feedback_rate) / max(spread_rate, feedback_rate, 1e-10)

        # Пиковое заражение и время пика
        peak_i = I.max()
        peak_time = t[np.argmax(I)]

        # Viral coefficient (R0 эпидемиологический)
        viral_coeff = beta / gamma

        return {
            'lci': round(lci, 3),
            'resonance': round(float(resonance), 3),
            'viral_coefficient': round(viral_coeff, 3),
            'total_reach_fraction': round(float(1 - S[-1]), 3),
            'peak_infected_fraction': round(float(peak_i), 3),
            'peak_time': round(float(peak_time), 1),
            'loop_closed_fraction': round(float(L[-1]), 3),
            'content_type': content.content_type.value,
            'is_viral': viral_coeff > 1.0,
            'S': S, 'I': I, 'R': R, 'L': L, 't': t,
        }

    def _compute_transmission_rate(self, content: ContentItem) -> float:
        """Скорость передачи = f(эмоциональность, новизна, сложность)."""
        # Высокая эмоциональность (позитивная или негативная) → высокое β
        emotional_factor = abs(content.emotional_valence) * 0.4
        # Новизна стимулирует распространение
        novelty_factor = content.novelty * 0.3
        # Сложность снижает распространение
        complexity_penalty = content.complexity * 0.2

        type_bonus = {
            ContentType.CONTROVERSIAL: 0.3,
            ContentType.EMOTIONAL: 0.25,
            ContentType.ENTERTAINMENT: 0.15,
            ContentType.NEWS: 0.1,
            ContentType.EDUCATIONAL: 0.05,
        }.get(content.content_type, 0.1)

        beta = 0.3 + emotional_factor + novelty_factor - complexity_penalty + type_bonus
        return max(0.05, min(0.95, beta))

    def _compute_recovery_rate(self, content: ContentItem) -> float:
        """Скорость «выздоровления» (люди перестают репостить)."""
        # Качественный контент → медленнее забывают (γ низкий)
        gamma = 0.3 - content.initial_quality * 0.15
        return max(0.05, min(0.8, gamma))

    def _compute_loop_closure_rate(self, content: ContentItem) -> float:
        """Скорость закрытия петли (обратная связь к создателю)."""
        # Позитивный контент → больше обратной связи
        lambda_l = 0.1 + max(0, content.emotional_valence) * 0.2
        return max(0.01, min(0.5, lambda_l))


class GraphLoopDetector:
    """
    Детектор информационных петель в графе социальной сети.
    Петля в графе = цикл (простой граф) = архетип Петли Крюкова.
    """

    def __init__(self, adjacency_dict: Dict[str, List[str]]):
        """adjacency_dict: {node_id: [neighbor_ids]}"""
        self.graph = adjacency_dict
        self.nodes = list(adjacency_dict.keys())

    def detect_influence_loops(self, max_loop_length: int = 7) -> List[Dict]:
        """
        Обнаружение циклов влияния (петель) в социальном графе.
        max_loop_length: максимальная длина петли (≤ 7 для закона памяти).
        """
        # Нечётные длины предпочтительны (закон нечётности)
        preferred_lengths = [3, 5, 7]

        loops_found = []
        visited = set()

        def dfs(node: str, path: List[str], depth: int):
            if depth > max_loop_length:
                return
            for neighbor in self.graph.get(node, []):
                if neighbor == path[0] and len(path) >= 3:
                    # Замкнутая петля найдена
                    loop_len = len(path)
                    lci = 1.0  # Замкнутая петля всегда LCI = 1
                    loops_found.append({
                        'nodes': path.copy(),
                        'length': loop_len,
                        'lci': lci,
                        'is_odd_length': loop_len % 2 != 0,
                        'is_preferred': loop_len in preferred_lengths,
                        'resonance_bonus': 0.2 if loop_len in preferred_lengths else 0.0,
                    })
                elif neighbor not in path:
                    path.append(neighbor)
                    dfs(neighbor, path, depth + 1)
                    path.pop()

        # Запускаем DFS из случайной выборки узлов (≤ 9 — закон памяти)
        sample_size = min(9, len(self.nodes))
        sampled_nodes = self.nodes[:sample_size]

        for start_node in sampled_nodes:
            dfs(start_node, [start_node], 0)

        # Дедупликация петель
        unique_loops = []
        seen_sets = []
        for loop in loops_found:
            node_set = frozenset(loop['nodes'])
            if node_set not in seen_sets:
                seen_sets.append(node_set)
                unique_loops.append(loop)

        return unique_loops

    def compute_network_lci(self, n_sample_pairs: int = 100) -> float:
        """
        LCI всей сети = средняя замкнутость информационных путей.
        Высокий LCI сети = высокая эхо-камерность.
        """
        nodes = list(self.nodes)
        if len(nodes) < 2:
            return 0.0

        closed_paths = 0
        total_paths = 0

        np.random.seed(42)
        for _ in range(min(n_sample_pairs, len(nodes) * (len(nodes) - 1) // 2)):
            i, j = np.random.choice(len(nodes), 2, replace=False)
            source = nodes[i]
            target = nodes[j]

            # BFS от source → target
            path_forward = self._bfs_path(source, target)
            path_back = self._bfs_path(target, source)

            total_paths += 1
            if path_forward is not None and path_back is not None:
                closed_paths += 1

        return closed_paths / max(total_paths, 1)

    def _bfs_path(self, source: str, target: str,
                   max_depth: int = 6) -> Optional[List[str]]:
        """BFS для поиска пути в графе."""
        if source not in self.graph:
            return None
        queue = deque([[source]])
        visited = {source}

        while queue:
            path = queue.popleft()
            node = path[-1]

            if len(path) > max_depth:
                return None

            for neighbor in self.graph.get(node, []):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return None
```

---

## ГЛАВА 2: ТРИ СФЕРЫ СОЦИАЛЬНОЙ ОРГАНИЗАЦИИ

### 2.1 МВС/СВС/БВС социальных сетей

| Сфера | Масштаб | Структуры | Характеристики |
|-------|---------|-----------|----------------|
| **МВС** (микро) | 1–9 человек | Диады, триады, малые группы | Сильные связи, высокое доверие |
| **СВС** (средняя) | 10–150 человек | Сообщества, группы по интересам | Число Данбара = 150 |
| **БВС** (макро) | 150+ | Движения, тренды, культуры | Слабые связи (Грановеттер) |

```python
class SocialThreeSphereAnalyzer:
    """
    Анализатор трёх сфер социальной организации.
    МВС = сильные связи, СВС = Данбар-группа, БВС = слабые связи и тренды.
    """

    # Числа Данбара (нечётные оптимумы!)
    DUNBAR_NUMBERS = {
        'intimate': 5,      # МВС: ближайшие (нечётное!)
        'close_friends': 15,  # МВС внешний слой
        'dunbar_group': 50,   # СВС
        'tribe': 150,         # СВС/БВС граница
        'clan': 500,          # БВС
        'mega_tribe': 1500,   # БВС
    }

    def analyze_user_network(self, user_id: str,
                              connections: Dict[str, float]) -> Dict:
        """
        Анализ сети пользователя.
        connections: {user_id: tie_strength (0-1)}
        """
        # Разделение на сферы по силе связей
        mvs_connections = {u: s for u, s in connections.items() if s >= 0.7}
        svs_connections = {u: s for u, s in connections.items() if 0.3 <= s < 0.7}
        bvs_connections = {u: s for u, s in connections.items() if s < 0.3}

        n_mvs = len(mvs_connections)
        n_svs = len(svs_connections)
        n_bvs = len(bvs_connections)

        # Оптимальные размеры по Данбару
        optimal_mvs = 5   # Нечётное!
        optimal_svs = 50
        optimal_bvs = 150

        # Резонанс: насколько близко к оптимальным числам Данбара
        mvs_resonance = 1.0 - min(1.0, abs(n_mvs - optimal_mvs) / optimal_mvs)
        svs_resonance = 1.0 - min(1.0, abs(n_svs - optimal_svs) / optimal_svs)
        bvs_resonance = 1.0 - min(1.0, abs(n_bvs - optimal_bvs) / optimal_bvs)

        total_resonance = (mvs_resonance + svs_resonance + bvs_resonance) / 3

        # LCI: доля сильных связей (замкнутые петли = сильные связи)
        total = n_mvs + n_svs + n_bvs
        lci = n_mvs / max(total, 1)

        # Средние силы связей
        avg_mvs_strength = np.mean(list(mvs_connections.values())) if mvs_connections else 0
        avg_svs_strength = np.mean(list(svs_connections.values())) if svs_connections else 0
        avg_bvs_strength = np.mean(list(bvs_connections.values())) if bvs_connections else 0

        return {
            'mvs_count': n_mvs,
            'svs_count': n_svs,
            'bvs_count': n_bvs,
            'total_connections': total,
            'lci': round(lci, 3),
            'mvs_resonance': round(mvs_resonance, 3),
            'svs_resonance': round(svs_resonance, 3),
            'bvs_resonance': round(bvs_resonance, 3),
            'total_resonance': round(total_resonance, 3),
            'avg_mvs_strength': round(avg_mvs_strength, 3),
            'avg_svs_strength': round(avg_svs_strength, 3),
            'avg_bvs_strength': round(avg_bvs_strength, 3),
            'network_health': self._assess_network_health(
                n_mvs, n_svs, n_bvs, total_resonance, lci),
        }

    def _assess_network_health(self, n_mvs: int, n_svs: int, n_bvs: int,
                                resonance: float, lci: float) -> str:
        if resonance > 0.7 and lci > 0.3:
            return "Здоровая сеть — три сферы в резонансе"
        elif n_mvs == 0:
            return "Изоляция МВС — нет сильных связей (риск одиночества)"
        elif n_svs == 0:
            return "Пропущена СВС — только близкие или чужие"
        elif lci > 0.8:
            return "Эхо-камера — слишком замкнутая петля (МВС гиперактивна)"
        elif lci < 0.05:
            return "Поверхностная сеть — связи слабые, петли не закрыты"
        else:
            return "Умеренный баланс — возможна оптимизация"

    def detect_echo_chambers(self, community_data: Dict[str, List[str]]) -> List[Dict]:
        """
        Обнаружение эхо-камер (петли с LCI → 1, замкнутые информационные пузыри).
        community_data: {community_id: [user_ids]}
        """
        echo_chambers = []

        for comm_id, members in community_data.items():
            n_members = len(members)
            if n_members < 3:
                continue

            # Нечётное число участников оптимально
            is_odd_size = n_members % 2 != 0

            # Симуляция внутренней связности vs внешней
            # (в реальности — через API данные)
            # Здесь: эвристика по размеру и паттернам
            internal_density = np.random.uniform(0.6, 0.95)  # Высокая внутренняя связность
            external_density = np.random.uniform(0.01, 0.2)  # Низкая внешняя

            # LCI эхо-камеры: отношение внутренних к внешним связям
            echo_lci = internal_density / (internal_density + external_density)

            # Информационное разнообразие (LCI → 1 = нет разнообразия)
            information_diversity = 1.0 - echo_lci

            is_echo_chamber = echo_lci > 0.8

            echo_chambers.append({
                'community_id': comm_id,
                'n_members': n_members,
                'is_odd_size': is_odd_size,
                'echo_lci': round(echo_lci, 3),
                'information_diversity': round(information_diversity, 3),
                'is_echo_chamber': is_echo_chamber,
                'recommendation': (
                    "Критический уровень изоляции — нужны мосты между сообществами"
                    if is_echo_chamber else "Умеренная изоляция"
                ),
            })

        return sorted(echo_chambers, key=lambda x: x['echo_lci'], reverse=True)
```

---

## ГЛАВА 3: МЕМЫ И НАРРАТИВЫ КАК МАСТЕР-ШАБЛОН

### 3.1 Мем = базовый шаблон движения идеи

Мем (по Докинзу) = единица культурной репликации = Мастер-шаблон (ОБД) в социальных сетях.

**Структура мема через ОБД:**
- **Базовый паттерн** = концептуальное ядро (идея)
- **Отклонение** = адаптация к контексту (новый формат)
- **Действие** = репликация (репост, переосмысление)

```python
class MemeEvolutionTracker:
    """
    Трекер эволюции мемов и нарративов.
    Мем = мастер-шаблон. Мутации мема = обновление ОБД.
    """

    def __init__(self):
        self.meme_registry: Dict[str, Dict] = {}
        self.mutation_history: Dict[str, List] = defaultdict(list)

    def register_meme(self, meme_id: str, content_vector: np.ndarray,
                       emotional_valence: float, virality: float) -> None:
        """Регистрация мема в реестре."""
        self.meme_registry[meme_id] = {
            'content_vector': content_vector,
            'emotional_valence': emotional_valence,
            'virality': virality,
            'generation': 0,
            'mutations': [],
            'lci': virality,  # Virality ≈ LCI для мемов
        }

    def simulate_meme_mutation(self, parent_meme_id: str,
                                mutation_rate: float = 0.3) -> Optional[str]:
        """
        Симуляция мутации мема (обновление мастер-шаблона).
        Нечётное число мутаций сохраняет жизнеспособность (закон нечётности).
        """
        if parent_meme_id not in self.meme_registry:
            return None

        parent = self.meme_registry[parent_meme_id]
        parent_vec = parent['content_vector']

        # Мутация вектора (случайный сдвиг)
        n_mutations = np.random.poisson(mutation_rate * len(parent_vec))
        if n_mutations % 2 == 0:
            n_mutations += 1  # Нечётное число мутаций
        n_mutations = min(n_mutations, len(parent_vec))

        mutated_vec = parent_vec.copy()
        mutation_indices = np.random.choice(len(parent_vec), n_mutations, replace=False)
        mutated_vec[mutation_indices] += np.random.normal(0, 0.1, n_mutations)
        mutated_vec = np.clip(mutated_vec, -1, 1)

        # LCI мутации = сходство с родителем
        cosine_sim = np.dot(parent_vec, mutated_vec) / (
            np.linalg.norm(parent_vec) * np.linalg.norm(mutated_vec) + 1e-10)
        mutation_lci = (cosine_sim + 1) / 2  # Нормализация в [0, 1]

        # Вирусность мутанта (частично наследуется)
        child_virality = parent['virality'] * 0.7 + np.random.uniform(0.0, 0.5) * 0.3

        # Новый мем
        child_id = f"{parent_meme_id}_mut_{len(self.mutation_history[parent_meme_id])}"
        self.meme_registry[child_id] = {
            'content_vector': mutated_vec,
            'emotional_valence': parent['emotional_valence'] + np.random.normal(0, 0.1),
            'virality': child_virality,
            'generation': parent['generation'] + 1,
            'parent': parent_meme_id,
            'lci': mutation_lci,
        }

        self.mutation_history[parent_meme_id].append({
            'child_id': child_id,
            'mutation_lci': round(mutation_lci, 3),
            'n_mutations': n_mutations,
            'child_virality': round(child_virality, 3),
        })

        return child_id

    def analyze_meme_fitness(self, meme_id: str) -> Dict:
        """
        Анализ жизнеспособности мема через архетипы Крюкова.
        Фитнес = произведение петли, резонанса и мастер-шаблона.
        """
        if meme_id not in self.meme_registry:
            return {}

        meme = self.meme_registry[meme_id]

        # LCI: вирусность
        lci = meme['lci']

        # Резонанс: баланс между новизной мутации и сохранением ядра
        mutations = self.mutation_history.get(meme_id, [])
        if mutations:
            avg_mutation_lci = np.mean([m['mutation_lci'] for m in mutations])
            # Оптимальный резонанс: мутации сохраняют ~70% исходного (LCI=0.7)
            resonance = 1.0 - abs(avg_mutation_lci - 0.7)
        else:
            resonance = 0.5

        # Сложность мастер-шаблона: число поколений мутаций
        n_generations = meme.get('generation', 0)
        template_complexity = min(1.0, n_generations / 9)  # Закон памяти: ≤ 9 поколений

        # Итоговый фитнес
        fitness = lci * resonance * (1 - abs(template_complexity - 0.5))

        return {
            'meme_id': meme_id,
            'lci': round(lci, 3),
            'resonance': round(resonance, 3),
            'generation': n_generations,
            'n_offspring': len(mutations),
            'fitness_score': round(fitness, 3),
            'survival_prediction': 'Высокая' if fitness > 0.5 else 'Умеренная' if fitness > 0.25 else 'Низкая',
        }
```

---

## ГЛАВА 4: АЛГОРИТМЫ РЕКОМЕНДАЦИЙ КАК АРХЕТИП МАСКИРОВКИ/УГРОЗЫ

### 4.1 Пузырь фильтров = патологическая петля

Алгоритм рекомендаций создаёт «пузырь фильтров» — суперзамкнутую петлю (LCI → 1), где пользователь видит только то, что подтверждает его взгляды.

**Архетип Камуфляж/Угроза:**
- **Камуфляж** = релевантный контент (маскируется под нейтральный)
- **Угроза** = поляризующий контент (скрытая радикализация)

```python
class RecommendationArchetypeAnalyzer:
    """
    Анализатор архетипов алгоритмов рекомендаций.
    Обнаруживает паттерны: пузырь фильтров, радикализацию, эхо-камеры.
    """

    def analyze_recommendation_loop(self,
                                     user_history: List[Dict],
                                     recommendations: List[Dict]) -> Dict:
        """
        Анализ петли рекомендаций.
        user_history: [{'content_id': ..., 'topic': ..., 'engagement': ...}]
        recommendations: [{'content_id': ..., 'topic': ..., 'extremity': ...}]
        """
        # Разнообразие тем в истории
        history_topics = [h['topic'] for h in user_history]
        topic_counts = defaultdict(int)
        for t in history_topics:
            topic_counts[t] += 1

        n_unique_topics = len(topic_counts)
        total_consumed = len(user_history)

        # Энтропия как мера информационного разнообразия
        if total_consumed > 0:
            probs = np.array(list(topic_counts.values())) / total_consumed
            diversity_entropy = -np.sum(probs * np.log(probs + 1e-10))
            max_entropy = np.log(max(n_unique_topics, 1))
            normalized_diversity = diversity_entropy / max(max_entropy, 1e-10)
        else:
            normalized_diversity = 0.0

        # LCI рекомендаций: совпадение тем истории и рекомендаций
        rec_topics = [r['topic'] for r in recommendations]
        overlap_count = sum(1 for t in rec_topics if t in topic_counts)
        recommendation_lci = overlap_count / max(len(rec_topics), 1)

        # Тренд экстремальности
        extremities = [r.get('extremity', 0.5) for r in recommendations]
        avg_extremity = np.mean(extremities) if extremities else 0.5

        # Градиент экстремальности (радикализация?)
        if len(extremities) > 2:
            extremity_trend = np.polyfit(range(len(extremities)), extremities, 1)[0]
        else:
            extremity_trend = 0.0

        # Резонанс: баланс между персонализацией и разнообразием
        # Оптимум: LCI = 0.6 (персонализированно, но не замкнуто)
        personalization_resonance = 1.0 - abs(recommendation_lci - 0.6)

        # Оценка рисков
        risks = []
        if recommendation_lci > 0.85:
            risks.append("Эхо-камера: LCI рекомендаций критически высок")
        if normalized_diversity < 0.3:
            risks.append("Информационная бедность: крайне низкое разнообразие")
        if extremity_trend > 0.02:
            risks.append(f"Тренд радикализации: +{extremity_trend:.3f}/рекомендацию")
        if avg_extremity > 0.7:
            risks.append(f"Высокая экстремальность контента: {avg_extremity:.2f}")

        return {
            'recommendation_lci': round(recommendation_lci, 3),
            'content_diversity': round(normalized_diversity, 3),
            'avg_content_extremity': round(avg_extremity, 3),
            'extremity_trend': round(extremity_trend, 4),
            'personalization_resonance': round(personalization_resonance, 3),
            'filter_bubble_risk': recommendation_lci > 0.75,
            'radicalization_risk': extremity_trend > 0.01,
            'risks': risks,
            'recommendation': self._generate_recommendation(recommendation_lci,
                                                            normalized_diversity,
                                                            extremity_trend),
        }

    def _generate_recommendation(self, lci: float, diversity: float,
                                  trend: float) -> str:
        if lci > 0.85:
            return "Принудительно вводить контент из других тематических сфер (разомкнуть петлю)"
        elif diversity < 0.3:
            return "Увеличить информационное разнообразие: алгоритм случайного исследования"
        elif trend > 0.01:
            return "Ввести фильтр экстремальности: ограничить рекомендации выше порога 0.6"
        else:
            return "Текущий алгоритм в норме — резонанс персонализации и разнообразия сохранён"
```

---

## ГЛАВА 5: ВИРУСНЫЙ МАРКЕТИНГ ЧЕРЕЗ ЗАКОНЫ КРЮКОВА

### 5.1 Законы Крюкова в SMM

**Закон нечётности в контент-стратегии:**
- Оптимальное число постов в неделю: 3, 5, 7 (не 4, не 6!)
- Оптимальное число ключевых сообщений: 3 или 5
- Оптимальное число форматов: 3 (видео + текст + изображение)

**Закон памяти (7±2) в контенте:**
- Заголовок: ≤ 9 слов
- Список преимуществ: 5–9 пунктов
- Hashtags: 5–9 на пост

```python
class ViralContentOptimizer:
    """
    Оптимизатор вирального контента через 12 архетипов Крюкова.
    Создаёт стратегии распространения с максимальным LCI.
    """

    def optimize_posting_strategy(self,
                                   target_audience_size: int,
                                   content_type: ContentType,
                                   budget_posts_per_week: int) -> Dict:
        """
        Оптимизация стратегии постинга.
        Применяет закон нечётности к расписанию.
        """
        # Нечётное число постов в неделю
        if budget_posts_per_week % 2 == 0:
            budget_posts_per_week -= 1  # Уменьшаем до нечётного
        budget_posts_per_week = max(1, budget_posts_per_week)

        # Нечётное число сфер-аудиторий для охвата
        n_audience_spheres = 3  # МВС, СВС, БВС

        # Распределение постов по сферам (1/3 - 1/3 - 1/3)
        posts_per_sphere = budget_posts_per_week // n_audience_spheres
        if posts_per_sphere == 0:
            posts_per_sphere = 1

        # Типы контента для каждой сферы
        sphere_content = {
            'MVS (ближайшие, 1-9)': {
                'format': 'Личные истории, диалоги, упоминания',
                'tone': 'Интимный, доверительный',
                'posts': posts_per_sphere,
                'expected_lci': 0.9,  # Высокий LCI — сильные связи
            },
            'SVS (сообщество, 10-150)': {
                'format': 'Кейсы, обсуждения, вопросы',
                'tone': 'Экспертный, вовлекающий',
                'posts': posts_per_sphere,
                'expected_lci': 0.6,
            },
            'BVS (широкая аудитория, 150+)': {
                'format': 'Вирусные хуки, мемы, тренды',
                'tone': 'Развлекательный, провокационный',
                'posts': budget_posts_per_week - 2 * posts_per_sphere,
                'expected_lci': 0.4,  # Низкий LCI — слабые связи, но широкий охват
            },
        }

        # Общий ожидаемый LCI стратегии (взвешенный)
        total_posts = sum(s['posts'] for s in sphere_content.values())
        weighted_lci = sum(
            s['posts'] * s['expected_lci']
            for s in sphere_content.values()
        ) / max(total_posts, 1)

        # Оптимальные дни постинга (нечётные дни недели оптимальны)
        # Пн=1, Вт=2, Ср=3, Чт=4, Пт=5, Сб=6, Вс=7
        optimal_days = [1, 3, 5, 7][:budget_posts_per_week]  # Нечётные дни

        return {
            'posts_per_week': budget_posts_per_week,
            'is_odd_frequency': budget_posts_per_week % 2 != 0,
            'sphere_strategy': sphere_content,
            'optimal_posting_days': optimal_days,
            'weighted_lci': round(weighted_lci, 3),
            'estimated_reach': int(target_audience_size * weighted_lci * 0.1),
            'resonance_score': round(
                1.0 - abs(weighted_lci - 0.6), 3),  # Оптимум LCI ≈ 0.6
        }

    def design_viral_hook(self, topic: str, archetype: str) -> Dict:
        """
        Создание вирального хука по архетипу Крюкова.
        """
        hook_templates = {
            'loop': f"[Проблема] → [Решение] → [Результат]: {topic}",
            'three_spheres': f"Три уровня {topic}: личный / групповой / общественный",
            'master_template': f"Универсальный шаблон {topic} (работает везде!)",
            'camouflage_threat': f"Скрытая угроза в {topic} — вы её не замечаете",
            'odd_number': f"7 принципов {topic}, которые меняют всё",
            'memory_law': f"5 вещей о {topic}, которые важно помнить",
            'window': f"Открываем окно в {topic}: что скрыто от большинства",
        }

        template = hook_templates.get(archetype, hook_templates['loop'])

        # Оценка хука
        n_words = len(template.split())
        word_compliance = n_words <= 9  # Закон памяти: ≤ 9 слов в хуке

        return {
            'hook': template,
            'archetype_used': archetype,
            'n_words': n_words,
            'memory_law_compliant': word_compliance,
            'predicted_engagement': 'высокое' if word_compliance else 'среднее',
        }
```

---

## ГЛАВА 6: ПЯТЬ УРОВНЕЙ МАСТЕРСТВА В СОЦИАЛЬНЫХ СЕТЯХ

```
УРОВЕНЬ 1 — ЭЛЕМЕНТЫ:      Создание отдельных постов и реакций
УРОВЕНЬ 2 — СХЕМЫ:         Построение последовательностей контента (воронки)
УРОВЕНЬ 3 — ПОСЛЕДОВАТЕЛЬНОСТИ: Управление петлями (контент-стратегия)
УРОВЕНЬ 4 — ОБРАЗЫ:        Восприятие социальной сети как трёхсферной системы
УРОВЕНЬ 5 — ДУХ:           Формирование культурных нарративов и движений
```

### 6.1 Анализатор уровня мастерства аккаунта

```python
class SocialMasteryAnalyzer:
    """
    Анализатор уровня мастерства в социальных сетях.
    Пять уровней Крюкова применительно к SMM.
    """

    MASTERY_THRESHOLDS = {
        1: {'engagement_rate': 0.01, 'posting_frequency': 1,
            'content_variety': 1, 'loop_closure': 0.1},
        2: {'engagement_rate': 0.03, 'posting_frequency': 3,
            'content_variety': 3, 'loop_closure': 0.3},
        3: {'engagement_rate': 0.05, 'posting_frequency': 5,
            'content_variety': 5, 'loop_closure': 0.5},
        4: {'engagement_rate': 0.08, 'posting_frequency': 7,
            'content_variety': 7, 'loop_closure': 0.7},
        5: {'engagement_rate': 0.15, 'posting_frequency': 9,
            'content_variety': 9, 'loop_closure': 0.9},
    }

    MASTERY_NAMES = {
        1: 'ЭЛЕМЕНТЫ (публикует и ждёт)',
        2: 'СХЕМЫ (строит воронки и серии)',
        3: 'ПОСЛЕДОВАТЕЛЬНОСТИ (управляет петлями)',
        4: 'ОБРАЗЫ (видит трёхсферную систему)',
        5: 'ДУХ (формирует культурные движения)',
    }

    def assess_account(self, metrics: Dict) -> Dict:
        """
        Оценка аккаунта по уровням мастерства.
        metrics: {engagement_rate, avg_posts_per_week, n_content_formats, loop_closure_rate}
        """
        scores = []
        for level in range(1, 6):
            thresholds = self.MASTERY_THRESHOLDS[level]
            level_score = 0
            for metric, threshold in thresholds.items():
                value = metrics.get(metric, 0)
                if value >= threshold:
                    level_score += 1
            scores.append(level_score / len(thresholds))

        # Текущий уровень = последний уровень с score ≥ 0.75
        current_level = 1
        for level, score in enumerate(scores, 1):
            if score >= 0.75:
                current_level = level

        # LCI аккаунта = loop_closure_rate
        lci = metrics.get('loop_closure', 0.0)

        # Резонанс = соответствие трёхсферной стратегии
        n_formats = metrics.get('content_variety', 1)
        # Нечётное число форматов = оптимально
        format_resonance = 1.0 if n_formats % 2 != 0 else 0.7

        return {
            'current_mastery_level': current_level,
            'mastery_name': self.MASTERY_NAMES[current_level],
            'level_scores': [round(s, 2) for s in scores],
            'lci': round(lci, 3),
            'format_resonance': round(format_resonance, 3),
            'next_level': min(current_level + 1, 5),
            'next_level_name': self.MASTERY_NAMES[min(current_level + 1, 5)],
            'growth_recommendations': self._recommend_growth(current_level, metrics),
        }

    def _recommend_growth(self, level: int, metrics: Dict) -> List[str]:
        recommendations = []
        if level < 2:
            recommendations.append("Создайте 3 формата контента (видео + текст + фото)")
            recommendations.append("Публикуйте 3 раза в неделю (нечётное число!)")
        elif level < 3:
            recommendations.append("Создайте контентную воронку: осведомлённость → интерес → действие")
            recommendations.append("Отслеживайте и закрывайте информационные петли (отвечайте на ВСЕ комментарии)")
        elif level < 4:
            recommendations.append("Разделите аудиторию на три сферы (МВС/СВС/БВС) и создайте контент для каждой")
            recommendations.append("Используйте 5-7 форматов контента (нечётное число)")
        elif level < 5:
            recommendations.append("Создайте собственный нарратив / движение")
            recommendations.append("Постройте экосистему создателей контента вокруг вашей идеи")
        return recommendations
```

---

## ГЛАВА 7: ТЕОРЕМА КРЮКОВА В СОЦИАЛЬНЫХ СЕТЯХ

**7 условий максимальной эффективности в социальных сетях:**

1. **Петля замкнута** — каждый пост получает обратную связь и порождает следующий
2. **Три сферы резонируют** — контент для МВС, СВС и БВС публикуется равномерно
3. **Мастер-шаблон сохранён** — мемы мутируют, сохраняя ≥70% ядра (LCI мутации ≥ 0.7)
4. **Камуфляж/Угроза различимы** — фильтр экстремальности работает (LCI рекомендаций ≤ 0.75)
5. **Закон нечётности** — посты в неделю: 3, 5, 7; форматы: 3, 5; ключевые сообщения: 5, 7
6. **Закон памяти** — заголовки ≤ 9 слов, пункты списков 5–9, хэштеги 5–9
7. **Режим адаптирован** — алгоритм выявляет текущий режим (рост / удержание / восстановление)

**При выполнении всех 7 условий — максимальный охват при минимальных ресурсах.**

---

## ЗАКЛЮЧЕНИЕ

Социальные сети — это живая система движения идей, подчинённая тем же 12 архетипам, что управляют движением в боевых искусствах, биологии, финансах и физике. Информационные петли, трёхсферная организация сообществ, эволюция мемов как мастер-шаблонов — всё это проявления универсальных законов движения Крюкова.

Ключевые выводы:
- **Вирусность** = высокий LCI информационной петли
- **Эхо-камера** = патологически высокий LCI (> 0.85)
- **Здоровое сообщество** = три сферы в резонансе (Данбар + слабые связи)
- **Алгоритм рекомендаций** = архетип Камуфляж/Угроза (оптимум LCI ≈ 0.6)
- **Контент-стратегия** = нечётные числа постов, форматов и ключевых сообщений

---

*Следующая книга: КНИГА 20 — «Единая теория движения: Великое объединение 12 архетипов»*

**© Серия «Архетипы движения» | Том 19**
