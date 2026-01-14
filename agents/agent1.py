"""
課題探索エージェント (Problem Discovery Agent)
=====================================

リーンスタートアップおよびJobs-to-be-Done理論に基づき、
ユーザーの自由記述から課題を構造化するエージェント。

Phase 1: problem_discovery
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv

# .envファイルを読み込み（agents/.env を優先）
_env_path = Path(__file__).parent / ".env"
load_dotenv(_env_path)

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

from agents.prompts.problem_discovery import (
    CRITIC_PROMPT,
    SYSTEM_PROMPT,
    get_user_prompt,
)
from agents.utils.schemas import (
    Context,
    CurrentSolution,
    Emotion,
    FirestoreOutput,
    FollowupQuestion,
    Job,
    Pain,
    ProblemDiscoveryInput,
    ProblemDiscoveryOutput,
    ProblemDiscoverySheet,
    QualityReport,
    UnmetNeed,
)


class ProblemDiscoveryAgent:
    """
    課題探索エージェント
    
    リーンスタートアップ伴走エージェントのPhase 1として、
    ユーザーの自由記述から課題を構造化します。
    """
    
    PHASE_NAME = "problem_discovery"
    PHASE_NUMBER = 1
    
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash-lite",
        temperature: float = 0.3,
        enable_critic: bool = True,
    ):
        """
        エージェントを初期化
        
        Args:
            model_name: 使用するLLMモデル名（デフォルト: gemini-2.5-flash-lite）
            temperature: 生成の温度パラメータ（低いほど決定的）
            enable_critic: 品質検査エージェントを有効にするか
        """
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            convert_system_message_to_human=True,
        )
        self.enable_critic = enable_critic
        
        # Critic用のLLM（より厳格な評価のため低温度）
        self.critic_llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,
            convert_system_message_to_human=True,
        )
    
    def run(self, input_data: ProblemDiscoveryInput) -> ProblemDiscoveryOutput:
        """
        エージェントのメイン実行メソッド
        
        Args:
            input_data: 入力データ（ユーザーの自由記述など）
            
        Returns:
            構造化された課題探索結果
        """
        # Step 1-4: 情報抽出・Why深掘り・不足判定・problemStatement生成
        raw_output = self._extract_and_structure(input_data)
        
        # パース
        output = self._parse_output(raw_output)
        
        # Critic（品質検査）が有効な場合
        if self.enable_critic:
            output = self._run_critic(output)
        
        return output
    
    def _extract_and_structure(self, input_data: ProblemDiscoveryInput) -> dict[str, Any]:
        """
        Step 1-4: LLMを使用して情報を抽出・構造化
        """
        # プロンプト構築
        project_meta_dict = None
        if input_data.project_meta:
            project_meta_dict = input_data.project_meta.model_dump()
        
        history_list = None
        if input_data.history:
            history_list = [msg.model_dump() for msg in input_data.history]
        
        user_prompt = get_user_prompt(
            user_free_text=input_data.user_free_text,
            project_meta=project_meta_dict,
            history=history_list,
        )
        
        # LLM呼び出し
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        
        response = self.llm.invoke(messages)
        
        # JSON解析
        try:
            # Markdownコードブロックを除去（Geminiが ```json ... ``` でラップする場合がある）
            content = response.content.strip() if response.content else ""
            if content.startswith("```"):
                # 最初の行（```json など）を除去
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # 最後の ``` を除去
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = "\n".join(lines)
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            # JSONパースエラーの場合、空の構造を返す
            return {
                "problemStatement": "",
                "problemDiscoverySheet": {},
                "followupQuestions": [],
                "qualityReport": {
                    "confidence": 0.0,
                    "missingFields": ["parse_error"],
                    "contradictions": [f"JSON解析エラー: {str(e)}"],
                    "nextAction": "ask_more",
                },
            }
    
    def _parse_output(self, raw_output: dict[str, Any]) -> ProblemDiscoveryOutput:
        """
        LLM出力をPydanticモデルにパース
        """
        try:
            # problemDiscoverySheet のパース
            sheet_data = raw_output.get("problemDiscoverySheet", {})
            
            # Job
            job_data = sheet_data.get("job", {})
            job = Job(
                main=job_data.get("main", ""),
                functional=job_data.get("functional", []),
                emotional=job_data.get("emotional", []),
                social=job_data.get("social", []),
            )
            
            # Context
            context_data = sheet_data.get("context", {})
            context = Context(
                who=context_data.get("who", ""),
                when=context_data.get("when", ""),
                where=context_data.get("where", ""),
                trigger=context_data.get("trigger", ""),
                constraints=context_data.get("constraints", []),
                stakeholders=context_data.get("stakeholders", []),
            )
            
            # Pains
            pains = [
                Pain(
                    pain=p.get("pain", ""),
                    impact=p.get("impact", ""),
                    severity=min(5, max(1, p.get("severity", 1))),
                    frequency=min(5, max(1, p.get("frequency", 1))),
                    evidence=p.get("evidence", ""),
                )
                for p in sheet_data.get("pains", [])
            ]
            
            # CurrentSolutions
            current_solutions = [
                CurrentSolution(
                    solution=s.get("solution", ""),
                    why_chosen=s.get("whyChosen", ""),
                    dissatisfaction=s.get("dissatisfaction", ""),
                )
                for s in sheet_data.get("currentSolutions", [])
            ]
            
            # UnmetNeeds
            unmet_needs = [
                UnmetNeed(
                    need=n.get("need", ""),
                    why_depth=n.get("whyDepth", []),
                )
                for n in sheet_data.get("unmetNeeds", [])
            ]
            
            # Emotion
            emotion_data = sheet_data.get("emotion", {})
            emotion = Emotion(
                feelings=emotion_data.get("feelings", []),
                moment_of_truth=emotion_data.get("momentOfTruth", ""),
            )
            
            # ProblemDiscoverySheet
            problem_discovery_sheet = ProblemDiscoverySheet(
                job=job,
                context=context,
                pains=pains,
                current_solutions=current_solutions,
                unmet_needs=unmet_needs,
                emotion=emotion,
                success_criteria=sheet_data.get("successCriteria", []),
                assumptions=sheet_data.get("assumptions", []),
                unknowns=sheet_data.get("unknowns", []),
            )
            
            # FollowupQuestions
            followup_questions = [
                FollowupQuestion(
                    question=q.get("question", ""),
                    intent=q.get("intent", ""),
                    type=q.get("type", "open"),
                )
                for q in raw_output.get("followupQuestions", [])
            ]
            
            # QualityReport
            qr_data = raw_output.get("qualityReport", {})
            quality_report = QualityReport(
                confidence=min(1.0, max(0.0, float(qr_data.get("confidence", 0.0)))),
                missing_fields=qr_data.get("missingFields", []),
                contradictions=qr_data.get("contradictions", []),
                next_action=qr_data.get("nextAction", "ask_more"),
            )
            
            return ProblemDiscoveryOutput(
                problem_statement=raw_output.get("problemStatement", ""),
                problem_discovery_sheet=problem_discovery_sheet,
                followup_questions=followup_questions,
                quality_report=quality_report,
            )
            
        except (ValidationError, KeyError, TypeError) as e:
            # パースエラーの場合、最小限の出力を返す
            return ProblemDiscoveryOutput(
                problem_statement="",
                problem_discovery_sheet=ProblemDiscoverySheet(),
                followup_questions=[],
                quality_report=QualityReport(
                    confidence=0.0,
                    missing_fields=["parse_error"],
                    contradictions=[f"パースエラー: {str(e)}"],
                    next_action="ask_more",
                ),
            )
    
    def _run_critic(self, output: ProblemDiscoveryOutput) -> ProblemDiscoveryOutput:
        """
        品質検査エージェント（Critic）を実行
        
        仕様書セクション7に基づく品質チェック:
        - job.main が「動詞＋目的語」か
        - context.trigger が具体か
        - pains が抽象語のみで終わっていないか
        - currentSolutions が最低1件あるか
        - unmetNeeds が pains と論理的につながっているか
        - problemStatement が1文で完結しているか
        """
        # 現在の出力をJSON形式で準備
        current_output_json = json.dumps(
            FirestoreOutput.from_output(output),
            ensure_ascii=False,
            indent=2,
        )
        
        messages = [
            SystemMessage(content=CRITIC_PROMPT),
            HumanMessage(content=f"以下の出力を評価してください:\n\n{current_output_json}"),
        ]
        
        response = self.critic_llm.invoke(messages)
        
        try:
            critic_result = json.loads(response.content)
            
            # qualityReportを更新
            output.quality_report = QualityReport(
                confidence=min(1.0, max(0.0, float(critic_result.get("confidence", 0.0)))),
                missing_fields=critic_result.get("missingFields", []),
                contradictions=critic_result.get("contradictions", []),
                next_action=critic_result.get("nextAction", "ask_more"),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            # Criticのエラーは無視して元の出力を返す
            pass
        
        return output
    
    def get_user_response(self, output: ProblemDiscoveryOutput) -> dict[str, Any]:
        """
        UI/UXに返すレスポンスを生成（仕様書セクション9に基づく）
        
        ユーザーに返すのは以下のみ:
        1. problemStatement（現時点の理解）
        2. followupQuestions（必要な場合のみ）
        """
        response = {
            "understanding": output.problem_statement,
            "status": output.quality_report.next_action,
        }
        
        if output.quality_report.next_action == "ask_more":
            response["questions"] = [
                {
                    "question": q.question,
                    "intent": q.intent,
                }
                for q in output.followup_questions[:3]  # 最大3問
            ]
            response["message"] = "ここまでの理解はこうです。もう少しだけ教えてください。"
        else:
            response["message"] = "課題の構造化が完了しました。次のフェーズに進めます。"
        
        return response
    
    def to_firestore(self, output: ProblemDiscoveryOutput) -> dict[str, Any]:
        """
        Firestoreに保存する形式に変換
        
        保存先: {projectId}/phase/problem_discovery
        """
        return FirestoreOutput.from_output(output)
    
    def should_proceed(self, output: ProblemDiscoveryOutput) -> bool:
        """
        次フェーズに進めるかどうかを判定（仕様書セクション8に基づく）
        """
        return output.quality_report.next_action == "proceed"


# ==================== チェーン定義（LangChain LCEL用） ====================

def create_problem_discovery_chain(
    model_name: str = "gemini-2.5-flash-lite",
    temperature: float = 0.3,
):
    """
    LangChain Expression Language (LCEL) 用のチェーンを作成
    """
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        convert_system_message_to_human=True,
    )
    
    parser = JsonOutputParser()
    
    return prompt | llm | parser


# ==================== オーケストレーション ====================

class ProblemDiscoveryOrchestrator:
    """
    課題探索フェーズのオーケストレーター
    
    仕様書セクション8に基づく分岐制御:
    - proceed: 次フェーズ（question_design）へ
    - ask_more: followupQuestionsを表示して再実行
    """
    
    def __init__(self, agent: ProblemDiscoveryAgent | None = None):
        self.agent = agent or ProblemDiscoveryAgent()
        self.max_iterations = 5  # 最大往復回数
    
    def run(
        self,
        initial_input: ProblemDiscoveryInput,
        on_question: Callable | None = None,
    ) -> tuple[ProblemDiscoveryOutput, str]:
        """
        オーケストレーションを実行
        
        Args:
            initial_input: 初期入力
            on_question: 追加質問が発生した場合のコールバック
                        引数: questions (list), 戻り値: ユーザーの回答 (str)
        
        Returns:
            (最終出力, 次のフェーズ名)
        """
        current_input = initial_input
        iteration = 0
        
        while iteration < self.max_iterations:
            # エージェント実行
            output = self.agent.run(current_input)
            
            # 進行可能かチェック
            if self.agent.should_proceed(output):
                return output, "question_design_phase"
            
            # 追加質問が必要
            if on_question is None:
                # コールバックがない場合は現状を返す
                return output, "problem_discovery"
            
            # ユーザーに質問
            user_response = on_question(output.followup_questions)
            
            if not user_response:
                # 回答がない場合は終了
                return output, "problem_discovery"
            
            # 新しい入力を構築（履歴に追加）
            new_history = list(current_input.history) if current_input.history else []
            new_history.append({"role": "user", "content": current_input.user_free_text})
            new_history.append({"role": "assistant", "content": output.problem_statement})
            new_history.append({"role": "user", "content": user_response})
            
            current_input = ProblemDiscoveryInput(
                user_free_text=user_response,
                project_meta=current_input.project_meta,
                history=new_history,
            )
            
            iteration += 1
        
        # 最大反復回数に達した場合
        return output, "problem_discovery"


# ==================== 使用例 ====================

def example_usage(output_format: str = "json"):
    """
    使用例（固定テキスト）
    """
    sample_text = """
    毎朝の通勤電車が混んでいて、スマホで仕事のメールを確認したいのに
    全然できない。立っているのも辛いし、カバンから物を取り出すのも大変。
    在宅勤務ができればいいけど、会社の方針で週3は出社必須。
    """
    return run_agent(sample_text, output_format)


def interactive_mode(output_format: str = "json"):
    """
    インタラクティブモード - ユーザー入力を受け付ける
    """
    print("=" * 60, file=sys.stderr)
    print("課題探索エージェント - インタラクティブモード", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)
    print("あなたの課題・困りごとを自由に入力してください。", file=sys.stderr)
    print("（入力完了後、空行でEnterを押してください）", file=sys.stderr)
    print("-" * 60, file=sys.stderr)
    
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except EOFError:
            break
    
    user_text = "\n".join(lines)
    
    if not user_text.strip():
        print("入力がありません。サンプルテキストを使用します。", file=sys.stderr)
        user_text = """
        毎朝の通勤電車が混んでいて、スマホで仕事のメールを確認したいのに
        全然できない。立っているのも辛いし、カバンから物を取り出すのも大変。
        在宅勤務ができればいいけど、会社の方針で週3は出社必須。
        """
    
    print(file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("処理中...", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    return run_agent(user_text, output_format)


def run_agent(user_text: str, output_format: str = "json"):
    """
    エージェントを実行して結果を表示
    
    Args:
        user_text: ユーザーの入力テキスト
        output_format: 出力形式 ("json" または "pretty")
    """
    # エージェントを初期化
    agent = ProblemDiscoveryAgent(
        model_name="gemini-2.5-flash-lite",
        temperature=0.3,
        enable_critic=True,
    )
    
    # 入力データを作成
    input_data = ProblemDiscoveryInput(
        user_free_text=user_text,
    )
    
    # エージェントを実行
    output = agent.run(input_data)
    
    if output_format == "json":
        # 仕様書セクション4のJSONスキーマ形式で出力
        json_output = FirestoreOutput.from_output(output)
        print(json.dumps(json_output, ensure_ascii=False, indent=2))
    else:
        # 整形済み出力
        print_pretty_output(output)
    
    return output


def print_pretty_output(output: ProblemDiscoveryOutput):
    """
    結果を整形して表示
    """
    print()
    print("=" * 60)
    print("結果")
    print("=" * 60)
    print()
    
    print("【課題ステートメント】")
    print(output.problem_statement if output.problem_statement else "(生成されませんでした)")
    print()
    
    print("【ジョブ】")
    print(f"  主ジョブ: {output.problem_discovery_sheet.job.main}")
    if output.problem_discovery_sheet.job.functional:
        print(f"  機能的: {', '.join(output.problem_discovery_sheet.job.functional)}")
    if output.problem_discovery_sheet.job.emotional:
        print(f"  感情的: {', '.join(output.problem_discovery_sheet.job.emotional)}")
    print()
    
    print("【付帯状況】")
    ctx = output.problem_discovery_sheet.context
    print(f"  誰が: {ctx.who}")
    print(f"  いつ: {ctx.when}")
    print(f"  どこで: {ctx.where}")
    print(f"  トリガー: {ctx.trigger}")
    print()
    
    if output.problem_discovery_sheet.pains:
        print("【課題・Pain】")
        for i, pain in enumerate(output.problem_discovery_sheet.pains, 1):
            print(f"  {i}. {pain.pain}")
            print(f"     影響: {pain.impact}")
            print(f"     重大度: {pain.severity}/5, 頻度: {pain.frequency}/5")
        print()
    
    if output.problem_discovery_sheet.current_solutions:
        print("【現状対策】")
        for i, sol in enumerate(output.problem_discovery_sheet.current_solutions, 1):
            print(f"  {i}. {sol.solution}")
            print(f"     不満: {sol.dissatisfaction}")
        print()
    
    if output.problem_discovery_sheet.unmet_needs:
        print("【残課題 (Unmet Needs)】")
        for i, need in enumerate(output.problem_discovery_sheet.unmet_needs, 1):
            print(f"  {i}. {need.need}")
            if need.why_depth:
                print(f"     Why深掘り: {' → '.join(need.why_depth)}")
        print()
    
    print("【品質レポート】")
    print(f"  信頼度: {output.quality_report.confidence:.1%}")
    print(f"  次アクション: {output.quality_report.next_action}")
    if output.quality_report.missing_fields:
        print(f"  不足情報: {', '.join(output.quality_report.missing_fields)}")
    print()
    
    # 追加質問があれば表示
    if output.followup_questions:
        print("【追加質問】")
        for i, q in enumerate(output.followup_questions, 1):
            print(f"  {i}. {q.question}")
            print(f"     意図: {q.intent}")
        print()


if __name__ == "__main__":
    # 環境変数チェック
    if not os.getenv("GOOGLE_API_KEY"):
        print("=" * 50, file=sys.stderr)
        print("警告: GOOGLE_API_KEY が設定されていません", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print(file=sys.stderr)
        print("方法1: agents/.env ファイルを作成", file=sys.stderr)
        print("  agents/.env に以下を記述:", file=sys.stderr)
        print("  GOOGLE_API_KEY=your-api-key-here", file=sys.stderr)
        print(file=sys.stderr)
        print("方法2: 環境変数を直接設定", file=sys.stderr)
        print("  export GOOGLE_API_KEY='your-api-key'", file=sys.stderr)
        print(file=sys.stderr)
        print("APIキーは https://aistudio.google.com/apikey で取得できます", file=sys.stderr)
        sys.exit(1)
    
    # コマンドライン引数を解析
    args = sys.argv[1:]
    output_format = "json"  # デフォルトはJSON出力
    mode = "interactive"    # デフォルトはインタラクティブ
    
    if "--pretty" in args:
        output_format = "pretty"
        args.remove("--pretty")
    
    if "--sample" in args:
        mode = "sample"
    elif "--interactive" in args:
        mode = "interactive"
    elif len(args) == 0:
        # 引数なしの場合はヘルプ表示後にインタラクティブモード
        print("使用方法:", file=sys.stderr)
        print("  python -m agents.agent1 --interactive         # 対話モード（JSON出力）", file=sys.stderr)
        print("  python -m agents.agent1 --interactive --pretty # 対話モード（整形出力）", file=sys.stderr)
        print("  python -m agents.agent1 --sample              # サンプル実行（JSON出力）", file=sys.stderr)
        print("  python -m agents.agent1 --sample --pretty     # サンプル実行（整形出力）", file=sys.stderr)
        print(file=sys.stderr)
        print("インタラクティブモードを開始します...", file=sys.stderr)
        print(file=sys.stderr)
    
    # 実行
    if mode == "sample":
        example_usage(output_format)
    else:
        interactive_mode(output_format)
