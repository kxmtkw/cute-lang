from Compiler.codegen.program import Procedure


SLOT_COUNT = 256

class GeneratorState:


	def __init__(self) -> None:
		self._current_procedure: Procedure | None = None
		self._proc_slots: list[bool] = []
		self._tmp_slots: set[int] = set()
		self._slots_stack: list[int] = []
		self._variable_assignments: dict[str, int] = {} # variable name to slot
		self._label_num: int = 0


	def new_procedure(self, proc: Procedure):
		if self._current_procedure is not None:
			raise ValueError()
		self._current_procedure = proc
		self._proc_slots = [False for slot in range(SLOT_COUNT)]
		self._tmp_slots: set[int] = set()
		self._slots_stack.clear()
		self._variable_assignments.clear()


	def end_procedure(self):
		if self._current_procedure is None:
			raise ValueError()
		self._current_procedure = None


	@property
	def current_procedure(self) -> Procedure:
		if self._current_procedure is None:
			raise ValueError("current_procedure not assigned yet.")
		return self._current_procedure


	def get_slot(self) -> int | None:
		for i, slot in enumerate(self._proc_slots):
			if not slot:
				self._proc_slots[i] = True
				return i
		return None


	def get_continous_slots(self, count: int) -> list[int] | None:
		found: bool = True
		candidate: int = 0

		for i, slot in enumerate(self._proc_slots):
			if not slot:
				if not found: candidate = i
				if (i - candidate + 1) == count:
					return list(range(candidate, i + 1))
			else:
				found = False

		return None


	def get_tmp_slot(self) -> int | None:
		for i, slot in enumerate(self._proc_slots):
			if not slot:
				self._proc_slots[i] = True
				self._tmp_slots.add(i)
				return i
		return None
	

	def free_slot(self, slot: int):
		self._proc_slots[slot] = False
		if slot in self._tmp_slots: self._tmp_slots.remove(slot)


	def free_slot_if_tmp(self, slot: int):
		if slot in self._tmp_slots:
			self._proc_slots[slot] = False
			self._tmp_slots.remove(slot)


	def push_slot(self, slot: int):
		self._slots_stack.append(slot)


	def pop_slot(self) -> int:
		return self._slots_stack.pop()


	def set_variable_slot(self, name: str, slot: int):
		self._variable_assignments[name] = slot


	def get_variable_slot(self, name: str) -> int:
		return self._variable_assignments[name]


	def label(self) -> int:
		self._label_num += 1
		return self._label_num




