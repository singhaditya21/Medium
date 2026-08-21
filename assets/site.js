(() => {
  const root = document.documentElement;
  const themeButton = document.querySelector('[data-theme-toggle]');
  const setTheme = (theme) => {
    root.dataset.theme = theme;
    try { localStorage.setItem('as-theme', theme); } catch (_) {}
    if (themeButton) {
      themeButton.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    }
  };

  if (themeButton) {
    themeButton.addEventListener('click', () => setTheme(root.dataset.theme === 'dark' ? 'light' : 'dark'));
  }

  document.querySelectorAll('[data-year]').forEach((node) => { node.textContent = String(new Date().getFullYear()); });

  const search = document.querySelector('[data-story-search]');
  const cards = [...document.querySelectorAll('[data-story-card]')];
  const empty = document.querySelector('[data-empty-state]');
  if (search && cards.length) {
    search.addEventListener('input', () => {
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach((card) => {
        const match = !query || card.dataset.search.includes(query);
        card.hidden = !match;
        if (match) visible += 1;
      });
      if (empty) empty.hidden = visible !== 0;
    });
  }

  const progress = document.querySelector('[data-progress]');
  const articleBody = document.querySelector('[data-article-body]');
  if (progress && articleBody) {
    const updateProgress = () => {
      const start = articleBody.offsetTop;
      const distance = Math.max(1, articleBody.offsetHeight - window.innerHeight * 0.55);
      const value = Math.min(1, Math.max(0, (window.scrollY - start + 80) / distance));
      progress.style.transform = `scaleX(${value})`;
    };
    updateProgress();
    addEventListener('scroll', updateProgress, { passive: true });
    addEventListener('resize', updateProgress);
  }

  const tocLinks = [...document.querySelectorAll('.article-rail a')];
  if (tocLinks.length && 'IntersectionObserver' in window) {
    const byId = new Map(tocLinks.map((link) => [decodeURIComponent(link.hash.slice(1)), link]));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        tocLinks.forEach((link) => link.removeAttribute('aria-current'));
        const active = byId.get(entry.target.id);
        if (active) active.setAttribute('aria-current', 'true');
      });
    }, { rootMargin: '-18% 0px -68% 0px' });
    document.querySelectorAll('.article-body h2[id], .article-body h3[id]').forEach((heading) => observer.observe(heading));
  }
})();
