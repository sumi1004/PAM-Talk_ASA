#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
다중서명 처리기
PRD 3.3: 거버넌스 패턴 구현

Manager: 2-of-3 다중서명
Freeze: 2-of-3 다중서명
Clawback: 2-of-2 다중서명
"""

from typing import List, Dict
from algosdk import transaction
from algosdk.v2client import algod
from algosdk.transaction import Multisig, MultisigTransaction


class MultiSigHandler:
    """다중서명 트랜잭션 처리기"""

    def __init__(self, algod_client: algod.AlgodClient):
        self.algod_client = algod_client

    def create_multisig_account(
        self,
        addresses: List[str],
        threshold: int
    ) -> Multisig:
        """
        다중서명 계정 생성

        Args:
            addresses: 서명자 주소 리스트
            threshold: 필요한 서명 수

        Returns:
            Multisig: 다중서명 객체
        """
        msig = Multisig(
            version=1,
            threshold=threshold,
            addresses=addresses
        )

        print(f"✅ 다중서명 계정 생성")
        print(f"   주소: {msig.address()}")
        print(f"   서명자: {len(addresses)}명")
        print(f"   임계값: {threshold}")

        return msig

    def create_freeze_transaction(
        self,
        msig: Multisig,
        asset_id: int,
        target_address: str,
        freeze_state: bool
    ) -> transaction.AssetFreezeTxn:
        """
        Freeze 트랜잭션 생성 (다중서명용)

        Args:
            msig: 다중서명 객체
            asset_id: ASA ID
            target_address: 동결 대상 주소
            freeze_state: True=동결, False=해제
        """
        params = self.algod_client.suggested_params()

        txn = transaction.AssetFreezeTxn(
            sender=msig.address(),
            sp=params,
            index=asset_id,
            target=target_address,
            new_freeze_state=freeze_state
        )

        print(f"✅ Freeze 트랜잭션 생성")
        print(f"   대상: {target_address[:10]}...")
        print(f"   상태: {'동결' if freeze_state else '해제'}")

        return txn

    def create_clawback_transaction(
        self,
        msig: Multisig,
        asset_id: int,
        target_address: str,
        recovery_address: str,
        amount: int
    ) -> transaction.AssetTransferTxn:
        """
        Clawback 트랜잭션 생성 (다중서명용)

        Args:
            msig: 다중서명 객체
            asset_id: ASA ID
            target_address: 회수 대상 주소
            recovery_address: 회수 자산 수신 주소
            amount: 회수량
        """
        params = self.algod_client.suggested_params()

        txn = transaction.AssetTransferTxn(
            sender=msig.address(),
            sp=params,
            receiver=recovery_address,
            amt=amount,
            index=asset_id,
            revocation_target=target_address
        )

        print(f"✅ Clawback 트랜잭션 생성")
        print(f"   대상: {target_address[:10]}...")
        print(f"   회수량: {amount}")

        return txn

    def sign_multisig_transaction(
        self,
        msig: Multisig,
        txn: transaction.Transaction,
        private_key: str
    ) -> MultisigTransaction:
        """
        다중서명 트랜잭션 서명

        Args:
            msig: 다중서명 객체
            txn: 트랜잭션
            private_key: 서명자 개인키

        Returns:
            MultisigTransaction: 서명된 트랜잭션
        """
        mtx = MultisigTransaction(txn, msig)
        mtx.sign(private_key)

        print(f"✅ 서명 추가 완료")

        return mtx

    def append_signature(
        self,
        mtx: MultisigTransaction,
        private_key: str
    ) -> MultisigTransaction:
        """
        추가 서명

        Args:
            mtx: 기존 다중서명 트랜잭션
            private_key: 서명자 개인키
        """
        mtx.sign(private_key)

        print(f"✅ 추가 서명 완료")

        return mtx

    def send_multisig_transaction(
        self,
        mtx: MultisigTransaction
    ) -> Dict:
        """
        다중서명 트랜잭션 전송

        Args:
            mtx: 완전히 서명된 다중서명 트랜잭션

        Returns:
            Dict: 결과
        """
        try:
            tx_id = self.algod_client.send_transaction(mtx)
            print(f"📤 트랜잭션 전송: {tx_id}")

            # 확인 대기
            confirmed_txn = transaction.wait_for_confirmation(
                self.algod_client,
                tx_id,
                4
            )

            print(f"✅ 트랜잭션 확인 완료!")

            return {
                "success": True,
                "tx_id": tx_id,
                "confirmed_round": confirmed_txn["confirmed-round"]
            }

        except Exception as e:
            print(f"❌ 트랜잭션 전송 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def freeze_with_multisig(
        self,
        msig: Multisig,
        asset_id: int,
        target_address: str,
        freeze_state: bool,
        signers_private_keys: List[str]
    ) -> Dict:
        """
        다중서명으로 계정 동결/해제

        Args:
            msig: 다중서명 객체 (Freeze 권한)
            asset_id: ASA ID
            target_address: 대상 주소
            freeze_state: True=동결, False=해제
            signers_private_keys: 서명자들의 개인키 (threshold 이상 필요)

        Returns:
            Dict: 결과
        """
        print("=" * 60)
        print(f"다중서명 Freeze 실행 ({msig.threshold}-of-{len(msig.subsigs)})")
        print("=" * 60)

        # 1. 트랜잭션 생성
        txn = self.create_freeze_transaction(
            msig, asset_id, target_address, freeze_state
        )

        # 2. 첫 번째 서명
        mtx = self.sign_multisig_transaction(msig, txn, signers_private_keys[0])

        # 3. 추가 서명
        for private_key in signers_private_keys[1:]:
            mtx = self.append_signature(mtx, private_key)

        # 4. 전송
        result = self.send_multisig_transaction(mtx)

        return result

    def clawback_with_multisig(
        self,
        msig: Multisig,
        asset_id: int,
        target_address: str,
        recovery_address: str,
        amount: int,
        signers_private_keys: List[str]
    ) -> Dict:
        """
        다중서명으로 자산 회수

        Args:
            msig: 다중서명 객체 (Clawback 권한)
            asset_id: ASA ID
            target_address: 회수 대상
            recovery_address: 회수 자산 수신
            amount: 회수량
            signers_private_keys: 서명자들의 개인키 (threshold 이상 필요)

        Returns:
            Dict: 결과
        """
        print("=" * 60)
        print(f"다중서명 Clawback 실행 ({msig.threshold}-of-{len(msig.subsigs)})")
        print("=" * 60)

        # 1. 트랜잭션 생성
        txn = self.create_clawback_transaction(
            msig, asset_id, target_address, recovery_address, amount
        )

        # 2. 첫 번째 서명
        mtx = self.sign_multisig_transaction(msig, txn, signers_private_keys[0])

        # 3. 추가 서명
        for private_key in signers_private_keys[1:]:
            mtx = self.append_signature(mtx, private_key)

        # 4. 전송
        result = self.send_multisig_transaction(mtx)

        return result


def main():
    """다중서명 테스트"""
    import sys
    sys.path.append("..")

    from algosdk.v2client import algod
    from security.keys_management import KeyManagementSystem

    # Algorand 클라이언트
    algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")

    # 키 로드
    kms = KeyManagementSystem()
    keys = kms.load_keys()

    # Freeze 다중서명 계정
    freeze_accounts = keys["freeze"]["accounts"]
    freeze_addresses = [acc["address"] for acc in freeze_accounts]
    freeze_threshold = keys["freeze"]["threshold"]

    # 다중서명 처리기
    handler = MultiSigHandler(algod_client)

    # Freeze 다중서명 객체 생성
    freeze_msig = handler.create_multisig_account(
        addresses=freeze_addresses,
        threshold=freeze_threshold
    )

    print(f"\n✅ Freeze 다중서명 주소: {freeze_msig.address()}")

    # 실제 Freeze 트랜잭션 테스트 (AssetID와 대상 주소 필요)
    # handler.freeze_with_multisig(
    #     msig=freeze_msig,
    #     asset_id=123456,
    #     target_address="TARGET_ADDRESS",
    #     freeze_state=True,
    #     signers_private_keys=[
    #         freeze_accounts[0]["private_key"],
    #         freeze_accounts[1]["private_key"]
    #     ]
    # )


if __name__ == "__main__":
    main()
