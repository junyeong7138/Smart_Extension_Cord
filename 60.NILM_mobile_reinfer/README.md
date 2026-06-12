# 60. NILM_mobile_reinfer — 수동 재스캔 (human-in-the-loop)

> 모바일 UI에 **[재스캔] 버튼**을 추가한 버전.
> AI가 오인식해도 사용자가 버튼 한 번으로 그 소켓만 다시 측정·재분류해 바로잡을 수 있습니다.

## What's New (vs 51)

- **`rescan_socket(sk)`** (orchestrator 신규): 해당 소켓 하나만 릴레이 토글해
  *물리적으로 격리된* delta를 측정하고 단독 재분류 — 다른 가전 노이즈가 섞인
  정상상태에서도 그 소켓의 부하만 깨끗하게 다시 판별
- **`AUTO_OFF_SCAN_ENABLED`** 시연 모드 스위치: 자동 OFF 전수 스캔을 켜고 끌 수 있음
  (False면 한 번 식별된 라벨 고정, 정정은 수동 재스캔으로)
- `mobile_ui.py` 에 `POST /api/rescan/<i>` 엔드포인트 + 🔄 재스캔 버튼

## Why It Matters

물리 한계 영역(예: 대형 부하 위의 소형 기기)에서 자동 인식이 틀릴 수 있는데,
재스캔은 **사람이 보고 누르는 최종 보정 수단**이라 시연 신뢰성을 크게 올려줍니다.
(이후 75 버전에서는 이 재스캔을 시스템이 스스로 누르는 auto-verify로 발전)

## Run

```bash
python RaspberryPi/main.py
# 폰에서 http://<Pi IP>:5000 접속 → 소켓별 🔄 재스캔
```

## Known Issue & Next

재스캔 시 릴레이 OFF 체류가 길면 TV가 꺼졌다 재부팅되는 문제
→ `61.relay_toggle_time` / `62.relay_toggle_sub_frame` 에서 해결.
