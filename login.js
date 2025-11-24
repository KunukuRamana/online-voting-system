document.getElementById("loginForm").addEventListener("submit", function(event){
    event.preventDefault();

    let voterId = document.getElementById("voterId").value;
    let password = document.getElementById("password").value;

    // Dummy login for now
    if (voterId === "VOTER123" && password === "1234") {
        document.getElementById("message").style.color = "green";
        document.getElementById("message").innerText = "Login Successful!";
        
        setTimeout(() => {
            window.location.href = "vote.html"; 
        }, 1000);

    } else {
        document.getElementById("message").innerText = "Invalid Voter ID or Password!";
    }
});
