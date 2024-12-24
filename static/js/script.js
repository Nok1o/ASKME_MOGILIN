function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function handleFeedbackQuestion(actionType, card, numericEntry) {
    const questionId = card.dataset.questionId;

    console.log(`${actionType.toUpperCase()}ING...`, questionId);
    fetch(new Request(`/question/${questionId}/feedback`, {
        method: "POST",
        body: JSON.stringify({ type: actionType }),
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        mode: 'same-origin'
    }))
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Failed to ${actionType} the question`);
            }
            return response.json();
        })
        .then((data) => {
            if (data['likes_count'] !== undefined) {
                numericEntry.value = String(data['likes_count']);
            } else {
                console.error("likes_count not found in response");
            }
        })
        .catch((error) => {
            console.error(`Error ${actionType}ing the question:`, error);
        });
}

function handleFeedbackAnswer(actionType, card, numericEntry) {
    const answerId = card.dataset.answerId;

    console.log(`${actionType.toUpperCase()}ING...`, answerId);
    fetch(new Request(`/answer/${answerId}/feedback`, {
        method: "POST",
        body: JSON.stringify({type: actionType}),
        headers: {'X-CSRFToken': getCookie('csrftoken')},
        mode: 'same-origin'
    }))
        .then((response) => {
            if (!response.ok) {
                throw new Error("Failed to like the answer");
            }
            return response.json();
        })
        .then((data) => {
            if (data['likes_count'] !== undefined) {
                numericEntry.value = String(data['likes_count']);
                previousValue = data['likes_count'];
            } else {
                console.error("likes_count not found in response");
            }
        })
        .catch((error) => {
            console.error("Error liking the answer:", error);
            numericEntry.value = previousValue;
        });
}

function handleCorrectFeedback(is_correct, card) {
    const answer_id = card.dataset.answerId;

    console.log(`Answer is correct now ${is_correct}`, answer_id);
    fetch(new Request(`/answer/${answer_id}/correct`, {
        method: "POST",
        body: JSON.stringify({ is_correct: is_correct }),
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        mode: 'same-origin'
    }))
        .then((response) => {
            if (!response.ok) {
                throw new Error(`Failed to set correct answer to ${is_correct}`);
            }
            return response.json();
        })
        .catch((error) => {
            console.error(`Failed to set correct answer to ${is_correct}:`, error);
        });
}


const cards = document.getElementsByClassName('card');

for (const card of cards) {
    const numericEntry = card.getElementsByClassName('card-likes')[0];
    const likeButton = card.getElementsByClassName('like-button')[0];
    const dislikeButton = card.getElementsByClassName('dislike-button')[0];

    likeButton.addEventListener('click', function () {
        handleFeedbackQuestion("like", card, numericEntry);
        if (! dislikeButton.disabled) {
            likeButton.disabled = true;
        }
        dislikeButton.disabled = false;
    });

    dislikeButton.addEventListener('click', function () {
        handleFeedbackQuestion("dislike", card, numericEntry);
        if (! likeButton.disabled) {
            dislikeButton.disabled = true;
        }
        likeButton.disabled = false;
    });
}

const answer_cards = document.getElementsByClassName('answer-card');
const question_card = document.getElementById('question-card');

let user_is_author = 'False';
if (question_card) {
    user_is_author = question_card.dataset.userIsAuthor;
}

for (const card of answer_cards) {
    const numericEntry = card.getElementsByClassName('card-likes')[0];
    const likeButton = card.getElementsByClassName('like-button')[0];
    const dislikeButton = card.getElementsByClassName('dislike-button')[0];
    const checkbox = card.getElementsByClassName('answer-checkbox')[0];


    likeButton.addEventListener('click', function () {
        handleFeedbackAnswer("like", card, numericEntry);
        if (! dislikeButton.disabled) {
            likeButton.disabled = true;
        }
        dislikeButton.disabled = false;
    });

    dislikeButton.addEventListener('click', function () {
        handleFeedbackAnswer("dislike", card, numericEntry);
        if (! likeButton.disabled) {
            dislikeButton.disabled = true;
        }
        likeButton.disabled = false;
    });

    if (user_is_author === 'False') {
        checkbox.disabled = true;
    }
    else {
        checkbox.addEventListener('change', function (){
            handleCorrectFeedback(checkbox.checked, card);
        });
    }
}