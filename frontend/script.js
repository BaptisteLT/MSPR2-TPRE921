const API_URL = "http://127.0.0.1:8080/function"; // L'adresse de ton OpenFaaS local

// Fonction 1 : Appel de cofrap-gen-pwd
async function createAccount() {
    const username = document.getElementById('reg-username').value;
    const resDiv = document.getElementById('reg-result');
    resDiv.style.display = 'block';
    resDiv.innerHTML = "Création en cours...";

    try {
        const response = await fetch(`${API_URL}/cofrap-gen-pwd`, {
            method: 'POST',
            body: JSON.stringify({ username: username })
        });
        const data = await response.json();
        
        if(data.error) {
            resDiv.innerHTML = `<span style="color:red">${data.error}</span>`;
        } else {
            resDiv.innerHTML = `
                <strong style="color:green">${data.message}</strong><br>
                Votre mot de passe généré : <b>${data.password}</b><br>
                <img src="data:image/png;base64,${data.qr_code_base64}" alt="QR Code contenant votre mot de passe généré pour le scanner" />
            `;
        }
    } catch (err) { resDiv.innerHTML = "Erreur de connexion à l'API OpenFaaS."; }
}

// Fonction 2 : Appel de cofrap-gen-2fa
async function generate2FA() {
    const username = document.getElementById('mfa-username').value;
    const resDiv = document.getElementById('mfa-result');
    resDiv.style.display = 'block';
    resDiv.innerHTML = "Génération en cours...";

    try {
        const response = await fetch(`${API_URL}/cofrap-gen-2fa`, {
            method: 'POST',
            body: JSON.stringify({ username: username })
        });
        const data = await response.json();
        
        if(data.error) {
            resDiv.innerHTML = `<span style="color:red">${data.error}</span>`;
        } else {
            resDiv.innerHTML = `
                <strong style="color:green">${data.message}</strong><br>
                Scannez ce QR Code dans Google Authenticator :<br>
                <img src="data:image/png;base64,${data.qr_code_2fa_base64}" alt="QR Code d'authentification à double facteur à scanner dans votre application de sécurité" />
            `;
        }
    } catch (err) { resDiv.innerHTML = "Erreur de connexion à l'API OpenFaaS."; }
}

// Fonction 3 : Appel de cofrap-auth
async function login() {
    const username = document.getElementById('auth-username').value;
    const password = document.getElementById('auth-password').value;
    const totp = document.getElementById('auth-totp').value;
    const resDiv = document.getElementById('auth-result');
    resDiv.style.display = 'block';
    resDiv.innerHTML = "Vérification...";

    try {
        const response = await fetch(`${API_URL}/cofrap-auth`, {
            method: 'POST',
            body: JSON.stringify({ 
                username: username, 
                password: password, 
                totp_code: totp 
            })
        });
        const data = await response.json();
        
        if(data.error) {
            resDiv.innerHTML = `<span style="color:red">Erreur : ${data.error}</span>`;
        } else {
            resDiv.innerHTML = `<strong style="color:green">${data.message}</strong>`;
        }
    } catch (err) { resDiv.innerHTML = "Erreur de connexion à l'API OpenFaaS."; }
}