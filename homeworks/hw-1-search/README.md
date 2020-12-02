# Домашнее задание №1 по курсу OTUS WebPython 2020

## 1.Задача:

Создать программу поисковик (консольную).

Пользователь вводит текст запроса, поисковую систему (google.com, yandex.ru, ...), количество 
результатов, рекурсивный поиск или нет, формат вывода (в консоль, в файл json, в csv)

Программа находит в интернете начиная от стартовой точки все ссылки на веб-странице в заданном 
количестве (название ссылки и саму ссылку)

Если поиск не рекурсивный, то берем ссылки только из поисковика, если рекурсивный, то берем 
первую ссылку, переходим, находим там ссылки, переходим, ...

В зависимости от выбранного формата вывода сохраняем результат (текст ссылки: ссылка) либо в 
консоль либо в файл выбранного формата

## 2. Обзор реализованного функционала

Особенности реализации

 - Функционал реализован на основе гибридного рекурсивного алгоритма поиска, на основе поиска в ширину.
 Алгоритм подробно задокументирован в коде.
 - Поисковый запрос проходит через фильтрацию стоп-слов (на русском и английском)
 - Для отправки HTTP запросов используется библиотека `requests`. 
 - Для парсинга результатов HTTP запросов используется библиотека Beautiful Soup (`bs4`). Обработка ошибок уровня сети и HTTP минимальна. 
 - Для получения списка релевантных ссылок со страницы поиска используются найденные эмпирическим путем
CSS селекторы, которые специфичны для каждого search engine. 
 - Для логирование процесса поиска используется стандартный модуль `logging`. 
 - Для удобной работы с аргументами командной строки используется библиотека `click`
 - В коде активно используются генераторы и их композиция. Также используются методы класса, 
декораторы и декораторы классов (для логирования)
 - Для факторизации общей части алгоритма поиска используются абстрактные классы (модуль `ABC`)

На данный момент реализация содержит следующий функционал:

 - Выбор поисковика (google, yahoo, yandex - последний не всегда работает из-за защиты от ботов)
 - Фильтрация запроса на стоп-слова на русском и английском (стоп-слова выбрасываются из запроса)
 - Полноценное логирование процесса поиска в файл и консоль, с настройкой уровней логирования
 - Гибридный рекурсивный алгоритм поиска, на основе поиска в ширину
 - Возможность регулировать жесткость поиска 
 - Возможно задавать следующие параметры:
    - Тип поисковой системы
    - Общее число результатов 
    - Тип поиска
        - Жесткий - все слова из запроса должны быть в url или text
        - Нежесткий - хотя бы одно слово из запросы должно быть в url или text
    - Рекурсивный поиск или нет
    - Выводить лог процесса и результат в консоль или нет
    - Максимальная глубина рекурсии
    - Краткий или подробный вывод результатов
    - Путь для сохранения результатов (`.csv`, `.json`)
    - Путь к лог-файлу
    - Уровень логирования
    
## 3.Установка / сборка

### 3.1 Установка и проверка на уровне source code

Выкачиваем репозиторий, устанавливаем venv, зависимости

    cd testdir
    git clone https://github.com/possibly-harmless/WebPythonOTUS.git
    cd WebPythonOTUS/homeworks/hw-1-search
    python -m venv venv
    deactivate
    cd venv/bin
    source activate
    cd ../..
    pip install -r requirements.txt
    
Простейшая проверка

    python -m search "Python generators" --limit=30
    
### 3.2 Все доступные опции и help    
    
После выполнения следующей строчки 

    python -m search --help
    
Должно вернуться что-то вроде этого:

    Usage: __main__.py [OPTIONS] QUERY
    
    Options:
      --engine [yahoo|yandex|google]  Search engine type. Defaults to 'google'
      --limit INTEGER                 Max number of results to return. Default is
                                      30
    
      --recursive / --non-recursive   Whether the search is recursive (default) or
                                      not
    
      --console / --no-console        Whether to print results to console
                                      (default) or not
    
      --mode [any|all]                Keep only links with all (default) or any of
                                      the words in the query
    
      --depth_limit INTEGER           Recursion depth limit. Defaults to 5
      --resultpath TEXT               A path to .csv or .json file to save the
                                      results to. Defaults to None
    
      --verbose / --brief             Whether or not (default) to keep extended
                                      search information in results.
    
      --logpath TEXT                  Path to log file. Defaults to /Users/archie/
                                      Projects/CoursesAndBooks/Python/Otus/Web2020
                                      /Homeworks/WebPythonOTUS/homeworks/hw-1-sear
                                      ch/search/logs/search.log
    
      --loglevel [info|error|warning|debug|critical]
                                      Sets the log level. Defaults to 'info'
      --help                          Show this message and exit.

    
### 3.3 Сборка пакета

Предполагая что шаги описанные в пункте 3.1 выполнены, и venv активирован, нужно из корня
проекта (`.../homeworks/hw-1-search/`) выполнить

    python setup.py sdist bdist_wheel 
        
Собранный дистрибутив можно забрать из папки `"/dist"` (в форматах `".tar.gz"` или `".whl"`).
Для проверки нужно пененести их в пустую папку (напр. `"/testsearch"`), затем

    cd testsearch
    python -m venv venv
    deactivate
    cd venv/bin
    source activate 
    cd ../..
 
Тестируем:   
    
    pip install lshifr-otus-websearch-1.0.0*.tar.gz
    python -m search "Python generators" --limit=30
    
Аналогочно с файлом  `lshifr_otus_websearch-1.0.0-py3-none-any.whl`
    

## Примеры использования  

    python -m search 'python generator' --engine=yahoo --mode=any --limit=40 
    
    python -m search 'python generator' --limit=40 --verbose
    
    python -m search 'python programming' --limit=40 --mode=any  --no-console --resultpath="search_results.csv"
    
    python -m search 'Программирование на python' --limit=30 --verbose --non-recursive

    python -m search 'python generator' --resultpath=search_results.json --mode=all --limit=40 \
    --depth_limit=7 --engine=yahoo --brief --non-recursive  