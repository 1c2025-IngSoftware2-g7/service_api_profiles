class Profile:
    def __init__(self, uuid: str, name: str, surname: str, email: str, password: str, 
                 role: str, location: str = None, profile_picture: str = None):
        self.uuid = uuid 
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password
        self.role = role  # 'student', 'teacher' o 'admin'
        self.location = location
        self.profile_picture = profile_picture
        return
    
