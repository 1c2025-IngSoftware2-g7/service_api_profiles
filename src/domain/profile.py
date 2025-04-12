class Profile:
    def __init__(self, uuid: str, email: str, role: str, display_name: str = None, phone: str = None, location: str = None, birthday: str = None, gender: str = None, description: str = None, display_image: str = None):
        self.uuid = uuid
        self.email = email
        self.role = role
        self.display_name = display_name
        self.phone = phone
        self.location = location
        self.birthday = birthday
        self.gender = gender
        self.description = description
        self.display_image = display_image
        return
    
