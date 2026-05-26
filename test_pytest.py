'''
Tests in Pytest
'''
from app import app


def test_client():
    '''
    Makes a request and checks the message received is the same
    '''
    response = app.test_client().get('/test')
    assert response.status_code == 200
    assert response.json['message'] == "Hello, World!"


def test_experience():
    '''
    Add a new experience and then get all experiences. 
    
    Check that it returns the new experience in that list
    '''
    example_experience = {
        "title": "Software Developer",
        "company": "A Cooler Company",
        "start_date": "October 2022",
        "end_date": "Present",
        "description": "Writing JavaScript Code",
        "logo": "example-logo.png"
    }

    item_id = app.test_client().post('/resume/experience',
                                     json=example_experience).json['id']
    response = app.test_client().get('/resume/experience')
    assert response.json[item_id] == example_experience


def test_education():
    '''
    Add a new education and then get all educations. 
    
    Check that it returns the new education in that list
    '''
    example_education = {
        "course": "Engineering",
        "school": "NYU",
        "start_date": "October 2022",
        "end_date": "August 2024",
        "grade": "86%",
        "logo": "example-logo.png"
    }
    item_id = app.test_client().post('/resume/education',
                                     json=example_education).json['id']

    response = app.test_client().get('/resume/education')
    assert response.json[item_id] == example_education


def test_education_by_index():
    '''
    Get a specific education by index.

    Check that it returns the expected education in JSON format
    '''
    expected_education = {
        "course": "Computer Science",
        "school": "University of Tech",
        "start_date": "September 2019",
        "end_date": "July 2022",
        "grade": "80%",
        "logo": "example-logo.png"
    }

    response = app.test_client().get('/resume/education/0')
    assert response.status_code == 200
    assert response.json == expected_education


def test_skill():
    '''
    Add a new skill and then get all skills. 
    
    Check that it returns the new skill in that list
    '''
    example_skill = {
        "name": "JavaScript",
        "proficiency": "2-4 years",
        "logo": "example-logo.png"
    }

    item_id = app.test_client().post('/resume/skill',
                                     json=example_skill).json['id']

    response = app.test_client().get('/resume/skill')
    assert response.json[item_id] == example_skill

def test_delete_skill():
    '''
    Add new skill and then delete it using the id. 

    Check that the count of skill entries is the same as before adding and deletion. 

    And verify that the return does not contain the deleted skill entry.
    '''
    client = app.test_client()

    example_skill = {
        "name": "Testing Skill",
        "proficiency": "1-2 years",
        "logo": "example-logo.png"
    }

    before = client.get('/resume/skill')
    assert before.status_code == 200
    before_count = len(before.json)

    post_response = client.post('/resume/skill', json=example_skill)
    assert post_response.status_code == 200
    item_id = post_response.json['id']

    delete_response = client.delete('/resume/skill', json={"id": item_id})
    assert delete_response.status_code == 200
    assert delete_response.json["deleted"] == item_id

    after = client.get('/resume/skill')
    assert after.status_code == 200
    assert len(after.json) == before_count
    assert not any(
        skill for skill in after.json if skill['name'] == example_skill['name']
        and skill['proficiency'] == example_skill['proficiency']
        and skill['logo'] == example_skill['logo']
    )
def test_delete_experience():
    """
    Add an experience, delete it by returned index id, 
    and verify count goes down and does not contain the specific experience added.
    """
    client = app.test_client()

    example_experience = {
        "title": "Software Developer for deleting",
        "company": "Delete Test Co 123",
        "start_date": "October 2022",
        "end_date": "Present",
        "description": "Writing JavaScript Code",
        "logo": "example-logo.png"
    }

    before = client.get('/resume/experience')
    assert before.status_code == 200
    before_count = len(before.json)

    post_response = client.post('/resume/experience', json=example_experience)
    assert post_response.status_code == 200
    item_id = post_response.json['id']

    delete_response = client.delete('/resume/experience', json={"id": item_id})
    assert delete_response.status_code == 200
    assert delete_response.json["deleted"] == item_id

    after = client.get('/resume/experience')
    assert after.status_code == 200
    assert len(after.json) == before_count
    assert not any(
        exp for exp in after.json if exp['title'] == example_experience['title'] and
        exp['company'] == example_experience['company'] and
        exp['start_date'] == example_experience['start_date'] and
        exp['end_date'] == example_experience['end_date'] and
        exp['description'] == example_experience['description'] and
        exp['logo'] == example_experience['logo']
    )

def test_get_user_info():
    '''
    Fetch user info and check if it returns matching data
    '''
    response = app.test_client().get('/resume/user_info')
    assert response.status_code == 200
    assert "name" in response.json
    assert "phone_number" in response.json
    assert "email_address" in response.json

def test_update_user_info():
    '''
    Update the user info and verify that it changes.
    '''
    client = app.test_client()
    new_user_info = {
        "name": "Jane Doe",
        "phone_number": "+0987654321",
        "email_address": "jane@example.com"
    }

    response = client.put('/resume/user_info', json=new_user_info)
    assert response.status_code == 200
    assert response.json["data"] == new_user_info

    get_response = client.get('/resume/user_info')
    assert get_response.json == new_user_info

def test_user_info_missing_fields():
    '''
    Test updating user info with missing fields
    '''
    client = app.test_client()
    incomplete_info = {
        "name": "No Phone Number"
    }
    response = client.post('/resume/user_info', json=incomplete_info)
    assert response.status_code == 400
    assert response.json["error"] == "Missing fields"

def test_user_info_invalid_phone():
    '''
    Test updating user info with an invalid phone number
    '''
    client = app.test_client()
    invalid_phone_info = {
        "name": "Jane",
        "phone_number": "12345678", # Missing '+'
        "email_address": "jane@example.com"
    }
    response = client.put('/resume/user_info', json=invalid_phone_info)
    assert response.status_code == 400
    assert "Phone number must include international country code" in response.json["error"]

def test_spellcheck_endpoint():
    '''
    Check that spelling corrections are returned for resume entries
    '''
    client = app.test_client()
    example_experience = {
        "title": "Tester",
        "company": "Speling Co",
        "start_date": "October 2022",
        "end_date": "Present",
        "description": "Teh dog",
        "logo": "example-logo.png"
    }

    client.post('/resume/experience', json=example_experience)

    response = client.get('/resume/spellcheck')
    assert response.status_code == 200
    assert any(
        item["before"] == "Teh dog" and item["after"] == "The dog"
        for item in response.json
    )
