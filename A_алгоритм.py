from typing import List, Tuple, Set, Dict, Iterator
from colorama import Fore, Style
import heapq
import copy
import math
import random


# Класс ошибки маршрута.
class RouteError(Exception):
    def __init__(self, message="Начальная и конечная ячейки не связаны маршрутом!"):
        self.message = message
        super().__init__(self.message)


# Ячейка.
class Cell:

    def __init__(self, value: int | float, row: int, col: int) -> None:
        self.neighbours: List[Cell] = []  # Список куда будем добавлять информацию о соседних ячейках для данной ячейки.
        self.indexes: Tuple[int, int] = (row, col)  # Список, в котором будет храниться информация об индексах данной
        # ячейки в матрице.
        self.value: int | float = value  # Значение данной ячейки.

    def __lt__(self, other: 'Cell') -> bool:
        return self.value < other.value


# Граф.
class Graph:

    def __init__(self, matrix: List[List[int | float]] = None) -> None:
        self.matrix = copy.deepcopy(matrix) if matrix else []
        self.rows: int = len(self.matrix)  # Количество строк матрицы.
        self.cols: int = len(self.matrix[0])  # Количество столбцов матрицы.
        self.create_cell_graph()

    # Формирование графа, где ячейки- объекты класса "Cell", при этом каждый объект "знает" о своих соседях.
    # Так же каждый объект хранит информацию о своем значении и индексе в матрице.
    def create_cell_graph(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.matrix[row][col] == 0:
                    self.matrix[row][col] = Cell(float(math.inf), row, col)  # Делаем нулевые ячейки запретными для
                    # прохода.
                else:
                    self.matrix[row][col] = Cell(self.matrix[row][col], row, col)
        self.add_neighbours()

    # Добавление к ячейке информации об ее соседях.
    def add_neighbours(self):
        for row in range(self.rows):
            for col in range(self.cols):
                cell: int = self.matrix[row][col]
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        new_row = row + dx
                        new_col = col + dy
                        if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                            cell.neighbours.append(self.matrix[new_row][new_col])

    # Итератор, выдающий строки матрицы.
    def __iter__(self) -> Iterator[List[int]]:
        yield from self.matrix

    # Выдача элементов матрицы по индексам.
    def __getitem__(self, index) -> int:
        row, col = index
        return self.matrix[row][col]


# Алгоритм поиска пути.
class ASearch:
    def __init__(self, matr: List[List[int]], start_vertex: Tuple[int, int], end_vertex: Tuple[int, int]) -> None:
        self.graph = Graph(matr)
        self.start: Tuple[int, int] = start_vertex  # Стартовая вершина поиска.
        self.goal: Tuple[int, int] = end_vertex  # Конечная вершина поиска.
        self.path: List[Tuple[int, int]] = []  # Список, где будут храниться кортежи индексов ячеек оптимального пути.
        self.came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}  # Cловарь для отслеживания предыдущих узлов в
        # оптимальном пути.
        self.travel_cost: int | float = self.graph[start_vertex[0], start_vertex[1]].value  # Стоимость пути от
        # стартовой до целевой ячейки. Первоначально ровняется стоимости стартовой ячейки.

    def __call__(self, *args, **kwargs):
        try:
            self.astar_search()  # Расчет оптимального пути.
            self.show_result()  # Вывод результата на экран.
            print()
            print(f"\033[33mСтоимость пути: {self.travel_cost} единицы\033[0m")
        except IndexError:
            print(f"\033[91mИндекс конечной ячейки выходит за пределы графа!\033[0m")
        except TypeError:
            print(f"\033[91mКонечная ячейка не может быть равной нулю!\033[0m")
        except RouteError as e:
            print(f"\033[91m{e.message}\033[0m")

    # Эвристическая функция для оценки расстояния от узла до цели.
    # Манхеттенская оценка.
    @staticmethod
    def heuristic(node: Cell, goal: Tuple[int, int]) -> int:
        return abs(node.indexes[0] - goal[0]) + abs(node.indexes[1] - goal[1])

    # Алгоритм поиска.
    def astar_search(self):
        self.__valid_type(self.graph[self.goal[0], self.goal[1]].value)  # Проверка, что конечная ячейка не
        # является нулем.
        self.__valid_index(self.goal)  # Проверка, что индекс конечной ячейки не выходит за пределы графа.
        x0, y0 = self.start
        open_set: List[Tuple[int, int]] = []  # Множество, в котором будут храниться непосещенные вершины графа.
        closed_set: Set[Tuple[int, int]] = set()  # Множество, в котором хранятся посещенные вершины графа.
        g_score: Dict[Tuple[int, int], float] = {node.indexes: float('inf') for row in self.graph for node in row}
        # Словарь для хранения стоимости пути от начального узла до текущего.
        g_score[(x0, y0)] = 0
        # стоимости пути от начального узла до данного узла. Изначально стоимости полагаем равными бесконечности.
        heapq.heappush(open_set, (self.graph[x0, y0].value, self.graph[x0, y0].indexes))  # Создаем кучу и добавляем
        # в нее начальный узел.

        while open_set:
            current_cost: int  # Значение ячейки матрицы.
            current_node: Tuple[int, int]  # Индексы ячейки матрицы.
            x: int  # Индекс строки в матрице.
            y: int  # Индекс столбца в матрице.
            current_cost, current_node = heapq.heappop(
                open_set)  # Извлекаем узел с наименьшей стоимостью из открытого множества кучи.
            x, y = current_node
            if current_node == self.goal:  # Если текущий узел равен целевому, завершаем поиск.
                self.get_path(current_node)
                break

            if current_node in closed_set:  # Если текущий узел уже был посещен, пропускаем его.
                continue

            closed_set.add((x, y))  # Добавляем текущий узел в закрытое множество.

            # Просматриваем соседние узлы текущего узла.
            for neighbor in self.graph[x, y].neighbours:
                cost: int | float = current_cost + neighbor.value  # Вычисляем стоимость пути до соседа.
                if cost < g_score[neighbor.indexes]:
                    g_score[neighbor.indexes]: int | float = cost
                    total_cost: int | float = cost + self.heuristic(neighbor, self.goal)  # Вычисляем общую стоимость
                    # (стоимость пути + эвристическая оценка).
                    heapq.heappush(open_set,
                                   (total_cost, neighbor.indexes))  # Добавляем соседа в открытое множество с общей
                    # стоимостью.
                    self.came_from[neighbor.indexes]: Tuple[int, int] = (x, y)

        # Стартовая и конечная ячейки не связаны маршрутом.
        if not self.goal in self.came_from:
            raise RouteError

    # Восстановление оптимального пути.
    def get_path(self, current_node: Tuple[int, int]) -> None:
        self.path: List[Tuple[int, int]] = [self.start]
        while current_node in self.came_from:
            self.path.insert(1, current_node)
            self.travel_cost += self.graph[current_node[0], current_node[1]].value  # Стоимость пути
            current_node: Tuple[int, int] = self.came_from[current_node]

    # Вывод результата на экран.
    def show_result(self):
        matrix = [[col.value if col.value != float(math.inf) else 0 for col in row] for row in self.graph.matrix]
        column_widths = [max(len(str(row[i])) for row in matrix) for i in range(len(matrix[0]))]
        column_padding = 1

        for i in range(len(matrix)):
            row_str = ""
            for j in range(len(matrix[i])):
                if (i, j) in self.path:
                    row_str += Fore.GREEN + str(matrix[i][j]) + " " + Style.RESET_ALL
                else:
                    row_str += str(matrix[i][j]) + " "
                padding = column_widths[j] - len(str(matrix[i][j]))
                row_str = f"{' ' * (padding // 2)}{row_str}{' ' * (padding - padding // 2 + column_padding)}"
            print(row_str)

    # Проверка, что конечная ячейка не является нулем.
    @staticmethod
    def __valid_type(vertex):
        if vertex == float(math.inf):
            raise TypeError

    # Проверка, что индекс конечной ячейки не выходит за пределы графа.
    def __valid_index(self, indexes):
        f = self.graph[-1, -1].indexes
        if abs(indexes[0]) > f[0] or abs(indexes[1]) > f[1]:
            raise IndexError


s = [[1, 0, 3, 4, 5, 0, 1, 9], [1, 0, 1, 0, 1, 0, 0, 1], [5, 0, 2, 0, 9, 0, 1, 5], [7, 0, 2, 0, 2, 0, 5, 1],
     [9, 0, 2, 0, 1, 0, 1, 5],
     [7, 0, 1, 0, 1, 0, 0, 4], [5, 0, 1, 0, 1, 0, 1, 3], [1, 3, 0, 0, 1, 1, 0, 1]]

# s = [[1, 1, 3, 4, 5, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 1], [0, 1, 2, 1, 9, 0, 0, 5], [0, 1, 0, 0, 0, 2, 0, 1],
#      [0, 1, 0, 2, 0, 3, 0, 5],
#      [0, 1, 0, 0, 1, 0, 0, 4], [0, 1, 0, 0, 0, 0, 0, 3], [0, 0, 1, 1, 1, 1, 1, 0]]


k = ASearch(s, (0, 0), (0, 6))
k()
