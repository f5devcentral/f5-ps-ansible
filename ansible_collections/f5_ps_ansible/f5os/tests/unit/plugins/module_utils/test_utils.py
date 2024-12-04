# -*- coding: utf-8 -*-
import sys

import pytest

from ansible_collections.f5_ps_ansible.f5os.plugins.module_utils.utils import (
    changes_add_deep_diff,
    dicts_equal,
    format_bool_values,
    number_values_to_string,
    recurse_remove_keys,
    remove_state_property,
)

try:
    import deepdiff

    DEEPDIFF_INSTALLED = True
except ImportError:
    DEEPDIFF_INSTALLED = False


class Test_recurse_remove_keys:
    def test_remove_keys(self):
        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        keys = ["key1", "key2"]
        expected = {
            "key3": "value3",
        }
        assert recurse_remove_keys(data, keys) == expected

    def test_remove_keys_not_present(self):
        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        keys = ["key4", "key5"]
        expected = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }
        assert recurse_remove_keys(data, keys) == expected

    def test_nested_remove_keys(self):
        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": {
                "key4": "value4",
                "key5": "value5",
            },
        }
        keys = ["key4"]
        expected = {
            "key1": "value1",
            "key2": "value2",
            "key3": {
                "key5": "value5",
            },
        }
        assert recurse_remove_keys(data, keys) == expected


class Test_number_values_to_string:
    d_1 = {
        "k": 1,
        "d": {"k": 1},
        "l": ["1", 2.0, 3],
        "l2": ["1", {"k": 1}, [1, 2.0, "3"]],
        "s": "str",
        "n": "9",
    }
    d_2 = {
        "k": "1",
        "d": {"k": "1"},
        "l": ["1", "2.0", "3"],
        "l2": ["1", {"k": "1"}, ["1", "2.0", "3"]],
        "s": "str",
        "n": "9",
    }
    d1 = {"d": d_1, "l": [d_1]}
    d2 = {"d": d_2, "l": [d_2]}

    def test_1(self):
        # copy of d1 matches d2
        assert number_values_to_string(self.d1) == self.d2
        # type of d1["d"]["k"] is int (no change!)
        assert type(self.d1["d"]["k"]) == int

    def test_2(self):
        assert number_values_to_string(self.d_1) == self.d_2
        # type of d1["d"]["k"] is int (no change!)
        assert type(self.d_1["d"]["k"]) == int


class Test_dicts_equal:
    _one_num_int = {"1": 1}
    _one_str_int = {"1": "1"}
    _one_num_flt = {"1": 1.0}
    _one_str_flt = {"1": "1.0"}

    _list_order_a = {"k": [_one_num_int, _one_str_int, "x", 1, "y"]}
    _list_order_b = {"k": [_one_str_int, _one_num_int, "y", "x", "1"]}

    def test_simple_int_str(self):
        d1 = {"k": self._one_num_int}
        d2 = {"k": self._one_str_int}
        assert dicts_equal(d1, d2) == True

    def test_simple_float_str(self):
        d1 = {"k": self._one_num_flt}
        d2 = {"k": self._one_str_flt}
        assert dicts_equal(d1, d2) == True

    def test_list_order(self):
        assert dicts_equal(self._list_order_a, self._list_order_b) == True

    def test_advanced_12(self):
        d1 = {"k": {"l": ["a", 1.0, {"a": self._list_order_a}]}}
        d2 = {"k": {"l": ["a", "1.0", {"a": self._list_order_b}]}}
        assert dicts_equal(d1, d2) == True

    def test_advanced_21(self):
        d1 = {"k": {"l": ["a", 1.0, {"a": self._list_order_a}]}}
        d2 = {"k": {"l": ["a", "1.0", {"a": self._list_order_b}]}}
        assert dicts_equal(d2, d1) == True

    def test_not_equal_advanced(self):
        d1 = {"k": {"l": ["a", 1.0, {"a": ["1", {"a": 1}]}]}}
        d2 = {"k": {"l": ["a", "1.0", {"a": ["1", {"a": "2"}]}]}}
        assert dicts_equal(d2, d1) == False

    @pytest.mark.parametrize(
        "d1, d2, result",
        [
            ({1: 2}, {1: 2}, True),  # equal
            ({1: 2}, {1: "2"}, True),  # equal
            ({1: 2}, {"1": 2}, False),  # type of keys different
            ({1: 2}, {1: "1"}, False),
            ({1: 2}, {1: 1}, False),
            ({}, {}, True),
        ],
    )
    def test_comparisons(self, d1, d2, result):
        assert dicts_equal(d1, d2) == result

    @pytest.mark.parametrize(
        "d1, d2, result",
        [
            ([1, 2], {1: 2}, False),
            (None, {1: 2}, False),
            ("", {1: 2}, False),
            (0, {1: 2}, False),
        ],
    )
    def test_types(self, d1, d2, result):
        assert dicts_equal(d1, d2) == result

    @pytest.mark.parametrize(
        "d1, d2, result",
        [
            (
                {
                    "one": [
                        {
                            "t": "1",
                            "1": True,
                            "k": "a",
                        },
                        {"t": "2", "l": ["a", 2, "c"]},
                        [1, 2, 3, False, True],
                    ],
                    "list": [
                        1,
                        2,
                        3,
                    ],
                },
                {
                    "one": [
                        {"t": "1", "k": "a", "1": True},
                        [1, 3, 2, True, False],
                        {"t": "2", "l": ["a", 2, "c"]},
                    ],
                    "list": [
                        2,
                        1,
                        3,
                    ],
                },
                True,
            ),
            (
                {
                    "one": [
                        {
                            "t": "XXX",
                            "1": True,
                            "k": "a",
                        },
                        {"t": "2", "l": ["a", 2, "c"]},
                        [1, 2, 3, False, True],
                    ],
                    "list": [
                        1,
                        2,
                        3,
                    ],
                },
                {
                    "one": [
                        {"t": "1", "k": "a", "1": True},
                        [1, 3, 2, True, False],
                        {"t": "2", "l": ["a", 2, "c"]},
                    ],
                    "list": [
                        2,
                        1,
                        3,
                    ],
                },
                False,
            ),
            (
                {
                    "one": [
                        {
                            "t": "1",
                            "1": True,
                            "k": "a",
                        },
                        {"t": "2", "l": ["a", 2, "c"]},
                        [1, 2, 3, False, True],
                    ],
                    "list": [
                        1,
                        2,
                        3,
                    ],
                },
                {
                    "one": [
                        {"t": "1", "k": "a", "1": False},
                        [1, 3, 2, True, False],
                        {"t": "2", "l": ["a", 2, "c"]},
                    ],
                    "list": [
                        2,
                        1,
                        3,
                    ],
                },
                False,
            ),
            (
                {
                    "one": [
                        {
                            "t": "1",
                            "1": True,
                            "k": "a",
                        },
                        {"t": "2", "l": ["a", 2, "c"]},
                        [1, 2, 3, False, True],
                    ],
                    "list": [
                        1,
                        2,
                        3,
                    ],
                },
                {
                    "one": [
                        {"t": "1", "k": "a", "1": True},
                        [1, 99999, 2, True, False],
                        {"t": "2", "l": ["a", 2, "c"]},
                    ],
                    "list": [
                        2,
                        1,
                        3,
                    ],
                },
                False,
            ),
            (
                {
                    "one": [
                        {
                            "t": "1",
                            "1": True,
                            "k": "a",
                        },
                        {"t": "2", "l": ["a", 2, "XXXX"]},
                        [1, 2, 3, False, True],
                    ],
                    "list": [
                        1,
                        2,
                        3,
                    ],
                },
                {
                    "one": [
                        {"t": "1", "k": "a", "1": True},
                        [1, 3, 2, True, False],
                        {"t": "2", "l": ["a", 2, "c"]},
                    ],
                    "list": [
                        2,
                        1,
                        3,
                    ],
                },
                False,
            ),
            (
                {
                    "one": [
                        {
                            "t": "1",
                            "1": True,
                            "k": "a",
                        },
                        {"t": "2", "l": ["a", 2, "c"]},
                        [1, 2, 3, False, True],
                    ],
                    "list": [
                        1,
                        2,
                        3,
                    ],
                },
                {
                    "one": [
                        {"t": "1", "k": "a", "1": True},
                        [1, 3, 2, True, False],
                        {"t": "2", "l": ["XXXX", 2, "c"]},
                    ],
                    "list": [
                        2,
                        1,
                        3,
                    ],
                },
                False,
            ),
        ],
    )
    def test_deep(self, d1, d2, result):
        assert dicts_equal(d1, d2) == result

    def test_mutation(self):
        """must not mutate input dictionaries"""
        d1 = {"list": [{"key1": "IGNORE!", "key2": 2}]}
        d2 = {"list": [{"key1": 1, "key2": 2}]}

        assert dicts_equal(d1, d2, remove_keys=["key1"]) == True
        assert d2 == {"list": [{"key1": 1, "key2": 2}]}


class Test_remove_state_property:
    TEST_NTP = [
        {
            "openconfig-system:servers": {
                "server": [
                    {
                        "address": "192.0.2.123",
                        "config": {
                            "address": "192.0.2.123",
                            "port": 123,
                            "version": 4,
                            "association-type": "SERVER",
                            "iburst": False,
                            "prefer": False,
                        },
                    }
                ]
            }
        },
        {
            "openconfig-system:servers": {
                "server": [
                    {
                        "address": "192.0.2.123",
                        "config": {
                            "address": "192.0.2.123",
                            "port": 123,
                            "version": 4,
                            "association-type": "SERVER",
                            "iburst": False,
                            "prefer": False,
                        },
                        "state": {
                            "address": "192.0.2.123",
                            "port": 123,
                            "version": 4,
                            "association-type": "SERVER",
                            "iburst": False,
                            "prefer": False,
                            "f5-openconfig-system-ntp:authenticated": False,
                        },
                    }
                ]
            }
        },
    ]

    def test_remove_state_property(self):
        testdata = {"key": {"list": [{"config": "entry1", "state": "entry1"}]}}
        expected = {"key": {"list": [{"config": "entry1"}]}}

        assert remove_state_property(testdata) == expected

    def test_leave_other_types_untouched(self):
        testdata = test_data = {
            "key": [{"state": {"k": "v"}, "config": {"k": "v"}}],
            "types": [{"state": {"k": "v"}, "config": {"k": "v"}}, "str", [1]],
        }
        expected = {
            "key": [{"config": {"k": "v"}}],
            "types": [{"config": {"k": "v"}}, "str", [1]],
        }

        assert remove_state_property(testdata) == expected

    def test_keep_state_property_without_config_present(self):
        testdata = {
            "key": {
                "list": [{"config": "entry1", "state": "entry1"}, {"state": "entry2"}]
            }
        }
        expected = {"key": {"list": [{"config": "entry1"}, {"state": "entry2"}]}}

        assert remove_state_property(testdata) == expected

    def test_keep_state_property_without_config_present_contains(self):
        testdata = {
            "key": {
                "list": [
                    {"prop1:config": "entry1", "prop1:state": "entry1"},
                    {"prop2:state": "entry2"},
                ]
            }
        }
        expected = {
            "key": {"list": [{"prop1:config": "entry1"}, {"prop2:state": "entry2"}]}
        }

        assert remove_state_property(testdata) == expected

    def test_keep_state_property_without_config_present_contains_exact(self):
        testdata = {
            "key": {
                "list": [
                    {"propX:config": "entry1", "propX:state": "entry1"},
                    {"propY:config": "entry2", "propZ:state": "entry2"},
                ]
            }
        }
        expected = {
            "key": {
                "list": [
                    {"propX:config": "entry1"},
                    {"propY:config": "entry2", "propZ:state": "entry2"},
                ]
            }
        }

        assert remove_state_property(testdata) == expected

    def test_ntp(self):
        assert remove_state_property(self.TEST_NTP[1]) == self.TEST_NTP[0]


class Test_changes_add_deep_diff:
    def test_no_diff(self):
        changes = {"before": {}, "after": {}}
        changes_add_deep_diff(changes)
        assert "diff" not in changes

    @pytest.mark.skipif(not DEEPDIFF_INSTALLED, reason="deepdiff not installed")
    def test_diff(self):
        changes = {"before": {"a": 1}, "after": {"a": 2}}
        changes_add_deep_diff(changes)
        assert "diff" in changes
        assert changes["diff"] == {
            "values_changed": {"root['a']": {"new_value": 2, "old_value": 1}}
        }

    def test_no_deepdiff(self):
        changes = {"before": {"a": 1}, "after": {"a": 2}}
        # mock ImportError
        sys.modules["deepdiff"] = None
        changes_add_deep_diff(changes)
        assert "diff" not in changes


class Test_format_bool_values:
    def test_format_bool_values(self):
        test_data = {
            "k1": [
                "true",
                "True",
                "false",
                "False",
                "str",
                1,
                1.0,
                True,
                False,
                {"True": "true"},
            ],
            "k2": {"k1": "true", "k2": "True", "k3": "false", "k4": "False"},
        }
        expected_data = {
            "k1": [
                True,
                True,
                False,
                False,
                "str",
                1,
                1.0,
                True,
                False,
                {"True": True},
            ],
            "k2": {"k1": True, "k2": True, "k3": False, "k4": False},
        }

        assert format_bool_values(test_data) == expected_data
