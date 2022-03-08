const loginRadio = document.querySelector('.slide-controls label.login');
const signupRadio = document.querySelector('.slide-controls label.signup');
const titleLogin = document.querySelector('.title-login');
const titleSignup = document.querySelector('.title-signup');
const loginForm = document.querySelector('.login-container');
const signupForm = document.querySelector('.signup-container');

signupRadio.addEventListener("click", (e) => {
    titleLogin.style.marginLeft = "-50%";
    loginForm.style.marginLeft = "-50%";
});

loginRadio.addEventListener("click", (e) => {
    titleLogin.style.marginLeft = "0%";
    loginForm.style.marginLeft = "0%";
});