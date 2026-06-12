# 75. Smart_Extension_Cord_v5 — NILM 인식 신뢰성 강화 (최종)

> **HP(드라이기+청소기) 배경 위에서 LP(TV/충전기)를 인식할 때** 생기던 실측 버그 4건을
> 로그 분석으로 잡고, 오인식을 시스템이 **스스로 검증·정정(auto-verify)** 하는
> 2단계 자동 회복을 넣은 최종 버전입니다.
> 변경 파일: `RaspberryPi/control/socket_orchestrator_v2.py` **단 1개** (나머지는 v4.1과 동일)

## Background

v4.1 실기 테스트(드라이기+청소기 가동 중 TV 연결)에서 발견된 문제들을 실제 로그로
추적해 수정. 모두 "큰 부하 배경 위에서 작은 부하를 측정할 때 신호가 찌그러지는"
물리 한계 영역의 2차 버그이며, **분류기(ai_engine_v2)와 골든 판정 로직은 불변** —
orchestrator의 측정·후처리만 고쳤습니다.

## Fixes (실측 로그 기반)

### v88 — 토글식별이 빈 소켓에 phantom을 할당하던 버그
- 증상: TV를 S1에 꽂았는데 빈 S4에 "charger ON"
- 원인: HP 노이즈로 모든 후보의 ΔI가 음수가 되면 fallback이 ΔH1 증거
  (실제 소켓 +6617 vs 빈 소켓 +48)를 무시하고 "덜 음수"인 빈 소켓을 채택
- 수정: ΔI 증거가 전무할 때만 발동하는 **H1-dominant fallback**

### v89 — 의심 LP 등록 자동 검증 (auto-verify)
- HP 배경에서 신호-RF 모순 fallback으로 등록된 charger/tv(오분류 의심 영역)는
  **12초 후(TV ramp 안정 대기) 그 소켓만 자동 재스캔**해 라벨을 스스로 검증/정정
- 신뢰 경로·재스캔 결과는 예약 제외(루프 방지). 스위치: `AUTO_VERIFY_LP_ENABLED`

### v90 — 살아있는 TV 강제차단 + 재인식 불가 (가장 심각)
- **A**: OFF-스캔 absent 판정 `|ratio|<0.30`이 음수 교란(relay OFF에 H1 상승)을
  "부재"로 오판 → absent 영역을 비대칭(`-0.15 < ratio < +0.30`)으로 좁히고
  음수 교란은 ΔI 보조판정에 위임
- **B**: 수동/타이머/안전차단 OFF 시 baseline을 차단 "직전" 값으로 동기화해
  생기던 데드존(baseline ≫ 실제 → ON 검출 불가) → baseline = **차단 직전 − 기기 sig**

### v91 — phantom 라벨 정리 + 토글식별 동기-펄스화
- **A**: auto-verify가 "부하 없음"을 확인하면 phantom 라벨 **삭제** → EMPTY 복귀
  (수동 재스캔은 기존대로 라벨 보존 — 진짜 재플러그 시나리오 보호)
- **B**: 처음 꽂았을 때의 소켓 위치 식별도 재스캔과 동일한 **동기-펄스 측정**
  (OFF 버스트 ≈33ms ×5, 인접 ON/OFF 차감)으로 통일 — TV 재부팅 위험 제거 +
  HP 배경 상쇄로 정확도 향상. 결정 로직은 불변, 측정만 교체

## Self-healing Flow (이 버전의 완성형)

```
HP 2대 가동 중 TV 연결
→ (오분류가 나더라도) v88이 올바른 소켓에 할당
→ 12초 후 v89가 자동 재스캔 → 라벨 정정 (tv)
→ (빈 소켓 phantom이면) v91이 라벨 삭제 → EMPTY 복귀
사람 개입 없이 스스로 회복. 수동 [재스캔] 버튼은 최후 보정 수단으로 유지.
```

## Test

```bash
python RaspberryPi/control/socket_orchestrator_v2.py
# self-test 케이스 A~H (E~H가 이번 버전 신규 — 실측 로그 수치 그대로 재현)
#   E: 빈 소켓 phantom 방지   F: auto-verify 예약/발화/제외
#   G: OFF-스캔 음수교란 오판 방지 + baseline sig 차감   H: phantom 라벨 정리
```

## Field Checklist

- [ ] 드라이기+청소기 가동 중 TV 연결 → TV ON 유지 (강제차단 없어야 함)
- [ ] 기기 수동 OFF 직후 다시 켜기 → 즉시 재인식 (데드존 없어야 함)
- [ ] phantom 발생 시 ~42초 내 빈 소켓 자동 복귀
- [ ] 로그: `[ORCH][AUTO-VERIFY]`, `H1-dominant fallback`, `phantom ... cleared`,
      `baseline sync (sig 차감, ...)`
