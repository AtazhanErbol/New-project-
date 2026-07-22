const dot = document.getElementById('cursorDot');
const outline = document.getElementById('cursorOutline');
if (dot && outline && window.innerWidth > 768) {
    let mx = 0, my = 0, ox = 0, oy = 0;
    document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; dot.style.left = mx - 4 + 'px'; dot.style.top = my - 4 + 'px'; });
    (function animate() { ox += (mx - ox) * 0.15; oy += (my - oy) * 0.15; outline.style.left = ox - 16 + 'px'; outline.style.top = oy - 16 + 'px'; requestAnimationFrame(animate); })();
    document.querySelectorAll('a, button, .service-card, .gallery__item').forEach(el => {
        el.addEventListener('mouseenter', () => { outline.style.width = '48px'; outline.style.height = '48px'; outline.style.borderColor = '#EBC8CE'; dot.style.transform = 'scale(1.5)'; });
        el.addEventListener('mouseleave', () => { outline.style.width = '32px'; outline.style.height = '32px'; outline.style.borderColor = '#B76E79'; dot.style.transform = 'scale(1)'; });
    });
}
