"""В Яндексе снова стартует проект «Мобилизация»! Компания набирает на трёхмесячную подготовку n молодых людей, увлечённых мобильной разработкой.
 В начале проекта был проведён тест, где скилл участника i в разработке был оценен как ai, а скилл в управлении как bi.

На время проекта участников необходимо разделить на две равные по количеству участников команды — разработчиков и менеджеров.
Планируется сделать это таким образом, чтобы максимизировать суммарную пользу, приносимую всеми участниками.
Если участнику достанется роль разработчика, его польза будет равняться ai, в противном случае — bi.

Но даже занятые проектом, участники находят время для получения новых знаний! Иногда участники приносят сертификаты о
 прохождении курсов, где сказано, что скилл участника i в разработке или же в управлении увеличился на di. В таком случае может быть выгодно
 переформировать команды для максимизации суммарной пользы (равные размеры команд необходимо сохранить).

Ваша задача помочь Яндексу и после рассмотрения каждого нового принесённого участником сертификата посчитать текущую суммарную пользу команд.

Формат ввода
В первой строке входного файла дано число n (2 ≤ n ≤ 2 ⋅ 105, n — чётное) — количество участников проекта. Вторая строка задаёт n целых
чисел ai (0 ≤ ai ≤ 109) — скилл каждого из участников в разработке. Следующая строка в том же формате задаёт скилл участников в
управлении bi (0 ≤ bi ≤ 109).

Следующая строка содержит целое число m (1 ≤ m ≤ 105) — количество принесённых участниками сертификатов. Каждая из следующих m
строк содержит три целых числа numi, typei, di (1 ≤ numi ≤ n, 1 ≤ typei ≤ 2, 1 ≤ di ≤ 104) — номер участника, тип увеличиваемого
скилла (1 — разработка, 2 — управление) и значение увеличения соответствующего навыка.

Формат вывода
После обработки каждого запроса на поступление нового сертификата выведите текущую суммарную пользу всех участников.
Пример 1.
Ввод
4
7 15 3 4
10 10 0 6
3
1 1 4
4 1 6
2 2 10
Вывод
34
35
43"""

from typing import List, Tuple, Dict, Optional, Iterator, Union
import time
import copy
import pprint

# total = 0  # Суммарный скилл.
# result_groups = set()  # Итоговый список с участниками разделенными на группы.
# intermediate_groups = []  # Список который будет хранить промежуточные группы, если при сравнениии скиллов от перестановки они оказались равны.
# viewed_groups = set()  # Список, хранящий комбинации групп с уже посчитанным итоговым "total", т.е группы, хранящиеся в данном множестве больше не рассматриваем.
# c = 0

"""
Имеется группа с четным количеством участников. Каждый участник имеет два скилла: разработка и управление. 
Данную группу необходимо разбить на две равные группы: разработка и управление. При этом в группе разработки для участника 
учитывается только скилл разработки, соответственно в группе управления — только скилл управления. Каждый участник может 
присутствовать только в одной из групп. Группы должны быть сформированы так, чтобы суммарный скилл был наибольшим.

При этом участники могут улучшать свои навыки с помощью сертификатов. Соответственно, формировать группы нужно также
с учетом сертификатов, если они есть. Если с максимальным общим скиллом может быть несколько комбинаций таких групп, 
их все необходимо указать.
"""


# ================================================

# Класс Юнит.

class Unit:

    def __init__(self, skill_dev: str, skill_mgmt: str, num: int = None) -> None:
        self.skill_dev = int(skill_dev)  # Скилл разработки.
        self.skill_mgmt = int(skill_mgmt)  # Скилл управления.
        self.num = num  # Уникальный идентификационный номер.

    def app_of_certificate(self, skill_num: int, skill_upgrade: int) -> None:  # Апгрейд навыков сертификатами.
        if skill_num == 1:
            self.skill_dev += skill_upgrade  # Апгрейд скиллов разработчика.
        elif skill_num == 2:
            self.skill_mgmt += skill_upgrade  # Апгрейд скиллов менеджера.
        else:
            raise ValueError("Номер скилла- целое число равное 1 или 2")

    # Сравнение обьектов по скиллам. Считаются равными если их скиллы разработки и управления совпадают.
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.skill_dev == other.skill_dev and self.skill_mgmt == other.skill_mgmt
        return NotImplemented

    # При создании обьекта-юнит, ему присваивается уникальный порядковый номер. В дальнейшем он будет использоваться
    # при сравнении обьектов в сортировках.
    def __lt__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.num < other.num
        return NotImplemented

    def __iter__(self) -> Iterator[int]:
        return iter((self.num, self.skill_dev, self.skill_mgmt))

    def __str__(self) -> str:
        return f"({self.num}, [{self.skill_dev}, {self.skill_mgmt}])"


# ===============================================

# Класс формирования групп с применением сертфикатов к участникам если такие есть.

class GroupBy:

    def __init__(self, skills_dev: str, skills_mgmt: str, certificates: Optional[List[List[
        int]]] = None) -> None:  # certificates [Номер участника, номер скилла (1 - разработка / 2- управление), значение скилла]

        skills_dev = skills_dev.split()
        skills_mgmt = skills_mgmt.split()
        len_groups = len(skills_dev) // 2

        if certificates:  # [[Номер участника, номер скилла  (1 - разработка / 2- управление, значение скилла], ...]
            certificates = {i[0]: (i[1], i[2]) for i in certificates}  # Список набора сертификатов приводим с словарю.

        self.group_dev = []  # Группа разработки.
        self.group_mgmt = []  # Группа управления.

        for i in range(
                len_groups):  # Наполняем группы обьектами типа "Unit", предварительно применив к обьектам сертификаты,
            # если таковые для них имеются.
            group_dev_item = i
            group_mgmt_item = i + len_groups

            unit_group_dev = Unit(skills_dev[group_dev_item], skills_mgmt[group_dev_item], group_dev_item + 1)
            unit_group_mgmt = Unit(skills_dev[group_mgmt_item], skills_mgmt[group_mgmt_item], group_mgmt_item + 1)

            if certificates:  # Апгрейдим юнитов сертификатами, если таковые у них имеются.
                if group_dev_item + 1 in certificates:
                    unit_group_dev.app_of_certificate(*certificates[group_dev_item + 1])
                if group_mgmt_item + 1 in certificates:
                    unit_group_mgmt.app_of_certificate(*certificates[group_mgmt_item + 1])

            self.group_dev.append(unit_group_dev)
            self.group_mgmt.append(unit_group_mgmt)

    # Вызов и возврат обьекта с примененными сертификатами.
    def __call__(self, certificates: Optional[List[List[int]]] = None) -> "GroupBy":
        self.app_of_certificates(certificates)
        return self

    # Апгрейд участников групп сертификатами, если таковые у них имеются.
    def app_of_certificates(self, certificates: Optional[List[List[int]]] = None) -> None:
        if certificates:  # [[Номер участника, номер скилла  (1 - разработка / 2- управление, значение скилла], ...]
            certificates = {i[0]: (i[1], i[2]) for i in certificates}  # Список набора сертификатов приводим с словарю.:
            for unit in (*self.group_dev, *self.group_mgmt):
                if unit.num in certificates:
                    unit.app_of_certificate(*certificates[unit.num])

    # Суммарный скилл групп.
    def summ_skills(self) -> int:
        # return sum(map(lambda z: z.skill_dev, self.group_dev)) + sum(map(lambda z: z.skill_mgmt, self.group_mgmt))
        return sum(unit_dev.skill_dev for unit_dev in self.group_dev) + sum(
            unit_mgmt.skill_mgmt for unit_mgmt in self.group_mgmt)

    # def __str__(self) -> str:
    #     # group_dev=str([(unit_dev.num, [unit_dev.skill_dev, unit_dev.skill_mgmt]) for unit_dev in sorted(self.group_dev)])
    #     # group_mgmt = str([(unit_mgmt.num, [unit_mgmt.skill_dev, unit_mgmt.skill_mgmt]) for unit_mgmt in sorted(self.group_mgmt)])
    #     # return f"Разработчики: {group_dev}\nМенеджеры: {group_mgmt}\nОбщий скилл: {self.summ_skills()}"
    #     group_dev = str(
    #         tuple(unit_dev.num for unit_dev in sorted(self.group_dev)))
    #     group_mgmt = str(
    #         tuple(unit_mgmt.num for unit_mgmt in sorted(self.group_mgmt)))
    #     return f"Разработка: {group_dev}\nУправление: {group_mgmt}\nОбщий скилл: {self.summ_skills()}"

    def __str__(self) -> str:
        group_dev = tuple(unit_dev.num for unit_dev in sorted(self.group_dev))
        group_mgmt = tuple(unit_mgmt.num for unit_mgmt in sorted(self.group_mgmt))
        return f"Разработка: {group_dev}\nУправление: {group_mgmt}\nОбщий скилл: {self.summ_skills()}"

    def __hash__(self) -> int:
        return hash(
            tuple(sorted([tuple(item) for item in self.group_dev])) +
            tuple(sorted([tuple(item) for item in self.group_mgmt]))
        )

    #  Сравнение групп по их скиллам, упорядоченными сортировками.
    #  Группы считаются равными...................................
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return [sorted(self.group_dev), sorted(self.group_mgmt)] == [sorted(other.group_dev),
                                                                         sorted(other.group_mgmt)]
        return False

    def __len__(self) -> int:
        return len(self.group_dev)


# ================================================

# Класс пераспределения поданных групп с учетом максимального общего скилла.

class GroupOptimizer:

    def __init__(self, groups: GroupBy) -> None:
        self.tatal = 0  # Общий скилл.
        self.item_count = 0  # Счетчик итераций.
        self.groups = groups
        self.result_groups = set()  # Итоговый список с участниками разделенными на группы.
        self.intermediate_groups = []  # Список который будет хранить промежуточные группы, если при сравнениии скиллов от перестановки они оказались равны.
        self.viewed_groups = set()  # Список, хранящий комбинации групп с уже посчитанным итоговым "total".

    #  Метод вызова обьекта класса с переданным сертификатом.
    def __call__(self, certificates: Optional[List[List[int]]] = None):
        if certificates:
            self.groups.app_of_certificates(certificates)
        self.calculate_result_benefit()
        return self

    # Метод просматривает список промежуточных групп, и если список не пуст, производит расчет.
    def calculate_result_benefit(self):
        self.intermediate_groups.append(self.groups)
        while self.intermediate_groups:
            self.groups = self.intermediate_groups.pop()
            self.сalculate_intermediate_benefit()

    def сalculate_intermediate_benefit(self):
        # Определяем цикл, в котором последовательно проходим по элементам первого списка,
        # каждый из таких элементов мы будем менять местами последовательно со всеми элементами второго списка и сравнивать,
        # полученный скилл с имеющимся.
        # Если полученный скилл меньше имеющегося, то снова возвращаем элементы в исходное состояние. Если полученный скилл
        # выше имеющегося, то перезаписываем его значение, обмен элементов сохраняем. Если полученный скилл равен имеющимуся,
        # то данную комбинацию групп отправляем с список "self.intermediate_groups", его рассмотрим после. При этом обмениваем элементы
        # снова местами и добаляем комбинацию в список "self.viewed_groups", чтобы более к нему не возвращаться.
        # И так пока для данного элемента первого списка s1[k] не пройдемся по всем элементам второго списка.
        # Затем увеличиваем значение k на единицу и повторяем все снова.
        k = 0
        self.total = self.groups.summ_skills()
        if not self.groups in self.viewed_groups:  # Проверка, не содержится ли поданный список в просмотренных.
            while k < len(self.groups):
                for j in range(len(self.groups)):
                    self.groups.group_mgmt[k], self.groups.group_dev[j] = self.groups.group_dev[j], \
                        self.groups.group_mgmt[k]
                    self.total1 = self.groups.summ_skills()
                    self.item_count += 1
                    if self.total1 < self.total:
                        self.groups.group_mgmt[k], self.groups.group_dev[j] = self.groups.group_dev[j], \
                            self.groups.group_mgmt[k]
                    elif self.total1 == self.total:
                        self.intermediate_groups.append(copy.deepcopy(self.groups))
                        self.groups.group_mgmt[k], self.groups.group_dev[j] = self.groups.group_dev[j], \
                            self.groups.group_mgmt[k]
                        self.viewed_groups.add(copy.deepcopy(self.groups))
                    else:
                        self.total = self.total1
                        k = 0
                        break
                else:  # Если цикл for завершился штатно, без "break", то отработает данный блок.
                    k += 1
            self.result_groups.add((self.groups))

    def __str__(self):
        self.calculate_result_benefit()
        s = '\n'
        for item, result_group in enumerate(self.result_groups):
            if len(self.result_groups) > 1:
                s += f"Вариант №{item + 1}:\n"
            s += str(result_group) + "\n\n"
        return s


skills_dev = '7 10 3 4 11 6 1 6 11 1 10 10 6 6 4 10 12 10'
skills_mgmt = '10 8 6 6 4 10 2 6 5 5 7 15 3 4 11 6 11 10'
certificates = [[1, 1, 2], [4, 1, 6], [7, 2, 10], [5, 1, 4], [10, 2, 5], [11, 2, 7], [6, 2, 5]]

Groups = GroupBy(skills_dev, skills_mgmt, certificates)
c = GroupOptimizer(Groups)

print(c)
