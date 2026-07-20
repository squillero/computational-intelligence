# Copyright © 2026 Giovanni Squillero / Politecnico di Torino
# https://github.com/squillero/computational-intelligence
# Free under certain conditions — see the license for detailsolver.

import z3

# Define variables
# For the God we ask:
god_is_truthful = z3.Bool("god_is_truthful")  # True if God is "True", False if "False"

# For the language:
da_means_yes = z3.Bool("da_means_yes")  # True if 'da' means Yes, False if 'da' means No

# The statement we actually want to know the truth of:
Q = z3.Bool("Q")


# Helper: Translate an English truth value into the God's internal language.
# If da_means_yes is True: True -> 'da', False -> 'ja'
# If da_means_yes is False: True -> 'ja', False -> 'da'
# This is equivalent to an XNOR (equality)
def to_native(val_bool, da_means_yes):
    return z3.If(da_means_yes, val_bool, z3.Not(val_bool))


# Step 1: What would this God's native response be if we directly asked them Q?
# If they are truthful, they answer Q's true value. If they are a liar, they answer z3.Not(Q).
direct_answer_bool = z3.If(god_is_truthful, Q, z3.Not(Q))
direct_answer_native = to_native(direct_answer_bool, da_means_yes)

# Step 2: Now we ask the compound question:
# "If I asked you Q, would you answer 'da'?"
#
# The truth of "Would you answer 'da'?" is: (direct_answer_native == True)
# We evaluate this statement, run it through the God's truth/lie filter, and get their native answer.
would_say_da = direct_answer_native == True
final_answer_bool = z3.If(god_is_truthful, would_say_da, z3.Not(would_say_da))
final_answer_native = to_native(final_answer_bool, da_means_yes)

# ----------------------------------------------------
# PROOF 1: If they answer 'da' (True), is Q guaranteed to be True?
# PROOF 2: If they answer 'ja' (False), is Q guaranteed to be False?
# ----------------------------------------------------
solver = z3.Solver()

# We assert that the final spoken answer 'da' (represented as True) is NOT equal to the truth of Q
solver.add(final_answer_native != Q)

print("Checking if the 'da/ja' bypass can fail...")
result = solver.check()

if result == z3.unsat:
    print("SUCCESS: Unsatisfiable! This proves that regardless of:")
    print("  1. Whether the God is True or False")
    print("  2. Whether 'da' means Yes or No")
    print("The God's spoken answer will ALWAYS perfectly match the truth value of Q!")
    print("  - If they say 'da', Q is TRUE.")
    print("  - If they say 'ja', Q is FALSE.")
else:
    print("Flaw found:", solver.model())
