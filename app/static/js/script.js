/* JobTracker DevOps – script.js */

document.addEventListener('DOMContentLoaded', () => {

  // ── Inline état update via AJAX ──────────────────────────
  document.querySelectorAll('.etat-select').forEach(sel => {
    sel.addEventListener('change', async () => {
      const cid  = sel.dataset.cid;
      const etat = sel.value;
      try {
        const res = await fetch(`/api/candidature/${cid}/etat`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ etat })
        });
        if (res.ok) {
          sel.classList.add('saved');
          setTimeout(() => sel.classList.remove('saved'), 1200);
          const row   = sel.closest('.cand-row, tr');
          const badge = row && row.querySelector('.etat-badge');
          if (badge) {
            badge.className = `badge etat-badge etat-${etat}`;
            badge.textContent = etat.replace(/_/g, ' ');
          }
        } else {
          sel.classList.add('error-flash');
          setTimeout(() => sel.classList.remove('error-flash'), 1000);
        }
      } catch (err) {
        sel.classList.add('error-flash');
        setTimeout(() => sel.classList.remove('error-flash'), 1000);
      }
    });
  });

  // ── Theme switcher ───────────────────────────────────────
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const theme = btn.dataset.theme;
      try {
        const res = await fetch('/api/theme', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ theme })
        });
        if (res.ok) {
          document.documentElement.setAttribute('data-theme', theme);
          document.querySelectorAll('.theme-btn').forEach(b =>
            b.classList.toggle('active', b.dataset.theme === theme)
          );
        }
      } catch(e) { console.error('Theme switch failed', e); }
    });
  });

  // ── Auto-dismiss flash messages ──────────────────────────
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity    = '0';
      setTimeout(() => el.remove(), 400);
    }, 3500);
  });

  // ── Routine : highlight élément actif ────────────────────
  function highlightRoutine() {
    const now  = new Date();
    const hhmm = now.getHours() * 60 + now.getMinutes();
    document.querySelectorAll('.routine-list li[data-start]').forEach(li => {
      const [sh, sm] = li.dataset.start.split(':').map(Number);
      const [eh, em] = li.dataset.end.split(':').map(Number);
      li.classList.toggle('active', hhmm >= sh*60+sm && hhmm < eh*60+em);
    });
  }
  highlightRoutine();
  setInterval(highlightRoutine, 60000);

});
