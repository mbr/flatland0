from flatland import (
    Dict,
    Integer,
    String,
    SparseDict,
    Unset,
)
from flatland.util import Unspecified, keyslice_pairs
from tests._util import (
    asciistr,
    udict,
    unicode_coercion_available,
)
import six

import pytest


def test_dict():
    with pytest.raises(TypeError):
        Dict()


def test_dict_immutable_keys():
    schema = Dict.of(Integer.named(u'x'), Integer.named(u'y'))
    el = schema()

    with pytest.raises(TypeError):
        el[u'z'] = 123

    with pytest.raises(TypeError):
        del el[u'x']

    with pytest.raises(KeyError):
        del el[u'z']

    with pytest.raises(TypeError):
        el.setdefault(u'x', 123)

    with pytest.raises(TypeError):
        el.setdefault(u'z', 123)

    with pytest.raises(TypeError):
        el.pop(u'x')

    with pytest.raises(KeyError):
        el.pop(u'z')

    with pytest.raises(TypeError):
        el.popitem()

    with pytest.raises(TypeError):
        el.clear()


def test_dict_reads():
    schema = Dict.of(Integer.named(u'x'), Integer.named(u'y'))
    el = schema()

    el[u'x'].set(u'10')
    el[u'y'].set(u'20')

    assert el[u'x'].value == 10
    assert el[u'y'].value == 20

    # the values are unhashable Elements, so this is a little painful
    assert set(el.keys()) == set(u'xy')
    assert (set([(u'x', 10), (u'y', 20)]) ==
            set([(_[0], _[1].value) for _ in el.items()]))
    assert set([10, 20]) == set([_.value for _ in el.values()])

    assert el.get(u'x').value == 10
    el[u'x'] = None
    assert el.get(u'x').value is None
    assert el.get(u'x', 'default is never used').value is None

    with pytest.raises(KeyError):
        el.get(u'z')

    with pytest.raises(KeyError):
        el.get(u'z', 'even with a default')


def test_dict_update():
    schema = Dict.of(Integer.named(u'x'), Integer.named(u'y'))
    el = schema()

    def value_dict(element):
        return dict((k, v.value) for k, v in six.iteritems(element))

    try:
        el.update(x=20, y=30)
    except UnicodeError:
        assert not unicode_coercion_available()
        el.update(udict(x=20, y=30))
    assert udict(x=20, y=30) == el.value

    el.update({u'y': 40})
    assert udict(x=20, y=40) == el.value

    el.update()
    assert udict(x=20, y=40) == el.value

    el.update((_, 100) for _ in u'xy')
    assert udict(x=100, y=100) == el.value

    try:
        el.update([(u'x', 1)], y=2)
        assert udict(x=1, y=2) == el.value
    except UnicodeError:
        assert not unicode_coercion_available()

    try:
        el.update([(u'x', 10), (u'y', 10)], x=20, y=20)
        assert udict(x=20, y=20) == el.value
    except UnicodeError:
        assert not unicode_coercion_available()

    if unicode_coercion_available():
        with pytest.raises(TypeError):
            el.update(z=1)

        with pytest.raises(TypeError):
            el.update(x=1, z=1)

    with pytest.raises(TypeError):
        el.update({u'z': 1})

    with pytest.raises(TypeError):
        el.update({u'x': 1, u'z': 1})

    with pytest.raises(TypeError):
        el.update({u'z': 1})

    with pytest.raises(TypeError):
        el.update({u'x': 1, u'z': 1})


class DictSetTest(object):
    schema = Dict
    policy = Unspecified
    x_default = Unspecified
    y_default = Unspecified

    def new_schema(self):
        dictkw, x_kw, y_kw = {}, {}, {}
        if self.policy is not Unspecified:
            dictkw['policy'] = self.policy
        if self.x_default is not Unspecified:
            x_kw['default'] = self.x_default
        if self.y_default is not Unspecified:
            y_kw['default'] = self.y_default

        return self.schema.named(u's').using(**dictkw).of(
            Integer.named(u'x').using(**x_kw),
            Integer.named(u'y').using(**y_kw))

    def new_element(self, schema=Unspecified, **kw):
        if schema is Unspecified:
            schema = self.new_schema()
        return schema(**kw)

    def test_empty_sets(self):
        wanted = {u'x': None, u'y': None}

        el = self.new_element()
        assert el.value == wanted

        el.set({})
        assert el.value == wanted

        el = self.new_element(value={})
        assert el.value == wanted

        el = self.new_element(value=iter(()))
        assert el.value == wanted

        el = self.new_element(value=())
        assert el.value == wanted

    def test_empty_set_flat(self):
        el = self.new_element()
        el.set_flat(())
        assert el.value == {u'x': None, u'y': None}

    def test_half_set(self):
        wanted = {u'x': 123, u'y': None}

        el = self.new_element()
        el.set({u'x': 123})
        assert el.value == wanted

        el = self.new_element()
        el.set([(u'x', 123)])
        assert el.value == wanted

    def test_half_set_flat(self):
        wanted = {u'x': 123, u'y': None}

        pairs = ((u's_x', u'123'),)
        el = self.new_element()
        el.set_flat(pairs)
        assert el.value == wanted

    def test_full_set(self):
        wanted = {u'x': 101, u'y': 102}

        el = self.new_element()
        el.set(wanted)
        assert el.value == wanted

        el = self.new_element()
        el.set(udict(x=101, y=102))
        assert el.value == wanted

        el = self.new_element()
        el.set([(u'x', 101), (u'y', 102)])
        assert el.value == wanted

        el = self.new_element(value=wanted)
        assert el.value == wanted

    def test_full_set_flat(self):
        wanted = {u'x': 101, u'y': 102}
        pairs = ((u's_x', u'101'), (u's_y', u'102'))

        el = self.new_element()
        el.set_flat(pairs)
        assert el.value == wanted

    def test_scalar_set_flat(self):
        wanted = {u'x': None, u'y': None}
        pairs = ((u's', u'xxx'),)

        el = self.new_element()

        canary = []

        def setter(self, value):
            canary.append(value)
            return type(el).set(self, value)

        el.set = setter.__get__(el, type(el))
        el.set_flat(pairs)
        assert el.value == wanted
        assert canary == []

    def test_over_set(self):
        too_much = {u'x': 1, u'y': 2, u'z': 3}

        el = self.new_element()

        with pytest.raises(KeyError):
            el.set(too_much)

        with pytest.raises(KeyError):
            self.new_element(value=too_much)

    def test_over_set_flat(self):
        wanted = {u'x': 123, u'y': None}

        pairs = ((u's_x', u'123'), (u's_z', u'nope'))
        el = self.new_element()
        el.set_flat(pairs)
        assert el.value == wanted

    def test_total_miss(self):
        miss = {u'z': 3}

        el = self.new_element()
        with pytest.raises(KeyError):
            el.set(miss)
        with pytest.raises(KeyError):
            self.new_element(value=miss)

    def test_total_miss_flat(self):
        pairs = ((u'miss', u'10'),)

        el = self.new_element()
        el.set_flat(pairs)
        assert el.value == {u'x': None, u'y': None}

    def test_set_return(self):
        el = self.new_element()
        assert el.set({u'x': 1, u'y': 2})

        el = self.new_element()
        assert not el.set({u'x': u'i am the new', u'y': u'number two'})

    def test_set_default(self):
        wanted = {u'x': 11, u'y': 12}
        schema = self.new_schema()
        schema.default = wanted

        el = schema()
        el.set_default()
        assert el.value == wanted

    def test_set_default_from_children(self):
        el = self.new_element()
        el.set_default()

        wanted = {
            u'x': self.x_default if self.x_default is not Unspecified
            else None,
            u'y': self.y_default if self.y_default is not Unspecified
            else None,
        }
        assert el.value == wanted


class TestEmptyDictSet(DictSetTest):
    pass


class TestDefaultDictSet(DictSetTest):
    x_default = 10
    y_default = 20


class TestEmptySparseDictRequiredSet(DictSetTest):
    schema = SparseDict.using(minimum_fields='required')


def test_dict_valid_policies():
    schema = Dict.of(Integer)
    el = schema()

    with pytest.raises(AssertionError):
        el.set({}, policy='bogus')


def test_dict_strict():
    # a mini test, this policy thing may get whacked
    schema = Dict.using(policy='strict').of(Integer.named(u'x'),
                                            Integer.named(u'y'))

    el = schema({u'x': 123, u'y': 456})

    el = schema()
    with pytest.raises(TypeError):
        el.set({u'x': 123})

    el = schema()
    with pytest.raises(KeyError):
        el.set({u'x': 123, u'y': 456, u'z': 7})


def test_dict_raw():
    schema = Dict.of(Integer.named('x').using(optional=False))
    el = schema()
    assert el.raw is Unset

    el = schema({u'x': u'bar'})
    assert el.raw == {u'x': u'bar'}

    el = schema([(u'x', u'bar')])
    assert el.raw == [(u'x', u'bar')]
    el.set_flat([(u'x', u'123')])
    assert el.raw is Unset

    el = schema.from_flat([(u'x', u'123')])
    assert el.raw is Unset
    assert el[u'x'].raw == u'123'


def test_dict_as_unicode():
    schema = Dict.of(Integer.named(u'x'), Integer.named(u'y'))
    el = schema({u'x': 1, u'y': 2})

    assert el.u in (u"{u'x': u'1', u'y': u'2'}", u"{u'y': u'2', u'x': u'1'}")


def test_nested_dict_as_unicode():
    schema = Dict.of(Dict.named(u'd').of(
        Integer.named(u'x').using(default=10)))
    el = schema.from_defaults()

    assert el.value == {u'd': {u'x': 10}}
    assert el.u == u"{u'd': {u'x': u'10'}}"


def test_nested_unicode_dict_as_unicode():
    schema = Dict.of(Dict.named(u'd').of(
        String.named(u'x').using(default=u'\u2308\u2309')))
    el = schema.from_defaults()
    assert el.value == {u'd': {u'x': u'\u2308\u2309'}}
    assert el.u == u"{u'd': {u'x': u'\u2308\u2309'}}"


def test_dict_el():
    # stub
    schema = Dict.named(u's').of(Integer.named(u'x'), Integer.named(u'y'))
    element = schema()

    assert element.el(u'x').name == u'x'
    with pytest.raises(KeyError):
        element.el(u'not_x')


def test_update_object():

    class Obj(object):

        def __init__(self, **kw):
            for (k, v) in kw.items():
                setattr(self, k, v)

    schema = Dict.of(String.named(u'x'), String.named(u'y'))

    o = Obj()
    assert not hasattr(o, 'x')
    assert not hasattr(o, 'y')

    def updated_(obj_factory, initial_value, wanted=None, **update_kw):
        el = schema(initial_value)
        obj = obj_factory()
        keyfunc = lambda x: x if six.PY3 else asciistr(x)
        update_kw.setdefault('key', keyfunc)
        el.update_object(obj, **update_kw)
        if wanted is None:
            wanted = dict((keyfunc(k), v) for k, v in initial_value.items())
        have = dict(obj.__dict__)
        assert have == wanted

    updated_(Obj, {u'x': u'X', u'y': u'Y'})
    updated_(Obj, {u'x': u'X'}, {'x': u'X', 'y': None})
    updated_(lambda: Obj(y=u'Y'), {u'x': u'X'}, {'x': u'X', 'y': None})
    updated_(lambda: Obj(y=u'Y'), {u'x': u'X'}, {'x': u'X', 'y': u'Y'},
             omit=('y',))
    updated_(lambda: Obj(y=u'Y'), {u'x': u'X'}, {'y': u'Y'},
             include=(u'z',))
    updated_(Obj, {u'x': u'X'}, {'y': None, 'z': u'X'},
             rename=(('x', 'z'),))


def test_slice():
    schema = Dict.of(String.named(u'x'), String.named(u'y'))

    def same_(source, kw):
        el = schema(source)

        sliced = el.slice(**kw)
        wanted = dict(keyslice_pairs(el.value.items(), **kw))

        assert sliced == wanted
        assert (set(type(_) for _ in sliced.keys()),
                set(type(_) for _ in wanted.keys()))

    yield same_, {u'x': u'X', u'y': u'Y'}, {}
    keyfunc = lambda x: x if six.PY3 else asciistr(x)
    yield same_, {u'x': u'X', u'y': u'Y'}, dict(key=keyfunc)
    yield same_, {u'x': u'X', u'y': u'Y'}, dict(include=[u'x'])
    yield same_, {u'x': u'X', u'y': u'Y'}, dict(omit=[u'x'])
    yield same_, {u'x': u'X', u'y': u'Y'}, dict(omit=[u'x'],
                                                rename={u'y': u'z'})


def test_sparsedict_key_mutability():
    schema = SparseDict.of(Integer.named(u'x'), Integer.named(u'y'))
    el = schema()

    ok, bogus = u'x', u'z'

    el[ok] = 123
    assert el[ok].value == 123
    with pytest.raises(TypeError):
        el.__setitem__(bogus, 123)

    del el[ok]
    assert ok not in el
    with pytest.raises(TypeError):
        el.__delitem__(bogus)

    assert el.setdefault(ok, 456)
    with pytest.raises(TypeError):
        el.setdefault(bogus, 456)

    el[ok] = 123
    assert el.pop(ok)
    with pytest.raises(KeyError):
        el.pop(bogus)

    with pytest.raises(NotImplementedError):
        el.popitem()

    el.clear()
    assert not el


def test_sparsedict_operations():
    schema = SparseDict.of(Integer.named(u'x'), Integer.named(u'y'))
    el = schema()

    el[u'x'] = 123
    del el[u'x']
    with pytest.raises(KeyError):
        el.__delitem__(u'x')

    assert el.setdefault(u'x', 123) == 123
    assert el.setdefault(u'x', 456) == 123

    assert el.setdefault(u'y', 123) == 123
    assert el.setdefault(u'y', 456) == 123

    assert schema().is_empty
    assert not schema().validate()

    opt_schema = schema.using(optional=True)
    assert opt_schema().validate()


def test_sparsedict_required_operations():
    schema = (SparseDict.using(minimum_fields='required').
              of(Integer.named(u'opt').using(optional=True),
              Integer.named(u'req')))

    el = schema({u'opt': 123, u'req': 456})

    del el[u'opt']
    with pytest.raises(KeyError):
        el.__delitem__(u'opt')
    with pytest.raises(TypeError):
        el.__delitem__(u'req')

    el = schema()
    assert el.setdefault(u'opt', 123) == 123
    assert el.setdefault(u'opt', 456) == 123

    assert el.setdefault(u'req', 123) == 123
    assert el.setdefault(u'req', 456) == 123

    assert not schema().is_empty
    assert not schema().validate()


def test_sparsedict_set_default():
    schema = SparseDict.of(Integer.named(u'x').using(default=123),
                           Integer.named(u'y'))
    el = schema()

    el.set_default()
    assert el.value == {}


def test_sparsedict_required_set_default():
    schema = (SparseDict.using(minimum_fields='required').
              of(Integer.named(u'x').using(default=123),
                 Integer.named(u'y').using(default=456, optional=True),
                 Integer.named(u'z').using(optional=True)))
    el = schema()

    el.set_default()
    assert el.value == {u'x': 123}


def test_sparsedict_bogus_set_default():
    schema = (SparseDict.using(minimum_fields='bogus').
              of(Integer.named(u'x')))
    el = schema()

    with pytest.raises(RuntimeError):
        el.set_default()


def test_sparsedict_required_key_mutability():
    schema = (SparseDict.of(Integer.named(u'x').using(optional=True),
                            Integer.named(u'y')).
              using(minimum_fields='required'))
    el = schema()
    ok, required, bogus = u'x', u'y', u'z'

    assert ok not in el
    assert required in el
    assert bogus not in el

    el[ok] = 123
    assert el[ok].value == 123
    el[required] = 456
    assert el[required].value == 456
    with pytest.raises(TypeError):
        el.__setitem__(bogus, 123)

    del el[ok]
    assert ok not in el
    with pytest.raises(TypeError):
        el.__delitem__(required)
    with pytest.raises(TypeError):
        el.__delitem__(bogus)

    assert el.setdefault(ok, 456)
    assert el.setdefault(required, 789)
    with pytest.raises(TypeError):
        el.setdefault(bogus, 456)

    el[ok] = 123
    assert el.pop(ok)
    el[required] = 456
    with pytest.raises(TypeError):
        el.pop(required)
    with pytest.raises(KeyError):
        el.pop(bogus)

    with pytest.raises(NotImplementedError):
        el.popitem()

    el.clear()
    assert list(el.keys()) == [required]


def test_sparsedict_from_flat():
    schema = SparseDict.of(Integer.named(u'x'),
                           Integer.named(u'y'))

    el = schema.from_flat([])
    assert list(el.items()) == []

    el = schema.from_flat([(u'x', u'123')])
    assert el.value == {u'x': 123}

    el = schema.from_flat([(u'x', u'123'), (u'z', u'456')])
    assert el.value == {u'x': 123}


def test_sparsedict_required_from_flat():
    schema = (SparseDict.of(Integer.named(u'x'),
                            Integer.named(u'y').using(optional=True)).
              using(minimum_fields='required'))

    el = schema.from_flat([])
    assert el.value == {u'x': None}

    el = schema.from_flat([(u'x', u'123')])
    assert el.value == {u'x': 123}

    el = schema.from_flat([(u'y', u'456'), (u'z', u'789')])
    assert el.value == {u'x': None, u'y': 456}


def test_sparsedict_required_validation():
    schema = (SparseDict.of(Integer.named(u'x'),
                            Integer.named(u'y').using(optional=True)).
              using(minimum_fields='required'))

    el = schema()
    assert not el.validate()

    el = schema({u'y': 456})
    assert not el.validate()

    el = schema({u'x': 123, u'y': 456})
    assert el.validate()


def test_sparsedict_flattening():
    schema = (SparseDict.named(u'top').
              of(Integer.named(u'x'), Integer.named(u'y')))

    els = [
        schema({'x': 123, 'y': 456}),
        schema(),
        schema(),
        schema(),
    ]

    els[1].set({'x': 123, 'y': 456})
    els[2]['x'] = 123
    els[2]['y'] = 456
    els[3]['x'] = Integer(123)
    els[3]['y'] = Integer(456)

    wanted = [(u'top_x', u'123'), (u'top_y', u'456')]
    for el in els:
        got = sorted(el.flatten())
        assert wanted == got
