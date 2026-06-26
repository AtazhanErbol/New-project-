document.addEventListener('DOMContentLoaded', function() {
    // NAVBAR
    var navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            navbar.classList.toggle('scrolled', window.scrollY > 50);
        });
    }
    var burger = document.getElementById('burger');
    var mobileMenu = document.getElementById('mobileMenu');
    if (burger && mobileMenu) {
        burger.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            var open = mobileMenu.classList.contains('active');
            document.body.classList.toggle('no-scroll', open);
            if (navbar) navbar.classList.toggle('menu-open', open);
        });
        var mlinks = mobileMenu.querySelectorAll('a');
        for (var i = 0; i < mlinks.length; i++) {
            mlinks[i].addEventListener('click', function() {
                mobileMenu.classList.remove('active');
                burger.classList.remove('active');
                document.body.classList.remove('no-scroll');
                if (navbar) navbar.classList.remove('menu-open');
            });
        }
    }

    // SMOOTH SCROLL for all anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    for (var i = 0; i < anchorLinks.length; i++) {
        anchorLinks[i].addEventListener('click', function(e) {
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                var offset = 80;
                var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
                window.scrollTo({ top: top, behavior: 'smooth' });
            }
        });
    }

    // SERVICE FILTERS
    var filterBtns = document.querySelectorAll('[data-filter]');
    for (var i = 0; i < filterBtns.length; i++) {
        filterBtns[i].addEventListener('click', function() {
            var allBtns = document.querySelectorAll('[data-filter]');
            for (var j = 0; j < allBtns.length; j++) allBtns[j].classList.remove('active');
            this.classList.add('active');
            var f = this.getAttribute('data-filter');
            var cards = document.querySelectorAll('.service-card');
            for (var k = 0; k < cards.length; k++) {
                var cat = cards[k].getAttribute('data-category');
                cards[k].style.display = (f === 'all' || cat === f) ? '' : 'none';
            }
        });
    }

    // GALLERY FILTERS (category + master)
    var galBtns = document.querySelectorAll('[data-gallery-filter]');
    for (var i = 0; i < galBtns.length; i++) {
        galBtns[i].addEventListener('click', function() {
            var allBtns = document.querySelectorAll('[data-gallery-filter]');
            for (var j = 0; j < allBtns.length; j++) allBtns[j].classList.remove('active');
            this.classList.add('active');
            var f = this.getAttribute('data-gallery-filter');
            var items = document.querySelectorAll('.gallery__item');
            for (var k = 0; k < items.length; k++) {
                var cat = items[k].getAttribute('data-gallery-category');
                var master = items[k].getAttribute('data-gallery-master');
                var show = false;
                if (f === 'all') { show = true; }
                else if (f.indexOf('master-') === 0) { show = (master === f.replace('master-', '')); }
                else { show = (cat === f); }
                items[k].style.display = show ? '' : 'none';
            }
        });
    }

    // SERVICE CARD -> BOOKING scroll
    var serviceBtns = document.querySelectorAll('.service-card__btn');
    for (var i = 0; i < serviceBtns.length; i++) {
        serviceBtns[i].addEventListener('click', function() {
            var sid = this.getAttribute('data-service-id');
            var radios = document.querySelectorAll('.booking-service-card__input');
            for (var j = 0; j < radios.length; j++) {
                if (radios[j].value === sid) radios[j].checked = true;
            }
            var booking = document.getElementById('booking');
            if (booking) {
                var top = booking.getBoundingClientRect().top + window.pageYOffset - 80;
                window.scrollTo({ top: top, behavior: 'smooth' });
            }
        });
    }

    // MULTI-STEP FORM
    var steps = document.querySelectorAll('.booking-step');
    var pSteps = document.querySelectorAll('.booking-progress-step');
    function showStep(n) {
        for (var i = 0; i < steps.length; i++) steps[i].classList.remove('active');
        for (var i = 0; i < pSteps.length; i++) {
            pSteps[i].classList.remove('active', 'completed');
            var sn = parseInt(pSteps[i].getAttribute('data-step'));
            if (sn < n) pSteps[i].classList.add('completed');
            if (sn === n) pSteps[i].classList.add('active');
        }
        var target = document.querySelector('.booking-step[data-step="' + n + '"]');
        if (target) target.classList.add('active');
    }

    // FILTER SERVICES BY SELECTED MASTER
    function filterServicesByMaster(masterId) {
        fetch('/booking/services/?master_id=' + masterId)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var allowedIds = (data.services || []).map(function(s) { return String(s.id); });
                var cards = document.querySelectorAll('#servicesList .booking-service-card');
                for (var i = 0; i < cards.length; i++) {
                    var input = cards[i].querySelector('.booking-service-card__input');
                    var allowed = allowedIds.indexOf(input.value) !== -1;
                    cards[i].style.display = allowed ? '' : 'none';
                    if (!allowed && input.checked) input.checked = false;
                }
            })
            .catch(function() {});
    }

    var masterRadios = document.querySelectorAll('.master-radio');
    for (var i = 0; i < masterRadios.length; i++) {
        masterRadios[i].addEventListener('change', function() {
            if (this.checked) filterServicesByMaster(this.value);
        });
    }

    var nextBtns = document.querySelectorAll('.booking-next');
    for (var i = 0; i < nextBtns.length; i++) {
        nextBtns[i].addEventListener('click', function() {
            var cur = parseInt(this.closest('.booking-step').getAttribute('data-step'));
            var nxt = parseInt(this.getAttribute('data-next'));
            if (cur === 1) {
                var checked = document.querySelector('.master-radio:checked');
                if (!checked) { alert('Выберите мастера'); return; }
                document.getElementById('selectedMasterId').value = checked.value;
            }
            if (cur === 2) {
                var svc = document.querySelector('.booking-service-card__input:checked');
                if (!svc) { alert('Выберите услугу'); return; }
            }
            if (cur === 3) {
                var slot = document.getElementById('selectedSlotId');
                if (!slot || !slot.value) { alert('Выберите время'); return; }
            }
            showStep(nxt);
        });
    }
    var prevBtns = document.querySelectorAll('.booking-prev');
    for (var i = 0; i < prevBtns.length; i++) {
        prevBtns[i].addEventListener('click', function() { showStep(parseInt(this.getAttribute('data-prev'))); });
    }

    // FLATPICKR
    var cal = document.getElementById('flatpickr');
    if (cal && typeof flatpickr !== 'undefined') {
        flatpickr(cal, {
            locale: 'ru', minDate: 'today', dateFormat: 'Y-m-d',
            onChange: function(sel, dateStr) { loadSlots(dateStr); }
        });
    }

    function loadSlots(date) {
        var c = document.getElementById('slotsContainer');
        if (!c) return;
        c.innerHTML = '<p class="booking-slots__hint">Загрузка...</p>';
        var masterId = document.getElementById('selectedMasterId').value;
        var svcInput = document.querySelector('.booking-service-card__input:checked');
        var url = '/booking/slots/?date=' + date;
        if (masterId) url += '&master_id=' + masterId;
        if (svcInput) url += '&service_id=' + svcInput.value;
        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                document.getElementById('selectedSlotId').value = '';
                if (!data.slots || !data.slots.length) {
                    c.innerHTML = '<p class="booking-slots__hint">Нет свободных слотов</p>';
                    return;
                }
                var html = '';
                for (var i = 0; i < data.slots.length; i++) {
                    var s = data.slots[i];
                    var cls = 'slot-btn';
                    var attrs = '';
                    if (s.booked) { cls += ' slot-btn--booked'; attrs = 'disabled title="Уже занято"'; }
                    else if (!s.available) { cls += ' slot-btn--unavailable'; attrs = 'disabled title="Недостаточно времени для услуги"'; }
                    html += '<button type="button" class="' + cls + '" data-slot-id="' + s.id + '" ' + attrs + '>' + s.time + '</button>';
                }
                c.innerHTML = html;
                var btns = c.querySelectorAll('.slot-btn:not([disabled])');
                for (var i = 0; i < btns.length; i++) {
                    btns[i].addEventListener('click', function() {
                        var all = c.querySelectorAll('.slot-btn');
                        for (var j = 0; j < all.length; j++) all[j].classList.remove('active');
                        this.classList.add('active');
                        document.getElementById('selectedSlotId').value = this.getAttribute('data-slot-id');
                    });
                }
            })
            .catch(function() { c.innerHTML = '<p class="booking-slots__hint">Ошибка загрузки</p>'; });
    }

    // PHONE MASK
    var phone = document.querySelector('input[name="client_phone"]');
    if (phone) {
        phone.addEventListener('input', function(e) {
            var input = e.target;
            var digitsBefore = input.value.slice(0, input.selectionStart).replace(/\D/g, '').length;
            var v = input.value.replace(/\D/g, '');
            if (!v) { input.value = ''; return; }
            if (!v.startsWith('7')) v = '7' + v;
            v = v.substring(0, 11);

            var formatted = '+7';
            if (v.length > 1) formatted += ' (' + v.substring(1, 4);
            if (v.length >= 4) formatted += ') ' + v.substring(4, 7);
            if (v.length >= 7) formatted += '-' + v.substring(7, 9);
            if (v.length >= 9) formatted += '-' + v.substring(9, 11);
            input.value = formatted;

            var pos = 0, seen = 0;
            for (; pos < formatted.length && seen < digitsBefore; pos++) {
                if (/\d/.test(formatted[pos])) seen++;
            }
            input.setSelectionRange(pos, pos);
        });
    }
    var cards = document.querySelectorAll('.service-card');
    for (var i = 0; i < cards.length; i++) {
        cards[i].addEventListener('mousemove', function(e) {
            var rect = this.getBoundingClientRect();
            var x = e.clientX - rect.left;
            var y = e.clientY - rect.top;
            var cx = rect.width / 2;
            var cy = rect.height / 2;
            var rx = (y - cy) / cy * -5;
            var ry = (x - cx) / cx * 5;
            this.querySelector('.service-card__inner').style.transform = 'rotateX(' + rx + 'deg) rotateY(' + ry + 'deg)';
        });
        cards[i].addEventListener('mouseleave', function() {
            this.querySelector('.service-card__inner').style.transform = '';
        });
    }
});
