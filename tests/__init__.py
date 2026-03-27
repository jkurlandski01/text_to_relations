from pathlib import Path
import sys

# All project imports must occur after we have updated the path.
path = Path(__file__).absolute()
tests_path = path.parent
sys.path.append(str(tests_path))
src_path = tests_path.parent / 'src'
# src_path = tests_path.parent / 'src' / 'text_to_relations'
sys.path.append(str(src_path))
