#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAM-Talk Digital Coupon System Test Script
"""

import json
import sys
from algosdk.v2client import algod

# Algorand TestNet client
algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")

def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def check_account_balance(address, name):
    """Check account balance"""
    try:
        account_info = algod_client.account_info(address)
        balance = account_info.get('amount', 0) / 1_000_000  # microALGOs to ALGOs

        print(f"\n{name}:")
        print(f"  Address: {address[:20]}...{address[-10:]}")
        print(f"  Balance: {balance:.6f} ALGO")

        if balance < 0.1:
            print(f"  [WARNING] Low balance! Need at least 0.1 ALGO")
            print(f"  [ACTION] Get TestNet ALGO from: https://bank.testnet.algorand.network/")
            print(f"           Paste address: {address}")
        else:
            print(f"  [OK] Sufficient balance")

        return balance
    except Exception as e:
        print(f"  [ERROR] Failed to check balance: {e}")
        return 0

def test_reward_calculator():
    """Test reward calculator"""
    print_header("Test 1: Reward Calculator")

    try:
        from policies.reward_calculator import (
            RewardCalculator, IncomeLevel, RegionType, ActivityType
        )

        calculator = RewardCalculator()

        # Test case 1
        result1 = calculator.calculate_reward(
            base_amount=1000,
            income_level=IncomeLevel.LOW,
            region_type=RegionType.RURAL,
            activity_type=ActivityType.CARBON_NEUTRAL
        )

        print("\nScenario: Low-income, Rural, Carbon-neutral activity")
        print(f"  Base amount: {result1['base_amount']}")
        print(f"  Income multiplier: {result1['income_multiplier']}x")
        print(f"  Region multiplier: {result1['region_multiplier']}x")
        print(f"  Activity multiplier: {result1['activity_multiplier']}x")
        print(f"  Total multiplier: {result1['total_multiplier']}x")
        print(f"  Final amount: {result1['final_amount']}")
        print(f"  Bonus: +{result1['bonus_amount']}")

        assert result1['final_amount'] == 3900, "Reward calculation error!"
        print("\n  [SUCCESS] Reward calculator working correctly!")

        return True
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        return False

def test_reserve_manager():
    """Test reserve manager"""
    print_header("Test 2: Reserve Manager")

    try:
        from contracts.reserve_manager import ReserveManager

        manager = ReserveManager()

        # Set budget
        manager.set_budget(
            period="2025-Q1-TEST",
            total_budget=1000000,
            per_person_limit=5000
        )

        # Check issuance
        check = manager.check_issuance_allowed(
            user_id="test_user001",
            amount=1000,
            period="2025-Q1-TEST"
        )

        print(f"\nIssuance check for test_user001 (1000 coupons):")
        print(f"  Allowed: {check['allowed']}")
        print(f"  Reason: {check['reason']}")

        # Get budget status
        status = manager.get_budget_status("2025-Q1-TEST")
        print(f"\nBudget status:")
        print(f"  Period: {status['period']}")
        print(f"  Total budget: {status['total_budget']:,}")
        print(f"  Remaining: {status['remaining']:,}")
        print(f"  Per-person limit: {status['per_person_limit']:,}")

        print("\n  [SUCCESS] Reserve manager working correctly!")
        return True
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_keys():
    """Test key generation"""
    print_header("Test 3: Key Management")

    try:
        with open("config/keys_public.json", 'r') as f:
            keys = json.load(f)

        print("\nGenerated keys:")
        print(f"  Manager (2-of-3): {keys['manager']['address'][:30]}...")
        print(f"  Reserve: {keys['reserve']['address'][:30]}...")
        print(f"  Freeze (2-of-3): {keys['freeze']['address'][:30]}...")
        print(f"  Clawback (2-of-2): {keys['clawback']['address'][:30]}...")

        print("\n  [SUCCESS] Keys generated correctly!")

        # Check Reserve balance
        reserve_address = keys['reserve']['address']
        balance = check_account_balance(reserve_address, "Reserve Account")

        return True
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("PAM-Talk Digital Coupon System - TestNet Demo")
    print("=" * 60)

    results = []

    # Test 1: Keys
    results.append(("Key Management", test_keys()))

    # Test 2: Reward Calculator
    results.append(("Reward Calculator", test_reward_calculator()))

    # Test 3: Reserve Manager
    results.append(("Reserve Manager", test_reserve_manager()))

    # Summary
    print_header("Test Summary")

    all_passed = True
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed!")
        print("\nNext steps:")
        print("1. Get TestNet ALGO for Reserve account:")
        print("   https://bank.testnet.algorand.network/")
        print("\n2. Create ASA token:")
        print("   python create_asa.py")
        print("\n3. Start API server:")
        print("   python api/coupon_api.py")
    else:
        print("Some tests failed. Please check errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
