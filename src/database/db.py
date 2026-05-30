from src.database.config import supabase

import bcrypt

# method to check whether the username is uniue or not

def hash_pass(password):
    # Convert string to bytes (bcrypt requires byte input)
    password_bytes = password.encode('utf-8')

    # Generate a salt and hash the password
    # Salt is a random value added to password before hashing.
    # The salt defaults to a cost factor of 12 rounds
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    return hashed_password.decode('utf-8')
def check_pass(pwd, hashed_pass):
    return bcrypt.checkpw(pwd.encode(), hashed_pass.encode())
def check_teacher_exists(username):
    """checks unique username,
    returns false when username already exists
    """

    response = supabase.table("teachers").select("username").eq("username", username).execute()


    return len(response.data) > 0

def create_teacher(username, password, name):
    data = {"username": username, "password": hash_pass(password), "name": name}

    response = supabase.table("teachers").inesrt(data).execute()

    return response.data


def teacher_login(username, password):

    response = supabase.table("teachers").select("*").eq("username", username).execute()

    if response.data:
        teacher = response.data[0]

        if check_pass(password, teacher['password']):
            return teacher
        
def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {'name': new_name, 'face_embedding':face_embedding, 'voice_embdding': voice_embedding}

    response = supabase.table("students").insert(data).execute()

    return response.data
