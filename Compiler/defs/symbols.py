from dataclasses import dataclass, field
from typing import TypeAlias


@dataclass
class Symbol:
	pass

SymbolTable: TypeAlias = dict[str, Symbol]


@dataclass
class Variable(Symbol):
	name: str
	type: "Container"


@dataclass
class Function(Symbol):
	name: str
	arguments: list[Variable]
	returns: "Container"


@dataclass
class Container(Symbol):
	name: str
	virtual: bool
	fields: dict[str, Variable]
	methods: dict[str, Function]