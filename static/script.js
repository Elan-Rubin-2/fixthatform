const canvas = document.getElementById('riveCanvas');
const happinessSlider = document.getElementById('happiness');
const sadnessSlider = document.getElementById('sadness');

// Load the Rive file
const riveFilePath = 'facial_expression_demo(2).riv'; // Update with your .riv file path
const riveInstance = new rive.Rive({
    src: riveFilePath,
    canvas: canvas,
    autoplay: true,
});

// Update animation parameters based on slider values
function updateAnimation() {
    const happinessValue = parseFloat(happinessSlider.value);
    const sadnessValue = parseFloat(sadnessSlider.value);

    // Adjust these according to your animation parameter names
    riveInstance.setInput('happiness', happinessValue);
    riveInstance.setInput('sadness', sadnessValue);
}

// Event listeners for sliders
happinessSlider.addEventListener('input', updateAnimation);
sadnessSlider.addEventListener('input', updateAnimation);

// Start the animation loop
function render() {
    riveInstance.advance();
    requestAnimationFrame(render);
}

render();
