import json
import pickle

with open('projects.json', 'r') as f:
    projects = json.load(f)

with open('projects.pickle', 'wb') as f:
    pickle.dump(projects, f)