import React, { useEffect } from "react";
import { addPropertyControls, ControlType } from "framer";
import RiveComponent from "https://rive.app/api/s/_I0fWHYbPEG9ateRcfkkHg/framer/";

export function MyRiveComponent(props) {
    useEffect(() => {
        // Any side effects can go here
    }, []);

    return <RiveComponent {...props} />;
}

// Add property controls
addPropertyControls(MyRiveComponent, {
    someControl: {
        type: ControlType.Number,
        title: "Example",
        defaultValue: 50,
    },
});


/**
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight any-prefer-fixed
 */
// export RiveComponent as React.ComponentType
RiveComponent.displayName = componentName

addPropertyControls(RiveComponent, propertyControls)

const RiveFramerWrapper = () => {
    useEffect(() => {
        const riveInstance = RiveComponent.getRive();
        
        if (riveInstance) {
            console.log('Rive instance loaded:', riveInstance);
    
            const inputs = riveInstance.stateMachineInputs(0);
            console.log('State machine inputs:', inputs);
    
            inputs.forEach(input => {
                console.log('Input Name:', input.name, ' | Input Type:', input.type);
            });
        } else {
            console.warn('Rive instance not loaded');
        }
    }, []);

    return <RiveComponent />;
};

export default RiveFramerWrapper;
