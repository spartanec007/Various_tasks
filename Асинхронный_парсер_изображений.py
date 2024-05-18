from aiohttp_retry import RetryClient, ExponentialRetry
from typing import List, Any, Callable
from bs4 import BeautifulSoup
import time, requests
import asyncio
import aiofiles
import aiohttp
import copy
import os


class ImgParser:

    def __init__(self, start_page, save_directory):
        self.start_page = start_page  # Адрес стартовой страницы с линками первого уровня.
        self.path = save_directory  # Путь к директории, куда будем сохраняять изображения.
        self.links_2 = []  # Список, куда будем помещать распарсенные линки второго уровня.
        self.links_images = set()  # В данное можество будут помещаться  распарсенные линки изображений.
        self.tasks = []  # Список, куда будут помещаться сформированные задачи.
        self.total = 0  # Счетчик количества сохраненных изображений.
        self.error = []  # При скачивании изображений могут возникать ошибки. В данный список будет помещать
        # линки на изображения, скачивание которых завершилось ошибкой.

    async def make_soup(self, link: str,
                        session: aiohttp.ClientSession) -> BeautifulSoup:  # Метод, создающий "суп" из данных HTML страницы.
        retry_options = ExponentialRetry(attempts=10)  # Количество повторных попыток подключений при
        # возникновении ошибок.
        retry_client = RetryClient(retry_options=retry_options, client_session=session, start_timeout=0.5)  # Создаем
        # объект для переподключений данной клиентской сессии.
        async with retry_client.get(link) as response:
            if response.ok:
                return BeautifulSoup(await response.text(), 'lxml')

    def first_nested_links(self) -> List[str]:  # Метод, возвращающий список из линков первой вложенности.
        resp = requests.get(self.start_page + 'index.html')
        soup = BeautifulSoup(resp.text, 'lxml')
        self.links_1 = [self.start_page + i['href']
                        for i in soup.find('div', class_='item_card').find_all('a')]
        return self.links_1

    async def second_nested_links(self, link: str, session: aiohttp.ClientSession,
                                  semaphore: asyncio.Semaphore):  # Метод, возвращающий список из линков второй вложенности.
        async with semaphore:  # Семафор, ограничиващий количество одновременных подключений для предотвращения перегрузки сервера.
            soup = await self.make_soup(link, session)
            self.links_2.extend([self.start_page + '/depth2/' + i['href']
                                 for i in soup.find('div', class_='item_card').find_all('a')])

    async def link_image(self, link: str, session: aiohttp.ClientSession,
                         semaphore: asyncio.Semaphore) -> None:  # Метод, возвращающий список с линками изображений.
        async with semaphore:
            soup = await self.make_soup(link, session)
            self.links_images.update([i['src'] for i in soup.find('div', class_='item_card').find_all('img')])

    def make_task(self, func: Callable, links: List[str], session: aiohttp.ClientSession,
                  semaphore: asyncio.Semaphore) -> List[Any]:  # Метод, формирующий задачи.
        if self.tasks:
            self.tasks.clear()  # Так как метод будет вызван неоднократно, перед его использованием очищаем список с задачами, если он не пуст.
        for link in links:
            self.tasks.append(func(link, session, semaphore))
        return self.tasks

    async def write_file(self, link: str, session: aiohttp.ClientSession,
                         semaphore: asyncio.Semaphore) -> None:  # Сохранение изображений.
        name_img = link.split('/')[-1]  # Вычленяем из имени файла уникальный номер.
        retry_options = ExponentialRetry(attempts=10)  # Количество повторных попыток подключений при
        # возникновении ошибок.
        retry_client = RetryClient(retry_options=retry_options, client_session=session, start_timeout=0.5)  # Создаем
        # объект для переподключений данной клиентской сессии.
        async with semaphore:  # Семафор, ограничиващий количество одновременных подключений для предотвращения
            # перегрузки сервера.
            async with aiofiles.open(f'{self.path}{name_img}', mode='wb') as f:
                async with retry_client.get(link) as response:
                    if response.ok:
                        try:
                            async for x in response.content.iter_chunked(
                                    2048):  # Разбиваем файл на чанки, скачиваем его частями.
                                await f.write(x)
                            self.total += 1
                            print(f'Изображение сохранено {name_img}', self.total)
                        except asyncio.exceptions.TimeoutError:
                            self.error.append(link)
                            print(f'Превышен таймаут при загрузке файла {name_img}')
                        except Exception as e:
                            self.error.append(link)
                            print(f'Ошибка сохранения файла {name_img}')

    async def main(self) -> None:  # Метод, запускающий цикл событий.
        semaphore = asyncio.Semaphore(
            100)  # Одновременно в любой момент времени может быть активным не более 100 корутин.
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=True)) as session:
            await asyncio.gather(
                *self.make_task(self.second_nested_links, self.first_nested_links(), session, semaphore))
            await asyncio.gather(*self.make_task(self.link_image, self.links_2, session, semaphore))
            await asyncio.gather(*self.make_task(self.write_file, self.links_images, session, semaphore))
            while self.error:  # Попытки дозаписать "упавшие файлы", их линки при сутствуют в списке.
                list_error = copy.deepcopy(
                    self.error)  # Делаем губокую копию списка с линками, т.к он будет полностью перезаписан далее.
                self.error.clear()  # Очищаем список с линками.
                await asyncio.gather(*self.make_task(self.write_file, list_error, session, semaphore))


if __name__ == '__main__':
    path = 'C:/!Django/Задачи на Python/pythonProject/Файлы к aiofiles_2/'
    t1 = time.perf_counter()
    start_parsing = ImgParser(start_page='https://parsinger.ru/asyncio/aiofile/3/', save_directory=path)
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(start_parsing.main())
    t2 = time.perf_counter()
    print(t2 - t1)


    def get_folder_size(filepath, size):
        for root, dirs, files in os.walk(filepath):
            for f in files:
                size += os.path.getsize(os.path.join(root, f))
        return size


    print(get_folder_size(filepath=path, size=0))
