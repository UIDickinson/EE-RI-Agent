from setuptools import setup, find_packages

setup(
    name="ee-research-scout",
    version="1.0.0",
    description="Production-grade AI research agent for Electrical/Electronics Engineers",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "httpx>=0.25.2",
        "openai>=1.3.7",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "asyncpg>=0.29.0",
        "motor>=3.3.2",
        "neo4j>=5.14.1",
        "redis>=5.0.1",
        "slowapi>=0.1.9",
        "PyPDF2>=3.0.1",
        "pdfplumber>=0.10.3",
        "pandas>=2.1.3",
        "numpy>=1.26.2",
        "ulid-py>=1.1.0",
        "tenacity>=8.2.3"
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "ee-scout=src.main:main",
            "ee-scout-terminal=terminal_interactive:main"
        ]
    }
)