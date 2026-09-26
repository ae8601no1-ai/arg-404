const PUZZLE_META = {
  p1: {message: '照合一致。整理票1104の人物名は「水城七海」。冬真が次に開いた新聞の保存束が見つかりました。', note: '佐伯からの追送：同じ人名で切り抜きを探したところ、結末が二つある記事が出てきた。', link: '二つの新聞記録を開く →'},
  p2: {message: '照合一致。二つの記事は同じ記事IDでした。冬真が次に保存したSNS記録を確認できます。', note: '冬真メモ：死亡と行方不明が同じ記事IDなら、訂正ではなく記録の差し替えかもしれない。', link: '七海のSNSを開く →'},
  p3: {message: '照合一致。七海の最後の投稿時刻が確定しました。次は同時刻の玄関カメラです。', note: '冬真メモ：16:51に着いたなら、玄関の入退館記録と一致するはずだ。', link: '玄関カメラの転記を開く →'},
  p4: {message: '照合一致。入館から退出までは11分でした。11分のあいだに別人へのすり替えが起きた可能性があります。', note: '佐伯メモ：冬真は「出てきたのが同じ人とは限らない」と付箋を残していた。', link: '2026年の写真を開く →'},
  p5: {message: '照合一致。第四資料館は地上3階建て。4階の少女は現実の窓ではありません。', note: '冬真メモ：怪異じゃない。加工された写真が配られた経路を追うべきだ。', link: '404の意味を調べる →'},
  p6: {message: '照合一致。旧番号404は B1-04 でした。次は地下区画に残る調査者一覧です。', note: '佐伯からの追送：B1-04 の保管箱に、七海を追った人たちの一覧が残っていた。', link: '調査者一覧を開く →'},
  p7: {message: '照合一致。事件は3年ごとに繰り返されていました。冬真は6人目の調査者です。', note: '冬真メモ：これは七海一人の事件じゃない。七海を調べた側の事件だ。', link: '原本閲覧会の招待状を開く →'},
  p8: {message: '照合一致。次の照合監査年は2029年です。誰かが日付を決めて人を呼び集めていました。', note: '佐伯メモ：招待状は個人のいたずらではなく、組織的な文面に見える。', link: '事業主体の資料を開く →'},
  p9: {message: '照合一致。事業主体は静浜記録技研。ここから先は個人の噂ではなく、組織の内部記録です。', note: '冬真メモ：Nの言う「台帳」は、会社の管理資料だ。', link: '人格生成台帳を開く →'},
  p10: {message: '照合一致。水城七海の試験IDは N-04。七海は人名ではなく、作られた人格でした。', note: '冬真メモ：名前を追っても実在の人物には届かない。写真に使われた本当の人を探す。', link: 'Nの手記を開く →'},
  p11: {message: '照合一致。Nの本名は新堂奈緒。17:02に制服で出たのは彼女でした。', note: '奈緒はあの日、妹だけを地下に残して外へ出た。その後悔から、15年間内部資料を持ち出し続けていた。次は妹の記録を追う。', link: '撮影対象台帳を開く →'},
  p12: {message: '照合一致。写真に写った実在の少女は M-17 でした。', note: '冬真メモ：七海を探すな。M-17の外部保管台帳を探せ。', link: '原記録 M-17 を開く →'},
  p13: {message: '照合一致。M-17の本名は新堂澪。奈緒が15年間取り戻そうとしていた妹です。', note: '奈緒が外へ送った施設経路と入所者記録をもとに、救出が始まった。最後の記録を確認する。', link: '最後の記録を開く →'}
};

async function request(path, payload) {
  const response = await fetch(path, {
    method: 'POST', headers: {'Content-Type': 'application/json', 'X-ARG-Request': '1'},
    body: JSON.stringify(payload), cache: 'no-store', credentials: 'same-origin'
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.message || '照合できませんでした。');
  return result;
}
try { localStorage.removeItem('arg404-last'); } catch (_) {}
document.querySelectorAll('form[data-puzzle]').forEach(form => {
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const input = form.querySelector('input');
    const button = form.querySelector('button');
    const status = form.querySelector('[role="status"]');
    const meta = PUZZLE_META[form.dataset.puzzle] || {message: '照合一致。次の資料が開きました。', note: '', link: '次の資料を開く →'};
    button.disabled = true;
    status.textContent = '資料を照合しています…';
    try {
      const result = await request('/api/solve', {puzzle: form.dataset.puzzle, answer: input.value});
      input.removeAttribute('aria-invalid');
      status.textContent = meta.message;
      let box = form.querySelector('.next-record');
      if (!box) { box = document.createElement('div'); box.className = 'next-record'; form.appendChild(box); }
      box.hidden = false;
      box.innerHTML = '';
      if (meta.note) {
        const note = document.createElement('p');
        note.className = 'unlock-note';
        note.textContent = meta.note;
        box.appendChild(note);
      }
      const link = document.createElement('a');
      link.className = 'button';
      link.href = result.next;
      link.textContent = meta.link;
      box.appendChild(link);
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
window.addEventListener('pageshow', event => { if (event.persisted) window.location.reload(); });
