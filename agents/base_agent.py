"""
Base Agent Class for Financial Intelligence System
Provides common functionality for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.execution_count = 0
        self.success_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's main functionality
        Must be implemented by subclasses
        """
        pass

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent with error handling and metrics tracking

        Args:
            input_data: Input parameters for agent

        Returns:
            Dict containing agent results and metadata
        """
        start_time = time.time()
        self.execution_count += 1

        try:
            logger.info(f"Starting {self.agent_name}")

            # Execute agent logic
            result = self.execute(input_data)

            # Add metadata
            execution_time = time.time() - start_time
            self.total_execution_time += execution_time
            self.success_count += 1
            self.last_execution = datetime.now()

            result.update({
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'status': 'success',
                'execution_time': execution_time,
                'timestamp': self.last_execution.isoformat()
            })

            logger.info(f"{self.agent_name} completed in {execution_time:.2f}s")
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{self.agent_name} failed: {e}")

            return {
                'agent_name': self.agent_name,
                'agent_type': self.agent_type,
                'status': 'error',
                'error': str(e),
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        avg_time = self.total_execution_time / self.execution_count if self.execution_count > 0 else 0
        success_rate = self.success_count / self.execution_count if self.execution_count > 0 else 0

        return {
            'agent_name': self.agent_name,
            'total_executions': self.execution_count,
            'successful_executions': self.success_count,
            'success_rate': success_rate,
            'avg_execution_time': avg_time,
            'total_time': self.total_execution_time,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None
        }

    def reset_metrics(self):
        """Reset performance metrics"""
        self.execution_count = 0
        self.success_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None
