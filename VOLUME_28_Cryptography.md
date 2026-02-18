# КНИГА 28: АРХЕТИПЫ ДВИЖЕНИЯ В КРИПТОГРАФИИ И ИНФОРМАЦИОННОЙ БЕЗОПАСНОСТИ

## «Шифр как петля: движение информации сквозь секрет»

**Серия II:** «Прикладная ЕТД» | **Том 28 из 40**
**Автор:** На основе Единой Теории Движения (Серия I, тома 1–20)

---

## АННОТАЦИЯ

Криптография — наука о секретном движении информации. Каждый шифр — это замкнутая петля: открытый текст → шифрование → шифртекст → расшифрование → открытый текст. Ключ — мастер-шаблон (A3). Протоколы безопасности — трёхсферная иерархия (криптопримитив / протокол / система). Атака — нарушение петли через камуфляж или угрозу (A4). В этой книге мы строим криптографические системы и модели безопасности на основе 12 архетипов Крюкова, доказывая, что стойкость шифра — это LCI его петли.

---

## ГЛАВА 1: ШИФР КАК ЗАМКНУТАЯ ПЕТЛЯ

### 1.1 Криптографическая петля

```
Открытый текст M →
Шифрование E_k(M) = C →
Передача C по открытому каналу →
Расшифрование D_k(C) = M' →
Проверка M' = M (замыкание петли)
```

**LCI шифра** = вероятность успешного восстановления исходного сообщения:
- LCI = 1.0: идеальный шифр (одноразовый блокнот, без ошибок)
- LCI < 1.0: шум канала или уязвимость шифра
- LCI = 0: взломан (петля разомкнута злоумышленником)

```python
import numpy as np
from scipy.spatial import ConvexHull
from scipy.stats import entropy as scipy_entropy
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac
import struct

class CipherType(Enum):
    """Типы криптографических примитивов."""
    STREAM_CIPHER = "Поточный шифр (МВС: побайтовая петля)"
    BLOCK_CIPHER  = "Блочный шифр (СВС: блоковая петля)"
    PUBLIC_KEY    = "Асимметричный (БВС: математическая петля)"
    HASH          = "Хеш (однонаправленная петля)"
    MAC           = "MAC (петля с ключом)"
    AEAD          = "AEAD (петля с аутентификацией)"

@dataclass
class CryptoPrimitive:
    """Криптографический примитив."""
    name: str
    cipher_type: CipherType
    key_bits: int
    block_bits: int
    rounds: int          # Число раундов (нечётное оптимально!)
    security_bits: int   # Битовая стойкость

class CryptographicLoopAnalyzer:
    """
    Анализатор криптографических петель через ЕТД.
    LCI шифра = стойкость его петли шифрования-расшифрования.
    """

    def analyze_cipher_loop(self, primitive: CryptoPrimitive) -> Dict:
        """
        Анализ криптографической петли через параметры примитива.
        """
        # A1: Петля — обратимость шифрования
        is_invertible = primitive.cipher_type in (
            CipherType.STREAM_CIPHER, CipherType.BLOCK_CIPHER,
            CipherType.PUBLIC_KEY, CipherType.AEAD)
        loop_lci = 1.0 if is_invertible else 0.0  # Хеш — однонаправленная петля

        # A5: Нечётность числа раундов (закон нечётности!)
        rounds = primitive.rounds
        if rounds % 2 == 0:
            rounds_suggested = rounds + 1
        else:
            rounds_suggested = rounds
        odd_rounds = primitive.rounds % 2 != 0

        # A3: Мастер-шаблон — длина ключа соответствует стандарту
        key_standards = {
            CipherType.STREAM_CIPHER: 128,
            CipherType.BLOCK_CIPHER: 128,
            CipherType.PUBLIC_KEY: 2048,
            CipherType.HASH: 256,
            CipherType.MAC: 128,
            CipherType.AEAD: 128,
        }
        standard_key = key_standards.get(primitive.cipher_type, 128)
        key_score = min(1.0, primitive.key_bits / standard_key)

        # A2: Три сферы — уровни безопасности (примитив / протокол / система)
        security_score = min(1.0, primitive.security_bits / 128)

        # Резонанс трёх сфер: ключ / блок / раунды
        norms = np.array([
            min(1.0, primitive.key_bits / 256),
            min(1.0, primitive.block_bits / 128),
            min(1.0, primitive.rounds / 20),
        ])
        fracs = norms / max(norms.sum(), 1e-10)
        imbalance = float(np.abs(fracs - 1/3).sum() / 2)
        sphere_resonance = 1.0 - imbalance

        # Итоговая криптографическая стойкость (LCI системы)
        crypto_strength = (
            loop_lci * 0.3 +
            key_score * 0.3 +
            security_score * 0.2 +
            sphere_resonance * 0.1 +
            (0.1 if odd_rounds else 0.0)
        )

        return {
            'primitive': primitive.name,
            'cipher_type': primitive.cipher_type.value,
            'loop_lci': round(loop_lci, 3),
            'key_adequacy': round(key_score, 3),
            'security_score': round(security_score, 3),
            'sphere_resonance': round(sphere_resonance, 3),
            'odd_rounds': odd_rounds,
            'rounds_suggested': rounds_suggested,
            'crypto_strength': round(crypto_strength, 3),
            'recommendation': (
                'Безопасен' if crypto_strength > 0.8
                else 'Требует обновления' if crypto_strength > 0.5
                else 'Небезопасен — заменить немедленно'
            ),
        }

    def compare_cipher_suite(self, primitives: List[CryptoPrimitive]) -> Dict:
        """
        Сравнение набора криптографических примитивов.
        Оптимальный набор: нечётное число, три сферы покрыты.
        """
        n = len(primitives)
        if n % 2 == 0:
            n_suggested = n + 1  # Нечётное
        else:
            n_suggested = n

        analyses = [self.analyze_cipher_loop(p) for p in primitives]

        # Покрытие сфер: МВС/СВС/БВС должны присутствовать
        spheres_covered = set()
        for p in primitives:
            if p.cipher_type in (CipherType.STREAM_CIPHER, CipherType.MAC):
                spheres_covered.add('МВС')
            if p.cipher_type in (CipherType.BLOCK_CIPHER, CipherType.AEAD):
                spheres_covered.add('СВС')
            if p.cipher_type == CipherType.PUBLIC_KEY:
                spheres_covered.add('БВС')

        sphere_coverage = len(spheres_covered) / 3

        # Средняя стойкость
        avg_strength = float(np.mean([a['crypto_strength'] for a in analyses]))

        return {
            'n_primitives': n,
            'n_primitives_suggested': n_suggested,
            'is_odd': n % 2 != 0,
            'spheres_covered': list(spheres_covered),
            'sphere_coverage': round(sphere_coverage, 3),
            'avg_crypto_strength': round(avg_strength, 3),
            'suite_lci': round(sphere_coverage * avg_strength, 3),
            'missing_spheres': [s for s in ['МВС', 'СВС', 'БВС']
                                 if s not in spheres_covered],
            'weakest_primitive': min(analyses, key=lambda x: x['crypto_strength'])['primitive'],
        }
```

---

## ГЛАВА 2: ТРИ СФЕРЫ ИНФОРМАЦИОННОЙ БЕЗОПАСНОСТИ

### 2.1 МВС/СВС/БВС кибербезопасности

| Сфера | Уровень | Механизмы | Временная реакция |
|-------|---------|-----------|------------------|
| **МВС** | Примитивы | Шифры, хеши, MAC | Наносекунды–мкс |
| **СВС** | Протоколы | TLS, SSH, OAuth | Миллисекунды |
| **БВС** | Архитектура | PKI, Zero Trust, политики | Часы–месяцы |

```python
class SecurityThreeSphereAnalyzer:
    """
    Анализатор информационной безопасности через три сферы ЕТД.
    Здоровая система безопасности = три сферы в резонансе.
    """

    SECURITY_CONTROLS = {
        'МВС': [
            'AES-256-GCM шифрование',
            'SHA-3 хеширование',
            'Ed25519 подписи',
            'ChaCha20-Poly1305',
            'Argon2id хеширование паролей',
            'HKDF деривация ключей',
            'BLAKE3',
        ],  # 7 контролей — нечётное!
        'СВС': [
            'TLS 1.3',
            'mTLS аутентификация',
            'OAuth 2.0 / OIDC',
            'JWT с коротким TTL',
            'Certificate Pinning',
        ],  # 5 контролей — нечётное!
        'БВС': [
            'Zero Trust Architecture',
            'PKI и CA',
            'IAM политики',
        ],  # 3 контроля — нечётное!
    }

    def audit_security_posture(self, implemented_controls: Dict[str, List[str]]) -> Dict:
        """
        Аудит безопасности организации.
        implemented_controls: {сфера: [список реализованных контролей]}
        """
        sphere_scores = {}

        for sphere, required in self.SECURITY_CONTROLS.items():
            implemented = implemented_controls.get(sphere, [])
            coverage = sum(1 for c in required if c in implemented) / len(required)
            sphere_scores[sphere] = round(coverage, 3)

        # Резонанс сфер
        vals = np.array(list(sphere_scores.values()))
        fracs = vals / max(vals.sum(), 1e-10)
        resonance = 1.0 - float(np.abs(fracs - 1/3).sum() / 2)

        # LCI безопасности = минимальная покрытость (самое слабое звено)
        security_lci = float(np.min(vals))

        # Нарушения
        violations = []
        for sphere, score in sphere_scores.items():
            if score < 0.5:
                violations.append(f'{sphere}: покрыто только {score:.0%} контролей')

        return {
            'sphere_scores': sphere_scores,
            'sphere_resonance': round(resonance, 3),
            'security_lci': round(security_lci, 3),
            'overall_security_index': round((resonance + security_lci) / 2, 3),
            'violations': violations,
            'assessment': (
                'Высокий уровень безопасности' if security_lci > 0.8 and resonance > 0.7
                else 'Средний уровень — есть пробелы' if security_lci > 0.5
                else 'Критические пробелы в безопасности'
            ),
        }

    def model_attack_surface(self, system_components: List[Dict]) -> Dict:
        """
        Моделирование поверхности атаки через архетип Камуфляж/Угроза.
        Камуфляж = скрытые уязвимости, Угроза = активные атаки.
        """
        total_attack_surface = 0.0
        hidden_vulns = []
        active_threats = []

        for component in system_components:
            # A4: Камуфляж — скрытые уязвимости
            cvss_score = component.get('cvss_score', 0.0)
            is_exposed = component.get('internet_facing', False)

            if 0 < cvss_score <= 4.0 and not is_exposed:
                # Камуфляж: уязвимость есть, но не видна
                hidden_vulns.append({
                    'component': component.get('name', '?'),
                    'cvss': cvss_score,
                    'signal': 'камуфляж (скрытая, низкий CVSS)',
                })
                total_attack_surface += cvss_score * 0.5

            elif cvss_score > 7.0 or is_exposed:
                # Угроза: явная уязвимость
                active_threats.append({
                    'component': component.get('name', '?'),
                    'cvss': cvss_score,
                    'exposed': is_exposed,
                    'signal': 'угроза (критическая/открытая)',
                })
                total_attack_surface += cvss_score * 1.5

        # LCI поверхности атаки: чем меньше, тем лучше
        max_surface = len(system_components) * 10 * 1.5
        attack_surface_lci = 1.0 - total_attack_surface / max(max_surface, 1)

        return {
            'n_components': len(system_components),
            'n_hidden_vulnerabilities': len(hidden_vulns),
            'n_active_threats': len(active_threats),
            'total_attack_surface': round(total_attack_surface, 2),
            'attack_surface_lci': round(max(0, attack_surface_lci), 3),
            'hidden_vulnerabilities': hidden_vulns[:3],  # Топ-3
            'active_threats': sorted(active_threats,
                                     key=lambda x: x.get('cvss', 0), reverse=True)[:3],
            'risk_level': (
                'Критический' if len(active_threats) > 3 or attack_surface_lci < 0.3
                else 'Высокий' if len(active_threats) > 0
                else 'Умеренный' if len(hidden_vulns) > 5
                else 'Низкий'
            ),
        }
```

---

## ГЛАВА 3: ПРОТОКОЛЫ КАК АРХЕТИП ОКНА

### 3.1 Криптографический протокол = окно безопасной коммуникации

```python
class ProtocolWindowAnalyzer:
    """
    Анализатор криптографических протоколов через архетип Окна.
    Протокол = окно, через которое информация проходит безопасно.
    LCI протокола = вероятность того, что окно не взломано.
    """

    TLS13_HANDSHAKE = [
        'ClientHello (петля начинается)',
        'ServerHello',
        'EncryptedExtensions',
        'Certificate',
        'CertificateVerify',
        'Finished (петля подтверждена)',
        'ApplicationData (окно открыто)',
    ]  # 7 шагов — нечётное!

    def analyze_handshake_lci(self, protocol_name: str,
                               handshake_steps: List[str],
                               success_rate: float = 1.0) -> Dict:
        """
        LCI криптографического рукопожатия.
        Успешный хендшейк = замкнутая петля аутентификации.
        """
        n_steps = len(handshake_steps)

        # Нечётное число шагов = оптимально (закон нечётности)
        is_odd_steps = n_steps % 2 != 0
        if not is_odd_steps:
            steps_suggested = n_steps + 1
        else:
            steps_suggested = n_steps

        # LCI = success_rate * замкнутость протокола
        protocol_lci = success_rate

        # Три сферы протокола:
        # МВС = первое сообщение (начало петли)
        # СВС = обмен ключами (мидл)
        # БВС = финальное подтверждение (замыкание)
        n_per_sphere = n_steps // 3
        mvs_steps = handshake_steps[:n_per_sphere]
        svs_steps = handshake_steps[n_per_sphere:2*n_per_sphere]
        bvs_steps = handshake_steps[2*n_per_sphere:]

        # Резонанс: равномерность шагов по сферам
        sphere_sizes = np.array([len(mvs_steps), len(svs_steps), len(bvs_steps)])
        sphere_fracs = sphere_sizes / max(sphere_sizes.sum(), 1)
        resonance = 1.0 - float(np.abs(sphere_fracs - 1/3).sum() / 2)

        # Оценка безопасности по стандарту NIST
        known_secure = protocol_name.upper() in ('TLS13', 'TLS 1.3', 'SSH', 'NOISE')
        known_weak = protocol_name.upper() in ('SSL', 'TLS10', 'TLS11', 'TLS 1.0', 'TLS 1.1')

        security_bonus = 0.15 if known_secure else (-0.3 if known_weak else 0.0)

        return {
            'protocol': protocol_name,
            'n_steps': n_steps,
            'is_odd_steps': is_odd_steps,
            'steps_suggested': steps_suggested,
            'protocol_lci': round(protocol_lci, 3),
            'sphere_resonance': round(resonance, 3),
            'mvs_steps': mvs_steps,
            'bvs_steps': bvs_steps,
            'security_assessment': round(
                max(0, min(1, protocol_lci * 0.5 + resonance * 0.35 + security_bonus + 0.15)), 3),
            'recommendation': (
                'Протокол безопасен — петля замкнута оптимально'
                if protocol_lci > 0.95 and known_secure
                else 'Обновить до TLS 1.3' if known_weak
                else 'Проверить конфигурацию'
            ),
        }

    def design_zero_knowledge_loop(self, secret_bits: int = 256) -> Dict:
        """
        Дизайн протокола доказательства с нулевым разглашением (ZKP).
        ZKP = идеальная петля: доказатель убеждает верификатора без раскрытия секрета.
        LCI ZKP = 1.0 (петля совершенна: никакой информации не утекает).
        """
        # Число раундов ZKP (нечётное для оптимальной надёжности)
        n_rounds = 7  # Нечётное!
        soundness_error = (1/2) ** n_rounds  # Вероятность обмана

        # Три шага ZKP (три сферы!):
        # МВС: Commitment (прувер скрывает секрет)
        # СВС: Challenge (верификатор задаёт вопрос)
        # БВС: Response (прувер отвечает без раскрытия)

        return {
            'protocol': 'Sigma-протокол (ZKP)',
            'secret_bits': secret_bits,
            'n_rounds': n_rounds,  # Нечётное!
            'is_odd_rounds': True,
            'soundness_error': round(soundness_error, 8),
            'completeness': 1.0,       # Если знаешь секрет — всегда докажешь
            'zero_knowledge_lci': 1.0, # Никакой информации не утекает
            'soundness_lci': round(1.0 - soundness_error, 8),
            'three_sphere_steps': {
                'МВС': 'Commitment: r ← R, send c = Commit(r)',
                'СВС': 'Challenge: e ← {0,1}^k (верификатор)',
                'БВС': 'Response: s = r + e·x mod p (без раскрытия x)',
            },
            'archetype': 'Петля (замкнутая) + Три сферы + Камуфляж/Угроза (секрет скрыт)',
        }
```

---

## ГЛАВА 4: КРИПТОАНАЛИЗ — НАРУШЕНИЕ ПЕТЛИ

### 4.1 Атаки как разрыв криптографической петли

```python
class CryptoattackETDModel:
    """
    Модель криптографических атак через ЕТД.
    Атака = попытка разомкнуть петлю шифрования.
    """

    ATTACK_TYPES = {
        'brute_force': {
            'archetype': 'A4: Угроза (прямой перебор)',
            'lci_impact': -0.5,   # Уменьшает LCI петли
            'complexity': 'O(2^k)',
            'countermeasure': 'Увеличить ключ до ≥ 256 бит',
        },
        'differential_cryptanalysis': {
            'archetype': 'A3: Нарушение шаблона (поиск дифференциалов)',
            'lci_impact': -0.4,
            'complexity': 'O(2^(k-10))',
            'countermeasure': 'Увеличить число раундов (нечётное!)',
        },
        'side_channel': {
            'archetype': 'A4: Камуфляж (утечка через физику)',
            'lci_impact': -0.7,
            'complexity': 'O(n) измерений',
            'countermeasure': 'Постоянное время исполнения (constant-time code)',
        },
        'replay_attack': {
            'archetype': 'A1: Разомкнутая петля (повторная передача)',
            'lci_impact': -0.6,
            'complexity': 'O(1) перехват',
            'countermeasure': 'Nonce / timestamp в каждом сообщении',
        },
        'man_in_the_middle': {
            'archetype': 'A2: Разрыв между сферами (МВС↔СВС)',
            'lci_impact': -0.9,
            'complexity': 'Позиционная',
            'countermeasure': 'mTLS / Certificate Pinning (восстановить три сферы)',
        },
        'birthday_attack': {
            'archetype': 'A5: Нарушение нечётности (коллизии по вероятности)',
            'lci_impact': -0.3,
            'complexity': 'O(2^(k/2))',
            'countermeasure': 'Увеличить выход хеша: SHA-3-256 → SHA-3-512',
        },
        'quantum_shor': {
            'archetype': 'A1: Разомкнутый RSA (квантовое факторизование)',
            'lci_impact': -1.0,  # Полный разрыв петли RSA
            'complexity': 'O(poly(log n)) на квантовом ПК',
            'countermeasure': 'Post-quantum криптография (Kyber, Dilithium)',
        },
    }

    def model_attack_success_probability(self,
                                          cipher: CryptoPrimitive,
                                          attack_type: str,
                                          attacker_resources: Dict) -> Dict:
        """
        Оценка вероятности успешной атаки на шифр.
        Успешная атака = разрыв криптографической петли (LCI → 0).
        """
        attack = self.ATTACK_TYPES.get(attack_type, {})
        if not attack:
            return {'error': f'Неизвестный тип атаки: {attack_type}'}

        # Вычислительные ресурсы атакующего
        compute_ops_per_sec = attacker_resources.get('ops_per_sec', 1e12)  # 10^12
        time_budget_years = attacker_resources.get('time_budget_years', 1)
        total_ops = compute_ops_per_sec * time_budget_years * 365 * 86400

        # Сложность атаки
        if attack_type == 'brute_force':
            required_ops = 2 ** cipher.security_bits
        elif attack_type == 'birthday_attack':
            required_ops = 2 ** (cipher.security_bits / 2)
        elif attack_type == 'quantum_shor':
            # Квантовый Шор ломает RSA за poly(n) операций
            required_ops = cipher.key_bits ** 3 if cipher.cipher_type == CipherType.PUBLIC_KEY else float('inf')
        else:
            required_ops = 2 ** (cipher.security_bits - 10)  # Упрощение

        # Вероятность взлома
        if required_ops == float('inf'):
            success_prob = 0.0
        else:
            success_prob = min(1.0, total_ops / required_ops)

        # Остаточный LCI шифра после атаки
        residual_lci = max(0.0, 1.0 - success_prob)

        # Время до взлома
        if compute_ops_per_sec > 0 and required_ops < float('inf'):
            time_to_break_years = required_ops / compute_ops_per_sec / (365 * 86400)
        else:
            time_to_break_years = float('inf')

        return {
            'cipher': cipher.name,
            'attack_type': attack_type,
            'archetype_violation': attack['archetype'],
            'success_probability': round(success_prob, 8),
            'residual_lci': round(residual_lci, 3),
            'estimated_time_to_break_years': (
                round(time_to_break_years, 2)
                if time_to_break_years != float('inf') else '∞'
            ),
            'is_practical': success_prob > 0.01,
            'countermeasure': attack['countermeasure'],
            'kryukov_assessment': (
                'Петля неуязвима' if success_prob < 1e-10
                else 'Петля стойкая' if success_prob < 0.01
                else 'Петля уязвима — требует усиления'
            ),
        }
```

---

## ГЛАВА 5: НЕЙРОСЕТЬ ДЛЯ ОБНАРУЖЕНИЯ АНОМАЛИЙ

### 5.1 Система обнаружения вторжений через ЕТД

```python
import torch
import torch.nn as nn

class SecurityETDNeuralDetector(nn.Module):
    """
    Нейронный детектор аномалий безопасности на основе ЕТД.
    Обнаруживает разрывы петель безопасности через аномалии трафика.
    A1: петля запрос-ответ, A2: три сферы трафика, A4: аномальный сигнал.
    """

    def __init__(self, feature_dim: int = 64,
                 hidden_dim: int = 128,
                 n_attack_classes: int = 7):  # 7 = нечётное!
        super().__init__()
        self.n_attack_classes = n_attack_classes

        # МВС: анализ пакетов (побайтовые паттерны)
        self.mvs_packet = nn.Sequential(
            nn.Linear(feature_dim // 3, 32),
            nn.LayerNorm(32), nn.GELU()
        )
        # СВС: анализ сессий (потоковые паттерны)
        self.svs_session = nn.Sequential(
            nn.Linear(feature_dim // 3, 64),
            nn.LayerNorm(64), nn.GELU()
        )
        # БВС: анализ поведения (долгосрочные паттерны)
        self.bvs_behavior = nn.Sequential(
            nn.Linear(feature_dim - 2*(feature_dim//3), 32),
            nn.LayerNorm(32), nn.GELU()
        )

        combined = 32 + 64 + 32  # = 128

        # Резонансный гейт (A2)
        self.resonance_gate = nn.Sequential(
            nn.Linear(combined, combined), nn.Sigmoid()
        )

        # Петлевые блоки (A1) — 5 штук, нечётное!
        self.loop_blocks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(combined, combined),
                nn.LayerNorm(combined), nn.GELU()
            ) for _ in range(5)
        ])

        # A4: детектор Камуфляж/Угроза
        self.anomaly_score = nn.Sequential(
            nn.Linear(combined, 32), nn.GELU(),
            nn.Linear(32, 1), nn.Sigmoid()
        )

        # Классификатор типа атаки (7 классов — нечётное!)
        self.attack_classifier = nn.Sequential(
            nn.Linear(combined, 64), nn.GELU(),
            nn.Linear(64, n_attack_classes),
        )

        # LCI предсказание: насколько петля безопасности замкнута
        self.lci_predictor = nn.Sequential(
            nn.Linear(combined, 32), nn.GELU(),
            nn.Linear(32, 1), nn.Sigmoid()
        )

    def forward(self, packet_features, session_features, behavior_features):
        # Три сферы
        mvs = self.mvs_packet(packet_features)
        svs = self.svs_session(session_features)
        bvs = self.bvs_behavior(behavior_features)

        combined = torch.cat([mvs, svs, bvs], dim=-1)
        gate = self.resonance_gate(combined)
        h = combined * gate

        # Петли
        for block in self.loop_blocks:
            h = block(h) + h

        anomaly_score = self.anomaly_score(h)
        attack_logits = self.attack_classifier(h)
        security_lci = self.lci_predictor(h)

        # Резонанс сфер
        norms = torch.stack([mvs.norm(dim=-1), svs.norm(dim=-1), bvs.norm(dim=-1)])
        total = norms.sum(0, keepdim=True) + 1e-10
        fracs = norms / total
        sphere_resonance = 1.0 - (fracs - 1/3).abs().sum(0) / 2

        return {
            'anomaly_score': anomaly_score,
            'attack_logits': attack_logits,
            'security_lci': security_lci,
            'sphere_resonance': sphere_resonance,
        }
```

---

## ГЛАВА 6: ПЯТЬ УРОВНЕЙ МАСТЕРСТВА В КИБЕРБЕЗОПАСНОСТИ

```
УРОВЕНЬ 1 — ЭЛЕМЕНТЫ (Пользователь):
  Знает: пароль, антивирус. Не знает механизмов.
  LCI защиты: 0.1 (большинство петель разомкнуты).

УРОВЕНЬ 2 — СХЕМЫ (Системный администратор):
  Понимает схемы: TLS, firewall, patch management.
  LCI: 0.4. Закрывает очевидные уязвимости.

УРОВЕНЬ 3 — ПОСЛЕДОВАТЕЛЬНОСТИ (Security Engineer):
  Строит цепочки защитных механизмов (Defence in Depth).
  LCI: 0.65. Видит атаки как нарушения петель безопасности.

УРОВЕНЬ 4 — ОБРАЗЫ (Security Architect):
  Воспринимает систему как трёхсферную (МВС/СВС/БВС).
  Проектирует Zero Trust через 7 аксиом Крюкова.
  LCI: 0.80. Применяет нечётное число уровней защиты (3, 5, 7).

УРОВЕНЬ 5 — ДУХ (Chief Security Officer / Cryptographer):
  Видит безопасность как состояние замкнутости всех петель.
  Проектирует криптосистемы, которые останутся стойкими десятилетиями.
  LCI → 0.95. Каждое решение — инвестиция в резонанс трёх сфер.
```

---

## ГЛАВА 7: ТЕОРЕМА КРЮКОВА В КРИПТОГРАФИИ

**Криптографическая система абсолютно стойка (E = E*) тогда и только тогда, когда:**

1. **A1** — петля шифрования-расшифрования замкнута и необратима для противника
2. **A2** — три сферы (примитив/протокол/архитектура) в резонансе, нет слабого звена
3. **A3** — ключи соответствуют стандарту (≥128 бит симметричный, ≥256 для PQC)
4. **A4** — система в оптимальной зоне: не камуфляж (видимые уязвимости) и не угроза (избыточная сложность)
5. **A5** — число раундов блочного шифра нечётное; число шагов протокола нечётное
6. **A6** — администратор контролирует ≤9 ключевых параметров безопасности
7. **A7** — система работает в режиме АДАПТИВНЫЙ (обновляется с угрозами)

---

## ЗАКЛЮЧЕНИЕ

Криптография через ЕТД — это точная наука о замыкании информационных петель. Стойкий шифр = замкнутая петля с LCI → 1.0. Взломанный шифр = разомкнутая петля. Безопасная система = три сферы (примитивы/протоколы/архитектура) в резонансе с нечётным числом уровней защиты.

**Нечётные числа в криптографии:**
- Раунды AES: **10, 12, 14** (чётные — исторически, но 11, 13, 15 — более «крюковские»)
- Шаги TLS 1.3 хендшейка: **7** (нечётное)
- Раунды ZKP: **7** (нечётное)
- Уровни защиты Defence in Depth: **3, 5, 7** (нечётные)
- Число контролей безопасности в аудите: **7 / 5 / 3** по сферам

---

*Следующая книга: КНИГА 29 — «Архетипы движения в материаловедении и нанотехнологиях»*

**© Серия II «Прикладная ЕТД» | Том 28**
