// Auto-dismiss messages
setTimeout(() => {
  document.querySelectorAll('.msg').forEach(m => {
    m.style.transition = 'opacity 0.5s';
    m.style.opacity = '0';
    setTimeout(() => m.remove(), 500);
  });
}, 4000);
