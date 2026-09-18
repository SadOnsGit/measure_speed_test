# measure speed

Простая утилита для последовательной загрузки файла/изображения и замера скорости скачивания.

Требования
- Python 3.8+
- Пакет `requests` (установите через `pip install requests`)

Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

Использование

```bash
python3 main.py <URL> [-n NUM] [-t TIMEOUT]
```

Параметры
- `<URL>` — ссылка на файл/картинку для скачивания
- `-n, --num` — количество последовательных запросов (по умолчанию 10)
- `-t, --timeout` — таймаут одного запроса в секундах (по умолчанию 60)

Пример

```bash
python3 main.py "https://example.com/image.jpg" -n 5 -t 30
```
