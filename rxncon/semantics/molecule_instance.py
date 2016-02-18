from typing import Set, Optional, Tuple

import typecheck as tc

from rxncon.semantics.molecule_definition import MoleculeDefinition, ModificationPropertyDefinition, AssociationPropertyDefinition, \
    LocalizationPropertyDefinition, Modifier, OccupationStatus, Compartment

import rxncon.core.specification as spe


class MoleculeInstance:
    @tc.typecheck
    def __init__(self,
                 mol_def: MoleculeDefinition,
                 modification_properties: Set['ModificationPropertyInstance'],
                 association_properties: Set['AssociationPropertyInstance'],
                 localization_property: Optional['LocalizationPropertyInstance']):
        self.mol_def = mol_def
        self.modification_properties = modification_properties
        self.association_properties = association_properties
        self.localization_property = localization_property

    @tc.typecheck
    def __eq__(self, other: 'MoleculeInstance'):
        return isinstance(other, MoleculeInstance) and \
            self.mol_def == other.mol_def and \
            self.localization_property == other.localization_property and \
            self.modification_properties == other.modification_properties and \
            self.association_properties == other.association_properties

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return 'MoleculeSpecification: {0}, mod_instances = {1}. assoc_instances = {2}. loc_instances = {3}'\
            .format(self.mol_def.spec, ', '.join([str(x) for x in self.modification_properties]),
                    ', '.join(str(x) for x in self.association_properties), str(self.localization_property))


class PropertyInstance:
    pass


class ModificationPropertyInstance(PropertyInstance):
    @tc.typecheck
    def __init__(self, modification_def: ModificationPropertyDefinition, modifier: 'Modifier'):
        self.modification_def = modification_def
        self.modifier = modifier
        self._validate()

    @tc.typecheck
    def __eq__(self, other: PropertyInstance) -> bool:
        return isinstance(other, ModificationPropertyInstance) and self.modification_def == other.modification_def and \
            self.modifier == other.modifier

    def __hash__(self) -> bool:
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return 'ModificationSpecification: Domain = {0}, Modifier = {1}'\
            .format(self.modification_def.spec, self.modifier)

    def _validate(self):
        if self.modifier not in self.modification_def.valid_modifiers:
            raise ValueError('Modifier {0} does not appear in Set of valid modifiers for domain {1}.'
                             .format(self.modifier, self.modification_def.spec))

    def complementary_instances(self):
        return [ModificationPropertyInstance(self.modification_def, modifier) for modifier
                in self.modification_def.valid_modifiers if modifier != self.modifier]


class AssociationPropertyInstance(PropertyInstance):
    @tc.typecheck
    def __init__(self, association_def: AssociationPropertyDefinition, occupation_status: 'OccupationStatus',
                 partner: Optional[spe.Specification]):
        self.association_def = association_def
        self.occupation_status = occupation_status
        self.partner = partner

        self._validate()

    @tc.typecheck
    def __eq__(self, other: PropertyInstance) -> bool:
        if not isinstance(other, AssociationPropertyInstance):
            return False

        if self.partner and other.partner:
            return self.association_def == other.association_def and self.occupation_status == other.occupation_status and self.partner == other.partner
        elif not self.partner and not other.partner:
            return self.association_def == other.association_def and self.occupation_status == other.occupation_status
        else:
            return False

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return 'AssociationInstance: Domain = {0}, occupation_status = {1}, partner = {2}'\
            .format(self.association_def.spec, self.occupation_status, self.partner)

    def complementary_instances(self):
        if self.occupation_status == OccupationStatus.occupied_known_partner:
            unoccupied = AssociationPropertyInstance(self.association_def, OccupationStatus.not_occupied, None)
            other_partners = [AssociationPropertyInstance(self.association_def, OccupationStatus.occupied_known_partner, x)
                              for x in self.association_def.valid_partners if x != self.partner]

            return other_partners + [unoccupied]
        elif self.occupation_status == OccupationStatus.not_occupied:
            return [AssociationPropertyInstance(self.association_def, OccupationStatus.occupied_known_partner, x)
                    for x in self.association_def.valid_partners]
        else:
            raise NotImplementedError

    def _validate(self):
        # For associations the molecule/domain/subdomain spec should match exactly.
        if self.partner:
            assert self.partner in self.association_def.valid_partners

        if self.occupation_status == OccupationStatus.not_occupied:
            assert not self.partner


class LocalizationPropertyInstance(PropertyInstance):
    @tc.typecheck
    def __init__(self, localization_def: LocalizationPropertyDefinition, compartment: Compartment):
        self.localization_def = localization_def
        self.compartment = compartment
        self._validate()

    @tc.typecheck
    def __eq__(self, other: PropertyInstance) -> bool:
        return isinstance(other, LocalizationPropertyInstance) and self.localization_def == other.localization_def and \
            self.compartment == other.compartment

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return 'LocalizationSpecification: {0}'.format(self.compartment)

    def _validate(self):
        if self.compartment not in self.localization_def.valid_compartments:
            raise ValueError('Compartment {0} does not appear in Set of valid compartments {1}.'
                             .format(self.compartment, ', '.join(str(x) for x in self.localization_def.valid_compartments)))

    def complementary_instances(self):
        return [LocalizationPropertyInstance(self.localization_def, compartment) for compartment
                in self.localization_def.valid_compartments if compartment != self.compartment]


class Binding:
    @tc.typecheck
    def __init__(self, left_partner: Tuple[int, AssociationPropertyInstance], right_partner: Tuple[int, AssociationPropertyInstance]):
        self.left_partner = left_partner
        self.right_partner = right_partner
        self._validate()

    @tc.typecheck
    def __eq__(self, other: 'Binding'):
        return self.left_partner == other.left_partner and self.right_partner == other.right_partner

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return 'Binding: L_molecule_index = {0}, L_domain = {1}, R_molecule_index = {2}, R_domain = {3}'\
            .format(self.left_partner[0], self.left_partner[1].association_def.spec,
                    self.right_partner[0], self.right_partner[1].association_def.spec)

    def _validate(self):
        if not self.left_partner[1].occupation_status or not self.right_partner[1].occupation_status:
            raise ValueError('Binding requires both partners to have occupied association domains.')

        if self.left_partner[0] == self.right_partner[0]:
            raise ValueError('Binding-molecule-indices are required to be distinct for each binding.')