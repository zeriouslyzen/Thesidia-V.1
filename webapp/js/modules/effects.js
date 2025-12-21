/**
 * Effects Module
 * Handles visual effects like Nano Dust, Status Indicators, and Astrological Time.
 */

export const Effects = {
    initNanoDust() {
        const canvas = document.getElementById('nanoDustCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const particles = [];
        const particleCount = 80;

        canvas.width = 200;
        canvas.height = 60;

        const textCenterX = canvas.width / 2;
        const textCenterY = canvas.height / 2;
        const textWidth = 140;
        const textHeight = 30;

        for (let i = 0; i < particleCount; i++) {
            const startX = textCenterX + (Math.random() - 0.5) * textWidth;
            const startY = textCenterY + (Math.random() - 0.5) * textHeight;
            const angle = Math.atan2(startY - textCenterY, startX - textCenterX);
            const speed = Math.random() * 0.3 + 0.1;

            particles.push({
                x: startX,
                y: startY,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                size: Math.random() * 0.8 + 0.3,
                opacity: Math.random() * 0.4 + 0.1,
                life: Math.random() * 100,
                maxDistance: Math.random() * 40 + 20
            });
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.life += 0.3;

                const dx = p.x - textCenterX;
                const dy = p.y - textCenterY;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance > p.maxDistance) {
                    p.x = textCenterX + (Math.random() - 0.5) * textWidth;
                    p.y = textCenterY + (Math.random() - 0.5) * textHeight;
                    const angle = Math.atan2(p.y - textCenterY, p.x - textCenterX);
                    const speed = Math.random() * 0.3 + 0.1;
                    p.vx = Math.cos(angle) * speed;
                    p.vy = Math.sin(angle) * speed;
                    p.life = 0;
                }

                const fade = Math.min(distance / p.maxDistance, 1);
                const alpha = p.opacity * (1 - fade * 0.7) * (Math.sin(p.life * 0.1) * 0.2 + 0.8);

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                ctx.fill();
            });
            requestAnimationFrame(animate);
        };
        animate();
    },

    initAstrologicalTime() {
        const timeText = document.getElementById('astroTimeText');
        if (!timeText) return;

        const update = async () => {
            try {
                const response = await fetch('/api/astronomical/current');
                const now = new Date();
                const hhmm = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
                timeText.textContent = hhmm; // For now just use local time, extensible to actual data
            } catch (error) {
                const now = new Date();
                timeText.textContent = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
            }
        };
        update();
        setInterval(update, 60000);
    },

    initStarNotepad() {
        const btn = document.getElementById('starNotepadBtn');
        const panel = document.getElementById('starNotepadPanel');
        const close = document.getElementById('notepadClose');
        const textarea = document.getElementById('notepadTextarea');

        if (!btn || !panel || !textarea) return;

        textarea.value = localStorage.getItem('thesidia_notes') || '';
        textarea.addEventListener('input', () => localStorage.setItem('thesidia_notes', textarea.value));

        btn.addEventListener('click', () => panel.classList.toggle('open'));
        if (close) close.addEventListener('click', () => panel.classList.remove('open'));

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') panel.classList.remove('open');
        });
    }
};
