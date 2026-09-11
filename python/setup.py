# ============================================================================
# SBRCORE Python Package
# Setup and requirements
# ============================================================================

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sbrcore',
    version='1.0.0',
    author='SBR Empire',
    description='Shared core library for SBR Empire products',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sbr-empire/sbrcore',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Flask>=2.3.0',
        'FastAPI>=0.100.0',
        'sqlalchemy>=2.0.0',
        'python-dotenv>=1.0.0',
        'pyjwt>=2.8.0',
        'bcrypt>=4.0.0',
        'httpx>=0.24.0',
        'pytest>=7.0.0',
        'python-multipart>=0.0.6',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'ai': [
            'openai>=1.0.0',
            'anthropic>=0.7.0',
            'google-generativeai>=0.3.0',
        ]
    }
)
