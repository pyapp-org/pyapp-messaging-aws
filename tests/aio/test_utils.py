from pyapp_ext.messaging_aws.aio import utils


def test_build_attributes():
    actual = utils.build_attributes(foo="bar", eek=None)

    assert actual == {
        "foo": {"DataType": "String", "StringValue": "bar"},
    }


def test_parse_attributes():
    actual = utils.parse_attributes({
        "foo": {"DataType": "String", "StringValue": "bar"},
    })

    assert actual == {
        "foo": "bar",
    }
