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


    document.addEventListener('DOMContentLoaded', () => {
        setup_navbar_clicks();
    });

}

function handleSearch(){
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

document.getElementById('searchInput').addEventListener('input', handleSearch);
