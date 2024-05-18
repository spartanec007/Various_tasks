from concurrent.futures import ProcessPoolExecutor
from asyncio.events import AbstractEventLoop
from functools import partial
from typing import List
import asyncio


def count(count_to: int) -> int:  # Простой счетчик
    counter = 0
    while counter < count_to:
        counter += 1
    return counter


async def donor(queue: asyncio.Queue, nums: List[int]) -> None:  # Донор
    with ProcessPoolExecutor() as process_pool:
        loop: AbstractEventLoop = asyncio.get_running_loop()  # Получаем ссылку на текущий цикл событий.
        calls: List[partial[int]] = [partial(count, num) for num in nums]  # Применяем к функции "count" функцию
        # "partial" модуля "functools", чтобы вызвать ее без аргументов.
        call_coros = []
        for call in calls:
            call_coros.append(loop.run_in_executor(process_pool, call))  # Добавляем задачи в пул процессов.
        for i in asyncio.as_completed(call_coros):  # Асинхронный итератор, выдающий результат
            # по мере выполнения задачи.
            await queue.put(await i)  # Добавление результата, выданного итератором в очередь.
        await queue.put(None)  # Для прерывания работы программы, помещаем в очередь значение "None".
        # После того как акцептор получит данное значение программа прервется.


async def acceptor(queue: asyncio.Queue) -> None:  # Акцептор.
    while True:
        item = await queue.get()  # Получаем значение из очереди.
        if item is None:
            break
        print(f'Потребитель начал обработку: {item}')
        await asyncio.sleep(5)  # Спим пять секунд.
        print(f'Потребитель закончил обработку: {item}')
        print(f'Элементов в очереди: {queue.qsize()}')
    print('Потребитель: Done')


async def main(nums: List[int]) -> None:
    queue = asyncio.Queue()  # Реализуем простую очередь.
    await asyncio.gather(donor(queue, nums), acceptor(queue))


if __name__ == '__main__':
    list_ = [300000001, 200000002, 30000007, 100000003, 1000009, 10000008]
    asyncio.run(main(list_))
