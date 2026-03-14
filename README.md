# ComfyUI-ImgSlider

**Get a shareable link for your before/after comparisons.** Publish image sliders directly from ComfyUI to [imgslider.com](https://imgslider.com).

<img width="500" alt="Image" src="https://github.com/user-attachments/assets/26851a72-7af3-4490-8a4f-6697f908d2b2" />

<img width="500" alt="Image" src="https://github.com/user-attachments/assets/290693bf-941c-4e77-8b41-46c064a3551c" />

Example - https://imgslider.com/25895cec-4656-40e9-bdf8-31ea08d27cf6

## Why ImgSlider?

Other comparison nodes only work locally. **ImgSlider gives you a link you can share anywhere** - Reddit, Discord, your portfolio, client reviews. One click to publish, instant shareable URL.

## Features

- **Shareable Links**: Publish and get a URL to share your comparison anywhere
- **No Account Required**: Create sliders instantly (expire after 30 days)
- **Inline Preview**: See the comparison directly in your workflow
- **One-Click Publishing**: Toggle publish, run workflow, get link

## Installation

### ComfyUI Manager (Recommended)

1. Open ComfyUI Manager
2. Click "Install Custom Nodes"
3. Search for "ImgSlider" or "Image Compare"
4. Install and restart ComfyUI

### Manual Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/imgslider/ComfyUI-ImgSlider.git
pip install -r ComfyUI-ImgSlider/requirements.txt
```

## Usage

1. Add **Image Compare (ImgSlider)** node to your workflow
2. Connect your images to **Image A** and **Image B**
3. Toggle **Publish** to YES
4. Run workflow
5. Copy the shareable link from the console output

### Anonymous (No Account)

Just toggle Publish and run. You'll get a shareable link instantly.

- Free, no signup
- Links expire after 30 days
- 20 sliders/day limit

### With API Key (Permanent and Editable)

1. Sign in at [imgslider.com](https://imgslider.com)
2. Go to Dashboard → API Tokens
3. Create a token and paste it in the node
4. Your sliders are now permanent and editable

| Feature | Anonymous | With API Key |
|---------|-----------|--------------|
| Shareable links | ✓ | ✓ |
| Editable | ✗ | ✓ |
| Permanent | 30 days | Forever |
| Rate limit | 20/day | 200/month |
| Max file size | 50MB/image | 50MB/image |

## Node Inputs

| Input | Type | Description |
|-------|------|-------------|
| image_a | IMAGE | First image (left side of slider) |
| image_b | IMAGE | Second image (right side of slider) |
| title | STRING | Optional title for the slider |
| api_key | STRING | Optional API key for permanent sliders |
| publish | BOOLEAN | Toggle to publish and get shareable link |

## Example Workflow

```
[Image A] ──┐
            ├──> [Image Compare (ImgSlider)] ──> Shareable URL
[Image B] ──┘         (publish: YES)
```

## Use Cases

- **Share AI generations**: Compare models, prompts, or settings with others
- **Client reviews**: Send a link instead of uploading multiple images
- **Portfolio**: Showcase before/after transformations
- **Social Networks**: Share comparisons on Reddit, Discord, X

## License

MIT License - See [LICENSE](LICENSE) for details.

## Links

- [imgslider.com](https://imgslider.com)
- [GitHub Issues](https://github.com/imgslider/ComfyUI-ImgSlider/issues)
