from brownie import network
import pytest
from scripts.helpful import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link,get_account
from scripts.deploy import deploy_lottery
import time

def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery= deploy_lottery()
    account= get_account()
    # start lottery
    lottery.startLottery({"from":account})
    # enter the lottery
    lottery.enter({"from":account,"value":lottery.getEntranceFee()})
    lottery.enter({"from":account,"value":lottery.getEntranceFee()})
    # fund with link
    fund_with_link(lottery)
    # end the lottery
    lottery.endLottery({"from":account})
    time.sleep(60)

    # assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0