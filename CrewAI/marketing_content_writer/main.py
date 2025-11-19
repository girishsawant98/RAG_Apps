import yaml
import os
from crewai import Crew, Agent, Task, Process, LLM
from tools import local_research_tool, keyword_extractor_tool, competitor_tool, BASE_DIR
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
load_dotenv
# Ensure CrewAI uses the Ollama provider (prevents default OpenAI provider requiring an API key)
os.environ.setdefault("CREWAI_LLM_PROVIDER", "ollama")
os.environ["USE_LOCAL_OLLAMA"] = "true"

## Load YAML FILE
def load_yaml(path):
    full_path = os.path.join(BASE_DIR, path)
    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    

agents_cfg = load_yaml("config/agents.yaml")
tasks_cfg = load_yaml("config/tasks.yaml")

##---- TOOL MAP

TOOL_MAP = {
    "local_research": local_research_tool,
    "keyword_extractor": keyword_extractor_tool,
    "competitor_finder": competitor_tool
}
#Loading Ollama Model
llm = LLM(
    model="ollama/llama3.2:latest",
    base_url="http://localhost:11434"
)
agents = {}
for name, cfg in agents_cfg.items():
    tools = [TOOL_MAP[t] for t in cfg.get("tools", [])]
    agents[name] = Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        llm=llm,
        verbose=cfg["verbose"],
        allow_delegation=cfg["allow_delegation"],
        tools=tools
    )

tasks = []
for name, cfg in tasks_cfg.items():
    output_file = cfg.get("output_file")
    if output_file:
        # make the path absolute
        output_file = os.path.join(BASE_DIR, output_file)
    tasks.append(
        Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=agents[cfg["agent"]],
            output_file=cfg.get("output_file")
        )
    )

crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process=Process.sequential,
)

if __name__ == "__main__":
    result = crew.kickoff(
        inputs={"product_name": "EcoFresh Natural Handwash"}
    )
    print("FINAL OUTPUT:\n", result)
    




