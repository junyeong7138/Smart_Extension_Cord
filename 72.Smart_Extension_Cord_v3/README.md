# 72. Smart_Extension_Cord_v3 — 토글 잔류 릴레이 정리 (시연 골든 버전)

> **2026-06-02 시연 발표 확정 "골든(정상 동작) 기준" 버전.**
> 토글식별이 끝난 뒤 켜진 채 남는 비승자 소켓 릴레이를 정리해
> "화면엔 OFF인데 릴레이는 ON"인 모순을 해소했습니다.

## What's New (vs 71)

- **`_restore_nonwinner_relays()`** 신규 (orchestrator):
  - 토글식별은 후보 소켓을 OFF→ON 시키므로 측정이 끝나면 **모든 후보 릴레이가 ON**으로 남음
  - PENDING 후보는 ON 유지가 맞지만, EMPTY/DEVICE_OFF 상태의 비승자 후보는
    릴레이를 다시 OFF로 되돌려 **UI 상태와 하드웨어 상태를 일치**시킴

## Snapshot (이 버전이 갖춘 것)

5기기 NILM 분류 · 토글식별/OFF 전수 스캔 · 동기-펄스 재스캔(TV 재부팅 방지) ·
LP 부호 override · 푸시버튼 2개 · 예약 타이머 · PENDING 30s 만료 ·
실시간 전력/절약 누적 표시 · Stabilizing 팝업 · 모바일/모니터 UI 통일

## Run

```bash
python RaspberryPi/main.py
python RaspberryPi/socket_orchestrator_v2.py   # Mock self-test
```

## Next

→ `73.Smart_Extension_Cord_v4` — 과열 방지(기기별 안전 자동차단) + Settings + 폴더 구조 정리.
