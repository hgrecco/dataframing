from typing import Protocol

from ..transform import Transformer, use


class Def1(Protocol):
    last_name: str
    first_name: str


class Def2(Protocol):
    full_name: str


def test_join():
    record: Def1 = dict(last_name="Grecco", first_name="Hernán")

    with Transformer.build(Def1, Def2) as (transformer, source, target):
        target.full_name = use("{}, {}".format, source.last_name, source.first_name)

    assert transformer.transform_record(record) == dict(
        full_name="Grecco, Hernán", last_name="Grecco", first_name="Hernán"
    )


def test_join_with_out():
    record: Def1 = dict(last_name="Grecco", first_name="Hernán")

    with Transformer.build(Def1, Def2) as (transformer, source, target):
        target.full_name = use("{}, {}".format, source.last_name, source.first_name)

    out = {}
    assert transformer.transform_record(record, out) == dict(full_name="Grecco, Hernán")
    assert out == dict(full_name="Grecco, Hernán")


def test_split():
    record: Def2 = dict(full_name="Grecco, Hernán")

    with Transformer.build(Def2, Def1) as (transformer, source, target):
        target.last_name, target.first_name = use(
            lambda s: s.split(","), source.full_name
        )

    assert transformer.transform_record(record) == dict(
        full_name="Grecco, Hernán", last_name="Grecco", first_name=" Hernán"
    )


def test_split_with_out():
    record: Def2 = dict(full_name="Grecco, Hernán")

    with Transformer.build(Def2, Def1) as (transformer, source, target):
        target.last_name, target.first_name = use(
            lambda s: s.split(","), source.full_name
        )

    out = {}
    assert transformer.transform_record(record, out) == dict(
        last_name="Grecco", first_name=" Hernán"
    )
    assert out == dict(last_name="Grecco", first_name=" Hernán")


def test_transform_collection():
    collection: list[Def1] = [
        dict(last_name="Grecco", first_name="Hernán"),
        dict(last_name="Perez", first_name="Juan"),
    ]

    with Transformer.build(Def1, Def2) as (transformer, source, target):
        target.full_name = use("{}, {}".format, source.last_name, source.first_name)

    assert transformer.transform_collection(collection) == [
        dict(full_name="Grecco, Hernán"),
        dict(full_name="Perez, Juan"),
    ]
