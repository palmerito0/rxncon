import input.shared.from_string as fst
import core.state as sta


# Component from string #
def test_from_string_component_without_domain():
    component = fst.component_from_string('Sln1')

    assert component.full_name == 'Sln1'
    assert str(component) == 'Sln1'
    assert component.name == 'Sln1'
    assert component.domain is None
    assert component.subdomain is None
    assert component.residue is None


def test_from_string_component_with_domain():
    component = fst.component_from_string('Pkc1_[HR1]')

    assert component.full_name == 'Pkc1_[HR1]'
    assert str(component) == 'Pkc1_[HR1]'
    assert component.name == 'Pkc1'
    assert component.domain == 'HR1'
    assert component.subdomain is None
    assert component.residue is None


def test_from_string_component_with_domain_and_subdomain():
    component = fst.component_from_string('Pbs2_[RSD2/PR]')

    assert component.full_name == 'Pbs2_[RSD2/PR]'
    assert str(component) == 'Pbs2_[RSD2/PR]'
    assert component.name == 'Pbs2'
    assert component.domain == 'RSD2'
    assert component.subdomain == 'PR'
    assert component.residue is None


def test_from_string_component_with_domain_and_residue():
    component = fst.component_from_string('Sln1_[HK(H576)]')

    assert component.full_name == 'Sln1_[HK(H576)]'
    assert str(component) == 'Sln1_[HK(H576)]'
    assert component.name == 'Sln1'
    assert component.domain == 'HK'
    assert component.subdomain is None
    assert component.residue == 'H576'


def test_from_string_component_with_domain_and_subdomain_and_residue():
    component = fst.component_from_string('A_[B/C(D)]')
    assert component.full_name == 'A_[B/C(D)]'
    assert str(component) == 'A_[B/C(D)]'
    assert component.name == 'A'
    assert component.domain == 'B'
    assert component.subdomain == 'C'
    assert component.residue == 'D'


# Reaction from string #
def test_from_string_reaction_ppi():
    reaction = fst.reaction_from_string('Fus3_[CD]_ppi_Msg5_[n]')

    assert reaction.classification_code == '2.1.1.1'

    assert reaction.subject.name == 'Fus3'
    assert reaction.subject.domain == 'CD'
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Msg5'
    assert reaction.object.domain == 'n'
    assert reaction.object.subdomain is None
    assert reaction.object.residue is None

    assert reaction.source is None
    assert reaction.product.full_name == 'Fus3_[CD]--Msg5_[n]'


def test_from_string_reaction_i():
    reaction = fst.reaction_from_string('Pkc1_i_PS')

    assert reaction.classification_code == '2.1.1.1'

    assert reaction.subject.name == 'Pkc1'
    assert reaction.subject.domain is None
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'PS'
    assert reaction.object.domain is None
    assert reaction.object.subdomain is None
    assert reaction.object.residue is None

    assert reaction.source is None
    assert reaction.product.full_name == 'Pkc1--PS'


def test_from_string_reaction_bind():
    reaction = fst.reaction_from_string('Tec1_[n/TEA]_BIND_TCS')

    assert reaction.classification_code == '2.1.1'

    assert reaction.subject.name == 'Tec1'
    assert reaction.subject.domain == 'n'
    assert reaction.subject.subdomain == 'TEA'
    assert reaction.subject.residue is None

    assert reaction.object.name == 'TCS'
    assert reaction.object.domain is None
    assert reaction.object.subdomain is None
    assert reaction.object.residue is None

    assert reaction.source is None
    assert reaction.product.full_name == 'Tec1_[n/TEA]--TCS'


def test_from_string_reaction_p_plus():
    reaction = fst.reaction_from_string('Fus3_[KD]_P+_Sst2_[(S539)]')

    assert reaction.classification_code == '1.1.1'

    assert reaction.subject.name == 'Fus3'
    assert reaction.subject.domain == 'KD'
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Sst2'
    assert reaction.object.domain is None
    assert reaction.object.subdomain is None
    assert reaction.object.residue == 'S539'

    assert reaction.source is None
    assert reaction.product.full_name == 'Sst2_[(S539)]-{P}'


def test_from_string_reaction_p_minus():
    reaction = fst.reaction_from_string('Msg5_[PD]_P-_Slt2_[(Y192)]')

    assert reaction.classification_code == '1.1.2'

    assert reaction.subject.name == 'Msg5'
    assert reaction.subject.domain == 'PD'
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Slt2'
    assert reaction.object.domain is None
    assert reaction.object.subdomain is None
    assert reaction.object.residue == 'Y192'

    assert reaction.source.full_name == 'Slt2_[(Y192)]-{P}'
    assert reaction.product is None


def test_from_string_reaction_gef():
    reaction = fst.reaction_from_string('Rom2_[DH]_GEF_Rho1_[GnP]')

    assert reaction.classification_code == '1.1.1'

    assert reaction.subject.name == 'Rom2'
    assert reaction.subject.domain == 'DH'
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Rho1'
    assert reaction.object.domain == 'GnP'
    assert reaction.object.subdomain is None
    assert reaction.object.residue is None

    assert reaction.source is None
    assert reaction.product.full_name == 'Rho1_[GnP]-{P}'


def test_from_string_reaction_gap():
    reaction = fst.reaction_from_string('Lrg1_[GAP]_GAP_Rho1_[GnP]')

    assert reaction.classification_code == '1.1.2'

    assert reaction.subject.name == 'Lrg1'
    assert reaction.subject.domain == 'GAP'
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Rho1'
    assert reaction.object.domain == 'GnP'
    assert reaction.object.subdomain is None
    assert reaction.object.residue is None

    assert reaction.source.full_name == 'Rho1_[GnP]-{P}'
    assert reaction.product is None


def test_from_string_reaction_ub_plus():
    reaction = fst.reaction_from_string('SCF_Ub+_Tec1')

    assert reaction.classification_code == '1.1.1'

    assert reaction.subject.name == 'SCF'
    assert reaction.subject.domain is None
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Tec1'
    assert reaction.object.domain is None
    assert reaction.object.subdomain is None
    assert reaction.object.residue is None

    assert reaction.source is None
    assert reaction.product.full_name == 'Tec1-{Ub}'


def test_from_string_reaction_ap():
    reaction = fst.reaction_from_string('Rck2_AP_Rck2_[Ser]')

    assert reaction.classification_code == '1.1.1'

    assert reaction.subject.name == 'Rck2'
    assert reaction.subject.domain is None
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Rck2'
    assert reaction.object.domain == 'Ser'
    assert reaction.object.subdomain is None
    assert reaction.object.residue is None

    assert reaction.source is None
    assert reaction.product.full_name == 'Rck2_[Ser]-{P}'


def test_from_string_reaction_pt():
    reaction = fst.reaction_from_string('Sln1_[HK(H576)]_PT_Sln1_[RR(D1144)]')

    assert reaction.classification_code == '1.1.3'

    assert reaction.subject.name == 'Sln1'
    assert reaction.subject.domain == 'HK'
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue == 'H576'

    assert reaction.object.name == 'Sln1'
    assert reaction.object.domain == 'RR'
    assert reaction.object.subdomain is None
    assert reaction.object.residue == 'D1144'

    assert reaction.source.full_name == 'Sln1_[HK(H576)]-{P}'
    assert reaction.product.full_name == 'Sln1_[RR(D1144)]-{P}'


def test_from_string_reaction_deg():
    reaction = fst.reaction_from_string('Bar1_[PepD]_DEG_MFalpha_[(L6-K7)]')

    assert reaction.classification_code == '3.2.2'

    assert reaction.subject.name == 'Bar1'
    assert reaction.subject.domain == 'PepD'
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'MFalpha'
    assert reaction.object.domain is None
    assert reaction.object.subdomain is None
    assert reaction.object.residue == 'L6-K7'

    assert reaction.source.full_name == 'MFalpha_[(L6-K7)]'
    assert reaction.product is None


def test_from_string_reaction_cut():
    reaction = fst.reaction_from_string('Yps1_CUT_Msb2_[HMH/CD]')

    assert reaction.classification_code == '1.2.1'

    assert reaction.subject.name == 'Yps1'
    assert reaction.subject.domain is None
    assert reaction.subject.subdomain is None
    assert reaction.subject.residue is None

    assert reaction.object.name == 'Msb2'
    assert reaction.object.domain == 'HMH'
    assert reaction.object.subdomain == 'CD'
    assert reaction.object.residue is None

    assert reaction.source is None
    assert reaction.product.full_name == 'Msb2_[HMH/CD]-{Truncated}'


# State from string
def test_from_string_state_interaction():
    state = fst.state_from_string('Fus3_[CD]--Msg5_[n]')

    assert isinstance(state, sta.InteractionState)
    assert state.full_name == 'Fus3_[CD]--Msg5_[n]'
    assert state.first_component.full_name == 'Fus3_[CD]'
    assert state.second_component.full_name == 'Msg5_[n]'


def test_from_string_state_phosphorylation():
    state = fst.state_from_string('Slt2_[(Y192)]-{P}')

    assert isinstance(state, sta.CovalentModificationState)
    assert state.full_name == 'Slt2_[(Y192)]-{P}'
    assert state.substrate.full_name == 'Slt2_[(Y192)]'
    assert state.modifier == sta.StateModifier.phosphor
