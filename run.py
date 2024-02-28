import json
import os
import random
import uuid

from flask import Flask, render_template, request, make_response, redirect, url_for
from schema import CreateFlashcard, ParticipantForm, PreExperimentFormData, User

from datetime import datetime


from crud.db import (
    check_database_connection,
    init_db,
)

from crud.flashcard import create_flashcard, get_flashcards
from crud.user import (
    create_initial_questions,
    create_participant,
    create_user,
    get_user,
)
from crud.section import (
    get_section,
    get_section_by_name,
)


# set the project root directory as the templates folder, you can set others.
app = Flask(__name__)

# All experiments are saved in the source folder 'resources/experiments'.
experiments_path = os.path.join("resources", "experiments")

# The list experiments contains all the files in the experiment directory
(_, _, experiments) = next(os.walk(experiments_path))


def choose_flashcard_review_experiment(user_id: str):
    """
    Assigns a user to a flashcard creation section and a review section.
    This is a simplified version that randomly assigns sections.
    """

    # TODO - Implement a more sophisticated assignment algorithm

    # Assuming section IDs are strings from "1" to "5"
    section_file_names = [
        "section_2_1_4.pdf",
        "section_2_2.pdf",
        "section_2_4_6.pdf",
        "section_2_4_7.pdf",
        "section_2_4_8.pdf",
        "section_2_4_9.pdf",
    ]
    flashcard_section_name = random.choice(section_file_names)

    # Ensure the review section is different from the flashcard section
    review_sections = [s for s in section_file_names if s != flashcard_section_name]
    review_section_name = random.choice(review_sections)

    flashcard_section = get_section_by_name(flashcard_section_name)
    review_section = get_section_by_name(review_section_name)

    # Create the section assignment and return the object
    return flashcard_section, review_section


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

        section_assignment = choose_flashcard_review_experiment(user_id=str(user_id))

        create_user(
            User(
                id=str(user_id),
                creator="student",
                flashcard_section_id=section_assignment[0].id,
                review_section_id=section_assignment[1].id,
            )
        )

    return resp


@app.get("/health")
def health():
    if check_database_connection():
        return "OK"
    else:
        return "Database connection failed", 500


@app.get("/init_db")
def db():
    if init_db():
        return "OK"
    else:
        return "Database connection failed", 500


@app.route("/pdfs/<filename>")
def serve_pdf(filename):
    """
    Serve the PDFs in the folder "resources/pdfs".
    This is used to serve the iframe in the "experiment.html" page.


    :param filename: the name of the file to serve
    """
    print(filename)
    # TODO move chapter_1 to a variable depending on the experiment
    return app.send_static_file("pdfs/chapter_2/" + filename)


# Loading of Personal Information Survey.
@app.route("/dem_questions", methods=["GET", "POST"])
def load_questions():
    """
    Loading of Demographic Questions. These questions can be found and
    changed in "templates/dem_questions.html"
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    if request.method == "POST":
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)
    first_time = request.cookies.get(
        "experiment-dem-questions", "experiment-dem-not_done"
    )

    if first_time == "experiment-dem-not_done":
        log_data(str(user_id), "start - dem", "dem_questions")
        resp = make_response(
            render_template("dem_questions.html", title="Demographics Questions")
        )
        resp.set_cookie("experiment-final", "experiment-final-done")
        resp.set_cookie("experiment-survey", "experiment-survey-done")
        return resp
    else:
        return redirect(url_for("already_done"))


@app.route("/data_policy", methods=["GET", "POST"])
def data_policy():
    resp = make_response(render_template("data_policy.html", title="Data Policy"))
    resp.set_cookie("data_policy", "open")
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
        print(data)
        create_participant(ParticipantForm(user_id=user_id, **data))
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

    if request.method == "POST":
        data: dict = request.form.to_dict()
        print(data)
        log_received_data(user_id, data)
        create_initial_questions(PreExperimentFormData(user_id=user_id, **data))

    return redirect(url_for("flashcard"))


@app.route("/flashcard", methods=["GET", "POST"])
def flashcard():
    """
    This function is called when the user creates a Flash Card.
    """

    user_id = request.cookies.get("experiment-userid", "userNotFound")
    user = get_user(user_id)
    section = get_section(user.flashcard_section_id)

    if request.method == "POST":
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

        create_flashcard(
            CreateFlashcard(
                user_id=user_id,
                section_id=section.id,
                file_name=section.file_name,
                section_heading=section.section_heading,
                **data,
            )
        )

    log_data(str(user_id), "start", "fcr-creation")

    user = get_user(user_id)

    resp = make_response(
        render_template(
            "create_flashcard.html",
            title="Create Flash Card",
            section=section,
        )
    )
    return resp


@app.route("/experiment", methods=["GET", "POST"])
def run_experiment():
    """
    Starts the experiment. This function calls "choose_experiment()" to decide
    which experiment to assign to the user. Afterwords, it reads the apposite
    file from "resources/experiments" and populate the page.
    """
    user_id = request.cookies.get("experiment-userid", "userNotFound")
    if request.method == "POST":
        data: dict = request.form.to_dict()
        print(data)
        log_received_data(user_id, data)

    log_data(str(user_id), "start", "fcr-experiment")

    user_id = request.cookies.get("experiment-userid", "userNotFound")
    exp_is_done = request.cookies.get("experiment-is_done", "not_done")
    if exp_is_done != "DONE":
        # Load from parquet file

        user = get_user(user_id)
        flashcards = get_flashcards(user.review_section_id)
        print(flashcards)

        resp = make_response(
            render_template(
                "experiment.html",
                title="Code Review Experiment",
                section=get_section(user.review_section_id),
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

    conclusion_text = read_files("conclusion.txt")
    return render_template(
        "conclusion.html", title="conclusion", conclusion=conclusion_text
    )


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
