function openNav() {
  const nav = document.querySelector(".nav");
  if (nav) nav.classList.add('opennav');
}

function closeNav() {
  const nav = document.querySelector(".nav");
  if (nav) nav.classList.remove('opennav');
}

function openHomeNav() {
  const nav = document.querySelector(".nav-links2");
  if (nav) nav.style.width = "25rem";
}

function closeHomeNav() {
  const nav = document.querySelector(".nav-links2");
  if (nav) nav.style.width = "0";
}



function myFunction() {
  /* Get the text field */
  var copyText = document.getElementById("myInput");

  /* Select the text field */
  copyText.select();
  copyText.setSelectionRange(0, 99999); /* For mobile devices */

  /* Copy the text inside the text field */
  document.execCommand("copy");

  /* Alert the copied text */
  alert("Copied the text: " + copyText.value);
}

if (window.Swiper && document.querySelector('.mySwiper')) {
  new Swiper(".mySwiper", {
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },

  loop: true,
  slidesPerView: 1,
  spaceBetween: 20,

  breakpoints: {
    640: {
      slidesPerView: 2,
      spaceBetween: 30,
    },
    768: {
      slidesPerView: 3,
      spaceBetween: 30,
    },
  },
  });
}

// let header = document.querySelector(".nav");
// console.log(header);


document.onscroll = function() {scrollFunction()};

function scrollFunction() {
  const navbar = document.getElementById("navbar");
  if (!navbar) return;

  if (document.body.scrollTop > 5 || document.documentElement.scrollTop > 5) {
    navbar.style.backgroundColor = "rgba(10, 14, 32, 0.96)";
  } else {
    navbar.style.backgroundColor = "transparent";
  }
}



// Hide and show password
const password = document.querySelector('#password');
const password2 = document.querySelector('#password2');

const togglePassword = document.querySelector('#togglePassword');
const togglePassword2 = document.querySelector('#togglePassword2');


if (togglePassword && password) togglePassword.addEventListener('click', function (e) {
  const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    // toggle the eye / eye slash icon
    // this.classList.toggle('bi-eye bi-eye);
    if(togglePassword.classList.contains("bi-eye")) {
      togglePassword.classList.remove('bi-eye')
      togglePassword.classList.add('bi-eye-slash')
    } else {
      togglePassword.classList.add('bi-eye')
      togglePassword.classList.remove('bi-eye-slash')
    }
});

if (togglePassword2 && password2) togglePassword2.addEventListener('click', function (e) {
  const type = password2.getAttribute('type') === 'password' ? 'text' : 'password';
    password2.setAttribute('type', type);
    // toggle the eye / eye slash icon
    if(togglePassword2.classList.contains("bi-eye")) {
      togglePassword2.classList.remove('bi-eye')
      togglePassword2.classList.add('bi-eye-slash')
    } else {
      togglePassword2.classList.add('bi-eye')
      togglePassword2.classList.remove('bi-eye-slash')
    }
});
