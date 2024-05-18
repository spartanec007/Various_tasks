from typing import List, Callable
import copy


def merger_end(list1: List[int], list2: List[int]) -> List[int]:
    list_sort = []
    s1 = copy.deepcopy(list1)
    s2 = copy.deepcopy(list2)

    while s1 and s2:
        if s1[-1] > s2[-1]:
            list_sort.insert(0, s1.pop())
        else:
            list_sort.insert(0, s2.pop())

    if s1 or s2:
        (list_sort := s1 + list_sort) if s1 else (list_sort := s2 + list_sort)

    return list_sort


def sort(s0: List[int]) -> List[int]:
    list_sort = []

    def inner(s1: List[int]) -> List[int]:
        if len(s1) <= 1:
            return s1

        k = len(s1) // 2
        s2, s3 = s1[:k], s1[k:]

        sorted_s2 = inner(s2)
        sorted_s3 = inner(s3)

        return merger_end(sorted_s2, sorted_s3)

    list_sort.append(inner(s0))

    return list_sort[0]


if __name__ == '__main__':
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

    sorted_arr = sort(arr)

    print(sorted_arr)
