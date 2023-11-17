[![Latest Version](https://img.shields.io/pypi/v/dataframing.svg)](https://pypi.python.org/pypi/dataframing)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License](https://img.shields.io/pypi/l/dataframing.svg)](https://pypi.python.org/pypi/dataframing)
[![Python Versions](https://img.shields.io/pypi/pyversions/dataframing.svg)](https://pypi.python.org/pypi/dataframing)
[![CI](https://github.com/hgrecco/dataframing/workflows/CI/badge.svg)](https://github.com/hgrecco/dataframing/actions?query=workflow%3ACI)
[![LINTER](https://github.com/hgrecco/dataframing/workflows/Lint/badge.svg)](https://github.com/hgrecco/dataframing/actions?query=workflow%3ALint)
[![Coverage](https://coveralls.io/repos/github/hgrecco/dataframing/badge.svg?branch=master)](https://coveralls.io/github/hgrecco/dataframing?branch=master)

# Motivation

The `dataframing` package provides useful functions to use dataframes.

# Data transformation

The main goal is to allow

```python
>>> from dataframing import Transformer, use
>>>
>>> class Def1(Protocol):
...     last_name: str
...     first_name: str
>>>
>>> class Def2(Protocol):
...    full_name: str
>>>
>>> with Transformer.build(Def1, Def2) as (transformer, source, target):
...    target.full_name = use("{}, {}".format, source.last_name, source.first_name)
>>>
>>> row = dict(last_name="Grecco", first_name="Hernán")
>>> transformer.transform_record(row)
{"full_name": "Grecco, Hernán"}
```

and also to split:

```python
>>> with Transformer.build(Def2, Def1) as (transformer, source, target):
...    target.last_name, target.first_name = use(lambda s: s.split(","), source.full_name)
>>>
>>> row = dict(last_name="Grecco", first_name="Hernán")
>>> transformer.transform_record(row)
{"last_name": "Grecco", "first_name": "Hernán"}
```

But the cool thing is that you can

```python
>>> transformer.transform_collection(my_dataframe)
```

# Input/Output

You can also use it to save and load data.

```python
>>> from dataframing import load, save
>>> save(my_dataframe, "example.xlsx")
>>> df = load("example.xlsx")
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
>>> from dataframing import load_many, save_many
>>> save_many(dict(raw_data=raw_data, processed_data=processed_data), "example.xlsx")
>>> dfdict = load_many("example.xlsx")
```

in which the input and output are dictionaries that allows you to group into
a single excel file multiple dataframes.

# Installation

Just install it using:

```bash
pip install dataframing
```
