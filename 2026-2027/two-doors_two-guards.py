# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for detailsolver.

import z3

# 1. Define the Variables
# True = Freedom/Truth, False = Damnation/Lie

# Door 1's destination (If True, Door 1 is Freedom. If False, Door 1 is Hell)
door1_is_freedom = z3.Bool("door1_is_freedom")

# Guard 1's nature (If True, they tell the truth. If False, they lie)
guard1_tells_truth = z3.Bool("guard1_tells_truth")

# 2. Establish the Rules of the Puzzle
solver = z3.Solver()

# Rule 1: One door is freedom, the other is hell (they are opposites)
# (Implicitly, Door 2 is freedom if Door 1 is not)
door2_is_freedom = z3.Not(door1_is_freedom)

# Rule 2: One guard tells the truth, the other lies (they are opposites)
guard2_tells_truth = z3.Not(guard1_tells_truth)


# 3. Model the Guards' behavior
# A guard's answer to a question matches the truth value of the statement
# IF they are a truth-teller. If they are a liar, their answer is the negated truth value.
def guard_answer(guard_truthful, statement_to_ask):
    return z3.If(guard_truthful, statement_to_ask, z3.Not(statement_to_ask))


# 4. Model the Complex Question:
# "If I asked the OTHER guard if Door 1 leads to freedom, what would they say?"

# What Guard 2 would say about Door 1:
what_guard2_would_say = guard_answer(guard2_tells_truth, door1_is_freedom)

# What Guard 1 actually answers when asked what Guard 2 would say:
guard1_final_answer = guard_answer(guard1_tells_truth, what_guard2_would_say)

# 5. Let's prove that Guard 1's final answer is ALWAYS the opposite of Door 1 being freedom
# We ask Z3 to find a scenario where the answer equals the truth about Door 1.
# If Z3 says "unsat" (unsatisfiable), it proves they can never be equal,
# meaning the answer is always the strict opposite!

solver.add(guard1_final_answer == door1_is_freedom)

print("Checking if the guard's answer could ever match the reality of Door 1...")
result = solver.check()

if result == z3.unsat:
    print("SUCCESS: Unsatisfiable! The guard's answer is mathematically guaranteed to be the OPPOSITE of the truth.")
    print("Therefore, if they answer 'Yes', Door 1 is Hell (go to Door 2). If they answer 'No', Door 1 is Freedom.")
else:
    print("Found a flaw in the logic:", solver.model())
