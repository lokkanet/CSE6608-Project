// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 private storedData; // there is a stored data unsigned int 256 bit private
    address public owner; // there is address owner public

    event DataStored(uint256 data, address indexed user);

    constructor() {
        owner = msg.sender;
    }

    function set(uint256 x) public {
        storedData = x;
        emit DataStored(x, msg.sender);
    }

    function get() public view returns (uint256) {
        return storedData;
    }

    function getOwner() public view returns (address) {
        return owner;
    }
}