import asyncio
from typing import Callable


def timer(timing: int) -> Callable:
    def inner_1(func: Callable) -> Callable:
        async def inner_2(*args, **kwargs):
            async def timer_inner(timing: int) -> None:  # Таймер.
                await asyncio.sleep(timing)

            task1 = asyncio.create_task(func(*args, **kwargs), name='func')  # Задача для выполняемой функции.
            task2 = asyncio.create_task(timer_inner(timing), name='timer')  # Задача для таймера.
            done, _ = await asyncio.wait([task1, task2],
                                         return_when=asyncio.FIRST_COMPLETED)  # Ждем до первой выполненной задачи.
            if len(done) == 2:  # В списке выполенных задач находятся обе.
                return task1.result()  # Возвращаем результат выполнения функции.
            if [*done][0].get_name() == 'timer':  # В списке выполенных задач только таймер.
                task1.cancel()  # Отмена task1
                await asyncio.sleep(0)  # Переключение контекста для отмены task1, иначе задача task1 останется в
                # ждущем режиме
                print('Превышен timeout ожидания, работа функции прервана!')
                return
            else:
                task2.cancel()  # Отмена task2
                await asyncio.sleep(0)  # Переключение контекста для отмены task2, иначе задача task2 останется в
                # ждущем режиме
                return task1.result()

        return inner_2

    return inner_1


if __name__ == '__main__':
    @timer(3)
    async def func(wait: int) -> None:
        await asyncio.sleep(wait)
        print('Функция выполнена!')


    async def main() -> None:
        await func(2)


    asyncio.run(main())
