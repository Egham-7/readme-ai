import logging
from langchain_groq import ChatGroq  
from langgraph.graph import StateGraph, START, END  
from typing import Any, Dict, TypedDict, Annotated, List, Union  
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage 
from pydantic import BaseModel, Field 
from langgraph.graph.message import add_messages  

logger = logging.getLogger(__name__)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    repo_analysis: Dict
    readme_chunks: List[str]


class ReadmeResponse(BaseModel):
    content: str = Field(description="The complete README content")


class Replan(BaseModel):
    feedback: str = Field(description="Analysis of why the README needs improvement")
    focus_areas: List[str] = Field(description="Areas to focus on in next iteration")


class JoinOutputs(BaseModel):
    thought: str = Field(description="Reasoning for the selected action")
    action: Union[ReadmeResponse, Replan]


class ReadmeCompilerAgent:
    def __init__(self, groq_api_key: str, model_name: str = "mixtral-8x7b-32768", temperature: float = 0.1):
        logger.info("Initializing ReadmeCompilerAgent")
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
        )
        self.graph = self._build_graph()
        logger.info("ReadmeCompilerAgent initialized successfully")
        self.groq_api_key = groq_api_key

    def _build_graph(self) -> StateGraph:
        logger.info("Building readme generation graph")
        graph = StateGraph(State)

        graph.add_node("process_analysis", self._process_analysis_node)
        graph.add_node("generate_readme", self._generate_readme_node)
        graph.add_node("join", self._join_node)

        graph.add_edge(START, "process_analysis")
        graph.add_edge("process_analysis", "generate_readme")
        graph.add_edge("generate_readme", "join")
        graph.add_edge("join", END)

        logger.info("Readme generation graph built successfully")
        return graph.compile()

    def _process_analysis_node(self, state: State) -> State:
        logger.info("Processing repository analysis")
        return {
            **state,
            "messages": state["messages"]
            + [
                SystemMessage(
                    content="Analyzing repository structure to generate a well-structured README."
                )
            ],
        }

    async def _generate_readme_node(self, state: State) -> State:
        logger.info("Generating README content")
        chunks = []
        async for chunk in self.model.astream(
            [
                {
                    "role": "system",
                    "content": "You are an expert technical writer. Based on the provided repository analysis, generate a clear, detailed, and well-structured README.md that highlights key project features, setup instructions, usage examples, and any important notes.",
                },
                {
                    "role": "user",
                    "content": f"Here is the repository analysis:\n\n{state['repo_analysis']}\n\nGenerate a high-quality README.md that effectively explains the project to new users.",
                },
            ]
        ):
            if isinstance(chunk.content, str):
                chunks.append(chunk.content)

        return {**state, "readme_chunks": chunks}

    def _join_node(self, state: State) -> State:
        readme_content = "".join(state["readme_chunks"])
        logger.info(f"Evaluating README quality:\n{readme_content}")

        evaluation = self.model.invoke(
            [
                {
                    "role": "system",
                    "content": "You are an expert technical reviewer. Evaluate the quality of the provided README.md based on clarity, completeness, structure, and usefulness. Determine if improvements are needed and suggest specific enhancements.",
                },
                {
                    "role": "user",
                    "content": f"Here is the current README:\n\n{readme_content}\n\nRepository Analysis:\n{state['repo_analysis']}\n\nAssess whether the README effectively explains the project. If improvements are needed, suggest clear and actionable revisions.",
                },
            ]
        )
        evaluation_text = str(evaluation.content)

        if "needs_improvement" in evaluation_text.lower():
            logger.info(f"README needs improvement: {evaluation}")
            return {
                **state,
                "messages": state["messages"]
                + [
                    SystemMessage(
                        content=f"Previous README needs improvement: {
                            evaluation}"
                    )
                ],
            }
        logger.info("README is satisfactory")
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=readme_content)],
        }



    async def generate_readme(self, repo_analysis: Dict[str, Any]) -> str:
        """Generate a complete README based on repository analysis."""
        logger.info("Starting README generation")

        initial_state = {
            "messages": [HumanMessage(content="Generate README")],
            "repo_analysis": repo_analysis,
            "readme_chunks": [],
        }

        final_state = None
        async for state in self.graph.astream(initial_state):
            final_state = state

        readme_content = "".join(final_state["readme_chunks"]) if final_state else ""
        logger.info("README generation completed")

        return readme_content
