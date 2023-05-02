const toggleSwitch = document.querySelector('#toggle');
const body = document.querySelector('body');

function toggleTheme() {
  if (toggleSwitch.checked) {
    body.classList.add('dark');
    body.classList.remove('light');
  } else {
    body.classList.add('light');
    body.classList.remove('dark');
  }
}

toggleSwitch.addEventListener('change', toggleTheme);

