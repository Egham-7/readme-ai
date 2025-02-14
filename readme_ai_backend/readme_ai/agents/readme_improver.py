import logging
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, START, END  # type:ignore
from langchain_groq import ChatGroq  # type:ignore

logger = logging.getLogger(__name__)


class ImprovedReadmeState(TypedDict):
    plan: str
    readme: str
    current_markdown: str
    feedback: str
    improved_readme: str


class ReadmeImproverAgent:
    def __init__(self, model: str):
        logger.info("Initializing ReadmeImproverAgent")
        self.llm = ChatGroq(model, temperature=0.1)
        self.graph = self._build_improvement_graph()
        logger.info("ReadmeImproverAgent initialized successfully")

    def _build_improvement_graph(self) -> StateGraph:
        logger.info("Building README improvement graph")
        graph = StateGraph(ImprovedReadmeState)

        graph.add_node("plan_improvements", self.plan_improvements)
        graph.add_node("write_improved_readme", self.write_improved_readme)

        graph.add_edge(START, "plan_improvements")
        graph.add_edge("plan_improvements", "write_improved_readme")
        graph.add_edge("write_improved_readme", END)

        logger.info("README improvement graph built successfully")
        return graph

    async def plan_improvements(
        self, state: ImprovedReadmeState
    ) -> ImprovedReadmeState:
        print("\n=== PLANNING README IMPROVEMENTS ===")

        prompt = f"""Given the following README content and improvement request, create a strategic plan for enhancing it:
        
        CURRENT README:
        {state["current_markdown"]}
        
        IMPROVEMENT REQUEST:
        {state["feedback"]}
        
        Create a detailed plan outlining specific improvements while preserving valuable existing content."""

        result = await self.llm.ainvoke(prompt)

        logger.info("README improvement planning completed")

        return {**state, "plan": str(result.content)}

    async def write_improved_readme(
        self, state: ImprovedReadmeState
    ) -> ImprovedReadmeState:
        print("\n=== WRITING IMPROVED README ===")

        prompt = f"""Following this improvement plan:
        {state["plan"]}
        
        Enhance this README while maintaining its core structure:
        {state["current_markdown"]}
        
        Apply the requested improvements:
        {state["feedback"]}
        
        Generate an improved version that incorporates all enhancements while preserving valuable existing content."""

        result = await self.llm.ainvoke(prompt)

        logger.info("README improvement completed")

        return {**state, "improved_readme": str(result.content)}

    async def improve_readme(
        self,
        current_markdown: str,
        feedback: str,
    ) -> Dict[str, Any]:
        """
        Improve an existing README based on feedback or specific enhancement prompt.

        Args:
            current_markdown: The existing README content
            feedback: Specific feedback or enhancement prompt
        """
        logger.info("=== INITIATING README IMPROVEMENT ===")

        initial_state: ImprovedReadmeState = {
            "plan": "",
            "readme": "",
            "current_markdown": current_markdown,
            "feedback": feedback,
            "improved_readme": "",
        }

        try:
            compiled_graph = self.graph.compile()
            final_state = await compiled_graph.ainvoke(initial_state)

            return {
                "original_readme": current_markdown,
                "improved_readme": final_state["improved_readme"],
                "improvement_plan": final_state["plan"],
                "feedback": feedback,
                "status": "success",
            }

        except Exception as e:
            logger.error(f"README improvement failed: {str(e)}")
            raise ValueError(f"README improvement failed: {str(e)}")
