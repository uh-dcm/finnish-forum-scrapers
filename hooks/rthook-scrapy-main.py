# Runtime hook for PyInstaller-frozen Scrapy apps.
# I dont know why but this is necessary to make scrapy work with pyinstaller. It almost drove me insane.

import ast
import functools
import inspect
import re

import scrapy.utils.misc as scrapy_misc

_original = scrapy_misc.is_generator_with_return_value


def _is_generator_with_return_value(callable):
    cache = scrapy_misc._generator_callbacks_cache
    if callable in cache:
        return bool(cache[callable])

    if inspect.isgeneratorfunction(callable):
        func = callable
        while isinstance(func, functools.partial):
            func = func.func
        try:
            src = inspect.getsource(func)
        except (OSError, TypeError, IOError):
            cache[callable] = False
            return False

        pattern = re.compile(r"(^[\t ]+)")
        code = pattern.sub("", src)
        match = pattern.match(src)
        if match:
            code = re.sub(f"\n{match.group(0)}", "\n", code)

        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Return) and not _returns_none(node):
                cache[callable] = True
                return True

    cache[callable] = False
    return False


def _returns_none(node):
    value = node.value
    return value is None or (isinstance(value, ast.Constant) and value.value is None)


scrapy_misc.is_generator_with_return_value = _is_generator_with_return_value
