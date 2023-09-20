# AWS Resource Counter

**Author**: Yash Jhunjhunwala

AWS Resource Counter is a Python script for counting various AWS resources in your organization or AWS account. It supports counting resources like EC2 instances, Lambda functions, ECS Fargate tasks, EKS instances, ECR repositories, and ECR images across multiple AWS regions.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Usage](#usage)
- [Configuration](#configuration)
- [Contributing](#contributing)

## Prerequisites
Before using AWS Resource Counter, make sure you have the following prerequisites:
- Python 3.6 or higher installed.
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured with the necessary credentials.

## Getting Started
Follow these steps to get started with AWS Resource Counter:

### Installation
1. Clone the repository to your local machine:
   ```shell
   git clone https://github.com/yjhunjhun/resource-counter/aws/aws-resource-counter.git
2. Change to the project directory:
   ```shell
   cd aws-resource-counter
3. Install the required Python packages using pip:
   ```shell 
   pip install -r requirements.txt

### Usage
To count AWS resources, run the script and follow the prompts.
   ```shell
   python aws_resource_counter.py
```
You will be asked to select the resource counting type ('org' for organization-level or 'account' for account-level).

The script will generate a CSV file (resource_counts.csv) containing the resource counts and a log file (resource_count.log) with detailed logging information.

### Configuration
Before running AWS Resource Counter, ensure that your AWS CLI is properly configured with the necessary credentials. You can configure it using the following steps:

1. Open your terminal.
2. Run the following command to configure your AWS CLI:
   ```shell
   aws configure
3. Enter your AWS Access Key ID and Secret Access Key when prompted.
4. Set your default region and preferred output format.

### Contributing
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Create a pull request with a clear description of your changes.
