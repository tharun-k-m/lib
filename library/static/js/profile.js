// library/static/js/profile.js

// This function gets the CSRF token from the cookie.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
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

// Function to show a message to the user (optional, but good practice)
function showMessage(message, type = 'success') {
    if (!messageContainer) return;

    const messageElement = document.createElement('div');
    messageElement.className = `alert alert-${type}`;
    messageElement.textContent = message;

    // Check if the container is already filled with a message
    if (messageContainer.hasChildNodes()) {
        messageContainer.innerHTML = '';
    }
    messageContainer.appendChild(messageElement);

    // Hide the message after 5 seconds
    setTimeout(() => {
        messageElement.remove();
    }, 5000);
}

// Function to handle the AJAX requests for returning a book
async function handleReturnAction(url, button) {
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
            // Find the parent book-item and remove it from the DOM
            const bookItem = button.closest('.book-item');
            if (bookItem) {
                bookItem.remove();
            }
        } else {
            showMessage(result.error, 'error');
        }
    } catch (error) {
        showMessage('An error occurred. Please try again.', 'error');
        console.error('Error:', error);
    }
}

// Event listeners for the "Return" buttons
document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the profile page by looking for a message container
    const returnButtons = document.querySelectorAll('.return-button');

    if (returnButtons.length > 0) {
        // Add a message container to the profile page dynamically
        const header = document.querySelector('.profile-header');
        if (header) {
            const containerDiv = document.createElement('div');
            containerDiv.id = 'message-container';
            header.insertAdjacentElement('afterend', containerDiv);
        }

        returnButtons.forEach(button => {
            button.addEventListener('click', () => {
                const bookId = button.dataset.bookId;
                const url = `/return-book/${bookId}/`;
                handleReturnAction(url, button);
            });
        });
    }
});
