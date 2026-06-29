// Лёгкий эффект печатной машинки в hero (без внешних библиотек).
(function () {
    var phrases = ['Маникюр', 'Педикюр', 'Дизайн ногтей', 'Наращивание', 'Покрытие гель-лаком'];
    var el = document.getElementById('typewriter');
    if (!el) return;
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        el.textContent = phrases[0];
        return;
    }
    var pi = 0, ci = 0, deleting = false;
    function tick() {
        var cur = phrases[pi];
        if (!deleting) {
            el.textContent = cur.substring(0, ci + 1);
            ci++;
            if (ci === cur.length) { setTimeout(function () { deleting = true; tick(); }, 2000); return; }
        } else {
            el.textContent = cur.substring(0, ci - 1);
            ci--;
            if (ci === 0) { deleting = false; pi = (pi + 1) % phrases.length; }
        }
        setTimeout(tick, deleting ? 50 : 110);
    }
    tick();
})();
