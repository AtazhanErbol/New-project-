# Деплой на VPS (PS.kz) с доменом devbench.shop

Пошаговая инструкция. Выполняй по порядку, **по одной команде**, проверяя результат.
Предполагается VPS с **Ubuntu 22.04 или 24.04** (команды одинаковые) и доступом
под **root** по SSH.

Везде ниже проект лежит в `/root/New-project-`. Если работаешь под другим
пользователем — замени пути на свои и в файлах `deploy/nginx-devbench.conf`
и `deploy/gunicorn.service`.

---

## Шаг 1. Направить домен на сервер (DNS)

1. Узнай **IP-адрес** своего VPS (в кабинете PS.kz, раздел с сервером).
2. В управлении доменом `devbench.shop` (DNS-записи) создай две A-записи:
   - `@`  → `IP_твоего_сервера`
   - `www` → `IP_твоего_сервера`
3. Подожди 10–30 минут, пока DNS обновится. Проверить можно с любого компьютера:
   ```
   ping devbench.shop
   ```
   Должен отвечать IP твоего сервера. **Пока это не так — SSL на шаге 8 не получится.**

---

## Шаг 2. Подключиться к серверу и установить пакеты

```
ssh root@IP_твоего_сервера
```
```
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx
```

---

## Шаг 3. Скачать проект

Репозиторий приватный, поэтому нужен **токен GitHub**:
1. На github.com → Settings → Developer settings → Personal access tokens →
   Tokens (classic) → Generate new token, поставь галочку **repo**, создай, скопируй.
2. На сервере (подставь СВОЙ токен вместо `ТОКЕН`):
   ```
   cd /root
   git clone -b claude/project-review-bugs-design-1tdbs2 https://ТОКЕН@github.com/AtazhanErbol/New-project-.git
   cd New-project-
   ```

---

## Шаг 4. Виртуальное окружение и зависимости

```
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Шаг 5. Настроить .env

```
cp .env.production.example .env
nano .env
```
Заполни:
- `DJANGO_SECRET_KEY` — сгенерируй ключ (выполни в другой строке и вставь результат):
  ```
  python3 -c "import secrets; print(secrets.token_urlsafe(50))"
  ```
- `ALLOWED_HOSTS=devbench.shop,www.devbench.shop`
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (пароль приложения Gmail), `ADMIN_EMAIL`.

Сохрани: `Ctrl+O`, `Enter`, `Ctrl+X`.

---

## Шаг 6. Инициализировать базу и статику

```
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```
(последняя команда создаёт админа — задай логин и пароль).

---

## Шаг 7. Запустить приложение через systemd (gunicorn)

```
cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
systemctl daemon-reload
systemctl enable --now gunicorn
systemctl status gunicorn
```
Статус должен быть **active (running)**. Если ошибка — покажи вывод
`journalctl -u gunicorn -n 50`.

---

## Шаг 8. Настроить nginx

```
cp deploy/nginx-devbench.conf /etc/nginx/sites-available/devbench.shop
ln -s /etc/nginx/sites-available/devbench.shop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```
`nginx -t` должен сказать **syntax is ok / test is successful**.

---

## Шаг 9. Включить HTTPS (бесплатный SSL Let's Encrypt)

DNS уже должен указывать на сервер (Шаг 1). Выполни:
```
certbot --nginx -d devbench.shop -d www.devbench.shop
```
На вопросы: укажи email, согласись с условиями, при вопросе о редиректе выбери
**2 (Redirect)**. Certbot сам получит сертификат и настроит https.

Открой `https://devbench.shop` — сайт должен открыться с замком 🔒.

---

## Шаг 10. Проверить

- `https://devbench.shop` — сайт открывается.
- `https://devbench.shop/admin/` — заходит под созданным суперюзером.
- Сделай тестовую запись → проверь почту.

---

## Как обновлять сайт в будущем

Когда я вношу новые изменения (пуш в ветку), на сервере:
```
cd /root/New-project-
source venv/bin/activate
git pull
pip install -r requirements.txt        # если менялись зависимости
python manage.py migrate               # если менялись модели
python manage.py collectstatic --noinput
systemctl restart gunicorn
```
(nginx перезапускать не нужно — только gunicorn.)

---

## Если что-то не работает
- Логи приложения: `journalctl -u gunicorn -n 80`
- Логи nginx: `tail -n 50 /var/log/nginx/error.log`
- Проверка статуса: `systemctl status gunicorn nginx`

Пришли мне вывод — подскажу, что поправить.
