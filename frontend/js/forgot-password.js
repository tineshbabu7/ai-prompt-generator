async function resetPassword() {
    const email = document.getElementById("email").value.trim();
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const errorBox = document.getElementById("error");
    const successBox = document.getElementById("success");
    const btn = document.getElementById("resetBtn");

    errorBox.innerText = "";
    successBox.innerText = "";

    if (!email || !newPassword || !confirmPassword) {
        errorBox.innerText = "Please fill in all fields."; return;
    }
    if (newPassword !== confirmPassword) {
        errorBox.innerText = "Passwords do not match."; return;
    }
    if (newPassword.length < 6) {
        errorBox.innerText = "Password must be at least 6 characters."; return;
    }

    btn.disabled = true;
    btn.textContent = "Resetting...";

    try {
        const res = await fetch("http://127.0.0.1:8000/reset-password", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, new_password: newPassword })
        });

        const data = await res.json();

        if (!res.ok) {
            errorBox.innerText = data.detail || "Reset failed. Please try again.";
            return;
        }

        successBox.innerText = "✅ Password reset! Redirecting to sign in...";
        setTimeout(() => { window.location.href = "index.html"; }, 2000);

    } catch (err) {
        errorBox.innerText = "Cannot reach server. Is the backend running?";
    } finally {
        btn.disabled = false;
        btn.textContent = "Reset Password";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("keydown", e => { if (e.key === "Enter") resetPassword(); });
});
