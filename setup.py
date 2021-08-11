import setuptools

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="backlog_google_chat",
    version="0.0.1",
    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="author",
    package_dir={"": "backlog_google_chat"},
    packages=setuptools.find_packages(where="backlog_google_chat"),
    install_requires=[
        "aws-cdk.aws-apigateway==1.117.0",
        "aws-cdk.aws-certificatemanager==1.117.0",
        "aws-cdk.aws-lambda==1.117.0",
        "aws-cdk.aws-lambda-python==1.117.0",
        "aws-cdk.aws-logs==1.117.0",
        "aws-cdk.aws-route53==1.117.0",
        "aws-cdk.aws-route53-targets==1.117.0",
        "aws-cdk.core==1.117.0",
        "python-dotenv",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
