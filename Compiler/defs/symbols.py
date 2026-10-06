from dataclasses import dataclass, field
from typing import Optional, TypeVar


@dataclass
class Symbol:
	pass


class SymbolTable(dict[str, Symbol]):
	"Extended dict class for parent/child symbol tables."

	def __init__(self):
		self.parent: Optional[SymbolTable] = None


	def set_parent(self, table: SymbolTable) -> SymbolTable:
		"Set the parent of the table and returns self."
		self.parent = table
		return self


	def get_parent(self) -> SymbolTable: 
		"Get the parent of the table, raises ValueError if no parent."
		if self.parent is None:
			raise ValueError("Symbol Table has no parent.")
		return self.parent


	def recursive_get(self, key: str, *, default: Symbol | None) -> Symbol | None:
		"Search the table and all its parents to get a symbol."  
		current = self
		while current is not None:
			if key in current:
				return current[key]
			current = current.parent

		return default

	
	def get_last_added(self) -> Symbol | None:
		"Get the last symbol added."
		return next(reversed(self.items()))[1]


	def __str__(self) -> str:
		return super().__str__() + " -> " + self.parent.__str__()




@dataclass
class Variable(Symbol):
	name: str = field(default_factory=str)
	type: Optional["Container"] = None


@dataclass
class Function(Symbol):
	name: str = field(default_factory=str)
	arguments: list[Variable] = field(default_factory=list)
	returns: Optional["Container"] = None
	is_entrypoint: bool = False


@dataclass
class Container(Symbol):
	name: str = field(default_factory=str)
	virtual: bool = False
	fields: dict[str, Variable] = field(default_factory=dict)
	methods: dict[str, Function] = field(default_factory=dict)