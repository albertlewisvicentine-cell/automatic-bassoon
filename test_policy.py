import pytest
from policy import ALL, LAYER, CompositePolicy, InvariantLayer


class AlwaysPass:
    def check(self, value):
        return True


class AlwaysFail:
    def check(self, value):
        return False


class PositivePolicy:
    def check(self, value):
        return value > 0


class EvenPolicy:
    def check(self, value):
        return value % 2 == 0


def is_positive(value):
    return value > 0


def is_even(value):
    return value % 2 == 0


def is_less_than_100(value):
    return value < 100


class TestCompositePolicy:
    def test_returns_composite_policy_instance(self):
        policy = ALL(AlwaysPass(), AlwaysPass())
        assert isinstance(policy, CompositePolicy)

    def test_stores_policies_as_list(self):
        p1, p2 = AlwaysPass(), AlwaysPass()
        policy = ALL(p1, p2)
        assert policy.policies == [p1, p2]

    def test_all_pass_returns_true(self):
        policy = ALL(AlwaysPass(), AlwaysPass())
        assert policy.check(42) is True

    def test_one_fail_returns_false(self):
        policy = ALL(AlwaysPass(), AlwaysFail())
        assert policy.check(42) is False

    def test_all_fail_returns_false(self):
        policy = ALL(AlwaysFail(), AlwaysFail())
        assert policy.check(42) is False

    def test_no_policies_returns_true(self):
        policy = ALL()
        assert policy.check(42) is True

    def test_single_policy(self):
        policy = ALL(PositivePolicy())
        assert policy.check(5) is True
        assert policy.check(-1) is False

    def test_multiple_real_policies(self):
        policy = ALL(PositivePolicy(), EvenPolicy())
        assert policy.check(4) is True
        assert policy.check(3) is False
        assert policy.check(-2) is False


class TestInvariantLayer:
    def test_returns_invariant_layer_instance(self):
        layer = LAYER("my_layer", is_positive)
        assert isinstance(layer, InvariantLayer)

    def test_stores_name(self):
        layer = LAYER("bounds", is_positive)
        assert layer.name == "bounds"

    def test_stores_rules_as_list(self):
        layer = LAYER("rules", is_positive, is_even)
        assert layer.rules == [is_positive, is_even]

    def test_all_rules_pass_returns_true(self):
        layer = LAYER("checks", is_positive, is_even)
        assert layer.check(4) is True

    def test_one_rule_fails_returns_false(self):
        layer = LAYER("checks", is_positive, is_even)
        assert layer.check(3) is False

    def test_all_rules_fail_returns_false(self):
        layer = LAYER("checks", is_positive, is_even)
        assert layer.check(-3) is False

    def test_no_rules_returns_true(self):
        layer = LAYER("empty")
        assert layer.check(0) is True

    def test_multiple_rules(self):
        layer = LAYER("range", is_positive, is_even, is_less_than_100)
        assert layer.check(50) is True
        assert layer.check(101) is False
        assert layer.check(-2) is False
        assert layer.check(51) is False
