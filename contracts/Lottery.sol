

// SPDX-License-Identifier: MIT

pragma solidity  ^0.6.6;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";




contract Lottery is VRFConsumerBase, Ownable{
    // array of all players
    address payable[] public players;
    uint256 public usdEntryFee;

    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    address payable public recentWinner;
    uint256 public randomness;
    uint256 public number_players;
    bytes32 public keyhash;
    event RequestedRandomness(bytes32 requestId);

    constructor(address _priceFeedAddress,
                address _vrfCoordinator, 
                address _linkToken,
                uint256 _fee,
                bytes32 _keyhash) 
    public VRFConsumerBase(_vrfCoordinator,_linkToken){
        usdEntryFee =50*(10**18);
        ethUsdPriceFeed =AggregatorV3Interface(_priceFeedAddress);
        lottery_state = LOTTERY_STATE.CLOSED;
        fee=_fee;
        keyhash=_keyhash;
    }

    // function to enter the lottery since it is payable
    function enter() public payable{
        require(lottery_state==LOTTERY_STATE.OPEN,"Lottery is not open");
        require(msg.value>=getEntranceFee(),"Not enough ETH, please use more");
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns(uint256){
        // 
      (,int price,,,) =ethUsdPriceFeed.latestRoundData();
      uint256 adjustedPrice = uint256(price) *(10**10);
      uint256 costToEnter = (usdEntryFee * 10**18)/adjustedPrice;
      return costToEnter;

    }

    function startLottery() public onlyOwner{
        require(lottery_state==LOTTERY_STATE.CLOSED,"The lottery state is not startedd"); 
  
    lottery_state=LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner{

        lottery_state=LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash,fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 requestID, uint256 _randomness) internal override {
        require(lottery_state==LOTTERY_STATE.CALCULATING_WINNER,"The Lottery is not calculating winner");
        // require the randomness be greater than zero
        require(_randomness>0,"random not found");

        // get the random index of the winner
        uint256 indexOfWinner = _randomness%players.length;
        // get the number of players
        number_players = players.length;
        // get the recent winner
        recentWinner=players[indexOfWinner];
        // pay the winner
        recentWinner.transfer(address(this).balance);
        // reset the players array
        players= new address payable[](0);
        
        // close the lottery
        lottery_state=LOTTERY_STATE.CLOSED;
        randomness=_randomness;



    }

}