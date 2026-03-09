
const registerForm = document.querySelector("form");

if (document.title === "Register Page") {

    registerForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const fullName = registerForm.children[0].value;
        const email = registerForm.children[1].value;
        const username = registerForm.children[2].value;
        const password = registerForm.children[3].value;
        const confirmPassword = registerForm.children[4].value;

        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        let users = JSON.parse(localStorage.getItem("users")) || [];

        const userExists = users.find(user => user.username === username);

        if (userExists) {
            alert("Username already exists!");
            return;
        }

        const newUser = {
            fullName: fullName,
            email: email,
            username: username,
            password: password
        };

        users.push(newUser);

        localStorage.setItem("users", JSON.stringify(users));

        alert("Registration successful!");

        window.location.href = "login.html";
    });

}


if (document.title === "Login Page") {

    registerForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const username = registerForm.children[0].value;
        const password = registerForm.children[1].value;

        let users = JSON.parse(localStorage.getItem("users")) || [];

        const validUser = users.find(
            user => user.username === username && user.password === password
        );

        if (validUser) {
            alert("Login successful!");
            window.location.href = "dashboard.html"; 
        } else {
            alert("Invalid username or password");
        }
    });

}