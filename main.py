import argparse
import requests
import sys
import time

from typing import List, Tuple

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

BYTES_TO_MB = 1024 * 1024


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


def download_files(
    url: str,
    num_requests: int,
    timeout: int
) -> None:
    times: List[float] = []
    sizes: List[int] = []
    for i in range(1, num_requests + 1):
        try:
            elapsed, size = download_once(url, timeout=timeout)
            times.append(elapsed)
            sizes.append(size)
            size_mb = size / BYTES_TO_MB
            logger.info("Запрос %2d: %7.3f с  |  %8.2f МБ", i, elapsed, size_mb)
        except requests.exceptions.Timeout:
            logger.error("Запрос %2d: таймаут (%d с)", i, timeout)
            return
        except requests.exceptions.RequestException as e:
            logger.error("Запрос %2d: ошибка — %s", i, e)
            return
        except Exception as e:
            logger.error("Запрос %2d: неожиданная ошибка — %s", i, e)
            return
    return times, sizes


def measure_stats(times: list, sizes: list) -> Tuple[int, int]:
    total_time = sum(times)
    total_size = sum(sizes)
    avg_time = total_time / len(times)
    avg_size = total_size / len(sizes)
    speed_mbs = (total_size / BYTES_TO_MB) / total_time
    return avg_time, avg_size, speed_mbs, total_size


def measure_speed(url: str, num_requests: int = 10, timeout: int = 60) -> None:
    logger.info("Ссылка для теста: %s", url)
    logger.info("Количество запросов: %d", num_requests)
    times, sizes = download_files(url, num_requests, timeout)
    avg_time, avg_size, speed_mbs, total_size = measure_stats(
        times, sizes
    )
    logger.info("Среднее время запроса : %.3f с", avg_time)
    logger.info(
        "Объём скачанных данных: %.2f МБ (в среднем %.2f МБ за запрос)",
        total_size / BYTES_TO_MB,
        avg_size / BYTES_TO_MB,
    )
    logger.info("Скорость: %.2f МБ/с", speed_mbs)


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