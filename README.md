# TVI Football Index

This project aims to create a Python library for calculating the Tactical Versatility Index (TVI) in football. The TVI is a metric that quantifies a player's or team's ability to perform different actions in various zones of the pitch.

## Features

*   **F24 Parser**: A module to parse and process F24 XML data from Wyscout.
*   **TVI Calculator**: A module to calculate the TVI for players based on their in-game actions.
*   **Customizable Zone Grid**: The flexibility to define custom pitch zones for analysis.

## Getting Started

### Prerequisites

*   Python 3.8 or higher
*   pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/TVI_footballindex.git
    cd TVI_footballindex
    ```

2.  **Install dependencies:**
    The required Python packages are listed in `requirements.txt`. You can install them using pip:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

The `examples` folder contains a script to demonstrate how to use the library.

1.  **Download the data:**
    The parsing functions are all based on OPTA data, but you can call the tvi functions with a custom dataframe.

2.  **Run the example script:**
    The `calculate_tvi_from_library.py` script in the `examples` folder shows how to use the library to calculate the TVI for players. You can run it from the root directory of the project:
    ```bash
    python examples/calculate_tvi_from_library.py
    ```

## Future Plans

This project is currently under development. The goal is to package it as a proper Python library and publish it on PyPI. This will allow for easy installation via pip and a more streamlined user experience.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.