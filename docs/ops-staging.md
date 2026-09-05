# Ops: staging-окружение и текущий статус проекта

> Документ-якорь: любое новое окно LLM читает этот файл и понимает, где мы.
> Обновлять при каждом изменении инфраструктуры или смене фазы.

Последнее обновление: 2026-09-05.

## Где мы (статус проекта)

- **Метод:** BMad, фаза 4 (implementation), спринт по Epic 1.
- **Текущая история:** 1.2 (Telegram bot wiring + /start) — статус `review` (code review идёт).
- **Задеплоено:** staging (см. ниже). В боте работает только `/start` и `/start salon1`.
- **Полный статус спринта:** `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- **Планирующие артефакты:** `_bmad-output/planning-artifacts/` (PRD, architecture, epics, readiness report).

## Staging-инфраструктура

| Параметр | Значение |
|---|---|
| Провайдер | Yandex Cloud VM `zabota-staging` |
| Адрес | `158.160.146.121`, пользователь `zabota_admin` |
| SSH-ключ | `~/.ssh/zabota_staging` (на маке Timurkarev) |
| Директория на VM | `~/zabota_mentor` |
| ОС / Docker | Ubuntu 24.04 / Docker 29.8 + Compose v5.5 |
| Транспорт бота | **polling** (webhook — на проде, см. D2 ниже) |
| Egress к Telegram | **Cloudflare WARP** через wireproxy (`TG_PROXY_URL=socks5://warp:1080`) |
| Стек | postgres 17 (volume `postgres_staging_data`), redis 8, app, worker, warp |
| Compose-файл | `docker-compose.staging.yml` (в репо) |

Секреты: `.env` живёт **только на VM** (`~/zabota_mentor/.env`): `POSTGRES_PASSWORD`
(сгенерирован на месте), `BOT_TOKEN` (вставлен вручную). Через git/чат не проходит.
rsync его исключает — деплой конфигурацию не перетирает.

## Как задеплоить обновление

После merge в `main` (деплоим только main):

```bash
cd ~/Projects/zabota_mentor && git pull
./scripts/deploy-staging.sh
```

Скрипт: rsync кода → `up -d --build` (база сохраняется) → миграции → статус.
Адрес/ключ переопределяются: `STAGING_HOST=... ./scripts/deploy-staging.sh`.

## Окружения (базы изолированы)

- **dev** — compose на маке, volume `postgres_data`, креды `zabota/zabota` (throwaway).
- **test** — `zabota_test` на той же ноде, для контрактных тестов (`TEST_DATABASE_URL`).
- **staging** — контейнер postgres на VM (см. выше).
- **prod** — не существует; план: managed Yandex Postgres + Yandex Lockbox (AD-5),
  `BOT_MODE=webhook`, 2 VM (app + worker) по AD-11. Гейты: Roskomnadzor-файл (7.5c).

## Известные проблемы / решения code review 1.2 (D1–D3)

- **D1:** дев-сид `salon1` в миграции `0002` — попадёт и в прод. Решено: оставить до
  прода, выпилить к гейту 7.5c (нужен staging-тестам `/start salon1`).
- **D2:** `set_webhook` вне try/finally в `src/app/main.py` — при сбое crash-loop +
  утечка сессии. Решено: чинить утечку в 1.2, retry/backoff — в прод-историю.
- **D3:** live-смоук закрыт прогоном на staging (`/start salon1`, 2026-09-05).

## Инциденты

### 2026-09-05 (2): api.telegram.org недоступен из Yandex Cloud (РКН)

Симптом: после деплоя бот молчал, в логах — таймауты TCP к `149.154.166.110`
(api.telegram.org). Диагностика: с хоста и из контейнера — IPv4 timeout, IPv6
unreachable. **Причина: блокировка РКН** — весь исходящий Telegram-трафик из
RU-сетей (включая Yandex Cloud) резолвится, но не проходит.

**Решение (бесплатное): Cloudflare WARP-туннель.** Весь Bot API трафик идёт через
SOCKS5-прокси `socks5://warp:1080` (переменная `TG_PROXY_URL`, транспорт-агностично —
смена на VPS/VLESS = смена одной переменной, без правок кода). Подробности ниже.

Два грабля, на которые наступили:
1. Образ `caomingjun/warp` регистрирует WARP-аккаунт на месте — а
   `api.cloudflareclient.com` из RU-сетей **DNS-отравлен** (8.47.69.0 вместо
   162.159.x.x) → регистрация всегда падает. Регистрировать надо с чистой сети.
2. Готового docker-образа wireproxy нет (ghcr отдаёт denied) — используется
   статический бинарник релиза, смонтированный в alpine.

### 2026-09-05 (1): бот молчал после деплоя (пустой ответ на /start)

Причина: временный сетевой таймаут к `api.telegram.org` в момент старта контейнера
убил фоновую задачу polling **насовсем** (`start_polling` упал на `bot.me()`,
исключение не перехвачено). Приложение при этом оставалось healthy (`/health` жив),
бот — мёртв. Вылечено рестартом `docker compose restart app`. (Чуть позже выяснилось,
что «временный таймаут» был не временным — см. инцидент 2.)

**Открытый код-фикс (добавить к правкам 1.2 вместе с D2):** supervise polling-задачи —
ретрай с backoff или рестарт задачи при падении; сейчас одиночная сетевая ошибка
на старте = молчаливая смерть бота при зелёном health-check.

## WARP-туннель: как это устроено и как чинить

Схема: `app → socks5://warp:1080 → wireproxy (userspace WireGuard) → Cloudflare WARP → api.telegram.org`.

Файлы на VM (только там, в git их нет — `.gitignore`, содержат PrivateKey):

- `~/zabota_mentor/warp/wireproxy.conf` — конфиг туннеля (профиль WARP)
- `~/zabota_mentor/warp/wireproxy` — статический бинарник wireproxy v1.1.3

Контейнер `warp` (alpine) монтирует оба файла и поднимает SOCKS5 на :1080.

### Если туннель надо пересоздать (например, WARP-аккаунт забанили)

Регистрация нового профиля — **только с чистой сети** (мак Timurkarev подходит):

```bash
# на маке (не из RU-сети без VPN, если сеть грязная):
mkdir -p /tmp/wgcf-work && cd /tmp/wgcf-work
curl -sL -o wgcf https://github.com/ViRb3/wgcf/releases/latest/download/wgcf_<версия>_darwin_arm64
chmod +x wgcf && ./wgcf register --accept-tos && ./wgcf generate
# → wgcf-profile.conf (Address/PrivateKey/Peer) — собрать из него wireproxy.conf:
#   [Interface]: PrivateKey, Address = <IPv4 из профиля>/32, DNS = 1.1.1.1
#   [Peer]: PublicKey/Endpoint/AllowedIPs из профиля (IPv6 убрать)
#   [Socks5]: BindAddress = 0.0.0.0:1080
# затем залить на VM:
scp -i ~/.ssh/zabota_staging wireproxy.conf \
  zabota_admin@158.160.146.121:~/zabota_mentor/warp/wireproxy.conf
ssh -i ~/.ssh/zabota_staging zabota_admin@158.160.146.121 \
  "chmod 600 ~/zabota_mentor/warp/wireproxy.conf && \
   cd ~/zabota_mentor && docker compose -f docker-compose.staging.yml restart warp app"
```

### Проверка туннеля

```bash
# egress: должен вернуть HTTP 302
ssh -i ~/.ssh/zabota_staging zabota_admin@158.160.146.121 \
  'curl -s --max-time 10 --socks5-hostname 127.0.0.1:1080 -o /dev/null -w "%{http_code}\n" https://api.telegram.org/'

# polling жив (должен вернуть 409 Conflict — значит наш poller держит соединение):
ssh -i ~/.ssh/zabota_staging zabota_admin@158.160.146.121 \
  'curl -s --socks5-hostname 127.0.0.1:1080 "https://api.telegram.org/bot$(grep ^BOT_TOKEN ~/zabota_mentor/.env | cut -d= -f2)/getUpdates"'
```

## Шпаргалки

```bash
# логи бота на staging
ssh -i ~/.ssh/zabota_staging zabota_admin@158.160.146.121 \
  "cd ~/zabota_mentor && docker compose -f docker-compose.staging.yml logs -f app"

# psql в staging-базу
ssh -i ~/.ssh/zabota_staging zabota_admin@158.160.146.121 \
  "docker exec -it zabota_mentor-postgres-1 psql -U zabota -d zabota_staging"

# перезапустить только app (не трогая БД)
ssh -i ~/.ssh/zabota_staging zabota_admin@158.160.146.121 \
  "cd ~/zabota_mentor && docker compose -f docker-compose.staging.yml restart app"
```
