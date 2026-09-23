# 公開手順（Render Free + 一時SQLite）

このARGは `server.py` が進捗判定・資料解放を行うため、GitHub Pages単体では動きません。
無料運用のため、SQLite DBをRenderの一時ファイルシステムへ保存する構成です。再起動・スピンダウン・再デプロイ時にプレイヤー進捗は失われます。

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
- Plan: `free`
- DB: `/tmp/progress.sqlite3`
- Persistent Disk: なし

`server.py` はRenderが渡す `PORT` を自動取得し、`0.0.0.0` で待受します。
HTTPSリバースプロキシ経由でもフォーム送信とSecure Cookieが動作します。

## 3. 一時保存について重要

RenderのFree Web Serviceはファイルシステムが一時的で、再起動・スピンダウン・再デプロイ時にSQLiteが消えます。この `render.yaml` は無料運用を優先し、永続ディスクを使用しません。

SQLite DBは次に保存されます:

```text
/tmp/progress.sqlite3
```

`ARG_DB_PATH` も同じ一時領域に設定済みです。

プレイヤー進捗を保持できるのは、同じFreeインスタンスが稼働している間だけです。

## 4. ローカル確認

通常:

```bash
python3 server.py
```

ブラウザー:

```text
http://127.0.0.1:8040/
```

Renderの一時パスを模擬して確認する場合:

```bash
ARG_DB_PATH=/tmp/progress.sqlite3 python3 server.py
```

別ポート:

```bash
PORT=9000 python3 server.py
```

## 5. バックアップ

Free Web Serviceのローカルファイルは失われるため、この構成では継続的なバックアップ先として利用できません。

同梱の `backup_progress.py` を使えます:

```bash
ARG_DB_PATH=/tmp/progress.sqlite3 python3 backup_progress.py /tmp/backups
```

日時付きのバックアップDBを生成します。
