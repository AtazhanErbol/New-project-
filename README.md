# Beauty by Kabylova — Букинг-лендинг

> Профессиональный лендинг с системой онлайн-записи для beauty-мастера в Астане

**Стек:** Django 5.2 · PostgreSQL/SQLite · Gmail SMTP · GSAP · Render.com

**Instagram:** [@by_kabylova](https://www.instagram.com/by_kabylova)

**Адрес:** г. Астана, ул. Байтурсынова 17/1

---

## Скриншоты

### Главный экран (Hero)
![Hero](screenshots/01_hero.png)

### Услуги
![Услуги](screenshots/02_services.png)

### О мастере
![О мастере](screenshots/03_about.png)

### Галерея работ
![Галерея](screenshots/04_gallery.png)

### Как записаться
![Как записаться](screenshots/05_how_it_works.png)

### Отзывы
![Отзывы](screenshots/06_reviews.png)

### Форма записи — выбор мастера
![Выбор мастера](screenshots/07_booking_master.png)

### Форма записu — выбор услуги
![Выбор услуги](screenshots/08_booking_service.png)

### Форма записи — дата и время
![Дата и время](screenshots/09_booking_datetime.png)

### Форма записи — контактные данные
![Контакты](screenshots/10_booking_contacts.png)

### Модальное окно после записи
![Модалка](screenshots/11_modal.png)

### Админка — записи с цветными статусами
![Админка записи](screenshots/12_admin_bookings.png)

### Админка — мастера
![Админка мастера](screenshots/13_admin_masters.png)

### Админка — настройки сайта
![Админка настройки](screenshots/14_admin_settings.png)

### Мобильная версия
![Мобильная](screenshots/15_mobile.png)

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
| **Hero** | Полноэкранный баннер с фото, розовым оверлеем, typewriter-эффектом |
| **Услуги** | 8 услуг с ценами, фильтрами и 3D hover |
| **О мастере** | Bio, фото, анимированные счётчики, адрес, Instagram |
| **Галерея** | 12 фото, Masonry, фильтры по категориям и мастерам, GLightbox |
| **Как записаться** | 4 шага с SVG-прогрессом |
| **Отзывы** | Swiper.js карусель с рейтингами |
| **Запись** | 4-шаговая форма: Мастер → Услуга → Дата/время → Контакты |
| **Контакты** | Адрес, телефон, соцсети |

### 2. Система записи

- **4-шаговая форма** с прогресс-баром
- **Выбор мастера** — Алина (маникюр) и Марина (педикюр)
- **Календарь Flatpickr** с русской локализацией
- **AJAX-загрузка слотов** при выборе даты
- **Автогенерация слотов** — при создании мастера (9:00–21:30, 2 недели)
- **Фильтрация прошедших слотов** — сегодня после обеда утренние не показываются
- **Race-condition защита** — select_for_update()
- **Маска телефона** — +7 (___) ___-__-__
- **Honeypot** — защита от спам-ботов

### 3. Модальное окно

- Кнопки **WhatsApp и Telegram** для связи
- Закрывается: X, кликом вне окна, кнопкой «Отлично»
- Не конфликтует с баннером (z-index: 10002)

### 4. Gmail SMTP

- HTML-письма с градиентным дизайном
- Клиенту: подтверждение + ссылка отмены (7 дней)
- Администратору: уведомление о новой записи
- Если SMTP не настроен — запись создаётся, письмо помечается «не отправлено»

### 5. Django Admin (всё на русском)

- **Мастера** — аватар, имя, специализация
- **Услуги** — категория, цена, привязка к мастерам
- **Записи** — цветные бейджи, клиент, дата, email статус
- **Слоты** — экшн «Сгенерировать на 2 недели»
- **Портфолио** — фото, категория, мастер
- **Отзывы** — рейтинг, модерация
- **Настройки** — название, лого, тексты, фото, контакты, соцсети
- **CSV экспорт** — UTF-8 BOM (Excel без иероглифов)

### 6. Динамические данные (всё через Admin)

| Поле | Где отображается |
|------|-----------------|
| Название сайта | Шапка, футер |
| Лого (SVG) | Навбар |
| Фото героя | Hero + розовый оверлей |
| Фото о мастере | About |
| Bio | Hero + About |
| Телефон | Навбар, футер |
| Адрес | About, футер |
| Режим работы | About, футер |
| Акция | Hero badge, футер |
| Статистика | Анимированные счётчики |
| Instagram, WhatsApp, Telegram, VK, Facebook, TikTok, YouTube | Модалка, футер |

> Если поле не заполнено — не отображается

### 7. Дизайн

- **Палитра:** слоновая кость · пудровый розовый · матовое золото · шоколад
- **Типографика:** Playfair Display + Inter
- **12+ анимаций:** parallax, typewriter, 3D hover, Masonry, курсор, badge, progress, counter
- **Mobile-first:** 480px, 768px, 1024px
- **prefers-reduced-motion** — анимации отключаются

### 8. Безопасность

CSRF · axes · honeypot · CSP · HSTS · TimestampSigner · select_for_update · Django ORM

### 9. SEO

HTML5 семантика · Open Graph · canonical · lazy loading · alt атрибуты

---

## Установка

```bash
git clone https://github.com/AtazhanErbol/New-project-.git
cd New-project-
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Настройка почты (.env)

```env
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

## Деплой на Render

```bash
# Автоматический через render.yaml
# Нужно: PostgreSQL, переменные окружения
```

---

**Автор:** AtazhanErbol
**Год:** 2024
