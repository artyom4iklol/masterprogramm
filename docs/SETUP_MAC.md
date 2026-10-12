# Запуск на Mac

## 1. Скачать и открыть

На https://github.com/artyom4iklol/masterprogramm выбери Code → Download ZIP.
Распакуй архив или клонируй репозиторий по инструкции docs/GITHUB.md.
В VS Code: File → Open Folder → выбери папку с `course.json`. Для просмотра инструкции
без установки открой `START_HERE.html` двойным щелчком.

## 2. Python и расширения

Проверь в терминале VS Code: `python3.12 --version`.
Если команды нет, установи Python3.12.x с официального сайта
https://www.python.org/downloads/macos/ либо используй существующий менеджер
окружений, если уже работаешь с ним. Номер в `python --version` после активации
среды должен начинаться с3.12. Поставка рассчитана на эту ветку.

Установи расширения Microsoft Python (`ms-python.python`) и Jupyter
(`ms-toolsai.jupyter`). VS Code также предложит их из списка рекомендаций.
Вычислительное ядро и локальный сборщик книги используют Python.

## 3. Выполнить команды

Все команды ниже выполняются в папке, где лежит `course.json`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name masters-2027 --display-name "Masters2027"
python course.py environment
python course.py status
```

`status` первоначально покажет незавершённые задания. Это ожидаемый результат,
поскольку решения в архиве не заполнены. Для нового терминала повторяй
`source .venv/bin/activate`.

## 4. Открыть первый ноутбук

Файл `notebooks/00_environment.ipynb`. В правом верхнем углу Select Kernel →
Masters2027. Если ядро не появилось, выбери Python Environments и интерпретатор
`.venv/bin/python` внутри папки курса. Run All должен показать версии,
контроль умножения матриц и график. Это техническая проверка установки.

Официальная инструкция VS Code:
https://code.visualstudio.com/docs/datascience/jupyter-notebooks
Изоляция окружения Python:
https://docs.python.org/3.12/tutorial/venv.html

## 5. Начать содержание

Прочитай `course/week01.md` и `assignments/week01/W01_KKT.md`.
Запиши вывод в `work/week01/W01.md`, реализуй `consumer_quadratic` в answers.py.
Открой `notebooks/01_choice_and_duality.ipynb`; запускай блоки после реализации.
При изменении answers.py повторно выполни ячейку `a = load_answers()`.

## 6. Ошибки запуска

| Сообщение | Действие |
|---|---|
| command not found: python3.12 | Установи/выбери Python3.12; перезапусти терминал |
| ModuleNotFoundError: numpy | Активируй .venv и выполни установку requirements.txt |
| Ядро не найдено | Выбери интерпретатор .venv в Select Kernel |
| Не найдена course.json | Открой целую папку курса, не отдельный ноутбук вне неё |
| НЕ ВЫПОЛНЕНО / pending | Реализуй указанную учебную функцию |
| failed в selfcheck | Читай конкретную проверку, сохраняй ошибочную попытку |

Не используй `sudo pip`. Запиши фактические версии после успешной установки:
`python -m pip freeze > reports/environment-lock.txt`.
Первые установки требуют интернета; чтение локальных файлов и расчёты после
установки работают локально.
