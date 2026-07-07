from scoring.matching import (
    calculate_priority_multiplier
)


def test_matching_returns_score():

    score = calculate_priority_multiplier(

        priority_mode="smart",

        loc_score=50,

        rep_score=50,

        speed_score=50,

        price_score=50
    )

    assert score > 0


def test_nearest_priority():

    score = calculate_priority_multiplier(

        priority_mode="nearest",

        loc_score=80,

        rep_score=10,

        speed_score=10,

        price_score=10
    )

    assert score > 0
