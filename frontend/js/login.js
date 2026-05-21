async function login() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const errorBox = document.getElementById("error");
  const btn = document.getElementById("loginBtn");

  errorBox.innerText = "";

  if (!email || !password) {
    errorBox.innerText = "Please fill in all fields.";
    return;
  }

  btn.disabled = true;
  btn.textContent = "Signing in...";

  try {
    const response = await fetch("https://ai-prompt-generator-yfi4.onrender.com/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: email, password: password })
    });

    const data = await response.json();

    if (!response.ok) {
      errorBox.innerText = data.detail || "Invalid email or password.";
      return;
    }

    localStorage.setItem("token", data.access_token);
    window.location.href = "prompt.html";

  } catch (err) {
    errorBox.innerText = "Cannot reach server. Is the backend running?";
  } finally {
    btn.disabled = false;
    btn.textContent = "Sign In";
  }
}

// Allow pressing Enter to submit
document.addEventListener("DOMContentLoaded", () => {
  document.addEventListener("keydown", (e) => {
    if (e.key === "Enter") login();
  });
});
