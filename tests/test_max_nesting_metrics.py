"""Focused tests for the MaxNesting metric used by mutation analysis."""

import pytest

from openunderstand.metrics.max_nesting import MaxNesting


def test_max_nesting_starts_empty():
    metric = MaxNesting()

    assert metric.stack == []
    assert metric.max_nesting == 0
    assert metric.is_in_else_if is False
    assert metric.number_of_else_if == 0


def test_push_tracks_current_depth_and_maximum_depth():
    metric = MaxNesting()

    metric.push_to_stack()
    metric.push_to_stack()
    metric.pop_from_stack()
    metric.push_to_stack()

    assert metric.stack == [0, 0]
    assert metric.max_nesting == 2


def test_maximum_depth_is_not_reduced_after_unwinding():
    metric = MaxNesting()

    for _ in range(3):
        metric.push_to_stack()
    for _ in range(3):
        metric.pop_from_stack()

    assert metric.stack == []
    assert metric.max_nesting == 3


@pytest.mark.parametrize(
    "enter_method, exit_method",
    [
        ("enterStatement2", "exitStatement2"),
        ("enterStatement3", "exitStatement3"),
        ("enterStatement4", "exitStatement4"),
        ("enterStatement5", "exitStatement5"),
        ("enterStatement8", "exitStatement8"),
    ],
)
def test_statement_listener_methods_push_and_pop(enter_method, exit_method):
    metric = MaxNesting()

    getattr(metric, enter_method)(None)
    assert len(metric.stack) == 1
    getattr(metric, exit_method)(None)
    assert metric.stack == []
