from util.decorators import RequestJsonError, check_json, OptionalArg

import copy

import pytest

def test_nested_json():
    schema = {
        "test1": {
            "test2": int,
            "test3": str,
            "test4": {
                "test5": float
            }
        },
        "test5": dict, # Might confuse our type checker
        "test6": [{
            "test7": int
        }],
        "test8": OptionalArg(int)
    }

    request_json = {
        "test1": {
            "test2": 1,
            "test3": "hello",
            "test4": {
                "test5": 4.5
            }
        },
        "test5": {"abc": "xyz", "def": 123},
        "test6": [{
            "test7": i
        } for i in range(5)],
    }

    check_json(schema, request_json)
    request_json["test5"] = {}
    check_json(schema, request_json)

    # change a field
    bad_json = copy.deepcopy(request_json)
    bad_json["test1"] = "badvalue"
    with pytest.raises(RequestJsonError): check_json(schema, bad_json)

    # Change a nested field
    bad_json = copy.deepcopy(request_json)
    bad_json["test1"]["test4"]["test5"] = "badvalue"
    with pytest.raises(RequestJsonError): check_json(schema, bad_json)

    # Change a list field
    bad_json = copy.deepcopy(request_json)
    bad_json["test6"][0] = "badvalue"
    with pytest.raises(RequestJsonError): check_json(schema, bad_json)
