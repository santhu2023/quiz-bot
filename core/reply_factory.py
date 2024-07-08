
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    # Check if current_question_id is valid
    if current_question_id is None or current_question_id < 0 or current_question_id >= len(PYTHON_QUESTION_LIST):
        return False, "Invalid question ID."

    # Assuming each question has an "id" and a "validation_function" to check the answer format
    question = PYTHON_QUESTION_LIST[current_question_id]
    validation_function = question.get("validation_function")

    # Validate the answer
    if validation_function and not validation_function(answer):
        return False, f"Invalid answer format for question ID {current_question_id}."

    # Store the answer in the session
    if "answers" not in session:
        session["answers"] = {}
    session["answers"][current_question_id] = answer

    return True, ""



def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    # If current_question_id is None or less than 0, start from the beginning
    if current_question_id is None or current_question_id < 0:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    # Check if the next_question_id is within the range of the PYTHON_QUESTION_LIST
    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]["question"]
        return next_question, next_question_id
    else:
        # No more questions
        return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    answers = session.get("answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0

    # Validate each answer against the correct answer in the question list
    for question_id, answer in answers.items():
        question = PYTHON_QUESTION_LIST[question_id]
        validation_function = question.get("validation_function")

        if validation_function and validation_function(answer):
            correct_answers += 1

    # Calculate the score
    score = (correct_answers / total_questions) * 100

    # Generate the final result message
    result_message = (
        f"Quiz Completed!\n"
        f"You answered {correct_answers} out of {total_questions} questions correctly.\n"
        f"Your score is {score:.2f}%."
    )

    return result_message
