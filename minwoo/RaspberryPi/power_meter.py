#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
power_meter.py
==============
각 가전의 *실시간 전력(W)* 추정. UI(socket_dashboard / mobile_ui) 전용 표시 계산.

설계 배경
---------
이 시스템은 CT/PT 가 멀티탭 전체 1쌍뿐이라, 물리적으로 직접 측정되는 건 항상
"멀티탭 전체 합산 전력" 이다 (win_feat["P_proxy_mean"], 매 frame 실시간 갱신).
개별 소켓 전력은 *직접 측정 불가* → 아래 방식으로 추정한다.

추정 방식 ("전체 → 기기별 실시간 배분")
----------------------------------------
    전체 실시간 W = CALIB_PROXY_TO_W × |P_proxy_mean|        (전체, 매 frame)
    기기 i 의 W  = 전체 W × (weight_i / Σ weight)            (기기별 비율)

- weight_i 는 그 기기 ON 등록 시점에 측정해둔 signature 의 |delta_pabs|.
  (각 가전이 단독으로 더한 순시전력 크기 → 기기간 상대 비율의 실측 근거)
- 비율 배분이라 weight 의 절대 단위는 무관하고, 소켓 W 합 = 전체 W 가 보장된다.
- 전체 전력이 변하면(예: dryer 약→강) 각 소켓 W 도 비례해 실시간으로 변동한다.

이 모듈은 *읽기 전용* 이다. engine/orchestrator 상태를 바꾸지 않으므로 기존
분류/OFF 흐름에 어떤 영향도 주지 않는다.
"""

import logging

# =====================================================================
# 실측 보정 계수
# =====================================================================
# 실제 유효전력(W) = CALIB_PROXY_TO_W × |P_proxy_mean(전체)|
#
# ⚠️ 이 값을 와트미터 실측 보정값으로 교체하세요.
#    구하는 법: 한 기기만 켠 상태에서 (실측 W) / (그때 win_feat 의 |P_proxy_mean|).
#    임시 기본값은 실행 로그(dryer 정격 1800W ↔ P_proxy ≈ 194000)에서 역산한
#    근사치이므로, 실측 계수가 있으면 반드시 덮어쓰세요.
CALIB_PROXY_TO_W = 0.00926

# signature 가중치가 전부 0/없을 때(등록 직후 등) 균등 배분 fallback 사용.
_WEIGHT_KEY = "delta_pabs"


def _latest_win_feat(engine):
    return getattr(engine, "_latest_win_feat", None)


def total_power_w(engine):
    """멀티탭 전체 실시간 추정 전력(W). win_feat 없으면 0.0."""
    wf = _latest_win_feat(engine)
    if not wf:
        return 0.0
    try:
        p_proxy = abs(float(wf.get("P_proxy_mean", 0.0)))
    except (TypeError, ValueError):
        return 0.0
    return CALIB_PROXY_TO_W * p_proxy


def per_device_power_w(engine):
    """현재 active 인 각 기기의 추정 실시간 전력(W) dict {device: watts}.

    active 기기가 없으면 빈 dict. 전체 실시간 W 를 기기별 signature 비율로 배분.
    """
    active = dict(getattr(engine, "active_devices", {}) or {})
    if not active:
        return {}

    total_w = total_power_w(engine)
    if total_w <= 0.0:
        return {dev: 0.0 for dev in active}

    sigs = getattr(engine, "device_signatures", {}) or {}
    weights = {}
    for dev in active:
        try:
            weights[dev] = abs(float(sigs.get(dev, {}).get(_WEIGHT_KEY, 0.0)))
        except (TypeError, ValueError):
            weights[dev] = 0.0

    sum_w = sum(weights.values())
    if sum_w <= 1e-9:
        # signature 아직 없음 → 균등 배분 (등록 직후 잠깐)
        n = len(active)
        return {dev: total_w / n for dev in active}

    return {dev: total_w * weights[dev] / sum_w for dev in active}


def socket_power_w(engine, orchestrator):
    """물리 소켓별 추정 실시간 전력(W) dict {socket_idx: watts}.

    ASSIGNED 인 소켓만 그 기기의 추정 W, 그 외(EMPTY/PENDING/DEVICE_OFF)는 0.0.
    """
    result = {}
    try:
        sk_status = orchestrator.get_socket_status()
    except Exception as e:  # noqa: BLE001
        logging.debug(f"[power_meter] get_socket_status 실패: {e}")
        return result

    dev_power = per_device_power_w(engine)
    for sk, info in sk_status.items():
        dev = info.get("device")
        state = info.get("state")
        if dev and state == "ASSIGNED":
            result[sk] = float(dev_power.get(dev, 0.0))
        else:
            result[sk] = 0.0
    return result
