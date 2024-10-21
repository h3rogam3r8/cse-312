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


function handleSearch() {
    const search = document.getElementById('searchInput').value.toLowerCase();

    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        if (title.includes(search)) {
            card.parentElement.style.display = ''; // Show the card
        } else {
            card.parentElement.style.display = 'none'; // Hide the card
        }
    });
}

const searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('input', handleSearch);
}

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
