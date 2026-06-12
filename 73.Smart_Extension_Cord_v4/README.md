# Smart Extension Cord v4 — 과열 방지 (기기별 안전 자동차단)

## 개요
기기가 너무 오래 연속 동작하면(예: 드라이기 켜둔 채 방치) 멀티탭이 스스로
릴레이를 차단하는 **과열 방지 기능**. NILM이 소켓별 기기를 알기 때문에
**기기마다 다른 한도**를 적용할 수 있다 — 고전력·발열 기기일수록 짧게.

- 한도 80% 도달: 두 UI 모두 소켓 테두리 **빨간색 깜빡임** + "Auto-off Ns" 카운트다운
- 한도 100% 도달: 릴레이 자동 차단 → DEVICE_OFF (라벨 보존, 대기전력 절약 누적에 포함)
- 복귀: 버튼1 또는 UI ON 토글 → PENDING → 재식별 (기존 흐름 그대로)

## 기기별 기본 한도 (시연용, 초)
| dryer | microwave | cleaner | tv | charger |
|---|---|---|---|---|
| 30 | 60 | 90 | 0(무제한) | 0(무제한) |

- 실제 제품 기준은 10분/20분/40분 (발표 멘트용)
- **0 = 무제한**, 설정 상한 30분(1800s)

## Settings 팝업 (신규)
- **모니터 UI**: 우상단 [Settings] 버튼 → Limit(기기별 ▲▼ 편집, 5초 단위) / About(팀 정보)
- **모바일 UI**: 우상단 [⚙ 설정] → Limit(숫자 입력) / About. API: GET/POST `/api/limits`
- OK 시 `RaspberryPi/control/safety_limits.json` 에 저장 → **재시작 후에도 유지**, 즉시 반영
- 파일이 없거나 깨지면 기본값 자동 생성 (원자적 저장)

## 폴더 구조 정리 (이번 버전부터)
RaspberryPi/
  main.py        # 진입점 (하위 폴더들을 sys.path 에 추가)
  hardware/      # spi_core, dsp_engine, relay_controller, touch_sensor
  control/       # socket_orchestrator_v2, socket_timer, safety_limits(+json)
  ui/            # socket_dashboard, mobile_ui, timer_dialog, settings_dialog, stabilizing_overlay
  NILM/          # ai_engine_v2, feature_extractor, 데이터 파이프라인 (변경 없음)

## 버그픽스 3건
1. **팝업 click-through**: 팝업이 떠 있을 때 뒤에 숨은 버튼(Timer 등)이 클릭을
   가로채던 문제 → 배경 버튼을 off-screen 으로 이동시켜 차단 (timer/settings 공통)
2. **안전차단 후 기기 자율 재가동**: 차단 직후 baseline drift 가 가짜 LP 등록을
   일으켜 toggle-id 가 꺼진 소켓 릴레이를 다시 켜던 문제 → 차단 전 engine mute +
   HP OFF 시각 기록(가짜 LP 등록 가드 활성화)
3. **Settings 버튼이 Socket 4 제목 가림** → 버튼 전용 띠 분리 (그리드 top 0.91)

## 실행 / 테스트
```bash
python RaspberryPi/main.py                            # Pi (기존과 동일)
python RaspberryPi/control/socket_orchestrator_v2.py  # Mock self-test (안전차단 케이스 D 포함)
python RaspberryPi/control/safety_limits.py           # 한도 파일 로드/저장/복구 self-test

주의

- 이전 버전에서 한도를 바꿨었다면 control/safety_limits.json 을 이 버전으로 복사할 것
(없으면 기본값으로 재생성됨)
- 로그 라벨: [ORCH][SAFETY](한도 초과 차단), [SAFETY-LIMITS](파일 로드/저장)