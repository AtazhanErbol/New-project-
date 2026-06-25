AOS.init({ duration: 800, easing: 'ease-out-cubic', once: true, disable: window.matchMedia('(prefers-reduced-motion: reduce)').matches });

const swiper = new Swiper('.reviews-swiper', {
    slidesPerView: 1, spaceBetween: 24,
    autoplay: { delay: 5000, disableOnInteraction: false, pauseOnMouseEnter: true },
    pagination: { el: '.swiper-pagination', clickable: true },
    breakpoints: { 768: { slidesPerView: 2 }, 1024: { slidesPerView: 3 } }
});

const lightbox = GLightbox({ selector: '.glightbox' });

function initCounters() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-count'));
                let current = 0;
                const increment = target / 60;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) { el.textContent = target.toLocaleString(); clearInterval(timer); }
                    else { el.textContent = Math.floor(current).toLocaleString(); }
                }, 30);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });
    document.querySelectorAll('.counter__number').forEach(c => observer.observe(c));
}
initCounters();
