# Beauty by Kabylova — Букинг-лендинг

> Профессиональный лендинг с системой онлайн-записи для beauty-мастера в Астане

**Стек:** Django 5.2 · PostgreSQL/SQLite · Gmail SMTP · GSAP · Render.com

**Instagram:** [@by_kabylova](https://www.instagram.com/by_kabylova)

**Адрес:** г. Астана, ул. Байтурсынова 17/1

---

## Демо

**Сайт:** http://localhost:8000

**Админ-панель:** http://localhost:8000/admin/

**Логин:** admin / admin123

---

## Что было сделано

### 1. Лендинг (8 секций)

| Секция | Описание |
|--------|----------|
| **Hero** | Полноэкранный баннер с фото, розовым оверлеем, typewriter-эффектом и анимированной акцией |
| **Услуги** | 8 услуг с ценами, фильтрацией по категориям и 3D hover-эффектом |
| **О мастере** | Bio, фото, анимированные счётчики (лет/клиентов/работ), адрес, Instagram |
| **Галерея** | 12 фото в Masonry-сетке с фильтрами по категориям и мастерам, GLightbox |
| **Как записаться** | 4 шага с SVG-прогрессом |
| **Отзывы** | Swiper.js карусель с рейтингами и привязкой к мастерам |
| **Запись** | 4-шаговая форма: Мастер → Услуга → Дата/время → Контакты |
| **Контакты + Футер** | Адрес, телефон, соцсети (Instagram, WhatsApp, Telegram, VK, Facebook, TikTok, YouTube) |

### 2. Система записи

- **4-шаговая форма** с прогресс-баром
- **Выбор мастера** — 2 мастера: Алина (маникюр/наращивание) и Марина (педикюр/дизайн)
- **Календарь Flatpickr** — мини-календарь с русской локализацией
- **AJAX-загрузка слотов** — время загружается динамически при выборе даты
- **Автогенерация слотов** — при создании мастера слоты на 2 недели генерируются автоматически (9:00–21:30)
- **Фильтрация прошедших слотов** — сегодня после обеда утренние слоты не показываются
- **Race-condition защита** — `select_for_update()` при бронировании
- **Маска телефона** — +7 (___) ___-__-__
- **Honeypot** — защита от спам-ботов

### 3. Модальное окно

- Появляется после успешной записи
- **Кнопки WhatsApp и Telegram** — клиент может написать если письмо не пришло
- Закрывается: кнопка X, кликом вне окна, кнопкой «Отлично»
- **Не конфликтует** с кнопками баннера (z-index: 10002, opaque фон)

### 4. Gmail SMTP

- HTML-письма с фирменным дизайном (градиент розовый → золотой)
- **Клиенту:** подтверждение записи (услуга, дата, время, адрес, ссылка отмены)
- **Администратору:** уведомление о новой записи с полными данными
- **Ссылка отмены** через `TimestampSigner` (действует 7 дней)
- Если SMTP не настроен — запись создаётся, письмо помечается как «не отправлено»

### 5. Django Admin

- **Все на русском языке**
- **Мастера** — аватар (превью), имя, специализация, статус
- **Услуги** — категория, цена, длительность, привязка к мастерам
- **Записи** — цветные бейджи статусов, клиент+телефон, дата+время, email статус
- **Слоты** — дата, время, мастер, статус. Экшн «Сгенерировать слоты на 2 недели»
- **Портфолио** — фото, категория, мастер
- **Отзывы** — имя, рейтинг, мастер, модерация
- **Настройки сайта** — всё редактируется: название, лого, тексты, фото, контакты, соцсети
- **CSV экспорт** — UTF-8 BOM (открывается в Excel без иероглифов)

### 6. Динамические данные (всё через Admin)

| Поле | Где отображается |
|------|-----------------|
| Название сайта | Шапка, футер, SEO |
| Лого (текст/SVG) | Навбар |
| Фото героя | Hero секция с розовым оверлеем |
| Фото о мастере | Секция «О мастере» |
| Bio / описание | Hero подзаголовок, About секция |
| Телефон | Навбар, футер |
| Адрес | About, футер |
| Режим работы | About, футер |
| Email | Футер |
| Акция | Hero badge, футер |
| Статистика | Анимированные счётчики |
| Instagram | About, футер |
| WhatsApp | Модалка, футер |
| Telegram | Модалка, футер |
| VK, Facebook, TikTok, YouTube | Футер |
| Текст футера | Нижняя строка |

> **Если поле не заполнено — не отображается на сайте**

### 7. Дизайн

- **Палитра:** слоновая кость (#FAF7F2) · пудровый розовый (#F5C6D0) · матовое золото (#C9A96E) · шоколад (#2C1A1A)
- **Типографика:** Playfair Display (заголовки) + Inter (текст)
- **12+ анимаций:** parallax, typewriter, 3D hover, Masonry, кастомный курсор, floating badge, SVG progress, counter animation
- **Mobile-first:** 3 брейкпоинта (480px, 768px, 1024px)
- **prefers-reduced-motion** — все анимации отключаются

### 8. Безопасность

| Защита | Реализация |
|--------|-----------|
| CSRF | Django `{% csrf_token %}` |
| Brute force | django-axes (5 попыток) |
| Спам-боты | django-honeypot |
| XSS | Django auto-escape |
| SQL Injection | Django ORM |
| Секреты | django-environ + .env |
| CSP | django-csp middleware |
| HSTS | production settings |
| Отмена записи | TimestampSigner (7 дней) |
| Race condition | select_for_update() |

### 9. SEO

- Семантический HTML5 (`<header>`, `<main>`, `<section>`, `<footer>`)
- Open Graph + Twitter Card мета-теги
- Canonical URL
- `loading="lazy"` для изображений
- `alt` атрибуты для всех фото
- Иерархия заголовков: h1 → h2 → h3

---

## Установка

```bash
# Клонировать
git clone https://github.com/AtazhanErbol/New-project-.git
cd New-project-

# Виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Зависимости
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Заполнить данными (опционально)
python manage.py shell
>>> from apps.booking.models import Master
>>> Master.objects.create(name='Алина', specialization='Маникюр, наращивание')
>>> Master.objects.create(name='Марина', specialization='Педикюр, дизайн')
>>> exit()

# Запуск
python manage.py runserver
```

## Настройка почты (.env)

```env
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

> Для Gmail: настройте **App Password** в Google Account → Security → 2-Step Verification → App Passwords

## Деплой на Render

1. Создайте Blueprint в Render
2. Подключите PostgreSQL
3. Настройте переменные окружения
4. Деплой автоматический через `render.yaml`

---

## Структура проекта

```
beauty_site/
├── manage.py
├── requirements.txt
├── .env
├── render.yaml
├── config/
│   ├── settings/ (base, development, production)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/ (SiteSettings, context_processors)
│   ├── booking/ (Master, Service, TimeSlot, Booking)
│   ├── portfolio/ (PortfolioItem)
│   └── reviews/ (Review)
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── emails/ (2 HTML-письма)
│   └── partials/ (9 partials)
└── static/
    ├── css/ (main.css, animations.css)
    └── js/ (main.js, animations.js, booking.js, cursor.js)
```

---

**Автор:** AtazhanErbol
**Год:** 2024
