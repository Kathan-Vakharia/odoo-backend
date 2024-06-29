from flask import Flask, request, jsonify
from src.config.database import create_db_conn
from datetime import datetime
import mysql
import uuid
from flask_cors import CORS
from dotenv import load_dotenv


app = Flask(__name__)
CORS(app)

load_dotenv()

def get_department_id(user_id):
    conn = create_db_conn()
    cursor = conn.cursor()
    query = "SELECT dept_id FROM User WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return None


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

    try:
        cursor.execute(query, values)
        conn.commit()
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
    print("all went well")
    return jsonify({'message': 'Grievance submitted successfully', 'grievance_id': grievance_id}), 201


if __name__ == '__main__':
    # app.run(debug=True, port=8000)
    app.run(host="0.0.0.0", port=8000, debug=True)
