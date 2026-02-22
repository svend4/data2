# ТОМ 135: 4 БУЛЕВЫ ОПЕРАЦИИ → ЛОГИКА РЕШЕНИЙ ЧВС
## AND · OR · NOT · XOR — Алгебра булевых ЧВС-решений
### «4 основные булевы операции = фундамент цифровой логики»

**Автор**: Крюков В.В. / синтез ЕТД
**Серия VII — Математические основания ЕТД**
**Источник**: Булева алгебра / логика высказываний

---

## ВВЕДЕНИЕ

**Булева алгебра** (Джордж Буль, 1854) — система логики с двумя значениями (0/1, ложь/истина). Основу составляют **4 операции**:

1. **AND** (конъюнкция, ∧) — «и»
2. **OR** (дизъюнкция, ∨) — «или»
3. **NOT** (отрицание, ¬) — «не»
4. **XOR** (исключающее или, ⊕) — «или, но не оба»

Из этих 4 операций строится вся цифровая электроника, логика, теория вычислений.

**Тезис тома**: 4 булевы операции = 4 типа ЧВС-решений. Каждое тактическое решение в ЕТД — один из 4 логических типов.

---

## ЧАСТЬ I: 4 БУЛЕВЫ ОПЕРАЦИИ → 4 ТИПА ЧВС-РЕШЕНИЙ

### 1.1 Таблица соответствий

| Операция | Логика | ЧВС-решение | ЕТД-пример |
|----------|--------|------------|-----------|
| **AND** | A ∧ B = 1 только если оба 1 | Одновременное условие | Атаковать ТОЛЬКО если: свободный = True AND дистанция = True |
| **OR** | A ∨ B = 1 если хоть один 1 | Альтернативное условие | Защита: блок OR уход OR контратака |
| **NOT** | ¬A = инверсия | Инверсия контекста | Не атака → защита; Не защита → атака |
| **XOR** | A ⊕ B = 1 если ровно один 1 | Исключительный выбор | Или бросок, или удар — но не оба одновременно |

```python
from typing import Union

BoolVal = Union[bool, int]

class CVSBooleanLogic:
    """
    4 булевы операции как 4 типа тактических ЧВС-решений.
    """

    @staticmethod
    def AND(cond_a: BoolVal, cond_b: BoolVal) -> bool:
        """
        AND (МВС ∧ СВС): Атаковать ТОЛЬКО если ОБА условия выполнены.
        Дистанция в норме И кисть свободна → удар.
        Строгое условие.
        """
        return bool(cond_a) and bool(cond_b)

    @staticmethod
    def OR(cond_a: BoolVal, cond_b: BoolVal) -> bool:
        """
        OR (МВС ∨ СВС): Действовать если ХОТЯ БЫ ОДНО условие.
        Блок OR контратака → хоть что-то делать при атаке.
        Мягкое условие.
        """
        return bool(cond_a) or bool(cond_b)

    @staticmethod
    def NOT(cond_a: BoolVal) -> bool:
        """
        NOT (¬МВС): Инверсия — если атака невозможна, то защита.
        NOT атака → защита.
        NOT напряжение → расслабление.
        """
        return not bool(cond_a)

    @staticmethod
    def XOR(cond_a: BoolVal, cond_b: BoolVal) -> bool:
        """
        XOR (МВС ⊕ СВС): Исключительный выбор — одно или другое, но не оба.
        Или бросок, или удар (нельзя одновременно).
        Ситуации «или-или».
        """
        return bool(cond_a) ^ bool(cond_b)

    def cvs_decision(self, situation: dict) -> str:
        """
        Логическая система ЧВС-решений на основе 4 булевых операций.
        """
        in_range = situation.get('in_range', False)
        hand_free = situation.get('hand_free', False)
        attack_possible = situation.get('attack_possible', False)
        throw_position = situation.get('throw_position', False)

        # AND: атаковать кулаком — ТОЛЬКО при дистанции И свободной руке
        punch = self.AND(in_range, hand_free)

        # OR: защищаться — при любой угрозе (блок OR уход)
        defend = self.OR(not in_range, not attack_possible)

        # XOR: бросок OR удар (но не оба)
        decisive_action = self.XOR(throw_position, attack_possible)

        # NOT: если атаковать нельзя → обязательно в защиту
        must_defend = self.NOT(attack_possible)

        if punch and decisive_action:
            return 'МВС-удар (AND + XOR выбрали удар)'
        elif throw_position and decisive_action:
            return 'Бросок (XOR выбрал бросок)'
        elif must_defend:
            return 'Защита (NOT атака)'
        else:
            return 'Ожидание (OR: нет угрозы)'

logic = CVSBooleanLogic()
result = logic.cvs_decision({'in_range': True, 'hand_free': True,
                              'attack_possible': True, 'throw_position': False})
print(result)  # МВС-удар
```

### 1.2 Таблицы истинности для ЧВС

```python
def print_cvs_truth_table():
    """Таблица истинности 4 операций для ЧВС."""
    logic = CVSBooleanLogic()
    print("A   B  | AND  OR   NOT_A XOR")
    print("───────┼─────────────────────")
    for a in [False, True]:
        for b in [False, True]:
            and_r = int(logic.AND(a, b))
            or_r  = int(logic.OR(a, b))
            not_r = int(logic.NOT(a))
            xor_r = int(logic.XOR(a, b))
            print(f"{int(a)}   {int(b)}  |  {and_r}    {or_r}    {not_r}     {xor_r}")

# Таблица истинности ЧВС:
# A   B  | AND  OR   NOT_A XOR
# ───────┼─────────────────────
# 0   0  |  0    0    1     0
# 0   1  |  0    1    1     1
# 1   0  |  0    1    0     1
# 1   1  |  1    1    0     0
```

---

## ЧАСТЬ II: ЛОГИЧЕСКИЕ ВЕНТИЛИ = СФЕРЫ

### 2.1 4 базовых вентиля → 4 сферы

```python
class LogicGates:
    """
    4 логических вентиля = 4 «элементарных» сферы в пространстве ЧВС.
    Любая схема = комбинация 4 вентилей.
    Любая техника ЕТД = комбинация 4 сфер.
    """

    GATES = {
        'AND': 'МВС',    # кисть — строгое точечное условие
        'OR':  'БВС',    # тело — широкое охватывающее условие
        'NOT': 'ЧВС',    # контекст — инверсия ситуации
        'XOR': 'СВС',    # предплечье — выбор между двумя вариантами
    }

    def universal_gate_nand(self, a: bool, b: bool) -> bool:
        """
        NAND = NOT(AND) — универсальный вентиль.
        Из одного NAND строится любая булева функция.
        ЕТД-аналог: ЧВС(МВС) = контекст отрицает прямое условие.
        Универсальность = из одного приёма — любая техника.
        """
        return not (a and b)
```

### 2.2 Булева функция ЛЗП

```python
def lci_boolean_function(mvs_active: bool, svs_active: bool,
                           bvs_active: bool, cvs_active: bool) -> float:
    """
    Булева функция ЛЗП:
    ЛЗП зависит от булевой комбинации активных сфер.
    """
    import math

    # Вклад каждой активной сферы
    weights = {'МВС': 0.5, 'СВС': 1.0, 'БВС': 1.5, 'ЧВС': 2.0}
    active = [
        (mvs_active, 'МВС'),
        (svs_active, 'СВС'),
        (bvs_active, 'БВС'),
        (cvs_active, 'ЧВС'),
    ]

    # AND всех активных: синергия только при полной активации
    all_active = all(a for a, _ in active)

    base = sum(weights[s] for a, s in active if a)
    synergy = base * math.pi / 4 if all_active else base

    return synergy

# Все 4 активны → π/4 синергия
print(lci_boolean_function(True, True, True, True))   # > base
# Только 3 → нет синергии
print(lci_boolean_function(True, True, True, False))  # = base
```

---

## ЗАКЛЮЧЕНИЕ

**4 булевы операции** → **4 типа ЧВС-решений**:

1. **AND** (∧) → МВС: Строгое условие — «удар только если И дистанция, И рука свободна»
2. **OR** (∨) → БВС: Мягкое условие — «защита при любой из угроз»
3. **NOT** (¬) → ЧВС: Инверсия — «если атака невозможна → защита»
4. **XOR** (⊕) → СВС: Исключительный выбор — «или бросок, или удар»

> Из 4 булевых операций строится любая логическая схема. Из 4 сфер ЕТД строится любая тактическая схема. NAND (универсальный вентиль) = ЧВС(МВС) = контекст+кисть — из них одних можно построить всё.

---
*ТОМ 135 / СЕРИЯ VII / ЕТД 2026*
