# 40. final_NILM_1turn — 릴레이 토글 식별 1차 완성

> 31의 교훈("추측하지 말고 물리적으로 확인하자")을 구현한 첫 버전.
> **SocketOrchestrator** 가 릴레이를 짧게 토글해 *어느 물리 소켓에 꽂혔는지*를 확정하고,
> 기기가 꺼지면 그 소켓 릴레이를 차단해 **대기전력을 자동으로 끊습니다.**

## Architecture (이후 모든 버전의 골격)

```
SPICore → AIEngine(분류만: ai_engine_v2) ──┐   RelayController(4ch) · TouchSensor
                                           ▼
                              SocketOrchestrator (물리 소켓 매핑의 진실원)
                                           │
                       SocketDashboard(모니터) · mobile_ui(Flask :5000)
```

- **AIEngine** — "무엇이 켜졌나"만 분류 (RandomForest 28 features)
- **SocketOrchestrator** — "어느 소켓인가"를 릴레이 토글로 물리 확정,
  OFF 판정도 ASSIGNED 소켓 전수 토글 스캔으로 결정 (signature 추측 제거)
- 분류 대상 5종 확정: **charger(5W) / tv(60W) / cleaner(600W) / microwave(900W) / dryer(1800W)**

## Key Files

| File | Description |
|---|---|
| `RaspberryPi/main.py` | 진입점 — 터치/orchestrator/UI 통합 |
| `RaspberryPi/socket_orchestrator_v2.py` | 소켓 매핑 + 토글 식별 + OFF 전수 스캔 |
| `RaspberryPi/NILM/ai_engine_v2.py` | 분류 엔진 (ON 감지/분류, OFF 결정은 orchestrator로 위임) |
| `RaspberryPi/relay_controller.py` | 4채널 릴레이 GPIO 제어 |
| `RaspberryPi/mobile_ui.py` | 폰 브라우저 원격 제어 (Flask :5000) |
| `RaspberryPi/socket_dashboard.py` | matplotlib 메인 모니터 UI |

## Test Result

- ✅ charger + tv + dryer: ON/OFF/소켓 위치 모두 정확
- ⚠️ 4기기(+microwave) 동시 ON 상태에서 charger 제거 시 변화 감지 실패
  → 작은 부하가 큰 부하 노이즈에 묻히는 문제, 이후 버전들에서 단계적으로 해결

## Run

```bash
python RaspberryPi/main.py
```
