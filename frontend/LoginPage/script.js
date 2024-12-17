const username = document.getElementById('username')
const password = document.getElementById('password')
const form = document.getElementById('form')
const errorElement = document.getElementById('error')

form.addEventListener('submit', (e) => {
    e.preventDefault(); // Prevents the default form submission
    
    // Validation logic here
    let message = [];
    if (username.value === '' || username.value == null) {
        message.push('Username is required');
    }
    if (password.value.length < 6) {
        message.push('Password must be at least 6 characters');
    }
    if (password.value.length > 20) {
        message.push('Password cannot be more than 20 characters');
    }
    if (password.value === 'password') {
        message.push('Password cannot be "password"');
    }
    if (message.length > 0) {
        errorElement.innerText = message.join(', ');
    } else {
        errorElement.innerText = 'Login successful'; // Placeholder message
    }
});
