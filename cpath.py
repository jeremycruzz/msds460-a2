#!/usr/bin/env python3

# Critical Path Analysis 
from pulp import *
import matplotlib.pyplot as plt
import argparse

# Parse which case we want to do
parser = argparse.ArgumentParser(description="Critcal Path Analysis")
arggroup = parser.add_mutually_exclusive_group()
arggroup.add_argument('-w', action='store_true')
arggroup.add_argument('-b', action='store_true')
args = parser.parse_args()

# variables based on flag
case = 'expected'

if args.w:
    case = 'worst'

elif args.b:
    case = 'best'

plotFilePath = f'./data/{case}-case.png'
filePath = f'./data/{case}-case.txt'
plotTitle = f'({case} case)'

# Map for tasks that I probably should have done differently to avoid spaghetti
tasks = {
  'A': {
      'name': 'describe_product', 
      'expected': 10, 
      'best': 8, 
      'worst': 12, 
      'blockers':[]
      },
  'B': {
    'name': 'develop_marketing_strategy',
    'expected': 20,
    'best': 14,
    'worst': 23,
    'blockers':[]
    },
  'C': {'name': 'design_brochure',
    'expected': 30,
    'best': 21,
    'worst': 35,
    'blockers':['A']
    },
  'D1': {'name': 'requirements_analysis',
    'expected': 50,
    'best': 30,
    'worst': 70,
    'blockers':['A']
    },
  'D2': {'name': 'software_design',
    'expected': 50,
    'best': 30,
    'worst': 70,
    'blockers':['D1']
    },
  'D3': {'name': 'system_design',
    'expected': 60,
    'best': 35,
    'worst': 79,
    'blockers':['D1']
    },
  'D4': {'name': 'coding',
    'expected': 360,
    'best': 196,
    'worst': 536,
    'blockers':['D2','D3']
    },
  'D5': {'name': 'write_documentation',
    'expected': 60,
    'best': 34,
    'worst': 80,
    'blockers':['D4']
    },
  'D6': {'name': 'unit_testing',
    'expected': 130,
    'best': 70,
    'worst': 199,
    'blockers':['D4']
    },
  'D7': {'name': 'system_testing',
    'expected': 200,
    'best': 112,
    'worst': 276,
    'blockers':['D6']
    },
  'D8': {'name': 'package_deliverables',
    'expected': 40,
    'best': 23,
    'worst': 56,
    'blockers':['D5','D7']
    },
  'E': {'name': 'survey_potential_market',
    'expected': 60,
    'best': 44,
    'worst': 70,
    'blockers':['B','C']
    },
  'F': {'name': 'develop_pricing_plan',
    'expected': 40,
    'best': 28,
    'worst': 46,
    'blockers':['D8','E']
    },
  'G': {'name': 'develop_implementation_plan',
    'expected': 40,
    'best': 28,
    'worst': 46,
    'blockers':['A','D8']
    },
  'H': {'name': 'write_client_proposal',
    'expected': 20,
    'best': 16,
    'worst': 24,
    'blockers':['F','G']}
}

# Create a list of task Ids
idList = list(tasks.keys())

# Create the LP problem
prob = LpProblem("Critical_Path", LpMinimize)

# Create the LP variables
start_times = {task: LpVariable(f"start_{task}", 0, None) for task in idList}
end_times = {task: LpVariable(f"end_{task}", 0, None) for task in idList}

# Add the constraints
for id in idList:
    prob += end_times[id] == start_times[id] + tasks[id][case], f"{tasks[id]['name']}_expected"
    for blocker in tasks[id]['blockers']:
        prob += start_times[id] >= end_times[blocker], f"{id}_predecessor_{blocker}"

# Set the objective function
prob += lpSum([end_times[task] for task in idList]), "minimize_end_times"

# Solve the LP problem
status = prob.solve()

# Plot data and save
fig, ax = plt.subplots(figsize=(20,6))
y_pos = range(len(tasks))

for i, task in enumerate(tasks):
    start = value(start_times[task])
    end = value(end_times[task])
    ax.broken_barh([(start, end - start)], (i * 10, 9))

ax.set_yticks([5 + 10 * i for i in range(len(tasks))])
ax.set_yticklabels([f"[{id}]{tasks[id]['name']}" for id in tasks])
ax.set_xlabel('Hours')
ax.set_title(f'Project Schedule {plotTitle}')
plt.grid(True)
plt.savefig(plotFilePath)

# Write Data
print(f'writing to {filePath}')
with open(filePath, 'w') as file:
    original_stdout = sys.stdout
    sys.stdout = file
    print("Critical Path time:")
    for id in idList:
        if value(start_times[id]) == 0:
            print(f"{id} starts at time 0")
        if value(end_times[id]) == max([value(end_times[task]) for task in idList]):
            print(f"{id} ends at {value(end_times[id])} hours in expected")


    print("\nSolution variable values:")
    for var in prob.variables():
        if var.name != "_dummy":
            print(var.name, "=", var.varValue)

sys.stdout = original_stdout
print('write successful!')
