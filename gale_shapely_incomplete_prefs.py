
# student and firm preferences, firm quotas (open positions)
student_preferences = {
    'C1': ['Firm1', 'Firm2', 'Firm3'],
    'C2': ['Firm2', 'Firm3', 'Firm1'],
    'C3': ['Firm3', 'Firm2', 'Firm1'],
    'C4': ['Firm2', 'Firm1', 'Firm3']
}

firm_preferences = {
    'Firm1': ['C1', 'C2', 'C3', 'C4'],
    'Firm2': ['C2', 'C4', 'C3', 'C1'],
    'Firm3': ['C1', 'C3', 'C2', 'C4']
}

firm_quotas = {
    'Firm1': 1,
    'Firm2': 1,
    'Firm3': 2
}
# functions 
def stable_matching(student_prefs, firm_prefs, firm_quotas):
    # dictionaries for mappings
    students_matched = {s: None for s in student_prefs}
    firm_matches = {f: [] for f in firm_prefs}
    # student proposal index
    proposal_index = {s: 0 for s in student_prefs}
    # list of students not yet matched
    free_students = list(student_prefs.keys())

    #proposal loop
    while free_students:
        student = free_students.pop(0)
        # get the most preferred firm on the student list
        prefs = student_prefs[student]

        # if student finished their list and found no match student stays unmatched
        if proposal_index[student] >= len(prefs):
            continue

        if proposal_index[student] < len(prefs):
            firm = prefs[proposal_index[student]]
            proposal_index[student] += 1

            # the firm makes a decision - accept or reject
            current_firm_matches = firm_matches[firm]
            quota = firm_quotas[firm]

            if len(current_firm_matches) < quota:
                # scenario 1: firm has more open positions so it accepts student for now
                firm_matches[firm].append(student)
                students_matched[student] = firm
            else:
                # scenario 2: firm is full
                # firm compares student to least preferred existing match
                f_prefs = firm_prefs[firm]

                current_firm_matches.sort(key=lambda s: f_prefs.index(s))
                least_preferred_student = current_firm_matches[-1]

                if f_prefs.index(student) < f_prefs.index(least_preferred_student):
                    # new student is preferred to  least preferred current match
                    firm_matches[firm].remove(least_preferred_student)
                    firm_matches[firm].append(student)

                    #rejects least preferred student
                    students_matched[least_preferred_student] = None
                    students_matched[student] = firm

                    # least preferred student rejected, can now propose again to other firms
                    free_students.append(least_preferred_student)
                else:
                    # scenario 3: firm prefers current matches to new proposal
                    free_students.append(student)

    return firm_matches


def check_stability(matches, student_prefs, firm_prefs, firm_quotas):
    # map student to their matched firm
    student_to_firm = {s: f for f, students in matches.items() for s in students}

    for s, prefs in student_prefs.items():
        # get the firms each student prefers over current match
        current_f = student_to_firm.get(s)

        # ff student is unmatched, they prefer any firm on their list over 'None'
        if current_f is None:
            better_firms = prefs
        else:
            better_firms = prefs[:prefs.index(current_f)]

        for f in better_firms:
            f_rank = firm_prefs[f]
            # a pair blocks if f prefers s over one of the current interns or f has unfilled position
            if len(matches[f]) < firm_quotas[f] or any(f_rank.index(s) < f_rank.index(curr) for curr in matches[f]):
                return False
    return True

# run gale shapely
matches = stable_matching(student_preferences, firm_preferences, firm_quotas)

print("Stable Matching")
for firm, students in matches.items():
    print(f"{firm}: {', '.join(students)}")

# check if matching is stable
is_stable = check_stability(matches, student_preferences, firm_preferences, firm_quotas)
print(f"is matching stable? {is_stable}")
