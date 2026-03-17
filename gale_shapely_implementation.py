# student and firm rankings: lower number = better. same number = indifference
student_preferences = {
    'C1': {'Firm1': 1, 'Firm2': 2, 'Firm3': 3},
    'C2': {'Firm1': 1, 'Firm2': 1, 'Firm3': 2},
    'C3': {'Firm1': 3, 'Firm2': 2, 'Firm3': 1},
    'C4': {'Firm1': 2, 'Firm2': 1, 'Firm3': 3}
}

firm_preferences = {
    'Firm1': {'C1': 1, 'C2': 2, 'C3': 3, 'C4': 4},
    'Firm2': {'C1': 2, 'C2': 4, 'C3': 3, 'C4': 1},
    'Firm3': {'C1': 1, 'C2': 2, 'C3': 2, 'C4': 3}
}

firm_quotas = {'Firm1': 1, 'Firm2': 1, 'Firm3': 2}

def stable_matching(student_prefs, firm_prefs, firm_quotas):
    # dictionaries for mapping
    students_matched = {s: None for s in student_prefs}
    firm_matches = {f: [] for f in firm_prefs}

    # create a queue of proposals for each student (order acts as tie breaker if ties exist)
    proposal_queues = {s: sorted(prefs.keys(), key=lambda x: prefs[x]) for s, prefs in student_prefs.items()}
    # student proposal index
    proposal_index = {s: 0 for s in student_prefs}
    #list of students not yet matched
    free_students = list(student_prefs.keys())

    # proposal loop
    while free_students:
        student = free_students.pop(0)
        student_queue = proposal_queues[student]
        # if student finished their list and found no match student stays unmatched
        if proposal_index[student] >= len(student_queue):
            continue
        # get the most preferred firm on the student list
        firm = student_queue[proposal_index[student]]
        proposal_index[student] += 1

        current_matches = firm_matches[firm]
        firm_ranks = firm_prefs[firm]

        # scenario 1: firm has more open positions so it accepts student for now
        if len(current_matches) < firm_quotas[firm]:
            firm_matches[firm].append(student)
            students_matched[student] = firm
        else:
            # scenario 2: firm is full
            # firm compares student to least preferred existing match
            current_matches.sort(key=lambda s: firm_ranks[s], reverse=True)
            least_preferred_student = current_matches[0]

            # firms only swap least preferred with new proposal if new student is strictly better
            if firm_ranks[student] < firm_ranks[least_preferred_student]:
                # rejects least preferred student
                firm_matches[firm].remove(least_preferred_student)
                # new student is accepted
                firm_matches[firm].append(student)
                # least preferred student can now propose to other firms
                students_matched[least_preferred_student] = None
                students_matched[student] = firm
                free_students.append(least_preferred_student)
            else:
                # scenario 3: firm prefers current matches to new proposal (or they are equally preferred)
                free_students.append(student)

    return firm_matches


def check_stability(matches, student_prefs, firm_prefs, firm_quotas):
    # map student to their matched firm
    student_to_firm = {s: f for f, students in matches.items() for s in students}

    for s, s_ranks in student_prefs.items():
        # get the firms each student prefers over current match
        current_f = student_to_firm.get(s)
        # if student is unmatched, they prefer any firm on their list over None
        current_s_rank = s_ranks[current_f] if current_f else float('inf')

        # check every firm the student prefers or is indifferent to
        for f, f_ranks in firm_prefs.items():
            if s_ranks[f] < current_s_rank:
                # blocking pair is when student strictly prefers firm f
                # check only for weak stability: does firm f prefer student s strictly over any current intern
                if len(matches[f]) < firm_quotas[f] or any(f_ranks[s] < f_ranks[curr] for curr in matches[f]):
                    return False
    return True


matches = stable_matching(student_preferences, firm_preferences, firm_quotas)
print("Matching:", matches)
print("Is stable?", check_stability(matches, student_preferences, firm_preferences, firm_quotas))


##############################
# functions to check stability for the case of indifference: check other definitions of stability
def check_strong_stability(matches, student_prefs, firm_prefs, firm_quotas):
    # map student to their matched firm
    student_to_firm = {s: f for f, students in matches.items() for s in students}

    for s, s_ranks in student_prefs.items():
        # get the firms each student prefers over current match
        current_f = student_to_firm.get(s)
        # if student is unmatched, they prefer any firm on their list over None
        curr_s_rank = s_ranks[current_f] if current_f else float('inf')

        for f, f_ranks in firm_prefs.items():
            # a pair strongly blocks if:            
            # 1-student prefers firm strictly and firm prefers student at least as much as a current intern
            # or 2-student prefers firm at least as much and firm prefers student strictly over a current intern
            s_pref_strictly = s_ranks[f] < curr_s_rank
            s_indifferent = s_ranks[f] <= curr_s_rank
            
            # check firm side against its current interns
            current_interns = matches[f]

            # if firm has open positions, it strictly prefers any student on its list over an empty spot
            f_has_capacity = len(current_interns) < firm_quotas[f]

            f_prefers_strictly = f_has_capacity or any(f_ranks[s] < f_ranks[curr] for curr in current_interns)
            f_indifferent = f_has_capacity or any(f_ranks[s] <= f_ranks[curr] for curr in current_interns)

            if (s_pref_strictly and f_indifferent) or (s_indifferent and f_prefers_strictly):
                return False  
    return True


def check_super_stability(matches, student_prefs, firm_prefs, firm_quotas):
    # map student to their matched firm
    student_to_firm = {s: f for f, students in matches.items() for s in students}

    for s, s_ranks in student_prefs.items():
        # get the firms each student prefers over current match
        current_f = student_to_firm.get(s)
        #if student is unmatched they prefer any firm on their list over None
        curr_s_rank = s_ranks[current_f] if current_f else float('inf')

        for f, f_ranks in firm_prefs.items():
            # a pair super blocks if both are at least indifferent to the change
            s_indifferent = s_ranks[f] <= curr_s_rank
            current_interns = matches[f]
            f_has_capacity = len(current_interns) < firm_quotas[f]
            f_indifferent = f_has_capacity or any(f_ranks[s] <= f_ranks[curr] for curr in current_interns)

            if s_indifferent and f_indifferent:
                # ensures this is not the student's current match
                if f != current_f:
                    return False  
    return True

print(f"Is Strongly Stable: {check_strong_stability(matches, student_preferences, firm_preferences, firm_quotas)}")
print(f"Is Super Stable: {check_super_stability(matches, student_preferences, firm_preferences, firm_quotas)}")


