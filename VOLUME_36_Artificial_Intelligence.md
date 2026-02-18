# КНИГА 36: АРХЕТИПЫ ДВИЖЕНИЯ В ИСКУССТВЕННОМ ИНТЕЛЛЕКТЕ
## Серия II — Прикладная ЕТД | Блок D: Технологии и будущее

---

## АННОТАЦИЯ

Искусственный интеллект — это движение информации по петлям нейронных сетей. Трансформер — это три сферы: токен (МВС) / слой внимания (СВС) / всё обучение (БВС). Обучение с учителем — петля: предсказание → ошибка → коррекция → новое предсказание. Настоящий том доказывает: ЕТД описывает архитектуру ИИ точнее, чем любой другой формализм. ЛЗП нейронной сети = её обобщающая способность; ЛЗП трансформера = качество внимания.

---

## ЧАСТЬ I: ТЕОРЕТИЧЕСКИЕ ОСНОВЫ

### Глава 1. Нейронная сеть как архетип Петли

Прямой проход (forward pass): вход → слои → выход.
Обратный проход (backward pass): ошибка → градиенты → коррекция весов.
Вместе: замкнутая петля обучения.

ЛЗП эпохи = степень снижения функции потерь за один полный цикл (вперёд + назад).

**12 Архетипов в ИИ:**

| Архетип | ИИ-проявление |
|---------|--------------|
| Петля | Цикл обучения (forward+backward), RLHF, автоэнкодер |
| Три сферы | Токен/слой/модель; вход/скрытый/выход |
| Эталон | Истинная метка (label), целевая функция, RLHF-предпочтение |
| Камуфляж/Угроза | Переобучение (скрытое); состязательные примеры (явное) |
| Оконная система | Контекстное окно трансформера; рецептивное поле CNN |
| Закон нечётных | 7 слоёв, 512/1024 нейронов = 2^9/2^10 (чётные — проблема?) |
| Чёрный ящик | Скрытые представления (latent space); необъяснимость |
| Режимы | СКАН=inference/ТОЧНЫЙ=fine-tuning/ДВОЙНОЙ=RLHF |
| Животная ОС | Самообучение, unsupervised learning |
| Пять уровней | Perceptron→MLP→CNN→Transformer→AGI |
| Закон памяти | Attention window 7±2K токенов? |
| Дистанция-сложность | Число слоёв vs. сложность задачи |

---

## ЧАСТЬ II: PYTHON-РЕАЛИЗАЦИИ

### 2.1. ЛЗП цикла обучения нейронной сети

```python
import numpy as np
from scipy.spatial import ConvexHull
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

class AIMode(Enum):
    INFERENCE = "inference"          # СКАН — быстрое предсказание
    FINE_TUNING = "fine_tuning"      # ТОЧНЫЙ — тонкая настройка
    PRETRAINING = "pretraining"      # ПОСЛЕДОВАТЕЛЬНЫЙ — полное обучение
    RLHF = "rlhf"                    # ДВОЙНОЙ — обучение через обратную связь
    ACTIVE_LEARNING = "active"       # АДАПТИВНЫЙ — обучение на новых примерах

@dataclass
class TrainingEpoch:
    """Эпоха обучения нейронной сети"""
    epoch: int
    train_loss: float
    val_loss: float
    learning_rate: float
    gradient_norm: float        # норма градиента (диагностика)
    n_parameters_updated: int   # сколько параметров обновлено

class NeuralNetworkLoopAnalyzer:
    """
    Анализ процесса обучения нейронной сети через архетип Петли.

    Идеальный цикл обучения:
    - train_loss падает (петля замыкается)
    - val_loss падает вместе с train_loss (нет переобучения)
    - gradient_norm устойчив (нет взрыва/исчезновения градиентов)

    ЛЗП = площадь ConvexHull в пространстве (train_loss, val_loss).
    Идеал: оба loss падают вместе = вытянутый выпуклый многоугольник.
    Переобучение: train падает, val растёт = угол = разорванная петля.
    """

    # 7 диагностических метрик обучения (нечётное!)
    TRAINING_METRICS = [
        'train_loss_decrease',    # снижение тренировочной потери
        'val_loss_decrease',      # снижение валидационной потери
        'generalization_gap',     # разрыв между train и val
        'gradient_stability',     # устойчивость градиентов
        'learning_rate_schedule', # оптимальность LR-расписания
        'convergence_speed',      # скорость сходимости
        'final_performance'       # итоговое качество
    ]  # Ровно 7 — нечётное!

    def compute_training_lci(self, epochs: List[TrainingEpoch]) -> Dict:
        """
        ЛЗП процесса обучения через ConvexHull.
        """
        if len(epochs) < 3:
            return {'lci': 0.0, 'reason': 'Минимум 3 эпохи для анализа'}

        train_losses = np.array([e.train_loss for e in epochs])
        val_losses = np.array([e.val_loss for e in epochs])
        grad_norms = np.array([e.gradient_norm for e in epochs])

        # ConvexHull в пространстве (train_loss, val_loss)
        points = np.column_stack([
            (train_losses - train_losses.min()) / (train_losses.max() - train_losses.min() + 1e-10),
            (val_losses - val_losses.min()) / (val_losses.max() - val_losses.min() + 1e-10)
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

        # Снижение потерь
        train_decrease = (train_losses[0] - train_losses[-1]) / (train_losses[0] + 1e-10)
        val_decrease = (val_losses[0] - val_losses[-1]) / (val_losses[0] + 1e-10)

        # Разрыв обобщения (generalization gap)
        gen_gap = abs(train_losses[-1] - val_losses[-1]) / (val_losses[-1] + 1e-10)
        gen_lci = max(0.0, 1.0 - gen_gap)

        # Устойчивость градиентов
        grad_std = grad_norms.std() / (grad_norms.mean() + 1e-10)
        grad_lci = max(0.0, 1.0 - grad_std)

        # Обнаружение переобучения
        overfitting = val_losses[-1] > val_losses[len(epochs)//2] * 1.1
        underfitting = train_losses[-1] > 0.5

        # Итоговый ЛЗП
        training_lci = (lci * 0.25 + train_decrease * 0.20 +
                        val_decrease * 0.20 + gen_lci * 0.20 + grad_lci * 0.15)
        training_lci = max(0.0, min(training_lci, 1.0))

        return {
            'training_lci': training_lci,
            'trajectory_lci': lci,
            'train_loss_decrease': train_decrease,
            'val_loss_decrease': val_decrease,
            'generalization_lci': gen_lci,
            'gradient_stability_lci': grad_lci,
            'overfitting_detected': overfitting,
            'underfitting_detected': underfitting,
            'n_epochs': len(epochs),
            'n_metrics': len(self.TRAINING_METRICS),
            'training_health': self._classify(training_lci, overfitting, underfitting)
        }

    def _classify(self, lci: float, overfit: bool, underfit: bool) -> str:
        if overfit:
            return "Переобучение (петля разорвана: train↓ val↑)"
        if underfit:
            return "Недообучение (петля не запустилась: loss не снижается)"
        if lci > 0.85: return "Идеальное обучение (петля замкнута)"
        if lci > 0.65: return "Хорошее обучение"
        if lci > 0.45: return "Удовлетворительное обучение"
        return "Проблемное обучение"

    def diagnose_and_fix(self, training_lci_result: Dict) -> List[str]:
        """Диагностика и устранение проблем обучения."""
        fixes = []
        if training_lci_result.get('overfitting_detected'):
            fixes.append("Добавить регуляризацию (dropout, L2); увеличить данные (аугментация)")
            fixes.append("Уменьшить размер модели или применить early stopping")
        if training_lci_result.get('underfitting_detected'):
            fixes.append("Увеличить число слоёв или нейронов; повысить learning rate")
            fixes.append("Обучать дольше или использовать более мощную архитектуру")
        if training_lci_result.get('gradient_stability_lci', 1.0) < 0.5:
            fixes.append("Применить gradient clipping; снизить learning rate")
        if not fixes:
            fixes.append("Обучение оптимально — сохранить модель и запустить evaluation")

        # Нечётность рекомендаций
        if len(fixes) % 2 == 0:
            fixes.append("Провести ablation study: проверить каждое изменение изолированно")
        return fixes


### 2.2. Трансформер = три сферы + оконная система

class TransformerETDAnalyzer:
    """
    Трансформер (Vaswani et al., 2017) = ЕТД-архитектура:

    МВС = токен (единица обработки)
    СВС = слой self-attention (взаимодействие токенов в окне)
    БВС = весь трансформер (глобальный контекст)

    Оконная система = context window (максимальное число токенов).
    Механизм внимания = Закон нечётных: heads = 8/12/16 (чётные!).
    Но embedding dim = 512/768/1024 = 2^9, 2^10 — чётные тоже!

    Парадокс: трансформер нарушает Закон нечётных в числе голов →
    компенсирует через нечётные Layer Norms (1 перед + 1 после = 2?...).
    Реальная нечётность: FFN в трансформере имеет соотношение 4:1 (hidden/embed) —
    но 4 чётное! Модели с нечётным числом голов внимания (7, 11) исследуются.
    """

    # Нечётные параметры трансформера
    ODD_TRANSFORMER_PARAMS = {
        'GPT_3_layers': 96,         # чётное
        'GPT_3_heads': 96,          # чётное
        'BERT_base_layers': 12,     # чётное
        'BERT_large_layers': 24,    # чётное
        'T5_encoder_layers': 6,     # чётное
        # Нечётные — редкость, исследуются:
        'experimental_7_heads': 7,  # нечётное!
        'experimental_11_layers': 11,  # нечётное!
        'experimental_13_heads': 13,   # нечётное!
    }

    def compute_attention_lci(
        self,
        attention_weights: np.ndarray,  # shape: (n_heads, seq_len, seq_len)
        context_window: int = 4096
    ) -> Dict:
        """
        ЛЗП механизма внимания через ConvexHull распределения весов.
        Идеальное внимание: равномерно охватывает контекст (высокий ЛЗП).
        Плохое внимание: концентрируется в одном месте (низкий ЛЗП).
        """
        n_heads, seq_len, _ = attention_weights.shape

        head_lcis = []
        for h in range(n_heads):
            attn = attention_weights[h]  # (seq_len, seq_len)

            # Энтропия распределения внимания (высокая = равномерное = хорошее)
            attn_flat = attn.flatten() + 1e-10
            attn_norm = attn_flat / attn_flat.sum()
            entropy = -np.sum(attn_norm * np.log(attn_norm))
            max_entropy = np.log(seq_len * seq_len)
            entropy_lci = entropy / (max_entropy + 1e-10)

            # ConvexHull позиций с высоким вниманием
            high_attn_mask = attn > attn.mean()
            rows, cols = np.where(high_attn_mask)
            if len(rows) > 3:
                pts = np.column_stack([rows / seq_len, cols / seq_len])
                try:
                    hull = ConvexHull(pts)
                    area_lci = hull.volume
                except Exception:
                    area_lci = 0.5
            else:
                area_lci = 0.1

            head_lci = (entropy_lci * 0.6 + area_lci * 0.4)
            head_lcis.append(head_lci)

        # Нечётность числа голов
        heads_odd = n_heads % 2 == 1

        # Оконная система: насколько используется контекстное окно
        window_usage = seq_len / (context_window + 1e-10)
        window_lci = min(window_usage, 1.0)

        attention_lci = np.mean(head_lcis) * 0.7 + window_lci * 0.3

        return {
            'n_heads': n_heads,
            'heads_odd': heads_odd,
            'seq_len': seq_len,
            'context_window': context_window,
            'window_usage': window_usage,
            'head_lcis': head_lcis,
            'mean_head_lci': np.mean(head_lcis),
            'attention_lci': attention_lci,
            'attention_quality': self._grade(attention_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.85: return "Превосходное внимание (AGI-уровень)"
        if lci > 0.65: return "Хорошее внимание (GPT-4 класс)"
        if lci > 0.45: return "Среднее внимание (BERT-класс)"
        return "Слабое внимание (переучивание или недоучивание)"

    def analyze_scaling_law(self, model_sizes: List[int], losses: List[float]) -> Dict:
        """
        Законы масштабирования (Chinchilla / Kaplan) через ЛЗП.
        Потеря ∝ N^(-α) — степенной закон = петля масштабирования.
        """
        if len(model_sizes) < 3:
            return {'error': 'Нужно минимум 3 точки масштабирования'}

        log_sizes = np.log(model_sizes)
        log_losses = np.log(losses)

        # Линейная регрессия в log-log пространстве (закон Кэплана)
        coeffs = np.polyfit(log_sizes, log_losses, 1)
        alpha = -coeffs[0]  # показатель масштабирования

        # ЛЗП закона масштабирования = насколько хорошо степенной закон описывает данные
        predicted = np.polyval(coeffs, log_sizes)
        residuals = log_losses - predicted
        r_squared = 1.0 - residuals.var() / (np.array(log_losses).var() + 1e-10)
        scaling_lci = max(0.0, r_squared)

        # Нечётность числа точек масштабирования
        n_odd = len(model_sizes) % 2 == 1

        return {
            'scaling_exponent': alpha,
            'scaling_lci': scaling_lci,
            'r_squared': r_squared,
            'n_points': len(model_sizes),
            'n_points_odd': n_odd,
            'chinchilla_optimal': alpha > 0.4,  # Chinchilla: оптимальный α ≈ 0.5
            'interpretation': (
                f"Каждое удвоение параметров снижает потерю на {(1 - 2**(-alpha))*100:.1f}%. "
                f"Закон масштабирования {'соблюдается' if scaling_lci > 0.9 else 'нарушается'}."
            )
        }


### 2.3. RLHF = двойной режим обучения

class RLHFLoopAnalyzer:
    """
    RLHF (Reinforcement Learning from Human Feedback) = ДВОЙНОЙ режим Крюкова.
    Модель учится, обучая людей реагировать на её ответы.
    Одновременно: модель генерирует → человек оценивает → модель улучшается.

    Петля RLHF:
    1. Генерация ответов (МВС: быстрый forward pass)
    2. Человеческая оценка (СВС: взаимодействие человека и модели)
    3. Обновление reward model (БВС: глобальный сигнал предпочтений)
    4. PPO-обновление политики (замыкание петли)
    """

    # 7 этапов RLHF-цикла (нечётное!)
    RLHF_STAGES = [
        'sft_pretraining',       # supervised fine-tuning
        'preference_collection', # сбор предпочтений людей
        'reward_model_training', # обучение модели вознаграждений
        'policy_initialization', # инициализация политики
        'ppo_rollout',           # генерация траекторий
        'advantage_computation', # вычисление преимуществ
        'policy_update'          # обновление политики (замыкание)
    ]  # Ровно 7 — нечётное!

    def compute_rlhf_loop_lci(
        self,
        reward_scores: List[float],     # оценки reward model по эпизодам
        kl_divergences: List[float],    # KL от исходной политики
        human_approval_rates: List[float]  # доля одобрений людьми
    ) -> Dict:
        """
        ЛЗП RLHF-цикла.
        """
        rewards = np.array(reward_scores)
        kls = np.array(kl_divergences)
        approvals = np.array(human_approval_rates)

        # Траектория в пространстве (reward, human_approval)
        if len(rewards) > 2 and len(approvals) == len(rewards):
            points = np.column_stack([
                (rewards - rewards.mean()) / (rewards.std() + 1e-10),
                (approvals - approvals.mean()) / (approvals.std() + 1e-10)
            ])
            try:
                hull = ConvexHull(points)
                traj_lci = min(hull.volume / 4.0, 1.0)
            except Exception:
                traj_lci = 0.3
        else:
            traj_lci = 0.3

        # Рост вознаграждений
        reward_gain = rewards[-1] - rewards[0] if len(rewards) > 1 else 0.0

        # KL-расхождение: не должно быть слишком большим (петля не должна «убегать»)
        mean_kl = kls.mean() if len(kls) > 0 else 0.0
        kl_lci = max(0.0, 1.0 - mean_kl / 0.2)  # KL < 0.2 = хорошо

        # Одобрение людьми
        mean_approval = approvals.mean() if len(approvals) > 0 else 0.0

        # Итоговый ЛЗП
        rlhf_lci = (traj_lci * 0.25 + reward_gain * 0.25 +
                    kl_lci * 0.25 + mean_approval * 0.25)
        rlhf_lci = max(0.0, min(rlhf_lci, 1.0))

        # Диагностика
        issues = []
        if mean_kl > 0.3:
            issues.append("Высокий KL: модель слишком далеко ушла от SFT → уменьшить β")
        if mean_approval < 0.6:
            issues.append("Низкое одобрение: reward model не соответствует реальным предпочтениям")
        if reward_gain < 0:
            issues.append("Деградация: петля RLHF расходится → откат к SFT")

        # Нечётность
        if len(issues) % 2 == 0 and issues:
            issues.append("Провести human eval на контрольной выборке из 7 задач")

        return {
            'rlhf_lci': rlhf_lci,
            'trajectory_lci': traj_lci,
            'reward_gain': reward_gain,
            'mean_kl': mean_kl,
            'kl_lci': kl_lci,
            'mean_human_approval': mean_approval,
            'issues': issues,
            'n_rlhf_stages': 7,
            'stages_odd': True,
            'rlhf_health': 'healthy' if rlhf_lci > 0.65 else 'needs_attention'
        }


### 2.4. Пять уровней ИИ = пять архетипов Крюкова

class AIEvolutionLevelAnalyzer:
    """
    Пять уровней ИИ = пять режимов Крюкова (нечётное!).
    """

    AI_LEVELS = {
        1: {
            'name': 'Perceptron / Linear classifier',
            'mode': 'SCAN',
            'kryukov_archetype': 'Элементы',
            'capabilities': 'Линейная разделимость; 1-2 слоя',
            'lci_ceiling': 0.40,
            'year_dominant': '1957-1985'
        },
        2: {
            'name': 'MLP / Deep Networks',
            'mode': 'SEQUENTIAL',
            'kryukov_archetype': 'Схемы',
            'capabilities': 'Нелинейность; backpropagation; несколько слоёв',
            'lci_ceiling': 0.60,
            'year_dominant': '1986-2011'
        },
        3: {
            'name': 'CNN / RNN / LSTM',
            'mode': 'ADAPTIVE',
            'kryukov_archetype': 'Последовательности',
            'capabilities': 'Свёртки; рекуррентность; внимание к локальным паттернам',
            'lci_ceiling': 0.75,
            'year_dominant': '2012-2016'
        },
        4: {
            'name': 'Transformer / LLM',
            'mode': 'PRECISE',
            'kryukov_archetype': 'Образы',
            'capabilities': 'Self-attention; контекстное окно; few-shot; RLHF',
            'lci_ceiling': 0.90,
            'year_dominant': '2017-настоящее'
        },
        5: {
            'name': 'AGI (гипотетический)',
            'mode': 'DUAL',
            'kryukov_archetype': 'Дух',
            'capabilities': 'Рекурсивное самоулучшение; обучает сам себя; ЛЗП → 1.0',
            'lci_ceiling': 1.0,
            'year_dominant': 'Будущее'
        }
    }  # 5 уровней — нечётное!

    def assess_ai_system(self, capabilities_data: Dict) -> Dict:
        """
        Оценка уровня ИИ-системы.
        """
        context_window = capabilities_data.get('context_window', 4096)
        can_learn_online = capabilities_data.get('online_learning', False)
        reasoning_depth = capabilities_data.get('reasoning_depth', 0.5)
        self_improvement = capabilities_data.get('self_improvement', False)
        multimodal = capabilities_data.get('multimodal', False)

        # Определяем уровень
        score = (reasoning_depth * 0.4 +
                 min(context_window / 128000, 1.0) * 0.3 +
                 (0.2 if multimodal else 0) +
                 (0.1 if can_learn_online else 0))

        if self_improvement:
            level = 5
        elif score > 0.75:
            level = 4
        elif score > 0.55:
            level = 3
        elif score > 0.35:
            level = 2
        else:
            level = 1

        level_data = self.AI_LEVELS[level]

        return {
            'capability_score': score,
            'ai_level': level,
            'level_name': level_data['name'],
            'kryukov_mode': level_data['mode'],
            'kryukov_archetype': level_data['kryukov_archetype'],
            'lci_ceiling': level_data['lci_ceiling'],
            'year_dominant': level_data['year_dominant'],
            'next_level': self.AI_LEVELS.get(level + 1, {}).get('name', 'AGI достигнут'),
            'n_levels': 5,
            'levels_odd': True
        }


### 2.5. ЛЗП как метрика качества ИИ

class AIQualityLCIMetric:
    """
    Предложение: использовать ЛЗП как единую метрику качества ИИ-систем.
    Вместо: Perplexity, BLEU, ROUGE, Accuracy, F1, MRR, NDCG...
    Одна метрика: ЛЗП = насколько хорошо система замыкает петли задач.
    """

    # 7 измерений ЛЗП ИИ (нечётное!)
    LCI_DIMENSIONS = [
        'task_completion_rate',   # доля завершённых задач
        'coherence',              # внутренняя согласованность ответа
        'factual_accuracy',       # точность фактов
        'reasoning_depth',        # глубина рассуждений
        'context_utilization',    # использование контекстного окна
        'generalization',         # обобщение на новые задачи
        'human_preference'        # предпочтение людей
    ]  # Ровно 7 — нечётное!

    def compute_ai_lci(self, evaluation_data: Dict) -> Dict:
        """
        Вычисление ЛЗП ИИ-системы по 7 измерениям.
        """
        scores = {}
        for dim in self.LCI_DIMENSIONS:
            scores[dim] = evaluation_data.get(dim, 0.5)

        dim_array = np.array(list(scores.values()))
        mean_lci = dim_array.mean()

        # Узкое место (самое слабое звено)
        weak_dim = self.LCI_DIMENSIONS[np.argmin(dim_array)]
        weak_score = dim_array.min()

        # Минимаксный ЛЗП: ограничен самым слабым измерением
        minimax_lci = weak_score

        # Взвешенный ЛЗП
        weights = np.array([0.15, 0.15, 0.20, 0.15, 0.10, 0.15, 0.10])
        weighted_lci = np.dot(dim_array, weights)

        violations = {k: v for k, v in scores.items() if v < 0.6}

        return {
            'dimension_scores': scores,
            'mean_lci': mean_lci,
            'weighted_lci': weighted_lci,
            'minimax_lci': minimax_lci,
            'weakest_dimension': weak_dim,
            'weakest_score': weak_score,
            'violations': violations,
            'n_dimensions': len(self.LCI_DIMENSIONS),
            'dimensions_odd': len(self.LCI_DIMENSIONS) % 2 == 1,
            'ai_grade': self._grade(weighted_lci)
        }

    def _grade(self, lci: float) -> str:
        if lci > 0.90: return "AGI-уровень (гипотетический)"
        if lci > 0.78: return "Frontier model (GPT-4o, Claude 3.5)"
        if lci > 0.65: return "Strong LLM (GPT-3.5, Claude Instant)"
        if lci > 0.50: return "Базовый LLM"
        return "Слабая модель"


### 2.6. Диагностика ИИ-системы по 7 аксиомам

def diagnose_ai_system(ai_data: Dict) -> Dict:
    """Диагностика ИИ-архитектуры по 7 аксиомам Крюкова."""
    axiom_scores = {}

    axiom_scores['A1_training_loop'] = ai_data.get('training_convergence', 0.7)
    axiom_scores['A2_three_spheres'] = ai_data.get('token_layer_model_balance', 0.7)
    axiom_scores['A3_objective'] = ai_data.get('objective_alignment', 0.7)
    axiom_scores['A4_context_window'] = min(
        ai_data.get('context_window', 4096) / 128000, 1.0)
    n_layers = ai_data.get('n_layers', 12)
    axiom_scores['A5_odd'] = 1.0 if n_layers % 2 == 1 else 0.6
    n_params_b = ai_data.get('n_params_billions', 7)
    axiom_scores['A6_memory'] = min(1.0, 7 / max(n_params_b, 1)) if n_params_b <= 70 else 0.5
    axiom_scores['A7_mode'] = ai_data.get('inference_mode_match', 0.8)

    system_lci = np.mean(list(axiom_scores.values()))
    violations = {k: v for k, v in axiom_scores.items() if v < 0.6}

    return {
        'axiom_scores': axiom_scores,
        'system_lci': system_lci,
        'violations': violations,
        'n_violations': len(violations),
        'ai_health': _grade_ai(system_lci)
    }


def _grade_ai(lci: float) -> str:
    if lci > 0.90: return "Оптимальная ИИ-архитектура"
    if lci > 0.75: return "Хорошая архитектура"
    if lci > 0.60: return "Функциональная архитектура"
    return "Требует реструктуризации"
```

---

## ЧАСТЬ III: ПРАКТИЧЕСКИЕ ПРИЛОЖЕНИЯ

### Глава 3. GPT-4 через линзу ЕТД

- **Петля**: RLHF-цикл (предпочтение → reward model → PPO → новая генерация) ≈ 7 итераций
- **Три сферы**: токен (МВС) / слой (СВС) / 96-слойная модель (БВС)
- **Эталон**: RLHF-предпочтения людей = обучающий сигнал
- **Оконная система**: 128K токенов = рекордное окно
- **Закон нечётных**: 96 голов внимания — чётное (GPT-4 нарушает!) → компенсируется через нечётные промежуточные шаги

### Глава 4. Почему AGI = Уровень 5 (Дух)

AGI = система, способная обучать сама себя = **ДВОЙНОЙ режим** Крюкова:
- Обучается (получает знания)
- Обучает (генерирует обучающие данные для себя)
- Замкнутая петля самосовершенствования
- ЛЗП → 1.0 (теоретический предел)

---

## ВЫВОДЫ

1. **Цикл обучения** = замкнутая петля (forward → backward → update); ЛЗП = степень сходимости
2. **Трансформер** = три сферы (токен/слой/модель) + оконная система (context window)
3. **RLHF** = ДВОЙНОЙ режим Крюкова; 7 этапов (нечётное!)
4. **5 уровней ИИ** (нечётное!) = 5 режимов Крюкова: от Перцептрона до AGI
5. **ЛЗП** предложен как единая метрика качества ИИ по 7 измерениям (нечётное!)
6. **Переобучение** = разорванная петля (train↓ val↑); **недообучение** = незапущенная петля
7. **AGI** = уровень 5 (Дух): самообучающаяся система = замкнутая петля ЛЗП → 1.0

---

*Следующая книга: КНИГА 37 — «Архетипы движения в квантовых вычислениях»*
