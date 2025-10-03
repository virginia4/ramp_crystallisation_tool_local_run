# OptiScreen Tool

Tool to optimise screening crystallisation conditions

## Use OptiScreen Tool 

Try it line [here](https://ramp-mdl.appspot.com)  ---> CURRENTLY UNAVAILABLE

## Run OptiScreen Tool locally (for development)

Use requirements.txt to install all dependencies: 
```
pip install -r requirements.txt 
pip freeze > requirements.txt 
```

Then you can run the tool using run_RAMPCT.py:
```
python run_RAMPCT.py 
open http://0.0.0.0:8050/
```

## Deploy with gcloud 
To deploy the code in gcloud:
1. Open a virtual environment

2. Install all the requirement packages (requirements.txt)

3. Install [Cloud SDK](https://cloud.google.com/sdk/docs/quickstart-macos) 

4. Connect to gcloud account 

5. Run the following
```
gcloud app deploy 
gcloud browse 
```

## Acknowledgements 
Initial version of this tool was based on [SyCoFinder](https://github.com/ltalirz/sycofinder)

## Contact
For information please contact apostolop.virginia@gmail.com
