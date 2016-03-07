import operator
from Patient import Patient

operators = {'>':operator.gt,
            '<':operator.lt,
            "==":operator.eq,
            '>=':operator.ge}

class Criterion:
    def __init__(self, name, type, conditions):
        self.name = name
        self.type = type
        self.conditions = conditions

    def evaluate(self, patient_state):
        for var,sense,thresh in self.conditions:
            op = operators[sense]
            if var in patient_state:
                if any([op(val,thresh) for val in patient_state[var]]):
                    return True
        return False

def readCriteria(filename):
    infile = file(filename)
    criteria = []
    for l in infile:
        if '#' in l:
            continue

        l = l.split('|')
        type = l[0]
        name = l[1]
        conditions = [(' '.join(z.split()[:-2]), z.split()[-2], float(z.split()[-1])) for z in l[2:]]
        criteria.append(Criterion(name, type, conditions))
    return criteria
        

class Alerter:
    def __init__(self):
        self.criteria = readCriteria('settings/SEPSIS_CRITERIA.txt')
        self.patient = Patient()

    def ingest(self, record):
        self.patient.update_state(record)
        return [(c.name, c.type) for c in self.criteria if c.evaluate(self.patient.get_combined_state())]
