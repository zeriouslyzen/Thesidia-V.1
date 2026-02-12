/**
 * Thesidia Mini-Chat Widget
 * ==========================
 * Self-contained floating assistant for platform-wide embedding.
 * FAB button -> expandable drawer with compact message thread.
 * Communicates with the same /api/thesidia endpoint.
 */

(function () {
  'use strict';

  const API_URL = '/api/thesidia';
  let isOpen = false;
  let isProcessing = false;
  let messages = [];
  let container = null;

  function init() {
    // Don't inject on pages that already have the full chat (#thesidia-app)
    if (document.getElementById('thesidia-app')) return;

    // Create container
    container = document.createElement('div');
    container.id = 'thesidia-mini';
    container.innerHTML = buildHTML();
    document.body.appendChild(container);

    // Load CSS if not already present
    if (!document.querySelector('link[href*="thesidia-mini.css"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = '/css/thesidia-mini.css';
      document.head.appendChild(link);
    }
    if (!document.querySelector('link[href*="tokens.css"]')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = '/css/tokens.css';
      document.head.appendChild(link);
    }

    // Bind events
    bindEvents();
  }

  function buildHTML() {
    return `
      <button class="th-mini-fab" id="thMminiFab" aria-label="Open Thesidia" title="Ask Thesidia">/</button>
      <div class="th-mini-drawer" id="thMiniDrawer">
        <div class="th-mini-header">
          <span class="th-mini-brand"><span class="th-slash">/</span>thesidia</span>
          <div class="th-mini-actions">
            <button class="th-mini-btn" id="thMiniOpen" title="Open full chat">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </button>
            <button class="th-mini-btn" id="thMiniClose" title="Close">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>
        <div class="th-mini-messages" id="thMiniMessages"></div>
        <div class="th-mini-typing" id="thMiniTyping">
          <span></span><span></span><span></span>
        </div>
        <div class="th-mini-prompt">
          <div class="th-mini-prompt-row">
            <textarea class="th-mini-input" id="thMiniInput" placeholder="Ask anything..." rows="1"></textarea>
            <button class="th-mini-send" id="thMiniSend" aria-label="Send">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  function bindEvents() {
    const fab = document.getElementById('thMminiFab');
    const drawer = document.getElementById('thMiniDrawer');
    const closeBtn = document.getElementById('thMiniClose');
    const openBtn = document.getElementById('thMiniOpen');
    const input = document.getElementById('thMiniInput');
    const sendBtn = document.getElementById('thMiniSend');

    if (fab) fab.addEventListener('click', toggle);
    if (closeBtn) closeBtn.addEventListener('click', close);
    if (openBtn) openBtn.addEventListener('click', () => {
      window.location.href = '/';  // Navigate to full chat
    });

    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          send();
        }
      });
      input.addEventListener('input', () => {
        sendBtn.classList.toggle('ready', input.value.trim().length > 0);
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 80) + 'px';
      });
    }

    if (sendBtn) sendBtn.addEventListener('click', send);

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (isOpen && !container.contains(e.target)) {
        close();
      }
    });
  }

  function toggle() {
    isOpen ? close() : open();
  }

  function open() {
    isOpen = true;
    const fab = document.getElementById('thMminiFab');
    const drawer = document.getElementById('thMiniDrawer');
    if (fab) fab.classList.add('hidden');
    if (drawer) drawer.classList.add('open');
    const input = document.getElementById('thMiniInput');
    if (input) setTimeout(() => input.focus(), 250);
  }

  function close() {
    isOpen = false;
    const fab = document.getElementById('thMminiFab');
    const drawer = document.getElementById('thMiniDrawer');
    if (fab) fab.classList.remove('hidden');
    if (drawer) drawer.classList.remove('open');
  }

  function addMiniMessage(type, content) {
    const container = document.getElementById('thMiniMessages');
    if (!container) return;

    const div = document.createElement('div');
    div.className = 'th-mini-msg ' + (type === 'user' ? 'th-mini-msg-user' : 'th-mini-msg-ai');

    if (type === 'user') {
      div.textContent = content;
    } else {
      div.innerHTML = `
        <div class="th-mini-msg-label">THESIDIA</div>
        <div class="th-mini-msg-body">${escapeHTML(content)}</div>
      `;
    }

    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    messages.push({ type, content });
  }

  async function send() {
    const input = document.getElementById('thMiniInput');
    const text = input ? input.value.trim() : '';
    if (!text || isProcessing) return;

    input.value = '';
    input.style.height = 'auto';
    document.getElementById('thMiniSend').classList.remove('ready');

    addMiniMessage('user', text);
    showTyping(true);
    isProcessing = true;

    try {
      const resp = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          mode: 'auto',
          fast_mode: true,
          stream: false,
        }),
      });

      const data = await resp.json();
      showTyping(false);
      addMiniMessage('ai', data.response || 'No response.');
    } catch (err) {
      showTyping(false);
      addMiniMessage('ai', 'Could not reach Thesidia. Try the full interface.');
    } finally {
      isProcessing = false;
    }
  }

  function showTyping(show) {
    const typing = document.getElementById('thMiniTyping');
    if (typing) typing.classList.toggle('active', show);
  }

  function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Auto-init when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for external control
  window.ThesidiaMini = { open, close, toggle };
})();
