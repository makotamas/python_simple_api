from flask import Flask, render_template, jsonify, request
import pickle
import uuid

app = Flask(__name__)

with open('projects.pickle', 'rb') as file:
    projects = pickle.load(file)['projects']

def save_data(data):
    with open('projects.pickle', 'wb') as file:
        pickle.dump(data, file)

@app.route("/")
def home():
  return render_template("index.html.j2", name="Tomi")


@app.route("/projects")
def get_projects():
  # ezt még belewrapeljük egy dictionary-ba, csakhogy szebb legyen
  return jsonify({'projects': projects}), 200, {
      # jsonify fv átalakítja a kapott fájt json  response formátummá
      # add Access-Control-Allow-Origin header
      'Access-Control-Allow-Origin': 'http://127.0.0.1:8080'
  }


@app.route("/project", methods=['POST'])
def create_project():
  request_data = request.get_json()
  new_project_id = uuid.uuid4().hex[:24]
  new_project = {
      'name': request_data['name'],
      'creation_date': request_data['creation_date'],
      'completed': request_data['completed'],
      'tasks': request_data['tasks'],
      'project_id': new_project_id
  }
  # loop through each task and add task_id for each:
  for task in new_project['tasks']:
    task['task_id'] = uuid.uuid4().hex[:24]
    # also add checklist_id to each checklist item
    for checklist_item in task['checklist']:
      checklist_item['checklist_id'] = uuid.uuid4().hex[:24]

  projects.append(new_project)
  return jsonify({'message': f'project created with id: {new_project_id}'})


@app.route("/project/<string:project_id>")
def get_project(project_id):
  print(project_id)
  for project in projects:
    if project['project_id'] == project_id:
      return jsonify(project)
  return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:name>/tasks")
def get_project_tasks(name):
  for project in projects:
    if project['name'] == name:
      return jsonify({'tasks': project['tasks']})
  return jsonify({'message': 'project not found'}), 404


@app.route("/project/<string:name>/task", methods=['POST'])
def add_task_to_project(name):
  request_data = request.get_json()
  for project in projects:
    if 'name' in project and project['name'] == name:
      if 'completed' not in request_data or type(
          request_data['completed']) is not bool:
        return jsonify(
            {'message': 'completed is required and must be a boolean'}), 400
      new_task = {
          'name': request_data['name'],
          'completed': request_data['completed']
      }
      project['tasks'].append(new_task)
      return jsonify(new_task), 201
  return jsonify({'message': 'project not found'}), 404

@app.route("/project/<string:project_id>/complete", methods=['POST'])
def complete_project(project_id):
    for project in projects["projects"]:
        if project['project_id'] == project_id:
            if project['completed']:
                return '', 200
            else:
                project['completed'] = True
                save_data(projects)
                return jsonify(project), 200
    return jsonify({'message': 'project not found'}), 404
