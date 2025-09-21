import random, math
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
                   s=80, edgecolors="k", alpha=0.8, label="Слабые агенты")

    # Рисуем сильных агентов
    if strong_indices:
        strong_xs = [xs[i] for i in strong_indices]
        strong_ys = [ys[i] for i in strong_indices]
        strong_vals = [values[i] for i in strong_indices]
        ax.scatter(strong_xs, strong_ys, c=strong_vals, vmin=0, vmax=1, cmap="viridis",
                   s=150, edgecolors="red", linewidth=2, alpha=1.0, label="Сильные агенты")

    ax.set_title(title, fontsize=14)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.legend(loc="upper right", fontsize=10)
    return ax

# параметры
N = 40
p = 0.2
T = 50

adj = er_graph(N, p)
pos = circle_layout(N)

# Начальные значения
# x = [random.random() for _ in range(N)]
x = [1]*3 + [0]*(N-3)
alphas = [1]*3+[0.001]*(N-3)  # Все агенты с высоким уровнем упрямства

indices = list(range(N))
random.shuffle(indices)
x = [x[i] for i in indices]
alphas = [alphas[i] for i in indices]


# # Сделаем несколько агентов слабыми (менее упрямыми)
# for i in random.sample(range(N), 15):  # 15 случайных агентов будут слабыми
#     alphas[i] = 0.1

# Сохраним историю мнений для графика эволюции
history = [x.copy()]

# Создаем фигуру с двумя subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# plt.pause(5)
# Первый subplot для графа
sc = draw_graph(pos, adj, x, ax1, "t=0")

# Второй subplot для эволюции мнений
ax2.set_xlim(0, T)
ax2.set_ylim(0, 1)
ax2.set_xlabel("Время (t)")
ax2.set_ylabel("Мнение")
ax2.set_title("Эволюция мнений агентов")
ax2.grid(True, alpha=0.3)

# Инициализируем линии для графика эволюции
lines = []
colors = plt.cm.viridis(np.linspace(0, 1, N))
for i in range(N):
    line, = ax2.plot([0], [x[i]], color=colors[i], alpha=0.7 if alphas[i] < 0.7 else 1.0,
                     linewidth=2 if alphas[i] >= 0.7 else 1.0)
    lines.append(line)

# Функция для анимации
def update(t):
    global x
    if t > 0:
        x = degroot_step(x, adj, alphas)
        history.append(x.copy())

    # Обновляем граф
    draw_graph(pos, adj, x, ax1, f"t={t}")

    # Обновляем график эволюции
    for i in range(N):
        y_data = [step[i] for step in history]
        lines[i].set_data(range(len(y_data)), y_data)

    ax2.set_xlim(0, len(history)-1)

    return ax1, ax2

# Создаем анимацию
ani = FuncAnimation(fig, update, frames=T+1, interval=300, repeat=False)
ani.save('./media/animation2.gif', writer='pillow', fps=10, dpi=100)

plt.tight_layout()
plt.show()

# Выведем финальные значения
print("Финальные значения мнений:")
strong_agents = []
weak_agents = []
for i, val in enumerate(x):
    if alphas[i] >= 0.7:
        strong_agents.append((i, val))
    else:
        weak_agents.append((i, val))

print("\nСильные агенты (упрямые):")
for i, val in strong_agents:
    print(f"Агент {i}: {val:.3f}")

print("\nСлабые агенты (гибкие):")
for i, val in weak_agents:
    print(f"Агент {i}: {val:.3f}")

# Статистика
avg_strong = sum(val for _, val in strong_agents) / len(strong_agents) if strong_agents else 0
avg_weak = sum(val for _, val in weak_agents) / len(weak_agents) if weak_agents else 0

print(f"\nСреднее мнение сильных агентов: {avg_strong:.3f}")
print(f"Среднее мнение слабых агентов: {avg_weak:.3f}")
print(f"Общее среднее мнение: {sum(x)/len(x):.3f}")
