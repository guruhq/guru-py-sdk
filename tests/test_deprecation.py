"""Tests for guru_sdk._deprecation — deprecation decorator."""

import warnings

from guru_sdk._deprecation import deprecated


class TestDeprecated:
    """The @deprecated decorator emits DeprecationWarning with guidance."""

    def test_emits_deprecation_warning(self):
        @deprecated(removal_version="2.0", alternative="new_func()")
        def old_func():  # type: ignore[no-untyped-def]
            return 42

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_func()

        assert result == 42
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

    def test_warning_message_includes_version(self):
        @deprecated(removal_version="3.0", alternative="g.cards.get()")
        def get_card():  # type: ignore[no-untyped-def]
            return "card"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            get_card()

        msg = str(w[0].message)
        assert "3.0" in msg

    def test_warning_message_includes_alternative(self):
        @deprecated(removal_version="2.0", alternative="g.cards.get()")
        def get_card():  # type: ignore[no-untyped-def]
            return "card"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            get_card()

        msg = str(w[0].message)
        assert "g.cards.get()" in msg

    def test_warning_message_includes_function_name(self):
        @deprecated(removal_version="2.0", alternative="new_thing()")
        def old_thing():  # type: ignore[no-untyped-def]
            pass

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_thing()

        msg = str(w[0].message)
        assert "old_thing" in msg

    def test_preserves_function_name(self):
        @deprecated(removal_version="2.0", alternative="new()")
        def original_name():  # type: ignore[no-untyped-def]
            """Original docstring."""
            pass

        assert original_name.__name__ == "original_name"
        assert original_name.__doc__ == "Original docstring."

    def test_passes_through_args_and_kwargs(self):
        @deprecated(removal_version="2.0", alternative="add_v2()")
        def add(a, b, *, extra=0):  # type: ignore[no-untyped-def]
            return a + b + extra

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            assert add(1, 2, extra=10) == 13

    def test_works_on_methods(self):
        class MyClass:
            @deprecated(removal_version="2.0", alternative="self.new_method()")
            def old_method(self):  # type: ignore[no-untyped-def]
                return "old"

        obj = MyClass()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = obj.old_method()

        assert result == "old"
        assert len(w) == 1
        assert "MyClass.old_method" in str(w[0].message)
