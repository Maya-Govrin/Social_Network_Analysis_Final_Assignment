# functions to implement Gale Shapely Stable Marriage Algorithm for the case of Law firms and students who are candidates for law internships
# implementation allows for unequal set sizes (num of positions != num of candidates), ties in preference lists and incomplete preference lists. each firm may offer several positions
# functions to check for stability are included (strong stability and super stability are relevant for the case of ties)

### functions ###
def stable_matching(student_prefs, firm_prefs, firm_quotas):
    # dictionaries for mapping
    students_matches_to_firms = {s: None for s in student_prefs}
    firms_matches_to_students = {f: [] for f in firm_prefs}

    # create a queue of proposals for each student, ordered by the rank (order acts as tie-breaker if ties exist)
    student_prefs_ordered = {s: sorted(prefs.keys(), key=lambda x: prefs[x]) for s, prefs in student_prefs.items()}
    # student proposal counter, starting at 0
    proposal_index = {s: 0 for s in student_prefs}
    # list of students not yet matched
    free_students = list(student_prefs.keys())

    # student proposal loops
    while free_students:
        student = free_students.pop(0)
        # the list of firms the student is interested in by order
        student_prefs_queue = student_prefs_ordered[student]

        # if student proposed to all firms in their list and was rejected, they are not returned to free_students (they stay unmatched in final matching)
        if proposal_index[student] >= len(student_prefs_queue):
            continue

        # the firm currently most preferred by the student
        firm = student_prefs_queue[proposal_index[student]]
        # proposal made, index incremented
        proposal_index[student] += 1

        # firm considers proposal:
        # check is firm even considers this student
        if student not in firm_prefs[firm]:
            # student is rejected and returned to free_students
            free_students.append(student)
            continue

        # deferred acceptance mechanism
        # if student is in the preference list of the firm, it is temporarily considered by the firm
        # current matches for the firm
        firm_current_matches = firms_matches_to_students[firm]
        # the preferences of that firm
        firm_ranks = firm_prefs[firm]

        # checking if firm still has open positions
        if len(firm_current_matches) < firm_quotas[firm]:
            firms_matches_to_students[firm].append(student)
            students_matches_to_firms[student] = firm
        else:
            # if firm quotas are full, new possible match is compared to least preferred student in the current matches of the firm
            firm_current_matches.sort(key=lambda s: firm_ranks[s], reverse=True)
            worst_student = firm_current_matches[0]
            # if new student is preferred to worst student in the current matches, a switch is made
            if firm_ranks[student] < firm_ranks[worst_student]:
                firms_matches_to_students[firm].remove(worst_student)
                firms_matches_to_students[firm].append(student)
                students_matches_to_firms[worst_student] = None
                students_matches_to_firms[student] = firm
                # worst student is now free to propose to new firms
                free_students.append(worst_student)
            else:
                # if new student is not better preferred than any student of the firm current matches, he is rejected and is free to propose to new firms
                free_students.append(student)

    return firms_matches_to_students, students_matches_to_firms

# stability checks functions
def check_weak_stability(firm_matches, student_matches, student_prefs, firm_prefs, firm_quotas):
    for student, student_ranks in student_prefs.items():
        current_firm = student_matches.get(student)
        # if student is unmatched, current rank is worse than any possible firm
        current_student_rank = student_ranks[current_firm] if current_firm else float('inf')

        #checking if a blocking pair exists
        # check only firms the student actually ranked
        for firm in student_ranks:
            firm_ranks = firm_prefs[firm]
            # if student isn't on firm's list, no blocking pair
            if student not in firm_ranks:
                continue
            # if student prefers a firm over their current rank
            if student_ranks[firm] < current_student_rank:
                # check if preferred firm has open positions
                if len(firm_matches[firm]) < firm_quotas[firm]:
                    return False
                # or if firm strictly prefers student to current matches
                elif any(firm_ranks[student] < firm_ranks[curr] for curr in firm_matches[firm]):
                    return False
    return True

def check_strong_stability(firm_matches, student_matches, student_prefs, firm_prefs, firm_quotas):
    for student, student_ranks in student_prefs.items():
        current_firm = student_matches.get(student)
        # if student is unmatched, current rank is worse than any possible firm
        current_student_rank = student_ranks[current_firm] if current_firm else float('inf')

        # checking if a blocking pair exists
        # check only firms the student actually ranked
        for firm in student_ranks:
            # skip pairs already matched
            if firm == current_firm:
                continue
            firm_ranks = firm_prefs[firm]
            # if student isn't on firm's list, no blocking pair
            if student not in firm_ranks:
                continue

            # student preference checks
            #  student strictly prefers a firm over their current match
            student_strictly = student_ranks[firm] < current_student_rank
            #  student weakly prefers a firm over their current match
            student_weakly = student_ranks[firm] <= current_student_rank

            # firm preference checks
            open_positions = len(firm_matches[firm]) < firm_quotas[firm]
            #  firm strictly prefers a student over current match
            firm_strictly = open_positions or any(firm_ranks[student] < firm_ranks[curr] for curr in firm_matches[firm])
            # firm weakly prefers a student over their current match
            firm_weakly = open_positions or any(firm_ranks[student] <= firm_ranks[curr] for curr in firm_matches[firm])

            # check strong stability: a pair blocks if one is indifferent and the other has strict preference
            if (student_strictly and firm_weakly) or (student_weakly and firm_strictly):
                return False
    return True

def check_super_stability(firm_matches, student_matches, student_prefs, firm_prefs, firm_quotas):
    for student, student_ranks in student_prefs.items():
        current_firm = student_matches.get(student)
        # if student is unmatched, current rank is worse than any possible firm
        current_student_rank = student_ranks[current_firm] if current_firm else float('inf')

        # checking if a blocking pair exists
        # check only firms the student actually ranked
        for firm in student_ranks:
            # skip pairs already matched
            if firm == current_firm:
                continue
            firm_ranks = firm_prefs[firm]
            # if student isn't on firm's list, no blocking pair
            if student not in firm_ranks:
                continue

            #  student weakly prefers a firm over their current match
            student_weakly = student_ranks[firm] <= current_student_rank

            # firm preference checks
            open_positions = len(firm_matches[firm]) < firm_quotas[firm]
            # firm weakly prefers a student over their current match
            firm_weakly = open_positions or any(firm_ranks[student] <= firm_ranks[curr] for curr in firm_matches[firm])

            # check super stability: blocking pair exists of both are indifferent
            if firm_weakly and student_weakly:
                return False
    return True

if __name__ == '__main__':
  ### example data: lower number = better, same number = indifference ###
  student_preferences = {
      'C1': {'Firm1': 1, 'Firm2': 2},
      'C2': {'Firm1': 1, 'Firm2': 2, 'Firm3': 2},
      'C3': {'Firm2': 2, 'Firm3': 1},
      'C4': {'Firm1': 2, 'Firm2': 1, 'Firm3': 3}
  }
  
  firm_preferences = {
      'Firm1': {'C1': 1, 'C2': 1, 'C3': 1, 'C4': 2},
      'Firm2': {'C1': 2, 'C3': 1, 'C4': 1},
      'Firm3': {'C1': 1, 'C2': 1, 'C3': 1, 'C4': 2}
  }
  
  firm_quotas = {'Firm1': 1, 'Firm2': 2, 'Firm3': 3}

  ### printing results
  firm_matches, student_matches = stable_matching(student_preferences, firm_preferences, firm_quotas)
  print(f'firm matching results: {firm_matches}')
  print(f'student matching results: {student_matches}')
  
  weak_stability = check_weak_stability(firm_matches, student_matches, student_preferences, firm_preferences, firm_quotas)
  strong_stability = check_strong_stability(firm_matches, student_matches, student_preferences, firm_preferences, firm_quotas)
  super_stability = check_super_stability(firm_matches, student_matches, student_preferences, firm_preferences, firm_quotas)
  
  print(f'is matching weakly stable?: {weak_stability}')
  print(f'is matching strongly stable?: {strong_stability}')
  print(f'is matching super stable?: {super_stability}')



