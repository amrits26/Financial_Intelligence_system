"""State Manager for Multi-Agent Workflow"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class AgentState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class StateManager:
    """Manages state for multi-agent workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.current_workflow_id: Optional[str] = None
    
    def create_workflow(self, workflow_id: str, agents: List[str]) -> str:
        self.workflows[workflow_id] = {
            'id': workflow_id,
            'agents': {agent: AgentState.PENDING for agent in agents},
            'results': {},
            'errors': {},
            'start_time': datetime.now(),
            'end_time': None
        }
        self.current_workflow_id = workflow_id
        return workflow_id
    
    def save_agent_result(self, agent_name: str, result: Dict[str, Any]):
        if self.current_workflow_id:
            self.workflows[self.current_workflow_id]['results'][agent_name] = result
            self.workflows[self.current_workflow_id]['agents'][agent_name] = AgentState.COMPLETED
    
    def get_agent_result(self, agent_name: str) -> Optional[Dict[str, Any]]:
        if self.current_workflow_id:
            return self.workflows[self.current_workflow_id]['results'].get(agent_name)
        return None
    
    def get_all_results(self) -> Dict[str, Any]:
        if self.current_workflow_id:
            return self.workflows[self.current_workflow_id]['results']
        return {}
    
    def complete_workflow(self, workflow_id: str = None):
        """Mark workflow as completed"""
        wf_id = workflow_id or self.current_workflow_id
        if wf_id and wf_id in self.workflows:
            self.workflows[wf_id]['end_time'] = datetime.now()
            duration = (self.workflows[wf_id]['end_time'] - 
                       self.workflows[wf_id]['start_time']).total_seconds()
            logger.info(f"Completed workflow: {wf_id} in {duration:.2f}s")
    
    def fail_workflow(self, error: str, workflow_id: str = None):
        """Mark workflow as failed"""
        wf_id = workflow_id or self.current_workflow_id
        if wf_id and wf_id in self.workflows:
            self.workflows[wf_id]['end_time'] = datetime.now()
            self.workflows[wf_id]['error'] = error
            logger.error(f"Workflow {wf_id} failed: {error}")
