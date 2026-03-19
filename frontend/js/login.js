document.getElementById('loginForm').addEventListener('submit', function(event) {
    // Prevent the page from reloading when you click submit
    event.preventDefault();
    
    // Get the values typed into the boxes
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    // Check if the admin name and password are correct
    // (If your original password was something else, just change 'admin' below)
    if (user === 'admin' && pass === 'admin') {
        // Success! Go directly to the room dashboard
        window.location.href = 'dashboard.html';
    } else {
        // Show the error message if they type it wrong
        document.getElementById('error-msg').style.display = 'block';
    }
});