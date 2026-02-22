# ТОМ 145: 4 МЕТОДА ИНТЕГРИРОВАНИЯ → НАКОПЛЕНИЕ ЛЗП
## Подстановка · По частям · Дроби · Тригонометрия → 4 способа накопления потенциала
### «4 классических метода нахождения первообразных»

**Автор**: Крюков В.В. / синтез ЕТД
**Серия VII — Математические основания ЕТД**
**Источник**: Математический анализ / интегральное исчисление

---

## ВВЕДЕНИЕ

В математическом анализе существуют **4 основных метода интегрирования**:

1. **Метод подстановки** (замена переменной): ∫f(g(x))g'(x)dx = ∫f(u)du
2. **Интегрирование по частям**: ∫u·dv = u·v − ∫v·du
3. **Разложение на простые дроби**: рациональные функции → сумма простейших дробей
4. **Тригонометрические подстановки**: x = a·sin(t), a·tan(t), a·sec(t)

**Тезис тома**: 4 метода интегрирования = 4 стратегии накопления ЛЗП. Интеграл = суммарный потенциал, накопленный за тренировку. Каждая «стратегия» оптимальна в своём контексте.

---

## ЧАСТЬ I: 4 МЕТОДА → 4 СТРАТЕГИИ НАКОПЛЕНИЯ ЛЗП

```python
import math
from typing import Callable

class IntegrationETD:
    """
    4 метода интегрирования как 4 стратегии накопления ЛЗП.
    ЛЗП_total = ∫ lci_rate(t) dt = суммарный потенциал.
    """

    @staticmethod
    def substitution_mvs(lci_function: Callable, g: Callable,
                          g_prime: Callable, t_0: float, t_1: float,
                          n: int = 1000) -> float:
        """
        МЕТОД ПОДСТАНОВКИ (МВС):
        ∫f(g(t))·g'(t)dt = ∫f(u)du, где u = g(t).

        ЕТД: Заменить «переменную» техники.
        Вместо прямого удара (t) → подставить косвенный (u = поворот t).
        Тот же ЛЗП, другая форма техники.

        Численно: метод прямоугольников.
        """
        dt = (t_1 - t_0) / n
        total = 0.0
        for i in range(n):
            t = t_0 + i * dt
            u = g(t)
            total += lci_function(u) * g_prime(t) * dt
        return total

    @staticmethod
    def integration_by_parts_svs(u_fn: Callable, v_prime_fn: Callable,
                                   t_0: float, t_1: float,
                                   n: int = 1000) -> float:
        """
        ИНТЕГРИРОВАНИЕ ПО ЧАСТЯМ (СВС):
        ∫u·dv = [u·v]_{t0}^{t1} − ∫v·du

        ЕТД: «По частям» = БВС делает одно, МВС делает другое.
        Суммарный ЛЗП = (БВС×МВС)|граница − ∫(МВС × d_БВС).
        Разделение труда между сферами.
        """
        dt = (t_1 - t_0) / n

        # v(t) = ∫v'(t)dt (численно)
        v_values = []
        v = 0.0
        t_grid = [t_0 + i * dt for i in range(n + 1)]
        for t in t_grid:
            v_values.append(v)
            v += v_prime_fn(t) * dt

        # u·v на границах
        uv_t1 = u_fn(t_1) * v_values[-1]
        uv_t0 = u_fn(t_0) * v_values[0]
        boundary_term = uv_t1 - uv_t0

        # ∫v·du = ∫v(t)·u'(t)dt (численно)
        eps = 1e-5
        integral_v_du = 0.0
        for i in range(n):
            t = t_grid[i]
            u_prime = (u_fn(t + eps) - u_fn(t)) / eps
            integral_v_du += v_values[i] * u_prime * dt

        return boundary_term - integral_v_du

    @staticmethod
    def partial_fractions_bvs(coefficients: list,
                                t_0: float, t_1: float) -> float:
        """
        РАЗЛОЖЕНИЕ НА ДРОБИ (БВС):
        f(t) = A₁/(t−r₁) + A₂/(t−r₂) + ...
        ∫f dt = Σ Aₖ·ln|t−rₖ|

        ЕТД: Разложить сложную технику на простейшие компоненты.
        Каждый «простейший дробный» компонент = одна базовая сфера.
        Суммарный ЛЗП = сумма вкладов компонент.
        """
        # Каждый коэффициент: (A, r) → вклад A·ln|t−r|
        lci_t1 = sum(A * math.log(abs(t_1 - r) + 1e-10) for A, r in coefficients)
        lci_t0 = sum(A * math.log(abs(t_0 - r) + 1e-10) for A, r in coefficients)
        return lci_t1 - lci_t0

    @staticmethod
    def trig_substitution_cvs(a: float, t_0: float, t_1: float,
                               n: int = 1000) -> float:
        """
        ТРИГОНОМЕТРИЧЕСКАЯ ПОДСТАНОВКА (ЧВС):
        При ∫√(a²−x²)dx: x = a·sin(θ) → dx = a·cos(θ)dθ.

        ЕТД: ЧВС-подстановка = «тригонометрический» контекст.
        Область под кривой ЛЗП в форме полуокружности (радиус a).
        = площадь = π·a²/2.
        При a = π/4: площадь = π·(π/4)²/2 = π³/32 ≈ 0.969.
        """
        # Численно: ∫_{-a}^{a} √(a²−x²) dx = π·a²/2
        dt = (t_1 - t_0) / n
        total = 0.0
        for i in range(n):
            x = t_0 + i * dt
            under = a**2 - x**2
            if under >= 0:
                total += math.sqrt(under) * dt
        return total
```

### 1.2 Накопленный ЛЗП = определённый интеграл

```python
def total_lci_session(lci_rate: Callable, duration: float,
                       method: str = 'substitution') -> float:
    """
    Суммарный ЛЗП тренировки = ∫₀^T lci_rate(t) dt.
    lci_rate(t) = мгновенная «скорость» накопления потенциала.

    4 метода интегрирования:
    - substitution:    lci_rate через «замену» техники (МВС)
    - by_parts:        lci_rate = u·v' (разделение сфер, СВС)
    - partial_fractions: lci_rate = A/(t−r) (компоненты, БВС)
    - trigonometric:   lci_rate = √(a²−t²) (ЧВС-окружность)
    """
    integrator = IntegrationETD()

    if method == 'substitution':
        g = lambda t: math.sin(t)
        g_prime = lambda t: math.cos(t)
        return integrator.substitution_mvs(lambda u: u**2, g, g_prime, 0, duration)

    elif method == 'by_parts':
        u_fn = lambda t: t
        v_prime = lambda t: math.exp(-t * math.pi / 4)
        return integrator.integration_by_parts_svs(u_fn, v_prime, 0, duration)

    elif method == 'partial_fractions':
        coefficients = [(1.0, -1.0), (2.0, -2.0)]
        return integrator.partial_fractions_bvs(coefficients, 0.1, duration)

    elif method == 'trigonometric':
        a = math.pi / 4
        return integrator.trig_substitution_cvs(a, -a, a)

    return 0.0

# Тригонометрическая подстановка: ЧВС-круг с радиусом π/4
lci_cvs_circle = total_lci_session(None, 0, method='trigonometric')
print(f"ЛЗП ЧВС-полуокружности: {lci_cvs_circle:.4f}")
# ≈ π·(π/4)²/2 ≈ 0.969
```

---

## ЗАКЛЮЧЕНИЕ

**4 метода интегрирования** → **4 стратегии накопления ЛЗП**:

1. **Подстановка** (МВС) → Замена техники: тот же потенциал, иная форма
2. **По частям** (СВС) → Разделение труда: одна сфера работает, другая «интегрирует»
3. **Дроби** (БВС) → Декомпозиция: сложная техника = сумма простых компонент
4. **Тригонометрия** (ЧВС) → Круговая подстановка: ЧВС-цикл с радиусом π/4

> Суммарный ЛЗП тренировки = ∫lci_rate(t)dt. Тригонометрическая подстановка для ЧВС: площадь полуокружности = π·(π/4)²/2 ≈ 0.969 — это «базовая» ЛЗП-единица ЧВС.

---
*ТОМ 145 / СЕРИЯ VII / ЕТД 2026*
