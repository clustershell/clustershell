(() => {
  'use strict';

  const state = { data: null, benchmark: null, series: null };
  const elements = {
    list: document.getElementById('benchmark-list'),
    title: document.getElementById('benchmark-title'),
    subtitle: document.getElementById('benchmark-subtitle'),
    series: document.getElementById('series-select'),
    environment: document.getElementById('environment'),
    freshness: document.getElementById('freshness'),
    chart: document.getElementById('performance-chart'),
    chartFrame: document.getElementById('chart-frame'),
    tooltip: document.getElementById('chart-tooltip'),
    changeValue: document.getElementById('change-value'),
    changeNote: document.getElementById('change-note'),
    latestResults: document.getElementById('latest-results'),
    regressionList: document.getElementById('regression-list'),
    error: document.getElementById('error-state')
  };

  function svgElement(name, attributes = {}, text) {
    const element = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    if (text !== undefined) element.textContent = text;
    elements.chart.appendChild(element);
    return element;
  }

  function formatDuration(seconds) {
    if (seconds >= 1) return `${seconds.toFixed(2)} s`;
    if (seconds >= 1e-3) return `${(seconds * 1e3).toFixed(seconds < .01 ? 2 : 1)} ms`;
    if (seconds >= 1e-6) return `${(seconds * 1e6).toFixed(seconds < 1e-5 ? 2 : 1)} µs`;
    return `${(seconds * 1e9).toFixed(1)} ns`;
  }

  function formatDate(timestamp) {
    return new Intl.DateTimeFormat('en', { year: 'numeric', month: 'short' }).format(new Date(timestamp));
  }

  function formatIsoDate(timestamp) {
    return new Date(timestamp).toISOString().slice(0, 10);
  }

  function chartXPositions(points, left, right, requestedGap) {
    if (points.length < 2) return [left];
    const span = Math.max(1, points.at(-1).date - points[0].date);
    const gap = Math.min(requestedGap, (right - left) / (points.length - 1));
    const positions = points.map(point => left + ((point.date - points[0].date) / span) * (right - left));

    for (let index = 1; index < positions.length; index += 1) {
      positions[index] = Math.max(positions[index], positions[index - 1] + gap);
    }
    positions[positions.length - 1] = Math.min(positions.at(-1), right);
    for (let index = positions.length - 2; index >= 0; index -= 1) {
      positions[index] = Math.min(positions[index], positions[index + 1] - gap);
    }
    return positions;
  }

  function revisionLabel(point) {
    return point.tags.length ? point.tags.join(', ') : point.shortHash;
  }

  function formatChange(current, previous) {
    if (!previous) return null;
    return ((current / previous) - 1) * 100;
  }

  function renderNavigation() {
    const groups = new Map();
    state.data.benchmarks.forEach(benchmark => {
      if (!groups.has(benchmark.group)) groups.set(benchmark.group, []);
      groups.get(benchmark.group).push(benchmark);
    });
    elements.list.replaceChildren();
    groups.forEach((benchmarks, group) => {
      const section = document.createElement('section');
      section.className = 'benchmark-group';
      const heading = document.createElement('h2');
      heading.textContent = group;
      section.appendChild(heading);
      benchmarks.forEach(benchmark => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'benchmark-button';
        button.dataset.benchmark = benchmark.id;
        button.textContent = benchmark.operation;
        button.addEventListener('click', () => {
          showView('benchmarks');
          selectBenchmark(benchmark.id);
        });
        section.appendChild(button);
      });
      elements.list.appendChild(section);
    });
  }

  function selectBenchmark(benchmarkId) {
    state.benchmark = state.data.benchmarks.find(item => item.id === benchmarkId);
    document.querySelectorAll('.benchmark-button').forEach(button => {
      button.classList.toggle('active', button.dataset.benchmark === benchmarkId);
      button.setAttribute('aria-pressed', String(button.dataset.benchmark === benchmarkId));
    });
    elements.title.textContent = state.benchmark.label;
    elements.subtitle.textContent = 'ClusterShell performance benchmark';
    elements.series.replaceChildren();
    state.benchmark.series.forEach(series => {
      const machine = state.data.machines.find(item => item.id === series.machineId);
      const option = document.createElement('option');
      option.value = series.id;
      option.textContent = series.parameterLabel;
      option.dataset.machine = machine ? `${machine.name} · Python ${machine.python}` : '';
      elements.series.appendChild(option);
    });
    const preferred = state.benchmark.series.find(series => Object.values(series.parameters).includes('100000'));
    state.series = preferred || state.benchmark.series[0];
    elements.series.value = state.series.id;
    updateEnvironment();
    renderChart();
    renderSummary();
  }

  function updateEnvironment() {
    const machine = state.data.machines.find(item => item.id === state.series.machineId);
    elements.environment.textContent = machine ? `${machine.name} · Python ${machine.python}` : 'Unknown environment';
  }

  function renderChart() {
    const points = state.series ? state.series.points : [];
    const width = Math.max(300, elements.chart.clientWidth || 760);
    const height = elements.chart.clientHeight || 390;
    const margin = { top: 28, right: 24, bottom: 45, left: 72 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;
    elements.chart.setAttribute('viewBox', `0 0 ${width} ${height}`);
    elements.chart.replaceChildren();
    svgElement('title', { id: 'chart-title' }, 'Performance over time');
    svgElement('desc', { id: 'chart-description' }, 'Benchmark duration by release and commit.');
    if (!points.length) return;

    const values = points.map(point => point.value);
    const maxValue = Math.max(...values) * 1.16;
    const xPositions = chartXPositions(
      points, margin.left, width - margin.right, width < 520 ? 30 : 44
    );
    const x = index => xPositions[index];
    const y = value => margin.top + innerHeight - (value / maxValue) * innerHeight;

    for (let index = 0; index <= 4; index += 1) {
      const value = maxValue * index / 4;
      const position = y(value);
      svgElement('line', { x1: margin.left, x2: width - margin.right, y1: position, y2: position, class: 'chart-grid' });
      svgElement('text', { x: margin.left - 11, y: position + 4, 'text-anchor': 'end' }, formatDuration(value));
    }
    svgElement('line', { x1: margin.left, x2: margin.left, y1: margin.top, y2: height - margin.bottom, class: 'chart-axis' });
    svgElement('line', { x1: margin.left, x2: width - margin.right, y1: height - margin.bottom, y2: height - margin.bottom, class: 'chart-axis' });

    const tickIndexes = width < 520 ? [0, points.length - 1] : points.map((_, index) => index).filter((_, index) => index % Math.max(1, Math.ceil(points.length / 5)) === 0);
    [...new Set(tickIndexes)].forEach(index => {
      const point = points[index];
      svgElement('text', { x: x(index), y: height - 18, 'text-anchor': index === 0 ? 'start' : index === points.length - 1 ? 'end' : 'middle' }, formatDate(point.date));
    });

    let lastTagPosition = -Infinity;
    points.forEach((point, index) => {
      if (!point.tags.length) return;
      const position = x(index);
      svgElement('line', { x1: position, x2: position, y1: margin.top, y2: height - margin.bottom, class: 'tag-line' });
      if (position - lastTagPosition >= (width < 520 ? 58 : 42)) {
        svgElement('text', { x: position + 4, y: margin.top + 11, class: 'tag-label' }, point.tags.join(', '));
        lastTagPosition = position;
      }
    });

    const path = points.map((point, index) => `${index ? 'L' : 'M'} ${x(index)} ${y(point.value)}`).join(' ');
    const area = `${path} L ${x(points.length - 1)} ${height - margin.bottom} L ${x(0)} ${height - margin.bottom} Z`;
    svgElement('path', { d: area, class: 'chart-area' });
    svgElement('path', { d: path, class: 'chart-line' });

    points.forEach((point, index) => {
      const marker = svgElement('circle', {
        cx: x(index), cy: y(point.value), r: 5,
        class: `chart-point${index === points.length - 1 ? ' latest' : ''}`,
        tabindex: 0,
        'aria-label': `${revisionLabel(point)}: ${formatDuration(point.value)}`
      });
      const showTooltip = () => {
        elements.tooltip.innerHTML = `<strong>${revisionLabel(point)}</strong><code>${point.shortHash}</code><br>${formatDuration(point.value)} · ${formatDate(point.date)}`;
        elements.tooltip.style.display = 'block';
        elements.tooltip.style.left = `${Math.min(width - 185, Math.max(5, x(index) - 70))}px`;
        elements.tooltip.style.top = `${Math.max(3, y(point.value) - 76)}px`;
      };
      marker.addEventListener('mouseenter', showTooltip);
      marker.addEventListener('focus', showTooltip);
      marker.addEventListener('mouseleave', () => { elements.tooltip.style.display = 'none'; });
      marker.addEventListener('blur', () => { elements.tooltip.style.display = 'none'; });
      marker.addEventListener('click', () => { window.open(point.url, '_blank', 'noopener'); });
    });
  }

  function renderSummary() {
    const points = state.series ? state.series.points : [];
    elements.latestResults.replaceChildren();
    if (!points.length) {
      elements.changeValue.textContent = '—';
      elements.changeNote.textContent = 'Waiting for enough measurements.';
      return;
    }

    const first = points[0];
    const latest = points.at(-1);
    const change = points.length > 1 ? formatChange(latest.value, first.value) : null;
    elements.changeValue.classList.remove('faster', 'slower');
    if (change === null) {
      elements.changeValue.textContent = 'First result';
      elements.changeNote.textContent = `${formatDuration(latest.value)} measured at ${revisionLabel(latest)}.`;
    } else {
      const direction = change <= 0 ? 'faster' : 'slower';
      elements.changeValue.classList.add(direction);
      elements.changeValue.textContent = `${change > 0 ? '+' : '−'}${Math.abs(change).toFixed(1)}% ${direction}`;
      elements.changeNote.textContent = `${revisionLabel(first)} to ${revisionLabel(latest)} · ${formatDuration(first.value)} to ${formatDuration(latest.value)}.`;
    }

    points.slice(-3).reverse().forEach(point => {
      const originalIndex = points.indexOf(point);
      const previous = originalIndex > 0 ? points[originalIndex - 1] : null;
      const delta = previous ? formatChange(point.value, previous.value) : null;
      const row = document.createElement('tr');
      const revision = document.createElement('td');
      const link = document.createElement('a');
      link.href = point.url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = revisionLabel(point);
      revision.appendChild(link);
      const duration = document.createElement('td');
      duration.textContent = formatDuration(point.value);
      const variation = document.createElement('td');
      variation.textContent = delta === null ? '—' : `${delta > 0 ? '+' : ''}${delta.toFixed(1)}%`;
      row.append(revision, duration, variation);
      elements.latestResults.appendChild(row);
    });
  }

  function collectRegressions() {
    const regressions = [];
    state.data.benchmarks.forEach(benchmark => {
      benchmark.series.forEach(series => {
        series.points.forEach((point, index) => {
          if (index === 0) return;
          const previous = series.points[index - 1];
          const change = formatChange(point.value, previous.value);
          if (change >= 10) regressions.push({ benchmark, series, previous, point, change });
        });
      });
    });
    return regressions.sort((left, right) => right.change - left.change).slice(0, 25);
  }

  function renderRegressions() {
    const regressions = collectRegressions();
    elements.regressionList.replaceChildren();
    if (!regressions.length) {
      const empty = document.createElement('div');
      empty.className = 'empty-regressions';
      empty.textContent = 'No regression above the 10% threshold.';
      elements.regressionList.appendChild(empty);
      return;
    }
    regressions.forEach(regression => {
      const row = document.createElement('div');
      row.className = 'regression-row';
      const name = document.createElement('span');
      name.className = 'regression-name';
      name.textContent = regression.benchmark.label;
      const dataset = document.createElement('small');
      dataset.textContent = regression.series.parameterLabel;
      name.appendChild(dataset);
      const change = document.createElement('span');
      change.className = 'regression-change';
      change.textContent = `+${regression.change.toFixed(1)}%`;
      const changedAt = document.createElement('a');
      changedAt.className = 'regression-changed';
      changedAt.href = `${state.data.project.repositoryUrl}/compare/${regression.previous.hash}...${regression.point.hash}`;
      changedAt.target = '_blank';
      changedAt.rel = 'noopener';
      changedAt.append(`${formatIsoDate(regression.point.date)} `);
      const commitRange = document.createElement('code');
      commitRange.textContent = `${regression.previous.shortHash}...${regression.point.shortHash}`;
      changedAt.appendChild(commitRange);
      row.append(name, change, changedAt);
      elements.regressionList.appendChild(row);
    });
  }

  function showView(view) {
    document.getElementById('benchmarks-view').hidden = view !== 'benchmarks';
    document.getElementById('regressions-view').hidden = view !== 'regressions';
    document.querySelectorAll('.tab').forEach(tab => {
      const active = tab.dataset.view === view;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-selected', String(active));
    });
    if (view === 'regressions') renderRegressions();
  }

  elements.series.addEventListener('change', () => {
    state.series = state.benchmark.series.find(series => series.id === elements.series.value);
    updateEnvironment();
    renderChart();
    renderSummary();
  });
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => showView(tab.dataset.view));
  });
  new ResizeObserver(renderChart).observe(elements.chartFrame);

  fetch('data.json')
    .then(response => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (!data.benchmarks.length) throw new Error('No benchmark results');
      state.data = data;
      elements.freshness.textContent = data.generatedAt ? `Updated ${new Date(data.generatedAt).toLocaleDateString()}` : 'Results available';
      renderNavigation();
      selectBenchmark(data.benchmarks[0].id);
      renderRegressions();
    })
    .catch(error => {
      console.error(error);
      document.getElementById('benchmarks-view').hidden = true;
      elements.error.hidden = false;
      elements.freshness.textContent = 'Data unavailable';
    });
})();
