from typing import Protocol

import dataframing as dfr


class Def1(Protocol):
    last_name: str
    first_name: str


class Def2(Protocol):
    full_name: str


class Def3(Protocol):
    value_len: str


class AttrExample:
    def __init__(self, value) -> None:
        self.value = value

    @property
    def value_len(self):
        return len(self.value)


def splitter(s: str) -> tuple[str, str]:
    part1, part2 = s.split(",")
    return part1.strip(), part2.strip()


def test_join():
    record: Def1 = dict(last_name="Cleese", first_name="John")

    with dfr.morph(Def1, Def2) as (transformer, source, target):
        target.full_name = dfr.wrap(
            "{}, {}".format, source.last_name, source.first_name
        )

    assert transformer.transform_record(record) == dict(full_name="Cleese, John")


def test_join_wrap_appart():
    record: Def1 = dict(last_name="Cleese", first_name="John")

    fullnamer = dfr.wrap("{}, {}".format)
    with dfr.morph(Def1, Def2) as (transformer, source, target):
        target.full_name = fullnamer(source.last_name, source.first_name)

    assert transformer.transform_record(record) == dict(full_name="Cleese, John")


def test_join_getattr():
    record: Def1 = dict(last_name="Cleese", first_name="John")

    with dfr.morph(Def1, Def3) as (transformer, source, target):
        target.value_len = dfr.wrap(AttrExample, source.last_name).value_len

    assert transformer.transform_record(record) == dict(value_len=6)


def test_join_with_out():
    record: Def1 = dict(last_name="Cleese", first_name="John")

    with dfr.morph(Def1, Def2) as (transformer, source, target):
        target.full_name = dfr.wrap(
            "{}, {}".format, source.last_name, source.first_name
        )

    out = {}
    expected_out = dict(full_name="Cleese, John")
    assert transformer.transform_record(record, out) == expected_out
    assert out == expected_out


def test_split():
    record: Def2 = dict(full_name="Cleese, John")

    with dfr.morph(Def2, Def1) as (transformer, source, target):
        target.last_name, target.first_name = dfr.wrap(splitter, source.full_name)

    assert transformer.transform_record(record) == dict(
        last_name="Cleese", first_name="John"
    )


def test_split_with_out():
    record: Def2 = dict(full_name="Cleese, John")

    with dfr.morph(Def2, Def1) as (transformer, source, target):
        target.last_name, target.first_name = dfr.wrap(splitter, source.full_name)

    out = {}
    expected_out = dict(last_name="Cleese", first_name="John")
    assert transformer.transform_record(record, out) == expected_out
    assert out == expected_out


def test_transform_collection():
    collection: list[Def1] = [
        dict(last_name="Cleese", first_name="John"),
        dict(last_name="Gilliam", first_name="Terry"),
    ]

    with dfr.morph(Def1, Def2) as (transformer, source, target):
        target.full_name = dfr.wrap(
            "{}, {}".format, source.last_name, source.first_name
        )

    assert transformer.transform_collection(collection) == [
        dict(full_name="Cleese, John"),
        dict(full_name="Gilliam, Terry"),
    ]
