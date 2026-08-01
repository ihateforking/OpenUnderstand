"""Smoke tests for the package-level testing infrastructure."""


def test_openunderstand_package_imports():
    """The installable OpenUnderstand package is importable."""
    import openunderstand

    assert openunderstand.__file__ is not None
