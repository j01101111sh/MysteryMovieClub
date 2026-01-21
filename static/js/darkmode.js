(() => {
  const getStoredTheme = () => {
    try {
      return localStorage.getItem('theme');
    } catch {
      return null;
    }
  }
  const setStoredTheme = theme => {
    try {
      localStorage.setItem('theme', theme);
    } catch {
      // Ignore errors if localStorage is not available.
    }
  }

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme()
    if (storedTheme) {
      return storedTheme
    }
    return 'dark'
  }

  const setTheme = theme => {
    document.documentElement.setAttribute('data-bs-theme', theme)
  }

  setTheme(getPreferredTheme())

  // Update functionality when DOM is loaded
  window.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
      // Update icon/text based on current theme if you want logic here
      toggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setStoredTheme(newTheme);
        setTheme(newTheme);
      });
    }
  });
})()
