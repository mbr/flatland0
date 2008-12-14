from flatland.util import signals
from tests._util import eq_, assert_raises


def test_meta_connect():
    sentinel = []
    def meta_received(**kw):
        sentinel.append(kw)

    assert not signals.receiver_connected.has_connected
    signals.receiver_connected.connect(meta_received)
    assert not sentinel

    def receiver(**kw):
        pass
    sig = signals.Signal('sig')
    sig.connect(receiver)

    eq_(sentinel, [dict(sender=sig,
                        receiver_arg=receiver,
                        sender_arg=signals.ANY,
                        weak_arg=True)])

    signals.receiver_connected._clear_state()

def test_meta_connect_failure():
    def meta_received(**kw):
        raise TypeError('boom')

    assert not signals.receiver_connected.has_connected
    signals.receiver_connected.connect(meta_received)

    def receiver(**kw):
        pass
    sig = signals.Signal('sig')

    assert_raises(TypeError, sig.connect, receiver)
    assert not sig._receivers
    assert not sig._by_receiver
    eq_(sig._by_sender, {signals.ANY: set()})

    signals.receiver_connected._clear_state()

def test_singletons():
    assert 'abc' not in signals._signals
    s1 = signals.signal('abc')
    assert s1 is signals.signal('abc')
    assert s1 is not signals.signal('def')
    assert 'abc' in signals._signals
    del s1
    assert 'abc' not in signals._signals

def test_weak_receiver():
    sentinel = []
    def received(**kw):
        sentinel.append(kw)

    sig = signals.Signal('sig')
    sig.connect(received, weak=True)
    del received

    assert not sentinel
    sig.send()
    assert not sentinel
    assert not sig._receivers
    values_are_empty_sets_(sig._by_receiver)
    values_are_empty_sets_(sig._by_sender)

def test_strong_receiver():
    sentinel = []
    def received(**kw):
        sentinel.append(kw)
    fn_id = id(received)

    sig = signals.Signal('sig')
    sig.connect(received, weak=False)
    del received

    assert not sentinel
    sig.send()
    assert sentinel
    eq_([id(fn) for fn in sig._receivers.values()], [fn_id])

def test_filtered_receiver():
    sentinel = []
    def received(sender):
        sentinel.append(sender)

    sig = signals.Signal('sig')

    sig.connect(received, 123)

    assert not sentinel
    sig.send()
    assert not sentinel
    sig.send(123)
    assert sentinel == [123]
    sig.send()
    assert sentinel == [123]

def test_filtered_receiver_weakref():
    sentinel = []
    def received(sender):
        sentinel.append(sender)

    class Object(object):
        pass
    obj = Object()

    sig = signals.Signal('sig')
    sig.connect(received, obj)

    assert not sentinel
    sig.send(obj)
    assert sentinel == [obj]
    del sentinel[:]
    del obj

    # general index isn't cleaned up
    assert sig._receivers
    # but receiver/sender pairs are
    values_are_empty_sets_(sig._by_receiver)
    values_are_empty_sets_(sig._by_sender)

def test_no_double_send():
    sentinel = []
    def received(sender):
        sentinel.append(sender)

    sig = signals.Signal('sig')

    sig.connect(received, 123)
    sig.connect(received)

    assert not sentinel
    sig.send()
    assert sentinel == [None]
    sig.send(123)
    assert sentinel == [None, 123]
    sig.send()
    assert sentinel == [None, 123, None]

def test_has_receivers():
    received = lambda sender: None

    sig = signals.Signal('sig')
    assert not sig.has_receivers_for(None)
    assert not sig.has_receivers_for(signals.ANY)

    sig.connect(received, 'xyz')
    assert not sig.has_receivers_for(None)
    assert not sig.has_receivers_for(signals.ANY)
    assert sig.has_receivers_for('xyz')

    class Object(object):
        pass
    o = Object()

    sig.connect(received, o)
    assert sig.has_receivers_for(o)

    del received
    assert sig.has_receivers_for('xyz')
    assert sig.has_receivers_for(o)
    assert list(sig.receivers_for('xyz')) == []
    assert list(sig.receivers_for(o)) == []

    sig.connect(lambda sender: None, weak=False)
    assert sig.has_receivers_for('xyz')
    assert sig.has_receivers_for(o)
    assert sig.has_receivers_for(None)
    assert sig.has_receivers_for(signals.ANY)
    assert sig.has_receivers_for('xyz')

def test_repr():
    sig = signals.Signal('squiznart')
    assert 'squiznart' in repr(sig)

def values_are_empty_sets_(dictionary):
    for val in dictionary.itervalues():
        eq_(val, set())
