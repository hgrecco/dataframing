from typing import TypedDict

import dataframing as dfr
import pandas as pd


class Def1(TypedDict):
    last_name: str
    first_name: str


class Def2(TypedDict):
    full_name: str


class Def3(TypedDict):
    value_len: str


class Def4(Def2):
    inverted_full_name: str


class Def5(Def1, Def2):
    pass


def splitter(s: str) -> tuple[str, str]:
    part1, part2 = s.split(",")
    return part1.strip(), part2.strip()


def fullnamer(source: Def1, target: Def2):
    target["full_name"] = "{}, {}".format(source["last_name"], source["first_name"])


def fullnamer2(source: Def1, target: Def4):
    target["full_name"] = "{}, {}".format(source["last_name"], source["first_name"])
    target["inverted_full_name"] = "{}, {}".format(
        source["first_name"], source["last_name"]
    )


wfullnamer = dfr.wrap(fullnamer)
wfullnamer2 = dfr.wrap(fullnamer2)


def test_join():
    record: Def1 = dict(last_name="Cleese", first_name="John")
    expected = dict(full_name="Cleese, John")

    assert wfullnamer(record) == expected


def test_transform_collection():
    records: list[Def1] = [
        dict(last_name="Cleese", first_name="John"),
        dict(last_name="Gilliam", first_name="Terry"),
    ]

    expected = [
        dict(full_name="Cleese, John"),
        dict(full_name="Gilliam, Terry"),
    ]

    assert list(map(wfullnamer, records)) == expected


def test_transform_dataframe():
    records: list[Def1] = pd.DataFrame(
        [
            dict(last_name="Cleese", first_name="John"),
            dict(last_name="Gilliam", first_name="Terry"),
        ]
    )

    expected = pd.DataFrame(
        [
            dict(full_name="Cleese, John"),
            dict(full_name="Gilliam, Terry"),
        ]
    )

    assert wfullnamer.map(records).equals(expected)
    assert wfullnamer.map(records, max_workers=2).equals(expected)


def test_inheritance():
    record: Def1 = dict(last_name="Cleese", first_name="John")
    expected = dict(full_name="Cleese, John", inverted_full_name="John, Cleese")

    assert wfullnamer2(record) == expected


def test_copy():
    record: Def1 = dict(last_name="Cleese", first_name="John")
    expected: Def5 = dict(
        last_name="Cleese",
        first_name="John",
        full_name="Cleese, John",
    )

    def transformer3(source: Def1, target: Def5):
        dfr.copy(source, target)
        target["full_name"] = "{}, {}".format(source["last_name"], source["first_name"])

    wtransformer3 = dfr.wrap(transformer3)

    assert wtransformer3(record) == expected
