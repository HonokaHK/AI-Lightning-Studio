"""
課題探索エージェント用のデータスキーマ定義
Problem Discovery Agent - Data Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


# ==================== 入力スキーマ ====================

class ProjectMeta(BaseModel):
    """プロジェクトメタ情報"""
    industry: Optional[str] = Field(default=None, description="業界")
    target_customer: Optional[str] = Field(default=None, description="想定顧客")
    constraints: Optional[list[str]] = Field(default_factory=list, description="制約")
    existing_assets: Optional[list[str]] = Field(default_factory=list, description="既存アセット")


class ConversationMessage(BaseModel):
    """会話履歴メッセージ"""
    role: str = Field(description="発言者ロール（user/assistant）")
    content: str = Field(description="メッセージ内容")


class ProblemDiscoveryInput(BaseModel):
    """課題探索エージェントへの入力"""
    user_free_text: str = Field(description="ユーザーの自由記述（課題感・違和感・困りごと）")
    project_meta: Optional[ProjectMeta] = Field(default=None, description="プロジェクトメタ情報")
    history: Optional[list[ConversationMessage]] = Field(default_factory=list, description="会話履歴")


# ==================== 出力スキーマ ====================

class Job(BaseModel):
    """ジョブ定義（Jobs-to-be-Done）"""
    main: str = Field(default="", description="主ジョブ（動詞＋目的語）")
    functional: list[str] = Field(default_factory=list, description="機能的ジョブ")
    emotional: list[str] = Field(default_factory=list, description="感情的ジョブ")
    social: list[str] = Field(default_factory=list, description="社会的ジョブ")


class Context(BaseModel):
    """ジョブが発生する付帯状況"""
    who: str = Field(default="", description="誰が")
    when: str = Field(default="", description="いつ")
    where: str = Field(default="", description="どこで")
    trigger: str = Field(default="", description="きっかけ・トリガー")
    constraints: list[str] = Field(default_factory=list, description="制約条件")
    stakeholders: list[str] = Field(default_factory=list, description="関係者")


class Pain(BaseModel):
    """課題・不満"""
    pain: str = Field(default="", description="課題・不満の内容")
    impact: str = Field(default="", description="影響")
    severity: int = Field(default=1, ge=1, le=5, description="重大度（1-5）")
    frequency: int = Field(default=1, ge=1, le=5, description="頻度（1-5）")
    evidence: str = Field(default="", description="エビデンス・根拠")


class CurrentSolution(BaseModel):
    """現状対策"""
    solution: str = Field(default="", description="現在の解決策")
    why_chosen: str = Field(default="", description="なぜこれを選んだか")
    dissatisfaction: str = Field(default="", description="不満点・限界")


class UnmetNeed(BaseModel):
    """残課題（Unmet Needs）"""
    need: str = Field(default="", description="満たされていないニーズ")
    why_depth: list[str] = Field(default_factory=list, description="Why深掘り結果（最大5段階）")


class Emotion(BaseModel):
    """感情面"""
    feelings: list[str] = Field(default_factory=list, description="感情リスト")
    moment_of_truth: str = Field(default="", description="真実の瞬間")


class ProblemDiscoverySheet(BaseModel):
    """課題探索シート（構造化データ）"""
    job: Job = Field(default_factory=Job, description="ジョブ")
    context: Context = Field(default_factory=Context, description="付帯状況")
    pains: list[Pain] = Field(default_factory=list, description="課題・不満リスト")
    current_solutions: list[CurrentSolution] = Field(default_factory=list, description="現状対策リスト")
    unmet_needs: list[UnmetNeed] = Field(default_factory=list, description="残課題リスト")
    emotion: Emotion = Field(default_factory=Emotion, description="感情面")
    success_criteria: list[str] = Field(default_factory=list, description="成功基準")
    assumptions: list[str] = Field(default_factory=list, description="仮説・推測")
    unknowns: list[str] = Field(default_factory=list, description="未知・不明点")


class FollowupQuestion(BaseModel):
    """追加質問"""
    question: str = Field(default="", description="質問文")
    intent: str = Field(default="", description="質問の意図")
    type: str = Field(default="open", description="質問タイプ（open/closed/scale）")


class QualityReport(BaseModel):
    """品質レポート"""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="信頼度（0.0-1.0）")
    missing_fields: list[str] = Field(default_factory=list, description="不足フィールド")
    contradictions: list[str] = Field(default_factory=list, description="矛盾点")
    next_action: str = Field(default="proceed", description="次アクション（proceed/ask_more）")


class ProblemDiscoveryOutput(BaseModel):
    """課題探索エージェントの出力"""
    problem_statement: str = Field(
        default="",
        description="1文サマリ: 誰が/いつ/どこで/何を達成したいが/何が障害で困っている"
    )
    problem_discovery_sheet: ProblemDiscoverySheet = Field(
        default_factory=ProblemDiscoverySheet,
        description="構造化データ"
    )
    followup_questions: list[FollowupQuestion] = Field(
        default_factory=list,
        description="追加質問（不足時のみ）"
    )
    quality_report: QualityReport = Field(
        default_factory=QualityReport,
        description="品質レポート"
    )


# ==================== Firestore用変換 ====================

class FirestoreOutput(BaseModel):
    """Firestore保存用のスネークケース→キャメルケース変換済み出力"""
    
    @classmethod
    def from_output(cls, output: ProblemDiscoveryOutput) -> dict:
        """ProblemDiscoveryOutputをFirestore保存用の辞書に変換"""
        return {
            "problemStatement": output.problem_statement,
            "problemDiscoverySheet": {
                "job": {
                    "main": output.problem_discovery_sheet.job.main,
                    "functional": output.problem_discovery_sheet.job.functional,
                    "emotional": output.problem_discovery_sheet.job.emotional,
                    "social": output.problem_discovery_sheet.job.social,
                },
                "context": {
                    "who": output.problem_discovery_sheet.context.who,
                    "when": output.problem_discovery_sheet.context.when,
                    "where": output.problem_discovery_sheet.context.where,
                    "trigger": output.problem_discovery_sheet.context.trigger,
                    "constraints": output.problem_discovery_sheet.context.constraints,
                    "stakeholders": output.problem_discovery_sheet.context.stakeholders,
                },
                "pains": [
                    {
                        "pain": p.pain,
                        "impact": p.impact,
                        "severity": p.severity,
                        "frequency": p.frequency,
                        "evidence": p.evidence,
                    }
                    for p in output.problem_discovery_sheet.pains
                ],
                "currentSolutions": [
                    {
                        "solution": s.solution,
                        "whyChosen": s.why_chosen,
                        "dissatisfaction": s.dissatisfaction,
                    }
                    for s in output.problem_discovery_sheet.current_solutions
                ],
                "unmetNeeds": [
                    {
                        "need": n.need,
                        "whyDepth": n.why_depth,
                    }
                    for n in output.problem_discovery_sheet.unmet_needs
                ],
                "emotion": {
                    "feelings": output.problem_discovery_sheet.emotion.feelings,
                    "momentOfTruth": output.problem_discovery_sheet.emotion.moment_of_truth,
                },
                "successCriteria": output.problem_discovery_sheet.success_criteria,
                "assumptions": output.problem_discovery_sheet.assumptions,
                "unknowns": output.problem_discovery_sheet.unknowns,
            },
            "followupQuestions": [
                {
                    "question": q.question,
                    "intent": q.intent,
                    "type": q.type,
                }
                for q in output.followup_questions
            ],
            "qualityReport": {
                "confidence": output.quality_report.confidence,
                "missingFields": output.quality_report.missing_fields,
                "contradictions": output.quality_report.contradictions,
                "nextAction": output.quality_report.next_action,
            },
        }
