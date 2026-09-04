from Compiler.codegen.program import Procedure


SLOT_COUNT = 256

class ProcedureState:

	def __init__(self, proc: Procedure) -> None:
		self.proc: Procedure = proc
		self.slots: list[bool] = [False for _ in range(SLOT_COUNT)]
		self.tmp_slots: set[int] = set()
		self.slots_stack: list[int] = []
		self.variable_assignments: dict[str, int] = {}


class GeneratorState:

	def __init__(self) -> None:
		self._proc_state: ProcedureState | None = None
		self._label_num: int = 0
		self._procedure_id_table: dict[str, int] = {}


	def get_procedure_id(self, name: str) -> int:
		if name == "main":
			return 0
		if name not in self._procedure_id_table:
			self._procedure_id_table[name] = len(self._procedure_id_table) + 1
		return self._procedure_id_table[name]


	def new_procedure(self, proc: Procedure) -> None:
		self._proc_state = ProcedureState(proc)


	def end_procedure(self) -> None:
		self._proc_state = None


	@property
	def current_state(self) -> ProcedureState:
		if self._proc_state is None:
			raise ValueError("No active procedure state.")
		return self._proc_state
	

	@property
	def current_procedure(self) -> Procedure:
		return self.current_state.proc


	def get_slot(self) -> int | None:
		state = self.current_state
		for i, occupied in enumerate(state.slots):
			if not occupied:
				state.slots[i] = True
				return i
		return None


	def get_continous_slots(self, count: int) -> list[int] | None:
		state = self.current_state
		found: bool = False
		candidate: int = 0

		for i, occupied in enumerate(state.slots):
			if occupied:
				found = False
				continue

			if not found:
				candidate = i
				found = True

			if (i - candidate + 1) == count:
				slots = list(range(candidate, i + 1))
				for s in slots:
					state.slots[s] = True
				return slots

		return None
	

	def get_tmp_slot(self) -> int | None:
		slot = self.get_slot()
		if slot is not None:
			self.current_state.tmp_slots.add(slot)
		return slot


	def free_slot(self, slot: int) -> None:
		state = self.current_state
		state.slots[slot] = False
		state.tmp_slots.discard(slot)


	def free_slot_if_tmp(self, slot: int) -> None:
		state = self.current_state
		if slot in state.tmp_slots:
			state.slots[slot] = False
			state.tmp_slots.remove(slot)


	def push_slot(self, slot: int) -> None:
		self.current_state.slots_stack.append(slot)


	def pop_slot(self) -> int:
		return self.current_state.slots_stack.pop()


	def set_variable_slot(self, name: str, slot: int) -> None:
		self.current_state.variable_assignments[name] = slot


	def get_variable_slot(self, name: str) -> int | None:
		return self.current_state.variable_assignments.get(name)


	def label(self) -> int:
		self._label_num += 1
		return self._label_num



