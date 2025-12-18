#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG 디지털 쿠폰 ASA 토큰
PRD 3.1: ASA 파라미터 설계 구현

주요 기능:
- M/R/F/C 권한 분리
- defaultFrozen=True (초기 동결)
- metadataHash 포함
- Clawback 지원
"""

import json
import hashlib
from typing import Dict, Optional
from algosdk import account
from algosdk.v2client import algod
from algosdk.transaction import (
    AssetConfigTxn,
    AssetTransferTxn,
    AssetFreezeTxn,
    wait_for_confirmation
)


class ESGCouponASA:
    """ESG 디지털 쿠폰 ASA 관리"""

    def __init__(
        self,
        algod_address: str = "https://testnet-api.algonode.cloud",
        algod_token: str = ""
    ):
        self.algod_client = algod.AlgodClient(algod_token, algod_address)
        self.asset_id = None

    def create_coupon_asa(
        self,
        creator_address: str,
        creator_private_key: str,
        manager_address: str,
        reserve_address: str,
        freeze_address: str,
        clawback_address: str,
        total_supply: int,
        policy_document_hash: str,
        decimals: int = 0
    ) -> Dict:
        """
        ESG 쿠폰 ASA 생성
        PRD 3.1 파라미터 적용

        Args:
            creator_address: Creator 계정 주소
            creator_private_key: Creator 개인키
            manager_address: Manager 주소 (2-of-3 multisig)
            reserve_address: Reserve 주소 (단일)
            freeze_address: Freeze 주소 (2-of-3 multisig)
            clawback_address: Clawback 주소 (2-of-2 multisig)
            total_supply: 총 발행량 (예: 연간 예산 / 단가)
            policy_document_hash: 정책 문서 SHA-256 해시
            decimals: 소수점 자리 (0=정수, 2=0.01단위)

        Returns:
            Dict: 생성 결과
        """
        print("🪙 ESG 디지털 쿠폰 ASA 생성 중...")

        # 트랜잭션 파라미터
        params = self.algod_client.suggested_params()

        # ASA 생성 트랜잭션
        txn = AssetConfigTxn(
            sender=creator_address,
            sp=params,
            total=total_supply,
            default_frozen=True,  # PRD 3.1: 초기 동결
            unit_name="ESG-CPN",  # 행동 단위 명시
            asset_name="PAM-TALK-ESG-2025",  # 정책명 반영
            manager=manager_address,  # M: 메타데이터 변경
            reserve=reserve_address,  # R: 미발행량 보유
            freeze=freeze_address,    # F: 계정 동결
            clawback=clawback_address,  # C: 자산 회수
            url="https://pam-talk.com/policy/esg-coupon-2025",
            metadata_hash=bytes.fromhex(policy_document_hash),  # 정책 해시
            decimals=decimals
        )

        # 서명
        signed_txn = txn.sign(creator_private_key)

        # 전송
        try:
            tx_id = self.algod_client.send_transaction(signed_txn)
            print(f"📤 트랜잭션 전송: {tx_id}")

            # 확인 대기
            confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)

            # Asset ID 추출
            self.asset_id = confirmed_txn["asset-index"]

            print(f"✅ ASA 생성 완료!")
            print(f"   Asset ID: {self.asset_id}")
            print(f"   Manager: {manager_address[:10]}...")
            print(f"   Reserve: {reserve_address[:10]}...")
            print(f"   Freeze: {freeze_address[:10]}...")
            print(f"   Clawback: {clawback_address[:10]}...")

            return {
                "success": True,
                "asset_id": self.asset_id,
                "tx_id": tx_id,
                "confirmed_round": confirmed_txn["confirmed-round"],
                "manager": manager_address,
                "reserve": reserve_address,
                "freeze": freeze_address,
                "clawback": clawback_address
            }

        except Exception as e:
            print(f"❌ ASA 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def opt_in(
        self,
        user_address: str,
        user_private_key: str,
        asset_id: int
    ) -> Dict:
        """
        ASA Opt-in (수령 준비)
        PRD 2.1: S2→S3 단계
        """
        params = self.algod_client.suggested_params()

        txn = AssetTransferTxn(
            sender=user_address,
            sp=params,
            receiver=user_address,
            amt=0,
            index=asset_id
        )

        signed_txn = txn.sign(user_private_key)

        try:
            tx_id = self.algod_client.send_transaction(signed_txn)
            wait_for_confirmation(self.algod_client, tx_id, 4)

            print(f"✅ Opt-in 완료: {user_address[:10]}... → Asset {asset_id}")

            return {
                "success": True,
                "tx_id": tx_id,
                "user_address": user_address,
                "asset_id": asset_id
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def unfreeze_account(
        self,
        freeze_address: str,
        freeze_private_key: str,
        target_address: str,
        asset_id: int
    ) -> Dict:
        """
        계정 동결 해제 (자격 확인 후)
        PRD 3.1: defaultFrozen=True 후 Unfreeze
        """
        params = self.algod_client.suggested_params()

        txn = AssetFreezeTxn(
            sender=freeze_address,
            sp=params,
            index=asset_id,
            target=target_address,
            new_freeze_state=False  # 동결 해제
        )

        signed_txn = txn.sign(freeze_private_key)

        try:
            tx_id = self.algod_client.send_transaction(signed_txn)
            wait_for_confirmation(self.algod_client, tx_id, 4)

            print(f"✅ 동결 해제: {target_address[:10]}... → Asset {asset_id}")

            return {
                "success": True,
                "tx_id": tx_id,
                "target_address": target_address,
                "frozen": False
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def freeze_account(
        self,
        freeze_address: str,
        freeze_private_key: str,
        target_address: str,
        asset_id: int
    ) -> Dict:
        """
        계정 동결 (부정 의심 시)
        PRD 2.1: S4→S5 단계
        """
        params = self.algod_client.suggested_params()

        txn = AssetFreezeTxn(
            sender=freeze_address,
            sp=params,
            index=asset_id,
            target=target_address,
            new_freeze_state=True  # 동결
        )

        signed_txn = txn.sign(freeze_private_key)

        try:
            tx_id = self.algod_client.send_transaction(signed_txn)
            wait_for_confirmation(self.algod_client, tx_id, 4)

            print(f"⚠️  계정 동결: {target_address[:10]}... → Asset {asset_id}")

            return {
                "success": True,
                "tx_id": tx_id,
                "target_address": target_address,
                "frozen": True
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def clawback_asset(
        self,
        clawback_address: str,
        clawback_private_key: str,
        target_address: str,
        recovery_address: str,
        amount: int,
        asset_id: int
    ) -> Dict:
        """
        자산 회수 (부정수급 처리)
        PRD 2.1: S4→S6 단계

        Args:
            clawback_address: Clawback 권한 주소
            clawback_private_key: Clawback 개인키
            target_address: 회수 대상 주소
            recovery_address: 회수 자산 수신 주소
            amount: 회수량
            asset_id: ASA ID
        """
        params = self.algod_client.suggested_params()

        # Clawback 트랜잭션
        txn = AssetTransferTxn(
            sender=clawback_address,
            sp=params,
            receiver=recovery_address,
            amt=amount,
            index=asset_id,
            revocation_target=target_address  # 회수 대상
        )

        signed_txn = txn.sign(clawback_private_key)

        try:
            tx_id = self.algod_client.send_transaction(signed_txn)
            wait_for_confirmation(self.algod_client, tx_id, 4)

            print(f"⚠️  자산 회수 완료!")
            print(f"   대상: {target_address[:10]}...")
            print(f"   회수량: {amount}")
            print(f"   수신: {recovery_address[:10]}...")

            return {
                "success": True,
                "tx_id": tx_id,
                "target_address": target_address,
                "recovery_address": recovery_address,
                "amount": amount
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def transfer_from_reserve(
        self,
        reserve_address: str,
        reserve_private_key: str,
        recipient_address: str,
        amount: int,
        asset_id: int
    ) -> Dict:
        """
        Reserve에서 쿠폰 발급
        PRD 2.1: S0→S1→S2 단계
        """
        params = self.algod_client.suggested_params()

        txn = AssetTransferTxn(
            sender=reserve_address,
            sp=params,
            receiver=recipient_address,
            amt=amount,
            index=asset_id
        )

        signed_txn = txn.sign(reserve_private_key)

        try:
            tx_id = self.algod_client.send_transaction(signed_txn)
            wait_for_confirmation(self.algod_client, tx_id, 4)

            print(f"✅ 쿠폰 발급: {amount} → {recipient_address[:10]}...")

            return {
                "success": True,
                "tx_id": tx_id,
                "recipient": recipient_address,
                "amount": amount
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_asset_info(self, asset_id: int) -> Dict:
        """ASA 정보 조회"""
        try:
            asset_info = self.algod_client.asset_info(asset_id)
            return asset_info
        except Exception as e:
            return {"error": str(e)}

    def get_account_asset_balance(
        self,
        address: str,
        asset_id: int
    ) -> Optional[int]:
        """계정의 ASA 잔액 조회"""
        try:
            account_info = self.algod_client.account_info(address)
            assets = account_info.get("assets", [])

            for asset in assets:
                if asset["asset-id"] == asset_id:
                    return asset["amount"]

            return None

        except Exception as e:
            print(f"잔액 조회 실패: {e}")
            return None


def generate_policy_hash(policy_document: str) -> str:
    """정책 문서 해시 생성 (SHA-256)"""
    return hashlib.sha256(policy_document.encode()).hexdigest()


def main():
    """ASA 생성 테스트"""
    import sys
    sys.path.append("..")

    from security.keys_management import KeyManagementSystem

    # 키 로드
    kms = KeyManagementSystem()
    try:
        asa_keys = kms.export_for_asa_creation()
    except FileNotFoundError:
        print("❌ 키가 없습니다. 먼저 keys_management.py --init을 실행하세요.")
        return

    # Creator 계정 (Reserve 사용)
    keys = kms.load_keys()
    creator_address = keys["reserve"]["address"]
    creator_private_key = keys["reserve"]["private_key"]

    # 정책 문서 해시
    policy_doc = """
    PAM-Talk ESG 디지털 쿠폰 정책 v1.0
    - 발행 주체: 중앙정부
    - 대상: 시민참여형 탄소중립 활동
    - 유효기간: 2025년 1월 1일 ~ 2025년 12월 31일
    """
    policy_hash = generate_policy_hash(policy_doc)

    # ASA 생성
    asa = ESGCouponASA()
    result = asa.create_coupon_asa(
        creator_address=creator_address,
        creator_private_key=creator_private_key,
        manager_address=asa_keys["manager"],
        reserve_address=asa_keys["reserve"],
        freeze_address=asa_keys["freeze"],
        clawback_address=asa_keys["clawback"],
        total_supply=1000000,  # 100만개
        policy_document_hash=policy_hash,
        decimals=0  # 정수 단위
    )

    if result["success"]:
        # 설정 저장
        config = {
            "asset_id": result["asset_id"],
            "created_at": result["confirmed_round"],
            "policy_hash": policy_hash
        }

        with open("../config/asa_config.json", "w") as f:
            json.dump(config, f, indent=2)

        print("\n✅ ASA 설정 저장: config/asa_config.json")


if __name__ == "__main__":
    main()
