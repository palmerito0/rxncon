import re
from abc import ABCMeta, abstractproperty
from typing import List, Optional, Dict
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
    def __init__(self, namespace: List[str], spec: Spec):
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
    def is_in_root_namespace(self):
        return not self.namespace

    def with_prepended_namespace(self, extra_namespace: List[str]):
        new_namespace = deepcopy(extra_namespace) + deepcopy(self.namespace)
        return QualSpec(new_namespace, self.spec)


def qual_spec_from_str(qualified_spec_str: str) -> QualSpec:
    namespace = [x for x in qualified_spec_str.split('.')[:-1]]
    spec      = spec_from_str(qualified_spec_str.split('.')[-1])

    return QualSpec(namespace, spec)


class StructEquivalences:
    def __init__(self):
        self.eq_classes = []

    def __str__(self):
        return '\n'.join(str(x) for x in self.eq_classes)

    def add_equivalence(self, first_qual_spec: QualSpec, second_qual_spec: QualSpec):
        first_qual_spec, second_qual_spec = first_qual_spec.to_component_qual_spec(), second_qual_spec.to_component_qual_spec()

        found_first = None
        found_second = None
        for eq_class in self.eq_classes:
            if first_qual_spec in eq_class:
                if second_qual_spec not in eq_class:
                    eq_class.append(second_qual_spec)
                found_first = eq_class
            elif second_qual_spec in eq_class:
                if first_qual_spec not in eq_class:
                    eq_class.append(first_qual_spec)
                found_second = eq_class

        if found_first and found_second:
            found_first += found_second
            self.eq_classes.remove(found_second)

        if not (found_first or found_second):
            self.eq_classes.append([first_qual_spec, second_qual_spec])

    def add_equivalence_class(self, eq_class: List[QualSpec]):
        for existing_class in self.eq_classes:
            if next((x for x in existing_class if x.to_component_qual_spec() in eq_class), False):
                for elem in eq_class:
                    self.add_equivalence(elem.to_component_qual_spec(), existing_class[0])
                return

        self.eq_classes.append([x.to_component_qual_spec() for x in eq_class])

    def merge_with(self, other: 'StructEquivalences', other_base_namespace: List[str]):
        for other_eq_class in other.eq_classes:
            self.add_equivalence_class([x.with_prepended_namespace(other_base_namespace) for x in other_eq_class])

    def find_unqualified_spec(self, qual_spec: QualSpec) -> Optional[Spec]:
        for eq_class in self.eq_classes:
            if qual_spec.to_component_qual_spec() in eq_class:
                existing_spec = deepcopy(next((x.spec for x in eq_class if x.is_in_root_namespace), None))
                if existing_spec:
                    existing_spec.locus = deepcopy(qual_spec.spec.locus)
                    return existing_spec

        return None

    def indices_in_root_namespace(self):
        return [qspec.spec.struct_index for eq_class in self.eq_classes for qspec in eq_class if qspec.is_in_root_namespace]


class TrivialStructEquivalences(StructEquivalences):
    def __init__(self, initial_struct_specs: Dict[Spec, Spec]=None):
        if not initial_struct_specs:
            self.struct_specs = {}
        else:
            self.struct_specs = initial_struct_specs

        self.cur_index = 2

    def __str__(self):
        return 'TrivialStructEquivalences'

    def add_equivalence(self, first_qual_spec: QualSpec, second_qual_spec: QualSpec):
        pass

    def add_equivalence_class(self, eq_class: List[QualSpec]):
        pass

    def merge_with(self, other: 'StructEquivalences', other_base_namespace: List[str]):
        pass

    def find_unqualified_spec(self, qual_spec: QualSpec):
        try:
            struct_spec = deepcopy(self.struct_specs[qual_spec.spec.to_component_spec()])
            struct_spec.locus = deepcopy(qual_spec.spec.locus)
            return struct_spec
        except KeyError:
            self.struct_specs[qual_spec.spec.to_component_spec()] = \
                deepcopy(qual_spec.spec.to_component_spec().with_struct_index(self.cur_index))
            self.cur_index += 1
            return self.find_unqualified_spec(qual_spec)

    def indices_in_root_namespace(self):
        return [x for x in range(self.cur_index)]

class StructCounter:
    def __init__(self):
        self.value = 2

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
    def is_structured(self) -> bool:
        raise NotImplementedError

    def to_merged_struct_effector(self, glob_equivs: StructEquivalences=None,
                                  counter: StructCounter=None,
                                  cur_namespace: List[str]=None) -> 'Effector':
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
    def is_structured(self) -> bool:
        return self.expr.is_structured

    def to_merged_struct_effector(self, glob_equivs: StructEquivalences=None,
                                  counter: StructCounter=None,
                                  cur_namespace: List[str]=None):
        glob_equivs, counter, cur_namespace = self._init_to_struct_effector_args(glob_equivs, counter, cur_namespace)

        state = deepcopy(self.expr)

        updates = {}

        for spec in state.specs:
            existing_spec = glob_equivs.find_unqualified_spec(QualSpec(cur_namespace, spec))

            if existing_spec:
                updates[spec] = existing_spec
            else:
                new_spec = deepcopy(spec)
                new_spec.struct_index = self._generate_index(glob_equivs, counter)

                updates[spec] = new_spec
                glob_equivs.add_equivalence(QualSpec([], new_spec), QualSpec(cur_namespace, spec))

        state.update_specs(updates)

        return StateEffector(state)

    def _generate_index(self, glob_equivs: StructEquivalences, cur_index: StructCounter):
        index = cur_index.value
        while index in glob_equivs.indices_in_root_namespace():
            cur_index.increment()
            index = cur_index.value

        return index


class NotEffector(Effector):
    def __init__(self, expr: Effector, **kwargs):
        try:
            self.name = kwargs['name']
        except KeyError:
            pass
        self.expr = expr

    def __str__(self) -> str:
        return 'NotEffector({})'.format(self.expr)

    def __eq__(self, other: Effector) -> bool:
        return isinstance(other, NotEffector) and self.expr == other.expr and self.name == other.name

    @property
    def states(self) -> List[State]:
        return self.expr.states

    @property
    def is_structured(self):
        return self.expr.is_structured

    def to_merged_struct_effector(self, glob_equivs: StructEquivalences=None,
                                  counter: StructCounter=None,
                                  cur_namespace: List[str]=None):
        glob_equivs, counter, cur_namespace = self._init_to_struct_effector_args(glob_equivs, counter, cur_namespace)
        return NotEffector(self.expr.to_merged_struct_effector(glob_equivs, counter, cur_namespace), name=self.name)


class NaryEffector(Effector):
    def __init__(self, *exprs, **kwargs):
        try:
            self.name = kwargs['name']
        except KeyError:
            pass
        self.exprs  = exprs
        self.equivs = StructEquivalences()

    @property
    def states(self) -> List[State]:
        return [state for x in self.exprs for state in x.states]

    @property
    def is_structured(self) -> bool:
        return all(x.is_structured for x in self.exprs)

    def to_merged_struct_effector(self, glob_equivs: StructEquivalences=None,
                                  counter: StructCounter=None,
                                  cur_namespace: List[str]=None):
        glob_equivs, counter, cur_namespace = self._init_to_struct_effector_args(glob_equivs, counter, cur_namespace)
        glob_equivs.merge_with(self.equivs, cur_namespace)

        return type(self)(*(x.to_merged_struct_effector(
            glob_equivs, counter, cur_namespace + [self.name]) for x in self.exprs), name=self.name)


class AndEffector(NaryEffector):
    def __str__(self) -> str:
        if self.name:
            return 'AndEffector{0}({1})'.format(self.name, ','.join(str(x) for x in self.exprs))
        else:
            return 'AndEffector({0})'.format(','.join(str(x) for x in self.exprs))

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Effector) -> bool:
        return isinstance(other, AndEffector) and self.name == other.name and self.exprs == other.exprs


class OrEffector(NaryEffector):
    def __str__(self) -> str:
        if self.name:
            return 'OrEffector{0}({1})'.format(self.name, ','.join(str(x) for x in self.exprs))
        else:
            return 'OrEffector({0})'.format(','.join(str(x) for x in self.exprs))

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Effector) -> bool:
        return isinstance(other, OrEffector) and self.name == other.name and \
               self.exprs == other.exprs
