
from brownie import Lottery,accounts,network,config,exceptions

import pytest
from scripts.deploy import deploy_lottery
from web3 import  Web3
from scripts.helpful import LOCAL_BLOCKCHAIN_ENVIRONMENTS,get_account,fund_with_link,get_contract
# only test this on local blockchain environments because its a unit test
def test_get_entrance_fee():
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip()
   # deploy the lottery contract
   # Arrange
   lottery=deploy_lottery()
   # Act
   expected_entrance_fee= Web3.toWei(0.025,"ether")
   entrance_fee=lottery.getEntranceFee()
   # Assert
   assert expected_entrance_fee == entrance_fee
def test_cant_enter_unless_started():
   # arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip()
   lottery=deploy_lottery()
   account=get_account()
   # try to enter a lottery that has not started yet
   # act/assert
   with pytest.raises(exceptions.VirtualMachineError):
      # try entering the lottery
      lottery.enter({"from":account,"value":lottery.getEntranceFee()})

def test_can_start_and_enter_lottery():
   # arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip()
   lottery=deploy_lottery()
   account=get_account()
   # act
   # start the lottery
   lottery.startLottery({"from":account})
   # enter lottery
   lottery.enter({"from":account,"value":lottery.getEntranceFee()})
   # assert
   assert lottery.players(0) ==account
def test_can_end_lottery():
   # arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip()
   lottery= deploy_lottery()
   account= get_account()
   # start lottery
   lottery.startLottery({"from":account})
   # enter lottery
   lottery.enter({"from":account,"value":lottery.getEntranceFee()})
   # fund with link
   fund_with_link(lottery)
   # end the lottery
   lottery.endLottery({"from":account})

   # assert
   assert lottery.lottery_state() ==2
 
# choosing the winner
def test_can_pick_winner_correctly():
   # arrange
   if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
      pytest.skip()
   
   lottery= deploy_lottery()
   account=get_account()
   account2= get_account(index=1)
   account3=get_account(index=2)
   # start the lottery
   lottery.startLottery({"from":account})
   # enter multiple users into the lottery
   lottery.enter({"from":account,"value":lottery.getEntranceFee()})
   print(f" Account 1 {account}")
   lottery.enter({"from":account2,"value":lottery.getEntranceFee()})
   print(f" Account 2 {account2}")
   lottery.enter({"from":account3,"value":lottery.getEntranceFee()})
   print(f" Account 3 {account3}")
   print(f"The players array length is {lottery.number_players()}")
   # fund contract with some link
   fund_with_link(lottery)
   # end the lottery
   transaction =lottery.endLottery({"from":account})
   # get the event
   request_id=transaction.events["RequestedRandomness"]["requestId"]
   # dummy getting a response from a chainlink node
   STATIC_RAND= 777
   get_contract("vrf_coordinator").callBackWithRandomness(request_id,STATIC_RAND,lottery.address)
   print(f"the recent winner is {lottery.recentWinner()}")

   # if 777%3 ==0 then the winner will be the player at the first index in the players array
   starting_account_balance= account.balance()
   lottery_balance= lottery.balance()
   # assert
   assert lottery.number_players() == 3
   assert lottery.recentWinner() == account
   # the lottery should have no money
   assert lottery.balance() == 0
   # the recent winner has all the funds from the lottery
   assert account.balance() == starting_account_balance +lottery_balance
  
   