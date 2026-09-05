from enum import Enum
from typing import List, Union


class NodeBase:

	def dump(self, level: int = 0) -> str:
		indent = "  " * level
		node_name = self.__class__.__name__

		children: List[tuple[str, Union["NodeBase", List["NodeBase"]]]] = []
		info_bits = []

		for k, v in self.__dict__.items():
			if isinstance(v, NodeBase) or (
				isinstance(v, list) and v and isinstance(v[0], NodeBase)
			):
				children.append((k, v))
			elif isinstance(v, Enum):
				info_bits.append(f"{k}={v.name}")
			elif v is not None:
				info_bits.append(f"{k}={v!r}")

		info_str = f" ({', '.join(info_bits)})" if info_bits else ""
		lines = [f"{indent}{node_name}{info_str}"]

		for name, child in children:
			if isinstance(child, list):
				lines.append(f"{indent}  {name}:")
				for item in child:
					lines.append(item.dump(level + 2))
			else:
				lines.append(f"{indent}  {name}:")
				lines.append(child.dump(level + 2))

		return "\n".join(lines)

	def __repr__(self) -> str:
		return self.dump()
