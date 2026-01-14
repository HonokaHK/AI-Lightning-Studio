# **AI Lightning Studio**

新規事業開発の構想フェーズを自動化するSaaS \+ AIエージェント基盤

## **🎯 プロジェクト概要**

**目的**: 30日でMVPを構築し、企業の新規事業開発における稟議/PoC準備のリードタイムを90%以上短縮する

**ターゲットユーザー**: 大企業の新規事業責任者（部長〜役員）、DX推進担当者、CVC室長

**主要機能**: 10フェーズのAIエージェントが課題探索からピッチデック作成までを自動化

## **👥 チーム体制**

このプロジェクトは**2人並行開発**で進めます:

| 役割 | 担当範囲 | 主な技術 |
| ----- | ----- | ----- |
| **フロントエンド担当** | 画面デザイン・UI実装・ユーザー体験 | Next.js, React, TypeScript, Figma, v0 |
| **バックエンド担当** | API開発・AIエージェント・データベース | Python, FastAPI, LangChain, Firebase |

**連携ポイント**: API仕様（Swagger）を通じて、お互い独立して開発できます

## **🚀 クイックスタート**

### **必要なもの**

**全員必須:**

* Git（コード管理ツール）  
* GCPアカウント（Googleのクラウドサービス）  
* OpenAI APIキー（AIを使うための鍵）

**フロントエンド担当に必要:**

* Node.js 18以上（JavaScriptを動かすツール）  
* npm または yarn（パッケージ管理ツール）  
* Figma アカウント（デザインツール）

**バックエンド担当に必要:**

* Python 3.11以上（プログラミング言語）  
* Firebase CLI（Firebaseを操作するツール）

### **セットアップ手順**

#### **📱 フロントエンド担当の方**

\<details\> \<summary\>\<strong\>macOS の場合（クリックして開く）\</strong\>\</summary\>

```shell
# 1. Homebrewをインストール（パッケージ管理ツール）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Node.jsをインストール
brew install node

# 3. リポジトリをダウンロード
git clone <repository-url>
cd ai-lightning-studio

# 4. フロントエンドのフォルダに移動
cd apps/web

# 5. 必要なパッケージをインストール
npm install

# 6. 開発サーバーを起動
npm run dev
```

ブラウザで `http://localhost:3000` を開けば画面が表示されます！

\</details\> \<details\> \<summary\>\<strong\>Windows の場合（クリックして開く）\</strong\>\</summary\>

```
# 1. PowerShellを管理者権限で開く

# 2. Chocolateyをインストール（パッケージ管理ツール）
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 3. Node.jsをインストール
choco install nodejs

# 4. リポジトリをダウンロード
git clone <repository-url>
cd ai-lightning-studio

# 5. フロントエンドのフォルダに移動
cd apps/web

# 6. 必要なパッケージをインストール
npm install

# 7. 開発サーバーを起動
npm run dev
```

ブラウザで `http://localhost:3000` を開けば画面が表示されます！

\</details\>

**💡 ポイント:**

* 最初はバックエンドなしでも開発できます（モックデータを使用）  
* バックエンドが完成したら、設定ファイルで接続を切り替えます

---

#### **⚙️ バックエンド担当の方**

\<details\> \<summary\>\<strong\>macOS の場合（クリックして開く）\</strong\>\</summary\>

```shell
# 1. Homebrewをインストール（パッケージ管理ツール）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Pythonをインストール
brew install python@3.11

# 3. Firebase CLIをインストール
brew install node  # Firebaseに必要
npm install -g firebase-tools

# 4. リポジトリをダウンロード
git clone <repository-url>
cd ai-lightning-studio

# 5. バックエンドのフォルダに移動
cd backend

# 6. 仮想環境を作成（Pythonのプロジェクト専用環境）
python3.11 -m venv venv

# 7. 仮想環境を有効化
source venv/bin/activate

# 8. 必要なパッケージをインストール
pip install -r requirements.txt

# 9. 開発サーバーを起動
uvicorn app.main:app --reload --port 8000
```

ブラウザで以下のURLを開いて確認:

* API: `http://localhost:8000`  
* API仕様書（Swagger）: `http://localhost:8000/docs`

\</details\> \<details\> \<summary\>\<strong\>Windows の場合（クリックして開く）\</strong\>\</summary\>

```
# 1. PowerShellを管理者権限で開く

# 2. Chocolateyをインストール
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 3. Pythonをインストール
choco install python --version=3.11.0

# 4. Node.jsをインストール（Firebaseに必要）
choco install nodejs

# 5. Firebase CLIをインストール
npm install -g firebase-tools

# 6. リポジトリをダウンロード
git clone <repository-url>
cd ai-lightning-studio

# 7. バックエンドのフォルダに移動
cd backend

# 8. 仮想環境を作成
python -m venv venv

# 9. 仮想環境を有効化
venv\Scripts\activate

# 10. 必要なパッケージをインストール
pip install -r requirements.txt

# 11. 開発サーバーを起動
uvicorn app.main:app --reload --port 8000
```

ブラウザで以下のURLを開いて確認:

* API: `http://localhost:8000`  
* API仕様書（Swagger）: `http://localhost:8000/docs`

\</details\>

**💡 ポイント:**

* 仮想環境（venv）は、プロジェクト専用のPython環境を作る仕組みです  
* 次回からは `source venv/bin/activate`（Windows: `venv\Scripts\activate`）だけでOK

### **設定ファイルの準備**

#### **フロントエンド担当の方**

`apps/web/.env.local` ファイルを作成して、以下をコピー:

```shell
# Firebase設定（バックエンド担当からもらう）
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...

# バックエンドAPI（開発中はモックを使用）
NEXT_PUBLIC_API_URL=http://localhost:8000
# ↑ モックモードの場合は不要
```

**💡 最初はモックモードで開発:**

* バックエンドなしでも画面開発ができます  
* `NEXT_PUBLIC_USE_MOCK=true` を追加すると、ダミーデータで動作します

#### **バックエンド担当の方**

`backend/.env` ファイルを作成して、以下をコピー:

```shell
# OpenAI API（AIを使うための鍵）
OPENAI_API_KEY=sk-...

# Firebase Admin SDK（データベースにアクセスするための設定）
FIREBASE_PROJECT_ID=...
GOOGLE_APPLICATION_CREDENTIALS=./firebase-service-account.json

# GCP
GCP_PROJECT_ID=...
```

**💡 OpenAI APIキーの取得方法:**

1. https://platform.openai.com/ にアクセス  
2. アカウント作成 → API Keys → Create new secret key  
3. 表示されたキーを `OPENAI_API_KEY` に設定

### **開発サーバーの起動**

#### **フロントエンド担当の方**

```shell
cd apps/web
npm run dev
```

画面を確認:

* **フロントエンド**: http://localhost:3000

**💡 開発のコツ:**

* ファイルを編集すると、自動で画面が更新されます（ホットリロード）  
* エラーが出たら、ブラウザの開発者ツール（F12キー）で確認

---

#### **バックエンド担当の方**

```shell
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

APIを確認:

* **バックエンドAPI**: http://localhost:8000  
* **API仕様書（Swagger）**: http://localhost:8000/docs ← ここで動作確認できます！

**💡 開発のコツ:**

* Swagger（http://localhost:8000/docs）で、APIを実際に試せます  
* コードを編集すると、自動で再起動します（`--reload`オプション）  
* エラーが出たら、ターミナルのログを確認

---

### **🔗 2人で連携して開発する方法**

1. **最初はそれぞれ独立して開発**

   * フロント: モックデータで画面を作る  
   * バック: SwaggerでAPIをテストする  
2. **API仕様（Swagger）で連携**

   * バックエンド担当が `http://localhost:8000/docs` を共有  
   * フロントエンド担当がその仕様に合わせて実装  
3. **統合テスト（4週目〜）**

   * フロントエンドの設定で `NEXT_PUBLIC_API_URL=http://localhost:8000` を設定  
   * 実際のAPIを使って動作確認

## **📅 5週間の開発スケジュール**

| 週 | フロントエンド担当 | バックエンド担当 | 統合ポイント |
| ----- | ----- | ----- | ----- |
| **1週目**\<br\>1/8-1/12 | プロジェクト理解\<br\>リポジトリ確認 | プロジェクト理解\<br\>開発環境構築 | キックオフMTG |
| **2週目**\<br\>1/13-1/19 | 画面構成整理\<br\>Figmaワイヤー作成 | Firebase/GCP初期化\<br\>API基盤構築 | API仕様の合意 |
| **3週目**\<br\>1/20-1/26 | Figmaデザイン\<br\>v0でUI試作 | エージェント実装\<br\>(フェーズ1-5) | Swagger共有 |
| **4週目**\<br\>1/27-2/2 | レイアウト実装\<br\>画面遷移 | エージェント実装\<br\>(フェーズ6-10) | API接続テスト |
| **5週目**\<br\>2/3-2/9 | UI調整\<br\>全体確認 | 統合テスト\<br\>デプロイ準備 | 動作確認・デモ |

**詳細なタスクは [DEVELOPMENT\_PLAN.md](https://claude.ai/chat/docs/DEVELOPMENT_PLAN.md) を参照してください**

## **📁 プロジェクト構成**

```
ai-lightning-studio/
├── apps/
│   └── web/              # Next.js フロントエンド
│       ├── app/          # App Router
│       ├── components/   # Reactコンポーネント
│       └── lib/          # ユーティリティ
├── agents/               # LangChainエージェント
│   ├── chains/           # 各フェーズのチェーン
│   ├── prompts/          # プロンプトテンプレート
│   └── utils/            # エージェント用ユーティリティ
├── backend/              # Python FastAPI バックエンド
│   ├── app/
│   │   ├── main.py       # FastAPI アプリケーション
│   │   ├── api/          # APIルート
│   │   │   └── v1/       # APIバージョン
│   │   ├── models/       # Pydanticモデル
│   │   ├── core/         # 設定・認証
│   │   └── utils/        # ユーティリティ
│   ├── tests/            # Pytestテスト
│   ├── requirements.txt  # Python依存関係
│   └── Dockerfile        # Cloud Run用
├── packages/
│   └── ui/               # 共有UIコンポーネント
├── infra/                # Terraform設定
│   ├── modules/
│   └── environments/
├── .github/
│   └── workflows/        # CI/CD設定
└── docs/                 # ドキュメント
    ├── ARCHITECTURE.md
    └── AGENT_SPEC.md
```

## **🛠️ 開発フロー**

### **ブランチ戦略**

* `main` \- 本番環境  
* `develop` \- 開発環境  
* `feature/*` \- 機能開発  
* `fix/*` \- バグ修正

### **コミットメッセージ規約**

```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
style: コードフォーマット
refactor: リファクタリング
test: テスト追加・修正
chore: ビルド・設定変更
```

## **📅 30日MVP開発マイルストーン**

| 週 | 主要成果物 | タスク |
| ----- | ----- | ----- |
| W0 | インフラ基盤 | GCP・Firebase初期化、Terraform設定 |
| W1 | UIスケルトン・Agent基盤 | V0.devでUI生成、LangChainボイラープレート |
| W2 | フェーズ1-5実装 | 課題探索〜アイデア評価 |
| W3 | フェーズ6-10実装 | プロトタイピング〜ピッチデック |
| W4 | 結合テスト・デプロイ | E2Eテスト、Firebase Hosting公開 |

## **🧪 テスト**

```shell
# バックエンドテスト (Python/Pytest)
cd backend
pytest

# フロントエンドテスト (Vitest)
cd apps/web
npm run test

# E2Eテスト (Cypress)
npm run test:e2e

# 負荷テスト (k6)
k6 run tests/load/api-load-test.js
```

## **📦 デプロイ**

```shell
# ステージング環境
npm run deploy:staging

# 本番環境
npm run deploy:production
```

## **🔧 困ったときは**

### **よくある問題と解決方法**

\<details\> \<summary\>\<strong\>フロントエンド: 画面が表示されない\</strong\>\</summary\>

**原因1: ポート3000が使用中**

```shell
# 別のアプリが使っている可能性
lsof -ti:3000 | xargs kill -9  # macOS/Linux

# または別のポートで起動
npm run dev -- -p 3001
```

**原因2: node\_modulesが壊れている**

```shell
cd apps/web
rm -rf node_modules .next
npm install
```

**原因3: Node.jsのバージョンが古い**

```shell
node -v  # 18以上か確認

# nvmを使ってバージョン変更（推奨）
nvm install 18
nvm use 18
```

\</details\> \<details\> \<summary\>\<strong\>バックエンド: サーバーが起動しない\</strong\>\</summary\>

**原因1: 仮想環境が有効化されていない**

```shell
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# (venv) と表示されればOK
```

**原因2: パッケージがインストールされていない**

```shell
pip install -r requirements.txt
```

**原因3: ポート8000が使用中**

```shell
# 別のポートで起動
uvicorn app.main:app --reload --port 8001
```

**原因4: Pythonのバージョンが違う**

```shell
python --version  # 3.11以上か確認

# pyenvを使ってバージョン変更（推奨）
pyenv install 3.11.0
pyenv local 3.11.0
```

\</details\> \<details\> \<summary\>\<strong\>Firebase: ログインできない\</strong\>\</summary\>

```shell
# 一度ログアウトして再ログイン
firebase logout
firebase login
firebase projects:list  # プロジェクト一覧が表示されればOK
```

\</details\> \<details\> \<summary\>\<strong\>Git: プッシュできない\</strong\>\</summary\>

**原因: 認証情報が設定されていない**

```shell
# ユーザー名とメールを設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# GitHubのトークンを使う場合
# Settings → Developer settings → Personal access tokens
```

\</details\>

### **💬 それでも解決しない場合**

1. **エラーメッセージをコピー** して検索  
2. **ターミナルのログ全体** を確認  
3. チームメンバーに相談（Slackなど）

## **📚 関連ドキュメント**

* [アーキテクチャ仕様](https://claude.ai/chat/docs/ARCHITECTURE.md)  
* [エージェント仕様](https://claude.ai/chat/docs/AGENT_SPEC.md)  
* [Firebase ドキュメント](https://firebase.google.com/docs)  
* [Next.js ドキュメント](https://nextjs.org/docs)  
* [FastAPI ドキュメント](https://fastapi.tiangolo.com/)  
* [LangChain Python ドキュメント](https://python.langchain.com/docs/get_started/introduction)

## **📄 ライセンス**

Proprietary \- All Rights Reserved

## **👥 開発チーム**

開発に関する質問は開発チームまでお問い合わせください。

