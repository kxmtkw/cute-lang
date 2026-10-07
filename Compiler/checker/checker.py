from typing import Optional

from Compiler.defs.nodes import Node, NodeVisitor
from Compiler.defs.op import BinaryOpType, UnaryOpType
import Compiler.defs.primitives as prim
import Compiler.defs.symbols as sym


class TypeChecker(NodeVisitor):


    def __init__(self) -> None:
        super().__init__()
        self.program: Node.Program
        self.current_symtable: sym.SymbolTable

        self.symbol_stack: list[sym.Symbol] = []

        self.current_func_sym: Optional[sym.Function] = None
        self.first_pass: bool = True


    def _pop_symbol(self) -> sym.Symbol:
        if not self.symbol_stack:
            raise ValueError("Type checker expression stack is empty.")
        return self.symbol_stack.pop()


    def _get_expression_type(self, expression: Node.Expression, context: str) -> sym.Container:
        if not isinstance(expression, Node.Identifier):
            raise TypeError(f"{context} must name a container type.")
        type_symbol = expression.refers
        if not isinstance(type_symbol, sym.Container):
            raise TypeError(f"{expression.value} is not a valid {context}.")
        return type_symbol


    def typeof(self, symbol: sym.Symbol) -> sym.Container:
        "Returns the 'type' of any symbol."
        if isinstance(symbol, sym.Function):
            assert symbol.returns
            return symbol.returns
        elif isinstance(symbol, sym.Variable):
            assert symbol.type
            return symbol.type
        else:
            assert isinstance(symbol, sym.Container)
            return symbol


    def visitProgram(self, node: Node.Program):

        self.program = node
        self.current_symtable = node.symtable
        self.first_pass = True

        for artif in node.artifacts:
            self.visit(artif)

        self.first_pass = False

        for artif in node.artifacts:
            self.visit(artif)

        return node


    def visitFunction(self, node: Node.Function):

        self.current_symtable = node.symtable.set_parent(self.current_symtable)

        assert node.symbol

        if self.first_pass:

            for parameter in node.params:
                assert parameter.symbol
                assert parameter.type
                parameter.symbol.type = self._get_expression_type(
                    parameter.type,
                    f"parameter type for {parameter.name}",
                )

            node.symbol.returns = self._get_expression_type(
                node.return_type,
                f"return type for {node.name}",
            )

            self.current_symtable = self.current_symtable.get_parent()
            return node

        self.current_func_sym = node.symbol

        for decl in node.params:
            self.visit(decl)

        self.visit(node.return_type)
        symbol = self._pop_symbol()

        if not isinstance(symbol, sym.Container):
            raise TypeError(f"{symbol} is not a valid type.")

        self.current_func_sym.returns = symbol

        self.visit(node.body)

        self.current_symtable = self.current_symtable.get_parent()

        return node


    def visitLiteral(self, node: Node.Literal):
        match node.type:
            case "int":
                self.symbol_stack.append(prim.INT_CONTAINER)
            case "float":
                self.symbol_stack.append(prim.FLOAT_CONTAINER)
            case "bool":
                self.symbol_stack.append(prim.BOOL_CONTAINER)
            case "char":
                self.symbol_stack.append(prim.INT_CONTAINER)
            case "string":
                raise ValueError("String literals do not have a supported type.")
        return node


    def visitIdentifier(self, node: Node.Identifier):
        symbol = self.current_symtable.recursive_get(node.value, default=None)
        if symbol is None:
            raise ValueError(f"Unknown identifier: {node.value}")

        self.symbol_stack.append(symbol)
        return node


    def visitBlock(self, node: Node.Block):

        self.current_symtable = node.symtable.set_parent(self.current_symtable)

        for stmt in node.statements:
            self.visit(stmt)

        self.current_symtable = self.current_symtable.get_parent()

        return node


    def visitIf(self, node: Node.If):
        self.visit(node.condition)
        condition = self.typeof(self._pop_symbol())
        
        if condition is not prim.BOOL_CONTAINER:
            raise ValueError("if condition must be bool.")

        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)
        return node


    def visitWhile(self, node: Node.While):
        self.visit(node.condition)
        condition = self.typeof(self._pop_symbol())
        
        if condition is not prim.BOOL_CONTAINER:
            raise ValueError("while condition must be bool.")

        self.visit(node.body)
        return node


    def visitFor(self, node: Node.For):
        self.current_symtable = node.symtable.set_parent(self.current_symtable)
        self.visit(node.init)
        self.visit(node.condition)
        condition = self.typeof(self._pop_symbol())
        
        if condition is not prim.BOOL_CONTAINER:
            raise ValueError("for condition must be bool.")

        self.visit(node.step)
        self.visit(node.body)
        self.current_symtable = node.symtable.get_parent()
        return node


    def visitDeclaration(self, node: Node.Declaration):
        assert node.symbol

        if node.type is not None:
            self.visit(node.type)
            type_sym = self._pop_symbol()
            if not isinstance(type_sym, sym.Container):
                raise ValueError(f"Expected type to be a container, not {type_sym}.")
            node.symbol.type = type_sym

        if node.value is not None:
            self.visit(node.value)
            value_sym = self._pop_symbol()
            value_type = self.typeof(value_sym)
            if node.symbol.type is None:
                node.symbol.type = value_type
            elif value_type is not node.symbol.type:
                raise ValueError(
                    f"{value_type.name} is not assignable to {node.symbol.type.name} "
                    f"in declaration of {node.name}."
                )

        if node.symbol.type is None:
            raise ValueError(f"Declaration of {node.name} needs a type or an initializer.")

        return node


    def visitBinaryOp(self, node: Node.BinaryOp):
        self.visit(node.left)
        self.visit(node.right)

        right_type = self.typeof(self._pop_symbol())
        left_type = self.typeof(self._pop_symbol())

        if right_type is not left_type:
            raise ValueError(f"Cannot perform {node.op} between {node.left} and {node.right}.")

        if node.op == BinaryOpType.Assign:
            if not isinstance(node.left, Node.Identifier): # this should instead check for whether lhs is a Variable symbol todo
                raise ValueError("The left side of an assignment must be a variable.")
            self.symbol_stack.append(right_type)
            
        elif node.op == BinaryOpType.Access:
            self.symbol_stack.append(left_type)
            
        elif node.op in (
            BinaryOpType.Eq,
            BinaryOpType.Neq,
            BinaryOpType.Lt,
            BinaryOpType.Lte,
            BinaryOpType.Gt,
            BinaryOpType.Gte,
        ):
            self.symbol_stack.append(prim.BOOL_CONTAINER)
            
        elif node.op in (BinaryOpType.And, BinaryOpType.Or):
            if left_type is not prim.BOOL_CONTAINER or right_type is not prim.BOOL_CONTAINER:
                raise ValueError(f"{node.op} requires bool operands.")
            self.symbol_stack.append(prim.BOOL_CONTAINER)
            
        else:
            if left_type not in (prim.INT_CONTAINER, prim.FLOAT_CONTAINER):
                raise ValueError(f"{node.op} requires numeric operands.")
            self.symbol_stack.append(left_type)

        return node


    def visitUnaryOp(self, node: Node.UnaryOp):
        self.visit(node.operand)
        operand = self._pop_symbol()
        
        operand_type = self.typeof(operand)
        
        if node.op is UnaryOpType.Not and operand_type is not prim.BOOL_CONTAINER:
            raise ValueError(f"Unary {node.op} requires a bool operand.")
        
        if node.op is UnaryOpType.BitNot and operand_type is not prim.INT_CONTAINER:
            raise ValueError(f"Unary {node.op} requires an int operand.")
        
        if node.op is UnaryOpType.Negate and operand_type not in (
            prim.INT_CONTAINER,
            prim.FLOAT_CONTAINER,
        ):
            raise ValueError(f"Unary {node.op} requires a numeric operand.")
        
        self.symbol_stack.append(prim.BOOL_CONTAINER if node.op is UnaryOpType.Not else operand_type)
        
        return node


    def visitCall(self, node: Node.Call):

        self.visit(node.callee)

        func_sym = self._pop_symbol()

        if not isinstance(func_sym, sym.Function):
            raise ValueError(f"{node.callee} is not callable.")

        if len(node.args) != len(func_sym.arguments):
            raise ValueError(
                f"Function {func_sym.name} expects {len(func_sym.arguments)} arguments, "
                f"got {len(node.args)}."
            )

        assert func_sym.returns
        
        for index, (arg, parameter) in enumerate(zip(node.args, func_sym.arguments), start=1):
            self.visit(arg)
            argument = self._pop_symbol()
            assert parameter.type
            argument_type = self.typeof(argument)
            if argument_type is not parameter.type:
                raise ValueError(
                    f"{argument_type.name} is not assignable to {parameter.type.name} "
                    f"in argument {index} to {func_sym.name}."
                )

        self.symbol_stack.append(func_sym.returns)

        return node


    def visitReturn(self, node: Node.Return):
        if self.current_func_sym is None:
            raise TypeError("Return outside of function.")

        assert self.current_func_sym.returns
        
        if node.value is None:
            if self.current_func_sym.returns is not prim.VOID_CONTAINER:
                raise ValueError(f"Function {self.current_func_sym.name} must return a value.")
            
        else:
            self.visit(node.value)
            value = self._pop_symbol()
            value_type = self.typeof(value)
            if value_type is not self.current_func_sym.returns:
                raise ValueError(
                    f"{value_type.name} is not assignable to {self.current_func_sym.returns.name} "
                    f"in return from {self.current_func_sym.name}."
                )

        return node


    def visitBuiltinCommand(self, node: Node.BuiltinCommand):
        return node


    def visitContainer(self, node: Node.Container):

        assert node.symbol

        for member in node.fields:
            self.visit(member)

        return node


    def visitContainerImpl(self, node: Node.ContainerImpl):
        container = node.symbol
        
        if container is None:
            container_symbol = self.current_symtable.recursive_get(node.name, default=None)
            if not isinstance(container_symbol, sym.Container):
                raise ValueError(f"Container not found so can not be implemented: {node.name}")
            container = container_symbol
            node.symbol = container

        for method in node.methods:
            self.visit(method)

        return node
