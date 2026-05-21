async function signup() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const errorBox = document.getElementById("error");
    const successBox = document.getElementById("success");
    const btn = document.getElementById("signupBtn");

    errorBox.innerText = "";
    successBox.innerText = "";

    if (!email || !password || !confirmPassword) {
        errorBox.innerText = "Please fill in all fields.";
        return;
    }

    if (password !== confirmPassword) {
        errorBox.innerText = "Passwords do not match.";
        return;
    }

    if (password.length < 6) {
        errorBox.innerText = "Password must be at least 6 characters.";
        return;
    }

    btn.disabled = true;
    btn.textContent = "Creating account...";

    try {
        const response = await fetch("https://ai-prompt-generator-yfi4.onrender.com/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, password: password })
        });
        const data = await response.json();

        if (!response.ok) {
            errorBox.innerText = data.detail || "Registration failed.";
            return;
        }

        successBox.innerText = "Account created! Redirecting to login...";
        setTimeout(() => {
            window.location.href = "index.html";
        }, 1500);

    } catch (err) {
        errorBox.innerText = "Cannot reach server. Is the backend running?";
    } finally {
        btn.disabled = false;
        btn.textContent = "Create Account";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("keydown", (e) => {
        if (e.key === "Enter") signup();
    });
});
