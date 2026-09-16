/* redirect to dashboard */

function goDashboard(){

window.location.href="dashboard.html";

}


/* reveal animation */

const reveals=document.querySelectorAll(".reveal");

function revealOnScroll(){

reveals.forEach((el)=>{

const top=el.getBoundingClientRect().top;

if(top < window.innerHeight - 100){

el.classList.add("active");

}

});

}

window.addEventListener("scroll",revealOnScroll);

revealOnScroll();



/* scroll progress bar */

window.addEventListener("scroll",()=>{

const scrollTop=document.documentElement.scrollTop;

const height=document.documentElement.scrollHeight -
document.documentElement.clientHeight;

const progress=(scrollTop/height)*100;

document.getElementById("scrollBar").style.width=progress+"%";

});


/* animated counters */

const counters=document.querySelectorAll(".counter");

counters.forEach(counter=>{

const target=+counter.dataset.target;

let count=0;

const update=()=>{

count += target/120;

if(count < target){

counter.innerText=Math.floor(count);

requestAnimationFrame(update);

}else{

counter.innerText=target;

}

};

update();

});
/* API BASE URL */

const BASE_URL="http://localhost:5000/api";

/* SIGNUP */

async function signupUser(){

const name=document.getElementById("name").value;
const email=document.getElementById("email").value;
const password=document.getElementById("password").value;

try{

const res=await fetch(BASE_URL+"/signup",{

method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({name,email,password})

});

const data=await res.json();

if(data.success){

alert("Signup successful");
window.location.href="login.html";

}else{

alert(data.message);

}

}catch(e){

alert("Server error");

}

}

/* LOGIN */

async function loginUser(){

const email=document.getElementById("email").value;
const password=document.getElementById("password").value;

try{

const res=await fetch(BASE_URL+"/login",{

method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({email,password})

});

const data=await res.json();

if(data.success){

localStorage.setItem("token",data.token);

window.location.href="dashboard.html";

}else{

alert("Invalid credentials");

}

}catch(e){

alert("Server error");

}

}

/* PROTECT DASHBOARD */

if(window.location.pathname.includes("dashboard.html")){

if(!localStorage.getItem("token")){

window.location.href="login.html";

}

}