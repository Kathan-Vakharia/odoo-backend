from config.database import create_db_conn
import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.utils import cloudinary_url


def get_user_by_id(user_id: str):
    """
        Get user by user_id
        param user_id: user_id
        return: user
    """
    conn = create_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def fetch_ser_department(user_id: str):
    """
        Get user by user_id
        param user_id: user_id
        return: user
    """
    conn = create_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def store_user(user_id: str, role: str, email: str, dept_id: str):
    """
        Create user
        param user_id: user_id
        param name: name
        param email: email
        param password: password

        Returns:
        - str: user_id
    """
    conn = create_db_conn()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (id, role, email, dept_id) VALUES (%s, %s, %s, %s)",
                   (user_id, role, email, dept_id))
    conn.commit()
    cursor.close()
    conn.close()

    return user_id





def upload_file_to_cloudinary(file, folder=None, tags=None, transformation=None, **kwargs):
    """
    Uploads a file to Cloudinary.

    Parameters:
    - file_path(str): Path to the file to be uploaded.
    - folder(str, optional): Folder path in Cloudinary to upload the file to.
    - tags(list, optional): List of tags for categorization.
    - transformation(dict or list, optional): Transformation parameters for image processing.

    Returns:
    - str: Secure URL of the uploaded file.
    """

    try:
        # Configure Cloudinary (replace with your credentials)
        cloudinary.config(
            cloud_name=kwargs.get('cloud_name'),
            api_key=kwargs.get('api_key'),
            api_secret=kwargs.get('api_secret')
        )

        # Upload file to Cloudinary
        upload_params = {
            "folder": folder,
            "tags": tags,
            "transformation": transformation
        }

        print(upload_params)

        print(file)
        upload_result = cloudinary_upload(file, **upload_params,resource_type="raw")

        # Get the secure URL of the uploaded file
        secure_url = upload_result['secure_url']

        return secure_url

    except cloudinary.exceptions.Error as e:
        print(f"Error uploading file to Cloudinary: {e}")
        return None
