from nose.tools import assert_equal, assert_raises
import simpleproto

# Basic protocol messages


class Message(simpleproto.Protocol):
    char_field = simpleproto.CharField()
    bool_field = simpleproto.BooleanField()
    num_field = simpleproto.NumberField()


class MessageNoRequired(simpleproto.Protocol):
    char_field = simpleproto.CharField(required=False)
    bool_field = simpleproto.BooleanField(required=False)
    num_field = simpleproto.NumberField(required=False)


class MessageDefaults(simpleproto.Protocol):
    char_field = simpleproto.CharField(default='default')
    bool_field = simpleproto.BooleanField(default=True)
    num_field = simpleproto.NumberField(default=100)

# Nested protocol messages


class ChildMessage(simpleproto.Protocol):
    char_field = simpleproto.CharField()


class ParentMessage(simpleproto.Protocol):
    char_field = simpleproto.CharField()
    child_field = simpleproto.ProtocolField(ChildMessage)

# Tests


def test_ctor_attrs():
    # Does not throw
    m = Message(char_field='test')

    assert_equal(m.char_field, 'test')

    # Throws
    with assert_raises(NameError):
        Message(does_not_exist=1)


def test_class_field_removed():
    with assert_raises(AttributeError):
        Message.char_field


def test_default_attributes():
    m = Message()
    assert_equal(m.char_field, None)
    assert_equal(m.bool_field, None)
    assert_equal(m.num_field, None)


def test_specified_defaults():
    m = MessageDefaults()
    assert_equal(m.char_field, 'default')
    assert_equal(m.bool_field, True)
    assert_equal(m.num_field, 100)


def _valid_msg():
    m = Message()
    m.bool_field = True
    m.num_field = 10
    m.char_field = 'hello'
    return m


def test_validation():
    m = _valid_msg()
    m.validate()

    # Wrong type
    with assert_raises(simpleproto.ValidationError):
        m.num_field = True
        m.validate()
    with assert_raises(simpleproto.ValidationError):
        m.num_field = []
        m.validate()

    with assert_raises(simpleproto.ValidationError):
        m = _valid_msg()
        m.bool_field = "hi"
        m.validate()

    with assert_raises(simpleproto.ValidationError):
        m = _valid_msg()
        m.char_field = 23
        m.validate()

    # Missing values
    with assert_raises(simpleproto.ValidationError):
        m = Message()
        m.validate()


def test_validation_no_required():
    m = MessageNoRequired()
    m.validate()


def test_serialize():
    m = _valid_msg()
    json_str = m.serialize()
    assert_equal(json_str, '{"char_field": "hello", "num_field": 10, "bool_field": true}')

    m = MessageNoRequired()
    json_str = m.serialize()
    assert_equal(json_str, '{}')


def test_deserialize():
    json_str = '{"char_field": "hello", "num_field": 10, "bool_field": true}'
    m = Message.deserialize(json_str)
    assert_equal(m.char_field, "hello")
    assert_equal(m.bool_field, True)
    assert_equal(m.num_field, 10)


def test_nested_msgs():
    p = ParentMessage()
    c = ChildMessage()

    p.char_field = "parent"
    p.child_field = c

    c.char_field = "child"

    expected_json = '{"char_field": "parent", "child_field": {"char_field": "child"}}'

    # Serialization
    json_str = p.serialize()
    assert_equal(json_str, expected_json)

    # Deserialization
    m = ParentMessage.deserialize(expected_json)
    assert_equal(m.char_field, "parent")
    assert_equal(m.child_field.char_field, "child")

    # Serialize again for kicks
    json_str = m.serialize()
    assert_equal(json_str, expected_json)


def test_nested_msgs_validation():
    p = ParentMessage()
    c = ChildMessage()

    p.char_field = "parent"
    p.child_field = c

    c.char_field = 1000

    with assert_raises(simpleproto.ValidationError):
        p.validate()