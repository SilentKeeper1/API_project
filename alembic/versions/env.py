import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models import Base
target_metadata = Base.metadata
