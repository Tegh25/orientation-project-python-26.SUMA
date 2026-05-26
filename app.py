'''
Flask Application
'''
import re
from dataclasses import asdict
from flask import Flask, jsonify, request
from spellchecker import SpellChecker
from models import Experience, Education, Skill, UserInfo

app = Flask(__name__)
spellchecker = SpellChecker()

data = {
    "user_info": UserInfo(
        "John Doe",
        "+1234567890",
        "john@example.com"
    ),
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


@app.route('/resume/experience', methods=['GET', 'POST', 'DELETE'])
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

    if request.method == 'DELETE':
        return _delete_experience(request.get_json())
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
@app.route('/resume/education/<int:index>', methods=['GET'])
def education(index=None):
    '''
    Handles education requests
    '''
    if request.method == 'GET' and index is not None:
        if 0 <= index < len(data['education']):
            return jsonify(asdict(data['education'][index]))
        return jsonify({"error": "Education not found"}), 404

    if request.method == 'GET':
        return jsonify([asdict(entry) for entry in data['education']])

    if request.method == 'POST':
        education_entry = Education(**request.get_json())
        data['education'].append(education_entry)
        return jsonify({'id': len(data['education']) - 1})

    return jsonify({})


def _get_skill():
    index_param = request.args.get('index')
    if index_param is None:
        return jsonify([asdict(s) for s in data["skill"]])
    try:
        index = int(index_param)
    except ValueError:
        return jsonify({"error": "index must be an integer"}), 400
    if index < 0 or index >= len(data["skill"]):
        return jsonify({"error": "skill not found"}), 404
    return jsonify(asdict(data["skill"][index]))


def _post_skill():
    try:
        new_skill = Skill(**request.get_json())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid skill payload"}), 400
    data["skill"].append(new_skill)
    return jsonify({"id": len(data["skill"]) - 1})


@app.route('/resume/skill', methods=['GET', 'POST', 'DELETE'])
def skill(): # pylint: disable=too-many-return-statements
    '''
    Handles Skill requests
    '''
    if request.method == 'GET':
        return _get_skill()
    if request.method == 'POST':
        return _post_skill()
    if request.method == 'DELETE':
        return _delete_skill(request.get_json())
    return jsonify({})

def _delete_experience(body):
    if not body or 'id' not in body:
        return jsonify({"error": "ID is required for deletion"}), 400
    try:
        item_id = int(body['id'])
    except (ValueError, TypeError):
        return jsonify({"error": "ID must be an integer"}), 400
    if item_id < 0 or item_id >= len(data["experience"]):
        return jsonify({"error": "ID is out of range"}), 400
    data["experience"].pop(item_id)
    return jsonify({"deleted": item_id}), 200

def _delete_skill(body):
    if not body or 'id' not in body:
        return jsonify({"error": "ID is required for deletion"}), 400
    try:
        item_id = int(body['id'])
    except (ValueError, TypeError):
        return jsonify({"error": "ID must be an integer"}), 400
    if item_id < 0 or item_id >= len(data["skill"]):
        return jsonify({"error": "ID is out of range"}), 400
    data["skill"].pop(item_id)
    return jsonify({"deleted": item_id}), 200

@app.route('/resume/user_info', methods=['GET', 'POST', 'PUT'])
def user_info():
    '''
    Handles user_info requests
    '''
    if request.method == 'GET':
        return jsonify(asdict(data['user_info']))

    if request.method in ['POST', 'PUT']:
        req_data = request.get_json()
        name = req_data.get('name')
        phone_number = req_data.get('phone_number')
        email_address = req_data.get('email_address')

        if not all([name, phone_number, email_address]):
            return jsonify({"error": "Missing fields"}), 400

        # Enforce international country code (e.g. +1...)
        if not re.match(r'^\+\d{1,15}$', phone_number):
            return jsonify({
                "error": "Phone number must include international country code (e.g. +123456789)"
            }), 400

        data['user_info'] = UserInfo(
            name=name,
            phone_number=phone_number,
            email_address=email_address
        )
        return jsonify({
            "message": "User info updated successfully",
            "data": asdict(data['user_info'])
        })
    return jsonify({})


def _apply_spelling_correction(word):
    correction = spellchecker.correction(word)
    if correction is None:
        return word
    if word.isupper():
        return correction.upper()
    if word[0].isupper():
        return correction.capitalize()
    return correction


def _correct_text_spelling(text):
    return re.sub(r"[A-Za-z]+", lambda m: _apply_spelling_correction(m.group(0)), text)


def _collect_spelling_results():
    results = []

    def check_value(value):
        if not isinstance(value, str):
            return
        corrected = _correct_text_spelling(value)
        if corrected != value:
            results.append({"before": value, "after": corrected})

    for exp in data["experience"]:
        check_value(exp.title)
        check_value(exp.company)
        check_value(exp.description)

    for edu in data["education"]:
        check_value(edu.course)
        check_value(edu.school)

    for skill_entry in data["skill"]:
        check_value(skill_entry.name)
        check_value(skill_entry.proficiency)

    return results


@app.route('/resume/spellcheck', methods=['GET'])
def spellcheck():
    '''
    Returns spelling correction suggestions for resume entries
    '''
    return jsonify(_collect_spelling_results())
