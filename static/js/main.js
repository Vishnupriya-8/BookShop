jQuery(document).ready(function() {
    // Initialize slider only if it exists
    if (jQuery('#demo').length > 0) {
        jQuery('#demo').skdslider({
            delay: 2000,
            animationSpeed: 2000,
            showNextPrev: true,
            showPlayButton: true,
            autoSlide: true,
            animationType: 'fading'
        });
    }

    // Initialize other components
    jQuery('.menu-trigger').on('click', function() {
        jQuery('.off-canvas-menu').addClass('open');
        jQuery('.off-canvas-menu-overlay').addClass('active');
    });

    jQuery('.menu-close, .off-canvas-menu-overlay').on('click', function() {
        jQuery('.off-canvas-menu').removeClass('open');
        jQuery('.off-canvas-menu-overlay').removeClass('active');
    });

    // Search functionality
    jQuery('.search-trigger').on('click', function() {
        jQuery('.search-bar').addClass('active');
    });

    jQuery('.search-close').on('click', function() {
        jQuery('.search-bar').removeClass('active');
    });
});

// Add error handling for slider images
window.addEventListener('error', function(e) {
    if (e.target.tagName === 'IMG') {
        console.log('Image load error:', e.target.src);
        e.target.src = '/static/images/placeholder.jpg'; // Add a placeholder image
    }
}, true); 