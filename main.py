import argparse
import requests
import sys
import time

from typing import List, Tuple

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def download_once(url: str, timeout: int = 60) -> Tuple[float, int]:
    """
    Скачивает URL один раз.
    Возвращает (время_в_секундах, размер_в_байтах).
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    start = time.perf_counter()
    response = requests.get(
        url,
        timeout=timeout,
        stream=False,
        headers=headers
    )
    response.raise_for_status()
    content = response.content
    elapsed = time.perf_counter() - start
    return elapsed, len(content)


def measure_speed(url: str, num_requests: int = 10, timeout: int = 60) -> None:
    """
    Основная функция
    Замеряет среднее время запроса и выводит его.
    Вывод ошибок return, далее возможно прокидывать выше
    """
    times: List[float] = []
    sizes: List[int] = []

    print(f"Тестируем: {url}")
    print(f"Количество запросов: {num_requests}")

    for i in range(1, num_requests + 1):
        try:
            elapsed, size = download_once(url, timeout=timeout)
            times.append(elapsed)
            sizes.append(size)
            size_mb = size / (1024 * 1024)
            logger.debug(f"Запрос {i:2d}: {elapsed:7.3f} с  |  {size_mb:8.2f} МБ")
        except requests.exceptions.Timeout:
            logger.error(f"Запрос {i:2d}: таймаут ({timeout} с)")
            return
        except requests.exceptions.RequestException as e:
            logger.error(f"Запрос {i:2d}: ошибка — {e}")
            return
        except Exception as e:
            logger.error(f"Запрос {i:2d}: неожиданная ошибка — {e}")
            return

    total_time = sum(times)
    total_size = sum(sizes)
    avg_time = total_time / len(times)
    avg_size = total_size / len(sizes)

    speed_mbs = (total_size / (1024 * 1024)) / total_time

    logger.info(f"Среднее время запроса : {avg_time:.3f} с")
    logger.info(f"Объём скачанных данных: {total_size / (1024 * 1024):.2f} МБ "
          f"(в среднем {avg_size / (1024 * 1024):.2f} МБ за запрос)")
    logger.info(f"Скорость               : {speed_mbs:.2f} МБ/с")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Замер скорости интернета: 10 последовательных скачиваний файла/картинки."
    )
    parser.add_argument(
        "url",
        help="URL файла"
    )
    parser.add_argument(
        "-n", "--num",
        type=int,
        default=10,
        help="Количество запросов (по умолчанию 10)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=60,
        help="Таймаут одного запроса в секундах (по умолчанию 60)"
    )

    args = parser.parse_args()

    if args.num < 1:
        print("Количество запросов должно быть >= 1")
        sys.exit(1)

    measure_speed(args.url, num_requests=args.num, timeout=args.timeout)


if __name__ == "__main__":
    main()