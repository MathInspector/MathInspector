import pickle, os
from .savedata import get_basepath

FILEPATH = os.path.join(get_basepath(), "projectdata.pkl")

def load():
	try:
		with open(FILEPATH, "rb") as data:
			project_path = pickle.load(data)
	except Exception:
		return None

	return project_path
