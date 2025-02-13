import logging
from typing import Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, START, END  # type:ignore
from langchain_groq import ChatGroq  # type:ignore
from pydantic import BaseModel, Field  # type:ignore
from functools import lru_cache
from readme_ai.prompts import plan_prompt, writing_readme_prompt
from readme_ai.templates import default_readme

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


class ReadmeCompilerAgent:
    def __init__(self):
        logger.info("Initializing ReadmeCompilerAgent")
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1)
        self.graph = self._build_gen_readme_graph()
        self._cache = {}
        logger.info("ReadmeCompilerAgent initialized successfully")

    @lru_cache(maxsize=100)
    def _build_gen_readme_graph(self) -> Any:
        logger.info("Building README generation graph")
        graph = StateGraph(RepoAnalyzerState)

        # Add nodes with enhanced error handling
        graph.add_node("readme_plan", self.plan)
        graph.add_node("write_readme", self._write_readme)

        # Define graph flow
        graph.add_edge(START, "readme_plan")
        graph.add_edge("readme_plan", "write_readme")
        graph.add_edge("write_readme", END)

        logger.info("README generation graph built successfully")
        return graph

    async def plan(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== PLANNING README ===")
        logger.info("Processing repository analysis for planning")

        def _format_analysis_for_prompt(analysis_list: list[dict[str, str]]) -> str:
            analysis_formatted = []
            for analysis in analysis_list:
                formatted_analysis = "Repository Analysis:\n\n"
                formatted_analysis += f"File: {analysis['path']}\n"
                formatted_analysis += f"Analysis: {analysis['analysis']}\n"
                formatted_analysis += "-" * 50 + "\n"
                analysis_formatted.append(formatted_analysis)
            return "\n".join(analysis_formatted)

        prompt = plan_prompt
        logger.info(f"Analysis: {state['analysis']} ")
        formatted_analysis = _format_analysis_for_prompt(state["analysis"])
        logger.info(f"Formatted Analysis: {formatted_analysis}")

        result = await self.llm.ainvoke(
            prompt.format(
                repo_analysis=formatted_analysis,
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
        chain = writing_readme_prompt | self.llm
        result = await chain.ainvoke({"strategic_plan": state["plan"]})
        logger.info("README content generation completed")
        return {
            **state,
            "readme": str(result.content),
        }

    async def gen_readme(
        self,
        repo_url: str,
        repo_analysis: list[dict[str, str]],
        template_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        logger.info("=== INITIATING README GENERATION ===")
        logger.info(f"Processing repository: {repo_url}")

        template_to_use = template_content if template_content else default_readme

        initial_state: RepoAnalyzerState = {
            "plan": "",
            "readme": "",
            "template": template_to_use,
            "analysis": repo_analysis,
            "repo_url": repo_url,
        }

        try:
            compiled_graph = self.graph.compile()
            final_state = await compiled_graph.ainvoke(initial_state)

            return {
                "repo_url": repo_url,
                "readme": final_state["readme"],
                "analysis": final_state["analysis"],
                "metadata": final_state.get("metadata", {}),
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
