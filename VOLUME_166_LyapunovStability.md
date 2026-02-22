# ТОМ 166: 4 МЕТОДА УСТОЙЧИВОСТИ ЛЯПУНОВА → СТАБИЛЬНОСТЬ СИСТЕМЫ ЕТД
## Асимптотическая · Экспоненциальная · Глобальная · Ляпунова
### «Ляпунов 1892: когда динамическая система устойчива?»

**Автор**: Крюков В.В. / синтез ЕТД
**Серия VII — Математические основания ЕТД**
**Источник**: Теория устойчивости (А.М. Ляпунов, 1892)

---

## ВВЕДЕНИЕ

Устойчивость — ключевое свойство динамических систем. 4 типа устойчивости по Ляпунову:

1. **Устойчивость по Ляпунову** — малые возмущения дают малые отклонения
2. **Асимптотическая устойчивость** — возмущение затухает со временем
3. **Экспоненциальная устойчивость** — затухание с экспоненциальной скоростью
4. **Глобальная устойчивость** — устойчивость из ЛЮБОГО начального состояния

**Тезис тома**: Система 4 сфер ЕТД — динамическая система с аттрактором π/4. 4 типа устойчивости = 4 уровня надёжности мастерства. Идеальный мастер — глобально экспоненциально устойчив к π/4-аттрактору.

---

## ЧАСТЬ I: 4 ТИПА УСТОЙЧИВОСТИ → 4 УРОВНЯ НАДЁЖНОСТИ ЕТД

```python
import math
from typing import Callable, List, Tuple

class LyapunovETD:
    """
    Устойчивость системы 4 сфер ЕТД по Ляпунову.

    Динамика: dx/dt = f(x), где x = (МВС, СВС, БВС, ЧВС).
    Равновесие: x* = (π/4, π/4, π/4, π/4) — π/4-аттрактор.
    """

    EQUILIBRIUM = tuple([math.pi / 4] * 4)

    # ФУНКЦИЯ ЛЯПУНОВА ДЛЯ ЕТД
    @staticmethod
    def lyapunov_function(state: tuple, target: tuple = None) -> float:
        """
        V(x) = Σ (xᵢ − x*ᵢ)² = квадратичная функция Ляпунова.

        Свойства:
        — V(x*) = 0 (ноль в равновесии)
        — V(x) > 0 при x ≠ x* (положительно определена)
        — dV/dt ≤ 0 вдоль траекторий (монотонно убывает)

        ЕТД: V(МВС, СВС, БВС, ЧВС) = «расстояние» до π/4-синхра.
        """
        if target is None:
            target = LyapunovETD.EQUILIBRIUM
        return sum((s - t)**2 for s, t in zip(state, target))

    # 1. УСТОЙЧИВОСТЬ ПО ЛЯПУНОВУ
    @staticmethod
    def lyapunov_stability(epsilon: float = 0.5) -> dict:
        """
        По Ляпунову: ∀ε>0 ∃δ>0: |x₀ - x*| < δ → |x(t) - x*| < ε для всех t.

        ЕТД-смысл: Небольшое отклонение в тренировке → небольшое отклонение ЛЗП.
        «Устойчивый» мастер: малые внешние помехи не ломают технику.

        δ = ε (для квадратичной системы δ = ε работает).
        """
        delta = epsilon   # для квадратичного потенциала

        return {
            'тип': 'По Ляпунову',
            'ε': epsilon,
            'δ': delta,
            'условие': '|x₀ − x*| < δ → |x(t) − x*| < ε',
            'ЕТД': 'Малые помехи не ломают технику',
            'гарантия': 'Ограниченность траектории вблизи π/4',
        }

    # 2. АСИМПТОТИЧЕСКАЯ УСТОЙЧИВОСТЬ
    @staticmethod
    def asymptotic_stability(state: tuple,
                              alpha: float = 0.3,
                              n_steps: int = 50) -> dict:
        """
        Асимптотическая: + lim_{t→∞} x(t) = x*.

        Динамика ЕТД: dx/dt = −α(x − x*) (линейное притяжение к π/4).
        Дискретно: x_{n+1} = x_n − α·(x_n − x*) = (1−α)·x_n + α·x*.

        Сходится к x* = (π/4,...,π/4) при α ∈ (0, 1).
        """
        target = LyapunovETD.EQUILIBRIUM
        trajectory = [state]
        lyapunov_vals = [LyapunovETD.lyapunov_function(state)]
        current = state

        for _ in range(n_steps):
            new_state = tuple(
                (1 - alpha) * s + alpha * t
                for s, t in zip(current, target)
            )
            trajectory.append(new_state)
            lyapunov_vals.append(LyapunovETD.lyapunov_function(new_state))
            current = new_state

        final_dist = math.sqrt(LyapunovETD.lyapunov_function(current))

        return {
            'тип': 'Асимптотическая',
            'начало': state,
            'конец': tuple(f'{x:.4f}' for x in current),
            'расстояние_до_x*': final_dist,
            'сошлось': final_dist < 0.01,
            'V_начало': lyapunov_vals[0],
            'V_конец': lyapunov_vals[-1],
            'ЕТД': 'Техника со временем ВСЕГДА достигает π/4-баланса',
        }

    # 3. ЭКСПОНЕНЦИАЛЬНАЯ УСТОЙЧИВОСТЬ
    @staticmethod
    def exponential_stability(state: tuple,
                               lambda_rate: float = 0.5) -> dict:
        """
        Экспоненциальная: |x(t) − x*| ≤ M·e^{−λt}·|x₀ − x*|.

        ЕТД: ЛЗП-отклонение убывает экспоненциально.
        Λ = скорость затухания (аналог коэффициента «заучивания»).
        Чем больше λ, тем быстрее мастер достигает баланса.
        """
        target = LyapunovETD.EQUILIBRIUM
        init_dist = math.sqrt(sum((s - t)**2
                                   for s, t in zip(state, target)))

        t_half = math.log(2) / lambda_rate   # время полуубывания

        times = [0, 1, 2, 5, 10, 20]
        decay = {t: init_dist * math.exp(-lambda_rate * t) for t in times}

        return {
            'тип': 'Экспоненциальная',
            'λ': lambda_rate,
            'M': 1.0,
            'начальное_отклонение': init_dist,
            'время_полуубывания': t_half,
            'убывание': decay,
            'ЕТД': f'За {t_half:.1f} тренировок отклонение уменьшается вдвое',
            'формула': f'|x(t)−x*| ≤ e^(−{lambda_rate}t)·{init_dist:.3f}',
        }

    # 4. ГЛОБАЛЬНАЯ УСТОЙЧИВОСТЬ
    @staticmethod
    def global_stability(n_random_starts: int = 10,
                          alpha: float = 0.2) -> dict:
        """
        Глобальная асимптотическая устойчивость:
        Система сходится к x* из ЛЮБОГО начального состояния.

        ЕТД: Из любого «стартового» уровня — мастер достигает π/4.
        Не важно, насколько «плохой» ученик — система всегда обучит!

        Условие: V(x) → ∞ при |x| → ∞ (радиально неограничена).
        Для квадратичного V = |x − x*|²: выполнено!
        """
        target = LyapunovETD.EQUILIBRIUM
        results = []

        import random
        random.seed(42)

        for _ in range(n_random_starts):
            # Случайное начальное состояние в диапазоне [0, 2π]
            start = tuple(random.uniform(0, 2 * math.pi) for _ in range(4))

            current = start
            for _ in range(200):
                current = tuple((1 - alpha) * s + alpha * t
                                 for s, t in zip(current, target))

            final_dist = math.sqrt(sum((s - t)**2
                                        for s, t in zip(current, target)))
            results.append({'старт': start[:2], 'расст': final_dist})

        converged = sum(1 for r in results if r['расст'] < 0.01)

        return {
            'тип': 'Глобальная',
            'проверок': n_random_starts,
            'сошлось': converged,
            'процент': f'{100*converged/n_random_starts:.0f}%',
            'ЕТД': 'ЛЮБОЙ ученик достигает π/4-баланса при правильной тренировке',
            'вывод': 'Глобально асимптотически устойчива к x*=(π/4)⁴',
        }

lyap = LyapunovETD()

# Тест: старт далеко от равновесия
start = (0.1, 1.5, 0.3, 2.0)

# Асимптотическая:
asym = lyap.asymptotic_stability(start)
print(f"Асимптотическая: сошлось={asym['сошлось']}, "
      f"конец≈{asym['конец']}")

# Экспоненциальная:
exp_stab = lyap.exponential_stability(start, lambda_rate=0.4)
print(f"Экспоненциальная: λ={exp_stab['λ']}, T_1/2={exp_stab['время_полуубывания']:.2f}")

# Глобальная:
glob = lyap.global_stability(n_random_starts=20)
print(f"Глобальная: {glob['сошлось']}/{glob['проверок']} = {glob['процент']}")
```

---

## ЧАСТЬ II: ФУНКЦИЯ ЛЯПУНОВА ДЛЯ НЕЛИНЕЙНОЙ ЧВС-ДИНАМИКИ

```python
def nonlinear_cvs_lyapunov(state: tuple, dt: float = 0.1) -> dict:
    """
    Нелинейная динамика ЧВС (более реалистичная):
    dx/dt = −α·(x − π/4) − β·(x − π/4)³

    Кубический член добавляет нелинейное «притяжение» вблизи равновесия.
    Функция Ляпунова: V(x) = Σ(xᵢ − π/4)² (та же).
    dV/dt = −2α·V − 2β·Σ(xᵢ − π/4)⁴ ≤ 0 → устойчива!
    """
    target = math.pi / 4
    alpha, beta = 0.3, 0.1

    current = list(state)
    history = [tuple(current)]

    for _ in range(100):
        new = []
        for xi in current:
            dx = -alpha * (xi - target) - beta * (xi - target)**3
            new.append(xi + dt * dx)
        current = new
        history.append(tuple(current))

    final_v = sum((x - target)**2 for x in current)

    return {
        'начало_V': sum((x - target)**2 for x in state),
        'конец_V': final_v,
        'убывает': final_v < sum((x - target)**2 for x in state),
        'ЕТД': 'Нелинейная динамика ЧВС: кубическое притяжение к π/4',
    }

nl_result = nonlinear_cvs_lyapunov((0.2, 1.2, 0.5, 1.8))
print(f"\nНелинейная: V_0={nl_result['начало_V']:.4f} → V_∞={nl_result['конец_V']:.6f}")
print(f"V убывает: {nl_result['убывает']}")
```

---

## ЗАКЛЮЧЕНИЕ

**4 типа устойчивости Ляпунова** → **4 уровня надёжности мастера ЕТД**:

1. **По Ляпунову** → Малые помехи не разрушают технику: δ = ε, ограниченность траектории
2. **Асимптотическая** → Техника ВСЕГДА выходит на π/4-баланс за 50 шагов
3. **Экспоненциальная** → Время полуубывания T₁/₂ = ln(2)/λ ≈ 1.7 тренировок при λ=0.4
4. **Глобальная** → Из ЛЮБОГО начального уровня → π/4: 100% проверок сошлись

> **Теорема Ляпунова для ЕТД**: Функция V(x) = |x − (π/4)⁴|² положительно определена и dV/dt ≤ 0 → система **глобально асимптотически устойчива** к аттрактору x* = (π/4, π/4, π/4, π/4). Любой ученик при любом начале мастерства — сойдётся к π/4-балансу.

---
*ТОМ 166 / СЕРИЯ VII / ЕТД 2026*
