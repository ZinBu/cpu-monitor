import os
import shelve

from src import tools, config
from src.protocols import Database, DBConfigData

_COLOR_FIELD = 'color'


class ConfigDB(Database):

    def _get_file_path(self) -> str:
        return tools.executable_file_path(config.DB_NAME + config.DB_EXT)

    def save_config(self, conf: DBConfigData) -> None:
        db_path = self._get_file_path()
        with shelve.open(db_path) as db:
            db[_COLOR_FIELD] = conf.color

    def load_config(self) -> DBConfigData:
        db_path = self._get_file_path()
        # Create a folder if doesn't exist
        if not os.path.exists(db_path):
            os.mkdir(os.path.join(os.getcwd(), config.DB_DIR))
        with shelve.open(db_path) as db:
            color = db.get(_COLOR_FIELD)
            return DBConfigData(color=color)
