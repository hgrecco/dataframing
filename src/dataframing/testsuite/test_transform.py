from typing import Protocol

import dataframing as dfr


class Def1(Protocol):
    last_name: str
    first_name: str


class Def2(Protocol):
    full_name: str


class Def3(Protocol):
    value_len: str


class Def4(Def2, Protocol):
    inverted_full_name: str


class Def5(Def1, Def2, Protocol):
    pass


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


def test_inheritance():
    record: Def1 = dict(last_name="Cleese", first_name="John")

    with dfr.morph(Def1, Def4) as (transformer, source, target):
        target.full_name = dfr.wrap(
            "{}, {}".format, source.last_name, source.first_name
        )
        target.inverted_full_name = dfr.wrap(
            "{}, {}".format, source.first_name, source.last_name
        )

    assert transformer.transform_record(record) == dict(
        full_name="Cleese, John", inverted_full_name="John, Cleese"
    )


def test_constant():
    record: Def1 = dict(last_name="Cleese", first_name="John")

    with dfr.morph(Def1, Def3) as (transformer, source, target):
        target.value_len = "cheese"

    assert transformer.transform_record(record) == dict(value_len="cheese")


def test_copy1():
    record: Def1 = dict(last_name="Cleese", first_name="John")
    expected: Def5 = dict(
        last_name="Cleese",
        first_name="John",
        full_name="Cleese, John",
    )
    with dfr.morph(Def1, Def5) as (transformer, source, target):
        target.first_name = source.first_name
        target.last_name = source.last_name
        target.full_name = dfr.wrap(
            "{}, {}".format, source.last_name, source.first_name
        )
    assert transformer.transform_record(record) == expected


def test_copy2():
    record: Def1 = dict(last_name="Cleese", first_name="John")
    expected: Def5 = dict(
        last_name="Cleese",
        first_name="John",
        full_name="Cleese, John",
    )

    with dfr.morph(Def1, Def5) as (transformer, source, target):
        dfr.copy(source, target)
        target.full_name = dfr.wrap(
            "{}, {}".format, source.last_name, source.first_name
        )
    assert transformer.transform_record(record) == expected


def test_split_with_temporary():
    record: Def2 = dict(full_name="Cleese, John")

    with dfr.morph(Def2, Def1) as (transformer, source, target):
        tmp = dfr.wrap(splitter, source.full_name)
        target.last_name = tmp[0]
        target.first_name = tmp[1]

    out = {}
    expected_out = dict(last_name="Cleese", first_name="John")
    assert transformer.transform_record(record, out) == expected_out
    assert out == expected_out


def test_transform_collection_temp():
    records = [
        dict(full_name="Cleese, John"),
        dict(full_name="Gilliam, Terry"),
    ]
    expected: list[Def1] = [
        dict(last_name="Cleese", first_name="John"),
        dict(last_name="Gilliam", first_name="Terry"),
    ]

    with dfr.morph(Def2, Def1) as (transformer, source, target):
        tmp = dfr.wrap(splitter, source.full_name)
        target.first_name = tmp[1]
        target.last_name = tmp[0]

    assert transformer.transform_collection(records) == expected

    assert transformer.transform_collection(records, max_workers=2) == expected
