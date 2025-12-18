#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
불변식(Invariant) 검증 시스템
PRD 4.2: 필수 불변식 구현

불변식:
1. 자산 보존: total = Reserve + 시민지갑 + 가맹점 + 회수
2. 한도 검증: 기간별_누적지급 ≤ 정책_최대치
3. 회수 검증: 회수계정_ASA잔량 = 0
4. 감사 검증: 정책버전별_증빙해시 ≥ 1건
"""

from typing import Dict, List, Optional
from algosdk.v2client import algod
import json


class InvariantViolationError(Exception):
    """불변식 위반 예외"""
    pass


class InvariantVerifier:
    """불변식 검증기"""

    def __init__(
        self,
        algod_client: algod.AlgodClient,
        asset_id: int,
        config_file: str = "../config/accounts_config.json"
    ):
        self.algod_client = algod_client
        self.asset_id = asset_id
        self.config_file = config_file
        self._load_accounts_config()

    def _load_accounts_config(self):
        """계정 설정 로드"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.reserve_address = config.get("reserve_address")
                self.citizen_addresses = config.get("citizen_addresses", [])
                self.merchant_addresses = config.get("merchant_addresses", [])
                self.clawback_address = config.get("clawback_address")
        except FileNotFoundError:
            print("⚠️  계정 설정 파일 없음. 기본값 사용.")
            self.reserve_address = None
            self.citizen_addresses = []
            self.merchant_addresses = []
            self.clawback_address = None

    def verify_all_invariants(self) -> Dict:
        """모든 불변식 검증"""
        print("🔍 불변식 검증 시작...")

        results = {
            "asset_conservation": None,
            "limit_compliance": None,
            "clawback_compliance": None,
            "audit_trail": None,
            "all_passed": False
        }

        try:
            # 1. 자산 보존 검증
            results["asset_conservation"] = self.verify_asset_conservation()

            # 2. 한도 검증
            results["limit_compliance"] = self.verify_limit_compliance()

            # 3. 회수 검증
            results["clawback_compliance"] = self.verify_clawback_compliance()

            # 4. 감사 검증
            results["audit_trail"] = self.verify_audit_trail()

            # 전체 결과
            results["all_passed"] = all([
                results["asset_conservation"]["passed"],
                results["limit_compliance"]["passed"],
                results["clawback_compliance"]["passed"],
                results["audit_trail"]["passed"]
            ])

            if results["all_passed"]:
                print("✅ 모든 불변식 검증 통과!")
            else:
                print("❌ 일부 불변식 위반 발견!")

        except Exception as e:
            print(f"❌ 불변식 검증 실패: {e}")
            results["error"] = str(e)

        return results

    def verify_asset_conservation(self) -> Dict:
        """
        불변식 1: 자산 보존
        total = Reserve + 시민지갑 + 가맹점 + 회수
        """
        print("\n1️⃣  자산 보존 검증 중...")

        try:
            # 총 발행량
            asset_info = self.algod_client.asset_info(self.asset_id)
            total_supply = asset_info["params"]["total"]

            # Reserve 잔액
            reserve_balance = self._get_asset_balance(self.reserve_address) or 0

            # 시민 지갑 합계
            citizen_sum = sum(
                self._get_asset_balance(addr) or 0
                for addr in self.citizen_addresses
            )

            # 가맹점 합계
            merchant_sum = sum(
                self._get_asset_balance(addr) or 0
                for addr in self.merchant_addresses
            )

            # 회수 계정
            clawback_sum = self._get_asset_balance(self.clawback_address) or 0

            # 계산
            total_distributed = reserve_balance + citizen_sum + merchant_sum + clawback_sum

            passed = (total_supply == total_distributed)

            result = {
                "passed": passed,
                "total_supply": total_supply,
                "reserve_balance": reserve_balance,
                "citizen_sum": citizen_sum,
                "merchant_sum": merchant_sum,
                "clawback_sum": clawback_sum,
                "total_distributed": total_distributed,
                "difference": total_supply - total_distributed
            }

            if passed:
                print(f"   ✅ 자산 보존 확인: {total_supply} = {total_distributed}")
            else:
                print(f"   ❌ 자산 보존 위반: {total_supply} ≠ {total_distributed}")
                print(f"      차이: {result['difference']}")

            return result

        except Exception as e:
            print(f"   ❌ 검증 실패: {e}")
            return {
                "passed": False,
                "error": str(e)
            }

    def verify_limit_compliance(self) -> Dict:
        """
        불변식 2: 한도 검증
        기간별_누적지급 ≤ 정책_최대치
        """
        print("\n2️⃣  한도 검증 중...")

        try:
            # Reserve Manager에서 데이터 로드
            from contracts.reserve_manager import ReserveManager
            manager = ReserveManager()

            violations = []

            # 모든 발급 기록 확인
            for record in manager.issuance_records:
                user_id = record.user_id

                # 사용자 총 발급량
                user_summary = manager.get_user_issuance_summary(user_id)
                total_issued = user_summary["total_issued"]

                # 한도 확인 (임시로 2025-Q1 사용)
                allocation = manager.budget_allocations.get("2025-Q1")
                if allocation:
                    limit = allocation.per_person_limit

                    if total_issued > limit:
                        violations.append({
                            "user_id": user_id,
                            "total_issued": total_issued,
                            "limit": limit,
                            "excess": total_issued - limit
                        })

            passed = (len(violations) == 0)

            result = {
                "passed": passed,
                "violations_count": len(violations),
                "violations": violations
            }

            if passed:
                print(f"   ✅ 한도 준수 확인")
            else:
                print(f"   ❌ 한도 위반 발견: {len(violations)}건")
                for v in violations[:3]:
                    print(f"      - {v['user_id']}: {v['total_issued']} > {v['limit']}")

            return result

        except Exception as e:
            print(f"   ❌ 검증 실패: {e}")
            return {
                "passed": False,
                "error": str(e)
            }

    def verify_clawback_compliance(self) -> Dict:
        """
        불변식 3: 회수 검증
        회수계정_ASA잔량 = 0 (회수 후 즉시 처리)
        """
        print("\n3️⃣  회수 검증 중...")

        try:
            if not self.clawback_address:
                return {
                    "passed": True,
                    "note": "회수 계정 미설정"
                }

            clawback_balance = self._get_asset_balance(self.clawback_address) or 0

            passed = (clawback_balance == 0)

            result = {
                "passed": passed,
                "clawback_address": self.clawback_address,
                "balance": clawback_balance
            }

            if passed:
                print(f"   ✅ 회수 계정 잔액 0 확인")
            else:
                print(f"   ⚠️  회수 계정 잔액 존재: {clawback_balance}")
                print(f"      (회수 후 미처리 자산이 있을 수 있음)")

            return result

        except Exception as e:
            print(f"   ❌ 검증 실패: {e}")
            return {
                "passed": False,
                "error": str(e)
            }

    def verify_audit_trail(self) -> Dict:
        """
        불변식 4: 감사 검증
        정책버전별_증빙해시 ≥ 1건
        """
        print("\n4️⃣  감사 증적 검증 중...")

        try:
            # ASA 메타데이터 확인
            asset_info = self.algod_client.asset_info(self.asset_id)
            metadata_hash = asset_info["params"].get("metadata-hash")

            passed = (metadata_hash is not None and len(metadata_hash) > 0)

            result = {
                "passed": passed,
                "asset_id": self.asset_id,
                "has_metadata_hash": metadata_hash is not None
            }

            if passed:
                print(f"   ✅ 메타데이터 해시 존재 확인")
            else:
                print(f"   ❌ 메타데이터 해시 없음")

            return result

        except Exception as e:
            print(f"   ❌ 검증 실패: {e}")
            return {
                "passed": False,
                "error": str(e)
            }

    def _get_asset_balance(self, address: str) -> Optional[int]:
        """계정의 ASA 잔액 조회"""
        if not address:
            return None

        try:
            account_info = self.algod_client.account_info(address)
            assets = account_info.get("assets", [])

            for asset in assets:
                if asset["asset-id"] == self.asset_id:
                    return asset["amount"]

            return 0

        except Exception as e:
            print(f"⚠️  잔액 조회 실패 ({address[:10]}...): {e}")
            return None

    def generate_compliance_report(self) -> str:
        """규정 준수 리포트 생성"""
        results = self.verify_all_invariants()

        report = f"""
================================================================================
불변식 검증 리포트
================================================================================
생성 시간: {json.dumps(results, indent=2, ensure_ascii=False)}

1. 자산 보존 검증
   - 통과: {results['asset_conservation']['passed']}
   - 총 발행량: {results['asset_conservation'].get('total_supply', 'N/A')}
   - 분산 합계: {results['asset_conservation'].get('total_distributed', 'N/A')}

2. 한도 검증
   - 통과: {results['limit_compliance']['passed']}
   - 위반 건수: {results['limit_compliance'].get('violations_count', 0)}

3. 회수 검증
   - 통과: {results['clawback_compliance']['passed']}
   - 회수 잔액: {results['clawback_compliance'].get('balance', 'N/A')}

4. 감사 증적
   - 통과: {results['audit_trail']['passed']}
   - 메타데이터: {results['audit_trail'].get('has_metadata_hash', False)}

전체 결과: {'✅ 통과' if results['all_passed'] else '❌ 위반'}
================================================================================
        """

        return report


def main():
    """불변식 검증 테스트"""
    from algosdk.v2client import algod

    # Algorand 클라이언트
    algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")

    # Asset ID (테스트용)
    asset_id = 123456  # 실제 ASA ID로 변경

    # 검증기 생성
    verifier = InvariantVerifier(algod_client, asset_id)

    # 전체 검증
    results = verifier.verify_all_invariants()

    # 리포트 생성
    report = verifier.generate_compliance_report()
    print(report)


if __name__ == "__main__":
    main()
