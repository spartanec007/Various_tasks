import math
from typing import Dict, Tuple, List


def color_text(text, color=None):
    if color == 'red':
        return f"\033[91m{text}\033[0m"
    if color == 'green':
        return f"\033[32m{text}\033[0m"
    if color == 'blue':
        return f"\033[34m{text}\033[0m"
    if color == 'yellow':
        return f"\033[33m{text}\033[0m"


# Класс ошибки маршрута.
class RouteError(Exception):
    def __init__(self, message="Начальная и конечная станция не связаны маршрутом!"):
        self.message = message
        super().__init__(self.message)


# Станции, в дальнейшем вершины графа.
class Station:
    # Для каждой вершины(станции) в ее атрибуте "links" будем хранить информацию о всех ветвях,
    # которыми она связана с другими станциями в виде объектов класса "LinkMetro".
    def __init__(self, name: str):
        self.links = []
        self.name = name

    def __repr__(self) -> str:
        return f'"{self.name}"'


# Ветви графа.
class LinkMetro:

    def __init__(self, station1: Station, station2: Station, distance: int = 1):
        try:
            self.v1 = station1
            self.v2 = station2
            self.distance: int = distance
            # Далее в список связей каждой из вершин добавляем смежную с ней вершину и саму связь(ветвь).
            station1.links.append([self, station2])
            station2.links.append([self, station1])
        except AttributeError:  # Прокинем ошибку далее, в момент формирования графа.
            # Данная ошибка возникнет при неверном типе данных одной или обеих вершин
            pass

    # Для того чтобы в списках связей вершин не было дубликатов, добавляем метод проверки объектов
    # связей на равенство.
    def __eq__(self, other: 'LinkMetro') -> bool:
        return ((self.v1 == other.v1 and self.v2 == other.v2) or
                (self.v1 == other.v2 and self.v2 == other.v1))


# Граф.
class LinkedGraph:

    def __init__(self):
        self.links = []  # Список для хранения ветвей графа.
        self.vertex = []  # Список для хранения вершин графа.
        self.route = None

    def add_vertex(self, v: Station) -> None:
        try:
            self.__valid_type(v)
            if v not in self.vertex:
                self.vertex.append(v)
        except:
            print(color_text(f'Станция "{v}" должна быть объектом класса "Station"!', 'red'))

    def add_link(self, link: LinkMetro) -> None:
        if link not in self.links:
            self.links.append(link)
            self.add_vertex(link.v1)
            self.add_vertex(link.v2)

    # Согласно алгоритму Дейкстры назначаем длины кратчайших путей от стартовой вершины до остальных
    # вершин равными бесконечности. Самой стартовой вершине назначаем длину кратчайшего пути равной нулю.
    def __init_dijkstra_distances(self, start_v: Station) -> Dict[Station, float]:
        return {i: float(math.inf) if i != start_v else 0 for i in self.vertex}

    # Улучшаем расстояния от вершины, находящейся первой в очереди до остальных смежных к ней вершин
    # графа на каждой итерации, в результате получим словарь с улучшенными расстояниями от каждой из
    # вершин графа до стартовой.
    def __update_distances(self, start_v: Station, end_v: Station) -> Dict[Station, float | int]:
        improved_distance = self.__init_dijkstra_distances(start_v)
        queue = [start_v]  # Создаем простую очередь("Первым пришел-первым ушел").
        while queue:
            i = queue[0]
            for k, v in i.links:
                if improved_distance[v] > k.distance + improved_distance[i]:
                    improved_distance[v] = k.distance + improved_distance[i]
                    queue.append(v)
            del queue[0]
        if improved_distance[end_v] == math.inf:  # Проверка что связь между конечной и начальной станциями существует.
            raise RouteError
        return improved_distance

    # Восстанавливаем маршрут от конечной вершины графа до стартовой.
    def __restore_route(self, start_v: Station, end_v: Station) -> Tuple[List[Station], List[LinkMetro]]:
        improved_distance = self.__update_distances(start_v, end_v)
        i, rout = end_v, [[end_v], []]
        while i != start_v:  # Цикл, восстанавливающий маршрут от конечной вершины графа до стартовой.
            for k, v in i.links:
                if improved_distance[i] - k.distance == improved_distance[v]:
                    rout[0].insert(0, v)  # Вершины.
                    rout[1].insert(0, k)  # Ветви.
                    i = v
        return rout[0], rout[1]

    # Вывод итоговой информации по маршруту.
    def show_path(self, start_v: Station, end_v: Station) -> str:
        try:
            self.__valid_type(start_v)
            self.__valid_type(end_v)
            self.__valid_value(start_v, end_v)
            route = self.__restore_route(start_v, end_v)
            return (f"Маршрут: {'-> '.join([color_text(str(i), 'green') for i in route[0]])}\nКоличество станций: "
                    f"{color_text(f'{len(route[0])}', 'yellow')}\nДистанция: "
                    f"{color_text(f'{sum(x.distance for x in route[1])}км', 'yellow')}")
        except RouteError:
            return color_text("Начальная и конечная станция не связаны маршрутом!", 'red')
        except TypeError:
            return color_text("Неверный тип входных данных!", 'red')
        except ValueError:
            return color_text(f"Станция(и): {','.join(map(str, self.off_base))} отсутствует(ют) в базе!", 'red')

    # Проверка наличия вершины в базе.
    def __valid_value(self, start_v: Station, end_v: Station):
        if (s := {start_v, end_v} - set(self.vertex)) != set():
            self.off_base = s
            raise ValueError

    # Проверка вершины на верный тип данных.
    @staticmethod
    def __valid_type(vertex):
        if type(vertex) != Station:
            raise TypeError


map_metro = LinkedGraph()
v1 = Station("Сретенский бульвар")
v2 = Station("Тургеневская")
v3 = Station("Чистые пруды")
v4 = Station("Лубянка")
v5 = Station("Кузнецкий мост")
v6 = Station("Китай-город 1")
v7 = Station("Китай-город 2")
v8 = 1
v9 = Station("222")
v10 = Station("333")
map_metro.add_link(LinkMetro(v1, v2))
map_metro.add_link(LinkMetro(v2, v3))
map_metro.add_link(LinkMetro(v1, v3))
# map_metro.add_link(LinkMetro(v8, v9))  ###
map_metro.add_link(LinkMetro(v4, v5))
map_metro.add_link(LinkMetro(v6, v7))

map_metro.add_link(LinkMetro(v2, v7, distance=5))
map_metro.add_link(LinkMetro(v3, v4, distance=3))
map_metro.add_link(LinkMetro(v5, v6, distance=3))

# print(len(map_metro.links))
# print(len(map_metro.vertex))
path = map_metro.show_path(v1, v6)  # от Сретенского бульвара до Китай-город 1
print(path)  # [Сретенский бульвар, Тургеневская, Китай-город 2, Китай-город 1]
# print(sum([x.dist for x in path[1]]))  # 7
