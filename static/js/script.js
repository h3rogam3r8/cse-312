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