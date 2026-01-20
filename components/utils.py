from decimal import Decimal as D

def two_d(value):
    ret_val = "{:,.2f}".format(D(value))
    return ret_val