
import os
import sys
import shutil
import subprocess
from pathlib import Path
from textwrap import wrap
from platform import uname


class _NamePath:
    def __init__(self, name, path, authors=None):
        self.name = name
        self.path = path
        self.authors = authors


class Books:
    SPLIT_MARK = '__'
    TEXT_WRAP = 70

    XDG_OPEN = 'xdg-open'
    WSL_OPEN = 'wsl-open'

    def __init__(self, directory):
        self.directory = directory
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
        ext = {'.pdf', '.djvu', '.epub', '.ps'}
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
            try:
                val = input(_msg)
                if val == 'q':
                    return None
                elif val in _dict:
                    return val
            except KeyboardInterrupt:
                sys.exit(0)

    def key_not_found(self):
        _str = self.__str__()
        _msg = f'{_str}: wrong directory key "{self.key}", directory keys:'
        print(_msg)

    def search_term_no_match(self):
        _str = self.__str__()
        _msg = f'{_str}: found no match for "{self.search_term}", files found:'
        print(_msg)

    def _open(self, _file):
        def on_wsl():
            return "microsoft" in uname()[3].lower()

        def on_windows():
            return os.name == 'nt'

        if on_wsl():
            if shutil.which(self.WSL_OPEN) is None:
                raise OSError(f'not found executable {self.WSL_OPEN}')
            cmd = ' '.join([self.WSL_OPEN, str(_file)])
            subprocess.Popen(cmd, shell=True)
        elif on_windows():
            subprocess.Popen([str(_file)], shell=True)
        else:
            if shutil.which(self.XDG_OPEN) is None:
                raise OSError(f'not found executable {self.XDG_OPEN}')
            cmd = ' '.join([self.XDG_OPEN, str(_file)])
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


class Notes(Rtfm):
    def __str__(self):
        return 'notes'


if __name__ == '__main__':
    root = Path().home() / 'Documents' / 'books'
    Books(root).run()
