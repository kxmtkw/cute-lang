from typing import Optional, TypeAlias

from Compiler.defs.node_base import NodeBase


class NameScope:

	def __init__(self) -> None:
		self._defintions: dict[str, NodeBase] = {}


	def __setitem__(self, key: str, value: NodeBase):
		self._defintions[key] = value


	def __getitem__(self, key: str):
		return self._defintions[key]


	def get(self, key: str, default: Optional[NodeBase]):
		return self._defintions.get(key, default)


	def has(self, key: str) -> bool:
		return key in self._defintions


	def remove(self, key: str):
		self._defintions.pop(key)


NameScopeStack: TypeAlias = list[NameScope]