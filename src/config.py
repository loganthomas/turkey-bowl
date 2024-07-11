import os
from dataclasses import dataclass
from pathlib import Path

basedir = Path(__file__).parent.resolve()


@dataclass
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{basedir.joinpath('app.db')}"
    )


# 'sqlite:///' + os.path.join(basedir, 'app.db')
# 'sqlite:////Users/logan/Desktop/repos/turkey-bowl/app.db'
