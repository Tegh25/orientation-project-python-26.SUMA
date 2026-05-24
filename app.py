'''
Flask Application
'''
from dataclasses import asdict
from flask import Flask, jsonify, request
from models import Experience, Education, Skill

app = Flask(__name__)

data = {
    "experience": [
        Experience("Software Developer",
                   "A Cool Company",
                   "October 2022",
                   "Present",
                   "Writing Python Code",
                   "example-logo.png")
    ],
    "education": [
        Education("Computer Science",
                  "University of Tech",
                  "September 2019",
                  "July 2022",
                  "80%",
                  "example-logo.png")
    ],
    "skill": [
        Skill("Python",
              "1-2 Years",
              "example-logo.png")
    ]
}


@app.route('/test')
def hello_world():
    '''
    Returns a JSON test message
    '''
    return jsonify({"message": "Hello, World!"})


@app.route('/resume/experience', methods=['GET', 'POST'])
def experience():
    '''
    Handle experience requests
    '''
    if request.method == 'GET':
        experience_list = [
            {
                "title": exp.title,
                "company": exp.company,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "description": exp.description,
                "logo": exp.logo
            }
            for exp in data['experience']
        ]
        return jsonify(experience_list)

    if request.method == 'POST':
        new_experience = Experience(
            title=request.json['title'],
            company=request.json['company'],
            start_date=request.json['start_date'],
            end_date=request.json['end_date'],
            description=request.json['description'],
            logo=request.json['logo']
        )
        data['experience'].append(new_experience)
        index = len(data['experience']) - 1
        return jsonify({"id": index})

    return jsonify({})


@app.route('/resume/experience/<int:index>', methods=['GET'])
def get_experience(index):
    '''
    Get a specific experience by index
    '''
    if 0 <= index < len(data['experience']):
        exp = data['experience'][index]
        return jsonify({
            "title": exp.title,
            "company": exp.company,
            "start_date": exp.start_date,
            "end_date": exp.end_date,
            "description": exp.description,
            "logo": exp.logo
        })
    return jsonify({"error": "Experience not found"}), 404

@app.route('/resume/education', methods=['GET', 'POST'])
def education():
    '''
    Handles education requests
    '''
    if request.method == 'GET':
        return jsonify([asdict(entry) for entry in data['education']])

    if request.method == 'POST':
        education_entry = Education(**request.get_json())
        data['education'].append(education_entry)
        return jsonify({'id': len(data['education']) - 1})
    if request.method == 'DELETE':
        return _delete_education(request.get_json())

    return jsonify({})


@app.route('/resume/skill', methods=['GET', 'POST'])
def skill():
    '''
    Handles Skill requests
    '''
    if request.method == 'GET':
        index_param = request.args.get('index')
        if index_param is not None:
            try:
                index = int(index_param)
            except ValueError:
                return jsonify({"error": "index must be an integer"}), 400
            if index < 0 or index >= len(data["skill"]):
                return jsonify({"error": "skill not found"}), 404
            return jsonify(asdict(data["skill"][index]))
        return jsonify([asdict(s) for s in data["skill"]])

    if request.method == 'POST':
        try:
            new_skill = Skill(**request.get_json())
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid skill payload"}), 400
        data["skill"].append(new_skill)
        return jsonify({"id": len(data["skill"]) - 1})

    return jsonify({})

def _delete_education(body):
    if not body or 'id' not in body:
        return jsonify({"error": "ID is required for deletion"}), 400
    try:
        item_id = int(body['id'])
    except (ValueError, TypeError):
        return jsonify({"error": "ID must be an integer"}), 400
    if item_id < 0 or item_id >= len(data['education']):
        return jsonify({"error": "ID out of range"}), 404
    data['education'].pop(item_id)
    return jsonify({"deleted": item_id}), 200
    