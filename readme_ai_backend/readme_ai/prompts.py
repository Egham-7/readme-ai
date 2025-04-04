from langchain.prompts import ChatPromptTemplate  # type:ignore

choose_file_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a README documentation expert. Select only the essential files needed to create an effective README. Focus on:\n"
            "1. Files that demonstrate the core purpose and functionality\n"
            "2. Configuration files that show how to set up the project\n"
            "3. Files containing API endpoints or main interfaces\n"
            "4. Entry points that show how to run the project\n\n"
            "Return only the minimum number of file paths needed for README creation, ordered by importance. Select no more than 3-4 files total.",
        ),
        (
            "human",
            "From this repository structure, select only the files strictly necessary for creating an informative README:\n{repo_tree_md}\n\n"
            "Focus on files that will help users understand how to use, set up, and run the project. Be extremely selective - choose only what's essential for the README.",
        ),
    ]
)


binary_extensions = {
    # Audio
    ".mp3",
    ".wav",
    ".aac",
    ".flac",
    ".ogg",
    ".wma",
    ".m4a",
    # Video
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".flv",
    ".mpeg",
    ".mpg",
    ".webm",
    # Archives & Compressed Files
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".7z",
    ".rar",
    ".iso",
    ".cab",
    ".lz",
    ".xz",
    # Documents (binary formats)
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".odt",
    ".ods",
    ".odp",
    ".epub",
    ".mobi",
    # Executable & System Files
    ".exe",
    ".dll",
    ".com",
    ".msi",
    ".bin",
    ".sh",
    ".deb",
    ".rpm",
    ".so",
    ".jar",
    ".apk",
    ".app",
    ".sys",
    ".drv",
    ".efi",
    ".dmg",
    ".img",
    # Fonts
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".fon",
    # Compiled or Intermediate Files
    ".pyc",
    ".class",
    ".o",
    ".obj",
    ".a",
    ".lib",
    # Miscellaneous
    ".psd",
    ".indd",
    ".swf",
    ".bak",
    ".cache",
    # Images
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".ico",
    ".svg",
    # Other Binary Files
    ".bin",
    ".dat",
    ".dmp",
    ".iso",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".lz",
    ".7z",
    ".s7z",
    ".apk",
    ".bat",
    ".cab",
    ".cpl",
    ".cur",
    ".dll",
    ".dmg",
    ".drv",
    ".icns",
    ".ico",
    ".img",
    ".lnk",
    ".msi",
    ".sys",
    ".tmp",
}


analyse_file_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a technical documentation expert. Provide a concise and comprehensive analysis of the file. Your summary should be in a few sentences that clearly state what the file mainly contains and highlight any critical details necessary for writing a README.md file.",
        ),
        ("human", "Analyze this file:\nPath: {file_path}\nContent: {file_content}\n"),
    ]
)

plan_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a README specialist focused on creating clear, user-friendly documentation. Structure your README plan with:\n\n"
            "1. **Project Overview**\n"
            "   - Project name and description\n"
            "   - Key features\n\n"
            "2. **Getting Started**\n"
            "   - Prerequisites\n"
            "   - Installation steps\n\n"
            "3. **Usage**\n"
            "   - Basic examples\n"
            "   - Common use cases\n\n"
            "4. **Additional Information**\n"
            "   - Configuration\n"
            "   - Contributing guidelines\n"
            "   - License\n\n"
            "{template}"
            "Keep the plan focused on essential README elements.",
        ),
        (
            "human",
            "Create a README plan for: {repo_url}\n"
            "Based on this analysis:\n{repo_analysis}\n"
            "Provide a clear README outline.",
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
