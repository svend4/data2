# ТОМ 3: БЫТОВЫЕ РОБОТЫ
## Архетипы движения «Тотальной Системы Боя» применительно к программированию
## бытовых роботов ростом 0.5–1.5 м

---

## ВВЕДЕНИЕ

Бытовой гуманоидный робот ростом 0,5–1,5 м — это, с точки зрения кинематики, **та же система сочленений**, что и человеческое тело. Проблемы, которые решала многовековая традиция кунг-фу — плавность движений, экономия энергии, координация нескольких конечностей, переключение между задачами — это те же проблемы, что стоят перед инженерами бытовой робототехники.

Архетипы движения из книги Крюкова предлагают **готовую библиотеку паттернов** для программирования роботов, занимающихся:
- Уборкой (подметание, протирание, вынос мусора)
- Приготовлением пищи (перемешивание, нарезка, мытьё посуды)
- Уходом за людьми (подача предметов, поддержка при ходьбе)
- Обслуживанием (перенос объектов, открывание дверей, сортировка)

---

## ГЛАВА 1: АРХИТЕКТУРА ДВИЖЕНИЯ РОБОТА — СИСТЕМА СФЕР

### 1.1 Три рабочие зоны робота

Иерархия МВС/СВС/БВС напрямую отображается на **три рабочие зоны** бытового робота.

```
БВС (Большая Внешняя Сфера):
  Радиус: вся досягаемость вытянутых рук
  Функция: навигация, перемещение к объекту, оценка пространства
  Управление: базовый контроллер движения (локомоторный уровень)

СВС (Средняя Внутренняя Сфера):
  Радиус: зона предплечий (~30–40 см от корпуса)
  Функция: основные манипуляции (перенос, открывание, нарезка)
  Управление: контроллер манипуляций

МВС (Малая Внутренняя Сфера):
  Радиус: зона кистей (~10–15 см)
  Функция: точная работа (застёгивание, набор текста, захват мелких объектов)
  Управление: контроллер тонкой моторики
```

### 1.2 Архитектура управляющего ПО

```python
class RobotMotionController:
    """
    Иерархический контроллер движения по модели трёх сфер.
    Каждый уровень независимо управляет своей зоной,
    но подчиняется вышестоящему.
    """

    def __init__(self):
        self.bvs = LargeExternalSphereController()   # Локомоция
        self.svs = MediumInternalSphereController()  # Манипуляции
        self.mvs = SmallInternalSphereController()   # Тонкая моторика

    def execute_task(self, task: Task):
        # Уровень БВС: подойти к объекту
        self.bvs.navigate_to(task.target_position)

        # Уровень СВС: выполнить основное действие
        self.svs.execute_manipulation(task.manipulation_type)

        # Уровень МВС: уточнить хват/позицию
        self.mvs.fine_adjust(task.precision_requirement)
```

### 1.3 Резонанс = Синхронизация уровней

Условие «резонанса» — одинаковая частота работы всех сфер — в робототехнике означает **синхронизацию управляющих циклов**:

```python
class ResonanceController:
    """
    Максимальная эффективность достигается, когда частоты
    обновления всех трёх контроллеров совпадают.
    """
    RESONANCE_FREQ_HZ = 50  # 50 Гц — оптимальная частота

    def is_resonant(self):
        return (
            self.bvs.update_freq == self.RESONANCE_FREQ_HZ and
            self.svs.update_freq == self.RESONANCE_FREQ_HZ and
            self.mvs.update_freq == self.RESONANCE_FREQ_HZ
        )

    def force_resonance(self):
        """При резонансе — плавность движений максимальна,
        нагрузка на сервоприводы минимальна."""
        for controller in [self.bvs, self.svs, self.mvs]:
            controller.set_update_freq(self.RESONANCE_FREQ_HZ)
```

---

## ГЛАВА 2: АРХЕТИП ПЕТЛИ — НЕПРЕРЫВНОСТЬ МАНИПУЛЯЦИЙ

### 2.1 Проблема «холостого хода»

Традиционные роботы-манипуляторы движутся по прямым траекториям (точка A → точка B), затем возвращаются. Возврат — «холостой ход», потеря времени и энергии.

**Решение по архетипу петли:**

Программировать движения роботической руки как **замкнутые кривые**, где возврат руки несёт полезную нагрузку:

```python
class LoopMotionPlanner:
    """
    Планировщик движений, основанный на замкнутых петлях.
    Возврат руки всегда несёт полезное действие.
    """

    def plan_wiping_motion(self, surface_area):
        """
        Протирание поверхности.
        Традиционно: прямые ходы туда-обратно.
        По петле: эллиптические дуги, каждый ход = чистая часть.
        """
        loops = []
        for strip in surface_area.horizontal_strips():
            loop = EllipticalLoop(
                center=strip.center,
                a=strip.width / 2,
                b=strip.height / 2,
                direction=CW  # или CCW в зависимости от сектора
            )
            loops.append(loop)
        return ChainedLoops(loops)

    def plan_stirring_motion(self, pot_radius, viscosity):
        """
        Помешивание в кастрюле.
        По петле: не прямые, а спиральные движения с изменяющимся радиусом.
        Эффективнее перемешивает, меньше брызг.
        """
        if viscosity < MEDIUM:
            return SimpleCircularLoop(radius=pot_radius * 0.7)
        else:
            return FigureEightLoop(
                radius1=pot_radius * 0.5,
                radius2=pot_radius * 0.8
            )
```

### 2.2 Двойная петля (восьмёрка) для двуручных операций

Перемешивание теста, мытьё посуды, складывание одежды — все двуручные операции естественно описываются восьмёркообразными траекториями:

```python
class BimanualLoopPlanner:
    """
    Двуручные операции на основе фигуры восьмёрки.
    Обе руки движутся синхронно или в противофазе.
    """

    def plan_dough_kneading(self):
        """
        Замес теста: классическая задача для восьмёрки.
        Левая рука: верхняя дуга
        Правая рука: нижняя дуга (противофаза)
        В точке пересечения: нажим (фиксация)
        """
        left_loop = UpperArcLoop(phase=0)
        right_loop = LowerArcLoop(phase=PI)  # противофаза

        return SynchronizedBimanualMotion(
            left=left_loop,
            right=right_loop,
            sync_point=CROSSOVER,
            sync_action=PRESS_DOWN
        )

    def plan_dish_washing(self, dish_shape):
        """
        Мытьё посуды: одна рука держит тарелку,
        другая описывает восьмёрку по её поверхности.
        """
        if dish_shape == PLATE:
            return FigureEightOnSurface(
                surface=dish_shape,
                amplitude=0.8,
                cross_point=CENTER
            )
```

---

## ГЛАВА 3: КАМУФЛЯЖ/УГРОЗА — МНОГОЗАДАЧНОСТЬ В ДВИЖЕНИИ

### 3.1 Принцип двойного назначения конечности

Каждое движение руки робота должно нести **двойную функцию**: выполнять основное действие и одновременно подготавливать следующее.

```python
class DualPurposeMotionEngine:
    """
    Каждое движение несёт две функции одновременно:
    PRIMARY (текущее действие) + SECONDARY (подготовка следующего).
    """

    def plan_table_clearing(self, items: List[Item]):
        """
        Уборка со стола.
        Рука несёт тарелку к мойке (PRIMARY),
        одновременно сканирует следующий объект (SECONDARY).
        """
        sequence = []
        for i, item in enumerate(items):
            next_item = items[i+1] if i+1 < len(items) else None

            move = DualPurposeMove(
                primary=CarryToSink(item),
                secondary=ScanObject(next_item) if next_item else ReturnToStandby()
            )
            sequence.append(move)
        return sequence
```

### 3.2 Противофаза рук

Из принципа камуфляж/угроза следует правило: когда одна рука работает «громко» (большая нагрузка), другая «дежурит» (малая нагрузка или подготовка). Это **балансировка нагрузки**:

```python
class LoadBalancer:
    """
    Балансировка нагрузки между двумя руками-манипуляторами.
    Аналог принципа Камуфляж/Угроза.
    """

    def balance_arms(self, left_arm: Arm, right_arm: Arm):
        left_load = left_arm.current_load()
        right_load = right_arm.current_load()

        if left_load > HEAVY_THRESHOLD:
            # Левая рука перегружена → правая берёт вспомогательную задачу
            right_arm.assign(LIGHT_SUPPORT_TASK)
        elif right_load > HEAVY_THRESHOLD:
            left_arm.assign(LIGHT_SUPPORT_TASK)
        else:
            # Обе свободны → работают в противофазе
            left_arm.set_phase(0)
            right_arm.set_phase(PI)
```

---

## ГЛАВА 4: РЕЖИМЫ ДЕЙСТВИЙ — ПОВЕДЕНЧЕСКИЕ ПРОФИЛИ РОБОТА

### 4.1 Режимы как состояния конечного автомата

Пять режимов боя из книги (фехтование, этажи, обезьяна, богомол, вьетнамский ключ) переводятся в **режимы работы бытового робота**:

```python
class RobotBehaviorFSM:
    """
    Конечный автомат поведения робота.
    Аналог режимов боя из системы Крюкова.
    """

    MODES = {
        'SCAN':      ScanMode(),       # Аналог фехтования: обследование среды
        'SEQUENTIAL': SeqMode(),       # Аналог этажей: последовательные операции
        'ADAPTIVE':  AdaptiveMode(),   # Аналог обезьяны: адаптация к изменениям
        'PRECISE':   PreciseMode(),    # Аналог богомола: долгая подготовка → точный удар
        'DUAL':      DualMode(),       # Аналог вьетнамского ключа: двойное действие
    }

    def select_mode(self, task: Task, env: Environment):
        if env.has_unknown_obstacles():
            return 'SCAN'
        elif task.requires_sequence():
            return 'SEQUENTIAL'
        elif env.is_dynamic():
            return 'ADAPTIVE'
        elif task.requires_high_precision():
            return 'PRECISE'
        elif task.benefits_from_dual_action():
            return 'DUAL'
```

### 4.2 Режим PRECISE — «Богомол» в бытовой робототехнике

Богомол долго замахивается и мгновенно бьёт. Для робота это означает **длинную фазу прицеливания и мгновенную фазу исполнения**:

```python
class PreciseMode:
    """
    Режим высокой точности.
    Долгая подготовка → мгновенное точное действие.
    Применение: нарезка продуктов, застёгивание одежды,
    вставка ключа в замок, набор мелких деталей.
    """

    def execute(self, task):
        # Фаза 1: долгая (0.5–2 сек) — позиционирование и прицеливание
        self.slow_approach(task.target, speed=VERY_SLOW)
        self.fine_position_adjustment(iterations=10)
        self.lock_position()

        # Фаза 2: мгновенная (0.05–0.1 сек) — само действие
        self.execute_action(task.action, speed=FAST)
```

### 4.3 Режим DUAL — «Вьетнамский ключ» для максимальной эффективности

```python
class DualMode:
    """
    Одно движение = два полезных действия одновременно.
    Применение: переноска + сортировка, уборка + сканирование,
    подача предмета + захват следующего.
    """

    def execute_dual_action(self, primary_task, secondary_task):
        if self.tasks_are_compatible(primary_task, secondary_task):
            # Оба действия выполняются одновременно
            motion = self.fuse_motions(
                primary_task.motion,
                secondary_task.motion
            )
            self.actuators.execute(motion)
        else:
            # Если несовместимы — выполняем последовательно
            self.execute_sequential(primary_task, secondary_task)
```

---

## ГЛАВА 5: ЗАКОН НЕЧЁТНОСТИ — ЦИКЛИЧЕСКИЕ ДОМАШНИЕ ОПЕРАЦИИ

### 5.1 Нечётные паттерны в уборке

Закон нечётности применяется к **циклическим операциям** уборки: подметание, протирание, пылесос.

```python
class CleaningPathPlanner:
    """
    Планировщик пути уборки на основе закона нечётности.
    Нечётное число проходов → симметричное завершение (робот возвращается в базу с той же стороны).
    Чётное → зеркальное (нужен дополнительный разворот).
    """

    def plan_sweeping_path(self, room: Room):
        strips = room.divide_into_strips()

        if len(strips) % 2 == 0:
            # Добавляем завершающий проход у базы
            strips.append(ReturnStrip())

        # Нечётное число полос → плавный возврат в базу
        return SweepingPath(
            strips=strips,
            direction=ALTERNATING,  # чередование направлений
            return_smooth=True
        )

    def plan_mopping_figure_eight(self, area):
        """
        Мытьё пола восьмёркой — оптимальный паттерн.
        3 восьмёрки = один цикл, робот возвращается на старт
        с противоположной стороны → симметричное покрытие.
        """
        return FigureEightCoverage(
            area=area,
            num_eights=3,       # нечётное
            overlap=0.2         # 20% перекрытие для качества
        )
```

---

## ГЛАВА 6: ПЯТЬ УРОВНЕЙ МАСТЕРСТВА — ОБУЧЕНИЕ РОБОТА

### 6.1 Уровни как этапы обучения / калибровки

Пять уровней мастерства описывают **эволюцию системы управления** — от жёстко запрограммированной до адаптивной:

| Уровень | Архетип Крюкова | Робот | Технология |
|---------|-----------------|-------|------------|
| 1 | Отдельные элементы | Жёсткое программирование | FSM, scripted actions |
| 2 | Связки и схемы | Поведенческое дерево | Behavior Trees |
| 3 | Серии + ритм | RL с фиксированным reward | Reinforcement Learning |
| 4 | Образы + установки | Высокоуровневое планирование | PDDL / HTN Planning |
| 5 | Боевой дух | Адаптивный агент с целями | Goal-Oriented Action Planning |

### 6.2 Прогрессивное обучение домашнего робота

```python
class RobotLearningPipeline:
    """
    Прогрессивный курс обучения по 5 уровням.
    """

    def level_1_scripted(self, robot):
        """Уровень 1: жёсткие скрипты для базовых задач."""
        robot.add_script('carry_cup', CupCarryScript())
        robot.add_script('wipe_table', TableWipeScript())
        robot.add_script('open_door', DoorOpenScript())

    def level_2_behavior_tree(self, robot):
        """Уровень 2: деревья поведения для связок действий."""
        bt = BehaviorTree()
        bt.add_sequence('make_tea', [
            FillKettle(), BoilWater(), PlaceTeabag(),
            PourWater(), WaitBrewing(), ServeInCup()
        ])
        robot.behavior_tree = bt

    def level_3_reinforcement_learning(self, robot):
        """Уровень 3: обучение с подкреплением для адаптации."""
        env = HouseholdEnvironment()
        agent = PPOAgent(
            observation_space=env.obs_space,
            action_space=env.action_space,
            reward_fn=smooth_motion_reward  # Поощряем плавность (петли!)
        )
        robot.rl_agent = agent

    def level_4_symbolic_planning(self, robot):
        """Уровень 4: символическое планирование (образы = высокоуровневые цели)."""
        planner = HTNPlanner()
        planner.add_method('clean_kitchen', KitchenCleaningMethod())
        planner.add_method('prepare_breakfast', BreakfastPreparationMethod())
        robot.planner = planner

    def level_5_goal_oriented(self, robot):
        """Уровень 5: Goal-Oriented Agent — робот понимает намерения хозяина."""
        goap = GOAPAgent()
        goap.add_goal('house_is_clean', weight=0.8)
        goap.add_goal('owner_is_comfortable', weight=1.0)
        goap.add_goal('energy_efficient', weight=0.5)
        robot.goap = goap
```

---

## ГЛАВА 7: ЗАКОН ПАМЯТИ — КОМПРЕССИЯ ЗАДАЧ РОБОТА

### 7.1 Число Миллера в памяти робота

Закон максимальной памяти (≤ 9 элементов в рабочей памяти) соответствует когнитивным ограничениям — но также и **вычислительным ограничениям** роботов в реальном времени.

```python
class TaskMemoryManager:
    """
    Управление рабочей памятью задач.
    По закону Крюкова: не более 9 задач одновременно в рабочей очереди.
    """
    MAX_WORKING_TASKS = 7  # Оптимум (число Миллера 7±2)

    def schedule_tasks(self, all_tasks: List[Task]):
        # Группируем похожие задачи в «схемы» (аналог связок)
        grouped = self.cluster_by_similarity(all_tasks)

        # В рабочей очереди — не более MAX_WORKING_TASKS схем
        working_queue = grouped[:self.MAX_WORKING_TASKS]

        # Остальное — в «долгосрочной памяти» (следующий цикл уборки)
        deferred_queue = grouped[self.MAX_WORKING_TASKS:]

        return working_queue, deferred_queue
```

### 7.2 «Сжатие» движений для экономии энергии

Аналог «сжатия схемы» (уровень 3) — **adaptive amplitude control**:

```python
class AmplitudeAdaptiveController:
    """
    Адаптирует амплитуду движений к ситуации.
    Малая амплитуда + высокая частота = экономия энергии.
    Большая амплитуда = реальное исполнение.
    """

    def execute_with_adaptive_amplitude(self, motion, priority):
        if priority == HIGH:
            # Полная амплитуда — задача важная
            self.execute_full_amplitude(motion)
        elif priority == MEDIUM:
            # 50% амплитуды — стандартный режим
            self.execute_scaled_motion(motion, scale=0.5)
        elif priority == LOW:
            # Минимальная амплитуда — «вхолостую», подготовка
            self.execute_minimal_motion(motion, scale=0.1)
```

---

## ГЛАВА 8: КОНКРЕТНЫЕ АЛГОРИТМЫ ДЛЯ БЫТОВОГО РОБОТА

### 8.1 Алгоритм приготовления пищи (архетип восьмёрки)

```python
def cook_scrambled_eggs(robot, pan, eggs, spatula):
    """
    Приготовление яичницы.
    Использует: петлю (помешивание), камуфляж/угроза (одна рука держит сковороду,
    другая мешает), закон нечётности (нечётное число мешающих движений = симметричное
    покрытие всей поверхности).
    """

    # Фаза 1: БВС — подойти к плите
    robot.bvs.navigate_to(stove.position)

    # Фаза 2: СВС — поставить сковороду
    with robot.dual_arm_mode():
        robot.left_arm.hold(pan)          # КАМУФЛЯЖ (держит)
        robot.right_arm.execute(          # УГРОЗА (действует)
            FigureEightLoop(
                radius=pan.radius * 0.7,
                tool=spatula,
                num_loops=7,              # НЕЧЁТНОЕ число
                pressure=LIGHT
            )
        )

    # Фаза 3: МВС — следить за готовностью
    while not pan.eggs_are_done():
        robot.mvs.scan_surface(pan.surface)
        robot.mvs.adjust_spatula_angle()

    robot.bvs.navigate_to(plate.position)
    robot.svs.transfer(pan, plate)
```

### 8.2 Алгоритм уборки с адаптацией (архетип системы окон)

```python
def adaptive_room_cleaning(robot, room):
    """
    Уборка комнаты с адаптацией к препятствиям.
    Использует систему окон: робот намеренно оставляет 'окна'
    в маршруте, анализирует препятствия и возвращается.
    """

    cleaned_zones = set()
    obstacle_map = ObstacleMap(room)

    while not room.is_fully_cleaned(cleaned_zones):
        # Выбрать следующую зону
        target_zone = robot.planner.next_zone(room, cleaned_zones, obstacle_map)

        # Попытаться добраться (оставляет 'окна' для повторного посещения)
        result = robot.bvs.try_navigate_to(target_zone)

        if result == BLOCKED:
            # 'Окно' заблокировано → запомнить, вернуться позже
            obstacle_map.mark_blocked(target_zone)
            # Атаковать следующее 'окно' (обходная схема)
            alt_zone = robot.planner.alternative_zone(target_zone)
            robot.bvs.navigate_to(alt_zone)
            robot.svs.clean(alt_zone)
            cleaned_zones.add(alt_zone)
        else:
            robot.svs.clean(target_zone)
            cleaned_zones.add(target_zone)
            # Заблокированная ранее зона теперь доступна
            obstacle_map.recheck_blocked_zones()
```

---

## ГЛАВА 9: ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ ЦЕЛЕВЫХ РОБОТОВ

### 9.1 Робот ростом 0.5 м (домашний ассистент малого формата)

```
Ростом 0.5 м — дети, пожилые люди, домашние животные — не угроза.
Зоны работы:
  БВС: радиус ~0.4 м (ограниченная мобильность)
  СВС: радиус ~0.2 м (работа у рабочей поверхности высотой 0.3–0.5 м)
  МВС: радиус ~0.08 м (тонкая работа)

Приоритетные задачи:
  - Подача предметов с нижних полок
  - Уборка пола
  - Сортировка мелких объектов
  - Игровой партнёр для детей

Ключевые алгоритмы:
  - Восьмёрка для подметания (амплитуда = 15 см)
  - Нечётные паттерны для обхода мебели
  - Режим DUAL для сортировки (захват + перенос одним движением)
```

### 9.2 Робот ростом 1.0–1.5 м (полноценный домашний ассистент)

```
Ростом 1.0–1.5 м — рабочие поверхности кухни, стол, кровать.
Зоны работы:
  БВС: радиус ~1.2 м (полная мобильность в комнате)
  СВС: радиус ~0.5 м (кухонные операции)
  МВС: радиус ~0.15 м (тонкая кулинарная работа)

Приоритетные задачи:
  - Приготовление пищи
  - Мытьё посуды
  - Застилание кровати
  - Помощь при одевании пожилых
  - Перенос и сортировка предметов

Ключевые алгоритмы:
  - Иерархия сфер в полном объёме
  - Режим PRECISE для нарезки (точность ±2 мм)
  - Закон нечётности для двуручных операций
  - Резонанс = энергоэффективный режим работы (снижение потребления на 25–30%)
```

---

## ГЛАВА 10: СРАВНЕНИЕ ПОДХОДОВ И ВЫВОДЫ

### 10.1 Традиционная vs. «Сферическая» архитектура

| Параметр | Традиционный подход | Подход «Трёх Сфер» |
|----------|--------------------|--------------------|
| Траектории | Прямолинейные | Криволинейные (петли) |
| Возврат руки | Холостой ход | Активная фаза |
| Управление | Единый контроллер | Иерархия 3 уровней |
| Адаптация | Заранее запрограммированная | Динамическое переключение режимов |
| Двуручность | Последовательная | Противофазная (синхронная) |
| Энергопотребление | Базовое | -20…30% при резонансе |
| Плавность | Требует специальной настройки | Вытекает из петлевых траекторий |

### 10.2 Ключевой принцип

Книга Крюкова даёт нам фундаментальный принцип, который в робототехнике ещё не получил явной формулировки:

> **Движение эффективно тогда, когда каждая фаза несёт двойную функцию (PRIMARY + SECONDARY), все уровни управления синхронизированы (РЕЗОНАНС), а траектория является замкнутой кривой (ПЕТЛЯ).**

Это принцип **тотальной эффективности движения** — применимый к любой кинематической системе, включая бытовых роботов любого размера.

---

*Том 3 из 10. Продолжение — Том 4: Программирование и алгоритмы.*
