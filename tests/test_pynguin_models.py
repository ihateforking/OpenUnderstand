"""Curated tests produced from a Pynguin run against ``oudb.models``.

The raw Pynguin output was reviewed before being committed.  The retained
cases exercise the model representations and Peewee's clone behavior with
deterministic, assertion-based checks.
"""

from openunderstand.oudb.models import EntityModel, KindModel, ProjectModel


def test_generated_kind_model_representation_and_reference_kind_flag():
    """Pynguin's representation case is retained with meaningful assertions."""
    kind = KindModel(_name="Java Call", is_ent_kind=False)

    assert str(kind) == "Java Call"
    assert repr(kind) == "Java Call"
    assert kind.is_ref_kind is True


def test_generated_entity_clone_preserves_identity_fields():
    """The generated clone case preserves the entity's identifying fields."""
    entity = EntityModel(_name="run", _longname="Caller.run()")

    clone = entity.clone()

    assert clone is not entity
    assert clone.__data__ == entity.__data__


def test_generated_project_model_representation():
    """Project model string and repr use the project name."""
    project = ProjectModel(name="demo", root=".", db_path="demo.oudb")

    assert str(project) == "demo"
    assert repr(project) == "demo"


def test_generated_entity_model_representation():
    """Entity model representations expose the expected name fields."""
    entity = EntityModel(_name="run", _longname="Caller.run()")

    assert str(entity) == "run"
    assert repr(entity) == "Caller.run()"
