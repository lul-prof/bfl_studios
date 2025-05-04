// Booking calendar functionality
document.addEventListener('DOMContentLoaded', function() {
    const bookingForm = document.querySelector('#booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            const startTime = document.querySelector('#start_time').value;
            const endTime = document.querySelector('#end_time').value;
            
            if (new Date(startTime) >= new Date(endTime)) {
                e.preventDefault();
                alert('End time must be after start time');
            }
        });
    }

    // Profile picture preview
    const profilePicInput = document.querySelector('#profile_picture');
    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('#profile-preview');
                    if (preview) {
                        preview.src = e.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Toast notifications
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        new bootstrap.Toast(toast).show();
    });
});

// Dark mode toggle
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Check for saved dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}