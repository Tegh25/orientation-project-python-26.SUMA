'''
Flask Application
'''
import re
from dataclasses import asdict
from flask import Flask, jsonify, request
from models import Experience, Education, Skill, UserInfo

app = Flask(__name__)

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
        req = request.get_json()

        required_fields = ["title", "company", "start_date", "end_date", "description", "logo"]
        if not req or not isinstance(req, dict) or any(
            field not in req for field in required_fields
        ):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            new_experience = Experience(**req)
        except TypeError:
            return jsonify({"error": "Invalid format"}), 400

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

def _get_education(index):
    if index is not None:
        if 0 <= index < len(data['education']):
            return jsonify(asdict(data['education'][index]))
        return jsonify({"error": "Education not found"}), 404
    return jsonify([asdict(entry) for entry in data['education']])

def _post_education():
    req = request.get_json()

    required_fields = ["course", "school", "start_date", "end_date", "grade", "logo"]
    if not req or not isinstance(req, dict) or any(
        field not in req for field in required_fields
    ):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        education_entry = Education(**req)
    except TypeError:
        return jsonify({"error": "Invalid format"}), 400

    data['education'].append(education_entry)
    return jsonify({'id': len(data['education']) - 1})
@app.route('/resume/education', methods=['GET', 'POST', 'DELETE'])
@app.route('/resume/education/<int:index>', methods=['GET'])
def education(index=None):
    '''
    Handles education requests
    '''
    if request.method == 'GET':
        return _get_education(index)
    if request.method == 'POST':
        return _post_education()
    if request.method == 'DELETE':
        return _delete_education(request.get_json())

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
    req = request.get_json()
    required_fields = ["name", "proficiency", "logo"]
    if not req or not isinstance(req, dict) or any(
        field not in req for field in required_fields
    ):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        new_skill = Skill(**req)
    except TypeError:
        return jsonify({"error": "Invalid format"}), 400

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
def _delete_experience(body):
    if not body or 'id' not in body:
        return jsonify({"error": "ID is required for deletion"}), 400
    try:
        item_id = int(body['id'])
    except (ValueError, TypeError):
        return jsonify({"error": "ID must be an integer"}), 400
    if item_id < 0 or item_id >= len(data['experience']):
        return jsonify({"error": "ID out of range"}), 404
    data['experience'].pop(item_id)
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
