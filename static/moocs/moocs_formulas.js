/* Pattern switching, live search and KaTeX rendering for the formula reference. */
(function () {
  const panels = Array.from(document.querySelectorAll('.fx-pattern'));
  const tabs = Array.from(document.querySelectorAll('.fx-tab'));
  const searchInput = document.getElementById('fx-search-input');
  const resultCount = document.getElementById('fx-result-count');
  const emptyState = document.getElementById('fx-empty');
  const subjects = Array.from(document.querySelectorAll('.fx-subject'));

  if (!panels.length) return;

  let activePattern = panels.find(panel => !panel.hidden)?.dataset.pattern || panels[0].dataset.pattern;

  const renderMath = function () {
    if (typeof window.katex === 'undefined') return;
    document.querySelectorAll('.fx-math').forEach(function (host) {
      if (host.dataset.rendered === 'true' || host.hidden) return;
      const tex = host.dataset.tex;
      if (!tex) return;
      try {
        window.katex.render(tex, host, { throwOnError: false, displayMode: true });
        host.dataset.rendered = 'true';
      } catch (error) {
        host.textContent = tex;
      }
    });
  };

  const revealMatches = function (host, visible) {
    if (visible && host.dataset.rendered !== 'true' && host.offsetParent !== null) {
      const tex = host.dataset.tex;
      if (tex && typeof window.katex !== 'undefined') {
        try {
          window.katex.render(tex, host, { throwOnError: false, displayMode: true });
          host.dataset.rendered = 'true';
          return;
        } catch (error) {
          host.textContent = tex;
        }
      }
    }
  };

  const applyFilter = function () {
    const query = searchInput.value.trim().toLowerCase();
    const active = panels.find(panel => panel.dataset.pattern === activePattern);
    if (!active) return;

    let visibleFormulas = 0;

    subjects.forEach(function (subject) {
      if (subject.closest('.fx-pattern') !== active) return;

      let visibleInSubject = 0;

      subject.querySelectorAll('.fx-topic').forEach(function (topic) {
        let visibleInTopic = 0;

        topic.querySelectorAll('.fx-formula').forEach(function (card) {
          const haystack = (card.dataset.search || '') + ' ' + (card.dataset.tex || '').toLowerCase();
          const matches = !query || haystack.includes(query);
          card.hidden = !matches;
          if (matches) {
            visibleInTopic += 1;
            revealMatches(card.querySelector('.fx-math'), true);
          }
        });

        topic.hidden = visibleInTopic === 0;
        visibleInSubject += visibleInTopic;
      });

      subject.hidden = visibleInSubject === 0;
      visibleFormulas += visibleInSubject;

      if (query) subject.open = visibleInSubject > 0;
    });

    resultCount.textContent = query
      ? visibleFormulas + ' formula' + (visibleFormulas === 1 ? '' : 's') + ' match "' + searchInput.value.trim() + '"'
      : '';

    emptyState.hidden = visibleFormulas !== 0 || !query;
  };

  const showPattern = function (slug, updateHistory) {
    activePattern = slug;
    panels.forEach(function (panel) {
      panel.hidden = panel.dataset.pattern !== slug;
    });
    tabs.forEach(function (tab) {
      const selected = tab.dataset.pattern === slug;
      tab.classList.toggle('is-active', selected);
      tab.setAttribute('aria-current', selected ? 'true' : 'false');
    });
    applyFilter();
    renderMath();
    if (updateHistory) {
      const url = new URL(window.location.href);
      url.searchParams.set('pattern', slug);
      window.history.replaceState({}, '', url);
    }
  };

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function (event) {
      event.preventDefault();
      showPattern(tab.dataset.pattern, true);
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', applyFilter);
    searchInput.addEventListener('search', applyFilter);
  }

  document.getElementById('fx-expand')?.addEventListener('click', function () {
    subjects.forEach(function (subject) {
      if (!subject.hidden) subject.open = true;
    });
  });

  document.getElementById('fx-collapse')?.addEventListener('click', function () {
    subjects.forEach(function (subject) {
      subject.open = false;
    });
  });

  document.getElementById('fx-print')?.addEventListener('click', function () {
    window.print();
  });

  document.getElementById('moocs-signout')?.addEventListener('submit', function () {
    if (typeof window.allowNavigation !== 'undefined') window.allowNavigation = true;
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === '/' && document.activeElement !== searchInput) {
      event.preventDefault();
      searchInput.focus();
    }
    if (event.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.value = '';
      applyFilter();
      searchInput.blur();
    }
  });

  window.addEventListener('katex-ready', renderMath);
  window.addEventListener('load', renderMath);
  if (document.readyState !== 'loading') renderMath();

  showPattern(activePattern, false);
})();
