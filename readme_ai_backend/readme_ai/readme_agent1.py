from urllib.parse import urlparse
from github.ContentFile import ContentFile  # type:ignore
from github import Github, UnknownObjectException  # type: ignore
from typing import List
import logging
from typing import Dict, Any, TypedDict, Annotated, cast
from langgraph.graph import StateGraph, START, END  # type:ignore
from langchain_groq import ChatGroq  # type: ignore
from langchain.prompts import ChatPromptTemplate  # type: ignore
from pydantic import BaseModel, Field  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





class FileAnalysis(BaseModel):
    path: str = Field(description="Path of the analyzed file")
    analysis: str = Field(
        description="Detailed analysis of the file's purpose and functionality"
    )


class RepoAnalyzerState(TypedDict):
    plan: str
    readme:str
    template:str
    analysis:str


class ReadmeCompilerAgent:
    def __init__(self, groq_api_key: str):
        logger.info("Initializing RepoAnalyzerAgent")
        self.groq_api_key = groq_api_key
        self.llm = ChatGroq(
            model="mixtral-8x7b-32768",
            temperature=0.1,
        )
        self.graph = self._build_gen_readme_graph()
        logger.info("RepoAnalyzerAgent initialized successfully")

    def _build_gen_readme_graph(self) -> StateGraph:
        logger.info("Building analysis graph")
        graph = StateGraph(RepoAnalyzerState)

        graph.add_node("readme_plan", self.plan)
        graph.add_node("write_readme", self._write_readme)

        graph.add_edge(START, "readme_plan")
        graph.add_edge("readme_plan", "write_readme")
        graph.add_edge("write_readme", END)

        logger.info("Genrating README built successfully")
        return graph.compile()


    def plan(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== PLANNING README ===")
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a technical documentation strategist. Your role is to create a clear action plan for README generation based on repository analysis. Focus on:
                1. Content Prioritization
                - Identify critical features to highlight
                - Map technical complexities to explain
                - List unique selling points
                
                2. Structure Planning
                - Define section hierarchy
                - Plan content flow
                - Determine documentation gaps
                
                3. Implementation Strategy
                - Code example selection
                - Configuration showcase points
                - Integration demonstration areas
                
                4. Documentation Requirements
                - API documentation needs
                - Setup instruction details
                - Deployment guidance points"""
            ),
            (
                "human",
                """Using this repository analysis, create a detailed README generation plan:
                
                Analysis Data:
                {repo_analysis}
                
                Outline the strategic approach for converting this analysis into effective documentation."""
            )
        ])

        result = self.llm.invoke(prompt.format(repo_analysis=state["analysis"])),
        
        logger.info(f"README File PLAN: {result}")
        return {**state, "plan": str(result)}


    def _write_readme(self, state: RepoAnalyzerState) -> RepoAnalyzerState:
        print("\n=== WRITING README ===")
       
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a markdown documentation expert. Transform the repository analysis into a clear, professional README.md using proper markdown formatting. Include:

                1. Essential Sections
                - Project overview
                - Installation steps
                - Usage examples
                - API documentation
                - Development setup

                2. Technical Elements
                - Code blocks with language specification
                - Configuration examples
                - Command line instructions

                3. Markdown Best Practices
                - Consistent header hierarchy
                - Well-structured lists
                - Proper code formatting
                - Clear tables when needed"""
            ),
            (
                "human",
                """Create a README.md based on this analysis:

                Analysis:
                {strategic_plan}

                Generate production-ready markdown documentation."""
            )
        ])

        result = self.llm.invoke(prompt.format(strategic_plan=state["plan"])),
        
        logger.info(f"README File: {result}")

        return {**state, "readme":result }

    

    def gen_readme(self, repo_url: str, repo_analysis: str) -> str:
        logger.info("=== STARTING README GENERATION ===")
        logger.info(f"Repository URL: {repo_url}")

        initial_state: RepoAnalyzerState = {
            "plan": "",
            "readme": "",
            "template": "",
            "analysis": repo_analysis
        }

        logger.info("=== PROCESSING README GENERATION ===")
        
        final_state = initial_state
        for step in self.graph.stream(initial_state):
            if hasattr(step, "content"):
                current_state = {
                    **final_state,
                    "readme": step.content
                }
            else:
                current_state = step
                
            final_state = current_state["readme"]
            logger.info(f"Generation Step Completed: {current_state}")

        logger.info("=== README GENERATION COMPLETED ===")
        
        return final_state



    