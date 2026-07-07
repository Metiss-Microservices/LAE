from wallet.pricing import (
    toman_to_credit,
    credit_to_toman
)


def test_credit_conversion():

    credit = toman_to_credit(
        100000
    )

    assert credit > 0


def test_reverse_conversion():

    amount = credit_to_toman(
        10
    )

    assert amount > 0
