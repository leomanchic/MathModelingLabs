import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap

# --- параметры ---
N = 100              # размер решетки NxN
fps = 100 # кадров в секунду
interval = 0.1 # задержка между кадрами в мс (100 -> 10 кадров в секунду)
steps = 200          # сколько шагов моделировать

# --- начальная конфигурация ---
# 0 = синий, 1 = красный
grid = np.random.choice([0, 1], size=(N, N))

# --- правило обновления ---
# Таблица переходов (как на слайде)
# индекс = число соседей другого цвета
rule = np.array([0, 0, 0, 0, 1, 0, 1, 1, 1])

def update(frame):
    global grid
    new_grid = grid.copy()
    
    for i in range(N):
        for j in range(N):
            # Считаем соседей (с учётом границ, тороидальная топология)
            neighbors = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni = (i + di) % N
                    nj = (j + dj) % N
                    if grid[ni, nj] != grid[i, j]:
                        neighbors += 1
            # Применяем правило
            if rule[neighbors] == 1:
                new_grid[i, j] = 1 - grid[i, j]  # смена цвета
            else:
                new_grid[i, j] = grid[i, j]      # оставить цвет
    
    grid = new_grid
    mat.set_data(grid)
    return [mat]

# --- анимация ---
fig, ax = plt.subplots()
# цветовая карта: синий = 0, красный = 1
cmap = ListedColormap(["blue", "red"])
mat = ax.matshow(grid, cmap=cmap)

ani = animation.FuncAnimation(
    fig, update, frames=steps, interval=interval, blit=True
)

# Сохраняем анимацию как GIF
print("Сохранение анимации как GIF...")
ani.save('droplet_simulation.gif', writer='pillow', fps=10)
print("Анимация сохранена как droplet_simulation.gif")

plt.show()
