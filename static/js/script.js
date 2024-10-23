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


// function handleSearch() {
//     const search = document.getElementById('searchInput').value.toLowerCase();

//     cards.forEach(card => {
//         const title = card.querySelector('.card-title').textContent.toLowerCase();
//         if (title.includes(search)) {
//             card.parentElement.style.display = ''; // Show the card
//         } else {
//             card.parentElement.style.display = 'none'; // Hide the card
//         }
//     });
// }

// const searchInput = document.getElementById('searchInput');
// if (searchInput) {
//     searchInput.addEventListener('input', handleSearch);
// }

document.addEventListener('DOMContentLoaded', () => {
    const stars = document.querySelectorAll('.star-rating i');
    const selectedRatingInput = document.getElementById('selectedRating');
    
    // Handle click event to store the rating
    stars.forEach(star => {
        star.addEventListener('click', function () {
            const rating = this.getAttribute('data-value');
            selectedRatingInput.value = rating; // Set the hidden input value

            // Highlight all stars up to the clicked one
            stars.forEach(s => {
                if (s.getAttribute('data-value') <= rating) {
                    s.classList.add('text-warning'); // Highlight star (yellow color)
                    s.classList.remove('bi-star'); // Empty star
                    s.classList.add('bi-star-fill'); // Filled star
                } else {
                    s.classList.remove('text-warning'); // Remove highlight
                    s.classList.add('bi-star'); // Empty star
                    s.classList.remove('bi-star-fill'); // Remove filled star
                }
            });

            console.log(`User selected rating: ${rating}`); // For debugging
        });

        // Handle hover effect for a preview
        star.addEventListener('mouseover', function () {
            const rating = this.getAttribute('data-value');
            
            // Highlight stars up to the hovered one
            stars.forEach(s => {
                if (s.getAttribute('data-value') <= rating) {
                    s.classList.add('text-warning'); // Highlight star
                } else {
                    s.classList.remove('text-warning'); // Unhighlight the others
                }
            });
        });

        // Reset stars to the selected rating when the mouse leaves
        star.addEventListener('mouseout', function () {
            const selectedRating = selectedRatingInput.value; // Get the current selected rating

            // Reset the stars to the currently selected rating
            stars.forEach(s => {
                if (s.getAttribute('data-value') <= selectedRating) {
                    s.classList.add('text-warning'); // Keep stars highlighted
                } else {
                    s.classList.remove('text-warning'); // Unhighlight unselected stars
                }
            });
        });
    });
});

// Display/Add comment
document.addEventListener('DOMContentLoaded', async () => {
    if (window.location.pathname !== '/') {
        const commentForm = document.getElementById('commentForm');
        const commentsSection = document.getElementById('commentsSection');
        const restaurant = document.getElementById('commentsSection').getAttribute('restaurant');

        fetch(`/comments/${restaurant}`)
        .then(response => response.json())
        .then(data => {
            data.forEach(comment => addCommentToDOM(comment));
        })
        .catch(error => console.error('Error fetching comments:', error));
        
        commentForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(commentForm);
            const userComment = formData.get('userComment') || '';

            const response = await fetch(commentForm.action, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            addCommentToDOM({
                username: data.username,
                comment: userComment,
                rating: data.rating,
            });

        });

        function htmlEscaper(str) {
            const div = document.createElement('div');
            div.innerText = str;
            return div.innerHTML; 
        }

        function addCommentToDOM(commentData) {
            const emptyStars = 5 - commentData.rating;
            const commentHTML = `
                <div class="comment mb-4">
                    <div class="d-flex">
                        <div class="flex-shrink-0">
                            <img src="/static/images/kris.png" alt="User Avatar" class="rounded-circle" style="width: 50px;">
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="mb-0">${commentData.username}</h6>
                            <div class="star-rating" style="margin-top: 5px;">
                                ${'<i class="bi bi-star-fill"></i>'.repeat(commentData.rating)}
                                ${'<i class="bi bi-star"></i>'.repeat(emptyStars)}
                            </div>
                            <p class="mb-1">${htmlEscaper(commentData.comment)}</p>
        
                            <!-- Reply link -->
                            <span class="reply-link" style="cursor: pointer; color: #007bff;">Reply</span>
        
                            <!-- Reply form (initially hidden) -->
                            <form class="replyForm" style="display: none; margin-top: 10px;">
                                <div class="mb-2">
                                    <textarea class="form-control" rows="2" placeholder="Reply to this comment..."></textarea>
                                </div>
                                <button type="submit" class="btn btn-secondary btn-sm">Submit Reply</button>
                            </form>
                        </div>
                    </div>
                </div>
            `;
            commentsSection.insertAdjacentHTML('beforeend', commentHTML);
        
            const replyLink = commentsSection.lastElementChild.querySelector('.reply-link');
            replyLink.addEventListener('click', (event) => {
                event.preventDefault(); 
                const replyForm = replyLink.nextElementSibling; // find reply form
                replyForm.style.display = replyForm.style.display === 'block' ? 'none' : 'block';
            });
        }
    }
});
    