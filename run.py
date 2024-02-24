import json
import os
import uuid
from collections import Counter
from datetime import datetime
import sys

from flask import Flask, render_template, request, make_response, redirect, url_for
import polars as pl
from pydantic import BaseModel


class Flashcard(BaseModel):
    front: str
    back: str
    section_heading: str
    file_name: str


# set the project root directory as the templates folder, you can set others.
app = Flask(__name__)

# All experiments are saved in the source folder 'resources/experiments'.
experiments_path = os.path.join("resources", "experiments")

# The list experiments contains all the files in the experiment directory
(_, _, experiments) = next(os.walk(experiments_path))

# Counters of how many experiments have started
# For this example, the possible options are:

# FlashCard Review -- Pilot1 control // Shirin Chapter 1
# FlashCard Review -- Pilot1 test // LLM Chapter 1

# FlashCard Review -- Experiment1 control // Shirin Chapter 2
# FlashCard Review -- Experiment1 test // LLM Chapter 2
# FlashCard Review -- Experiment2 control // Shirin Chapter 3
# FlashCard Review -- Experiment2 test // LLM Chapter 3

experiments_started = Counter()

PILOT = True

# Pilot Experiment
experiments_started["FC-P1-control"] = 0
experiments_started["FC-P1-test"] = 0

# Main Experiment
experiments_started["FC-R1-control"] = 0
experiments_started["FC-R1-test"] = 0
experiments_started["FC-R2-control"] = 0
experiments_started["FC-R2-test"] = 0

# Counters of how many experiments have concluded
experiments_concluded = Counter()

# Pilot Experiment
experiments_concluded["FC-P1-control"] = 0
experiments_concluded["FC-P1-test"] = 0

# Main Experiment
experiments_concluded["FC-R1-control"] = 0
experiments_concluded["FC-R1-test"] = 0
experiments_concluded["FC-R2-control"] = 0
experiments_concluded["FC-R2-test"] = 0

# Creation of log file based on id name
html_tags = ["<li", "<ul", "<a"]


def choose_experiment():
    """
    Assign an experiment to a new user. We choose the type of experiment that
    has the least amount of concluded experiments.
    If we have more than one such case, we choose the one that has the least
    amount of started experiments.
    """
    min_val = experiments_concluded.most_common()[-1][1]

    mins = []
    for k in experiments_concluded:
        if experiments_concluded[k] == min_val:
            mins.append(k)

    if len(mins) > 1:
        # more than 1 type has the same amount of concluded
        # experiments. Hence, we choose the one that has the least amount of
        # started ones
        min_val = sys.maxsize
        to_assing = ""
        for k in mins:
            if experiments_started[k] < min_val:
                min_val = experiments_started[k]
                to_assing = k
    else:
        to_assing = mins[0]

    print("Assigned to " + to_assing)

    # ADD Code for PILOT
    if PILOT:
        if to_assing.startswith("FC-P1"):
            # assign to Pilot/Chapter 1

            if to_assing.endswith("control"):
                # assigned to control group
                fcr = "control_flashcards_chapter_1.parquet"
                test = False
            else:
                # assigned to test group
                fcr = "test_flashcards_chapter_1.parquet"
                test = True

    else:
        # Assign Chapter 2 or 3
        if to_assing.startswith("FC-R2"):
            # assign to experiment 1
            if to_assing.split("-")[0].endswith("control"):
                # assigned to control group
                test = False
                fcr = "control_flashcards_chapter_2.parquet"
            else:
                # assigned to test group
                test = True
                fcr = "test_flashcards_chapter_2.parquet"
        else:
            # assign to experiment 2
            if to_assing.split("-")[0].endswith("control"):
                # assigned to control group
                test = False
                fcr = "control_flashcards_chapter_3_.parquet"
            else:
                # assigned to test group
                test = True
                fcr = "test_flashcards_chapter_3.parquet"

    experiments_started[to_assing] += 1

    return fcr, test


@app.route("/pdfs/<filename>")
def serve_pdf(filename):
    """
    Serve the PDFs in the folder "resources/pdfs".
    This is used to serve the iframe in the "experiment.html" page.


    :param filename: the name of the file to serve
    """
    print(filename)
    # TODO move chapter_1 to a variable depending on the experiment
    return app.send_static_file("pdfs/chapter_1/" + filename)


@app.route("/")
def index():
    """
    Start of the application. It return the file "templates/index.html" and
    create the unique identifier "userid", if not already found.
    """

    resp = make_response(
        render_template(
            "index.html",
            title="Intro",
        )
    )
    user_id = request.cookies.get("experiment-userid", None)

    if user_id is None:
        user_id = uuid.uuid4()
        resp.set_cookie("experiment-userid", str(user_id))
        print(f"Userid was None, now is {user_id}")
    return resp


@app.route("/start", methods=["GET", "POST"])
def start():
    """
    Loading of Personal Information Survey. These questions can be found and
    changed in "templates/initial_questions.html"
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    if request.method == "POST":
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

    # to avoid people re-doing the experiment, we set a cookie.
    first_time = request.cookies.get("experiment-init-questions", "first-time")

    if first_time == "first-time":
        log_data(str(user_id), "start", "initial_questions")
        resp = make_response(
            render_template("initial_questions.html", title="Initial Questions")
        )
        return resp
    else:
        return redirect(url_for("already_done"))


@app.route("/results", methods=["POST"])
def results():
    """This function is called when the user submits the experiment results."""
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    print("Results", request.form.to_dict())
    if request.method == "POST":
        data: dict = request.form.to_dict()
        print("Data:", data)
        log_received_data(user_id, data)

    log_data(str(user_id), "end", "initial_questions")

    return redirect(url_for("run_experiment"))


@app.route("/experiment/init", methods=["GET", "POST"])
def init_experiment():
    """
    Initializes the experiment. This function calls "choose_experiment()" to decide
    """

    user_id = request.cookies.get("experiment-userid", "userNotFound")
    fcr_file, is_test = choose_experiment()
    print(fcr_file, is_test)
    log_data(str(user_id), "setexperimentFCRtype", fcr_file)
    log_data(str(user_id), "setexperimentFCRistest", str(is_test))

    if request.method == "POST":
        data: dict = request.form.to_dict()
        print(data)
        log_received_data(user_id, data)

    resp = make_response(
        render_template(
            "experiment.html",
            title="Code Review Experiment",
        )
    )
    resp = make_response(redirect(url_for("run_experiment")))
    resp.set_cookie("experiment-init-questions", "init-questions-done")
    resp.set_cookie("experiment-experimentCRtype", fcr_file)
    resp.set_cookie("experiment-experimentCRistest", str(is_test))

    return resp


@app.route("/experiment", methods=["GET", "POST"])
def run_experiment():
    """
    Starts the experiment. This function calls "choose_experiment()" to decide
    which experiment to assign to the user. Afterwords, it reads the apposite
    file from "resources/experiments" and populate the page.
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    fcr_file = request.cookies.get("experiment-experimentCRtype", "not_found")
    if request.method == "POST":
        data: dict = request.form.to_dict()
        print(data)
        log_received_data(user_id, data)

    log_data(str(user_id), "start", "fcr-experiment")

    exp_is_done = request.cookies.get("experiment-is_done", "not_done")
    if exp_is_done != "DONE":
        # Load from parquet file

        flashcards_df = pl.read_parquet(f"resources/experiments/{fcr_file}")

        flashcards = []
        for i, flashcard in enumerate(flashcards_df.rows(named=True)):
            if i >= 2:
                break
            flashcards.append(
                Flashcard(
                    front=flashcard["front"],
                    back=flashcard["back"],
                    section_heading=flashcard["section_heading"][:-4]
                    if flashcard["section_heading"].endswith(".txt")
                    else flashcard["section_heading"],
                    file_name=flashcard["file_name"],
                )
            )

        resp = make_response(
            render_template(
                "experiment.html",
                title="Code Review Experiment",
                flashcards=flashcards,
            )
        )
        return resp
    else:
        return redirect(url_for("already_done"))


@app.route("/experiment_concluded", methods=["GET", "POST"])
def experiment_concluded():
    """
    After the experiment, you may ask the participant to answer some questions.
    This function reads the questions from "resources/post_questions.txt" and
    populate the page "templates/experiment_concluded.html"
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    exp_is_done = request.cookies.get("experiment-is_done", "not_done")
    if request.method == "POST":
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

    log_data(str(user_id), "end", "cr_experiment")
    if exp_is_done != "DONE":
        post_questions = read_files("post_questions.txt")
        resp = make_response(
            render_template(
                "experiment_concluded.html",
                post_questions=post_questions,
                title="Post Questions",
            )
        )
        return resp
    else:
        return redirect(url_for("already_done"))


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    """
    As for the final page, we ask the participants for feedback.
    Return the page "templates/feedback.html"
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    if request.method == "POST":
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

    resp = make_response(render_template("feedback.html", title="Feedback"))
    return resp


@app.route("/conclusion", methods=["GET", "POST"])
def conclusion():
    """
    Finally, thank the participant.
    Return "templates/conclusion.html"
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    if request.method == "POST":
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

    log_data(str(user_id), "end", "experiment_concluded")

    exp_type = request.cookies.get("experiment-experimentCRtype")
    exp_is_test = request.cookies.get("experiment-experimentCRistest")

    # update the correspondent counter
    if exp_type == "files_experiment1" and exp_is_test == "True":
        experiments_concluded["FC-R1-control"] += 1
    elif exp_type == "files_experiment1" and exp_is_test == "False":
        experiments_concluded["FC-R1-test"] += 1
    elif exp_type == "files_experiment2" and exp_is_test == "True":
        experiments_concluded["FC-R2-control"] += 1
    elif exp_type == "files_experiment2" and exp_is_test == "False":
        experiments_concluded["FC-R2-test"] += 1

    conclusion_text = read_files("conclusion.txt")
    return render_template(
        "conclusion.html", title="conclusion", conclusion=conclusion_text
    )


def build_experiments(experiment_snippets):
    codes = []
    for num_experiment in experiment_snippets:
        experiment_snippet = experiment_snippets[num_experiment]
        codes.append(
            {
                "id": num_experiment,
                "filename": experiment_snippet["filename"],
                "linecount": max(
                    experiment_snippet["num_lines_L"], experiment_snippet["num_lines_R"]
                ),
                "contextLineCount": 1,
                "left_line_number": 1,
                "left_content": experiment_snippet["L"],
                "right_line_number": 1,
                "right_content": experiment_snippet["R"],
                "prefix_line_count": 1,
                "prefix_escaped": 1,
                "suffix_escaped": 1,
            }
        )
    return codes


@app.route("/already_done", methods=["GET", "POST"])
def already_done():
    """
    If a participant tries to complete the experiment twice, we send him
    directly to the conclusion.
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    log_data(str(user_id), "already_done", "already_done")
    conclusion_text = (
        "Sorry but it seems you already tried to answer the "
        "initial questions. <br>This means that (1) you "
        "failed the first time, or (2) you already did the "
        "experiment. In both cases, you can't take the "
        "experiment a second time, sorry!"
    )
    return render_template(
        "conclusion.html", title="Already done", conclusion=conclusion_text
    )


def log_received_data(user_id, data):
    """
    We log all the data to a file (filename=userid)
    """
    for key in data.keys():
        if key == "hidden_log":
            d = json.loads(data[key])
            for log in d["data"]:
                splitted = log.strip().split(";")
                dt = splitted[0]
                action = splitted[1]
                info = ";".join(splitted[2:])
                log_data(user_id, action, info, dt)
        else:
            log_data(user_id, key, data[key])


def read_files(filename):
    with open(os.path.join("resources", filename)) as f:
        return f.read()


def log_data(user_id: str, key: str, data: str, dt: datetime = None):
    with open(f"{user_id}.log", "a") as f:
        log_dt = dt if dt is not None else datetime.timestamp(datetime.now())
        f.write(f"{log_dt};" f"{key};" f"{data}\n")
