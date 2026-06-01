#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mobile_ui.py
============
핸드폰 브라우저에서 자체 제작 4구 멀티탭의 각 소켓을 ON/OFF 하기 위한 Flask 웹서버.

같은 WiFi 의 핸드폰 브라우저에서 http://<라즈베리파이IP>:5000 접속.
백그라운드 daemon thread 로 실행되어 NILM 메인 흐름(matplotlib UI) 을 막지 않는다.

엔드포인트:
    GET  /                       모바일 토글 UI (HTML)
    GET  /api/status             현재 4 소켓 상태 JSON
    POST /api/relay/<i>/on       소켓 i ON
    POST /api/relay/<i>/off      소켓 i OFF
    POST /api/relay/<i>/toggle   소켓 i 토글
    POST /api/rescan/<i>         소켓 i 수동 재추론 (릴레이 토글 → AI 재분류)

라즈베리파이 IP 확인: 시작 시 콘솔에 출력됨.
"""

import socket
import threading
import logging

try:
    from flask import Flask, jsonify, request
except ImportError as _e:
    raise ImportError(
        "Flask 가 필요합니다. 라즈베리파이에서 `pip install flask` 후 다시 실행하세요."
    ) from _e


PORT = 5000


# =====================================================================
# Flask 앱 빌더
# =====================================================================

INDEX_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
  <title>WattsUp Multi-Tap</title>
  <style>
    :root { color-scheme: dark; }
    * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
    body {
      margin: 0; padding: 16px;
      background: #1e1e1e; color: #eee;
      font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", system-ui, sans-serif;
    }
    h1 { font-size: 17px; margin: 0 0 4px; color: #ddd; }
    .sub { font-size: 12px; color: #888; margin-bottom: 16px; }
    .power-card {
      background: #2a2a2a; border: 1px solid #444; border-radius: 12px;
      padding: 14px 16px; margin-bottom: 16px;
    }
    .power-head { font-size: 11px; color: #888; letter-spacing: 1px; margin-bottom: 6px; }
    .power-main { font-size: 26px; font-weight: 700; color: #4caf50; }
    .power-sub {
      display: flex; gap: 14px; margin-top: 8px; font-size: 12px; color: #aaa;
      flex-wrap: wrap;
    }
    .power-sub b { color: #ddd; font-weight: 600; }
    .sockets { display: grid; gap: 12px; }
    .socket {
      display: flex; align-items: center; justify-content: space-between;
      padding: 14px 16px; border-radius: 12px;
      background: #2a2a2a; border: 1px solid #444;
      transition: background .15s, border-color .15s;
    }
    .socket.on { background: #1f3a1f; border-color: #4caf50; }
    .socket.pending { background: #3a3320; border-color: #d4a017; }
    .socket.deviceoff { background: #2a1f1f; border-color: #aa5050; }
    .socket-info { flex: 1; min-width: 0; }
    .label { font-size: 17px; font-weight: 600; }
    .device {
      font-size: 14px; color: #4caf50; margin-top: 4px;
      font-weight: 600;
    }
    .device.empty { color: #777; font-weight: 400; font-style: italic; }
    .state {
      font-size: 11px; color: #888; margin-top: 2px;
      letter-spacing: .5px;
    }
    .btn {
      padding: 14px 22px; border-radius: 10px; border: none;
      font-size: 14px; font-weight: 700; cursor: pointer; min-width: 76px;
      background: #444; color: #ccc;
      transition: background .15s;
    }
    .btn.on { background: #4caf50; color: #fff; }
    .btn:active { filter: brightness(.85); }
    .row { margin-top: 14px; display: flex; gap: 10px; }
    .row .btn { flex: 1; background: #333; }
    .socket-btns { display: flex; flex-direction: column; gap: 8px; align-items: stretch; }
    .btn.rescan {
      background: #2d3a4a; color: #9ec5ff; min-width: 84px;
      font-size: 12px; padding: 9px 12px; font-weight: 600;
      border: 1px solid #3d5570;
    }
    .btn.rescan:active { filter: brightness(1.25); }
    .toast {
      position: fixed; left: 16px; right: 16px; bottom: 16px;
      background: #333; color: #eee; border: 1px solid #555;
      border-radius: 10px; padding: 12px 16px; font-size: 13px; line-height: 1.4;
      opacity: 0; transform: translateY(8px); pointer-events: none;
      transition: opacity .2s, transform .2s; z-index: 10;
    }
    .toast.show { opacity: 1; transform: translateY(0); }
    .toast.ok  { border-color: #4caf50; }
    .toast.err { border-color: #c0504d; }
    .footer { margin-top: 22px; font-size: 11px; color: #555; text-align: center; }
  </style>
</head>
<body>
  <h1>WattsUp 멀티탭 원격 제어</h1>
  <div class="sub">tap 으로 토글 · 2초마다 자동 새로고침</div>

  <div class="power-card">
    <div class="power-head">실시간 전력 (총합)</div>
    <div class="power-main"><span id="p-main">--</span></div>
    <div class="power-sub">
      <span>Irms: <b id="p-irms">--</b> ADC</span>
      <span>H1: <b id="p-h1">--</b></span>
      <span>P_proxy: <b id="p-p">--</b></span>
    </div>
  </div>

  <div class="sockets" id="sockets"></div>
  <div class="row">
    <button class="btn" onclick="allOff()">모두 OFF</button>
    <button class="btn" onclick="refresh()">새로고침</button>
  </div>
  <div class="footer">NILM intelligent multi-tap</div>
  <div id="toast" class="toast"></div>

<script>
  const SOCKETS = [1, 2, 3, 4];
  let busy = false;

  function fmt(n, digits) {
    if (n === null || n === undefined || isNaN(n)) return '--';
    return Number(n).toFixed(digits === undefined ? 1 : digits);
  }

  function stateClass(st) {
    if (st === 'ASSIGNED') return 'on';
    if (st === 'PENDING')  return 'pending';
    if (st === 'DEVICE_OFF') return 'deviceoff';
    return '';
  }

  function stateLabel(st, relayOn) {
    if (st) return st;
    return relayOn ? 'ON' : 'OFF';
  }

  async function refresh() {
    try {
      const r = await fetch('/api/status').then(x => x.json());

      // 실시간 전력
      const pw = r.power || {};
      document.getElementById('p-main').textContent = fmt(pw.irms_adc, 1) + ' ADC';
      document.getElementById('p-irms').textContent = fmt(pw.irms_adc, 1);
      document.getElementById('p-h1').textContent   = fmt(pw.h1_mag, 0);
      document.getElementById('p-p').textContent    = fmt(pw.p_proxy, 0);

      // 소켓별 정보
      const sockets = r.sockets || {};
      const relayState = r.state || {};
      const root = document.getElementById('sockets');
      root.innerHTML = '';
      for (const i of SOCKETS) {
        const info = sockets[i] || {};
        const relayOn = !!relayState[i];
        const sc = stateClass(info.state);
        const el = document.createElement('div');
        el.className = 'socket' + (sc ? ' ' + sc : (relayOn ? ' on' : ''));
        const devText = info.device
          ? `<div class="device">${info.device}</div>`
          : `<div class="device empty">기기 없음</div>`;
        el.innerHTML = `
          <div class="socket-info">
            <div class="label">소켓 ${i}</div>
            ${devText}
            <div class="state">${stateLabel(info.state, relayOn)}</div>
          </div>
          <div class="socket-btns">
            <button class="btn ${relayOn ? 'on' : ''}" onclick="toggle(${i})">
              ${relayOn ? 'ON' : 'OFF'}
            </button>
            <button class="btn rescan" onclick="rescan(${i})">🔄 재스캔</button>
          </div>
        `;
        root.appendChild(el);
      }
    } catch (e) {
      console.warn('refresh fail', e);
    }
  }

  async function toggle(i) {
    if (busy) return;
    busy = true;
    try {
      await fetch('/api/relay/' + i + '/toggle', { method: 'POST' });
      await refresh();
    } finally { busy = false; }
  }

  async function allOff() {
    if (busy) return;
    busy = true;
    try {
      for (const i of SOCKETS) {
        await fetch('/api/relay/' + i + '/off', { method: 'POST' });
      }
      await refresh();
    } finally { busy = false; }
  }

  async function rescan(i) {
    if (busy) return;
    busy = true;
    showToast(`소켓 ${i} 재스캔 중… (릴레이 토글 측정, 몇 초 걸립니다)`);
    try {
      const r = await fetch('/api/rescan/' + i, { method: 'POST' }).then(x => x.json());
      const res = r.result || {};
      showToast(res.msg || (res.ok ? '재스캔 완료' : '재스캔 실패'), !!res.ok);
      await refresh();
    } catch (e) {
      showToast('재스캔 오류: ' + e, false);
    } finally { busy = false; }
  }

  let toastTimer = null;
  function showToast(msg, ok) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast show' + (ok === true ? ' ok' : (ok === false ? ' err' : ''));
    if (toastTimer) { clearTimeout(toastTimer); toastTimer = null; }
    // 결과 메시지(ok 지정)는 6초 후 사라지고, 진행중 메시지(ok 미지정)는 유지
    if (ok !== undefined) toastTimer = setTimeout(() => { t.className = 'toast'; }, 6000);
  }

  refresh();
  // 재스캔/토글 진행 중(busy)에는 자동 새로고침을 건너뛴다 (토스트·요청 충돌 방지).
  setInterval(() => { if (!busy) refresh(); }, 2000);
</script>
</body>
</html>
"""


def _read_power(engine):
    """엔진의 가장 최근 win_feat 에서 실시간 전력 지표 추출.

    win_feat 은 10-frame sliding window 평균이라 모바일 표시에 적당히 안정적.
    engine 미주입 또는 win_feat 아직 없으면 None 들 반환.
    """
    if engine is None:
        return {"irms_adc": None, "h1_mag": None, "p_proxy": None}
    try:
        wf = getattr(engine, "_latest_win_feat", None)
        if wf:
            return {
                "irms_adc": float(wf.get("Irms_adc_mean", 0.0)),
                "h1_mag":   float(wf.get("H1_60_mag_mean", 0.0)),
                "p_proxy":  float(wf.get("P_proxy_mean", 0.0)),
            }
        # win_feat 아직 없으면 baseline 사용 (시작 직후 idle 표시)
        return {
            "irms_adc": float(getattr(engine, "baseline_irms", 0.0)),
            "h1_mag":   float(getattr(engine, "baseline_h1", 0.0)),
            "p_proxy":  None,
        }
    except Exception:  # noqa: BLE001
        return {"irms_adc": None, "h1_mag": None, "p_proxy": None}


def _read_sockets(orchestrator):
    """orchestrator 의 물리 socket 상태 + device 매핑.

    orchestrator 미주입 시 None.
    """
    if orchestrator is None:
        return None
    try:
        return orchestrator.get_socket_status()
    except Exception:  # noqa: BLE001
        return None


def create_app(relay, engine=None, orchestrator=None):
    app = Flask(__name__)

    # 로그 노이즈 감소 (요청 로그 INFO 가 NILM 디버그 로그와 섞이는 것 방지)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    @app.route("/")
    def index():
        return INDEX_HTML

    @app.route("/api/status", methods=["GET"])
    def status():
        return jsonify(
            state=relay.get_state(),
            sockets=_read_sockets(orchestrator),
            power=_read_power(engine),
        )

    @app.route("/api/relay/<int:idx>/<string:action>", methods=["POST"])
    def relay_ctrl(idx, action):
        try:
            if action == "on":
                relay.set(idx, True)
            elif action == "off":
                relay.set(idx, False)
            elif action == "toggle":
                relay.toggle(idx)
            else:
                return jsonify(error=f"unknown action: {action}"), 400
        except ValueError as e:
            return jsonify(error=str(e)), 404

        # v65: orchestrator socket_state 동기화. mobile UI 토글이 단순 GPIO 만 바꾸면
        # orchestrator 가 DEVICE_OFF 그대로 인식 → 사용자가 그 socket 에 새 기기 꽂아도
        # candidates 에서 제외돼서 식별 실패. on_external_relay_change 가 relay 실제 상태
        # 읽어서 state 전이 (DEVICE_OFF↔PENDING 등) 적용.
        if orchestrator is not None:
            try:
                orchestrator.on_external_relay_change(idx)
            except Exception as e:  # noqa: BLE001
                logging.warning(f"[MOBILE UI] orchestrator sync 실패: {e}")

        return jsonify(
            state=relay.get_state(),
            sockets=_read_sockets(orchestrator),
            power=_read_power(engine),
        )

    @app.route("/api/rescan/<int:idx>", methods=["POST"])
    def rescan(idx):
        """소켓 idx 수동 재추론: orchestrator.rescan_socket() 호출 → 결과 + 갱신 상태 반환."""
        if orchestrator is None:
            return jsonify(result={
                "ok": False, "socket": idx, "msg": "orchestrator 미연결 (재스캔 불가)"
            })
        try:
            res = orchestrator.rescan_socket(idx)
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[MOBILE UI] rescan({idx}) 실패: {e}")
            res = {"ok": False, "socket": idx, "msg": f"재스캔 오류: {e}"}
        return jsonify(
            result=res,
            state=relay.get_state(),
            sockets=_read_sockets(orchestrator),
            power=_read_power(engine),
        )

    return app


# =====================================================================
# 백그라운드 실행
# =====================================================================

def _get_local_ip() -> str:
    """라즈베리파이의 LAN IP 추정 (외부 도달성 없으면 hostname 으로 fallback)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "0.0.0.0"


def start_in_background(relay, engine=None, orchestrator=None,
                        port: int = PORT) -> threading.Thread:
    """Flask 서버를 daemon thread 로 시작. NILM 메인 흐름은 그대로 진행.

    engine / orchestrator 를 같이 넘기면 모바일 UI 에 실시간 전력 + 소켓별 기기 정보
    표시. 둘 다 옵션이라 미주입 시 기존 단순 토글 UI 와 동일하게 동작 (state 만 표시).
    """
    app = create_app(relay, engine=engine, orchestrator=orchestrator)
    ip = _get_local_ip()

    def _run():
        try:
            from werkzeug.serving import make_server
            srv = make_server("0.0.0.0", port, app, threaded=True)
            logging.info(f"[MOBILE UI] serving on http://0.0.0.0:{port}")
            srv.serve_forever()
        except Exception as e:  # noqa: BLE001
            logging.error(f"[MOBILE UI] server error: {e}")

    t = threading.Thread(target=_run, daemon=True, name="mobile_ui")
    t.start()

    print("=" * 60)
    print(f"  📱  Mobile UI: http://{ip}:{port}")
    print("       (같은 WiFi 의 핸드폰 브라우저에서 위 주소 접속)")
    print("=" * 60)
    return t


# =====================================================================
# 단독 실행 (relay 없이 UI 만 테스트 - Mock relay 로 띄움)
# =====================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    from relay_controller import RelayController
    r = RelayController()
    app = create_app(r)
    ip = _get_local_ip()
    print(f"Mobile UI standalone test: http://{ip}:{PORT}")
    try:
        app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
    finally:
        r.close()
