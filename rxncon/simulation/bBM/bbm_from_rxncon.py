import typing as tg
import rxncon.core.rxncon_system as rxs
import rxncon.core.reaction as rxn
import rxncon.simulation.bBM.bipartite_boolean_model as bbm
import rxncon.venntastic.sets as venn

from rxncon.semantics.molecule_from_rxncon import set_of_states_from_contingencies

def bipartite_boolean_model_from_rxncon(rxconsys: rxs.RxnConSystem):
    return bbm.Bipartite_Boolean_Model(rules_from_rxncon(rxconsys), initial_states_from_rxncon(rxconsys))

def rules_from_rxncon(rxconsys: rxs.RxnConSystem):

    rules = []
    for reaction in rxconsys.reactions:
        rules.append(rule_for_reaction_from_rxnconsys_and_reaction(rxconsys, reaction))

        rules.append(rule_for_state_from_rxnconsys_and_reaction(rxconsys, reaction, rules))
    rules = [rule for rule in rules if rule]
    return rules


def initial_states_from_rxncon(rxconsys: rxs.RxnConSystem):
    initial_states = []
    for reaction in rxconsys.reactions:
        if bbm.InitConditions(bbm.Node(reaction.subject), None) not in initial_states:
            initial_states.append(bbm.InitConditions(bbm.Node(reaction.subject), None))
        if bbm.InitConditions(bbm.Node(reaction.object), None) not in initial_states:
            initial_states.append(bbm.InitConditions(bbm.Node(reaction.object), None))
    return initial_states


def rule_for_reaction_from_rxnconsys_and_reaction(rxnconsys: rxs.RxnConSystem, reaction: rxn.Reaction) -> bbm.Rule:

    strict_contingency_state_set = set_of_states_from_contingencies(rxnconsys.strict_contingencies_for_reaction(reaction))

    if strict_contingency_state_set != venn.UniversalSet():
        vennset = venn.Intersection(strict_contingency_state_set,
                                   venn.Intersection(venn.PropertySet(reaction.subject),
                                                     venn.PropertySet(reaction.object)))
    else:
        vennset = venn.Intersection(venn.PropertySet(reaction.subject),
                                    venn.PropertySet(reaction.object))
    quantitative_contingency_state_set= set_of_states_from_contingencies(rxnconsys.quantitative_contingencies_for_reaction(reaction)) # todo: ersetze k+ durch ! und k- durch x. in venntastic: ! ^= PropertySet(), x ^= Complement(PropertySet())
    return bbm.Rule(bbm.Node(reaction), bbm.Factor(vennset_to_bbm_factor_vennset(vennset.simplified_form())))



def vennset_to_bbm_factor_vennset(vennset: venn.Set):
    # creates new vennset with states contained by Node objects, for compareability
    # want to rewrite venn.Set into bbm.Factor like venn.PropertySet(A--B) -> venn.PropertySet(bbm.Node(A--B))
    if isinstance(vennset, venn.PropertySet):
        return venn.PropertySet(bbm.Node(vennset.value))
    elif isinstance(vennset, venn.Intersection):
        return venn.Intersection(vennset_to_bbm_factor_vennset(vennset.left_expr), vennset_to_bbm_factor_vennset(vennset.right_expr))
    elif isinstance(vennset, venn.Union):
        return venn.Union(vennset_to_bbm_factor_vennset(vennset.left_expr), vennset_to_bbm_factor_vennset(vennset.right_expr))
    else:
        raise NotImplementedError


def get_rule_targets(rules: tg.List[bbm.Rule]):

    all_visited_states = [bbm.Node(rule.target.value) for rule in rules if rule]
    return all_visited_states


def rule_for_state_from_rxnconsys_and_reaction(rxnconsys: rxs.RxnConSystem, reaction: rxn.Reaction, system_rules: tg.List[bbm.Rule]) -> bbm.Rule:
    all_visited_states = get_rule_targets(system_rules)
    rules = []
    if reaction.product is None or bbm.Node(reaction.product) in all_visited_states:
        return rules

    pos_bool_def=[venn.PropertySet(bbm.Node(reaction.product)), venn.PropertySet(bbm.Node(reaction))]
    neg_bool_def=[]

    for rxn in rxnconsys.reactions:
        if rxn.product is not None and rxn != reaction and reaction.product in [rxn.product]:
            pos_bool_def.append(venn.PropertySet(bbm.Node(rxn)))
        if rxn.source is not None and rxn != reaction and reaction.product in [rxn.source]:
            neg_bool_def.append(venn.PropertySet(bbm.Node(rxn)))


    pos_rules= venn.nested_expression_from_list_and_binary_op(pos_bool_def, venn.Union)
    neg_rules = venn.nested_expression_from_list_and_binary_op(neg_bool_def, venn.Union)

    if not pos_rules.is_equivalent_to(venn.EmptySet()) and not neg_rules.is_equivalent_to(venn.EmptySet()):
        return bbm.Rule(bbm.Node(reaction.product),
                        bbm.Factor(venn.Intersection(pos_rules, venn.Complement(neg_rules))))
    elif not pos_rules.is_equivalent_to(venn.EmptySet()):
        return bbm.Rule(bbm.Node(reaction.product),
                        bbm.Factor(pos_rules))
    elif not neg_rules.is_equivalent_to(venn.EmptySet()):
        return bbm.Rule(bbm.Node(reaction.product),
                        bbm.Factor(venn.Complement(neg_rules)))


    # bool_rules.simplified_form() InterProteinInteraction has no _complement_expanded



