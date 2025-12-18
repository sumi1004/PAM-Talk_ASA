#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
차등 보상 계산기
PRD 2.2: 차등 보상 - 소득·지역·행동유형별 지급 강도 조정

보상 공식:
최종 보상 = 기본 보상 × 소득 가중치 × 지역 가중치 × 행동 가중치
"""

from typing import Dict
from dataclasses import dataclass
from enum import Enum


class IncomeLevel(Enum):
    """소득 분위"""
    LOW = "low"           # 저소득 (1~3분위)
    MIDDLE = "middle"     # 중소득 (4~7분위)
    HIGH = "high"         # 고소득 (8~10분위)


class RegionType(Enum):
    """지역 유형"""
    URBAN = "urban"           # 도시권
    SUBURBAN = "suburban"     # 도농복합
    RURAL = "rural"           # 농어촌


class ActivityType(Enum):
    """행동 유형"""
    BASIC = "basic"                     # 기본 활동
    LOCAL_FOOD = "local_food"           # 로컬푸드 구매
    PUBLIC_TRANSPORT = "public_transport"  # 대중교통 이용
    ENERGY_SAVING = "energy_saving"     # 에너지 절약
    RECYCLING = "recycling"             # 재활용
    CARBON_NEUTRAL = "carbon_neutral"   # 탄소중립 활동


@dataclass
class RewardMultipliers:
    """보상 가중치"""
    income_multiplier: float
    region_multiplier: float
    activity_multiplier: float

    def total_multiplier(self) -> float:
        """총 가중치"""
        return self.income_multiplier * self.region_multiplier * self.activity_multiplier


class RewardCalculator:
    """차등 보상 계산기"""

    # PRD 기반 가중치 설정
    INCOME_MULTIPLIERS = {
        IncomeLevel.LOW: 1.5,      # 150%
        IncomeLevel.MIDDLE: 1.2,   # 120%
        IncomeLevel.HIGH: 1.0      # 100%
    }

    REGION_MULTIPLIERS = {
        RegionType.URBAN: 1.0,     # 100%
        RegionType.SUBURBAN: 1.15, # 115%
        RegionType.RURAL: 1.3      # 130%
    }

    ACTIVITY_MULTIPLIERS = {
        ActivityType.BASIC: 1.0,              # 100%
        ActivityType.LOCAL_FOOD: 1.2,         # 120%
        ActivityType.PUBLIC_TRANSPORT: 1.3,   # 130%
        ActivityType.ENERGY_SAVING: 1.4,      # 140%
        ActivityType.RECYCLING: 1.5,          # 150%
        ActivityType.CARBON_NEUTRAL: 2.0      # 200%
    }

    def __init__(self):
        pass

    def calculate_reward(
        self,
        base_amount: int,
        income_level: IncomeLevel,
        region_type: RegionType,
        activity_type: ActivityType
    ) -> Dict:
        """
        차등 보상 계산
        PRD 2.2

        Args:
            base_amount: 기본 보상 금액
            income_level: 소득 분위
            region_type: 지역 유형
            activity_type: 행동 유형

        Returns:
            Dict: 계산 결과
        """
        # 가중치 조회
        income_mult = self.INCOME_MULTIPLIERS[income_level]
        region_mult = self.REGION_MULTIPLIERS[region_type]
        activity_mult = self.ACTIVITY_MULTIPLIERS[activity_type]

        multipliers = RewardMultipliers(
            income_multiplier=income_mult,
            region_multiplier=region_mult,
            activity_multiplier=activity_mult
        )

        # 최종 보상 계산
        total_mult = multipliers.total_multiplier()
        final_amount = int(base_amount * total_mult)

        result = {
            "base_amount": base_amount,
            "income_level": income_level.value,
            "income_multiplier": income_mult,
            "region_type": region_type.value,
            "region_multiplier": region_mult,
            "activity_type": activity_type.value,
            "activity_multiplier": activity_mult,
            "total_multiplier": total_mult,
            "final_amount": final_amount,
            "bonus_amount": final_amount - base_amount
        }

        return result

    def explain_calculation(self, result: Dict) -> str:
        """계산 과정 설명"""
        explanation = f"""
차등 보상 계산 결과
================================================================================
기본 보상:    {result['base_amount']:,} 쿠폰

가중치 적용:
  - 소득 ({result['income_level']}):     × {result['income_multiplier']:.2f}
  - 지역 ({result['region_type']}):     × {result['region_multiplier']:.2f}
  - 행동 ({result['activity_type']}): × {result['activity_multiplier']:.2f}

총 가중치:    × {result['total_multiplier']:.2f}
최종 보상:    {result['final_amount']:,} 쿠폰
보너스:       +{result['bonus_amount']:,} 쿠폰
================================================================================
        """
        return explanation

    def get_income_level(self, income_decile: int) -> IncomeLevel:
        """
        소득 10분위 → 소득 레벨 변환

        Args:
            income_decile: 소득 10분위 (1~10)

        Returns:
            IncomeLevel
        """
        if 1 <= income_decile <= 3:
            return IncomeLevel.LOW
        elif 4 <= income_decile <= 7:
            return IncomeLevel.MIDDLE
        else:
            return IncomeLevel.HIGH

    def simulate_rewards(self) -> None:
        """다양한 시나리오 시뮬레이션"""
        print("=" * 80)
        print("차등 보상 시뮬레이션")
        print("=" * 80)

        scenarios = [
            {
                "name": "시나리오 1: 저소득 농어촌 탄소중립 활동",
                "base": 1000,
                "income": IncomeLevel.LOW,
                "region": RegionType.RURAL,
                "activity": ActivityType.CARBON_NEUTRAL
            },
            {
                "name": "시나리오 2: 고소득 도시 기본 활동",
                "base": 1000,
                "income": IncomeLevel.HIGH,
                "region": RegionType.URBAN,
                "activity": ActivityType.BASIC
            },
            {
                "name": "시나리오 3: 중소득 도농복합 로컬푸드 구매",
                "base": 1000,
                "income": IncomeLevel.MIDDLE,
                "region": RegionType.SUBURBAN,
                "activity": ActivityType.LOCAL_FOOD
            },
            {
                "name": "시나리오 4: 저소득 도시 대중교통 이용",
                "base": 1000,
                "income": IncomeLevel.LOW,
                "region": RegionType.URBAN,
                "activity": ActivityType.PUBLIC_TRANSPORT
            }
        ]

        for scenario in scenarios:
            print(f"\n{scenario['name']}")
            print("-" * 80)

            result = self.calculate_reward(
                base_amount=scenario['base'],
                income_level=scenario['income'],
                region_type=scenario['region'],
                activity_type=scenario['activity']
            )

            print(f"기본: {result['base_amount']:,} → 최종: {result['final_amount']:,} "
                  f"(+{result['bonus_amount']:,}, ×{result['total_multiplier']:.2f})")


def main():
    """보상 계산기 테스트"""
    calculator = RewardCalculator()

    # 예시 1: 저소득 농어촌 거주자의 탄소중립 활동
    result1 = calculator.calculate_reward(
        base_amount=1000,
        income_level=IncomeLevel.LOW,
        region_type=RegionType.RURAL,
        activity_type=ActivityType.CARBON_NEUTRAL
    )

    print(calculator.explain_calculation(result1))

    # 예시 2: 고소득 도시 거주자의 기본 활동
    result2 = calculator.calculate_reward(
        base_amount=1000,
        income_level=IncomeLevel.HIGH,
        region_type=RegionType.URBAN,
        activity_type=ActivityType.BASIC
    )

    print(calculator.explain_calculation(result2))

    # 시뮬레이션
    calculator.simulate_rewards()


if __name__ == "__main__":
    main()
