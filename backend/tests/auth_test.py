from identity.service import (
    create_access_token,
    verify_access_token
)


def test_token_roundtrip():

    token = create_access_token(

        supplier_id="123",

        role="supplier"
    )

    payload = verify_access_token(
        token
    )

    assert payload is not None

    assert (
        payload["supplier_id"]
        ==
        "123"
    )

    assert (
        payload["role"]
        ==
        "supplier"
    )
