from setuptools import find_packages, setup

setup(
    name="diabetes-analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "uvicorn>=0.27.0",
    ],
    python_requires=">=3.9",
)
