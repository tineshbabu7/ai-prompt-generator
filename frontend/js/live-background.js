document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.createElement("canvas");
    canvas.id = "liveBgCanvas";

    // Style the canvas to act as a fixed background
    Object.assign(canvas.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        zIndex: '-1', // Behind everything
        opacity: '0.4', // Very faded so it doesn't overpower the light UI
        pointerEvents: 'none', // Allow clicking through
        background: '#f4f4f8' // Light base color (old app-body background)
    });

    // Insert it behind the app layout
    document.body.insertBefore(canvas, document.body.firstChild);

    const ctx = canvas.getContext("2d");

    let width, height;
    let columns;
    const fontSize = 16;
    let drops = [];

    // Characters for the falling code
    const characters = "01010101<>{}[]()/**/#!=+-$&|%?".split("");

    function resizeCanvas() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        columns = Math.floor(width / fontSize);

        // Reset drops
        drops = [];
        for (let x = 0; x < columns; x++) {
            drops[x] = Math.random() * -100;
        }
    }

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    function draw() {
        // Semi-transparent light grey for the fading trail effect
        ctx.fillStyle = "rgba(244, 244, 248, 0.15)";
        ctx.fillRect(0, 0, width, height);

        // Set font style
        ctx.font = fontSize + "px 'Courier New', monospace";

        for (let i = 0; i < drops.length; i++) {
            // Pick a random character
            const text = characters[Math.floor(Math.random() * characters.length)];

            // Color: Primarily #4D4DFF (the chosen blue), occasionally a brighter highlight
            if (Math.random() > 0.95) {
                ctx.fillStyle = "#ffffff"; // Brighter white tip
            } else if (Math.random() > 0.8) {
                ctx.fillStyle = "#8585ff"; // Lighter blue
            } else {
                ctx.fillStyle = "#4D4DFF"; // Primary blue
            }

            // Draw the character
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            // Send drop back to the top randomly after it crosses the screen
            if (drops[i] * fontSize > height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            // Move drop down
            drops[i]++;
        }

        requestAnimationFrame(draw);
    }

    // Start drawing
    draw();
});
