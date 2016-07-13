import pytest
from collections import namedtuple

from rxncon.core.spec import Locus, MolSpec, DnaSpec, MRnaSpec, ProteinSpec, EmptyMolSpec, mol_spec_from_string, locus_from_string, \
    LocusResolution, bond_spec_from_string, spec_from_string



def test_loci():
    LocusTestCase = namedtuple('LocusTestCase',
                               ['locus_str', 'expected_domain', 'expected_subdomain', 'expected_residue'])

    locus_cases = [
        LocusTestCase('d', 'd', None, None),
        LocusTestCase('d/s', 'd', 's', None),
        LocusTestCase('d/s(r)', 'd', 's', 'r'),
        LocusTestCase('(r)', None, None, 'r')
    ]

    for locus_case in locus_cases:
        assert locus_from_string(locus_case.locus_str) == \
            Locus(locus_case.expected_domain, locus_case.expected_subdomain, locus_case.expected_residue)


def test_unstructured_specs():
    protein_spec = mol_spec_from_string('A_[dd/ss(rr)')
    # Protein
    assert isinstance(protein_spec, ProteinSpec)
    assert protein_spec.has_resolution(LocusResolution.residue)
    assert protein_spec.to_component_spec().has_resolution(LocusResolution.component)
    # DNA
    assert isinstance(protein_spec.to_dna_component_spec(), DnaSpec)
    assert protein_spec.to_dna_component_spec().has_resolution(LocusResolution.component)
    # mRNA
    assert isinstance(protein_spec.to_mrna_component_spec(), MRnaSpec)
    assert protein_spec.to_mrna_component_spec().has_resolution(LocusResolution.component)

    empty_spec = mol_spec_from_string('0')
    assert isinstance(empty_spec, EmptyMolSpec)


def test_structured_specs():
    protein_spec = mol_spec_from_string('A@0_[dd/ss(rr)')
    # Protein
    assert isinstance(protein_spec, ProteinSpec)
    assert protein_spec.has_resolution(LocusResolution.residue)
    assert protein_spec.to_component_spec().has_resolution(LocusResolution.component)
    assert protein_spec.struct_index == 0
    # DNA
    assert isinstance(protein_spec.to_dna_component_spec(), DnaSpec)
    assert protein_spec.to_dna_component_spec().has_resolution(LocusResolution.component)
    assert not protein_spec.to_dna_component_spec().struct_index
    # mRNA
    assert isinstance(protein_spec.to_mrna_component_spec(), MRnaSpec)
    assert protein_spec.to_mrna_component_spec().has_resolution(LocusResolution.component)
    assert not protein_spec.to_mrna_component_spec().struct_index

    with pytest.raises(SyntaxError):
        empty_spec = mol_spec_from_string('0@1')


def test_bond_specs():
    bond_spec = bond_spec_from_string('A_[x]~B_[y]')
    assert bond_spec.first == mol_spec_from_string('A_[x]')
    assert bond_spec.second == mol_spec_from_string('B_[y]')

    assert bond_spec_from_string('B_[y]~A_[x]') == bond_spec_from_string('A_[x]~B_[y]')

    assert bond_spec_from_string('A_[x]~0') == mol_spec_from_string('A_[x]')