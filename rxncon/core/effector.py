import re
from abc import ABCMeta, abstractproperty
from typing import List, Optional
from copy import deepcopy

from rxncon.core.spec import spec_from_str, Spec
from rxncon.core.state import State
from rxncon.util.utils import OrderedEnum


BOOLEAN_CONTINGENCY_REGEX = '^<.*>$'


class BooleanOperator(OrderedEnum):
    op_and = 'and'
    op_or  = 'or'
    op_not = 'not'
    op_eqv = 'eqv'


class BooleanContingencyName:
    def __init__(self, name: str):
        assert re.match(BOOLEAN_CONTINGENCY_REGEX, name)
        self.name = name

    def __eq__(self, other: 'BooleanContingencyName') -> bool:
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.name


class QualSpec:
    def __init__(self, namespace: List[BooleanContingencyName], spec: Spec):
        self.namespace = namespace
        self.spec      = spec
        self._name     = '.'.join(str(x) for x in namespace + [spec])

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return 'QualSpec<{}>'.format(self._name)

    def __eq__(self, other: 'QualSpec') -> bool:
        return self.namespace == other.namespace and self.spec == other.spec

    def to_component_qual_spec(self):
        return QualSpec(self.namespace, self.spec.to_component_spec())

    @property
    def has_trivial_namespace(self):
        return not self.namespace

    def with_prepended_namespace(self, extra_namespace: List[BooleanContingencyName]):
        new_namespace = deepcopy(extra_namespace) + deepcopy(self.namespace)
        return QualSpec(new_namespace, self.spec)


def qual_spec_from_str(qualified_spec_str: str) -> QualSpec:
    namespace = [BooleanContingencyName(x) for x in qualified_spec_str.split('.')[:-1]]
    spec      = spec_from_str(qualified_spec_str.split('.')[-1])

    return QualSpec(namespace, spec)


class StructEquivalences:
    def __init__(self):
        self.eq_classes = []

    def __str__(self):
        return '\n'.join(str(x) for x in self.eq_classes)

    def add_equivalence(self, first_qual_spec: QualSpec, second_qual_spec: QualSpec):
        first_qual_spec, second_qual_spec = first_qual_spec.to_component_qual_spec(), second_qual_spec.to_component_qual_spec()

        found = False
        for eq_class in self.eq_classes:
            if first_qual_spec in eq_class:
                eq_class.append(second_qual_spec)
                found = True
            elif second_qual_spec in eq_class:
                eq_class.append(first_qual_spec)
                found = True

        if not found:
            self.eq_classes.append([first_qual_spec, second_qual_spec])

    def add_equivalence_class(self, eq_class: List[QualSpec]):
        for existing_class in self.eq_classes:
            if next((x for x in existing_class if x.to_component_qual_spec() in eq_class), False):
                existing_class += [x.to_component_qual_spec() for x in eq_class]
                return

        self.eq_classes.append([x.to_component_qual_spec() for x in eq_class])

    def merge_with(self, other: 'StructEquivalences', other_base_namespace: List[BooleanContingencyName]):
        for other_eq_class in other.eq_classes:
            self.add_equivalence_class([x.with_prepended_namespace(other_base_namespace) for x in other_eq_class])

    def find_unqualified_spec(self, qual_spec: QualSpec) -> Optional[Spec]:
        for eq_class in self.eq_classes:
            if qual_spec.to_component_qual_spec() in eq_class:
                existing_spec = deepcopy(next((x.spec for x in eq_class if x.has_trivial_namespace), None))
                if existing_spec:
                    existing_spec.locus = deepcopy(qual_spec.spec.locus)
                    return existing_spec

        return None


class StructCounter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1


class Effector(metaclass=ABCMeta):
    @property
    def name(self) -> Optional[str]:
        try:
            return self._name
        except AttributeError:
            return None

    @name.setter
    def name(self, value: str):
        self._name = value

    @abstractproperty
    def states(self) -> List[State]:
        pass

    @property
    def is_leaf(self) -> bool:
        raise NotImplementedError

    def to_struct_effector(self, glob_equivs: StructEquivalences=None,
                           cur_index: StructCounter=None,
                           cur_namespace: List[BooleanContingencyName]=None) -> 'Effector':
        raise AssertionError

    def _init_to_struct_effector_args(self, glob_equivs, cur_index, cur_namespace):
        if not glob_equivs:
            glob_equivs = StructEquivalences()
        if not cur_index:
            cur_index = StructCounter()
        if not cur_namespace:
            cur_namespace = []

        return glob_equivs, cur_index, cur_namespace


class StateEffector(Effector):
    def __init__(self, expr: State):
        self.expr = expr

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return 'StateEffector({})'.format(str(self.expr))

    def __eq__(self, other: Effector) -> bool:
        return isinstance(other, StateEffector) and self.expr == other.expr and self.name == other.name

    @property
    def states(self) -> List[State]:
        return [self.expr]

    @property
    def is_leaf(self) -> bool:
        return True

    def to_struct_effector(self, glob_equivs: StructEquivalences=None,
                           cur_index: StructCounter=None,
                           cur_namespace: List[BooleanContingencyName]=None):
        glob_equivs, cur_index, cur_namespace = self._init_to_struct_effector_args(glob_equivs, cur_index, cur_namespace)

        state = deepcopy(self.expr)

        for spec in state.specs:
            existing_spec = glob_equivs.find_unqualified_spec(QualSpec(cur_namespace, spec))

            if existing_spec:
                state.update_spec(spec, existing_spec)
            else:
                new_spec = deepcopy(spec)
                new_spec.struct_index = cur_index.value
                cur_index.increment()

                state.update_spec(spec, new_spec)
                glob_equivs.add_equivalence(QualSpec([], new_spec), QualSpec(cur_namespace, spec))

        return StateEffector(state)


class NotEffector(Effector):
    def __init__(self, expr: Effector):
        self.expr = expr

    def __str__(self) -> str:
        return 'NotEffector({})'.format(self.expr)

    def __eq__(self, other: Effector) -> bool:
        return isinstance(other, NotEffector) and self.expr == other.expr and self.name == other.name

    @property
    def states(self) -> List[State]:
        return self.expr.states

    @property
    def is_leaf(self):
        return self.expr.is_leaf

    def to_struct_effector(self, glob_equivs: StructEquivalences=None,
                           cur_index: StructCounter=None,
                           cur_namespace: List[BooleanContingencyName]=None):
        glob_equivs, cur_index, cur_namespace = self._init_to_struct_effector_args(glob_equivs, cur_index, cur_namespace)
        return NotEffector(self.expr.to_struct_effector(glob_equivs, cur_index, cur_namespace))


class NaryEffector(Effector):
    def __init__(self, *exprs):
        self.exprs  = exprs
        self.equivs = StructEquivalences()

    @property
    def states(self) -> List[State]:
        return [state for x in self.exprs for state in x.states]

    @property
    def is_leaf(self) -> bool:
        return False

    def to_struct_effector(self, glob_equivs: StructEquivalences=None,
                           cur_index: StructCounter=None,
                           cur_namespace: List[BooleanContingencyName]=None):
        glob_equivs, cur_index, cur_namespace = self._init_to_struct_effector_args(glob_equivs, cur_index, cur_namespace)
        glob_equivs.merge_with(self.equivs, cur_namespace + [BooleanContingencyName(self.name)])

        print('===')
        print(glob_equivs)

        return self.__class__(*(x.to_struct_effector(
            glob_equivs, cur_index, cur_namespace + [BooleanContingencyName(self.name)]) for x in self.exprs))


class AndEffector(NaryEffector):
    def __str__(self) -> str:
        if self.name:
            return 'AndEffector{0}({1})'.format(self.name, ','.join(str(x) for x in self.exprs))
        else:
            return 'AndEffector({0})'.format(','.join(str(x) for x in self.exprs))

    def __eq__(self, other: Effector) -> bool:
        return isinstance(other, AndEffector) and self.name == other.name and \
               self.exprs == other.exprs


class OrEffector(NaryEffector):
    def __str__(self) -> str:
        if self.name:
            return 'OrEffector{0}({1})'.format(self.name, ','.join(str(x) for x in self.exprs))
        else:
            return 'OrEffector({0})'.format(','.join(str(x) for x in self.exprs))

    def __eq__(self, other: Effector) -> bool:
        return isinstance(other, OrEffector) and self.name == other.name and \
               self.exprs == other.exprs


