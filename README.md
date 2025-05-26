# SocietySims: An Open-Source Sandbox for Simulating Societal Interactions with Large Language Models

## Overview

SocietySims is an infrastructure designed for researchers and developers to explore emergent societal behaviors and capabilities of Large Language Model (LLM) powered agents within a simulated environment. Originally based on AgentSims, which focused on LLM evaluation, SocietySims extends this by providing a platform to build, observe, and interact with communities of intelligent agents.

Researchers can construct diverse scenarios by designing the environment, populating it with autonomous agents (NPCs) driven by LLMs, and defining their goals and interaction protocols. The system allows for the study of how these agents collaborate, compete, form relationships, and develop complex societal dynamics. Additionally, a "Mayor" agent functionality allows for higher-level programmatic interventions and guidance within the simulated society.

The platform is designed to be customizable, allowing users to deploy different LLM models, implement custom agent memory and planning systems, and design unique evaluation metrics or observational frameworks.

**Note on Current Status (Important):**
*   **`tick.py` Script:** The core simulation progression script, `tick.py`, is suspected to have issues that may prevent simulations from running correctly. Due to limitations with the available development tools, diagnosing and fixing this script has not been possible. Users may encounter errors or unexpected behavior when attempting to run simulations using `python -u tick.py`.
*   **Tooling Limitations:** The development environment currently has limitations that prevent automated code modifications. This has impacted the ability to fully debug and verify all components.

Despite these challenges, the server setup, agent creation, and client interface can still be explored.

## Features

*   **LLM-Powered Agents:** Create autonomous NPCs driven by models like GPT-3.5, GPT-4, or custom LLMs.
*   **Customizable Environment:** Design and build simulation environments with various buildings and interactive objects.
*   **Mayor Functionality:** Implement a "Mayor" agent (`mayor.py`) that can make high-level decisions, such as constructing new buildings or introducing new NPCs, influencing the town's development.
*   **Interactive Web Client:** A web-based GUI (`client/index.html`) allows for visualization of the simulation, creation of agents and buildings, and interaction.
*   **Configurable Agent Systems:** Define different memory and planning systems for agents (see `config/agent.json`).
*   **Evaluation Framework:** (Inherited from AgentSims) A system for posing questions to agents and evaluating their responses, which can be adapted for observing societal metrics (see `config/eval.json`).

## Dependencies
```
Python: 3.9.x (recommended, as per original docs)
MySQL: 8.0.31 (or compatible)
```
Deployment on MacOS or Linux is recommended for better stability.

## API Key for LLMs
To use LLM-powered agents, you need to provide API keys. Create the following file:
```
config/api_key.json
```
**Do not commit this file to Git.**

Example content for `config/api_key.json`:
```json
{"gpt-4": "YOUR_GPT4_API_KEY", "gpt-3.5": "YOUR_GPT3.5_API_KEY"}
```
For deploying your own models, refer to the original AgentSims documentation (links may be in older README versions or project wiki if available).

## Folder Creation
Before running, ensure these directories exist in the project root:
```
mkdir snapshot
mkdir logs
```
It's also recommended to review `config/app.json` and adjust `tick_count_limit`, `mayor_count_limit`, and cooldowns to suitable values to manage API costs and simulation speed.

## Setup and Execution

**1. MySQL Initialization**
MySQL is used for data storage. After installing MySQL:
   * Start the MySQL service.
   * Connect to MySQL (e.g., using `sudo mysql` or `mysql -u root -p`).
   * Execute the following commands:
    ```sql
    -- If your root user has a password, you might need to authenticate differently.
    -- The following command attempts to set passwordless auth for 'root'@'localhost' if not already set.
    -- USE WITH CAUTION and adapt to your MySQL security policy.
    ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '';
    flush privileges;

    create database `llm_account` default character set utf8mb4 collate utf8mb4_unicode_ci;
    create database `llm_game` default character set utf8mb4 collate utf8mb4_unicode_ci;
    create database `llm_game0001` default character set utf8mb4 collate utf8mb4_unicode_ci;
    create database `llm_game0002` default character set utf8mb4 collate utf8mb4_unicode_ci;
    ```
    *Note: If these `create database` commands fail due to existing databases, you might need to drop them first if you intend a clean setup (see 'Restarting the Simulation' section).*

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```
This will install Tornado, mysql-connector-python, websockets, and openai_async.

**3. (Optional) Design Tasks / Scenarios**
Refer to original AgentSims documentation or explore `config/` files to understand how to customize agent behaviors, goals, and evaluation criteria.

**4. Run the Main Server**
The server application (`main.py`) handles game logic and WebSocket connections.
```bash
./restart.sh
```
*   **Make it executable:** `chmod +x restart.sh`
*   **Functionality:** This script stops any existing `main.py` server process and starts a new one in the background. Output (stdout and stderr) from `main.py` is redirected to `nohup.log` in the directory where `restart.sh` is executed.
*   **Potential Issue in Older Versions:** Some older versions of `restart.sh` might have included a line like `tail -f nohup.log` at the end, which could cause the script to hang. If `restart.sh` doesn't exit after printing "process python server restarted", check the script and remove or comment out any such `tail -f` line. The version of `restart.sh` currently in the repository should be fine.
*   **Verification:** When the server starts successfully, you should see a message like `--------Server Started--------` in the `nohup.log` file.

**5. Run the Web Client**
Once the server is running:
   * Open `client/index.html` in your web browser.
   * **Note:** If it fails to open or connect, try right-clicking `index.html` in your IDE and selecting "Open in Browser," or serve the `client` directory using a local web server (e.g., `python -m http.server` from within the `client` directory, then access `http://localhost:PORT`).
   * When the client connects successfully, you should see a message like `somebody linked.` in the server's `nohup.log`.

**6. Create Agents and Buildings**
Use the web client interface to create agents and buildings in the simulation.

**7. Set Evaluation Targets (Optional)**
The evaluation system (from AgentSims) uses QA forms. Configure `config/eval.json` to define questions asked to agents and how their responses are measured. This may require a functioning simulation loop.

**8. Run the Simulation**

*   **Using `tick.py` (for simulation ticks):**
    ```bash
    python -u tick.py
    ```
    or with a step limit:
    ```bash
    python -u tick.py <number_of_ticks>
    ```
    **IMPORTANT NOTE:** As mentioned, `tick.py` is suspected to have unresolved issues. It may not run correctly or produce the intended simulation progression. This is due to tool limitations preventing its diagnosis and repair.

*   **Using `mayor.py` (for Mayor agent actions):**
    ```bash
    python -u mayor.py
    ```
    This script runs the Mayor agent, which can make decisions like building structures or creating NPCs based on its programming.

Refer to the original AgentSims paper (arXiv:2308.04026) for more details on the conceptual differences between tick-based simulation and mayor-driven actions if needed.

## Restarting the Simulation (Full Reset)
If you need to completely reset the simulation state:
1.  Stop the server (e.g., by running `kill $(ps -ef|grep main.py|grep -v grep|awk '{print $2}')` if `restart.sh` doesn't work).
2.  Remove snapshot data: `rm -rf snapshot/app.json` (and potentially `snapshot/mayors.json`).
3.  Reset MySQL databases (USE WITH CAUTION - this deletes data):
    ```sql
    -- Connect to MySQL
    drop database llm_account;
    drop database llm_game0001;
    -- Potentially drop llm_game and llm_game0002 if they also need resetting
    -- Recreate them:
    create database `llm_account` default character set utf8mb4 collate utf8mb4_unicode_ci;
    create database `llm_game0001` default character set utf8mb4 collate utf8mb4_unicode_ci;
    -- etc.
    ```
4.  Run `./restart.sh` to start the server again.

## Contributing
Given the current tooling limitations impacting development, contributions for bug fixes (especially for `tick.py`) and improvements are welcome. If you identify issues or have suggestions, please open an issue on the project's repository. Adding a robust testing framework would also be highly beneficial.

## Authors and Citation (from original AgentSims)
***Authors***: Jiaju Lin, Haoran Zhao*, Aochi Zhang, Yiting Wu, Huqiuyue Ping, Qin Chen
***About Us***: PTA Studio (original developers)
***Contact Us***: zhaohaoran@buaa.edu.cn (original contact)

Please cite the original AgentSims paper if you use concepts or code from this repository:
```
@misc{lin2023agentsims,
      title={AgentSims: An Open-Source Sandbox for Large Language Model Evaluation}, 
      author={Jiaju Lin and Haoran Zhao and Aochi Zhang and Yiting Wu and Huqiuyue Ping and Qin Chen},
      year={2023},
      eprint={2308.04026},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```