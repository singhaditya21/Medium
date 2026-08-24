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

  document.querySelectorAll('[data-copy-url]').forEach((button) => {
    button.addEventListener('click', async () => {
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(button.dataset.copyUrl);
        button.textContent = 'Copied';
      } catch (error) {
        const temporary = document.createElement('textarea');
        temporary.value = button.dataset.copyUrl;
        temporary.setAttribute('readonly', '');
        temporary.style.position = 'fixed';
        temporary.style.opacity = '0';
        document.body.appendChild(temporary);
        temporary.select();
        document.execCommand('copy');
        temporary.remove();
        button.textContent = 'Copied';
      }
      setTimeout(() => { button.textContent = original; }, 1800);
    });
  });

  const figures = [...document.querySelectorAll('.story-figure')];
  if (figures.length) {
    root.classList.add('figure-explorer-enabled');

    const viewer = document.createElement('dialog');
    viewer.className = 'figure-viewer';
    viewer.setAttribute('aria-labelledby', 'figure-viewer-title');
    viewer.setAttribute('aria-describedby', 'figure-viewer-caption');
    viewer.innerHTML = `
      <div class="figure-viewer-shell">
        <header class="figure-viewer-header">
          <div>
            <p>Interactive technical infographic</p>
            <h2 id="figure-viewer-title"></h2>
          </div>
          <div class="figure-viewer-navigation" aria-label="Figure navigation">
            <button type="button" data-figure-previous>← Previous</button>
            <button type="button" data-figure-next>Next →</button>
            <form method="dialog"><button type="submit" class="figure-viewer-close" aria-label="Close figure viewer">Close</button></form>
          </div>
        </header>
        <div class="figure-viewer-stage" data-figure-stage data-zoomed="false" tabindex="0" aria-label="Scrollable infographic canvas">
          <img data-figure-image alt="">
        </div>
        <footer class="figure-viewer-footer">
          <div class="figure-viewer-copy">
            <p class="figure-viewer-meta" data-figure-meta aria-live="polite"></p>
            <p id="figure-viewer-caption" data-figure-caption></p>
          </div>
          <div class="figure-viewer-controls" aria-label="Figure zoom controls">
            <button type="button" data-figure-fit>Fit</button>
            <button type="button" data-figure-zoom-out aria-label="Zoom out">−</button>
            <output data-figure-zoom aria-live="polite">Fit</output>
            <button type="button" data-figure-zoom-in aria-label="Zoom in">+</button>
            <a data-figure-download download>Download PNG</a>
          </div>
        </footer>
      </div>`;
    document.body.appendChild(viewer);

    const viewerTitle = viewer.querySelector('#figure-viewer-title');
    const viewerStage = viewer.querySelector('[data-figure-stage]');
    const viewerImage = viewer.querySelector('[data-figure-image]');
    const viewerMeta = viewer.querySelector('[data-figure-meta]');
    const viewerCaption = viewer.querySelector('[data-figure-caption]');
    const zoomOutput = viewer.querySelector('[data-figure-zoom]');
    const download = viewer.querySelector('[data-figure-download]');
    const previousButton = viewer.querySelector('[data-figure-previous]');
    const nextButton = viewer.querySelector('[data-figure-next]');
    const initialSource = figures[0].querySelector('img').src;
    download.href = initialSource;
    download.download = initialSource.split('/').pop().split('?')[0] || 'figure-1.png';
    let activeFigure = 0;
    let zoom = 0;
    let returnFocus = null;

    const applyZoom = (value, center = true) => {
      zoom = value === 0 ? 0 : Math.min(2, Math.max(0.5, value));
      viewerStage.dataset.zoomed = zoom === 0 ? 'false' : 'true';
      if (zoom === 0) {
        viewerImage.style.removeProperty('width');
        viewerImage.style.removeProperty('max-width');
        viewerImage.style.removeProperty('max-height');
        zoomOutput.value = 'Fit';
        zoomOutput.textContent = 'Fit';
      } else {
        const naturalWidth = viewerImage.naturalWidth || 2400;
        viewerImage.style.width = `${Math.round(naturalWidth * zoom)}px`;
        viewerImage.style.maxWidth = 'none';
        viewerImage.style.maxHeight = 'none';
        const label = `${Math.round(zoom * 100)}%`;
        zoomOutput.value = label;
        zoomOutput.textContent = label;
      }
      if (center) {
        requestAnimationFrame(() => {
          viewerStage.scrollTo({
            left: Math.max(0, (viewerStage.scrollWidth - viewerStage.clientWidth) / 2),
            top: Math.max(0, (viewerStage.scrollHeight - viewerStage.clientHeight) / 2),
            behavior: 'smooth',
          });
        });
      }
    };

    const showFigure = (index) => {
      activeFigure = (index + figures.length) % figures.length;
      const figure = figures[activeFigure];
      const image = figure.querySelector('img');
      const caption = figure.querySelector('figcaption');
      const source = image.currentSrc || image.src;
      const number = activeFigure + 1;
      const naturalWidth = image.naturalWidth || Number(image.getAttribute('width')) || 2400;
      const naturalHeight = image.naturalHeight || Number(image.getAttribute('height')) || 1600;
      viewerTitle.textContent = `Figure ${number} of ${figures.length}`;
      viewerImage.src = source;
      viewerImage.alt = image.alt;
      viewerCaption.textContent = caption ? caption.textContent.trim() : image.alt;
      viewerMeta.textContent = `${naturalWidth.toLocaleString()} × ${naturalHeight.toLocaleString()} pixels · full-resolution source`;
      download.href = source;
      download.download = source.split('/').pop().split('?')[0] || `figure-${number}.png`;
      previousButton.setAttribute('aria-label', `View figure ${number === 1 ? figures.length : number - 1}`);
      nextButton.setAttribute('aria-label', `View figure ${number === figures.length ? 1 : number + 1}`);
      applyZoom(0, false);
      viewerStage.scrollTo({ left: 0, top: 0 });
    };

    const openFigure = (index, trigger) => {
      returnFocus = trigger;
      showFigure(index);
      document.body.classList.add('figure-viewer-open');
      if (typeof viewer.showModal === 'function') viewer.showModal();
      else viewer.setAttribute('open', '');
      viewer.querySelector('.figure-viewer-close').focus();
    };

    const closeViewer = () => {
      if (typeof viewer.close === 'function') viewer.close();
      else {
        viewer.removeAttribute('open');
        document.body.classList.remove('figure-viewer-open');
        if (returnFocus) returnFocus.focus();
      }
    };

    const revealObserver = 'IntersectionObserver' in window
      ? new IntersectionObserver((entries, observer) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-figure-visible');
            observer.unobserve(entry.target);
          });
        }, { threshold: 0.12 })
      : null;

    figures.forEach((figure, index) => {
      const button = figure.querySelector('[data-figure-open]');
      button.hidden = false;
      button.addEventListener('click', () => openFigure(index, button));
      if (revealObserver) revealObserver.observe(figure);
      else figure.classList.add('is-figure-visible');
    });

    previousButton.addEventListener('click', () => showFigure(activeFigure - 1));
    nextButton.addEventListener('click', () => showFigure(activeFigure + 1));
    viewer.querySelector('[data-figure-fit]').addEventListener('click', () => applyZoom(0));
    viewer.querySelector('[data-figure-zoom-in]').addEventListener('click', () => applyZoom(zoom === 0 ? 0.5 : zoom + 0.25));
    viewer.querySelector('[data-figure-zoom-out]').addEventListener('click', () => applyZoom(zoom <= 0.5 ? 0 : zoom - 0.25));
    viewerImage.addEventListener('dblclick', () => applyZoom(zoom === 0 ? 1 : 0));
    viewer.addEventListener('close', () => {
      document.body.classList.remove('figure-viewer-open');
      if (returnFocus) returnFocus.focus();
    });
    viewer.addEventListener('cancel', () => document.body.classList.remove('figure-viewer-open'));
    viewer.addEventListener('click', (event) => { if (event.target === viewer) closeViewer(); });
    document.addEventListener('keydown', (event) => {
      if (!viewer.open) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        closeViewer();
      } else if (event.key === 'ArrowLeft') showFigure(activeFigure - 1);
      else if (event.key === 'ArrowRight') showFigure(activeFigure + 1);
      else if (event.key === '+' || event.key === '=') applyZoom(zoom === 0 ? 0.5 : zoom + 0.25);
      else if (event.key === '-') applyZoom(zoom <= 0.5 ? 0 : zoom - 0.25);
      else if (event.key === '0') applyZoom(0);
    });
  }
})();
