from brownie import Contract, accounts,config,network,MockV3Aggregator,VRFCoordinatorMock,LinkToken

FORKED_LOCAL_ENVIRONMENTS=["mainnet-fork","mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS=["development","ganache-local"]
def get_account(index=None,id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS):
        account=accounts[0]
        return account
  
    return accounts.add(config["wallets"]["from_key"])
# create a mapping between contract types and their mock contracts
contract_to_mock={
    "eth_usd_price_feed":MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}
def get_contract(contract_name):
    """
    This function will grab contract addresses from the brownie config if defined, otherwise, it will deploy a 
    mock version of that contract and return that mock contract

    Args: contract_name(String)
    Returns: most recently deployed version of this contract

    """
    contract_type=contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
    #   check if any mocks have been deployed
        if len(contract_type) <=0:
            deploy_mocks()
        contract=contract_type[-1]
    else:
        contract_address=config["networks"][network.show_active()][contract_name]
        contract=Contract.from_abi(contract_type._name,contract_address,contract_type.abi)
    return contract


DECIMALS=8
INITIAL_VALUE=200000000000
def deploy_mocks(decimals=DECIMALS,initial_value=INITIAL_VALUE):
    account=get_account()
    MockV3Aggregator.deploy(decimals,initial_value,{"from":account})
    link_token=LinkToken.deploy({"from":account})
    VRFCoordinatorMock.deploy(link_token.address,{"from":account})
    print("Deployed!")
def fund_with_link(contract_address, account=None, link_token=None, amount=250000000000000000):
    if account:
        account=account
    else: 
        account=get_account()
    if link_token:
        link_token=link_token
    else:
        link_token=get_contract("link_token")
    # interact with the deployed contract
    tx= link_token.transfer(contract_address,amount,{"from":account})
    tx.wait(1)
    print("Contract is funded")
    return tx