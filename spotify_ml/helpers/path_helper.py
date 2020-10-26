import os
import re

class PathHelper:

    def __init__(self):
        pass

    def remove_base_path(self, path):
        base_path = os.environ.get('BASEPATH')
        if base_path:
            for piece in base_path.split('/'):
                if not piece:
                    continue
                path = re.sub(f'^/{piece}', '', path)
        return path