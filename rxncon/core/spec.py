from collections import OrderedDict
from typecheck import typecheck
from abc import ABCMeta, abstractmethod
from typing import Optional
from enum import Enum, unique
import re

from rxncon.util.utils import OrderedEnum

EMPTY_SPEC = '0'

class Spec(metaclass=ABCMeta):
    @typecheck
    def __init__(self, component_name: str, struct_index: Optional[int], locus: 'Locus'):
        self.component_name, self.struct_index, self.locus = component_name, struct_index, locus
        self._validate()

    def __hash__(self) -> int:
        return hash(str(self))

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return _string_from_spec(self)

    @typecheck
    def __eq__(self, other: 'Spec') -> bool:
        return isinstance(other, type(self)) and self.component_name == other.component_name and self.locus == other.locus

    @typecheck
    def __lt__(self, other: 'Spec') -> bool:
        if self.component_name < other.component_name:
            return True
        elif self.component_name == other.component_name:
            return self.locus < other.locus
        return False

    def _validate(self):
        assert self.component_name is not None and re.match("\w+", self.component_name)

    @typecheck
    def is_equivalent_to(self, other: 'Spec') -> bool:
        return self == other or type(self) == type(other) and self.locus.residue == other.locus.residue and \
                                self.struct_index == other.struct_index

    @typecheck
    def is_subspec_of(self, other: 'Spec') -> bool:
        if self.is_equivalent_to(other):
            return True

        spec_pairs = zip([self.component_name, self.locus.domain, self.locus.subdomain, self.locus.residue],
                         [other.component_name, other.locus.domain, other.locus.subdomain, other.locus.residue])

        for my_property, other_property in spec_pairs:
            if my_property and other_property and my_property != other_property:
                return False

            elif not my_property and other_property:
                return False

        return True

    @typecheck
    def is_superspec_of(self, other: 'Spec') -> bool:
        if self.is_equivalent_to(other):
            return True

        return other.is_subspec_of(self)

    @property
    def is_component_spec(self) -> bool:
        return self.has_resolution(LocusResolution.component)

    @abstractmethod
    def to_component_spec(self) -> 'Spec':
        pass

    def to_dna_component_spec(self) -> 'DnaSpec':
        return DnaSpec(self.component_name, self.struct_index, EmptyLocus())

    def to_rna_component_spec(self) -> 'MRnaSpec':
        return MRnaSpec(self.component_name, self.struct_index, EmptyLocus())

    def to_protein_component_spec(self) -> 'ProteinSpec':
        return ProteinSpec(self.component_name, self.struct_index, EmptyLocus())

    @property
    def resolution(self) -> 'LocusResolution':
        return self.locus.resolution

    @typecheck
    def has_resolution(self, resolution: 'LocusResolution') -> bool:
        return self.resolution == resolution


class EmptySpec(Spec):
    def __init__(self):
        super().__init__(EMPTY_SPEC, None, EmptyLocus())

    def _validate(self):
        assert self.component_name == EMPTY_SPEC
        assert self.locus.is_empty

    def __hash__(self) -> int:
        return hash(str(self))

    def __str__(self) -> str:
        return EMPTY_SPEC

    @typecheck
    def __eq__(self, other: 'Spec') -> bool:
        return isinstance(other, EmptySpec)

    @typecheck
    def __lt__(self, other: Spec) -> bool:
        if isinstance(other, EmptySpec):
            return super().__lt__(other)
        elif isinstance(other, ProteinSpec):
            return True
        elif isinstance(other, MRnaSpec):
            return True
        elif isinstance(other, DnaSpec):
            return True
        else:
            raise NotImplementedError

    def to_component_spec(self):
        raise AssertionError


class ProteinSpec(Spec):
    def __hash__(self):
        return hash(str(self))

    @typecheck
    def __eq__(self, other: Spec) -> bool:
        return isinstance(other, ProteinSpec) and self.component_name == other.component_name \
            and self.locus == other.locus and self.struct_index == other.struct_index

    @typecheck
    def __lt__(self, other: Spec) -> bool:
        if isinstance(other, ProteinSpec):
            return super().__lt__(other)
        elif isinstance(other, MRnaSpec):
            return False
        elif isinstance(other, DnaSpec):
            return False
        elif isinstance(other, EmptySpec):
            return False
        else:
            raise NotImplementedError

    def to_component_spec(self) -> 'ProteinSpec':
        return ProteinSpec(self.component_name, self.struct_index, EmptyLocus())


class MRnaSpec(Spec):
    def __hash__(self):
        return hash(str(self))

    @typecheck
    def __eq__(self, other: Spec) -> bool:
        return isinstance(other, MRnaSpec) and self.component_name == other.component_name \
            and self.locus == other.locus and self.struct_index == other.struct_index

    @typecheck
    def __lt__(self, other: Spec) -> bool:
        if isinstance(other, MRnaSpec):
            return super().__lt__(other)
        elif isinstance(other, DnaSpec):
            return False
        elif isinstance(other, ProteinSpec):
            return True
        elif isinstance(other, EmptySpec):
            return False
        else:
            raise NotImplementedError

    def to_component_spec(self) -> 'MRnaSpec':
        return MRnaSpec(self.component_name, self.struct_index, EmptyLocus())


class DnaSpec(Spec):
    def __hash__(self):
        return hash(str(self))

    @typecheck
    def __eq__(self, other: Spec) -> bool:
        return isinstance(other, DnaSpec) and self.component_name == other.component_name \
               and self.locus == other.locus and self.struct_index == other.struct_index

    @typecheck
    def __lt__(self, other: Spec):
        if isinstance(other, DnaSpec):
            return super().__lt__(other)
        elif isinstance(other, MRnaSpec):
            return True
        elif isinstance(other, ProteinSpec):
            return True
        elif isinstance(other, EmptySpec):
            return False
        else:
            raise NotImplementedError

    def to_component_spec(self) -> 'DnaSpec':
        return DnaSpec(self.component_name, self.struct_index, EmptyLocus())


class Locus:
    @typecheck
    def __init__(self, domain: Optional[str], subdomain: Optional[str], residue: Optional[str]):
        self.domain, self.subdomain, self.residue = domain, subdomain, residue
        self._validate()

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        if self.domain and self.subdomain and self.residue:
            return '{0}/{1}({2})'.format(self.domain, self.subdomain, self.residue)
        elif self.domain and not self.subdomain and self.residue:
            return '{0}({1})'.format(self.domain, self.residue)
        elif self.domain and self.subdomain and not self.residue:
            return '{0}/{1}'.format(self.domain, self.subdomain)
        elif not self.domain and not self.subdomain and self.residue:
            return '({0})'.format(self.residue)
        elif self.domain and not self.subdomain and not self.residue:
            return '{0}'.format(self.domain)
        elif not self.domain and not self.subdomain and not self.residue:
            return ''
        else:
            raise AssertionError

    @typecheck
    def __eq__(self, other) -> bool:
        return isinstance(other, Locus) and self.domain == other.domain \
            and self.subdomain == other.subdomain and self.residue == other.residue

    @typecheck
    def __lt__(self, other: 'Locus') -> bool:
        if self.domain is None and other.domain is not None:
            return True
        if other.domain is not None and other.domain is not None \
                and self.domain < other.domain:
            return True
        if self.subdomain is None and other.subdomain is not None:
            return True
        if self.subdomain is not None and other.subdomain is not None \
                and self.subdomain < other.subdomain:
            return True
        if self.residue is None and other.residue is not None:
            return True
        if self.residue is not None and other.residue is not None \
                and self.residue < other.residue:
            return True
        return False

    def _validate(self):
        if self.domain:
            assert re.match("\w+", self.domain)
        if self.subdomain:
            assert re.match("\w+", self.subdomain)
            assert self.domain is not None
        if self.residue:
            assert re.match("\w+", self.residue)

    @property
    def is_empty(self):
        return not (self.domain or self.subdomain or self.residue)

    @property
    def resolution(self) -> 'LocusResolution':
        if not self.domain and not self.subdomain and not self.residue:
            return LocusResolution.component
        elif self.domain and not self.subdomain and not self.residue:
            return LocusResolution.domain
        elif self.domain and self.subdomain and not self.residue:
            return LocusResolution.subdomain
        elif self.residue is not None:
            return LocusResolution.residue
        else:
            raise NotImplementedError


def EmptyLocus():
    return Locus(None, None, None)


class LocusResolution(Enum):
    component = 'component'
    domain    = 'domain'
    subdomain = 'subdomain'
    residue   = 'residue'


@unique
class SpecSuffix(OrderedEnum):
    mrna    = 'mRNA'
    dna     = 'DNA'
    protein = ''

suffix_to_spec = OrderedDict(
    [
        (SpecSuffix.mrna, MRnaSpec),
        (SpecSuffix.dna, DnaSpec),
        (SpecSuffix.protein, ProteinSpec)
    ]
)

spec_to_suffix = OrderedDict((k, v) for v, k in suffix_to_spec.items())

@typecheck
def _string_from_spec(spec: Spec) -> str:
    def struct_name(spec: Spec, suffix: SpecSuffix):
        if spec.struct_index:
            return "{0}{1}@{2}".format(spec.component_name, suffix.value, spec.struct_index)
        else:
            return "{0}{1}".format(spec.component_name, suffix.value)

    suffix = spec_to_suffix[type(spec)]

    if str(spec.locus):
        return '{0}_[{1}]'.format(struct_name(spec, suffix), str(spec.locus))
    else:
        return '{0}'.format(struct_name(spec, suffix))


@typecheck
def spec_from_string(spec_str: str) -> Spec:
    def _spec_from_suffixed_name_and_items(name, struct_index, domain, subdomain, residue):
        for suffix in suffix_to_spec:
            if name.endswith(suffix.value):
                name = name[:len(name) - len(suffix.value)]
                return suffix_to_spec[suffix](name, struct_index, Locus(domain, subdomain, residue))

        raise AssertionError('Could not parse spec component_name {}'.format(name))

    def _locus_items_from_string(full_locus_str):
        DOMAIN_SUBDOMAIN_RESIDUE_REGEX = '^[\w:-]+\/[\w:-]+\([\w:-]+\)$'
        DOMAIN_RESIDUE_REGEX = '^[\w:-]+\([\w:-]+\)$'
        DOMAIN_SUBDOMAIN_REGEX = '^[\w:-]+\/[\w:-]+$'
        RESIDUE_REGEX = '^\([\w:-]+\)$'
        DOMAIN_REGEX = '^[\w:-]+$'

        if re.match(DOMAIN_SUBDOMAIN_RESIDUE_REGEX, full_locus_str):
            domain = full_locus_str.split('/')[0]
            subdomain = full_locus_str.split('/')[1].split('(')[0]
            residue = full_locus_str.split('/')[1].split('(')[1].strip(')')

        elif re.match(DOMAIN_RESIDUE_REGEX, full_locus_str):
            domain = full_locus_str.split('(')[0]
            subdomain = None
            residue = full_locus_str.split('(')[1].strip(')')

        elif re.match(DOMAIN_SUBDOMAIN_REGEX, full_locus_str):
            domain = full_locus_str.split('/')[0]
            subdomain = full_locus_str.split('/')[1]
            residue = None

        elif re.match(RESIDUE_REGEX, full_locus_str):
            domain = None
            subdomain = None
            residue = full_locus_str.strip('()')

        elif re.match(DOMAIN_REGEX, full_locus_str):
            domain = full_locus_str
            subdomain = None
            residue = None

        else:
            raise SyntaxError('Could not parse locus string {}'.format(full_locus_str))

        return domain, subdomain, residue

    DOMAIN_DELIMITER = '_'
    STRUCT_DELIMITER = '@'

    struct_index = None
    items = spec_str.split(DOMAIN_DELIMITER, maxsplit=1)

    if items[0] == EMPTY_SPEC:
        return EmptySpec()
    elif STRUCT_DELIMITER in items[0]:
        name, struct_index = items[0].split(STRUCT_DELIMITER)
        struct_index = int(struct_index)
    else:
        name = items[0]

    if len(items) == 1:
        return _spec_from_suffixed_name_and_items(name, struct_index, None, None, None)
    elif len(items) == 2:
        locus_str = items[1].strip('[]')
        domain, subdomain, residue = _locus_items_from_string(locus_str)
        return _spec_from_suffixed_name_and_items(name, struct_index, domain, subdomain, residue)
    else:
        raise SyntaxError('Could not parse spec string {}'.format(spec_str))





