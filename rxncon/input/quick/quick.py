from typing import List

import rxncon.input.rxncon_input as inp
import rxncon.core.rxncon_system as rxs
import rxncon.input.shared.contingency_list as cli
import rxncon.syntax.rxncon_from_string as fst


class Quick(inp.RxnConInput):
    def __init__(self, rxncon_string: str):
        assert isinstance(rxncon_string, str)
        self.quick_input = rxncon_string.split("\n")  # seperating the input into lines
        self._reactions = []                    # type: List[rxn.Reaction]
        self._contingencies = []                # type: List[con.Contingency]
        self._contingency_list_entries = []     # type: List[cli.ContingencyListEntry]
        self._rxncon_system = None              # type: rxs.RxnConSystem

        self._parse_str()
        self._construct_contingencies()
        self._construct_rxncon_system()

    @property
    def rxncon_system(self) -> rxs.RxnConSystem:
        return self._rxncon_system

    def _parse_str(self):
        # @basti You can leave out the docstrings for now. Furthermore in this case it's rather obvious what this function does :)
        """
        parsing the input
        :return:
        """
        assert isinstance(self.quick_input, list)
        for line in self.quick_input:
            full_reaction_str = line.split(";")[0].strip()
            contingencies = line.split(";")[1:]
            if full_reaction_str:  # as long as we have a full_reaction != ""
                # @basti For simple methods with no optional arguments, preferably don't use the 'named_argument=xxx' syntax,
                #        just do 'self._add_reactions(full_reaction_str)
                if full_reaction_str[0] != "<":
                    # @basti To be pedantic, I would parse the reaction string here, and change the _add_reaction function
                    #        to one that accepts a 'Reaction' object. That way both this function and that really do what their
                    #        name suggests.
                    self._add_reactions(full_reaction_str=full_reaction_str)
                self._add_contingencies(contingencies=contingencies, full_reaction_str=full_reaction_str)

    # @basti This should be called 'add_reaction' (singular)?
    def _add_reactions(self, full_reaction_str: str):
        """
        converting a full_reaction_str into reaction object
        :param full_reaction_str: str
        :return: None
        """
        assert isinstance(full_reaction_str, str)
        reaction = fst.reaction_from_string(full_reaction_str)
        self._reactions.append(reaction)

    # @basti Leave out the :param part of the docstrings. It's covered by having type annotations in the function header.
    def _add_contingencies(self, contingencies: List[str], full_reaction_str: str):
        """
        itterating over the lists of contingencies and converting them into contingenccy objects
        :param contingencies: List[str]
        :param full_reaction_str:  str
        :return: None
        """
        assert isinstance(contingencies, list)
        for cont in contingencies:
            cont = cont.strip()
            cont_type = cont.split()[0]
            modifier = cont.split()[-1]
            entry = cli.contingency_list_entry_from_subject_predicate_agent_strings(
                full_reaction_str, cont_type, modifier)
            self._contingency_list_entries.append(entry)

    def _construct_contingencies(self):
        self._contingencies = cli.contingencies_from_contingency_list_entries(self._contingency_list_entries)

    def _construct_rxncon_system(self):
        pass

# @basti This should go: I guess it's just for trying out stuff?
if __name__ == "__main__":
    quick = Quick("""A_ppi_B; ! <bool>
                    <bool>; AND A--C
                    <bool>; AND A--D
                    <bool>; AND B--E
                  """)