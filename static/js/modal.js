document.addEventListener('DOMContentLoaded', function () {
    var params = new URLSearchParams(window.location.search);
    var overlay = document.getElementById('bookingModal');
    if (params.get('booking') === 'ok') {
        if (overlay) { overlay.classList.add('active'); overlay.style.display = 'flex'; }
        window.history.replaceState(null, null, window.location.pathname + '#booking');
    }
    var closeBtn = document.getElementById('modalClose');
    if (closeBtn) {
        closeBtn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            overlay.classList.remove('active');
            overlay.style.display = 'none';
        });
    }
    if (overlay) {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) {
                this.classList.remove('active');
                this.style.display = 'none';
            }
        });
        var modalBtns = overlay.querySelectorAll('.btn');
        for (var i = 0; i < modalBtns.length; i++) {
            modalBtns[i].addEventListener('click', function () {
                overlay.classList.remove('active');
                overlay.style.display = 'none';
            });
        }
    }
});
