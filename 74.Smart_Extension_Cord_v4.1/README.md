## 1. 과열 방지 — 기기별 안전 자동차단 (신규)

기기가 한도 시간을 넘겨 연속 동작하면(예: 드라이기 켜둔 채 방치) 멀티탭이 스스로
릴레이를 차단한다. NILM이 소켓별 기기를 알기 때문에 **기기마다 다른 한도** 적용.

- 한도 **80% 도달**: 두 UI 모두 소켓 테두리 **빨간 깜빡임** + "Auto-off Ns" 카운트다운
- 한도 **100% 도달**: 릴레이 자동 차단 → DEVICE_OFF (라벨 보존, 대기전력 절약 누적 포함)
- 복귀: 버튼1 또는 UI ON 토글 → PENDING → 재식별 (기존 흐름 그대로)

### 기기별 기본 한도 (시연용, 초) — 0 = 무제한, 상한 30분
| dryer | microwave | cleaner | tv | charger |
|---|---|---|---|---|
| 30 | 60 | 90 | 0 | 0 |

- 한도의 단일 진실 소스: `RaspberryPi/control/safety_limits.json`
  (없으면 기본값 자동 생성 / 원자적 저장 / 파손 시 복구)
- 로그: `[ORCH][SAFETY]` (차단), `[SAFETY-LIMITS]` (파일 로드·저장)

## 2. Settings 팝업 (신규)

- **모니터**: 우상단 [Settings] → **Overheat Protection**(기기별 한도 ▲▼ 편집, 5초 단위,
  Cancel/OK) / **About**(팀 정보). OK 시 json 저장 → **재시작 후에도 유지** + 즉시 반영
- **모바일**: 우상단 [⚙ 설정] → **🔥 과열 방지**(숫자 입력) / About.
  API: GET/POST `/api/limits`
- 메뉴명은 "Limit"이었다가 의미가 안 읽혀 **Overheat Protection 으로 개명**

## 3. 꺼짐 임박 소리 알림 (신규) — 모니터(TV 스피커) + 모바일 동시

대상은 **과열 방지 차단 + OFF 타이머만** (PENDING 만료 / ON 타이머 / 수동 토글 무음).

1. **음성** "OO가 곧 꺼질 예정입니다" — 종료까지 **잔여 20% 시점에 1회**
2. **삐빅 알람** — **꺼지기 5초 전부터 꺼질 때까지** 0.9초 간격 (음성 끝난 뒤부터)

예) 한도 30초 드라이기: 24초 음성 → 25초부터 삐빅 → 30초 차단.

- **모니터(Pi)**: `ui/audio_alerts.py` 가 `ui/sounds/*.wav`(Yuna TTS 음성 6개 + beep)를
  aplay 로 재생. **`ui/sounds/` 폴더 복사 필수!** HDMI 오디오 설정 전제
  (볼륨 아이콘 우클릭 → 장치 프로필 Stereo Output, `aplay ui/sounds/beep.wav` 로 확인)
- **모바일**: 브라우저 내장 한국어 음성(SpeechSynthesis) + WebAudio 삐빅 (파일 불필요)
  - **첫 터치 필수**: 자동재생 정책 때문에 화면을 한 번 탭해야 소리 활성화
    (탭하면 확인음 "삑" + "🔊 소리 알림 활성화" 토스트)
  - **[🔊 소리 테스트] 버튼**: 삐빅+음성+진단 토스트(AudioContext 상태 / 한국어 보이스 수)
    — 무음일 때 원인 판별용. 페이지 푸터의 "sound v2" 로 최신 페이지 로드 확인
  - 서버가 `Cache-Control: no-store` 전송 (옛 페이지 캐시로 새 기능 안 도는 문제 방지)

## 4. 폴더 구조 정리 (이번 버전부터)

RaspberryPi/
  main.py        # 진입점 — hardware/control/ui/NILM 을 sys.path 에 추가
  hardware/      # spi_core, dsp_engine, relay_controller, touch_sensor
  control/       # socket_orchestrator_v2, socket_timer, safety_limits(+json)
  ui/            # socket_dashboard, mobile_ui, timer_dialog, settings_dialog,
                 # stabilizing_overlay, audio_alerts, sounds/, dashboard_ui(legacy)
  NILM/          # ai_engine_v2, feature_extractor, 파이프라인 1~4 (로직 변경 없음)
실행은 기존과 동일: `python RaspberryPi/main.py`

## 5. 버그픽스

1. **팝업 click-through**: 팝업 열림 중 뒤에 숨은 버튼(Timer 등)이 클릭을 가로채던 문제
   → 배경 버튼을 off-screen 으로 이동시켜 차단 (timer/settings 팝업 공통)
2. **안전차단 후 기기 자율 재가동**: 차단 직후 baseline drift 가 가짜 기기 등록을 일으켜
   꺼진 소켓 릴레이가 다시 켜지던 문제 → 차단 전 engine mute + HP OFF 시각 기록
   (가짜 LP 등록 가드를 수동/타이머/안전차단 OFF 전 경로로 확장)
3. **Settings 버튼이 Socket 4 제목 가림** → 버튼 전용 띠 분리 (그리드 top 0.91)
4. **모바일 무음**: 페이지 캐시 / 오디오 unlock / Android 음성 큐 멈춤 3중 원인
   → no-store 헤더 + unlock 확인음 + speak 전 cancel·8초 타임아웃으로 해결

## 6. 테스트 (Mac 개발 환경)

```bash
python RaspberryPi/control/socket_orchestrator_v2.py  # 안전차단 포함 Mock self-test
python RaspberryPi/control/safety_limits.py           # 한도 파일 self-test
python RaspberryPi/ui/audio_alerts.py                 # 소리 알림 규칙 self-test

7. 시연 체크리스트

- [ ] TV 켠 상태로 Pi 부팅 (HDMI 오디오 인식)
- [ ] aplay RaspberryPi/ui/sounds/beep.wav 소리 확인
- [ ] 폰: 페이지 열고 한 번 탭 → 확인음 → [🔊 소리 테스트]로 음성까지 확인
- [ ] 드라이기 시나리오: 24초 음성 → 25초 삐빅 → 30초 자동 차단 (모니터+폰 동시)
- [ ] Settings → Overheat Protection 에서 한도 변경 → 재시작 후 유지 확인