document.getElementById("chat-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    let input = document.getElementById("user-input").value;
    let response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
    });
    let data = await response.json();
    document.getElementById("chat-box").innerHTML += "<p><b>Du:</b> " + input + "</p>";
    document.getElementById("chat-box").innerHTML += "<p><b>Nova AI:</b> " + data.response + "</p>";
    document.getElementById("user-input").value = "";
});
