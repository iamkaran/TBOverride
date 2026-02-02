from pathlib import Path
from tb_override import FileIO

css_file = Path("tests/example_css.css")
conf_file = Path("tests/example_tb_proxy")

fileio = FileIO(conf_path=conf_file, css_path=css_file)


