#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
차등 보상 계산기 테스트
"""

import sys
sys.path.append("..")

import pytest
from policies.reward_calculator import (
    RewardCalculator,
    IncomeLevel,
    RegionType,
    ActivityType
)


class TestRewardCalculator:
    """보상 계산기 테스트"""

    def setup_method(self):
        """테스트 초기화"""
        self.calculator = RewardCalculator()

    def test_basic_reward_no_multiplier(self):
        """기본 보상 (가중치 없음)"""
        result = self.calculator.calculate_reward(
            base_amount=1000,
            income_level=IncomeLevel.HIGH,
            region_type=RegionType.URBAN,
            activity_type=ActivityType.BASIC
        )

        assert result["base_amount"] == 1000
        assert result["final_amount"] == 1000
        assert result["bonus_amount"] == 0
        assert result["total_multiplier"] == 1.0

    def test_low_income_multiplier(self):
        """저소득 가중치 (1.5x)"""
        result = self.calculator.calculate_reward(
            base_amount=1000,
            income_level=IncomeLevel.LOW,
            region_type=RegionType.URBAN,
            activity_type=ActivityType.BASIC
        )

        assert result["income_multiplier"] == 1.5
        assert result["final_amount"] == 1500

    def test_rural_region_multiplier(self):
        """농어촌 가중치 (1.3x)"""
        result = self.calculator.calculate_reward(
            base_amount=1000,
            income_level=IncomeLevel.HIGH,
            region_type=RegionType.RURAL,
            activity_type=ActivityType.BASIC
        )

        assert result["region_multiplier"] == 1.3
        assert result["final_amount"] == 1300

    def test_carbon_neutral_activity_multiplier(self):
        """탄소중립 활동 가중치 (2.0x)"""
        result = self.calculator.calculate_reward(
            base_amount=1000,
            income_level=IncomeLevel.HIGH,
            region_type=RegionType.URBAN,
            activity_type=ActivityType.CARBON_NEUTRAL
        )

        assert result["activity_multiplier"] == 2.0
        assert result["final_amount"] == 2000

    def test_maximum_multiplier(self):
        """최대 가중치 (1.5 × 1.3 × 2.0 = 3.9x)"""
        result = self.calculator.calculate_reward(
            base_amount=1000,
            income_level=IncomeLevel.LOW,
            region_type=RegionType.RURAL,
            activity_type=ActivityType.CARBON_NEUTRAL
        )

        assert result["income_multiplier"] == 1.5
        assert result["region_multiplier"] == 1.3
        assert result["activity_multiplier"] == 2.0
        assert result["total_multiplier"] == 3.9
        assert result["final_amount"] == 3900

    def test_income_decile_conversion(self):
        """소득 10분위 → 레벨 변환"""
        assert self.calculator.get_income_level(1) == IncomeLevel.LOW
        assert self.calculator.get_income_level(3) == IncomeLevel.LOW
        assert self.calculator.get_income_level(4) == IncomeLevel.MIDDLE
        assert self.calculator.get_income_level(7) == IncomeLevel.MIDDLE
        assert self.calculator.get_income_level(8) == IncomeLevel.HIGH
        assert self.calculator.get_income_level(10) == IncomeLevel.HIGH

    def test_zero_base_amount(self):
        """기본 보상 0원"""
        result = self.calculator.calculate_reward(
            base_amount=0,
            income_level=IncomeLevel.LOW,
            region_type=RegionType.RURAL,
            activity_type=ActivityType.CARBON_NEUTRAL
        )

        assert result["final_amount"] == 0

    def test_large_base_amount(self):
        """큰 금액 보상"""
        result = self.calculator.calculate_reward(
            base_amount=1000000,
            income_level=IncomeLevel.LOW,
            region_type=RegionType.RURAL,
            activity_type=ActivityType.CARBON_NEUTRAL
        )

        assert result["final_amount"] == 3900000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
