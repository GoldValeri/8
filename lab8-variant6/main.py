"""
Лабораторная работа № 8. Вариант 6.

Жадные алгоритмы: задача о загрузке контейнеров (bin packing).

Параметры варианта 6 (табл. 1):
  - задача: загрузка контейнеров (bin packing)
  - жадный критерий 1: Первый подходящий (First Fit, FF)
  - жадный критерий 2: Наилучший подходящий (Best Fit, BF)
  - размерность: 100 предметов
  - доп. Ж6: улучшенная схема — лучшее из двух критериев + FFD

Дисциплина: Основы алгоритмизации и программирование
Студент: Голдаева Валерия Валентиновна, группа БИ 2-1
"""

import random
import statistics
import time
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Константы
# ---------------------------------------------------------------------------
CAPACITY = 100          # вместимость контейнера
N_ITEMS = 100           # число предметов в основном эксперименте
TRIALS = 200            # число случайных наборов


# ===========================================================================
# 1. ЖАДНЫЕ АЛГОРИТМЫ УПАКОВКИ
# ===========================================================================

def first_fit(sizes: List[int], capacity: int) -> int:
    """
    Первый подходящий (First Fit).

    Каждый предмет кладётся в ПЕРВЫЙ контейнер, куда он помещается.
    Если ни один не подходит — открывается новый.
    Трудоёмкость: O(n · B), B — число контейнеров (≤ n).
    """
    bins: List[int] = []                  # остаточные вместимости
    for s in sizes:
        placed = False
        for i, rem in enumerate(bins):
            if rem >= s:                  # первый подходящий
                bins[i] -= s
                placed = True
                break
        if not placed:
            bins.append(capacity - s)     # новый контейнер
    return len(bins)


def best_fit(sizes: List[int], capacity: int) -> int:
    """
    Наилучший подходящий (Best Fit).

    Предмет кладётся в контейнер с НАИМЕНЬШИМ остатком среди тех,
    куда он ещё помещается (минимизируем «дыры»).
    """
    bins: List[int] = []
    for s in sizes:
        best_i = -1
        best_rem = capacity + 1           # ищем минимальный остаток ≥ s
        for i, rem in enumerate(bins):
            if s <= rem < best_rem:
                best_i = i
                best_rem = rem
        if best_i >= 0:
            bins[best_i] -= s
        else:
            bins.append(capacity - s)
    return len(bins)


def first_fit_decreasing(sizes: List[int], capacity: int) -> int:
    """
    First Fit Decreasing (FFD): сортировка по убыванию + First Fit.

    На практике значительно ближе к оптимуму (Ж6 — улучшение).
    """
    ordered = sorted(sizes, reverse=True)
    return first_fit(ordered, capacity)


def improved_greedy(sizes: List[int], capacity: int) -> int:
    """
    Ж6: улучшенная схема — минимум из FF, BF и FFD.
    """
    return min(
        first_fit(sizes, capacity),
        best_fit(sizes, capacity),
        first_fit_decreasing(sizes, capacity),
    )


def lower_bound(sizes: List[int], capacity: int) -> int:
    """
    Нижняя оценка числа контейнеров: ceil(sum(sizes) / capacity).

    Точный оптимум ≥ LB. Используем как эталон при больших n,
    где полный перебор невозможен.
    """
    total = sum(sizes)
    return (total + capacity - 1) // capacity


# ===========================================================================
# 2. КОНТРПРИМЕР
# ===========================================================================

def show_counterexample() -> None:
    """
    Контрпример: First Fit / Best Fit хуже оптимума.

    Предметы [2, 2, 2, 2, 3, 3], вместимость 5.
    FF/BF → 4 контейнера; оптимум (и FFD) → 3.
    """
    print('=' * 70)
    print('Контрпример')
    print('=' * 70)
    sizes = [2, 2, 2, 2, 3, 3]
    C = 5
    ff = first_fit(sizes, C)
    bf = best_fit(sizes, C)
    ffd = first_fit_decreasing(sizes, C)
    lb = lower_bound(sizes, C)
    # оптимальная упаковка вручную: (2,3), (2,3), (2,2)
    opt = 3
    print(f'Предметы: {sizes}, вместимость C = {C}')
    print(f'  First Fit:           {ff} контейнеров')
    print(f'  Best Fit:            {bf} контейнеров')
    print(f'  FFD:                 {ffd} контейнеров')
    print(f'  Нижняя оценка LB:    {lb}')
    print(f'  Оптимум (вручную):   {opt}  — (2+3), (2+3), (2+2)')
    print(f'  Отклонение FF от opt: {(ff - opt) / opt * 100:.1f} %')
    print()


# ===========================================================================
# 3. СЕРИЯ СЛУЧАЙНЫХ НАБОРОВ
# ===========================================================================

def experiment(trials: int = TRIALS, n: int = N_ITEMS,
               capacity: int = CAPACITY, seed: int = 42) -> None:
    """
    ≥ 200 случайных наборов: отклонение от нижней оценки LB.
    """
    print('=' * 70)
    print(f'Серия из {trials} наборов (n = {n}, C = {capacity})')
    print('=' * 70)
    rng = random.Random(seed)
    names = ['FF', 'BF', 'FFD', 'Improved']
    excess = {name: [] for name in names}
    hits = {name: 0 for name in names}

    for _ in range(trials):
        # размеры от 1 до C/2+10 (чтобы не было тривиальных «один предмет = один контейнер»)
        sizes = [rng.randint(1, capacity // 2 + 10) for _ in range(n)]
        sizes = [min(s, capacity) for s in sizes]
        lb = lower_bound(sizes, capacity)
        vals = {
            'FF': first_fit(sizes, capacity),
            'BF': best_fit(sizes, capacity),
            'FFD': first_fit_decreasing(sizes, capacity),
            'Improved': improved_greedy(sizes, capacity),
        }
        for name, v in vals.items():
            if lb > 0:
                excess[name].append((v - lb) / lb * 100)
            if v == lb:
                hits[name] += 1

    print(f"{'Критерий':<12}{'среднее excess%':>16}{'медиана%':>10}"
          f"{'макс%':>10}{'совпало с LB':>14}")
    for name in names:
        d = excess[name]
        print(f'{name:<12}{statistics.mean(d):>16.2f}{statistics.median(d):>10.2f}'
              f'{max(d):>10.2f}{hits[name] / trials * 100:>13.1f}%')
    print()


# ===========================================================================
# 4. СРАВНЕНИЕ ВРЕМЕНИ
# ===========================================================================

def timing() -> None:
    print('=' * 70)
    print('Время работы при росте n (C = 100)')
    print('=' * 70)
    print(f"{'n':>6}{'FF, с':>12}{'BF, с':>12}{'FFD, с':>12}")
    rng = random.Random(1)
    for n in [50, 100, 500, 1000, 5000]:
        sizes = [rng.randint(1, 50) for _ in range(n)]
        t0 = time.perf_counter(); first_fit(sizes, 100); t_ff = time.perf_counter() - t0
        t0 = time.perf_counter(); best_fit(sizes, 100); t_bf = time.perf_counter() - t0
        t0 = time.perf_counter(); first_fit_decreasing(sizes, 100); t_ffd = time.perf_counter() - t0
        print(f'{n:6d}{t_ff:12.5f}{t_bf:12.5f}{t_ffd:12.5f}')
    print()


# ===========================================================================
# 5. ТОЧКА ВХОДА
# ===========================================================================

if __name__ == '__main__':
    show_counterexample()
    experiment()
    timing()
