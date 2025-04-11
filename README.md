tstringlogger
=============

> [!WARNING]
> This is just an early prototype of an idea based on reading
> [PEP 750](https://peps.python.org/pep-0750/). I might rewrite it, abandon it, or completely delete
> it - do not rely on it in any way.

Adds support for using t-strings in log messages while preserving all interpolated values.

Usage example:
```python
from tstringlogger import get_logger

__log__ = get_logger(__name__)

test1, test2 = "A", "B"
__log__.info(t"{test1=}, {test2}")
```

In this example the message "test1=A, B" will be displayed as expected. Additionally, the
`LogRecord` that this call produced will have the data that was interpolated into the message
available as `record.args[0]`. In this example the data would be `{"test1": "A", "test2": "B"}`
