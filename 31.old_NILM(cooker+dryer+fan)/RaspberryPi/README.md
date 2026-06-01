# WattsUp 실행 로그

- 시작 시간: 2026-05-19 23:54:22
- 저장 위치: `/home/wattsup/Project/minungnung/RaspberryPi/README.md`

```text
[AI VERSION] ai_extension_2026_05_19_v37_cooker_dryer_fan_entry_guard
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
[AI] STATE=plugged_off raw=plugged_off sconf=0.75 | DEVICE=None | I=4.75, Pabs=2117.1, H1=34.6, THD=2.068 | state_probs[plugged_off=0.75, empty=0.25, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.75 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.73 | DEVICE=None | I=4.55, Pabs=2113.7, H1=17.8, THD=5.279 | state_probs[plugged_off=0.73, empty=0.27, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.73 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.76 | DEVICE=None | I=4.18, Pabs=1853.4, H1=43.9, THD=0.604 | state_probs[plugged_off=0.76, empty=0.24, on=0.00]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.76 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.72 | DEVICE=None | I=28.60, Pabs=12553.3, H1=1040.5, THD=0.131 | state_probs[plugged_off=0.72, on=0.21, empty=0.07]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.72 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.70 | DEVICE=None | I=21.42, Pabs=9179.6, H1=1007.1, THD=0.160 | state_probs[plugged_off=0.70, on=0.22, empty=0.07]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.70 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.69 | DEVICE=None | I=19.97, Pabs=8026.4, H1=959.2, THD=0.186 | state_probs[plugged_off=0.69, on=0.25, empty=0.07]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.69 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.68 | DEVICE=None | I=19.90, Pabs=8992.0, H1=954.6, THD=0.142 | state_probs[plugged_off=0.68, on=0.26, empty=0.06]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.68 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.68 | DEVICE=None | I=20.65, Pabs=8589.4, H1=976.5, THD=0.113 | state_probs[plugged_off=0.68, on=0.27, empty=0.06]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.68 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.68 | DEVICE=None | I=20.73, Pabs=8807.8, H1=1032.4, THD=0.113 | state_probs[plugged_off=0.68, on=0.28, empty=0.04]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.68 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.65 | DEVICE=None | I=20.89, Pabs=8434.5, H1=976.9, THD=0.144 | state_probs[plugged_off=0.65, on=0.30, empty=0.05]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.65 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.57 | DEVICE=None | I=22.28, Pabs=9743.3, H1=1072.3, THD=0.139 | state_probs[plugged_off=0.57, on=0.39, empty=0.04]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.57 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=plugged_off sconf=0.52 | DEVICE=None | I=22.14, Pabs=9801.5, H1=1027.1, THD=0.129 | state_probs[plugged_off=0.52, on=0.45, empty=0.03]
[AI ADAPTER] state=plugged_off raw=plugged_off sconf=0.52 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=plugged_off raw=on sconf=0.70 | DEVICE=None | I=20.66, Pabs=8712.8, H1=992.8, THD=0.127 | state_probs[on=0.70, plugged_off=0.30, empty=0.00]
[AI ADAPTER] state=plugged_off raw=on sconf=0.70 abs_device=None dconf=0.00 event=None active=['EMPTY', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: EMPTY
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.75 | DEVICE=cooker dconf=0.56 | I=20.22, Pabs=8271.9, H1=977.2, THD=0.170 | state_probs[on=0.75, plugged_off=0.25, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.75 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.76 | DEVICE=cooker dconf=0.56 | I=20.52, Pabs=8747.7, H1=987.4, THD=0.073 | state_probs[on=0.76, plugged_off=0.24, empty=0.00] | device_probs[cooker=0.56, fan=0.31, charger=0.13, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.76 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.76 | DEVICE=cooker dconf=0.56 | I=21.33, Pabs=9856.5, H1=981.4, THD=0.166 | state_probs[on=0.76, plugged_off=0.24, empty=0.00] | device_probs[cooker=0.56, fan=0.31, charger=0.13, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.76 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.77 | DEVICE=cooker dconf=0.56 | I=22.45, Pabs=9619.6, H1=1061.9, THD=0.139 | state_probs[on=0.77, plugged_off=0.23, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.77 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.77 | DEVICE=cooker dconf=0.56 | I=20.42, Pabs=9056.1, H1=966.0, THD=0.059 | state_probs[on=0.77, plugged_off=0.23, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.13, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.77 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.77 | DEVICE=cooker dconf=0.56 | I=20.14, Pabs=8625.8, H1=935.3, THD=0.111 | state_probs[on=0.77, plugged_off=0.23, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.13, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.77 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.76 | DEVICE=cooker dconf=0.56 | I=19.38, Pabs=8533.6, H1=958.0, THD=0.143 | state_probs[on=0.76, plugged_off=0.24, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.13, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.76 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.71 | DEVICE=cooker dconf=0.56 | I=22.00, Pabs=9684.1, H1=1034.0, THD=0.140 | state_probs[on=0.71, plugged_off=0.29, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.13, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.71 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.69 | DEVICE=cooker dconf=0.55 | I=20.16, Pabs=9017.8, H1=973.0, THD=0.098 | state_probs[on=0.69, plugged_off=0.31, empty=0.00] | device_probs[cooker=0.55, fan=0.31, charger=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.69 abs_device=cooker dconf=0.55 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.70 | DEVICE=cooker dconf=0.55 | I=20.39, Pabs=8710.8, H1=1005.1, THD=0.199 | state_probs[on=0.70, plugged_off=0.30, empty=0.00] | device_probs[cooker=0.55, fan=0.31, charger=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.70 abs_device=cooker dconf=0.55 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.75 | DEVICE=cooker dconf=0.55 | I=22.15, Pabs=9866.5, H1=1035.0, THD=0.167 | state_probs[on=0.75, plugged_off=0.25, empty=0.00] | device_probs[cooker=0.55, fan=0.31, charger=0.14, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.75 abs_device=cooker dconf=0.55 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.76 | DEVICE=cooker dconf=0.56 | I=19.94, Pabs=8760.0, H1=898.6, THD=0.078 | state_probs[on=0.76, plugged_off=0.24, empty=0.00] | device_probs[cooker=0.56, fan=0.31, charger=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.76 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.68 | DEVICE=cooker dconf=0.56 | I=21.55, Pabs=9544.8, H1=1019.7, THD=0.059 | state_probs[on=0.68, plugged_off=0.31, empty=0.00] | device_probs[cooker=0.56, fan=0.31, charger=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.68 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.55 | I=20.51, Pabs=9165.6, H1=1033.4, THD=0.091 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.55, fan=0.31, charger=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.55 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.55 | I=21.12, Pabs=8822.4, H1=1031.4, THD=0.079 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.55, fan=0.31, charger=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.55 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.96 | DEVICE=cooker dconf=0.80 | I=767.88, Pabs=429265.2, H1=38760.6, THD=0.014 | state_probs[on=0.96, plugged_off=0.04, empty=0.00] | device_probs[cooker=0.80, dryer=0.10, charger=0.05, fan=0.05]
[DELTA EVENT] ON COOKER slot=1 conf=0.56 source=delta | dPabs=139820.4, dI=248.80, dH1=12614.3 | device_probs[cooker=0.56, fan=0.25, dryer=0.12, charger=0.07]
[AI ADAPTER] state=on raw=on sconf=0.96 abs_device=cooker dconf=0.80 event=ON active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.96 | DEVICE=cooker dconf=0.79 | I=779.25, Pabs=447767.0, H1=38063.7, THD=0.014 | state_probs[on=0.96, plugged_off=0.04, empty=0.00] | device_probs[cooker=0.79, dryer=0.13, charger=0.05, fan=0.04]
[AI ADAPTER] state=on raw=on sconf=0.96 abs_device=cooker dconf=0.79 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.97 | DEVICE=cooker dconf=0.79 | I=752.47, Pabs=417657.6, H1=38703.9, THD=0.016 | state_probs[on=0.97, plugged_off=0.03, empty=0.00] | device_probs[cooker=0.79, dryer=0.13, charger=0.05, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.97 abs_device=cooker dconf=0.79 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.98 | DEVICE=cooker dconf=0.78 | I=750.97, Pabs=430689.5, H1=37859.4, THD=0.015 | state_probs[on=0.98, plugged_off=0.02, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.98 abs_device=cooker dconf=0.78 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.89 | DEVICE=cooker dconf=0.79 | I=18.93, Pabs=7709.0, H1=914.0, THD=0.220 | state_probs[on=0.89, plugged_off=0.11, empty=0.00] | device_probs[cooker=0.79, dryer=0.13, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.89 abs_device=cooker dconf=0.79 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.89 | DEVICE=cooker dconf=0.78 | I=21.00, Pabs=9064.9, H1=1015.1, THD=0.106 | state_probs[on=0.89, plugged_off=0.11, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.89 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.89 | DEVICE=cooker dconf=0.78 | I=21.84, Pabs=9220.9, H1=1029.4, THD=0.105 | state_probs[on=0.89, plugged_off=0.11, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.89 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.88 | DEVICE=cooker dconf=0.78 | I=19.86, Pabs=8975.2, H1=927.7, THD=0.187 | state_probs[on=0.88, plugged_off=0.12, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.88 abs_device=cooker dconf=0.78 event=OFF active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.88 | DEVICE=cooker dconf=0.78 | I=19.45, Pabs=8289.9, H1=969.1, THD=0.094 | state_probs[on=0.88, plugged_off=0.12, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.88 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.87 | DEVICE=cooker dconf=0.78 | I=20.63, Pabs=9018.3, H1=998.1, THD=0.092 | state_probs[on=0.87, plugged_off=0.13, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.87 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.87 | DEVICE=cooker dconf=0.78 | I=21.90, Pabs=10266.9, H1=1027.0, THD=0.168 | state_probs[on=0.87, plugged_off=0.13, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.87 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.87 | DEVICE=cooker dconf=0.78 | I=19.84, Pabs=8460.1, H1=920.1, THD=0.205 | state_probs[on=0.87, plugged_off=0.13, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.05, fan=0.04]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.87 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.87 | DEVICE=cooker dconf=0.80 | I=123.67, Pabs=75175.2, H1=6142.5, THD=0.040 | state_probs[on=0.87, plugged_off=0.13, empty=0.00] | device_probs[cooker=0.80, dryer=0.11, charger=0.05, fan=0.04]
[AI ADAPTER] state=on raw=on sconf=0.87 abs_device=cooker dconf=0.80 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.85 | DEVICE=cooker dconf=0.73 | I=121.51, Pabs=75715.3, H1=5876.1, THD=0.043 | state_probs[on=0.85, plugged_off=0.15, empty=0.00] | device_probs[cooker=0.73, fan=0.14, charger=0.12, dryer=0.01]
[DELTA EVENT] ON COOKER slot=1 conf=0.73 source=absolute_sync_heating
[AI ADAPTER] state=on raw=on sconf=0.85 abs_device=cooker dconf=0.73 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.75 | I=121.78, Pabs=72623.8, H1=5913.7, THD=0.048 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.75, fan=0.14, charger=0.09, dryer=0.03]
[DELTA SELECT] ON DRYER -> COOKER: cooker heating transition suspected | abs_device=cooker, abs_conf=0.75, cooker_prob=0.75, I=121.78, Pabs=72623.8, H1=5913.7
[DELTA EVENT] ON update COOKER conf=0.90 source=delta
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.75 event=ON active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.79 | I=121.37, Pabs=72982.3, H1=5863.1, THD=0.056 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.79, dryer=0.11, charger=0.05, fan=0.05]
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.79 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.85 | DEVICE=cooker dconf=0.70 | I=41.45, Pabs=16125.6, H1=1131.0, THD=0.073 | state_probs[on=0.85, plugged_off=0.15, empty=0.00] | device_probs[cooker=0.70, dryer=0.14, charger=0.12, fan=0.05]
[AI ADAPTER] state=on raw=on sconf=0.85 abs_device=cooker dconf=0.70 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.70 | I=20.38, Pabs=8852.2, H1=941.0, THD=0.140 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.70, dryer=0.14, charger=0.12, fan=0.05]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.70 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.85 | DEVICE=cooker dconf=0.70 | I=20.22, Pabs=8826.2, H1=962.9, THD=0.098 | state_probs[on=0.85, plugged_off=0.15, empty=0.00] | device_probs[cooker=0.70, dryer=0.14, charger=0.12, fan=0.05]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.85 abs_device=cooker dconf=0.70 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.70 | I=20.77, Pabs=9462.0, H1=1002.8, THD=0.106 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.70, dryer=0.14, charger=0.12, fan=0.05]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.70 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.70 | I=19.54, Pabs=8383.1, H1=905.5, THD=0.153 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.70, dryer=0.14, charger=0.12, fan=0.05]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.70 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.71 | I=22.76, Pabs=9568.6, H1=1028.7, THD=0.113 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.71, dryer=0.14, charger=0.12, fan=0.04]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.71 event=OFF active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.86 | DEVICE=cooker dconf=0.66 | I=20.51, Pabs=8942.9, H1=930.8, THD=0.107 | state_probs[on=0.86, plugged_off=0.14, empty=0.00] | device_probs[cooker=0.66, charger=0.16, fan=0.13, dryer=0.05]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.86 abs_device=cooker dconf=0.66 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.85 | DEVICE=cooker dconf=0.67 | I=21.76, Pabs=10005.9, H1=1031.1, THD=0.136 | state_probs[on=0.85, plugged_off=0.15, empty=0.00] | device_probs[cooker=0.67, charger=0.19, fan=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.85 abs_device=cooker dconf=0.67 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.84 | DEVICE=cooker dconf=0.66 | I=19.86, Pabs=8134.6, H1=925.7, THD=0.194 | state_probs[on=0.84, plugged_off=0.16, empty=0.00] | device_probs[cooker=0.66, charger=0.20, fan=0.13, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.84 abs_device=cooker dconf=0.66 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.87 | DEVICE=cooker dconf=0.75 | I=785.79, Pabs=445509.0, H1=38426.5, THD=0.026 | state_probs[on=0.87, plugged_off=0.13, empty=0.00] | device_probs[cooker=0.75, charger=0.12, dryer=0.09, fan=0.04]
[AI ADAPTER] state=on raw=on sconf=0.87 abs_device=cooker dconf=0.75 event=None active=['COOKER_OFF', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.88 | DEVICE=cooker dconf=0.77 | I=775.19, Pabs=420091.3, H1=39101.7, THD=0.020 | state_probs[on=0.88, plugged_off=0.12, empty=0.00] | device_probs[cooker=0.77, dryer=0.13, charger=0.05, fan=0.04]
[DELTA EVENT] ON COOKER slot=1 conf=0.77 source=absolute_sync_heating
[AI ADAPTER] state=on raw=on sconf=0.88 abs_device=cooker dconf=0.77 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.89 | DEVICE=cooker dconf=0.78 | I=753.54, Pabs=418127.0, H1=39336.1, THD=0.012 | state_probs[on=0.89, plugged_off=0.11, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.06, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.89 abs_device=cooker dconf=0.78 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.88 | DEVICE=cooker dconf=0.78 | I=780.00, Pabs=454370.7, H1=38196.7, THD=0.016 | state_probs[on=0.88, plugged_off=0.12, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.06, fan=0.03]
[DELTA SELECT] ON DRYER -> COOKER: cooker heating transition suspected | abs_device=cooker, abs_conf=0.78, cooker_prob=0.78, I=780.00, Pabs=454370.7, H1=38196.7
[DELTA EVENT] ON update COOKER conf=0.90 source=delta
[AI ADAPTER] state=on raw=on sconf=0.88 abs_device=cooker dconf=0.78 event=ON active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.89 | DEVICE=cooker dconf=0.75 | I=752.35, Pabs=434876.5, H1=37790.1, THD=0.014 | state_probs[on=0.89, plugged_off=0.11, empty=0.00] | device_probs[cooker=0.75, dryer=0.16, charger=0.06, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.89 abs_device=cooker dconf=0.75 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.92 | DEVICE=cooker dconf=0.75 | I=756.99, Pabs=421570.7, H1=36322.5, THD=0.026 | state_probs[on=0.92, plugged_off=0.08, empty=0.00] | device_probs[cooker=0.75, dryer=0.17, charger=0.06, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.92 abs_device=cooker dconf=0.75 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=cooker dconf=0.75 | I=765.06, Pabs=451155.7, H1=37674.0, THD=0.016 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[cooker=0.75, dryer=0.17, charger=0.06, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=cooker dconf=0.75 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=cooker dconf=0.74 | I=755.40, Pabs=416470.1, H1=37615.0, THD=0.019 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[cooker=0.74, dryer=0.17, charger=0.06, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=cooker dconf=0.74 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=cooker dconf=0.73 | I=752.23, Pabs=401277.8, H1=37804.3, THD=0.016 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[cooker=0.73, dryer=0.18, charger=0.06, fan=0.03]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=cooker dconf=0.73 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=cooker dconf=0.90 | I=760.52, Pabs=422423.4, H1=37671.6, THD=0.017 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.90, cooker=0.09, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=cooker dconf=0.90 event=None active=['COOKER_ON', 'EMPTY', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.90 | I=754.42, Pabs=430236.6, H1=37749.7, THD=0.017 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.90, cooker=0.09, charger=0.00, fan=0.00]
[DELTA EVENT] ON DRYER slot=2 conf=0.90 source=absolute_sync
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.90 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.91 | I=769.39, Pabs=449739.6, H1=37616.3, THD=0.015 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.91, cooker=0.09, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.91 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=1.00 | DEVICE=dryer dconf=0.93 | I=767.72, Pabs=429560.8, H1=37707.5, THD=0.017 | state_probs[on=1.00, plugged_off=0.00, empty=0.00] | device_probs[dryer=0.93, cooker=0.07, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=1.00 abs_device=dryer dconf=0.93 event=None active=['COOKER_ON', 'DRYER_ON', 'EMPTY', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=1.00 | DEVICE=dryer dconf=0.92 | I=760.43, Pabs=446355.9, H1=37727.4, THD=0.013 | state_probs[on=1.00, plugged_off=0.00, empty=0.00] | device_probs[dryer=0.92, cooker=0.08, charger=0.00, fan=0.00]
[DELTA EVENT] ON FAN slot=3 conf=0.91 source=high_dryer_axis | dPabs=18029.7, dI=8.41, dH1=210.9 | device_probs[fan=0.91, charger=0.08, cooker=0.01, dryer=0.00]
[DELTA EVENT] ON FAN slot confirmed by high-dryer axis | conf=0.91, dPabs=18029.7, dI=8.41, dH1=210.9
[AI ADAPTER] state=on raw=on sconf=1.00 abs_device=dryer dconf=0.92 event=ON active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=1.00 | DEVICE=dryer dconf=0.93 | I=773.32, Pabs=429214.8, H1=37639.4, THD=0.017 | state_probs[on=1.00, plugged_off=0.00, empty=0.00] | device_probs[dryer=0.93, cooker=0.07, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=1.00 abs_device=dryer dconf=0.93 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.93 | I=773.97, Pabs=431355.8, H1=37658.8, THD=0.017 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.93, cooker=0.07, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.93 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.93 | I=749.38, Pabs=404971.8, H1=38686.8, THD=0.021 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.93, cooker=0.07, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.93 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.93 | I=768.14, Pabs=445483.7, H1=37693.5, THD=0.016 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.93, cooker=0.07, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.93 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.93 | I=752.39, Pabs=414360.0, H1=39415.1, THD=0.023 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.93, cooker=0.07, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.93 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.99 | DEVICE=dryer dconf=0.92 | I=768.55, Pabs=430122.1, H1=37637.4, THD=0.015 | state_probs[on=0.99, plugged_off=0.01, empty=0.00] | device_probs[dryer=0.92, cooker=0.08, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=0.99 abs_device=dryer dconf=0.92 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=1.00 | DEVICE=dryer dconf=0.93 | I=757.60, Pabs=443037.7, H1=37737.6, THD=0.019 | state_probs[on=1.00, plugged_off=0.00, empty=0.00] | device_probs[dryer=0.93, cooker=0.07, charger=0.00, fan=0.00]
[AI ADAPTER] state=on raw=on sconf=1.00 abs_device=dryer dconf=0.93 event=None active=['COOKER_ON', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_ON + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.92 | DEVICE=dryer dconf=0.73 | I=21.65, Pabs=9470.9, H1=1011.7, THD=0.142 | state_probs[on=0.92, plugged_off=0.08, empty=0.00] | device_probs[cooker=0.73, dryer=0.19, charger=0.05, fan=0.03]
[DELTA EVENT] OFF COOKER slot=1 conf=0.90 | dPabs=-134413.4, dI=-247.00, dH1=-12674.6 | device_probs[dryer=0.83, cooker=0.16, fan=0.01, charger=0.00]
[AI ADAPTER] state=on raw=on sconf=0.92 abs_device=dryer dconf=0.73 event=OFF active=['COOKER_OFF', 'DRYER_ON', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_ON + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.92 | DEVICE=cooker dconf=0.74 | I=20.75, Pabs=8262.5, H1=979.6, THD=0.131 | state_probs[on=0.92, plugged_off=0.08, empty=0.00] | device_probs[cooker=0.74, dryer=0.17, charger=0.05, fan=0.03]
[ABS DEVICE GUARD] false DRYER moved OFF: cooker standby/off remains
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.92 abs_device=cooker dconf=0.74 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.92 | DEVICE=cooker dconf=0.75 | I=21.75, Pabs=9592.7, H1=1011.3, THD=0.122 | state_probs[on=0.92, plugged_off=0.08, empty=0.00] | device_probs[cooker=0.75, dryer=0.17, charger=0.05, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.92 abs_device=cooker dconf=0.75 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.91 | DEVICE=cooker dconf=0.75 | I=19.81, Pabs=8664.0, H1=939.8, THD=0.207 | state_probs[on=0.91, plugged_off=0.09, empty=0.00] | device_probs[cooker=0.75, dryer=0.17, charger=0.06, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.91 abs_device=cooker dconf=0.75 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.90 | DEVICE=cooker dconf=0.75 | I=22.00, Pabs=9306.1, H1=1021.2, THD=0.150 | state_probs[on=0.90, plugged_off=0.10, empty=0.00] | device_probs[cooker=0.75, dryer=0.17, charger=0.06, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.90 abs_device=cooker dconf=0.75 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.89 | DEVICE=cooker dconf=0.78 | I=20.20, Pabs=9038.0, H1=969.8, THD=0.145 | state_probs[on=0.89, plugged_off=0.11, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.06, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.89 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.88 | DEVICE=cooker dconf=0.78 | I=22.17, Pabs=9492.2, H1=1029.2, THD=0.132 | state_probs[on=0.88, plugged_off=0.12, empty=0.00] | device_probs[cooker=0.78, dryer=0.13, charger=0.06, fan=0.03]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.88 abs_device=cooker dconf=0.78 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_ON', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_ON
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.88 | DEVICE=cooker dconf=0.78 | I=19.46, Pabs=8517.1, H1=918.7, THD=0.127 | state_probs[on=0.88, plugged_off=0.12, empty=0.00] | device_probs[cooker=0.78, dryer=0.14, charger=0.05, fan=0.03]
[DELTA EVENT] OFF FAN slot=3 conf=0.57 | dPabs=-72373.2, dI=-123.32, dH1=-6144.3 | device_probs[cooker=0.57, fan=0.25, dryer=0.11, charger=0.07]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.88 abs_device=cooker dconf=0.78 event=OFF active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.88 | DEVICE=cooker dconf=0.80 | I=20.80, Pabs=8446.3, H1=990.5, THD=0.098 | state_probs[on=0.88, plugged_off=0.12, empty=0.00] | device_probs[cooker=0.80, dryer=0.11, charger=0.05, fan=0.04]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.88 abs_device=cooker dconf=0.80 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.70 | DEVICE=cooker dconf=0.56 | I=21.34, Pabs=8451.6, H1=977.8, THD=0.205 | state_probs[on=0.70, plugged_off=0.30, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.70 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.70 | DEVICE=cooker dconf=0.57 | I=20.24, Pabs=9116.1, H1=953.0, THD=0.119 | state_probs[on=0.70, plugged_off=0.30, empty=0.00] | device_probs[cooker=0.57, fan=0.28, charger=0.14, dryer=0.01]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.70 abs_device=cooker dconf=0.57 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.69 | DEVICE=cooker dconf=0.56 | I=20.43, Pabs=8395.3, H1=825.6, THD=0.088 | state_probs[on=0.69, plugged_off=0.31, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.69 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.70 | DEVICE=cooker dconf=0.56 | I=20.50, Pabs=9102.9, H1=966.6, THD=0.110 | state_probs[on=0.70, plugged_off=0.30, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.70 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.71 | DEVICE=cooker dconf=0.56 | I=22.02, Pabs=10040.4, H1=1048.9, THD=0.102 | state_probs[on=0.71, plugged_off=0.28, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.71 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.71 | DEVICE=cooker dconf=0.56 | I=21.02, Pabs=8674.8, H1=989.2, THD=0.136 | state_probs[on=0.71, plugged_off=0.29, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.71 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.71 | DEVICE=cooker dconf=0.56 | I=21.03, Pabs=9381.7, H1=973.5, THD=0.113 | state_probs[on=0.71, plugged_off=0.29, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.71 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.76 | DEVICE=cooker dconf=0.56 | I=20.88, Pabs=8867.0, H1=950.6, THD=0.147 | state_probs[on=0.76, plugged_off=0.24, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.14, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.76 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
[AI] STATE=on raw=on sconf=0.78 | DEVICE=cooker dconf=0.56 | I=19.99, Pabs=7998.4, H1=983.9, THD=0.087 | state_probs[on=0.78, plugged_off=0.22, empty=0.00] | device_probs[cooker=0.56, fan=0.30, charger=0.13, dryer=0.00]
[DELTA EVENT] COOKER marked OFF source=cooker_standby_absolute slot=1
[AI ADAPTER] state=on raw=on sconf=0.78 abs_device=cooker dconf=0.56 event=None active=['COOKER_OFF', 'DRYER_OFF', 'FAN_OFF', 'EMPTY'] display=🤖 AI: COOKER_OFF + DRYER_OFF + FAN_OFF
/home/wattsup/Project/minungnung/RaspberryPi/dashboard_ui.py:145: UserWarning: Glyph 129302 (\N{ROBOT FACE}) missing from font(s) DejaVu Sans.
  plt.show()
SPI 포트가 안전하게 닫혔습니다.

[LOG] README.md 저장 완료: /home/wattsup/Project/minungnung/RaspberryPi/README.md

```

- 종료 시간: 2026-05-19 23:56:03
