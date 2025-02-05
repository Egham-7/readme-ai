from langchain.prompts import ChatPromptTemplate  # type:ignore

choose_file_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a repository analysis expert. Identify the most essential files based on their position and name. Prioritize:\n"
            "1. Main entry point or core implementation file\n"
            "2. Primary configuration file\n"
            "3. Key documentation, if available\n"
            "4. Build/deployment definition\n\n"
            "Return only the exact file paths in order of importance, from most to least."
        ),
        (
            "human",
            "Analyze this repository structure and select only the most critical files based on their relevance:\n{repo_tree_md}\n\n"
            "Choose files strictly necessary for understanding the project—less is more."
        ),
    ]
)    

binary_extensions = {
            # Audio
        ".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", ".m4a",
        # Video
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".mpeg", ".mpg", ".webm",
        # Archives & Compressed Files
        ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".iso", ".cab", ".lz", ".xz",
        # Documents (binary formats)
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp", ".epub", ".mobi",
        # Executable & System Files
        ".exe", ".dll", ".com", ".msi", ".bin", ".sh", ".deb", ".rpm", ".so", ".jar", ".apk", ".app", ".sys", ".drv", ".efi", ".dmg", ".img",
        # Fonts
        ".ttf", ".otf", ".woff", ".woff2", ".fon",
        # Compiled or Intermediate Files
        ".pyc", ".class", ".o", ".obj", ".a", ".lib",
        # Miscellaneous
        ".psd", ".indd", ".swf", ".bak", ".cache"
        }


analyse_file_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a technical documentation expert. Provide a concise and comprehensive analysis of the file. Your summary should be in a few sentences that clearly state what the file mainly contains and highlight any critical details necessary for writing a README.md file."
        ),
        (
            "human",
            "Analyze this file:\nPath: {file_path}\nContent: {file_content}\n"
        ),
    ]
)

plan_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a technical documentation strategist crafting an effective README plan. Prioritize clarity, completeness, and usability by focusing on:\n\n"
            "1. **Content Strategy**\n"
            "   - Core features and unique selling points\n"
            "   - High-level technical architecture\n"
            "   - Key differentiators of the project\n\n"
            "2. **Structure Design**\n"
            "   - Logical section flow and organization\n"
            "   - Clear hierarchy for readability\n"
            "   - Ensuring content completeness\n\n"
            "3. **Technical Depth**\n"
            "   - Selecting relevant code examples\n"
            "   - Configuration and setup instructions\n"
            "   - Integration and usage patterns\n\n"
            "4. **Documentation Scope**\n"
            "   - API references (if applicable)\n"
            "   - Installation and setup requirements\n"
            "   - Deployment and usage guidelines\n"
            "   - Contribution and maintenance notes\n\n"
            "5. **Template Format**\n"
            "{template}"
            
            

            "Ensure the plan is concise, structured, and tailored to the project's complexity."
        ),
        (
            "human",
            "Based on the following analysis, create a structured README plan for next repo: {repo_url}:\n\n"
            "**Analysis Data:**\n{repo_analysis}\n\n"
            "Provide a refined, actionable documentation outline."
        ),
    ]
)



writing_readme_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a technical writer specializing in concise, high-quality MARKDOWN documentation. Your task is to create a production-ready README.md. Follow these guidelines:

            - **Project Overview**: Clear description with relevant badges.
            - **Quick Start**: Minimal setup instructions.
            - **Installation**: Dependencies, system requirements, and setup steps.
            - **Usage Examples**: Code snippets for real-world use.
            - **API Docs**: If applicable, structured API reference.
            - **Build & Deployment**: Steps for different environments.
            - **Contribution Guide**: Instructions for contributors.

            """,
        ),
        (
            "human",
            """Generate a **production-grade** README.md using the following:

            ### Inputs:
            - **Strategic Plan**: {strategic_plan}
            
            Ensure clarity, completeness, and professional formatting.
            """,
        ),
    ]
)
