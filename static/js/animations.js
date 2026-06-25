gsap.registerPlugin(ScrollTrigger, TextPlugin);

const typewriterPhrases = ['Маникюр', 'Педикюр', 'Дизайн ногтей', 'Наращивание', 'Покрытие гель-лаком'];
let phraseIndex = 0, charIndex = 0, isDeleting = false;

function typewrite() {
    const el = document.getElementById('typewriter');
    if (!el) return;
    const current = typewriterPhrases[phraseIndex];
    if (!isDeleting) {
        el.textContent = current.substring(0, charIndex + 1);
        charIndex++;
        if (charIndex === current.length) { setTimeout(() => { isDeleting = true; typewrite(); }, 2000); return; }
    } else {
        el.textContent = current.substring(0, charIndex - 1);
        charIndex--;
        if (charIndex === 0) { isDeleting = false; phraseIndex = (phraseIndex + 1) % typewriterPhrases.length; }
    }
    setTimeout(typewrite, isDeleting ? 50 : 100);
}
typewrite();

gsap.to('.hero', { scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }, backgroundPosition: '50% 100%', ease: 'none' });

document.querySelectorAll('.step__number svg circle').forEach(circle => {
    const r = circle.r.baseVal.value;
    const c = 2 * Math.PI * r;
    circle.style.strokeDasharray = c;
    circle.style.strokeDashoffset = c;
    gsap.to(circle, { scrollTrigger: { trigger: circle.closest('.step'), start: 'top 80%' }, strokeDashoffset: 0, duration: 1, ease: 'power2.out' });
});
