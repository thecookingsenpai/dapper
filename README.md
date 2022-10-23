# dApper

## A solidity to javascript translator for dApps

### What is it

dApper is a command line utility designed to write a .js file compatible with ethers.js that will allow you to interact with a smart contract defined in a solidity file from your dApp.

### Installation

Simply put dapper.py in the same folder as your smart contract.

### Usage

    python3 dapper.py <smart_contract.sol> [<contract_address>, <json_file_with_abi>]

By default, the script will create a new contract type with ethers.js without any address or abi. You can specify both if your script is already deployed somewhere.

You will find your js file as smart_contract_name.js
