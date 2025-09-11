(() => {
  const toastEl = document.getElementById('toast');
  const toastBody = document.getElementById('toast-body');
  const toast = new bootstrap.Toast(toastEl);
  const notify = (msg) => { toastBody.textContent = msg; toast.show(); };

  const setupDropzone = (dzId, inputId, previewContainerId) => {
    const dz = document.getElementById(dzId);
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewContainerId);
    const setPreview = (file) => {
      const url = URL.createObjectURL(file);
      preview.innerHTML = `<img src="${url}" class="preview-img" alt="preview"/>`;
    };
    dz.addEventListener('dragover', (e) => { e.preventDefault(); dz.classList.add('dragover'); });
    dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
    dz.addEventListener('drop', (e) => {
      e.preventDefault(); dz.classList.remove('dragover');
      const file = e.dataTransfer.files?.[0]; if (!file) return; input.files = e.dataTransfer.files; setPreview(file);
    });
    input.addEventListener('change', (e) => { const f = e.target.files?.[0]; if (f) setPreview(f); });
  };

  setupDropzone('dz-classify', 'file-classify', 'preview-classify');
  setupDropzone('dz-similar',  'file-similar',  'preview-similar');

  const spin = (id, show) => document.getElementById(id).classList.toggle('d-none', !show);

  document.getElementById('btn-classify').addEventListener('click', async () => {
    const file = document.getElementById('file-classify').files?.[0];
    if (!file) return notify('이미지를 선택하세요');
    const fd = new FormData(); fd.append('file', file);
    spin('spinner-classify', true);
    try {
      const res = await fetch('/api/v1/dogs/classify', { method: 'POST', body: fd });
      if (!res.ok) throw new Error(await res.text());
      const json = await res.json();
      const items = (json.topk || []).map((x, i) => `
        <tr><td>${i+1}</td><td>${x.label}</td><td>${(x.score*100).toFixed(1)}%</td></tr>`).join('');
      document.getElementById('result-classify').innerHTML = `
        <div class="table-responsive"><table class="table table-sm align-middle">
          <thead><tr><th>#</th><th>견종</th><th>확률</th></tr></thead>
          <tbody>${items}</tbody></table></div>
          <div class="text-muted small">inference: ${json.inference_ms} ms</div>`;
    } catch (e) {
      notify('분류 실패: ' + e.message);
    } finally { spin('spinner-classify', false); }
  });

  document.getElementById('btn-similar').addEventListener('click', async () => {
    const file = document.getElementById('file-similar').files?.[0];
    if (!file) return notify('이미지를 선택하세요');
    const fd = new FormData(); fd.append('file', file);
    spin('spinner-similar', true);
    try {
      const res = await fetch('/api/v1/dogs/search-similar?top_k=8', { method: 'POST', body: fd });
      if (!res.ok) throw new Error(await res.text());
      const { results } = await res.json();
      const html = (results || []).map(r => `
        <div class="col"><div class="card h-100">
          <img src="${r.url}" class="card-img-top" alt="${r.breed}"/>
          <div class="card-body p-2">
            <div class="small fw-semibold">${r.breed || 'Unknown'}</div>
            <div class="small text-muted">sim ${(r.similarity||0).toFixed(2)}</div>
          </div>
        </div></div>`).join('');
      document.getElementById('result-similar').innerHTML = html || '<div class="text-muted">결과 없음</div>';
    } catch (e) {
      notify('검색 실패: ' + e.message);
    } finally { spin('spinner-similar', false); }
  });

  document.getElementById('btn-copy').addEventListener('click', async () => {
    const breed = document.getElementById('breed').value.trim();
    const traits = document.getElementById('traits').value.split(',').map(s=>s.trim()).filter(Boolean);
    const age = document.getElementById('age').value.trim();
    if (!breed) return notify('견종을 입력하세요');
    spin('spinner-copy', true);
    try {
      const res = await fetch('/api/v1/text/adoption-copy', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ breed, traits, age, tone: '따뜻하고 간결' })
      });
      if (!res.ok) throw new Error(await res.text());
      const { copy } = await res.json();
      document.getElementById('result-copy').innerHTML = `
        <div class="alert alert-warning mb-0">${copy}</div>`;
    } catch (e) {
      notify('문구 생성 실패: ' + e.message);
    } finally { spin('spinner-copy', false); }
  });
})();
