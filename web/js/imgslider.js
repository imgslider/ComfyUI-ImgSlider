// ImgSlider ComfyUI Frontend
// Hover-based before/after comparison slider

import { app } from "../../../scripts/app.js";

// Helper to build image URL from ComfyUI file reference
function getImageUrl(imageInfo) {
    const params = new URLSearchParams({
        filename: imageInfo.filename,
        type: imageInfo.type || "temp",
        subfolder: imageInfo.subfolder || ""
    });
    return `/view?${params.toString()}`;
}

// Register the custom extension
app.registerExtension({
    name: "ImgSlider.Node",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ImgSlider") {

            const onExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function(message) {
                if (onExecuted) {
                    onExecuted.apply(this, arguments);
                }

                if (message && message.slider_images && message.slider_images.length >= 2) {
                    const sliderUrl = message.slider_url ? message.slider_url[0] : "";
                    const sliderError = message.slider_error ? message.slider_error[0] : "";

                    const sliders = [{
                        beforeUrl: getImageUrl(message.slider_images[0]),
                        afterUrl: getImageUrl(message.slider_images[1]),
                    }];

                    this.updateSliderWidget(sliders, sliderUrl, sliderError);
                }
            };

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }

                this.sliderContainer = document.createElement("div");
                this.sliderContainer.className = "imgslider-container";
                this.sliderContainer.style.cssText = `
                    width: 100%;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                `;

                this.addDOMWidget("slider_preview", "customSlider", this.sliderContainer, {
                    serialize: false,
                    hideOnZoom: false,
                    getValue: () => null,
                    setValue: () => {},
                });
            };

            nodeType.prototype.updateSliderWidget = function(sliders, sliderUrl, sliderError) {
                if (!this.sliderContainer) return;

                this.sliderContainer.innerHTML = "";

                // URL bar at top if we have a URL
                if (sliderUrl) {
                    const urlBar = document.createElement("div");
                    urlBar.style.cssText = `
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        padding: 8px 12px;
                        border-radius: 6px;
                        margin-bottom: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        gap: 8px;
                    `;
                    urlBar.innerHTML = `
                        <span style="color: white; font-size: 11px; font-weight: 500;">✓ Published</span>
                        <a href="${sliderUrl}" target="_blank" style="
                            color: white;
                            font-size: 11px;
                            text-decoration: none;
                            background: rgba(255,255,255,0.2);
                            padding: 4px 8px;
                            border-radius: 4px;
                            flex: 1;
                            text-align: center;
                            overflow: hidden;
                            text-overflow: ellipsis;
                            white-space: nowrap;
                        ">${sliderUrl}</a>
                        <button onclick="navigator.clipboard.writeText('${sliderUrl}')" style="
                            background: rgba(255,255,255,0.2);
                            border: none;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            cursor: pointer;
                            font-size: 10px;
                        ">Copy</button>
                    `;
                    this.sliderContainer.appendChild(urlBar);
                } else if (sliderError) {
                    const errorBar = document.createElement("div");
                    errorBar.style.cssText = `
                        background: #ef4444;
                        padding: 8px 12px;
                        border-radius: 6px;
                        margin-bottom: 8px;
                        color: white;
                        font-size: 11px;
                    `;
                    errorBar.textContent = `Error: ${sliderError}`;
                    this.sliderContainer.appendChild(errorBar);
                }

                sliders.forEach((data) => {
                    const sliderWidget = createSlider(data);
                    this.sliderContainer.appendChild(sliderWidget);
                });

                app.graph.setDirtyCanvas(true, true);
            };
        }
    }
});

function createSlider(data) {
    const container = document.createElement("div");
    container.style.cssText = `
        position: relative;
        width: 100%;
        flex: 1;
        min-height: 100px;
        background: #0a0a0a;
        border-radius: 6px;
        overflow: hidden;
    `;

    // Image wrapper
    const imageWrapper = document.createElement("div");
    imageWrapper.style.cssText = `
        position: relative;
        width: 100%;
        height: 100%;
    `;

    // BEFORE image (base layer - shows on right side)
    const beforeImg = document.createElement("img");
    beforeImg.src = data.beforeUrl;
    beforeImg.draggable = false;
    beforeImg.style.cssText = `
        display: block;
        width: 100%;
        height: 100%;
        object-fit: contain;
        pointer-events: none;
    `;

    // AFTER clip container (shows on left side, clips the after image)
    const afterClip = document.createElement("div");
    afterClip.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 50%;
        height: 100%;
        overflow: hidden;
    `;

    // AFTER image
    const afterImg = document.createElement("img");
    afterImg.src = data.afterUrl;
    afterImg.draggable = false;
    afterImg.style.cssText = `
        display: block;
        height: 100%;
        max-width: none;
        object-fit: contain;
        pointer-events: none;
    `;

    // Match after image width to container
    const syncWidth = () => {
        afterImg.style.width = imageWrapper.offsetWidth + "px";
    };
    beforeImg.onload = syncWidth;

    // Divider line - 1px, 50% opacity white
    const divider = document.createElement("div");
    divider.style.cssText = `
        position: absolute;
        top: 0;
        left: 50%;
        width: 1px;
        height: 100%;
        background: rgba(255, 255, 255, 0.5);
        transform: translateX(-50%);
        z-index: 10;
        pointer-events: none;
    `;

    // Labels
    const beforeLabel = document.createElement("span");
    beforeLabel.textContent = "Before";
    beforeLabel.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.6);
        color: rgba(255, 255, 255, 0.8);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-family: system-ui, sans-serif;
        z-index: 5;
        pointer-events: none;
    `;

    const afterLabel = document.createElement("span");
    afterLabel.textContent = "After";
    afterLabel.style.cssText = `
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(0, 0, 0, 0.6);
        color: rgba(255, 255, 255, 0.8);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-family: system-ui, sans-serif;
        z-index: 5;
        pointer-events: none;
    `;

    // Assemble
    afterClip.appendChild(afterImg);
    imageWrapper.appendChild(beforeImg);
    imageWrapper.appendChild(afterClip);
    imageWrapper.appendChild(divider);
    imageWrapper.appendChild(beforeLabel);
    imageWrapper.appendChild(afterLabel);
    container.appendChild(imageWrapper);

    // Hover-based slider
    function updateSlider(clientX) {
        const rect = imageWrapper.getBoundingClientRect();
        let position = ((clientX - rect.left) / rect.width) * 100;
        position = Math.max(0, Math.min(100, position));

        afterClip.style.width = position + "%";
        divider.style.left = position + "%";
    }

    imageWrapper.addEventListener("mousemove", (e) => {
        updateSlider(e.clientX);
    });

    imageWrapper.addEventListener("mouseleave", () => {
        // Reset to 50% on mouse leave
        afterClip.style.width = "50%";
        divider.style.left = "50%";
    });

    // Touch support
    imageWrapper.addEventListener("touchmove", (e) => {
        e.preventDefault();
        if (e.touches[0]) {
            updateSlider(e.touches[0].clientX);
        }
    }, { passive: false });

    // Prevent canvas interaction
    container.addEventListener("mousedown", (e) => e.stopPropagation());
    container.addEventListener("pointerdown", (e) => e.stopPropagation());

    // Handle resize
    const resizeObserver = new ResizeObserver(syncWidth);
    resizeObserver.observe(imageWrapper);

    return container;
}
