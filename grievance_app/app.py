from config.database import create_db_conn
from flask import Flask, request, jsonify
from datetime import datetime
import mysql
import uuid
from flask_cors import CORS
from dotenv import load_dotenv
from utils.user import upload_file_to_cloudinary, store_user
from middleware.jwt import verify_jwt
import os
from utils.grievance import get_department_id, fetch_messages, get_user_role, assign_grievance


app = Flask(__name__)
CORS(app)

load_dotenv()


@app.route('/update_grievance_status', methods=['PUT'])
def update_grievance_status():
    data = request.json
    grievance_id = data.get('grievance_id')
    new_status = data.get('new_status')

    # Fetch user ID from request headers or session
    # Replace with actual header name or session logic
    user_id = request.headers.get('X-User-ID')

    if not user_id:
        return jsonify({'error': 'User ID not provided in headers'}), 400

    # Fetch user role from database
    current_user_role = get_user_role(user_id)

    if current_user_role != 'admin':
        return jsonify({'error': 'Unauthorized access'}), 403

    if not (grievance_id and new_status):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = create_db_conn()
    cursor = conn.cursor()

    try:
        # Update the status of the grievance
        update_query = """
        UPDATE Grievance
        SET status = %s, updated_at = %s
        WHERE id = %s
        """
        cursor.execute(update_query, (new_status,
                       datetime.now(), grievance_id))

        # Record the status change in the log table
        log_query = """
        INSERT INTO GrievanceStatusLog (grievance_id, status, changed_by, changed_at)
        VALUES (%s, %s, %s, %s)
        """
        updated_by = user_id  # Assuming updated_by is the user ID fetched from headers or session
        cursor.execute(log_query, (grievance_id, new_status,
                       updated_by, datetime.now()))

        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Grievance status updated successfully'}), 200


@app.route('/get_grievance_details/<user_id>', methods=['GET'])
def get_grievance_details_by_user_id(user_id):
    print(user_id)
    conn = create_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch the grievance details
        grievance_query = """
        SELECT * FROM Grievance WHERE user_id = %s
        """
        cursor.execute(grievance_query, (user_id,))
        grievances = cursor.fetchall()

        if not grievances:
            return jsonify({'error': 'No grievances found for the specified user ID'}), 404

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'grievances': grievances}), 200


@app.route('/get_all_grievances', methods=['GET'])
def get_all_grievances():
    status = request.args.get('status')
    department_id = request.args.get('department_id')

    query = "SELECT * FROM Grievance"
    filters = []
    params = []

    if status:
        filters.append("status = %s")
        params.append(status)
    if department_id:
        filters.append("dep_id = %s")
        params.append(department_id)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    conn = create_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params)
        grievances = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    # Getting attachments for each grievance
    for grievance in grievances:
        grievance_id = grievance.get('id')
        conn = create_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT url FROM Attachment WHERE grievance_id = %s"
        cursor.execute(query, (grievance_id,))
        attachments = cursor.fetchall()
        grievance['attachments'] = [attachment.get(
            'url') for attachment in attachments]

    return jsonify({'grievances': grievances}), 200


@app.route('/grievance', methods=['POST', 'GET'])
def submit_grievance():
    if (request.method == 'GET'):
        return jsonify({'message': 'GET request received'}), 200
    data = request.json
    print(data)
    # Extract data from request
    user_id = data.get('user_id')
    grievance_type = data.get('grievance_type')
    title = data.get('title')
    description = data.get('description')
    # assigned_to = data.get('assigned_to')
    # assigned_type = data.get('assigned_type')
    dep_id = get_department_id(user_id)
    severity = data.get('severity', 'low')
    status = data.get('status', 'submitted')  # Default status to 'submitted'
    created_at = datetime.now()
    updated_at = datetime.now()
    # print(user_id, grievance_type, title, description, dep_id, severity, status, created_at, updated_at)
    # Validate required fields
    if not (user_id and grievance_type and title and description and dep_id and severity):
        return jsonify({'error': 'Missing required fields'}), 400

    # Connect to the database
    conn = create_db_conn()
    cursor = conn.cursor()

    # Generate a unique ID for the grievance
    grievance_id = str(uuid.uuid4())

    # Insert grievance into the database
    query = """
    INSERT INTO Grievance (id, user_id, grievance_type, title, description,
      dep_id, severity, status, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (grievance_id, user_id, grievance_type, title, description,
              dep_id, severity, status, created_at, updated_at)

    print(data.get('attachments', []))

    # Add attachments url to the gravient
    for url in data.get('attachments', []):

        attach_id = str(uuid.uuid4())
        query = """
        INSERT INTO Attachment (id, grievance_id, url)
        VALUES (%s, %s, %s)
        """

        print(query)
        values = (attach_id, grievance_id, url)
        cursor.execute(query, values)
        conn.commit()

    try:
        cursor.execute(query, values)
        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Grievance submitted successfully', 'grievance_id': grievance_id}), 201


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        cloud_name = os.getenv('CLOUD_NAME')
        api_key = os.getenv('API_KEY')
        api_secret = os.getenv('API_SECRET')

        f = request.files['file']
        if not f:
            return jsonify({'error': 'No file provided'}), 400

        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID not provided'}), 400

        # Upload file to Cloudinary
        cloudinary_credentials = {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret
        }

        file_url = upload_file_to_cloudinary(
            f, user_id, **cloudinary_credentials)
        return jsonify({'message': 'File uploaded successfully', "url": file_url}), 201


@app.route('/create_user', methods=['POST'])
@verify_jwt
def create_user(decoded_token):

    # Extract data from request
    email = decoded_token.get('email')
    user_id = decoded_token.get('user_id')
    role = decoded_token.get('role')
    dept_id = decoded_token.get('dept_id')

    # Validate required fields
    if not (email and user_id and role):
        return jsonify({'error': 'Missing required fields'}), 400

    # Insert user into the database
    user_id = store_user(user_id, email, role, dept_id)
    return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201


# @app.route('/assign/<grievance_id>', methods=['POST'])
# def grevieance_assigne():

@app.route('/all_hr/<name>', methods=['GET'])
def all_hr():

    name = request.params.get('name')
    conn = create_db_conn()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM User WHERE role = 'hr' and name = %s"
    cursor.execute(query, (name,))
    hr = cursor.fetchall()

    return jsonify({'hr': hr}), 200


@app.route('/assigne/<hr_id>/<grievance_id>', methods=['POST'])
def assign_grievance():

    hr_id = request.params.get('hr_id')
    grievance_id = request.params.get('grievance_id')

    conn = create_db_conn()
    cursor = conn.cursor()

    try:

        assign_grievance(hr_id, grievance_id)

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'Grievance assigned successfully'}), 200


# Route to fetch and return messages as JSON
@app.route('/get_messages/<grievance_id>', methods=['GET'])
def get_messages():
    try:
        grievance_id = request.get('grievance_id')
        messages = fetch_messages(grievance_id)
        return jsonify(messages), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # app.run(debug=True, port=8000)
    app.run(host="0.0.0.0", port=8000)
