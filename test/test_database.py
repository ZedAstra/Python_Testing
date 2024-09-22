from models import Club

# Vérifie qu'il est possible de se connecter à la base de données
def test_connection():
    assert Club.table_exists() == True