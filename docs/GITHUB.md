# Репозиторий masterprogramm

Учебный проект: https://github.com/artyom4iklol/masterprogramm.

## Получить рабочую копию

В терминале выбери папку для курса, затем:

```bash
git clone https://github.com/artyom4iklol/masterprogramm.git
cd masterprogramm
```

В VS Code открой эту папку целиком. Альтернатива без Git: Code → Download ZIP
на странице репозитория, распаковать и открыть папку с course.json.
Архив подходит для учёбы; история commit требует Git.

## Учебная ветка и первая попытка

```bash
git switch -c work/week01
```

После собственного решения W01:

```bash
git add work/week01/W01.md work/week01/answers.py notebooks/01_choice_and_duality.ipynb research/help_log.csv
git commit -m "W01: first independent attempt"
git push -u origin work/week01
```

Для push используй обычный вход GitHub в VS Code; токены в файлы курса не вписывай.
Сохраняй первую попытку до чтения разбора. Исправление — отдельный commit с
объяснением причины ошибки. Заполняй research/help_log.csv: собственную работу,
полученную помощь и то, что воспроизвёл после закрытия подсказки.

Для разбора можно открыть draft pull request из work/week01 в main или прислать
в чат ZIP от `python course.py submit`. Автоматического слияния в поставке нет.

## Автоматическая проверка

GitHub Actions проверяет структуру, запускает status и selfcheck. Начальный
pending допустим: решения ещё не написаны. Зелёный workflow означает исправность
инфраструктуры и отсутствие обнаруженных ошибок кода; он не означает учебный зачёт.
Письменные решения, предпосылки и защита требуют отдельного разбора.

## Сайт

Локальная сборка описана в README. Публикация GitHub Pages пока не настроена;
ссылка репозитория ведёт к исходникам, а не к работающему интерактивному Jupyter.
Для расчётов используй своё окружение Python.

Официальные инструкции:
https://code.visualstudio.com/docs/sourcecontrol/overview
https://jupyterbook.org/v1/start/build.html
