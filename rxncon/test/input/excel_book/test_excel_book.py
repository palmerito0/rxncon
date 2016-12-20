import os

from rxncon.input.excel_book.excel_book import ExcelBook
from rxncon.simulation.rule_based.rule_based_model import rule_based_model_from_rxncon

CELL_CYCLE_XLS = os.path.join(os.path.dirname(__file__), 'cell_cycle_toy_model.xls')
INSULIN  = os.path.join(os.path.dirname(__file__), '../../../../test/insulin.xls')
SPS_XLS        = os.path.join(os.path.dirname(__file__), 'sps.xls')


def test_insulin():
    book = ExcelBook(INSULIN)
    system = book.rxncon_system

    rbm = rule_based_model_from_rxncon(system)

    for r in rbm.rules:
        print()
        print(r)

