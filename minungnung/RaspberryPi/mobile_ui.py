#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mobile_ui.py
============
라즈베리파이 시연 화면과 같은 status를 모바일에서 보여주는 Flask UI.

핵심 원칙
---------
- NILM 판단/소켓 분류/relay-probe 로직은 건드리지 않는다.
- ai_extension_v3.py의 process_ai_frame()이 만든 최신 status를 그대로 읽는다.
- 따라서 라즈베리파이 화면의 sockets/device/state/power_w와 모바일 UI가 같은 값을 본다.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, Optional

try:
    from flask import Flask, jsonify, request
except Exception as e:  # pragma: no cover
    Flask = None
    jsonify = None
    request = None
    _FLASK_IMPORT_ERROR = e
else:
    _FLASK_IMPORT_ERROR = None

_APP_THREAD = None
_APP = None


def _safe_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return float(default)


def _relay_state(relay) -> Dict[int, bool]:
    try:
        st = relay.get_state()
        return {int(k): bool(v) for k, v in st.items()}
    except Exception:
        return {1: False, 2: False, 3: False, 4: False}


def _latest_engine_status(ai_engine) -> Dict[str, Any]:
    """ai_extension_v3.py가 라즈베리파이 화면에 넘긴 최신 status를 읽는다."""
    status = getattr(ai_engine, "_latest_status", None)
    if isinstance(status, dict):
        return status

    # fallback: 아직 라즈베리파이 화면 update_frame이 한 번도 안 돈 경우.
    sockets = []
    for sk in getattr(ai_engine, "sockets", []) or []:
        try:
            sockets.append(sk.to_dict())
        except Exception:
            pass
    wf = getattr(ai_engine, "_latest_win_feat", {}) or {}
    return {
        "frame_count": getattr(ai_engine, "frame_count", 0),
        "event": "INIT",
        "win_feat": wf,
        "baseline_irms": getattr(ai_engine, "baseline_irms", 0.0),
        "baseline_h1": getattr(ai_engine, "baseline_h1", 0.0),
        "sockets": sockets,
        "active_devices": dict(getattr(ai_engine, "active_devices", {}) or {}),
        "event_cooldown": getattr(ai_engine, "event_cooldown", 0),
        "pending_on": getattr(ai_engine, "pending_on", None) is not None,
        "fs_actual": getattr(ai_engine, "_last_fs", 0.0),
        "total_live_power_w": sum(_safe_float(s.get("power_w")) for s in sockets),
    }


def _normalize_status(relay=None, ai_engine=None, orchestrator=None) -> Dict[str, Any]:
    status = _latest_engine_status(ai_engine) if ai_engine is not None else {}
    sockets_raw = status.get("sockets", []) or []
    relay_st = _relay_state(relay) if relay is not None else {1: False, 2: False, 3: False, 4: False}

    sockets = []
    total_power = 0.0
    for i in range(1, 5):
        raw = None
        for s in sockets_raw:
            try:
                if int(s.get("idx", 0)) == i:
                    raw = s
                    break
            except Exception:
                pass
        if raw is None:
            raw = {"idx": i, "state": "EMPTY", "device": None, "power_w": 0.0}

        state = str(raw.get("state") or "EMPTY")
        dev = raw.get("device") or ""
        power_w = _safe_float(raw.get("power_w", raw.get("live_power_w", 0.0)))
        if state != "DEVICE_ON":
            power_w = 0.0
        total_power += power_w

        sockets.append({
            "idx": i,
            "state": state,
            "device": dev,
            "power_w": round(power_w, 1),
            "live_power_w": round(_safe_float(raw.get("live_power_w", power_w)), 1),
            "fixed_power_w": round(_safe_float(raw.get("fixed_power_w", 0.0)), 1),
            "relay_on": bool(relay_st.get(i, False)),
        })

    wf = status.get("win_feat") or {}
    return {
        "ok": True,
        "ts": time.time(),
        "frame_count": int(status.get("frame_count", 0) or 0),
        "event": str(status.get("event", "")),
        "event_cooldown": int(status.get("event_cooldown", 0) or 0),
        "pending_on": bool(status.get("pending_on", False)),
        "fs_actual": _safe_float(status.get("fs_actual", 0.0)),
        "baseline_irms": round(_safe_float(status.get("baseline_irms", 0.0)), 2),
        "baseline_h1": round(_safe_float(status.get("baseline_h1", 0.0)), 2),
        "irms": round(_safe_float(wf.get("Irms_adc_mean", 0.0)), 2),
        "h1": round(_safe_float(wf.get("H1_60_mag_mean", 0.0)), 2),
        "h3": round(_safe_float(wf.get("H3_180_mag_mean", 0.0)), 2),
        "thd": round(_safe_float(wf.get("THD_i_mean", 0.0)), 4),
        "total_power_w": round(_safe_float(status.get("total_live_power_w", total_power)), 1),
        "sockets": sockets,
        "active_devices": status.get("active_devices", {}) or {},
    }


HTML = r"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>WattsUp NILM Monitor</title>
  <style>
    :root { --bg:#111827; --card:#1f2937; --line:#374151; --on:#10b981; --off:#f97316; --empty:#4b5563; --text:#f9fafb; --muted:#9ca3af; --accent:#facc15; }
    * { box-sizing:border-box; }
    body { margin:0; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:var(--bg); color:var(--text); }
    .wrap { max-width: 980px; margin:0 auto; padding:16px; }
    h1 { font-size:22px; margin:0 0 12px; }
    .summary { display:grid; grid-template-columns: repeat(2, 1fr); gap:10px; margin-bottom:12px; }
    .metric { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:12px; }
    .metric .label { color:var(--muted); font-size:12px; }
    .metric .value { font-size:24px; font-weight:800; margin-top:4px; }
    .grid { display:grid; grid-template-columns: repeat(2, 1fr); gap:12px; }
    .socket { border:2px solid var(--line); border-radius:18px; padding:14px; min-height:148px; background:var(--card); }
    .socket.on { border-color:var(--on); box-shadow:0 0 0 1px rgba(16,185,129,.2); }
    .socket.off { border-color:var(--off); }
    .socket.pending { border-color:#38bdf8; }
    .socket.empty { border-color:var(--empty); opacity:.85; }
    .top { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
    .num { font-size:15px; color:var(--muted); font-weight:700; }
    .badge { font-size:12px; padding:4px 8px; border-radius:999px; background:#374151; color:white; }
    .badge.on { background:var(--on); color:#06281d; }
    .badge.off { background:var(--off); color:#2b1202; }
    .badge.pending { background:#38bdf8; color:#082f49; }
    .device { font-size:23px; font-weight:900; min-height:31px; margin-top:6px; }
    .power { color:var(--accent); font-size:30px; font-weight:900; margin-top:8px; }
    .sub { color:var(--muted); font-size:12px; margin-top:6px; }
    button { width:100%; border:0; border-radius:14px; padding:13px 12px; margin:12px 0; font-size:16px; font-weight:800; background:#2563eb; color:white; }
    .small { color:var(--muted); font-size:12px; line-height:1.5; }
    @media (min-width: 760px) { .summary { grid-template-columns: repeat(4,1fr); } .grid { grid-template-columns: repeat(4,1fr); } }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>WattsUp NILM Monitor</h1>
    <div class="summary">
      <div class="metric"><div class="label">전체 실시간 전력</div><div class="value"><span id="total">0</span> W</div></div>
      <div class="metric"><div class="label">Irms</div><div class="value"><span id="irms">0</span></div></div>
      <div class="metric"><div class="label">H1</div><div class="value"><span id="h1">0</span></div></div>
      <div class="metric"><div class="label">THD</div><div class="value"><span id="thd">0</span></div></div>
    </div>
    <button onclick="prepareSockets()">소켓 준비(PENDING)</button>
    <div class="grid" id="sockets"></div>
    <p class="small" id="info"></p>
  </div>
<script>
function cls(st){ if(st==='DEVICE_ON') return 'on'; if(st==='DEVICE_OFF') return 'off'; if(st==='PENDING') return 'pending'; return 'empty'; }
function label(st){ if(st==='DEVICE_ON') return 'ON'; if(st==='DEVICE_OFF') return 'OFF'; if(st==='PENDING') return 'PENDING'; return 'EMPTY'; }
async function load(){
  try{
    const r = await fetch('/api/status', {cache:'no-store'});
    const d = await r.json();
    document.getElementById('total').textContent = Number(d.total_power_w||0).toFixed(1);
    document.getElementById('irms').textContent = Number(d.irms||0).toFixed(1);
    document.getElementById('h1').textContent = Number(d.h1||0).toFixed(0);
    document.getElementById('thd').textContent = Number(d.thd||0).toFixed(3);
    const box = document.getElementById('sockets');
    box.innerHTML = '';
    (d.sockets||[]).forEach(s=>{
      const c = cls(s.state);
      const dev = s.device ? String(s.device).toUpperCase() : '-';
      const p = Number(s.power_w||0).toFixed(1);
      const div = document.createElement('div');
      div.className = 'socket ' + c;
      div.innerHTML = `<div class="top"><div class="num">Socket ${s.idx}</div><div class="badge ${c}">${label(s.state)}</div></div>
        <div class="device">${dev}</div>
        <div class="power">${p} W</div>
        <div class="sub">Relay: ${s.relay_on ? 'ON' : 'OFF'} / live sensor display</div>`;
      box.appendChild(div);
    });
    document.getElementById('info').textContent = `frame ${d.frame_count} / event ${d.event} / cooldown ${d.event_cooldown} / pending ${d.pending_on}`;
  }catch(e){ console.log(e); }
}
async function prepareSockets(){ await fetch('/api/prepare', {method:'POST'}); setTimeout(load, 300); }
setInterval(load, 700); load();
</script>
</body>
</html>
"""


def create_app(relay=None, ai_engine=None, orchestrator=None):
    if Flask is None:
        raise RuntimeError(f"Flask import failed: {_FLASK_IMPORT_ERROR}")
    app = Flask(__name__)

    @app.route("/")
    def index():
        return HTML

    @app.route("/api/status")
    def api_status():
        return jsonify(_normalize_status(relay=relay, ai_engine=ai_engine, orchestrator=orchestrator))

    @app.route("/api/prepare", methods=["POST"])
    def api_prepare():
        if orchestrator is None or not hasattr(orchestrator, "on_touch"):
            return jsonify({"ok": False, "error": "orchestrator.on_touch unavailable"}), 400
        try:
            activated = orchestrator.on_touch()
            return jsonify({"ok": True, "activated": activated})
        except Exception as e:
            logging.exception("mobile prepare failed")
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/relay/<int:idx>/<action>", methods=["POST"])
    def api_relay(idx, action):
        if relay is None:
            return jsonify({"ok": False, "error": "relay unavailable"}), 400
        try:
            if action == "on":
                relay.set(idx, True)
            elif action == "off":
                relay.set(idx, False)
            elif action == "toggle":
                st = _relay_state(relay).get(idx, False)
                relay.set(idx, not st)
            else:
                return jsonify({"ok": False, "error": "unknown action"}), 400
            return jsonify({"ok": True, "state": _relay_state(relay)})
        except Exception as e:
            logging.exception("mobile relay action failed")
            return jsonify({"ok": False, "error": str(e)}), 500

    return app


def start_in_background(relay=None, ai_engine=None, orchestrator=None, host="0.0.0.0", port=5000):
    global _APP_THREAD, _APP
    if _APP_THREAD is not None and _APP_THREAD.is_alive():
        return _APP_THREAD
    _APP = create_app(relay=relay, ai_engine=ai_engine, orchestrator=orchestrator)

    def run():
        logging.info(f"[MOBILE UI] serving on http://{host}:{port}")
        _APP.run(host=host, port=int(port), debug=False, use_reloader=False, threaded=True)

    _APP_THREAD = threading.Thread(target=run, daemon=True, name="mobile_ui")
    _APP_THREAD.start()
    return _APP_THREAD
