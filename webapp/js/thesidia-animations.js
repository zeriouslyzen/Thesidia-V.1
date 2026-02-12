/**
 * Thesidia Animations Controller
 * ===============================
 * Triangle grid (lattice) generation + state management.
 * Gear SVG generation for synthesis indicator.
 * Pure inline SVG animated with CSS classes -- no external libs.
 */

const ThesidiaAnimations = (() => {
  'use strict';

  /* ── Triangle Grid Generator ─────────────────────────── */

  /**
   * Build an inline SVG tessellated triangle grid.
   * @param {number} cols   – columns of vertices (default 13 => 12 cols of triangles)
   * @param {number} rows   – rows of vertices (default 9 => 8 rows)
   * @param {number} size   – spacing between vertices in px
   * @returns {SVGElement}
   */
  function createGrid(cols = 13, rows = 9, size = 48) {
    const ns = 'http://www.w3.org/2000/svg';
    const w = (cols - 1) * size;
    const h = (rows - 1) * size * 0.866; // equilateral triangle height ratio

    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'th-lattice');
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
    svg.setAttribute('preserveAspectRatio', 'xMidYMid slice');
    svg.setAttribute('aria-hidden', 'true');

    const edgesGroup = document.createElementNS(ns, 'g');
    edgesGroup.setAttribute('class', 'th-lattice-edges');
    const verticesGroup = document.createElementNS(ns, 'g');
    verticesGroup.setAttribute('class', 'th-lattice-vertices');

    // Build vertex positions
    const verts = [];
    for (let r = 0; r < rows; r++) {
      const row = [];
      for (let c = 0; c < cols; c++) {
        const x = c * size + (r % 2 === 1 ? size * 0.5 : 0);
        const y = r * size * 0.866;
        row.push({ x, y, idx: r * cols + c });
      }
      verts.push(row);
    }

    // Center point for wave delay calculation
    const cx = w / 2;
    const cy = h / 2;
    const maxDist = Math.sqrt(cx * cx + cy * cy);

    // Draw edges
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const v = verts[r][c];
        // Right neighbor
        if (c + 1 < cols) {
          _edge(edgesGroup, ns, v, verts[r][c + 1]);
        }
        // Down-left / down-right
        if (r + 1 < rows) {
          if (r % 2 === 0) {
            if (c < cols) _edge(edgesGroup, ns, v, verts[r + 1][c]);
            if (c - 1 >= 0) _edge(edgesGroup, ns, v, verts[r + 1][c - 1]);
          } else {
            if (c < cols) _edge(edgesGroup, ns, v, verts[r + 1][c]);
            if (c + 1 < cols) _edge(edgesGroup, ns, v, verts[r + 1][c + 1]);
          }
        }
      }
    }

    // Draw vertices
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const v = verts[r][c];
        const circle = document.createElementNS(ns, 'circle');
        circle.setAttribute('cx', v.x);
        circle.setAttribute('cy', v.y);
        circle.setAttribute('r', '2');
        circle.setAttribute('class', 'th-vertex');
        // Wave delay: distance from center mapped to 0-1.2s
        const dist = Math.sqrt((v.x - cx) ** 2 + (v.y - cy) ** 2);
        const delay = (dist / maxDist) * 1.2;
        circle.style.animationDelay = `${delay.toFixed(3)}s`;
        verticesGroup.appendChild(circle);
      }
    }

    svg.appendChild(edgesGroup);
    svg.appendChild(verticesGroup);
    return svg;
  }

  function _edge(group, ns, a, b) {
    const line = document.createElementNS(ns, 'line');
    line.setAttribute('x1', a.x);
    line.setAttribute('y1', a.y);
    line.setAttribute('x2', b.x);
    line.setAttribute('y2', b.y);
    line.setAttribute('class', 'th-edge');
    group.appendChild(line);
  }

  /* ── Gear SVG Generator ──────────────────────────────── */

  function createGears() {
    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    svg.setAttribute('class', 'th-gears');
    svg.setAttribute('width', '32');
    svg.setAttribute('height', '20');
    svg.setAttribute('viewBox', '0 0 32 20');
    svg.setAttribute('aria-hidden', 'true');

    // Gear 1 (left, larger)
    const g1 = document.createElementNS(ns, 'g');
    g1.setAttribute('class', 'th-gear th-gear-1');
    g1.innerHTML = `<circle cx="10" cy="10" r="5" fill="none" stroke="currentColor" stroke-width="1"/>
      <line x1="10" y1="3" x2="10" y2="5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="10" y1="15" x2="10" y2="17" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="3" y1="10" x2="5" y2="10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="15" y1="10" x2="17" y2="10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="5.05" y1="5.05" x2="6.46" y2="6.46" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="13.54" y1="13.54" x2="14.95" y2="14.95" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="14.95" y1="5.05" x2="13.54" y2="6.46" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="6.46" y1="13.54" x2="5.05" y2="14.95" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>`;
    svg.appendChild(g1);

    // Gear 2 (right, smaller)
    const g2 = document.createElementNS(ns, 'g');
    g2.setAttribute('class', 'th-gear th-gear-2');
    g2.innerHTML = `<circle cx="24" cy="10" r="3.5" fill="none" stroke="currentColor" stroke-width="1"/>
      <line x1="24" y1="5" x2="24" y2="6.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="24" y1="13.5" x2="24" y2="15" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="19" y1="10" x2="20.5" y2="10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="27.5" y1="10" x2="29" y2="10" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="20.46" y1="6.46" x2="21.52" y2="7.52" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      <line x1="26.48" y1="12.48" x2="27.54" y2="13.54" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>`;
    svg.appendChild(g2);

    return svg;
  }

  /* ── State Management ────────────────────────────────── */

  let _gridEl = null;
  let _gearsEl = null;

  function init(gridContainer, gearsContainer) {
    if (gridContainer && !gridContainer.querySelector('.th-lattice')) {
      _gridEl = createGrid();
      gridContainer.appendChild(_gridEl);
    }
    if (gearsContainer && !gearsContainer.querySelector('.th-gears')) {
      _gearsEl = createGears();
      gearsContainer.appendChild(_gearsEl);
    }
  }

  function setState(state) {
    // States: 'idle' | 'searching' | 'ranking' | 'synthesizing' | 'complete'
    if (!_gridEl) return;
    const parent = _gridEl.closest('#thesidia-app') || document.body;

    // Remove all state classes
    parent.classList.remove(
      'lattice-idle', 'lattice-searching', 'lattice-ranking',
      'lattice-synthesizing', 'lattice-complete'
    );

    if (state === 'idle') {
      parent.classList.add('lattice-idle');
    } else if (state === 'searching') {
      parent.classList.add('lattice-searching');
    } else if (state === 'ranking') {
      parent.classList.add('lattice-ranking');
    } else if (state === 'synthesizing') {
      parent.classList.add('lattice-synthesizing');
    } else if (state === 'complete') {
      parent.classList.add('lattice-complete');
      // Auto-return to idle after completion animation
      setTimeout(() => {
        parent.classList.remove('lattice-complete');
        parent.classList.add('lattice-idle');
      }, 800);
    }
  }

  return { createGrid, createGears, init, setState };
})();

// Export for module and global access
if (typeof window !== 'undefined') {
  window.ThesidiaAnimations = ThesidiaAnimations;
}
