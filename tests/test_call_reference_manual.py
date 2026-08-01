"""Handcrafted tests for Java Call/Callby references and class structure."""

import pytest

from openunderstand.oudb.api import UnderstandError, create_db
from openunderstand.oudb.api import open as open_db
from openunderstand.oudb.models import EntityModel, KindModel, ReferenceModel


@pytest.fixture
def analysis_db(tmp_path):
    """Create a small deterministic database representing two Java files."""
    db_path = tmp_path / "manual.oudb"
    create_db(
        dbname=db_path.name,
        project_dir=str(tmp_path),
        db_path=str(tmp_path),
    )

    file_kind = KindModel.create(_name="Java File")
    class_kind = KindModel.create(_name="Java Class Type Public Member")
    method_kind = KindModel.create(_name="Java Method Public Member")
    unknown_class_kind = KindModel.create(_name="Java Unknown Class Type Member")
    call_kind = KindModel.create(_name="Java Call", is_ent_kind=False)
    callby_kind = KindModel.create(_name="Java Callby", is_ent_kind=False)
    call_kind._inv = callby_kind._id
    call_kind.save()
    callby_kind._inv = call_kind._id
    callby_kind.save()

    file_a = EntityModel.create(
        _kind=file_kind,
        _name="Caller.java",
        _longname=str(tmp_path / "Caller.java"),
        _contents="class Caller { void run() { Callee.work(); } }",
    )
    class_a = EntityModel.create(
        _kind=class_kind,
        _parent=file_a,
        _name="Caller",
        _longname="Caller",
    )
    caller = EntityModel.create(
        _kind=method_kind,
        _parent=class_a,
        _name="run",
        _longname="Caller.run()",
    )

    file_b = EntityModel.create(
        _kind=file_kind,
        _name="Callee.java",
        _longname=str(tmp_path / "Callee.java"),
        _contents="class Callee { static void work() {} }",
    )
    class_b = EntityModel.create(
        _kind=class_kind,
        _parent=file_b,
        _name="Callee",
        _longname="Callee",
    )
    callee = EntityModel.create(
        _kind=method_kind,
        _parent=class_b,
        _name="work",
        _longname="Callee.work()",
    )
    unknown = EntityModel.create(
        _kind=unknown_class_kind,
        _parent=file_a,
        _name="MissingType",
        _longname="MissingType",
    )

    ReferenceModel.create(
        _kind=call_kind,
        _file=file_a,
        _line=1,
        _column=31,
        _ent=callee,
        _scope=caller,
    )
    ReferenceModel.create(
        _kind=callby_kind,
        _file=file_a,
        _line=1,
        _column=31,
        _ent=caller,
        _scope=callee,
    )

    return open_db(str(db_path)), {
        "caller": caller,
        "callee": callee,
        "class_a": class_a,
        "class_b": class_b,
        "file_a": file_a,
        "file_b": file_b,
        "unknown": unknown,
    }


def test_normal_class_lookup_and_call(analysis_db):
    db, entities = analysis_db
    caller = db.ent_from_id(entities["caller"]._id)

    classes = {
        ent.longname()
        for ent in db.ents("Class")
        if "Unknown" not in ent.kindname()
    }
    calls = caller.refs("Call")

    assert classes == {"Caller", "Callee"}
    assert len(calls) == 1
    assert calls[0].ent().longname() == "Callee.work()"
    assert calls[0].scope().longname() == "Caller.run()"


def test_malformed_java_source_is_reported_without_crashing(tmp_path):
    from openunderstand.ounderstand.project import Project

    source = tmp_path / "Broken.java"
    source.write_text("class Broken { void f( {", encoding="utf-8")

    tree = Project().Parse(str(source))

    assert tree is not None


def test_empty_call_query_and_zero_column_edge_case(analysis_db):
    db, entities = analysis_db
    caller = db.ent_from_id(entities["caller"]._id)
    class_a = db.ent_from_id(entities["class_a"]._id)

    assert class_a.refs("Call") == []
    assert caller.refs("Call", unique=True)[0].column() == 31
    assert db.lookup("NoSuchClass", "Class") == []


def test_unknown_class_is_kept_as_an_explicit_entity(analysis_db):
    db, entities = analysis_db

    unknown = [ent for ent in db.ents("Unknown Class")]

    assert [ent.longname() for ent in unknown] == ["MissingType"]
    assert unknown[0].kind().check("unknown class")
    assert unknown[0].parent().longname() == entities["file_a"]._longname


def test_call_has_callby_inverse_and_reverse_scope(analysis_db):
    db, entities = analysis_db
    caller = db.ent_from_id(entities["caller"]._id)
    callee = db.ent_from_id(entities["callee"]._id)

    call = caller.refs("Call")[0]
    callby = callee.refs("Callby")[0]

    assert call.kind().inv().name() == "Java Callby"
    assert callby.kind().inv().name() == "Java Call"
    assert callby.ent().longname() == call.scope().longname()
    assert callby.scope().longname() == call.ent().longname()


def test_parent_child_relationship_survives_second_pass(analysis_db):
    db, entities = analysis_db

    first_pass = db.ent_from_id(entities["callee"]._id).parent()
    second_pass = db.ent_from_id(entities["callee"]._id).parent()

    assert first_pass.longname() == "Callee"
    assert second_pass.longname() == first_pass.longname()
    assert second_pass.parent().longname() == entities["file_b"]._longname


def test_entity_kind_rejects_inverse_lookup(analysis_db):
    db, entities = analysis_db
    class_a = db.ent_from_id(entities["class_a"]._id)

    with pytest.raises(UnderstandError):
        class_a.kind().inv()
