import pytest
import psycopg2
from src import db_manager
##https://docs.python.org/3/library/unittest.mock.html
def test_table_creation():
    db_manager.pk_constraint([])
    assert True
    pass


if __name__ == '__main__':
    pass