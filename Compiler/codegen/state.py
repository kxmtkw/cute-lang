from Compiler.imagen.program import Procedure


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
		self._current_procedure_id: int = 1


	def get_procedure_id(self) -> int:
		"Return a new procedure ID starting from 1."
		curr_id = self._current_procedure_id
		self._current_procedure_id += 1
		return curr_id
	

	def new_procedure(self, proc: Procedure) -> None:
		"Start a new procedure context."
		self._proc_state = ProcedureState(proc)


	def end_procedure(self) -> None:
		"End the current procedure context."
		self._proc_state = None


	@property
	def current_state(self) -> ProcedureState:
		"Get the current procedure state."
		if self._proc_state is None:
			raise ValueError("No active procedure state.")
		return self._proc_state
	

	@property
	def current_procedure(self) -> Procedure:
		"Get the current procedure."
		return self.current_state.proc


	def get_slot(self) -> int | None:
		"Find an empty slot in the current procedure context. Returns None if no empty slot is found."
		state = self.current_state
		for i, occupied in enumerate(state.slots):
			if not occupied:
				state.slots[i] = True
				return i
		return None


	def get_continous_slots(self, count: int) -> list[int] | None:
		"Get `count` continuous slots, return None if the conditions could not be met."
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
		"Get a temporary slot for expression evaluations."
		slot = self.get_slot()
		if slot is not None:
			self.current_state.tmp_slots.add(slot)
		return slot

	def get_continous_tmp_slots(self, count: int) -> list[int] | None:
		"Get `count` temporary continuous slots, return None if the conditions could not be met."
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
					state.tmp_slots.add(s)
				return slots

		return None


	def free_slot(self, slot: int) -> None:
		"Free a slot."
		state = self.current_state
		state.slots[slot] = False
		state.tmp_slots.discard(slot)


	def free_slot_if_tmp(self, slot: int) -> None:
		"Only free a slot if it was temporary. Prevents freeing of variable slots."
		state = self.current_state
		if slot in state.tmp_slots:
			state.slots[slot] = False
			state.tmp_slots.remove(slot)


	def push_slot(self, slot: int) -> None:
		"Push a slot to the stack."
		self.current_state.slots_stack.append(slot)


	def pop_slot(self) -> int:
		"Pop a slot from the stack."
		return self.current_state.slots_stack.pop()


	def label(self) -> int:
		"Get a label ID to be used for Label generation."
		self._label_num += 1
		return self._label_num



