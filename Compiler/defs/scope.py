from typing import Optional, TypeAlias

from Compiler.defs.node_base import NodeBase


class NameScope:

	def __init__(self, parent: Optional["NameScope"] = None) -> None:
		self.parent = parent
		self._defintions: dict[str, NodeBase] = {}


	def __setitem__(self, key: str, value: NodeBase):
		self._defintions[key] = value


	def __getitem__(self, key: str):
		if key in self._defintions:
			return self._defintions[key]

		if self.parent is not None:
			return self.parent[key]

		raise KeyError(key)


	def get(self, key: str, default: Optional[NodeBase]):
		if key in self._defintions:
			return self._defintions[key]

		if self.parent is not None:
			return self.parent.get(key, default)

		return default


	def has(self, key: str) -> bool:
		return key in self._defintions


	def remove(self, key: str):
		if key in self._defintions:
			return self._defintions.pop(key)

		if self.parent is not None:
			return self.parent.remove(key)

		raise KeyError(key)