# 71. Smart_Extension_Cord_v2 — 반응속도 개선 (cooldown 단축)

> 70과 기능은 같고, 토글/스캔 후 판별이 보류되는 **mute/cooldown 시간을 단축**해
> 체감 반응속도를 올린 버전입니다.

## What's New (vs 70)

- **`ENGINE_MUTE_FRAMES = 30 → 18`** (≈2.3초 → ≈1.4초)
  - 토글식별/OFF스캔이 끝난 뒤 남던 "Stabilizing…" 꼬리를 단축
  - 릴레이 settle(50 ms) + 신호 재안정화 구간 대비 **3~4배 마진은 유지** —
    토글을 가짜 이벤트로 오인하지 않게 정확도는 보존하면서 UX만 개선
- 관련 cooldown 상수들 함께 정리 (이벤트 디바운스/검증 취소 등)

## Why It Matters

시연에서 버튼을 누르고 기기를 꽂는 흐름이 빨라야 하는데, 매 동작마다 2초 이상
멈춰 보이면 답답함 → 정확도 마진을 계산해서 깎을 수 있는 만큼만 깎은 튜닝입니다.

## Run

```bash
python RaspberryPi/main.py
```

## Next

→ `72.Smart_Extension_Cord_v3` — 토글 잔류 릴레이 정리 (시연 골든 버전).
