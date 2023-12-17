[![Latest Version](https://img.shields.io/pypi/v/dataframing.svg)](https://pypi.python.org/pypi/dataframing)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License](https://img.shields.io/pypi/l/dataframing.svg)](https://pypi.python.org/pypi/dataframing)
[![Python Versions](https://img.shields.io/pypi/pyversions/dataframing.svg)](https://pypi.python.org/pypi/dataframing)
[![CI](https://github.com/hgrecco/dataframing/workflows/CI/badge.svg)](https://github.com/hgrecco/dataframing/actions?query=workflow%3ACI)
[![LINTER](https://github.com/hgrecco/dataframing/workflows/Lint/badge.svg)](https://github.com/hgrecco/dataframing/actions?query=workflow%3ALint)
[![Coverage](https://coveralls.io/repos/github/hgrecco/dataframing/badge.svg?branch=main)](https://coveralls.io/github/hgrecco/dataframing?branch=main)

# Motivation

The `dataframing` package provides useful functions to use dataframes.

# Data transformation

The main goal is to allow you to transforme a dataframe structure into
another in a way which is easy to use, understand how structures are
connected and allows you to work with typing.

It assumes that you have a `TypedDict` defining your dataframes (which
by the way is a convenient thing to do!). For example:

```python
>>> from typing import TypedDict
>>> import dataframing as dfr
>>>
>>> class Original(TypedDict):
...     last_name: str
...     first_name: str
>>>
>>> class Modified(TypedDict):
...    full_name: str
```

Now we build a transformer that connects `Original` and `Modified`

```python
>>> @dfr.wrap
... def ori2mod(source: Original, target: Modified):
...    target["full_name"] = "{}, {}".format(source["last_name"], source["first_name"])
```

And now is ready to use!

```python
>>> row = dict(last_name="Cleese", first_name="John")
>>> ori2mod(row)
{'full_name': 'Cleese, John'}
```

Notice that we are demonstrating this with a dictionary but it will work this
with a dataframe row, or a full dataframe (or iterable of dicts).

```python
>>> import pandas as pd
>>> data = pd.DataFrame([
...   dict(last_name="Cleese", first_name="John"),
...   dict(last_name="Gilliam", first_name="Terry")
...   ])
>>> ori2mod.map(data)
        full_name
0    Cleese, John
1  Gilliam, Terry
```

To show case how to create two columns from one, we are going to build the reverse
transformer.

```python
>>> def splitter(s: str) -> tuple[str, str]:
...     part1, part2 = s.split(",")
...     return part1.strip(), part2.strip()
>>> @dfr.wrap
... def mod2ori(source: Modified, target: Original):
...    target["last_name"], target["first_name"] = splitter(source["full_name"])
>>>
>>> row = dict(full_name="Cleese, John")
>>> mod2ori(row)
{'last_name': 'Cleese', 'first_name': 'John'}
```

If you want to enrich a record

```python
>>> from typing import Protocol
>>> import dataframing as dfr
>>>
>>> class Original(TypedDict):
...     last_name: str
...     first_name: str
>>>
>>> class Complete(Original):
...     full_name: str
```

you can copy each attribute

```python
>>> @dfr.wrap
... def with_copy(source: Original, target: Complete):
...    target["last_name"] = source["last_name"]
...    target["first_name"] = source["first_name"]
...    target["full_name"] = fullnamer(source["last_name"], source["first_name"])
```

or all in one go:

```python
>>> @dfr.wrap
... def with_copy(source: Original, target: Complete):
...    # This will copy all attributes present in both definitions
...    dfr.copy(source, target)
...    target.full_name = fullnamer(source["last_name"], source["first_name"])
```

# Input/Output

You can also use it to save and load data.

```python
>>> dfr.save(my_dataframe, "example.xlsx") # doctest: +SKIP
>>> df = dfr.load("example.xlsx") # doctest: +SKIP
```

Why using this instead of the standard `pandas.to_excel`?
`save` does two extra things:

1. Stores the metadata stored in `my_dataframe.attrs` from/into another sheet.
1. Calculates a hash for the data and metadata and store it in the
   metadata sheet.

Loads will compare the data content with the stored hash. This behaviour is
useful for data validation, but can be disable with `use_hash` keyword argument.

Another useful pair of functions are `load_many`, `save_many`

```python
>>> dfr.save_many(dict(raw_data=raw_data, processed_data=processed_data), "example.xlsx") # doctest: +SKIP
>>> dfdict = dfr.load_many("example.xlsx") # doctest: +SKIP
```

in which the input and output are dictionaries that allows you to group into
a single excel file multiple dataframes.

# Installation

Just install it using:

```bash
pip install dataframing
```
