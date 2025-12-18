#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M/R/F/C 키 관리 시스템
PRD 3.2: 권한키 구조 구현

Manager (M): 메타데이터·권한 변경 - 다중서명 2-of-3
Reserve (R): 미발행량 보유·배분 - HSM 보안 저장
Freeze (F): 계정 동결 권한 - 2-of-3 다중서명
Clawback (C): 자산 회수 권한 - 2-of-2 다중서명
"""

import json
import os
from typing import Dict, List, Tuple
from algosdk import account, mnemonic
from algosdk.transaction import Multisig
from datetime import datetime
import hashlib


class KeyRole:
    """키 역할 상수"""
    MANAGER = "manager"
    RESERVE = "reserve"
    FREEZE = "freeze"
    CLAWBACK = "clawback"


class KeyManagementSystem:
    """M/R/F/C 키 관리 시스템"""

    def __init__(self, config_dir: str = "./config"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        self.keys_file = os.path.join(config_dir, "keys_secure.json")
        self.public_keys_file = os.path.join(config_dir, "keys_public.json")

    def generate_key_structure(self) -> Dict:
        """
        PRD 3.2에 따른 M/R/F/C 키 생성

        Returns:
            Dict: 생성된 키 구조
        """
        print("🔐 M/R/F/C 키 구조 생성 중...")

        # Manager: 2-of-3 다중서명 (중앙정부, 광역지자체, 기술운영팀)
        manager_accounts = self._create_multisig_accounts(
            role="manager",
            count=3,
            threshold=2,
            parties=["중앙정부", "광역지자체", "기술운영팀"]
        )

        # Reserve: 단일 계정 (HSM 보관 권장)
        reserve_account = self._create_single_account(
            role="reserve",
            party="재정담당부서"
        )

        # Freeze: 2-of-3 다중서명 (감사기관, 상위감독기관, 내부감사팀)
        freeze_accounts = self._create_multisig_accounts(
            role="freeze",
            count=3,
            threshold=2,
            parties=["감사기관", "상위감독기관", "내부감사팀"]
        )

        # Clawback: 2-of-2 다중서명 (운영기관, 감사기관)
        clawback_accounts = self._create_multisig_accounts(
            role="clawback",
            count=2,
            threshold=2,
            parties=["운영기관", "감사기관"]
        )

        key_structure = {
            "created_at": datetime.now().isoformat(),
            "network": "testnet",
            "manager": manager_accounts,
            "reserve": reserve_account,
            "freeze": freeze_accounts,
            "clawback": clawback_accounts
        }

        # 보안 저장 (private keys 포함)
        self._save_secure_keys(key_structure)

        # 공개 정보만 저장 (주소만)
        self._save_public_keys(key_structure)

        print("✅ M/R/F/C 키 생성 완료!")
        print(f"   - Manager (2-of-3): {manager_accounts['multisig_address']}")
        print(f"   - Reserve: {reserve_account['address']}")
        print(f"   - Freeze (2-of-3): {freeze_accounts['multisig_address']}")
        print(f"   - Clawback (2-of-2): {clawback_accounts['multisig_address']}")

        return key_structure

    def _create_multisig_accounts(
        self,
        role: str,
        count: int,
        threshold: int,
        parties: List[str]
    ) -> Dict:
        """다중서명 계정 생성"""
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

            print(f"  ✓ {role.upper()} #{i+1} ({party}): {address[:10]}...")

        # 다중서명 주소 생성
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
        """단일 계정 생성"""
        private_key, address = account.generate_account()
        account_mnemonic = mnemonic.from_private_key(private_key)

        print(f"  ✓ {role.upper()} ({party}): {address[:10]}...")

        return {
            "role": role,
            "type": "single",
            "party": party,
            "address": address,
            "private_key": private_key,
            "mnemonic": account_mnemonic
        }

    def _save_secure_keys(self, key_structure: Dict):
        """보안 키 저장 (private keys 포함) - 암호화 권장"""
        with open(self.keys_file, 'w') as f:
            json.dump(key_structure, f, indent=2)

        print(f"⚠️  보안 키 파일 저장: {self.keys_file}")
        print(f"   ⚠️  이 파일은 절대 공개하지 마세요!")

    def _save_public_keys(self, key_structure: Dict):
        """공개 키 정보만 저장 (주소만)"""
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

        with open(self.public_keys_file, 'w') as f:
            json.dump(public_info, f, indent=2)

        print(f"✅ 공개 키 파일 저장: {self.public_keys_file}")

    def load_keys(self) -> Dict:
        """저장된 키 로드"""
        if not os.path.exists(self.keys_file):
            raise FileNotFoundError(
                f"키 파일이 없습니다. 먼저 generate_key_structure()를 실행하세요."
            )

        with open(self.keys_file, 'r') as f:
            return json.load(f)

    def load_public_keys(self) -> Dict:
        """공개 키만 로드"""
        if not os.path.exists(self.public_keys_file):
            raise FileNotFoundError(
                f"공개 키 파일이 없습니다."
            )

        with open(self.public_keys_file, 'r') as f:
            return json.load(f)

    def get_role_address(self, role: str) -> str:
        """역할별 주소 반환"""
        keys = self.load_public_keys()
        return keys[role]["address"]

    def export_for_asa_creation(self) -> Dict:
        """ASA 생성용 키 정보 추출"""
        keys = self.load_public_keys()

        return {
            "manager": keys["manager"]["address"],
            "reserve": keys["reserve"]["address"],
            "freeze": keys["freeze"]["address"],
            "clawback": keys["clawback"]["address"]
        }

    def verify_key_structure(self) -> bool:
        """키 구조 무결성 검증"""
        try:
            keys = self.load_keys()

            # Manager 검증
            assert keys["manager"]["type"] == "multisig"
            assert keys["manager"]["threshold"] == 2
            assert keys["manager"]["total"] == 3

            # Reserve 검증
            assert keys["reserve"]["type"] == "single"

            # Freeze 검증
            assert keys["freeze"]["type"] == "multisig"
            assert keys["freeze"]["threshold"] == 2
            assert keys["freeze"]["total"] == 3

            # Clawback 검증
            assert keys["clawback"]["type"] == "multisig"
            assert keys["clawback"]["threshold"] == 2
            assert keys["clawback"]["total"] == 2

            print("✅ 키 구조 검증 성공!")
            return True

        except Exception as e:
            print(f"❌ 키 구조 검증 실패: {e}")
            return False


def main():
    """키 관리 시스템 초기화"""
    import argparse

    parser = argparse.ArgumentParser(description="M/R/F/C 키 관리 시스템")
    parser.add_argument("--init", action="store_true", help="새로운 키 생성")
    parser.add_argument("--verify", action="store_true", help="키 검증")
    parser.add_argument("--export", action="store_true", help="ASA 생성용 키 추출")

    args = parser.parse_args()

    kms = KeyManagementSystem()

    if args.init:
        print("=" * 60)
        print("PAM-Talk 디지털 쿠폰 시스템 - M/R/F/C 키 생성")
        print("=" * 60)
        kms.generate_key_structure()
        print("\n⚠️  중요: config/keys_secure.json 파일을 안전하게 보관하세요!")

    elif args.verify:
        kms.verify_key_structure()

    elif args.export:
        asa_keys = kms.export_for_asa_creation()
        print("ASA 생성용 키 정보:")
        print(json.dumps(asa_keys, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
