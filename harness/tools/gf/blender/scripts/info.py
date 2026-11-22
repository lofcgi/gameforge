import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _common as common

(source,) = common.script_args()
common.load(source)
common.write_result(common.stats())
