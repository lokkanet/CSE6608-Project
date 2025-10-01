// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FileSharing {
    struct FileMetadata {
        string fileName;
        string fileType;
        uint256 fileSize;
        string ipfsHash;
        address owner;
        uint256 timestamp;
        bool isEncrypted;
    }

    struct AccessControl {
        address user;
        uint256 grantedAt;
        bool canShare;
    }

    mapping(uint256 => FileMetadata) public files;
    mapping(uint256 => mapping(address => AccessControl)) public fileAccess;
    mapping(address => uint256[]) public userFiles;
    mapping(address => bool) public registeredUsers;

    uint256 public fileCount;

    event UserRegistered(address indexed user, uint256 timestamp);
    event FileUploaded(uint256 indexed fileId, address indexed owner, string ipfsHash);
    event AccessGranted(uint256 indexed fileId, address indexed owner, address indexed grantee);
    event AccessRevoked(uint256 indexed fileId, address indexed owner, address indexed revokee);
    event FileDeleted(uint256 indexed fileId, address indexed owner);

    modifier onlyRegistered() {
        require(registeredUsers[msg.sender], "User not registered");
        _;
    }

    modifier onlyFileOwner(uint256 fileId) {
        require(files[fileId].owner == msg.sender, "Not file owner");
        _;
    }

    function registerUser() public {
        require(!registeredUsers[msg.sender], "User already registered");
        registeredUsers[msg.sender] = true;
        emit UserRegistered(msg.sender, block.timestamp);
    }

    function uploadFile(
        string memory fileName,
        string memory fileType,
        uint256 fileSize,
        string memory ipfsHash,
        bool isEncrypted
    ) public onlyRegistered returns (uint256) {
        fileCount++;

        files[fileCount] = FileMetadata({
            fileName: fileName,
            fileType: fileType,
            fileSize: fileSize,
            ipfsHash: ipfsHash,
            owner: msg.sender,
            timestamp: block.timestamp,
            isEncrypted: isEncrypted
        });

        userFiles[msg.sender].push(fileCount);
        fileAccess[fileCount][msg.sender] = AccessControl({
            user: msg.sender,
            grantedAt: block.timestamp,
            canShare: true
        });

        emit FileUploaded(fileCount, msg.sender, ipfsHash);
        return fileCount;
    }

    function grantAccess(uint256 fileId, address user, bool canShare)
        public
        onlyFileOwner(fileId)
    {
        require(user != address(0), "Invalid address");
        require(registeredUsers[user], "User not registered");

        fileAccess[fileId][user] = AccessControl({
            user: user,
            grantedAt: block.timestamp,
            canShare: canShare
        });

        emit AccessGranted(fileId, msg.sender, user);
    }

    function revokeAccess(uint256 fileId, address user)
        public
        onlyFileOwner(fileId)
    {
        delete fileAccess[fileId][user];
        emit AccessRevoked(fileId, msg.sender, user);
    }

    function hasAccess(uint256 fileId, address user) public view returns (bool) {
        return fileAccess[fileId][user].user == user;
    }

    function getFileMetadata(uint256 fileId)
        public
        view
        returns (FileMetadata memory)
    {
        require(hasAccess(fileId, msg.sender), "No access to file");
        return files[fileId];
    }

    function getUserFiles(address user) public view returns (uint256[] memory) {
        return userFiles[user];
    }

    function deleteFile(uint256 fileId) public onlyFileOwner(fileId) {
        delete files[fileId];
        emit FileDeleted(fileId, msg.sender);
    }
}
