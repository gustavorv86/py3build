# py3build
Create Python3 zipapp with pyc files from Python3 sources.

## Usage
Compile the sources and create the zip application file:
```bash
./py3build.py -i /path/to/myapp/main.py -o myapp.bin
```

## Run your application
Just run the file:
```bash
./myapp.bin
```

## Troubleshooting

### ModuleNotFoundError
Create the `__init__.py` file into the module directories.

