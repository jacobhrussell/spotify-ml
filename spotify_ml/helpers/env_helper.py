import os

class EnvHelper():
    def __init__(self):
        pass

    def get_env(self):
        env = os.getenv("Envrionment")
        if env is not None:
            return env
        else:
            return 'dev'