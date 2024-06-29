from config.database import create_db_conn


def get_user_role(user_id):
    conn = create_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM user WHERE id = %s", (user_id,))
    role = cursor.fetchone()
    cursor.close()
    conn.close()
    return role[0] if role else None


def get_department_id(user_id):
    conn = create_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT dept_id FROM user WHERE id = %s", (user_id,))
    department_id = cursor.fetchone()
    cursor.close()
    conn.close()
    return department_id[0] if department_id else None


def fetch_messages(grievance_id):
    try:

        conn = create_db_conn()
        # Use dictionary cursor for JSON output
        cursor = conn.cursor(dictionary=True)
        # Ensure you have a 'timestamp' column
        cursor.execute(
            f"SELECT * FROM messages Where grievance_id = {grievance_id} ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []


def assign_grievance(grievance_id, hr_id):

    try:

        conn = create_db_conn()
        cursor = conn.cursor()
        query = "UPDATE Grievance SET assigned_to = %s, assigned_type = 'HR'  and assigned_type = " % "WHERE id = %s"
        cursor.execute(query, (hr_id, grievance_id))
        conn.commit()
        cursor.close()

    except Exception as e:
        
        return e