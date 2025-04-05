import logging
from typing import Dict, Any, Optional, TypedDict, List
from langgraph.graph import StateGraph, START, END  # type:ignore
from langchain_groq import ChatGroq  # type:ignore
from langchain_openai import OpenAIEmbeddings  # type:ignore
from pydantic import BaseModel, Field  # type:ignore
from functools import lru_cache
from readme_ai.models.repository import Repository
from readme_ai.prompts import (
    plan_prompt,
    writing_readme_prompt,
    question_generation_prompt,
)
from readme_ai.templates import default_readme
from readme_ai.services.repository_service import RepositoryService

logger = logging.getLogger(__name__)


class FileAnalysis(BaseModel):
    path: str = Field(description="Path of the analyzed file")
    analysis: str = Field(
        description="Detailed analysis of the file's purpose and functionality"
    )


class RepoAnalyzerState(TypedDict):
    plan: str
    readme: str
    template: str
    analysis: list[dict[str, str]]
    repo_url: str
    repository_id: int
    context: List[dict]
    questions: List[str]


class ReadmeCompilerAgent:
    def __init__(self, repository_service: RepositoryService):
        logger.info("Initializing ReadmeCompilerAgent")
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        self.graph = self._build_gen_readme_graph()
        self._cache = {}
        self.repository_service = repository_service
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        logger.info("ReadmeCompilerAgent initialized successfully")

    def _build_gen_readme_graph(self) -> Any:
        logger.info("Building README generation graph")
        graph = StateGraph(RepoAnalyzerState)

        # Add nodes with enhanced error handling
        graph.add_node("generate_questions", self.generate_questions)
        graph.add_node("gather_context", self.gather_context)
        graph.add_node("readme_plan", self.plan)
        graph.add_node("write_readme", self._write_readme)

        # Define graph flow
        graph.add_edge(START, "generate_questions")
        graph.add_edge("generate_questions", "gather_context")
        graph.add_edge("gather_context", "readme_plan")
        graph.add_edge("readme_plan", "write_readme")
        graph.add_edge("write_readme", END)

        logger.info("README generation graph built successfully")
        return graph

    async def generate_questions(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== GENERATING QUESTIONS ABOUT REPOSITORY ===")
        logger.info("Generating questions to understand repository better")

        def _format_analysis_for_prompt(analysis_list: list[dict[str, str]]) -> str:
            analysis_formatted = []
            for analysis in analysis_list:
                formatted_analysis = f"File: {analysis['path']}\n"
                formatted_analysis += f"Analysis: {analysis['analysis']}\n"
                formatted_analysis += "-" * 50 + "\n"
                analysis_formatted.append(formatted_analysis)
            return "\n".join(analysis_formatted)

        formatted_analysis = _format_analysis_for_prompt(state["analysis"])

        # Use a prompt to generate questions about the repository
        result = await self.llm.ainvoke(
            question_generation_prompt.format(
                repo_analysis=formatted_analysis, repo_url=state["repo_url"]
            )
        )

        # Parse questions from the response
        questions_text = str(result.content)
        questions = [q.strip()
                     for q in questions_text.split("\n") if q.strip()]

        logger.info(f"Generated {len(questions)
                                 } questions about the repository")

        return {**state, "questions": questions}

    async def gather_context(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== GATHERING CONTEXT FROM REPOSITORY FILES ===")
        logger.info("Searching repository files for answers to questions")

        context = []

        # For each question, perform a vector search to find relevant file content
        for question in state["questions"]:
            try:
                # Convert question to embedding
                question_embedding = self.embeddings.embed_query(question)

                # Use the embedding to search for similar content
                relevant_files = await self.repository_service.search_similar_content(
                    embedding=question_embedding,
                    limit=3,  # Get top 3 most relevant files per question
                )

                for file_content in relevant_files:
                    context.append(
                        {
                            "question": question,
                            "file_path": file_content.path,
                            "content": file_content.content,
                        }
                    )

                logger.info(
                    f"Found {len(relevant_files)} relevant files for question: {
                        question
                    }"
                )
            except Exception as e:
                logger.error(
                    f"Error gathering context for question '{
                        question}': {str(e)}"
                )

        logger.info(f"Gathered context from {len(context)} file segments")

        return {**state, "context": context}

    async def plan(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== PLANNING README ===")
        logger.info("Processing repository analysis and context for planning")

        def _format_analysis_for_prompt(analysis_list: list[dict[str, str]]) -> str:
            analysis_formatted = []
            for analysis in analysis_list:
                formatted_analysis = f"File: {analysis['path']}\n"
                formatted_analysis += f"Analysis: {analysis['analysis']}\n"
                formatted_analysis += "-" * 50 + "\n"
                analysis_formatted.append(formatted_analysis)
            return "\n".join(analysis_formatted)

        def _format_context_for_prompt(context_list: list[dict]) -> str:
            context_formatted = []
            for ctx in context_list:
                formatted_ctx = f"Question: {ctx['question']}\n"
                formatted_ctx += f"File: {ctx['file_path']}\n"
                formatted_ctx += (
                    # Truncate long content
                    f"Content: {ctx['content'][:1000]}...\n"
                )
                formatted_ctx += "-" * 50 + "\n"
                context_formatted.append(formatted_ctx)
            return "\n".join(context_formatted)

        formatted_analysis = _format_analysis_for_prompt(state["analysis"])
        formatted_context = _format_context_for_prompt(state["context"])

        # Combine analysis and context for a more informed plan
        combined_input = f"Repository Analysis:\n{
            formatted_analysis
        }\n\nAdditional Context:\n{formatted_context}"

        result = await self.llm.ainvoke(
            plan_prompt.format(
                repo_analysis=combined_input,
                template=state["template"],
                repo_url=state["repo_url"],
            )
        )

        logger.info("README planning completed")

        return {
            **state,
            "plan": str(result.content),
        }

    async def _write_readme(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== WRITING README ===")

        # Format context for inclusion in the prompt
        def _format_context_for_prompt(context_list: list[dict]) -> str:
            context_formatted = []
            for ctx in context_list:
                formatted_ctx = f"Question: {ctx['question']}\n"
                formatted_ctx += f"File: {ctx['file_path']}\n"
                formatted_ctx += (
                    # Truncate long content
                    f"Content: {ctx['content'][:1000]}...\n"
                )
                formatted_ctx += "-" * 50 + "\n"
                context_formatted.append(formatted_ctx)
            return "\n".join(context_formatted)

        formatted_context = _format_context_for_prompt(state["context"])

        # Enhance the writing prompt with the gathered context
        enhanced_prompt = writing_readme_prompt.format(
            strategic_plan=state["plan"], additional_context=formatted_context
        )

        result = await self.llm.ainvoke(enhanced_prompt)
        logger.info("README content generation completed")

        return {
            **state,
            "readme": str(result.content),
        }

    async def gen_readme(
        self,
        repository: Repository,
        repo_analysis: list[dict[str, str]],
        template_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        logger.info("=== INITIATING README GENERATION ===")
        logger.info(f"Processing repository: {repository.url}")

        template_to_use = template_content if template_content else default_readme

        initial_state: RepoAnalyzerState = {
            "plan": "",
            "readme": "",
            "template": template_to_use,
            "analysis": repo_analysis,
            "repo_url": repository.url,
            "repository_id": repository.id,
            "context": [],
            "questions": [],
        }

        try:
            compiled_graph = self.graph.compile()
            final_state = await compiled_graph.ainvoke(initial_state)

            return {
                "repo_url": repository.url,
                "readme": final_state["readme"],
                "analysis": final_state["analysis"],
                "metadata": {
                    "questions": final_state["questions"],
                    "context_files": [
                        ctx["file_path"] for ctx in final_state["context"]
                    ],
                },
                "template": template_to_use,
                "status": "success",
            }
        except Exception as e:
            logger.error(f"README generation failed: {str(e)}")
            raise ValueError(f"README generation failed: {str(e)}")

    def clear_cache(self):
        """Clear internal caches"""
        self._cache.clear()
        self._build_gen_readme_graph.cache_clear()
