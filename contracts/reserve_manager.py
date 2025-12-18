#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reserve 계정 관리
PRD 3.2: Reserve 권한 - 미발행량 보유·배분

주요 기능:
- 예산 관리 (연/월/분기)
- 1인당 한도 설정
- 배분 이력 추적
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class BudgetAllocation:
    """예산 배분 정보"""
    allocation_id: str
    period: str  # "2025-Q1", "2025-01"
    total_budget: int
    allocated: int
    remaining: int
    per_person_limit: int
    created_at: str


@dataclass
class IssuanceRecord:
    """발급 기록"""
    record_id: str
    user_id: str
    amount: int
    reason: str  # "carbon_reduction", "local_food_purchase"
    tx_id: str
    timestamp: str


class ReserveManager:
    """Reserve 계정 관리자"""

    def __init__(self, config_file: str = "./config/budget_config.json"):
        self.config_file = config_file
        self.budget_allocations: Dict[str, BudgetAllocation] = {}
        self.issuance_records: List[IssuanceRecord] = []
        self._load_config()

    def _load_config(self):
        """설정 로드"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.budget_allocations = {
                    k: BudgetAllocation(**v)
                    for k, v in data.get("allocations", {}).items()
                }
                self.issuance_records = [
                    IssuanceRecord(**r)
                    for r in data.get("issuance_records", [])
                ]
        except FileNotFoundError:
            self._initialize_default_config()

    def _save_config(self):
        """설정 저장"""
        data = {
            "allocations": {
                k: asdict(v) for k, v in self.budget_allocations.items()
            },
            "issuance_records": [asdict(r) for r in self.issuance_records]
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _initialize_default_config(self):
        """기본 설정 초기화"""
        # 2025년 Q1 예산
        allocation = BudgetAllocation(
            allocation_id="2025-Q1",
            period="2025-Q1",
            total_budget=1000000,  # 100만개
            allocated=0,
            remaining=1000000,
            per_person_limit=5000,  # 1인당 5,000개
            created_at=datetime.now().isoformat()
        )
        self.budget_allocations["2025-Q1"] = allocation
        self._save_config()

    def set_budget(
        self,
        period: str,
        total_budget: int,
        per_person_limit: int
    ) -> BudgetAllocation:
        """
        예산 설정
        PRD 2.2: 예산 관리

        Args:
            period: 기간 (예: "2025-Q1", "2025-01")
            total_budget: 총 예산
            per_person_limit: 1인당 한도
        """
        allocation = BudgetAllocation(
            allocation_id=period,
            period=period,
            total_budget=total_budget,
            allocated=0,
            remaining=total_budget,
            per_person_limit=per_person_limit,
            created_at=datetime.now().isoformat()
        )

        self.budget_allocations[period] = allocation
        self._save_config()

        print(f"[OK] Budget set: {period}")
        print(f"     Total budget: {total_budget:,}")
        print(f"     Per-person limit: {per_person_limit:,}")

        return allocation

    def check_issuance_allowed(
        self,
        user_id: str,
        amount: int,
        period: str
    ) -> Dict:
        """
        발급 가능 여부 확인
        PRD 2.2: 1인당 한도 설정

        Returns:
            Dict: {"allowed": bool, "reason": str}
        """
        # 예산 확인
        if period not in self.budget_allocations:
            return {
                "allowed": False,
                "reason": f"예산 기간 {period} 없음"
            }

        allocation = self.budget_allocations[period]

        # 예산 잔액 확인
        if allocation.remaining < amount:
            return {
                "allowed": False,
                "reason": f"예산 부족 (잔액: {allocation.remaining})"
            }

        # 1인 한도 확인
        user_total = self._get_user_total_issuance(user_id, period)
        if user_total + amount > allocation.per_person_limit:
            return {
                "allowed": False,
                "reason": f"1인 한도 초과 (현재: {user_total}, 한도: {allocation.per_person_limit})"
            }

        return {
            "allowed": True,
            "reason": "발급 가능"
        }

    def _get_user_total_issuance(self, user_id: str, period: str) -> int:
        """사용자의 기간별 누적 발급량 조회"""
        total = 0
        for record in self.issuance_records:
            # 기간 매칭 (간단히 timestamp로 비교)
            if record.user_id == user_id:
                # TODO: 실제로는 timestamp를 파싱하여 period와 비교
                total += record.amount
        return total

    def record_issuance(
        self,
        user_id: str,
        amount: int,
        reason: str,
        tx_id: str,
        period: str
    ) -> IssuanceRecord:
        """
        발급 기록 저장
        PRD 2.2: 배분 이력 추적
        """
        record = IssuanceRecord(
            record_id=f"ISS-{len(self.issuance_records)+1:06d}",
            user_id=user_id,
            amount=amount,
            reason=reason,
            tx_id=tx_id,
            timestamp=datetime.now().isoformat()
        )

        self.issuance_records.append(record)

        # 예산 차감
        if period in self.budget_allocations:
            allocation = self.budget_allocations[period]
            allocation.allocated += amount
            allocation.remaining -= amount

        self._save_config()

        print(f"[OK] Issuance recorded: {user_id} -> {amount}")

        return record

    def get_budget_status(self, period: str) -> Optional[Dict]:
        """예산 현황 조회"""
        if period not in self.budget_allocations:
            return None

        allocation = self.budget_allocations[period]

        return {
            "period": allocation.period,
            "total_budget": allocation.total_budget,
            "allocated": allocation.allocated,
            "remaining": allocation.remaining,
            "utilization_rate": (allocation.allocated / allocation.total_budget) * 100,
            "per_person_limit": allocation.per_person_limit
        }

    def get_user_issuance_summary(self, user_id: str) -> Dict:
        """사용자 발급 내역 요약"""
        user_records = [
            r for r in self.issuance_records if r.user_id == user_id
        ]

        total_amount = sum(r.amount for r in user_records)

        return {
            "user_id": user_id,
            "total_issued": total_amount,
            "issuance_count": len(user_records),
            "records": [asdict(r) for r in user_records[-10:]]  # 최근 10건
        }

    def get_top_recipients(self, limit: int = 10) -> List[Dict]:
        """상위 수혜자 조회"""
        user_totals = {}

        for record in self.issuance_records:
            if record.user_id not in user_totals:
                user_totals[record.user_id] = 0
            user_totals[record.user_id] += record.amount

        sorted_users = sorted(
            user_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [
            {"user_id": user_id, "total_issued": amount}
            for user_id, amount in sorted_users
        ]


def main():
    """Reserve Manager 테스트"""
    manager = ReserveManager()

    # 예산 설정
    manager.set_budget(
        period="2025-Q1",
        total_budget=1000000,
        per_person_limit=5000
    )

    # 발급 가능 확인
    check = manager.check_issuance_allowed(
        user_id="user001",
        amount=1000,
        period="2025-Q1"
    )
    print(f"\n발급 가능 여부: {check}")

    # 발급 기록
    if check["allowed"]:
        record = manager.record_issuance(
            user_id="user001",
            amount=1000,
            reason="carbon_reduction",
            tx_id="TX123456",
            period="2025-Q1"
        )

    # 예산 현황
    status = manager.get_budget_status("2025-Q1")
    print(f"\n예산 현황: {json.dumps(status, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
