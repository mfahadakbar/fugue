from typing import Any, Dict, Iterable, List

from fugue.dataframe import ArrayDataFrame
from fugue.exceptions import FugueInterfacelessError
from fugue.extensions.transformer import (
    Transformer,
    _to_output_transformer,
    output_transformer,
)
from fugue.extensions.transformer.constants import OUTPUT_TRANSFORMER_DUMMY_SCHEMA
from pytest import raises
from triad.collections.schema import Schema
from triad.utils.hash import to_uuid


def test_transformer():
    assert isinstance(t1, Transformer)
    assert t1.get_output_schema(None) == OUTPUT_TRANSFORMER_DUMMY_SCHEMA


def test__to_output_transformer():
    a = _to_output_transformer(MockTransformer)
    assert isinstance(a, MockTransformer)
    b = _to_output_transformer("MockTransformer")
    assert isinstance(b, MockTransformer)

    a = _to_output_transformer(t1)
    assert isinstance(a, Transformer)
    a._x = 1
    # every parse should produce a different transformer even the input is
    # a transformer instance
    b = _to_output_transformer(t1)
    assert isinstance(b, Transformer)
    assert "_x" not in b.__dict__
    c = _to_output_transformer("t1")
    assert isinstance(c, Transformer)
    assert "_x" not in c.__dict__
    c._x = 1
    d = _to_output_transformer("t1")
    assert isinstance(d, Transformer)
    assert "_x" not in d.__dict__
    e = _to_output_transformer("t4")
    assert isinstance(e, Transformer)
    f = _to_output_transformer("t5")
    assert isinstance(f, Transformer)


def test__to_output_transformer_determinism():
    a = _to_output_transformer(t1)
    b = _to_output_transformer(t1)
    c = _to_output_transformer("t1")
    assert a is not b
    assert to_uuid(a) == to_uuid(b)
    assert a is not c
    assert to_uuid(a) == to_uuid(c)

    a = _to_output_transformer(t4)
    b = _to_output_transformer("t4")
    assert a is not b
    assert to_uuid(a) == to_uuid(b)

    a = _to_output_transformer(MockTransformer)
    b = _to_output_transformer("MockTransformer")
    assert a is not b
    assert to_uuid(a) == to_uuid(b)


def test_to_output_transformer_validation():
    @output_transformer(input_has=" a , b ")
    def tv1(df: Iterable[Dict[str, Any]]) -> None:
        pass

    # input_has: a , b
    def tv2(df: Iterable[Dict[str, Any]]) -> None:
        pass

    class MockTransformerV(Transformer):
        @property
        def validation_rules(self):
            return {"input_is": "a:int,b:int"}

        def get_output_schema(self, df):
            pass

        def transform(self, df):
            pass

    a = _to_output_transformer(tv1, None)
    assert {"input_has": ["a", "b"]} == a.validation_rules
    b = _to_output_transformer(tv2, None)
    assert {"input_has": ["a", "b"]} == b.validation_rules
    c = _to_output_transformer(MockTransformerV)
    assert {"input_is": "a:int,b:int"} == c.validation_rules


@output_transformer()
def t1(df: Iterable[Dict[str, Any]]) -> None:
    pass


def t4(df: Iterable[List[Any]]) -> None:
    pass


# schema: *,b:int
def t5(df: Iterable[Dict[str, Any]]) -> Iterable[Dict[str, Any]]:
    for r in df:
        r["b"] = 1
        yield r


class MockTransformer(Transformer):
    def get_output_schema(self, df):
        pass

    def transform(self, df):
        pass