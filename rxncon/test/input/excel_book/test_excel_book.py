import os

from rxncon.input.excel_book.excel_book import ExcelBook
from rxncon.simulation.boolean.boolean_model import boolean_model_from_rxncon


CELL_CYCLE_XLS = os.path.join(os.path.dirname(__file__), 'cell_cycle_toy_model.xls')
PHEROMONE_XLS  = os.path.join(os.path.dirname(__file__), 'pheromone.xls')
SPS_XLS        = os.path.join(os.path.dirname(__file__), 'sps.xls')
CIRCADIAN_XLS  = os.path.join(os.path.dirname(__file__), 'CircadianClock.xls')

def test_cell_cycle_toy_model():
    book = ExcelBook(CELL_CYCLE_XLS)
    print('hallo')


def test_pheromone():
    book = ExcelBook(PHEROMONE_XLS)
    system = book.rxncon_system
    boolean = boolean_model_from_rxncon(system)
    print('hallo')

def test_sps():
    book = ExcelBook(SPS_XLS)
    system = book.rxncon_system
    print('hallo')

def test_circadian():
    book = ExcelBook(CIRCADIAN_XLS)
    system = book.rxncon_system
    boolean = boolean_model_from_rxncon(system)
    print('hallo')
