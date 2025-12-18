#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
정책 메타데이터 및 해시 앵커링
PRD 5.1, 5.2: 온·오프체인 데이터 분리

주요 기능:
- ARC-3 기반 메타데이터 생성
- SHA-256 해시 앵커링
- 오프체인 문서 IPFS 저장
"""

import json
import hashlib
from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class PolicyMetadata:
    """정책 메타데이터 (ARC-3 기반)"""
    name: str
    description: str
    policy_version: str
    valid_from: str
    valid_until: str
    reward_type: str  # "carbon_reduction", "local_food", etc.
    target_region: str
    image: Optional[str] = None
    properties: Optional[Dict] = None


@dataclass
class PolicyDocument:
    """정책 문서"""
    document_id: str
    title: str
    content: str
    version: str
    effective_date: str
    expiry_date: str
    issuer: str
    metadata: Dict
    created_at: str


class PolicyMetadataManager:
    """정책 메타데이터 관리자"""

    def __init__(self, storage_dir: str = "../config/policies"):
        import os
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def create_policy_metadata(
        self,
        name: str,
        description: str,
        policy_version: str,
        valid_from: str,
        valid_until: str,
        reward_type: str,
        target_region: str,
        image_url: Optional[str] = None,
        properties: Optional[Dict] = None
    ) -> PolicyMetadata:
        """
        정책 메타데이터 생성 (ARC-3)
        PRD 5.2

        Returns:
            PolicyMetadata: 메타데이터 객체
        """
        metadata = PolicyMetadata(
            name=name,
            description=description,
            policy_version=policy_version,
            valid_from=valid_from,
            valid_until=valid_until,
            reward_type=reward_type,
            target_region=target_region,
            image=image_url,
            properties=properties or {}
        )

        print(f"✅ 정책 메타데이터 생성: {name}")
        print(f"   버전: {policy_version}")
        print(f"   유효기간: {valid_from} ~ {valid_until}")

        return metadata

    def generate_metadata_json(self, metadata: PolicyMetadata) -> str:
        """ARC-3 JSON 생성"""
        arc3_metadata = {
            "name": metadata.name,
            "description": metadata.description,
            "image": metadata.image,
            "properties": {
                "policy_version": metadata.policy_version,
                "valid_from": metadata.valid_from,
                "valid_until": metadata.valid_until,
                "reward_type": metadata.reward_type,
                "target_region": metadata.target_region,
                **metadata.properties
            }
        }

        return json.dumps(arc3_metadata, indent=2, ensure_ascii=False)

    def calculate_metadata_hash(self, metadata_json: str) -> str:
        """
        메타데이터 SHA-256 해시 계산
        PRD 3.1: metadataHash 파라미터
        """
        hash_bytes = hashlib.sha256(metadata_json.encode()).digest()
        hash_hex = hash_bytes.hex()

        print(f"✅ 메타데이터 해시: {hash_hex[:16]}...")

        return hash_hex

    def create_policy_document(
        self,
        title: str,
        content: str,
        version: str,
        effective_date: str,
        expiry_date: str,
        issuer: str,
        metadata: Dict
    ) -> PolicyDocument:
        """
        정책 문서 생성
        PRD 5.1: 오프체인 문서

        Returns:
            PolicyDocument: 정책 문서 객체
        """
        doc_id = f"POL-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        document = PolicyDocument(
            document_id=doc_id,
            title=title,
            content=content,
            version=version,
            effective_date=effective_date,
            expiry_date=expiry_date,
            issuer=issuer,
            metadata=metadata,
            created_at=datetime.now().isoformat()
        )

        # 파일로 저장
        filepath = f"{self.storage_dir}/{doc_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(document), f, indent=2, ensure_ascii=False)

        print(f"✅ 정책 문서 생성: {doc_id}")
        print(f"   저장 위치: {filepath}")

        return document

    def anchor_hash_to_blockchain(
        self,
        policy_hash: str,
        asset_id: int
    ) -> Dict:
        """
        정책 해시를 블록체인에 앵커링
        PRD 5.1: 증빙 해시 앵커링

        Note: 실제로는 ASA 메타데이터나 별도 트랜잭션 note에 기록
        """
        anchor_record = {
            "anchor_id": f"ANCHOR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "policy_hash": policy_hash,
            "asset_id": asset_id,
            "timestamp": datetime.now().isoformat(),
            "blockchain": "Algorand"
        }

        # 앵커 기록 저장
        anchor_file = f"{self.storage_dir}/anchors.json"
        try:
            with open(anchor_file, 'r') as f:
                anchors = json.load(f)
        except FileNotFoundError:
            anchors = []

        anchors.append(anchor_record)

        with open(anchor_file, 'w', encoding='utf-8') as f:
            json.dump(anchors, f, indent=2, ensure_ascii=False)

        print(f"✅ 해시 앵커링 완료")
        print(f"   Policy Hash: {policy_hash[:16]}...")
        print(f"   Asset ID: {asset_id}")

        return anchor_record

    def verify_policy_integrity(
        self,
        policy_document: PolicyDocument,
        stored_hash: str
    ) -> bool:
        """
        정책 문서 무결성 검증

        Args:
            policy_document: 정책 문서
            stored_hash: 블록체인에 저장된 해시

        Returns:
            bool: 무결성 검증 결과
        """
        # 문서 내용 해시 계산
        doc_json = json.dumps(asdict(policy_document), sort_keys=True)
        calculated_hash = hashlib.sha256(doc_json.encode()).hexdigest()

        is_valid = (calculated_hash == stored_hash)

        if is_valid:
            print(f"✅ 정책 문서 무결성 검증 통과")
        else:
            print(f"❌ 정책 문서 무결성 검증 실패!")
            print(f"   계산된 해시: {calculated_hash[:16]}...")
            print(f"   저장된 해시: {stored_hash[:16]}...")

        return is_valid

    def get_policy_by_version(self, version: str) -> Optional[PolicyDocument]:
        """버전별 정책 문서 조회"""
        import os
        import glob

        pattern = f"{self.storage_dir}/POL-*.json"
        files = glob.glob(pattern)

        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                if doc_data.get("version") == version:
                    return PolicyDocument(**doc_data)

        return None

    def list_all_policies(self) -> list:
        """모든 정책 목록 조회"""
        import os
        import glob

        pattern = f"{self.storage_dir}/POL-*.json"
        files = glob.glob(pattern)

        policies = []
        for filepath in files:
            with open(filepath, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                policies.append({
                    "document_id": doc_data["document_id"],
                    "title": doc_data["title"],
                    "version": doc_data["version"],
                    "effective_date": doc_data["effective_date"],
                    "issuer": doc_data["issuer"]
                })

        return policies


def main():
    """정책 메타데이터 관리 테스트"""
    manager = PolicyMetadataManager()

    # 1. 정책 메타데이터 생성
    metadata = manager.create_policy_metadata(
        name="PAM-TALK ESG Coupon 2025",
        description="시민참여형 탄소중립 보상 쿠폰",
        policy_version="v1.0",
        valid_from="2025-01-01",
        valid_until="2025-12-31",
        reward_type="carbon_reduction",
        target_region="전국",
        image_url="ipfs://QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        properties={
            "issuer": "중앙정부",
            "department": "환경부",
            "contact": "esg@gov.kr"
        }
    )

    # 2. ARC-3 JSON 생성
    metadata_json = manager.generate_metadata_json(metadata)
    print(f"\n📄 ARC-3 메타데이터:")
    print(metadata_json)

    # 3. 메타데이터 해시 계산
    metadata_hash = manager.calculate_metadata_hash(metadata_json)

    # 4. 정책 문서 생성
    policy_doc = manager.create_policy_document(
        title="2025년 PAM-Talk ESG 디지털 쿠폰 발행 및 운영 지침",
        content="""
        제1조 (목적)
        이 지침은 시민참여형 ESG 활동을 장려하고 탄소중립 실현을 위한 디지털 쿠폰 발행 및 운영에 관한 사항을 규정함을 목적으로 한다.

        제2조 (정의)
        1. "디지털 쿠폰"이란 Algorand 블록체인 기반 ASA로 발행된 보상 토큰을 말한다.
        2. "탄소중립 활동"이란 온실가스 배출을 줄이는 개인 또는 단체의 행위를 말한다.

        제3조 (발행 주체)
        디지털 쿠폰은 중앙정부 환경부가 발행하며, 지방자치단체가 위탁 집행할 수 있다.
        """,
        version="v1.0",
        effective_date="2025-01-01",
        expiry_date="2025-12-31",
        issuer="중앙정부 환경부",
        metadata=asdict(metadata)
    )

    # 5. 블록체인 앵커링
    anchor = manager.anchor_hash_to_blockchain(
        policy_hash=metadata_hash,
        asset_id=123456  # 실제 ASA ID
    )

    print(f"\n✅ 앵커 기록:")
    print(json.dumps(anchor, indent=2, ensure_ascii=False))

    # 6. 정책 목록 조회
    print(f"\n📋 등록된 정책 목록:")
    policies = manager.list_all_policies()
    for policy in policies:
        print(f"  - {policy['document_id']}: {policy['title']} ({policy['version']})")


if __name__ == "__main__":
    main()
