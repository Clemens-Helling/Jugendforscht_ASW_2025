from test import add, devide
import pytest
def test_add():
    result= add(1, 2)
    assert result == 3

def test_devide():
    result= devide(10, 1)
    assert result == 10 
    with pytest.raises(ZeroDivisionError):
        10/0