from random import randint

import pandas as pd
import pytest

from access.access import weights


class TestWeights:
    def setup_method(self):
        self.r_int = randint(2, 101)
        self.series = pd.Series(range(1, self.r_int))

    def apply_weight_fn(self, weight_fn):
        weight_vs = self.series.apply(weight_fn)
        w_applied = self.series * weight_vs

        return w_applied

    def test_step_fn_all_weight_zero_equals_zero_sum(self):
        weight_fn = weights.step_fn({self.r_int: 0})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        assert expected == 0

    def test_step_fn_all_weight_one_equals_self(self):
        weight_fn = weights.step_fn({self.r_int: 1})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        actual = self.series.sum()

        assert expected == actual

    def test_step_fn_all_weight_half_equals_half(self):
        weight_fn = weights.step_fn({self.r_int: 0.5})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        actual = self.series.sum() / 2

        assert expected == actual

    def test_step_fn_all_weight_two_equals_twice(self):
        weight_fn = weights.step_fn({self.r_int: 2})
        w_applied = self.apply_weight_fn(weight_fn)

        expected = w_applied.sum()
        actual = self.series.sum() * 2

        assert expected == actual

    def test_step_fn_negative_weight_raises_error(self):
        with pytest.raises(ValueError):
            weights.step_fn({self.r_int: -1})

    def test_step_fn_non_dict_input_raises_error(self):
        with pytest.raises(TypeError):
            weights.step_fn(1)

        with pytest.raises(TypeError):
            weights.step_fn("a")

        with pytest.raises(TypeError):
            weights.step_fn([])

        with pytest.raises(TypeError):
            weights.step_fn(1.0)

    def test_gaussian_width_zero_raises_error(self):
        with pytest.raises(ValueError):
            weight_fn = weights.gaussian(0)
            self.apply_weight_fn(weight_fn)

    def test_gaussian_weight_sigma_one(self):
        weight_fn = weights.gaussian(1)
        w_applied = self.apply_weight_fn(weight_fn)

        actual = w_applied.loc[0]

        assert pytest.approx(actual) == 0.6065306597

    def test_gaussian_weight_sigma_varied(self):
        sigma_vals = [-50, -2, 2, 50]
        expected_vals = [
            0.99980001,
            0.88249690,
            0.88249690,
            0.99980001,
        ]
        for sigma, expected in zip(sigma_vals, expected_vals, strict=False):
            weight_fn = weights.gaussian(sigma)
            w_applied = self.apply_weight_fn(weight_fn)
            print(w_applied.loc[0])
            actual = w_applied.loc[0]

            assert pytest.approx(actual) == expected

    def test_gravity_with_zero_alpha(self):
        rand_int = randint(1, 100)
        weight_fn = weights.gravity(scale=rand_int, alpha=0)
        w_applied = self.apply_weight_fn(weight_fn)

        actual = w_applied.loc[0]

        assert actual == 1
