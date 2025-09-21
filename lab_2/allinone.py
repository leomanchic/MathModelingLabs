import random
import math
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from matplotlib.animation import FuncAnimation

random.seed(42)

def er_graph(n, p):
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < p:
                adj[i].append(j)
                adj[j].append(i)
    return adj

def circle_layout(n):
    return [(math.cos(2*math.pi*k/n), math.sin(2*math.pi*k/n)) for k in range(n)]

def degroot_step(x, adj, alphas):
    x_next = []
    for i in range(len(x)):
        if len(adj[i]) == 0:
            x_next.append(x[i])
            continue
        avg = sum(x[j] for j in adj[i]) / len(adj[i])
        x_next.append(alphas[i]*x[i] + (1-alphas[i])*avg)
    return x_next

def draw_graph(pos, adj, values, ax, title=""):
    ax.clear()
    segs = [[pos[i], pos[j]] for i in range(len(adj)) for j in adj[i] if j > i]
    ax.add_collection(LineCollection(segs, colors="lightgray", linewidths=0.8, alpha=0.7))
    xs, ys = zip(*pos)

    # Разделяем точки на сильные и слабые агенты для разных стилей отображения
    strong_indices = [i for i in range(len(alphas)) if alphas[i] >= 0.7]
    weak_indices = [i for i in range(len(alphas)) if alphas[i] < 0.7]

    # Рисуем слабых агентов
    if weak_indices:
        weak_xs = [xs[i] for i in weak_indices]
        weak_ys = [ys[i] for i in weak_indices]
        weak_vals = [values[i] for i in weak_indices]
        ax.scatter(weak_xs, weak_ys, c=weak_vals, vmin=0, vmax=1, cmap="viridis",
                   s=50, edgecolors="k", alpha=0.8)

    # Рисуем сильных агентов
    if strong_indices:
        strong_xs = [xs[i] for i in strong_indices]
        strong_ys = [ys[i] for i in strong_indices]
        strong_vals = [values[i] for i in strong_indices]
        ax.scatter(strong_xs, strong_ys, c=strong_vals, vmin=0, vmax=1, cmap="viridis",
                   s=100, edgecolors="red", linewidth=0, alpha=1.0)

    ax.set_title(title, fontsize=10)
    ax.set_aspect("equal")
    ax.axis("off")
    return ax

# Параметры
N = 40  # Уменьшим количество агентов для лучшей визуализации
T = 50

# Создаем сетку параметров
p_values = [0.02, 0.1, 0.2]
alpha_values = [0.0, 0.5, 0.9]

# Создаем фигуру с 3x3 subplots
fig, axes = plt.subplots(3, 3, figsize=(12, 12))
plt.subplots_adjust(hspace=0.3, wspace=0.2)
# plt.pause(5)
# Инициализируем графы и состояния для каждой комбинации параметров
graphs = []
positions = []
initial_opinions = []
alphas_list = []
histories = []

for i, p in enumerate(p_values):
    for j, alpha_val in enumerate(alpha_values):
        # Создаем граф
        adj = er_graph(N, p)
        pos = circle_layout(N)

        # Начальные значения мнений
        x = [random.random() for _ in range(N)]

        # Параметры упрямства
        alphas = [alpha_val] * N

        # Сохраняем данные
        graphs.append(adj)
        positions.append(pos)
        initial_opinions.append(x.copy())
        alphas_list.append(alphas)
        histories.append([x.copy()])

        # Рисуем начальное состояние
        draw_graph(pos, adj, x, axes[i, j], f"p={p}, α={alpha_val}\nt=0")

# Функция для анимации
def update(t):
    if t == 0:
        return

    for idx in range(len(graphs)):
        # Обновляем мнения
        new_opinions = degroot_step(histories[idx][-1], graphs[idx], alphas_list[idx])
        histories[idx].append(new_opinions)

        # Обновляем график
        i = idx // 3
        j = idx % 3
        p = p_values[i]
        alpha_val = alpha_values[j]
        draw_graph(positions[idx], graphs[idx], new_opinions,
                  axes[i, j], f"p={p}, α={alpha_val}\nt={t}")

    return axes

# Создаем анимацию
ani = FuncAnimation(fig, update, frames=T+1, interval=300, repeat=False)
ani.save('animation.gif', writer='pillow', fps=10, dpi=100)

plt.tight_layout()
plt.show()

# Выводим финальные значения для каждой конфигурации
print("Финальные значения мнений для каждой конфигурации:")
for idx in range(len(graphs)):
    i = idx // 3
    j = idx % 3
    p = p_values[i]
    alpha_val = alpha_values[j]

    final_opinions = histories[idx][-1]
    avg_opinion = sum(final_opinions) / len(final_opinions)
    std_opinion = math.sqrt(sum((x - avg_opinion)**2 for x in final_opinions) / len(final_opinions))

    print(f"\nКонфигурация p={p}, α={alpha_val}:")
    print(f"  Среднее мнение: {avg_opinion:.3f}")
    print(f"  Стандартное отклонение: {std_opinion:.3f}")
    print(f"  Диапазон мнений: [{min(final_opinions):.3f}, {max(final_opinions):.3f}]")

    # Для конфигураций с α=0.9 показываем детали по агентам
    if alpha_val == 0.9:
        strong_agents = [x for i, x in enumerate(final_opinions) if alphas_list[idx][i] >= 0.7]
        print(f"  Мнения упрямых агентов: {[f'{x:.3f}' for x in strong_actors]}")
