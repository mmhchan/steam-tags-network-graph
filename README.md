# Steam Tag Network Graph Builder

An interactive web application that visualizes the relationships between Steam games based on their tags. This tool allows users to see which games "cluster" together and which tags act as the strongest bridges in a specific set of titles.

**Live App:** [steam-tags-network-graph.streamlit.app](https://steam-tags-network-graph.streamlit.app/)

## Background
This project is an evolution of the data visualization work I previously performed in Jupyter Notebooks for the **GameDiscoverCo newsletter** during Steam Next Fest reporting. My goal was to turn those static analytical scripts into a dynamic, user-friendly tool that anyone can use to explore Steam metadata.

## Features
- **Interactive Graph:** Drag, zoom, and explore nodes representing games and tags.
- **Custom Uploads:** Upload your own CSV to visualize specific datasets.
- **Dynamic Physics:** Adjust node spacing, gravitational constant, and colors in real-time.
- **High-Res Export:** Export your network as a crisp, 3x resolution PNG for use in reports or articles.

## How to Use
1. **Visit the App:** Launch the tool via the Streamlit link above.
2. **Use Sample Data:** The app loads with a built-in dataset by default.
3. **Upload Your Own:** - Download the [sample.csv](./data/sample.csv) from the `data` folder in this repo to see the required format.
   - The CSV should contain columns: `Game`, `Tag 1`, `Tag 2`, `Tag 3`, `Tag 4`, and `Tag 5`.
   - Upload your file via the sidebar to generate a custom network.

## Exporting & Limitations
I have implemented a **"Save 3x High-Res PNG"** function that forces the browser to re-render the network at a higher density for professional clarity.

**Note on Game Labels:**
Due to how `Pyvis` handles canvas rendering, game titles (labels) are not drawn. 

**My current workflow:** I personally import the high-res PNG into **Affinity Designer** to manually add the game name labels and final annotations before publishing. You can use similar tools like Photoshop, Figma, or Canva for this step.

### Contributing
If you are a developer and know a way to force `Pyvis` to include the labels in the canvas export without compromising the interactive layout, I would be happy to see a Pull Request or a suggestion!

## Project Structure
- `src/app.py`: The Streamlit application logic.
- `data/sample.csv`: Example dataset for user testing.
- `requirements.txt`: Python dependencies.