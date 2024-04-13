import datetime as dt

import pytest
import pytz

import stix2

from .constants import FAKE_TIME, GROUPING_ID, GROUPING_KWARGS

EXPECTED_GROUPING = """{
    "type": "grouping",
    "spec_version": "2.1",
    "id": "grouping--753abcde-3141-5926-ace5-0a810b1ff996",
    "created": "2017-01-01T12:34:56.000Z",
    "modified": "2017-01-01T12:34:56.000Z",
    "name": "Harry Potter and the Leet Hackers",
    "context": "suspicious-activity",
    "object_refs": [
        "malware--c8d2fae5-7271-400c-b81d-931a4caf20b9",
        "identity--988145ed-a3b4-4421-b7a7-273376be67ce"
    ]
}"""


def test_grouping_with_all_required_properties():
    now = dt.datetime(2017, 1, 1, 12, 34, 56, tzinfo=pytz.utc)

    grp = stix2.v21.Grouping(
        type="grouping",
        id=GROUPING_ID,
        created=now,
        modified=now,
        name="Harry Potter and the Leet Hackers",
        context="suspicious-activity",
        object_refs=[
            "malware--c8d2fae5-7271-400c-b81d-931a4caf20b9",
            "identity--988145ed-a3b4-4421-b7a7-273376be67ce",
        ],
    )

    assert grp.serialize(pretty=True) == EXPECTED_GROUPING


def test_grouping_autogenerated_properties(grouping):
    assert grouping.type == 'grouping'
    assert grouping.id == 'grouping--00000000-0000-4000-8000-000000000001'
    assert grouping.created == FAKE_TIME
    assert grouping.modified == FAKE_TIME
    assert grouping.name == "Harry Potter and the Leet Hackers"
    assert grouping.context == "suspicious-activity"

    assert grouping['type'] == 'grouping'
    assert grouping['id'] == 'grouping--00000000-0000-4000-8000-000000000001'
    assert grouping['created'] == FAKE_TIME
    assert grouping['modified'] == FAKE_TIME
    assert grouping['name'] == "Harry Potter and the Leet Hackers"
    assert grouping['context'] == "suspicious-activity"


def test_grouping_type_must_be_grouping():
    with pytest.raises(stix2.exceptions.InvalidValueError) as excinfo:
        stix2.v21.Grouping(type='xxx', **GROUPING_KWARGS)

    assert excinfo.value.cls == stix2.v21.Grouping
    assert excinfo.value.prop_name == "type"
    assert excinfo.value.reason == "must equal 'grouping'."
    assert str(excinfo.value) == "Invalid value for Grouping 'type': must equal 'grouping'."


def test_grouping_id_must_start_with_grouping():
    with pytest.raises(stix2.exceptions.InvalidValueError) as excinfo:
        stix2.v21.Grouping(id='my-prefix--', **GROUPING_KWARGS)

    assert excinfo.value.cls == stix2.v21.Grouping
    assert excinfo.value.prop_name == "id"
    assert excinfo.value.reason == "must start with 'grouping--'."
    assert str(excinfo.value) == "Invalid value for Grouping 'id': must start with 'grouping--'."


def test_grouping_required_properties():
    with pytest.raises(stix2.exceptions.MissingPropertiesError) as excinfo:
        stix2.v21.Grouping()

    assert excinfo.value.cls == stix2.v21.Grouping
    assert excinfo.value.properties == ["context", "object_refs"]


def test_invalid_kwarg_to_grouping():
    with pytest.raises(stix2.exceptions.ExtraPropertiesError) as excinfo:
        stix2.v21.Grouping(my_custom_property="foo", **GROUPING_KWARGS)

    assert excinfo.value.cls == stix2.v21.Grouping
    assert excinfo.value.properties == ['my_custom_property']
    assert str(excinfo.value) == "Unexpected properties for Grouping: (my_custom_property)."


@pytest.mark.parametrize(
    "data", [
        EXPECTED_GROUPING,
        {
            "type": "grouping",
            "spec_version": "2.1",
            "id": GROUPING_ID,
            "created": "2017-01-01T12:34:56.000Z",
            "modified": "2017-01-01T12:34:56.000Z",
            "name": "Harry Potter and the Leet Hackers",
            "context": "suspicious-activity",
            "object_refs": [
                "malware--c8d2fae5-7271-400c-b81d-931a4caf20b9",
                "identity--988145ed-a3b4-4421-b7a7-273376be67ce",
            ],
        },
    ],
)
def test_parse_grouping(data):
    grp = stix2.parse(data)

    assert grp.type == 'grouping'
    assert grp.spec_version == '2.1'
    assert grp.id == GROUPING_ID
    assert grp.created == dt.datetime(2017, 1, 1, 12, 34, 56, tzinfo=pytz.utc)
    assert grp.modified == dt.datetime(2017, 1, 1, 12, 34, 56, tzinfo=pytz.utc)
    assert grp.name == "Harry Potter and the Leet Hackers"
    assert grp.context == "suspicious-activity"
    assert grp.object_refs == [
        "malware--c8d2fae5-7271-400c-b81d-931a4caf20b9",
        "identity--988145ed-a3b4-4421-b7a7-273376be67ce",
    ]
