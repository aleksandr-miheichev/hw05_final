# Платформа для социальных сетей

[![Python-Lint-Test](https://github.com/aleksandr-miheichev/social_platform/actions/workflows/python-app.yml/badge.svg)](https://github.com/aleksandr-miheichev/social_platform/actions/workflows/python-app.yml)

## Содержание

- [Описание проекта](#описание-проекта)
- [Технологический стек](#технологический-стек)
- [Как развернуть проект](#как-развернуть-проект)
- [Запуск приложения](#запуск-приложения)
- [Над проектом работал](#над-проектом-работал)

---

### Описание проекта:

Основанная на Django социальная медиаплатформа, на которой пользователи могут:

- **создавать сообщения**: поделитесь мыслями, историями или любым контентом с
  сообществом;
- **присоединиться к сообществам**: изучите различные группы, каждая из которых
  имеет свою уникальную тему и участников. Создавайте или присоединяйтесь к
  существующим сообществам, исходя из своих интересов.
- **просматривать профиля пользователей**: погрузитесь в профили пользователей,
  чтобы увидеть их сообщения и активность.
- **взаимодействовать с контентом**: взаимодействуйте с сообщениями различных
  сообществ или отдельных пользователей.

Платформа предоставляет простой и интуитивно понятный интерфейс, обеспечивая
беспрепятственный опыт как для создателей контента, так и для читателей.

---

### Технологический стек:

- [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
- [![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
- [![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://html.spec.whatwg.org/multipage/)
- [![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://www.w3.org/TR/css-2023/)
- [![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)](https://docs.github.com/en/actions)

---

### Как развернуть проект:

Клонировать репозиторий и перейти в него в терминале используя команду

```bash
cd
```

```bash
git clone git@github.com:aleksandr-miheichev/social_platform.git
```

Создать и активировать виртуальное окружение:

```bash
python -m venv venv
```

```bash
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

---

### Запуск приложения:

Чтобы запустить модуль, необходимо в терминале перейти в папку yatube:

```bash
cd .\yatube\
```

Далее необходимо применить миграции:

```bash
python manage.py migrate
```

После этого осуществить запуск приложения:

```bash
python manage.py runserver
```

Далее отрыть сайт с проектом перейдя по ссылке:

http://127.0.0.1:8000/

---

### Над проектом работал:

- [Михеичев Александр](https://github.com/aleksandr-miheichev)
