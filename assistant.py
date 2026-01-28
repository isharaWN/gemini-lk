import json
from pathlib import Path

from livekit.agents import Agent, function_tool

from utils import Utils


class Assistant(Agent):
    def __init__(self, utils: Utils) -> None:
        self.utils = utils
        super().__init__(instructions=self.utils.read_instructions())
