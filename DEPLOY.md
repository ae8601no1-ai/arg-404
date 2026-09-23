# 公開手順（Render + 永続SQLite）

このARGは `server.py` が進捗判定・資料解放を行うため、GitHub Pages単体では動きません。
プレイヤー進捗を再起動・再デプロイ後も保持するため、SQLite DBをRenderの永続ディスクへ保存する構成にしています。

## 1. GitHubリポジトリ

この公開用構成には、サーバーが進行度に応じて配信する `private/` が含まれます。
制作専用資料は含まれていません。

公開URLから見えるのは `server.py` が配信したファイルだけです。

## 2. Renderへデプロイ

リポジトリ直下の `render.yaml` を利用するのが簡単です。

設定済み内容:

- Web Service: Python
- Start Command: `python3 server.py`
- Health Check: `/healthz`
- DB: `/var/data/progress.sqlite3`
- Persistent Disk: `/var/data`

`server.py` はRenderが渡す `PORT` を自動取得し、`0.0.0.0` で待受します。
HTTPSリバースプロキシ経由でもフォーム送信とSecure Cookieが動作します。

## 3. 永続化について重要

RenderのFree Web Serviceはファイルシステムが一時的で、再起動・スピンダウン・再デプロイ時にSQLiteが消えます。
永続ディスクはFree Web Serviceでは利用できないため、この `render.yaml` は `starter` プラン + Persistent Disk を指定しています。

SQLite DBは次に保存されます:

```text
/var/data/progress.sqlite3
```

`ARG_DB_PATH` も同じ場所に設定済みです。

これにより、通常の再起動や再デプロイ後もプレイヤー進捗を保持できます。

## 4. ローカル確認

通常:

```bash
python3 server.py
```

ブラウザー:

```text
http://127.0.0.1:8040/
```

永続パスを模擬して確認する場合:

```bash
mkdir -p ./persistent-data
ARG_DB_PATH="$PWD/persistent-data/progress.sqlite3" python3 server.py
```

別ポート:

```bash
PORT=9000 python3 server.py
```

## 5. バックアップ

SQLiteは1ファイルなので、必要に応じて `progress.sqlite3` をバックアップしてください。
サービス稼働中に直接コピーするより、SQLiteのバックアップ機能を使う方が安全です。

同梱の `backup_progress.py` を使えます:

```bash
ARG_DB_PATH=/var/data/progress.sqlite3 python3 backup_progress.py /var/data/backups
```

日時付きのバックアップDBを生成します。
