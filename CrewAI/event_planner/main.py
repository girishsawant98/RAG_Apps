import os 
import yaml
import json
from pathlib import Path
from pydantic import BaseModel
from langchain_community.llms import Ollama
from helper import load_env, get_serper_api_key
load_env()

from crewai import Agent, Task, Crew, tools, Process, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel

#Environment setup
os.environ["CREWAI_LLM_PROVIDER"] = "ollama"
os.environ["SERPER_API_KEY"] = get_serper_api_key()
os.environ['OLLAMA_MODEL'] = 'llama3.2:b'
#os.environ["OPENAI_API_KEY"] = "NA"
#Setting up Ollama 
llm = LLM(model="ollama/llama3.2:3b", 
          temperature=0.1,
          base_url="http://localhost:11434"
    )  
    

# Configure CrewAI to use Ollama
os.environ["USE_LOCAL_OLLAMA"] = "true"

#initializing directory files to save the output files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Load Config files

with open(os.path.join(BASE_DIR, "config", "agents.yaml"), "r") as f:
    agents_config = yaml.safe_load(f)

with open(os.path.join(BASE_DIR, "config", "tasks.yaml"), "r") as f:
    tasks_config = yaml.safe_load(f)


# 3. Initializing Tools

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()


# 4. Create agents from Configs

agents = {}
for name, cfg in agents_config.items():
    agents[name] = Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        verbose=cfg.get("verbose", False),
        llm=llm
    )


# 5. Define Pydantic models

class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str


#6. Create tasks from Config

tasks = []
for name, cfg in tasks_config.items():
    output_file = cfg.get("output_file")
    if output_file:
        # make the path absolute
        output_file = os.path.join(BASE_DIR, output_file)
    task_kwargs = {
       "description": cfg["description"],
        "expected_output": cfg["expected_output"],
        "agent": agents[cfg["agent"]],
        #"human_input": cfg.get("human_input", False),
       # "async_execution": cfg.get("async_execution", True),
        "output_file": output_file       
    }
    if cfg.get("output_json") == "VenueDetails":
        task_kwargs["output_json"] = VenueDetails
    tasks.append(Task(**task_kwargs))


# 7. Create the Crew
crew = Crew(
    agents=list(agents.values()),
    tasks=tasks,
    process = Process.sequential,
    verbose=True,
    llm=llm

)

# 8. Run the crew

event_details = {
    "event_topic": "Tech Innovation Conference",
    "event_description": "A gathering of tech innovators and industry leaders to explore future technologies.",
    "event_city": "San Francisco",
    "tentative_date": "2023-09-15",
    "expected_participants": 500,
    "budget": 20000,
    "venue_type": "Conference Hall"
}


result = crew.kickoff(inputs=event_details)
print("\n🎯 Final Result:\n", result)


#Read Output
venue_file = os.path.join(OUTPUT_DIR, "venue_details.json")
marketing_file = os.path.join(OUTPUT_DIR, "marketing_report.md")

if os.path.exists(venue_file):
    with open(venue_file) as f:
        data = json.load(f)
        print("\n🏢 Venue Details:")
        print(json.dumps(data, indent=2))

if os.path.exists(marketing_file):
    print("\n📢 Marketing plan saved at:", marketing_file)



import asyncio, sys
try:
    asyncio.get_event_loop().close()
except Exception:
    pass
sys.exit(0)

