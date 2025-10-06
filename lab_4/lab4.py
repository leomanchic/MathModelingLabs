import random
import shutil
import matplotlib.pyplot as plt
import matplotlib.animation as animation

NUM_CARS_TARGET = 10
SPAWN_PROB = 0.35
L = 25
TOTAL_STEPS = 300
WARMUP_STEPS = 200
MEASURE_STEPS = TOTAL_STEPS - WARMUP_STEPS

random.seed(1)


class Car:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.dir = direction
        self.turned = False

    def next_forward(self):
        if self.dir == 'up':    return self.x, self.y + 1
        if self.dir == 'down':  return self.x, self.y - 1
        if self.dir == 'right': return self.x + 1, self.y
        if self.dir == 'left':  return self.x - 1, self.y
        return self.x, self.y


def init_cars():
    return []


def pick_spawn_point(L):
    side = random.choice(['south', 'west', 'north', 'east'])
    if side == 'south': return 0, -L, 'up'
    if side == 'west':  return -L, -1, 'right'
    if side == 'north': return -1, L, 'down'
    return L, 0, 'left'


def maybe_spawn_one(cars, L, occupied, target):
    if len(cars) >= target or random.random() >= SPAWN_PROB:
        return
    for _ in range(8):
        x, y, d = pick_spawn_point(L)
        if (x, y) not in occupied:
            cars.append(Car(x, y, d))
            occupied.add((x, y))
            break


def in_segment(x, y):
    return x == 0 and 1 <= y <= L


def step(cars, L, target):
    occupied = {(c.x, c.y) for c in cars}
    maybe_spawn_one(cars, L, occupied, target)

    cars_in_seg_before = [c for c in cars if in_segment(c.x, c.y)]
    N = len(cars_in_seg_before)
    moved_flags = {id(c): False for c in cars_in_seg_before}

    for car in cars:
        if not car.turned:
            if car.dir == 'up'    and (car.x, car.y) == (0, 0):   car.dir = 'left';  car.turned = True
            elif car.dir == 'right' and (car.x, car.y) == (0, -1): car.dir = 'up';    car.turned = True
            elif car.dir == 'down' and (car.x, car.y) == (-1, -1): car.dir = 'right'; car.turned = True
            elif car.dir == 'left'  and (car.x, car.y) == (-1, 0): car.dir = 'down';  car.turned = True

        nx, ny = car.next_forward()

        if car.dir == 'up' and ny > L:    ny = -L
        if car.dir == 'down' and ny < -L: ny = L
        if car.dir == 'right' and nx > L: nx = -L
        if car.dir == 'left' and nx < -L: nx = L

        if (nx, ny) not in occupied:
            occupied.discard((car.x, car.y))
            occupied.add((nx, ny))
            if in_segment(car.x, car.y) and (nx, ny) != (car.x, car.y):
                moved_flags[id(car)] = True
            car.x, car.y = nx, ny

        if not (-1 <= car.x <= 0 and -1 <= car.y <= 0):
            car.turned = False

    M = sum(moved_flags.values())
    return [(c.x, c.y) for c in cars], N, M


def run_with_history():
    cars = init_cars()
    hist = []

    for t in range(TOTAL_STEPS):
        positions, N, M = step(cars, L, NUM_CARS_TARGET)
        hist.append(positions)
    # повторный прогон для метрик (после прогрева)
    cars = init_cars()
    for _ in range(WARMUP_STEPS):
        step(cars, L, NUM_CARS_TARGET)

    rhos, flows = [], []
    for _ in range(MEASURE_STEPS):
        _, N, M = step(cars, L, NUM_CARS_TARGET)
        rho = N / L if L > 0 else 0.0
        vavg = (M / N) if N > 0 else 0.0
        flow = rho * vavg
        rhos.append(rho)
        flows.append(flow)
    return hist, rhos, flows


def plot_fundamental(rhos, flows):
    fig, ax = plt.subplots(figsize=(7, 5))
    xs = [0.0, 0.5, 1.0]
    ys = [0.0, 0.5, 0.0]
    ax.plot(xs, ys, linestyle="--", color="black")
    ax.set_xlabel("car density ρ")
    ax.set_ylabel("flow j = ρ⟨v⟩")
    ax.set_title("Фундаментальная диаграмма")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()


def animate(hist, L, interval=80):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-L - 1, L + 1)
    ax.set_ylim(-L - 1, L + 1)
    ax.set_aspect('equal')
    ax.set_xticks(range(-L, L + 1, max(1, L // 10)))
    ax.set_yticks(range(-L, L + 1, max(1, L // 10)))
    ax.grid(True, which='both', color='lightgray', linewidth=0.5)
    for x in [0, -1]:
        ax.fill_between([x, x + 1], -L - 1, L + 1, color='gray', alpha=0.2)
    for y in [0, -1]:
        ax.fill_betweenx([y, y + 1], -L - 1, L + 1, color='gray', alpha=0.2)

    cars_dots, = ax.plot([], [], 'ro', markersize=6)

    def update(frame):
        positions = hist[frame]
        xs = [p[0] + 0.5 for p in positions]
        ys = [p[1] + 0.5 for p in positions]
        cars_dots.set_data(xs, ys)
        ax.set_title(f"Шаг {frame+1}/{len(hist)} | машин: {len(positions)}")
        return cars_dots,

    ani = animation.FuncAnimation(fig, update, frames=len(hist), interval=interval, blit=False)
    return fig, ani


if name == "__main__":
    hist, rhos, flows = run_with_history()
    plot_fundamental(rhos, flows)
    fig, ani = animate(hist, L, interval=80)
    plt.show()