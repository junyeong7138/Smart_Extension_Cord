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
      background: #2a2a2a; border: 2px solid #888;   /* EMPTY = gray (모니터와 동일) */
      transition: background .15s, border-color .15s;
    }
    /* 소켓 state 색 — 모니터 UI 와 동일 (PENDING=파랑 / ON=초록 / OFF=주황 / EMPTY=회색) */
    .socket.on { background: #14331a; border-color: #00C853; }       /* ASSIGNED(device on) = green */
    .socket.pending { background: #14283d; border-color: #1976D2; }  /* PENDING = blue */
    .socket.deviceoff { background: #3a2a14; border-color: #FF8C00; }/* DEVICE_OFF = orange */
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
    .state .pend { color: #6ab0ff; font-weight: 700; letter-spacing: 0; }
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

    /* "Stabilizing" 팝업 (모니터 UI 의 StabilizingOverlay 와 동일 의미) */
    .stab-overlay {
      position: fixed; inset: 0; z-index: 50;
      background: rgba(0,0,0,.55);
      display: flex; align-items: center; justify-content: center;
      opacity: 0; pointer-events: none; transition: opacity .2s;
    }
    .stab-overlay.show { opacity: 1; pointer-events: auto; }
    .stab-card {
      background: #23272e; border: 2px solid #4caf50; border-radius: 16px;
      padding: 26px 30px; width: 80%; max-width: 360px; text-align: center;
      box-shadow: 0 8px 30px rgba(0,0,0,.55);
    }
    .stab-title { font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 14px; }
    .stab-pct { font-size: 30px; font-weight: 800; color: #4caf50; margin-bottom: 14px; }
    .stab-bar { height: 12px; background: #3a3f47; border-radius: 6px; overflow: hidden; }
    .stab-bar-fg {
      height: 100%; width: 0%; background: #4caf50; border-radius: 6px;
      transition: width .25s;
    }
    .stab-sub { margin-top: 12px; font-size: 12px; color: #aab2bd; }

    /* 타이머 버튼 + 소켓 카운트다운 */
    .btn.timer {
      background: #3a2d4a; color: #d6b3ff; min-width: 84px;
      font-size: 12px; padding: 9px 12px; font-weight: 600;
      border: 1px solid #5a3d70;
    }
    .btn.timer:active { filter: brightness(1.25); }
    .socket-timer {
      margin-top: 6px; font-size: 13px; color: #d6b3ff; font-weight: 600;
    }
    .socket-timer .tcancel {
      font-size: 11px; color: #aaa; border: 1px solid #555; border-radius: 6px;
      padding: 1px 7px; margin-left: 8px; cursor: pointer; font-weight: 500;
    }

    /* 타이머 설정 팝업 */
    .tpop {
      position: fixed; inset: 0; z-index: 60;
      background: rgba(0,0,0,.6);
      display: flex; align-items: center; justify-content: center;
      opacity: 0; pointer-events: none; transition: opacity .2s;
    }
    .tpop.show { opacity: 1; pointer-events: auto; }
    .tpop-card {
      background: #23272e; border: 2px solid #8a5cc0; border-radius: 16px;
      padding: 22px 22px 18px; width: 86%; max-width: 360px; text-align: center;
      box-shadow: 0 8px 30px rgba(0,0,0,.55);
    }
    .tpop-title { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 16px; }
    .tpop-screen { display: flex; flex-direction: column; gap: 12px; }
    .tbtn {
      padding: 14px; border-radius: 10px; border: none; font-size: 15px;
      font-weight: 700; cursor: pointer; background: #444; color: #eee;
    }
    .tbtn.on { background: #2e7d32; color: #fff; }
    .tbtn.off { background: #b23b3b; color: #fff; }
    .tbtn.ok { background: #8a5cc0; color: #fff; }
    .tbtn.ghost { background: #333; color: #bbb; }
    .tbtn:active { filter: brightness(.85); }
    /* 스크롤 시:분:초 picker */
    .picker-wrap { position: relative; margin: 6px 0 2px; }
    .picker { display: flex; justify-content: center; align-items: center; gap: 4px; }
    .pcol {
      height: 120px; width: 62px; overflow-y: scroll;
      scroll-snap-type: y mandatory; padding: 40px 0;
      -ms-overflow-style: none; scrollbar-width: none;
    }
    .pcol::-webkit-scrollbar { display: none; }
    .pitem {
      height: 40px; line-height: 40px; font-size: 26px; color: #ddd;
      scroll-snap-align: center; font-variant-numeric: tabular-nums;
    }
    .psep { font-size: 26px; color: #8a5cc0; font-weight: 700; }
    .picker-band {
      position: absolute; left: 0; right: 0; top: 40px; height: 40px;
      border-top: 1px solid #8a5cc0; border-bottom: 1px solid #8a5cc0;
      pointer-events: none;
    }
    .picker-cap { font-size: 11px; color: #888; letter-spacing: 6px; margin: 4px 0 12px; }
    .tpop-actions { display: flex; gap: 10px; margin-top: 6px; }
    .tpop-actions .tbtn { flex: 1; }
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

  <!-- 안정화 중(Stabilizing) 팝업: cooldown>0 동안 표시, 0 이 되면 사라짐 -->
  <div id="stab" class="stab-overlay">
    <div class="stab-card">
      <div class="stab-title">Stabilizing...</div>
      <div class="stab-pct" id="stab-pct">0%</div>
      <div class="stab-bar"><div class="stab-bar-fg" id="stab-bar-fg"></div></div>
      <div class="stab-sub">please wait</div>
    </div>
  </div>

  <!-- 타이머 설정 팝업: ON/OFF 선택 → 시:분:초 스크롤 → 취소/OK -->
  <div id="timer-pop" class="tpop">
    <div class="tpop-card">
      <div class="tpop-title" id="tpop-title">타이머</div>
      <!-- 1단계: ON/OFF 선택 -->
      <div id="tpop-choice" class="tpop-screen">
        <button class="tbtn on" onclick="chooseTimer('on')">ON timer</button>
        <button class="tbtn off" onclick="chooseTimer('off')">OFF timer</button>
        <button class="tbtn ghost" onclick="closeTimer()">닫기</button>
      </div>
      <!-- 2단계: 시:분:초 스크롤 picker -->
      <div id="tpop-picker" class="tpop-screen" style="display:none">
        <div class="picker-wrap">
          <div class="picker">
            <div class="pcol" id="pick-h"></div>
            <div class="psep">:</div>
            <div class="pcol" id="pick-m"></div>
            <div class="psep">:</div>
            <div class="pcol" id="pick-s"></div>
          </div>
          <div class="picker-band"></div>
        </div>
        <div class="picker-cap">시&nbsp;&nbsp;&nbsp;분&nbsp;&nbsp;&nbsp;초</div>
        <div class="tpop-actions">
          <button class="tbtn ghost" onclick="closeTimer()">취소</button>
          <button class="tbtn ok" onclick="confirmTimer()">OK</button>
        </div>
      </div>
    </div>
  </div>

<script>
  const SOCKETS = [1, 2, 3, 4];
  let busy = false;
  let stabPeak = 0;   // 현재 안정화 episode 의 cooldown 최댓값
  let lastCd = 0;     // 마지막으로 본 cooldown (적응형 새로고침 간격용)

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
    if (st === 'EMPTY') return 'OFF';   // 빈 소켓도 'OFF' 로 표기 (회색 유지)
    if (st) return st;
    return relayOn ? 'ON' : 'OFF';
  }

  // cooldown(안정화 카운터) → 팝업 표시/퍼센트/숨김.
  // cooldown 이 처음 보인 최댓값을 peak 로 잡고 percent=(1-cd/peak)*100,
  // cooldown 이 0 이 되면 100% 의미로 팝업을 숨긴다 (모니터 UI 와 동일).
  function updateStabilizing(cd) {
    cd = Number(cd) || 0;
    lastCd = cd;
    const box = document.getElementById('stab');
    if (cd <= 0) { box.classList.remove('show'); stabPeak = 0; return; }
    if (cd > stabPeak) stabPeak = cd;
    const pct = Math.max(0, Math.min(100, (1 - cd / Math.max(stabPeak, 1)) * 100));
    document.getElementById('stab-pct').textContent = Math.round(pct) + '%';
    document.getElementById('stab-bar-fg').style.width = pct + '%';
    box.classList.add('show');
  }

  async function refresh() {
    try {
      const r = await fetch('/api/status').then(x => x.json());

      // 안정화 중 팝업 (cooldown)
      updateStabilizing(r.cooldown);

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
            <div class="state">${stateLabel(info.state, relayOn)}<span class="pend" id="pend-${i}"></span></div>
            <div class="socket-timer" id="stimer-${i}"></div>
          </div>
          <div class="socket-btns">
            <button class="btn ${relayOn ? 'on' : ''}" onclick="toggle(${i})">
              ${relayOn ? 'ON' : 'OFF'}
            </button>
            <button class="btn rescan" onclick="rescan(${i})">🔄 재스캔</button>
            <button class="btn timer" onclick="openTimer(${i})">⏱ 타이머</button>
          </div>
        `;
        root.appendChild(el);
      }
      applyTimers(r.timers);
      applyPending(r.sockets);
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

  // ===================== 타이머 =====================
  const PICK_ITEM_H = 40;            // .pitem 높이(px) — CSS 와 일치해야 함
  let timerSk = null, timerAction = 'off';
  let timerDeadlines = {};           // sk -> {action, deadline(ms)} (부드러운 카운트다운용)
  let pendingDeadlines = {};         // sk -> deadline(ms) (PENDING 30s 카운트다운)

  function fmtHMS(sec) {
    sec = Math.max(0, Math.floor(sec));
    const p = (n) => String(n).padStart(2, '0');
    return p(Math.floor(sec / 3600)) + ':' + p(Math.floor((sec % 3600) / 60)) + ':' + p(sec % 60);
  }

  function openTimer(i) {
    timerSk = i;
    document.getElementById('tpop-title').textContent = '소켓 ' + i + ' 타이머';
    document.getElementById('tpop-choice').style.display = 'flex';
    document.getElementById('tpop-picker').style.display = 'none';
    document.getElementById('timer-pop').classList.add('show');
  }
  function closeTimer() {
    document.getElementById('timer-pop').classList.remove('show');
    timerSk = null;
  }
  function chooseTimer(action) {
    timerAction = action;
    document.getElementById('tpop-title').textContent =
      '소켓 ' + timerSk + ' · ' + (action === 'on' ? 'ON' : 'OFF') + ' timer';
    document.getElementById('tpop-choice').style.display = 'none';
    document.getElementById('tpop-picker').style.display = 'flex';
    buildPicker();
  }
  function fillCol(id, n) {
    const col = document.getElementById(id);
    col.innerHTML = '';
    for (let v = 0; v < n; v++) {
      const d = document.createElement('div');
      d.className = 'pitem';
      d.textContent = String(v).padStart(2, '0');
      col.appendChild(d);
    }
  }
  function buildPicker() {
    fillCol('pick-h', 24);
    fillCol('pick-m', 60);
    fillCol('pick-s', 60);
    // 00:00:00 으로 초기화 (col 이 보인 뒤 scrollTop 적용)
    setTimeout(() => {
      ['pick-h', 'pick-m', 'pick-s'].forEach(id => { document.getElementById(id).scrollTop = 0; });
    }, 0);
  }
  function readCol(id) {
    return Math.round(document.getElementById(id).scrollTop / PICK_ITEM_H);
  }
  async function confirmTimer() {
    const seconds = readCol('pick-h') * 3600 + readCol('pick-m') * 60 + readCol('pick-s');
    const sk = timerSk, action = timerAction;
    closeTimer();
    if (seconds <= 0) { showToast('시간이 00:00:00 이라 타이머를 설정하지 않았습니다.', false); return; }
    try {
      const r = await fetch('/api/timer/' + sk, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, seconds })
      }).then(x => x.json());
      if (r && r.timers) applyTimers(r.timers);
      showToast('소켓 ' + sk + ' ' + action.toUpperCase() + ' 타이머 ' + fmtHMS(seconds) + ' 설정', true);
      await refresh();
    } catch (e) { showToast('타이머 오류: ' + e, false); }
  }
  async function cancelTimer(sk) {
    try {
      const r = await fetch('/api/timer/' + sk + '/cancel', { method: 'POST' }).then(x => x.json());
      if (r && r.timers) applyTimers(r.timers);
      showToast('소켓 ' + sk + ' 타이머 취소', true);
      await refresh();
    } catch (e) { showToast('취소 오류: ' + e, false); }
  }
  // 서버 timers(remaining 초) → 클라이언트 deadline 으로 재동기. 1초 단위 부드러운 카운트다운.
  function applyTimers(timers) {
    timers = timers || {};
    const seen = {};
    for (const k in timers) {
      seen[k] = 1;
      timerDeadlines[k] = { action: timers[k].action, deadline: Date.now() + (timers[k].remaining * 1000) };
    }
    for (const k in timerDeadlines) { if (!seen[k]) delete timerDeadlines[k]; }
    tickTimers();
  }
  function tickTimers() {
    const now = Date.now();
    for (const i of SOCKETS) {
      const el = document.getElementById('stimer-' + i);
      if (!el) continue;
      const t = timerDeadlines[i];
      if (!t) { el.innerHTML = ''; continue; }
      const rem = Math.max(0, Math.round((t.deadline - now) / 1000));
      el.innerHTML = '⏱ ' + (t.action === 'on' ? 'ON' : 'OFF') + ' in ' + fmtHMS(rem) +
        ' <span class="tcancel" onclick="cancelTimer(' + i + ')">취소</span>';
    }
  }

  // PENDING 30s 카운트다운 (state 'PENDING' 옆에 표시). 서버 pending_remaining → deadline 동기.
  function applyPending(sockets) {
    sockets = sockets || {};
    const seen = {};
    for (const i of SOCKETS) {
      const info = sockets[i] || {};
      if (info.state === 'PENDING' && info.pending_remaining != null) {
        seen[i] = 1;
        pendingDeadlines[i] = Date.now() + info.pending_remaining * 1000;
      }
    }
    for (const k in pendingDeadlines) { if (!seen[k]) delete pendingDeadlines[k]; }
    tickPending();
  }
  function tickPending() {
    const now = Date.now();
    for (const i of SOCKETS) {
      const el = document.getElementById('pend-' + i);
      if (!el) continue;
      const dl = pendingDeadlines[i];
      if (dl == null) { el.textContent = ''; continue; }
      const rem = Math.max(0, Math.round((dl - now) / 1000));
      el.textContent = ' · ' + rem + 's';
    }
  }
  setInterval(() => { tickTimers(); tickPending(); }, 1000);

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
  // 적응형 새로고침: 안정화 중(cooldown>0)이면 0.4s 로 빠르게(팝업 % 부드럽게),
  // 평상시엔 2s. 재스캔/토글 진행 중(busy)엔 건너뛴다 (토스트·요청 충돌 방지).
  function scheduleNext() {
    // 안정화 중(cooldown>0) 또는 PENDING 카운트다운 중이면 0.4s 로 빠르게.
    const fast = lastCd > 0 || Object.keys(pendingDeadlines).length > 0;
    setTimeout(async () => {
      if (!busy) { await refresh(); }
      scheduleNext();
    }, fast ? 400 : 2000);
  }
  scheduleNext();
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


def _read_cooldown(engine):
    """엔진의 현재 event_cooldown (안정화 중 프레임 카운터). 0 이면 정상 판별 상태.

    모바일 '안정화 중(Stabilizing)' 팝업이 cooldown>0 동안 0~100% 진행률을 표시한다
    (모니터 UI 의 StabilizingOverlay 와 동일 의미). engine 미주입이면 0.
    """
    if engine is None:
        return 0
    try:
        return int(getattr(engine, "event_cooldown", 0) or 0)
    except Exception:  # noqa: BLE001
        return 0


def _read_timers(timer_manager):
    """{sk: {"action","remaining","duration"}} — 소켓별 예약 타이머 남은 시간(초).

    timer_manager 미주입이면 빈 dict.
    """
    if timer_manager is None:
        return {}
    try:
        return timer_manager.get_timers()
    except Exception:  # noqa: BLE001
        return {}


def create_app(relay, engine=None, orchestrator=None, timer_manager=None):
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
            cooldown=_read_cooldown(engine),
            timers=_read_timers(timer_manager),
        )

    @app.route("/api/timer/<int:idx>", methods=["POST"])
    def timer_set(idx):
        """소켓 idx 에 ON/OFF 예약 설정. body: {action:"on"/"off", seconds:int}."""
        if timer_manager is None:
            return jsonify(ok=False, msg="timer 미연결")
        data = request.get_json(silent=True) or {}
        action = data.get("action", "off")
        try:
            seconds = int(data.get("seconds", 0))
        except (TypeError, ValueError):
            seconds = 0
        try:
            set_ok = timer_manager.set_timer(idx, action, seconds)
            msg = (f"소켓{idx} {str(action).upper()} 타이머 설정"
                   if set_ok else f"소켓{idx} 타이머 취소(0초)")
        except Exception as e:  # noqa: BLE001
            logging.warning(f"[MOBILE UI] timer_set({idx}) 실패: {e}")
            return jsonify(ok=False, msg=f"타이머 오류: {e}")
        return jsonify(ok=True, msg=msg, timers=_read_timers(timer_manager))

    @app.route("/api/timer/<int:idx>/cancel", methods=["POST"])
    def timer_cancel(idx):
        """소켓 idx 예약 타이머 취소."""
        if timer_manager is None:
            return jsonify(ok=False, msg="timer 미연결")
        timer_manager.cancel_timer(idx)
        return jsonify(ok=True, msg=f"소켓{idx} 타이머 취소",
                       timers=_read_timers(timer_manager))

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
            cooldown=_read_cooldown(engine),
            timers=_read_timers(timer_manager),
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
            cooldown=_read_cooldown(engine),
            timers=_read_timers(timer_manager),
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
                        timer_manager=None, port: int = PORT) -> threading.Thread:
    """Flask 서버를 daemon thread 로 시작. NILM 메인 흐름은 그대로 진행.

    engine / orchestrator 를 같이 넘기면 모바일 UI 에 실시간 전력 + 소켓별 기기 정보
    표시. timer_manager 를 넘기면 소켓별 ON/OFF 예약 타이머 기능 활성화.
    셋 다 옵션이라 미주입 시 기존 단순 토글 UI 와 동일하게 동작.
    """
    app = create_app(relay, engine=engine, orchestrator=orchestrator,
                     timer_manager=timer_manager)
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
