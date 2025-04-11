#!/usr/bin/env python

"""Use t-strings in log messages"""

import functools
import logging
from string import Formatter
from string.templatelib import Template, Interpolation


_FORMATTER = Formatter()


_class_cache = {}
def _add_mixin(type_):
    """Create a copy of the class with TLoggerMixin mixed into it"""
    if type_ not in _class_cache:
        _class_cache[type_] = type(type_.__name__, (TLoggerMixin,) + type_.__mro__, {})
    return _class_cache[type_]


def _template_to_msg_args(template: Template) -> tuple[str, dict]:
    """Format a t-string like an f-string

    Returns the formatted string and a dict of the raw values
    """
    parts = []
    data = {}
    for item in template:
        match item:
            case str() as s:
                parts.append(s)
            case Interpolation(value, expression, conversion, format_spec):
                data[expression] = value
                parts.append(
                    _FORMATTER.format_field(
                        _FORMATTER.convert_field(value, conversion),
                        format_spec
                    )
                )
    return "".join(parts), data


class TLoggerMixin:
    """Mixin class that overrides `makeRecord` to process t-strings

    If the original `makeRecord` implementation produces a `LogRecord` with a
    t-string `msg` attribute, it will:
     - format it like an f-string and extract the interpolated values
     - prepend the dict of interpolated values to `LogRecord.args`
     - patch `LogRecord.getMessage` so it returns the formatted string.

    The `msg` attribute will be left unmodified so that other
    `logging.Formatter`s can directly use the t-string if needed.
    """

    def makeRecord(self, *args, **kwargs):
        record = super().makeRecord(*args, **kwargs)
        if isinstance(record.msg, Template):
            msg, args = _template_to_msg_args(record.msg)
            # make getMessage just return the message
            record.getMessage = functools.partial(str, msg)
            record.args = (args, *record.args)
        return record


def apply_mixin(logger: logging.Logger):
    """Add t-string support to a logging.Logger instance"""
    if not isinstance(logger, TLoggerMixin):
        # Insert the TLoggerMixin into the mro of the returned logger
        logger.__class__ = _add_mixin(type(logger))
    return logger


def get_logger(name=None):
    """Get a logger instance that supports t-string formatting"""
    return apply_mixin(logging.getLogger(name))
