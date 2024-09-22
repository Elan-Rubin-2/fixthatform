import "./sandbox/src/styles.css";
import RiveCanvas  from "./node_modules/@rive-app/canvas-advanced-single";
// import { registerListeners } from "./registerListeners";

async function main() {
  // Load in Rive and create instances
  const rive = await RiveCanvas();
  const riveFileBytes = await (
    await fetch(new Request("./facial_expression_demo(3).riv"))
  ).arrayBuffer();
  const riveFile = await rive.load(new Uint8Array(riveFileBytes));
  const artboard = riveFile.artboardByName("Artboard");
  const stateMachine = new rive.StateMachineInstance(
    artboard.stateMachineByIndex(0),
    artboard
  );
  const volumeInput = stateMachine.input(1).asNumber();
  console.log(volumeInput);

  const canvas = document.querySelector("canvas");
  const renderer = rive.makeRenderer(canvas);


  const smileInput = stateMachine.inputs.find(input => input.name === 'Smile');
  const sadInput = stateMachine.inputs.find(input => input.name === 'Sad');
  const happyInput = stateMachine.inputs.find(input => input.name === 'Happy');
  const surpriseInput = stateMachine.inputs.find(input => input.name === 'Surprise');
  const neutralInput = stateMachine.inputs.find(input => input.name === 'Neutral');

        // Function to update Rive inputs
    function updateRiveInput(input, value) {
        if (input && input instanceof rive.NumberInput) {
            input.value = value;
        }
    }

    // Add event listeners to sliders
    document.getElementById('smile').addEventListener('input', (e) => {
        updateRiveInput(smileInput, e.target.value / 100);
    });

    document.getElementById('sad').addEventListener('input', (e) => {
        updateRiveInput(sadInput, e.target.value / 100);
    });

    document.getElementById('happy').addEventListener('input', (e) => {
        updateRiveInput(happyInput, e.target.value / 100);
    });

    document.getElementById('surprise').addEventListener('input', (e) => {
        updateRiveInput(surpriseInput, e.target.value / 100);
    });

    document.getElementById('neutral').addEventListener('input', (e) => {
        updateRiveInput(neutralInput, e.target.value / 100);
    });

  // registerListeners({
  //   canvas,
  //   artboard,
  //   stateMachines: [stateMachine],
  //   renderer,
  //   rive,
  //   fit: rive.Fit.contain,
  //   alignment: rive.Alignment.center
  // });

  // Render loop
  let lastTime = 0;
  function renderLoop(time) {
    if (!lastTime) {
      lastTime = time;
    }
    const elapsedTimeInMS = time - lastTime;
    const elapsedTimeInSeconds = elapsedTimeInMS / 1000;
    lastTime = time;

    // Clear the canvas
    renderer.clear();

    stateMachine.advance(elapsedTimeInSeconds);
    artboard.advance(elapsedTimeInSeconds);
    renderer.save();
    renderer.align(
      rive.Fit.contain,
      rive.Alignment.center,
      {
        minX: 0,
        minY: 0,
        maxX: canvas.width,
        maxY: canvas.height
      },
      artboard.bounds
    );
    // Draw the artboard to the canvas
    artboard.draw(renderer);
    renderer.restore();

    rive.requestAnimationFrame(renderLoop);
  }
  rive.requestAnimationFrame(renderLoop);


}
main();