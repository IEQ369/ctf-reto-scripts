// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;
// Referencia de estado mutable, NO auditada ni desplegada.
contract Vault {
    bool public unlocked;
    function unlock() external { unlocked = true; }
}
