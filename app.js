let pyodide;
let terminalOutput = document.getElementById('terminal-output');
let terminalInput = document.getElementById('terminal-input');
let fileTree = document.getElementById('file-tree');

async function loadPyodide() {
    pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
    });
    terminalOutput.textContent += 'Pyodide loaded.\\n';
}

loadPyodide();

terminalInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const code = terminalInput.value;
        terminalOutput.textContent += '> ' + code + '\\n';
        try {
            const result = await pyodide.runPythonAsync(code);
            terminalOutput.textContent += result + '\\n';
        } catch (error) {
            terminalOutput.textContent += 'Error: ' + error.message + '\\n';
        }
        terminalInput.value = '';
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
    }
});

// Load file tree
fetch('static/aeternum-cognisphere.json')
    .then(response => response.json())
    .then(data => {
        fileTree.textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        fileTree.textContent = 'Error loading file tree: ' + error.message;
    });

// Demo buttons
document.getElementById('quantum-demo').addEventListener('click', () => {
    openVirtualTimeSandbox();
});

document.getElementById('adamic-pulse').addEventListener('click', () => {
    terminalOutput.textContent += 'Running Adamic Pulse...\\n';
});

document.getElementById('merkaba-viz').addEventListener('click', () => {
    terminalOutput.textContent += 'Running Merkaba Visualization...\\n';
});

document.getElementById('sacred-naming').addEventListener('click', () => {
    terminalOutput.textContent += 'Running Sacred Naming...\\n';
});

// Auto-connect to Aeternum / Cognisphere JSON
// Assuming it's loaded in file tree

class SyntropicVirtualClock {
    constructor(onTick = () => {}) {
        this.virtualMs = 0;
        this.rate = 1;
        this.running = false;
        this.timers = new Map();
        this.nextTimerId = 1;
        this.onTick = onTick;
        this.frameId = null;
        this.lastWallMs = null;
        this.callbackLimit = 1000;
        this._frame = this._frame.bind(this);
    }

    now() {
        return this.virtualMs;
    }

    setRate(rate) {
        if (!Number.isFinite(rate) || rate < 1 / 500 || rate > 1000) {
            throw new RangeError('Rate must be between 1/500× and 1000×.');
        }
        this.rate = rate;
        this.onTick(this);
    }

    setTimeout(callback, delayMs = 0) {
        return this._schedule(callback, delayMs, 0);
    }

    setInterval(callback, intervalMs = 0) {
        const interval = Math.max(1, Number(intervalMs) || 0);
        return this._schedule(callback, interval, interval);
    }

    clearTimeout(id) {
        this.timers.delete(id);
    }

    clearInterval(id) {
        this.clearTimeout(id);
    }

    _schedule(callback, delayMs, intervalMs) {
        if (typeof callback !== 'function') {
            throw new TypeError('Scheduled work must be a function.');
        }
        const id = this.nextTimerId++;
        const delay = Math.max(0, Number(delayMs) || 0);
        this.timers.set(id, {
            id,
            callback,
            dueAt: this.virtualMs + delay,
            intervalMs
        });
        return id;
    }

    start() {
        if (this.running) return;
        this.running = true;
        this.lastWallMs = performance.now();
        this.frameId = requestAnimationFrame(this._frame);
        this.onTick(this);
    }

    pause() {
        this.running = false;
        if (this.frameId !== null) cancelAnimationFrame(this.frameId);
        this.frameId = null;
        this.lastWallMs = null;
        this.onTick(this);
    }

    step(stepMs = 1000) {
        if (this.running) return;
        const amount = Number(stepMs);
        if (!Number.isFinite(amount) || amount <= 0) {
            throw new RangeError('Step size must be a positive number of milliseconds.');
        }
        this._advance(amount);
        this.onTick(this);
    }

    reset() {
        this.pause();
        this.virtualMs = 0;
        this.rate = 1;
        this.timers.clear();
        this.onTick(this);
    }

    _frame(wallMs) {
        if (!this.running) return;
        const elapsed = Math.max(0, Math.min(wallMs - this.lastWallMs, 250));
        this.lastWallMs = wallMs;
        this._advance(elapsed * this.rate);
        this.onTick(this);
        this.frameId = requestAnimationFrame(this._frame);
    }

    _advance(deltaMs) {
        const target = this.virtualMs + deltaMs;
        let callbacksRun = 0;

        while (callbacksRun < this.callbackLimit) {
            let next = null;
            for (const timer of this.timers.values()) {
                if (timer.dueAt <= target && (!next || timer.dueAt < next.dueAt)) {
                    next = timer;
                }
            }
            if (!next) break;

            this.virtualMs = next.dueAt;
            if (next.intervalMs === 0) {
                this.timers.delete(next.id);
            } else {
                next.dueAt += next.intervalMs;
            }

            try {
                next.callback();
            } catch (error) {
                console.error('Virtual-time callback failed:', error);
            }
            callbacksRun += 1;
        }

        let skipped = 0;
        if (callbacksRun === this.callbackLimit) {
            for (const timer of this.timers.values()) {
                if (timer.dueAt <= target) {
                    skipped += 1;
                    if (timer.intervalMs === 0) {
                        this.timers.delete(timer.id);
                    } else {
                        timer.dueAt = target + timer.intervalMs;
                    }
                }
            }
        }

        this.virtualMs = target;
        if (skipped) {
            console.warn('Virtual-time callback limit reached; overdue callbacks were skipped.');
        }
    }
}

function openVirtualTimeSandbox() {
    const trigger = document.getElementById('quantum-demo');
    const host = trigger.closest('.demos') || trigger.parentElement;
    let panel = document.getElementById('virtual-time-sandbox');

    if (panel) {
        panel.hidden = false;
        panel.scrollIntoView({ block: 'nearest' });
        return;
    }

    panel = document.createElement('section');
    panel.id = 'virtual-time-sandbox';
    panel.className = 'virtual-time-sandbox';
    panel.setAttribute('aria-labelledby', 'virtual-time-title');
    panel.innerHTML = `
        <h3 id="virtual-time-title">Virtual-time sandbox</h3>
        <p class="virtual-time-note">Controls simulation time only. Fast is 1000×; slow is 1/500× of wall-clock time.</p>
        <output class="virtual-time-clock" aria-live="polite">Virtual time: 00:00:00.000</output>
        <output class="virtual-time-rate" aria-live="polite">Rate: 1× · Paused</output>
        <div class="virtual-time-controls" role="group" aria-label="Virtual time controls">
            <button type="button" data-rate="1000">Fast 1000×</button>
            <button type="button" data-rate="0.002">Slow 500×</button>
            <button type="button" data-action="pause">Pause</button>
            <button type="button" data-action="step">Step +1 virtual second</button>
            <button type="button" data-action="reset">Reset</button>
        </div>
        <h4>Simulation events</h4>
        <ol class="virtual-time-events" aria-live="polite"></ol>
    `;
    host.appendChild(panel);

    const clockDisplay = panel.querySelector('.virtual-time-clock');
    const rateDisplay = panel.querySelector('.virtual-time-rate');
    const events = panel.querySelector('.virtual-time-events');
    const formatTime = (ms) => {
        const totalSeconds = ms / 1000;
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = Math.floor(totalSeconds % 60);
        const millis = Math.floor(ms % 1000);
        return [hours, minutes, seconds].map(value => String(value).padStart(2, '0')).join(':')
            + '.' + String(millis).padStart(3, '0');
    };
    const clock = new SyntropicVirtualClock((state) => {
        clockDisplay.textContent = 'Virtual time: ' + formatTime(state.now());
        const rateLabel = state.rate === 0.002
            ? '1/500× (500× slower)'
            : state.rate === 1000 ? '1000× (1000× faster)' : state.rate + '×';
        rateDisplay.textContent = 'Rate: ' + rateLabel + (state.running ? ' · Running' : ' · Paused');
        const pauseButton = panel.querySelector('[data-action="pause"]');
        pauseButton.textContent = state.running ? 'Pause' : 'Resume';
    });
    window.SyntropicVirtualClock = clock;

    let eventCount = 0;
    const addEvent = (message) => {
        const item = document.createElement('li');
        item.textContent = formatTime(clock.now()) + ' — ' + message;
        events.appendChild(item);
        while (events.children.length > 30) events.firstElementChild.remove();
        panel.querySelector('h4').textContent = 'Simulation events (' + (++eventCount) + ')';
    };
    clock.setInterval(() => addEvent('One virtual minute elapsed.'), 60_000);

    panel.querySelectorAll('[data-rate]').forEach((button) => {
        button.addEventListener('click', () => {
            clock.setRate(Number(button.dataset.rate));
            clock.start();
        });
    });
    panel.querySelector('[data-action="pause"]').addEventListener('click', () => {
        if (clock.running) clock.pause();
        else clock.start();
    });
    panel.querySelector('[data-action="step"]').addEventListener('click', () => {
        clock.step(1000);
    });
    panel.querySelector('[data-action="reset"]').addEventListener('click', () => {
        clock.reset();
        eventCount = 0;
        events.replaceChildren();
        panel.querySelector('h4').textContent = 'Simulation events';
        clock.setInterval(() => addEvent('One virtual minute elapsed.'), 60_000);
    });

    clock.start();
    terminalOutput.textContent += 'Virtual-time sandbox ready. Simulation clock started at 1×.\\n';
}
