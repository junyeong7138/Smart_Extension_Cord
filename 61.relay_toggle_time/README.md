# 61. relay_toggle_time — 릴레이 OFF 체류를 시간 기반으로

> 60의 재스캔은 릴레이 OFF 체류를 **프레임 개수**로 지정했는데,
> 이를 **초 단위 시간**으로 바꿔 미세 튜닝이 가능해진 버전입니다.
> (TV처럼 전원이 잠깐만 끊겨도 재부팅되는 기기 대응의 1단계)

## What's New (vs 60)

`socket_orchestrator_v2.py` 의 재스캔 체류 파라미터가 시간 기반으로 변경:

```python
RESCAN_FRAME_S     = 0.078   # 1 frame(150샘플) 소요 시간 근사
RESCAN_ON_DWELL_S  = 0.94    # ON 측정 체류 (relay ON — 재부팅 무관, 길게)
RESCAN_OFF_DWELL_S = 0.078   # OFF 측정 체류 ← TV 재부팅 방지 핵심 노브
RESCAN_EXCLUDE_S   = 0.16    # relay 전이 직후 과도구간 제외
```

기능 자체는 60과 동일하고, OFF 체류시간을 숫자 하나로 조절할 수 있게 된 것이 차이입니다.

## Limitation & Next

`RESCAN_OFF_DWELL_S` 를 아무리 줄여도 **1 프레임(150샘플 ≈ 78 ms)이 하한** —
측정 단위가 프레임이라 그 밑으로 못 쪼개기 때문.
TV PSU hold-up(전원 유지 시간)은 그보다 짧아서 여전히 재부팅 위험이 남음.
→ `62.relay_toggle_sub_frame` 에서 **서브프레임 측정**으로 하한 자체를 깸.
