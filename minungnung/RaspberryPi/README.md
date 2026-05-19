# WattsUp 실행 로그

- 시작 시간: 2026-05-20 00:20:55
- 저장 위치: `/home/wattsup/Project/minungnung/RaspberryPi/README.md`

```text
[AI VERSION] ai_extension_2026_05_20_v38_cooker_off_fast_high_as_dryer
[AI INIT] state_model = /home/wattsup/Project/minungnung/Model/rf_state_classifier.joblib
[AI INIT] device_model = /home/wattsup/Project/minungnung/Model/rf_device_classifier.joblib
[AI INIT] state_classes = ['empty', 'on', 'plugged_off']
[AI INIT] device_classes = ['charger', 'cooker', 'dryer', 'fan']
[AI INIT] state_feature_count = 92
[AI INIT] device_feature_count = 92
[AI INIT] window_size = 10
🚀 WattsUp DSP Monitor + AI를 시작합니다...
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.51, Pabs=1987.2, H1=3.2, THD=21.749 | state_probs[plugged_off=0.86, empty=0.12, on=0.02]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.80, Pabs=2221.1, H1=68.5, THD=1.156 | state_probs[plugged_off=0.84, empty=0.14, on=0.02]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.50 | DEVICE=None | I=435.52, Pabs=121591.5, H1=18664.1, THD=0.619 | state_probs[plugged_off=0.50, on=0.43, empty=0.07]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.50 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.51 | DEVICE=None | I=453.98, Pabs=125345.8, H1=18755.6, THD=0.622 | state_probs[plugged_off=0.51, on=0.44, empty=0.06]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.51 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.49 | DEVICE=None | I=432.85, Pabs=106687.4, H1=19121.2, THD=0.535 | state_probs[plugged_off=0.49, on=0.44, empty=0.06]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.49 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=on sconf=0.56 | DEVICE=None | I=550.39, Pabs=297919.7, H1=25648.0, THD=0.423 | state_probs[on=0.56, plugged_off=0.37, empty=0.06]
[AI ADAPTER] state=plugged_off raw=on sconf=0.56 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.58 | DEVICE=cooker dconf=0.45 | I=550.74, Pabs=294051.3, H1=25563.7, THD=0.393 | state_probs[on=0.58, plugged_off=0.36, empty=0.06] | device_probs[cooker=0.45, charger=0.22, fan=0.19, dryer=0.14]
[AI ADAPTER] state=on raw=on sconf=0.58 abs_device=cooker dconf=0.45 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.59 | DEVICE=cooker dconf=0.45 | I=559.60, Pabs=315485.3, H1=25294.7, THD=0.420 | state_probs[on=0.59, plugged_off=0.35, empty=0.06] | device_probs[cooker=0.45, charger=0.21, fan=0.19, dryer=0.14]
[AI ADAPTER] state=on raw=on sconf=0.59 abs_device=cooker dconf=0.45 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.59 | DEVICE=cooker dconf=0.44 | I=559.16, Pabs=313060.8, H1=25097.0, THD=0.432 | state_probs[on=0.59, plugged_off=0.35, empty=0.06] | device_probs[cooker=0.44, charger=0.21, fan=0.19, dryer=0.15]
[DELTA EVENT] ON DRYER deferred: waiting stable ON state=on, on_prob=0.59 | dPabs=198240.3, dI=242.82, dH1=11608.4
[AI ADAPTER] state=on raw=on sconf=0.59 abs_device=cooker dconf=0.44 event=ON active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.59 | DEVICE=cooker dconf=0.43 | I=548.77, Pabs=291997.1, H1=25516.8, THD=0.414 | state_probs[on=0.59, plugged_off=0.34, empty=0.07] | device_probs[cooker=0.43, charger=0.21, fan=0.19, dryer=0.16]
[AI ADAPTER] state=on raw=on sconf=0.59 abs_device=cooker dconf=0.43 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.64 | DEVICE=cooker dconf=0.49 | I=551.01, Pabs=293217.5, H1=25360.9, THD=0.420 | state_probs[on=0.64, plugged_off=0.32, empty=0.04] | device_probs[cooker=0.49, fan=0.21, dryer=0.15, charger=0.14]
[AI ADAPTER] state=on raw=on sconf=0.64 abs_device=cooker dconf=0.49 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.95 | DEVICE=cooker dconf=0.64 | I=552.70, Pabs=307388.7, H1=25042.7, THD=0.426 | state_probs[on=0.95, plugged_off=0.05, empty=0.00] | device_probs[dryer=0.64, cooker=0.31, charger=0.05, fan=0.00]
[DELTA EVENT] ON COOKER slot=1 conf=0.64 source=absolute_sync_heating
[AI ADAPTER] state=on raw=on sconf=0.95 abs_device=cooker dconf=0.64 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.95 | DEVICE=dryer dconf=0.64 | I=548.14, Pabs=299182.6, H1=24189.6, THD=0.444 | state_probs[on=0.95, plugged_off=0.05, empty=0.00] | device_probs[dryer=0.64, cooker=0.31, charger=0.05, fan=0.00]
[ABS DEVICE GUARD] DRYER sync blocked: cooker heating context | abs_conf=0.64, dryer_prob=0.64, cooker_prob=0.31, I=548.14, Pabs=299182.6, H1=24189.6
[AI ADAPTER] state=on raw=on sconf=0.95 abs_device=dryer dconf=0.64 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.94 | DEVICE=dryer dconf=0.65 | I=552.33, Pabs=298935.4, H1=25907.7, THD=0.408 | state_probs[on=0.94, plugged_off=0.05, empty=0.00] | device_probs[dryer=0.65, cooker=0.30, charger=0.05, fan=0.00]
[ABS DEVICE GUARD] DRYER sync blocked: cooker heating context | abs_conf=0.65, dryer_prob=0.65, cooker_prob=0.30, I=552.33, Pabs=298935.4, H1=25907.7
[AI ADAPTER] state=on raw=on sconf=0.94 abs_device=dryer dconf=0.65 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.82 | I=558.91, Pabs=311839.4, H1=25313.7, THD=0.422 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.82, cooker=0.13, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.82 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=546.40, Pabs=296789.1, H1=24734.0, THD=0.298 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[DELTA EVENT] ON DRYER slot=2 conf=0.87 source=fast_absolute_sync
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.86 | I=552.82, Pabs=298581.3, H1=25527.8, THD=0.408 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.86, cooker=0.13, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.86 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=548.90, Pabs=298327.4, H1=25338.6, THD=0.430 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.86 | I=559.89, Pabs=312456.2, H1=25351.9, THD=0.427 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.86, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.86 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.86 | I=546.01, Pabs=300514.6, H1=25230.6, THD=0.419 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.86, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.86 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.86 | I=541.35, Pabs=293675.2, H1=25186.8, THD=0.413 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.86, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.86 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=538.75, Pabs=292994.4, H1=25345.4, THD=0.269 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[DELTA EVENT] OFF DRYER canceled: dryer mode change/still alive | dPabs=-7093.4, dI=-11.17, dH1=-108.0
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=OFF active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=555.20, Pabs=311829.4, H1=25384.2, THD=0.414 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=544.40, Pabs=292840.3, H1=25027.6, THD=0.429 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=556.26, Pabs=311813.7, H1=25146.2, THD=0.416 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=547.64, Pabs=302783.8, H1=25422.2, THD=0.415 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=544.20, Pabs=288749.9, H1=25339.8, THD=0.418 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=539.62, Pabs=290578.7, H1=25093.0, THD=0.420 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.86 | I=555.81, Pabs=308404.8, H1=25165.4, THD=0.417 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.86, cooker=0.13, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.86 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=562.93, Pabs=314194.6, H1=25022.7, THD=0.427 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=547.89, Pabs=295318.5, H1=25230.6, THD=0.422 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=558.88, Pabs=316584.8, H1=25198.8, THD=0.422 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[DELTA EVENT] ON FAN slot=3 conf=0.87 source=high_dryer_axis | dPabs=9504.1, dI=8.58, dH1=-48.3 | device_probs[fan=0.87, charger=0.11, cooker=0.02, dryer=0.00]
[DELTA EVENT] ON FAN slot confirmed by high-dryer axis | conf=0.87, dPabs=9504.1, dI=8.58, dH1=-48.3
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=ON active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.83 | I=546.03, Pabs=307133.1, H1=24934.6, THD=0.427 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.83 | I=541.62, Pabs=299208.8, H1=25139.4, THD=0.417 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=543.67, Pabs=292964.2, H1=24263.2, THD=0.426 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=557.52, Pabs=309670.6, H1=25045.1, THD=0.431 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=539.02, Pabs=292743.9, H1=24965.0, THD=0.419 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=545.03, Pabs=292281.1, H1=25177.1, THD=0.411 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=541.70, Pabs=293421.8, H1=25186.1, THD=0.423 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=534.07, Pabs=286466.1, H1=25188.1, THD=0.392 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[DELTA EVENT] OFF FAN canceled: fast_high dryer fluctuation protected | dPabs=-12327.9, dI=-7.52, dH1=259.4
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=OFF active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=537.96, Pabs=289936.4, H1=24977.3, THD=0.426 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=559.70, Pabs=310545.6, H1=25294.1, THD=0.413 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=547.55, Pabs=295390.0, H1=24666.3, THD=0.419 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=537.73, Pabs=293474.6, H1=25158.4, THD=0.392 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=534.74, Pabs=286333.5, H1=24973.5, THD=0.413 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=536.78, Pabs=298468.1, H1=24861.5, THD=0.426 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=541.81, Pabs=291818.6, H1=25024.8, THD=0.419 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=553.23, Pabs=309934.2, H1=25090.6, THD=0.410 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=544.42, Pabs=303500.3, H1=24863.5, THD=0.385 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=552.00, Pabs=311703.5, H1=24946.5, THD=0.411 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.85 | I=546.30, Pabs=291486.2, H1=24940.3, THD=0.427 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.85, cooker=0.11, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.85 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=536.28, Pabs=285077.9, H1=25002.8, THD=0.416 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.84 | I=542.16, Pabs=303710.0, H1=24751.3, THD=0.415 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.84 | I=537.46, Pabs=294802.0, H1=24923.2, THD=0.414 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.84 | I=544.33, Pabs=289882.8, H1=25047.8, THD=0.416 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=555.71, Pabs=313775.2, H1=25111.0, THD=0.413 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=539.91, Pabs=291836.5, H1=24809.6, THD=0.413 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=546.09, Pabs=307042.4, H1=24715.6, THD=0.410 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=537.27, Pabs=296082.1, H1=24809.0, THD=0.423 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=548.59, Pabs=307920.2, H1=24856.4, THD=0.413 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.83 | I=533.12, Pabs=292630.4, H1=24702.4, THD=0.407 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.83 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.84 | I=530.35, Pabs=294942.6, H1=24449.1, THD=0.417 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.84, cooker=0.11, charger=0.05, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.84 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.64 | DEVICE=dryer dconf=0.50 | I=4.67, Pabs=2063.1, H1=51.6, THD=0.837 | state_probs[on=0.64, plugged_off=0.32, empty=0.04] | device_probs[cooker=0.50, fan=0.22, dryer=0.15, charger=0.14]
[DELTA EVENT] OFF DRYER slot=2 conf=0.90 | dPabs=-104544.5, dI=-189.27, dH1=-8490.6 | device_probs[dryer=0.86, cooker=0.14, charger=0.00, fan=0.00]
[DELTA STALE] moved active COOKER, FAN to OFF: latest is idle
[AI ADAPTER] state=on raw=on sconf=0.64 abs_device=dryer dconf=0.50 event=OFF active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.63 | DEVICE=cooker dconf=0.49 | I=4.32, Pabs=1831.6, H1=42.0, THD=1.078 | state_probs[on=0.63, plugged_off=0.33, empty=0.04] | device_probs[cooker=0.49, fan=0.21, dryer=0.15, charger=0.15]
[AI ADAPTER] state=on raw=on sconf=0.63 abs_device=cooker dconf=0.49 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.49 | I=4.53, Pabs=2011.4, H1=23.7, THD=2.294 | state_probs[on=0.61, plugged_off=0.34, empty=0.05] | device_probs[cooker=0.49, fan=0.21, charger=0.15, dryer=0.15]
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.49 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.50 | I=5.06, Pabs=2378.1, H1=93.4, THD=0.512 | state_probs[on=0.61, plugged_off=0.34, empty=0.05] | device_probs[cooker=0.50, fan=0.21, charger=0.15, dryer=0.13]
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.50 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.51 | I=4.94, Pabs=2342.2, H1=59.1, THD=0.534 | state_probs[on=0.61, plugged_off=0.35, empty=0.04] | device_probs[cooker=0.51, fan=0.21, charger=0.15, dryer=0.13]
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.51 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.48 | I=5.26, Pabs=2314.6, H1=31.5, THD=1.846 | state_probs[on=0.61, plugged_off=0.35, empty=0.04] | device_probs[cooker=0.48, fan=0.21, charger=0.17, dryer=0.14]
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.48 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.59 | DEVICE=cooker dconf=0.49 | I=4.63, Pabs=2021.8, H1=19.1, THD=3.163 | state_probs[on=0.59, plugged_off=0.36, empty=0.05] | device_probs[cooker=0.49, fan=0.21, charger=0.19, dryer=0.12]
[AI ADAPTER] state=on raw=on sconf=0.59 abs_device=cooker dconf=0.49 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.58 | DEVICE=cooker dconf=0.48 | I=5.06, Pabs=2293.3, H1=36.7, THD=1.567 | state_probs[on=0.58, plugged_off=0.37, empty=0.05] | device_probs[cooker=0.48, fan=0.21, charger=0.19, dryer=0.11]
[AI ADAPTER] state=on raw=on sconf=0.58 abs_device=cooker dconf=0.48 event=OFF active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.57 | DEVICE=unknown_on dconf=0.38 | I=4.44, Pabs=2046.5, H1=52.9, THD=0.820 | state_probs[on=0.57, plugged_off=0.38, empty=0.05] | device_probs[cooker=0.38, charger=0.27, fan=0.26, dryer=0.09]
[AI ADAPTER] state=on raw=on sconf=0.57 abs_device=None dconf=0.38 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=plugged_off sconf=0.88 | DEVICE=cooker dconf=0.71 | I=4.76, Pabs=2335.6, H1=60.3, THD=1.398 | state_probs[plugged_off=0.88, empty=0.11, on=0.00] | device_probs[fan=0.71, charger=0.27, dryer=0.01, cooker=0.01]
[AI ADAPTER] state=on raw=plugged_off sconf=0.88 abs_device=cooker dconf=0.71 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.53, Pabs=1931.1, H1=63.1, THD=0.788 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=5.12, Pabs=2400.7, H1=61.2, THD=1.096 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.90, Pabs=2063.8, H1=11.3, THD=8.741 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.41, Pabs=2099.2, H1=24.6, THD=2.326 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.87, Pabs=2293.6, H1=42.1, THD=1.660 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.45, Pabs=2011.4, H1=24.5, THD=2.069 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.23, Pabs=1896.0, H1=40.9, THD=1.333 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.91, Pabs=2137.4, H1=72.1, THD=0.648 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.84, Pabs=2128.6, H1=17.5, THD=3.368 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=6.59, Pabs=2869.1, H1=60.0, THD=1.122 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.36, Pabs=2043.3, H1=35.4, THD=0.808 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.51, Pabs=2008.3, H1=43.2, THD=1.542 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=5.08, Pabs=2414.2, H1=80.6, THD=0.550 | state_probs[plugged_off=0.87, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.74, Pabs=2198.5, H1=53.6, THD=0.763 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.51, Pabs=2081.7, H1=43.1, THD=1.528 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.52, Pabs=2038.5, H1=27.4, THD=2.649 | state_probs[plugged_off=0.86, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.49, Pabs=1954.5, H1=34.1, THD=1.647 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.86, Pabs=2225.6, H1=72.3, THD=0.513 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.78, Pabs=2095.9, H1=34.2, THD=1.928 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.66, Pabs=2194.6, H1=6.9, THD=8.300 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=5.09, Pabs=2354.0, H1=36.8, THD=1.867 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=3.79, Pabs=1727.0, H1=15.4, THD=3.743 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.57, Pabs=2199.0, H1=43.0, THD=1.094 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.65, Pabs=1929.1, H1=12.3, THD=5.587 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.07, Pabs=2304.4, H1=58.9, THD=0.980 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.59, Pabs=1952.2, H1=8.9, THD=9.804 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.23, Pabs=1992.7, H1=24.6, THD=2.735 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.93, Pabs=2298.1, H1=21.1, THD=2.235 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.22, Pabs=1961.7, H1=8.6, THD=7.901 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.91, Pabs=2235.6, H1=57.1, THD=1.711 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=5.07, Pabs=2374.4, H1=36.3, THD=1.300 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.43, Pabs=2084.3, H1=44.1, THD=1.299 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=5.06, Pabs=2271.2, H1=103.6, THD=0.400 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.58, Pabs=2063.2, H1=35.5, THD=1.127 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=5.24, Pabs=2443.6, H1=28.9, THD=2.247 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.80, Pabs=2351.1, H1=68.6, THD=0.935 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.89, Pabs=2232.1, H1=48.3, THD=0.793 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.63, Pabs=2088.1, H1=23.2, THD=1.522 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.77, Pabs=2292.8, H1=13.3, THD=2.603 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.75, Pabs=2053.6, H1=49.7, THD=0.796 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.68, Pabs=2124.4, H1=83.9, THD=0.941 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.94, Pabs=2400.9, H1=42.6, THD=2.140 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=5.21, Pabs=2462.7, H1=15.8, THD=3.716 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.91, Pabs=2334.5, H1=40.2, THD=0.825 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.72, Pabs=2086.7, H1=37.6, THD=1.693 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.65, Pabs=2118.5, H1=44.5, THD=1.907 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.56, Pabs=2146.8, H1=70.7, THD=0.799 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.67, Pabs=2099.0, H1=16.1, THD=1.790 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.49, Pabs=2111.4, H1=36.9, THD=2.159 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.90 | DEVICE=None | I=5.38, Pabs=2634.3, H1=106.8, THD=0.536 | state_probs[plugged_off=0.90, empty=0.09, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.90 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.90 | DEVICE=None | I=4.53, Pabs=2106.9, H1=68.5, THD=0.675 | state_probs[plugged_off=0.90, empty=0.10, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.90 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.90 | DEVICE=None | I=4.95, Pabs=2218.5, H1=35.8, THD=1.498 | state_probs[plugged_off=0.90, empty=0.10, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.90 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.38, Pabs=1831.4, H1=29.9, THD=1.683 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=5.07, Pabs=2356.9, H1=51.0, THD=1.617 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.81, Pabs=2161.9, H1=62.5, THD=0.853 | state_probs[plugged_off=0.88, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.76, Pabs=2073.5, H1=18.3, THD=3.926 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.77, Pabs=2423.5, H1=68.0, THD=0.794 | state_probs[plugged_off=0.88, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.74, Pabs=2199.4, H1=46.6, THD=1.619 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.83, Pabs=2112.0, H1=14.4, THD=3.154 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.23, Pabs=2392.9, H1=35.9, THD=1.704 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.67, Pabs=2082.5, H1=36.5, THD=1.889 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.99, Pabs=2417.7, H1=42.7, THD=1.961 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.90, Pabs=2390.9, H1=40.7, THD=2.225 | state_probs[plugged_off=0.86, empty=0.13, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.43, Pabs=2368.6, H1=78.1, THD=0.846 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.72, Pabs=2155.0, H1=62.3, THD=1.440 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=5.47, Pabs=2652.7, H1=69.0, THD=1.065 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.80, Pabs=2291.5, H1=82.9, THD=0.468 | state_probs[plugged_off=0.86, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.92, Pabs=2328.0, H1=62.5, THD=0.855 | state_probs[plugged_off=0.86, empty=0.13, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.59, Pabs=2157.3, H1=18.9, THD=3.313 | state_probs[plugged_off=0.84, empty=0.16, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.64, Pabs=2101.0, H1=44.4, THD=1.316 | state_probs[plugged_off=0.84, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.97, Pabs=2379.9, H1=80.5, THD=0.994 | state_probs[plugged_off=0.84, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.72, Pabs=2375.5, H1=45.9, THD=1.215 | state_probs[plugged_off=0.85, empty=0.14, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.71, Pabs=2146.5, H1=37.4, THD=2.367 | state_probs[plugged_off=0.86, empty=0.13, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.84, Pabs=2163.6, H1=45.6, THD=1.641 | state_probs[plugged_off=0.87, empty=0.13, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.34, Pabs=2045.1, H1=82.2, THD=0.492 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.13, Pabs=2502.6, H1=30.0, THD=1.309 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.45, Pabs=2053.7, H1=51.6, THD=1.356 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.50, Pabs=2038.2, H1=34.9, THD=1.245 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.69, Pabs=2105.3, H1=60.4, THD=0.566 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=5.21, Pabs=2580.3, H1=33.8, THD=1.826 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.37, Pabs=2081.2, H1=75.9, THD=0.871 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.69, Pabs=2088.6, H1=33.7, THD=2.146 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.88, Pabs=2216.1, H1=52.9, THD=0.866 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.50, Pabs=2130.3, H1=48.7, THD=1.063 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.90, Pabs=2398.9, H1=67.2, THD=0.786 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.08, Pabs=2260.7, H1=53.2, THD=1.036 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=5.29, Pabs=2344.5, H1=64.7, THD=1.749 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.89, Pabs=2391.2, H1=28.0, THD=2.369 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.75, Pabs=2102.4, H1=31.2, THD=1.570 | state_probs[plugged_off=0.86, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=5.13, Pabs=2249.5, H1=67.9, THD=0.890 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.63, Pabs=2059.3, H1=32.4, THD=1.930 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.30, Pabs=1990.9, H1=29.9, THD=2.370 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.99, Pabs=2372.9, H1=25.9, THD=3.378 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=5.13, Pabs=2464.1, H1=94.8, THD=0.474 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=5.12, Pabs=2457.7, H1=34.4, THD=1.971 | state_probs[plugged_off=0.88, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.58, Pabs=1968.4, H1=19.4, THD=3.594 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.82, Pabs=2254.6, H1=75.6, THD=0.737 | state_probs[plugged_off=0.87, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.81, Pabs=2249.3, H1=52.5, THD=0.675 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.85, Pabs=2251.9, H1=99.4, THD=0.956 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.54, Pabs=2085.0, H1=19.5, THD=2.968 | state_probs[plugged_off=0.87, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.87, Pabs=2316.7, H1=50.5, THD=1.476 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.53, Pabs=2026.1, H1=43.3, THD=0.889 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.95, Pabs=2224.0, H1=33.1, THD=2.087 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.94, Pabs=2268.8, H1=43.4, THD=1.341 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.90 | DEVICE=None | I=5.15, Pabs=2465.7, H1=18.4, THD=4.016 | state_probs[plugged_off=0.90, empty=0.10, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.90 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.06, Pabs=1827.8, H1=28.6, THD=2.218 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=5.07, Pabs=2379.3, H1=63.5, THD=0.456 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.90 | DEVICE=None | I=5.00, Pabs=2164.8, H1=27.3, THD=2.966 | state_probs[plugged_off=0.90, empty=0.10, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.90 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.87, Pabs=2271.1, H1=37.7, THD=1.306 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.84, Pabs=2289.4, H1=27.1, THD=2.874 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.87, Pabs=2325.2, H1=43.7, THD=1.467 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=5.01, Pabs=2348.4, H1=70.1, THD=0.960 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=5.24, Pabs=2516.0, H1=47.5, THD=1.259 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.69, Pabs=2143.1, H1=43.7, THD=2.198 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.49, Pabs=2173.4, H1=41.5, THD=1.004 | state_probs[plugged_off=0.89, empty=0.10, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.90 | DEVICE=None | I=4.73, Pabs=2277.8, H1=35.6, THD=2.108 | state_probs[plugged_off=0.90, empty=0.10, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.90 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.68, Pabs=2345.8, H1=65.7, THD=0.954 | state_probs[plugged_off=0.89, empty=0.10, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.91 | DEVICE=None | I=5.37, Pabs=2363.4, H1=59.2, THD=1.239 | state_probs[plugged_off=0.91, empty=0.09, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.91 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.91 | DEVICE=None | I=4.81, Pabs=2308.8, H1=33.7, THD=1.996 | state_probs[plugged_off=0.91, empty=0.09, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.91 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.10, Pabs=1810.7, H1=34.7, THD=1.101 | state_probs[plugged_off=0.87, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.65, Pabs=2227.4, H1=17.0, THD=3.927 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.92, Pabs=2289.1, H1=59.2, THD=0.715 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.83, Pabs=2297.0, H1=60.3, THD=0.768 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.30, Pabs=2415.0, H1=53.0, THD=1.428 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.78, Pabs=2147.2, H1=79.3, THD=0.635 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.68, Pabs=2161.0, H1=11.9, THD=3.737 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=5.01, Pabs=2321.3, H1=27.8, THD=2.335 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.95, Pabs=2336.9, H1=38.9, THD=0.944 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.03, Pabs=2324.7, H1=39.4, THD=2.050 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.75, Pabs=2121.6, H1=42.1, THD=1.553 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.34, Pabs=2115.9, H1=26.7, THD=2.670 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.49, Pabs=2118.1, H1=32.7, THD=1.215 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.29, Pabs=2129.4, H1=30.5, THD=3.086 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.29, Pabs=2478.3, H1=33.7, THD=2.595 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.74, Pabs=2303.8, H1=40.2, THD=2.166 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.57, Pabs=2280.8, H1=27.6, THD=2.390 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.78, Pabs=2232.2, H1=54.3, THD=0.755 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.69, Pabs=2106.1, H1=36.7, THD=1.806 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.34, Pabs=2499.8, H1=76.3, THD=0.783 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.02, Pabs=2253.8, H1=60.3, THD=1.078 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.95, Pabs=2210.6, H1=14.2, THD=2.151 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.62, Pabs=2103.6, H1=40.2, THD=1.786 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.79, Pabs=2211.1, H1=45.4, THD=2.049 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.48 | DEVICE=None | I=463.37, Pabs=133220.7, H1=18813.5, THD=0.605 | state_probs[plugged_off=0.48, on=0.48, empty=0.04]
[DELTA EVENT] COOKER marked OFF source=cooker_on_deferred_unstable_state slot=1
[DELTA EVENT] ON COOKER deferred/marked OFF: waiting stable cooker heating | state=plugged_off, on_prob=0.48, dPabs=43581.3, dI=152.70, dH1=6254.8
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.48 abs_device=None dconf=0.00 event=ON active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.48 | DEVICE=None | I=449.58, Pabs=122882.4, H1=18533.5, THD=0.628 | state_probs[plugged_off=0.48, on=0.47, empty=0.04]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.48 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=on sconf=0.49 | DEVICE=None | I=437.97, Pabs=130480.1, H1=18812.8, THD=0.543 | state_probs[on=0.49, plugged_off=0.47, empty=0.04]
[AI ADAPTER] state=plugged_off raw=on sconf=0.49 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.60 | DEVICE=cooker dconf=0.49 | I=509.24, Pabs=281235.3, H1=23450.4, THD=0.406 | state_probs[on=0.60, plugged_off=0.36, empty=0.04] | device_probs[cooker=0.49, fan=0.21, charger=0.17, dryer=0.13]
[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | abs_conf=0.49, cooker_prob=0.49, dryer_prob=0.13, I=509.24, Pabs=281235.3, H1=23450.4
[AI ADAPTER] state=on raw=on sconf=0.60 abs_device=cooker dconf=0.49 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.50 | I=501.50, Pabs=272651.2, H1=23514.8, THD=0.393 | state_probs[on=0.61, plugged_off=0.36, empty=0.04] | device_probs[cooker=0.50, fan=0.21, charger=0.16, dryer=0.13]
[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | abs_conf=0.50, cooker_prob=0.50, dryer_prob=0.13, I=501.50, Pabs=272651.2, H1=23514.8
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.50 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.49 | I=504.20, Pabs=273841.9, H1=23439.0, THD=0.403 | state_probs[on=0.61, plugged_off=0.35, empty=0.04] | device_probs[cooker=0.49, fan=0.21, charger=0.16, dryer=0.14]
[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | abs_conf=0.49, cooker_prob=0.49, dryer_prob=0.14, I=504.20, Pabs=273841.9, H1=23439.0
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.49 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.62 | DEVICE=cooker dconf=0.50 | I=509.26, Pabs=274910.1, H1=23714.1, THD=0.387 | state_probs[on=0.62, plugged_off=0.34, empty=0.04] | device_probs[cooker=0.50, fan=0.21, charger=0.15, dryer=0.14]
[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | abs_conf=0.50, cooker_prob=0.50, dryer_prob=0.14, I=509.26, Pabs=274910.1, H1=23714.1
[AI ADAPTER] state=on raw=on sconf=0.62 abs_device=cooker dconf=0.50 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.63 | DEVICE=cooker dconf=0.52 | I=507.29, Pabs=278152.0, H1=21992.5, THD=0.205 | state_probs[on=0.63, plugged_off=0.34, empty=0.03] | device_probs[cooker=0.52, fan=0.22, dryer=0.15, charger=0.11]
[DELTA SELECT] ON DRYER -> COOKER: cooker heating transition suspected | abs_device=cooker, abs_conf=0.52, cooker_prob=0.52, I=507.29, Pabs=278152.0, H1=21992.5
[DELTA EVENT] COOKER marked OFF source=blocked_false_cooker_fast_dryer slot=1
[DELTA EVENT] ON COOKER blocked before active: dryer fast_high/mode context | source=delta, conf=0.90, I=507.29, Pabs=278152.0, H1=21992.5
[DELTA EVENT] ON DRYER slot=2 conf=0.90 source=blocked_cooker_as_dryer_v33 | dPabs=118521.2, dI=112.51, dH1=5853.4 | device_probs[dryer=0.41, fan=0.31, cooker=0.28, charger=0.00]
[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | abs_conf=0.52, cooker_prob=0.52, dryer_prob=0.15, I=507.29, Pabs=278152.0, H1=21992.5
[AI ADAPTER] state=on raw=on sconf=0.63 abs_device=cooker dconf=0.52 event=ON active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.64 | DEVICE=cooker dconf=0.53 | I=512.65, Pabs=284367.0, H1=23484.4, THD=0.395 | state_probs[on=0.64, plugged_off=0.32, empty=0.04] | device_probs[cooker=0.53, fan=0.22, dryer=0.15, charger=0.10]
[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | abs_conf=0.53, cooker_prob=0.53, dryer_prob=0.15, I=512.65, Pabs=284367.0, H1=23484.4
[AI ADAPTER] state=on raw=on sconf=0.64 abs_device=cooker dconf=0.53 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.95 | DEVICE=cooker dconf=0.69 | I=517.64, Pabs=285975.6, H1=23542.1, THD=0.393 | state_probs[on=0.95, plugged_off=0.05, empty=0.00] | device_probs[dryer=0.69, cooker=0.30, charger=0.01, fan=0.00]
[ABS DEVICE GUARD] COOKER sync blocked: dryer mode/restart over COOKER_OFF suspected | abs_conf=0.69, cooker_prob=0.30, dryer_prob=0.69, I=517.64, Pabs=285975.6, H1=23542.1
[AI ADAPTER] state=on raw=on sconf=0.95 abs_device=cooker dconf=0.69 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.95 | DEVICE=dryer dconf=0.70 | I=500.85, Pabs=269427.4, H1=23359.5, THD=0.396 | state_probs[on=0.95, plugged_off=0.05, empty=0.00] | device_probs[dryer=0.70, cooker=0.30, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.95 abs_device=dryer dconf=0.70 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.95 | DEVICE=dryer dconf=0.72 | I=516.17, Pabs=286991.5, H1=23426.2, THD=0.196 | state_probs[on=0.95, plugged_off=0.05, empty=0.00] | device_probs[dryer=0.72, cooker=0.27, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.95 abs_device=dryer dconf=0.72 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=497.14, Pabs=271275.3, H1=24170.0, THD=0.352 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=503.14, Pabs=274550.5, H1=23364.9, THD=0.249 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=498.99, Pabs=271153.4, H1=23438.4, THD=0.387 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.00, fan=0.00]
[DELTA EVENT] OFF DRYER canceled: dryer mode change/still alive | dPabs=-7644.2, dI=-10.89, dH1=404.6
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=OFF active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=504.88, Pabs=273615.8, H1=22745.3, THD=0.395 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=508.29, Pabs=284932.5, H1=22741.2, THD=0.401 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=503.79, Pabs=281552.1, H1=23173.8, THD=0.387 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=504.12, Pabs=284209.5, H1=22791.3, THD=0.396 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=489.36, Pabs=261659.7, H1=22946.8, THD=0.384 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=491.04, Pabs=267294.7, H1=22752.5, THD=0.397 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=489.68, Pabs=262348.9, H1=23005.2, THD=0.380 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[DELTA EVENT] OFF DRYER canceled: dryer mode change/still alive | dPabs=-14567.9, dI=-13.84, dH1=-141.0
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=OFF active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.87 | I=494.70, Pabs=266593.4, H1=22896.2, THD=0.384 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.87 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.83 | I=499.10, Pabs=282666.4, H1=22819.1, THD=0.393 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.83 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.84 | I=488.50, Pabs=261067.8, H1=22912.6, THD=0.384 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.84 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.84 | I=486.65, Pabs=262165.8, H1=22789.8, THD=0.388 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.84 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.97 | DEVICE=dryer dconf=0.84 | I=493.10, Pabs=269313.6, H1=22768.5, THD=0.391 | state_probs[on=0.97, plugged_off=0.03, empty=0.00] | device_probs[dryer=0.84, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.97 abs_device=dryer dconf=0.84 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.97 | DEVICE=dryer dconf=0.83 | I=496.29, Pabs=282605.2, H1=22692.6, THD=0.380 | state_probs[on=0.97, plugged_off=0.03, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.97 abs_device=dryer dconf=0.83 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.97 | DEVICE=dryer dconf=0.83 | I=493.73, Pabs=273891.1, H1=22760.7, THD=0.382 | state_probs[on=0.97, plugged_off=0.03, empty=0.00] | device_probs[dryer=0.83, cooker=0.12, charger=0.04, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.97 abs_device=dryer dconf=0.83 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=484.59, Pabs=266310.2, H1=23154.2, THD=0.313 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=488.36, Pabs=267148.3, H1=22624.0, THD=0.392 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=491.43, Pabs=267582.9, H1=22547.1, THD=0.394 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=490.05, Pabs=278604.2, H1=23354.8, THD=0.274 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=492.80, Pabs=275701.0, H1=23381.9, THD=0.361 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=485.09, Pabs=259503.8, H1=22609.3, THD=0.391 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=489.58, Pabs=275749.8, H1=23823.4, THD=0.241 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=482.32, Pabs=267349.4, H1=23061.1, THD=0.334 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=491.49, Pabs=268912.1, H1=22590.4, THD=0.378 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=479.04, Pabs=262199.9, H1=22341.3, THD=0.385 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[DELTA EVENT] OFF DRYER canceled: dryer mode change/still alive | dPabs=-4561.2, dI=-5.27, dH1=-392.5
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=OFF active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=486.73, Pabs=270901.0, H1=22317.0, THD=0.384 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=488.78, Pabs=277287.2, H1=22231.7, THD=0.390 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=477.60, Pabs=263496.4, H1=22586.8, THD=0.218 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=482.89, Pabs=261339.6, H1=22347.3, THD=0.375 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=475.50, Pabs=257158.8, H1=22323.1, THD=0.376 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=475.49, Pabs=265461.9, H1=22210.1, THD=0.382 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.88 | I=486.85, Pabs=270563.0, H1=22083.4, THD=0.390 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=dryer dconf=0.88 | I=485.61, Pabs=269662.8, H1=22154.5, THD=0.382 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[dryer=0.88, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=472.57, Pabs=254648.7, H1=22215.5, THD=0.372 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=471.79, Pabs=259649.2, H1=22176.5, THD=0.377 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.88 | I=477.20, Pabs=264767.6, H1=22071.2, THD=0.383 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.88, cooker=0.11, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.88 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.87 | I=484.00, Pabs=267865.6, H1=22040.5, THD=0.383 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.87, cooker=0.12, charger=0.01, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.87 event=None active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.97 | DEVICE=dryer dconf=0.58 | I=187.51, Pabs=52164.4, H1=589.6, THD=0.293 | state_probs[on=0.97, plugged_off=0.03, empty=0.00] | device_probs[dryer=0.58, cooker=0.27, charger=0.13, fan=0.03]
[DELTA EVENT] OFF DRYER canceled: dryer mode change/still alive | dPabs=-67924.9, dI=-95.06, dH1=-7293.4
[AI ADAPTER] state=on raw=on sconf=0.97 abs_device=dryer dconf=0.58 event=OFF active=['COOKER_OFF', 'DRYER_ON', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.68 | DEVICE=dryer dconf=0.51 | I=6.41, Pabs=2808.4, H1=67.3, THD=0.490 | state_probs[on=0.68, plugged_off=0.29, empty=0.02] | device_probs[cooker=0.51, fan=0.21, dryer=0.14, charger=0.14]
[DELTA STALE] moved active DRYER to OFF: latest is idle
[AI ADAPTER] state=on raw=on sconf=0.68 abs_device=dryer dconf=0.51 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.62 | DEVICE=cooker dconf=0.48 | I=4.82, Pabs=2080.3, H1=29.2, THD=3.453 | state_probs[on=0.62, plugged_off=0.34, empty=0.03] | device_probs[cooker=0.48, fan=0.20, charger=0.18, dryer=0.14]
[AI ADAPTER] state=on raw=on sconf=0.62 abs_device=cooker dconf=0.48 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.47 | I=4.58, Pabs=2090.5, H1=27.3, THD=3.031 | state_probs[on=0.61, plugged_off=0.35, empty=0.04] | device_probs[cooker=0.47, fan=0.20, charger=0.19, dryer=0.14]
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.47 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.47 | I=4.67, Pabs=2243.4, H1=57.5, THD=0.831 | state_probs[on=0.61, plugged_off=0.35, empty=0.04] | device_probs[cooker=0.47, fan=0.20, charger=0.20, dryer=0.13]
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.47 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.61 | DEVICE=cooker dconf=0.47 | I=4.97, Pabs=2308.9, H1=40.5, THD=1.364 | state_probs[on=0.61, plugged_off=0.35, empty=0.04] | device_probs[cooker=0.47, charger=0.20, fan=0.20, dryer=0.13]
[AI ADAPTER] state=on raw=on sconf=0.61 abs_device=cooker dconf=0.47 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.60 | DEVICE=cooker dconf=0.48 | I=5.17, Pabs=2350.3, H1=49.0, THD=0.933 | state_probs[on=0.60, plugged_off=0.35, empty=0.04] | device_probs[cooker=0.48, charger=0.21, fan=0.20, dryer=0.11]
[AI ADAPTER] state=on raw=on sconf=0.60 abs_device=cooker dconf=0.48 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.59 | DEVICE=cooker dconf=0.47 | I=5.22, Pabs=2428.1, H1=31.7, THD=2.326 | state_probs[on=0.59, plugged_off=0.36, empty=0.04] | device_probs[cooker=0.47, charger=0.23, fan=0.19, dryer=0.11]
[AI ADAPTER] state=on raw=on sconf=0.59 abs_device=cooker dconf=0.47 event=OFF active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.59 | DEVICE=unknown_on dconf=0.34 | I=4.86, Pabs=2339.4, H1=21.0, THD=1.801 | state_probs[on=0.59, plugged_off=0.37, empty=0.05] | device_probs[cooker=0.34, charger=0.33, fan=0.24, dryer=0.09]
[AI ADAPTER] state=on raw=on sconf=0.59 abs_device=None dconf=0.34 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=plugged_off sconf=0.78 | DEVICE=cooker dconf=0.41 | I=4.33, Pabs=1935.7, H1=36.0, THD=1.474 | state_probs[plugged_off=0.78, on=0.16, empty=0.06] | device_probs[fan=0.41, charger=0.40, cooker=0.17, dryer=0.03]
[AI ADAPTER] state=on raw=plugged_off sconf=0.78 abs_device=cooker dconf=0.41 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.10, Pabs=1830.9, H1=29.3, THD=1.480 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.57, Pabs=2064.8, H1=33.8, THD=2.287 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.81, Pabs=2271.9, H1=16.7, THD=2.449 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=3.84, Pabs=1852.5, H1=37.9, THD=1.412 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.99, Pabs=2343.6, H1=80.1, THD=0.759 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=6.05, Pabs=2761.6, H1=42.2, THD=0.694 | state_probs[plugged_off=0.85, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.31, Pabs=2376.8, H1=74.4, THD=0.745 | state_probs[plugged_off=0.85, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.58, Pabs=2200.4, H1=62.4, THD=0.819 | state_probs[plugged_off=0.85, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.03, Pabs=2130.0, H1=66.2, THD=0.842 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.89, Pabs=2150.0, H1=36.8, THD=1.711 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.37, Pabs=2347.6, H1=72.2, THD=0.619 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.88, Pabs=2358.9, H1=35.3, THD=1.266 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=13.37, Pabs=6167.2, H1=46.0, THD=1.764 | state_probs[plugged_off=0.84, empty=0.14, on=0.02]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.74, Pabs=2260.5, H1=55.3, THD=0.975 | state_probs[plugged_off=0.85, empty=0.12, on=0.03]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.48, Pabs=2150.3, H1=10.7, THD=6.747 | state_probs[plugged_off=0.85, empty=0.13, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.54, Pabs=1974.1, H1=3.1, THD=26.440 | state_probs[plugged_off=0.83, empty=0.16, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=7.58, Pabs=3693.7, H1=41.7, THD=1.409 | state_probs[plugged_off=0.83, empty=0.16, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.95, Pabs=2350.2, H1=25.9, THD=3.486 | state_probs[plugged_off=0.82, empty=0.17, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.16, Pabs=2497.6, H1=44.7, THD=1.130 | state_probs[plugged_off=0.82, empty=0.16, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.87, Pabs=2729.4, H1=59.0, THD=1.041 | state_probs[plugged_off=0.82, empty=0.17, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.66, Pabs=1942.4, H1=46.1, THD=1.197 | state_probs[plugged_off=0.85, empty=0.14, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=6.41, Pabs=2834.7, H1=24.9, THD=2.135 | state_probs[plugged_off=0.84, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.81, Pabs=2735.7, H1=62.1, THD=1.020 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=6.03, Pabs=2638.4, H1=74.9, THD=0.687 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.38, Pabs=2276.1, H1=70.4, THD=0.922 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.59, Pabs=2130.4, H1=0.6, THD=78.576 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.81, Pabs=2265.9, H1=61.7, THD=1.066 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.57, Pabs=1938.7, H1=23.6, THD=1.367 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.77, Pabs=2221.8, H1=34.1, THD=3.088 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.37, Pabs=2088.3, H1=37.8, THD=1.227 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.82, Pabs=2161.0, H1=24.5, THD=3.066 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.18, Pabs=2015.5, H1=31.8, THD=1.868 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.80, Pabs=2297.5, H1=42.3, THD=1.512 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.80, Pabs=2260.4, H1=38.8, THD=1.366 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.81, Pabs=2334.0, H1=32.8, THD=2.059 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.40, Pabs=2540.0, H1=16.8, THD=4.208 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.29, Pabs=1945.2, H1=60.4, THD=1.329 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.87, Pabs=2303.1, H1=22.0, THD=3.752 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.03, Pabs=1757.7, H1=30.7, THD=0.852 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.00, Pabs=1796.2, H1=63.9, THD=0.723 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.37, Pabs=2379.5, H1=57.8, THD=1.168 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.41, Pabs=2122.4, H1=31.2, THD=2.111 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.47, Pabs=2091.9, H1=43.9, THD=0.826 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.96, Pabs=2298.8, H1=52.4, THD=1.448 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.77 | DEVICE=None | I=3.82, Pabs=1757.0, H1=15.4, THD=2.786 | state_probs[plugged_off=0.77, empty=0.23, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.77 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.75 | DEVICE=None | I=4.64, Pabs=2120.2, H1=14.6, THD=3.192 | state_probs[plugged_off=0.75, empty=0.25, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.75 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.75 | DEVICE=None | I=4.75, Pabs=2146.3, H1=28.6, THD=3.123 | state_probs[plugged_off=0.75, empty=0.25, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.75 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.77 | DEVICE=None | I=5.51, Pabs=2443.7, H1=56.5, THD=0.846 | state_probs[plugged_off=0.77, empty=0.23, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.77 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.96, Pabs=2268.9, H1=22.7, THD=2.609 | state_probs[plugged_off=0.79, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.89, Pabs=2215.1, H1=37.1, THD=3.121 | state_probs[plugged_off=0.84, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.65, Pabs=2295.1, H1=33.0, THD=1.866 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.18, Pabs=1966.7, H1=49.1, THD=0.827 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.37, Pabs=2004.5, H1=51.5, THD=1.353 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.30, Pabs=1949.9, H1=40.8, THD=1.858 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.67, Pabs=2149.8, H1=50.0, THD=1.269 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.55, Pabs=1994.2, H1=89.5, THD=0.647 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.66, Pabs=2084.7, H1=60.5, THD=0.681 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.77 | DEVICE=None | I=4.87, Pabs=2206.4, H1=51.7, THD=0.963 | state_probs[plugged_off=0.77, empty=0.23, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.77 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.24, Pabs=1895.4, H1=48.5, THD=1.307 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.63, Pabs=2155.3, H1=37.0, THD=1.665 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.73, Pabs=2126.3, H1=41.1, THD=1.096 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.23, Pabs=2066.6, H1=35.6, THD=2.074 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.45, Pabs=2046.4, H1=14.5, THD=2.679 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=5.10, Pabs=2422.2, H1=77.9, THD=0.737 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.85, Pabs=2268.2, H1=4.0, THD=6.963 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.73, Pabs=2152.7, H1=52.5, THD=1.708 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.47, Pabs=2194.3, H1=24.4, THD=1.923 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=5.04, Pabs=2305.3, H1=39.6, THD=1.226 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.68, Pabs=2236.6, H1=43.9, THD=1.205 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.85, Pabs=2247.3, H1=57.5, THD=1.028 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.01, Pabs=2510.3, H1=49.4, THD=0.851 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.08, Pabs=2370.9, H1=48.6, THD=1.522 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=6.75, Pabs=2957.8, H1=30.4, THD=2.332 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=6.39, Pabs=2873.4, H1=59.0, THD=1.063 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.94, Pabs=2310.1, H1=40.8, THD=1.784 | state_probs[plugged_off=0.86, empty=0.13, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=5.71, Pabs=2457.5, H1=62.1, THD=0.607 | state_probs[plugged_off=0.86, empty=0.14, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.52, Pabs=1989.1, H1=71.5, THD=0.806 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.77, Pabs=2253.5, H1=88.9, THD=0.615 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.59, Pabs=2104.9, H1=20.4, THD=3.249 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.41, Pabs=1936.7, H1=21.6, THD=2.961 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.48, Pabs=2183.8, H1=54.5, THD=0.747 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.67, Pabs=2085.9, H1=18.6, THD=2.950 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.97, Pabs=2232.2, H1=65.3, THD=0.832 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=5.10, Pabs=2207.5, H1=31.3, THD=1.421 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.25, Pabs=1921.1, H1=77.9, THD=0.296 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.63, Pabs=2038.0, H1=34.9, THD=1.289 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.89, Pabs=2218.2, H1=27.6, THD=2.894 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.89, Pabs=2244.5, H1=21.6, THD=3.200 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.12, Pabs=2325.9, H1=54.3, THD=1.037 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.99, Pabs=2254.0, H1=28.8, THD=2.631 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.55, Pabs=2013.5, H1=19.0, THD=1.861 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.10, Pabs=2469.5, H1=22.8, THD=2.086 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.96, Pabs=2343.9, H1=26.4, THD=2.732 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.08, Pabs=2286.9, H1=51.2, THD=1.340 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.54, Pabs=1919.4, H1=36.1, THD=1.457 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.43, Pabs=2187.9, H1=31.2, THD=1.970 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.21, Pabs=2573.7, H1=64.4, THD=1.327 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.53, Pabs=2172.5, H1=39.0, THD=0.882 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.57, Pabs=2199.7, H1=46.5, THD=1.541 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.84, Pabs=2255.5, H1=95.4, THD=0.402 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.95, Pabs=2130.9, H1=24.5, THD=2.709 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.62, Pabs=2101.6, H1=55.1, THD=1.019 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.71, Pabs=2277.9, H1=45.1, THD=0.930 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.05, Pabs=2266.0, H1=36.8, THD=1.601 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.35, Pabs=1990.0, H1=52.1, THD=1.158 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.61, Pabs=2137.6, H1=59.7, THD=0.856 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.60, Pabs=2113.4, H1=52.0, THD=0.668 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.79, Pabs=2181.6, H1=45.2, THD=1.338 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=5.13, Pabs=2291.2, H1=48.8, THD=1.172 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.97, Pabs=2286.1, H1=81.2, THD=0.498 | state_probs[plugged_off=0.81, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.73, Pabs=2165.0, H1=32.1, THD=1.895 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.95, Pabs=2233.2, H1=6.8, THD=9.537 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.29, Pabs=1855.7, H1=64.0, THD=0.833 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=5.00, Pabs=2234.1, H1=29.3, THD=1.509 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.52, Pabs=2082.8, H1=30.9, THD=2.336 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.28, Pabs=2522.0, H1=23.4, THD=2.502 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.70, Pabs=2290.8, H1=64.1, THD=0.722 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.66, Pabs=2152.1, H1=14.6, THD=3.234 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.80, Pabs=2294.5, H1=43.0, THD=1.600 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.69, Pabs=2011.4, H1=1.9, THD=22.243 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.28, Pabs=1964.7, H1=16.9, THD=3.471 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.69, Pabs=2300.1, H1=28.3, THD=2.780 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.27, Pabs=2192.6, H1=51.5, THD=1.265 | state_probs[plugged_off=0.84, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=8.99, Pabs=4333.7, H1=69.6, THD=0.342 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=8.85, Pabs=3254.3, H1=137.0, THD=0.583 | state_probs[plugged_off=0.85, empty=0.14, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=9.13, Pabs=4168.2, H1=69.8, THD=0.415 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.54, Pabs=2043.5, H1=27.6, THD=1.870 | state_probs[plugged_off=0.85, empty=0.15, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=10.08, Pabs=5039.0, H1=45.8, THD=2.096 | state_probs[plugged_off=0.85, empty=0.14, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.97, Pabs=2280.6, H1=32.4, THD=1.385 | state_probs[plugged_off=0.85, empty=0.14, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=5.08, Pabs=2253.1, H1=61.9, THD=0.741 | state_probs[plugged_off=0.87, empty=0.12, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=5.74, Pabs=2808.7, H1=16.9, THD=3.018 | state_probs[plugged_off=0.88, empty=0.11, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=5.96, Pabs=2777.1, H1=48.5, THD=1.150 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.64, Pabs=2035.6, H1=22.9, THD=2.297 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.70, Pabs=2185.5, H1=60.8, THD=1.254 | state_probs[plugged_off=0.88, empty=0.12, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=5.25, Pabs=2452.9, H1=63.5, THD=0.799 | state_probs[plugged_off=0.86, empty=0.13, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.61, Pabs=2150.6, H1=83.5, THD=0.750 | state_probs[plugged_off=0.88, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.88, Pabs=2176.1, H1=27.3, THD=1.200 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.23, Pabs=1827.5, H1=36.1, THD=1.112 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=4.48, Pabs=2090.5, H1=24.4, THD=2.523 | state_probs[plugged_off=0.88, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.89 | DEVICE=None | I=4.54, Pabs=2002.8, H1=37.8, THD=1.452 | state_probs[plugged_off=0.89, empty=0.11, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.89 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.35, Pabs=1967.5, H1=16.4, THD=3.099 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.92, Pabs=2251.9, H1=23.1, THD=2.867 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.49, Pabs=2073.9, H1=46.6, THD=1.221 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.86, Pabs=2182.7, H1=34.4, THD=1.417 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=5.05, Pabs=2257.0, H1=15.5, THD=3.648 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.63, Pabs=2131.4, H1=24.1, THD=2.611 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.70, Pabs=2215.3, H1=15.3, THD=5.076 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.48, Pabs=2068.1, H1=29.6, THD=1.915 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.77, Pabs=2066.8, H1=18.8, THD=2.976 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.30, Pabs=1974.9, H1=9.3, THD=3.838 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=5.13, Pabs=2400.9, H1=48.6, THD=1.112 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.37, Pabs=1905.2, H1=21.9, THD=3.112 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.77 | DEVICE=None | I=4.43, Pabs=1986.1, H1=13.7, THD=3.883 | state_probs[plugged_off=0.77, empty=0.23, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.77 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.76 | DEVICE=None | I=4.25, Pabs=1938.6, H1=32.4, THD=1.796 | state_probs[plugged_off=0.76, empty=0.24, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.76 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.46, Pabs=2042.5, H1=15.9, THD=3.926 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=5.25, Pabs=2385.5, H1=47.0, THD=1.303 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.59, Pabs=1951.4, H1=39.8, THD=0.904 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.67, Pabs=2111.8, H1=21.0, THD=3.159 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.52, Pabs=2005.3, H1=20.0, THD=2.058 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.32, Pabs=2071.2, H1=38.8, THD=1.611 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.93, Pabs=2379.2, H1=37.4, THD=1.056 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=5.00, Pabs=2165.5, H1=63.5, THD=0.744 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.74, Pabs=2141.5, H1=30.8, THD=2.079 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.84, Pabs=2308.7, H1=33.1, THD=1.998 | state_probs[plugged_off=0.85, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.31, Pabs=1955.8, H1=18.8, THD=3.122 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.63, Pabs=2138.4, H1=5.8, THD=11.737 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.70, Pabs=2103.8, H1=21.3, THD=3.024 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.04, Pabs=2308.9, H1=53.9, THD=1.207 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.50, Pabs=1953.9, H1=54.0, THD=1.308 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.89, Pabs=2065.2, H1=50.5, THD=1.383 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.97, Pabs=2324.8, H1=38.8, THD=1.767 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.99, Pabs=2201.1, H1=15.1, THD=3.823 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.01, Pabs=2391.8, H1=56.9, THD=1.506 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.82, Pabs=2235.2, H1=29.8, THD=2.330 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.13, Pabs=2356.0, H1=47.3, THD=1.172 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=5.30, Pabs=2497.6, H1=12.6, THD=3.451 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.37, Pabs=2180.5, H1=39.0, THD=1.931 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.07, Pabs=2201.5, H1=27.7, THD=2.597 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.55, Pabs=2085.6, H1=16.7, THD=2.978 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.51, Pabs=2033.0, H1=26.6, THD=2.011 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=5.07, Pabs=2381.8, H1=89.2, THD=0.479 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.37, Pabs=2055.5, H1=25.3, THD=1.300 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.00, Pabs=2315.2, H1=28.3, THD=3.341 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.40, Pabs=1941.8, H1=18.6, THD=4.124 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.45, Pabs=2001.3, H1=33.7, THD=2.197 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.91, Pabs=2211.6, H1=33.6, THD=1.545 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.54, Pabs=2128.6, H1=33.2, THD=1.735 | state_probs[plugged_off=0.79, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.93, Pabs=2288.3, H1=36.8, THD=2.059 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.63, Pabs=2102.1, H1=45.8, THD=1.843 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.54, Pabs=2123.4, H1=30.4, THD=1.111 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=5.33, Pabs=2505.0, H1=78.4, THD=0.827 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.80, Pabs=2192.1, H1=54.6, THD=1.474 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.60, Pabs=2098.0, H1=59.4, THD=0.769 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.95, Pabs=2245.8, H1=42.0, THD=1.131 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.41, Pabs=2123.9, H1=23.0, THD=3.526 | state_probs[plugged_off=0.87, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.88 | DEVICE=None | I=5.13, Pabs=2487.0, H1=58.7, THD=0.690 | state_probs[plugged_off=0.88, empty=0.11, on=0.01]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.88 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.75, Pabs=2187.0, H1=21.4, THD=2.036 | state_probs[plugged_off=0.87, empty=0.12, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.91, Pabs=2316.4, H1=43.0, THD=2.111 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.87 | DEVICE=None | I=4.59, Pabs=2045.3, H1=31.6, THD=0.993 | state_probs[plugged_off=0.87, empty=0.13, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.87 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.67, Pabs=2183.8, H1=52.2, THD=0.956 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.44, Pabs=1951.1, H1=10.1, THD=7.360 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.63, Pabs=2087.3, H1=53.1, THD=0.848 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.87, Pabs=2231.5, H1=69.3, THD=0.986 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=5.46, Pabs=2653.7, H1=80.6, THD=1.397 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.38, Pabs=2036.1, H1=9.0, THD=5.969 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.58, Pabs=2086.9, H1=25.5, THD=0.819 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.98, Pabs=2377.8, H1=42.6, THD=0.897 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.72, Pabs=2184.7, H1=31.6, THD=2.164 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.56, Pabs=2154.6, H1=29.9, THD=2.127 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.32, Pabs=1908.0, H1=50.0, THD=1.476 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.86 | DEVICE=None | I=4.93, Pabs=2254.3, H1=6.3, THD=10.340 | state_probs[plugged_off=0.86, empty=0.14, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.86 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.85 | DEVICE=None | I=4.91, Pabs=2318.8, H1=15.5, THD=2.088 | state_probs[plugged_off=0.85, empty=0.15, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.85 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=5.25, Pabs=2341.0, H1=56.8, THD=1.729 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.63, Pabs=2113.6, H1=21.3, THD=3.346 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.52, Pabs=1890.4, H1=36.5, THD=1.670 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.85, Pabs=2267.5, H1=32.1, THD=2.793 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.50, Pabs=1973.0, H1=19.8, THD=1.749 | state_probs[plugged_off=0.80, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=5.31, Pabs=2391.1, H1=37.7, THD=1.817 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.84 | DEVICE=None | I=4.80, Pabs=2239.9, H1=24.3, THD=1.644 | state_probs[plugged_off=0.84, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.84 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.77, Pabs=2185.0, H1=6.3, THD=6.492 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.80, Pabs=2367.9, H1=31.1, THD=1.235 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.13, Pabs=2306.3, H1=18.1, THD=3.197 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.21, Pabs=1795.9, H1=28.8, THD=2.336 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.99, Pabs=2122.7, H1=17.9, THD=2.937 | state_probs[plugged_off=0.80, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.33, Pabs=1887.3, H1=50.3, THD=0.845 | state_probs[plugged_off=0.81, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.89, Pabs=2177.7, H1=33.8, THD=1.955 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=4.76, Pabs=2127.5, H1=22.0, THD=4.477 | state_probs[plugged_off=0.83, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=5.18, Pabs=2289.2, H1=35.3, THD=1.133 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.69, Pabs=2130.5, H1=32.0, THD=2.348 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.83 | DEVICE=None | I=5.01, Pabs=2386.6, H1=39.4, THD=1.987 | state_probs[plugged_off=0.83, empty=0.16, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.83 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.61, Pabs=2137.9, H1=33.6, THD=1.362 | state_probs[plugged_off=0.82, empty=0.17, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.52, Pabs=1846.4, H1=32.4, THD=1.965 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=5.09, Pabs=2117.0, H1=42.8, THD=2.328 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.85, Pabs=2086.3, H1=62.9, THD=0.925 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.49, Pabs=2113.9, H1=60.8, THD=1.049 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.63, Pabs=2139.0, H1=20.6, THD=3.108 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.74, Pabs=2149.6, H1=25.9, THD=1.357 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=5.07, Pabs=2228.9, H1=37.2, THD=1.635 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.82 | DEVICE=None | I=4.42, Pabs=1921.3, H1=18.0, THD=4.053 | state_probs[plugged_off=0.82, empty=0.18, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.82 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.77 | DEVICE=None | I=4.68, Pabs=1930.4, H1=19.7, THD=3.837 | state_probs[plugged_off=0.77, empty=0.23, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.77 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.11, Pabs=1828.5, H1=37.4, THD=1.398 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=5.16, Pabs=2402.3, H1=42.4, THD=1.632 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.67, Pabs=2133.9, H1=34.7, THD=2.243 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.36, Pabs=2005.2, H1=39.7, THD=1.401 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.84, Pabs=2243.2, H1=63.6, THD=0.906 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.52, Pabs=1960.6, H1=16.4, THD=3.769 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.77 | DEVICE=None | I=4.50, Pabs=2041.2, H1=19.4, THD=2.743 | state_probs[plugged_off=0.77, empty=0.23, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.77 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.74, Pabs=2176.8, H1=29.9, THD=1.702 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=5.06, Pabs=2291.1, H1=6.1, THD=8.479 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.33, Pabs=1878.1, H1=23.6, THD=3.266 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.48, Pabs=1903.1, H1=35.4, THD=1.211 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.96, Pabs=2320.4, H1=21.5, THD=3.613 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.09, Pabs=1845.3, H1=24.0, THD=1.169 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.80 | DEVICE=None | I=4.50, Pabs=2181.3, H1=18.9, THD=4.317 | state_probs[plugged_off=0.80, empty=0.20, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.80 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.26, Pabs=1959.0, H1=30.5, THD=1.453 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=5.05, Pabs=2268.6, H1=29.9, THD=2.354 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.81 | DEVICE=None | I=4.65, Pabs=2200.4, H1=43.7, THD=1.389 | state_probs[plugged_off=0.81, empty=0.19, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.81 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.78 | DEVICE=None | I=4.56, Pabs=2195.7, H1=3.5, THD=19.569 | state_probs[plugged_off=0.78, empty=0.22, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.78 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.76 | DEVICE=None | I=4.62, Pabs=2126.9, H1=28.5, THD=1.126 | state_probs[plugged_off=0.76, empty=0.24, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.76 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.77 | DEVICE=None | I=4.72, Pabs=2138.4, H1=56.9, THD=1.487 | state_probs[plugged_off=0.77, empty=0.23, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.77 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.79 | DEVICE=None | I=4.69, Pabs=2304.5, H1=20.7, THD=2.342 | state_probs[plugged_off=0.79, empty=0.21, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.79 abs_device=None dconf=0.00 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
SPI 포트가 안전하게 닫혔습니다.

[LOG] README.md 저장 완료: /home/wattsup/Project/minungnung/RaspberryPi/README.md

```

- 종료 시간: 2026-05-20 00:28:34
