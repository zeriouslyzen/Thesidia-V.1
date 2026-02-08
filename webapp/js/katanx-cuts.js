/**
 * Katanx Cuts - Debate/Challenge System
 * 
 * Structured debates with real debate rules adapted for social media.
 * The best content feature on the platform.
 * 
 * @author Katanx Team
 */

const KatanxCuts = (function () {
    'use strict';

    // ═══════════════════════════════════════════════════════════════
    // CONFIGURATION
    // ═══════════════════════════════════════════════════════════════

    const Config = {
        // Phase durations (in seconds)
        PHASES: {
            OPENING: 60,          // Opening statement
            REBUTTAL_1: 45,       // First rebuttal
            POI: 15,              // Point of Information
            REBUTTAL_2: 30,       // Second rebuttal
            CLOSING: 30           // Closing statement
        },

        // Voting
        VOTING_DURATION_HOURS: 24,
        MIN_VOTES_FOR_DECISION: 10,

        // Limits
        MAX_ACTIVE_CUTS_PER_STREAM: 3,
        COOLDOWN_BETWEEN_CHALLENGES_MS: 5 * 60 * 1000,  // 5 minutes

        // Scoring weights
        SCORING: {
            MATTER: 0.4,    // Evidence and logic
            MANNER: 0.3,    // Delivery and respect  
            METHOD: 0.3     // Structure and clarity
        }
    };

    // ═══════════════════════════════════════════════════════════════
    // STATE
    // ═══════════════════════════════════════════════════════════════

    const CutStatus = Object.freeze({
        PENDING: 'pending',           // Waiting for defender to accept
        ACTIVE: 'active',             // Debate in progress
        VOTING: 'voting',             // Community voting
        COMPLETE: 'complete',         // Winner declared
        DECLINED: 'declined',         // Defender declined
        EXPIRED: 'expired'            // Challenge timed out
    });

    const PhaseType = Object.freeze({
        CHALLENGER_OPENING: 'challenger_opening',
        DEFENDER_OPENING: 'defender_opening',
        CHALLENGER_REBUTTAL_1: 'challenger_rebuttal_1',
        DEFENDER_REBUTTAL_1: 'defender_rebuttal_1',
        CHALLENGER_POI: 'challenger_poi',
        DEFENDER_POI: 'defender_poi',
        CHALLENGER_REBUTTAL_2: 'challenger_rebuttal_2',
        DEFENDER_REBUTTAL_2: 'defender_rebuttal_2',
        CHALLENGER_CLOSING: 'challenger_closing',
        DEFENDER_CLOSING: 'defender_closing',
        VOTING: 'voting'
    });

    let state = {
        activeCuts: [],
        currentCut: null,
        currentPhase: null,
        timerInterval: null,
        container: null
    };

    // ═══════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════════

    function init(options) {
        state.container = typeof options.container === 'string'
            ? document.querySelector(options.container)
            : options.container;

        // Listen for challenge events from comments
        document.addEventListener('katanx:challenge', handleChallengeEvent);

        // Load existing cuts
        loadCuts(options.streamId);

        console.log('[KatanxCuts] Initialized');
    }

    function handleChallengeEvent(e) {
        const { targetComment, challenger, streamId } = e.detail;
        issueChallenge(targetComment.user, challenger, streamId, targetComment.content);
    }

    // ═══════════════════════════════════════════════════════════════
    // CHALLENGE FLOW
    // ═══════════════════════════════════════════════════════════════

    /**
     * Issue a challenge to another user
     */
    function issueChallenge(defender, challenger, streamId, topic) {
        // Validate
        if (defender.id === challenger.id) {
            showError("You can't challenge yourself");
            return null;
        }

        const activeCuts = getActivecuts(streamId);
        if (activeCuts.length >= Config.MAX_ACTIVE_CUTS_PER_STREAM) {
            showError(`Maximum ${Config.MAX_ACTIVE_CUTS_PER_STREAM} active cuts per stream`);
            return null;
        }

        // Check cooldown
        const lastChallenge = getLastChallengeTime(challenger.id);
        if (Date.now() - lastChallenge < Config.COOLDOWN_BETWEEN_CHALLENGES_MS) {
            const remaining = Math.ceil((Config.COOLDOWN_BETWEEN_CHALLENGES_MS - (Date.now() - lastChallenge)) / 1000);
            showError(`Wait ${remaining}s before issuing another challenge`);
            return null;
        }

        const cut = {
            id: generateId(),
            stream_id: streamId,
            topic: topic || 'Open Debate',
            challenger: challenger,
            defender: defender,
            status: CutStatus.PENDING,
            phases: [],
            votes: { challenger: 0, defender: 0 },
            created_at: new Date().toISOString(),
            expires_at: new Date(Date.now() + 5 * 60 * 1000).toISOString()  // 5 min to accept
        };

        saveCut(cut);
        renderPendingChallenge(cut);

        // Track last challenge time
        localStorage.setItem(`kx_last_challenge_${challenger.id}`, Date.now().toString());

        return cut;
    }

    /**
     * Accept a challenge
     */
    function acceptChallenge(cutId) {
        const cut = getCut(cutId);
        if (!cut || cut.status !== CutStatus.PENDING) {
            showError('Challenge no longer available');
            return;
        }

        cut.status = CutStatus.ACTIVE;
        cut.started_at = new Date().toISOString();
        cut.current_phase = 0;

        // Initialize phases
        cut.phases = [
            { type: PhaseType.CHALLENGER_OPENING, duration: Config.PHASES.OPENING, content: null },
            { type: PhaseType.DEFENDER_OPENING, duration: Config.PHASES.OPENING, content: null },
            { type: PhaseType.CHALLENGER_REBUTTAL_1, duration: Config.PHASES.REBUTTAL_1, content: null },
            { type: PhaseType.DEFENDER_REBUTTAL_1, duration: Config.PHASES.REBUTTAL_1, content: null },
            { type: PhaseType.CHALLENGER_REBUTTAL_2, duration: Config.PHASES.REBUTTAL_2, content: null },
            { type: PhaseType.DEFENDER_REBUTTAL_2, duration: Config.PHASES.REBUTTAL_2, content: null },
            { type: PhaseType.CHALLENGER_CLOSING, duration: Config.PHASES.CLOSING, content: null },
            { type: PhaseType.DEFENDER_CLOSING, duration: Config.PHASES.CLOSING, content: null }
        ];

        saveCut(cut);
        startPhase(cut, 0);
        renderActiveCut(cut);
    }

    /**
     * Decline a challenge
     */
    function declineChallenge(cutId) {
        const cut = getCut(cutId);
        if (!cut) return;

        cut.status = CutStatus.DECLINED;
        saveCut(cut);

        showToast(`${cut.defender.display_name} declined the challenge`);
        renderDeclinedCut(cut);
    }

    // ═══════════════════════════════════════════════════════════════
    // PHASE MANAGEMENT
    // ═══════════════════════════════════════════════════════════════

    /**
     * Start a debate phase
     */
    function startPhase(cut, phaseIndex) {
        if (phaseIndex >= cut.phases.length) {
            // All phases complete, start voting
            startVoting(cut);
            return;
        }

        const phase = cut.phases[phaseIndex];
        cut.current_phase = phaseIndex;
        state.currentCut = cut;
        state.currentPhase = phase;

        // Start timer
        let remaining = phase.duration;
        updateTimerDisplay(remaining);

        state.timerInterval = setInterval(() => {
            remaining--;
            updateTimerDisplay(remaining);

            if (remaining <= 0) {
                clearInterval(state.timerInterval);
                completePhase(cut, phaseIndex);
            }
        }, 1000);

        renderPhaseUI(cut, phase);

        // Play dramatic sound effect
        playPhaseSound('phase_start');
    }

    /**
     * Submit content for current phase
     */
    function submitPhaseContent(cutId, content) {
        const cut = getCut(cutId);
        if (!cut || cut.status !== CutStatus.ACTIVE) return;

        const phase = cut.phases[cut.current_phase];
        phase.content = content;
        phase.submitted_at = new Date().toISOString();

        saveCut(cut);

        // Auto-advance to next phase
        clearInterval(state.timerInterval);
        completePhase(cut, cut.current_phase);
    }

    /**
     * Complete a phase and move to next
     */
    function completePhase(cut, phaseIndex) {
        const phase = cut.phases[phaseIndex];
        phase.completed = true;
        saveCut(cut);

        // Brief pause before next phase
        setTimeout(() => {
            startPhase(cut, phaseIndex + 1);
        }, 2000);
    }

    // ═══════════════════════════════════════════════════════════════
    // VOTING
    // ═══════════════════════════════════════════════════════════════

    /**
     * Start voting period
     */
    function startVoting(cut) {
        cut.status = CutStatus.VOTING;
        cut.voting_ends_at = new Date(Date.now() + Config.VOTING_DURATION_HOURS * 60 * 60 * 1000).toISOString();
        saveCut(cut);

        renderVotingUI(cut);
        showToast('🗡️ Debate complete! Voting is now open for 24 hours');
    }

    /**
     * Cast a vote
     */
    function vote(cutId, choice) {
        const cut = getCut(cutId);
        if (!cut || cut.status !== CutStatus.VOTING) {
            showError('Voting is not available');
            return;
        }

        const userId = getCurrentUserId();
        const voteKey = `kx_vote_${cutId}_${userId}`;

        // Check if already voted
        if (localStorage.getItem(voteKey)) {
            showError("You've already voted on this cut");
            return;
        }

        // Record vote
        if (choice === 'challenger') {
            cut.votes.challenger++;
        } else if (choice === 'defender') {
            cut.votes.defender++;
        }

        localStorage.setItem(voteKey, choice);
        saveCut(cut);

        renderVoteConfirmation(cut, choice);
        checkVotingComplete(cut);
    }

    /**
     * Check if voting should end
     */
    function checkVotingComplete(cut) {
        const now = new Date();
        const votingEnds = new Date(cut.voting_ends_at);

        if (now >= votingEnds) {
            finalizeCut(cut);
        }
    }

    /**
     * Finalize the cut and declare winner
     */
    function finalizeCut(cut) {
        cut.status = CutStatus.COMPLETE;

        const totalVotes = cut.votes.challenger + cut.votes.defender;

        if (totalVotes < Config.MIN_VOTES_FOR_DECISION) {
            cut.winner = 'draw';
            cut.result_reason = 'Not enough votes for a decision';
        } else if (cut.votes.challenger > cut.votes.defender) {
            cut.winner = 'challenger';
        } else if (cut.votes.defender > cut.votes.challenger) {
            cut.winner = 'defender';
        } else {
            cut.winner = 'draw';
            cut.result_reason = 'Tie vote';
        }

        saveCut(cut);
        renderWinnerAnnouncement(cut);
    }

    // ═══════════════════════════════════════════════════════════════
    // RENDERING
    // ═══════════════════════════════════════════════════════════════

    function renderPendingChallenge(cut) {
        const html = `
            <div class="kx-cut kx-cut--pending" data-cut-id="${cut.id}">
                <div class="kx-cut__header">
                    <div class="kx-cut__badge">🗡️ CHALLENGE ISSUED</div>
                </div>
                <div class="kx-cut__challengers">
                    <div class="kx-cut__fighter kx-cut__fighter--challenger">
                        <img src="${cut.challenger.avatar_url}" alt="${cut.challenger.display_name}">
                        <span>${cut.challenger.display_name}</span>
                    </div>
                    <div class="kx-cut__vs">VS</div>
                    <div class="kx-cut__fighter kx-cut__fighter--defender">
                        <img src="${cut.defender.avatar_url}" alt="${cut.defender.display_name}">
                        <span>${cut.defender.display_name}</span>
                    </div>
                </div>
                <div class="kx-cut__topic">"${escapeHtml(cut.topic)}"</div>
                <div class="kx-cut__actions">
                    <button class="kx-cut__btn kx-cut__btn--accept" onclick="KatanxCuts.acceptChallenge('${cut.id}')">
                        Accept Challenge
                    </button>
                    <button class="kx-cut__btn kx-cut__btn--decline" onclick="KatanxCuts.declineChallenge('${cut.id}')">
                        Decline
                    </button>
                </div>
                <div class="kx-cut__timer">Expires in 5:00</div>
            </div>
        `;

        if (state.container) {
            state.container.insertAdjacentHTML('afterbegin', html);
        }
    }

    function renderActiveCut(cut) {
        const phase = cut.phases[cut.current_phase];
        const isChallenger = phase.type.includes('challenger');
        const speaker = isChallenger ? cut.challenger : cut.defender;

        const html = `
            <div class="kx-cut kx-cut--active" data-cut-id="${cut.id}">
                <div class="kx-cut__header">
                    <div class="kx-cut__badge kx-cut__badge--live">🔴 LIVE CUT</div>
                    <div class="kx-cut__phase-name">${formatPhaseName(phase.type)}</div>
                </div>
                
                <div class="kx-cut__arena">
                    <div class="kx-cut__speaker">
                        <img src="${speaker.avatar_url}" alt="${speaker.display_name}">
                        <span>${speaker.display_name}</span>
                    </div>
                    
                    <div class="kx-cut__timer-display">
                        <div class="kx-cut__timer-ring"></div>
                        <div class="kx-cut__timer-value" id="cutTimer">${phase.duration}</div>
                    </div>
                </div>

                <div class="kx-cut__input-area" id="phaseInput">
                    <textarea placeholder="Enter your statement..." maxlength="500"></textarea>
                    <button onclick="KatanxCuts.submitPhaseContent('${cut.id}', this.previousElementSibling.value)">
                        Submit
                    </button>
                </div>

                <div class="kx-cut__phases-bar">
                    ${cut.phases.map((p, i) => `
                        <div class="kx-cut__phase-dot ${i < cut.current_phase ? 'done' : ''} ${i === cut.current_phase ? 'active' : ''}"></div>
                    `).join('')}
                </div>
            </div>
        `;

        updateCutContainer(cut.id, html);
    }

    function renderVotingUI(cut) {
        const html = `
            <div class="kx-cut kx-cut--voting" data-cut-id="${cut.id}">
                <div class="kx-cut__header">
                    <div class="kx-cut__badge">⚖️ VOTING OPEN</div>
                </div>
                
                <div class="kx-cut__summary">
                    ${cut.phases.filter(p => p.content).map(p => `
                        <div class="kx-cut__statement">
                            <strong>${formatPhaseName(p.type)}:</strong>
                            <p>${escapeHtml(p.content)}</p>
                        </div>
                    `).join('')}
                </div>

                <div class="kx-cut__vote-options">
                    <button class="kx-cut__vote-btn" onclick="KatanxCuts.vote('${cut.id}', 'challenger')">
                        <img src="${cut.challenger.avatar_url}" alt="">
                        <span>${cut.challenger.display_name}</span>
                        <span class="kx-cut__vote-count">${cut.votes.challenger}</span>
                    </button>
                    <button class="kx-cut__vote-btn" onclick="KatanxCuts.vote('${cut.id}', 'defender')">
                        <img src="${cut.defender.avatar_url}" alt="">
                        <span>${cut.defender.display_name}</span>
                        <span class="kx-cut__vote-count">${cut.votes.defender}</span>
                    </button>
                </div>

                <div class="kx-cut__voting-ends">
                    Voting ends: ${new Date(cut.voting_ends_at).toLocaleString()}
                </div>
            </div>
        `;

        updateCutContainer(cut.id, html);
    }

    function renderWinnerAnnouncement(cut) {
        const winner = cut.winner === 'challenger' ? cut.challenger
            : cut.winner === 'defender' ? cut.defender
                : null;

        const html = `
            <div class="kx-cut kx-cut--complete" data-cut-id="${cut.id}">
                <div class="kx-cut__header">
                    <div class="kx-cut__badge kx-cut__badge--complete">🏆 CUT COMPLETE</div>
                </div>
                
                ${winner ? `
                    <div class="kx-cut__winner">
                        <div class="kx-cut__winner-crown">👑</div>
                        <img src="${winner.avatar_url}" alt="${winner.display_name}">
                        <div class="kx-cut__winner-name">${winner.display_name}</div>
                        <div class="kx-cut__winner-label">WINNER</div>
                    </div>
                ` : `
                    <div class="kx-cut__draw">
                        <div class="kx-cut__draw-icon">🤝</div>
                        <div class="kx-cut__draw-text">DRAW</div>
                        <div class="kx-cut__draw-reason">${cut.result_reason || ''}</div>
                    </div>
                `}

                <div class="kx-cut__final-score">
                    <div>${cut.challenger.display_name}: ${cut.votes.challenger} votes</div>
                    <div>${cut.defender.display_name}: ${cut.votes.defender} votes</div>
                </div>
            </div>
        `;

        updateCutContainer(cut.id, html);

        // Celebration effects
        if (winner) {
            triggerCelebration();
        }
    }

    function renderPhaseUI(cut, phase) {
        // Update existing active cut UI
        const timerEl = document.getElementById('cutTimer');
        if (timerEl) {
            timerEl.textContent = phase.duration;
        }

        const phaseBar = state.container?.querySelector('.kx-cut__phases-bar');
        if (phaseBar) {
            const dots = phaseBar.querySelectorAll('.kx-cut__phase-dot');
            dots.forEach((dot, i) => {
                dot.classList.toggle('done', i < cut.current_phase);
                dot.classList.toggle('active', i === cut.current_phase);
            });
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // UTILITIES
    // ═══════════════════════════════════════════════════════════════

    function updateCutContainer(cutId, html) {
        const existing = state.container?.querySelector(`[data-cut-id="${cutId}"]`);
        if (existing) {
            existing.outerHTML = html;
        } else if (state.container) {
            state.container.insertAdjacentHTML('afterbegin', html);
        }
    }

    function updateTimerDisplay(seconds) {
        const timerEl = document.getElementById('cutTimer');
        if (timerEl) {
            timerEl.textContent = seconds;
            if (seconds <= 10) {
                timerEl.classList.add('kx-cut__timer--warning');
            }
            if (seconds <= 5) {
                timerEl.classList.add('kx-cut__timer--critical');
            }
        }
    }

    function formatPhaseName(type) {
        const names = {
            challenger_opening: 'Challenger Opening',
            defender_opening: 'Defender Opening',
            challenger_rebuttal_1: 'Challenger Rebuttal',
            defender_rebuttal_1: 'Defender Rebuttal',
            challenger_rebuttal_2: 'Challenger Counter',
            defender_rebuttal_2: 'Defender Counter',
            challenger_closing: 'Challenger Closing',
            defender_closing: 'Defender Closing'
        };
        return names[type] || type;
    }

    function getCut(id) {
        const stored = localStorage.getItem(`kx_cut_${id}`);
        return stored ? JSON.parse(stored) : null;
    }

    function saveCut(cut) {
        localStorage.setItem(`kx_cut_${cut.id}`, JSON.stringify(cut));

        // Update index
        const index = JSON.parse(localStorage.getItem('kx_cuts_index') || '[]');
        if (!index.includes(cut.id)) {
            index.push(cut.id);
            localStorage.setItem('kx_cuts_index', JSON.stringify(index));
        }
    }

    function loadCuts(streamId) {
        const index = JSON.parse(localStorage.getItem('kx_cuts_index') || '[]');
        state.activeCuts = index
            .map(id => getCut(id))
            .filter(cut => cut && cut.stream_id === streamId && cut.status !== CutStatus.COMPLETE);
    }

    function getActivecuts(streamId) {
        return state.activeCuts.filter(c =>
            c.stream_id === streamId &&
            (c.status === CutStatus.PENDING || c.status === CutStatus.ACTIVE)
        );
    }

    function getLastChallengeTime(userId) {
        return parseInt(localStorage.getItem(`kx_last_challenge_${userId}`) || '0', 10);
    }

    function getCurrentUserId() {
        const user = JSON.parse(localStorage.getItem('kx_current_user') || '{}');
        return user.id || 'anonymous';
    }

    function generateId() {
        return 'cut_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'kx-toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    function showError(message) {
        const toast = document.createElement('div');
        toast.className = 'kx-toast kx-toast--error';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    function playPhaseSound(type) {
        // Audio feedback (implement when audio assets available)
        console.log('[KatanxCuts] Sound:', type);
    }

    function triggerCelebration() {
        // Confetti or particle effects
        console.log('[KatanxCuts] 🎉 Winner celebration triggered!');
    }

    function renderDeclinedCut(cut) {
        const el = state.container?.querySelector(`[data-cut-id="${cut.id}"]`);
        if (el) {
            el.classList.add('kx-cut--declined');
            el.innerHTML = `
                <div class="kx-cut__header">
                    <div class="kx-cut__badge kx-cut__badge--declined">Challenge Declined</div>
                </div>
            `;
            setTimeout(() => el.remove(), 3000);
        }
    }

    function renderVoteConfirmation(cut, choice) {
        showToast(`Vote cast for ${choice === 'challenger' ? cut.challenger.display_name : cut.defender.display_name}!`);
    }

    // ═══════════════════════════════════════════════════════════════
    // PUBLIC API
    // ═══════════════════════════════════════════════════════════════

    return {
        init,
        issueChallenge,
        acceptChallenge,
        declineChallenge,
        submitPhaseContent,
        vote,
        getCut,
        Config,
        CutStatus,
        PhaseType
    };

})();

// Export for Node.js / testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KatanxCuts;
}
