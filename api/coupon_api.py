#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디지털 쿠폰 API
PRD 기반 REST API 엔드포인트

주요 기능:
- 쿠폰 발급
- 잔액 조회
- 사용·정산
- 회수 처리
"""

import sys
sys.path.append("..")

from flask import Flask, request, jsonify
from flask_cors import CORS
from algosdk.v2client import algod

from contracts.esg_coupon_asa import ESGCouponASA
from contracts.reserve_manager import ReserveManager
from policies.reward_calculator import (
    RewardCalculator,
    IncomeLevel,
    RegionType,
    ActivityType
)
from verification.invariants import InvariantVerifier
from security.multisig_handler import MultiSigHandler


app = Flask(__name__)
CORS(app)

# Algorand 클라이언트
algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")

# 서비스 초기화
asa_service = ESGCouponASA(algod_address="https://testnet-api.algonode.cloud")
reserve_manager = ReserveManager()
reward_calculator = RewardCalculator()


@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        "status": "healthy",
        "service": "PAM-Talk Digital Coupon API",
        "version": "1.0.0"
    })


@app.route('/api/coupon/info', methods=['GET'])
def get_coupon_info():
    """
    쿠폰 정보 조회
    PRD 8: 성능 및 제약사항
    """
    try:
        # Asset ID (config에서 로드)
        import json
        with open("../config/asa_config.json", 'r') as f:
            config = json.load(f)
            asset_id = config["asset_id"]

        asset_info = asa_service.get_asset_info(asset_id)

        return jsonify({
            "success": True,
            "data": {
                "asset_id": asset_id,
                "name": asset_info["params"]["name"],
                "unit_name": asset_info["params"]["unit-name"],
                "total_supply": asset_info["params"]["total"],
                "decimals": asset_info["params"]["decimals"],
                "creator": asset_info["params"]["creator"],
                "manager": asset_info["params"]["manager"],
                "reserve": asset_info["params"]["reserve"],
                "freeze": asset_info["params"]["freeze"],
                "clawback": asset_info["params"]["clawback"]
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/coupon/balance/<address>', methods=['GET'])
def get_balance(address: str):
    """
    잔액 조회
    PRD 2.1: 수령(Receive) 상태 확인
    """
    try:
        import json
        with open("../config/asa_config.json", 'r') as f:
            config = json.load(f)
            asset_id = config["asset_id"]

        balance = asa_service.get_account_asset_balance(address, asset_id)

        if balance is None:
            return jsonify({
                "success": False,
                "error": "계정이 ASA를 opt-in하지 않았습니다."
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "address": address,
                "asset_id": asset_id,
                "balance": balance
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/coupon/calculate-reward', methods=['POST'])
def calculate_reward():
    """
    보상 계산 (미리보기)
    PRD 2.2: 차등 보상
    """
    try:
        data = request.json

        # 파라미터 추출
        base_amount = data.get("base_amount", 1000)
        income_level = IncomeLevel(data.get("income_level", "middle"))
        region_type = RegionType(data.get("region_type", "urban"))
        activity_type = ActivityType(data.get("activity_type", "basic"))

        # 보상 계산
        result = reward_calculator.calculate_reward(
            base_amount=base_amount,
            income_level=income_level,
            region_type=region_type,
            activity_type=activity_type
        )

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/coupon/issue', methods=['POST'])
def issue_coupon():
    """
    쿠폰 발급
    PRD 2.1: 발급(Issue) S0→S1→S2

    요청 예시:
    {
        "user_id": "user001",
        "user_address": "ALGORAND_ADDRESS",
        "base_amount": 1000,
        "income_level": "low",
        "region_type": "rural",
        "activity_type": "carbon_neutral",
        "reason": "탄소중립 활동 참여"
    }
    """
    try:
        data = request.json

        user_id = data.get("user_id")
        user_address = data.get("user_address")
        base_amount = data.get("base_amount", 1000)

        # 차등 보상 계산
        income_level = IncomeLevel(data.get("income_level", "middle"))
        region_type = RegionType(data.get("region_type", "urban"))
        activity_type = ActivityType(data.get("activity_type", "basic"))

        reward_result = reward_calculator.calculate_reward(
            base_amount=base_amount,
            income_level=income_level,
            region_type=region_type,
            activity_type=activity_type
        )

        final_amount = reward_result["final_amount"]

        # 발급 가능 여부 확인
        check = reserve_manager.check_issuance_allowed(
            user_id=user_id,
            amount=final_amount,
            period="2025-Q1"
        )

        if not check["allowed"]:
            return jsonify({
                "success": False,
                "error": check["reason"]
            }), 403

        # Reserve에서 발급 (실제로는 private key 필요 - 보안상 별도 처리)
        # result = asa_service.transfer_from_reserve(...)

        # 발급 기록
        record = reserve_manager.record_issuance(
            user_id=user_id,
            amount=final_amount,
            reason=data.get("reason", "보상 지급"),
            tx_id="TX_SIMULATED",  # 실제로는 블록체인 TX ID
            period="2025-Q1"
        )

        return jsonify({
            "success": True,
            "data": {
                "record_id": record.record_id,
                "user_id": user_id,
                "amount_issued": final_amount,
                "reward_breakdown": reward_result,
                "tx_id": record.tx_id
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/coupon/budget/status', methods=['GET'])
def get_budget_status():
    """
    예산 현황 조회
    PRD 2.2: 예산 관리
    """
    try:
        period = request.args.get("period", "2025-Q1")
        status = reserve_manager.get_budget_status(period)

        if not status:
            return jsonify({
                "success": False,
                "error": f"예산 기간 {period} 없음"
            }), 404

        return jsonify({
            "success": True,
            "data": status
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/coupon/user/<user_id>/summary', methods=['GET'])
def get_user_summary(user_id: str):
    """
    사용자 발급 내역 요약
    PRD 2.2: 배분 이력 추적
    """
    try:
        summary = reserve_manager.get_user_issuance_summary(user_id)

        return jsonify({
            "success": True,
            "data": summary
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/coupon/verify-invariants', methods=['POST'])
def verify_invariants():
    """
    불변식 검증
    PRD 4.2: 필수 불변식
    """
    try:
        import json
        with open("../config/asa_config.json", 'r') as f:
            config = json.load(f)
            asset_id = config["asset_id"]

        verifier = InvariantVerifier(algod_client, asset_id)
        results = verifier.verify_all_invariants()

        return jsonify({
            "success": True,
            "data": results
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/admin/top-recipients', methods=['GET'])
def get_top_recipients():
    """
    상위 수혜자 조회
    관리자용 API
    """
    try:
        limit = int(request.args.get("limit", 10))
        top_recipients = reserve_manager.get_top_recipients(limit)

        return jsonify({
            "success": True,
            "data": top_recipients
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "엔드포인트를 찾을 수 없습니다."
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "서버 내부 오류가 발생했습니다."
    }), 500


if __name__ == "__main__":
    print("=" * 60)
    print("PAM-Talk 디지털 쿠폰 API 서버")
    print("=" * 60)
    print("주소: http://localhost:5000")
    print("문서: http://localhost:5000/health")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
