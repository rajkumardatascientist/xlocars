document.addEventListener('DOMContentLoaded', function() {
    const carCards = document.querySelectorAll('.car-card');

    carCards.forEach(card => {
        const img = card.querySelector('.image-slider img'); // Find the image
        if (img) {
            const imageUrl = img.src; // Get the image URL

            card.style.setProperty('--bg-image', `url(${imageUrl})`); // Set the CSS variable
            card.style.setProperty('--has-image', 'true');  // To prevent empty bg when no images exist
        } else {
          card.style.setProperty('--has-image', 'false');
        }
    });
});