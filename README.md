Simple Proto
=============
A simple way to define and verify JSON protocol messages using Django style model/form definitions


Setup
-------------
    cd proto
    virtualenv --no-site-packages env
    . env/bin/activate
    pip install -r requirements.txt


Unit tests
-------------
    cd simpleproto
    nosetests


Example
-------------

Serialization

    import simpleproto


    class SampleMessage(simpleproto.Protocol):
        name = simpleproto.CharField()
        student = simpleproto.BooleanField()
        age = simpleproto.NumberField()
        optional = simpleproto.CharField(required=False)


    s = SampleMessage(name='Bob', student=False)
    s.age = 30
    print s.serialize()

prints: {"age": 30, "name": "Bob", "student": false}

Deserialization

    m = SampleMessage.deserialize('{"age": 30, "name": "Bob", "student": false}')
    print m.name

prints: Bob
