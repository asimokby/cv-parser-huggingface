# cv-parser-huggingface 🤗

A CV parser built with Hugging Face. The tool parses only the Job History, name, and email for now. Here is a [demo](https://huggingface.co/spaces/asimokby/cv-parser-huggingface) 🚀 on HuggingFace Spaces.


## Installation


1) Clone the Project

```
git clone https://github.com/asimokby/cv-parser-huggingface.git
```
2) Create the environment

* You may use **environment.yml** or **requirements.txt** to setup the environment. For environment.yml, run the following commands. Replace <env_name> with the name you choose.

```
  conda env create --name <env_name> --file=environment.yml 
```
3) Activate the environment
```
  conda activate <env_name>
```

## Usage

You can find the following use case in this [example](https://github.com/asimokby/cv-parser-huggingface/blob/main/example.py)

```python 
from parcv import parcv

parser = parcv.Parser(pickle=True, load_pickled=True)
json_output = parser.parse('your_cv.pdf')
print(json_output)
```
To save the output in a json file

```python 
file_name = "output.json"
parser.save_as_json(file_name)
```

You can get a list of the lines in the CV: 

```python
lines = parser.get_resume_lines()
print(lines)
```

Or the segments/sections of the CV:

```python
segments = parser.get_resume_segments()
print(segments)
```



