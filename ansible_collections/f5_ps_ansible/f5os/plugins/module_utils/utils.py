# -*- coding: utf-8 -*-
#
# Copyright: Simon Kowallik for the F5 DevCentral Community
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from copy import deepcopy

from ansible.module_utils.connection import Connection


class APIClient:
    """Class to interact with the BIG-IP F5OS API."""

    def __init__(self, module):
        """Initialize the API class."""
        self.module = module
        self.connection = Connection(module._socket_path)

    def call(self, method, uri, config=None):
        """query the API with a GET request."""
        if config is None:
            headers = {"Accept": "application/yang-data+json"}
        else:
            headers = {
                "Content-Type": "application/yang-data+json",
                "Accept": "application/yang-data+json",
            }
        response = self.connection.send_request(
            method=method,
            path=uri,
            headers=headers,
            payload=config,
        )
        return response

    def delete(self, *args, **kwargs):
        """delete a resource."""
        return self.call("DELETE", *args, **kwargs)

    def get(self, *args, **kwargs):
        """get a resource."""
        return self.call("GET", *args, **kwargs)

    def put(self, *args, **kwargs):
        """update a resource."""
        return self.call("PUT", *args, **kwargs)

    def patch(self, *args, **kwargs):
        """update a resource."""
        return self.call("PATCH", *args, **kwargs)


def remove_state_property(data: dict) -> dict:
    """Recursively remove the 'state' property from the data structure if a 'config' property is present on the same level. It also supports ':config' and ':state' suffixes for an identical key."""

    def _remove_suffix(s: str, suffix: str) -> str:
        if s.endswith(suffix):
            return s[: -len(suffix)]
        return s

    data_items = list(data.items())
    for key, value in data_items:
        if key == "state" or str(key).endswith(":state"):
            _base_key_name = _remove_suffix(str(key), ":state")
            if "config" in data.keys() or any(
                k.endswith(f"{_base_key_name}:config") for k in data.keys()
            ):
                data.pop(key)
        elif isinstance(value, dict):
            data[key] = remove_state_property(value)
        elif isinstance(value, list):
            data[key] = [
                remove_state_property(item) if isinstance(item, dict) else item
                for item in value
            ]
    return data


def recurse_remove_keys(data: dict, keys: list) -> dict:
    """Recursively remove keys from the data structure."""
    data_items = list(data.items())
    for key, value in data_items:
        if key in keys:
            data.pop(key)
        elif isinstance(value, dict):
            data[key] = recurse_remove_keys(value, keys)
        elif isinstance(value, list):
            data[key] = [
                recurse_remove_keys(item, keys) if isinstance(item, dict) else item
                for item in value
            ]
    return data


def dicts_equal(d1, d2, remove_keys=[]) -> bool:
    """
    Compare two dictionaries recursively, return True if they are equal, False otherwise.

    d1, d2: dictionaries to compare
    remove_keys: list of keys to remove from the dictionaries before comparison

    Lists with different order but same content are considered equal.
    Values with integers and floats are compared as strings, hence the type is ignored.

    d1 will be mutated by this function, so make sure to pass a copy if you want to keep the original.
    d2 will not be mutated by this function.
    """

    def _process_lists(_d1, _d2):
        def _sort_key(element):
            if isinstance(element, dict):
                return (3, str(element))  # Assign a higher priority to dicts
            elif isinstance(element, list):
                return (2, str(element))  # Assign a medium priority to lists
            elif isinstance(element, str):
                return (1, element)  # Assign a medium-low priority to strings
            elif isinstance(element, (int, float)):
                return (0, element)  # Assign a lower priority to numbers
            else:
                return (4, str(element))  # Catch-all for other types

        if len(_d1) != len(_d2):
            return False

        # sort lists by type and value
        _l1 = sorted(_d1, key=_sort_key)
        _l2 = sorted(_d2, key=_sort_key)

        for i, item in enumerate(_l1):
            if isinstance(item, dict):
                if not dicts_equal(item, _l2[i]):
                    return False
            elif isinstance(item, list):
                if not _process_lists(item, _l2[i]):
                    return False
            else:
                if str(item) not in [
                    str(entry) for entry in _l2 if not isinstance(entry, (list, dict))
                ]:
                    return False
        return True

    _d1 = d1  # d1 will be mutated by this function
    _d2 = deepcopy(d2)

    if remove_keys:
        _d1 = recurse_remove_keys(_d1, remove_keys)
        _d2 = recurse_remove_keys(_d2, remove_keys)

    # simplest case: if the dictionaries are the same object, they are the same
    if _d1 == _d2:
        return True

    # If the types are different, the dictionaries are different
    if type(_d1) != type(_d2):
        return False

    # If the dictionaries are not the same length, they are different
    if len(_d1) != len(_d2):
        return False

    # If the dictionaries are empty, they are the same
    if len(_d1) == 0:
        return False

    # If the dictionaries are not empty, compare the keys
    if set(_d1) != set(_d2):
        return False

    # If the keys are the same, compare the values
    for key in _d1.keys():
        if isinstance(_d1[key], dict):
            if not dicts_equal(_d1[key], _d2[key]):
                return False
        elif isinstance(_d1[key], list):
            if not _process_lists(_d1[key], _d2[key]):
                return False
        else:
            if str(_d1[key]) != str(_d2[key]):
                return False

    return True


def format_bool_values(d):
    """Returns a copy of dict `d` with all boolean values (True, False) properly formatted. It converts str values of 'true', 'True', 'false', 'False' to the actual boolean python representation."""

    def _list_format_bool_values(l: list):
        _l = []
        for i in l:
            if isinstance(i, dict):
                _l.append(_dict_format_bool_values(i))
            elif isinstance(i, list):
                _l.append(_list_format_bool_values(i))
            elif isinstance(i, str):
                if i.lower() == "true":
                    _l.append(True)
                elif i.lower() == "false":
                    _l.append(False)
                else:
                    _l.append(i)
            else:
                _l.append(i)
        return _l

    def _dict_format_bool_values(d):
        try:
            for k, v in d.items():
                if isinstance(v, dict):
                    _dict_format_bool_values(v)
                elif isinstance(v, list):
                    d[k] = _list_format_bool_values(v)
                elif isinstance(v, str):
                    if v.lower() == "true":
                        d[k] = True
                    elif v.lower() == "false":
                        d[k] = False
                    else:
                        d[k] = v
                else:
                    d[k] = v
        except AttributeError:
            pass
        return d

    import copy

    _d = copy.deepcopy(d)

    return _dict_format_bool_values(_d)


def number_values_to_string(d):
    """Returns a copy of dict `d` with all numeric values (int, float) converted strings (str)."""

    def _list_number_elements_to_string(l: list):
        _l = []
        for i in l:
            if isinstance(i, dict):
                _l.append(_dict_number_values_to_string(i))
            elif isinstance(i, list):
                _l.append(_list_number_elements_to_string(i))
            elif isinstance(i, (int, float)):
                _l.append(str(i))
            else:
                _l.append(i)
        return _l

    def _dict_number_values_to_string(d):
        try:
            for k, v in d.items():
                if isinstance(v, dict):
                    _dict_number_values_to_string(v)
                elif isinstance(v, list):
                    d[k] = _list_number_elements_to_string(v)
                elif isinstance(v, (int, float)):
                    d[k] = str(v)
                else:
                    d[k] = v
        except AttributeError:
            pass
        return d

    import copy

    _d = copy.deepcopy(d)

    return _dict_number_values_to_string(_d)


def changes_add_deep_diff(changes):
    """Updates `changes` dict with `diff` if deepdiff dependency is installed. The diff will be created based on 'before' and 'after' keys of `changes`."""
    diff = None
    if changes:
        try:
            from deepdiff import DeepDiff

            diff = DeepDiff(
                changes.get("before", {}),
                changes.get("after", {}),
                ignore_order=True,
                verbose_level=2,
            ).to_dict()
        except ImportError:
            pass
    if diff:
        changes.update({"diff": diff})
