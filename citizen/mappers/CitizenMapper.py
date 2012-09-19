from citizen.models import Citizen

class CitizenMapper:
    @staticmethod
    def getDisplayName(citizen):
        return citizen.firstname.capitalize() + " " + citizen.lastname.capitalize()
    @staticmethod
    def getCitizenById(id):
        citizen = Citizen.objects.filter(id = id)
        if len(citizen) == 0:
            return None
        else:
            return citizen[0]
    @staticmethod
    def getCitizenByCitizenId(id):
        citizen = Citizen.objects.filter(citizenid = id)
        if len(citizen) == 0:
            return None
        else:
            return citizen[0]
    @staticmethod
    def getAllCitizens():
        return Citizen.objects.all()
    
