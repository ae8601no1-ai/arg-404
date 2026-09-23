async function request(path, payload) {
  const response = await fetch(path, {
    method: 'POST', headers: {'Content-Type': 'application/json', 'X-ARG-Request': '1'},
    body: JSON.stringify(payload), cache: 'no-store', credentials: 'same-origin'
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.message || '照合できませんでした。');
  return result;
}
// Earlier static prototypes stored a destination here; it cannot grant access now.
try { localStorage.removeItem('arg404-last'); } catch (_) {}
document.querySelectorAll('form[data-puzzle]').forEach(form => {
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const input = form.querySelector('input');
    const button = form.querySelector('button');
    const status = form.querySelector('[role="status"]');
    button.disabled = true;
    status.textContent = '資料を照合しています…';
    try {
      const result = await request('/api/solve', {puzzle: form.dataset.puzzle, answer: input.value});
      input.removeAttribute('aria-invalid');
      window.location.assign(result.next);
    } catch (error) {
      input.setAttribute('aria-invalid', 'true');
      status.textContent = error instanceof TypeError ? '接続できません。サーバーの起動を確認して再試行してください。' : error.message;
    } finally { button.disabled = false; }
  });
});
document.querySelectorAll('[data-reset]').forEach(button => button.addEventListener('click', async () => {
  button.disabled = true;
  try { await request('/api/reset', {}); window.location.assign('/'); }
  catch (_) { button.disabled = false; button.textContent = '接続を確認して、もう一度やり直す'; }
}));
const resume = document.querySelector('[data-resume]');
if (resume) {
  fetch('/api/progress', {cache: 'no-store', credentials: 'same-origin'})
    .then(response => { if (!response.ok) throw new Error(); return response.json(); })
    .then(state => { if (state.resume) { resume.href = state.resume; resume.hidden = false; } })
    .catch(() => {});
}
// A page restored from back/forward cache must be checked against current progress.
window.addEventListener('pageshow', event => { if (event.persisted) window.location.reload(); });
