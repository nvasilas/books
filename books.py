
import os
import sys
import shutil
import subprocess
from pathlib import Path
from textwrap import wrap
from platform import uname


def on_wsl():
    return "microsoft" in uname()[3].lower()

def on_windows():
    return os.name == 'nt'


class Config:
    """Configuration class for Books.

    Attributes:

        Set the following:

        BOOKS_DICT (dict): Set this dict with the location of the books.
        PAPERS_DICT (dict): Set this dict with the location of the papers.
        RTFM_DICT (dict): Set this dict with the location of the rtfm.

        Do not set the following:

        _WSL (str): internal represantaion of dict key, do not edit.
        _WIN (str): internal represantaion of dict key, do not edit.
        _LINUX (str): internal represantaion of dict key, do not edit.

    """

    _WSL = 'wsl'
    _WIN = 'win'
    _LINUX = 'linux'

    BOOKS_DICT = {
        _WSL: '/home/nvasilas/docs/books',
        _LINUX: '/home/nikos/docs/books',
        # _WIN: '/home/nikos/docs/books',
    }

    PAPERS_DICT = {
        _WSL: '/home/nvasilas/docs/papers',
        _LINUX: '/home/nikos/docs/papers',
        # _WIN: '/home/nikos/docs/books',
    }

    RTFM_DICT = {
        _WSL: '/home/nvasilas/docs/rtfm',
        _LINUX: '/home/nikos/docs/rtfm',
        # _WIN: '/home/nikos/docs/books',
    }

    def __init__(self):
        _key = self._get_os()
        self.books_dir = self.BOOKS_DICT[_key]
        self.papers_dir = self.PAPERS_DICT[_key]
        self.rtfm_dir = self.RTFM_DICT[_key]

    def _get_os(self):
        if on_wsl():
            return self._WSL
        elif on_windows():
            return self._WIN
        else:
            return self._LINUX


class _NamePath:
    def __init__(self, name, path, authors=None):
        self.name = name
        self.path = path
        self.authors = authors


class Books:
    _XDG_OPEN = 'xdg-open'
    _WIN_PROJECT = 'C:\\Users\\nvasilas\\Documents\\MEGA'

    SPLIT_MARK = '__'
    TEXT_WRAP = 80

    def __init__(self, directory):
        self.directory = Path(directory)
        self.key = self.parse_key()
        self.search_term = self.parse_search_term()

        self._max_key = self._max_num = 0

    def __str__(self):
        return 'books'

    @staticmethod
    def parse_key():
        if len(sys.argv) >= 2:
            return sys.argv[1]
        else:
            return ''

    @staticmethod
    def parse_search_term():
        if len(sys.argv) >= 3:
            return sys.argv[2]
        else:
            return ''

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, d):
        if not Path.is_dir(d):
            raise FileNotFoundError(f'Directory {d} not valid')
        self._directory = d

    @staticmethod
    def is_dir_hidden(_dir):
        return str(_dir).startswith('.')

    def _dirs(self, _dir):
        return (i for i in _dir.iterdir()
                if i.is_dir()
                and not self.is_dir_hidden(i))

    @staticmethod
    def is_doc(f):
        ext = {'.pdf', '.djvu', '.epub'}
        return f.suffix.lower() in ext

    def _files(self, _dir, _search_term=''):
        return (i for i in _dir.iterdir()
                if i.is_file()
                and self.is_doc(i)
                and _search_term in str(i.stem).lower())

    def get_root_dict(self):
        _key_dict = {}
        for d in self._dirs(self.directory):
            try:
                _name, key = str(d).split(self.SPLIT_MARK)
            except ValueError:
                print(f'Fix directory {d} to match split pattern')
                continue
            self._max_key = max(self._max_key, len(key))
            name = Path(_name).stem.replace('_', ' ')
            path = d.absolute()
            _key_dict[key] = _NamePath(name=name, path=path)
        return _key_dict

    def get_folder_dict(self, _dir, _search_term=''):
        _folder_dict = {}
        for number, _file in enumerate(self._files(_dir, _search_term),
                                       start=1):
            try:
                _authors, _name = str(_file.stem).split(self.SPLIT_MARK)
            except ValueError:
                print(f'Fix file {_file} to match split pattern')
                _name = str(_file.stem)
                _authors = None
            self._max_num = max(self._max_num, len(str(number)))
            name = Path(_name).stem.replace('_', ' ')
            authors = _authors.split('_') if _authors else None
            path = _file.absolute()
            _folder_dict[str(number)] = _NamePath(name=name,
                                                  authors=authors,
                                                  path=path)
        return _folder_dict

    def _get_spaces_key(self, key):
        return abs(self._max_key - len(key)) + 1

    def _get_spaces_num(self, key):
        return abs(self._max_num - len(str(key))) + 1

    @staticmethod
    def _format_authors(authors):
        return (', '.join(authors) + '.'
                if authors else
                'NO_AUTHOR.')

    def print_root(self, root_dict):
        for k, v in root_dict.items():
            _spaces = ' '*self._get_spaces_key(k)
            print(f'({k}) {_spaces} {v.name}')

    def print_folder(self, _dict):
        for number, _namepath in _dict.items():
            _text = self._split_text(number, _namepath)
            _ = '\n'.join(_text)
            print(f'{_}')

    def _split_text(self, k, v):
        _first = True
        _text = []
        _spaces = ' '*self._get_spaces_num(k)
        authors = self._format_authors(v.authors)
        for i in wrap(f'{authors} {v.name}.',
                      self.TEXT_WRAP):
            if _first:
                _text.append(f'({k}){_spaces} {i}')
                _first = False
            else:
                _len = (len(str(k)) + 2)*' '
                _text.append(f'{_len}{_spaces} {i}')
        return _text

    def get_key(self, _dict):
        _str = self.__str__()
        _msg = f"{_str}: type {_str} (id) to preview | 'q' to return\n"
        while True:
            val = input(_msg)
            if val == 'q':
                return None
            elif val in _dict:
                return val

    def key_not_found(self):
        _str = self.__str__()
        _msg = f'{_str}: wrong directory key "{self.key}", directory keys:'
        print(_msg)

    def search_term_no_match(self):
        _str = self.__str__()
        _msg = f'{_str}: found no match for "{self.search_term}", files found:'
        print(_msg)

    @staticmethod
    def _to_win_format(f):
        if f.startswith('.'):
            f = f[1:]
        return f.replace(os.sep, '\\')

    def _open(self, _file):
        if on_wsl():
            _file = _file.relative_to(*_file.parts[:3])
            file_to_open = (self._WIN_PROJECT
                            + '\\'
                            + self._to_win_format(str(_file)))
            subprocess.Popen(["cmd.exe /c '%s'" % file_to_open], shell=True)
        elif os.name == 'nt':
            subprocess.Popen([str(_file)], shell=True)
        else:
            if shutil.which(self._XDG_OPEN) is None:
                raise OSError(f'not found executable {self._XDG_OPEN}')
            cmd = ' '.join([self._XDG_OPEN, str(_file)])
            subprocess.Popen(cmd, shell=True)

    def run(self):
        root_dict = self.get_root_dict()
        if self.key in root_dict:
            _dir = root_dict[self.key].path
            folder_dict = self.get_folder_dict(_dir, self.search_term)
            if not folder_dict:
                self.search_term_no_match()
                folder_dict = self.get_folder_dict(_dir)
            self.print_folder(folder_dict)
            key = self.get_key(folder_dict)
            if not key:
                return
            _file = folder_dict[key].path
            self._open(_file)
        else:
            self.key_not_found()
            self.print_root(root_dict)
            key = self.get_key(root_dict)
            if not key:
                return
            else:
                self.key = key
                self.run()


class Rtfm(Books):
    def __init__(self, directory):
        super().__init__(directory)
        self.search_term = self.key

    def __str__(self):
        return 'rtfm'

    def get_folder_dict(self, _dir, _search_term=''):
        _folder_dict = {}
        for number, _file in enumerate(self._files(_dir, _search_term),
                                       start=1):
            _name = str(_file.stem)
            self._max_num = max(self._max_num, len(str(number)))
            name = _name.replace('_', ' ')
            path = _file.absolute()
            _folder_dict[str(number)] = _NamePath(name=name,
                                                  path=path)
        return _folder_dict

    def _split_text(self, k, v):
        _first = True
        _text = []
        _spaces = ' '*self._get_spaces_num(k)
        for i in wrap(f'{v.name}', self.TEXT_WRAP):
            if _first:
                _text.append(f'({k}){_spaces} {i}')
                _first = False
            else:
                _len = (len(str(k)) + 2)*' '
                _text.append(f'{_len}{_spaces} {i}')
        return _text

    def print_folder(self, _dict):
        for number, _namepath in _dict.items():
            _text = self._split_text(number, _namepath)
            _ = '\n'.join(_text)
            print(f'{_}')

    def run(self):
        folder_dict = self.get_folder_dict(self.directory, self.search_term)
        if not folder_dict:
            self.search_term_no_match()
            folder_dict = self.get_folder_dict(self.directory)
        self.print_folder(folder_dict)
        key = self.get_key(folder_dict)
        if not key:
            return
        _file = folder_dict[key].path
        self._open(_file)


if __name__ == '__main__':
    if os.name == 'nt':
        b = r'C:\Users\nvasilas\Documents\MEGA\docs\books\topology__topo'
    else:
        b = '/home/nikos/docs/books'
        p = '/home/nikos/docs/papers'
        r = '/home/nikos/docs/rtfm'
    # Books(b).run()
    # Books(p).run()
    Rtfm(r).run()
