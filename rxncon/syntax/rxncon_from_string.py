import re
from typing import Tuple, Union
from collections import OrderedDict
import typecheck as tc

import rxncon.core.specification as com
import rxncon.core.error as err
#import rxncon.core.reaction as rxn
import rxncon.core.state as sta




# @tc.typecheck
# def reaction_from_string(reaction_string: str) -> rxn.Reaction:
#     INPUT_REGEX = '^\[.+?\]$'
#
#     if re.match(INPUT_REGEX, reaction_string):
#         return rxn.OutputReaction(reaction_string)
#
#     subject, verb, object = _reaction_string_to_subject_verb_object_strings(reaction_string)
#
#     subject = specification_from_string(subject)
#     verb = rxn.Verb(verb.lower())
#     object = specification_from_string(object)
#
#     try:
#         reaction_definition = rxn.VERB_REACTION_TABLE[verb]
#
#     except KeyError:
#         raise err.RxnConParseError('The verb {} could not be found in the reaction lookup table'.format(verb))
#
#     category, directionality, influence, isomerism, modifier = reaction_definition
#
#     return rxn.Reaction(subject, verb, object, category, directionality, influence, isomerism, modifier)
#
#
# @tc.typecheck
# def _reaction_string_to_subject_verb_object_strings(reaction_string: str) -> Tuple[str, str, str]:
#     known_verbs = [v.value for v in rxn.Verb]
#     delimiters = ['_' + verb + '_' for verb in known_verbs]
#
#     matches = 0
#     verb_position, object_position = 0, 0
#
#     for delimiter in delimiters:
#         splitted = reaction_string.lower().split(delimiter)
#
#         if len(splitted) > 1:
#             matches += 1
#
#             if len(splitted) != 2:
#                 raise err.RxnConParseError('Incorrect S-V-O in reaction string {}'.format(reaction_string))
#
#             verb_position = len(splitted[0]) + 1
#             object_position = verb_position + len(delimiter) - 1
#
#     if matches == 0:
#         raise err.RxnConParseError('Unknown verb in reaction string {}'.format(reaction_string))
#
#     elif matches > 1:
#         raise err.RxnConParseError('Ambiguous verb in reaction string {}'.format(reaction_string))
#
#     subject_string = reaction_string[0:verb_position-1]
#     verb_string = reaction_string[verb_position:object_position-1]
#     object_string = reaction_string[object_position:]
#
#     return subject_string, verb_string, object_string


# @tc.typecheck
# def state_from_string(state_string: str) -> sta.State:
#     OUTPUT_REGEX = '^\[.+?\]$'
#     INTERACTION_REGEX = '^.+?--.+?$'
#     MODIFIER_REGEX = '.+?-{.+?}'
#     MODIFIER_VALUE_REGEX = '{.+?}'
#     COMPONENT_REGEX = '\w'
#
#     assert isinstance(state_string, str)
#
#     if re.match(INTERACTION_REGEX, state_string):
#         return _interaction_state_from_string(state_string)
#
#     elif re.match(MODIFIER_REGEX, state_string):
#         modifier_string = re.search(MODIFIER_VALUE_REGEX, state_string).group(0).strip('{}').lower()
#
#         # @todo Maybe this is a bit dirty.
#         try:
#             modifier = sta.StateModifier(modifier_string)
#             return _covalent_modification_state_from_string(state_string, modifier)
#
#         except ValueError:
#             return _translocation_state_from_string(state_string)
#
#     elif re.match(OUTPUT_REGEX, state_string):
#         return sta.GlobalQuantityState(state_string)
#     elif re.match(COMPONENT_REGEX, state_string):
#         return _component_state_from_string(state_string)
#     else:
#         raise err.RxnConParseError('Could not parse state string {} into State'.format(state_string))
#
#
# @tc.typecheck
# def _interaction_state_from_string(state_string: str) -> Union[sta.InteractionState,
#                                                                sta.SelfInteractionState]:
#     component_strings = state_string.split('--')
#
#     if component_strings[1].startswith('['):
#         first_component = specification_from_string(component_strings[0])
#         second_component = specification_from_string("{0}_{1}".format(first_component.name, component_strings[1]))
#
#         return sta.SelfInteractionState(first_component, second_component)
#
#     else:
#         first_component = specification_from_string(component_strings[0])
#         second_component = specification_from_string(component_strings[1])
#
#         return sta.InteractionState(first_component, second_component)
#
#
# @tc.typecheck
# def _covalent_modification_state_from_string(state_string: str, modifier: sta.StateModifier) -> sta.CovalentModificationState:
#     substrate_string = state_string.split('-{')[0]
#     substrate = specification_from_string(substrate_string)
#
#     return sta.CovalentModificationState(substrate, modifier)
#
#
# def _component_state_from_string(state_string: str):
#     return sta.ComponentState(specification_from_string(state_string))
#
#
# @tc.typecheck
# def _translocation_state_from_string(state_string) -> sta.TranslocationState:
#     # @todo Implement this.
#     pass
#
