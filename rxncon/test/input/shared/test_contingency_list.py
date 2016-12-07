from rxncon.input.shared.contingency_list import contingency_list_entry_from_strs as cle_from_str, contingencies_from_contingency_list_entries
from rxncon.venntastic.sets import venn_from_str, Set as VennSet, ValueSet, Intersection, Union, Complement
from rxncon.core.state import state_from_str
from rxncon.core.effector import Effector, StateEffector, AndEffector, OrEffector, NotEffector


def venn_from_effector(effector: Effector) -> VennSet:
    if isinstance(effector, StateEffector):
        return ValueSet(effector.expr)
    elif isinstance(effector, AndEffector):
        return Intersection(*(venn_from_effector(x) for x in effector.exprs))
    elif isinstance(effector, OrEffector):
        return Union(*(venn_from_effector(x) for x in effector.exprs))
    elif isinstance(effector, NotEffector):
        return Complement(venn_from_effector(effector.expr))
    else:
        raise AssertionError


def test_nested_boolean():
    cles = [
        cle_from_str('<C1>', 'AND', 'A_[x]--B_[y]'),
        cle_from_str('<C1>', 'AND', 'A_[(r)]-{p}'),
        cle_from_str('<C2>', 'AND', 'B_[z]--D_[y]'),
        cle_from_str('<C2>', 'AND', 'B_[(r1)]-{p}'),
        cle_from_str('<C2>', 'AND', 'B_[(r2)]-{p}'),
        cle_from_str('<C1C2>', 'AND', '<C1>'),
        cle_from_str('<C1C2>', 'AND', '<C2>'),
        cle_from_str('A_[q]_ppi+_Q_[a]', '!', '<C1C2>')
    ]

    contingencies = contingencies_from_contingency_list_entries(cles)
    assert len(contingencies) == 1

    expected = venn_from_str('( A_[x]--B_[y] & A_[(r)]-{p} & B_[z]--D_[y] & B_[(r1)]-{p} & B_[(r2)]-{p} )', state_from_str)
    assert venn_from_effector(contingencies[0].effector).is_equivalent_to(expected)


def test_simple_namespace():
    cles = [
        cle_from_str('<C1>', 'AND', 'A@1_[x]--B@2_[a]'),
        cle_from_str('<C1>', 'AND', 'A@1_[y]--C@3_[a]'),
        cle_from_str('<C>', 'AND', '<C1>'),
        cle_from_str('<C>', 'AND', 'X@1_[a]--A@2_[z]'),
        cle_from_str('<C>', 'EQV', 'A@2,<C1>.A@1'),
        cle_from_str('A_p+_B_[(r)]', '!', '<C>')
    ]

    contingencies = contingencies_from_contingency_list_entries(cles)

    for x in contingencies:
        print(x)
