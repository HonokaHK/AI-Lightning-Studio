# **システムアーキテクチャ仕様**

## **🏗️ システム概要図**

```
┌─────────────────────────────────────────────────────────┐
│ Web/API Frontend (Next.js)                              │
│ SSR / ISR / Edge Functions                              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ API Gateway (FastAPI on Cloud Run)                      │
│ - REST API                                              │
│ - AuthZ ミドルウェア (admin/user)                        │
│ - 自動APIドキュメント (OpenAPI/Swagger)                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ Agent Orchestrator (LangChain Python)                   │
│ - フェーズ別 PromptTemplate / LLMChain                   │
│ - Conversation Store (Firestore)                        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│ External LLM API (OpenAI GPT-4o)                        │
└─────────────────────────────────────────────────────────┘
```

## **🔧 技術スタック**

### **フロントエンド**

| レイヤ | 技術 | 選定理由 |
| ----- | ----- | ----- |
| UIコンポーネント | V0.dev (React/Next UI) | 生成AIでラフ→コード生成を高速化 |
| IDE | Cursor | GPT-4統合、リファクタリング自動化 |
| フレームワーク | Next.js 14 / React 18 / TypeScript | App Router、並列UI、メンテナンス容易 |
| ホスティング | Firebase Hosting \+ Cloud Run | 低運用コスト、CDN、SSR対応 |

### **バックエンド**

| レイヤ | 技術 | 選定理由 |
| ----- | ----- | ----- |
| ランタイム | Python 3.11+ on Cloud Run | AI/ML エコシステムが充実 |
| Webフレームワーク | FastAPI | 非同期対応、自動APIドキュメント、高速 |
| AIオーケストレーション | LangChain (Python) | プロンプト管理、チェーン構築の標準化 |
| LLMモデル | OpenAI GPT-4o (API) | 高精度、プライバシー確保 |
| パッケージ管理 | pip \+ requirements.txt | シンプル、再現性確保 |

### **データ & 認証**

| レイヤ | 技術 | 選定理由 |
| ----- | ----- | ----- |
| データベース | Firebase Firestore (NoSQL) | スキーマレス、フェーズ出力の高速保存 |
| ストレージ | Google Cloud Storage | ドキュメント/アセット保管 |
| 認証 | Firebase Auth (SAML/OIDC) | 企業SSO対応 |

### **DevOps**

| レイヤ | 技術 | 選定理由 |
| ----- | ----- | ----- |
| CI/CD | GitHub Actions | Firebase/Cloud Run自動デプロイ |
| IaC | Terraform \+ Firebase Extensions | 再現性、マルチ環境管理 |
| 監視 | Cloud Logging/Monitoring \+ Sentry | SLA 99.9%維持 |

## **📊 データモデル**

### **ER図**

```
erDiagram
    Project ||--o{ Phase : contains
    Project ||--o{ AuditLog : tracks
    Phase ||--o{ AuditLog : tracks
    
    Project {
        string id PK
        string name
        string ownerUid FK
        string status
        timestamp createdAt
        timestamp updatedAt
    }
    
    Phase {
        string id PK
        string projectId FK
        string name
        json input
        json output
        timestamp startedAt
        timestamp finishedAt
    }
    
    AuditLog {
        string id PK
        string projectId FK
        string phaseId FK
        string action
        string actorUid
        json metadata
        timestamp at
    }
```

### **Firestoreコレクション構造**

```
/projects/{projectId}
  - name: string
  - ownerUid: string
  - status: "draft" | "in_progress" | "completed"
  - createdAt: timestamp
  - updatedAt: timestamp
  
  /phases/{phaseName}
    - name: string (e.g., "problem_extraction")
    - input: object
    - output: object
    - startedAt: timestamp
    - finishedAt: timestamp
    
/auditLogs/{logId}
  - projectId: string
  - phaseId: string
  - action: string
  - actorUid: string
  - metadata: object
  - at: timestamp
```

## **🔄 データフロー**

### **フェーズ実行フロー**

```
1. ユーザーがフェーズを開始
   ↓
2. Frontend → API Gateway (認証チェック)
   ↓
3. API Gateway → Agent Orchestrator
   ↓
4. Agent Orchestrator が:
   - Firestoreから前フェーズの出力を取得
   - LLMChain にコンテキスト注入
   - OpenAI API呼び出し
   ↓
5. LLM応答を受け取り
   ↓
6. 出力をFirestoreに保存
   ↓
7. Frontend に結果を返す
```

### **コンテキスト連携**

すべてのフェーズ出力は以下のパスで保存:

```
/projects/{projectId}/phases/{phaseName}
```

次フェーズ実行時、`contextLoader`が自動的に前フェーズの出力を読み込み、プロンプトに注入します。

## **🏛️ インフラ構成**

### **GCP リソース**

```
Project: ai-lightning-studio-prod
├── Cloud Run
│   └── api-service (backend)
├── Firestore
│   └── (default database)
├── Cloud Storage
│   └── project-assets bucket
├── Cloud Logging
└── Cloud Monitoring
```

### **Firebase リソース**

```
Firebase Project: ai-lightning-studio
├── Authentication
│   ├── Email/Password
│   └── SAML/OIDC (enterprise)
├── Hosting
│   └── web app (frontend)
└── Extensions
    └── (future: Stripe, SendGrid, etc.)
```

### **Terraform ディレクトリ構成**

```
infra/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── production/
├── modules/
│   ├── cloud-run/
│   ├── firestore/
│   ├── storage/
│   └── monitoring/
└── shared/
    └── variables.tf
```

## **🔐 セキュリティ & 非機能要件**

### **セキュリティ**

| 項目 | 実装 |
| ----- | ----- |
| 認証 | Firebase Auth (JWT) |
| 認可 | Cloud Run IAM \+ カスタムミドルウェア |
| データ暗号化 (保管時) | AES-256 (GCP標準) |
| データ暗号化 (転送時) | TLS 1.3 |
| APIキー管理 | Secret Manager |
| 監査ログ | Cloud Audit Logs \+ Firestore audit collection |

### **パフォーマンス**

| 項目 | 要件 |
| ----- | ----- |
| 同時プロジェクト処理 | 50 |
| 平均レスポンス時間 | ≤ 8秒 |
| LLM API タイムアウト | 30秒 |

### **可用性**

| 項目 | 要件 |
| ----- | ----- |
| SLA | 99.9% / 月 |
| Cloud Run最小インスタンス | 1 (ウォームスタート) |
| Cloud Run最大インスタンス | 10 |

### **拡張性**

| 項目 | 実装 |
| ----- | ----- |
| 新フェーズ追加 | Prompt \+ Chain追加のみ |
| 多言語対応 | LLM system promptで言語自動検知 (JA/EN) |

### **プライバシー**

| 項目 | 実装 |
| ----- | ----- |
| OpenAI API | data\_opt\_out 設定 |
| データ保持期間 | プロジェクト削除後30日で完全削除 |

## **🧪 テスト戦略**

| レベル | フレームワーク | カバー範囲 |
| ----- | ----- | ----- |
| 単体テスト | Vitest \+ React Testing Library | コンポーネント、ユーティリティ |
| AIプロンプトテスト | PromptLayer Diff \+ Golden File | 出力フォーマット回帰 |
| 統合テスト | Jest \+ SuperTest | API & Firestore連携 |
| E2Eテスト | Cypress Cloud | UI全フロー (10フェーズ) |
| 負荷テスト | k6 | RPS 100 / 10分 |

## **🚀 CI/CD パイプライン**

### **GitHub Actions ワークフロー**

```
# .github/workflows/deploy.yml (概要)

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  test:
    - lint
    - unit test
    - integration test
    
  build:
    - Next.js build
    - Docker image build (backend)
    
  deploy:
    - Firebase Hosting (frontend)
    - Cloud Run (backend)
    - Terraform apply (infra changes)
```

### **環境別デプロイ**

| ブランチ | 環境 | 自動デプロイ |
| ----- | ----- | ----- |
| `feature/*` | Preview (Firebase) | ✅ PR時 |
| `develop` | Staging | ✅ マージ時 |
| `main` | Production | ✅ マージ時 |

## **📈 監視 & アラート**

### **メトリクス**

* API レスポンスタイム  
* LLM API 呼び出し回数 & コスト  
* エラー率 (4xx, 5xx)  
* Cloud Run インスタンス数

### **アラート条件**

* エラー率 \> 5% (5分間)  
* レスポンスタイム \> 10秒 (P95, 5分間)  
* OpenAI API エラー \> 10回/分

### **ログ集約**

* Cloud Logging → BigQuery (長期保存)  
* Sentry (フロントエンドエラー)

## **🔄 災害復旧 (DR)**

| 項目 | 戦略 |
| ----- | ----- |
| RPO (目標復旧時点) | 1時間 |
| RTO (目標復旧時間) | 4時間 |
| バックアップ | Firestore自動バックアップ (日次) |
| リージョン | asia-northeast1 (東京) |

## **🎯 パフォーマンス最適化**

### **フロントエンド**

* Next.js ISR (Incremental Static Regeneration)  
* 画像最適化 (next/image)  
* Code splitting (React.lazy)

### **バックエンド**

* LLM応答のストリーミング (Server-Sent Events)  
* Firestore クエリ最適化 (複合インデックス)  
* Cloud Run コールドスタート対策 (min-instances=1)

### **コスト最適化**

* OpenAI API token budgeting  
* Embedding キャッシュ  
* Cloud Run スケーリング設定調整

## **📋 開発環境セットアップ詳細**

### **1\. GCP プロジェクト作成**

```shell
# gcloud CLI インストール後
gcloud projects create ai-lightning-studio-dev
gcloud config set project ai-lightning-studio-dev

# 必要なAPIを有効化
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com
```

### **2\. Firebase プロジェクト初期化**

```shell
firebase login
firebase projects:create ai-lightning-studio-dev
firebase use ai-lightning-studio-dev
firebase init hosting
firebase init firestore
```

### **3\. Terraform初期化**

```shell
cd infra/environments/dev
terraform init
terraform plan
terraform apply
```

### **4\. シークレット設定**

```shell
# OpenAI API Key
echo -n "sk-..." | gcloud secrets create openai-api-key --data-file=-

# Firebase設定
firebase apps:sdkconfig web > firebase-config.json
```

## **🔗 外部サービス連携**

| サービス | 用途 | SDK/ライブラリ |
| ----- | ----- | ----- |
| OpenAI | LLM API | `openai` (Python) |
| Firebase | Auth, Hosting, Firestore | `firebase-admin` (Python) |
| GCP | Cloud Run, Storage, Logging | `google-cloud-*` (Python) |
| Sentry | エラー追跡 | `sentry-sdk` (Python) |

## **🤝 フロント・バック連携方法**

### **2人並行開発のための仕組み**

このプロジェクトは**完全分業型**で進めます。お互いが独立して開発できるよう、以下の仕組みを用意しています。

### **API仕様書（Swagger）で連携**

バックエンドは **FastAPI** を使用しているため、API仕様書が自動生成されます。

**バックエンド担当:**

```shell
# サーバー起動
uvicorn app.main:app --reload --port 8000

# Swagger UIで仕様を確認・共有
# http://localhost:8000/docs
```

**フロントエンド担当:**

1. `http://localhost:8000/docs` にアクセス  
2. APIの仕様を確認  
3. 「Try it out」ボタンで実際に試せる  
4. レスポンス形式を確認してコードに反映

### **モックAPI vs 実API の切り替え**

開発初期は**モックデータ**で進め、APIができたら**実API**に切り替えます。

#### **フロントエンド実装例**

```ts
// apps/web/lib/api-client.ts

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// モックデータ
const MOCK_DATA = {
  phase1: { problem_statement: "サンプル課題..." },
  phase2: { questions: ["質問1", "質問2"] },
  // ...
};

export async function executePhase(
  projectId: string,
  phaseName: string,
  input: any
) {
  // モックモードの場合
  if (USE_MOCK) {
    console.log('🔷 モックモード: APIは呼ばれていません');
    return MOCK_DATA[phaseName];
  }
  
  // 実APIを呼ぶ
  const response = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/phases/${phaseName}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    }
  );
  
  return await response.json();
}
```

#### **環境変数で切り替え**

**モックモードで開発:**

```shell
# apps/web/.env.local
NEXT_PUBLIC_USE_MOCK=true
```

**実APIに接続:**

```shell
# apps/web/.env.local
NEXT_PUBLIC_USE_MOCK=false
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **ローカル開発時の同時起動**

**2つのターミナルで同時に起動:**

ターミナル1（バックエンド）:

```shell
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

ターミナル2（フロントエンド）:

```shell
cd apps/web
npm run dev
```

これで以下のURLが使えます:

* フロントエンド: http://localhost:3000  
* バックエンドAPI: http://localhost:8000  
* Swagger UI: http://localhost:8000/docs

### **CORS設定（重要）**

フロントエンド（3000番ポート）からバックエンド（8000番ポート）にアクセスするため、CORS設定が必要です。

```py
# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Lightning Studio API")

# CORS設定（開発環境用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # フロントエンド
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **API仕様の例**

#### **プロジェクト作成API**

**エンドポイント:** `POST /api/v1/projects`

**リクエスト:**

```json
{
  "name": "新規事業アイデア検討"
}
```

**レスポンス:**

```json
{
  "id": "proj_abc123",
  "name": "新規事業アイデア検討",
  "status": "draft",
  "created_at": "2025-01-10T10:00:00Z"
}
```

#### **フェーズ実行API**

**エンドポイント:** `POST /api/v1/projects/{project_id}/phases/{phase_name}`

**リクエスト（Phase 1の例）:**

```json
{
  "user_input": "社内の情報共有がうまくいっていない"
}
```

**レスポンス:**

```json
{
  "problem_statement": "社内コミュニケーションの非効率性により、チーム間の情報共有が滞り、業務の重複や意思決定の遅延が発生している。"
}
```

### **エラーハンドリング**

APIエラーは以下の形式で返されます:

```json
{
  "detail": "OpenAI APIへの接続に失敗しました",
  "status_code": 500
}
```

フロントエンドでの処理例:

```ts
try {
  const result = await executePhase(projectId, 'phase1', input);
  // 成功時の処理
} catch (error) {
  console.error('APIエラー:', error);
  // ユーザーにエラーメッセージを表示
  alert('処理に失敗しました。もう一度お試しください。');
}
```

### **主要Pythonパッケージ (requirements.txt)**

```
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# AI/ML
langchain==0.1.0
langchain-openai==0.0.5
openai==1.10.0

# Firebase & GCP
firebase-admin==6.4.0
google-cloud-firestore==2.14.0
google-cloud-storage==2.14.0
google-cloud-logging==3.9.0

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Monitoring
sentry-sdk[fastapi]==1.40.0

# Testing
pytest==7.4.0
pytest-asyncio==0.21.0
httpx==0.26.0
```

### **フロントエンド主要パッケージ (package.json)**

```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "typescript": "^5.3.0",
    "firebase": "^10.7.0",
    "tailwindcss": "^3.4.0"
  }
}
```

## **📚 参考リンク**

* [Next.js App Router](https://nextjs.org/docs/app)  
* [LangChain.js ドキュメント](https://js.langchain.com/)  
* [Firebase ドキュメント](https://firebase.google.com/docs)  
* [Cloud Run ドキュメント](https://cloud.google.com/run/docs)  
* [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

