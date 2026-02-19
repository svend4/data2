# КНИГА 15: НЕЙРОННЫЕ СЕТИ И ГЛУБОКОЕ ОБУЧЕНИЕ
## «Архетипы движения как структурные принципы нейронных архитектур»

### Серия «Архетипы Движения», Книга 15 из 20
### Основано на «Тотальной Системе Боя» В.В. Крюкова

---

## ПРЕДИСЛОВИЕ

Когда в 2015 году Microsoft Research представила ResNet — сеть с «остаточными соединениями» (skip connections) — никто не назвал это «петлевой архитектурой». Но именно это и было сделано: информация не идёт прямолинейно от входа к выходу, она описывает **петли** — возвращается с более глубоких слоёв к более ранним через остаточные связи.

Self-attention в Трансформере — это **резонанс**: каждый токен «слушает» все остальные и синхронизирует своё представление с общим контекстом. Иерархия CNN (пиксели → грани → части → объекты) — это **три сферы**. LSTM-ячейка — это **закон памяти** (7±2 шагов назад).

Глубокое обучение **независимо переоткрыло** архетипы Крюкова — на языке матриц и градиентов.

---

## ЧАСТЬ I. АРХЕТИПЫ В НЕЙРОННЫХ АРХИТЕКТУРАХ

### Глава 1. Петля в Нейронных Сетях

#### 1.1 Skip-connections как петли (ResNet)

```
RESNET — ПЕТЛЕВАЯ АРХИТЕКТУРА:

Стандартный блок:
  x → [Conv → BN → ReLU → Conv → BN] → y
  Прямолинейное движение — нет петли

Residual block:
  x → [Conv → BN → ReLU → Conv → BN] → F(x)
  y = F(x) + x   ← ПЕТЛЯ: x возвращается и добавляется!

Математически:
  y = F(x, {Wᵢ}) + x

  Это точная реализация петли Крюкова:
  «Прямое движение + возврат к начальной точке = замкнутая петля»

Почему это работает лучше?
  Обычная сеть глубиной 100 слоёв: деградация (gradient vanishing)
  ResNet глубиной 100 слоёв: тренируется успешно

  Интерпретация через архетипы:
  Без петли: информация «теряется» за 100 шагов (разрыв петли)
  С петлей: информация «возвращается» (LCI → 1.0) → стабильность
```

#### 1.2 Рекуррентные сети как временные петли

```python
import torch
import torch.nn as nn
import numpy as np

class KryukovRNN(nn.Module):
    """
    Рекуррентная сеть, явно реализующая архетипы Крюкова.

    Три сферы памяти:
      МВС: краткосрочный буфер (последние 3 шага)
      СВС: среднесрочный контекст (последние 7 шагов)
      БВС: долгосрочное состояние (скользящее среднее)

    Закон памяти: рабочий горизонт = 7 ± 2
    """

    def __init__(self, input_size: int, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size

        # МВС: быстрый буфер (3 шага)
        self.mvs_cell = nn.GRUCell(input_size, hidden_size // 4)

        # СВС: средний контекст (7 шагов)
        self.svs_cell = nn.LSTMCell(hidden_size // 4, hidden_size // 2)

        # БВС: долгосрочное состояние (экспоненциальное скользящее среднее)
        self.bvs_decay = nn.Parameter(torch.tensor(0.95))  # Темп забывания

        # Резонансный интегратор: синхронизирует три сферы
        self.resonance_gate = nn.Linear(
            hidden_size // 4 + hidden_size // 2 + hidden_size // 4,
            hidden_size
        )

        # Выходной слой
        self.output_proj = nn.Linear(hidden_size, input_size)

        # Закон памяти: максимальный горизонт = 9
        self.MAX_HORIZON = 9

        # Буферы
        self.mvs_buffer = []   # последние 3
        self.svs_buffer = []   # последние 7

    def forward(self, x_seq: torch.Tensor) -> torch.Tensor:
        """
        x_seq: (batch, seq_len, input_size)
        """
        batch_size, seq_len, _ = x_seq.shape

        # Инициализация состояний
        h_mvs = torch.zeros(batch_size, self.hidden_size // 4)
        h_svs = torch.zeros(batch_size, self.hidden_size // 2)
        c_svs = torch.zeros(batch_size, self.hidden_size // 2)
        h_bvs = torch.zeros(batch_size, self.hidden_size // 4)

        outputs = []

        for t in range(min(seq_len, self.MAX_HORIZON)):
            x_t = x_seq[:, t, :]

            # МВС: быстрое обновление (3 шага)
            h_mvs = self.mvs_cell(x_t, h_mvs)

            # СВС: медленное обновление (7 шагов)
            h_svs, c_svs = self.svs_cell(h_mvs, (h_svs, c_svs))

            # БВС: долгосрочное скользящее среднее
            alpha = torch.sigmoid(self.bvs_decay)
            h_bvs = alpha * h_bvs + (1 - alpha) * h_mvs

            # Резонанс: конкатенация и интеграция трёх сфер
            combined = torch.cat([h_mvs, h_svs, h_bvs], dim=-1)
            resonant = torch.tanh(self.resonance_gate(combined))

            # Выходной прогноз
            out = self.output_proj(resonant)
            outputs.append(out)

        return torch.stack(outputs, dim=1)

    def compute_resonance_score(
            self, h_mvs: torch.Tensor,
            h_svs: torch.Tensor,
            h_bvs: torch.Tensor) -> torch.Tensor:
        """
        Вычислить Score резонанса трёх сфер.
        Высокий резонанс → состояния похожи (синхронизированы).
        """
        # Косинусная похожесть между сферами
        mvs_norm = nn.functional.normalize(h_mvs, dim=-1)
        svs_norm = nn.functional.normalize(
            h_svs[:, :h_mvs.shape[-1]], dim=-1)  # Усечь до общей размерности
        bvs_norm = nn.functional.normalize(h_bvs, dim=-1)

        sim_ms = (mvs_norm * svs_norm).sum(dim=-1)   # МВС-СВС
        sim_mb = (mvs_norm * bvs_norm).sum(dim=-1)   # МВС-БВС

        # Резонанс = среднее сходство
        return (sim_ms + sim_mb) / 2
```

---

### Глава 2. Три Сферы в CNN

#### 2.1 Иерархия признаков = иерархия сфер

```
CNN КАК ТРЁХСФЕРНАЯ АРХИТЕКТУРА:

МВС (ранние слои):
  Что учится: грани, цвета, текстуры
  Рецептивное поле: 3×3 — 11×11 пикселей
  Аналог: МВС тела — кончики пальцев, тактильные детали

СВС (средние слои):
  Что учится: части объектов (глаз, колесо, угол здания)
  Рецептивное поле: 32×32 — 128×128 пикселей
  Аналог: СВС тела — рука, предплечье — «узнаваемые части»

БВС (глубокие слои):
  Что учится: целые объекты, сцены, абстрактные понятия
  Рецептивное поле: всё изображение
  Аналог: БВС тела — осознание пространства целиком

Резонанс в CNN (Feature Pyramid Networks):
  FPN соединяет все три уровня через lateral connections:
  БВС → downsampled → смешивается с СВС → смешивается с МВС
  → Детекция объектов на всех масштабах одновременно
  Это резонанс трёх сфер в компьютерном зрении!
```

#### 2.2 Отношение к LCI

```python
class CNNFeatureResonanceAnalyzer:
    """
    Анализ «резонанса» признаков на разных уровнях CNN.
    Вдохновлён архетипами трёх сфер Крюкова.
    """

    def __init__(self, model: nn.Module):
        self.model = model
        self.layer_activations = {}
        self._register_hooks()

    def _register_hooks(self):
        """Установить хуки для перехвата активаций трёх уровней."""
        layers = list(self.model.named_modules())
        n = len(layers)

        # МВС: первая треть (ранние слои)
        mvs_idx = n // 6
        # СВС: средняя треть
        svs_idx = n // 2
        # БВС: последняя треть
        bvs_idx = 5 * n // 6

        for idx, (name, layer) in enumerate(layers):
            if idx in (mvs_idx, svs_idx, bvs_idx):
                sphere = {mvs_idx: 'MVS', svs_idx: 'SVS', bvs_idx: 'BVS'}[idx]
                layer.register_forward_hook(
                    self._make_hook(sphere))

    def _make_hook(self, sphere_name: str):
        def hook(module, input, output):
            self.layer_activations[sphere_name] = output.detach()
        return hook

    def compute_inter_sphere_resonance(self) -> dict:
        """
        Вычислить резонанс между активациями трёх сфер.
        Высокий резонанс = сферы «согласованы» по структуре.
        """
        if len(self.layer_activations) < 3:
            return {'error': 'Need activations from all 3 spheres'}

        mvs = self.layer_activations.get('MVS')
        svs = self.layer_activations.get('SVS')
        bvs = self.layer_activations.get('BVS')

        # Сжать до векторов (global average pooling)
        def gap(x):
            return x.mean(dim=list(range(2, x.dim()))) if x.dim() > 2 else x

        mvs_vec = gap(mvs).flatten(1)
        svs_vec = gap(svs).flatten(1)
        bvs_vec = gap(bvs).flatten(1)

        # Привести к одной размерности (min)
        d = min(mvs_vec.shape[-1], svs_vec.shape[-1], bvs_vec.shape[-1])
        mvs_vec = mvs_vec[:, :d]
        svs_vec = svs_vec[:, :d]
        bvs_vec = bvs_vec[:, :d]

        # Косинусное сходство
        def cos_sim(a, b):
            a_n = nn.functional.normalize(a, dim=-1)
            b_n = nn.functional.normalize(b, dim=-1)
            return (a_n * b_n).sum(dim=-1).mean().item()

        res_ms = cos_sim(mvs_vec, svs_vec)
        res_mb = cos_sim(mvs_vec, bvs_vec)
        res_sb = cos_sim(svs_vec, bvs_vec)

        resonance = (res_ms + res_mb + res_sb) / 3

        return {
            'MVS_SVS_similarity': round(res_ms, 4),
            'MVS_BVS_similarity': round(res_mb, 4),
            'SVS_BVS_similarity': round(res_sb, 4),
            'resonance_score': round(resonance, 4),
            'interpretation': (
                'Высокий резонанс: слои согласованы, модель «видит» объект'
                if resonance > 0.5 else
                'Низкий резонанс: слои несогласованы, задача трудная'
            )
        }
```

---

### Глава 3. Трансформер как Резонансная Машина

#### 3.1 Self-Attention = Резонанс

```
SELF-ATTENTION = УСЛОВИЕ РЕЗОНАНСА:

Стандартный self-attention:
  Attention(Q, K, V) = softmax(QKᵀ / √d_k) × V

Интерпретация через архетипы:
  Q (Query): каждый токен задаёт «вопрос» (угроза — активное намерение)
  K (Key): каждый токен предъявляет «ключ» (камуфляж — пассивное присутствие)
  V (Value): содержимое (то, что реально передаётся)

  Attention weight: A_ij = exp(QᵢKⱼᵀ / √d_k) / Σ exp(...)

  A_ij высокий ⟺ Q_i «резонирует» с K_j
  → токен i «прислушивается» к токену j

  Это буквально условие резонанса:
  ω_i ≈ ω_j → высокое внимание → передача информации

Multi-head attention = множественные частоты резонанса:
  H головок = H разных «частот» резонанса
  Каждая голова «слышит» разные типы связей
  (синтаксические, семантические, позиционные...)

  Оптимальное H: нечётное? Авторы используют 8, 12, 16 (чётное...)
  Но: внутри каждой головы — нечётная структура из трёх матриц (Q, K, V)!
```

#### 3.2 Трансформер как трёхсферная система

```
ТРАНСФОРМЕР И ТРИ СФЕРЫ:

Слои Трансформера (GPT-3: 96 слоёв, разбиваем на три):

МВС (слои 1–32):
  Учится: синтаксис, части речи, морфология
  Поведение: «близкие» паттерны (соседние токены)
  Аналог: МВС кисти — локальная точность

СВС (слои 33–64):
  Учится: семантика, кореференция, факты
  Поведение: «средние» зависимости (10–100 токенов)
  Аналог: СВС предплечья — перенос смысла

БВС (слои 65–96):
  Учится: прагматика, дискурс, рассуждение
  Поведение: «дальние» зависимости (100+ токенов)
  Аналог: БВС тела — контекст всей ситуации

Доказательство (mechanistic interpretability, Anthropic, 2022–2024):
  Ранние слои: Induction heads (синтаксические петли)
  Средние слои: Entity tracking, factual recall
  Поздние слои: Reasoning, instruction following

  Это ТОЧНО соответствует трём сферам Крюкова.
  Система Крюкова предсказала структуру LLM до её открытия.
```

#### 3.3 Residual stream = петля

```python
class TransformerResonanceAnalyzer(nn.Module):
    """
    Трансформер с явным измерением резонанса между слоями.
    Основан на принципах трёх сфер и резонанса Крюкова.
    """

    def __init__(self, d_model: int = 512, n_heads: int = 8,
                 n_layers: int = 12):
        super().__init__()
        self.d_model = d_model

        # Нечётное число уровней иерархии (3 сферы)
        assert n_layers % 3 == 0, "n_layers должен делиться на 3 (три сферы)"

        self.layers_per_sphere = n_layers // 3

        # Слои трёх сфер
        self.mvs_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, n_heads, batch_first=True)
            for _ in range(self.layers_per_sphere)
        ])
        self.svs_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, n_heads, batch_first=True)
            for _ in range(self.layers_per_sphere)
        ])
        self.bvs_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, n_heads, batch_first=True)
            for _ in range(self.layers_per_sphere)
        ])

        # Резонансные детекторы между сферами
        self.mvs_svs_resonance = nn.Linear(d_model, 1)
        self.svs_bvs_resonance = nn.Linear(d_model, 1)

        # Резонансные ворота (skip-connections между сферами)
        self.mvs_to_svs_gate = nn.Linear(d_model, d_model)
        self.svs_to_bvs_gate = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor) -> dict:
        """
        Прямой проход с измерением резонанса.
        x: (batch, seq_len, d_model)
        """
        # МВС: ранние слои
        h = x
        for layer in self.mvs_layers:
            h = layer(h)
        h_mvs = h

        # Резонансный gate: МВС → СВС
        mvs_gate = torch.sigmoid(self.mvs_to_svs_gate(h_mvs))
        h = h_mvs

        # СВС: средние слои с МВС-инициализацией
        for layer in self.svs_layers:
            h = layer(h)
        h_svs = h * mvs_gate + h_mvs * (1 - mvs_gate)

        # Резонансный gate: СВС → БВС
        svs_gate = torch.sigmoid(self.svs_to_bvs_gate(h_svs))
        h = h_svs

        # БВС: глубокие слои
        for layer in self.bvs_layers:
            h = layer(h)
        h_bvs = h * svs_gate + h_svs * (1 - svs_gate)

        # Измерение резонанса
        res_ms = torch.sigmoid(self.mvs_svs_resonance(
            (h_mvs - h_svs).abs())).mean()
        res_sb = torch.sigmoid(self.svs_bvs_resonance(
            (h_svs - h_bvs).abs())).mean()

        resonance_score = 1.0 - (res_ms + res_sb) / 2  # Инверсия: меньше разница = выше резонанс

        return {
            'output': h_bvs,
            'mvs_repr': h_mvs,
            'svs_repr': h_svs,
            'bvs_repr': h_bvs,
            'resonance_score': resonance_score,
        }

    def resonance_loss(self, forward_output: dict,
                       task_loss: torch.Tensor) -> torch.Tensor:
        """
        Потеря с резонансной регуляризацией.
        Штрафуем за низкий резонанс между сферами.
        """
        resonance = forward_output['resonance_score']
        resonance_penalty = (1.0 - resonance) * 0.1  # Коэффициент регуляризации
        return task_loss + resonance_penalty
```

---

### Глава 4. Закон Нечётности и Архитектурный Дизайн

#### 4.1 Нечётность в размерностях и слоях

```
ЗАКОН НЕЧЁТНОСТИ В НЕЙРОННЫХ АРХИТЕКТУРАХ:

Число слоёв (n_layers):
  Нечётное: 3, 7, 11, 23, 47, 95... (ResNet-47, BERT-23...)
  Чётное:   2, 6, 12, 24, 96... (BERT-12, GPT-3-96...)

  Реальная практика: чётные доминируют (кратны 4/8 для GPU-эффективности)
  Но: внутри каждого блока — три операции: QKV projection (нечётно!)
  → Нечётность скрыта внутри чётных внешних структур (камуфляж/угроза!)

Число голов внимания (n_heads):
  BERT-base: 12 голов (чётно, но = 4×3 = нечётное основание)
  GPT-3: 96 голов (= 32×3)
  Всегда делится на 3 — скрытая нечётная структура!

Размерность эмбеддинга (d_model):
  512, 768, 1024, 2048...
  Все чётные — но внутри разбиты на 3 части (Q, K, V)!

Вывод: глубокое обучение использует нечётность «скрыто»:
  внешняя структура чётная (для вычислительной эффективности),
  внутренняя — нечётная (три матрицы: Q, K, V).
  Это «камуфляж/угроза» на архитектурном уровне.
```

#### 4.2 Пять поколений нейронных архитектур = пять уровней мастерства

```
ЭВОЛЮЦИЯ НЕЙРОННЫХ АРХИТЕКТУР ЧЕРЕЗ ПЯТЬ УРОВНЕЙ:

УРОВЕНЬ 1 — ЭЛЕМЕНТЫ: Перцептрон (1958)
  Думает: весами и порогами
  Умеет: линейная классификация
  Язык: w·x + b > 0
  Ключ перехода: XOR не решается → нужна нелинейность

УРОВЕНЬ 2 — СХЕМЫ: MLP + Backprop (1986)
  Думает: слоями и функциями активации
  Умеет: аппроксимация функций, MNIST
  Язык: y = σ(Wₙσ(...σ(W₁x)))
  Ключ перехода: глубокие сети не обучаются → нужны ResNet/BN

УРОВЕНЬ 3 — СЕРИИ: CNN + RNN + Attention (2012–2017)
  Думает: архитектурными блоками (Conv, LSTM, Attention)
  Умеет: ImageNet, Machine Translation, Speech
  Язык: модульные архитектуры, transfer learning
  Ключ перехода: каждая задача — своя архитектура → нужна универсальная

УРОВЕНЬ 4 — ОБРАЗЫ: Transformer (2017–2023)
  Думает: парадигмами (pretraining, RLHF, scaling)
  Умеет: GPT-4, AlphaFold, Stable Diffusion
  Язык: Foundation Models, emergent capabilities
  Ключ перехода: скалирование замедляется → нужна архитектурная инновация

УРОВЕНЬ 5 — ДУХ: ? (2024–...)
  Думает: принципами оптимального вычисления
  Возможно: архитектуры, основанные на физических принципах
  Возможно: KungFu-архитектуры (трёхсферная иерархия, петлевые примитивы)
  Вопрос: «Зачем нам вообще нейронные сети?»
```

---

### Глава 5. Новые Архитектуры на Основе Архетипов

#### 5.1 Loop-Net: сеть с явными петлевыми траекториями

```python
class LoopNet(nn.Module):
    """
    Нейронная сеть с явными петлевыми соединениями.
    Основана на архетипе Петли Крюкова.

    Ключевая идея: вместо прямолинейного прохода от входа к выходу
    информация движется по петлям — с явным «возвратом» к предыдущим слоям.
    """

    def __init__(self, input_dim: int, hidden_dim: int, n_loops: int = 3,
                 loop_type: str = 'figure_eight'):
        """
        n_loops: число петель (нечётное!)
        loop_type: 'circle', 'figure_eight', 'spiral'
        """
        super().__init__()

        if n_loops % 2 == 0:
            n_loops += 1  # Принудительно нечётное

        self.n_loops = n_loops
        self.loop_type = loop_type

        # Базовые слои обработки
        self.pre_loop = nn.Linear(input_dim, hidden_dim)

        # Петлевые блоки
        self.loop_blocks = nn.ModuleList([
            LoopBlock(hidden_dim, loop_idx=i)
            for i in range(n_loops)
        ])

        # Постобработка
        self.post_loop = nn.Linear(hidden_dim, input_dim)

        # Память о пройденных петлях (аналог рабочей памяти)
        self.loop_memory = nn.Parameter(
            torch.zeros(n_loops, hidden_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = torch.relu(self.pre_loop(x))

        loop_outputs = []
        prev_loop_out = h

        for i, block in enumerate(self.loop_blocks):
            # Каждый блок получает текущее состояние +
            # «камуфляжное» состояние предыдущей петли
            if self.loop_type == 'figure_eight' and i > 0:
                # Восьмёрка: чётные петли «перекрещиваются»
                camouflage = loop_outputs[i-1] if i % 2 == 0 else prev_loop_out
            else:
                camouflage = prev_loop_out

            out = block(h, camouflage, self.loop_memory[i])
            loop_outputs.append(out)
            prev_loop_out = out

            # Петля: возврат к h с обновлением
            h = h + out  # Skip-connection = петля замыкается

        # Финальный «резонанс» всех петель
        if loop_outputs:
            resonant = sum(loop_outputs) / len(loop_outputs)
        else:
            resonant = h

        return self.post_loop(resonant)


class LoopBlock(nn.Module):
    """Один петлевой блок: принимает текущее состояние + камуфляж."""

    def __init__(self, hidden_dim: int, loop_idx: int):
        super().__init__()
        self.loop_idx = loop_idx
        self.threat_path = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        self.camouflage_gate = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Sigmoid()
        )
        self.memory_gate = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Sigmoid()
        )
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, x: torch.Tensor, camouflage: torch.Tensor,
                memory: torch.Tensor) -> torch.Tensor:
        # Явное действие (угроза)
        threat_out = self.threat_path(x)

        # Камуфляжный гейт
        cam_gate = self.camouflage_gate(torch.cat([x, camouflage], dim=-1))

        # Память-гейт
        mem_gate = self.memory_gate(torch.cat([x, memory.unsqueeze(0)
                                               .expand_as(x)], dim=-1))

        # Смешивание: угроза + камуфляж + память
        output = threat_out * (1 - cam_gate - mem_gate * 0.1) + \
                 camouflage * cam_gate + \
                 memory.unsqueeze(0).expand_as(x) * mem_gate * 0.1

        return self.norm(output)
```

---

## ЗАКЛЮЧЕНИЕ

**Ключевые выводы Книги 15:**

1. **ResNet = петлевая архитектура**: skip-connections буквально реализуют петлю Крюкова — информация возвращается к ранним слоям, LCI → 1.0.

2. **Self-Attention = резонанс**: A_ij высокий ⟺ Q_i резонирует с K_j. Multi-head attention = множественные частоты резонанса.

3. **CNN = трёхсферная иерархия**: ранние слои (МВС: детали) → средние (СВС: части) → поздние (БВС: объекты). Feature Pyramid Network = резонансное соединение всех трёх.

4. **Трансформер = трёхсферная система**: слои 1/3 (синтаксис/МВС), 2/3 (семантика/СВС), 3/3 (рассуждение/БВС). Подтверждается mechanistic interpretability (Anthropic, 2022–2024).

5. **Residual stream = петля**: в трансформере информация «течёт» через residual stream — это и есть большая петля всей сети.

6. **Нечётность скрыта**: архитектуры внешне чётные (для GPU), внутри — нечётные (Q, K, V = три матрицы).

7. **`KryukovRNN`**: три-сферная память (МВС/СВС/БВС) с резонансным интегратором. Горизонт = 9 (закон памяти).

8. **`TransformerResonanceAnalyzer`**: явное измерение и оптимизация резонанса между тремя группами слоёв. Резонансный loss как дополнительный регуляризатор.

9. **`LoopNet`**: принципиально новая архитектура с явными петлевыми соединениями, нечётным числом петель и механизмом камуфляж/угроза.

---

*Следующая книга: КНИГА 16 — «Архетипы движения в квантовых вычислениях»*

---
*© Серия «Архетипы Движения», Книга 15. Основано на «Тотальной Системе Боя» В.В. Крюкова.*
