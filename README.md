<p align="center">
  <img src="https://studio.piktid.com/logo.svg" alt="SuperID by PiktID logo" width="150">
  </br>
  <h3 align="center"><a href="[https://studio.piktid.com](https://studio.piktid.com)">Background Generator by PiktID</a></h3>
</p>


# Background Generator 1.0.0
[![Official Website](https://img.shields.io/badge/Official%20Website-piktid.com-blue?style=flat&logo=world&logoColor=white)](https://piktid.com)
[![Discord Follow](https://dcbadge.vercel.app/api/server/FJU39e9Z4P?style=flat)](https://discord.com/invite/FJU39e9Z4P)

Background Generator is a GenAI tool designed to generate coherent backgrounds in images.
It allows you to upload a photo with a subject (object, product or a person) and generate a consistent background. The subject's illumination is also adjusted.

## About
Background generator utilizes generative AI to create authentic-looking backgrounds in photos. It's particularly useful for:

- <ins>Content creation</ins>: Create diverse representation in your visual content

## Getting Started

The following instructions suppose you have already installed a recent version of Python. To use any PiktID API, an access token is required.

> **Step 0** - Register <a href="https://studio.piktid.com">here</a>. 10 credits are given for free to all new users.

> **Step 1** - Clone the Eddie - Person Generator repository
```bash
# Installation commands
$ git clone https://github.com/piktid/background-generator.git
$ cd background-generator
```

> **Step 2** - Export your email and password as environmental variables
```bash
$ export EDDIE_EMAIL={Your email here}
$ export EDDIE_PASSWORD={Your password here}
```

> **Step 3** - Run the main function with a URL or local file path of the image and specify a text
```bash
# Using a URL with a text
$ python3 main.py --input_url 'your-url' --prompt ' .. commercial photo, red and white room lighting, depth of field，high level feeling，perfect lighting'

# Using a local file path with a text
$ python3 main.py --input_filepath '/path/to/your/image.jpg' --prompt ' .. commercial photo, depth of field，high level feeling，perfect lighting'
```

You can customize the generation parameters with the following options:

```bash
# Generate a variation with specific parameters
$ python3 main.py --input_filepath '/path/to/your/image.jpg' --seed 12345 --prompt_strength 0.8 --output_filepath '/path/to/save/output.jpg'
```

## Available Parameters

- **input_url**: URL of the image to process
- **input_filepath**: Local path to the image file
- **output_filepath**: Where to save the generated image
- **prompt**: Textual description of the background (REQUIRED)
- **prompt_strength**: How much the background follows the prompt (default: 1)
- **seed**: Random seed for reproducible results (default: random)

## Using Reference Images

You can also generate backgrounds based on reference images. There are two ways to provide a reference image:

```bash

# Using a local reference image file
$ python3 main.py --input_filepath '/path/to/your/image.jpg' --reference_path '/path/to/reference.jpg' --prompt 'a beer in ..' --seed 0 --prompt_strength 0.5

# Using a reference image URL
$ python3 main.py --input_filepath '/path/to/your/image.jpg' --reference_url 'https://example.com/reference-image.jpg' --prompt 'background is ..' --seed 0 --prompt_strength 0.3
```

The reference image will be used as a style guide for generating the background while maintaining consistency with the provided prompt.

## Resuming Operations

After uploading images, you'll receive unique IDs for both the input and reference images. You can use these IDs to resume or create new variations without uploading the images again:

```bash
$ python3 main.py --id_image "22FXXXXXX" --reference_name "0OqUXXXXXX" --prompt "shoes on a white room" --seed 0
```

This is particularly useful when:
- Working with the same images multiple times
- Creating variations of previous generations
- Saving bandwidth by avoiding re-uploads

## Contact
office@piktid.com
