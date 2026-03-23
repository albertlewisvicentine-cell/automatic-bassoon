import pytest

from policy import CompositePolicy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _AlwaysPass:
    """Leaf policy that always returns True."""

    def evaluate(self, context):
        return True


class _AlwaysFail:
    """Leaf policy that always returns False."""

    def evaluate(self, context):
        return False


class _ContextCheck:
    """Leaf policy that passes when *context* equals *expected*."""

    def __init__(self, expected):
        self.expected = expected

    def evaluate(self, context):
        return context == self.expected


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_empty_policy_passes():
    assert CompositePolicy([]).evaluate(None) is True


def test_single_pass_policy():
    assert CompositePolicy([_AlwaysPass()]).evaluate(None) is True


def test_single_fail_policy():
    assert CompositePolicy([_AlwaysFail()]).evaluate(None) is False


def test_all_pass_policies():
    policies = [_AlwaysPass(), _AlwaysPass(), _AlwaysPass()]
    assert CompositePolicy(policies).evaluate(None) is True


def test_one_fail_causes_failure():
    policies = [_AlwaysPass(), _AlwaysFail(), _AlwaysPass()]
    assert CompositePolicy(policies).evaluate(None) is False


# ---------------------------------------------------------------------------
# Nested CompositePolicy
# ---------------------------------------------------------------------------

def test_nested_single_level_all_pass():
    inner = CompositePolicy([_AlwaysPass(), _AlwaysPass()])
    outer = CompositePolicy([inner])
    assert outer.evaluate(None) is True


def test_nested_single_level_inner_fails():
    inner = CompositePolicy([_AlwaysPass(), _AlwaysFail()])
    outer = CompositePolicy([inner])
    assert outer.evaluate(None) is False


def test_nested_two_levels_all_pass():
    innermost = CompositePolicy([_AlwaysPass()])
    middle = CompositePolicy([innermost, _AlwaysPass()])
    outer = CompositePolicy([middle, _AlwaysPass()])
    assert outer.evaluate(None) is True


def test_nested_two_levels_deepest_fails():
    innermost = CompositePolicy([_AlwaysFail()])
    middle = CompositePolicy([innermost, _AlwaysPass()])
    outer = CompositePolicy([middle, _AlwaysPass()])
    assert outer.evaluate(None) is False


def test_triple_nested_composite_all_pass():
    """Mirrors the pattern in the problem statement."""
    level3 = CompositePolicy([_AlwaysPass(), _AlwaysPass()])
    level2 = CompositePolicy([level3, _AlwaysPass()])
    level1 = CompositePolicy([level2, _AlwaysPass()])
    assert level1.evaluate(None) is True


def test_triple_nested_composite_innermost_fails():
    level3 = CompositePolicy([_AlwaysFail()])
    level2 = CompositePolicy([level3])
    level1 = CompositePolicy([level2])
    assert level1.evaluate(None) is False


def test_deeply_nested_all_pass():
    """Ten levels of nesting, all passing."""
    policy = CompositePolicy([_AlwaysPass()])
    for _ in range(9):
        policy = CompositePolicy([policy, _AlwaysPass()])
    assert policy.evaluate(None) is True


def test_deeply_nested_one_fail_at_bottom():
    """Ten levels of nesting, innermost fails."""
    policy = CompositePolicy([_AlwaysFail()])
    for _ in range(9):
        policy = CompositePolicy([policy])
    assert policy.evaluate(None) is False


# ---------------------------------------------------------------------------
# Context is forwarded correctly
# ---------------------------------------------------------------------------

def test_context_forwarded_through_nesting():
    ctx = {"user": "admin"}
    inner = CompositePolicy([_ContextCheck(ctx)])
    outer = CompositePolicy([inner, _ContextCheck(ctx)])
    assert outer.evaluate(ctx) is True


def test_context_forwarded_wrong_value():
    ctx = {"user": "admin"}
    inner = CompositePolicy([_ContextCheck("wrong")])
    outer = CompositePolicy([inner])
    assert outer.evaluate(ctx) is False


# ---------------------------------------------------------------------------
# Constructor validation
# ---------------------------------------------------------------------------

def test_non_list_raises_type_error():
    with pytest.raises(TypeError):
        CompositePolicy((_AlwaysPass(),))


def test_none_policies_raises_type_error():
    with pytest.raises(TypeError):
        CompositePolicy(None)


def test_policy_without_evaluate_raises_type_error():
    with pytest.raises(TypeError):
        CompositePolicy([object()])


def test_second_policy_without_evaluate_raises_type_error():
    with pytest.raises(TypeError):
        CompositePolicy([_AlwaysPass(), "not-a-policy"])
