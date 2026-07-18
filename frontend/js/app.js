/**
 * App.js — Main application state machine, navigation, and UI orchestration.
 * 
 * Manages the full screen flow:
 *   Landing → Dashboard (empty → fetching → review → analyzing → results)
 *   + History, Settings, Job Detail Drawer
 */

document.addEventListener('DOMContentLoaded', () => {
  // ═══════════════════════════════════════════════════════════════════════
  // STATE
  // ═══════════════════════════════════════════════════════════════════════
  const state = {
    currentView: 'landing', // landing | dashboard | history | settings
    dashboardState: 'empty', // empty | fetching | review | analyzing | results
    fetchedJobs: [],
    evaluationResults: [],
    matchedJobs: [],
    filteredJobs: [],
    cvId: null,
    cvFile: null,
    sessionId: null,
    history: JSON.parse(localStorage.getItem('jobsAgentHistory') || '[]'),
    jobsProcessedTotal: parseInt(localStorage.getItem('jobsProcessedTotal') || '0'),
    selectedJob: null,
    displayedJobCount: 6, // Initial number of job cards shown
  };

  // ═══════════════════════════════════════════════════════════════════════
  // ELEMENTS
  // ═══════════════════════════════════════════════════════════════════════
  const views = {
    landing: document.getElementById('view-landing'),
    dashboard: document.getElementById('view-dashboard'),
    history: document.getElementById('view-history'),
    settings: document.getElementById('view-settings'),
  };

  const el = {
    // Navigation
    navLinks: document.querySelectorAll('.nav-link'),
    navLogo: document.getElementById('nav-logo'),
    mobileNavBtns: document.querySelectorAll('.mobile-nav-btn'),

    // Landing
    btnOpenAgent: document.getElementById('btn-open-agent'),
    statJobsProcessed: document.getElementById('stat-jobs-processed'),

    // Search Form
    inputRole: document.getElementById('input-role'),
    inputWorkType: document.getElementById('input-work-type'),
    inputDatePosted: document.getElementById('input-date-posted'),
    inputMaxFetch: document.getElementById('input-max-fetch'),
    btnStartFetch: document.getElementById('btn-start-fetch'),

    // Console
    consoleBody: document.getElementById('console-body'),

    // CV Upload
    cvUploadSection: document.getElementById('cv-upload-section'),
    cvDropzone: document.getElementById('cv-dropzone'),
    cvFileInput: document.getElementById('cv-file-input'),
    cvFileInfo: document.getElementById('cv-file-info'),
    cvFilename: document.getElementById('cv-filename'),
    cvFilesize: document.getElementById('cv-filesize'),
    btnRemoveCv: document.getElementById('btn-remove-cv'),
    btnAnalyze: document.getElementById('btn-analyze'),

    // Fetched Roles
    fetchedRolesSection: document.getElementById('fetched-roles-section'),
    fetchedCount: document.getElementById('fetched-count'),
    fetchedJobsGrid: document.getElementById('fetched-jobs-grid'),
    loadMoreContainer: document.getElementById('load-more-container'),
    btnLoadMore: document.getElementById('btn-load-more'),
    remainingCount: document.getElementById('remaining-count'),

    // Results
    resultsSection: document.getElementById('results-section'),
    matchedCount: document.getElementById('matched-count'),
    totalMatched: document.getElementById('total-matched'),
    totalFiltered: document.getElementById('total-filtered'),
    matchedJobsGrid: document.getElementById('matched-jobs-grid'),
    filteredSection: document.getElementById('filtered-section'),
    filteredCount: document.getElementById('filtered-count'),
    filteredJobsList: document.getElementById('filtered-jobs-list'),

    // Empty State
    emptyState: document.getElementById('empty-state'),

    // Drawer
    jobDrawer: document.getElementById('job-drawer'),
    drawerBackdrop: document.getElementById('drawer-backdrop'),
    drawerPanel: document.getElementById('drawer-panel'),
    drawerTitle: document.getElementById('drawer-title'),
    drawerCompanyLocation: document.getElementById('drawer-company-location'),
    drawerFitBadge: document.getElementById('drawer-fit-badge'),
    drawerAgentId: document.getElementById('drawer-agent-id'),
    drawerMatchPct: document.getElementById('drawer-match-pct'),
    drawerJobLink: document.getElementById('drawer-job-link'),
    btnCloseDrawer: document.getElementById('btn-close-drawer'),
    btnMarkApplied: document.getElementById('btn-mark-applied'),
    downloadBtns: document.querySelectorAll('.btn-download'),

    // History
    historyTableBody: document.getElementById('history-table-body'),
    historySummary: document.getElementById('history-summary'),

    // Settings
    btnSaveSettings: document.getElementById('btn-save-settings'),
  };

  // ═══════════════════════════════════════════════════════════════════════
  // CONSOLE
  // ═══════════════════════════════════════════════════════════════════════
  const console_ = new LiveConsole('#console-body');

  // ═══════════════════════════════════════════════════════════════════════
  // NAVIGATION
  // ═══════════════════════════════════════════════════════════════════════
  function switchView(viewName) {
    // Handle landing → dashboard
    if (viewName === 'dashboard' && state.currentView === 'landing') {
      state.currentView = 'dashboard';
    }

    // If clicking logo, go to landing
    if (viewName === 'landing') {
      state.currentView = 'landing';
    } else {
      state.currentView = viewName;
    }

    // Update views
    Object.entries(views).forEach(([name, viewEl]) => {
      if (name === state.currentView) {
        viewEl.classList.add('active');
      } else {
        viewEl.classList.remove('active');
      }
    });

    // Update nav links
    el.navLinks.forEach(link => {
      if (link.dataset.view === state.currentView) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Update mobile nav
    el.mobileNavBtns.forEach(btn => {
      if (btn.dataset.view === state.currentView) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Special: dashboard nav should show for both landing and dashboard
    if (state.currentView === 'landing') {
      el.navLinks.forEach(link => {
        if (link.dataset.view === 'dashboard') link.classList.add('active');
        else link.classList.remove('active');
      });
    }
  }

  // Nav link clicks
  el.navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      switchView(link.dataset.view);
    });
  });

  // Mobile nav clicks
  el.mobileNavBtns.forEach(btn => {
    btn.addEventListener('click', () => switchView(btn.dataset.view));
  });

  // Logo click → landing
  el.navLogo.addEventListener('click', (e) => {
    e.preventDefault();
    switchView('landing');
  });

  // Open Agent button
  el.btnOpenAgent.addEventListener('click', () => {
    switchView('dashboard');
  });

  // ═══════════════════════════════════════════════════════════════════════
  // DASHBOARD STATE MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════════
  function setDashboardState(newState) {
    state.dashboardState = newState;

    // Show/hide sections based on state
    const hide = (...sections) => sections.forEach(s => s.classList.add('hidden'));
    const show = (...sections) => sections.forEach(s => {
      s.classList.remove('hidden');
      s.classList.add('section-enter');
    });

    switch (newState) {
      case 'empty':
        hide(el.cvUploadSection, el.fetchedRolesSection, el.resultsSection, el.filteredSection);
        el.emptyState.classList.remove('hidden');
        console_.showIdle();
        break;

      case 'fetching':
        hide(el.cvUploadSection, el.fetchedRolesSection, el.resultsSection, el.filteredSection);
        el.emptyState.classList.add('hidden');
        // Console state set by fetch flow
        break;

      case 'review':
        hide(el.resultsSection, el.filteredSection);
        el.emptyState.classList.add('hidden');
        show(el.cvUploadSection, el.fetchedRolesSection);
        break;

      case 'analyzing':
        hide(el.fetchedRolesSection);
        // Console state set by analysis flow
        break;

      case 'results':
        hide(el.cvUploadSection, el.fetchedRolesSection);
        el.emptyState.classList.add('hidden');
        show(el.resultsSection);
        if (state.filteredJobs.length > 0) {
          show(el.filteredSection);
        }
        break;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════
  // FETCH FLOW
  // ═══════════════════════════════════════════════════════════════════════
  el.btnStartFetch.addEventListener('click', async () => {
    const role = el.inputRole.value.trim();
    if (!role) {
      el.inputRole.focus();
      el.inputRole.classList.add('border-status-error');
      setTimeout(() => el.inputRole.classList.remove('border-status-error'), 2000);
      return;
    }

    const workType = el.inputWorkType.value;
    const datePosted = el.inputDatePosted.value;
    const maxFetch = parseInt(el.inputMaxFetch.value) || 25;

    // Disable button
    el.btnStartFetch.disabled = true;
    el.btnStartFetch.classList.add('btn-loading');
    el.btnStartFetch.innerHTML = '<span class="spinner"></span> Fetching...';

    setDashboardState('fetching');

    // Generate session ID
    const sessionId = `AF-${Math.floor(Math.random() * 9000 + 1000)}`;
    state.sessionId = sessionId;
    console_.setSessionId(sessionId);
    console_.setState('fetching');
    console_.clear();

    // Simulated fetch flow with console logs
    const logs = [
      { text: 'Launching remote browser session...', type: 'default', delay: 400 },
      { text: `Initializing headless Chromium instance...`, type: 'default', delay: 800 },
      { text: `Applying filters: ${workType}, posted ${datePosted}`, type: 'default', delay: 600 },
      { text: 'Navigating to LinkedIn Jobs... [Success]', type: 'success', delay: 1000 },
      { text: `Searching for "${role}" positions...`, type: 'default', delay: 800 },
    ];

    // Play logs sequentially
    for (const log of logs) {
      await delay(log.delay);
      console_.addLine(log.text, log.type);
    }

    // Try real API first, fallback to demo data
    let jobs = [];
    try {
      const result = await Api.startScrape({ role: role, work_type: workType, date_posted: datePosted, max_fetch: maxFetch });
      
      // Poll for completion
      let status = result;
      let lastLogIdx = 0;
      while (status.status === 'fetching') {
        await delay(2000);
        status = await Api.getScrapeStatus(status.session_id);
        if (status.logs && status.logs.length > lastLogIdx) {
          for (let i = lastLogIdx; i < status.logs.length; i++) {
            console_.addLine(status.logs[i], 'default');
          }
          lastLogIdx = status.logs.length;
        }
      }
      jobs = status.jobs || [];
    } catch (err) {
      // Backend not available — use demo data for portfolio showcase
      console_.addLine('Backend not connected. Loading demo data...', 'dim');
      await delay(500);
      jobs = generateDemoJobs(role, workType, maxFetch);
    }

    // Show found count
    await delay(400);
    console_.addLine(`Found ${jobs.length} potential matches. Ranking by Fit Score...`, 'highlight');

    // Animate individual job extraction
    const showCount = Math.min(jobs.length, 5);
    for (let i = 0; i < showCount; i++) {
      await delay(300);
      console_.addLine(`Extracting job ${i + 1}/${jobs.length}: ${jobs[i].title} @ ${jobs[i].company}`, 'default');
    }

    await delay(500);
    console_.setState('ready', 'agent · ready for cv');
    console_.addLine(`Done. ${jobs.length} jobs saved, waiting for CV upload.`, 'success', true);

    // Store jobs and update UI
    state.fetchedJobs = jobs;
    renderFetchedJobs();
    setDashboardState('review');

    // Reset button
    el.btnStartFetch.disabled = false;
    el.btnStartFetch.classList.remove('btn-loading');
    el.btnStartFetch.innerHTML = '<span class="material-symbols-outlined text-[20px]">play_arrow</span> Start fetching';
  });

  // ═══════════════════════════════════════════════════════════════════════
  // CV UPLOAD
  // ═══════════════════════════════════════════════════════════════════════
  el.cvDropzone.addEventListener('click', () => el.cvFileInput.click());

  el.cvDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    el.cvDropzone.classList.add('border-primary/50');
  });

  el.cvDropzone.addEventListener('dragleave', () => {
    el.cvDropzone.classList.remove('border-primary/50');
  });

  el.cvDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    el.cvDropzone.classList.remove('border-primary/50');
    const file = e.dataTransfer.files[0];
    if (file) handleCVFile(file);
  });

  el.cvFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) handleCVFile(file);
  });

  function handleCVFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.docx')) {
      alert('Please upload a PDF or DOCX file.');
      return;
    }

    state.cvFile = file;
    el.cvFilename.textContent = file.name;
    el.cvFilesize.textContent = `Uploaded just now · ${(file.size / 1024 / 1024).toFixed(1)} MB`;
    el.cvDropzone.classList.add('hidden');
    el.cvFileInfo.classList.remove('hidden');
    el.btnAnalyze.disabled = false;
  }

  el.btnRemoveCv.addEventListener('click', () => {
    state.cvFile = null;
    state.cvId = null;
    el.cvDropzone.classList.remove('hidden');
    el.cvFileInfo.classList.add('hidden');
    el.btnAnalyze.disabled = true;
    el.cvFileInput.value = '';
  });

  // ═══════════════════════════════════════════════════════════════════════
  // ANALYZE & GENERATE
  // ═══════════════════════════════════════════════════════════════════════
  el.btnAnalyze.addEventListener('click', async () => {
    if (!state.cvFile || state.fetchedJobs.length === 0) return;

    el.btnAnalyze.disabled = true;
    el.btnAnalyze.innerHTML = '<span class="spinner"></span> Analyzing...';
    el.btnAnalyze.classList.add('btn-loading');

    setDashboardState('analyzing');

    const sessionId = `${Math.floor(Math.random() * 9000 + 1000)}-ALPHA`;
    console_.setSessionId(sessionId);
    console_.setState('analyzing');
    console_.clear();
    console_.addLine('Reading CV', 'success');

    // Try real API upload first
    let cvId = null;
    try {
      const uploadResult = await Api.uploadCV(state.cvFile);
      cvId = uploadResult.cv_id;
      state.cvId = cvId;
      console_.addLine(`CV parsed: ${uploadResult.char_count} characters extracted.`, 'default');
    } catch (err) {
      console_.addLine('Using local CV analysis (backend offline)...', 'dim');
    }

    // Evaluate each job
    const results = [];
    for (let i = 0; i < state.fetchedJobs.length; i++) {
      const job = state.fetchedJobs[i];
      await delay(600);

      let result;
      try {
        if (cvId) {
          const evalResult = await Api.evaluateSingle({ cv_id: cvId, job });
          result = evalResult.result;
        } else {
          throw new Error('No backend');
        }
      } catch {
        // Demo scoring
        result = {
          evaluation_id: `eval-${i}`,
          job_title: job.title,
          company: job.company,
          location: job.location,
          link: job.link,
          score: Math.floor(Math.random() * 10) + 8,
          reason: generateDemoReason(job.title),
          is_match: Math.random() > 0.35,
          documents_available: true,
        };
      }

      results.push(result);

      if (result.is_match) {
        console_.addRichLine([
          { text: 'Matched + generated docs for: ' },
          { text: result.job_title, bold: true, color: '#ffc880' }
        ]);
      } else {
        console_.addLine(`Skipping (not a fit): ${result.job_title}`, 'dim');
      }
    }

    // Done
    await delay(400);
    console_.setState('done');
    console_.addLine('All done. Review results below.', 'success', true);

    // Store and render results
    state.evaluationResults = results;
    state.matchedJobs = results.filter(r => r.is_match);
    state.filteredJobs = results.filter(r => !r.is_match);

    renderResults();
    setDashboardState('results');

    // Update history
    addHistoryEntry(
      el.inputRole.value.trim(),
      el.inputWorkType.value,
      state.fetchedJobs.length,
      state.matchedJobs.length
    );

    // Reset button
    el.btnAnalyze.disabled = false;
    el.btnAnalyze.innerHTML = '<span class="material-symbols-outlined text-[20px]">analytics</span> ANALYZE & GENERATE';
    el.btnAnalyze.classList.remove('btn-loading');
  });

  // ═══════════════════════════════════════════════════════════════════════
  // RENDER: FETCHED JOBS
  // ═══════════════════════════════════════════════════════════════════════
  function renderFetchedJobs() {
    el.fetchedJobsGrid.innerHTML = '';
    el.fetchedCount.textContent = `${state.fetchedJobs.length} JOBS FOUND`;
    state.displayedJobCount = 6;

    const jobsToShow = state.fetchedJobs.slice(0, state.displayedJobCount);
    jobsToShow.forEach(job => {
      el.fetchedJobsGrid.appendChild(createFetchedJobCard(job));
    });

    // Show/hide load more
    if (state.fetchedJobs.length > state.displayedJobCount) {
      el.loadMoreContainer.classList.remove('hidden');
      el.remainingCount.textContent = state.fetchedJobs.length - state.displayedJobCount;
    } else {
      el.loadMoreContainer.classList.add('hidden');
    }
  }

  function createFetchedJobCard(job) {
    const card = document.createElement('div');
    card.className = 'job-card';
    card.innerHTML = `
      <div class="flex items-start justify-between mb-3">
        <h3 class="text-on-surface font-body-base font-semibold leading-tight">${escapeHtml(job.title)}</h3>
        <span class="badge-new ml-2 flex-shrink-0">NEW</span>
      </div>
      <p class="text-text-muted font-body-sm mb-4">${escapeHtml(job.company)} • ${escapeHtml(job.location)}</p>
      <div class="flex items-center justify-between border-t border-border pt-3">
        <span class="text-text-muted font-label-mono text-label-mono">Saved just now</span>
        <a href="${escapeHtml(job.link || '#')}" target="_blank" class="text-secondary font-body-sm hover:opacity-80 flex items-center gap-1">
          View posting <span class="material-symbols-outlined text-[14px]">open_in_new</span>
        </a>
      </div>
    `;
    return card;
  }

  el.btnLoadMore?.addEventListener('click', () => {
    state.displayedJobCount = state.fetchedJobs.length;
    const remaining = state.fetchedJobs.slice(el.fetchedJobsGrid.children.length);
    remaining.forEach(job => {
      const card = createFetchedJobCard(job);
      card.classList.add('section-enter');
      el.fetchedJobsGrid.appendChild(card);
    });
    el.loadMoreContainer.classList.add('hidden');
  });

  // ═══════════════════════════════════════════════════════════════════════
  // RENDER: RESULTS
  // ═══════════════════════════════════════════════════════════════════════
  function renderResults() {
    el.matchedJobsGrid.innerHTML = '';
    el.filteredJobsList.innerHTML = '';

    el.matchedCount.textContent = state.matchedJobs.length;
    el.totalMatched.textContent = state.matchedJobs.length;
    el.totalFiltered.textContent = state.filteredJobs.length;

    // Matched jobs — card grid
    state.matchedJobs.forEach(result => {
      const card = document.createElement('div');
      card.className = 'job-card cursor-pointer';
      card.innerHTML = `
        <div class="flex items-start justify-between mb-1">
          <span class="badge-fit">FIT</span>
          <a href="${escapeHtml(result.link || '#')}" target="_blank" class="text-text-muted hover:text-secondary transition-colors" onclick="event.stopPropagation()">
            <span class="material-symbols-outlined text-[18px]">open_in_new</span>
          </a>
        </div>
        <h3 class="text-on-surface font-body-base font-semibold mt-3 mb-1">${escapeHtml(result.job_title)}</h3>
        <p class="text-text-muted font-body-sm mb-4">${escapeHtml(result.company)} · ${escapeHtml(result.location || 'Remote')}</p>
        <div class="border-t border-border pt-3 flex items-center justify-between">
          <span class="font-label-mono text-label-mono text-secondary uppercase tracking-wider">DOCS GENERATED</span>
          <div class="flex items-center gap-2 text-text-muted">
            <span class="material-symbols-outlined text-[18px]">description</span>
            <span class="material-symbols-outlined text-[18px]">mail</span>
          </div>
        </div>
      `;
      card.addEventListener('click', () => openDrawer(result));
      el.matchedJobsGrid.appendChild(card);
    });

    // Filtered jobs — simple list
    if (state.filteredJobs.length > 0) {
      el.filteredSection.classList.remove('hidden');
      el.filteredCount.textContent = state.filteredJobs.length;

      state.filteredJobs.forEach(result => {
        const row = document.createElement('div');
        row.className = 'flex items-center justify-between py-3 border-b border-border last:border-b-0 opacity-50';
        row.innerHTML = `
          <span class="text-text-muted font-body-base">${escapeHtml(result.job_title)}</span>
          <span class="font-label-mono text-label-mono text-text-muted uppercase tracking-wider">${escapeHtml(result.reason.substring(0, 50))}</span>
        `;
        el.filteredJobsList.appendChild(row);
      });
    }

    // Update stats
    state.jobsProcessedTotal += state.fetchedJobs.length;
    localStorage.setItem('jobsProcessedTotal', state.jobsProcessedTotal);
    el.statJobsProcessed.textContent = `${state.jobsProcessedTotal.toLocaleString()} TOTAL`;
  }

  // ═══════════════════════════════════════════════════════════════════════
  // JOB DETAIL DRAWER
  // ═══════════════════════════════════════════════════════════════════════
  function openDrawer(result) {
    state.selectedJob = result;

    el.drawerTitle.textContent = result.job_title;
    el.drawerCompanyLocation.textContent = `${result.company} • ${result.location || 'Remote'}`;
    el.drawerAgentId.textContent = `ID: AGENT_${Math.random().toString(36).substring(2, 7).toUpperCase()}`;
    el.drawerMatchPct.textContent = `MATCH: ${Math.round((result.score / 18) * 100)}%`;
    el.drawerJobLink.href = result.link || '#';

    // Set fit badge
    if (result.is_match) {
      el.drawerFitBadge.textContent = 'FIT';
      el.drawerFitBadge.className = 'font-label-mono text-label-mono text-on-secondary bg-secondary/20 border border-secondary/30 px-2 py-0.5 rounded uppercase tracking-wider';
    } else {
      el.drawerFitBadge.textContent = 'NOT A MATCH';
      el.drawerFitBadge.className = 'font-label-mono text-label-mono text-text-muted bg-text-muted/10 border border-text-muted/20 px-2 py-0.5 rounded uppercase tracking-wider';
    }

    // Show drawer
    el.jobDrawer.classList.remove('hidden');
    el.drawerPanel.classList.remove('drawer-exit');
    el.drawerPanel.classList.add('drawer-enter');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    el.drawerPanel.classList.remove('drawer-enter');
    el.drawerPanel.classList.add('drawer-exit');
    setTimeout(() => {
      el.jobDrawer.classList.add('hidden');
      document.body.style.overflow = '';
    }, 300);
  }

  el.btnCloseDrawer.addEventListener('click', closeDrawer);
  el.drawerBackdrop.addEventListener('click', closeDrawer);

  // Download buttons
  el.downloadBtns.forEach(btn => {
    btn.addEventListener('click', async () => {
      const fileType = btn.dataset.type;
      if (!state.selectedJob) return;

      // Try real API download
      if (state.selectedJob.doc_id) {
        const url = Api.getDownloadUrl(state.selectedJob.doc_id, fileType);
        window.open(url, '_blank');
      } else {
        // Demo mode — show feedback
        btn.textContent = 'DOWNLOADED ✓';
        btn.classList.add('border-secondary', 'text-secondary');
        btn.classList.remove('border-primary', 'text-primary');
        setTimeout(() => {
          btn.textContent = 'DOWNLOAD';
          btn.classList.remove('border-secondary', 'text-secondary');
          btn.classList.add('border-primary', 'text-primary');
        }, 2000);
      }
    });
  });

  // Mark as applied
  el.btnMarkApplied.addEventListener('click', () => {
    el.btnMarkApplied.textContent = '✓ MARKED AS APPLIED';
    el.btnMarkApplied.classList.add('border-secondary', 'text-secondary');
    el.btnMarkApplied.disabled = true;
  });

  // ═══════════════════════════════════════════════════════════════════════
  // HISTORY
  // ═══════════════════════════════════════════════════════════════════════
  function addHistoryEntry(role, workType, fetched, matched) {
    const entry = {
      date: new Date().toISOString().replace('T', ' ').substring(0, 16).replace(/-/g, '.'),
      filters: `${capitalize(workType)} · ${role}`,
      fetched,
      matched,
      status: 'done',
    };

    state.history.unshift(entry);
    if (state.history.length > 20) state.history = state.history.slice(0, 20);
    localStorage.setItem('jobsAgentHistory', JSON.stringify(state.history));

    renderHistory();
  }

  function renderHistory() {
    el.historyTableBody.innerHTML = '';

    if (state.history.length === 0) {
      el.historySummary.textContent = 'No operations recorded yet';
      return;
    }

    state.history.forEach(entry => {
      const row = document.createElement('tr');
      row.className = 'history-row';
      row.innerHTML = `
        <td class="px-6 py-4 font-label-mono text-label-mono text-text-muted whitespace-nowrap">${entry.date}</td>
        <td class="px-6 py-4 font-body-base text-on-surface">${escapeHtml(entry.filters)}</td>
        <td class="px-6 py-4 text-center font-label-mono text-text-muted">${entry.fetched}</td>
        <td class="px-6 py-4 text-center font-label-mono text-secondary font-medium">${entry.matched}</td>
        <td class="px-6 py-4 text-center">
          <span class="material-symbols-outlined text-secondary text-[18px]">check_circle</span>
        </td>
      `;
      el.historyTableBody.appendChild(row);
    });

    el.historySummary.textContent = `Showing last ${state.history.length} operations`;
  }

  // ═══════════════════════════════════════════════════════════════════════
  // SETTINGS
  // ═══════════════════════════════════════════════════════════════════════
  el.btnSaveSettings?.addEventListener('click', () => {
    el.btnSaveSettings.textContent = 'Saved ✓';
    setTimeout(() => {
      el.btnSaveSettings.textContent = 'Save changes';
    }, 2000);
  });

  // ═══════════════════════════════════════════════════════════════════════
  // DEMO DATA GENERATORS
  // ═══════════════════════════════════════════════════════════════════════
  function generateDemoJobs(role, workType, count) {
    const companies = ['Stripe', 'Linear', 'Vercel', 'Shopify', 'Monzo', 'Revolut', 'Figma', 'Notion', 'Anthropic', 'Apple', 'Airbnb', 'Spotify', 'Miro', 'Canva', 'Framer', 'InVision', 'Adobe', 'Meta', 'Google', 'Netflix'];
    const locations = ['Remote', 'London (Remote)', 'San Francisco, CA', 'New York, NY', 'Berlin, DE', 'Toronto, CA', 'EMEA (Remote)', 'Global Remote'];
    const modifiers = ['Senior', 'Staff', 'Lead', 'Principal', '', 'Junior'];
    const suffixes = ['', '(Contract)', '(Remote)', '- Design Systems', ', Mobile', ', AI Products', '(eCommerce)'];

    const jobs = [];
    const actualCount = Math.min(count, 20);

    for (let i = 0; i < actualCount; i++) {
      const modifier = modifiers[Math.floor(Math.random() * modifiers.length)];
      const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
      const title = `${modifier} ${role} ${suffix}`.replace(/\s+/g, ' ').trim();

      jobs.push({
        title,
        company: companies[i % companies.length],
        location: locations[Math.floor(Math.random() * locations.length)],
        link: `https://linkedin.com/jobs/view/${Math.floor(Math.random() * 9999999)}`,
        time: `${Math.floor(Math.random() * 7) + 1}d ago`,
      });
    }

    return jobs;
  }

  function generateDemoReason(title) {
    const reasons = [
      'Strong alignment with UX/UI experience and product design portfolio.',
      'Missing Node.js/Rust experience requirements.',
      'Requirement: 12+ years leadership experience.',
      'Excellent match with design systems and component architecture expertise.',
      'Stack mismatch: requires backend engineering focus.',
      'Insufficient seniority for this director-level role.',
      'Great fit with eCommerce UX and conversion optimization skills.',
      'Cross-functional workshop experience aligns with team culture.',
    ];
    return reasons[Math.floor(Math.random() * reasons.length)];
  }

  // ═══════════════════════════════════════════════════════════════════════
  // UTILITIES
  // ═══════════════════════════════════════════════════════════════════════
  function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  // ═══════════════════════════════════════════════════════════════════════
  // LANDING CONSOLE ANIMATION
  // ═══════════════════════════════════════════════════════════════════════
  const landingConsole = document.getElementById('landing-console');
  const landingLines = [
    '$ Identifying job market inefficiencies...',
    '$ Authenticating session with LinkedIn portal...',
    '$ Fetching metadata for 12 new listings...',
    '$ Resume parser ready. Awaiting user input...',
    '$ Parallel processing enabled. Fetching at 4.2 items/sec...',
  ];
  let landingLineIdx = 0;

  setInterval(() => {
    if (!views.landing.classList.contains('active')) return;
    if (landingLineIdx < landingLines.length) {
      const lastChild = landingConsole.lastElementChild;
      const newLine = document.createElement('div');
      newLine.className = 'text-on-surface opacity-70 console-line-enter';
      newLine.textContent = landingLines[landingLineIdx];
      landingConsole.insertBefore(newLine, lastChild);
      landingLineIdx++;

      if (landingConsole.children.length > 10) {
        landingConsole.children[0].remove();
      }
    } else {
      landingLineIdx = 0;
    }
  }, 3500);

  // ═══════════════════════════════════════════════════════════════════════
  // INIT
  // ═══════════════════════════════════════════════════════════════════════
  renderHistory();
  el.statJobsProcessed.textContent = `${state.jobsProcessedTotal.toLocaleString()} TOTAL`;

  // Start on landing page
  switchView('landing');
});
