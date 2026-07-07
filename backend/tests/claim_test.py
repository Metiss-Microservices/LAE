def test_claim_status_values():

    allowed = [

        "pending",

        "race",

        "won",

        "lost",

        "expired"
    ]

    assert "won" in allowed

    assert "lost" in allowed
