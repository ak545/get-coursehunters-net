#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Program: Get Courses from coursehunters.net
#
# Author: Andrey Klimov < ak545 at mail dot ru >
# https://github.com/ak545
#
# Current Version: 0.1.2
# Date: 14-07-2019 (dd-mm-yyyy)
#
# License:
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.

import os
import sys
import platform
import argparse
import requests
import re
import itertools
from pathlib import Path
import time
import urllib3

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("""You need bs4!
                install it from https://pypi.org/project/bs4
                or run pip install bs4.""")

try:
    from colorama import init
    from colorama import Fore, Back, Style
except ImportError:
    sys.exit(
        """You need colorama!
                install it from http://pypi.python.org/pypi/colorama
                or run pip install colorama"""
    )

# Init colorama
init(autoreset=True)

urllib3.disable_warnings()

# Check Python Version
if sys.version_info < (3, 6):
    print("Error. Python version 3.6 or later required to run this script")
    print("Your version:", sys.version)
    sys.exit(-1)

# Глобальные константы
__version__ = "0.1.2"

FR = Fore.RESET
FLW = Fore.LIGHTWHITE_EX
FLG = Fore.LIGHTGREEN_EX
FLR = Fore.LIGHTRED_EX
FLC = Fore.LIGHTCYAN_EX
FLY = Fore.LIGHTYELLOW_EX
FLM = Fore.LIGHTMAGENTA_EX
FLB = Fore.LIGHTBLUE_EX

BLB = Back.LIGHTBLACK_EX
BR = Back.RESET

SDIM = Style.DIM
SNORMAL = Style.NORMAL
SBRIGHT = Style.BRIGHT
SR = Style.RESET_ALL

SEP = os.sep

# Command line parameters
NAMESPACE = None

# User-Agent for requests
S_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.46 Safari/537.36'

STREAM = sys.stderr

# Шаблоны для progress bar
BAR_TEMPLATE = '%s[%s%s] %s ( %s ) ( %s )\r'
MILL_TEMPLATE = '%s %s %i/%i\r'
DOTS_CHAR = '.'
BAR_FILLED_CHAR = '#'
BAR_EMPTY_CHAR = ' '
MILL_CHARS = ['|', '/', '-', '\\']

# How long to wait before recalculating the ETA
ETA_INTERVAL = 1
# How many intervals (excluding the current one) 
# to calculate the simple moving average
ETA_SMA_WINDOW = 9


def humanize_bytes(bytesize, precision=2):
    """
    Humanize byte size figures
    :param bytesize: float
    :param precision: int
    :return: string
    """
    abbrevs = (
        (1 << 50, 'PB'),
        (1 << 40, 'TB'),
        (1 << 30, 'GB'),
        (1 << 20, 'MB'),
        (1 << 10, 'kB'),
        (1, 'bytes')
    )
    if bytesize == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if bytesize >= factor:
            break
    return '%.*f %s' % (precision, bytesize / factor, suffix)


class MyBar(object):
    """
    Рисует прогресс бар в консоли
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()
        return False  # we're not suppressing exceptions

    def __init__(self, label='', width=32, hide=None, empty_char=BAR_EMPTY_CHAR,
                 filled_char=BAR_FILLED_CHAR, expected_size=None, every=1, total_length=None):
        self.label = label
        self.width = width
        self.hide = hide
        # Only show bar in terminals by default (better for piping, logging etc.)
        if hide is None:
            try:
                self.hide = not STREAM.isatty()
            except AttributeError:  # output does not support isatty()
                self.hide = True
        self.empty_char = empty_char
        self.filled_char = filled_char
        self.expected_size = expected_size
        self.every = every
        self.total_length = total_length
        self.str_total_length = humanize_bytes(self.total_length)
        self.str_percent = '0.00 %'
        self.start = time.time()
        self.ittimes = []
        self.eta = 0
        self.etadelta = time.time()
        self.etadisp = self.format_time(self.eta)
        self.last_progress = 0
        if (self.expected_size):
            self.show(0)

    def show(self, progress, count=None):
        if count is not None:
            self.expected_size = count
        if self.total_length is None:
            self.total_length = 0
        self.str_total_length = humanize_bytes(self.total_length)
        if self.expected_size is None:
            raise Exception("expected_size not initialized")

        if (progress == self.expected_size):
            self.str_percent = "100 %"
        else:
            self.str_percent = "{:6.2f} %".format(progress * 100 / self.expected_size)

        self.last_progress = progress
        if (time.time() - self.etadelta) > ETA_INTERVAL:
            self.etadelta = time.time()
            self.ittimes = \
                self.ittimes[-ETA_SMA_WINDOW:] + \
                [-(self.start - time.time()) / (progress + 1)]
            self.eta = \
                sum(self.ittimes) / float(len(self.ittimes)) * \
                (self.expected_size - progress)
            self.etadisp = self.format_time(self.eta)
        x = int(self.width * progress / self.expected_size)
        if not self.hide:
            if ((progress % self.every) == 0 or  # True every "every" updates
                    (progress == self.expected_size)):  # And when we're done
                STREAM.write(BAR_TEMPLATE % (
                    self.label, self.filled_char * x,
                    self.empty_char * (self.width - x), self.etadisp, self.str_percent, self.str_total_length))

                STREAM.flush()

    def done(self):
        # self.elapsed = time.time() - self.start
        # elapsed_disp = self.format_time(self.elapsed)
        elapsed_disp = self.format_time(0)
        self.str_percent = "100.00 %"
        if not self.hide:
            # Print completed bar with elapsed time
            STREAM.write(BAR_TEMPLATE % (
                self.label, self.filled_char * self.width,
                self.empty_char * 0, elapsed_disp, self.str_percent, self.str_total_length))

            STREAM.write('\n')
            STREAM.flush()

    def format_time(self, seconds):
        return time.strftime('%H:%M:%S', time.gmtime(seconds))


# Функция рисования progress bar
def bar(it, label='', width=32, hide=None, empty_char=BAR_EMPTY_CHAR,
        filled_char=BAR_FILLED_CHAR, expected_size=None, every=1, total_length=None):
    """Progress iterator. Wrap your iterables with it."""

    count = len(it) if expected_size is None else expected_size

    with MyBar(label=label, width=width, hide=hide, empty_char=empty_char,
               filled_char=filled_char, expected_size=count, every=every, total_length=total_length) \
            as bar:
        for i, item in enumerate(it):
            yield item
            bar.show(i + 1)


def dots(it, label='', hide=None, every=1):
    """Progress iterator. Prints a dot for each item being iterated"""

    count = 0

    if not hide:
        STREAM.write(label)

    for i, item in enumerate(it):
        if not hide:
            if i % every == 0:  # True every "every" updates
                STREAM.write(DOTS_CHAR)
                sys.stderr.flush()

        count += 1

        yield item

    STREAM.write('\n')
    STREAM.flush()


def mill(it, label='', hide=None, expected_size=None, every=1):
    """Progress iterator. Prints a mill while iterating over the items."""

    def _mill_char(_i):
        if _i >= count:
            return ' '
        else:
            return MILL_CHARS[(_i // every) % len(MILL_CHARS)]

    def _show(_i):
        if not hide:
            if ((_i % every) == 0 or  # True every "every" updates
                    (_i == count)):  # And when we're done

                STREAM.write(MILL_TEMPLATE % (
                    label, _mill_char(_i), _i, count))
                STREAM.flush()

    count = len(it) if expected_size is None else expected_size

    if count:
        _show(0)

    for i, item in enumerate(it):
        yield item
        _show(i + 1)

    if not hide:
        STREAM.write('\n')
        STREAM.flush()


def save_html_dump(html, filename):
    """
    Сохранение отладочного дампа html в файл
    :param html: string  # Содержимое
    :param filename: string  # Имя файла для записи отладочного дампа
    :return: None
    """
    bs = BeautifulSoup(html, 'html.parser')
    dump = []
    dump.append(bs.prettify())
    open_mode = "w+"
    with open(filename, open_mode, encoding="utf-8", newline="\n") as f:
        for item in dump:
            f.write("%s\n" % item)


def get_html(url, error_msg=''):
    """
    Загрузка веб страницы курса

    Возвращает: Строку-дамп HTML-страницы

    :param url: string  # url курса
    :param error_msg: string  # Строка выводимая во время 
                              # ошибки при попытке загрузить 
                              # HTML страницу курса
    :return: str
    """
    global S_USER_AGENT
    if error_msg.strip() != '':
        error_msg = error_msg + ' невозможен'

    headers = {
        'User-Agent': S_USER_AGENT
    }
    try:
        result = requests.get(url, timeout=10, headers=headers, verify=False)
        result.raise_for_status()
        return result.text
    except requests.exceptions.RequestException as e:
        if error_msg.strip() != '':
            print(f'\r{FLR}{error_msg}         ')
        print(f'Не получилось подключиться к сайту: {FLG}{url}')
        print(f'{e}')
        sys.exit(-1)


def get_videos(url):
    """
    Поиск видео файлов на HTML странице курса

    Возвращает: 
    язык курса (string), 
    название курса (string), 
    описание курса (string),
    список из словарей ["название видео", "ссылка на видео"] 
        list[
                {'title': 'item1', 'link': 'item2'}, 
                {'title': 'item1', 'link': 'item2'}, 
                ..., 
                {'title': 'item1', 'link': 'item2'}, 
            ]
    
    :param url: string  # url курса
    :return: string, string, list
    """
    title_course = ''
    title_description = ''
    data = []
    lng = 'en'
    html = get_html(url=url, error_msg='Поиск видео')
    if html:
        # save_html_dump(html=html, filename='dump.txt')
        bs = BeautifulSoup(html, 'html.parser')
        item = bs.find('h1', class_='hero-title')
        if item:
            title_course = item.text.strip()

        item = bs.find('div', class_='course-wrap-description')
        if item:
            title_description = str(item).strip()
            title_description = str(title_description).replace('<div class="course-wrap-description">', '').replace(
                '</div>', '').replace('<br>', "\n").replace('<br/>', "\n").replace(
                '<p>', '').replace('</p>', "\n").replace(
                '<ul>', '').replace('</ul>', "\n").replace('<li>', '- ').replace('</li>', "\n").replace(
                '<strong>', '').replace('</strong>', '').replace('<em>', '').replace('</em>', '')

        items = bs.find_all('div', class_='course-box-value')
        if items:
            for item in items:
                if 'Ангельский' in item.text.strip():
                    print(f'Язык     : [ {FLB}Ангельский{FR} ]')
                    lng = 'en'
                if 'Русский' in item.text.strip():
                    print(f'Язык     : [ {FLB}Русский{FR} ]')
                    lng = 'ru'

        items = bs.find_all('li', class_='lessons-item')
        if items:
            for item in items:
                item_title = item.find('div', class_='lessons-name')
                item_href = item.find('link', itemprop="contentUrl")
                if item_href:
                    data.append({
                        'title': item_title.text.strip(),
                        'link': item_href.get('href').strip()
                    })

        item = bs.find('a', class_='section-block-btn btn-outline')
        if item:
            data.append({
                'title': item.text.strip(),
                'link': item.get('href').strip()
            })
    return lng, title_course, title_description, data


def sanitize_filename(s, restricted=False, is_id=False):
    """
    Изменяет строку (s) так, чтобы её можно было использовать,
    как часть имени файла.
    Параметр restricted изменит строку на основании более
    строгого подмножества разрешенных для файловой системы
    символов (accent_chars).
    Параметр is_id позволяет не изменять идентификаторы
    (если это возможно).

    Modifies the string (s) so that it can be used as part of
    the file name.
    The restricted parameter will change the string based on
    a more strict subset of the allowed characters (accent_chars)
    for the file system.
    The is_id parameter allows not to change identifiers
    (if possible).

    :param s: string
    :param restricted: bool
    :param is_id: bool
    :return: string
    """

    def replace_insane(char):
        accent_chars = dict(zip('ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñò'
                                'óôõöőøœùúûüűýþÿ',
                                itertools.chain(
                                    'AAAAAA',
                                    ['AE'],
                                    'CEEEEIIIIDNOOOOOOO',
                                    ['OE'],
                                    'UUUUUYP',
                                    ['ss'],
                                    'aaaaaa',
                                    ['ae'],
                                    'ceeeeiiiionooooooo',
                                    ['oe'],
                                    'uuuuuypy'
                                )))
        if restricted and char in accent_chars:
            return accent_chars[char]
        if char == '?' or ord(char) < 32 or ord(char) == 127:
            return ''
        elif char == '"':
            return '' if restricted else '\''
        elif char == ':':
            return '_-' if restricted else ' -'
        elif char in '\\/|*<>':
            return '_'
        if restricted and (char in '!&\'()[]{}$;`^,#' or char.isspace()):
            return '_'
        if restricted and ord(char) > 127:
            return '_'
        return char

    # Handle timestamps
    s = re.sub(r'[0-9]+(?::[0-9]+)+',
               lambda m: m.group(0).replace(':', '_'), s)
    result = ''.join(map(replace_insane, s))
    if not is_id:
        while '__' in result:
            result = result.replace('__', '_')
        result = result.strip('_')
        # Common case of "Foreign band name - English song title"
        if restricted and result.startswith('-_'):
            result = result[2:]
        if result.startswith('-'):
            result = '_' + result[len('-'):]
        result = result.lstrip('.')
        if not result:
            result = '_'
    return result


def download_file(url, file_out, title, i, total):
    """
    Загрузка файла
    Возвращает: код ошибки
    0 - файл успешно загружен
    1 - файл уже существует
    2 - ошибка загрузки файла
    28 - недостаточно место для сохранения файла

    :param url: string
    :param file_out: string
    :param title: string
    :param i: int
    :param total: int

    :return: int
    """

    global S_USER_AGENT
    headers = {
        'User-Agent': S_USER_AGENT
    }
    print(f'Имя      : [ {i}/{total} ] {FLC}{title}{FR}')
    try:
        r = requests.get(url, stream=True, headers=headers, verify=False)

        if r.status_code < 200 or r.status_code > 299:
            print(f'Статус   : [ {FLM}Error{FR} ]\n'
                  f'Cсылка   : {FLW}{url}{FR}\n'
                  f'Файл     : {FLW}{file_out}{FR}\n'
                  f'Код      : {FLM}{r.status_code}')
            exit(-1)

        total_length = int(r.headers.get('content-length'))
        # Проверка на наличие уже скаченного файла
        if Path(file_out).is_file():
            file_size = os.stat(Path(file_out)).st_size
            if file_size == int(total_length):
                print(f'Статус   : [ {FLG}Уже существует ]\n')
                return 1

        # Скачивание файла
        def_chunk_size = min(total_length, 8192)
        # def_chunk_size = min(total_length, 4096)
        with open(file_out, "wb") as f:
            for chunk in bar(r.iter_content(chunk_size=def_chunk_size), label="Загружено: ",
                             filled_char='#',
                             expected_size=(total_length / def_chunk_size) + 1,
                             total_length=total_length):
                if chunk:
                    f.write(chunk)
                    f.flush()

        print(f'Статус   : [ {FLG}Ok{FR} ]\n')
        return 0

    except Exception as e:
        print(f'Статус   : [ {FLM}Error{FR} ]\n'
              f'Cсылка   : {FLW}{url}{FR}\n'
              f'Файл     : {FLW}{file_out}{FR}\n'
              f'Код      : {FLM}{e}\n')
        if '[Errno 28]' in str(e):  # [Errno 28] No space left on device
            return 28
        else:
            return 2


def process_cli():
    """
    parses the CLI arguments and returns a domain or
        a file with a list of domains etc.
    :return: dict
    """
    parser = argparse.ArgumentParser(
        description="""Get Courses from coursehunters.net
        A simple python script for download the courses from coursehunters.net.
        """,
        usage='%(prog)s [-h][-v][-nb] -u URL [-o DIR]',
        epilog="(c) AK545 (Andrey Klimov) 2019, e-mail: ak545@mail.ru",
        add_help=False
    )
    parent_group = parser.add_argument_group(
        title="Options"
    )
    parent_group.add_argument(
        "-h",
        "--help",
        action="help",
        help="Help"
    )
    parent_group.add_argument(
        "-v",
        "--version",
        action="version",
        help="Display the version number",
        version="%(prog)s version: {}".format(__version__)
    )
    parent_group.add_argument(
        "-u",
        "--url",
        help="URL of the Course (default is None)",
        metavar="URL"
        # required=True
    )
    parent_group.add_argument(
        "-o",
        "--out",
        help="Download dir for the Course (default is None)",
        metavar="DIR"
    )
    parent_group.add_argument(
        "-nb",
        "--no-banner",
        action="store_true",
        default=False,
        help="Do not print banner (default is False)"
    )
    return parser


def print_namespase():
    """
    Print preset options to console
    :return: None
    """
    global NAMESPACE
    print(
        f"\tPreset options\n"
        f"\t-------------------------\n"
        f"\tUrl                      : {NAMESPACE.url}\n"
        f"\tOut Dir                  : {NAMESPACE.out}\n"
        f"\tPrint banner             : {NAMESPACE.no_banner}\n"
        f"\t-------------------------"
    )


def main():
    """
    Main function
    :return: None
    """
    global NAMESPACE

    if NAMESPACE.out:
        # Создание папки для сохранения видео и материалов курса
        try:
            Path(NAMESPACE.out).mkdir(parents=True, exist_ok=True)
        except:
            print(f'Ошибка создания папки:\n{FLY}{NAMESPACE.out}')
            print(f'Проверьте корректность задания параметров.')
            print(f'Не добавляйте в конце параметра обратный слеш "{FLY}\\"')
            sys.exit(-1)
    else:
        NAMESPACE.out = os.getcwd()

    if NAMESPACE.url:
        lng, title_course, title_description, data = get_videos(NAMESPACE.url)
        if title_course != "":
            print(f'Курс     : [ {FLC}{title_course}{FR} ]')
            print()
            title_course = sanitize_filename(title_course)
            NAMESPACE.out = NAMESPACE.out + SEP + '( ' + lng + ' ) ' + title_course
            # Создание папки для сохранения видео и материалов курса
            try:
                Path(NAMESPACE.out).mkdir(parents=True, exist_ok=True)
            except:
                print(f'Ошибка создания папки:\n{FLY}{NAMESPACE.out}')
                print(f'Проверьте корректность задания параметров.')
                print(f'Не добавляйте в конце параметра обратный слеш "{FLY}\\"')
                sys.exit(-1)

        if title_description != "":
            filename = NAMESPACE.out + SEP + "description.txt"
            with open(filename, "w+", encoding="utf-8", newline="\n") as f:
                f.write(title_description)

        data_len = len(data)
        for i, item in enumerate(data, start=1):
            url = str(item.get('link')).strip()
            f = str(item.get('link')).strip().split('/')[-1]
            f = sanitize_filename(f)
            title = str(item.get('title')).strip()
            title = sanitize_filename(title)
            file = os.path.join(str(NAMESPACE.out), str(i) + '. ' + title + ' - ' + f)

            ret = download_file(url, file, title, i, data_len)
            if ret == 28:  # No space left on device
                break
        print()
        print(f'{FLW}Завершена загрузка курса{FR}')
        print()


if __name__ == "__main__":
    print(f"{SR}")

    # Parsing command line
    parser = process_cli()
    NAMESPACE = parser.parse_args(sys.argv[1:])
    if not NAMESPACE.url:
        print(f'{FLM}Error! The following arguments are required: {FLY}-u{FR} / {FLY}--url')
        parser.print_help()
    if not NAMESPACE.no_banner:
        if platform.platform().startswith('Windows'):
            home_path = os.path.join(os.getenv('HOMEDRIVE'),
                                     os.getenv('HOMEPATH'))
        else:
            home_path = os.path.join(os.getenv('HOME'))
        print(
            f"\tPython  : {FLC}{sys.version}{FR}\n"
            f"\tNode    : {FLC}{platform.node()}{FR}\n"
            f"\tHome    : {FLC}{home_path}{FR}\n"
            f"\tOS      : {FLC}{platform.system()}{FR}\n"
            f"\tRelease : {FLC}{platform.release()}{FR}\n"
            f"\tVersion : {FLC}{platform.version()}{FR}\n"
            f"\tArch    : {FLC}{platform.machine()}{FR}\n"
            f"\tCPU     : {FLC}{platform.processor()}{FR}"
        )
    rc = 0
    try:
        main()
    except Exception as e:
        print('Error: %s' % e, file=sys.stderr)
    sys.exit(rc)
