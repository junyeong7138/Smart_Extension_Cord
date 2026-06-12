#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
safety_limits.py
================
기기별 안전 자동차단 한도(초)의 *단일 진실 소스*.

`safety_limits.json` (이 파일과 같은 디렉터리)에 기기별 연속 동작 한도(초)를 저장한다.
SocketOrchestrator 의 monitor loop 가 ASSIGNED(기기 동작 중) 연속 시간을 이 한도와
비교해서, 80% 도달 시 UI 경고(소켓 테두리 빨간 깜빡임 + 카운트다운), 100% 도달 시
릴레이 자동 차단(DEVICE_OFF → 대기전력 절약 누적에 포함)한다.

규칙
----
- 0 = 무제한 (tv/charger 기본 — 장시간 사용이 정상 패턴).
- 파일이 없거나 깨졌으면 기본값으로 자동 (재)생성 → 첫 실행/파손에도 항상 동작.
- 저장은 임시파일 + os.replace 로 *원자적* (저장 중 전원 차단 시 JSON 파손 방지).
- Settings UI (모니터 socket_dashboard / 모바일 mobile_ui) 의 Limit 메뉴에서 편집 →
  set_all() 이 파일에 즉시 반영 → 재시작 후에도 사용자 설정 유지. 메모리 값도 같이
  갱신되므로 orchestrator 는 재시작 없이 다음 monitor tick 부터 새 한도를 참조한다.
"""

import json
import logging
import os
import threading

# 시연용 기본값(초). "고전력·발열 기기일수록 한도가 짧다" 원칙.
# (실제 제품 기준은 dryer 600s/10분 · microwave 1200s/20분 · cleaner 2400s/40분 —
#  발표장에서 기다릴 수 있도록 기본값은 단축판.)
DEFAULT_LIMITS_S = {
    "dryer": 30,
    "microwave": 60,
    "cleaner": 90,
    "tv": 0,        # 0 = 무제한
    "charger": 0,   # 0 = 무제한
}

# 설정 UI 상한 (30분). 스테퍼/입력 검증용.
MAX_LIMIT_S = 1800

LIMITS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "safety_limits.json"
)


def _clamp(value):
    """한도값 정규화: int 변환 + [0, MAX_LIMIT_S] 클램프. 변환 불가면 0(무제한)."""
    try:
        v = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return min(MAX_LIMIT_S, max(0, v))


class SafetyLimits:
    """기기별 한도(초) 로드/저장. thread-safe (UI 저장 thread vs monitor 읽기 thread)."""

    def __init__(self, path=LIMITS_PATH):
        self.path = path
        self._lock = threading.Lock()
        self._limits = dict(DEFAULT_LIMITS_S)
        self.load()

    # -----------------------------------------------------------------
    def load(self):
        """파일 → 메모리. 없거나 깨졌으면 기본값으로 재생성. 반환: 현재 한도 dict."""
        with self._lock:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("limits json 최상위가 dict 가 아님")
                # 알려진 기기만 채택, 빠진 키는 기본값 유지 (미래 키 추가에도 안전)
                merged = dict(DEFAULT_LIMITS_S)
                for dev in DEFAULT_LIMITS_S:
                    if dev in data:
                        merged[dev] = _clamp(data[dev])
                self._limits = merged
                logging.info(f"[SAFETY-LIMITS] 로드: {self._limits} ({self.path})")
                return dict(self._limits)
            except FileNotFoundError:
                logging.info(f"[SAFETY-LIMITS] {self.path} 없음 → 기본값으로 생성")
            except Exception as e:  # noqa: BLE001
                logging.warning(
                    f"[SAFETY-LIMITS] {self.path} 로드 실패({e}) → 기본값으로 재생성"
                )
            self._limits = dict(DEFAULT_LIMITS_S)
            self._save_locked()
            return dict(self._limits)

    def _save_locked(self):
        """원자적 저장 (호출자가 self._lock 보유 가정): tmp 에 쓰고 os.replace."""
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._limits, f, indent=2, ensure_ascii=False)
                f.write("\n")
            os.replace(tmp, self.path)
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[SAFETY-LIMITS] 저장 실패: {e}")

    # -----------------------------------------------------------------
    def get(self, device):
        """기기 한도(초). 0 = 무제한. 미등록 기기/None 도 0."""
        if not device:
            return 0
        with self._lock:
            return int(self._limits.get(device, 0))

    def get_all(self):
        with self._lock:
            return dict(self._limits)

    def set_all(self, new_limits):
        """부분/전체 dict 로 한도 갱신 + 파일 저장. 알려진 기기 외 키는 무시.
        반환: 갱신된 전체 한도 dict (UI 응답용)."""
        if not isinstance(new_limits, dict):
            raise ValueError("limits 는 dict 여야 합니다")
        with self._lock:
            for dev in DEFAULT_LIMITS_S:
                if dev in new_limits:
                    self._limits[dev] = _clamp(new_limits[dev])
            self._save_locked()
            logging.info(f"[SAFETY-LIMITS] 저장: {self._limits} ({self.path})")
            return dict(self._limits)


# =====================================================================
# CLI 자가 테스트 (Mac에서 python RaspberryPi/control/safety_limits.py)
# =====================================================================
if __name__ == "__main__":
    import tempfile

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "safety_limits.json")

        print("=== 케이스 A: 파일 없음 → 기본값 자동 생성 ===")
        sl = SafetyLimits(path=p)
        assert os.path.exists(p), "파일이 생성되지 않음!"
        assert sl.get("dryer") == 30 and sl.get("tv") == 0
        print(f"  ✅ {sl.get_all()}")

        print("=== 케이스 B: set_all 저장 → 새 인스턴스로 재로드(재시작 시뮬) ===")
        sl.set_all({"dryer": 45, "microwave": 120, "unknown_dev": 999, "cleaner": -5})
        sl2 = SafetyLimits(path=p)
        assert sl2.get("dryer") == 45, "dryer 저장/재로드 실패!"
        assert sl2.get("microwave") == 120
        assert sl2.get("cleaner") == 0, "음수가 0 으로 클램프되지 않음!"
        assert "unknown_dev" not in sl2.get_all(), "알 수 없는 기기가 저장됨!"
        print(f"  ✅ {sl2.get_all()}")

        print("=== 케이스 C: 파일 파손 → 기본값 복구 ===")
        with open(p, "w", encoding="utf-8") as f:
            f.write("{ broken json !!!")
        sl3 = SafetyLimits(path=p)
        assert sl3.get("dryer") == 30, "파손 파일에서 기본값 복구 실패!"
        print(f"  ✅ {sl3.get_all()}")

        print("=== 케이스 D: 상한 클램프 (MAX_LIMIT_S) ===")
        sl3.set_all({"tv": 99999})
        assert sl3.get("tv") == MAX_LIMIT_S
        print(f"  ✅ tv={sl3.get('tv')} (≤{MAX_LIMIT_S})")

    print("\n✅ ALL PASS")
