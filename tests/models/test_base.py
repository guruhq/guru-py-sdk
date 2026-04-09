"""Tests for guru_sdk.models._base — GuruModel base class."""

import pydantic
import pytest
from pydantic import Field

from guru_sdk.models._base import GuruModel


class SampleModel(GuruModel):
    """A test model to verify GuruModel behavior."""

    id: str
    title: str = Field(alias="preferredPhrase")
    count: int = 0


class TestGuruModelExtraIgnore:
    """extra='ignore' means unknown fields are silently dropped."""

    def test_unknown_fields_ignored(self):
        data = {"id": "abc", "preferredPhrase": "Hello", "newField": "surprise"}
        model = SampleModel.model_validate(data)
        assert model.id == "abc"
        assert model.title == "Hello"
        assert not hasattr(model, "newField")

    def test_known_fields_preserved(self):
        data = {"id": "abc", "preferredPhrase": "Hello", "count": 5}
        model = SampleModel.model_validate(data)
        assert model.count == 5


class TestGuruModelPopulateByName:
    """populate_by_name=True means both alias and field name work."""

    def test_alias_works(self):
        model = SampleModel.model_validate({"id": "1", "preferredPhrase": "Title"})
        assert model.title == "Title"

    def test_field_name_works(self):
        model = SampleModel.model_validate({"id": "1", "title": "Title"})
        assert model.title == "Title"


class TestGuruModelFrozen:
    """frozen=True means models are immutable."""

    def test_cannot_set_attribute(self):
        model = SampleModel.model_validate({"id": "1", "preferredPhrase": "Hello"})
        with pytest.raises(pydantic.ValidationError):
            model.title = "New"  # type: ignore[misc]

    def test_model_is_hashable(self):
        """Frozen models are hashable — can be used in sets/dicts."""
        model = SampleModel.model_validate({"id": "1", "preferredPhrase": "Hello"})
        # Should not raise
        hash(model)


class TestGuruModelSerialization:
    """Models serialize to dicts with aliases by default."""

    def test_model_dump_uses_field_names(self):
        model = SampleModel.model_validate({"id": "1", "preferredPhrase": "Hello"})
        data = model.model_dump()
        assert data["title"] == "Hello"
        assert "preferredPhrase" not in data

    def test_model_dump_by_alias(self):
        model = SampleModel.model_validate({"id": "1", "preferredPhrase": "Hello"})
        data = model.model_dump(by_alias=True)
        assert data["preferredPhrase"] == "Hello"
