from dataclasses import dataclass, field
from typing import List, Literal, Optional, Union
from abc import ABC, abstractmethod

from Compiler.defs.op import BinaryOpType, UnaryOpType
from Compiler.defs.node_base import NodeBase
import Compiler.defs.symbols as sym


class Node:

    @dataclass
    class Program(NodeBase):
        artifacts: List[Node.Artifact]
        symtable: sym.SymbolTable = field(default_factory=sym.SymbolTable)

    @dataclass
    class Artifact(NodeBase):
        pass

    @dataclass
    class Function(Artifact):
        name: str
        params: List[Node.Declaration]
        body: Node.Block
        return_type: Node.Expression
        symbol: Optional[sym.Function] = None
        symtable: sym.SymbolTable = field(default_factory=sym.SymbolTable)

    @dataclass
    class Container(Artifact):
        name: str
        virtual: bool
        fields: list[Node.Declaration]
        symbol: Optional[sym.Container] = None

    @dataclass
    class ContainerImpl(Artifact):
        name: str
        methods: list["Node.Function"]
        symbol: Optional[sym.Container] = None

    class Statement(NodeBase):
        pass

    class Expression(Statement):
        pass

    # Statements

    @dataclass
    class Block(Statement):
        statements: List[Node.Statement]
        symtable: sym.SymbolTable = field(default_factory=sym.SymbolTable)

    @dataclass
    class If(Statement):
        condition: Node.Expression
        then_branch: Node.Statement
        else_branch: Optional[Node.Statement] = None

    @dataclass
    class While(Statement):
        condition: Node.Expression
        body: Node.Statement

    @dataclass
    class For(Statement):
        init: Node.Statement
        condition: Node.Expression
        step: Node.Expression
        body: Node.Statement
        symtable: sym.SymbolTable = field(default_factory=sym.SymbolTable)

    @dataclass
    class Declaration(Statement):
        name: str
        type: Optional[Node.Expression]
        value: Optional[Node.Expression]
        symbol: Optional[sym.Variable] = None

    @dataclass
    class BuiltinCommand(Statement):
        args: list[Node.Identifier]

    # expressions

    @dataclass
    class Literal(Expression):
        type: Literal["int", "float", "string", "char", "bool"]
        value: Union[int, float, str, bool]

    @dataclass
    class Identifier(Expression):
        value: str
        refers: Optional[sym.Symbol] = None

    @dataclass
    class BinaryOp(Expression):
        op: BinaryOpType
        left: Node.Expression
        right: Node.Expression

    @dataclass
    class UnaryOp(Expression):
        op: UnaryOpType
        operand: Node.Expression

    @dataclass
    class Call(Expression):
        callee: Node.Expression
        args: List[Node.Expression]

    @dataclass
    class Return(Expression):
        value: Optional[Node.Expression] = None


class NodeVisitor(ABC):


    def visit(self, node: NodeBase) -> NodeBase:
        method_name = f"visit{node.__class__.__name__}"
        visitor_method = getattr(self, method_name, self._generic_visit)
        return visitor_method(node)


    def _generic_visit(self, node: NodeBase):
        raise NotImplementedError(
            f"No visit{node.__class__.__name__} method defined in {self.__class__.__name__}"
        )


    def visitProgram(self, node: Node.Program) -> NodeBase:
        pass


    def visitFunction(self, node: Node.Function) -> NodeBase:
        pass


    def visitLiteral(self, node: Node.Literal) -> NodeBase:
        pass


    def visitIdentifier(self, node: Node.Identifier) -> NodeBase:
        pass


    def visitBlock(self, node: Node.Block) -> NodeBase:
        pass


    def visitIf(self, node: Node.If) -> NodeBase:
        pass


    def visitWhile(self, node: Node.While) -> NodeBase:
        pass


    def visitFor(self, node: Node.For) -> NodeBase:
        pass


    def visitDeclaration(self, node: Node.Declaration) -> NodeBase:
        pass


    def visitBinaryOp(self, node: Node.BinaryOp) -> NodeBase:
        pass


    def visitUnaryOp(self, node: Node.UnaryOp) -> NodeBase:
        pass


    def visitCall(self, node: Node.Call) -> NodeBase:
        pass


    def visitReturn(self, node: Node.Return) -> NodeBase:
        pass


    def visitBuiltinCommand(self, node: Node.BuiltinCommand) -> NodeBase:
        pass


    def visitContainer(self, node: Node.Container) -> NodeBase:
        pass


    def visitContainerImpl(self, node: Node.ContainerImpl) -> NodeBase:
        pass
