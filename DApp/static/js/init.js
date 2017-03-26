var Web3 = require('./node_modules/web3/index.js');
if (typeof web3 !== 'undefined') {
  web3 = new Web3(web3.currentProvider);
} else {
  // set the provider you want from Web3.providers
  web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
}

// NOTE: Need to compile with browserify init.js -o main.js
var SolidityCoder = require("web3/lib/solidity/coder.js");

var account         = '0x98181b49bf309364fba5d75ff57d30509b2a24fd'; // Manjaro
var contractAddress = '0x124f1fb67f450bd3234ec0e12d519fa61e6bc543'; // daisee005

web3.eth.defaultAccount = account;

var now = new Date();

// Assemble function hashes
var functionHashes = getFunctionHashes(abiArray);

// Get hold of contract instance
var contract = web3.eth.contract(abiArray).at(contractAddress);

// Setup filter to watch transactions
var filter = web3.eth.filter('latest');
//var filter = web3.eth.filter({fromBlock:0, toBlock: 'latest', address: contractAddress, 'topics':['0x' + web3.sha3('newtest(string,uint256,string,string,uint256)')]});

filter.watch(function(error, result){

  if (error) return;
  
  var block = web3.eth.getBlock(result, true);
  console.log('block #' + block.number);

  console.dir(block.transactions);

  for (var index = 0; index < block.transactions.length; index++) {
    var t = block.transactions[index];

    // Decode from
    var from = t.from==account ? "me" : t.from;

    // Decode function
    var func = findFunctionByHash(functionHashes, t.input);

    if (func == 'setProduction') {
      var inputData = SolidityCoder.decodeParams(["uint256"], t.input.substring(10));
      console.dir(inputData);
      $('#transactions').append('<tr><td>' + t.blockNumber + 
        '</td><td>' + from + 
        '</td><td>' + "DAISEE" + 
        '</td><td>setProduction(' + inputData[0].toString() + ')</td></tr>');
    } else if (func == 'consumeEnergy') {
      var inputData = SolidityCoder.decodeParams(["uint256"], t.input.substring(10));
      console.dir(inputData);
      $('#transactions').append('<tr><td>' + t.blockNumber + 
        '</td><td>' + from + 
        '</td><td>' + "DAISEE" + 
        '</td><td>consumeEnergy(' + inputData[0].toString() + ')</td></tr>');
    } else if (func == 'buyEnergy') {
      var inputData = SolidityCoder.decodeParams(["uint256"], t.input.substring(10));
      console.dir(inputData);
      $('#transactions').append('<tr><td>' + t.blockNumber + 
        '</td><td>' + from + 
        '</td><td>' + "DAISEE" + 
        '</td><td>buyEnergy(' + inputData[0].toString() + ')</td></tr>');
	  } else {
      // Default log => for debug
      $('#transactions').append('<tr><td>' + t.blockNumber + '</td><td>' + from + '</td><td>' + t.to + '</td><td>' + t.input + '</td></tr>')
    }
  }
});

// Update labels every second
setInterval(function() {

  // Account
  $('#coinbase').text(account);
  //$('#coinbase').text(contractAddress);

  // Account balance in Ether
  var balanceWei = web3.eth.getBalance(account).toNumber();
  var balance = web3.fromWei(balanceWei, 'ether');
  $('#balance').text(balance);

  // Block infos
  var number = web3.eth.blockNumber;
  if ($('#latestBlock').text() != number)
    $('#latestBlock').text(number);

  var hash = web3.eth.getBlock(number).hash
  $('#latestBlockHash').text(hash);

  var timeStamp = web3.eth.getBlock(number).timestamp;
  var d = new Date(0);
  d.setUTCSeconds(timeStamp);
  $('#latestBlockTimestamp').text(d);

  // Contract energy balance: call (not state changing)
  var energyBalance = contract.getEnergyBalance.call();
  $('#energyBalance').text(energyBalance);

  $('#startedAt').text(now);

}, 1000);




// Get function hashes
// TODO: also extract input parameter types for later decoding

function getFunctionHashes(abi) {
  var hashes = [];
  for (var i=0; i<abi.length; i++) {
    var item = abi[i];
    if (item.type != "function") continue;
    var signature = item.name + "(" + item.inputs.map(function(input) {return input.type;}).join(",") + ")";
    var hash = web3.sha3(signature);
    console.log(item.name + '=' + hash);
    hashes.push({name: item.name, hash: hash});
  }
  return hashes;
}

function findFunctionByHash(hashes, functionHash) {
  for (var i=0; i<hashes.length; i++) {
    if (hashes[i].hash.substring(0, 10) == functionHash.substring(0, 10))
      return hashes[i].name;
  }
  return null;
}