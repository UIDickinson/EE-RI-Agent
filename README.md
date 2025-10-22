# EE-RI-Agent

## Electrical/Electronics Research & Innovation AI Agent- Powered by Sentient ROMA & ODS

Specializing in Power Management ICs, EMC/EMI solutions, and Embedded Systems.

## Quick Start

```bash
# Clone and setup
git clone 
cd ee-research-scout
chmod +x setup.sh
./setup.sh

# Start services
cd roma && docker-compose up -d
cd ../frontend && npm install && npm run dev
```

## Access
- Chat Interface: http://localhost:3000
- ROMA Backend: http://localhost:5000
- Neo4j Browser: http://localhost:7474

## Architecture

Built on [ROMA framework](https://github.com/sentient-agi/ROMA):
- **Planner**: EEPlanner decomposes queries into parallel research threads
- **Executors**: Datasheet, Paper, Patent, Supply Chain searches
- **Aggregator**: Synthesizes findings into academic reports
- **Tools**: Knowledge Graph, TRL Classifier, Regional Filters

## Usage

```python
from agents.ee_research_agent import create_ee_agent

agent = create_ee_agent()
result = await agent.run_query(
    "Find latest GaN power ICs for 48V automotive applications"
)
print(result)
```

## Features
- Query-driven (no automatic streaming)
- Multi-source intelligence (papers, patents, datasheets, supply chain)
- TRL classification (1-9 scale)
- EU/Asia regional focus
- Knowledge graph integration
- Academic-grade reports

## For test scripts check tests/test.md