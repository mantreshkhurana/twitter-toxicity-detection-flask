const toggleSwitch = document.querySelector('#toggle');
const body = document.querySelector('body');

function setTheme(theme) {
  if (theme === 'dark') {
    body.classList.add('dark');
    body.classList.remove('light');
    toggleSwitch.checked = true;
  } else {
    body.classList.add('light');
    body.classList.remove('dark');
    toggleSwitch.checked = false;
  }
}

function toggleTheme() {
  if (toggleSwitch.checked) {
    setTheme('dark');
    localStorage.setItem('theme', 'dark');
  } else {
    setTheme('light');
    localStorage.setItem('theme', 'light');
  }
}

toggleSwitch.addEventListener('change', toggleTheme);

const storedTheme = localStorage.getItem('theme');
if (storedTheme) {
  setTheme(storedTheme);
}
