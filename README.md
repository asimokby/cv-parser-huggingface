# cv-parser-huggingface 🤗

A CV parser built with Hugging Face. The tool parses the following sections: Job History, Education History, Skills, Name, Email, Phone Numbers, and address. Here is a (NOT up to date as this repo) [demo](https://huggingface.co/spaces/asimokby/cv-parser-huggingface) 🚀 on HuggingFace Spaces.

![image](https://user-images.githubusercontent.com/34512671/153226336-e8b0388b-57de-46d0-9d21-cbe29a528be5.png)

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



