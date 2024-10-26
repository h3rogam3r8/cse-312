function initialize() {
    console.log("Page initialized");
}

//button for nav-bar
const button = document.querySelector('button');
button.addEventListener('mouseover', () => {
  button.style.backgroundColor = 'gray';
});
button.addEventListener('mouseout', () => {
  button.style.backgroundColor = '';
});

//button for directions
const button2 = document.querySelector('.btn');
button2.addEventListener('mouseover', () => {
  button2.style.backgroundColor = 'gray';
});
button2.addEventListener('mouseout', () => {
  button2.style.backgroundColor = '';
});


const cards = document.querySelectorAll('.card');
cards.forEach(card => {
    card.style.cursor = 'pointer';
    card.addEventListener('mouseover', () => {
        card.classList.add('highlight');
    });

    card.addEventListener('mouseout', () => {
        card.classList.remove('highlight');
    });
});

function setup_navbar_clicks() {
    const nav = document.querySelectorAll('.nav-link');
    nav.forEach(link => {
        link.addEventListener('click', function (event) {
            console.log(`${link.textContent} clicked`);
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setup_navbar_clicks();
    const darkModeToggle = document.getElementById('darkModeToggle');

    const storedToggle = localStorage.getItem('darkMode');
    if (storedToggle === 'enabled') {
        document.documentElement.classList.add('dark-mode');
        darkModeToggle.textContent = 'Light Mode';
    } else {
        document.documentElement.classList.remove('dark-mode');
        darkModeToggle.textContent = 'Dark Mode';
    }

    darkModeToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark-mode');

        if (document.documentElement.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
            darkModeToggle.textContent = 'Light Mode';
        } else {
            localStorage.setItem('darkMode', 'disabled');
            darkModeToggle.textContent = 'Dark Mode';
        }
    });
});

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
}

document.querySelectorAll('.comment-textarea').forEach(textarea => {
    textarea.addEventListener('input', () => autoResizeTextarea(textarea));
});

function updateCharacterCount(textarea, counterElement) {
    const CHAR_LIMIT = 280;
    const text = textarea.value;
    const remaining = CHAR_LIMIT - text.length;
    
    // Updating
    counterElement.innerHTML = `${remaining}`;
    
    // Update counter colors 
    if (remaining < 0) {
        counterElement.classList.remove('warning');
        counterElement.classList.add('error');
    } else if (remaining <= 40) {
        counterElement.classList.remove('error');
        counterElement.classList.add('warning');
    } else {
        counterElement.classList.remove('error', 'warning');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // For comment
    const commentArea = document.getElementById('userComment');
    const commentCounter = document.createElement('div');
    commentCounter.className = 'char-counter';
    commentCounter.innerHTML = '280';
    commentArea.parentNode.appendChild(commentCounter);
    
    commentArea.addEventListener('input', () => {
        updateCharacterCount(commentArea, commentCounter);
    });
    
    // For reply 
    document.querySelectorAll('textarea[name="replyComment"]').forEach(textarea => {
        const replyCounter = document.createElement('div');
        replyCounter.className = 'char-counter';
        replyCounter.innerHTML = '280';
        textarea.parentNode.insertBefore(replyCounter, textarea.nextSibling);
        
        textarea.addEventListener('input', () => {
            updateCharacterCount(textarea, replyCounter);
        });
    });
    
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const textarea = this.querySelector('textarea');
            if (textarea && textarea.value.length > 280) {
                e.preventDefault();
                alert('Your content exceeds the character limit.');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.reaction-buttons').forEach(container => {
        const commentId = container.querySelector('.reaction-btn').dataset.commentId;
        updateReactionCounts(commentId);
        getUserReaction(commentId);
    });

    document.querySelectorAll('.reaction-btn').forEach(button => {
        button.addEventListener('click', handleReaction);
    });

    // Async function for the purpose of live updates
    async function handleReaction(event) {
        const button = event.currentTarget;
        const commentId = button.dataset.commentId;
        const isLike = button.classList.contains('like-btn');
        const reactionType = isLike ? 'like' : 'dislike';

        try {
            const response = await fetch(`/react/${commentId}/${reactionType}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            const data = await response.json();
            updateButtonStates(commentId, reactionType);
            updateCountDisplay(commentId, data.likes, data.dislikes);
        } catch (error) {
            console.error('Reaction incorrectly handled', error);
        }
    }

    // Updating reaction count
    async function updateReactionCounts(commentId) {
        try {
            const response = await fetch(`/react/${commentId}/count`);
            const data = await response.json();
            updateCountDisplay(commentId, data.likes, data.dislikes);
        } catch (error) {
            console.error('Error updating reaction counts:', error);
        }
    }

    async function getUserReaction(commentId) {
        try {
            const response = await fetch(`/get-user-reaction/${commentId}`);
            const data = await response.json();
            if (data.reaction) {
                const container = document.querySelector(`.reaction-buttons [data-comment-id="${commentId}"]`).parentElement;
                const activeBtn = container.querySelector(`.${data.reaction}-btn`);
                activeBtn.classList.add('active');
            }
        } catch (error) {
            console.error('Error getting user reaction:', error);
        }
    }

    function updateCountDisplay(commentId, likes, dislikes) {
        const container = document.querySelector(`.reaction-buttons [data-comment-id="${commentId}"]`).parentElement;
        const likeCount = container.querySelector('.like-count');
        const dislikeCount = container.querySelector('.dislike-count');
        likeCount.textContent = likes > 0 ? likes : '';
        dislikeCount.textContent = dislikes > 0 ? dislikes : '';
    }

    // Function to ensure mutually exclusive likes and dislikes
    function updateButtonStates(commentId, newReaction) {
        const container = document.querySelector(`.reaction-buttons [data-comment-id="${commentId}"]`).parentElement;
        const likeBtn = container.querySelector('.like-btn');
        const dislikeBtn = container.querySelector('.dislike-btn');
        
        if (likeBtn.classList.contains('active') && newReaction === 'dislike') {
            likeBtn.classList.remove('active');
            dislikeBtn.classList.add('active');
        } else if (dislikeBtn.classList.contains('active') && newReaction === 'like') {
            dislikeBtn.classList.remove('active');
            likeBtn.classList.add('active');
        } else {
            const clickedBtn = container.querySelector(`.${newReaction}-btn`);
            clickedBtn.classList.toggle('active');
        }
    }
});