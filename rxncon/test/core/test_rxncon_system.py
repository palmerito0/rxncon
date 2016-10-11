from rxncon.input.quick.quick import Quick
from rxncon.core.state import state_from_str
from collections import namedtuple
from rxncon.util.utils import elems_eq
from rxncon.core.spec import spec_from_str


ReactionTestCase = namedtuple('ReactionTestCase', ['synthesised_states', 'produced_states', 'consumed_states'])

def test_translation():
    rxncon_sys = Quick('''A_trsl_BmRNA
                          C_p+_B_[(r1)]
                          D_p+_B_[(r2)] ; ! B@1_[(r1)]-{p}
                          D_[x]_ppi+_B_[y]
                          E_ub+_B_[(r1)]''').rxncon_system

    expected_rxns = {
        'A_trsl_BmRNA': ReactionTestCase(
            [
                state_from_str('B_[(r1)]-{0}'),
                state_from_str('B_[(r2)]-{0}'),
                state_from_str('B_[y]--0')
            ],
            [],
            []
        ),
        'C_p+_B_[(r1)]': ReactionTestCase(
            [],
            [state_from_str('B_[(r1)]-{p}')],
            [state_from_str('B_[(r1)]-{0}')]
        ),
        'D_p+_B_[(r2)]': ReactionTestCase(
            [],
            [state_from_str('B_[(r2)]-{p}')],
            [state_from_str('B_[(r2)]-{0}')]
        ),
        'D_[x]_ppi+_B_[y]': ReactionTestCase(
            [],
            [state_from_str('D_[x]--B_[y]')],
            [state_from_str('D_[x]--0'), state_from_str('B_[y]--0')]
        ),
        'E_ub+_B_[(r1)]': ReactionTestCase(
            [],
            [state_from_str('B_[(r1)]-{ub}')],
            [state_from_str('B_[(r1)]-{0}')]
        )
    }

    for rxn in rxncon_sys.reactions:
        assert elems_eq(rxn.synthesised_states, expected_rxns[str(rxn)].synthesised_states)
        assert elems_eq(rxn.produced_states, expected_rxns[str(rxn)].produced_states)
        assert elems_eq(rxn.consumed_states, expected_rxns[str(rxn)].consumed_states)

    assert rxncon_sys.states_for_component_grouped(spec_from_str('A')) == {}
    assert rxncon_sys.states_for_component_grouped(spec_from_str('C')) == {}
    assert rxncon_sys.states_for_component_grouped(spec_from_str('E')) == {}
    assert elems_eq(rxncon_sys.states_for_component_grouped(spec_from_str('B')).values(), [
        [state_from_str('B_[y]--0'), state_from_str('D_[x]--B_[y]')],
        [state_from_str('B_[(r1)]-{0}'), state_from_str('B_[(r1)]-{p}'), state_from_str('B_[(r1)]-{ub}')],
        [state_from_str('B_[(r2)]-{0}'), state_from_str('B_[(r2)]-{p}')]
    ])
    assert elems_eq(rxncon_sys.states_for_component_grouped(spec_from_str('D')).values(), [
        [state_from_str('D_[x]--0'), state_from_str('D_[x]--B_[y]')]
    ])
