const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('captureBtn');
const statusDisplay = document.getElementById('status');
const emotionDisplay = document.getElementById('emotion');
const confidenceDisplay = document.getElementById('confidence');
const detailsDisplay = document.getElementById('details');

let emotionChart = null;

let predictionInProgress = false;

if (video) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            if (captureBtn) captureBtn.disabled = false;
            if (statusDisplay) statusDisplay.textContent = 'Webcam ready. Click "Start Prediction" to begin.';
        })
        .catch((err) => {
            console.error("Error accessing webcam:", err);
            if (statusDisplay) statusDisplay.textContent = 'Error accessing webcam.';
        });
}

function createEmotionChart() {
    const chartCanvas = document.getElementById('emotionChart');
    if (!chartCanvas) return;
    
    const ctx = chartCanvas.getContext('2d');
    emotionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'],
            datasets: [{
                label: 'Emotion Scores (%)',
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',   // Angry
                    'rgba(153, 102, 255, 0.6)',  // Disgust
                    'rgba(255, 159, 64, 0.6)',   // Fear
                    'rgba(75, 192, 192, 0.6)',   // Happy
                    'rgba(54, 162, 235, 0.6)',   // Sad
                    'rgba(255, 206, 86, 0.6)',   // Surprise
                    'rgba(201, 203, 207, 0.6)'   // Neutral
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function updateEmotionChart(details) {
    if (!emotionChart) return;

    emotionChart.data.datasets[0].data = [
        details.angry || 0,
        details.disgust || 0,
        details.fear || 0,
        details.happy || 0,
        details.sad || 0,
        details.surprise || 0,
        details.neutral || 0
    ];
    emotionChart.update();
}

async function captureAndPredict() {
    if (!statusDisplay || !canvas || !video) return;
    
    statusDisplay.textContent = 'Capturing...';

    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg');

    try {
        statusDisplay.textContent = 'Sending for prediction...';
        const response = await fetch('http://127.0.0.1:5000/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();
        console.log('Received prediction data:', data);

        if (data.error) {
            statusDisplay.textContent = 'Error: ' + (data.error || 'Unknown error.');
            if (emotionDisplay) emotionDisplay.textContent = '---';
            if (confidenceDisplay) confidenceDisplay.textContent = '---';
            if (detailsDisplay) detailsDisplay.textContent = 'No details available.';
            updateEmotionChart({ angry: 0, disgust: 0, fear: 0, happy: 0, sad: 0, surprise: 0, neutral: 0 });
        } else {
            statusDisplay.textContent = 'Prediction received.';
            if (emotionDisplay) emotionDisplay.textContent = data.emotion || 'N/A';
            if (confidenceDisplay) {
                confidenceDisplay.textContent = (data.confidence !== undefined)
                    ? `${parseFloat(data.confidence).toFixed(2)}%`
                    : '---';
            }

            let detailsText = 'Emotion Scores:\n';
            if (data.details && typeof data.details === 'object') {
                for (const [emotion, score] of Object.entries(data.details)) {
                    detailsText += `${emotion}: ${parseFloat(score).toFixed(2)}%\n`;
                }
                updateEmotionChart(data.details);
            } else {
                detailsText += 'No details available.';
                updateEmotionChart({ angry: 0, disgust: 0, fear: 0, happy: 0, sad: 0, surprise: 0, neutral: 0 });
            }
            if (detailsDisplay) detailsDisplay.textContent = detailsText;
        }
    } catch (error) {
        console.error('Error during prediction:', error);
        if (statusDisplay) statusDisplay.textContent = 'Prediction failed: ' + (error.message || error);
        if (emotionDisplay) emotionDisplay.textContent = '---';
        if (confidenceDisplay) confidenceDisplay.textContent = '---';
        if (detailsDisplay) detailsDisplay.textContent = 'No details available.';
        updateEmotionChart({ angry: 0, disgust: 0, fear: 0, happy: 0, sad: 0, surprise: 0, neutral: 0 });
    }
}


function startAutoPredict() {
    autoPredictInterval = setInterval(async () => {
      if (!predictionInProgress) {
        predictionInProgress = true;
        await captureAndPredict();
        predictionInProgress = false;
      }
    }, 2000);
  }
  
function stopAutoPredict() {
    if (autoPredictInterval) {
      clearInterval(autoPredictInterval);
      autoPredictInterval = null;
      if (statusDisplay) statusDisplay.textContent = 'Auto-prediction stopped.';
    }
  }

// Add event listeners if elements exist
if (captureBtn) {
    captureBtn.addEventListener('click', () => {
        startAutoPredict();
        captureBtn.disabled = true;
        if (document.getElementById('stopBtn')) {
            document.getElementById('stopBtn').disabled = false;
        }
        if (statusDisplay) statusDisplay.textContent = 'Auto-prediction started!';
    });
}

if (document.getElementById('stopBtn')) {
    document.getElementById('stopBtn').addEventListener('click', () => {
        stopAutoPredict();
        if (captureBtn) captureBtn.disabled = false;
        document.getElementById('stopBtn').disabled = true;
    });
}

// Login and User Management Functions -----------------------------

function checkLoginStatus() {
    const loggedInUser = localStorage.getItem('loggedInUser');
    return loggedInUser !== null;
}

function getCurrentUser() {
    return localStorage.getItem('loggedInUser');
}

function getUserProfilePicture() {
    return localStorage.getItem('userProfilePicture');
}

function loginUser(username) {
    localStorage.setItem('loggedInUser', username);
    updateNavigation();
    // Redirect to profile page after login
    window.location.href = "profile.html";
}

function saveUserProfilePicture(imageData) {
    if (imageData) {
        localStorage.setItem('userProfilePicture', imageData);
    }
}

function logoutUser() {
    localStorage.removeItem('loggedInUser');
    localStorage.removeItem('userProfilePicture');
    updateNavigation();
    window.location.href = "index.html"; 
}

function updateNavigation() {
    const isLoggedIn = checkLoginStatus();
    
    const navLinks = document.querySelectorAll('.navbar ul li');
    const navItems = {
        emotion: document.querySelector('.navbar a[href="index.html"]')?.parentElement,
        analyze: document.querySelector('.navbar a[href="analyze.html"]')?.parentElement,
        demo: document.querySelector('.navbar a[href="demo.html"]')?.parentElement,
        login: document.querySelector('.navbar a[href="login.html"]')?.parentElement,
        register: document.querySelector('.navbar a[href="register.html"]')?.parentElement,
        profile: document.querySelector('.navbar a[href="profile.html"]')?.parentElement
    };
    
    if (!navItems.login || !navItems.register || !navItems.profile) {
        console.error('One or more navigation elements not found');
        return;
    }
    
    if (isLoggedIn) {
        navItems.login.style.display = 'none';
        navItems.register.style.display = 'none';
        navItems.profile.style.display = 'block';
    } else {
        navItems.login.style.display = 'block';
        navItems.register.style.display = 'block';
        navItems.profile.style.display = 'none';
    }
    
    if (navItems.emotion) navItems.emotion.style.display = 'block';
    if (navItems.analyze) navItems.analyze.style.display = 'block';
    if (navItems.demo) navItems.demo.style.display = 'block';
    
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    navLinks.forEach(navItem => {
        const link = navItem.querySelector('a');
        if (link && link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        } else if (link) {
            link.classList.remove('active');
        }
    });
    
    if (currentPage === 'profile.html' && !isLoggedIn) {
        window.location.href = 'login.html';
        return; // Stop execution
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded - updating navigation");
    updateNavigation();
    
    if (document.getElementById('emotionChart')) {
        createEmotionChart();
    }
    
    const profileContainer = document.getElementById('profileContainer');
    const notLoggedInMessage = document.getElementById('notLoggedInMessage');
    
    if (profileContainer && notLoggedInMessage) {
        const username = getCurrentUser();
        if (username) {
            if (document.getElementById('usernameDisplay')) {
                document.getElementById('usernameDisplay').textContent = username;
            }
            profileContainer.style.display = 'block';
            notLoggedInMessage.style.display = 'none';
            
            const profilePicture = getUserProfilePicture();
            if (profilePicture && document.getElementById('profilePicture')) {
                document.getElementById('profilePicture').src = profilePicture;
                document.getElementById('profilePicture').style.display = 'block';
                const fallbackElement = document.querySelector('.profile-avatar-fallback');
                if (fallbackElement) {
                    fallbackElement.style.display = 'none';
                }
            }
        } else {
            profileContainer.style.display = 'none';
            notLoggedInMessage.style.display = 'block';
        }
    }
});