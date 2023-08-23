$(document).ready(function() {
    // Open image in a new tab on click
    $('.image-box').click(function() {
        const imgSrc = $(this).find('img').attr('src');
        window.open(imgSrc, '_blank');
    });
});
