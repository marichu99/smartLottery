import time
from scripts.helpful import get_account,get_contract,fund_with_link
from brownie import Lottery,config,network

def deploy_lottery():
   account=get_account()
   lottery=Lottery.deploy(get_contract("eth_usd_price_feed").address,
   get_contract("vrf_coordinator").address,
   get_contract("link_token").address,
   config["networks"][network.show_active()]["fee"],
   config["networks"][network.show_active()]["keyhash"],                     
   {"from":account},publish_source=config["networks"][network.show_active()].get("verify",False))
   
   return lottery
   
    
    
                   

# start the lottery
def start_lottery():
    # get the player account
    account=get_account()
    # get the latest deployed lottery contract
    lottery=Lottery[-1]
    # call the start lottery function
    startin_tx= lottery.startLottery({"from":account})
    startin_tx.wait(1)
    print("The lottery has been started")

# enter the lottery
def enter_lottery():
    # get the account
    account=get_account()
    lottery=Lottery[-1]
    # get the entrance fee
    entrance_value=lottery.getEntranceFee() +100000000
    # enter the lottery
    tx= lottery.enter({"from":account, "value":entrance_value})
    tx.wait(1)
    print("We have entered the lottery")
# end the lottery
def end_lottery():
    account=get_account()
    lottery=Lottery[-1]
    # fund with link
    tx=fund_with_link(lottery.address)
    tx.wait(1)
    # end the lottery
    ending_tx=lottery.endLottery({"from":account})
    ending_tx.wait(1)
    time.sleep(60)
    # declare the winner
    print(f"The winner of the lottery is {lottery.recentWinner()}")




# function that gets called
def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()