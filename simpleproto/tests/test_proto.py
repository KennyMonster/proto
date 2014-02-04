from nose.tools import assert_equal, assert_raises
import simpleproto


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


def test_ctor_attrs():
    # Does now throw
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