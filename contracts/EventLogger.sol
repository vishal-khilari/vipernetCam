// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EventLogger {
    struct LogEntry {
        bytes32 dataHash;
        string cid;
        uint256 timestamp;
        address reporter;
    }
    LogEntry[] public logs;
    event LogAdded(uint256 indexed id, bytes32 dataHash, string cid, uint256 timestamp, address reporter);

    function logEvent(bytes32 dataHash, string memory cid, uint256 timestamp) public returns (uint256) {
        logs.push(LogEntry(dataHash, cid, timestamp, msg.sender));
        uint256 id = logs.length - 1;
        emit LogAdded(id, dataHash, cid, timestamp, msg.sender);
        return id;
    }

    function getLog(uint256 id) public view returns (bytes32, string memory, uint256, address) {
        LogEntry storage e = logs[id];
        return (e.dataHash, e.cid, e.timestamp, e.reporter);
    }

    function totalLogs() public view returns (uint256) {
        return logs.length;
    }
}
