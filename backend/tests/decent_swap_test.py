import pytest
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
)
from algosdk.v2client.algod import AlgodClient

from smart_contracts.decent_swap import contract as decent_swap_contract


@pytest.fixture(scope="session")
def decent_swap_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return decent_swap_contract.app.build(algod_client)


@pytest.fixture(scope="session")
def decent_swap_client(
    algod_client: AlgodClient, decent_swap_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=decent_swap_app_spec,
        signer=get_localnet_default_account(algod_client),
    )
    client.create()
    return client


def test_says_hello(decent_swap_client: ApplicationClient) -> None:
    result = decent_swap_client.call(decent_swap_contract.hello, name="World")

    assert result.return_value == "Hello, World"
