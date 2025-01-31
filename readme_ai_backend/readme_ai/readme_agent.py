import logging
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import AsyncIterator, Dict, TypedDict, Annotated, List, Union
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages

logging.basicConfig(level=logging.INFO)
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
    def __init__(self, api_key: str, model_name: str, temperature: float, streaming: bool):
        self.model = ChatGroq(
            temperature=temperature,
            api_key=api_key,
            model_name=model_name,
            streaming=streaming
        )
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(State)
        
        graph.add_node("process_analysis", self._process_analysis_node)
        graph.add_node("generate_readme", self._generate_readme_node)
        graph.add_node("join", self._join_node)
        
        graph.add_edge("process_analysis", "generate_readme")
        graph.add_edge("generate_readme", "join")
        graph.add_edge(START, "process_analysis")
        
        graph.add_conditional_edges(
            "join",
            self._should_continue,
            {
                True: "process_analysis",
                False: END
            }
        )
        
        return graph.compile()

    def _process_analysis_node(self, state: State) -> State:
        """Processes repository analysis and prepares for README generation"""
        logger.info("Processing repository analysis")
        return {
            **state,
            "messages": state["messages"] + [
                SystemMessage(content="Processing repository structure for README generation")
            ]
        }

    async def _generate_readme_node(self, state: State) -> State:
        logger.info("Generating README content")
        chunks = []
        async for chunk in self.model.astream([
            {
                "role": "system",
                "content": "Generate a comprehensive README.md based on repository analysis"
            },
            {
                "role": "user", 
                "content": f"Repository analysis: {state['repo_analysis']}"
            }
        ]):
            chunks.append(chunk.content)
            logger.info(f"Generated README chunk: {chunk.content}")
            
        return {
            **state,
            "readme_chunks": chunks
        }

    def _join_node(self, state: State) -> State:
        """Evaluates README quality and decides on replanning"""
        readme_content = "".join(state["readme_chunks"])
        logger.info(f"Evaluating README quality:\n{readme_content}")
        
        evaluation = self.model.invoke([
            {
                "role": "system",
                "content": "Evaluate the README quality and decide if it needs improvement"
            },
            {
                "role": "user",
                "content": f"README:\n{readme_content}\nRepo Analysis:{state['repo_analysis']}"
            }
        ])
        
        if "needs_improvement" in evaluation.content.lower():
            logger.info(f"README needs improvement: {evaluation}")
            return {
                **state,
                "messages": state["messages"] + [
                    SystemMessage(content=f"Previous README needs improvement: {evaluation}")
                ]
            }
        logger.info("README is satisfactory")
        return {
            **state,
            "messages": state["messages"] + [
                AIMessage(content=readme_content)
            ]
        }

    def _should_continue(self, state: State) -> bool:
        return isinstance(state["messages"][-1], SystemMessage)

    async def generate_readme(self, repo_analysis: Dict) -> AsyncIterator[str]:
        logger.info("Starting README generation")
        initial_state = {
            "messages": [HumanMessage(content="Generate README")],
            "repo_analysis": repo_analysis,
            "readme_chunks": []
        }
        
        async for state in self.graph.astream(initial_state):
            if "readme_chunks" in state and state["readme_chunks"]:
                for chunk in state["readme_chunks"]:
                    logger.info(f"Yielding README chunk: {chunk}")
                    yield chunk
