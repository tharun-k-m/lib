// library/static/js/actions.js

// This function gets the CSRF token from the cookie.
// It's required for all POST requests in Django.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
const messageContainer = document.getElementById('message-container');
const container = document.querySelector('.container');
const isAuthenticated = container ? container.dataset.isAuthenticated === 'true' : false;

// Function to show a message to the user
function showMessage(message, type = 'success') {
    const messageElement = document.createElement('div');
    messageElement.className = `alert alert-${type}`; // We'll use this class for styling
    messageElement.textContent = message;
    messageContainer.innerHTML = ''; // Clear previous messages
    messageContainer.appendChild(messageElement);
}

// Function to handle the AJAX requests
async function handleAction(url, button) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
        });

        const result = await response.json();

        if (response.ok) {
            showMessage(result.message, 'success');
            // Add a class to the link to make it look disabled
            button.classList.add('disabled');
            if (button.id === 'favorite-btn') {
                button.textContent = 'Favorited';
            } else if (button.id === 'borrow-btn') {
                button.textContent = 'Borrowed';
            } else if (button.id === 'buy-btn') {
                button.textContent = 'Purchased';
            }
        } else {
            showMessage(result.error, 'error');
        }
    } catch (error) {
        showMessage('An error occurred. Please try again.', 'error');
        console.error('Error:', error);
    }
}

// Event listeners for the buttons
document.addEventListener('DOMContentLoaded', () => {
    const actionButtons = document.querySelectorAll('.action-buttons a');

    actionButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            if (isAuthenticated) {
                event.preventDefault(); // Stop the default link behavior
                handleAction(button.dataset.url, button);
            }
        });
    });
});
