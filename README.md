# SoCal GenAI Agents

Welcome to the Southern California Generative AI Meetup Agents project! This repository contains the code and 
resources for developing and deploying AI agents demonstrated at our meetup on December 12, 2024.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project contains sample code using Streamlit and OpenAI Assistants API. 

## Features

- **Custom AI Models**: Tailored Agents for specific tasks. The agents are:
  - Simple: Respond like Shakespeare
  - Spreadsheet: Use the attached spreadsheet and code interpreter to respond
  - Tool: Uses a python function to to process two numbers
  - Google Spreadsheet: Uses sql to query a remote Google spreadsheet to respond
  - Message Action: Like Google Spreadsheet but will also email results
- **User-Friendly Interface**: Intuitive interfaces using Streamlit for interaction with gents.

## Installation

To get started with the SoCal GenAI Agents project, follow these steps:

1. Clone the repository:
  ```bash
  git clone https://github.com/yourusername/socal-genai-agents.git
  ```
2. Navigate to the project directory:
  ```bash
  cd socal-genai-agents
  ```
3. Install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Configuration

You will need to set the following environment variables (use .env)

- OPENAI_API_KEY
- OPENAI_DEPLOYMENT
- OPENAI_PROJECT
- GOOGLE_SECRETS_FILE
- GOOGLE_SHEETS_ID
- GOOGLE_SHEETS_RANGE
- CUSTOMER_DATA_FILE
- METADATA_FILE

If you want to use Google Auth you will also want to set

- GOOGLE_AUTH_ENABLED=True
- GOOGLE_AUTH_CREDS_PATH
- GOOGLE_AUTH_COOKIE_NAME
- GOOGLE_AUTH_COOKIE_KEY
- GOOGLE_AUTH_REDIRECT_URI

## Creation of the Agents

To create the agents execute the cells in the notebook
```
create_agents.ipynb
```


## Usage

To use the AI agents, run the following command:

```bash
streamlit run index.py
```

For detailed usage instructions, refer to the [documentation](docs/USAGE.md).

## Contributing

We welcome contributions to the SoCal GenAI Agents project! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.