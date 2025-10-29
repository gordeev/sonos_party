# Sonos: сканер и плеер (bash + Python, без Node)

Мини-набор утилит для локальной сети:
- `sonos_scan.sh` — ищет колонки Sonos по CIDR, вытягивает `device_description.xml`, показывает IP / RoomName / Model.
- `sonos_play.py` — запускает воспроизведение по IP на указанной колонке из переданного URL (HTTP/HTTPS), опционально задаёт громкость и стопает текущий трек.

> Без Node.js. Управление — через [SoCo](https://github.com/SoCo/SoCo).

---

## Требования

- Linux/macOS с:
  - `bash`, `curl`, `awk`, `sed`
  - `nmap` (для сканера)
  - Python 3.8+
  - `pip install soco`
- Сеть, в которой доступны Sonos-устройства (обычно порты `1400/tcp`, иногда `1443/tcp`).

---

## Установка

```bash
# Клонируем ваш репозиторий (пример):
git clone https://github.com/<you>/sonos-tools.git
cd sonos-tools

# Делаем исполняемыми
chmod +x sonos_scan.sh
chmod +x sonos_play.py

# Ставим зависимости Python
pip install --upgrade soco
```

## Поиск колонок
# Скан всей подсети
./sonos_scan.sh 192.168.1.0/24
Скрипт ищет открытые 1400/1443, скачивает xml/device_description.xml, проверяет <manufacturer>Sonos</manufacturer> и печатает имя комнаты/модель.

Пример вывода:
```
IP               | RoomName                  | Model
-----------------+---------------------------+-----------------------------
192.168.1.18     | Living Room               | Sonos One
```

Воспроизведение по IP и URL
# Базовый пример
./sonos_play.py --ip 192.168.1.18 --url "http://example.com/stream.mp3"

# С громкостью и принудительной остановкой текущего трека
./sonos_play.py --ip 192.168.1.18 --url "https://radio.example/stream" --volume 25 --force

Аргументы:
--ip — IP колонки (например, 192.168.1.18)
--url — аудио URL (http:// или https://)
--volume — 0..100 (необязательно)
--force — остановить текущее воспроизведение перед запуском нового

## Проверка TLS-серта на 1443 (опционально)
IP=192.168.1.18
echo | openssl s_client -connect "${IP}:1443" -servername "${IP}" -showcerts 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

##Содержимое репозитория
.
├── sonos_scan.sh     # bash-сканер Sonos по сети (CIDR)
├── sonos_play.py     # Python-плеер через SoCo: play_uri(), volume, force-stop
└── README.md         # этот файл
