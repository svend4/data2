# ЕДИНАЯ ТЕОРИЯ ДВИЖЕНИЯ (ЕТД)
## Том 48: ЕТД и Архитектура ИИ-систем
### «Искусственный интеллект как иерархия замкнутых орбит»

**Автор**: Крюков
**Серия III** — Математические основания и прикладные следствия
**Блок 2** — Прикладные науки

---

## 📋 ДВУХВЕРСИОННЫЙ ДОКУМЕНТ

> Этот файл содержит **ДВЕ версии** параллельно — оригинал и расширение.

| Параметр | ВЕРСИЯ 1.0 (оригинал) | ВЕРСИЯ 2.0 (ЧВС-апдейт) |
|---|---|---|
| Число сфер ИИ-системы | 3 (МВС / СВС / БВС) | **4 (МВС / СВС / БВС / ЧВС)** |
| МВС | Данные / токены / эмбеддинги | Данные / токены / эмбеддинги |
| СВС | Модель / архитектура / веса | Модель / архитектура / веса |
| БВС | Деплой / сервис / мониторинг | Деплой / сервис / мониторинг |
| ЧВС | — | **Адаптер / Fine-tune / Domain** (LoRA, Prefix, Prompt) |
| Аудитор | `AISystemETDAuditor` (7 аксиом) | **`FourSphereAIAuditor`** (9 аксиом) |
| Добавлены аксиомы | — | **A8** (ЧВС-наличие) + **A9** (ЧВС-резонанс ранга) |
| ЛЗП формула | 3-сферная | **4-сферная** (additive / multiplicative / weighted) |
| Тип ЧВС | — | `AdapterType`: LoRA / PrefixTuning / AdapterLayers / PromptTuning |
| Смена домена | Полный retraining | **Сменить ЧВС-адаптер** (`CHS_ADAPTER_LIBRARY`) |
| Источник v2.0 | — | Том 101, Часть IV |

---

## ══════════════════════════════════════════
## ВЕРСИЯ 1.0 — ОРИГИНАЛ (3 СФЕРЫ, ПОЛНАЯ)
## ══════════════════════════════════════════

---

## АННОТАЦИЯ

Любая успешная ИИ-система — это иерархия замкнутых орбит. В данном томе доказывается, что архитектурные решения, обеспечивающие высокое качество ИИ, подчиняются семи аксиомам ЕТД. Трансформер = три сферы (QKV). Обучение с подкреплением = петля. Масштабный закон Чинчиллы = степенной закон с нечётными показателями. Иерархия агентов: 5 уровней (нечётное!). ЛЗП системы = отношение выпуклой оболочки орбиты активаций к её описывающему боксу; системы с ЛЗП > 0.85 достигают emergent abilities. Три сферы ИИ: данные (МВС) — модель (СВС) — деплой (БВС).

**Ключевые слова**: ЛЗП, трансформер, агентные системы, масштабный закон, RLHF, RAG, ЕТД

---

## ЧАСТЬ I — ТЕОРЕТИЧЕСКАЯ

### Глава 1. ИИ-архитектура через призму ЕТД

#### 1.1 Нейронная сеть как орбита в пространстве активаций

**Определение 48.1** (Активационная орбита):
Орбита нейронной сети γ_L: ℝⁿ → ℝᵐ — траектория входных данных через L слоёв: γ(x) = f_L ∘ f_{L-1} ∘ … ∘ f_1(x).

ЛЗП активаций = μ(CH({f_l(x) : x ∈ X})) / μ(BB({f_l(x) : x ∈ X})) на слое l.

#### 1.2 Закон нечётных в ИИ-архитектурах

| Структура | Количество | Чётность |
|-----------|-----------|---------|
| Головы внимания (GPT-3) | 96 → ключевые слои 1,3,5,…,95 | НЕЧЁТНЫЕ |
| Слои трансформера (GPT-4, оценка) | ~120 → нечётных: 61 | 61 = НЕЧЁТНОЕ |
| Уровни иерархии агентов (ЕТД) | 5 | НЕЧЁТНОЕ |
| Шагов RLHF-цикла | 7 (sample→rank→train→eval→deploy→monitor→iterate) | НЕЧЁТНОЕ |
| Размерность KV-кэша (головы) | 128 → реальных информативных измерений | → нечётное подпространство |
| Этапов RAG-пайплайна | 5 (retrieve→rerank→augment→generate→verify) | НЕЧЁТНОЕ |
| Уровней знаний (онтология) | 5 (данные→информация→знания→мудрость→понимание) | НЕЧЁТНОЕ |
| Итераций Constitutional AI | 3 (critique→revise→repeat) | НЕЧЁТНОЕ |

**Теорема 48.1** (Нечётность эффективных архитектур):
Количество уровней в иерархической ИИ-архитектуре, обеспечивающих emergent abilities, нечётно.
*Основание*: Из масштабного закона Чинчиллы: L_opt(C) = C^α, где α ≈ 0.5 — но на нечётных ступенях мощности (C = 10^{2k+1}) происходят качественные скачки. □

#### 1.3 Три сферы ИИ-системы

| Сфера | Масштаб | Компонент | Ответственность |
|-------|---------|-----------|----------------|
| МВС (микро) | Токен, эмбеддинг | Данные, предобработка | DataEng, MLOps |
| СВС (мезо) | Слой, внимание, блок | Модель, архитектура | ML Research |
| БВС (макро) | Сервис, продукт | Деплой, A/B, мониторинг | Platform, Product |

**Трёхсферный резонанс ИИ-системы**:
R₃ = 1 − 0.5 · Σ|budget_fraction_i − 1/3|, где budget_fraction_i — доля бюджета на каждую сферу.

#### 1.4 Трансформер как реализация трёх сфер

Механизм внимания: Attention(Q, K, V) = softmax(QKᵀ / √d_k) · V

- **Q (Query)** = МВС: текущий запрос (что ищем?)
- **K (Key)** = СВС: контекстный индекс (что доступно?)
- **V (Value)** = БВС: содержательный ответ (что берём?)

Три матрицы = три сферы ЕТД в самом сердце трансформера!

#### 1.5 Масштабный закон и ЕТД

Закон Чинчиллы (Hoffmann et al., 2022):
N_opt = C^0.5, D_opt = C^0.5 — оптимальные параметры и токены.

ЕТД-интерпретация: коэффициент 0.5 = 1/2 → граница между «чётным» и «нечётным» режимом. Модели при N = 10^{2k+1} (нечётная степень десятки: 10¹, 10³, 10⁵, 10⁷, 10⁹) демонстрируют качественные скачки (emergent abilities согласно Wei et al., 2022).

#### 1.6 Архетипы ЕТД в ИИ-архитектуре

| Архетип ЕТД | ИИ-манифестация |
|-------------|----------------|
| Петля | Обучающий цикл (forward→loss→backward→update); RLHF loop |
| Три сферы | Q/K/V в Attention; данные/модель/деплой |
| Шаблон | Системный промпт; few-shot примеры; LoRA base |
| Камуфляж/Угроза | Adversarial примеры; prompt injection; jailbreak |
| Оконная система | Контекстное окно; RAG retrieval window; beam search |
| Закон нечётных | 5 уровней агентов; 7 шагов RLHF; 3 этапа Constitutional AI |
| Чёрный ящик | Foundation model как black box через API |
| Режимы | Greedy / Beam / Top-p / Top-k / Sampling = 5 режимов! |
| Животный ОС | In-context learning (аналог импринтинга) |
| Пять уровней | Токен→Слой→Блок→Модель→Агентная система |
| Закон памяти | Контекстное окно = рабочая память; KV-кэш = долговременная |
| Дистанция-сложность | Чем длиннее цепочка рассуждений, тем больше шагов нужно |

---

## ЧАСТЬ II — ПРОГРАММНАЯ РЕАЛИЗАЦИЯ

```python
"""
VOLUME 48 — ЕТД и Архитектура ИИ-систем
Kryukov Unified Theory of Movement
"""

import numpy as np
from scipy.spatial import ConvexHull
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from enum import Enum
import warnings


# ─────────────────────────────────────────────
# БАЗОВЫЕ СТРУКТУРЫ
# ─────────────────────────────────────────────

class AILevel(Enum):
    """5 уровней ИИ-системы (нечётное!) = пять уровней ЕТД"""
    TOKEN       = 1  # Токен, эмбеддинг (МВС)
    LAYER       = 2  # Слой, блок внимания
    MODEL       = 3  # Полная модель (СВС)
    AGENT       = 4  # Агент с инструментами
    MULTI_AGENT = 5  # Мульти-агентная система (БВС)


class InferenceMode(Enum):
    """5 режимов инференса (нечётное!) = 5 режимов ЕТД"""
    GREEDY      = "greedy"      # Детерминированный (ТОЧНЫЙ)
    BEAM        = "beam"        # Лучевой поиск (ПОСЛЕДОВАТЕЛЬНЫЙ)
    TOP_P       = "top_p"       # Nucleus sampling (АДАПТИВНЫЙ)
    TOP_K       = "top_k"       # Top-K sampling (СКАНИРОВАНИЕ)
    SPECULATIVE = "speculative" # Спекулятивный декодинг (ДВОЙНОЙ)


@dataclass
class TransformerConfig:
    """Конфигурация трансформера"""
    n_layers: int           # Число слоёв (оптимально нечётное!)
    n_heads: int            # Число голов внимания (кратно n_layers)
    d_model: int            # Размерность модели
    d_ff: int               # Размерность FF-слоя (обычно 4×d_model)
    context_length: int     # Длина контекста
    vocab_size: int         # Размер словаря


@dataclass
class AgentConfig:
    """Конфигурация агента"""
    agent_id: str
    level: AILevel
    n_tools: int            # Число инструментов (оптимально нечётное!)
    memory_k: int           # Размер памяти (7±2 — закон Миллера!)
    can_spawn_subagents: bool = False


@dataclass
class TrainingRun:
    """Метрики тренировочного запуска"""
    step: int
    train_loss: float
    val_loss: float
    learning_rate: float
    tokens_seen: int
    grad_norm: float = 1.0


# ─────────────────────────────────────────────
# 1. ActivationOrbitAnalyzer
# ─────────────────────────────────────────────

class ActivationOrbitAnalyzer:
    """
    ЛЗП орбиты активаций нейронной сети.
    Активации L слоёв → орбита в пространстве представлений → ЛЗП.
    Архетип ЕТД: ПЕТЛЯ (forward pass) + ЧЁРНЫЙ ЯЩИК
    """

    def compute_activation_lci(self, activations_per_layer: List[np.ndarray]) -> Dict:
        """
        ЛЗП активаций по слоям.
        activations_per_layer: список массивов shape (batch, d_model).
        """
        n_layers = len(activations_per_layer)
        if n_layers < 3:
            return {'lci': 0.0, 'error': 'Нужно минимум 3 слоя'}

        # Нечётное число слоёв!
        if n_layers % 2 == 0:
            n_layers -= 1
            activations_per_layer = activations_per_layer[:n_layers]

        # Средние активации по батчу для каждого слоя
        layer_means = np.array([a.mean(axis=0) if a.ndim > 1 else a
                                for a in activations_per_layer[:n_layers]])

        # PCA: d_model → 3D (нечётное!)
        if layer_means.shape[1] > 3:
            mean = layer_means.mean(axis=0)
            centered = layer_means - mean
            try:
                U, S, Vt = np.linalg.svd(centered, full_matrices=False)
                orbit_3d = centered @ Vt[:3].T
            except Exception:
                orbit_3d = layer_means[:, :3]
        else:
            orbit_3d = layer_means

        try:
            hull = ConvexHull(orbit_3d)
            ch_vol = hull.volume
        except Exception:
            ch_vol = 0.0

        bb_vol = np.prod(orbit_3d.max(0) - orbit_3d.min(0)) + 1e-10
        lci = min(ch_vol / bb_vol, 1.0)

        # Норма активаций по слоям (должна расти нечётно!)
        norms = [float(np.linalg.norm(a.mean(axis=0) if a.ndim > 1 else a))
                 for a in activations_per_layer[:n_layers]]
        norm_trend = (norms[-1] - norms[0]) / (abs(norms[0]) + 1e-10)

        return {
            'lci': round(lci, 4),
            'n_layers': n_layers,
            'is_odd_layers': n_layers % 2 == 1,
            'activation_norm_trend': round(norm_trend, 4),
            'emergent_potential': lci > 0.85,  # Порог emergent abilities!
            'grade': self._grade_activation(lci)
        }

    def compute_attention_orbit_lci(self, attention_weights: np.ndarray) -> Dict:
        """
        ЛЗП орбиты весов внимания.
        attention_weights: (n_heads, seq_len, seq_len) — матрицы внимания.
        Q,K,V = три сферы ЕТД!
        """
        n_heads, seq_len, _ = attention_weights.shape

        # Нечётное число голов!
        if n_heads % 2 == 0:
            n_heads -= 1
            attention_weights = attention_weights[:n_heads]

        # Для каждой головы: вектор диагонального внимания (self-attention)
        head_profiles = []
        for h in range(n_heads):
            diag = np.diag(attention_weights[h])
            head_profiles.append([
                float(diag.mean()),   # Среднее self-внимание
                float(diag.std()),    # Разброс
                float(attention_weights[h].max()),  # Максимум
            ])

        orbit = np.array(head_profiles)

        try:
            hull = ConvexHull(orbit)
            ch_vol = hull.volume
        except Exception:
            ch_vol = 0.0

        bb_vol = np.prod(orbit.max(0) - orbit.min(0)) + 1e-10
        lci = min(ch_vol / bb_vol, 1.0)

        # Три сферы голов внимания:
        q_heads = attention_weights[:n_heads//3 + 1]   # МВС: локальные
        k_heads = attention_weights[n_heads//3:2*n_heads//3]  # СВС: средние
        v_heads = attention_weights[2*n_heads//3:]     # БВС: глобальные

        entropy = lambda w: -np.sum(w * np.log(w + 1e-10), axis=-1).mean()
        entropies = np.array([entropy(q_heads.mean(0)),
                               entropy(k_heads.mean(0)),
                               entropy(v_heads.mean(0))])
        fracs = entropies / (entropies.sum() + 1e-10)
        r3 = 1.0 - 0.5 * np.sum(np.abs(fracs - 1/3))

        return {
            'lci': round(lci, 4),
            'n_heads': n_heads,
            'is_odd_heads': n_heads % 2 == 1,
            'three_sphere_resonance_qkv': round(r3, 4),
            'grade': 'Богатое внимание' if lci > 0.7 else 'Монотонное внимание'
        }

    def _grade_activation(self, lci: float) -> str:
        if lci >= 0.85: return 'A — Emergent abilities возможны'
        if lci >= 0.70: return 'B — Богатые представления'
        if lci >= 0.50: return 'C — Стандартные представления'
        if lci >= 0.30: return 'D — Ограниченные представления'
        return 'E — Коллапс представлений (dead neurons)'


# ─────────────────────────────────────────────
# 2. TrainingLoopETDAnalyzer
# ─────────────────────────────────────────────

class TrainingLoopETDAnalyzer:
    """
    Анализ цикла обучения через ЕТД.
    Тренировочный цикл = петля ЕТД.
    Loss curve → орбита (шаг, train_loss, val_loss) → ЛЗП сходимости.
    Архетип ЕТД: ПЕТЛЯ + ОКОННАЯ СИСТЕМА (learning rate schedule)
    """

    def compute_training_lci(self, runs: List[TrainingRun]) -> Dict:
        """
        ЛЗП тренировочной орбиты.
        (step, train_loss, val_loss) → 3D орбита → ЛЗП.
        """
        n = len(runs)
        if n < 4:
            return {'lci': 0.0, 'error': 'Мало шагов'}

        # Нечётное число точек!
        if n % 2 == 0:
            n -= 1
            runs = runs[:n]

        max_step = runs[-1].step + 1
        orbit = np.array([
            [r.step / max_step,
             min(r.train_loss, 10.0) / 10.0,
             min(r.val_loss, 10.0) / 10.0]
            for r in runs[:n]
        ])

        try:
            hull = ConvexHull(orbit)
            ch_vol = hull.volume
        except Exception:
            ch_vol = 0.0

        bb_vol = np.prod(orbit.max(0) - orbit.min(0)) + 1e-10
        lci = min(ch_vol / bb_vol, 1.0)

        # Обобщение: val_loss должен следовать за train_loss
        train_losses = np.array([r.train_loss for r in runs[:n]])
        val_losses   = np.array([r.val_loss for r in runs[:n]])
        generalization_gap = float((val_losses - train_losses).mean())
        overfit_score = max(0.0, generalization_gap / (train_losses.mean() + 1e-10))

        # Закон нечётных: шаги с warmup = нечётные числа
        n_warmup_candidates = [s for s in [1000, 3000, 5000, 7000, 9000]
                               if runs[-1].step > s]  # Все нечётные!

        return {
            'lci': round(lci, 4),
            'n_steps': n,
            'final_train_loss': round(float(train_losses[-1]), 4),
            'final_val_loss': round(float(val_losses[-1]), 4),
            'generalization_gap': round(generalization_gap, 4),
            'overfit_score': round(overfit_score, 4),
            'recommended_warmup_steps': n_warmup_candidates[-1] if n_warmup_candidates else 1000,
            'grade': self._grade_training(lci, overfit_score)
        }

    def compute_scaling_law_lci(self, model_sizes: List[int],
                                  val_losses: List[float]) -> Dict:
        """
        ЛЗП масштабного закона Чинчиллы.
        log(N) vs log(L) → орбита → ЛЗП степенного закона.
        """
        if len(model_sizes) < 3:
            return {'lci': 0.0}

        log_n = np.log10(model_sizes)
        log_l = np.log(val_losses)

        orbit = np.column_stack([log_n, log_l])

        try:
            hull = ConvexHull(orbit)
            ch_area = hull.volume
        except Exception:
            ch_area = 0.0

        bb_area = np.prod(orbit.max(0) - orbit.min(0)) + 1e-10
        lci = min(ch_area / bb_area, 1.0)

        # Оцениваем показатель степени (должен быть ≈ -0.076 по Чинчилле)
        coeffs = np.polyfit(log_n, log_l, 1)
        scaling_exponent = float(coeffs[0])

        # Нечётные степени 10: 1M, 1B, 1T, 1000T = 10^6, 10^9, 10^12, 10^15
        # (показатели 6, 9, 12, 15 → нечётные кратны 3!)
        emergent_thresholds = [1e6, 1e9, 1e12, 1e15]  # Все нечётные кратности

        return {
            'scaling_lci': round(lci, 4),
            'scaling_exponent': round(scaling_exponent, 4),
            'n_model_sizes': len(model_sizes),
            'emergent_thresholds': emergent_thresholds,
            'follows_power_law': abs(scaling_exponent + 0.076) < 0.05,
        }

    def _grade_training(self, lci: float, overfit: float) -> str:
        score = lci * (1.0 - min(overfit, 1.0))
        if score >= 0.70: return 'A — Отличная сходимость, нет переобучения'
        if score >= 0.50: return 'B — Хорошее обучение'
        if score >= 0.30: return 'C — Умеренное обучение, есть дисбаланс'
        return 'D — Проблемное обучение (divergence или overfit)'


# ─────────────────────────────────────────────
# 3. RLHFLoopETDAnalyzer
# ─────────────────────────────────────────────

class RLHFLoopETDAnalyzer:
    """
    Анализ цикла RLHF через ЕТД.
    7 шагов RLHF = нечётный полный цикл (Архетип: ПЕТЛЯ).
    Constitutional AI: 3 этапа (Архетип: ТРИ СФЕРЫ).
    """

    # 7 шагов RLHF (нечётное!)
    RLHF_STEPS = [
        'sample_responses',     # 1. Генерируем ответы
        'human_rank',           # 2. Люди ранжируют
        'train_reward_model',   # 3. Обучаем модель вознаграждения
        'ppo_optimization',     # 4. PPO-оптимизация политики
        'safety_evaluation',    # 5. Оценка безопасности
        'deploy_checkpoint',    # 6. Деплой чекпоинта
        'monitor_and_iterate',  # 7. Мониторинг → следующая итерация
    ]

    # 3 этапа Constitutional AI (нечётное!)
    CAI_STAGES = ['critique', 'revise', 'repeat']

    def compute_rlhf_lci(self, reward_scores: List[float],
                          safety_scores: List[float],
                          iteration_ids: List[int]) -> Dict:
        """
        ЛЗП RLHF-цикла.
        Орбита: (итерация, reward, safety) → ЛЗП качества RLHF.
        """
        n = len(reward_scores)
        assert len(safety_scores) == n

        if n < 3:
            return {'lci': 0.0}

        if n % 2 == 0:
            n -= 1

        t_norm = np.array(iteration_ids[:n]) / (max(iteration_ids[:n]) + 1)
        r_norm = np.array(reward_scores[:n])
        s_norm = np.array(safety_scores[:n])

        orbit = np.column_stack([t_norm, r_norm, s_norm])

        try:
            hull = ConvexHull(orbit)
            ch_vol = hull.volume
        except Exception:
            ch_vol = 0.0

        bb_vol = np.prod(orbit.max(0) - orbit.min(0)) + 1e-10
        lci = min(ch_vol / bb_vol, 1.0)

        # Три сферы RLHF: полезность (МВС) / безопасность (СВС) / честность (БВС)
        helpfulness = float(np.mean(reward_scores[:n]))
        safety      = float(np.mean(safety_scores[:n]))
        honesty     = float(1.0 - np.std(reward_scores[:n]))  # Консистентность = честность

        fracs = np.array([helpfulness, safety, honesty])
        fracs = np.clip(fracs, 0, 1)
        fracs /= (fracs.sum() + 1e-10)
        r3 = 1.0 - 0.5 * np.sum(np.abs(fracs - 1/3))

        return {
            'rlhf_lci': round(lci, 4),
            'n_iterations': n,
            'is_odd_iterations': n % 2 == 1,
            'n_rlhf_steps': len(self.RLHF_STEPS),     # 7 — нечётное!
            'n_cai_stages': len(self.CAI_STAGES),       # 3 — нечётное!
            'helpfulness': round(helpfulness, 4),
            'safety': round(safety, 4),
            'three_sphere_resonance_hsh': round(r3, 4),
            'aligned': lci > 0.7 and r3 > 0.6,
        }

    def simulate_cai_refinement(self, initial_response_score: float,
                                 n_rounds: int = 3) -> Dict:
        """
        Симуляция Constitutional AI (3 раунда — нечётное!).
        Каждый раунд: critique → revise.
        """
        if n_rounds % 2 == 0:
            n_rounds += 1  # Нечётное!

        scores = [initial_response_score]
        for r in range(n_rounds):
            # Critique улучшает на 15–20% за раунд (нелинейный рост)
            improvement = 0.15 * (1 - scores[-1]) * (1 + 0.1 * r)
            new_score = min(scores[-1] + improvement, 1.0)
            scores.append(new_score)

        # Орбита улучшений
        t = np.linspace(0, 1, len(scores))
        orbit = np.column_stack([t, scores])

        try:
            ch_area = ConvexHull(orbit).volume
        except Exception:
            ch_area = 0.0

        bb_area = np.prod(orbit.max(0) - orbit.min(0)) + 1e-10
        lci = min(ch_area / bb_area, 1.0)

        return {
            'n_rounds': n_rounds,            # Нечётное!
            'initial_score': round(initial_response_score, 4),
            'final_score': round(scores[-1], 4),
            'improvement': round(scores[-1] - initial_response_score, 4),
            'cai_lci': round(lci, 4),
            'stages': self.CAI_STAGES * (n_rounds // 3 + 1),
        }


# ─────────────────────────────────────────────
# 4. AgentHierarchyETDAnalyzer
# ─────────────────────────────────────────────

class AgentHierarchyETDAnalyzer:
    """
    Анализ иерархии агентов через ЕТД.
    5 уровней агентной системы (нечётное!).
    Архетип: ПЯТЬ УРОВНЕЙ + ОКОННАЯ СИСТЕМА (tool calls) + ТРИ СФЕРЫ
    """

    # 5 уровней агентной иерархии (нечётное!)
    AGENT_LEVELS = {
        1: 'Токен-предсказатель (базовый LLM)',
        2: 'Рассуждающий агент (CoT)',
        3: 'Агент с инструментами (ReAct)',
        4: 'Оркестрирующий агент (мульти-шаговый)',
        5: 'Мета-агент (управляет другими агентами)',
    }

    def compute_agent_lci(self, configs: List[AgentConfig],
                           task_success_rates: List[float]) -> Dict:
        """
        ЛЗП агентной системы.
        Орбита: (уровень, n_tools, success_rate) в 3D.
        """
        n = len(configs)
        assert len(task_success_rates) == n

        if n < 3:
            return {'lci': 0.0}

        if n % 2 == 0:
            n -= 1

        orbit = np.array([
            [c.level.value / 5.0,
             min(c.n_tools, 21) / 21.0,  # 21 = 3×7 — нечётное!
             task_success_rates[i]]
            for i, c in enumerate(configs[:n])
        ])

        try:
            hull = ConvexHull(orbit)
            ch_vol = hull.volume
        except Exception:
            ch_vol = 0.0

        bb_vol = np.prod(orbit.max(0) - orbit.min(0)) + 1e-10
        lci = min(ch_vol / bb_vol, 1.0)

        # Три сферы агентной системы: восприятие / рассуждение / действие
        perception_agents  = [c for c in configs[:n] if c.level.value <= 2]
        reasoning_agents   = [c for c in configs[:n] if c.level.value == 3]
        action_agents      = [c for c in configs[:n] if c.level.value >= 4]

        counts = np.array([len(perception_agents), len(reasoning_agents), len(action_agents)],
                          dtype=float)
        fracs = counts / (counts.sum() + 1e-10)
        r3 = 1.0 - 0.5 * np.sum(np.abs(fracs - 1/3))

        # Закон памяти: память агента = 7±2
        memory_compliance = float(np.mean([
            max(0, 1 - abs(c.memory_k - 7) / 5) for c in configs[:n]
        ]))

        return {
            'lci': round(lci, 4),
            'n_agents': n,
            'is_odd_agents': n % 2 == 1,
            'three_sphere_resonance': round(r3, 4),
            'memory_law_compliance': round(memory_compliance, 4),
            'avg_success_rate': round(float(np.mean(task_success_rates[:n])), 4),
            'max_level': max(c.level.value for c in configs[:n]),
            'grade': self._grade_agents(lci, r3)
        }

    def design_optimal_agent_system(self, task_complexity: int = 5) -> Dict:
        """
        Проектирование оптимальной агентной системы по ЕТД.
        task_complexity: 1-5 (нечётные уровни!).
        """
        if task_complexity % 2 == 0:
            task_complexity += 1  # Нечётное!

        n_agents = task_complexity  # 1, 3, 5 агентов — нечётное!
        n_tools_per_agent = 7       # 7 инструментов — нечётное!
        memory_k = 7                # Миллер 7±2!
        max_level = min(task_complexity, 5)

        return {
            'n_agents': n_agents,       # Нечётное!
            'n_tools_each': n_tools_per_agent,  # 7 — нечётное!
            'memory_k': memory_k,       # 7 — нечётное!
            'max_hierarchy_level': max_level,
            'agent_levels': [min(i + 1, 5) for i in range(n_agents)],
            'total_tools': n_agents * n_tools_per_agent,
            'etd_compliance': 'Полное (нечётные агенты, 7 инструментов, память 7±2)'
        }

    def _grade_agents(self, lci: float, r3: float) -> str:
        score = 0.5 * lci + 0.5 * r3
        if score >= 0.80: return 'A — Оптимальная агентная архитектура'
        if score >= 0.60: return 'B — Эффективная система'
        if score >= 0.40: return 'C — Базовая агентная система'
        return 'D — Неструктурированная система'


# ─────────────────────────────────────────────
# 5. RAGPipelineETDAnalyzer
# ─────────────────────────────────────────────

class RAGPipelineETDAnalyzer:
    """
    Анализ RAG-пайплайна через ЕТД.
    5 шагов RAG = нечётный цикл (Архетип: ПЕТЛЯ + ОКОННАЯ СИСТЕМА).
    """

    # 5 шагов RAG (нечётное!)
    RAG_STEPS = [
        'retrieve',    # Поиск релевантных документов
        'rerank',      # Переранжирование
        'augment',     # Добавление в контекст (ОКОННАЯ СИСТЕМА)
        'generate',    # Генерация ответа
        'verify',      # Верификация (замыкание петли)
    ]

    def compute_rag_lci(self, retrieval_scores: List[float],
                         generation_quality: List[float],
                         query_ids: List[int]) -> Dict:
        """
        ЛЗП RAG-пайплайна.
        (запрос, retrieval_score, generation_quality) → орбита → ЛЗП.
        """
        n = min(len(retrieval_scores), len(generation_quality), len(query_ids))
        if n < 3:
            return {'lci': 0.0}

        if n % 2 == 0:
            n -= 1

        t = np.array(query_ids[:n]) / (max(query_ids[:n]) + 1)
        r = np.array(retrieval_scores[:n])
        g = np.array(generation_quality[:n])

        orbit = np.column_stack([t, r, g])

        try:
            hull = ConvexHull(orbit)
            ch_vol = hull.volume
        except Exception:
            ch_vol = 0.0

        bb_vol = np.prod(orbit.max(0) - orbit.min(0)) + 1e-10
        lci = min(ch_vol / bb_vol, 1.0)

        # Корреляция retrieval → generation (RAG эффективен, если высокая)
        correlation = float(np.corrcoef(r, g)[0, 1]) if len(r) > 1 else 0.0

        # Оконная система: контекстное окно = N документов
        # Оптимум = 7 документов (нечётное!)
        optimal_k_docs = 7
        rag_k = n  # Текущее k (нечётное!)

        return {
            'rag_lci': round(lci, 4),
            'n_queries': n,
            'n_rag_steps': len(self.RAG_STEPS),       # 5 — нечётное!
            'optimal_k_docs': optimal_k_docs,          # 7 — нечётное!
            'retrieval_generation_correlation': round(correlation, 4),
            'avg_retrieval_score': round(float(r.mean()), 4),
            'avg_generation_quality': round(float(g.mean()), 4),
            'grade': 'Эффективный RAG' if lci > 0.65 and correlation > 0.5 else 'RAG требует настройки'
        }


# ─────────────────────────────────────────────
# 6. AISystemETDAuditor
# ─────────────────────────────────────────────

class AISystemETDAuditor:
    """
    Полный ЕТД-аудит ИИ-системы по 7 аксиомам.
    Архетип: ПЯТЬ УРОВНЕЙ + ЧЁРНЫЙ ЯЩИК
    """

    def __init__(self):
        self.activation_analyzer = ActivationOrbitAnalyzer()
        self.training_analyzer   = TrainingLoopETDAnalyzer()
        self.rlhf_analyzer       = RLHFLoopETDAnalyzer()
        self.agent_analyzer      = AgentHierarchyETDAnalyzer()
        self.rag_analyzer        = RAGPipelineETDAnalyzer()

    def audit_ai_system(self, system_config: Dict,
                         training_runs: List[TrainingRun],
                         agent_configs: List[AgentConfig]) -> Dict:
        """
        7-аксиомный аудит ИИ-системы.
        """
        # A1: Петля — наличие тренировочного цикла
        n_runs = len(training_runs)
        if n_runs % 2 == 0: n_runs -= 1
        axiom1_loop = min(n_runs / 21.0, 1.0)  # 21 = нечётное!

        # A2: Три сферы — баланс данные/модель/деплой
        data_budget    = system_config.get('data_budget_pct', 0.33)
        model_budget   = system_config.get('model_budget_pct', 0.33)
        deploy_budget  = system_config.get('deploy_budget_pct', 0.34)
        fracs = np.array([data_budget, model_budget, deploy_budget])
        fracs /= (fracs.sum() + 1e-10)
        axiom2_spheres = float(1.0 - 0.5 * np.sum(np.abs(fracs - 1/3)))

        # A3: Шаблон — наличие системного промпта и архитектурного шаблона
        has_system_prompt = system_config.get('has_system_prompt', True)
        has_arch_template = system_config.get('has_arch_template', True)
        axiom3_template = (0.5 * has_system_prompt + 0.5 * has_arch_template)

        # A4: Оконная система — контекст + RAG
        context_len = system_config.get('context_length', 8192)
        # Оптимальная длина контекста = 2^k — 1 (нечётное! = 2^k - 1)
        optimal_lens = [127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767]
        best = min(optimal_lens, key=lambda x: abs(x - context_len))
        axiom4_window = max(0.0, 1.0 - abs(context_len - best) / context_len)

        # A5: Закон нечётных — нечётные гиперпараметры
        n_layers = system_config.get('n_layers', 33)
        axiom5_odd = 1.0 if n_layers % 2 == 1 else 0.5

        # A6: Закон памяти — KV-кэш ~ 7 ключей на позицию
        kv_heads = system_config.get('kv_heads', 8)
        axiom6_memory = max(0.0, 1.0 - abs(kv_heads - 7) / 7)  # Оптимум = 7!

        # A7: 5 режимов инференса
        n_modes = system_config.get('n_inference_modes', 5)
        if n_modes % 2 == 0: n_modes += 1
        axiom7_modes = min(n_modes / 5.0, 1.0)

        axioms = np.array([axiom1_loop, axiom2_spheres, axiom3_template,
                           axiom4_window, axiom5_odd, axiom6_memory, axiom7_modes])
        overall_lci = float(np.mean(axioms))

        # Уровень ИИ-системы
        ai_level = self._compute_ai_level(overall_lci,
                                          system_config.get('n_params', 1e9))

        return {
            'system_name': system_config.get('name', 'ИИ-система'),
            'overall_etd_lci': round(overall_lci, 4),
            'ai_level': ai_level,
            'ai_level_name': AgentHierarchyETDAnalyzer.AGENT_LEVELS.get(ai_level, 'Неизвестно'),
            'axiom_scores': {
                'A1_loop': round(float(axiom1_loop), 3),
                'A2_spheres': round(float(axiom2_spheres), 3),
                'A3_template': round(float(axiom3_template), 3),
                'A4_window': round(float(axiom4_window), 3),
                'A5_odd': round(float(axiom5_odd), 3),
                'A6_memory': round(float(axiom6_memory), 3),
                'A7_modes': round(float(axiom7_modes), 3),
            },
            'n_axioms': 7,  # Нечётное!
            'emergent_potential': overall_lci > 0.85,
            'recommendations': self._gen_recs(axioms)
        }

    def _compute_ai_level(self, lci: float, n_params: float) -> int:
        param_score = min(np.log10(n_params + 1) / 12, 1.0)
        score = 0.5 * lci + 0.5 * param_score
        if score >= 0.85: return 5
        if score >= 0.70: return 4
        if score >= 0.55: return 3
        if score >= 0.40: return 2
        return 1

    def _gen_recs(self, axioms: np.ndarray) -> List[str]:
        names = ['A1-Цикл обучения', 'A2-ДанныеМодельДеплой',
                 'A3-Шаблон', 'A4-КонтекстОкно',
                 'A5-НечётностьСлоёв', 'A6-KV-память', 'A7-РежимыИнференса']
        return [f'Улучшить {n} (балл: {s:.2f})'
                for n, s in zip(names, axioms) if s < 0.6] or ['Система сбалансирована']


# ─────────────────────────────────────────────
# ГЛАВНАЯ ДЕМОНСТРАЦИЯ
# ─────────────────────────────────────────────

def demonstrate_ai_architecture_etd():
    """
    Демонстрация ЕТД на архитектурах ИИ-систем.
    """
    print("=" * 70)
    print("ЕТД В АРХИТЕКТУРЕ ИИ-СИСТЕМ — Демонстрация")
    print("=" * 70)

    rng = np.random.default_rng(seed=42)

    # ── Анализ активаций ──
    print("\n── Орбита активаций (33-слойный трансформер — нечётное!) ──")
    # Симулируем активации через 33 слоя
    d_model = 128
    activations = [rng.normal(0, 1 + i * 0.05, (8, d_model))
                   for i in range(33)]  # 33 = нечётное!

    act_analyzer = ActivationOrbitAnalyzer()
    act_result = act_analyzer.compute_activation_lci(activations)
    print(f"  ЛЗП активаций: {act_result['lci']}")
    print(f"  Слоёв: {act_result['n_layers']} (нечётное: {act_result['is_odd_layers']})")
    print(f"  Emergent potential: {act_result['emergent_potential']}")
    print(f"  Оценка: {act_result['grade']}")

    # ── Масштабный закон ──
    print("\n── Масштабный закон Чинчиллы (LCI степенного закона) ──")
    model_sizes = [1_000_000, 7_000_000, 13_000_000, 70_000_000,
                   175_000_000, 540_000_000, 1_000_000_000]  # 7 моделей — нечётное!
    val_losses  = [4.2, 3.8, 3.5, 3.1, 2.8, 2.6, 2.4]

    train_analyzer = TrainingLoopETDAnalyzer()
    scaling = train_analyzer.compute_scaling_law_lci(model_sizes, val_losses)
    print(f"  ЛЗП масштабного закона: {scaling['scaling_lci']}")
    print(f"  Показатель масштаба: {scaling['scaling_exponent']}")
    print(f"  Следует закону Чинчиллы: {scaling['follows_power_law']}")
    print(f"  Модельных точек: {scaling['n_model_sizes']} (нечётное!)")

    # ── RLHF-цикл ──
    print("\n── RLHF-цикл (7 шагов — нечётное!) ──")
    rlhf_analyzer = RLHFLoopETDAnalyzer()
    reward_scores = [0.55, 0.62, 0.68, 0.74, 0.79, 0.83, 0.87, 0.89, 0.91]  # 9 = нечётное!
    safety_scores = [0.80, 0.82, 0.84, 0.86, 0.87, 0.88, 0.89, 0.90, 0.91]
    rlhf_result = rlhf_analyzer.compute_rlhf_lci(reward_scores, safety_scores,
                                                   list(range(len(reward_scores))))
    print(f"  ЛЗП RLHF: {rlhf_result['rlhf_lci']}")
    print(f"  Шагов RLHF: {rlhf_result['n_rlhf_steps']} (нечётное!)")
    print(f"  Этапов CAI: {rlhf_result['n_cai_stages']} (нечётное!)")
    print(f"  HSH-резонанс (Helpful/Safe/Honest): {rlhf_result['three_sphere_resonance_hsh']}")
    print(f"  Выравнивание достигнуто: {rlhf_result['aligned']}")

    # CAI рафинирование
    cai = rlhf_analyzer.simulate_cai_refinement(0.55, n_rounds=3)
    print(f"\n  CAI (3 раунда — нечётное!): {cai['initial_score']} → {cai['final_score']}")
    print(f"  Улучшение: +{cai['improvement']:.3f}")

    # ── Агентная система ──
    print("\n── Агентная система (5 уровней — нечётное!) ──")
    agents = [
        AgentConfig('agent-1', AILevel.TOKEN,       n_tools=0, memory_k=5),
        AgentConfig('agent-2', AILevel.LAYER,        n_tools=3, memory_k=7),
        AgentConfig('agent-3', AILevel.MODEL,        n_tools=7, memory_k=7),
        AgentConfig('agent-4', AILevel.AGENT,        n_tools=9, memory_k=9),
        AgentConfig('agent-5', AILevel.MULTI_AGENT,  n_tools=21, memory_k=7,
                    can_spawn_subagents=True),
    ]  # 5 агентов — нечётное!
    success_rates = [0.70, 0.78, 0.85, 0.89, 0.93]

    agent_analyzer = AgentHierarchyETDAnalyzer()
    agent_result = agent_analyzer.compute_agent_lci(agents, success_rates)
    print(f"  ЛЗП агентной системы: {agent_result['lci']}")
    print(f"  Агентов: {agent_result['n_agents']} (нечётное: {agent_result['is_odd_agents']})")
    print(f"  3-сферный резонанс: {agent_result['three_sphere_resonance']}")
    print(f"  Средний успех задач: {agent_result['avg_success_rate']*100:.1f}%")
    print(f"  Оценка: {agent_result['grade']}")

    opt_system = agent_analyzer.design_optimal_agent_system(task_complexity=5)
    print(f"\n  Оптимальная система (сложность 5):")
    print(f"    Агентов: {opt_system['n_agents']} (нечётное!)")
    print(f"    Инструментов каждому: {opt_system['n_tools_each']} (нечётное!)")
    print(f"    Память (k): {opt_system['memory_k']} (нечётное — Миллер!)")

    # ── Полный аудит системы ──
    print("\n── Полный ЕТД-аудит: GPT-стиль система ──")
    auditor = AISystemETDAuditor()

    # Симулируем тренировочные запуски (21 чекпоинт — нечётное!)
    runs = [TrainingRun(i * 1000, 3.5 - i * 0.1, 3.7 - i * 0.09, 3e-4, i * 1e6)
            for i in range(21)]  # 21 = нечётное!

    system_config = {
        'name': 'ЕТД-ЯМ v1.0 (Языковая Модель)',
        'n_params': 7_000_000_000,    # 7B — нечётное начало!
        'n_layers': 33,               # Нечётное!
        'context_length': 8191,       # 8192 - 1 = нечётное!
        'kv_heads': 7,                # Нечётное!
        'n_inference_modes': 5,       # Нечётное!
        'has_system_prompt': True,
        'has_arch_template': True,
        'data_budget_pct': 0.30,
        'model_budget_pct': 0.40,
        'deploy_budget_pct': 0.30,
    }

    audit = auditor.audit_ai_system(system_config, runs, agents)
    print(f"  Система: {audit['system_name']}")
    print(f"  Общий ЛЗП: {audit['overall_etd_lci']}")
    print(f"  Уровень ИИ: {audit['ai_level']}/5")
    print(f"  Emergent potential: {audit['emergent_potential']}")
    print(f"\n  Аксиомный профиль (7 аксиом — нечётное!):")
    for ax, val in audit['axiom_scores'].items():
        bar = '█' * int(val * 10) + '░' * (10 - int(val * 10))
        print(f"    {ax}: [{bar}] {val}")
    print(f"\n  Рекомендации: {audit['recommendations']}")

    print("\n" + "=" * 70)
    print("Доказано: ИИ-архитектура подчиняется законам ЕТД.")
    print("33 слоя × 7 голов × 5 режимов = нечётная иерархия орбит.")
    print("RLHF = петля 7 шагов. CAI = три сферы (critique/revise/repeat).")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_ai_architecture_etd()
```

---

## ЧАСТЬ III — ПРАКТИЧЕСКИЕ ПРИМЕНЕНИЯ

### Приложение 1: ЕТД-метрики качества ИИ-систем

| Метрика | Формула ЕТД | Нечётность |
|---------|------------|-----------|
| ЛЗП активаций | CH(γ_{layers}) / BB | n_layers = нечётное |
| RLHF-ЛЗП | CH(reward, safety, iter) / BB | 7 шагов |
| Агент-ЛЗП | CH(level, tools, success) / BB | 5 уровней |
| RAG-ЛЗП | CH(query, retrieval, gen) / BB | 5 шагов |
| Масштабный ЛЗП | CH(log N, log L) / BB | 7 моделей |

### Приложение 2: ЕТД-архитектурные рекомендации

| Компонент | Рекомендация ЕТД | Обоснование |
|-----------|-----------------|-------------|
| Число слоёв | Нечётное: 33, 65, 97 | Закон нечётных |
| Число голов внимания | 7, 21, 35 (кратно 7) | Закон памяти |
| Контекстное окно | 2^k - 1: 4095, 8191, 32767 | Нечётное = устойчивое |
| RLHF итерации | 7, 21, 35 | Нечётное замыкание петли |
| Агентная иерархия | 5 уровней | Пять уровней ЕТД |
| RAG top-k | 7 документов | Закон памяти Миллера |

---

## ЗАКЛЮЧЕНИЕ

**Семь выводов тома (нечётное число!):**

1. **Трансформер = три сферы**: Q (МВС-запрос) / K (СВС-ключ) / V (БВС-значение) — нечётная тройка образует механизм внимания как идеальный трёхсферный резонатор.

2. **ЛЗП активаций**: орбита активаций через L слоёв в пространстве представлений — ЛЗП > 0.85 предсказывает emergent abilities; мёртвые нейроны = ЛЗП → 0.

3. **RLHF = 7-шаговая петля**: семь шагов (нечётное!) от сэмплирования до мониторинга замыкают орбиту выравнивания; Constitutional AI = три сферы (critique/revise/repeat).

4. **Масштабный закон и нечётность**: качественные скачки модели (emergent abilities) происходят при N = 10^{2k+1} параметрах — нечётные степени десятки.

5. **Пять уровней агентной иерархии**: токен-предсказатель→CoT→ReAct→Оркестратор→Мета-агент = пять нечётных ступеней ЕТД; оптимальная система содержит 5 или 7 агентов.

6. **RAG = оконная система**: 5 шагов RAG (нечётное!); оптимальный top-k = 7 документов (закон памяти Миллера); контекстное окно = 2^k − 1 (нечётное число!).

7. **KV-кэш = долговременная память ЕТД**: 7 голов KV (нечётное!) оптимальны по теореме Миллера; число групп Group Query Attention = 7 = нечётное.

---

*Единая Теория Движения. Том 48. Крюков.*
*«Великая ИИ-система — это иерархия замкнутых орбит нечётного порядка.»*

---

## ══════════════════════════════════════════
## ВЕРСИЯ 2.0 — ЧВС-АПДЕЙТ (4 СФЕРЫ)
## Источник: Том 101, Часть IV
## ══════════════════════════════════════════

### Что изменилось относительно v1.0

```
ВЕРСИЯ 1.0 (3 сферы ИИ):          ВЕРСИЯ 2.0 (4 сферы ИИ):
  МВС: Данные / токены               МВС: Данные / токены
  СВС: Модель / архитектура          СВС: Модель / архитектура
  БВС: Деплой / сервис               БВС: Деплой / сервис
  — нет домена —                     ЧВС: Адаптер / Fine-tune / Domain

ПРОБЛЕМА v1.0: «Трансформер = три сферы (QKV)» — верно,
  но где специализация под медицину, юриспруденцию, код?

РЕШЕНИЕ v2.0: ЧВС = LoRA-адаптер. Фундаментальная модель (БВС)
  остаётся; ЧВС-адаптер меняется при смене домена.

7 аксиом → 9 аксиом (нечётное!): +A8 (ЧВС-наличие) +A9 (ЧВС-резонанс).
```

---

### Глава 4v: ЧВС ИИ-системы — LoRA-адаптер как инструмент

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import numpy as np


class AdapterType(Enum):
    """Типы ЧВС-адаптеров ИИ-системы."""
    LORA            = "lora"
    PREFIX_TUNING   = "prefix_tuning"
    ADAPTER_LAYERS  = "adapter_layers"
    PROMPT_TUNING   = "prompt_tuning"
    FULL_FINETUNE   = "full_finetune"
    DOMAIN_SPECIFIC = "domain_specific"


@dataclass
class AISystemCHS:
    """
    ЧВС ИИ-системы — адаптер к конкретному прикладному домену.

    Аналогия:
      Фундаментальная модель (БВС) = тело бойца
      LoRA-адаптер (ЧВС) = меч в его руках
      Без ЧВС модель «общая»; с ЧВС — специализированная.

    Изменения относительно v1.0:
      + Параметр lora_rank (нечётное оптимально: 7, 13...)
      + target_modules по умолчанию = ['q_proj', 'v_proj', 'k_proj'] (QKV = три сферы!)
      + Метрика parameter_efficiency (% параметров, которые обучаются)
    """
    domain_name: str
    adapter_type: AdapterType
    lora_rank: int = 16
    lora_alpha: float = 32.0
    target_modules: List[str] = field(
        default_factory=lambda: ['q_proj', 'v_proj', 'k_proj']  # QKV = три сферы
    )
    training_samples: int = 1000
    eval_metric: str = 'accuracy'

    @property
    def parameter_efficiency(self) -> float:
        """% параметров модели, которые обучаются (vs полный retraining)."""
        approx_lora_params = 2 * self.lora_rank * 1024 * len(self.target_modules)
        approx_total_params = 7_000_000_000
        return approx_lora_params / approx_total_params

    @property
    def is_chs_odd_rank(self) -> bool:
        """Закон нечётности: нечётный ранг LoRA предпочтительнее."""
        return self.lora_rank % 2 == 1


# Библиотека стандартных ЧВС-адаптеров
CHS_ADAPTER_LIBRARY = {
    'medical_qa': AISystemCHS(
        domain_name='Медицинские вопросы-ответы',
        adapter_type=AdapterType.LORA,
        lora_rank=16, training_samples=50_000, eval_metric='medical_accuracy'
    ),
    'legal_analysis': AISystemCHS(
        domain_name='Юридический анализ',
        adapter_type=AdapterType.LORA,
        lora_rank=32, training_samples=20_000, eval_metric='legal_f1'
    ),
    'code_generation': AISystemCHS(
        domain_name='Генерация кода',
        adapter_type=AdapterType.ADAPTER_LAYERS,
        lora_rank=64, training_samples=100_000, eval_metric='pass@k'
    ),
    'robotics_control': AISystemCHS(
        domain_name='Управление роботами (связь с Томом 03 ЧВС)',
        adapter_type=AdapterType.DOMAIN_SPECIFIC,
        lora_rank=7, training_samples=10_000,  # 7 — нечётное!
        eval_metric='task_success_rate'
    ),
}
```

---

### Глава 5v: Обновлённый аудитор — 9 аксиом (АПДЕЙТ AISystemETDAuditor)

**v1.0** `AISystemETDAuditor` (7 аксиом) → **v2.0** `FourSphereAIAuditor` (9 аксиом)

```python
class FourSphereAIAuditor:
    """
    АПДЕЙТ AISystemETDAuditor (v1.0, Том 48).

    Было: 7 аксиом (A1–A7) — три сферы.
    Стало: 9 аксиом (A1–A9) — четыре сферы.

    Добавлены:
      A8: ЧВС-наличие (есть ли адаптер для домена)
      A9: ЧВС-резонанс (LoRA-ранг оптимален под задачу)
    """

    def audit_4sphere(self, system_config: Dict,
                       chs_adapter: Optional[AISystemCHS] = None) -> Dict:
        # A1–A7 из Тома 48 v1.0 (без изменений)
        base_scores = self._compute_base_axioms(system_config)

        # A8: ЧВС — наличие доменного адаптера (НОВОЕ)
        if chs_adapter is None:
            axiom8_chs_present = 0.0
            axiom9_chs_resonance = 0.0
        else:
            axiom8_chs_present = 1.0
            # A9: ЧВС-резонанс — LoRA rank оптимален
            rank_score = 1.0 - abs(np.log2(chs_adapter.lora_rank) - 4) / 4
            odd_bonus = 0.1 if chs_adapter.is_chs_odd_rank else 0.0
            axiom9_chs_resonance = min(max(rank_score + odd_bonus, 0.0), 1.0)

        all_scores = base_scores + [axiom8_chs_present, axiom9_chs_resonance]
        overall_lci = float(np.mean(all_scores))

        return {
            'system_name': system_config.get('name', 'ИИ-система'),
            'overall_4sphere_lci': round(overall_lci, 4),
            'n_axioms': 9,  # НЕЧЁТНОЕ!
            'axiom_scores': {
                **{f'A{i+1}': round(s, 3) for i, s in enumerate(base_scores)},
                'A8_chs_present':   round(axiom8_chs_present, 3),
                'A9_chs_resonance': round(axiom9_chs_resonance, 3),
            },
            'chs_adapter': chs_adapter.domain_name if chs_adapter else 'НЕ ЗАДАН',
            'chs_efficiency_pct': (
                round(chs_adapter.parameter_efficiency * 100, 3)
                if chs_adapter else 0.0
            ),
            'four_sphere_achieved': overall_lci > 0.80 and chs_adapter is not None,
            'recommendations': self._gen_4sphere_recs(all_scores, chs_adapter)
        }

    def _compute_base_axioms(self, cfg: Dict) -> List[float]:
        """A1–A7 из Тома 48 v1.0 (воспроизведены)."""
        a1 = min(cfg.get('n_training_runs', 0) / 21.0, 1.0)
        fracs = np.array([cfg.get('data_budget_pct', 0.33),
                          cfg.get('model_budget_pct', 0.33),
                          cfg.get('deploy_budget_pct', 0.34)])
        fracs /= fracs.sum() + 1e-10
        a2 = float(1.0 - 0.5 * np.sum(np.abs(fracs - 1/3)))
        a3 = 0.5 * cfg.get('has_system_prompt', True) + 0.5 * cfg.get('has_arch_template', True)
        cl = cfg.get('context_length', 8192)
        bests = [127, 255, 511, 1023, 2047, 4095, 8191, 16383, 32767]
        best = min(bests, key=lambda x: abs(x - cl))
        a4 = max(0.0, 1.0 - abs(cl - best) / max(cl, 1))
        a5 = 1.0 if cfg.get('n_layers', 33) % 2 == 1 else 0.5
        a6 = max(0.0, 1.0 - abs(cfg.get('kv_heads', 8) - 7) / 7)
        a7 = min(cfg.get('n_inference_modes', 5) / 5.0, 1.0)
        return [a1, a2, a3, a4, a5, a6, a7]

    def _gen_4sphere_recs(self, scores: List[float],
                          chs: Optional[AISystemCHS]) -> List[str]:
        names = ['A1-Цикл', 'A2-Бюджет', 'A3-Шаблон', 'A4-Контекст',
                 'A5-Нечётность', 'A6-KV', 'A7-Режимы', 'A8-ЧВС', 'A9-Ранг']
        recs = [f'Улучшить {n} ({s:.2f})' for n, s in zip(names, scores) if s < 0.6]
        if chs is None:
            recs.append('КРИТИЧНО: добавить ЧВС-адаптер (A8=0)!')
        elif not chs.is_chs_odd_rank:
            recs.append(f'Рекомендация: LoRA rank нечётный (текущий: {chs.lora_rank})')
        return recs or ['Система сбалансирована по 4 сферам']
```

---

### Глава 6v: Четырёхсферная формула ЛЗП ИИ-системы

```python
def compute_4sphere_ai_lci(
    data_quality: float,        # МВС: качество данных [0,1]
    model_capability: float,    # СВС: мощность модели [0,1]
    deploy_reliability: float,  # БВС: надёжность деплоя [0,1]
    domain_fit: float           # ЧВС: соответствие домену [0,1]
) -> Dict[str, float]:
    """
    v1.0: нет единой формулы для ЧВС.
    v2.0: три варианта ЛЗП (additive / multiplicative / weighted).

    Ключевое свойство v2.0: слабое звено (min сфера) тянет вниз
    через multiplicative_lci — мотивирует сбалансировать все 4 сферы.
    """
    spheres = np.array([data_quality, model_capability,
                         deploy_reliability, domain_fit])

    additive_lci      = float(np.mean(spheres))
    multiplicative_lci = float(np.prod(spheres))          # слабое звено

    resonance = 1.0 - 0.5 * float(np.sum(np.abs(spheres - 0.25 * spheres.sum())))

    chs_weight = 1.0 + (1.0 - np.mean(spheres[:3])) * 0.5
    weighted_lci = float(
        (data_quality + model_capability + deploy_reliability +
         domain_fit * chs_weight) / (3 + chs_weight)
    )

    grades = [
        (0.85, 'A — Элитная 4-сферная ИИ-система'),
        (0.70, 'B — Зрелая система с хорошей специализацией'),
        (0.55, 'C — Рабочая система, ЧВС требует усиления'),
        (0.40, 'D — Базовая система без специализации'),
        (0.0,  'E — Критические проблемы'),
    ]
    grade = next(g for threshold, g in grades if weighted_lci >= threshold)

    return {
        'additive_lci':       round(additive_lci, 4),
        'multiplicative_lci': round(multiplicative_lci, 4),
        'weighted_lci':       round(weighted_lci, 4),
        'resonance_4sphere':  round(resonance, 4),
        'bottleneck_sphere':  ['МВС/Данные', 'СВС/Модель',
                               'БВС/Деплой', 'ЧВС/Домен'][int(np.argmin(spheres))],
        'grade': grade,
        'sphere_balance': {
            'МВС_данные': round(float(data_quality), 3),
            'СВС_модель': round(float(model_capability), 3),
            'БВС_деплой': round(float(deploy_reliability), 3),
            'ЧВС_домен':  round(float(domain_fit), 3),
        }
    }
```

---

### Сравнительная таблица v1.0 vs v2.0

| Компонент | v1.0 (3 сферы) | v2.0 (+ ЧВС) |
|---|---|---|
| Три сферы ИИ | МВС/СВС/БВС | МВС/СВС/БВС **+ ЧВС** |
| ЧВС | Не формализована | **`AISystemCHS`** (LoRA, Prefix...) |
| Аудитор | `AISystemETDAuditor` | **`FourSphereAIAuditor`** |
| Число аксиом | 7 | **9 (нечётное!)** |
| Новые аксиомы | — | **A8** (ЧВС-наличие), **A9** (ЧВС-резонанс) |
| ЛЗП формула | Нет для ЧВС | **additive + multiplicative + weighted** |
| Узкое место | Из 7 аксиом | **+ ЧВС как 4-й фактор** |
| Смена домена | Полный retraining | **`CHS_ADAPTER_LIBRARY[domain]`** |

### Обновлённые архитектурные рекомендации ЕТД (v2.0)

| Компонент | v1.0 рекомендация | v2.0 рекомендация (+ ЧВС) |
|---|---|---|
| Число слоёв | Нечётное: 33, 65, 97 | Без изменений |
| KV-головы | 7, 21, 35 | Без изменений |
| Контекстное окно | 2^k − 1 | Без изменений |
| RLHF итерации | 7, 21, 35 | Без изменений |
| LoRA rank (ЧВС) | — | **Нечётное: 7, 13, 17, 33** |
| Число ЧВС-модулей | — | **3 (QKV — три сферы!)** |
| Число адаптеров в библиотеке | — | **7 (нечётное — закон памяти)** |

---

*Том 48, Версия 2.0 (ЧВС-апдейт). Источник: Том 101, Часть IV.*
*«Фундаментальная ИИ-модель без доменного адаптера — орбита без аттрактора: движется, но куда — не определено».*
