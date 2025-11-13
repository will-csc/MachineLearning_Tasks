# Configurações básicas do Flask e banco de dados
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///apoioja.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
