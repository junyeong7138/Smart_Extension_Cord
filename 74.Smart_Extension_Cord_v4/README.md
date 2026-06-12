# 74. Smart_Extension_Cord_v4 — 과열 방지 + 소리 알림 통합

> v4(과열 방지) 위에 **꺼짐 임박 소리 알림**(음성 + 삐빅)과 버그픽스 4건을 통합한 버전.
> 변경 파일: `control/`, `ui/` 일부 + `ui/sounds/`(신규).

## 1. Overheat Protection (v4 기능)

기기별 연속 동작 한도 초과 시 자동 차단. 80%부터 빨간 깜빡임 + 카운트다운.

| dryer | microwave | cleaner | tv | charger |
|---|---|---|---|---|
| 30s | 60s | 90s | 무제한 | 무제한 |

- 한도 파일: `RaspberryPi/control/safety_limits.json` (0 = 무제한, 재시작 후 유지)
- Settings 메뉴명 개선: "Limit" → **"Overheat Protection"** (모바일 "🔥 과열 방지")

## 2. Sound Alerts (신규) — 모니터(TV 스피커) + 모바일 동시

대상은 **과열 방지 차단 + OFF 타이머만** (PENDING 만료/ON 타이머/수동 토글은 무음).

1. **음성** "OO가 곧 꺼질 예정입니다" — 종료까지 **잔여 20% 시점에 1회**
2. **삐빅 알람** — **꺼지기 5초 전부터 꺼질 때까지** 0.9초 간격 (음성 끝난 뒤부터)

예) 한도 30초 드라이기: 24초 음성 → 25초부터 삐빅 → 30초 차단.

- **모니터(Pi)**: `ui/audio_alerts.py` 가 `ui/sounds/*.wav`(Yuna TTS 음성 6개 + beep)를
  aplay로 재생 — **`ui/sounds/` 폴더 복사 필수!**
  HDMI 오디오 설정 전제 (장치 프로필 Stereo Output, `aplay ui/sounds/beep.wav`로 확인)
- **모바일**: 브라우저 내장 한국어 음성(SpeechSynthesis) + WebAudio 삐빅 (파일 불필요)
  - **첫 터치 필수**: 자동재생 정책 때문에 화면을 한 번 탭해야 활성화 (확인음 + 토스트)
  - **[🔊 소리 테스트] 버튼**: 무음 시 원인 판별용 진단 (AudioContext 상태/보이스 수)
  - 서버가 `Cache-Control: no-store` 전송 (옛 페이지 캐시 방지, 푸터 "sound v2" 표식)

## 3. Bugfixes

1. **팝업 click-through**: 팝업 열림 중 뒤에 숨은 버튼이 클릭을 가로채던 문제
   → 배경 버튼 off-screen 이동 (timer/settings 팝업 공통)
2. **안전차단 후 기기 자율 재가동**: baseline drift발 가짜 등록이 꺼진 소켓 릴레이를
   다시 켜던 문제 → 차단 전 engine mute + HP OFF 시각 기록
3. **Settings 버튼이 Socket 4 제목 가림** → 버튼 전용 띠 분리
4. **모바일 무음**: 페이지 캐시 / 오디오 unlock / Android 음성 큐 멈춤 3중 원인 해결

## Structure & Test

```
RaspberryPi/  main.py · hardware/ · control/ · ui/(+sounds/) · NILM/
```

```bash
python RaspberryPi/main.py
python RaspberryPi/control/socket_orchestrator_v2.py  # Mock self-test (케이스 A~D)
python RaspberryPi/control/safety_limits.py
python RaspberryPi/ui/audio_alerts.py                 # 소리 알림 규칙 self-test
```

## Demo Checklist

- [ ] TV 켠 상태로 Pi 부팅 (HDMI 오디오 인식) → `aplay ui/sounds/beep.wav` 확인
- [ ] 폰: 페이지 열고 한 번 탭 → 확인음 → [🔊 소리 테스트]
- [ ] 드라이기: 24초 음성 → 25초 삐빅 → 30초 자동 차단 (모니터+폰 동시)
- [ ] Settings → Overheat Protection 한도 변경 → 재시작 후 유지 확인

## Next

→ `75.Smart_Extension_Cord_v5` — HP 배경 위 LP 인식 신뢰성 강화 (auto-verify 등).
