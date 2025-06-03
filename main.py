import os
import sys
import argparse
from random import randint

from editBackground_utils import generate_background
from editBackground_api import start_call

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_url', help='Image file url', type=str, default='https://images.piktid.com/frontend/studio/superid/upscaler_sample/21z.png')
    parser.add_argument('--input_filepath', help='Input image file absolute path', type=str, default=None)
    parser.add_argument('--output_filepath', help='Output image file absolute path', type=str, default=None)

    # Image parameters
    parser.add_argument('--id_image', help='Target image id, it overwrites the input path', type=str, default=None)

    # Ref image parameters
    parser.add_argument('--reference_path', help='Reference file absolute path', type=str, default=None)
    parser.add_argument('--reference_url', help='Reference url, use only if no face path was given', type=str, default=None)
    parser.add_argument('--reference_name', help='Reference code name, it overwrites the reference path', type=str, default=None)

    # Random generation parameters
    parser.add_argument('--keyword', help='Generation keyword', type=str, default=None)
    parser.add_argument('--prompt', help='Generation prompt', type=str, default=None)
    parser.add_argument('--seed', help='Generation seed', type=int, default=randint(0, 100000))
    parser.add_argument('--prompt_strength', help='Prompt strength', type=float, default=None)

    args = parser.parse_args()

    # be sure to export your email and psw as environmental variables
    EMAIL = os.getenv("EDDIE_EMAIL")
    PASSWORD = os.getenv("EDDIE_PASSWORD")

    # Parameters
    ID_IMAGE = args.id_image  # Default is None, otherwise a string of a stored name
    REF_NAME = args.reference_name  # Default is None, otherwise a string of a stored name

    # Generation parameters
    KEYWORD = args.keyword
    PROMPT = args.prompt
    SEED = args.seed
    PROMPT_STRENGTH = args.prompt_strength

    # Image parameters
    INPUT_URL = args.input_url 
    INPUT_PATH = args.input_filepath
    OUTPUT_PATH = args.output_filepath

    REF_PATH = args.reference_path
    REF_URL = args.reference_url


    if INPUT_PATH is not None:
        if os.path.exists(INPUT_PATH):
            print(f'Using as input image the file located at: {INPUT_PATH}')
        else:
            print('Wrong filepath, check again')
            sys.exit()
    else:
        print('Input filepath not assigned, trying with URL..')
        if INPUT_URL is not None:
            print(f'Using the input image located at: {INPUT_URL}')
        else:
            print('Wrong input url, check again, exiting..')
            sys.exit()

    if REF_PATH is not None:
        if os.path.exists(REF_PATH):
            print(f'Using the reference located at: {REF_PATH}')
        else:
            print('Wrong reference path, check again')
            sys.exit()
    else:
        print('Reference path not assigned, check again')
        if REF_URL is not None:
            print(f'Using the reference located at: {REF_URL}')
        else:
            print('No reference images given, proceeding')

    # log in
    TOKEN_DICTIONARY = start_call(EMAIL, PASSWORD)
    print(TOKEN_DICTIONARY)
    
    PARAM_DICTIONARY = {
            'INPUT_PATH': INPUT_PATH,
            'OUTPUT_PATH': OUTPUT_PATH,
            'INPUT_URL': INPUT_URL,
            'ID_IMAGE': ID_IMAGE,
            'REF_PATH': REF_PATH,
            'REF_URL': REF_URL,
            'REF_NAME': REF_NAME,
            'KEYWORD': KEYWORD,
            'PROMPT': PROMPT,
            'SEED': SEED,
            'PROMPT_STRENGTH': PROMPT_STRENGTH,
            'OPTIONS': {
                        'flag_detection': False,  # avoid people detection
                        'flag_background_removal': True, # remove background from the image
                        'flag_caption_extraction': True, # extract caption from the image
                        },
        }

    # run different process based on batch variation or not

    response, final_path, ID_IMAGE = generate_background(PARAM_DICTIONARY, TOKEN_DICTIONARY) 
    
    print(f'Response: {response}, final_path: {final_path}, ID_IMAGE: {ID_IMAGE}')  