import time
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple

@dataclass
class PersonState:
    last_seen: float = 0.0
    first_violation_time: Dict[str, Optional[float]] = field(default_factory=dict)
    fired: Dict[str, bool] = field(default_factory=dict)

class PPEViolationTracker:
    """
    ID bazlı PPE ihlallerini süreye göre takip eder.
    rule örnekleri: "no_helmet", "no_vest"
    """
    def __init__(self, rules_seconds: Dict[str, float], forget_after_sec: float = 2.0):
        self.rules_seconds = rules_seconds
        self.forget_after_sec = forget_after_sec
        self.people: Dict[int, PersonState] = {}

    def _get_state(self, pid: int) -> PersonState:
        if pid not in self.people:
            st = PersonState()
            for rule in self.rules_seconds:
                st.first_violation_time[rule] = None
                st.fired[rule] = False
            self.people[pid] = st
        return self.people[pid]

    def update_person(
        self,
        pid: int,
        now: float,
        violations: Dict[str, bool],  # {"no_helmet": True/False, ...}
    ) -> List[Tuple[int, str, float]]:
        """
        Trigger event döndürür: [(person_id, rule_name, duration_sec), ...]
        """
        st = self._get_state(pid)
        st.last_seen = now

        events = []

        for rule_name, is_viol in violations.items():
            if is_viol:
                if st.first_violation_time[rule_name] is None:
                    st.first_violation_time[rule_name] = now
                    st.fired[rule_name] = False

                dur = now - st.first_violation_time[rule_name]
                if dur >= self.rules_seconds[rule_name] and not st.fired[rule_name]:
                    st.fired[rule_name] = True
                    events.append((pid, rule_name, dur))
            else:
                st.first_violation_time[rule_name] = None
                st.fired[rule_name] = False

        return events

    def cleanup(self, now: float):
        to_del = [pid for pid, st in self.people.items() if (now - st.last_seen) > self.forget_after_sec]
        for pid in to_del:
            del self.people[pid]
