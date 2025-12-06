import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter
from tqdm import tqdm
import warnings

warnings.filterwarnings('ignore')


def Game(S, game_cost):
    '''
    :param S: начальный банк
    :param game_cost: стоимость одной игры
    :return: кортеж (финальный счет, количество игр, история баланса, результат: 0-выиграл, 1-проиграл)
    '''
    start_s = S
    history = [S]  # История изменения баланса

    while S >= game_cost:
        current_s = S
        S -= game_cost
        history.append(S)

        # Бросаем монетку до первой решки
        n = 0
        while random.choice([True, False]):  # True - орел, False - решка
            n += 1

        # Если был хотя бы один орел
        if n > 0:
            win = 2 ** n
            S += win
            history.append(S)

        # Проверяем условие остановки (выйти в плюс)
        if S > start_s:
            return S, len(history), history, 0  # Выиграл
        if S < game_cost:  # Денег не хватит на следующую игру
            history.append(S)
            break

    # Если дошли сюда - проиграли
    return S, len(history), history, 1  # Проиграл


def format_rubles(x, pos):
    """Форматирование для отображения рублей"""
    if x >= 1000000:
        return f'{x / 1000000:.1f}М'
    elif x >= 1000:
        return f'{x / 1000:.0f}К'
    else:
        return f'{x:.0f}'


def analyze_initial_amounts():
    """Анализ зависимости среднего выигрыша от начальной суммы"""
    game_cost = 20
    initial_amounts = []
    avg_profits = []
    win_rates = []

    # Тестируем разные начальные суммы
    test_amounts = [100, 200, 500, 1000, 2000, 5000, 10000, 20000,
                    50000, 100000, 200000, 500000, 1000000]

    print("\n" + "=" * 60)
    print("АНАЛИЗ ЗАВИСИМОСТИ ОТ НАЧАЛЬНОЙ СУММЫ")
    print("=" * 60)

    for S0 in tqdm(test_amounts, desc="Анализ сумм"):
        profits = []
        wins = 0
        total_games = 1000

        for _ in range(total_games):
            final_s, _, _, result = Game(S0, game_cost)
            profit = final_s - S0
            profits.append(profit)
            if result == 0:
                wins += 1

        avg_profit = np.mean(profits)
        win_rate = wins / total_games * 100

        initial_amounts.append(S0)
        avg_profits.append(avg_profit)
        win_rates.append(win_rate)

    # График зависимости среднего выигрыша от начальной суммы
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    ax1.plot(initial_amounts, avg_profits, 'b-o', linewidth=2, markersize=6)
    ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    ax1.set_xscale('log')
    ax1.xaxis.set_major_formatter(FuncFormatter(format_rubles))
    ax1.yaxis.set_major_formatter(FuncFormatter(format_rubles))
    ax1.set_xlabel('Начальная сумма (руб)', fontsize=12)
    ax1.set_ylabel('Средний выигрыш (руб)', fontsize=12)
    ax1.set_title('Зависимость среднего выигрыша от начальной суммы', fontsize=14)
    ax1.grid(True, alpha=0.3)

    # Добавляем аннотации для ключевых точек
    for i, amount in enumerate(initial_amounts):
        if amount in [1000, 100000, 1000000]:
            ax1.annotate(f'{avg_profits[i]:.0f}₽',
                         (amount, avg_profits[i]),
                         textcoords="offset points",
                         xytext=(0, 10),
                         ha='center',
                         fontsize=9)

    # График процента выигрышей
    ax2.plot(initial_amounts, win_rates, 'g-s', linewidth=2, markersize=6)
    ax2.set_xscale('log')
    ax2.xaxis.set_major_formatter(FuncFormatter(format_rubles))
    ax2.set_xlabel('Начальная сумма (руб)', fontsize=12)
    ax2.set_ylabel('Процент выигрышей (%)', fontsize=12)
    ax2.set_title('Процент успешных игр от начальной суммы', fontsize=14)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('initial_amount_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()

    # Вывод таблицы результатов
    print("\nРезультаты анализа:")
    print("-" * 60)
    print(f"{'Сумма':<10} {'Ср.выигрыш':<12} {'% выигрышей':<12}")
    print("-" * 60)
    for amount, profit, rate in zip(initial_amounts, avg_profits, win_rates):
        print(f"{format_rubles(amount, None):<10} {profit:>7.0f}₽ {rate:>11.1f}%")
    print("-" * 60)


def main():
    random.seed(42)  # Для воспроизводимости результатов
    game_cost = 20

    # Тестируем три начальные суммы
    initial_amounts = [1000, 100000, 1000000]

    for S0 in initial_amounts:
        print("\n" + "=" * 60)
        print(f"НАЧАЛЬНАЯ СУММА: {format_rubles(S0, None)}₽")
        print("=" * 60)

        # 1) Динамика одной игры
        print("\n1) ДИНАМИКА ОДНОЙ ИГРЫ:")
        final_s, games_played, history, result = Game(S0, game_cost)

        plt.figure(figsize=(12, 6))
        plt.plot(history, 'b-o', linewidth=2, markersize=4, alpha=0.7)
        plt.axhline(y=S0, color='r', linestyle='--', alpha=0.5, label='Начальная сумма')
        plt.xlabel('Номер шага', fontsize=12)
        plt.ylabel('Баланс (руб)', fontsize=12)
        plt.title(f'Динамика одной игры (Начальная сумма: {format_rubles(S0, None)}₽)', fontsize=14)
        plt.gca().yaxis.set_major_formatter(FuncFormatter(format_rubles))
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Добавляем аннотации для ключевых моментов
        if len(history) > 1:
            plt.annotate(f'Старт: {format_rubles(history[0], None)}₽',
                         (0, history[0]),
                         textcoords="offset points",
                         xytext=(10, 5),
                         ha='left')
            plt.annotate(f'Финиш: {format_rubles(history[-1], None)}₽',
                         (len(history) - 1, history[-1]),
                         textcoords="offset points",
                         xytext=(-10, 5),
                         ha='right')

        plt.tight_layout()
        plt.savefig(f'single_game_{S0}.png', dpi=150, bbox_inches='tight')
        plt.show()

        print(f"Начальная сумма: {format_rubles(S0, None)}₽")
        print(f"Финальный баланс: {format_rubles(final_s, None)}₽")
        print(f"Игр сыграно: {games_played // 2}")
        print(f"Результат: {'ВЫИГРЫШ' if result == 0 else 'ПРОИГРЫШ'}")
        print(f"Изменение: {'+' if final_s >= S0 else ''}{final_s - S0:.0f}₽")

        # 2) 20 игр
        print("\n2) РЕЗУЛЬТАТЫ 20 ИГР:")
        final_balances = []
        games_count = []
        results = []

        plt.figure(figsize=(14, 8))

        for i in range(20):
            final_s, games_played, history, result = Game(S0, game_cost)
            final_balances.append(final_s)
            games_count.append(games_played)
            results.append(result)

            # Рисуем каждую игру на графике
            color = 'g' if result == 0 else 'r'
            alpha = 0.3 if i > 0 else 0.5  # Первую игру выделяем
            linewidth = 2 if i == 0 else 1
            label = 'Выигрышные игры' if i == 0 and result == 0 else None
            if i == 0 and result == 1:
                label = 'Проигрышные игры'

            plt.plot(history, color=color, alpha=alpha, linewidth=linewidth, label=label)

        plt.axhline(y=S0, color='b', linestyle='--', linewidth=2, alpha=0.7, label='Начальная сумма')
        plt.xlabel('Номер шага', fontsize=12)
        plt.ylabel('Баланс (руб)', fontsize=12)
        plt.title(f'20 игр (Начальная сумма: {format_rubles(S0, None)}₽)', fontsize=14)
        plt.gca().yaxis.set_major_formatter(FuncFormatter(format_rubles))
        plt.grid(True, alpha=0.3)

        # Создаем кастомные легенды
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='g', lw=2, label='Выигрышные игры'),
            Line2D([0], [0], color='r', lw=2, label='Проигрышные игры'),
            Line2D([0], [0], color='b', linestyle='--', lw=2, label='Начальная сумма')
        ]
        plt.legend(handles=legend_elements, loc='upper right')

        plt.tight_layout()
        plt.savefig(f'20_games_{S0}.png', dpi=150, bbox_inches='tight')
        plt.show()

        wins_20 = results.count(0)
        losses_20 = results.count(1)
        avg_profit_20 = np.mean([bal - S0 for bal in final_balances])

        print(f"Выиграло: {wins_20} игр ({wins_20 / 20 * 100:.1f}%)")
        print(f"Проиграло: {losses_20} игр ({losses_20 / 20 * 100:.1f}%)")
        print(f"Средний выигрыш: {avg_profit_20:.0f}₽")
        print(f"Максимальный выигрыш: {max(final_balances) - S0:.0f}₽")
        print(f"Максимальный проигрыш: {min(final_balances) - S0:.0f}₽")

        # 3) 1000 игр
        print("\n3) СТАТИСТИКА 1000 ИГР:")
        final_balances_1000 = []
        results_1000 = []
        profits_1000 = []

        for _ in tqdm(range(1000), desc=f"Играем 1000 раз ({format_rubles(S0, None)}₽)"):
            final_s, _, _, result = Game(S0, game_cost)
            final_balances_1000.append(final_s)
            results_1000.append(result)
            profits_1000.append(final_s - S0)

        wins_1000 = results_1000.count(0)
        losses_1000 = results_1000.count(1)
        avg_profit_1000 = np.mean(profits_1000)

        # Гистограмма выигрышей/проигрышей
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # График распределения результатов
        labels = ['Выигрыши', 'Проигрыши']
        sizes = [wins_1000, losses_1000]
        colors = ['lightgreen', 'lightcoral']
        explode = (0.1, 0)

        ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        ax1.set_title(f'Распределение результатов\n{format_rubles(S0, None)}₽ начальных', fontsize=14)

        # Гистограмма выигрышей
        ax2.hist(profits_1000, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
        ax2.axvline(x=0, color='r', linestyle='--', linewidth=2, alpha=0.7)
        ax2.axvline(x=avg_profit_1000, color='g', linestyle='-', linewidth=2, alpha=0.7,
                    label=f'Среднее: {avg_profit_1000:.0f}₽')
        ax2.set_xlabel('Выигрыш/проигрыш (руб)', fontsize=12)
        ax2.set_ylabel('Количество игр', fontsize=12)
        ax2.set_title(f'Распределение выигрышей\n{format_rubles(S0, None)}₽ начальных', fontsize=14)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'1000_games_{S0}.png', dpi=150, bbox_inches='tight')
        plt.show()

        print(f"Выиграло: {wins_1000} игр ({wins_1000 / 10:.1f}%)")
        print(f"Проиграло: {losses_1000} игр ({losses_1000 / 10:.1f}%)")
        print(f"Средний выигрыш: {avg_profit_1000:.0f}₽")
        print(f"Медианный выигрыш: {np.median(profits_1000):.0f}₽")
        print(f"Стандартное отклонение: {np.std(profits_1000):.0f}₽")

        # Анализ максимальных выигрышей
        if wins_1000 > 0:
            max_win_idx = np.argmax(profits_1000)
            max_win = profits_1000[max_win_idx]
            print(f"Максимальный выигрыш: {max_win:.0f}₽")
            print(f"Максимальный проигрыш: {min(profits_1000):.0f}₽")

            # Анализ типичных сценариев
            positive_profits = [p for p in profits_1000 if p > 0]
            if positive_profits:
                print(f"Средний выигрыш (только выигрышные игры): {np.mean(positive_profits):.0f}₽")
                print(f"Медианный выигрыш (только выигрышные игры): {np.median(positive_profits):.0f}₽")

        print("\n" + "-" * 60)

    # Анализ зависимости от начальной суммы
    analyze_initial_amounts()


if __name__ == "__main__":
    print("МОДЕЛИРОВАНИЕ ИГРЫ С МОНЕТКОЙ")
    print("=" * 60)
    print("Правила:")
    print("- Стоимость игры: 20₽")
    print("- Бросаем монетку до первой решки")
    print("- Выигрыш: 2^n ₽, где n - количество орлов подряд")
    print("- Играем до первого выхода в плюс или пока есть деньги")
    print("=" * 60)

    main()