// Toggle between login and signup forms
function switchToSignup() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'flex';
    document.getElementById('form-header').innerText = 'Create an account';
}

function switchToLogin() {
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'flex';
    document.getElementById('form-header').innerText = 'Have an account?';
}

// Toggle password visibility
function togglePassword() {
    const passwordFields = document.querySelectorAll('.password-container input');
    passwordFields.forEach(field => {
        if (field.type === 'password') {
            field.type = 'text';
        } else {
            field.type = 'password';
        }
    });
}






const API_URL = "http://127.0.0.1:5000";

// Login Function
async function login(username, password) {
    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem("user_id", data.user_id);
        alert("Login Successful!");
    } else {
        alert(data.error);
    }
}

// Fetch Suggested Profiles
async function getSuggestedProfiles() {
    const response = await fetch(`${API_URL}/suggested_profiles`);
    const data = await response.json();
    document.getElementById("profiles").innerHTML = data.profiles.map(profile => `
        <div class="profile">
            <img src="${profile.profile_pic}" alt="Profile Pic">
            <h3>${profile.username} (${profile.age}, ${profile.gender})</h3>
            <p>${profile.profession} - ${profile.location}</p>
            <p>${profile.bio}</p>
            <button onclick="viewProfile(${profile.id})">View Profile</button>
        </div>
    `).join("");
}

// Fetch Profile Details
async function viewProfile(userId) {
    const response = await fetch(`${API_URL}/profile/${userId}`);
    const data = await response.json();
    document.getElementById("profileDetails").innerHTML = `
        <h2>${data.username}</h2>
        <p><strong>Profession:</strong> ${data.profession}</p>
        <p><strong>Location:</strong> ${data.location}</p>
        <p><strong>Age:</strong> ${data.age}</p>
        <p><strong>Gender:</strong> ${data.gender}</p>
        <p><strong>Interests:</strong> ${data.interests.join(", ")}</p>
        <p>${data.bio}</p>
        <button onclick="sendInterest(${userId})">Interested</button>
        <button onclick="removeProfile(${userId})">Not Interested</button>
    `;
}

// Send Interest
async function sendInterest(userId) {
    await fetch(`${API_URL}/interested/${userId}`, { method: "POST" });
    alert("Interest Sent!");
}

// Remove Profile
async function removeProfile(userId) {
    await fetch(`${API_URL}/not_interested/${userId}`, { method: "POST" });
    alert("Profile Removed!");
}
