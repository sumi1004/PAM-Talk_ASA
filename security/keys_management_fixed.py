#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M/R/F/C Key Management System
PRD 3.2: Key Authority Structure Implementation
"""

import json
import os
from typing import Dict, List
from algosdk import account, mnemonic
from algosdk.transaction import Multisig
from datetime import datetime


class KeyRole:
    """Key role constants"""
    MANAGER = "manager"
    RESERVE = "reserve"
    FREEZE = "freeze"
    CLAWBACK = "clawback"


class KeyManagementSystem:
    """M/R/F/C Key Management System"""

    def __init__(self, config_dir: str = "./config"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        self.keys_file = os.path.join(config_dir, "keys_secure.json")
        self.public_keys_file = os.path.join(config_dir, "keys_public.json")

    def generate_key_structure(self) -> Dict:
        """Generate M/R/F/C key structure according to PRD 3.2"""
        print("=" * 60)
        print("Generating M/R/F/C Key Structure...")
        print("=" * 60)

        # Manager: 2-of-3 multisig
        manager_accounts = self._create_multisig_accounts(
            role="manager",
            count=3,
            threshold=2,
            parties=["Government", "LocalGov", "TechTeam"]
        )

        # Reserve: single account
        reserve_account = self._create_single_account(
            role="reserve",
            party="Finance"
        )

        # Freeze: 2-of-3 multisig
        freeze_accounts = self._create_multisig_accounts(
            role="freeze",
            count=3,
            threshold=2,
            parties=["Auditor", "Supervisor", "InternalAudit"]
        )

        # Clawback: 2-of-2 multisig
        clawback_accounts = self._create_multisig_accounts(
            role="clawback",
            count=2,
            threshold=2,
            parties=["Operations", "Audit"]
        )

        key_structure = {
            "created_at": datetime.now().isoformat(),
            "network": "testnet",
            "manager": manager_accounts,
            "reserve": reserve_account,
            "freeze": freeze_accounts,
            "clawback": clawback_accounts
        }

        self._save_secure_keys(key_structure)
        self._save_public_keys(key_structure)

        print("\n[SUCCESS] M/R/F/C Keys Generated!")
        print(f"  - Manager (2-of-3): {manager_accounts['multisig_address'][:20]}...")
        print(f"  - Reserve: {reserve_account['address'][:20]}...")
        print(f"  - Freeze (2-of-3): {freeze_accounts['multisig_address'][:20]}...")
        print(f"  - Clawback (2-of-2): {clawback_accounts['multisig_address'][:20]}...")

        return key_structure

    def _create_multisig_accounts(
        self,
        role: str,
        count: int,
        threshold: int,
        parties: List[str]
    ) -> Dict:
        """Create multisig accounts"""
        accounts = []

        for i, party in enumerate(parties[:count]):
            private_key, address = account.generate_account()
            account_mnemonic = mnemonic.from_private_key(private_key)

            accounts.append({
                "party": party,
                "address": address,
                "private_key": private_key,
                "mnemonic": account_mnemonic
            })

            print(f"  [OK] {role.upper()} #{i+1} ({party}): {address[:20]}...")

        msig = Multisig(
            version=1,
            threshold=threshold,
            addresses=[acc["address"] for acc in accounts]
        )

        return {
            "role": role,
            "type": "multisig",
            "threshold": threshold,
            "total": count,
            "multisig_address": msig.address(),
            "accounts": accounts
        }

    def _create_single_account(self, role: str, party: str) -> Dict:
        """Create single account"""
        private_key, address = account.generate_account()
        account_mnemonic = mnemonic.from_private_key(private_key)

        print(f"  [OK] {role.upper()} ({party}): {address[:20]}...")

        return {
            "role": role,
            "type": "single",
            "party": party,
            "address": address,
            "private_key": private_key,
            "mnemonic": account_mnemonic
        }

    def _save_secure_keys(self, key_structure: Dict):
        """Save secure keys (includes private keys)"""
        with open(self.keys_file, 'w', encoding='utf-8') as f:
            json.dump(key_structure, f, indent=2, ensure_ascii=False)

        print(f"\n[WARNING] Secure keys saved: {self.keys_file}")
        print("  [WARNING] NEVER commit this file to Git!")

    def _save_public_keys(self, key_structure: Dict):
        """Save public keys only (addresses only)"""
        public_info = {
            "created_at": key_structure["created_at"],
            "network": key_structure["network"],
            "manager": {
                "address": key_structure["manager"]["multisig_address"],
                "type": "multisig",
                "threshold": key_structure["manager"]["threshold"]
            },
            "reserve": {
                "address": key_structure["reserve"]["address"],
                "type": "single"
            },
            "freeze": {
                "address": key_structure["freeze"]["multisig_address"],
                "type": "multisig",
                "threshold": key_structure["freeze"]["threshold"]
            },
            "clawback": {
                "address": key_structure["clawback"]["multisig_address"],
                "type": "multisig",
                "threshold": key_structure["clawback"]["threshold"]
            }
        }

        with open(self.public_keys_file, 'w', encoding='utf-8') as f:
            json.dump(public_info, f, indent=2, ensure_ascii=False)

        print(f"[OK] Public keys saved: {self.public_keys_file}")

    def load_keys(self) -> Dict:
        """Load saved keys"""
        with open(self.keys_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_public_keys(self) -> Dict:
        """Load public keys only"""
        with open(self.public_keys_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def export_for_asa_creation(self) -> Dict:
        """Export keys for ASA creation"""
        keys = self.load_public_keys()
        return {
            "manager": keys["manager"]["address"],
            "reserve": keys["reserve"]["address"],
            "freeze": keys["freeze"]["address"],
            "clawback": keys["clawback"]["address"]
        }


def main():
    """Initialize key management system"""
    print("=" * 60)
    print("PAM-Talk Digital Coupon - M/R/F/C Key Generator")
    print("=" * 60)

    kms = KeyManagementSystem()
    kms.generate_key_structure()

    print("\n" + "=" * 60)
    print("[IMPORTANT] Save config/keys_secure.json securely!")
    print("=" * 60)


if __name__ == "__main__":
    main()
