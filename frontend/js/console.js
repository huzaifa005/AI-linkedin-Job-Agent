/**
 * LiveConsole — The signature terminal-style console component.
 * 
 * Manages animated log lines, status dot states, blinking cursor,
 * and the agent status header. Central visual element of the Ops Console.
 */

class LiveConsole {
  constructor(containerSelector) {
    this.body = document.querySelector(containerSelector);
    this.statusDot = document.getElementById('console-status-dot');
    this.statusText = document.getElementById('console-status-text');
    this.sessionId = document.getElementById('console-session-id');
    this.maxLines = 15;
  }

  /**
   * Set the console state: idle, fetching, analyzing, done, error
   */
  setState(state, label) {
    // Remove previous state classes
    this.statusDot.classList.remove('bg-text-muted', 'bg-secondary', 'bg-primary', 'bg-status-error', 'animate-pulse', 'status-dot-pulse');

    switch (state) {
      case 'idle':
        this.statusDot.classList.add('bg-text-muted', 'status-dot-pulse');
        this.statusText.textContent = label || 'agent · standing by';
        break;
      case 'fetching':
        this.statusDot.classList.add('bg-primary', 'animate-pulse');
        this.statusText.textContent = label || 'agent · fetching';
        break;
      case 'analyzing':
        this.statusDot.classList.add('bg-primary', 'animate-pulse');
        this.statusText.textContent = label || 'agent · analyzing';
        break;
      case 'done':
        this.statusDot.classList.add('bg-secondary');
        this.statusText.textContent = label || 'agent · done';
        break;
      case 'error':
        this.statusDot.classList.add('bg-status-error');
        this.statusText.textContent = label || 'agent · error';
        break;
      case 'ready':
        this.statusDot.classList.add('bg-secondary', 'status-dot-pulse');
        this.statusText.textContent = label || 'agent · ready for cv';
        break;
    }
  }

  /**
   * Set session ID display
   */
  setSessionId(id) {
    if (id) {
      this.sessionId.textContent = `Session: #${id}`;
      this.sessionId.classList.remove('hidden');
    } else {
      this.sessionId.classList.add('hidden');
    }
  }

  /**
   * Clear the console
   */
  clear() {
    this.body.innerHTML = '';
  }

  /**
   * Add a log line to the console with optional styling
   * @param {string} text - The log message
   * @param {string} [type='default'] - Line type: 'default', 'success', 'primary', 'highlight', 'dim', 'error'
   * @param {boolean} [showCursor=false] - Show blinking cursor at end
   */
  addLine(text, type = 'default', showCursor = false) {
    // Remove any existing cursor
    this._removeCursor();

    const line = document.createElement('div');
    line.className = 'console-line console-line-enter';

    // Type classes
    const typeClasses = {
      success: 'log-success',
      primary: 'log-primary',
      highlight: 'log-highlight',
      dim: 'log-dim',
      error: '',
    };

    if (typeClasses[type]) {
      line.classList.add(typeClasses[type]);
    }

    // Build content
    const prefix = document.createElement('span');
    prefix.textContent = '$';
    prefix.className = type === 'error' ? 'text-status-error' : 'text-secondary';

    const content = document.createElement('span');
    if (type === 'error') {
      content.className = 'text-status-error';
    }
    content.textContent = text;

    line.appendChild(prefix);
    line.appendChild(content);

    if (showCursor) {
      const cursor = document.createElement('span');
      cursor.className = 'console-cursor';
      line.appendChild(cursor);
    }

    this.body.appendChild(line);

    // Trim excess lines
    while (this.body.children.length > this.maxLines) {
      this.body.children[0].remove();
    }

    // Scroll to bottom
    this.body.scrollTop = this.body.scrollHeight;
  }

  /**
   * Add a line with bold/highlighted text segments
   * @param {string} prefix - The $ prefix text
   * @param {Array<{text: string, bold?: boolean, color?: string}>} segments
   */
  addRichLine(segments, showCursor = false) {
    this._removeCursor();

    const line = document.createElement('div');
    line.className = 'console-line console-line-enter';

    const prefixEl = document.createElement('span');
    prefixEl.textContent = '$';
    prefixEl.className = 'text-secondary';
    line.appendChild(prefixEl);

    segments.forEach(seg => {
      const span = document.createElement('span');
      span.textContent = seg.text;
      if (seg.bold) span.style.fontWeight = '700';
      if (seg.color) span.style.color = seg.color;
      line.appendChild(span);
    });

    if (showCursor) {
      const cursor = document.createElement('span');
      cursor.className = 'console-cursor';
      line.appendChild(cursor);
    }

    this.body.appendChild(line);
    this.body.scrollTop = this.body.scrollHeight;
  }

  /**
   * Show the initial idle state
   */
  showIdle() {
    this.clear();
    this.setState('idle');
    this.setSessionId(null);
    this.addLine('Waiting for instructions…', 'default', true);
  }

  /**
   * Remove any existing cursors
   */
  _removeCursor() {
    const cursors = this.body.querySelectorAll('.console-cursor');
    cursors.forEach(c => c.remove());
  }
}

// Make globally available
window.LiveConsole = LiveConsole;
