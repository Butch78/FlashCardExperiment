# CRExperiment
This tool can be used to do online (controlled) experiments on code reviews. CRExperiment has been previously used in these studies:

1. Spadini, Davide, et al. "Test-driven code review: an empirical study." *2019 IEEE/ACM 41st International Conference on Software Engineering (ICSE). IEEE, 2019.*
2. Spadini, Davide, et al. "Primers or Reminders? The Effects of Existing Review Comments on Code Review" *42nd International Conference on Software Engineering (ICSE '20), May 23--29, 2020, Seoul, Republic of Korea*


## INSTALL
If you would like to run the tool, you can do it with very simple steps.
First, clone the repo:

```
> git clone https://github.com/ishepard/CRExperiment.git
> cd FlashCardExperiment
```

### (OPTIONAL)

If you are using VScode dev containers this application comes pre-installed will Python & [uv](https://github.com/astral-sh/uv)

It is suggested to make use of these commands:

```
> uv venv
> source .venv/bin/activate
```

### INSTALL THE REQUIREMENTS

Install the requirements:

```
> uv pip install -r requirements.txt
```

## RUN
FlashCardExperiment uses Flask to create a webserver. Fore more information about Flask, [check the documentation](http://flask.palletsprojects.com/en/1.1.x/).

In your terminal, type:

```
> export FLASK_APP=run.py
> flask run
```
On your browser, you can now visit the page [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to see the experiment landing page. 


2. **templates**: In the **templates/** directory you can find _all_ the webpages of the experiment, such as _index.html_, _initial\_questions.html_, _conclusion.html_, etc. Hence, if you want to create a new webpage, you need to create an html file in this directory. After creating the file, you need to create an entry point in the `run.py` following Flask sintax, that is `@app.route("/{WEBPAGE_NAME}", methods=['GET', 'POST'])`. In order to populate the webpage with text (or questions), you have 2 possibilities:
	
	1. **hardcoding**: in this case, you create a "real" html page, including html tags, links, etc., and in the entry point of `run.py` you just need to return the html page. An example of this case is _index.html_ and _initial\_questions.html_
	2. **you create a resource file**: we created a parser (`parser.py`) that can parse a txt file and automatically populate a webpage. In this case, you create an empty html page, and put a resource file in the **resources/** directory with the text (or questions) you want to be presented to the user. The parser will do the rest. Note: currently the parser can build relatively simple webpages. An example of these pages are _experiment\_concluded.html_ and _conclusion.html_.

3. `run.py`: this is the runner, the main file. For each webpage, there is an entry point that will populate the webpage. See [Flask documentation](http://flask.palletsprojects.com/en/1.1.x/) for more details.