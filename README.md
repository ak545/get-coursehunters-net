# Get Courses from coursehunters.net from ak545
**get.coursehunters.net.py** - Это python-скрипт для для загрузки курсов с сайта https://coursehunters.net/.

## Скриншоты
> Скрипт в работе
![](https://github.com/ak545/get-coursehunters-net/raw/master/images/script.png)

## Описание
Это python-скрипт для для загрузки курсов с сайта https://coursehunters.net/.


**Особенности скрипта:**

- Извлекает название курса (это название служит именем под-папки для загрузки контента курса); 
- Извлекает описание курса (сохраняет его в файле description.txt); 
- Извлекает язык курса (добавляет префикс языка к названию под-папки для загрузки контента курса);
- Скачивает все найденные видео курса; 
- Если на сайте https://coursehunters.net/ имеется ссылка на видео файл с просроченным или неверным SSL сертификатом, всё равно пытается скачать такой файл;
- Если имеется дополнительный материал, скачивает и его (за исключением ссылок на репозитории https://github.com/, размещённые в описании курса).

## Инсталляция
Для работы скрипта необходим **Python версии 3.6 или выше**.
Разумеется, необходимо сперва установить сам [Python](https://www.python.org/). В Linux он обычно уже установлен. Если нет, установите его, например:

---
**Для Linux:**
```console
foo@bar:~$ sudo yum install python3
foo@bar:~$ sudo dnf install python3
foo@bar:~$ sudo apt install python3
foo@bar:~$ sudo pacman -S python
```
---
**Для Apple macOS:**
```console 
foo@bar:~$ xcode-select --install
```

Установите brew:

```console
foo@bar:~$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Установите Python:

```console
foo@bar:~$ export PATH=/usr/local/bin:/usr/local/sbin:$PATH
foo@bar:~$ brew install python
```

Примечание: [brew](https://brew.sh/index_ru)

---
**Для Microsoft Windows:**

Для Microsoft Windows скачайте [дистрибутив](https://www.python.org/downloads/windows/) и установите его. Я рекомендую скачивать **"Download Windows x86 web-based installer"** если у вас 32-х битная ОС и **"Download Windows x86-64 web-based installer"** если у вас 64-х битная ОС. Во время установки рекомендую отметить все опции (Documentation, pip, tcl/tk and IDLE, Python test suit, py launcher, for all users (requeres elevation)).

---

Предварительно, возможно понадобится обновить сам **pip** (установщик модулей Python):

```console
foo@bar:~$ python -m pip install --upgrade pip
```

### Установка зависимостей

```console
foo@bar:~$ pip install colorama
foo@bar:~$ pip install beautifulsoup4
```

### Обновление зависимостей

```console
foo@bar:~$ pip install --upgrade colorama
foo@bar:~$ pip install --upgrade beautifulsoup4
```

В зависимости от вашего Pyton окружения, ваши действия будут немного иными, например, возможно, вам потребуется указать ключ **--user** (для **pip**) или вместо команд **python** и **pip** использовать команды **python3** и **pip3**. Если вы используете [виртуальные окружения](https://docs.python.org/3/library/venv.html), то скорее всего, все эти действия вам необходимо будет сделать после входа в соответствующее окружение.

## Использование
   
```console
foo@bar:~$ get.coursehunters.net.py -h

usage: get.coursehunters.net.py [-h][-v][-nb] -u URL [-o DIR]

Get Courses from coursehunters.net A simple python script for download the
courses from coursehunters.net.

Options:
-h, --help         Help
-v, --version      Display the version number
-u URL, --url URL  URL of the Course (default is None)
-o DIR, --out DIR  Download dir for the Course (default is None)
-nb, --no-banner   Do not print banner (default is False)
```

Например:

```console
foo@bar:~$ get.coursehunters.net.py -u "https://coursehunters.net/course/prakticheskiy-html" -o "~/courses"
```

или

```console
foo@bar:~$ python get.coursehunters.net.py "https://coursehunters.net/course/prakticheskiy-html"
```

или

```console
foo@bar:~$ ./get.coursehunters.net.py "https://coursehunters.net/course/prakticheskiy-html" -o "~/courses"
```

Чтобы запускать скрипт напрямую, выполните команду:

```console
foo@bar:~$ chmod +x /home/user/py/get.coursehunters.net.py
```

Скорректируйте в первой строке скрипта [Шебанг (Unix)](https://ru.wikipedia.org/wiki/%D0%A8%D0%B5%D0%B1%D0%B0%D0%BD%D0%B3_(Unix)), например:

Показать путь, где расположен python:
```console    
foo@bar:~$ which python
```

или
```console
foo@bar:~$ which python3
```

Коррекция пути python в Шебанг:

```python
    #!/usr/bin/python
    #!/usr/bin/python3
    #!/usr/bin/env python
    #!/usr/bin/env python3
```

Переименуйте скрипт:
```console
foo@bar:~$ mv /home/user/py/get.coursehunters.net.py /home/user/py/get.coursehunters.net
```

Проверьте запуск скрипта:
```console
foo@bar:~$ /home/user/py/get.coursehunters.net -h
foo@bar:~$ /home/user/py/./get.coursehunters.net -h
```

### Описание опций
**-h, --help**

Помощь

**-v, --version**
    
Показать номер версии

**-u URL, --url URL**

URL курса

**-o DIR, --out DIR**

Папка для загрузки курса (название курса и язык курса указывать не надо!)
> Если параметр не задан, загрузка происходит в текущую папку ( **[os.getcwd](https://www.tutorialspoint.com/python3/os_getcwd.htm)** )!
> ```python
> 
>     if NAMESPACE.out:
>         # Если параметр задан
>         # Создание папки для сохранения видео и материалов курса
>         try:
>             Path(NAMESPACE.out).mkdir(parents=True, exist_ok=True)
>         except:
>             print(f'Ошибка создания папки:\n{FLY}{NAMESPACE.out}')
>             print(f'Проверьте корректность задания параметров.')
>             print(f'Не добавляйте в конце параметра обратный слеш "{FLY}\\"')
>             sys.exit(-1)
>     else:
>         # Если параметр не задан
>         NAMESPACE.out = os.getcwd()
> ```

**-nb, --no-banner**

Не печатать баннер (по умолчанию False).
Баннер, это информация о среде исполнения скрипта: версия Python, имя компьютера, имя ОС, релиз ОС, версия ОС, архитектура, ЦПУ, сводная таблица предустановленных опций.


## Глобальные константы параметров в скрипте
Все параметры находятся внутри скрипта. Не стоит их изменять.

## Лицензия
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)

## Ограничения
Я, автор этого python-скрипта, написал этот скрипт исключительно для своих нужд. Никаких гарантий не предоставляется. Вы можете использовать этот скрипт свободно, без каких либо отчислений, в любых целях, кроме тех, что намеренно приводят ко [злу](https://ru.wikipedia.org/wiki/Зло).

Вы можете вносить любые правки в код скрипта и делать форк этого скрипта, указав в качестве источника вашего вдохновения [меня](https://github.com/ak545).
Я не тщеславен, но хорошее слово и кошке приятно.

## Постскриптум
- Работа скрипта проверялась в Microsoft Windows 10, Linux Fedora 30, Linux Ubuntu Descktop 18.10, Linux CentOS 6/7, Linux Manjaro 18.0.2.
- Программный код скрипта не идеален. 
- Все рекомендации данные мной для Apple macOS могут содержать в себе неточности. Простите, у меня нет под рукой Apple macBook (но вдруг, кто-то подарит мне его?).
- Да здравствует E = mc&sup2; !
- Желаю всем удачи!

## Последняя просьба
Пришло время положить конец Facebook. Работа там не является нейтральной с этической точки зрения: каждый день, когда вы идете туда на работу, вы делаете что-то не так. Если у вас есть учетная запись Facebook, удалите ее. Если ты работаешь в Facebook, увольняйся.

И давайте не будем забывать, что Агентство национальной безопасности должно быть уничтожено.

*(c) [David Fifield](mailto:david@bamsoftware.com)*


---


> Best regards, ak545 ( ru.mail&copy;ak545&sup2; )