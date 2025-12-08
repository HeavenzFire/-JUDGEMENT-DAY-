import asyncio
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import deque

@dataclass
class Message:
    sender: str
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentMemory:
    max_tokens: int = 100000
    current_tokens: int = 0
    messages: deque = field(default_factory=lambda: deque(maxlen=1000))

    def add_message(self, message: Message):
        # Rough token estimation (1 token ≈ 4 characters)
        token_estimate = len(message.content) // 4 + 1
        if self.current_tokens + token_estimate > self.max_tokens:
            # Remove oldest messages until we have space
            while self.messages and self.current_tokens + token_estimate > self.max_tokens:
                removed = self.messages.popleft()
                self.current_tokens -= len(removed.content) // 4 + 1
        self.messages.append(message)
        self.current_tokens += token_estimate

    def get_context(self) -> str:
        return "\n".join([f"{msg.sender}: {msg.content}" for msg in self.messages])

class Grok5Agent:
    def __init__(self, agent_id: str, max_memory_tokens: int = 100000):
        self.agent_id = agent_id
        self.memory = AgentMemory(max_tokens=max_memory_tokens)
        self.message_queue = asyncio.Queue()
        self.is_active = True
        self.task_count = 0

    async def send_message(self, recipient: 'Grok5Agent', content: str, metadata: Dict[str, Any] = None):
        message = Message(
            sender=self.agent_id,
            content=content,
            metadata=metadata or {}
        )
        await recipient.receive_message(message)

    async def receive_message(self, message: Message):
        await self.message_queue.put(message)
        self.memory.add_message(message)

    async def process_task(self, task: str) -> str:
        self.task_count += 1
        # Simulate processing time
        await asyncio.sleep(0.1)

        # Simple response generation (in real implementation, this would use LLM)
        response = f"Agent {self.agent_id} processed: {task[:50]}... (Task #{self.task_count})"

        # Add to memory
        self.memory.add_message(Message(sender=self.agent_id, content=f"Processed: {task}"))

        return response

    async def run(self):
        while self.is_active:
            try:
                # Check for messages
                if not self.message_queue.empty():
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
                    # Process message (could trigger actions)
                    print(f"{self.agent_id} received: {message.content[:50]}...")

                # Simulate periodic activity
                await asyncio.sleep(0.5)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Agent {self.agent_id} error: {e}")
                break

    def stop(self):
        self.is_active = False

    def get_stats(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "tasks_processed": self.task_count,
            "memory_tokens": self.memory.current_tokens,
            "messages_count": len(self.memory.messages)
        }