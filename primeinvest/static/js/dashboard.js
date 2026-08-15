(function () {
  'use strict';

  const body = document.body;
  const sidebar = document.getElementById('dashboard-sidebar');
  const openButton = document.querySelector('[data-sidebar-open]');
  const closeButtons = document.querySelectorAll('[data-sidebar-close]');

  function setSidebar(open) {
    body.classList.toggle('sidebar-is-open', open);
    if (openButton) openButton.setAttribute('aria-expanded', String(open));
    if (sidebar) sidebar.setAttribute('aria-hidden', String(!open && window.innerWidth < 1024));
  }

  if (openButton) openButton.addEventListener('click', function () { setSidebar(true); });
  closeButtons.forEach(function (button) {
    button.addEventListener('click', function () { setSidebar(false); });
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') setSidebar(false);
  });

  window.addEventListener('resize', function () {
    if (sidebar && window.innerWidth >= 1024) {
      body.classList.remove('sidebar-is-open');
      sidebar.removeAttribute('aria-hidden');
      if (openButton) openButton.setAttribute('aria-expanded', 'false');
    }
  });

  document.querySelectorAll('[data-copy-target]').forEach(function (button) {
    button.addEventListener('click', async function () {
      const input = document.getElementById(button.dataset.copyTarget);
      if (!input) return;

      const originalText = button.textContent;
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(input.value);
        } else {
          input.select();
          document.execCommand('copy');
          window.getSelection().removeAllRanges();
        }
        button.textContent = 'Address copied';
      } catch (error) {
        input.select();
        button.textContent = 'Press Ctrl+C';
      }
      window.setTimeout(function () { button.textContent = originalText; }, 2200);
    });
  });

  document.querySelectorAll('[data-dismiss-message]').forEach(function (button) {
    button.addEventListener('click', function () { button.parentElement.remove(); });
  });
})();
