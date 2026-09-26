"""Local ARG server: only released evidence is sent to the browser."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlsplit, unquote
import argparse, json, mimetypes, os, secrets, sqlite3, time, unicodedata
from contextlib import contextmanager

@contextmanager
def db_connection(path):
 db=sqlite3.connect(path)
 try:
  with db:yield db
 finally:db.close()

ROOT = Path(__file__).resolve().parent
WEB = ROOT / 'web'
PRIVATE = ROOT / 'private'
# required completed puzzle count, source file
LOCKED = {
 '/assets/evidence/newspaper-proof.png': (1, 'assets/evidence/newspaper-proof.png'),
 '/assets/evidence/newspaper-digital.png': (1, 'assets/evidence/newspaper-digital.png'),
 '/assets/evidence/nanami-sns.png': (2, 'assets/evidence/nanami-sns.png'),
 '/assets/evidence/camera-in.svg': (3, 'assets/evidence/camera-in.svg'),
 '/assets/evidence/camera-out.svg': (3, 'assets/evidence/camera-out.svg'),
 '/assets/evidence/camera-grid.svg': (3, 'assets/evidence/camera-grid.svg'),
 '/assets/evidence/floorplan-b104.svg': (5, 'assets/evidence/floorplan-b104.svg'),
 '/assets/evidence/cycle-board.svg': (6, 'assets/evidence/cycle-board.svg'),
 '/assets/evidence/invitation-scan.svg': (7, 'assets/evidence/invitation-scan.svg'),
 '/assets/evidence/company-contract.svg': (8, 'assets/evidence/company-contract.svg'),
 '/assets/evidence/persona-ledger.svg': (9, 'assets/evidence/persona-ledger.svg'),
 '/assets/evidence/persona-shock.svg': (9, 'assets/evidence/persona-shock.svg'),
 '/assets/evidence/nao-note.svg': (10, 'assets/evidence/nao-note.svg'),
 '/assets/evidence/target-sheet.svg': (11, 'assets/evidence/target-sheet.svg'),
 '/assets/evidence/identity-ledger.svg': (12, 'assets/evidence/identity-ledger.svg'),
 '/assets/evidence/participants-warning.svg': (13, 'assets/evidence/participants-warning.svg'),
 '/assets/evidence/final-warning.svg': (13, 'assets/evidence/final-warning.svg'),
 '/assets/building.svg': (4, 'assets/building.svg'),
 '/evidence/newspaper.html': (1, 'evidence/newspaper.html'),
 '/evidence/social.html': (2, 'evidence/social.html'),
 '/evidence/camera.html': (3, 'evidence/camera.html'),
 '/evidence/photo.html': (4, 'evidence/photo.html'),
 '/evidence/room404.html': (5, 'evidence/room404.html'),
 '/evidence/cycle.html': (6, 'evidence/cycle.html'),
 '/evidence/invitation.html': (7, 'evidence/invitation.html'),
 '/evidence/company.html': (8, 'evidence/company.html'),
 '/evidence/persona.html': (9, 'evidence/persona.html'),
 '/evidence/nao.html': (10, 'evidence/nao.html'),
 '/evidence/target.html': (11, 'evidence/target.html'),
 '/evidence/identity.html': (12, 'evidence/identity.html'),
 '/hidden/participants.html': (13, 'hidden/participants.html'),
 '/hidden/404.html': (13, 'hidden/404.html'),
 '/hidden/epilogue.html': (13, 'hidden/epilogue.html'),
}
PUZZLES = [
 ('p1', '水城七海', '/evidence/newspaper.html'),
 ('p2', 'SH-1105-04', '/evidence/social.html'),
 ('p3', '201110041651', '/evidence/camera.html'),
 ('p4', '11', '/evidence/photo.html'),
 ('p5', '3', '/evidence/room404.html'),
 ('p6', 'B1-04', '/evidence/cycle.html'),
 ('p7', '3', '/evidence/invitation.html'),
 ('p8', '2029', '/evidence/company.html'),
 ('p9', '静浜記録技研', '/evidence/persona.html'),
 ('p10', 'N-04', '/evidence/nao.html'),
 ('p11', '新堂奈緒', '/evidence/target.html'),
 ('p12', 'M-17', '/evidence/identity.html'),
 ('p13', '新堂澪', '/hidden/participants.html'),
]
def normalize(value):
 return ''.join(unicodedata.normalize('NFKC',value).split()).upper()

class ARGServer(ThreadingHTTPServer):
 def __init__(self, address, database=None):
  self.database = Path(database or os.environ.get('ARG_DB_PATH') or ROOT / '.local/progress.sqlite3')
  self.database.parent.mkdir(parents=True, exist_ok=True)
  with db_connection(self.database) as db:
   db.execute('CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, progress INTEGER NOT NULL DEFAULT 0, saw_article INTEGER NOT NULL DEFAULT 0, updated REAL NOT NULL)')
   db.execute('DELETE FROM sessions WHERE updated < ?', (time.time()-30*86400,))
  super().__init__(address, Handler)

class Handler(BaseHTTPRequestHandler):
 def log_message(self, fmt, *args):
  # Never log submitted answers or session identifiers.
  super().log_message(fmt,*args)
 def session(self):
  cookie=SimpleCookie()
  try: cookie.load(self.headers.get('Cookie',''))
  except Exception: pass
  token=cookie.get('arg404_session')
  token=token.value if token else ''
  with db_connection(self.server.database) as db:
   row=db.execute('SELECT progress,saw_article FROM sessions WHERE token=?',(token,)).fetchone()
   if row is None:
    token=secrets.token_urlsafe(32)
    db.execute('INSERT INTO sessions(token,updated) VALUES (?,?)',(token,time.time()))
    row=(0,0)
  self.token=token
  return row
 def reply(self, code, body, mime='text/html; charset=utf-8'):
  if isinstance(body,str):body=body.encode('utf-8')
  self.send_response(code)
  self.send_header('Content-Type',mime)
  self.send_header('Content-Length',str(len(body)))
  self.send_header('Cache-Control','no-store, max-age=0')
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('Referrer-Policy','same-origin')
  self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
  if hasattr(self,'token'):
   proto=(self.headers.get('X-Forwarded-Proto') or '').split(',')[0].strip().lower()
   secure='; Secure' if proto=='https' else ''
   self.send_header('Set-Cookie',f'arg404_session={self.token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=2592000{secure}')
  self.end_headers()
  if self.command!='HEAD':self.wfile.write(body)
 def json(self,code,data):self.reply(code,json.dumps(data,ensure_ascii=False),'application/json; charset=utf-8')
 def unavailable(self, code=403):
  self.reply(code,'<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>資料を開けません</title><link rel="stylesheet" href="/assets/style.css"><main><h1>この資料はまだ届いていません。</h1><p>手元の記事と資料の照合を進めてから、もう一度お越しください。</p><p><a href="/">受信箱に戻る</a> · <a href="/blog/index.html">ブログを読む</a></p></main></html>')
 def do_HEAD(self):self.do_GET()
 def do_GET(self):
  path=unquote(urlsplit(self.path).path)
  if path=='/healthz':
   self.reply(200,'ok','text/plain; charset=utf-8');return
  progress,saw=self.session()
  if path=='/api/progress':
   self.json(200,{'resume':PUZZLES[progress-1][2] if progress else None});return
  if path.startswith('/api/'):
   self.json(404,{'message':'見つかりません。'});return
  if '..' in path.split('/') or '\\' in path or '\x00' in path:
   self.unavailable(404);return
  if path in LOCKED:
   required,relative=LOCKED[path]
   if progress<required:self.unavailable();return
   target=PRIVATE/relative
  else:
   relative='index.html' if path=='/' else path.lstrip('/')
   target=WEB/relative
   # No listings, implicit directories, symlinks or arbitrary source files.
   if target.suffix not in {'.html','.css','.js','.svg','.png','.jpg','.webp'} or not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to(WEB):
    self.unavailable(404);return
  if self.command=='GET' and path in {'/blog/deleted.html','/blog/source.html'}:
   with db_connection(self.server.database) as db:
    db.execute('UPDATE sessions SET saw_article=1,updated=? WHERE token=?',(time.time(),self.token))
  mime=mimetypes.guess_type(target)[0] or 'application/octet-stream'
  if mime.startswith('text/') or mime=='application/javascript':mime+='; charset=utf-8'
  self.reply(200,target.read_bytes(),mime)
 def do_POST(self):
  progress,saw=self.session()
  origin=self.headers.get('Origin')
  proto=(self.headers.get('X-Forwarded-Proto') or 'http').split(',')[0].strip().lower()
  host=self.headers.get('Host','')
  expected=f'{proto}://{host}'
  if self.headers.get('X-ARG-Request')!='1' or (origin and origin!=expected):
   self.json(403,{'message':'ページを再読み込みしてお試しください。'});return
  path=urlsplit(self.path).path
  if path=='/api/reset':
   with db_connection(self.server.database) as db:
    db.execute('DELETE FROM sessions WHERE token=?',(self.token,))
   self.session() # rotate identifier; old links/cookie cannot revive progress
   self.json(200,{'next':'/'});return
  if path!='/api/solve':self.json(404,{'message':'見つかりません。'});return
  try:
   length=int(self.headers.get('Content-Length','0'))
   if not 0<length<=2048:raise ValueError()
   payload=json.loads(self.rfile.read(length))
   puzzle=payload.get('puzzle');answer=payload.get('answer')
   if not isinstance(answer,str):raise ValueError()
  except (ValueError,AttributeError,UnicodeDecodeError):
   self.json(400,{'message':'入力を確認してください。'});return
  index=next((i for i,p in enumerate(PUZZLES) if p[0]==puzzle),None)
  if index is None or index>progress:
   self.json(403,{'message':'先に手元の資料を照合してください。'});return
  if index==0 and not saw:
   self.json(403,{'message':'先に「静浜の古い失踪事件について」の記事と注釈を確認してください。'});return
  if normalize(answer)!=normalize(PUZZLES[index][1]):
   self.json(422,{'message':'記録が一致しません。資料の表記と照合してください。'});return
  with db_connection(self.server.database) as db:
   db.execute('UPDATE sessions SET progress=MAX(progress,?),updated=? WHERE token=?',(index+1,time.time(),self.token))
  self.json(200,{'next':PUZZLES[index][2]})

if __name__=='__main__':
 parser=argparse.ArgumentParser()
 parser.add_argument('--host',default=os.environ.get('HOST','0.0.0.0'))
 parser.add_argument('--port',type=int,default=int(os.environ.get('PORT','8040')))
 parser.add_argument('--database',default=os.environ.get('ARG_DB_PATH'))
 args=parser.parse_args()
 server=ARGServer((args.host,args.port),database=args.database)
 print(f'ARG server listening on {args.host}:{args.port}',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
